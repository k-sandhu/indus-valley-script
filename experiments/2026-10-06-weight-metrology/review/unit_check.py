"""Reviewer check of the fitted Dholavira unit (REVIEW.md, check 1).

Reads the local-only catalogue rows and the package's saved selection IDs.
Writes aggregates only (no catalogue rows) to review/unit-check.json.
Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/unit_check.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-weight-metrology'
RAW = ROOT / 'data/raw/2026-10-06-weight-metrology'
OUT = PKG / 'review/unit-check.json'

INDUS = np.array([1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 10, 12.5, 20, 40, 100, 200, 400, 1000])
BG = 1 / math.log(100000 / .01)
rng = np.random.default_rng(20261008)


def loglik(x, u, sigma, p, c=INDUS):
    """Own implementation of the declared mixture (log-normal signal + log-uniform background)."""
    res = x[:, None] - np.log(c)[None, :] - math.log(u)
    comp = np.exp(-.5 * (res / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi) * len(c))
    f = p * comp.sum(axis=1) + (1 - p) * BG
    return float(np.log(f).sum())


def fit_sigma_p(x, u, c=INDUS):
    """Maximise over sigma in [0.005,0.20] and p in [0.05,0.99] at a fixed unit u."""
    best = None
    for s0 in (.02, .04, .08):
        for p0 in (.4, .8):
            opt = minimize(lambda v: -loglik(x, u, math.exp(v[0]), v[1], c), [math.log(s0), p0],
                           method='L-BFGS-B',
                           bounds=[(math.log(.005), math.log(.20)), (.05, .99)])
            if best is None or opt.fun < best.fun:
                best = opt
    return -best.fun, math.exp(best.x[0]), float(best.x[1])


def fit_free(x, lo=12.5, hi=15.0, c=INDUS, step=0.01):
    """Grid over u with sigma, p optimised at every u; returns the profile and the maximum."""
    grid = np.arange(lo, hi + 1e-9, step)
    prof = []
    for u in grid:
        ll, s, p = fit_sigma_p(x, float(u), c)
        prof.append((float(u), ll, s, p))
    return prof


def main():
    rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    sel = json.loads((RAW / 'main/selection-ids.json').read_text())
    ids = sel['site_primary_ids']['Dholavira']
    group = [rows[i - 1] for i in ids]
    masses = np.array([r['mass_g'] for r in group])
    x = np.log(masses)
    out = {'n': len(masses)}

    # 1. Profile likelihood over the unit (own implementation), 0.01 g grid.
    prof = fit_free(x, step=0.01)
    ll = np.array([p[1] for p in prof]); us = np.array([p[0] for p in prof])
    imax = int(ll.argmax())
    out['profile'] = {'u_hat_grid': float(us[imax]), 'll_max': float(ll[imax]),
                      'sigma_at_max': prof[imax][2], 'p_at_max': prof[imax][3]}
    inside = us[ll >= ll.max() - 1.920729]  # chi-square(1) 95% / 2
    out['profile']['lr95_interval'] = [float(inside.min()), float(inside.max())]
    for ufix in (13.55, 13.6, 13.65, 13.7, 13.8, 14.0, 14.2):
        k = int(np.argmin(abs(us - ufix)))
        out['profile'][f'll_at_{ufix}'] = float(ll[k])
        out['profile'][f'delta_ll_at_{ufix}'] = float(ll[k] - ll.max())
        out['profile'][f'sigma_at_{ufix}'] = prof[k][2]
        out['profile'][f'p_at_{ufix}'] = prof[k][3]
    out['profile']['lr_test_13_65_chi2'] = 2 * (float(ll.max()) - out['profile']['ll_at_13.65'])
    out['profile']['aic_difference_fixed_13_65_minus_free'] = (4 - 2 * out['profile']['ll_at_13.65']) - (6 - 2 * float(ll.max()))

    # 2. Cross-check against the package's own fit function.
    sys.path.insert(0, str(PKG))
    import analyze  # noqa: E402
    pkg_fit = analyze.fit(list(masses), 'indus_binary_decimal')
    out['package_fit'] = {k: pkg_fit[k] for k in ('unit_g', 'sigma_log', 'signal_probability', 'log_likelihood')}
    out['package_fit']['own_loglik_at_package_params'] = loglik(x, pkg_fit['unit_g'], pkg_fit['sigma_log'], pkg_fit['signal_probability'])

    # 3. Level-by-level implied unit (median mass / multiple within +-8% windows of the 13.65 g grid).
    levels = {}
    for c in INDUS[:8]:
        t = 13.8 * c  # window centre chosen between 13.65 and 14.0
        sel_m = masses[(masses >= t * .92) & (masses <= t * 1.08)]
        if len(sel_m) >= 3:
            implied = sel_m / c
            boot = [np.median(rng.choice(implied, len(implied))) for _ in range(2000)]
            levels[str(float(c))] = {'n': int(len(sel_m)), 'median_implied_unit_g': float(np.median(implied)),
                                      'boot95': [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))],
                                      'mean_implied_unit_g': float(implied.mean())}
    out['level_medians_all_certain_primary'] = levels

    # chert cuboid subset
    chert = np.array([r['mass_g'] for r in group if r['material'] and 'chert' in r['material'] and r['shape'] == 'Cuboid'])
    clev = {}
    for c in INDUS[:8]:
        t = 13.8 * c
        sel_m = chert[(chert >= t * .92) & (chert <= t * 1.08)]
        if len(sel_m) >= 3:
            implied = sel_m / c
            boot = [np.median(rng.choice(implied, len(implied))) for _ in range(2000)]
            clev[str(float(c))] = {'n': int(len(sel_m)), 'median_implied_unit_g': float(np.median(implied)),
                                    'boot95': [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))]}
    out['level_medians_chert_cuboid'] = {'n_chert_cuboid': int(len(chert)), 'levels': clev}

    # 4. Trend of the implied unit with denomination: regression of log(implied unit) on log2(multiple).
    pts = []
    for m in masses:
        j = int(np.argmin(abs(math.log(m) - np.log(INDUS * 13.8))))
        if INDUS[j] <= 4 and abs(math.log(m / (13.8 * INDUS[j]))) < .08:
            pts.append((math.log2(INDUS[j]), math.log(m / INDUS[j])))
    pts = np.array(pts)
    A = np.vstack([np.ones(len(pts)), pts[:, 0]]).T
    coef, *_ = np.linalg.lstsq(A, pts[:, 1], rcond=None)
    boots = []
    for _ in range(2000):
        ix = rng.integers(0, len(pts), len(pts))
        cb, *_ = np.linalg.lstsq(A[ix], pts[ix, 1], rcond=None)
        boots.append(cb[1])
    out['trend'] = {'n_objects': int(len(pts)),
                    'slope_log_unit_per_doubling': float(coef[1]),
                    'slope_boot95': [float(np.quantile(boots, .025)), float(np.quantile(boots, .975))],
                    'intercept_unit_at_multiple_1_g': float(math.exp(coef[0])),
                    'interpretation': 'a negative slope means smaller denominations imply a larger unit'}

    # 5. Split-sample unit fits with the package's own fit function.
    split = {}
    for name, sub in [('mass_lt_5g', masses[masses < 5]), ('mass_ge_5g', masses[masses >= 5]),
                      ('mass_ge_6g_le_100g', masses[(masses >= 6) & (masses <= 100)]),
                      ('mass_le_100g', masses[masses <= 100]), ('mass_gt_100g', masses[masses > 100])]:
        if len(sub) >= 8:
            f = analyze.fit(list(sub), 'indus_binary_decimal')
            split[name] = {k: f[k] for k in ('n', 'unit_g', 'signal_cv_percent', 'signal_probability', 'unit_at_boundary', 'sigma_at_boundary', 'log_likelihood')}
        else:
            split[name] = {'n': int(len(sub)), 'note': 'below 8, not fitted'}
    # bootstrap interval of the split fits (500 draws)
    for name, sub in [('mass_lt_5g', masses[masses < 5]), ('mass_ge_5g', masses[masses >= 5])]:
        us_b = []
        for _ in range(300):
            s = rng.choice(sub, len(sub), replace=True)
            us_b.append(analyze.fit(list(s), 'indus_binary_decimal')['unit_g'])
        split[name]['bootstrap_unit_95'] = [float(np.quantile(us_b, .025)), float(np.quantile(us_b, .975))]
    out['split_fits'] = split

    # 6. Unit-trade check inside the declared model: fit with the pure binary model for comparison and with a 13.65 fixed unit
    # using the package optimiser (equal bounds fix the parameter).
    analyze.MODELS['fixed_13_65'] = (INDUS, (13.65, 13.65))
    f13 = analyze.fit(list(masses), 'fixed_13_65')
    out['package_optimizer_fixed_13_65'] = {k: f13[k] for k in ('unit_g', 'sigma_log', 'signal_cv_percent', 'signal_probability', 'log_likelihood', 'aic')}
    out['package_fit']['aic'] = pkg_fit['aic']
    out['aic_free_minus_fixed_13_65_package_optimizer'] = pkg_fit['aic'] - f13['aic']

    # 7. Wear and damage frames: same unit with the fixed-13.65 comparison.
    frames = {}
    cert = [r for r in rows if r['site'] == 'Dholavira' and r['balance_class'] == 'certain' and r['mass_g'] and not r['missing_mass']]
    for name, flt in [('primary_intact', lambda r: r['primary_eligible']),
                      ('wear_allowed', lambda r: (not r['damage']) and (r['intact_condition'] or r['worn'])),
                      ('all_complete', lambda r: True)]:
        m = np.array([r['mass_g'] for r in cert if flt(r)])
        f = analyze.fit(list(m), 'indus_binary_decimal')
        f13_ = analyze.fit(list(m), 'fixed_13_65')
        frames[name] = {'n': int(len(m)), 'unit_g': f['unit_g'], 'll_free': f['log_likelihood'], 'll_fixed_13_65': f13_['log_likelihood'],
                        'delta_ll': f['log_likelihood'] - f13_['log_likelihood']}
    out['frames'] = frames

    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1)[:6000])


if __name__ == '__main__':
    main()
