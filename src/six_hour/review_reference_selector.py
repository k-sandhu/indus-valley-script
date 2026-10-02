"""Independent scalar and dynamic-programming review of saved selector worlds."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/reference-selector'
OUT = BASE / 'review/main-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Model:
    def __init__(self, reference, k, rational=False):
        self.k = k
        self.starts = Counter(row[0] for row in reference)
        self.ends = Counter(row[-1] for row in reference)
        self.occurrences = Counter(c for row in reference for c in row)
        self.edges = Counter((a, b) for row in reference for a, b in zip(row, row[1:]))
        self.lengths = Counter(map(len, reference))
        self.cells = Counter((len(row), pos, c) for row in reference for pos, c in enumerate(row))
        ratio = Fraction if rational else lambda a, b: a / b
        self.start = [ratio(self.starts[c] + 1, len(reference) + k) for c in range(k)]
        self.end = [ratio(self.ends[c] + 1, self.occurrences[c] + k + 1) for c in range(k)]
        self.transition = [[ratio(self.edges[a, b] + 1, self.occurrences[a] + k + 1)
                            for b in range(k)] for a in range(k)]
        self.rational = rational
        self.norms = {}

    def length_mass(self, length):
        if length not in self.norms:
            state = list(self.start)
            add = sum if self.rational else math.fsum
            for _ in range(length - 1):
                state = [add(state[a] * self.transition[a][b] for a in range(self.k)) for b in range(self.k)]
            self.norms[length] = add(state[c] * self.end[c] for c in range(self.k))
        return self.norms[length]

    def raw_probability(self, row):
        value = self.start[row[0]]
        for a, b in zip(row, row[1:]):
            value *= self.transition[a][b]
        return value * self.end[row[-1]]

    def graph_record(self, row, mapping):
        decoded = [mapping[c] for c in row]
        return math.fsum([math.log2(self.start[decoded[0]]), math.log2(self.end[decoded[-1]])]
                         + [math.log2(self.transition[a][b]) for a, b in zip(decoded, decoded[1:])])

    def graph_raw(self, rows, mapping):
        counts = Counter(tuple(row) for row in rows)
        return math.fsum(count * self.graph_record(row, mapping) for row, count in counts.items())

    def graph_conditional(self, rows, mapping):
        counts = Counter(tuple(row) for row in rows)
        return math.fsum(count * (self.graph_record(row, mapping) - math.log2(self.length_mass(len(row))))
                         for row, count in counts.items())

    def slot_record(self, row, mapping):
        length = len(row)
        denominator = self.lengths[length] + self.k
        return math.fsum(math.log2((self.cells[length, pos, mapping[c]] + 1) / denominator)
                         for pos, c in enumerate(row))

    def slot(self, rows, mapping):
        counts = Counter(tuple(row) for row in rows)
        return math.fsum(count * self.slot_record(row, mapping) for row, count in counts.items())

    def weights(self, rows):
        counts = Counter((len(row), pos, c) for row in rows for pos, c in enumerate(row))
        w = np.zeros((self.k, self.k))
        for code in range(self.k):
            for target in range(self.k):
                w[code, target] = math.fsum(n * math.log2((self.cells[length, pos, target] + 1)
                                                         / (self.lengths[length] + self.k))
                                          for (length, pos, c), n in counts.items() if c == code)
        return w


def rational_checks():
    reference = [[0, 1, 0], [1, 0, 1], [0, 0], [1, 1], [0, 1, 1]]
    model = Model(reference, 2, rational=True)
    checks = []
    for length in range(1, 5):
        space = list(product(range(2), repeat=length))
        enumerated = sum(model.raw_probability(row) for row in space)
        norm = model.length_mass(length)
        conditional = sum(model.raw_probability(row) / norm for row in space)
        slot_mass = Fraction(0)
        for row in space:
            value = Fraction(1)
            for pos, c in enumerate(row):
                value *= Fraction(model.cells[length, pos, c] + 1, model.lengths[length] + 2)
            slot_mass += value
        checks.append({'length': length, 'graph_enumeration_equals_recurrence': enumerated == norm,
                       'graph_conditional_mass': str(conditional), 'slot_conditional_mass': str(slot_mass),
                       'raw_length_mass': str(norm)})
    return checks


def dual_certificate(w, mapping):
    k = len(w)
    constraints = np.zeros((k * k, 2 * k))
    for i in range(k):
        for j in range(k):
            constraints[i * k + j, i] = -1
            constraints[i * k + j, k + j] = -1
    bounds = [(None, None)] * (2 * k)
    bounds[k] = (0, 0)
    solved = linprog(np.ones(2 * k), A_ub=constraints, b_ub=-w.ravel(), bounds=bounds, method='highs')
    if not solved.success:
        return {'success': False, 'message': solved.message}
    potentials = solved.x[:k, None] + solved.x[None, k:]
    selected = math.fsum(float(w[i, mapping[i]]) for i in range(k))
    upper = math.fsum(map(float, solved.x))
    return {'success': True, 'upper_bound': upper, 'returned_score': selected,
            'gap': upper - selected, 'minimum_slack': float((potentials - w).min()),
            'potentials': solved.x.tolist()}


def main():
    if OUT.exists():
        raise RuntimeError('Preserve earlier review endpoints.')
    OUT.mkdir(parents=True)
    started = time.perf_counter()
    source_paths = [BASE / 'PROTOCOL.md', BASE / 'main/results.json', BASE / 'main/worlds.json',
                    BASE / 'main/code_snapshot.py', BASE / 'main/generator_snapshot.py',
                    BASE / 'main/slot_helper_snapshot.py', BASE / 'review/PROTOCOL.md']
    input_hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in source_paths}
    results = json.loads((BASE / 'main/results.json').read_text(encoding='utf-8'))
    worlds = json.loads((BASE / 'main/worlds.json').read_text(encoding='utf-8'))
    checks, discrepancies = [], []
    maxima = defaultdict(float)
    def check(name, value, detail=None):
        checks.append({'name': name, 'passed': bool(value), 'detail': detail})
        if not value:
            discrepancies.append(checks[-1])
    def close(name, actual, saved, tolerance):
        error = abs(actual - saved)
        maxima[name] = max(maxima[name], error)
        if error > tolerance:
            discrepancies.append({'name': name, 'actual': actual, 'saved': saved, 'error': error})
        return error <= tolerance
    rational = rational_checks()
    check('exact_rational_normalization', all(o['graph_enumeration_equals_recurrence'] and o['graph_conditional_mass'] == '1' and o['slot_conditional_mass'] == '1' for o in rational))
    check('source_hashes_match_snapshot', all(results[key] == digest(BASE / 'main' / name) for key, name in [('code_sha256', 'code_snapshot.py'), ('generator_sha256', 'generator_snapshot.py'), ('slot_helper_sha256', 'slot_helper_snapshot.py')]))
    check('protocol_hash', results['protocol_sha256'] == digest(BASE / 'PROTOCOL.md'))
    check('complete_grid_dimensions', len(worlds) == 96 and len(results['selections']) == 96 and len(results['rows']) == 1536)
    lookup = {(o['seed'], o['shift']): o for o in worlds}
    check('unique_world_keys', len(lookup) == 96)
    expected = {910261002 + 1000000 * ki + 100000 * fi + 1000 * r
                for ki in range(2) for fi in range(2) for r in range(12)}
    check('all48_declared_system_seeds', {o['seed'] for o in worlds} == expected)
    for world in worlds:
        seed, k, shift = world['seed'], world['k'], world['shift']
        check(f'world_integrity_{seed}_{shift}', len(world['reference']) == 400 and len(world['training']) == 640 and len(world['heldout']) == 400 and all(0 <= c < k for part in ('reference', 'training', 'heldout') for row in world[part] for c in row))
        encoding = np.random.default_rng(seed + 4).permutation(k)
        truth = [int(np.flatnonzero(encoding == i)[0]) for i in range(k)]
        check(f'truth_permutation_{seed}_{shift}', truth == world['truth'])
    for seed in expected:
        check(f'reference_shared_across_shift_{seed}', lookup[seed, 0]['reference'] == lookup[seed, .35]['reference'])
    selections, models = {}, {}
    for selection in results['selections']:
        seed, size, k = selection['seed'], selection['reference_records'], selection['k']
        reference = lookup[seed, 0]['reference'][:size]
        assigned = {int(i): pos % 3 for pos, i in enumerate(np.random.default_rng(seed + 50).permutation(size))}
        folds = [assigned[i] for i in range(size)]
        check(f'fold_assignment_{seed}_{size}', folds == selection['folds'])
        scores = []
        for fold in range(3):
            train = [row for i, row in enumerate(reference) if assigned[i] != fold]
            test = [row for i, row in enumerate(reference) if assigned[i] == fold]
            fitted = Model(train, k)
            score = {'fold': fold, 'train_records': len(train), 'test_records': len(test),
                     'slot_log2_score': fitted.slot(test, list(range(k))),
                     'graph_log2_score': fitted.graph_conditional(test, list(range(k))),
                     'length_masses': {str(length): float(fitted.length_mass(length)) for length in sorted(set(map(len, test)))}}
            saved = selection['scores'][fold]
            check(f'fold_record_counts_{seed}_{size}_{fold}', len(train) == saved['train_records'] and len(test) == saved['test_records'])
            close('fold_slot_score', score['slot_log2_score'], saved['slot_log2_score'], 1e-7)
            close('fold_graph_score', score['graph_log2_score'], saved['graph_log2_score'], 1e-7)
            scores.append(score)
        slot_score = math.fsum(o['slot_log2_score'] for o in scores)
        graph_score = math.fsum(o['graph_log2_score'] for o in scores)
        chosen = 'length_slot' if slot_score > graph_score else 'graph_multistart'
        check(f'reference_choice_{seed}_{size}', chosen == selection['selected'])
        close('pooled_slot_score', slot_score, selection['slot_score'], 1e-7)
        close('pooled_graph_score', graph_score, selection['graph_score'], 1e-7)
        selections[seed, size] = {'seed': seed, 'k': k, 'family': selection['family'], 'reference_records': size,
                                  'selected': chosen, 'slot_score': slot_score, 'graph_score': graph_score,
                                  'slot_minus_graph_bits': slot_score - graph_score, 'folds': scores}
        models[seed, size] = Model(reference, k)
    conditions = defaultdict(dict)
    for row in results['rows']:
        key = tuple(row[n] for n in ('seed', 'shift', 'reference_records', 'training_records'))
        conditions[key][row['algorithm']] = row
    check('384_conditions_four_distinct_outputs', len(conditions) == 384 and all(set(o) == {'length_slot', 'graph_multistart', 'reference_selected', 'family_oracle'} for o in conditions.values()))
    reviewed_rows, certificates = [], []
    for ci, (key, group) in enumerate(sorted(conditions.items())):
        seed, shift, ref_size, train_size = key
        world = lookup[seed, shift]
        fitted, k = models[seed, ref_size], world['k']
        train, heldout = world['training'][:train_size], world['heldout']
        choice = selections[seed, ref_size]['selected']
        check(f'selected_map_identity_{key}', group['reference_selected']['mapping'] == group[choice]['mapping'])
        oracle = 'length_slot' if world['family'] == 'administrative_form' else 'graph_multistart'
        check(f'oracle_map_identity_{key}', group['family_oracle']['mapping'] == group[oracle]['mapping'])
        w = fitted.weights(train)
        certificate = dual_certificate(w, group['length_slot']['mapping'])
        certificate['condition'] = list(key)
        certificates.append(certificate)
        check(f'slot_dual_certificate_{key}', certificate['success'] and abs(certificate['gap']) < 1e-7 and certificate['minimum_slack'] > -1e-7)
        tokens = sum(map(len, heldout))
        scored = {}
        for name, row in group.items():
            mapping = row['mapping']
            check(f'mapping_bijection_{key}_{name}', sorted(mapping) == list(range(k)))
            check(f'row_reference_choice_{key}_{name}', row['reference_choice'] == choice)
            truth = world['truth']
            exact = mapping == truth
            accuracy = sum(a == b for a, b in zip(mapping, truth)) / k
            check(f'truth_comparison_{key}_{name}', row['exact_recovery'] == exact and row['symbol_accuracy'] == accuracy)
            mkey = tuple(mapping)
            if mkey not in scored:
                scored[mkey] = {'slot_train_score': fitted.slot(train, mapping),
                               'graph_train_score': fitted.graph_raw(train, mapping),
                               'slot_heldout_bits_per_token': -fitted.slot(heldout, mapping) / tokens,
                               'graph_conditional_heldout_bits_per_token': -fitted.graph_conditional(heldout, mapping) / tokens}
            for metric, actual in scored[mkey].items():
                close(metric, actual, row[metric], 1e-9 if 'per_token' in metric else 1e-7)
            reviewed_rows.append({**{n: row[n] for n in ('seed', 'family', 'k', 'shift', 'reference_records', 'training_records', 'algorithm')},
                                  'mapping': mapping, 'exact_recovery': exact, 'symbol_accuracy': accuracy, **scored[mkey]})
        if ci % 64 == 0:
            print(json.dumps({'reviewed_conditions': ci + 1, 'of': 384}), flush=True)
    check('all_scalar_scores_agree', not [o for o in discrepancies if 'actual' in o])
    check('input_bytes_preserved', all(digest(ROOT / name) == value for name, value in input_hashes.items()))
    aggregates = []
    for k in (8, 20):
        for family in ('transition', 'administrative_form'):
            for algorithm in ('length_slot', 'graph_multistart', 'reference_selected', 'family_oracle'):
                group = [o for o in reviewed_rows if o['k'] == k and o['family'] == family and o['algorithm'] == algorithm]
                aggregates.append({'k': k, 'family': family, 'algorithm': algorithm, 'conditions': len(group),
                                   'complete_recovery_count': sum(o['exact_recovery'] for o in group),
                                   'mean_symbol_accuracy': math.fsum(o['symbol_accuracy'] for o in group) / len(group),
                                   'mean_slot_heldout_bits_per_token': math.fsum(o['slot_heldout_bits_per_token'] for o in group) / len(group),
                                   'mean_graph_conditional_heldout_bits_per_token': math.fsum(o['graph_conditional_heldout_bits_per_token'] for o in group) / len(group)})
    summary = {'checks': len(checks), 'passed': sum(o['passed'] for o in checks), 'discrepancies': discrepancies,
               'max_scalar_errors': dict(maxima), 'closest_reference_choice_gap_bits': min(abs(o['slot_minus_graph_bits']) for o in selections.values()),
               'choice_counts': dict(Counter(f"{o['k']}/{o['family']}/{o['reference_records']}/{o['selected']}" for o in selections.values())),
               'aggregates': aggregates, 'rational_checks': rational, 'input_hashes': input_hashes,
               'elapsed_seconds': time.perf_counter() - started, 'review_code_sha256': digest(Path(__file__))}
    for name, payload in [('verification.json', summary), ('checks.json', checks), ('selections.json', list(selections.values())),
                          ('reviewed-rows.json', reviewed_rows), ('slot-dual-certificates.json', certificates)]:
        (OUT / name).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    (OUT / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks': summary['checks'], 'passed': summary['passed'], 'discrepancies': len(discrepancies),
                      'max_errors': dict(maxima), 'seconds': summary['elapsed_seconds']}, indent=2))


def factor(n):
    powers = Counter()
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            powers[divisor] += 1
            n //= divisor
        divisor += 1
    if n > 1:
        powers[n] += 1
    return powers


def exact_delta(model, training, original, alternative):
    powers = Counter()
    cells = Counter((len(row), pos, c) for row in training for pos, c in enumerate(row))
    for (length, pos, code), n in cells.items():
        if original[code] == alternative[code]:
            continue
        for sign, target in [(1, alternative[code]), (-1, original[code])]:
            for prime, exponent in factor(model.cells[length, pos, target] + 1).items():
                powers[prime] += sign * n * exponent
    return {p: e for p, e in powers.items() if e}


def path_between(adjacency, start, goal):
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        for following in adjacency[current]:
            if following not in visited:
                visited.add(following)
                queue.append((following, path + [following]))
    return None


def additional():
    out = BASE / 'review/additional-v1'
    if out.exists():
        raise RuntimeError('Preserve earlier diagnostic endpoints.')
    out.mkdir()
    rows = json.loads((BASE / 'review/main-v1/reviewed-rows.json').read_text(encoding='utf-8'))
    worlds = json.loads((BASE / 'main/worlds.json').read_text(encoding='utf-8'))
    world_lookup = {(w['seed'], w['shift']): w for w in worlds}
    certificates = json.loads((BASE / 'review/main-v1/slot-dual-certificates.json').read_text(encoding='utf-8'))
    row_lookup = {(r['seed'], r['shift'], r['reference_records'], r['training_records'], r['algorithm']): r for r in rows}
    paired = []
    system_means = []
    for ki, k in enumerate((8, 20)):
        for fi, family in enumerate(('transition', 'administrative_form')):
            selected = [r for r in rows if r['k'] == k and r['family'] == family]
            seeds = sorted({r['seed'] for r in selected})
            rng_seed = 7710261002 + 1000 * ki + 100 * fi
            draws = np.random.default_rng(rng_seed).integers(0, 12, size=(20000, 12))
            means = {}
            for seed in seeds:
                means[seed] = {}
                for name in ('reference_selected', 'length_slot', 'graph_multistart', 'family_oracle'):
                    group = [r for r in selected if r['seed'] == seed and r['algorithm'] == name]
                    assert len(group) == 8
                    means[seed][name] = {metric: math.fsum(float(r[metric]) for r in group) / 8
                                         for metric in ('exact_recovery', 'symbol_accuracy', 'slot_heldout_bits_per_token', 'graph_conditional_heldout_bits_per_token')}
                system_means.append({'seed': seed, 'k': k, 'family': family, 'means': means[seed]})
            for comparison in ('length_slot', 'graph_multistart', 'family_oracle'):
                for metric in ('exact_recovery', 'symbol_accuracy', 'slot_heldout_bits_per_token', 'graph_conditional_heldout_bits_per_token'):
                    delta = np.asarray([means[seed]['reference_selected'][metric] - means[seed][comparison][metric] for seed in seeds])
                    samples = delta[draws].mean(axis=1)
                    paired.append({'k': k, 'family': family, 'comparator': comparison, 'metric': metric,
                                   'direction': 'selector minus comparator', 'systems': 12, 'conditions_per_system': 8,
                                   'mean_difference': float(delta.mean()),
                                   'percentile_95_interval': np.quantile(samples, [.025, .975]).tolist(),
                                   'bootstrap_replicates': 20000, 'bootstrap_seed': rng_seed,
                                   'system_differences': delta.tolist()})
    alternatives, rejections = [], []
    for cert in certificates:
        seed, shift, ref_size, train_size = cert['condition']
        world = world_lookup[seed, shift]
        k = world['k']
        model = Model(world['reference'][:ref_size], k)
        train = world['training'][:train_size]
        w = model.weights(train)
        original = row_lookup[seed, shift, ref_size, train_size, 'length_slot']['mapping']
        inverse = {column: i for i, column in enumerate(original)}
        p = cert['potentials']
        adjacency = {i: sorted({inverse[j] for j in range(k) if j != original[i] and p[i] + p[k + j] - w[i, j] <= 1e-7}) for i in range(k)}
        witnesses = []
        for start in range(k):
            for second in adjacency[start]:
                path = path_between(adjacency, second, start)
                if path is None:
                    continue
                cycle = [start] + path[:-1]
                candidate = list(original)
                for i, code in enumerate(cycle):
                    candidate[code] = original[cycle[(i + 1) % len(cycle)]]
                assert sorted(candidate) == list(range(k))
                delta = exact_delta(model, train, original, candidate)
                if delta:
                    rejections.append({'condition': cert['condition'], 'cycle': cycle, 'prime_exponent_difference': delta})
                    continue
                numerical_delta = model.slot(train, candidate) - model.slot(train, original)
                assert abs(numerical_delta) < 1e-7
                witnesses.append({'code': start, 'cycle': cycle, 'mapping': candidate,
                                  'changed_codes': [i for i in range(k) if candidate[i] != original[i]],
                                  'exact_numerator_ratio': '1', 'floating_log2_difference': numerical_delta})
                break
        if witnesses:
            alternatives.append({'condition': cert['condition'], 'k': k, 'family': world['family'],
                                 'selected_mapping': original, 'ambiguous_codes_witnessed': sorted({i for w in witnesses for i in w['changed_codes']}),
                                 'witnesses': witnesses})
    check = {'paired_comparisons': len(paired), 'system_means': len(system_means),
             'slot_conditions_checked': len(certificates), 'slot_conditions_with_exact_tie_witness': len(alternatives),
             'exact_tie_witnesses': sum(len(a['witnesses']) for a in alternatives),
             'rejected_near_tie_cycles': len(rejections),
             'tie_groups': dict(Counter(f"{a['k']}/{a['family']}" for a in alternatives)),
             'primary_endpoint_preserved': digest(BASE / 'review/main-v1/verification.json'),
             'additional_protocol_sha256': digest(BASE / 'review/ADDITIONAL_PROTOCOL.md'),
             'code_sha256': digest(Path(__file__))}
    for name, payload in [('paired-comparisons.json', paired), ('system-means.json', system_means),
                          ('exact-slot-alternatives.json', alternatives), ('rejected-cycles.json', rejections),
                          ('verification.json', check)]:
        (out / name).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    (out / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(check, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--additional', action='store_true')
    args = parser.parse_args()
    additional() if args.additional else main()
