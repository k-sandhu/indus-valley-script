"""Reviewer estimate: how far do first-order, second-order and MKN accuracies move on the
queries that the full-export links touch, when the linked training strings are removed?

Design (exploratory, post hoc):
  * Link rule: the package's own rule (object keys plus identical strings of any length over
    the whole observed export), which yields 6 bridged sets, 192 benchmark strings, 748 queries.
  * For each outer fold f, linked training strings L_f are the training strings that share a
    full-graph set with at least one test string of fold f; touched test queries are the queries
    of those test strings.
  * Models are refitted with the saved hyperparameters (Markov1 alpha 20; Markov2 alpha 20/20/100/20/20;
    MKN order 3, discount scale 1.0) on (a) the full training fold and (b) the fold minus L_f, and
    scored on the touched test strings.  Control: remove the same number of randomly chosen
    unlinked training strings, repeated with fixed seeds.
  * Only aggregates are written.
"""
import argparse
import importlib.util
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus, ROOT, RAW, old  # noqa: E402
from models import MKN  # noqa: E402
from graph_rules import build  # noqa: E402

ALPHA1 = {f: 20 for f in range(5)}
ALPHA2 = {0: 20, 1: 20, 2: 100, 3: 20, 4: 20}


def load_second_order():
    path = ROOT / 'experiments/2026-10-02-six-hour/markov-order2/main/code_snapshot.py'
    spec = importlib.util.spec_from_file_location('order2_snapshot', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def top1_markov(model, rows):
    out = []
    for r in rows:
        for slot, actual in enumerate(r['seq']):
            p = model.distribution(r, slot)
            order = np.argsort(-p, kind='stable')
            out.append(model.signs[order[0]] == actual)
    return np.array(out, dtype=float)


def top1_mkn(model, rows):
    p = model.predict(rows)
    actual = [s for r in rows for s in r['seq']]
    order = np.argsort(-p, axis=1, kind='stable')[:, 0]
    return np.array([model.signs[j] == a for j, a in zip(order, actual)], dtype=float)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--random-repeats', type=int, default=100)
    parser.add_argument('--mkn-repeats', type=int, default=40)
    parser.add_argument('--output', default=str(PKG / 'review' / 'link-respect-estimate.json'))
    args = parser.parse_args()
    started = time.time()
    c = Corpus()
    order2 = load_second_order()
    rows = c.rows
    n = len(rows)
    dsu, _ = build(c, min_string_len=1)
    fold = [c.assignment[i] for i in range(n)]
    members = defaultdict(list)
    for i in range(n):
        members[dsu.find(i)].append(i)
    comp_of = {}
    for g, mem in enumerate(c.groups):
        for i in mem:
            comp_of[i] = g
    bridged = [m for m in members.values() if len({comp_of[i] for i in m}) > 1]

    models = {
        'Markov1': (lambda tr, f: old.MarkovRestorer(tr, ALPHA1[f]), top1_markov, args.random_repeats),
        'Markov2': (lambda tr, f: order2.Restorer(tr, ALPHA2[f]), top1_markov, args.random_repeats),
        'MKN order 3': (lambda tr, f: MKN(tr, order=3, discount_scale=1.0), top1_mkn, args.mkn_repeats),
    }
    # Saved per-query top-one for correspondence checks (touched rows only).
    saved_first = {(s['record_id'], s['slot']): s['top1'] for s in old.read_jsonl(ROOT / 'experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl')}
    saved_second = {(s['record_id'], s['slot']): s['top1'] for s in old.read_jsonl(ROOT / 'experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl')}
    saved_mkn = {}
    for f in range(5):
        for s in old.read_jsonl(RAW / 'main' / f'classical-f{f}-extra0-outer-c3-queries.jsonl'):
            saved_mkn[(s['record_id'], s['slot'])] = s['top1']
    saved = {'Markov1': saved_first, 'Markov2': saved_second, 'MKN order 3': saved_mkn}

    result = {'status': 'Exploratory reviewer analysis', 'rule': 'object keys plus identical strings of any length over the observed export (package rule)',
              'random_repeats': {'Markov1': args.random_repeats, 'Markov2': args.random_repeats, 'MKN order 3': args.mkn_repeats},
              'folds': [], 'models': {}}
    per_model = {m: {'full': [], 'removed': [], 'random_delta': defaultdict(list), 'keys': [], 'comp': []} for m in models}
    untouched_stats = {m: {'touched_correct': 0, 'touched_n': 0, 'untouched_correct': 0, 'untouched_n': 0} for m in models}
    for f in range(5):
        train_idx = [i for i in range(n) if fold[i] != f]
        test_idx = [i for i in range(n) if fold[i] == f]
        linked, touched = set(), set()
        for m in bridged:
            t = [i for i in m if fold[i] == f]
            tr = [i for i in m if fold[i] != f]
            if t and tr:
                linked.update(tr)
                touched.update(t)
        unlinked_train = [i for i in train_idx if i not in linked]
        touched_rows = [rows[i] for i in sorted(touched)]
        keys = [(r['record_id'], s) for r in touched_rows for s in range(len(r['seq']))]
        comps = [comp_of[i] for i in sorted(touched) for _ in range(len(rows[i]['seq']))]
        result['folds'].append({'fold': f, 'training_rows': len(train_idx), 'linked_training_rows': len(linked),
                                'linked_training_tokens': sum(len(rows[i]['seq']) for i in linked),
                                'touched_test_rows': len(touched_rows), 'touched_test_queries': len(keys)})
        train_full = [rows[i] for i in train_idx]
        train_removed = [rows[i] for i in unlinked_train]
        for name, (fit, score, repeats) in models.items():
            model_full = fit(train_full, f)
            full_all = score(model_full, [rows[i] for i in test_idx])
            # Correspondence with the saved per-query results on every test query of the fold.
            test_keys = [(rows[i]['record_id'], s) for i in test_idx for s in range(len(rows[i]['seq']))]
            saved_vec = np.array([saved[name][k] for k in test_keys], dtype=float)
            result.setdefault('saved_correspondence', {}).setdefault(name, []).append(
                {'fold': f, 'queries': len(test_keys), 'identical_to_saved': bool(np.array_equal(saved_vec, full_all))})
            lookup = {k: v for k, v in zip(test_keys, full_all)}
            touched_set = set(keys)
            untouched_stats[name]['touched_correct'] += float(sum(lookup[k] for k in keys))
            untouched_stats[name]['touched_n'] += len(keys)
            untouched_stats[name]['untouched_correct'] += float(sum(v for k, v in lookup.items() if k not in touched_set))
            untouched_stats[name]['untouched_n'] += len(test_keys) - len(keys)
            full = np.array([lookup[k] for k in keys])
            removed = score(fit(train_removed, f), touched_rows)
            rng = np.random.default_rng(20261006 + 100 * f)
            for rep in range(repeats):
                # Control: keep every linked string, drop the same number of random unlinked strings.
                drop = set(rng.choice(len(unlinked_train), size=len(linked), replace=False).tolist())
                keep = sorted(set(linked) | {unlinked_train[j] for j in range(len(unlinked_train)) if j not in drop})
                subset = [rows[i] for i in keep]
                per_model[name]['random_delta'][f].append(float((score(fit(subset, f), touched_rows) - full).mean()))
            per_model[name]['full'].append(full)
            per_model[name]['removed'].append(removed)
            per_model[name]['keys'].append(keys)
            per_model[name]['comp'].append(np.array(comps))
        print('fold', f, 'done', round(time.time() - started, 1), 's', flush=True)

    rng = np.random.default_rng(23101)
    for name in models:
        full = np.concatenate(per_model[name]['full'])
        removed = np.concatenate(per_model[name]['removed'])
        comp = np.concatenate(per_model[name]['comp'])
        delta = removed - full
        ucomp = np.unique(comp)
        index = {g: j for j, g in enumerate(ucomp)}
        sums = np.zeros(len(ucomp)); counts = np.zeros(len(ucomp))
        for g, d in zip(comp, delta):
            sums[index[g]] += d; counts[index[g]] += 1
        boots = []
        for _ in range(2000):
            pick = rng.integers(0, len(ucomp), len(ucomp))
            boots.append(sums[pick].sum() / counts[pick].sum())
        random_means = np.array([np.mean(v) for v in zip(*[per_model[name]['random_delta'][f] for f in range(5)])])
        # Control pooled over folds: weight fold control by touched query counts.
        weights = np.array([fold_info['touched_test_queries'] for fold_info in result['folds']], dtype=float)
        control = np.array([sum(weights[f] * per_model[name]['random_delta'][f][r] for f in range(5)) / weights.sum()
                            for r in range(min(len(per_model[name]['random_delta'][f]) for f in range(5)))])
        u = untouched_stats[name]
        result['models'][name] = {
            'touched_queries': int(len(delta)),
            'touched_top1_full_training': float(full.mean()),
            'touched_top1_linked_strings_removed': float(removed.mean()),
            'change_when_linked_strings_removed_points': float(delta.mean() * 100),
            'change_interval_component_bootstrap_points': [float(np.quantile(boots, .025) * 100), float(np.quantile(boots, .975) * 100)],
            'control_change_random_unlinked_removal_mean_points': float(control.mean() * 100),
            'control_change_random_unlinked_removal_sd_points': float(control.std(ddof=1) * 100),
            'control_change_random_unlinked_removal_5_95_points': [float(np.quantile(control, .05) * 100), float(np.quantile(control, .95) * 100)],
            'excess_change_beyond_random_removal_points': float((delta.mean() - control.mean()) * 100),
            'implied_change_in_whole_benchmark_top1_if_only_touched_queries_change_points': float(delta.sum() / 8009 * 100),
            'implied_excess_change_in_whole_benchmark_top1_points': float((delta.mean() - control.mean()) * len(delta) / 8009 * 100),
            'saved_top1_touched_queries': u['touched_correct'] / u['touched_n'],
            'saved_top1_untouched_queries': u['untouched_correct'] / u['untouched_n'],
            'touched_queries_total': u['touched_n'], 'untouched_queries_total': u['untouched_n'],
        }
    result['elapsed_seconds'] = time.time() - started
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['models'], indent=1))
    print(json.dumps(result['saved_correspondence'], indent=1))


if __name__ == '__main__':
    main()
