"""Reviewer check 3: concentration views, terminal 740 under several nulls, richness, period and external motifs.

Run from the repository root:  python experiments/2026-10-06-sign-context-and-seals/review/check3_concentration_terminal.py
Writes review/check3-post-launch.json (aggregates only).
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import beta

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rv_common import *  # noqa

OUT = PKG / 'review/check3-post-launch.json'
rng = np.random.default_rng(910205)
B = 9999

rows = load_rows()
groups = components(rows)
principal, seals = principal_and_seals(groups)
res = {}

# ------------------------------------------------------------ concentration
def top_shares(texts):
    cnt = Counter(s for t in texts for s in t)
    readable = Counter({s: n for s, n in cnt.items() if s != '000'})
    rank = sorted(readable, key=lambda s: (-readable[s], s))
    out = {}
    for den_name, N in (('all', sum(cnt.values())), ('readable', sum(readable.values()))):
        out[den_name] = {'positions': N, '740': cnt['740'] / N,
                         **{f'top{k}': sum(readable[s] for s in rank[:k]) / N for k in (3, 6, 20)}}
    out['top3_codes'] = rank[:3]
    return out


views = {'all_faces': [r['signs_reading_rtl'] for r in rows],
         'principal': [r['signs_reading_rtl'] for r in principal],
         'unique_full_texts': [list(t) for t in {tuple(r['signs_reading_rtl']) for r in rows if r['signs_reading_rtl']}]}
res['concentration'] = {k: top_shares(v) for k, v in views.items()}
res['unique_text_count'] = len(views['unique_full_texts'])

# ------------------------------------------------------------ terminal 740
clean = [r for r in principal if r['complete_observed'] and r['single_line'] and r['direction'] in {'R/L', 'L/R'}
         and r['signs_reading_rtl'] and '000' not in r['signs_reading_rtl'] and len(r['signs_reading_rtl']) >= 2]
texts = [r['signs_reading_rtl'] for r in clean]
c740 = np.array([t.count('740') for t in texts])
ell = np.array([len(t) for t in texts])
last = np.array([t[-1] == '740' for t in texts])
res['terminal'] = {'objects': len(clean), 'occurrences': int(c740.sum()), 'objects_with_740': int((c740 > 0).sum()),
                   'ending': int(last.sum()), 'fraction_terminal': float(last.sum() / c740.sum()),
                   'ending_rate': float(last.mean()), 'expected_ending_count_uniform_anchor': float((c740 / ell).sum()),
                   'expected_rate': float((c740 / ell).mean())}

# exact Poisson-binomial tail by normal approximation check and by Monte Carlo of within-text shuffles
mu = (c740 / ell).sum()
var = ((c740 / ell) * (1 - c740 / ell)).sum()
res['terminal']['sd_of_expected_count'] = float(np.sqrt(var))
res['terminal']['z_score'] = float((last.sum() - mu) / np.sqrt(var))
sim = np.zeros(2000)
for b in range(2000):
    sim[b] = sum(rng.random() < p for p in (c740 / ell)[c740 > 0])
res['terminal']['shuffle_null_mc_mean_sd'] = [float(sim.mean()), float(sim.std())]

# position profile: share of 740 at each distance from the end, and from the start
prof_end, prof_start = Counter(), Counter()
tot_end, tot_start = Counter(), Counter()
for t in texts:
    for k, s in enumerate(reversed(t)):
        tot_end[k] += 1
        prof_end[k] += s == '740'
    for k, s in enumerate(t):
        tot_start[k] += 1
        prof_start[k] += s == '740'
res['terminal']['rate_740_by_distance_from_end'] = {str(k): [prof_end[k], tot_end[k], prof_end[k] / tot_end[k]] for k in range(5)}
res['terminal']['rate_740_by_position_from_start'] = {str(k): [prof_start[k], tot_start[k], prof_start[k] / tot_start[k]] for k in range(5)}

# by length
bylen = {}
for L in (2, 3, 4, 5, 6, 7, 8):
    ix = ell == L
    bylen[str(L)] = {'objects': int(ix.sum()), 'ending': int(last[ix].sum()), 'expected': float((c740[ix] / L).sum())}
ix = ell >= 9
bylen['9+'] = {'objects': int(ix.sum()), 'ending': int(last[ix].sum()), 'expected': float((c740[ix] / ell[ix]).sum())}
res['terminal']['by_length'] = bylen

# dedup: one object per (site, type, exact text)
seen, dd = set(), []
for r in sorted(clean, key=lambda r: r['record_id']):
    key = (r['site'], r['object_type'], tuple(r['signs_reading_rtl']))
    if key not in seen:
        seen.add(key)
        dd.append(r)
td = [r['signs_reading_rtl'] for r in dd]
cd = np.array([t.count('740') for t in td])
ld = np.array([len(t) for t in td])
lastd = np.array([t[-1] == '740' for t in td])
res['terminal_dedup_site_type_text'] = {'objects': len(dd), 'occurrences': int(cd.sum()), 'ending': int(lastd.sum()),
                                        'fraction_terminal': float(lastd.sum() / cd.sum()),
                                        'ending_rate': float(lastd.mean()), 'expected': float((cd / ld).sum()),
                                        'expected_rate': float((cd / ld).mean())}
# dedup globally by exact text only
seen, dd2 = set(), []
for r in sorted(clean, key=lambda r: r['record_id']):
    key = tuple(r['signs_reading_rtl'])
    if key not in seen:
        seen.add(key)
        dd2.append(r)
td = [r['signs_reading_rtl'] for r in dd2]
cd = np.array([t.count('740') for t in td])
ld = np.array([len(t) for t in td])
lastd = np.array([t[-1] == '740' for t in td])
res['terminal_dedup_global_text'] = {'objects': len(dd2), 'occurrences': int(cd.sum()), 'ending': int(lastd.sum()),
                                     'fraction_terminal': float(lastd.sum() / cd.sum()), 'ending_rate': float(lastd.mean()),
                                     'expected': float((cd / ld).sum()), 'expected_rate': float((cd / ld).mean())}

# direction check: L/R texts
for d in ('R/L', 'L/R'):
    ix = np.array([r['direction'] == d for r in clean])
    res['terminal'][f'direction_{d}'] = {'objects': int(ix.sum()), 'ending': int(last[ix].sum()), 'occurrences': int(c740[ix].sum()),
                                         'starting_with_740': int(sum(t[0] == '740' for t, f in zip(texts, ix) if f))}

# by type with site-by-type composition; and Harappa vs Mohenjo-daro within type
tab = {}
for typ in ['SEAL:S', 'SEAL:R', 'TAB:B', 'TAB:C', 'TAB:I', 'POT:T:g', 'POT:T:s', 'TAG']:
    for site in ['Harappa', 'Mohenjo-daro', 'all']:
        ix = np.array([r['object_type'] == typ and (site == 'all' or r['site'] == site) for r in clean])
        if ix.sum():
            tab[f'{typ}|{site}'] = {'objects': int(ix.sum()), 'occ': int(c740[ix].sum()), 'ending': int(last[ix].sum()),
                                    'expected': float((c740[ix] / ell[ix]).sum())}
res['terminal_type_site'] = tab

# single-sign texts: how many principal objects are single-sign, and how many are 740
single = [r for r in principal if len(r['signs_reading_rtl']) == 1]
res['single_sign_principal'] = {'objects': len(single), 'sign740': sum(r['signs_reading_rtl'] == ['740'] for r in single),
                                'directions': dict(Counter(r['direction'] for r in single))}

# ------------------------------------------------------------ richness: independent re-implementation of the block permutation
rr = [r for r in principal if any(s != '000' for s in r['signs_reading_rtl'])]
sites = sorted({r['site'] for r in rr})
codes = sorted({s for r in rr for s in r['signs_reading_rtl'] if s != '000'})
sid = {s: i for i, s in enumerate(sites)}
cid = {s: i for i, s in enumerate(codes)}
lab = np.array([sid[r['site']] for r in rr])
inc = np.zeros((len(rr), len(codes)), bool)
rl = np.zeros(len(rr), int)
for i, r in enumerate(rr):
    for s in r['signs_reading_rtl']:
        if s != '000':
            inc[i, cid[s]] = True
            rl[i] += 1
oi, si = np.where(inc)
strata = blocks(list(zip([r['object_type'] for r in rr], rl)))
S = len(sites)


def rich(l):
    a = np.bincount(l[oi] * len(codes) + si, minlength=S * len(codes)).reshape(S, len(codes))
    return (a > 0).sum(1)


obs = rich(lab)
nulls = np.array([rich(shuffle_in_blocks(lab, strata, rng)) for _ in range(B)])
mean, sd = nulls.mean(0), nulls.std(0, ddof=1)
elig = [i for i, s in enumerate(sites) if (lab == i).sum() >= 20 and s != 'Unknown']
tests = []
for i in elig:
    p = mc_p(obs[i], nulls[:, i], 'centred')
    tests.append([sites[i], int((lab == i).sum()), int(rl[lab == i].sum()), int(obs[i]), float(mean[i]), float(sd[i]), float((obs[i] - mean[i]) / sd[i]), p])
q = bh([t[-1] for t in tests])
res['richness_independent'] = [dict(zip(['site', 'objects', 'tokens', 'observed', 'null_mean', 'null_sd', 'z', 'p'], t), q=float(qq)) for t, qq in zip(tests, q)]
# share of the pooled reservoir contributed by the two largest sites
res['reservoir_share'] = {s: float((lab == sid[s]).mean()) for s in ('Harappa', 'Mohenjo-daro')}

# rarefaction of Harappa and Mohenjo-daro to the smaller sites' readable token totals (token-level, descriptive)
from math import lgamma, exp


def rarefy(freqs, N, k):
    f = np.array([x for x in freqs if x > 0])
    tot = 0.0
    lden = lgamma(N + 1) - lgamma(k + 1) - lgamma(N - k + 1)
    for fi in f:
        if N - fi >= k:
            tot += 1 - exp(lgamma(N - fi + 1) - lgamma(k + 1) - lgamma(N - fi - k + 1) - lden)
        else:
            tot += 1
    return tot


tokens_by_site = {}
for s in ('Harappa', 'Mohenjo-daro'):
    cnt = Counter(c for r in rr if r['site'] == s for c in r['signs_reading_rtl'] if c != '000')
    tokens_by_site[s] = (list(cnt.values()), sum(cnt.values()))
small = {'Dholavira': 623, 'Kalibangan': 495, 'Lothal': 642, 'Chanhu-daro': 316, 'Nausharo': 131, 'Banawali': 62}
obs_small = {r['site']: r['observed'] for r in res['richness_independent']}
res['rarefied_large_sites_at_small_site_sizes'] = {
    s: {'tokens': k, 'observed': obs_small.get(s), 'harappa_rarefied': rarefy(*tokens_by_site['Harappa'], k),
        'mohenjo_rarefied': rarefy(*tokens_by_site['Mohenjo-daro'], k)} for s, k in small.items()}

# ------------------------------------------------------------ period stability (Harappa square seals)
sqh = [r for r in seals if r['site'] == 'Harappa' and r['object_type'] == 'SEAL:S']
known = [r for r in sqh if motif(r['symbol']) is not None]
per = lambda r: r['metadata'].get('time', '-')
tab = defaultdict(lambda: [0, 0])
for r in known:
    tab[per(r)][1] += 1
    tab[per(r)][0] += motif(r['symbol']) == 'unicorn'
res['period_counts_known'] = {k: v for k, v in sorted(tab.items())}


def clop(k, n, a=.025):
    return (float(beta.ppf(a / 2, k, n - k + 1)) if k else 0., float(beta.ppf(1 - a / 2, k + 1, n - k)) if k < n else 1.)


def counts(pat):
    return [sum(v[1] for k, v in tab.items() if re.fullmatch(pat, k)), sum(v[0] for k, v in tab.items() if re.fullmatch(pat, k))]


nB, uB = counts(r'Period 3B(?:-\d+)?')
nC, uC = counts(r'Period 3C(?:-\d+)?')
nA, uA = tab['Period 3B/C'][1], tab['Period 3B/C'][0]
lo, hi, obsr = 9, -9, []
for ub in range(uA + 1):
    for mb in range(nA - uA + 1):
        nb, kb = nB + ub + mb, uB + ub
        nc, kc = nC + nA - ub - mb, uC + uA - ub
        cb, cc = clop(kb, nb), clop(kc, nc)
        lo, hi = min(lo, cc[0] - cb[1]), max(hi, cc[1] - cb[0])
        obsr.append(kc / nc - kb / nb)
res['period_envelope'] = {'nB_uB': [nB, uB], 'nC_uC': [nC, uC], 'nA_uA': [nA, uA], 'assignments': len(obsr),
                          'observed_range': [min(obsr), max(obsr)], 'envelope': [lo, hi]}
# raw heterogeneity test over labels with >= 10 known motifs
labs = [per(r) for r in known if re.fullmatch(r'Period 3(?:[ABC](?:-\d+)?|B/C)?', per(r)) and per(r) != '-']
ys = np.array([motif(r['symbol']) == 'unicorn' for r in known if re.fullmatch(r'Period 3(?:[ABC](?:-\d+)?|B/C)?', per(r))], int)
labs = np.array(labs)
tested = sorted(s for s, n in Counter(labs).items() if n >= 10)
m = ys.mean()
st = lambda yy: sum((yy[labs == s].sum() - (labs == s).sum() * m) ** 2 / ((labs == s).sum() * m * (1 - m)) for s in tested)
o = st(ys)
nl = np.array([st(rng.permutation(ys)) for _ in range(B)])
res['period_heterogeneity'] = {'objects': len(ys), 'tested_labels': tested, 'stat': float(o), 'p': mc_p(o, nl)}
# same test limited to the four 3C-n subphases (same nominal interval 2200-1900)
sub = [s for s in tested if re.fullmatch(r'Period 3C-\d', s)]
ix = np.isin(labs, sub)
ys2, labs2 = ys[ix], labs[ix]
m2 = ys2.mean()
st2 = lambda yy: sum((yy[labs2 == s].sum() - (labs2 == s).sum() * m2) ** 2 / ((labs2 == s).sum() * m2 * (1 - m2)) for s in sub)
o2 = st2(ys2)
n2 = np.array([st2(rng.permutation(ys2)) for _ in range(B)])
res['period_heterogeneity_within_3C_subphases'] = {'labels': sub, 'objects': int(ix.sum()), 'stat': float(o2), 'p': mc_p(o2, n2)}

# ------------------------------------------------------------ external motifs
CORE = {'Lower Indus', 'Upper Indus', 'Inter-Riverine', 'Eastern Headwaters', 'Gujarat/Kutch'}
EXT = {'Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia'}
BALUCH = {'Miri Qalat', 'Nindowari-damb', 'Ornach area', 'Sibri'}


def ext_test(is_ext, label):
    sel = [r for r in seals if motif(r['symbol']) is not None and (r['region'] in CORE or is_ext(r))]
    l = np.array([int(is_ext(r)) for r in sel])
    u = np.array([motif(r['symbol']) == 'unicorn' for r in sel], int)
    g = np.array([r['symbol'] == 'Gaur' for r in sel], int)
    st = blocks([r['object_type'] for r in sel])
    f = lambda z: np.array([u[z == 0].mean() - u[z == 1].mean(), g[z == 1].mean() - g[z == 0].mean()])
    o = f(l)
    n = np.array([f(shuffle_in_blocks(l, st, rng)) for _ in range(B)])
    p = [mc_p(o[j], n[:, j], 'centred') for j in range(2)]
    return {'label': label, 'core_known': int((l == 0).sum()), 'ext_known': int((l == 1).sum()), 'ext_unicorn': int(u[l == 1].sum()),
            'ext_gaur': int(g[l == 1].sum()), 'observed': o.round(4).tolist(), 'null_mean': n.mean(0).round(4).tolist(),
            'p': np.round(p, 4).tolist(), 'q': bh(p).round(4).tolist()}


res['external_package_definition'] = ext_test(lambda r: r['region'] in EXT, 'all four external regions')
res['external_gulf_mesopotamia'] = ext_test(lambda r: r['region'] in {'Persian Gulf', 'Mesopotamia'}, 'Gulf and Mesopotamia only')
res['external_without_baluchistan_sites'] = ext_test(lambda r: r['region'] in EXT and r['site'] not in BALUCH, 'external, four Balochistan sites dropped from the external class')
# restrict to seals excluding circular types
sel_sq = [r for r in seals if r['object_type'] == 'SEAL:S' and motif(r['symbol']) is not None]
core_sq = [r for r in sel_sq if r['region'] in CORE]
ext_sq = [r for r in sel_sq if r['region'] in EXT]
res['square_seals_only'] = {'core': [len(core_sq), sum(motif(r['symbol']) == 'unicorn' for r in core_sq), sum(r['symbol'] == 'Gaur' for r in core_sq)],
                            'external': [len(ext_sq), sum(motif(r['symbol']) == 'unicorn' for r in ext_sq), sum(r['symbol'] == 'Gaur' for r in ext_sq)]}
gaur_all = Counter((r['object_type'], r['region'] in CORE) for r in seals if r['symbol'] == 'Gaur')
res['gaur_by_type_and_core_flag'] = {f'{k[0]}|core={k[1]}': v for k, v in gaur_all.items()}
res['gaur_faces_with_trough'] = [sum(r['symbol'] == 'Gaur' and r['metadata'].get('cult') == 'Trough' for r in rows), sum(r['symbol'] == 'Gaur' for r in rows)]

OUT.write_text(json.dumps(res, indent=1, default=float) + '\n', encoding='utf-8')
print('written', OUT)
