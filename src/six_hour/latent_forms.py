"""Reference-only categorical mixture fitting and symbol-map EM assignment."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.special import logsumexp

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/latent-forms'
SOURCE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms'
K, M, LENGTH = 20, 3, 6
VARIANTS = ['same_length_0', 'same_length_35', 'same_length_70']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def expectation(rows, pi, theta):
    a = np.asarray(rows, dtype=np.int64)
    log_weights = np.log(pi)[None, :] + np.log(theta)[:, np.arange(LENGTH)[None, :], a].sum(axis=2).T
    normalizers = logsumexp(log_weights, axis=1)
    responsibilities = np.exp(log_weights - normalizers[:, None])
    return float(normalizers.sum()), responsibilities


def weighted_counts(rows, responsibilities):
    a = np.asarray(rows, dtype=np.int64)
    positions = (a + K * np.arange(LENGTH)[None, :]).ravel()
    return np.asarray([np.bincount(positions, weights=np.repeat(responsibilities[:, z], LENGTH), minlength=K * LENGTH).reshape(LENGTH, K) for z in range(M)])


def maximization(rows, responsibilities):
    totals = responsibilities.sum(axis=0)
    counts = weighted_counts(rows, responsibilities)
    return (totals + 1) / (len(rows) + M), (counts + 1) / (totals[:, None, None] + K)


def penalized(likelihood, pi, theta):
    return float(likelihood + np.log(pi).sum() + np.log(theta).sum())


def fit_reference(rows, seed):
    a = np.asarray(rows, dtype=np.int64)
    marginal = np.asarray([(np.bincount(a[:, j], minlength=K) + 1) / (len(a) + K) for j in range(LENGTH)])
    exemplars = [0]
    for _ in range(M - 1):
        distances = np.min(np.stack([np.sum(a != a[index], axis=1) for index in exemplars]), axis=0)
        exemplars.append(int(np.argmax(distances)))
    initializations = [('marginal', np.full(M, 1 / M), np.repeat(marginal[None, :, :], M, axis=0))]
    exemplar_theta = np.asarray([.2 * marginal + .8 * np.eye(K)[a[index]] for index in exemplars])
    initializations.append(('farthest_records', np.full(M, 1 / M), exemplar_theta))
    for start in range(2, 8):
        order = np.random.default_rng(seed + start).permutation(len(a))
        labels = np.empty(len(a), dtype=int)
        labels[order] = np.arange(len(a)) % M
        r = np.eye(M)[labels]
        pi, theta = maximization(a, r)
        initializations.append((f'partition_{start}', pi, theta))
    fits = []
    for start, (name, pi, theta) in enumerate(initializations):
        initial_pi, initial_theta = pi.copy(), theta.copy()
        likelihood, r = expectation(a, pi, theta)
        objective = penalized(likelihood, pi, theta)
        trace = [dict(iteration=0, likelihood=likelihood, penalized_objective=objective)]
        stop = 'iteration_budget'
        for iteration in range(1, 151):
            prior_pi, prior_theta = pi.copy(), theta.copy()
            previous = objective
            pi, theta = maximization(a, r)
            likelihood, r = expectation(a, pi, theta)
            objective = penalized(likelihood, pi, theta)
            delta = objective - previous
            if delta < -1e-7:
                raise RuntimeError(f'Reference MAP objective decreased: {delta}')
            trace.append(dict(iteration=iteration, likelihood=likelihood, penalized_objective=objective))
            if delta <= 1e-8 * (1 + abs(previous)):
                stop = 'relative_objective_tolerance'
                break
        fits.append(dict(start=start, name=name, iterations=iteration, stop=stop, initial_pi=initial_pi.tolist(),
                         initial_theta=initial_theta.tolist(), last_input_pi=prior_pi.tolist(), last_input_theta=prior_theta.tolist(),
                         pi=pi.tolist(), theta=theta.tolist(), likelihood=likelihood, penalized_objective=objective, trace=trace))
    chosen = max(range(len(fits)), key=lambda index: fits[index]['penalized_objective'])
    return dict(fit_seed=seed, component_count=M, chosen_start=chosen, starts=fits,
                pi=fits[chosen]['pi'], theta=fits[chosen]['theta'])


def mixture_score(rows, mapping, model):
    decoded = np.asarray(mapping)[np.asarray(rows, dtype=np.int64)]
    return expectation(decoded, np.asarray(model['pi']), np.asarray(model['theta']))[0]


def map_records(rows, reference, model, slot_map, graph_map, seed):
    a = np.asarray(rows, dtype=np.int64)
    pi, theta = np.asarray(model['pi']), np.asarray(model['theta'])
    code_counts = np.bincount(a.ravel(), minlength=K)
    ref_counts = np.bincount(np.asarray(reference).ravel(), minlength=K)
    _, frequency = linear_sum_assignment(code_counts[:, None] * np.log((ref_counts + 1) / (ref_counts.sum() + K))[None, :], maximize=True)
    starts = [('slot', np.asarray(slot_map)), ('graph', np.asarray(graph_map)), ('frequency', frequency),
              ('identity', np.arange(K)), ('reversal', np.arange(K)[::-1])]
    starts += [(f'random_{index}', np.random.default_rng(seed + 200 + index).permutation(K)) for index in range(6)]
    records, candidates, seen_initial = [], [], set()
    for name, initial in starts:
        marker = tuple(initial.tolist())
        initial_score = mixture_score(a, initial, model)
        candidates.append(dict(mapping=initial.tolist(), likelihood=initial_score, origin=name + '/initial'))
        if marker in seen_initial:
            records.append(dict(name=name, initial_mapping=initial.tolist(), initial_likelihood=initial_score, duplicate_initial=True, trace=[]))
            continue
        seen_initial.add(marker)
        mapping = initial.copy()
        visited = {marker}
        trace = []
        stop = 'iteration_budget'
        for step in range(1, 26):
            likelihood, r = expectation(mapping[a], pi, theta)
            counts = weighted_counts(a, r)
            weights = np.einsum('zjc,zjr->cr', counts, np.log(theta))
            _, candidate = linear_sum_assignment(weights, maximize=True)
            old_q = float(weights[np.arange(K), mapping].sum())
            new_q = float(weights[np.arange(K), candidate].sum())
            next_likelihood = mixture_score(a, candidate, model)
            if new_q < old_q - 1e-7 or next_likelihood < likelihood - 1e-7:
                raise RuntimeError('Mapping assignment failed its Q/likelihood ascent check.')
            trace.append(dict(step=step, previous_mapping=mapping.tolist(), mapping=candidate.tolist(),
                              previous_likelihood=likelihood, likelihood=next_likelihood, previous_q=old_q, assignment_q=new_q,
                              responsibility_totals=r.sum(axis=0).tolist(), responsibility_entropy=float(-(r * np.log(r)).sum())))
            candidates.append(dict(mapping=candidate.tolist(), likelihood=next_likelihood, origin=f'{name}/step{step}'))
            marker = tuple(candidate.tolist())
            mapping = candidate
            if marker in visited:
                stop = 'repeated_map'
                break
            visited.add(marker)
        records.append(dict(name=name, initial_mapping=initial.tolist(), initial_likelihood=initial_score,
                            duplicate_initial=False, stop=stop, trace=trace))
    best = max(candidates, key=lambda candidate: candidate['likelihood'])
    ties = {}
    for candidate in candidates:
        if abs(candidate['likelihood'] - best['likelihood']) <= 1e-8:
            ties[tuple(candidate['mapping'])] = candidate
    return dict(mapping=best['mapping'], likelihood=best['likelihood'], winning_origin=best['origin'],
                candidate_ties=list(ties.values()), starts=records, candidates=candidates, mapping_seed=seed)


def main(args):
    output = BASE / args.endpoint
    if output.exists():
        raise RuntimeError('Preserve earlier endpoints.')
    output.mkdir(parents=True)
    source_folder = SOURCE / ('pilot-v1' if args.pilot else 'main-v1')
    worlds_path, results_path = source_folder / 'worlds.json', source_folder / 'results.json'
    frozen = dict(created_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=digest(BASE / 'PROTOCOL.md'),
                  code_sha256=digest(Path(__file__)), source_hashes={p.relative_to(ROOT).as_posix(): digest(p) for p in (worlds_path, results_path)})
    write(output / 'execution-freeze.json', frozen)
    (output / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    started = time.perf_counter()
    source = json.loads(results_path.read_text())
    all_worlds = json.loads(worlds_path.read_text())
    variants = ['same_length_0', 'same_length_70'] if args.pilot else VARIANTS
    worlds = [w for w in all_worlds if w['variant'] in variants]
    seeds = sorted({w['seed'] for w in worlds})
    model_records, choices, mappings, outcomes = [], [], [], []
    models = {}
    for replicate, system_seed in enumerate(seeds):
        for vi, variant in enumerate(VARIANTS):
            if variant not in variants:
                continue
            world = next(w for w in worlds if w['seed'] == system_seed and w['variant'] == variant and w['shift'] == 0.)
            for ri, size in enumerate([40] if args.pilot else [40, 400]):
                reference = world['reference'][:size]
                old_choice = next(c for c in source['choices'] if c['seed'] == system_seed and c['variant'] == variant and c['reference_records'] == size)
                fit_seed = 1310261002 + 1000 * replicate + 100 * vi + 10 * ri
                fitted = fit_reference(reference, fit_seed)
                models[system_seed, variant, size] = fitted
                model_records.append(dict(seed=system_seed, variant=variant, reference_records=size, stage='full_reference', **fitted))
                folds = old_choice['folds']
                mixture_scores = []
                for fold in range(3):
                    train = [row for i, row in enumerate(reference) if folds[i] != fold]
                    test = [row for i, row in enumerate(reference) if folds[i] == fold]
                    fold_model = fit_reference(train, fit_seed + 100000 + 100 * fold)
                    score = mixture_score(test, np.arange(K), fold_model) / np.log(2)
                    mixture_scores.append(score)
                    model_records.append(dict(seed=system_seed, variant=variant, reference_records=size, stage='reference_fold', fold=fold, **fold_model))
                scores = dict(graph_multistart=old_choice['graph_score'], length_slot=old_choice['slot_score'], latent_mixture=sum(mixture_scores))
                chosen = max(scores, key=scores.get)
                choices.append(dict(seed=system_seed, variant=variant, reference_records=size, scores=scores, selected=chosen,
                                    mixture_fold_scores=mixture_scores, folds=folds))
                for si, shift in enumerate([0.] if args.pilot else [0., .35]):
                    case = next(w for w in worlds if w['seed'] == system_seed and w['variant'] == variant and w['shift'] == shift)
                    existing = [r for r in source['rows'] if r['seed'] == system_seed and r['variant'] == variant and r['shift'] == shift and r['reference_records'] == size]
                    base = {r['algorithm']: r for r in existing}
                    map_seed = 1410261002 + 1000 * replicate + 100 * vi + 10 * si + ri
                    fitted_map = map_records(case['training'], reference, fitted, base['length_slot']['mapping'], base['graph_multistart']['mapping'], map_seed)
                    condition = dict(seed=system_seed, variant=variant, reference_records=size, shift=shift)
                    mappings.append(dict(**condition, **fitted_map))
                    maps = {name: row['mapping'] for name, row in base.items()}
                    maps['latent_mixture'] = fitted_map['mapping']
                    maps['reference_selected_three'] = maps[chosen]
                    tokens = sum(map(len, case['heldout']))
                    for method, mapping in maps.items():
                        outcomes.append(dict(**condition, algorithm=method, mapping=mapping,
                                             exact_recovery=mapping == case['truth'], symbol_accuracy=sum(a == b for a, b in zip(mapping, case['truth'])) / K,
                                             mixture_train_log2=mixture_score(case['training'], mapping, fitted) / np.log(2),
                                             mixture_heldout_bits_per_token=-mixture_score(case['heldout'], mapping, fitted) / (tokens * np.log(2)),
                                             three_model_reference_choice=chosen))
            print(json.dumps(dict(seed=system_seed, variant=variant, completed_conditions=len(mappings))), flush=True)
    payload = dict(**frozen, completed_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                   status='separate-pilot-world-reuse' if args.pilot else 'post-outcome-frozen-world-model-comparison',
                   component_count_prior=M, models=model_records, choices=choices, mapping_runs=mappings, rows=outcomes)
    write(output / 'results.json', payload)
    print(json.dumps(dict(conditions=len(mappings), rows=len(outcomes), reference_fits=len(model_records), seconds=payload['elapsed_seconds'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--endpoint', required=True)
    main(parser.parse_args())
