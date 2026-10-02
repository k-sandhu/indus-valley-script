"""Linear assignment of observed length/slot profiles, with graph comparator."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
from itertools import permutations
import json
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.optimize import linear_sum_assignment, linprog
import graph_mapping as graph

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'experiments/2026-10-02-six-hour/slot-mapping'


def cell_counts(rows, k):
    cells = defaultdict(lambda: np.zeros(k, dtype=np.int64))
    for row in rows:
        for slot, code in enumerate(row):
            cells[len(row), slot][code] += 1
    return cells


def weights(training, reference, k):
    result = np.zeros((k, k))
    for cell, counts in training.items():
        ref = reference.get(cell, np.zeros(k, dtype=np.int64))+1
        logp = np.log2(ref/ref.sum())
        result += counts[:, None]*logp[None, :]
    return result


def direct(rows, reference, mapping, k):
    result = 0.
    for row in rows:
        for slot, code in enumerate(row):
            ref = reference.get((len(row), slot), np.zeros(k, dtype=np.int64))+1
            result += np.log2(ref[mapping[code]]/ref.sum())
    return float(result)


def assignment_certificate(w, mapping):
    k = len(w)
    # Independent continuous assignment relaxation; its vertices are bijections.
    constraints = np.zeros((2*k, k*k))
    for i in range(k):
        constraints[i, i*k:(i+1)*k] = 1
        constraints[k+i, i::k] = 1
    result = linprog(-w.ravel(), A_eq=constraints, b_eq=np.ones(2*k),
                     bounds=(0, None), method='highs')
    assert result.success
    dual = result.eqlin.marginals
    selected = float(w[np.arange(k), mapping].sum())
    slack = -w.ravel()-constraints.T@dual
    gap = -float(result.fun)-selected
    assert abs(gap) < 1e-7 and float(slack.min()) > -1e-7
    return {'lp_score': -float(result.fun), 'dual': dual.tolist(),
            'max_objective_gap': abs(gap), 'minimum_dual_slack': float(slack.min())}


def exact(w):
    maps = np.asarray(list(permutations(range(len(w)))), dtype=np.int16)
    scores = w[np.arange(len(w))[None, :], maps].sum(axis=1)
    best = float(scores.max())
    return {'score': best, 'ties_at_1e_8': int(np.sum(abs(scores-best) < 1e-8))}


def serialized(cells):
    return [{'length': length, 'slot': slot, 'counts': counts.tolist()}
            for (length, slot), counts in sorted(cells.items())]


def run(args):
    output = ROOT/args.output
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    start = time.perf_counter()
    cases, results, worlds = [], [], []
    reps = 1 if args.pilot else 12
    for ki, k in enumerate([8, 20]):
        for fi, family in enumerate(['transition', 'administrative_form']):
            for replicate in range(reps):
                seed = 810261002+1000000*ki+100000*fi+1000*replicate
                spec = graph.system(seed, family, k)
                reference = graph.sample(spec, 400, seed+1)
                encoding = np.random.default_rng(seed+4).permutation(k)
                truth = np.argsort(encoding)
                for si, shift in enumerate([0, .35]):
                    training = [[int(encoding[c]) for c in row]
                                for row in graph.sample(spec, 640, seed+2, shift)]
                    heldout = [[int(encoding[c]) for c in row]
                               for row in graph.sample(spec, 400, seed+3, shift)]
                    worlds.append({'seed': seed, 'family': family, 'k': k, 'shift': shift,
                                   'truth': truth.tolist(), 'reference': reference,
                                   'training': training, 'heldout': heldout})
                    for ri, ref_size in enumerate([40] if args.pilot else [40, 400]):
                        ref_cells = cell_counts(reference[:ref_size], k)
                        ref_edges, ref_uni = graph.counts(reference[:ref_size], k)
                        logp = graph.reference_matrix(ref_edges, k)
                        for ti, train_size in enumerate([160] if args.pilot else [160, 640]):
                            train = training[:train_size]
                            train_cells = cell_counts(train, k)
                            w = weights(train_cells, ref_cells, k)
                            begin = time.perf_counter()
                            _, mapping = linear_sum_assignment(w, maximize=True)
                            seconds = time.perf_counter()-begin
                            certificate = assignment_certificate(w, mapping)
                            enumeration = exact(w) if k == 8 else None
                            if enumeration:
                                assert abs(enumeration['score']-w[np.arange(k), mapping].sum()) < 1e-7
                            matrix, uni = graph.counts(train, k)
                            solver_seed = 820000000+ki*1000000+fi*100000+replicate*1000+si*100+ri*10+ti
                            candidate = graph.fit(matrix, logp, uni, ref_uni, k, solver_seed)[-1]
                            row_key = {'family': family, 'k': k, 'seed': seed, 'shift': shift,
                                       'reference_records': ref_size, 'training_records': train_size}
                            cases.append({**row_key, 'truth': truth.tolist(),
                                          'training_cells': serialized(train_cells),
                                          'reference_cells': serialized(ref_cells), 'weights': w.tolist(),
                                          'certificate': certificate, 'exact': enumeration,
                                          'unobserved_training_codes': np.flatnonzero(uni == 0).tolist(),
                                          'solver_seed': solver_seed})
                            for name, selected, duration in [
                                    ('length_slot', mapping, seconds),
                                    ('graph_multistart', candidate['mapping'][:k], candidate['seconds'])]:
                                slot_score = float(w[np.arange(k), selected].sum())
                                assert abs(slot_score-direct(train, ref_cells, selected, k)) < 1e-7
                                selected_graph = np.r_[selected, k, k+1]
                                heldout_edges, _ = graph.counts(heldout, k)
                                heldout_tokens = sum(map(len, heldout))
                                results.append({**row_key, 'algorithm': name, 'mapping': selected.tolist(),
                                    'exact_recovery': bool(np.array_equal(selected, truth)),
                                    'symbol_accuracy': float(np.mean(selected == truth)),
                                    'slot_train_score': slot_score,
                                    'graph_train_score': graph.score(matrix, logp, selected_graph),
                                    'slot_heldout_bits_per_token': -direct(heldout, ref_cells, selected, k)/heldout_tokens,
                                    'graph_heldout_bits_per_edge': -graph.score(heldout_edges, logp, selected_graph)/int(heldout_edges.sum()),
                                    'seconds': duration})
                print(json.dumps({'family': family, 'k': k, 'systems': replicate+1}), flush=True)
    output.mkdir(parents=True)
    result = {'experiment_id': 'CRYPTO-07', 'created_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'synthetic-pilot' if args.pilot else 'new-world-post-outcome-model-comparison',
              'cases': cases, 'rows': results, 'elapsed_seconds': time.perf_counter()-start,
              'protocol_sha256': hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest(),
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'generator_sha256': hashlib.sha256(Path(graph.__file__).read_bytes()).hexdigest(),
              'scipy_version': scipy.__version__, 'numpy_version': np.__version__}
    (output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (output/'worlds.json').write_text(json.dumps(worlds, indent=2)+'\n', encoding='utf-8')
    (output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (output/'generator_snapshot.py').write_bytes(Path(graph.__file__).read_bytes())
    print(json.dumps({'conditions': len(cases), 'results': len(results), 'seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', default='experiments/2026-10-02-six-hour/slot-mapping/main')
    run(parser.parse_args())
