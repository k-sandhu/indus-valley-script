"""Matched administrative forms with common length and shared symbol mass."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.optimize import linear_sum_assignment

import graph_mapping as graph
import reference_selector as selector
import slot_mapping as slot

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms'
K = 20
VARIANTS = [('separated', None), ('same_length_0', 0.), ('same_length_35', .35), ('same_length_70', .70)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def generate(seed):
    base = graph.system(seed, 'administrative_form', K)
    original = [[p.copy() for p in form] for form in base['forms']]
    extended = [[p.copy() for p in form] for form in original]
    pools = [np.flatnonzero(p) for p in original[0]]
    rng = np.random.default_rng(seed + 100)
    for fi, roles in [(0, [0, 3]), (1, [3])]:
        for role in roles:
            p = np.zeros(K)
            p[pools[role]] = rng.dirichlet(np.full(len(pools[role]), .7))
            extended[fi].append(p)
    background = rng.dirichlet(np.full(K, .7))
    return dict(seed=seed, original=original, extended=extended, mixture=base['mixture'], background=background,
                pools=[p.tolist() for p in pools])


def stream(spec, variant, n, seed, shift=0):
    name, alpha = variant
    mixture = (1 - shift) * spec['mixture'] + shift * np.roll(spec['mixture'], 1)
    forms = spec['original'] if alpha is None else [[(1 - alpha) * p + alpha * spec['background'] for p in form] for form in spec['extended']]
    draws = np.random.default_rng(seed).random((n, 7))
    rows, labels = [], []
    for draw in draws:
        fi = min(int(np.searchsorted(np.cumsum(mixture), draw[0])), 2)
        row = [min(int(np.searchsorted(np.cumsum(p), draw[j + 1])), K - 1) for j, p in enumerate(forms[fi])]
        rows.append(row)
        labels.append(fi)
    return rows, labels


def form_cells(rows, labels):
    cells = defaultdict(lambda: np.zeros(K, dtype=np.int64))
    for row, label in zip(rows, labels):
        for pos, code in enumerate(row):
            cells[label, pos][code] += 1
    return cells


def form_weights(rows, labels, reference, ref_labels):
    ref = form_cells(reference, ref_labels)
    w = np.zeros((K, K))
    for cell, counts in form_cells(rows, labels).items():
        p = ref.get(cell, np.zeros(K)) + 1
        w += counts[:, None] * np.log2(p / p.sum())[None, :]
    return w


def form_score(rows, labels, reference, ref_labels, mapping):
    ref = form_cells(reference, ref_labels)
    total = 0.
    for row, label in zip(rows, labels):
        for pos, code in enumerate(row):
            p = ref.get((label, pos), np.zeros(K)) + 1
            total += np.log2(p[mapping[code]] / p.sum())
    return float(total)


def serial_spec(spec):
    return {key: value if key in ('seed', 'pools') else (value.tolist() if isinstance(value, np.ndarray) else [[p.tolist() for p in form] for form in value]) for key, value in spec.items()}


def main(args):
    output = BASE / args.endpoint
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    output.mkdir(parents=True)
    snapshots = [('code_snapshot.py', Path(__file__)), ('graph_snapshot.py', Path(graph.__file__)),
                 ('slot_snapshot.py', Path(slot.__file__)), ('selector_snapshot.py', Path(selector.__file__))]
    for name, path in snapshots:
        (output / name).write_bytes(path.read_bytes())
    frozen = dict(created_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=digest(BASE / 'PROTOCOL.md'),
                  sources={name: digest(path) for name, path in snapshots}, numpy_version=np.__version__, scipy_version=scipy.__version__)
    write(output / 'execution-freeze.json', frozen)
    started = time.perf_counter()
    rows, worlds, parameters, choices, cases = [], [], [], [], []
    reps = 1 if args.pilot else 12
    for replicate in range(reps):
        seed = (2010261002 if args.pilot else 1010261002) + 1000 * replicate
        spec = generate(seed)
        parameters.append(serial_spec(spec))
        encoding = np.random.default_rng(seed + 4).permutation(K)
        truth = np.argsort(encoding)
        for vi, variant in enumerate(VARIANTS):
            name, alpha = variant
            reference, reference_labels = stream(spec, variant, 400, seed + 1)
            selected_by_size = {}
            sizes = [40] if args.pilot else [40, 400]
            for size in sizes:
                choice = selector.select_reference(reference[:size], K, seed + 50)
                selected_by_size[size] = choice['selected']
                choices.append(dict(seed=seed, variant=name, alpha=alpha, reference_records=size, **choice))
            for si, shift in enumerate([0.] if args.pilot else [0., .35]):
                plain, training_labels = stream(spec, variant, 640, seed + 2, shift)
                held_plain, held_labels = stream(spec, variant, 400, seed + 3, shift)
                training = [[int(encoding[c]) for c in row] for row in plain]
                heldout = [[int(encoding[c]) for c in row] for row in held_plain]
                key = dict(seed=seed, variant=name, alpha=alpha, shift=shift, k=K)
                worlds.append(dict(**key, encoding=encoding.tolist(), truth=truth.tolist(), reference=reference,
                                   reference_labels=reference_labels, training=training, training_labels=training_labels,
                                   heldout=heldout, heldout_labels=held_labels))
                for ri, size in enumerate(sizes):
                    reference_rows = reference[:size]
                    ref_labels = reference_labels[:size]
                    ref_edges, ref_uni = graph.counts(reference_rows, K)
                    logp = graph.reference_matrix(ref_edges, K)
                    train_edges, train_uni = graph.counts(training, K)
                    w = slot.weights(slot.cell_counts(training, K), slot.cell_counts(reference_rows, K), K)
                    _, slot_map = linear_sum_assignment(w, maximize=True)
                    fw = form_weights(training, training_labels, reference_rows, ref_labels)
                    _, form_map = linear_sum_assignment(fw, maximize=True)
                    solver_seed = 1110261002 + 1000 * replicate + 10 * si + ri
                    graph_map = graph.fit(train_edges, logp, train_uni, ref_uni, K, solver_seed)[-1]['mapping'][:K]
                    maps = dict(length_slot=slot_map, graph_multistart=graph_map, form_observed_slot=form_map)
                    maps['reference_selected'] = maps[selected_by_size[size]]
                    condition = dict(**key, reference_records=size, training_records=640, solver_seed=solver_seed,
                                     reference_choice=selected_by_size[size])
                    cases.append(dict(**condition, slot_weights=w.tolist(), form_weights=fw.tolist(),
                                      slot_certificate=slot.assignment_certificate(w, slot_map),
                                      form_certificate=slot.assignment_certificate(fw, form_map),
                                      unobserved_training_codes=np.flatnonzero(train_uni == 0).tolist()))
                    tokens = sum(map(len, heldout))
                    for method, mapping in maps.items():
                        rows.append(dict(**condition, algorithm=method, mapping=mapping.tolist(),
                                         exact_recovery=bool(np.array_equal(mapping, truth)), symbol_accuracy=float(np.mean(mapping == truth)),
                                         slot_train_score=float(w[np.arange(K), mapping].sum()),
                                         graph_train_score=graph.score(train_edges, logp, np.r_[mapping, K, K + 1]),
                                         form_train_score=float(fw[np.arange(K), mapping].sum()),
                                         slot_heldout_bits_per_token=-selector.conditional_slot(heldout, reference_rows, K, mapping) / tokens,
                                         graph_conditional_heldout_bits_per_token=-selector.conditional_graph(heldout, reference_rows, K, mapping) / tokens,
                                         form_observed_heldout_bits_per_token=-form_score(heldout, held_labels, reference_rows, ref_labels, mapping) / tokens))
            print(json.dumps(dict(seed=seed, variant=name, completed_conditions=len(cases))), flush=True)
    result = dict(status='fresh-pilot' if args.pilot else 'post-outcome-fresh-world-stress-test',
                  completed_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - started,
                  selfchecks=selector.selfcheck(), rows=rows, cases=cases, choices=choices, **frozen)
    for name, value in [('results.json', result), ('worlds.json', worlds), ('parameters.json', parameters)]:
        write(output / name, value)
    print(json.dumps(dict(conditions=len(cases), rows=len(rows), seconds=result['elapsed_seconds'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--endpoint', required=True)
    main(parser.parse_args())
