"""Reviewer measurement: one-edit neighbors of test strings inside the extra-text pool actually fitted.

For each outer fold, count test strings that have a one-edit neighbor among the extra strings (any length,
and length 3 or more) and compare with the benchmark training strings of the same fold.  Aggregates only.
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus  # noqa: E402
from neighbor_exposure import one_edit  # noqa: E402


def main():
    c = Corpus()
    out = {'status': 'Exploratory reviewer measurement', 'folds': []}
    for f in range(5):
        train, test, extra, _ = c.outer(f)
        e_all = [r['seq'] for r in extra]
        e3 = [s for s in e_all if len(s) >= 3]
        t_all = [r['seq'] for r in train]
        row = {'fold': f, 'test_strings': len(test), 'extra_strings': len(e_all), 'extra_strings_len3plus': len(e3), 'benchmark_training_strings': len(t_all)}
        for label, pool in [('extra_any_length', e_all), ('extra_len3plus', e3), ('benchmark_training', t_all)]:
            row['test_strings_with_one_edit_neighbor_in_' + label] = sum(any(one_edit(r['seq'], s) for s in pool) for r in test)
        out['folds'].append(row)
    keys = [k for k in out['folds'][0] if k.startswith('test_strings_with')]
    out['totals'] = {k: sum(r[k] for r in out['folds']) for k in keys}
    out['totals']['test_strings'] = sum(r['test_strings'] for r in out['folds'])
    (PKG / 'review' / 'extra-neighbor-exposure.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out['totals'], indent=1))


if __name__ == '__main__':
    main()
