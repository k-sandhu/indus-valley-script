"""Scalar Bayes, terminal MAP-EM and every mapping-assignment dual audit."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import time

import numpy as np

from review_reference_selector import Model, dual_certificate

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/latent-forms'
SOURCE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms/main-v1'
K, M, LENGTH = 20, 3, 6


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


class ScalarMixture:
    def __init__(self, pi, theta):
        self.pi, self.theta = pi, theta
        self.log_pi = [math.log(p) for p in pi]
        self.log_theta = [[[math.log(p) for p in slot] for slot in form] for form in theta]

    def expectation(self, rows, mapping=None):
        mapping = list(range(K)) if mapping is None else mapping
        cache = {}
        responsibilities, contributions = [], []
        for row in rows:
            decoded = tuple(mapping[c] for c in row)
            if decoded not in cache:
                logs = [math.fsum([self.log_pi[z]] + [self.log_theta[z][j][c] for j, c in enumerate(decoded)]) for z in range(M)]
                peak = max(logs)
                scaled = [math.exp(value - peak) for value in logs]
                norm = math.fsum(scaled)
                likelihood = peak + math.log(norm)
                cache[decoded] = likelihood, [value / norm for value in scaled]
            likelihood, r = cache[decoded]
            contributions.append(likelihood)
            responsibilities.append(r)
        return math.fsum(contributions), np.asarray(responsibilities)

    def penalty(self, likelihood):
        return math.fsum([likelihood] + self.log_pi + [p for form in self.log_theta for slot in form for p in slot])


def scalar_counts(rows, responsibilities):
    counts = np.zeros((M, LENGTH, K))
    for row, r in zip(rows, responsibilities):
        for j, c in enumerate(row):
            for z in range(M):
                counts[z, j, c] += r[z]
    return counts


def scalar_update(rows, r):
    totals = [math.fsum(float(row[z]) for row in r) for z in range(M)]
    counts = scalar_counts(rows, r)
    pi = [(n + 1) / (len(rows) + M) for n in totals]
    theta = [[[(counts[z, j, c] + 1) / (totals[z] + K) for c in range(K)] for j in range(LENGTH)] for z in range(M)]
    return np.asarray(pi), np.asarray(theta)


def scalar_weights(rows, r, log_theta):
    counts = scalar_counts(rows, r)
    return np.asarray([[math.fsum(counts[z, j, c] * log_theta[z][j][target] for z in range(M) for j in range(LENGTH)) for target in range(K)] for c in range(K)])


def exact_normalization():
    pi = [Fraction(1, 3), Fraction(2, 3)]
    theta = [[[Fraction(1, 4), Fraction(3, 4)], [Fraction(1, 2), Fraction(1, 2)]],
             [[Fraction(4, 5), Fraction(1, 5)], [Fraction(2, 3), Fraction(1, 3)]]]
    total = Fraction(0)
    for row in product(range(2), repeat=2):
        terms = [pi[z] * theta[z][0][row[0]] * theta[z][1][row[1]] for z in range(2)]
        probability = sum(terms)
        assert sum(term / probability for term in terms) == 1
        total += probability
    return str(total)


def main():
    out = BASE / 'review-v1'
    if out.exists():
        raise RuntimeError('Preserve prior endpoints.')
    out.mkdir()
    start = time.perf_counter()
    files = list((BASE / 'main-v1').iterdir()) + [SOURCE / 'results.json', SOURCE / 'worlds.json']
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in files if p.is_file()}
    result = json.loads((BASE / 'main-v1/results.json').read_text())
    source = json.loads((SOURCE / 'results.json').read_text())
    worlds = json.loads((SOURCE / 'worlds.json').read_text())
    lookup = {(w['seed'], w['variant'], w['shift']): w for w in worlds}
    choices = {(c['seed'], c['variant'], c['reference_records']): c for c in result['choices']}
    model_lookup = {}
    for model in result['models']:
        key = model['seed'], model['variant'], model['reference_records'], model['stage'], model.get('fold', -1)
        model_lookup[key] = model
    checks, failures = [], []
    maxima = defaultdict(float)

    def check(name, passed, details=None):
        checks.append(dict(check=name, passed=bool(passed), details=details))
        if not passed:
            failures.append(checks[-1])

    def close(name, actual, saved, tol=1e-7):
        error = abs(float(actual) - float(saved))
        maxima[name] = max(maxima[name], error)
        check(name, error <= tol, dict(error=error) if error > tol else None)

    check('main dimensions', len(result['models']) == 288 and len(result['choices']) == 72 and len(result['mapping_runs']) == 144 and len(result['rows']) == 864)
    check('exact rational mixture normalization', exact_normalization() == '1')
    check('protocol and source snapshot', result['protocol_sha256'] == digest(BASE / 'PROTOCOL.md') and result['code_sha256'] == digest(BASE / 'main-v1/code_snapshot.py'))
    for path, sha in result['source_hashes'].items():
        check('reused source hash ' + path, digest(ROOT / path) == sha)
    raw_fit_decreases = 0
    fit_budget_stops = 0
    separation = []
    for mi, model in enumerate(result['models']):
        key = model['seed'], model['variant'], model['reference_records']
        reference = lookup[key[0], key[1], 0.]['reference'][:key[2]]
        if model['stage'] == 'reference_fold':
            fold = model['fold']
            reference = [row for i, row in enumerate(reference) if choices[key]['folds'][i] != fold]
        check('all eight reference starts retained', len(model['starts']) == 8)
        penalties = []
        for fit in model['starts']:
            initial = ScalarMixture(fit['initial_pi'], fit['initial_theta'])
            initial_ll, _ = initial.expectation(reference)
            close('initial reference likelihood', initial_ll, fit['trace'][0]['likelihood'])
            close('initial MAP objective', initial.penalty(initial_ll), fit['trace'][0]['penalized_objective'])
            preceding = ScalarMixture(fit['last_input_pi'], fit['last_input_theta'])
            preceding_ll, responsibilities = preceding.expectation(reference)
            close('terminal preceding likelihood', preceding_ll, fit['trace'][-2]['likelihood'])
            predicted_pi, predicted_theta = scalar_update(reference, responsibilities)
            close('terminal mixture M update maximum error', np.max(abs(predicted_pi - fit['pi'])), 0., 1e-10)
            close('terminal categorical M update maximum error', np.max(abs(predicted_theta - fit['theta'])), 0., 1e-10)
            final = ScalarMixture(fit['pi'], fit['theta'])
            final_ll, final_r = final.expectation(reference)
            close('final reference likelihood', final_ll, fit['likelihood'])
            penalty = final.penalty(final_ll)
            close('final MAP objective', penalty, fit['penalized_objective'])
            penalties.append(penalty)
            check('all reported MAP steps ascend', all(b['penalized_objective'] >= a['penalized_objective'] - 1e-7 for a, b in zip(fit['trace'], fit['trace'][1:])))
            check('reference responsibilities normalize', np.max(abs(final_r.sum(axis=1) - 1)) < 1e-12)
            last_delta = fit['trace'][-1]['penalized_objective'] - fit['trace'][-2]['penalized_objective']
            if fit['stop'] == 'relative_objective_tolerance':
                check('reference stopping threshold', last_delta <= 1e-8 * (1 + abs(fit['trace'][-2]['penalized_objective'])))
            else:
                check('reference iteration budget', fit['iterations'] == 150)
                fit_budget_stops += 1
            raw_fit_decreases += sum(b['likelihood'] < a['likelihood'] - 1e-7 for a, b in zip(fit['trace'], fit['trace'][1:]))
        selected = model['chosen_start']
        check('reference choice maximizes reported MAP score', selected == max(range(8), key=lambda i: model['starts'][i]['penalized_objective']))
        check('reference choice independently reaches best retained MAP score', penalties[selected] >= max(penalties) - 1e-7)
        check('chosen parameter fields match retained start', model['pi'] == model['starts'][selected]['pi'] and model['theta'] == model['starts'][selected]['theta'])
        if model['stage'] == 'full_reference':
            theta = np.asarray(model['theta'])
            distance = max(float(abs(theta[a] - theta[b]).sum(axis=1).max()) for a in range(M) for b in range(a))
            separation.append(dict(seed=key[0], variant=key[1], reference_records=key[2], maximum_slot_component_l1=distance,
                                   mixture_weights=model['pi'], chosen_start=selected))
        if mi % 48 == 0:
            print(json.dumps(dict(reviewed_reference_models=mi + 1)), flush=True)
    reviewed_choices = []
    for key, choice in choices.items():
        reference = lookup[key[0], key[1], 0.]['reference'][:key[2]]
        order = np.random.default_rng(key[0] + 50).permutation(key[2])
        folds = [0] * len(reference)
        for i, index in enumerate(order):
            folds[index] = i % 3
        check('reference folds reproduced', folds == choice['folds'])
        scores = defaultdict(float)
        for fold in range(3):
            training = [row for i, row in enumerate(reference) if folds[i] != fold]
            heldout = [row for i, row in enumerate(reference) if folds[i] == fold]
            saved = model_lookup[key + ('reference_fold', fold)]
            fitted = ScalarMixture(saved['pi'], saved['theta'])
            mixture_score = fitted.expectation(heldout)[0] / math.log(2)
            close('mixture reference fold score', mixture_score, choice['mixture_fold_scores'][fold])
            scores['latent_mixture'] += mixture_score
            ordinary = Model(training, K)
            scores['length_slot'] += ordinary.slot(heldout, list(range(K)))
            scores['graph_multistart'] += ordinary.graph_conditional(heldout, list(range(K)))
        for name, actual in scores.items():
            close('pooled reference ' + name, actual, choice['scores'][name])
        ranked = ['graph_multistart', 'length_slot', 'latent_mixture']
        selected = max(ranked, key=lambda name: scores[name])
        check('three-model reference selection', selected == choice['selected'])
        reviewed_choices.append(dict(seed=key[0], variant=key[1], reference_records=key[2], selected=selected, scores=dict(scores)))
    mapping_lookup = {}
    certificates, objective_checks = [], []
    total_steps = 0
    minimum_bound_residual = float('inf')
    for ci, run in enumerate(result['mapping_runs']):
        key = run['seed'], run['variant'], run['shift'], run['reference_records']
        world = lookup[key[:3]]
        saved = model_lookup[(key[0], key[1], key[3], 'full_reference', -1)]
        model = ScalarMixture(saved['pi'], saved['theta'])
        mapping_lookup[key] = model
        check('eleven named initial candidates retained', len(run['starts']) == 11)
        for initial in run['starts']:
            score, _ = model.expectation(world['training'], initial['initial_mapping'])
            close('mapping initial likelihood', score, initial['initial_likelihood'])
            check('mapping update budget', len(initial['trace']) <= 25)
            for trace in initial['trace']:
                total_steps += 1
                old_ll, r = model.expectation(world['training'], trace['previous_mapping'])
                new_ll, _ = model.expectation(world['training'], trace['mapping'])
                close('mapping previous likelihood', old_ll, trace['previous_likelihood'])
                close('mapping next likelihood', new_ll, trace['likelihood'])
                close('responsibility total maximum error', np.max(abs(r.sum(axis=0) - trace['responsibility_totals'])), 0., 1e-8)
                entropy = math.fsum(-float(value) * math.log(float(value)) for row in r for value in row)
                close('responsibility entropy', entropy, trace['responsibility_entropy'])
                w = scalar_weights(world['training'], r, model.log_theta)
                old_q = math.fsum(w[c, trace['previous_mapping'][c]] for c in range(K))
                new_q = math.fsum(w[c, trace['mapping'][c]] for c in range(K))
                close('previous assignment Q', old_q, trace['previous_q'])
                close('selected assignment Q', new_q, trace['assignment_q'])
                cert = dual_certificate(w, trace['mapping'])
                check('mapping assignment independent dual', cert['success'] and abs(cert['gap']) <= 1e-7 and cert['minimum_slack'] > -1e-7)
                certificates.append(dict(condition=list(key), initial=initial['name'], step=trace['step'], **cert))
                residual = new_ll - old_ll - (new_q - old_q)
                minimum_bound_residual = min(minimum_bound_residual, residual)
                check('actual mapping ascent and EM lower bound', new_ll >= old_ll - 1e-7 and new_q >= old_q - 1e-7 and residual >= -1e-7)
        best = max(run['candidates'], key=lambda candidate: candidate['likelihood'])
        check('best initial and intermediate candidate retained', run['mapping'] == best['mapping'] and run['likelihood'] == best['likelihood'])
        check('candidate ties retained', {tuple(c['mapping']) for c in run['candidate_ties']} == {tuple(c['mapping']) for c in run['candidates'] if abs(c['likelihood'] - best['likelihood']) <= 1e-8})
        returned, _ = model.expectation(world['training'], run['mapping'])
        truth, _ = model.expectation(world['training'], world['truth'])
        objective_checks.append(dict(condition=list(key), recovered=run['mapping'] == world['truth'], returned_minus_truth_nats=returned - truth,
                                     candidate_ties=len(run['candidate_ties'])))
        if ci % 24 == 0:
            print(json.dumps(dict(reviewed_mapping_conditions=ci + 1, assignment_steps=total_steps)), flush=True)
    outcome_lookup = {(r['seed'], r['variant'], r['shift'], r['reference_records'], r['algorithm']): r for r in result['rows']}
    source_lookup = {(r['seed'], r['variant'], r['shift'], r['reference_records'], r['algorithm']): r for r in source['rows']}
    reviewed_rows = []
    ordinary_models = {}
    for row in result['rows']:
        key = row['seed'], row['variant'], row['shift'], row['reference_records']
        world = lookup[key[:3]]
        mapping = row['mapping']
        model = mapping_lookup[key]
        check('returned map bijective', sorted(mapping) == list(range(K)))
        check('truth opened only for reported accuracy', row['exact_recovery'] == (mapping == world['truth']) and row['symbol_accuracy'] == sum(a == b for a, b in zip(mapping, world['truth'])) / K)
        if row['algorithm'] in ('length_slot', 'graph_multistart', 'reference_selected', 'form_observed_slot'):
            check('frozen comparator map preserved', mapping == source_lookup[key + (row['algorithm'],)]['mapping'])
        elif row['algorithm'] == 'reference_selected_three':
            chosen = choices[key[0], key[1], key[3]]['selected']
            check('new selector uses chosen returned map', mapping == outcome_lookup[key + (chosen,)]['mapping'])
        train_score = model.expectation(world['training'], mapping)[0] / math.log(2)
        tokens = sum(map(len, world['heldout']))
        test_loss = -model.expectation(world['heldout'], mapping)[0] / (tokens * math.log(2))
        close('mixture train log2', train_score, row['mixture_train_log2'])
        close('mixture test loss', test_loss, row['mixture_heldout_bits_per_token'], 1e-9)
        ordinary_key = key[0], key[1], key[3]
        if ordinary_key not in ordinary_models:
            ordinary_models[ordinary_key] = Model(world['reference'][:key[3]], K)
        ordinary = ordinary_models[ordinary_key]
        reviewed_rows.append(dict(**row, slot_heldout_bits_per_token=-ordinary.slot(world['heldout'], mapping) / tokens,
                                  graph_conditional_heldout_bits_per_token=-ordinary.graph_conditional(world['heldout'], mapping) / tokens))
    aggregates = []
    methods = sorted({r['algorithm'] for r in reviewed_rows})
    for variant in ('same_length_0', 'same_length_35', 'same_length_70'):
        for size in (40, 400):
            for method in methods:
                group = [r for r in reviewed_rows if r['variant'] == variant and r['reference_records'] == size and r['algorithm'] == method]
                aggregates.append(dict(variant=variant, reference_records=size, algorithm=method, conditions=len(group),
                                       complete_recovery=sum(r['exact_recovery'] for r in group),
                                       mean_symbol_accuracy=math.fsum(r['symbol_accuracy'] for r in group) / len(group),
                                       mean_mixture_heldout_bits_per_token=math.fsum(r['mixture_heldout_bits_per_token'] for r in group) / len(group),
                                       mean_slot_heldout_bits_per_token=math.fsum(r['slot_heldout_bits_per_token'] for r in group) / len(group),
                                       mean_graph_conditional_heldout_bits_per_token=math.fsum(r['graph_conditional_heldout_bits_per_token'] for r in group) / len(group)))
    seeds = sorted({r['seed'] for r in reviewed_rows})
    draws = np.random.default_rng(1510261002).integers(0, 12, (20000, 12))
    paired = []
    for variant in ('same_length_0', 'same_length_35', 'same_length_70'):
        for method, comparator in [('latent_mixture', 'reference_selected'), ('reference_selected_three', 'reference_selected'), ('latent_mixture', 'form_observed_slot')]:
            for metric in ('exact_recovery', 'symbol_accuracy'):
                delta = []
                for seed in seeds:
                    means = {name: math.fsum(float(r[metric]) for r in reviewed_rows if r['variant'] == variant and r['seed'] == seed and r['algorithm'] == name) / 4 for name in (method, comparator)}
                    delta.append(means[method] - means[comparator])
                differences = np.asarray(delta)
                paired.append(dict(variant=variant, algorithm=method, comparator=comparator, metric=metric,
                                   mean_difference=float(differences.mean()), percentile_95_interval=np.quantile(differences[draws].mean(axis=1), [.025, .975]).tolist(),
                                   system_differences=delta, systems=12, conditions_per_system=4, bootstrap_draws=20000, bootstrap_seed=1510261002))
    check('all frozen inputs preserved', all(digest(ROOT / path) == sha for path, sha in hashes.items()))
    summary = dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks), failures=failures,
                   elapsed_seconds=time.perf_counter() - start, source_hashes=hashes, protocol_sha256=digest(BASE / 'REVIEW_PROTOCOL.md'),
                   code_sha256=digest(Path(__file__)), mapping_assignments_checked=total_steps, minimum_EM_bound_residual_nats=minimum_bound_residual,
                   max_scalar_errors=dict(maxima), reference_iteration_budget_stops=fit_budget_stops,
                   reported_raw_reference_likelihood_decreases=raw_fit_decreases, aggregates=aggregates,
                   choice_counts=dict(Counter(f"{c['variant']}/{c['reference_records']}/{c['selected']}" for c in reviewed_choices)))
    for name, value in [('verification.json', summary), ('checks.json', checks), ('reviewed-rows.json', reviewed_rows), ('reference-choices.json', reviewed_choices),
                        ('assignment-duals.json', certificates), ('paired-comparisons.json', paired), ('objective-diagnostics.json', objective_checks), ('component-separation.json', separation)]:
        write(out / name, value)
    (out / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (out / 'independent_helper_snapshot.py').write_bytes((ROOT / 'src/six_hour/review_reference_selector.py').read_bytes())
    print(json.dumps(dict(checks=summary['checks_total'], passed=summary['checks_passed'], failures=len(failures), seconds=summary['elapsed_seconds'], assignments=total_steps)))


if __name__ == '__main__':
    main()
