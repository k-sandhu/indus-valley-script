"""Reviewer decomposition of the extra-text effect by whether the target code occurs in the benchmark
training fold.  For targets outside the benchmark-only training alphabet, both regimes score the pooled
UNKNOWN event (common-alphabet loss); for targets inside it, native and common loss coincide.
Aggregates only are written.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus  # noqa: E402
from recompute_headlines import per_query, read_probs  # noqa: E402

NAMES = {'classical': 'MKN', 'gru': 'GRU', 'transformer': 'Transformer', 'metadata': 'Conditioned neural', 'ensemble': 'Log ensemble'}


def main():
    c = Corpus()
    group = np.array([s['group'] for s in c.template])
    n_groups = len(c.groups)
    in_vocab = np.zeros(8009, dtype=bool)
    for f in range(5):
        train, test, _, _ = c.outer(f)
        alphabet = {s for r in train for s in r['seq']}
        for r in test:
            for i, s in enumerate(r['seq']):
                in_vocab[c.keyindex[(r['record_id'], i)]] = s in alphabet
    rng = np.random.default_rng(23101)
    weights = np.zeros((2000, n_groups))
    for i in range(2000):
        weights[i] = np.bincount(rng.integers(0, n_groups, n_groups), minlength=n_groups)

    def boot(delta, mask):
        sums = np.bincount(group[mask], weights=delta[mask], minlength=n_groups)
        counts = np.bincount(group[mask], minlength=n_groups).astype(float)
        valid = (weights @ counts) > 0
        b = (weights @ sums)[valid] / (weights @ counts)[valid]
        return float(delta[mask].mean()), np.quantile(b, [.025, .975]).tolist()

    out = {'status': 'Exploratory reviewer analysis', 'targets_in_benchmark_training_alphabet': int(in_vocab.sum()),
           'targets_outside': int((~in_vocab).sum()), 'families': {}}
    for family, label in NAMES.items():
        cols = {}
        for extra in (0, 1):
            cur = {k: np.zeros(8009) for k in ['top1', 'common', 'native']}
            for f in range(5):
                sel = json.loads((PKG / 'main' / f'{family}-f{f}-extra{extra}-selection.json').read_text(encoding='utf-8'))
                p, signs = read_probs(sel['outer']['loss']['probability_file'])
                train, test, _, _ = c.outer(f)
                alphabet = {s for r in train for s in r['seq']}
                actual = [s for r in test for s in r['seq']]
                q = per_query(p, signs, actual, alphabet)
                idx = np.array([c.keyindex[(r['record_id'], i)] for r in test for i in range(len(r['seq']))])
                for k in cur:
                    cur[k][idx] = q[k]
            cols[extra] = cur
        entry = {}
        for name, mask in [('targets_in_training_alphabet', in_vocab), ('targets_outside_training_alphabet', ~in_vocab)]:
            d_top, ci_top = boot(cols[1]['top1'] - cols[0]['top1'], mask)
            d_loss, ci_loss = boot(cols[1]['common'] - cols[0]['common'], mask)
            entry[name] = {'queries': int(mask.sum()),
                           'top1_points_extra_minus_noextra': [100 * d_top, 100 * ci_top[0], 100 * ci_top[1]],
                           'common_bits_extra_minus_noextra': [d_loss, ci_loss[0], ci_loss[1]],
                           'mean_common_bits_noextra': float(cols[0]['common'][mask].mean()),
                           'mean_common_bits_extra': float(cols[1]['common'][mask].mean())}
        total_gain = float((cols[1]['common'] - cols[0]['common']).sum())
        entry['share_of_total_common_bit_change_from_outside_targets'] = float((cols[1]['common'] - cols[0]['common'])[~in_vocab].sum() / total_gain)
        out['families'][label] = entry
    (PKG / 'review' / 'extra-text-decomposition.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
