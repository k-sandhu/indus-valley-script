"""Reviewer supplement: coverage of the true code inside the smallest candidate set holding 90% of
the predicted probability, for each primary procedure.  This is the event credited in the
2010 PLoS ONE cross-validation (sensitivity within the 90% cumulative-probability set); the
corpus, deletion law and model differ, so the numbers are descriptive only.
Aggregates only are written.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from data import Corpus, ROOT, UNKNOWN  # noqa: E402

NAMES = {'classical': 'MKN', 'gru': 'GRU', 'transformer': 'Transformer', 'metadata': 'Conditioned neural', 'ensemble': 'Log ensemble'}


def main():
    c = Corpus()
    out = {'status': 'Exploratory reviewer supplement', 'definition': 'true fine code lies in the smallest set of top-ranked candidates whose cumulative probability reaches 0.90 (UNKNOWN never credited)', 'procedures': {}}
    for extra in (0, 1):
        for family in NAMES:
            hits, sizes = 0, []
            n = 0
            for f in range(5):
                sel = json.loads((PKG / 'main' / f'{family}-f{f}-extra{extra}-selection.json').read_text(encoding='utf-8'))
                with np.load(ROOT / sel['outer']['loss']['probability_file'], allow_pickle=False) as z:
                    p, signs = z['probs'], z['signs'].tolist()
                _, test, _, _ = c.outer(f)
                actual = [s for r in test for s in r['seq']]
                order = np.argsort(-p, axis=1, kind='stable')
                cum = np.cumsum(np.take_along_axis(p, order, axis=1), axis=1)
                k = (cum < 0.90).sum(axis=1) + 1          # smallest set reaching 0.90
                index = {s: i for i, s in enumerate(signs)}
                for i, a in enumerate(actual):
                    top = order[i, :k[i]]
                    hits += int(a in index and index[a] in set(top.tolist()))
                    sizes.append(int(k[i]))
                    n += 1
            out['procedures'][NAMES[family] + (' + extra' if extra else '')] = {
                'queries': n, 'coverage_at_90_percent_mass': hits / n,
                'mean_set_size': float(np.mean(sizes)), 'median_set_size': float(np.median(sizes))}
    (PKG / 'review' / 'coverage-at-90-percent-mass.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
