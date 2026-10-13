"""Post-baseline shared-operation example, derived without importing model code."""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
COORDINATOR = HERE.parent / 'coordinator'
S = set(product(range(3), range(3), range(4)))
K = {s for s in S if s[0] > 0 and s[1] > 0}
W = {
    'none': ((0, 0),),
    'focal': ((0, 0), (1, 0)),
    'common': ((0, 0), (1, 1)),
    'full': ((0, 0), (1, 0), (0, 1), (1, 1)),
}
TASK = ('renew_A', 'renew_B', 'train')
START = (2, 2, 3)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def action(mask):
    return tuple(int(bool(mask & (1 << j))) for j in range(3))


def cost(u):
    assets = u[0] + u[1]
    return assets + int(u[2] and assets == 0)


def choices(s, budget, shared=True):
    return [action(mask) for mask in range(8)
            if (cost(action(mask)) if shared else sum(action(mask))) <= budget
            and (mask == 0 or s[2] > 0)]


def step(s, u, shock):
    # Baseline order: age, reset selected capacities, then asset shock.
    a = 2 if u[0] else max(0, s[0] - 1)
    b = 2 if u[1] else max(0, s[1] - 1)
    k = 3 if u[2] else max(0, s[2] - 1)
    return (max(0, a - shock[0]), max(0, b - shock[1]), k)


def solve(budget, support, mode):
    relation = {s: [(u, [step(s, u, w) for w in W[support]]) for u in choices(s, budget)] for s in K}
    layers = [set(K)]
    while True:
        previous = layers[-1]
        current = set()
        for s, alternatives in relation.items():
            for u, successors in alternatives:
                accepts = all(t in previous for t in successors) if mode == 'robust' else any(t in previous for t in successors)
                if accepts:
                    current.add(s)
                    break
        if not current <= previous:
            raise AssertionError('Safe-set elimination must descend')
        if current == previous:
            break
        layers.append(current)
    kernel = layers[-1]
    finite = [layers[min(h, len(layers) - 1)] for h in range(13)]
    policy = []
    for s in sorted(kernel):
        u, successors = next((u, t) for u, t in relation[s]
                             if (all(v in kernel for v in t) if mode == 'robust' else any(v in kernel for v in t)))
        policy.append({'state': s, 'action': [TASK[i] for i in range(3) if u[i]], 'action_cost': cost(u),
                       'successors': [{'shock': w, 'state': t, 'in_kernel': t in kernel} for w, t in zip(W[support], successors)]})
    return {'layers': layers, 'finite': finite, 'kernel': kernel, 'policy': policy,
            'primary_max_safe': None if START in kernel else max(h for h, layer in enumerate(layers) if START in layer)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f'Refusing existing output: {args.output}')
    baseline_path = COORDINATOR / 'run-v1/results.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    audit = json.loads((HERE / 'model-checks-v1/checks.json').read_text(encoding='utf-8'))
    checks = []

    def check(label, value):
        checks.append({'check': label, 'passed': bool(value)})
        if not value:
            raise AssertionError(label)

    check('baseline previously checked pin', audit['root_results_sha256'] == digest(baseline_path))
    check('baseline 5218 checks pass', audit['checks_passed'] == 5218 and all(r['passed'] for r in audit['checks']))
    check('declared state counts', len(S) == 36 and len(K) == 16)
    for budget in range(4):
        for s in sorted(K):
            check(f'baseline actions retained B{budget}/{s}', set(choices(s, budget, shared=False)) <= set(choices(s, budget)))
            check(f'zero-skill eligibility B{budget}/{s}', s[2] > 0 or choices(s, budget) == [(0, 0, 0)])
            check(f'B2 equals B3 choices/{s}', choices(s, 2) == choices(s, 3))
    worlds = []
    for budget, support in product(range(4), W):
        old = next(w for w in baseline['worlds'] if (w['budget'], w['skill_age'], w['shock_support']) == (budget, 1, support))
        world = {'budget': budget, 'skill_age': 1, 'shock_support': support}
        for mode in ('possible', 'robust'):
            result = solve(budget, support, mode)
            finite = []
            for h, states in enumerate(result['finite']):
                previous = {tuple(v) for v in old[mode]['finite_horizons'][h]['states']}
                check(f'{budget}/{support}/{mode}/h{h} baseline subset', previous <= states)
                finite.append({'transitions': h, 'states': sorted(states), 'count': len(states),
                               'primary_viable': START in states, 'baseline_count': len(previous),
                               'added_from_baseline': sorted(states - previous), 'removed_from_baseline': sorted(previous - states)})
            previous = {tuple(v) for v in old[mode]['infinite_kernel']}
            check(f'{budget}/{support}/{mode} infinite baseline subset', previous <= result['kernel'])
            for row in result['policy']:
                s = tuple(row['state'])
                u = tuple(int(t in row['action']) for t in TASK)
                check(f'{budget}/{support}/{mode} policy cost/{s}', u in choices(s, budget) and row['action_cost'] == cost(u))
                flags = [v['in_kernel'] for v in row['successors']]
                check(f'{budget}/{support}/{mode} policy quantifier/{s}', all(flags) if mode == 'robust' else any(flags))
            world[mode] = {'finite_horizons': finite,
                           'fixed_point_layers': [{'iteration': h, 'states': sorted(s), 'count': len(s)} for h, s in enumerate(result['layers'])],
                           'infinite_kernel': sorted(result['kernel']), 'infinite_count': len(result['kernel']),
                           'baseline_infinite_count': len(previous), 'added_from_baseline': sorted(result['kernel'] - previous),
                           'removed_from_baseline': sorted(previous - result['kernel']),
                           'primary': {'start': START, 'infinite_viable': START in result['kernel'],
                                       'maximum_safe_transitions_if_finite': result['primary_max_safe']},
                           'infinite_policy': result['policy']}
        worlds.append(world)
    for support, mode in product(W, ('possible', 'robust')):
        low = next(w for w in worlds if (w['budget'], w['shock_support']) == (2, support))[mode]
        high = next(w for w in worlds if (w['budget'], w['shock_support']) == (3, support))[mode]
        check(f'B2 equals B3 kernel {support}/{mode}', low['infinite_kernel'] == high['infinite_kernel'])
        check(f'B2 equals B3 finite sets {support}/{mode}', [r['states'] for r in low['finite_horizons']] == [r['states'] for r in high['finite_horizons']])
    output = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'Exploratory post-baseline invented law variant',
        'scope': 'Shared repair/training operation; no historical calibration or cost-free-learning inference',
        'protocol_sha256': digest(HERE / 'CO-PRODUCTION-PROTOCOL.md'),
        'code_sha256': digest(Path(__file__)),
        'baseline_results_sha256': digest(baseline_path),
        'baseline_independent_check_sha256': digest(HERE / 'model-checks-v1/checks.json'),
        'worlds': worlds, 'checks_passed': len(checks), 'checks': checks,
    }
    args.output.mkdir(parents=True)
    (args.output / 'results.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'worlds': len(worlds), 'checks_passed': len(checks)}))


if __name__ == '__main__':
    main()
