"""Reviewer exploratory check: how much does the Dholavira log-likelihood improve when three arbitrary extra levels are added
to the declared series, compared with the improvement from the three documented levels 1/6, 1/12 and 1/24?

Uses the package's fit function on the 298 intact certain masses. Random levels are drawn log-uniformly between 1/32 and 4 times
the unit. Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/extra_levels_null.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-weight-metrology'
RAW = ROOT / 'data/raw/2026-10-06-weight-metrology'
sys.path.insert(0, str(PKG))
import analyze  # noqa: E402

rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
ids = json.loads((RAW / 'main/selection-ids.json').read_text())['site_primary_ids']['Dholavira']
masses = [rows[i - 1]['mass_g'] for i in ids]
base = analyze.fit(masses, 'indus_binary_decimal')
rng = np.random.default_rng(20261012)
deltas = []
for k in range(120):
    extra = np.exp(rng.uniform(math.log(1 / 32), math.log(4), 3))
    analyze.MODELS['tmp'] = (np.array(sorted(set(analyze.INDUS.tolist() + extra.tolist()))), (12.5, 15.0))
    r = analyze.fit(masses, 'tmp')
    deltas.append(r['log_likelihood'] - base['log_likelihood'])
analyze.MODELS['doc'] = (np.array(sorted(set(analyze.INDUS.tolist() + [1 / 6, 1 / 12, 1 / 24]))), (12.5, 15.0))
doc = analyze.fit(masses, 'doc')
out = {'n': len(masses), 'declared_ll': base['log_likelihood'],
       'documented_levels_1_6_1_12_1_24': {'ll': doc['log_likelihood'], 'delta_ll': doc['log_likelihood'] - base['log_likelihood'], 'unit_g': doc['unit_g'], 'signal_probability': doc['signal_probability']},
       'random_three_levels': {'draws': len(deltas), 'delta_ll_mean': float(np.mean(deltas)), 'delta_ll_95_percentile': float(np.quantile(deltas, .95)),
                               'delta_ll_max': float(np.max(deltas)), 'fraction_ge_documented': float(np.mean(np.array(deltas) >= doc['log_likelihood'] - base['log_likelihood']))}}
(PKG / 'review/extra-levels-null.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1))
