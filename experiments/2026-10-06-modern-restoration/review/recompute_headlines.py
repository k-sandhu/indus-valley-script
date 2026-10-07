"""Independent recomputation of the REPORT headline table and paired contrasts.

Reads the saved probability arrays (npz) for each primary procedure, recomputes top-k,
native bucket loss, common-alphabet loss and the five-bin ECE with its own code, compares
them with the per-query JSONL fields, with aggregate-results.json and with the numbers
printed in REPORT.md, and recomputes the paired component-bootstrap contrasts
(2,000 draws, seed 23101) for the 20 REPORT rows.  A sensitivity bootstrap resamples the
full-graph link sets rather than saved components.  Aggregates only are written.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus, ROOT, UNKNOWN  # noqa: E402
from graph_rules import build  # noqa: E402

FAMILIES = ['classical', 'gru', 'transformer', 'metadata', 'ensemble']
NAMES = {'classical': 'MKN', 'gru': 'GRU', 'transformer': 'Transformer', 'metadata': 'Conditioned neural', 'ensemble': 'Log ensemble'}


def read_probs(path):
    with np.load(ROOT / path, allow_pickle=False) as f:
        return f['probs'], f['signs'].tolist()


def per_query(p, signs, actual, alphabet):
    index = {s: i for i, s in enumerate(signs)}
    unknown = index[UNKNOWN]
    target = np.array([index.get(a, unknown) for a in actual])
    order = np.argsort(-p, axis=1, kind='stable')
    sign_arr = np.array(signs, dtype=object)
    top = {}
    for k in (1, 5, 10):
        top[k] = np.array([a in set(sign_arr[order[i, :k]].tolist()) for i, a in enumerate(actual)], dtype=float)
    native = -np.log2(np.clip(p[np.arange(len(actual)), target], 1e-300, None))
    novel = [i for i, s in enumerate(signs) if s not in alphabet]
    pooled = p[:, novel].sum(axis=1)
    mass = np.array([p[i, index[a]] if (a in alphabet and a in index) else pooled[i] for i, a in enumerate(actual)])
    common = -np.log2(np.clip(mass, 1e-300, None))
    return {'top1': top[1], 'top5': top[5], 'top10': top[10], 'native': native, 'common': common, 'topmass': p.max(axis=1)}


def ece(topmass, correct):
    bins = np.minimum((topmass * 5).astype(int), 4)
    total = 0.0
    for b in range(5):
        sel = bins == b
        if sel.any():
            total += abs((topmass[sel] - correct[sel]).sum()) / len(topmass)
    return total


def parse_report_table(text):
    rows = {}
    for line in text.splitlines():
        m = re.match(r'^\| (.+?) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|$', line)
        if m:
            rows[m.group(1)] = [float(x) for x in m.groups()[1:]]
    return rows


def parse_contrasts(text):
    rows = {}
    for line in text.splitlines():
        m = re.match(r'^\| (.+?) \| (Markov[12]) \| ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] \| ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] \|$', line)
        if m:
            rows[(m.group(1), m.group(2))] = [float(x) for x in m.groups()[2:]]
    return rows


def main():
    c = Corpus()
    n_groups = len(c.groups)
    group = np.array([s['group'] for s in c.template])
    keys = c.keys
    report = (PKG / 'REPORT.md').read_text(encoding='utf-8')
    table = parse_report_table(report)
    contrasts = parse_contrasts(report)
    aggregate = json.loads((PKG / 'aggregate-results.json').read_text(encoding='utf-8'))
    out = {'status': 'Verified computation (reviewer, independent code)', 'procedures': {}, 'report_table_comparison': [],
           'contrast_comparison': [], 'sensitivity': {}}
    data = {}
    consistency = {'max_abs_top_flag_mismatch_vs_jsonl': 0, 'max_abs_loss_diff_vs_jsonl': 0.0, 'max_abs_mass_diff_vs_jsonl': 0.0}
    for extra in (0, 1):
        for family in FAMILIES:
            label = f'{NAMES[family]}' + (' + extra' if extra else '')
            cols = {k: np.zeros(8009) for k in ['top1', 'top5', 'top10', 'native', 'common', 'topmass']}
            for f in range(5):
                sel = json.loads((PKG / 'main' / f'{family}-f{f}-extra{extra}-selection.json').read_text(encoding='utf-8'))
                info = sel['outer']['loss']
                p, signs = read_probs(info['probability_file'])
                train, test, _, _ = c.outer(f)
                alphabet = {s for r in train for s in r['seq']}
                actual = [s for r in test for s in r['seq']]
                tkeys = [(r['record_id'], i) for r in test for i in range(len(r['seq']))]
                q = per_query(p, signs, actual, alphabet)
                idx = np.array([c.keyindex[k] for k in tkeys])
                jsonl = [json.loads(line) for line in (ROOT / info['query_file']).read_text(encoding='utf-8').splitlines() if line.strip()]
                assert [(j['record_id'], j['slot']) for j in jsonl] == tkeys
                consistency['max_abs_top_flag_mismatch_vs_jsonl'] += int(np.abs(q['top1'] - np.array([j['top1'] for j in jsonl], dtype=float)).sum())
                consistency['max_abs_top_flag_mismatch_vs_jsonl'] += int(np.abs(q['top10'] - np.array([j['top10'] for j in jsonl], dtype=float)).sum())
                consistency['max_abs_loss_diff_vs_jsonl'] = max(consistency['max_abs_loss_diff_vs_jsonl'], float(np.abs(q['native'] - np.array([j['bucket_loss_bits'] for j in jsonl])).max()))
                consistency['max_abs_mass_diff_vs_jsonl'] = max(consistency['max_abs_mass_diff_vs_jsonl'], float(np.abs(q['topmass'] - np.array([j['model_top_mass'] for j in jsonl])).max()))
                for k in cols:
                    cols[k][idx] = q[k]
            data[label] = cols
    for name, rows in c.references.items():
        cols = {
            'top1': np.zeros(8009), 'top5': np.zeros(8009), 'top10': np.zeros(8009), 'native': np.zeros(8009), 'common': np.zeros(8009), 'topmass': np.zeros(8009)}
        for r in rows:
            i = c.keyindex[(r['record_id'], r['slot'])]
            cols['top1'][i], cols['top5'][i], cols['top10'][i] = float(r['top1']), float(r['top5']), float(r['top10'])
            cols['native'][i] = cols['common'][i] = r['bucket_loss_bits']
            cols['topmass'][i] = r['model_top_mass']
        data[name] = cols
    out['consistency_with_per_query_jsonl'] = consistency

    def summary(cols):
        return {'top1': 100 * cols['top1'].mean(), 'top5': 100 * cols['top5'].mean(), 'top10': 100 * cols['top10'].mean(),
                'native': cols['native'].mean(), 'common': cols['common'].mean(), 'ece': 100 * ece(cols['topmass'], cols['top1'])}

    display = {'Markov1': 'Markov1, saved', 'Markov2': 'Markov2, saved'}
    worst = 0.0
    for label, cols in data.items():
        s = summary(cols)
        out['procedures'][label] = s
        rep = table.get(display.get(label, label))
        if rep is None:
            out['report_table_comparison'].append({'procedure': label, 'status': 'row not found in REPORT.md'})
            continue
        mine = [s['top1'], s['top5'], s['top10'], s['native'], s['common'], s['ece']]
        diffs = [abs(round(a, 4 if i in (0, 1, 2, 5) else 6) - b) for i, (a, b) in enumerate(zip(mine, rep))]
        worst = max(worst, max(diffs))
        out['report_table_comparison'].append({'procedure': label, 'max_abs_difference_after_rounding_to_report_precision': max(diffs),
                                               'recomputed': mine, 'report': rep})
    out['report_table_max_abs_difference'] = worst

    # Paired component bootstrap with the protocol's draws.
    rng = np.random.default_rng(23101)
    weights = np.zeros((2000, n_groups))
    for i in range(2000):
        weights[i] = np.bincount(rng.integers(0, n_groups, n_groups), minlength=n_groups)

    def paired(first, second, metric, w):
        delta = second[metric] - first[metric]
        sums = np.bincount(group, weights=delta, minlength=n_groups)
        counts = np.bincount(group, minlength=n_groups).astype(float)
        boot = (w @ sums) / (w @ counts)
        return float(delta.mean()), np.quantile(boot, [.025, .975]).tolist()

    worst_c = 0.0
    for (proc, ref), rep in contrasts.items():
        d1, ci1 = paired(data[ref], data[proc], 'top1', weights)
        d2, ci2 = paired(data[ref], data[proc], 'native', weights)
        mine = [100 * d1, 100 * ci1[0], 100 * ci1[1], d2, ci2[0], ci2[1]]
        diffs = [abs(round(a, 4) - b) for a, b in zip(mine, rep)]
        worst_c = max(worst_c, max(diffs))
        out['contrast_comparison'].append({'procedure': proc, 'comparator': ref, 'max_abs_difference': max(diffs), 'recomputed': mine, 'report': rep})
    out['contrast_rows_compared'] = len(contrasts)
    out['contrast_max_abs_difference'] = worst_c

    # Sensitivity: cluster by full-graph link sets (the package's own link rule) instead of saved components.
    dsu, n = build(c, min_string_len=1)
    cluster_of_row = {r['record_id']: dsu.find(i) for i, r in enumerate(c.rows)}
    roots = {}
    cluster = np.array([roots.setdefault(cluster_of_row[s['record_id']], len(roots)) for s in c.template])
    n_clusters = len(roots)
    rng = np.random.default_rng(23101)
    w2 = np.zeros((2000, n_clusters))
    for i in range(2000):
        w2[i] = np.bincount(rng.integers(0, n_clusters, n_clusters), minlength=n_clusters)

    def paired2(first, second, metric):
        delta = second[metric] - first[metric]
        sums = np.bincount(cluster, weights=delta, minlength=n_clusters)
        counts = np.bincount(cluster, minlength=n_clusters).astype(float)
        boot = (w2 @ sums) / (w2 @ counts)
        return float(delta.mean()), np.quantile(boot, [.025, .975]).tolist()

    out['sensitivity']['clusters_saved_components'] = n_groups
    out['sensitivity']['clusters_full_graph_sets'] = n_clusters
    sens = []
    for proc, ref in [('Log ensemble + extra', 'Markov1'), ('Log ensemble + extra', 'Markov2'), ('MKN', 'Markov1'), ('MKN', 'Markov2'), ('GRU', 'Markov2')]:
        d, ci = paired2(data[ref], data[proc], 'top1')
        d0, ci0 = paired(data[ref], data[proc], 'top1', weights)
        sens.append({'procedure': proc, 'comparator': ref, 'difference_points': 100 * d,
                     'interval_full_graph_sets_points': [100 * ci[0], 100 * ci[1]],
                     'interval_saved_components_points': [100 * ci0[0], 100 * ci0[1]]})
    out['sensitivity']['top1_intervals_when_resampling_link_sets'] = sens
    # Contrasts the REPORT does not tabulate: what the neural component and the extra text add on top of MKN.
    extra_pairs = [('MKN', 'GRU'), ('MKN', 'Transformer'), ('MKN', 'Conditioned neural'), ('MKN', 'Log ensemble'),
                   ('MKN + extra', 'GRU + extra'), ('MKN + extra', 'Log ensemble + extra'),
                   ('Log ensemble', 'Log ensemble + extra'), ('MKN', 'MKN + extra')]
    out['unreported_paired_contrasts'] = []
    for ref, proc in extra_pairs:
        d1, ci1 = paired(data[ref], data[proc], 'top1', weights)
        d2, ci2 = paired(data[ref], data[proc], 'native', weights)
        d3, ci3 = paired(data[ref], data[proc], 'common', weights)
        out['unreported_paired_contrasts'].append({
            'comparator': ref, 'procedure': proc, 'top1_points': [100 * d1, 100 * ci1[0], 100 * ci1[1]],
            'native_bits': [d2, ci2[0], ci2[1]], 'common_bits': [d3, ci3[0], ci3[1]]})
    (PKG / 'review' / 'recomputed-headlines.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k not in ('report_table_comparison', 'contrast_comparison')}, indent=1))
    print('worst table diff', worst, 'worst contrast diff', worst_c)


if __name__ == '__main__':
    main()
