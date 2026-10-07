"""Reviewer check 3: base rate of the western 'Indus preference' rules under synthetic masses.

Implements the package's geometric and close-preference rules in vectorised form, confirms it reproduces
136/701 and 18/701 on the observed masses, then evaluates the same rules for
  N1  observed masses jittered by exp(U(-0.15, 0.15)) (the package's own quantogram null width),
  N2  observed masses jittered by exp(U(-0.35, 0.35)),
  N3  masses drawn log-uniformly within each site's observed range,
  U   a sweep of the Indus reference unit with the observed masses.
Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/western_null.py
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

INDUS, NE, LOCAL = analyze.INDUS, analyze.NE, analyze.LOCAL
rng = np.random.default_rng(20261010)


def rules(masses, sites, indus_unit, local_units, threshold=.03):
    x = np.log(masses)
    res = x[:, None] - np.log(INDUS)[None, :] - math.log(indus_unit)
    ix = np.argmin(abs(res), axis=1)
    signed = res[np.arange(len(x)), ix]
    i_log = abs(signed)
    i_err = abs(np.expm1(signed))
    l_log = np.full(len(x), np.inf)
    l_err = np.full(len(x), np.inf)
    for site in set(sites):
        sel = np.array([s == site for s in sites])
        units = local_units.get(site, dict(zip(LOCAL, [7.8, 8.4, 9.4])))
        best_log = np.full(sel.sum(), np.inf)
        best_err = np.full(sel.sum(), np.inf)
        for model in LOCAL:
            r = x[sel][:, None] - np.log(NE)[None, :] - math.log(units[model])
            j = np.argmin(abs(r), axis=1)
            sg = r[np.arange(sel.sum()), j]
            better = abs(sg) < best_log
            best_log = np.where(better, abs(sg), best_log)
            best_err = np.where(better, abs(np.expm1(sg)), best_err)
        l_log[sel] = best_log
        l_err[sel] = best_err
    geometric = i_log < l_log
    close = geometric & (i_err <= threshold) & (l_err - i_err >= .01)
    return geometric, close, i_err, l_err


def main():
    rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    sel = json.loads((RAW / 'main/selection-ids.json').read_text())
    models = json.loads((PKG / 'runs/2026-10-06-main/model-comparisons.json').read_text())
    local_units = models['local_units']
    ids = sel['western_primary_ids']
    masses = np.array([rows[i - 1]['mass_g'] for i in ids])
    sites = [rows[i - 1]['site'] for i in ids]
    ref = next(f['unit_g'] for f in models['fits'] if f['group'] == 'Dholavira' and f['model'] == 'indus_binary_decimal')
    g, c, i_err, l_err = rules(masses, sites, ref, local_units)
    out = {'n': len(ids), 'reference_unit_g': ref, 'observed_geometric': int(g.sum()), 'observed_close': int(c.sum())}
    assert out['observed_geometric'] == 136 and out['observed_close'] == 18, out

    def summarise(name, geo, clo):
        geo, clo = np.array(geo), np.array(clo)
        return {'name': name, 'draws': len(geo),
                'geometric_mean': float(geo.mean()), 'geometric_95': [float(np.quantile(geo, .025)), float(np.quantile(geo, .975))],
                'close_mean': float(clo.mean()), 'close_95': [float(np.quantile(clo, .025)), float(np.quantile(clo, .975))],
                'p_close_ge_observed': float((1 + (clo >= 18).sum()) / (len(clo) + 1)),
                'p_geometric_ge_observed': float((1 + (geo >= 136).sum()) / (len(geo) + 1))}

    out['nulls'] = []
    for jitter in (.15, .35):
        geo, clo = [], []
        for _ in range(2000):
            m = masses * np.exp(rng.uniform(-jitter, jitter, len(masses)))
            a, b, _, _ = rules(m, sites, ref, local_units)
            geo.append(a.sum()); clo.append(b.sum())
        out['nulls'].append(summarise(f'observed masses x exp(U(+-{jitter}))', geo, clo))

    # N3 log-uniform within each site's observed range
    site_set = sorted(set(sites))
    lo = {s: min(m for m, t in zip(masses, sites) if t == s) for s in site_set}
    hi = {s: max(m for m, t in zip(masses, sites) if t == s) for s in site_set}
    geo, clo = [], []
    for _ in range(2000):
        m = np.array([math.exp(rng.uniform(math.log(lo[s]), math.log(hi[s]))) for s in sites])
        a, b, _, _ = rules(m, sites, ref, local_units)
        geo.append(a.sum()); clo.append(b.sum())
    out['nulls'].append(summarise('log-uniform within each site observed range', geo, clo))

    # Same restricted to masses 1-600 g (where Indus multiples are densest in the catalogue) for context
    # Reference-unit sweep on the observed masses
    sweep = []
    for u in np.round(np.arange(10.0, 18.01, .25), 2):
        a, b, _, _ = rules(masses, sites, float(u), local_units)
        sweep.append({'indus_unit_g': float(u), 'geometric': int(a.sum()), 'close': int(b.sum())})
    out['unit_sweep_observed_masses'] = sweep
    out['unit_sweep_summary'] = {'close_mean_over_10_to_18g': float(np.mean([s['close'] for s in sweep])),
                                  'close_max': int(max(s['close'] for s in sweep)),
                                  'close_at_14_0': next(s['close'] for s in sweep if s['indus_unit_g'] == 14.0),
                                  'close_at_13_75': next(s['close'] for s in sweep if s['indus_unit_g'] == 13.75),
                                  'geometric_mean_over_10_to_18g': float(np.mean([s['geometric'] for s in sweep]))}

    # Fine sweep at 0.01 g for 12.5-15 g to show the whole fitted-unit range
    fine = []
    for u in np.round(np.arange(12.5, 15.0001, .01), 3):
        a, b, _, _ = rules(masses, sites, float(u), local_units)
        fine.append((float(u), int(a.sum()), int(b.sum())))
    arr = np.array(fine)
    out['unit_sweep_12_5_to_15'] = {'close_min': int(arr[:, 2].min()), 'close_max': int(arr[:, 2].max()),
                                     'close_mean': float(arr[:, 2].mean()), 'close_at_13_65': int(arr[np.argmin(abs(arr[:, 0] - 13.65)), 2]),
                                     'close_at_14_00': int(arr[np.argmin(abs(arr[:, 0] - 14.0)), 2]),
                                     'geometric_min': int(arr[:, 1].min()), 'geometric_max': int(arr[:, 1].max()),
                                     'fraction_of_units_with_close_ge_18': float((arr[:, 2] >= 18).mean()),
                                     'fraction_of_units_with_close_ge_22': float((arr[:, 2] >= 22).mean()),
                                     'fraction_of_units_with_geometric_ge_136': float((arr[:, 1] >= 136).mean()),
                                     'n_grid_units': int(len(arr))}

    # Composition of the 18: shape/material/class categories (counts only)
    idx = np.where(c)[0]
    comp = {}
    for i in idx:
        r = rows[ids[i] - 1]
        key = f"{r['shape']} / {r['material']}"
        comp[key] = comp.get(key, 0) + 1
    out['close_objects_shape_material_counts'] = comp

    # Where do the observed objects with small masses sit relative to null: split by mass band
    bands = [(0, 2.5), (2.5, 10), (10, 100), (100, 1e7)]
    out['observed_by_band'] = []
    for lo_, hi_ in bands:
        m = (masses >= lo_) & (masses < hi_)
        out['observed_by_band'].append({'band_g': [lo_, hi_], 'n': int(m.sum()), 'geometric': int(g[m].sum()), 'close': int(c[m].sum())})

    (PKG / 'review/western-null.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
