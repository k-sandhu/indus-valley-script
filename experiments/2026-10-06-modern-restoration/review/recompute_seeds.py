"""Independent recomputation of the REPORT seed-range table from the per-seed probability arrays.

For each neural procedure and seed, pool the five outer folds, compute exact top-one and native bucket loss
with this script's own code, and compare the minimum and maximum over seeds with the REPORT table.
Aggregates only are written.
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

SEEDS = [20261006, 20261007, 20261008]
NAMES = {'gru': 'GRU', 'transformer': 'Transformer', 'metadata': 'Conditioned neural'}


def main():
    c = Corpus()
    report = (PKG / 'REPORT.md').read_text(encoding='utf-8')
    table = {}
    for line in report.splitlines():
        m = re.match(r'^\| (.+?) \| ([\d.]+)–([\d.]+) \| ([\d.]+)–([\d.]+) \|$', line)
        if m:
            table[m.group(1)] = [float(x) for x in m.groups()[1:]]
    out = {'status': 'Verified computation (reviewer, independent code)', 'procedures': []}
    worst = 0.0
    for extra in (0, 1):
        for family, label in NAMES.items():
            tops, losses = [], []
            for seed in SEEDS:
                hit = n = 0
                bits = 0.0
                for f in range(5):
                    sel = json.loads((PKG / 'main' / f'{family}-f{f}-extra{extra}-selection.json').read_text(encoding='utf-8'))
                    stem = sel['outer']['loss']['label']
                    with np.load(ROOT / 'data/raw/2026-10-06-modern-restoration/main' / f'{stem}-s{seed}.npz', allow_pickle=False) as z:
                        p, signs = z['probs'], z['signs'].tolist()
                    _, test, _, _ = c.outer(f)
                    actual = [s for r in test for s in r['seq']]
                    index = {s: i for i, s in enumerate(signs)}
                    unknown = index[UNKNOWN]
                    target = np.array([index.get(a, unknown) for a in actual])
                    top = np.argmax(p, axis=1)
                    hit += sum(signs[t] == a for t, a in zip(top, actual))
                    bits += float(-np.log2(np.clip(p[np.arange(len(actual)), target], 1e-300, None)).sum())
                    n += len(actual)
                tops.append(100 * hit / n)
                losses.append(bits / n)
            name = label + (' + extra' if extra else '')
            rep = table[name]
            mine = [round(min(tops), 4), round(max(tops), 4), round(min(losses), 6), round(max(losses), 6)]
            diff = max(abs(a - b) for a, b in zip(mine, rep))
            worst = max(worst, diff)
            out['procedures'].append({'procedure': name, 'top1_range_percent': [min(tops), max(tops)], 'bits_range': [min(losses), max(losses)], 'max_abs_difference_to_report': diff})
    out['max_abs_difference'] = worst
    (PKG / 'review' / 'recomputed-seed-ranges.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
