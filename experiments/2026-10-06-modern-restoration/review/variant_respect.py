"""Reviewer counterfactual (exploratory): accuracy on test strings that have a one-edit training neighbor,
when those neighbors are removed from training.

Same design as link_respect.py: fixed saved hyperparameters (Markov1 alpha 20; Markov2 alpha 20/20/100/20/20;
MKN order 3, scale 1.0), scoring restricted to the affected test strings, and a control that removes the same
number of randomly chosen training strings that are not neighbors.  Aggregates only are written.
"""
import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus, ROOT, old  # noqa: E402
from models import MKN  # noqa: E402
from neighbor_exposure import one_edit  # noqa: E402
from link_respect import ALPHA1, ALPHA2, load_second_order, top1_markov, top1_mkn  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repeats', type=int, default=100)
    parser.add_argument('--mkn-repeats', type=int, default=50)
    args = parser.parse_args()
    started = time.time()
    c = Corpus()
    order2 = load_second_order()
    rows = c.rows
    n = len(rows)
    fold = [c.assignment[i] for i in range(n)]
    comp = {}
    for g, mem in enumerate(c.groups):
        for i in mem:
            comp[i] = g
    models = {
        'Markov1': (lambda tr, f: old.MarkovRestorer(tr, ALPHA1[f]), top1_markov, args.repeats),
        'Markov2': (lambda tr, f: order2.Restorer(tr, ALPHA2[f]), top1_markov, args.repeats),
        'MKN order 3': (lambda tr, f: MKN(tr, order=3, discount_scale=1.0), top1_mkn, args.mkn_repeats)}
    per = {m: {'delta': [], 'comp': [], 'control': {f: [] for f in range(5)}} for m in models}
    info = []
    for f in range(5):
        train_idx = [i for i in range(n) if fold[i] != f]
        test_idx = [i for i in range(n) if fold[i] == f]
        neighbors, affected = set(), []
        for i in test_idx:
            near = [j for j in train_idx if one_edit(rows[i]['seq'], rows[j]['seq'])]
            if near:
                affected.append(i)
                neighbors.update(near)
        keep = [i for i in train_idx if i not in neighbors]
        others = [i for i in train_idx if i not in neighbors]
        affected_rows = [rows[i] for i in affected]
        comps = np.array([comp[i] for i in affected for _ in range(len(rows[i]['seq']))])
        info.append({'fold': f, 'training_rows': len(train_idx), 'neighbor_training_rows_removed': len(neighbors),
                     'affected_test_rows': len(affected), 'affected_test_queries': int(len(comps))})
        rng = np.random.default_rng(20261006 + 1000 + f)
        for name, (fit, score, repeats) in models.items():
            full = score(fit([rows[i] for i in train_idx], f), affected_rows)
            removed = score(fit([rows[i] for i in keep], f), affected_rows)
            for _ in range(repeats):
                drop = set(rng.choice(len(others), size=len(neighbors), replace=False).tolist())
                subset = sorted(set(neighbors) | {others[j] for j in range(len(others)) if j not in drop})
                per[name]['control'][f].append(float((score(fit([rows[i] for i in subset], f), affected_rows) - full).mean()))
            per[name]['delta'].append(removed - full)
            per[name]['comp'].append(comps)
        print('fold', f, round(time.time() - started, 1), 's', flush=True)
    out = {'status': 'Exploratory reviewer counterfactual', 'folds': info, 'models': {}}
    rng = np.random.default_rng(23101)
    weights = np.array([x['affected_test_queries'] for x in info], dtype=float)
    for name in models:
        delta = np.concatenate(per[name]['delta'])
        compv = np.concatenate(per[name]['comp'])
        u = np.unique(compv)
        index = {g: j for j, g in enumerate(u)}
        sums = np.zeros(len(u)); counts = np.zeros(len(u))
        for g, d in zip(compv, delta):
            sums[index[g]] += d; counts[index[g]] += 1
        boots = [sums[p].sum() / counts[p].sum() for p in (rng.integers(0, len(u), len(u)) for _ in range(2000))]
        reps = min(len(per[name]['control'][f]) for f in range(5))
        control = np.array([sum(weights[f] * per[name]['control'][f][r] for f in range(5)) / weights.sum() for r in range(reps)])
        out['models'][name] = {
            'affected_queries': int(len(delta)),
            'change_when_neighbors_removed_points': float(delta.mean() * 100),
            'interval_component_bootstrap_points': [float(np.quantile(boots, .025) * 100), float(np.quantile(boots, .975) * 100)],
            'control_change_random_removal_mean_points': float(control.mean() * 100),
            'control_change_random_removal_sd_points': float(control.std(ddof=1) * 100),
            'implied_change_in_whole_benchmark_top1_points': float(delta.sum() / 8009 * 100)}
    out['elapsed_seconds'] = time.time() - started
    (PKG / 'review' / 'variant-respect-estimate.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
