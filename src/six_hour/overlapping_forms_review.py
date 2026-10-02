"""Independent scalar, assignment-dual and sampled-input audit of fresh forms."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.optimize import linear_sum_assignment

from review_reference_selector import Model, dual_certificate, factor, rational_checks

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms'
K = 20
VARIANTS = [('separated', None), ('same_length_0', 0.), ('same_length_35', .35), ('same_length_70', .70)]
METHODS = ['length_slot', 'graph_multistart', 'reference_selected', 'form_observed_slot']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


class FormModel:
    def __init__(self, reference, labels):
        self.cells = Counter((label, pos, c) for row, label in zip(reference, labels) for pos, c in enumerate(row))
        self.totals = Counter(labels)

    def weights(self, rows, labels):
        by_code = defaultdict(list)
        for (label, pos, c), n in Counter((label, pos, c) for row, label in zip(rows, labels) for pos, c in enumerate(row)).items():
            by_code[c].append((label, pos, n))
        return np.asarray([[math.fsum(n * math.log2((self.cells[label, pos, target] + 1) / (self.totals[label] + K)) for label, pos, n in by_code[c]) for target in range(K)] for c in range(K)])

    def score(self, rows, labels, mapping):
        counts = Counter((label, pos, c) for row, label in zip(rows, labels) for pos, c in enumerate(row))
        return math.fsum(n * math.log2((self.cells[label, pos, mapping[c]] + 1) / (self.totals[label] + K)) for (label, pos, c), n in counts.items())


def reconstruct_parameters(seed):
    rng = np.random.default_rng(seed)
    rng.dirichlet(np.full(K, .6))
    rng.dirichlet(np.full(K, .35), size=K)
    pools = np.array_split(rng.permutation(K), 4)
    original = []
    for roles in [[0, 1, 2, 3], [0, 2, 1, 2, 3], [1, 0, 2, 1, 2, 3]]:
        form = []
        for role in roles:
            p = np.zeros(K)
            p[pools[role]] = rng.dirichlet(np.full(len(pools[role]), .7))
            form.append(p.tolist())
        original.append(form)
    mixture = rng.dirichlet(np.ones(3)).tolist()
    extended = [[list(p) for p in form] for form in original]
    padding_pools = [np.sort(pool) for pool in pools]
    added = np.random.default_rng(seed + 100)
    for fi, roles in [(0, [0, 3]), (1, [3])]:
        for role in roles:
            p = np.zeros(K)
            p[padding_pools[role]] = added.dirichlet(np.full(len(padding_pools[role]), .7))
            extended[fi].append(p.tolist())
    return dict(seed=seed, original=original, extended=extended, mixture=mixture,
                background=added.dirichlet(np.full(K, .7)).tolist(), pools=[p.tolist() for p in padding_pools])


def draw_category(weights, uniform):
    cumulative = 0.
    for index, value in enumerate(weights):
        cumulative += value
        if uniform < cumulative:
            return index
    return len(weights) - 1


def replay(spec, variant, n, seed, shift):
    alpha = dict(VARIANTS)[variant]
    mixture = [(1 - shift) * spec['mixture'][i] + shift * spec['mixture'][(i - 1) % 3] for i in range(3)]
    forms = spec['original'] if alpha is None else [[[(1 - alpha) * p[c] + alpha * spec['background'][c] for c in range(K)] for p in form] for form in spec['extended']]
    draws = np.random.default_rng(seed).random((n, 7))
    rows, labels = [], []
    for values in draws:
        label = draw_category(mixture, values[0])
        labels.append(label)
        rows.append([draw_category(p, values[pos + 1]) for pos, p in enumerate(forms[label])])
    return rows, labels


@lru_cache(None)
def factors(n):
    return dict(factor(n))


def equality(cells, training_counts, original, alternative):
    exponents = Counter()
    for (tag, pos, code), count in training_counts.items():
        for sign, target in [(1, alternative[code]), (-1, original[code])]:
            for prime, exponent in factors(cells[tag, pos, target] + 1).items():
                exponents[prime] += sign * count * exponent
    return {p: e for p, e in exponents.items() if e}


def alternatives(w, mapping, cells, training_counts):
    score = math.fsum(float(w[i, mapping[i]]) for i in range(K))
    witnesses, near = [], []
    exclusion_gaps = []
    for code in range(K):
        forbidden = w.copy()
        forbidden[code, mapping[code]] = -1e30
        _, alternate = linear_sum_assignment(forbidden, maximize=True)
        alternate_score = math.fsum(float(w[i, alternate[i]]) for i in range(K))
        gap = score - alternate_score
        exclusion_gaps.append(gap)
        if abs(gap) <= 1e-7:
            delta = equality(cells, training_counts, mapping, alternate)
            record = dict(excluded_code=code, mapping=alternate.tolist(), score_gap_bits=gap,
                          changed_codes=[i for i in range(K) if mapping[i] != alternate[i]])
            if delta:
                near.append(dict(**record, prime_exponents=delta))
            else:
                witnesses.append(dict(**record, exact_likelihood_ratio='1'))
    return dict(witnesses=witnesses, rejected_near_equalities=near, exclusion_score_gaps_bits=exclusion_gaps)


def main():
    out = BASE / 'review-v1'
    if out.exists():
        raise RuntimeError('Preserve earlier endpoint.')
    out.mkdir()
    start = time.perf_counter()
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in (BASE / 'main-v1').iterdir() if p.is_file()}
    result = json.loads((BASE / 'main-v1/results.json').read_text(encoding='utf-8'))
    worlds = json.loads((BASE / 'main-v1/worlds.json').read_text(encoding='utf-8'))
    params = json.loads((BASE / 'main-v1/parameters.json').read_text(encoding='utf-8'))
    choices = result['choices']
    checks, errors = [], []
    maxima = defaultdict(float)

    def check(name, passed, details=None):
        checks.append(dict(check=name, passed=bool(passed), details=details))
        if not passed:
            errors.append(checks[-1])

    def close(name, actual, saved, tol=1e-7):
        error = abs(float(actual) - float(saved))
        maxima[name] = max(maxima[name], error)
        check(name, error < tol, dict(error=error) if error >= tol else None)

    check('main dimensions', len(params) == 12 and len(worlds) == 96 and len(choices) == 96 and len(result['cases']) == 192 and len(result['rows']) == 768)
    check('fresh declared seeds', {p['seed'] for p in params} == {1010261002 + 1000 * r for r in range(12)})
    check('main protocol hash', result['protocol_sha256'] == digest(BASE / 'PROTOCOL.md'))
    for name, expected in result['sources'].items():
        check('executed snapshot ' + name, digest(BASE / 'main-v1' / name) == expected)
    rational = rational_checks()
    check('exact small-space conditional normalization', all(x['graph_enumeration_equals_recurrence'] and x['graph_conditional_mass'] == '1' and x['slot_conditional_mass'] == '1' for x in rational))
    specifications = {p['seed']: p for p in params}
    for p in params:
        check('parameter replay ' + str(p['seed']), reconstruct_parameters(p['seed']) == p)
        check('form lengths ' + str(p['seed']), list(map(len, p['original'])) == [4, 5, 6] and list(map(len, p['extended'])) == [6, 6, 6])
    world_lookup = {(w['seed'], w['variant'], w['shift']): w for w in worlds}
    for world in worlds:
        seed, variant, shift = world['seed'], world['variant'], world['shift']
        spec = specifications[seed]
        encoding = np.random.default_rng(seed + 4).permutation(K).tolist()
        truth = [encoding.index(c) for c in range(K)]
        check(f'encoding/truth {seed}/{variant}/{shift}', encoding == world['encoding'] and truth == world['truth'])
        for part, n, offset, change in [('reference', 400, 1, 0.), ('training', 640, 2, shift), ('heldout', 400, 3, shift)]:
            plain, labels = replay(spec, variant, n, seed + offset, change)
            replayed = plain if part == 'reference' else [[encoding[c] for c in row] for row in plain]
            check(f'input replay {seed}/{variant}/{shift}/{part}', replayed == world[part] and labels == world[part + '_labels'])
    models, form_models, reviewed_choices = {}, {}, []
    for choice in choices:
        seed, variant, size = choice['seed'], choice['variant'], choice['reference_records']
        world = world_lookup[seed, variant, 0.]
        reference = world['reference'][:size]
        order = np.random.default_rng(seed + 50).permutation(size)
        folds = [0] * size
        for ordinal, index in enumerate(order):
            folds[index] = ordinal % 3
        check(f'fold replay {seed}/{variant}/{size}', folds == choice['folds'])
        scores = []
        for fold in range(3):
            train = [row for i, row in enumerate(reference) if folds[i] != fold]
            test = [row for i, row in enumerate(reference) if folds[i] == fold]
            model = Model(train, K)
            scalar_slot = model.slot(test, list(range(K)))
            scalar_graph = model.graph_conditional(test, list(range(K)))
            close('fold slot score', scalar_slot, choice['scores'][fold]['slot_log2_score'])
            close('fold graph conditional score', scalar_graph, choice['scores'][fold]['graph_log2_score'])
            check('fold record totals', len(train) == choice['scores'][fold]['train_records'] and len(test) == choice['scores'][fold]['test_records'])
            scores.append((scalar_slot, scalar_graph))
        slot_score = math.fsum(x[0] for x in scores)
        graph_score = math.fsum(x[1] for x in scores)
        close('pooled slot score', slot_score, choice['slot_score'])
        close('pooled graph score', graph_score, choice['graph_score'])
        selected = 'length_slot' if slot_score > graph_score else 'graph_multistart'
        check('reference choice', selected == choice['selected'])
        key = seed, variant, size
        models[key] = Model(reference, K)
        form_models[key] = FormModel(reference, world['reference_labels'][:size])
        reviewed_choices.append(dict(seed=seed, variant=variant, reference_records=size, selected=selected,
                                     slot_minus_graph_bits=slot_score - graph_score, slot_score=slot_score, graph_score=graph_score))
    groups = defaultdict(dict)
    for row in result['rows']:
        key = tuple(row[field] for field in ('seed', 'variant', 'shift', 'reference_records'))
        groups[key][row['algorithm']] = row
    check('192 conditions have four methods', len(groups) == 192 and all(set(g) == set(METHODS) for g in groups.values()))
    certificates, ties, reviewed_rows, objective_diagnostics = [], [], [], []
    choice_lookup = {(c['seed'], c['variant'], c['reference_records']): c for c in reviewed_choices}
    case_lookup = {tuple(c[field] for field in ('seed', 'variant', 'shift', 'reference_records')): c for c in result['cases']}
    for ci, (key, group) in enumerate(sorted(groups.items())):
        seed, variant, shift, size = key
        world = world_lookup[seed, variant, shift]
        model, fmodel = models[seed, variant, size], form_models[seed, variant, size]
        train, heldout = world['training'], world['heldout']
        labels, held_labels = world['training_labels'], world['heldout_labels']
        w = model.weights(train)
        fw = fmodel.weights(train, labels)
        close('ordinary weight matrix maximum error', np.max(abs(w - np.asarray(case_lookup[key]['slot_weights']))), 0., 1e-8)
        close('form-observed weight matrix maximum error', np.max(abs(fw - np.asarray(case_lookup[key]['form_weights']))), 0., 1e-8)
        choice = choice_lookup[seed, variant, size]['selected']
        check('selected map comes from reference choice', group['reference_selected']['mapping'] == group[choice]['mapping'])
        for method, weights, cells, tcells in [
            ('length_slot', w, model.cells, Counter((len(row), pos, c) for row in train for pos, c in enumerate(row))),
            ('form_observed_slot', fw, fmodel.cells, Counter((label, pos, c) for row, label in zip(train, labels) for pos, c in enumerate(row)))]:
            mapping = group[method]['mapping']
            cert = dual_certificate(weights, mapping)
            certificates.append(dict(condition=list(key), algorithm=method, **cert))
            check('independent assignment dual', cert['success'] and abs(cert['gap']) < 1e-7 and cert['minimum_slack'] > -1e-7)
            alternatives_record = alternatives(weights, mapping, cells, tcells)
            ties.append(dict(condition=list(key), algorithm=method, **alternatives_record))
            check('exclusion assignments cannot improve selected optimum', min(alternatives_record['exclusion_score_gaps_bits']) > -1e-7)
        if variant == 'separated':
            close('separated length/form weights coincide', np.max(abs(w - fw)), 0., 1e-8)
        tokens = sum(map(len, heldout))
        for method, row in group.items():
            mapping = row['mapping']
            check('mapping bijection', sorted(mapping) == list(range(K)))
            exact = mapping == world['truth']
            symbol_accuracy = sum(a == b for a, b in zip(mapping, world['truth'])) / K
            check('complete and symbol accuracy', exact == row['exact_recovery'] and symbol_accuracy == row['symbol_accuracy'])
            metrics = dict(slot_train_score=model.slot(train, mapping), graph_train_score=model.graph_raw(train, mapping),
                           form_train_score=fmodel.score(train, labels, mapping),
                           slot_heldout_bits_per_token=-model.slot(heldout, mapping) / tokens,
                           graph_conditional_heldout_bits_per_token=-model.graph_conditional(heldout, mapping) / tokens,
                           form_observed_heldout_bits_per_token=-fmodel.score(heldout, held_labels, mapping) / tokens)
            for name, actual in metrics.items():
                close(name, actual, row[name], 1e-9 if 'per_token' in name else 1e-7)
            reviewed_rows.append(dict(condition=list(key), seed=seed, variant=variant, shift=shift, reference_records=size,
                                      algorithm=method, exact_recovery=exact, symbol_accuracy=symbol_accuracy, **metrics))
        returned = model.graph_raw(train, group['graph_multistart']['mapping'])
        truth_score = model.graph_raw(train, world['truth'])
        objective_diagnostics.append(dict(condition=list(key), graph_returned_minus_truth_bits=returned - truth_score,
                                          graph_recovered=group['graph_multistart']['exact_recovery'],
                                          slot_truth_gap_bits=model.slot(train, group['length_slot']['mapping']) - model.slot(train, world['truth']),
                                          form_truth_gap_bits=fmodel.score(train, labels, group['form_observed_slot']['mapping']) - fmodel.score(train, labels, world['truth'])))
        if ci % 32 == 0:
            print(json.dumps(dict(reviewed_conditions=ci + 1)), flush=True)
    check('main bytes preserved', all(digest(ROOT / path) == value for path, value in hashes.items()))
    summary_rows = []
    for variant, _ in VARIANTS:
        for size in (40, 400):
            for method in METHODS:
                group = [r for r in reviewed_rows if r['variant'] == variant and r['reference_records'] == size and r['algorithm'] == method]
                summary_rows.append(dict(variant=variant, reference_records=size, algorithm=method, conditions=len(group),
                                         complete_recovery=sum(r['exact_recovery'] for r in group),
                                         mean_symbol_accuracy=math.fsum(r['symbol_accuracy'] for r in group) / len(group),
                                         mean_slot_heldout_bits_per_token=math.fsum(r['slot_heldout_bits_per_token'] for r in group) / len(group),
                                         mean_graph_conditional_heldout_bits_per_token=math.fsum(r['graph_conditional_heldout_bits_per_token'] for r in group) / len(group),
                                         mean_form_observed_heldout_bits_per_token=math.fsum(r['form_observed_heldout_bits_per_token'] for r in group) / len(group)))
    seeds = sorted(specifications)
    bootstrap = np.random.default_rng(1210261002).integers(0, 12, (20000, 12))
    means = {(seed, variant, method, metric): math.fsum(float(r[metric]) for r in reviewed_rows if r['seed'] == seed and r['variant'] == variant and r['algorithm'] == method) / 4 for seed in seeds for variant, _ in VARIANTS for method in METHODS for metric in ('exact_recovery', 'symbol_accuracy')}
    paired = []
    for variant, baseline in [('same_length_0', 'separated'), ('same_length_35', 'same_length_0'), ('same_length_70', 'same_length_0')]:
        for method in METHODS:
            for metric in ('exact_recovery', 'symbol_accuracy'):
                delta = np.asarray([means[seed, variant, method, metric] - means[seed, baseline, method, metric] for seed in seeds])
                interval = np.quantile(delta[bootstrap].mean(axis=1), [.025, .975]).tolist()
                paired.append(dict(variant=variant, comparator_variant=baseline, algorithm=method, metric=metric,
                                   mean_difference=float(delta.mean()), percentile_95_interval=interval, system_differences=delta.tolist(),
                                   systems=12, conditions_per_system=4, bootstrap_draws=20000, bootstrap_seed=1210261002))
    summary = dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks), failures=errors,
                   elapsed_seconds=time.perf_counter() - start, max_scalar_errors=dict(maxima), aggregates=summary_rows,
                   choice_counts=dict(Counter(f"{c['variant']}/{c['reference_records']}/{c['selected']}" for c in reviewed_choices)),
                   closest_choice_gap_bits=min(abs(c['slot_minus_graph_bits']) for c in reviewed_choices),
                   linear_conditions_checked=len(ties), linear_conditions_with_exact_ties=sum(bool(t['witnesses']) for t in ties),
                   exact_tie_witnesses=sum(len(t['witnesses']) for t in ties), rejected_near_equalities=sum(len(t['rejected_near_equalities']) for t in ties),
                   source_hashes=hashes, review_protocol_sha256=digest(BASE / 'REVIEW_PROTOCOL.md'), code_sha256=digest(Path(__file__)),
                   reused_independent_helper_sha256=digest(ROOT / 'src/six_hour/review_reference_selector.py'))
    for name, value in [('verification.json', summary), ('checks.json', checks), ('reviewed-rows.json', reviewed_rows),
                        ('reference-choices.json', reviewed_choices), ('dual-certificates.json', certificates),
                        ('linear-alternatives.json', ties), ('paired-comparisons.json', paired), ('objective-diagnostics.json', objective_diagnostics)]:
        write(out / name, value)
    (out / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (out / 'independent_helper_snapshot.py').write_bytes((ROOT / 'src/six_hour/review_reference_selector.py').read_bytes())
    print(json.dumps(dict(checks=summary['checks_total'], passed=summary['checks_passed'], failures=len(errors), seconds=summary['elapsed_seconds'], exact_tie_conditions=summary['linear_conditions_with_exact_ties'])))


if __name__ == '__main__':
    main()
