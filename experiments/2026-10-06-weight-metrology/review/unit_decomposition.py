"""Reviewer check 1b: which mass bands favour 14.0 g over 13.65 g, and cluster medians of small chert cuboids.

Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/unit_decomposition.py
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

INDUS = analyze.INDUS
BG = analyze.BG


def per_object_ll(masses, u, sigma, p):
    x = np.log(np.asarray(masses))
    res = x[:, None] - np.log(INDUS)[None, :] - math.log(u)
    comp = np.exp(-.5 * (res / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi) * len(INDUS))
    return np.log(p * comp.sum(axis=1) + (1 - p) * BG)


def main():
    rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    sel = json.loads((RAW / 'main/selection-ids.json').read_text())
    ids = sel['site_primary_ids']['Dholavira']
    group = [rows[i - 1] for i in ids]
    masses = np.array([r['mass_g'] for r in group])
    free = analyze.fit(list(masses), 'indus_binary_decimal')
    analyze.MODELS['fixed_13_65'] = (INDUS, (13.65, 13.65))
    fixed = analyze.fit(list(masses), 'fixed_13_65')
    a = per_object_ll(masses, free['unit_g'], free['sigma_log'], free['signal_probability'])
    b = per_object_ll(masses, fixed['unit_g'], fixed['sigma_log'], fixed['signal_probability'])
    bands = [(0, 1.3), (1.3, 2.6), (2.6, 5.0), (5.0, 10.0), (10.0, 20.0), (20.0, 100.0), (100.0, 1e6)]
    out = {'free': {k: free[k] for k in ('unit_g', 'sigma_log', 'signal_probability', 'log_likelihood')},
           'fixed_13_65': {k: fixed[k] for k in ('unit_g', 'sigma_log', 'signal_probability', 'log_likelihood')},
           'total_delta_ll': float(a.sum() - b.sum()), 'bands': []}
    for lo, hi in bands:
        m = (masses >= lo) & (masses < hi)
        out['bands'].append({'mass_band_g': [lo, hi], 'n': int(m.sum()),
                             'delta_ll_free_minus_fixed': float((a[m] - b[m]).sum())})

    # Cluster medians for intact certain cuboid chert weights (aggregate summary only).
    chert = np.array([r['mass_g'] for r in group if r['material'] and 'chert' in r['material'] and r['shape'] == 'Cuboid'])
    clusters = {}
    for name, lo, hi, mult in [('about_0.86_g_(1/16)', .7, 1.1, 16), ('about_1.75_g_(1/8)', 1.6, 2.1, 8),
                               ('about_3.5_g_(1/4)', 3.3, 4.1, 4), ('about_6.85_g_(1/2)', 6.3, 7.7, 2),
                               ('about_13.7_g_(1)', 13.3, 14.9, 1), ('about_27.3_g_(2)', 26.5, 28.5, .5),
                               ('about_55_g_(4)', 53, 58, .25)]:
        s = chert[(chert >= lo) & (chert <= hi)]
        if len(s):
            clusters[name] = {'n': int(len(s)), 'median_g': float(np.median(s)), 'q25_g': float(np.quantile(s, .25)),
                              'q75_g': float(np.quantile(s, .75)), 'min_g': float(s.min()), 'max_g': float(s.max()),
                              'median_times_multiplier_g': float(np.median(s) * mult)}
    out['chert_cuboid_clusters'] = {'n_chert_cuboid_total': int(len(chert)), 'n_below_5g': int((chert < 5).sum()), 'clusters': clusters}

    # Same clusters for all intact certain Dholavira objects (any material).
    clusters_all = {}
    for name, lo, hi, mult in [('about_0.86_g_(1/16)', .7, 1.1, 16), ('about_1.75_g_(1/8)', 1.6, 2.1, 8),
                               ('about_3.5_g_(1/4)', 3.3, 4.1, 4), ('about_6.85_g_(1/2)', 6.3, 7.7, 2),
                               ('about_13.7_g_(1)', 13.3, 14.9, 1), ('about_27.3_g_(2)', 26.5, 28.5, .5),
                               ('about_55_g_(4)', 53, 58, .25)]:
        s = masses[(masses >= lo) & (masses <= hi)]
        if len(s):
            clusters_all[name] = {'n': int(len(s)), 'median_g': float(np.median(s)),
                                  'median_times_multiplier_g': float(np.median(s) * mult)}
    out['all_certain_primary_clusters'] = clusters_all

    # Pure binary comparison and AIC for the full sample, to show the series question separately.
    out['model_aic'] = {m: analyze.fit(list(masses), m)['aic'] for m in ('indus_binary_decimal', 'pure_binary')}

    # Mass-window fits with the package's own function (descriptive; windows chosen by the reviewer after seeing the bands).
    rng = np.random.default_rng(20261009)
    windows = {}
    for name, lo, hi in [('1.3_to_5_g', 1.3, 5.0), ('5_to_100_g', 5.0, 100.0), ('6_g_and_above', 6.0, 1e6),
                         ('2.6_to_5_g', 2.6, 5.0), ('1.3_to_2.6_g', 1.3, 2.6)]:
        sub = masses[(masses >= lo) & (masses < hi)]
        f = analyze.fit(list(sub), 'indus_binary_decimal')
        draws = [analyze.fit(list(rng.choice(sub, len(sub), replace=True)), 'indus_binary_decimal')['unit_g'] for _ in range(200)]
        windows[name] = {'n': int(len(sub)), 'unit_g': f['unit_g'], 'signal_cv_percent': f['signal_cv_percent'],
                         'signal_probability': f['signal_probability'],
                         'bootstrap200_unit_95': [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))]}
    out['mass_window_fits'] = windows

    (PKG / 'review/unit-decomposition.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
