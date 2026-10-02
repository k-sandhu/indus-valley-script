"""Rebuild corpus edges and independently check graph-search objectives."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
from itertools import permutations
import json
from pathlib import Path
import types
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/graph-mapping'


def edge_counts(rows, k):
    edges = Counter()
    symbols = Counter()
    for row in rows:
        chain = [k]+row+[k+1]
        edges.update(zip(chain, chain[1:]))
        symbols.update(row)
    matrix = [[edges[i, j] for j in range(k+2)] for i in range(k+2)]
    return matrix, [symbols[i] for i in range(k)]


def probabilities(matrix, k):
    b = np.zeros((k+2, k+2))
    for source in range(k):
        total = sum(matrix[source][j]+1 for j in list(range(k))+[k+1])
        for destination in list(range(k))+[k+1]:
            b[source, destination] = np.log2((matrix[source][destination]+1)/total)
    total = sum(matrix[k][j]+1 for j in range(k))
    for destination in range(k):
        b[k, destination] = np.log2((matrix[k][destination]+1)/total)
    return b


def scalar(matrix, b, mapping):
    return float(sum(value*b[mapping[i], mapping[j]] for i, row in enumerate(matrix) for j, value in enumerate(row) if value))


def exact(matrix, b, k):
    p = np.array([list(v)+[k, k+1] for v in permutations(range(k))])
    # One flattened matrix product independently sums the directed edge terms.
    indices = p[:, :, None]*(k+2)+p[:, None, :]
    values = b.ravel()[indices].reshape(len(p), -1) @ np.asarray(matrix).ravel()
    best = float(values.max())
    return best, int(np.sum(abs(values-best) < 1e-8))


def main():
    out = BASE/'review'
    if out.exists():
        raise RuntimeError('Use a fresh endpoint.')
    data = json.loads((BASE/'main/results.json').read_text(encoding='utf-8'))
    mod = types.ModuleType('frozen_generator')
    mod.__file__ = str(ROOT/'src/six_hour/graph_mapping.py')
    exec(compile((BASE/'main/code_snapshot.py').read_text(encoding='utf-8'), mod.__file__, 'exec'), mod.__dict__)
    fields = ['family', 'k', 'seed', 'reference_records', 'training_records', 'shift']
    key = lambda r: tuple(r[f] for f in fields)
    inputs = {key(r): r for r in data['inputs']}
    rows = defaultdict(list)
    for row in data['rows']:
        rows[key(row)].append(row)
    max_score_error = 0.
    all_counts = all_maps = all_outcomes = all_maxima = True
    global_count = 0
    cases_with_truth_preferred_wrong = []
    optimization_failures = []
    for number, (case, original) in enumerate(inputs.items()):
        family, k, seed, ref_n, train_n, shift = case
        spec = mod.system(seed, family, k)
        encoding = np.random.default_rng(seed+4).permutation(k)
        truth = list(np.argsort(encoding))+[k, k+1]
        reference = mod.sample(spec, 400, seed+1)[:ref_n]
        training = [[int(encoding[v]) for v in r] for r in mod.sample(spec, 640, seed+2, shift)[:train_n]]
        heldout = [[int(encoding[v]) for v in r] for r in mod.sample(spec, 400, seed+3, shift)]
        train_matrix, train_uni = edge_counts(training, k)
        ref_matrix, ref_uni = edge_counts(reference, k)
        held_matrix, _ = edge_counts(heldout, k)
        all_counts &= all(original[field] == value for field, value in [
            ('training_counts', train_matrix), ('training_unigrams', train_uni), ('reference_counts', ref_matrix),
            ('reference_unigrams', ref_uni), ('heldout_counts', held_matrix), ('truth', truth),
            ('unobserved_training_codes', [i for i, n in enumerate(train_uni) if n == 0])])
        b = probabilities(ref_matrix, k)
        truth_score = scalar(train_matrix, b, truth)
        max_score_error = max(max_score_error, abs(truth_score-original['truth_score']))
        if k == 8:
            global_count += 1
            optimum, ties = exact(train_matrix, b, k)
            all_maxima &= ties == original['global_ties'] and abs(optimum-original['global_score']) < 1e-7
            all_maxima &= original['truth_global'] == (abs(truth_score-optimum) < 1e-8)
            if not original['truth_global']:
                cases_with_truth_preferred_wrong.append(dict(zip(fields, case)))
        for row in rows[case]:
            p = row['mapping']
            all_maps &= sorted(p[:k]) == list(range(k)) and p[-2:] == [k, k+1]
            train_score = scalar(train_matrix, b, p)
            held_score = scalar(held_matrix, b, p)
            max_score_error = max(max_score_error, abs(train_score-row['train_score']), abs(held_score-row['heldout_score']))
            all_outcomes &= row['exact_recovery'] == (p == truth)
            all_outcomes &= abs(row['symbol_accuracy']-sum(p[i] == truth[i] for i in range(k))/k) < 1e-12
            all_outcomes &= abs(row['heldout_bits_per_edge']+held_score/sum(map(sum, held_matrix))) < 1e-12
            if k == 8:
                all_outcomes &= row['global_attained'] == (abs(train_score-optimum) < 1e-8)
                max_score_error = max(max_score_error, abs((optimum-train_score)-row['global_gap_bits']))
                if row['algorithm'] == 'multistart_refined' and not row['global_attained']:
                    optimization_failures.append({**dict(zip(fields, case)), 'gap_bits': optimum-train_score})
        if number % 48 == 0:
            print(json.dumps({'counted_conditions': number+1, 'exact_maxima': global_count}), flush=True)
    checks = {
        '48_systems_384_conditions': len(inputs) == 384 and len({(r['family'], r['k'], r['seed']) for r in data['inputs']}) == 48,
        '1536_rows_unique_four_algorithms': len(data['rows']) == 1536 and all(len(v) == 4 and len({r['algorithm'] for r in v}) == 4 for v in rows.values()),
        'independent_edge_counts_match': bool(all_counts), 'boundary_and_bijection_checks': bool(all_maps),
        'all_recovery_and_score_fields_match': bool(all_outcomes), '192_exact_maxima_match': bool(all_maxima) and global_count == 192,
        'scalar_scores_match': max_score_error < 1e-7,
        'multistart_score_dominates_baselines': all(next(r['train_score'] for r in v if r['algorithm'] == 'multistart_refined') >= max(r['train_score'] for r in v)-1e-8 for v in rows.values()),
        'code_hash_matches': hashlib.sha256((BASE/'main/code_snapshot.py').read_bytes()).hexdigest() == data['code_sha256'],
        'protocol_hash_matches': hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest() == data['protocol_sha256'],
    }
    assert all(checks.values()), checks
    groups = defaultdict(list)
    for row in data['rows']:
        groups[row['family'], row['k'], row['algorithm']].append(row)
    summary = []
    for (family, k, algorithm), group in sorted(groups.items()):
        summary.append({'family': family, 'k': k, 'algorithm': algorithm, 'conditions': len(group), 'systems': 12,
            'complete_recoveries': sum(r['exact_recovery'] for r in group),
            'symbol_accuracy': float(np.mean([r['symbol_accuracy'] for r in group])),
            'global_attained': sum(r['global_attained'] for r in group) if k == 8 else None,
            'mean_positive_global_gap_bits': float(np.mean([max(0, r['global_gap_bits']) for r in group])) if k == 8 else None,
            'mean_seconds': float(np.mean([r['seconds'] for r in group])),
            'mean_heldout_bits_per_edge': float(np.mean([r['heldout_bits_per_edge'] for r in group]))})
    bootstraps = []
    rng = np.random.default_rng(729001)
    for family in ['transition', 'administrative_form']:
        for k in [8, 20]:
            seeds = sorted({r['seed'] for r in data['inputs'] if r['family'] == family and r['k'] == k})
            differences = []
            for seed in seeds:
                paired = [v for case, v in rows.items() if case[:3] == (family, k, seed)]
                differences.append(np.mean([next(r['exact_recovery'] for r in v if r['algorithm'] == 'multistart_refined') - next(r['exact_recovery'] for r in v if r['algorithm'] == 'faq_barycenter') for v in paired]))
            values = np.array(differences)
            draw = rng.integers(0, 12, size=(20000, 12))
            bootstraps.append({'family': family, 'k': k, 'systems': 12, 'comparison': 'multistart_minus_barycenter_recovery',
                'difference': float(values.mean()), 'interval95': np.quantile(values[draw].mean(axis=1), [.025, .975]).tolist()})
    out.mkdir()
    (out/'checks.json').write_text(json.dumps({'created_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
        'max_score_error_bits': max_score_error, 'global_optimum_disagrees_with_truth': cases_with_truth_preferred_wrong,
        'multistart_optimization_failures': optimization_failures}, indent=2)+'\n', encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    (out/'paired-system-comparisons.json').write_text(json.dumps(bootstraps, indent=2)+'\n', encoding='utf-8')
    with (out/'summary.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader(); writer.writerows(summary)
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks_passed': len(checks), 'exact_maxima': global_count, 'max_error': max_score_error}))


if __name__ == '__main__':
    main()
