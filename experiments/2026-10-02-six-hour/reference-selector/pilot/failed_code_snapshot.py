"""Reference-only conditional likelihood choice between two mapping models."""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import linear_sum_assignment
import graph_mapping as graph
import slot_mapping as slot

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'experiments/2026-10-02-six-hour/reference-selector'


def conditional_graph(rows, reference, k, mapping=None):
    edges, _ = graph.counts(reference, k)
    logp = graph.reference_matrix(edges, k)
    start = np.exp2(logp[k, :k])
    transition = np.exp2(logp[:k, :k])
    end = np.exp2(logp[:k, k+1])
    length_prob = {length: float(start@np.linalg.matrix_power(transition, length-1)@end)
                   for length in set(map(len, rows))}
    assert all(0 < value <= 1 for value in length_prob.values())
    mapping = np.arange(k+2) if mapping is None else np.r_[mapping, k, k+1]
    return graph.direct_score(rows, logp, mapping, k)-sum(np.log2(length_prob[len(row)]) for row in rows)


def conditional_slot(rows, reference, k, mapping=None):
    mapping = np.arange(k) if mapping is None else mapping
    return slot.direct(rows, slot.cell_counts(reference, k), mapping, k)


def select_reference(reference, k, seed):
    order = np.random.default_rng(seed).permutation(len(reference))
    folds = np.empty(len(reference), dtype=np.int16)
    folds[order] = np.arange(len(reference)) % 3
    scores = []
    for fold in range(3):
        train = [row for i, row in enumerate(reference) if folds[i] != fold]
        test = [row for i, row in enumerate(reference) if folds[i] == fold]
        scores.append({'fold': fold, 'train_records': len(train), 'test_records': len(test),
                       'slot_log2_score': conditional_slot(test, train, k),
                       'graph_log2_score': conditional_graph(test, train, k)})
    slot_score = sum(v['slot_log2_score'] for v in scores)
    graph_score = sum(v['graph_log2_score'] for v in scores)
    return {'selected': 'length_slot' if slot_score > graph_score else 'graph_multistart',
            'slot_score': slot_score, 'graph_score': graph_score, 'folds': folds.tolist(), 'scores': scores}


def selfcheck():
    reference = [[0, 1, 0], [1, 0, 1], [0, 0], [1, 1], [0, 1, 1]]
    checks = {}
    for length in [2, 3]:
        space = list(map(list, product(range(2), repeat=length)))
        for name, function in [('graph', conditional_graph), ('slot', conditional_slot)]:
            mass = sum(2**function([row], reference, 2) for row in space)
            checks[name+str(length)] = abs(mass-1) < 1e-12
    assert all(checks.values())
    return checks


def run(args):
    output = ROOT/args.output
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    checks = selfcheck()
    start_time = time.perf_counter()
    rows, worlds, selections = [], [], []
    for ki, k in enumerate([8, 20]):
        for fi, family in enumerate(['transition', 'administrative_form']):
            for replicate in range(1 if args.pilot else 12):
                seed = 910261002+1000000*ki+100000*fi+1000*replicate
                spec = graph.system(seed, family, k)
                reference = graph.sample(spec, 400, seed+1)
                encoding = np.random.default_rng(seed+4).permutation(k)
                truth = np.argsort(encoding)
                ref_sizes = [40] if args.pilot else [40, 400]
                choices = {}
                for ref_size in ref_sizes:
                    choices[ref_size] = select_reference(reference[:ref_size], k, seed+50)
                    selections.append({'seed': seed, 'family': family, 'k': k, 'reference_records': ref_size,
                                       **choices[ref_size]})
                for si, shift in enumerate([0, .35]):
                    training = [[int(encoding[c]) for c in row] for row in graph.sample(spec, 640, seed+2, shift)]
                    heldout = [[int(encoding[c]) for c in row] for row in graph.sample(spec, 400, seed+3, shift)]
                    worlds.append({'seed': seed, 'family': family, 'k': k, 'shift': shift, 'truth': truth.tolist(),
                                   'reference': reference, 'training': training, 'heldout': heldout})
                    for ri, ref_size in enumerate(ref_sizes):
                        ref_rows = reference[:ref_size]
                        ref_edges, ref_uni = graph.counts(ref_rows, k)
                        ref_cells = slot.cell_counts(ref_rows, k)
                        logp = graph.reference_matrix(ref_edges, k)
                        for ti, train_size in enumerate([160] if args.pilot else [160, 640]):
                            train = training[:train_size]
                            w = slot.weights(slot.cell_counts(train, k), ref_cells, k)
                            _, slot_map = linear_sum_assignment(w, maximize=True)
                            edges, uni = graph.counts(train, k)
                            solver_seed = 920000000+ki*1000000+fi*100000+replicate*1000+si*100+ri*10+ti
                            graph_map = graph.fit(edges, logp, uni, ref_uni, k, solver_seed)[-1]['mapping'][:k]
                            maps = {'length_slot': slot_map, 'graph_multistart': graph_map}
                            maps['reference_selected'] = maps[choices[ref_size]['selected']]
                            maps['family_oracle'] = slot_map if family == 'administrative_form' else graph_map
                            for name, selected in maps.items():
                                rows.append({'seed': seed, 'family': family, 'k': k, 'shift': shift,
                                    'reference_records': ref_size, 'training_records': train_size,
                                    'algorithm': name, 'mapping': selected.tolist(),
                                    'reference_choice': choices[ref_size]['selected'], 'solver_seed': solver_seed,
                                    'exact_recovery': bool(np.array_equal(selected, truth)),
                                    'symbol_accuracy': float(np.mean(selected == truth)),
                                    'slot_train_score': float(w[np.arange(k), selected].sum()),
                                    'graph_train_score': graph.score(edges, logp, np.r_[selected, k, k+1]),
                                    'slot_heldout_bits_per_token': -conditional_slot(heldout, ref_rows, k, selected)/sum(map(len, heldout)),
                                    'graph_conditional_heldout_bits_per_token': -conditional_graph(heldout, ref_rows, k, selected)/sum(map(len, heldout))})
                print(json.dumps({'family': family, 'k': k, 'systems': replicate+1}), flush=True)
    output.mkdir(parents=True)
    result = {'experiment_id': 'CRYPTO-08', 'created_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'synthetic-pilot' if args.pilot else 'fresh-world-reference-only-selection',
              'selfchecks': checks, 'selections': selections, 'rows': rows,
              'elapsed_seconds': time.perf_counter()-start_time,
              'protocol_sha256': hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest(),
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'generator_sha256': hashlib.sha256(Path(graph.__file__).read_bytes()).hexdigest(),
              'slot_helper_sha256': hashlib.sha256(Path(slot.__file__).read_bytes()).hexdigest()}
    (output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (output/'worlds.json').write_text(json.dumps(worlds, indent=2)+'\n', encoding='utf-8')
    for name, source in [('code_snapshot.py', Path(__file__)), ('generator_snapshot.py', Path(graph.__file__)),
                         ('slot_helper_snapshot.py', Path(slot.__file__))]:
        (output/name).write_bytes(source.read_bytes())
    print(json.dumps({'rows': len(rows), 'selections': len(selections), 'seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', default='experiments/2026-10-02-six-hour/reference-selector/main')
    run(parser.parse_args())
