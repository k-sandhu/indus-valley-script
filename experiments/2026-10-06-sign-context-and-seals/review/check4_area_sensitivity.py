"""Reviewer check 4: does the area conclusion survive the alternative extents printed in the Treccani site entries?

The package's site table uses the hierarchy paragraph of Kenoyer, Pracchia and Vidale (2005). The same page has
site entries by Vidale with other extents (Harappa about 100 ha, Rakhigarhi over 100 ha, Lothal over 8 ha, Nausharo
about 6 ha, Mohenjo-daro at least 2 x 2 km, Banawali 400 m a side, Kot Diji 200 x 120 m, Surkotada 120 x 60 m).
This script repeats the package's amended test (site labels exchanged among whole objects inside object-type blocks,
Spearman rank correlation between area and the type-adjusted site residual, BH over ten signs) for several area vectors.

Run from the repository root. Writes review/check4-area-sensitivity.json (aggregates only).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv_common import *  # noqa

OUT = PKG / 'review/check4-area-sensitivity.json'
rng = np.random.default_rng(910206)
B = 9999

rows = load_rows()
groups = components(rows)
principal, seals = principal_and_seals(groups)
tok = Counter(s for r in rows for s in r['signs_reading_rtl'])
signs = [s for s, n in sorted(tok.items(), key=lambda kv: (-kv[1], kv[0])) if s != '000'][:10]
rr = [r for r in principal if any(s != '000' for s in r['signs_reading_rtl'])]
cnt = [Counter(s for s in r['signs_reading_rtl'] if s != '000') for r in rr]
Y = np.array([[c[s] for s in signs] for c in cnt], float)
N = np.array([sum(c.values()) for c in cnt], float)
types = [r['object_type'] for r in rr]
strata = blocks(types)
P = np.zeros_like(Y)
for ix in strata:
    P[ix] = Y[ix].sum(0) / N[ix].sum()
D = Y - N[:, None] * P
site_names = sorted({r['site'] for r in rr})
sid = {s: i for i, s in enumerate(site_names)}
lab = np.array([sid[r['site']] for r in rr])
S = len(site_names)
site_n = np.bincount(lab, minlength=S)

table = {t['site']: t for t in json.loads((PKG / 'site-table.json').read_text(encoding='utf-8'))['sites']}
package_ref = {s: t['area_reference'] for s, t in table.items()}
package_ref['Rodji'] = table['Rodji']['area_reference']


def vectors():
    base = dict(package_ref)
    v = {}
    v['A_package_reference'] = dict(base)
    # B: values printed in the Vidale site entries of the same Treccani page (visible or stated extents)
    b = dict(base)
    b.update({'Harappa': 100, 'Mohenjo-daro': 400, 'Rakhigarhi': 100, 'Lothal': 8, 'Nausharo': 6,
              'Kot-Diji': 2.4, 'Surkotada': 0.72, 'Chanhu-daro': 3})
    b['Banawali'] = 16
    v['B_Treccani_site_entries'] = b
    # C and D: lowest and highest value printed anywhere in the compiled sources, hierarchy plus site entries
    lo, hi = dict(base), dict(base)
    lo.update({'Harappa': 100, 'Mohenjo-daro': 100, 'Rakhigarhi': 80, 'Lothal': 7, 'Nausharo': 4, 'Kot-Diji': 1,
               'Surkotada': 0.72, 'Chanhu-daro': 3, 'Kalibangan': 11.5})
    hi.update({'Harappa': 150, 'Mohenjo-daro': 400, 'Rakhigarhi': 100, 'Lothal': 8, 'Nausharo': 6, 'Kot-Diji': 2.4,
               'Surkotada': 2.6, 'Chanhu-daro': 6, 'Kalibangan': 12.1})
    lo['Banawali'] = hi['Banawali'] = 16
    v['C_lowest_printed'] = lo
    v['D_highest_printed'] = hi
    return v


def run(area, min_objects=3):
    sel_sites = [s for s in area if s in sid and site_n[sid[s]] >= min_objects]
    sel = np.array([sid[s] for s in sel_sites])
    ar = rankdata(np.log2([area[s] for s in sel_sites]))
    ar -= ar.mean()

    def stat(l):
        sd = np.stack([np.bincount(l, weights=D[:, j], minlength=S) for j in range(len(signs))], 1)
        nn = np.bincount(l, weights=N, minlength=S)
        R = sd[sel] / nn[sel][:, None]
        Rr = np.apply_along_axis(rankdata, 0, R)
        Rr -= Rr.mean(0)
        den = np.sqrt((ar @ ar) * (Rr * Rr).sum(0))
        return np.divide(ar @ Rr, den, out=np.zeros(len(signs)), where=den > 0)
    obs = stat(lab)
    null = np.array([stat(shuffle_in_blocks(lab, strata, rng)) for _ in range(B)])
    p = np.array([mc_p(obs[j], null[:, j], 'abs') for j in range(len(signs))])
    q = bh(p)
    return {'sites': len(sel_sites), 'site_list': sel_sites, 'rho': dict(zip(signs, obs.round(4).tolist())),
            'p': dict(zip(signs, p.round(4).tolist())), 'q': dict(zip(signs, q.round(4).tolist()))}


res = {}
for name, area in vectors().items():
    res[name] = run(area)
    print(name, res[name]['sites'], 'min q', min(res[name]['q'].values()), 'rho520', res[name]['rho']['520'], 'q520', res[name]['q']['520'])
# omit the two largest cities (package sensitivity) under the alternative vectors
for name, area in vectors().items():
    a2 = {s: v for s, v in area.items() if s not in ('Harappa', 'Mohenjo-daro')}
    res[name + '_without_two_cities'] = run(a2)
    r = res[name + '_without_two_cities']
    print(name + ' without two cities', r['sites'], 'min q', min(r['q'].values()), 'q520', r['q']['520'])
OUT.write_text(json.dumps(res, indent=1) + '\n', encoding='utf-8')
