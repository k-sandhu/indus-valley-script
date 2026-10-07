"""Reviewer probe (exploratory): effect of keeping raw counts for n-grams that begin at the text start.

The package's MKN gives every k-gram below the top order a continuation count (distinct left contexts).
For k-grams that start with the start sentinel the only possible left context is the sentinel itself, so each
such continuation count is 1.  Several standard toolkits keep the raw count for these k-grams.  This probe
changes only that rule (order 3, discount scale 1.0, the package's folds, benchmark-only training) and reports
top-one, bucket loss and initial-slot accuracy for the package's MKN, for a rebuild that reproduces it exactly
(sanity check), and for the raw-start variant.  The variant is not part of the package's endpoints.
Aggregates only are written.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from data import Corpus, UNKNOWN  # noqa: E402
from models import MKN  # noqa: E402


def build(rows, order=3, scale=1.0, raw_start=False):
    """Rebuild the package's MKN tables; with raw_start=True, start-anchored lower-order k-grams keep raw counts."""
    m = MKN.__new__(MKN)
    m.order, m.scale = order, scale
    m.signs = sorted({s for r in rows for s in r['seq']}) + [UNKNOWN]
    m.index = {s: i for i, s in enumerate(m.signs)}
    m.n = len(m.signs)
    m.end, m.start = m.n, m.n + 1
    raw = [Counter() for _ in range(order + 1)]
    for r in rows:
        sequence = [m.start] * (order - 1) + [m.index[s] for s in r['seq']] + [m.end]
        for pos in range(order - 1, len(sequence)):
            for k in range(1, order + 1):
                raw[k][tuple(sequence[pos - k + 1:pos + 1])] += 1
    m.counts = [Counter() for _ in range(order + 1)]
    m.counts[order] = raw[order]
    for k in range(1, order):
        for gram in raw[k + 1]:
            m.counts[k][gram[1:]] += 1
        if raw_start:
            for gram, count in raw[k].items():
                if gram[0] == m.start:
                    m.counts[k][gram] = count
    bottom = np.full(m.n + 1, .5, dtype=np.float64)
    for (token,), count in m.counts[1].items():
        bottom[token] += count
    m.bottom = bottom / bottom.sum()
    m.discounts, m.rows, m.patterns = {}, {}, {}
    for k in range(2, order + 1):
        coc = Counter(m.counts[k].values())
        n1, n2, n3, n4 = [coc[j] for j in [1, 2, 3, 4]]
        y = n1 / (n1 + 2 * n2) if n1 + 2 * n2 else .5
        estimates = [1 - 2 * y * n2 / n1 if n1 else .5, 2 - 3 * y * n3 / n2 if n2 else 1.0, 3 - 4 * y * n4 / n3 if n3 else 1.5]
        ds = np.array([np.clip(d * scale, .05, j - .05) for j, d in enumerate(estimates, 1)])
        m.discounts[k] = {'count_of_counts': dict(coc), 'discounts': ds.tolist()}
        counts = defaultdict(Counter)
        for gram, count in m.counts[k].items():
            counts[gram[:-1]][gram[-1]] = count
        m.rows[k] = {}
        m.patterns[k] = [defaultdict(list) for _ in range(k - 1)]
        for hist, values in counts.items():
            total = sum(values.values())
            sparse = {token: (count - ds[min(count, 3) - 1]) / total for token, count in values.items()}
            gamma = sum(ds[min(count, 3) - 1] for count in values.values()) / total
            m.rows[k][hist] = (sparse, gamma)
            for pos in range(k - 1):
                key = hist[:pos] + hist[pos + 1:]
                m.patterns[k][pos][key].append((hist[pos], sparse, gamma))
    m._vector_cache = {}
    return m


def main():
    c = Corpus()
    names = ['package MKN', 'rebuild without override', 'raw counts for start-anchored k-grams']
    tot = {n: [0, 0, 0.0, 0, 0] for n in names}
    identical = True
    for f in range(5):
        train, test, _, _ = c.outer(f)
        models = {names[0]: MKN(train, order=3, discount_scale=1.0), names[1]: build(train), names[2]: build(train, raw_start=True)}
        actual = [s for r in test for s in r['seq']]
        initial = np.array([i == 0 for r in test for i in range(len(r['seq']))])
        probs = {}
        for name, m in models.items():
            p = m.predict(test)
            probs[name] = p
            top = np.array([m.signs[j] == a for j, a in zip(np.argmax(p, axis=1), actual)])
            target = np.array([m.index.get(a, m.index[UNKNOWN]) for a in actual])
            loss = -np.log2(p[np.arange(len(actual)), target])
            rec = tot[name]
            rec[0] += int(top.sum()); rec[1] += len(actual); rec[2] += float(loss.sum()); rec[3] += int(top[initial].sum()); rec[4] += int(initial.sum())
        identical &= bool(np.array_equal(probs[names[0]], probs[names[1]]))
    out = {'status': 'Exploratory reviewer probe', 'rebuild_identical_to_package_probabilities': identical}
    for name, rec in tot.items():
        out[name] = {'top1': rec[0] / rec[1], 'bits': rec[2] / rec[1], 'initial_slot_top1': rec[3] / rec[4], 'queries': rec[1], 'initial_slots': rec[4]}
    (PKG / 'review' / 'sentence-start-probe.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
