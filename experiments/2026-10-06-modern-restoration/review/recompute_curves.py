"""Independent recomputation of the REPORT learning-curve table and the 100% minus 75% contrasts.

Reads each curve cell's saved probability arrays, recomputes top-one and native bucket loss with
its own code, parses the REPORT.md curve tables, and recomputes the paired component-bootstrap
intervals (2,000 draws, seed 23101).  Aggregates only are written.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from data import Corpus, ROOT, UNKNOWN  # noqa: E402


def probs(path):
    with np.load(ROOT / path, allow_pickle=False) as f:
        return f['probs'], f['signs'].tolist()


def main():
    c = Corpus()
    n_groups = len(c.groups)
    group = np.array([s['group'] for s in c.template])
    report = (PKG / 'REPORT.md').read_text(encoding='utf-8')
    table = {}
    for line in report.splitlines():
        m = re.match(r'^\| (\d+)% \| ([\d.]+) / ([\d.]+) \| ([\d.]+) / ([\d.]+) \| ([\d.]+) / ([\d.]+) \| ([\d.]+) / ([\d.]+) \|$', line)
        if m:
            v = [float(x) for x in m.groups()[1:]]
            table[int(m.group(1))] = {'classical/0': v[0:2], 'classical/1': v[2:4], 'neural/0': v[4:6], 'neural/1': v[6:8]}
    rng = np.random.default_rng(23101)
    weights = np.zeros((2000, n_groups))
    for i in range(2000):
        weights[i] = np.bincount(rng.integers(0, n_groups, n_groups), minlength=n_groups)
    cells = {}
    out = {'status': 'Verified computation (reviewer, independent code)', 'cells': [], 'training_sizes': []}
    worst = 0.0
    for family in ('classical', 'neural'):
        for extra in (0, 1):
            for pct in (25, 50, 75, 100):
                top = np.zeros(8009)
                loss = np.zeros(8009)
                sizes = []
                for f in range(5):
                    cur = json.loads((PKG / 'main' / f'curve-f{f}-extra{extra}-p{pct}.json').read_text(encoding='utf-8'))
                    sizes.append((cur['training_components'], cur['training_texts'], cur['training_tokens']))
                    info = cur[family]
                    p, signs = probs(info['probability_file'])
                    _, test, _, _ = c.outer(f)
                    index = {s: i for i, s in enumerate(signs)}
                    unknown = index[UNKNOWN]
                    actual = [s for r in test for s in r['seq']]
                    keys = [(r['record_id'], i) for r in test for i in range(len(r['seq']))]
                    order = np.argsort(-p, axis=1, kind='stable')[:, 0]
                    target = np.array([index.get(a, unknown) for a in actual])
                    ok = np.array([signs[o] == a for o, a in zip(order, actual)], dtype=float)
                    nat = -np.log2(np.clip(p[np.arange(len(actual)), target], 1e-300, None))
                    idx = np.array([c.keyindex[k] for k in keys])
                    top[idx] = ok
                    loss[idx] = nat
                cells[(family, extra, pct)] = (top, loss)
                rep = table[pct][f'{family}/{extra}']
                mine = [round(100 * top.mean(), 4), round(loss.mean(), 4)]
                diff = max(abs(mine[0] - rep[0]), abs(mine[1] - rep[1]))
                worst = max(worst, diff)
                out['cells'].append({'family': family, 'extra': extra, 'fraction_percent': pct, 'top1_percent': 100 * top.mean(),
                                     'native_bits': loss.mean(), 'max_abs_difference_to_report_at_printed_precision': diff})
                if family == 'classical' and extra == 0:
                    out['training_sizes'].append({'fraction_percent': pct, 'components_per_fold': [s[0] for s in sizes],
                                                  'texts_per_fold': [s[1] for s in sizes], 'tokens_per_fold': [s[2] for s in sizes]})
    out['curve_table_max_abs_difference'] = worst

    def boot(first, second):
        delta = second - first
        sums = np.bincount(group, weights=delta, minlength=n_groups)
        counts = np.bincount(group, minlength=n_groups).astype(float)
        b = (weights @ sums) / (weights @ counts)
        return float(delta.mean()), np.quantile(b, [.025, .975]).tolist()

    out['contrasts_100_minus_75'] = []
    rows = {}
    for line in report.splitlines():
        m = re.match(r'^\| (MKN|MKN \+ extra|Selected neural|Selected neural \+ extra) \| ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] \|$', line)
        if m:
            rows[m.group(1)] = [float(x) for x in m.groups()[1:]]
    names = {('classical', 0): 'MKN', ('classical', 1): 'MKN + extra', ('neural', 0): 'Selected neural', ('neural', 1): 'Selected neural + extra'}
    worst_c = 0.0
    for key, label in names.items():
        d, ci = boot(cells[(key[0], key[1], 75)][0], cells[(key[0], key[1], 100)][0])
        mine = [round(100 * d, 4), round(100 * ci[0], 4), round(100 * ci[1], 4)]
        diff = max(abs(a - b) for a, b in zip(mine, rows[label]))
        worst_c = max(worst_c, diff)
        out['contrasts_100_minus_75'].append({'procedure': label, 'points': 100 * d, 'interval': [100 * ci[0], 100 * ci[1]], 'max_abs_difference_to_report': diff})
    out['contrast_max_abs_difference'] = worst_c
    # Increments between successive fractions (descriptive).
    steps = []
    for key, label in names.items():
        tops = [100 * cells[(key[0], key[1], p)][0].mean() for p in (25, 50, 75, 100)]
        steps.append({'procedure': label, 'increments_25_50_75_100_points': [tops[i + 1] - tops[i] for i in range(3)]})
    out['increments'] = steps
    (PKG / 'review' / 'recomputed-curves.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'cells'}, indent=1))
    print('worst cell diff', worst, 'worst contrast diff', worst_c)


if __name__ == '__main__':
    main()
