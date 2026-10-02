"""Short-record bijection search as a boundary-seeded quadratic assignment."""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import permutations
import json
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.optimize import linear_sum_assignment, quadratic_assignment

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/graph-mapping'


def system(seed, family, k):
    rng = np.random.default_rng(seed)
    initial = rng.dirichlet(np.full(k, .6))
    transition = rng.dirichlet(np.full(k, .35), size=k)
    pools = np.array_split(rng.permutation(k), 4)
    slot_probs = []
    patterns = [[0, 1, 2, 3], [0, 2, 1, 2, 3], [1, 0, 2, 1, 2, 3]]
    for pattern in patterns:
        probs = []
        for pool_index in pattern:
            p = np.zeros(k)
            p[pools[pool_index]] = rng.dirichlet(np.full(len(pools[pool_index]), .7))
            probs.append(p)
        slot_probs.append(probs)
    return {'family': family, 'k': k, 'initial': initial, 'transition': transition,
            'forms': slot_probs, 'mixture': rng.dirichlet(np.ones(3))}


def sample(spec, n, seed, shift=0):
    rng = np.random.default_rng(seed)
    k = spec['k']
    rows = []
    for _ in range(n):
        if spec['family'] == 'transition':
            length = int(rng.integers(3, 9))
            initial = (1-shift)*spec['initial'] + shift*np.roll(spec['initial'], 1)
            row = [int(rng.choice(k, p=initial))]
            for _ in range(length-1):
                p = (1-shift)*spec['transition'][row[-1]] + shift*np.roll(spec['transition'][row[-1]], 1)
                row.append(int(rng.choice(k, p=p)))
        else:
            mixture = (1-shift)*spec['mixture'] + shift*np.roll(spec['mixture'], 1)
            form = spec['forms'][int(rng.choice(3, p=mixture))]
            row = [int(rng.choice(k, p=p)) for p in form]
        rows.append(row)
    return rows


def counts(rows, k):
    matrix = np.zeros((k+2, k+2), dtype=np.int64)
    unigrams = np.zeros(k, dtype=np.int64)
    for row in rows:
        matrix[k, row[0]] += 1
        for a, b in zip(row, row[1:]):
            matrix[a, b] += 1
        matrix[row[-1], k+1] += 1
        for value in row:
            unigrams[value] += 1
    return matrix, unigrams


def reference_matrix(matrix, k):
    logp = np.zeros((k+2, k+2))
    destinations = list(range(k)) + [k+1]
    for i in range(k):
        row = matrix[i, destinations] + 1
        logp[i, destinations] = np.log2(row/row.sum())
    initial = matrix[k, :k] + 1
    logp[k, :k] = np.log2(initial/initial.sum())
    return logp


def score(matrix, logp, mapping):
    return float(np.sum(matrix*logp[np.ix_(mapping, mapping)]))


def direct_score(rows, logp, mapping, k):
    value = 0.
    for row in rows:
        decoded = [mapping[v] for v in row]
        value += logp[k, decoded[0]]
        for a, b in zip(decoded, decoded[1:]):
            value += logp[a, b]
        value += logp[decoded[-1], k+1]
    return float(value)


def exact_scores(matrix, logp, k):
    maps = np.asarray([list(p)+[k, k+1] for p in permutations(range(k))], dtype=np.int16)
    values = np.zeros(len(maps))
    for i, j in zip(*np.nonzero(matrix)):
        values += matrix[i, j]*logp[maps[:, i], maps[:, j]]
    index = int(np.argmax(values))
    return maps[index], float(values[index]), int(np.sum(np.abs(values-values[index]) < 1e-8))


def fit(matrix, logp, train_uni, ref_uni, k, seed):
    t0 = time.perf_counter()
    _, perm = linear_sum_assignment(train_uni[:, None]*np.log2((ref_uni+1)/(ref_uni.sum()+k))[None, :], maximize=True)
    frequency = np.r_[perm, k, k+1]
    outputs = [{'algorithm': 'frequency', 'mapping': frequency, 'seconds': time.perf_counter()-t0}]
    fixed = np.array([[k, k], [k+1, k+1]])
    candidates = [frequency]
    faq_candidates = []
    for name, initial in [('faq_barycenter', 'barycenter'), ('faq_frequency', np.eye(k)[perm])]:
        t1 = time.perf_counter()
        result = quadratic_assignment(matrix, logp, options={'maximize': True, 'partial_match': fixed,
            'rng': np.random.default_rng(seed), 'P0': initial, 'maxiter': 100, 'tol': .0001})
        assert np.array_equal(result.col_ind[-2:], [k, k+1])
        assert abs(score(matrix, logp, result.col_ind)-result.fun) < 1e-7
        faq_candidates.append(result.col_ind)
        outputs.append({'algorithm': name, 'mapping': result.col_ind, 'seconds': time.perf_counter()-t1})
    multistart_begin = time.perf_counter()
    faq_candidates += [quadratic_assignment(matrix, logp, options={'maximize': True, 'partial_match': fixed,
        'rng': np.random.default_rng(seed+100+restart), 'P0': 'randomized', 'maxiter': 100, 'tol': .0001}).col_ind for restart in range(10)]
    candidates += faq_candidates
    for restart, candidate in enumerate(faq_candidates):
        refined = quadratic_assignment(matrix, logp, method='2opt', options={'maximize': True, 'partial_match': fixed,
            'rng': np.random.default_rng(seed+1000+restart), 'partial_guess': np.column_stack((np.arange(k+2), candidate))})
        assert np.array_equal(refined.col_ind[-2:], [k, k+1])
        candidates.append(refined.col_ind)
    best = max(candidates, key=lambda p: score(matrix, logp, p))
    outputs.append({'algorithm': 'multistart_refined', 'mapping': best,
        'seconds': time.perf_counter()-multistart_begin+sum(o['seconds'] for o in outputs[1:])})
    return outputs


def run(args):
    out = ROOT / args.output
    if out.exists():
        raise RuntimeError('Use a fresh endpoint.')
    started = time.perf_counter()
    records = []
    inputs = []
    reps = 1 if args.pilot else 12
    ref_sizes = [40] if args.pilot else [40, 400]
    train_sizes = [160] if args.pilot else [160, 640]
    for ki, k in enumerate([8, 20]):
        for fi, family in enumerate(['transition', 'administrative_form']):
            for replicate in range(reps):
                seed = 710261002+1000000*ki+100000*fi+1000*replicate
                spec = system(seed, family, k)
                reference = sample(spec, 400, seed+1)
                encoding = np.random.default_rng(seed+4).permutation(k)
                truth = np.r_[np.argsort(encoding), k, k+1]
                for shift_index, shift in enumerate([0, .35]):
                    training = [[int(encoding[v]) for v in row] for row in sample(spec, 640, seed+2, shift)]
                    heldout = [[int(encoding[v]) for v in row] for row in sample(spec, 400, seed+3, shift)]
                    hmatrix, _ = counts(heldout, k)
                    for ri, ref_size in enumerate(ref_sizes):
                        ref_matrix, ref_uni = counts(reference[:ref_size], k)
                        logp = reference_matrix(ref_matrix, k)
                        for ti, train_size in enumerate(train_sizes):
                            matrix, uni = counts(training[:train_size], k)
                            solver_seed = 720000000+ki*1000000+fi*100000+replicate*1000+shift_index*100+ri*10+ti
                            fitted = fit(matrix, logp, uni, ref_uni, k, solver_seed)
                            exact_map, optimum, ties = exact_scores(matrix, logp, k) if k == 8 else (None, None, None)
                            truth_score = score(matrix, logp, truth)
                            case = {'family': family, 'k': k, 'seed': seed, 'reference_records': ref_size,
                                'training_records': train_size, 'shift': shift, 'solver_seed': solver_seed}
                            inputs.append({**case, 'truth': truth.tolist(), 'training_counts': matrix.tolist(),
                                'reference_counts': ref_matrix.tolist(), 'training_unigrams': uni.tolist(),
                                'reference_unigrams': ref_uni.tolist(), 'heldout_counts': hmatrix.tolist(),
                                'exact_map': None if exact_map is None else exact_map.tolist(), 'global_score': optimum,
                                'global_ties': ties, 'truth_score': truth_score,
                                'truth_global': None if optimum is None else abs(truth_score-optimum) < 1e-8,
                                'unobserved_training_codes': np.flatnonzero(uni == 0).tolist()})
                            for item in fitted:
                                mapping = item['mapping']
                                objective = score(matrix, logp, mapping)
                                direct = direct_score(training[:train_size], logp, mapping, k)
                                assert abs(objective-direct) < 1e-7
                                records.append({**case, 'algorithm': item['algorithm'], 'mapping': mapping.tolist(),
                                    'train_score': objective, 'heldout_score': score(hmatrix, logp, mapping),
                                    'heldout_bits_per_edge': -score(hmatrix, logp, mapping)/int(hmatrix.sum()),
                                    'seconds': item['seconds'], 'exact_recovery': bool(np.array_equal(mapping, truth)),
                                    'symbol_accuracy': float(np.mean(mapping[:k] == truth[:k])),
                                    'global_attained': None if optimum is None else abs(objective-optimum) < 1e-8,
                                    'global_gap_bits': None if optimum is None else optimum-objective,
                                    'direct_score_error': abs(objective-direct)})
                print(json.dumps({'k': k, 'family': family, 'systems_completed': replicate+1, 'rows': len(records)}), flush=True)
    result = {'experiment_id': 'NUM-02', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'synthetic-pilot' if args.pilot else 'declared-synthetic-optimization-study',
        'scipy_version': scipy.__version__, 'numpy_version': np.__version__, 'inputs': inputs, 'rows': records,
        'elapsed_seconds': time.perf_counter()-started,
        'protocol_sha256': hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest(),
        'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    payload = json.dumps(result, indent=2)+'\n'
    out.mkdir(parents=True)
    (out/'results.json').write_text(payload, encoding='utf-8')
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'conditions': len(inputs), 'rows': len(records), 'seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', default='experiments/2026-10-02-six-hour/graph-mapping/main')
    run(parser.parse_args())
