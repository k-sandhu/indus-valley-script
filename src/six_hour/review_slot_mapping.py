"""Independent scalar profiles, dual bounds and paired world summaries."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
from itertools import permutations
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'experiments/2026-10-02-six-hour/slot-mapping'
FIELDS = ['family', 'k', 'seed', 'shift', 'reference_records', 'training_records']


def cells(rows):
    result = Counter()
    for row in rows:
        result.update((len(row), slot, code) for slot, code in enumerate(row))
    return result


def likelihood(rows, ref, mapping, k):
    total = 0.
    for row in rows:
        for slot, code in enumerate(row):
            denominator = sum(ref[len(row), slot, c] for c in range(k))+k
            total += math.log2((ref[len(row), slot, mapping[code]]+1)/denominator)
    return total


def graph_likelihood(rows, reference, mapping, k):
    edges = Counter()
    for row in reference:
        chain = [k]+row+[k+1]
        edges.update(zip(chain, chain[1:]))
    score, count = 0., 0
    full_map = list(mapping)+[k, k+1]
    for row in rows:
        chain = [k]+row+[k+1]
        for a, b in zip(chain, chain[1:]):
            source, destination = full_map[a], full_map[b]
            targets = range(k) if source == k else list(range(k))+[k+1]
            denominator = sum(edges[source, c]+1 for c in targets)
            score += math.log2((edges[source, destination]+1)/denominator)
            count += 1
    return score, count


def main(args):
    source = BASE/args.endpoint/'results.json'
    world_source = source.parent/'worlds.json'
    out = BASE/args.output
    if out.exists():
        raise RuntimeError('Use a fresh review endpoint.')
    data = json.loads(source.read_text(encoding='utf-8'))
    worlds = {tuple(v[f] for f in ['family', 'k', 'seed', 'shift']): v
              for v in json.loads(world_source.read_text(encoding='utf-8'))}
    cases = {tuple(v[f] for f in FIELDS): v for v in data['cases']}
    outcomes = defaultdict(list)
    for row in data['rows']:
        outcomes[tuple(row[f] for f in FIELDS)].append(row)
    checks, max_error, ties, alt_rows = [], 0., [], []
    for key, case in cases.items():
        world = worlds[key[:4]]
        k = case['k']
        ref_rows = world['reference'][:case['reference_records']]
        train_rows = world['training'][:case['training_records']]
        ref, train = cells(ref_rows), cells(train_rows)
        for stored, independent in [(case['reference_cells'], ref), (case['training_cells'], train)]:
            actual = {(v['length'], v['slot'], c): n for v in stored
                      for c, n in enumerate(v['counts']) if n}
            assert actual == dict(independent)
        w = np.zeros((k, k))
        for (length, slot, code), number in train.items():
            denom = sum(ref[length, slot, c] for c in range(k))+k
            for target in range(k):
                w[code, target] += number*math.log2((ref[length, slot, target]+1)/denom)
        max_error = max(max_error, float(np.max(abs(w-np.asarray(case['weights'])))))
        assert np.allclose(w, case['weights'], atol=1e-8, rtol=0)
        slot_row = next(v for v in outcomes[key] if v['algorithm'] == 'length_slot')
        selected = np.array(slot_row['mapping'])
        selected_score = float(w[np.arange(k), selected].sum())
        dual = case['certificate']['dual']
        # The minimization dual has row+column <= -W and bounds max W.
        slack = -w-np.array(dual[:k])[:, None]-np.array(dual[k:])[None, :]
        assert slack.min() > -1e-7
        assert abs(-sum(dual)-selected_score) < 1e-7
        ambiguity = []
        for code in range(k):
            forbidden = w.copy()
            forbidden[code, selected[code]] = -np.inf
            _, alternative = linear_sum_assignment(forbidden, maximize=True)
            alt_score = float(w[np.arange(k), alternative].sum())
            gap = selected_score-alt_score
            assert gap > -1e-7
            if abs(gap) < 1e-8:
                ambiguity.append(code)
                alt_rows.append({**dict(zip(FIELDS, key)), 'code': code,
                                 'selected': selected.tolist(), 'alternative': alternative.tolist(), 'gap': gap})
        if k == 8:
            all_maps = np.array(list(permutations(range(k))))
            scores = np.array([sum(w[i, p[i]] for i in range(k)) for p in all_maps])
            assert abs(scores.max()-selected_score) < 1e-7
            assert int(np.sum(abs(scores-scores.max()) < 1e-8)) == case['exact']['ties_at_1e_8']
        ties.append({**dict(zip(FIELDS, key)), 'codes_movable_at_optimum': ambiguity})
        for row in outcomes[key]:
            mapping = row['mapping']
            assert sorted(mapping) == list(range(k))
            truth = world['truth']
            assert case['truth'] == truth
            assert row['exact_recovery'] == (mapping == truth)
            assert abs(row['symbol_accuracy']-sum(a == b for a, b in zip(mapping, truth))/k) < 1e-14
            train_slot = likelihood(train_rows, ref, mapping, k)
            held_slot = likelihood(world['heldout'], ref, mapping, k)
            train_graph, _ = graph_likelihood(train_rows, ref_rows, mapping, k)
            held_graph, held_edges = graph_likelihood(world['heldout'], ref_rows, mapping, k)
            token_count = sum(map(len, world['heldout']))
            errors = [abs(train_slot-row['slot_train_score']), abs(train_graph-row['graph_train_score']),
                      abs(-held_slot/token_count-row['slot_heldout_bits_per_token']),
                      abs(-held_graph/held_edges-row['graph_heldout_bits_per_edge'])]
            max_error = max(max_error, max(errors))
            assert max(errors) < 1e-7
        checks.append(key)
    groups = defaultdict(list)
    for row in data['rows']:
        groups[row['family'], row['k'], row['algorithm']].append(row)
    summaries = []
    for (family, k, algorithm), rows in sorted(groups.items()):
        summaries.append({'family': family, 'k': k, 'algorithm': algorithm,
                          'conditions': len(rows), 'recovered': sum(v['exact_recovery'] for v in rows),
                          **{f: float(np.mean([v[f] for v in rows])) for f in [
                              'symbol_accuracy', 'slot_heldout_bits_per_token', 'graph_heldout_bits_per_edge', 'seconds']}})
    paired = []
    for family in ['transition', 'administrative_form']:
        for k in [8, 20]:
            values = defaultdict(list)
            for key, rows in outcomes.items():
                if key[:2] != (family, k):
                    continue
                a = next(v for v in rows if v['algorithm'] == 'length_slot')
                b = next(v for v in rows if v['algorithm'] == 'graph_multistart')
                values[key[2]].append([float(a['exact_recovery'])-float(b['exact_recovery']),
                                      a['symbol_accuracy']-b['symbol_accuracy']])
            block = np.array([np.mean(v, axis=0) for _, v in sorted(values.items())])
            draws = np.random.default_rng(84102026+k).integers(len(block), size=(20000, len(block)))
            interval = np.quantile(block[draws].mean(axis=1), [.025, .975], axis=0)
            paired.append({'family': family, 'k': k, 'systems': len(block),
                           'direction': 'length_slot minus graph_multistart',
                           'recovery_difference': float(block[:, 0].mean()), 'recovery_95_ci': interval[:, 0].tolist(),
                           'symbol_difference': float(block[:, 1].mean()), 'symbol_95_ci': interval[:, 1].tolist()})
    result = {'created_utc': datetime.now(timezone.utc).isoformat(), 'conditions_reviewed': len(checks),
              'checks': {'all_cell_counts_rebuilt': True, 'all_weights_rebuilt': True,
                         'all_assignment_dual_bounds_match': True, 'all_eight_symbol_maxima_reenumerated': True,
                         'all_mapping_truth_comparisons_match': True, 'all_training_and_heldout_scores_match': True,
                         'all_code_exclusion_alternatives_checked': True,
                         'code_sha256_matches': hashlib.sha256((source.parent/'code_snapshot.py').read_bytes()).hexdigest() == data['code_sha256'],
                         'protocol_sha256_matches': hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest() == data['protocol_sha256']},
              'maximum_numeric_error': max_error, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'worlds_sha256': hashlib.sha256(world_source.read_bytes()).hexdigest(),
              'tied_conditions': sum(bool(v['codes_movable_at_optimum']) for v in ties)}
    assert all(result['checks'].values())
    out.mkdir(parents=True)
    for filename, value in [('verification.json', result), ('summary.json', {'groups': summaries, 'paired': paired}),
                            ('ties.json', {'conditions': ties, 'alternative_witnesses': alt_rows})]:
        (out/filename).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result))
    print(json.dumps(summaries))
    print(json.dumps(paired))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', default='main')
    parser.add_argument('--output', default='review')
    main(parser.parse_args())
