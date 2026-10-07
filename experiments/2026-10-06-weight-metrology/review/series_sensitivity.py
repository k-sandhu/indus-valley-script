"""Reviewer check 1c: does the fitted Dholavira unit move when the declared series changes?

Exploratory. Uses the package's own fit function on the 298 intact certain Dholavira masses with
  (a) the declared binary-then-decimal list,
  (b) the list plus the 1/6 level (Hemmy's 8/3 group) and the 1/12 and 1/24 levels discussed in Ascalone 2022 pp. 166-167,
  (c) the list with the 1/32 and 1/16 levels removed,
  (d) a list restricted to levels 1/4 ... 4 (mass 3.4-55 g),
  (e) the declared list after correcting cat. 1730 (printed '1,84 g') from 184.0 g to 1.84 g,
  (f) sigma held at 0.02, 0.03 and 0.05 (fixed) to show the effect of the dispersion assumption.
Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/series_sensitivity.py
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
from scipy.optimize import minimize  # noqa: E402

INDUS = analyze.INDUS
BG = analyze.BG


def fit_with_list(masses, mult, lo=12.5, hi=15.0):
    analyze.MODELS['tmp'] = (np.array(mult), (lo, hi))
    r = analyze.fit(list(masses), 'tmp')
    return {k: r[k] for k in ('n', 'unit_g', 'signal_cv_percent', 'signal_probability', 'log_likelihood', 'aic', 'unit_at_boundary')}


def fit_fixed_sigma(masses, mult, sigma, lo=12.5, hi=15.0):
    x = np.log(np.asarray(masses))
    c = np.array(mult)
    best = None
    for u0 in np.linspace(lo, hi, 11):
        def nll(v):
            u, p = v
            res = x[:, None] - np.log(c)[None, :] - math.log(u)
            comp = np.exp(-.5 * (res / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi) * len(c))
            return -float(np.log(p * comp.sum(axis=1) + (1 - p) * BG).sum())
        o = minimize(nll, [u0, .6], method='L-BFGS-B', bounds=[(lo, hi), (.05, .99)])
        if best is None or o.fun < best.fun:
            best = o
    return {'sigma_fixed': sigma, 'unit_g': float(best.x[0]), 'signal_probability': float(best.x[1]), 'log_likelihood': float(-best.fun)}


def main():
    rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    ids = json.loads((RAW / 'main/selection-ids.json').read_text())['site_primary_ids']['Dholavira']
    masses = np.array([rows[i - 1]['mass_g'] for i in ids])
    out = {}
    out['a_declared'] = fit_with_list(masses, INDUS)
    out['b_plus_1_6_1_12_1_24'] = fit_with_list(masses, sorted(set(INDUS.tolist() + [1/6, 1/12, 1/24])))
    out['b2_plus_1_6_only'] = fit_with_list(masses, sorted(set(INDUS.tolist() + [1/6])))
    out['c_without_1_32_and_1_16'] = fit_with_list(masses, [x for x in INDUS if x > 1/16 + 1e-9])
    out['d_levels_1_4_to_4_only'] = fit_with_list(masses[(masses > 2.8) & (masses < 70)], [1/4, 1/2, 1, 2, 4])
    corrected = masses.copy()
    k = [i for i, c in zip(range(len(ids)), ids) if c == 1730][0]
    assert abs(corrected[k] - 184.0) < 1e-9
    corrected[k] = 1.84
    out['e_cat1730_corrected'] = fit_with_list(corrected, INDUS)
    out['e_cat1730_corrected']['delta_unit_vs_declared'] = out['e_cat1730_corrected']['unit_g'] - out['a_declared']['unit_g']
    out['f_fixed_sigma'] = [fit_fixed_sigma(masses, INDUS, s) for s in (.02, .03, .05)]
    # all-classes sample with the two apparent source/parser mass errors handled
    allc = [r for r in rows if r['site'] == 'Dholavira' and r['balance_class'] != 'excluded-related-find' and analyze.eligible(r)]
    m_all = np.array([r['mass_g'] for r in allc])
    out['g_all_classes_declared'] = fit_with_list(m_all, INDUS)
    m_fix = np.array([1.84 if r['cat'] == 1730 else r['mass_g'] for r in allc if r['cat'] != 1503])
    out['g_all_classes_1730_corrected_1503_removed'] = fit_with_list(m_fix, INDUS)
    (PKG / 'review/series-sensitivity.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
