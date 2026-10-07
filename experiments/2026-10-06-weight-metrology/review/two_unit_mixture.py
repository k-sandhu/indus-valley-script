"""Reviewer exploratory check: does a two-unit version of the declared series fit the intact certain Dholavira masses
better than the single-unit model, without using Ascalone's group lists to select objects?

Model: f(x) = p * [ w * S(x; u1, s1) + (1 - w) * S(x; u2, s2) ] + (1 - p) * BG, with S the declared 16-level equal-weight
Gaussian series in log mass. Six free parameters versus three for the package model. Exploratory (post-outcome).
Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/two_unit_mixture.py
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
sys.path.insert(0, str(PKG))
import analyze  # noqa: E402

C = analyze.INDUS
BG = analyze.BG
rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
ids = json.loads((RAW / 'main/selection-ids.json').read_text())['site_primary_ids']['Dholavira']
masses = np.array([rows[i - 1]['mass_g'] for i in ids])
x = np.log(masses)
LC = np.log(C)


def series(u, s):
    r = x[:, None] - LC[None, :] - math.log(u)
    return (np.exp(-.5 * (r / s) ** 2) / (s * math.sqrt(2 * math.pi))).sum(axis=1) / len(C)


def nll(v):
    u1, u2, ls1, ls2, w, p = v
    s1, s2 = math.exp(ls1), math.exp(ls2)
    f = p * (w * series(u1, s1) + (1 - w) * series(u2, s2)) + (1 - p) * BG
    return -float(np.log(f).sum())


def run(cap):
    lims = [(12.5, 15.0), (12.5, 15.0), (math.log(.005), math.log(cap)), (math.log(.005), math.log(cap)), (.02, .98), (.05, .99)]
    best = None
    rng = np.random.default_rng(1)
    starts = []
    for u1 in (13.5, 13.7, 14.0):
        for u2 in (14.3, 14.5, 14.8):
            for sg in (.015, .03):
                starts.append([u1, u2, math.log(sg), math.log(min(sg * 1.5, cap)), .5, .6])
    for _ in range(30):
        starts.append([rng.uniform(12.6, 14.9), rng.uniform(12.6, 14.9), math.log(rng.uniform(.01, min(.06, cap))), math.log(rng.uniform(.01, min(.06, cap))), rng.uniform(.2, .8), rng.uniform(.4, .9)])
    fits = []
    for s0 in starts:
        o = minimize(nll, s0, method='L-BFGS-B', bounds=lims)
        fits.append(o)
        if best is None or o.fun < best.fun:
            best = o
    u1, u2, ls1, ls2, w, p = best.x
    if u1 > u2:
        u1, u2, ls1, ls2, w = u2, u1, ls2, ls1, 1 - w
    opts = sorted({(round(min(o.x[0], o.x[1]), 2), round(max(o.x[0], o.x[1]), 2), round(-o.fun, 1)) for o in fits}, key=lambda t: -t[2])[:6]
    return {'sigma_cap': cap, 'll': float(-best.fun), 'aic': float(2 * 6 + 2 * best.fun), 'u_low_g': float(u1), 'u_high_g': float(u2),
            'cv_low_percent': float(100 * math.sqrt(math.expm1(math.exp(ls1) ** 2))), 'cv_high_percent': float(100 * math.sqrt(math.expm1(math.exp(ls2) ** 2))),
            'weight_of_low_unit_component': float(w), 'signal_probability': float(p), 'n_starts': len(starts),
            'top_local_optima_(u_low,u_high,loglik)': opts}


single = analyze.fit(list(masses), 'indus_binary_decimal')
out = {'n': int(len(masses)),
       'single_unit': {'ll': single['log_likelihood'], 'aic': single['aic'], 'unit_g': single['unit_g'], 'cv_percent': single['signal_cv_percent']},
       'two_unit_sigma_cap_0.20': run(.20), 'two_unit_sigma_cap_0.05': run(.05), 'two_unit_sigma_cap_0.03': run(.03)}
for k in ('two_unit_sigma_cap_0.20', 'two_unit_sigma_cap_0.05', 'two_unit_sigma_cap_0.03'):
    out[k]['delta_aic_single_minus_two'] = float(single['aic'] - out[k]['aic'])
(PKG / 'review/two-unit-mixture.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1))
