"""Reviewer check 5: the length-per-doubling-of-face-area slope after collapsing repeated inscriptions.
Run from the repository root. Writes review/check5-slope-dedup.json (aggregates only)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv_common import *  # noqa
rng = np.random.default_rng(910207)
rows = load_rows(); groups = components(rows); principal, seals = principal_and_seals(groups)
def pos(x):
    try:
        v = float(x); return v if np.isfinite(v) and v > 0 else None
    except (TypeError, ValueError): return None
comp = []
for r in sorted(seals, key=lambda r: r['record_id']):
    if r['object_type'] != 'SEAL:S' or r['metadata'].get('preservation') != 'complete': continue
    h, v = pos(r['metadata'].get('horizontal(mm)')), pos(r['metadata'].get('vertical(mm)'))
    if h and v: comp.append((r, h * v))
def slope_test(items, B=9999):
    motifs = [motif(r['symbol']) or 'unknown_or_absent' for r, a in items]
    sites = [r['site'] for r, a in items]
    L = np.array([len(r['signs_reading_rtl']) for r, a in items], float)
    la = np.log2([a for r, a in items])
    def dum(vals):
        lv = sorted(set(vals)); return np.array([[1.0] + [float(v == l) for l in lv[1:]] for v in vals])
    Z = np.column_stack([dum(sites), dum(motifs)[:, 1:]])
    rx = la - Z @ np.linalg.lstsq(Z, la, rcond=None)[0]; den = rx @ rx
    s = float(rx @ L / den)
    st = blocks(list(zip(sites, motifs, [r['object_type'] for r, a in items])))
    null = np.array([rx @ shuffle_in_blocks(L, st, rng) / den for _ in range(B)])
    return {'n': len(items), 'slope': s, 'p_uncentred': mc_p(s, null, 'abs'), 'p_centred': mc_p(s, null, 'centred'),
            'movable': int(sum(len(ix) for ix in st if len(set(L[ix])) > 1))}
out = {'all_complete_squares': slope_test(comp)}
seen, dd = set(), []
for r, a in comp:
    key = (r['site'], tuple(r['signs_reading_rtl']))
    if key not in seen:
        seen.add(key); dd.append((r, a))
out['one_per_site_and_exact_text'] = slope_test(dd)
(Path(__file__).resolve().parent / 'check5-slope-dedup.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1))
