"""Reviewer check: independent regeneration of the Monte Carlo envelope for the Dholavira certain quantogram.

Uses a different random generator seed from the package (seeds 12345 and 777) and an independently written cosine
sum. Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/quantogram_mc_check.py
"""
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-weight-metrology'
RAW = ROOT / 'data/raw/2026-10-06-weight-metrology'

rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
ids = json.loads((RAW / 'main/selection-ids.json').read_text())['site_primary_ids']['Dholavira']
m = np.array([rows[i - 1]['mass_g'] for i in ids if rows[i - 1]['mass_g'] <= 100])
n = len(m)
q = np.arange(40, 1501) / 100.0


def qgram(x):
    return np.sqrt(2 / len(x)) * np.cos(2 * np.pi * x[:, None] / q[None, :]).sum(axis=0)


obs = qgram(m)
out = {'n': int(n), 'observed_max': float(obs.max()), 'observed_argmax_q': float(q[obs.argmax()])}
for seed in (12345, 777):
    rng = np.random.default_rng(seed)
    maxima = np.empty(999)
    for i in range(999):
        maxima[i] = qgram(m * np.exp(rng.uniform(-.15, .15, n))).max()
    out[f'seed_{seed}'] = {'global95': float(np.quantile(maxima, .95)), 'p': float((1 + (maxima >= obs.max()).sum()) / 1000),
                          'median_max': float(np.median(maxima))}
# a harder null: jitter +-0.30
rng = np.random.default_rng(99)
maxima = np.array([qgram(m * np.exp(rng.uniform(-.30, .30, n))).max() for _ in range(999)])
out['jitter_0.30_seed_99'] = {'global95': float(np.quantile(maxima, .95)), 'p': float((1 + (maxima >= obs.max()).sum()) / 1000)}
(PKG / 'review/quantogram-mc-check.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1))
