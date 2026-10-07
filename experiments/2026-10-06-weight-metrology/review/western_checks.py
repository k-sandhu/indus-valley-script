"""Reviewer check 3b: alternative standards and the book's own Susa attributions.

(a) Re-scores the 701 western records with canonical fixed local units (7.8, 8.4, 9.4 g) instead of
    site-fitted units, and with an enlarged competitor set (adds 7.83, 11.75 g from the 470 g mina and a
    Dilmun-type 13.5 g list), to show how the 136/18 counts depend on the competitor definition.
(b) Compares the package's close-preference IDs with the Susa weights that Ascalone 2022 (printed pp. 69-70)
    lists as following the Harappan standard and as 'Western group'.
Aggregates only. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/western_checks.py
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
sys.path.insert(0, str(PKG / 'review'))
import analyze  # noqa: E402
INDUS, NE = analyze.INDUS, analyze.NE


def best_err(masses, unit, c):
    x = np.log(masses)
    r = x[:, None] - np.log(c)[None, :] - math.log(unit)
    j = np.argmin(abs(r), axis=1)
    sg = r[np.arange(len(x)), j]
    return abs(sg), abs(np.expm1(sg)), c[j]


def rules(masses, sites, ref, local_units_by_site, local_default, extra=(), threshold=.03):
    i_log, i_err, _ = best_err(masses, ref, INDUS)
    l_log = np.full(len(masses), np.inf)
    l_err = np.full(len(masses), np.inf)
    for s in set(sites):
        sel = np.array([t == s for t in sites])
        units = local_units_by_site.get(s, local_default)
        for name, (u, lst) in list(units.items()) + list(extra):
            lg, er, _ = best_err(masses[sel], u, lst)
            better = lg < l_log[sel]
            idx = np.where(sel)[0]
            l_log[idx[better]] = lg[better]
            l_err[idx[better]] = er[better]
    geo = i_log < l_log
    close = geo & (i_err <= threshold) & (l_err - i_err >= .01)
    return geo, close


def main():
    rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    sel = json.loads((RAW / 'main/selection-ids.json').read_text())
    models = json.loads((PKG / 'runs/2026-10-06-main/model-comparisons.json').read_text())
    ids = sel['western_primary_ids']
    masses = np.array([rows[i - 1]['mass_g'] for i in ids])
    sites = [rows[i - 1]['site'] for i in ids]
    ref = next(f['unit_g'] for f in models['fits'] if f['group'] == 'Dholavira' and f['model'] == 'indus_binary_decimal')
    fitted = {s: {m: (u, NE) for m, u in d.items()} for s, d in models['local_units'].items()}
    canon = {'shekel_7_8': (7.8, NE), 'shekel_8_4': (8.4, NE), 'shekel_9_4': (9.4, NE)}
    out = {'n': len(ids)}

    g, c = rules(masses, sites, ref, fitted, canon)
    out['package_rule_site_fitted_units'] = {'geometric': int(g.sum()), 'close': int(c.sum())}
    g2, c2 = rules(masses, sites, ref, {}, canon)
    out['canonical_fixed_local_units_7_8_8_4_9_4'] = {'geometric': int(g2.sum()), 'close': int(c2.sum()),
                                                      'close_ids_dropped_vs_package': [int(ids[i]) for i in np.where(c & ~c2)[0]],
                                                      'close_ids_added_vs_package': [int(ids[i]) for i in np.where(~c & c2)[0]]}
    canon2 = dict(canon)
    canon2.update({'shekel_7_83': (7.83, NE), 'shekel_8_36': (8.36, NE), 'mina470_over40': (11.75, NE)})
    g3, c3 = rules(masses, sites, ref, {}, canon2)
    out['canonical_plus_7_83_8_36_11_75'] = {'geometric': int(g3.sum()), 'close': int(c3.sum()),
                                              'close_ids': [int(ids[i]) for i in np.where(c3)[0]]}
    # add sexagesimal fractions to the Near Eastern list (1/6, 1/3, 2/3, 5/6, 1/12, 1/24) and 1/5
    ne_plus = np.array(sorted(set(NE.tolist() + [1/24, 1/12, 1/6, 1/5, 1/3, 2/3, 5/6])))
    canon_plus = {k: (u, ne_plus) for k, (u, _) in canon2.items()}
    g4, c4 = rules(masses, sites, ref, {}, canon_plus)
    out['canonical_plus_fractions_1_24_to_5_6_and_1_5'] = {'geometric': int(g4.sum()), 'close': int(c4.sum()),
                                                           'close_ids': [int(ids[i]) for i in np.where(c4)[0]]}
    # same with reference 13.65
    g5, c5 = rules(masses, sites, 13.65, {}, canon_plus)
    out['canonical_plus_fractions_ref_13_65'] = {'geometric': int(g5.sum()), 'close': int(c5.sum())}

    # Ascalone 2022 pp. 69-70 lists (Susa)
    harappan = [34, 35, 81, 82, 224, 233, 324, 487, 499, 504, 601, 628, 680, 694, 698, 699, 700]
    western_group = [20, 70, 80, 220, 530, 669]
    pos = {i: k for k, i in enumerate(ids)}
    detail = []
    for cat in harappan + western_group:
        r = rows[cat - 1]
        rec = {'cat': cat, 'group': 'Ascalone Harappan-standard list' if cat in harappan else 'Ascalone Western group',
               'in_package_primary_701': cat in pos}
        m = np.array([r['mass_g']])
        for lab, u in (('indus_14_003', ref), ('indus_13_65', 13.65)):
            _, e, mult = best_err(m, u, INDUS)
            rec[f'err_{lab}_percent'] = float(100 * e[0]); rec[f'mult_{lab}'] = float(mult[0])
        for lab, u in (('ne_7_83', 7.83), ('ne_8_4', 8.4), ('ne_9_4', 9.4)):
            _, e, mult = best_err(m, u, NE)
            rec[f'err_{lab}_percent'] = float(100 * e[0]); rec[f'mult_{lab}'] = float(mult[0])
        if cat in pos:
            k = pos[cat]
            rec['package_geometric'] = bool(g[k]); rec['package_close'] = bool(c[k])
        detail.append(rec)
    out['ascalone_susa_lists'] = detail
    out['overlap'] = {'harappan_list_n': len(harappan),
                      'harappan_list_in_package_primary': int(sum(1 for d in detail if d['group'].startswith('Ascalone Harappan') and d['in_package_primary_701'])),
                      'harappan_list_package_geometric': int(sum(1 for d in detail if d['group'].startswith('Ascalone Harappan') and d.get('package_geometric'))),
                      'harappan_list_package_close': int(sum(1 for d in detail if d['group'].startswith('Ascalone Harappan') and d.get('package_close'))),
                      'harappan_list_within_3pct_of_indus_14_003': int(sum(1 for d in detail if d['group'].startswith('Ascalone Harappan') and d['err_indus_14_003_percent'] <= 3)),
                      'harappan_list_within_3pct_of_indus_13_65': int(sum(1 for d in detail if d['group'].startswith('Ascalone Harappan') and d['err_indus_13_65_percent'] <= 3)),
                      'western_group_n': len(western_group),
                      'western_group_package_close': int(sum(1 for d in detail if d['group'].endswith('Western group') and d.get('package_close'))),
                      'western_group_cats_in_package_close': [d['cat'] for d in detail if d['group'].endswith('Western group') and d.get('package_close')],
                      'package_close_ids_in_ascalone_harappan_list': [i for i in [int(ids[k]) for k in np.where(c)[0]] if i in harappan]}

    # Local unit boundary status
    out['local_units_at_range_boundary'] = {s: {m: u for m, (u, _) in d.items()} for s, d in fitted.items()}
    (PKG / 'review/western-checks.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'ascalone_susa_lists'}, indent=1))
    for d in detail:
        print(d)


if __name__ == '__main__':
    main()
