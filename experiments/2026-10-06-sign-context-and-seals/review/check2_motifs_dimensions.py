"""Reviewer check 2: motif concentration, unicorn versus rare texts, and seal dimensions.

Run from the repository root:  python experiments/2026-10-06-sign-context-and-seals/review/check2_motifs_dimensions.py
Writes review/check2-motifs-dimensions.json (aggregates only).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv_common import *  # noqa

OUT = PKG / 'review/check2-motifs-dimensions.json'
rng = np.random.default_rng(910204)
B = 9999

rows = load_rows()
groups = components(rows)
principal, seals = principal_and_seals(groups)
res = {}

# ---------------- motif concentration
sq = [r for r in seals if r['object_type'] == 'SEAL:S']
known_sq = [r for r in sq if motif(r['symbol']) is not None]
c = Counter(motif(r['symbol']) for r in known_sq)
n = len(known_sq)
hhi = sum((v / n) ** 2 for v in c.values())
res['square'] = {'components': len(sq), 'known': n, 'unicorn': c['unicorn'], 'share': c['unicorn'] / n,
                 'wilson': wilson(c['unicorn'], n), 'categories': len(c), 'hhi': hhi, 'effective': 1 / hhi,
                 'next': c.most_common(9)[1:]}
known_all = [r for r in seals if motif(r['symbol']) is not None]
ca = Counter(motif(r['symbol']) for r in known_all)
na = len(known_all)
res['all_seals'] = {'components': len(seals), 'known': na, 'unicorn': ca['unicorn'], 'share': ca['unicorn'] / na,
                    'hhi': sum((v / na) ** 2 for v in ca.values()), 'unknown': len(seals) - na}
# code sets
res['bull_family_codes_all_faces'] = dict(Counter(r['symbol'] for r in rows if r['symbol'].startswith('Bull')))
res['bull1_variants_in_square_known'] = dict(Counter(r['symbol'] for r in known_sq if r['symbol'].startswith('Bull1')))

# ---------------- clean-text comparison
rare = {k for k, v in ca.items() if k != 'unicorn' and v / na < .05}
res['rare_categories'] = sorted(rare)
valid = [r for r in seals if r['complete_observed'] and r['single_line'] and r['direction'] in {'R/L', 'L/R'}
         and r['signs_reading_rtl'] and '000' not in r['signs_reading_rtl'] and motif(r['symbol']) is not None]
res['eligible_clean_texts'] = len(valid)


def motif_test(objs, B, rng, cond=None, recode=None):
    """Permute the unicorn label inside (site, type[, extra]) blocks; six statistics as in the protocol."""
    lab = np.array([(recode or motif)(r['symbol']) == 'unicorn' for r in objs], int)
    seq = [tuple(r['signs_reading_rtl']) for r in objs]
    vocab = sorted({s for t in seq for s in t})
    idx = {s: i for i, s in enumerate(vocab)}
    A = np.zeros((len(objs), len(vocab)))
    F = A.copy()
    L = A.copy()
    for i, t in enumerate(seq):
        for s in t:
            A[i, idx[s]] += 1
        F[i, idx[t[0]]] = 1
        L[i, idx[t[-1]]] = 1
    tids = {t: i for i, t in enumerate(sorted(set(seq)))}
    ti = np.array([tids[t] for t in seq])
    lengths = A.sum(1)
    sums = [m.sum(0) for m in (A, F, L)]
    keys = [(r['site'], r['object_type']) + ((cond(r),) if cond else ()) for r in objs]
    strata = blocks(keys)

    def stats(l):
        n1 = l.sum()
        n0 = len(l) - n1
        v = [l @ m for m in (A, F, L)]
        tx = np.bincount(ti, weights=l, minlength=len(tids))
        tt = np.bincount(ti, minlength=len(tids))
        return np.array([js_bits(v[0], sums[0] - v[0]), js_bits(v[1], sums[1] - v[1]), js_bits(v[2], sums[2] - v[2]),
                         float(np.count_nonzero(v[0]) - np.count_nonzero(sums[0] - v[0])),
                         np.count_nonzero(tx) / n1 - np.count_nonzero(tt - tx) / n0,
                         l @ lengths / n1 - (1 - l) @ lengths / n0])
    obs = stats(lab)
    null = np.array([stats(shuffle_in_blocks(lab, strata, rng)) for _ in range(B)])
    names = ['js_tokens', 'js_initial', 'js_terminal', 'richness', 'distinct_rate', 'length']
    mode = ['upper'] * 3 + ['abs'] * 3
    p_pkg = np.array([mc_p(obs[j], null[:, j], mode[j]) for j in range(6)])
    p_cen = np.array([mc_p(obs[j], null[:, j], 'centred' if j >= 3 else 'upper') for j in range(6)])
    return {'n1': int(lab.sum()), 'n0': int((1 - lab).sum()), 'blocks': len(strata),
            'mixed_blocks': sum(len(set(lab[ix])) > 1 for ix in strata),
            'movable': int(sum(len(ix) for ix in strata if len(set(lab[ix])) > 1)),
            'observed': dict(zip(names, obs.round(6).tolist())),
            'null_mean': dict(zip(names, null.mean(0).round(5).tolist())),
            'p_package_rule': dict(zip(names, p_pkg.round(4).tolist())),
            'q_package_rule': dict(zip(names, bh(p_pkg).round(4).tolist())),
            'p_centred_two_sided': dict(zip(names, p_cen.round(4).tolist())),
            'q_centred': dict(zip(names, bh(p_cen).round(4).tolist()))}


primary = [r for r in valid if motif(r['symbol']) in rare | {'unicorn'}]
res['primary_counts'] = {'objects': len(primary),
                         'unicorn': sum(motif(r['symbol']) == 'unicorn' for r in primary),
                         'mean_len_unicorn': float(np.mean([len(r['signs_reading_rtl']) for r in primary if motif(r['symbol']) == 'unicorn'])),
                         'mean_len_rare': float(np.mean([len(r['signs_reading_rtl']) for r in primary if motif(r['symbol']) != 'unicorn']))}
res['test_primary_rare'] = motif_test(primary, B, rng)

# exact-length conditioned law (as in the package's exploratory amendment)
res['test_primary_rare_length_conditioned'] = motif_test(primary, B, rng, cond=lambda r: len(r['signs_reading_rtl']))

# dedup: one object per (site, type, class, exact text)
seen, dd = set(), []
for r in sorted(primary, key=lambda r: r['record_id']):
    key = (r['site'], r['object_type'], motif(r['symbol']) == 'unicorn', tuple(r['signs_reading_rtl']))
    if key not in seen:
        seen.add(key)
        dd.append(r)
res['dedup_counts'] = {'objects': len(dd), 'unicorn': sum(motif(r['symbol']) == 'unicorn' for r in dd),
                       'mean_len_unicorn': float(np.mean([len(r['signs_reading_rtl']) for r in dd if motif(r['symbol']) == 'unicorn'])),
                       'mean_len_rare': float(np.mean([len(r['signs_reading_rtl']) for r in dd if motif(r['symbol']) != 'unicorn']))}
res['test_primary_rare_dedup'] = motif_test(dd, B, rng)


# recoding sensitivity: Bull:i variants treated as unicorn
def motif_alt(raw):
    if raw.startswith('Bull1') or raw.startswith('Bull:i'):
        return 'unicorn'
    return None if raw in MISSING_MOTIFS else raw


ca2 = Counter(motif_alt(r['symbol']) for r in seals if motif_alt(r['symbol']) is not None)
rare2 = {k for k, v in ca2.items() if k != 'unicorn' and v / sum(ca2.values()) < .05}
valid2 = [r for r in seals if r['complete_observed'] and r['single_line'] and r['direction'] in {'R/L', 'L/R'}
          and r['signs_reading_rtl'] and '000' not in r['signs_reading_rtl'] and motif_alt(r['symbol']) is not None]
primary2 = [r for r in valid2 if motif_alt(r['symbol']) in rare2 | {'unicorn'}]
res['recode_Bull_i'] = {'objects': len(primary2), 'unicorn': sum(motif_alt(r['symbol']) == 'unicorn' for r in primary2),
                        'test': motif_test(primary2, B, rng, recode=motif_alt)}

# Gaur against unicorn, and Gaur against the rare cohort (descriptive means)
gaur = [r for r in valid if r['symbol'] == 'Gaur']
res['gaur_clean_texts'] = {'objects': len(gaur), 'mean_len': float(np.mean([len(r['signs_reading_rtl']) for r in gaur]))}

# ---------------- dimensions
def pos(x):
    try:
        v = float(x)
        return v if np.isfinite(v) and v > 0 else None
    except (TypeError, ValueError):
        return None


dim = []
for r in sq:
    h, v = pos(r['metadata'].get('horizontal(mm)')), pos(r['metadata'].get('vertical(mm)'))
    dim.append((r, h, v))
comp = [(r, h, v) for r, h, v in dim if h and v and r['metadata'].get('preservation') == 'complete']
size = np.array([(h * v) ** .5 for r, h, v in comp])
res['dimensions'] = {'square_components': len(sq), 'both_positive': sum(1 for r, h, v in dim if h and v),
                     'complete_both': len(comp), 'mean': float(size.mean()), 'sd': float(size.std(ddof=1)),
                     'cv': float(size.std(ddof=1) / size.mean()), 'median': float(np.median(size)),
                     'min': float(size.min()), 'max': float(size.max())}


# unit audit: raw h/v versus mm
def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


units = Counter()
for r, h, v in comp:
    m = r['metadata']
    for raw, mm in (('h', 'horizontal(mm)'), ('v', 'vertical(mm)')):
        a, b = num(m.get(raw)), num(m.get(mm))
        s = str(m.get(raw, ''))
        if a and a > 0 and b and b > 0:
            ratio = b / a
            units['inch_x25.4' if 24 <= ratio <= 27 else 'raw_is_mm' if .9 <= ratio <= 1.1 else 'raw_is_cm' if 9 <= ratio <= 11 else 'inconsistent'] += 1
        elif s.endswith('cm') and b:
            units['cm_string_x10' if abs(b - 10 * float(s[:-2] or 0)) < 1.5 else 'cm_string_inconsistent'] += 1
        elif s == '':
            units['mm_only_no_raw'] += 1
        else:
            units['other_raw:' + re.sub(r'[0-9.]+', '#', s)] += 1
res['dimension_unit_audit_complete_squares'] = dict(units)

# sensitivity: recover zero-mm entries from raw inches/cm when mm is zero but raw is positive
def raw_mm(m, raw):
    s = str(m.get(raw, '')).strip()
    if s.endswith('cm'):
        x = num(s[:-2])
        return x * 10 if x and x > 0 else None
    x = num(s)
    return x * 25.4 if x and x > 0 else None


rec = []
for r in sq:
    m = r['metadata']
    if m.get('preservation') != 'complete':
        continue
    h = pos(m.get('horizontal(mm)')) or raw_mm(m, 'h')
    v = pos(m.get('vertical(mm)')) or raw_mm(m, 'v')
    if h and v:
        rec.append((h * v) ** .5)
rec = np.array(rec)
res['dimensions_with_raw_recovery'] = {'n': len(rec), 'cv': float(rec.std(ddof=1) / rec.mean()), 'mean': float(rec.mean())}

# slope test: length ~ log2(area) adjusted for site and motif; permute length within (site, motif, type)
motifs = [motif(r['symbol']) or 'unknown_or_absent' for r, h, v in comp]
sites = [r['site'] for r, h, v in comp]
types = [r['object_type'] for r, h, v in comp]
lengths = np.array([len(r['signs_reading_rtl']) for r, h, v in comp], float)
la = np.log2(np.array([h * v for r, h, v in comp]))


def dummies(vals):
    lv = sorted(set(vals))
    return np.array([[1.0] + [float(v == l) for l in lv[1:]] for v in vals])


Xs, Xm = dummies(sites), dummies(motifs)
Z = np.column_stack([Xs, Xm[:, 1:]])
rx = la - Z @ np.linalg.lstsq(Z, la, rcond=None)[0]
den = rx @ rx
slope = float(rx @ lengths / den)
strata = blocks(list(zip(sites, motifs, types)))
null = np.array([rx @ shuffle_in_blocks(lengths, strata, rng) / den for _ in range(B)])
res['slope'] = {'n': len(comp), 'slope_per_doubling_area': slope, 'null_mean': float(null.mean()),
                'p_uncentred_abs': mc_p(slope, null, 'abs'), 'p_centred': mc_p(slope, null, 'centred'),
                'movable_blocks_objects': int(sum(len(ix) for ix in strata if len(set(lengths[ix])) > 1))}

# slope with raw-equivalent unit recovery is not repeated; check slope within the biggest site only
for site in ['Mohenjo-daro', 'Harappa']:
    ix = np.array([s == site for s in sites])
    if ix.sum() > 30:
        res['slope_site_' + site] = {'n': int(ix.sum()), 'spearman_len_vs_area': float(
            np.corrcoef(np.argsort(np.argsort(la[ix])), np.argsort(np.argsort(lengths[ix])))[0, 1])}

# length by face-area tercile (descriptive)
q = np.quantile(la, [1 / 3, 2 / 3])
res['mean_length_by_area_tercile'] = [float(lengths[la <= q[0]].mean()), float(lengths[(la > q[0]) & (la <= q[1])].mean()), float(lengths[la > q[1]].mean())]

# CV test unicorn versus rare, centred and uncentred
mot = np.array([motif(r['symbol']) for r, h, v in comp], dtype=object)
isrc = np.array([m == 'unicorn' or (m in rare) for m in mot])
sel = [i for i in range(len(comp)) if isrc[i]]
y = np.array([mot[i] == 'unicorn' for i in sel], int)
sz = size[sel]
keys = [(sites[i], types[i]) for i in sel]
strata = blocks(keys)
cv = lambda a: a.std(ddof=1) / a.mean()
obs = cv(sz[y == 1]) - cv(sz[y == 0])
nul = np.array([(lambda l: cv(sz[l == 1]) - cv(sz[l == 0]))(shuffle_in_blocks(y, strata, rng)) for _ in range(B)])
res['cv_unicorn_minus_rare'] = {'unicorn': int(y.sum()), 'rare': int((1 - y).sum()), 'observed': float(obs),
                                'null_mean': float(nul.mean()), 'p_uncentred_abs': mc_p(obs, nul, 'abs'),
                                'p_centred': mc_p(obs, nul, 'centred')}

OUT.write_text(json.dumps(res, indent=1, default=float) + '\n', encoding='utf-8')
print('written', OUT)
