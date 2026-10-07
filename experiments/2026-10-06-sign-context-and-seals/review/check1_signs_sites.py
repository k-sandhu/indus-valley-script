"""Reviewer check 1: corpus totals, site frequencies, the site omnibus test and dedup sensitivities.

Run from the repository root:  python experiments/2026-10-06-sign-context-and-seals/review/check1_signs_sites.py
Writes review/check1-signs-sites.json (aggregates only).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv_common import *  # noqa

OUT = PKG / 'review/check1-signs-sites.json'
rng = np.random.default_rng(910203)  # reviewer seed, different from the package's
B = 9999

rows = load_rows()
groups = components(rows)
principal, seals = principal_and_seals(groups)
res = {}

tok = Counter(s for r in rows for s in r['signs_reading_rtl'])
res['totals'] = {'faces': len(rows), 'positions': sum(tok.values()), 'unreadable_000': tok['000'],
                 'readable': sum(tok.values()) - tok['000'], 'sign740': tok['740'],
                 'share740_all': tok['740'] / sum(tok.values()),
                 'share740_readable': tok['740'] / (sum(tok.values()) - tok['000']),
                 'components': len(groups), 'principal': len(principal), 'seal_components': len(seals),
                 'components_multi_site': sum(len({r['site'] for r in g}) > 1 for g in groups),
                 'components_multi_type': sum(len({r['object_type'] for r in g}) > 1 for g in groups)}
signs = [s for s, n in sorted(tok.items(), key=lambda kv: (-kv[1], kv[0])) if s != '000'][:10]
res['top10'] = {s: tok[s] for s in signs}

# unresolved CISI-like references
unres = [r['source_cisi'] for r in rows if (r.get('source_cisi') or '').strip() not in {'', '-', '--'}
         and not re.fullmatch(r'([A-Za-z][A-Za-z0-9]*-\d+)[A-Za-z]?', r['source_cisi'].strip())]
res['unresolved_nonblank_cisi'] = len(unres)

# ---- site frequencies, all faces, readable denominators; component bootstrap
by_site = defaultdict(list)
for g in groups:
    for site in {r['site'] for r in g}:
        by_site[site].append([r for r in g if r['site'] == site])
site_rows = {}
for site in ['Harappa', 'Mohenjo-daro', 'Dholavira', 'Kalibangan', 'Lothal', 'Chanhu-daro', 'Nausharo', 'Banawali']:
    comp = by_site[site]
    y = np.array([sum(s == '740' for r in c for s in r['signs_reading_rtl']) for c in comp], float)
    n = np.array([sum(s != '000' for r in c for s in r['signs_reading_rtl']) for c in comp], float)
    w = rng.multinomial(len(comp), np.repeat(1 / len(comp), len(comp)), size=2000)
    vals = (w @ y) / np.maximum(w @ n, 1)
    site_rows[site] = {'components': len(comp), 'count740': int(y.sum()), 'readable': int(n.sum()),
                       'freq': float(y.sum() / n.sum()),
                       'ci95': [float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]}
res['site_table_740'] = site_rows


# ---- site omnibus
def omnibus(objs, B, rng, drop_unknown=False, label=''):
    objs = [r for r in objs if any(s != '000' for s in r['signs_reading_rtl'])]
    cnt = [Counter(s for s in r['signs_reading_rtl'] if s != '000') for r in objs]
    Y = np.array([[c[s] for s in signs] for c in cnt], float)
    N = np.array([sum(c.values()) for c in cnt], float)
    types = [r['object_type'] for r in objs]
    strata = blocks(types)
    P = np.zeros_like(Y)
    for ix in strata:
        P[ix] = Y[ix].sum(0) / N[ix].sum()
    E = N[:, None] * P
    V = N[:, None] * P * (1 - P)
    D = Y - E
    site_n = Counter(r['site'] for r in objs)
    elig = sorted(s for s, c in site_n.items() if c >= 20 and not (drop_unknown and s == 'Unknown'))
    lab = np.array([elig.index(r['site']) if r['site'] in elig else -1 for r in objs])
    K = len(elig)

    def stat(l):
        out = np.zeros(len(signs))
        for j in range(len(signs)):
            d = np.bincount(l + 1, weights=D[:, j], minlength=K + 1)[1:]
            v = np.bincount(l + 1, weights=V[:, j], minlength=K + 1)[1:]
            out[j] = np.divide(d * d, v, out=np.zeros(K), where=v > 0).sum()
        return out
    obs = stat(lab)
    null = np.array([stat(shuffle_in_blocks(lab, strata, rng)) for _ in range(B)])
    p = np.array([mc_p(obs[j], null[:, j]) for j in range(len(signs))])
    q = bh(p)
    return {'label': label, 'objects': len(objs), 'eligible_sites': elig, 'stat': obs.round(3).tolist(),
            'p': p.round(4).tolist(), 'q': q.round(4).tolist()}


res['omnibus_package_definition'] = omnibus(principal, B, rng, label='principal faces, as in package')
res['omnibus_without_Unknown'] = omnibus(principal, B, rng, drop_unknown=True, label='drop the Unknown label')

# dedup (site, type, exact text) -> one object per distinct inscription within site and type
seen, dedup = set(), []
for r in sorted(principal, key=lambda r: r['record_id']):
    if not any(s != '000' for s in r['signs_reading_rtl']):
        continue
    key = (r['site'], r['object_type'], tuple(r['signs_reading_rtl']))
    if key not in seen:
        seen.add(key)
        dedup.append(r)
res['omnibus_dedup_site_type_text'] = omnibus(dedup, B, rng, label='one object per (site, type, exact text)')
res['dedup_object_count'] = len(dedup)

# ---- sign 032 at Chanhu-daro: how many distinct texts carry it
ch = [r for r in principal if r['site'] == 'Chanhu-daro' and '032' in r['signs_reading_rtl']]
texts = Counter(tuple(r['signs_reading_rtl']) for r in ch)
res['chanhu_daro_032'] = {'objects_with_032': len(ch), 'distinct_texts': len(texts),
                          'tokens_032': sum(r['signs_reading_rtl'].count('032') for r in ch),
                          'largest_repeated_text_objects': max(texts.values()),
                          'types': dict(Counter(r['object_type'] for r in ch))}
kb = [r for r in principal if r['site'] == 'Kalibangan' and '032' in r['signs_reading_rtl']]
res['kalibangan_032'] = {'objects_with_032': len(kb), 'tokens_032': sum(r['signs_reading_rtl'].count('032') for r in kb)}

OUT.write_text(json.dumps(res, indent=1) + '\n', encoding='utf-8')
print(json.dumps({k: res[k] for k in ['totals', 'top10', 'unresolved_nonblank_cisi', 'chanhu_daro_032', 'kalibangan_032', 'dedup_object_count']}, indent=1))
for k in ['omnibus_package_definition', 'omnibus_without_Unknown', 'omnibus_dedup_site_type_text']:
    print(k, res[k]['label'], res[k]['objects'], res[k]['eligible_sites'])
    print('   p', res[k]['p'])
    print('   q', res[k]['q'])
print(json.dumps(res['site_table_740'], indent=0))
