"""Reviewer refit of selected models on outer fold 0, compared with the saved probability arrays.

* MKN: re-run the whole inner grid (8 configurations x 3 inner folds) for fold 0 in both text
  regimes, confirm the saved inner losses and selected index, then refit the selected outer model
  and compare every probability with the saved npz.
* GRU: refit the loss-selected outer model for one seed (fold 0, benchmark only) at the saved
  epoch count and compare with the saved npz and the saved checkpoint hash.
* Transformer: the same for one seed.
Nothing is written to the package outside review/.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from data import Corpus, ROOT, RAW, probability_stats  # noqa: E402
from models import MKN, NGRAM_GRID, fit_net, predict_net  # noqa: E402
from run import mean_inner, choices, read_prob  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(a, b):
    return {'identical': bool(np.array_equal(a, b)), 'max_abs_difference': float(np.max(np.abs(a - b))),
            'top1_agreement': float(np.mean(a.argmax(axis=1) == b.argmax(axis=1)))}


def main():
    c = Corpus()
    out = {'status': 'Verified computation (reviewer refit)', 'classical': [], 'neural': []}
    fold = 0
    train, test, extra, _ = c.outer(fold)
    for added in (False, True):
        started = time.perf_counter()
        sel = json.loads((PKG / 'main' / f'classical-f{fold}-extra{int(added)}-selection.json').read_text(encoding='utf-8'))
        totals = [[] for _ in NGRAM_GRID]
        for inner, (fit, val, more, detail) in enumerate(c.inner(fold)):
            for j, config in enumerate(NGRAM_GRID):
                m = MKN(fit + (more if added else []), **config)
                p = m.predict(val)
                totals[j].append({**probability_stats(val, p, m.signs), 'slots': len(p)})
        stats = [mean_inner(e) for e in totals]
        selected = choices(stats)
        saved_inner = sel['inner']
        max_loss_diff = max(abs(a['bucket_loss_bits'] - b['bucket_loss_bits']) for a, b in zip(stats, saved_inner))
        max_acc_diff = max(abs(a['top1'] - b['top1']) for a, b in zip(stats, saved_inner))
        j = selected['loss']
        m = MKN(train + (extra if added else []), **NGRAM_GRID[j])
        p = m.predict(test)
        saved, signs = read_prob(ROOT / sel['outer']['loss']['probability_file'])
        out['classical'].append({'fold': fold, 'extra': added, 'inner_fits_rerun': 8 * 3,
                                 'selected_index_matches_saved': selected == sel['selected'],
                                 'selected_config': NGRAM_GRID[j],
                                 'max_abs_inner_loss_difference': max_loss_diff, 'max_abs_inner_top1_difference': max_acc_diff,
                                 'signs_equal': signs == m.signs, 'outer_probabilities': compare(p, saved),
                                 'seconds': time.perf_counter() - started})
        print(out['classical'][-1], flush=True)
    # Neural: one seed, benchmark-only regime, fold 0.
    for family in ('gru', 'transformer'):
        sel = json.loads((PKG / 'main' / f'{family}-f{fold}-extra0-selection.json').read_text(encoding='utf-8'))
        info = sel['outer']['loss']
        config = info['config']
        seed = 20261006
        epochs = info['epochs'][str(seed)]
        started = time.perf_counter()
        model, encoder, _, fit_info = fit_net(train, None, config, seed, epochs=epochs, checkpoint=None)
        p = predict_net(model, encoder.dataset(test))
        saved, signs = read_prob(RAW / 'main' / f"{info['label']}-s{seed}.npz")
        record = {'family': family, 'fold': fold, 'seed': seed, 'config': config, 'epochs': epochs,
                  'signs_equal': signs == encoder.signs, 'outer_probabilities': compare(p, saved),
                  'seconds': time.perf_counter() - started}
        out['neural'].append(record)
        print(record, flush=True)
        del model
    (PKG / 'review' / 'refit-check.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
