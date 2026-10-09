"""Reviewer's independent recomputation and post-outcome sensitivities for Package Q.

Run from any directory with the system Python. It reads the pinned inputs listed in
the package manifest and writes review-checks.json next to this file (refuses to
overwrite). Nothing here edits a package file. All sensitivities in sections 4-7 are
reviewer-added, written after the package outcomes were known, and are Exploratory.
Dictionary hits and per-text rows are not written out.
"""
import collections, itertools, json, random, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(r'C:/Users/sandh/OneDrive/Projects/indus_valley_script')
PKG = ROOT / 'experiments/2026-10-08-bonta-review'
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
OUT = PKG / 'review/review-checks.json'
if OUT.exists():
    sys.exit('refusing to overwrite ' + str(OUT))
out = {}

sel = json.load(open(PKG / 'selection.json', encoding='utf8'))
vals, panel, roles = sel['values_slp1'], sel['panel'], list(sel['values_slp1'])

# --- dictionary (Cologne MW at pinned commit); k1 field parsed independently ---------
heads = set()
n_rows = 0
with open(RAW / 'acquisition-2026-10-08-v1/mw.txt', encoding='utf8') as f:
    for line in f:
        i = line.find('<k1>')
        if i >= 0:
            n_rows += 1
            h = line[i + 4:line.find('<', i + 4)]
            if re.fullmatch(r'[A-Za-z]+', h):
                heads.add(h)
out['dictionary'] = {'k1_rows': n_rows, 'distinct_alphabetic_headwords': len(heads)}

def mkmap(groups):
    return {c: g[0] for g in groups for c in g}
VOW = ['aA', 'iI', 'uU', 'fF', 'xX']
LEVELS = {
    'exact': {},
    'vowel_length_only': mkmap(VOW),
    'vowel_length_and_aspiration': mkmap(VOW + ['kK', 'gG', 'cC', 'jJ', 'wW', 'qQ', 'tT', 'dD', 'pP', 'bB']),
    'package_normalization': mkmap(VOW + ['kKgG', 'cCjJ', 'wWqQ', 'tTdD', 'pPbB', 'sSz', 'nR']),
}

def forms(mapping, roles_in_string):
    ch = []
    for i, r in enumerate(roles_in_string):
        v = mapping[r]
        if i > 0:
            v = [x for x in v if not x.lower().startswith('maha')]
        ch.append(v)
    return {''.join(p) for p in itertools.product(*ch)}

# --- 1-3. lexical permutation test and sensitivities ---------------------------------
lex = {}
for level, m in LEVELS.items():
    N = (lambda w, m=m: ''.join(m.get(c, c) for c in w))
    nk = {N(h) for h in heads}
    def score(assign, strings=panel):
        mp = {r: vals[a] for r, a in zip(roles, assign)}
        return sum(any(N(f) in nk for f in forms(mp, it['roles'])) for it in strings)
    allp = list(itertools.permutations(roles))
    sc = {p: score(p) for p in allp}
    obs = sc[tuple(roles)]
    hist = collections.Counter(sc.values())
    pu = roles.index('PU')
    fixed_pu = [p for p in allp if p[pu] == 'PU']
    anchors = ['MA', 'TRA', 'PALA', 'DHANA']
    four = 0
    for perm in itertools.permutations(anchors):
        p = list(roles)
        for a, b in zip(anchors, perm):
            p[roles.index(a)] = b
        four += sc[tuple(p)] >= obs
    lex[level] = {
        'headword_classes': len(nk), 'observed': obs, 'permutation_mean': sum(sc.values()) / 720,
        'histogram': {str(k): v for k, v in sorted(hist.items())},
        'tail': f"{sum(v >= obs for v in sc.values())}/720",
        'tail_with_PU_bundle_kept': f"{sum(sc[p] >= obs for p in fixed_pu)}/{len(fixed_pu)}",
        'tail_permuting_only_MA_TRA_PALA_DHANA': f"{four}/24",
        'tail_assignments_that_do_not_keep_PU': f"{sum(v >= obs for p, v in sc.items() if p[pu] != 'PU')}/{720 - len(fixed_pu)}",
    }
    if level == 'package_normalization':
        # prefix-intersection (L2) check
        def inter(rs):
            pools = []
            for r in rs:
                suf = {N(v) for v in vals[r] if not v.lower().startswith('maha')}
                pools.append({w[:-len(s)] for w in nk for s in suf if w.endswith(s) and len(w) > len(s)})
            return set.intersection(*pools)
        c = inter(['DHANA', 'MA', 'PALA'])
        cnt = [len(inter(x)) for x in itertools.combinations(roles, 3)]
        lex['consistency_intersection'] = {'candidate_classes': len(c), 'PU_class_present': N('BU') in c,
                                           'min_over_20_sets': min(cnt), 'max_over_20_sets': max(cnt),
                                           'candidates_of_two_characters_or_fewer': len([x for x in c if len(x) <= 2])}
out['lexical_independent'] = lex
out['panel_strings_containing_PU_or_PATI'] = f"{sum(('PU' in it['roles'] or 'PATI' in it['roles']) for it in panel)}/{len(panel)}"

# --- 4. distributional recomputation and exceptions -----------------------------------
rows = [json.loads(l) for l in open(ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl', encoding='utf8')]
best = {}
for r in rows:
    g = r['object_family_id']
    k = (-len(r['signs_reading_rtl']), r['record_id'])
    if g not in best or k < best[g][0]:
        best[g] = (k, r)
sel_rows = [v[1] for v in best.values()]
seqs = [r['signs_reading_rtl'] for r in sel_rows]
d = {'objects': len(seqs), 'tokens': sum(map(len, seqs)), 'minimum_length': min(map(len, seqs))}
for sign in ('740', '520'):
    n = sum(s.count(sign) for s in seqs)
    f = sum(s[-1] == sign for s in seqs)
    exp = sum(s.count(sign) / len(s) for s in seqs)
    nonfinal_next = collections.Counter()
    site_nf = collections.Counter()
    for r in sel_rows:
        s = r['signs_reading_rtl']
        nf = [i for i, x in enumerate(s) if x == sign and i != len(s) - 1]
        for i in nf:
            nonfinal_next[s[i + 1]] += 1
        if nf:
            site_nf[r['site']] += 1
    d[sign] = {'occurrences': n, 'final': f, 'final_fraction': f / n,
               'analytic_expected_final_under_within_text_shuffle': exp,
               'nonfinal_occurrences': n - f,
               'nonfinal_followed_by_top5': nonfinal_next.most_common(5),
               'objects_with_nonfinal_by_site_top4': site_nf.most_common(4)}
out['distribution_recomputed'] = d

# --- 5. fish-run power and clustering -------------------------------------------------
fish = {'220', '231', '233', '235', '240', '242'}
def runs(s):
    res, cur = [], []
    for x in s + ['#']:
        if x in fish:
            cur.append(x)
        elif cur:
            res.append(cur)
            cur = []
    return res
obs_runs = [r for s in seqs for r in runs(s)]
per_text = collections.Counter(min(sum(x in fish for x in s), 4) for s in seqs)
multi = [s for s in seqs if sum(x in fish for x in s) >= 2]
rng = random.Random(20261009)
rep_null, adj_null = [], []
def adj(ss):
    return sum(1 for s in ss for i in range(len(s) - 1) if s[i] in fish and s[i + 1] in fish)
for _ in range(2000):
    sh = []
    for s in multi:
        t = s[:]
        rng.shuffle(t)
        sh.append(t)
    rep_null.append(sum(len(set(r)) < len(r) for s in sh for r in runs(s)))
    adj_null.append(adj(sh))
adj_obs = adj(multi)
out['fish_proxy_power'] = {
    'runs': len(obs_runs), 'repeating_runs': sum(len(set(r)) < len(r) for r in obs_runs),
    'runs_longer_than_three': sum(len(r) > 3 for r in obs_runs),
    'fish_code_tokens_per_text_0_1_2_3_4plus': {str(k): v for k, v in sorted(per_text.items())},
    'texts_with_a_fish_code_occurring_twice': sum(any(s.count(c) >= 2 for c in fish) for s in seqs),
    'shuffle_expected_repeating_runs': float(np.mean(rep_null)), 'shuffle_probability_of_zero_repeating_runs': float(np.mean(np.array(rep_null) == 0)),
    'texts_with_at_least_two_fish_tokens': len(multi), 'observed_adjacent_fish_pairs': adj_obs,
    'shuffle_adjacent_pairs_mean': float(np.mean(adj_null)),
    'shuffle_adjacent_pairs_range_95': np.quantile(adj_null, [.025, .975]).tolist(), 'shuffle_adjacent_pairs_max_of_2000': int(max(adj_null)),
    'draws': 2000, 'seed': 20261009,
}

# --- 6. role-pair census and pairs outside the panel ---------------------------------
wells = {'MA': {'704', '705', '706', '707'}, 'TRA': {'033'}, 'PALA': {'390', '392', '405', '406', '407', '408'},
         'DHANA': {'125', '126'}, 'PU': {'590'}, 'PATI': {'817', '861'}}
inv = {c: r for r, cs in wells.items() for c in cs}
pair_obj = collections.defaultdict(set)
for r in sel_rows:
    s = [inv.get(x) for x in r['signs_reading_rtl']]
    for i in range(len(s) - 1):
        if s[i] and s[i + 1]:
            pair_obj[(s[i], s[i + 1])].add(r['object_family_id'])
panel_pairs = {tuple(it['roles']) for it in panel if len(it['roles']) == 2}
m_full = LEVELS['package_normalization']
def exact_match(a, b, mp):
    return any(w in heads for w in forms(mp, [a, b]))
base_map = {r: vals[r] for r in roles}
non_panel = [k for k in pair_obj if k not in panel_pairs]
in_panel = [k for k in pair_obj if k in panel_pairs]
def pair_score(assign, pairs, norm):
    mp = {r: vals[a] for r, a in zip(roles, assign)}
    if norm:
        N = lambda w: ''.join(m_full.get(c, c) for c in w)
        nk = {N(h) for h in heads}
        return sum(any(N(f) in nk for f in forms(mp, list(p))) for p in pairs)
    return sum(exact_match(p[0], p[1], mp) for p in pairs)
res = {'attested_ordered_pair_types': len(pair_obj), 'in_panel': len(in_panel), 'outside_panel': len(non_panel),
       'panel_pairs_matching_exact_under_his_values': sum(exact_match(a, b, base_map) for a, b in in_panel),
       'outside_pairs_matching_exact_under_his_values': sum(exact_match(a, b, base_map) for a, b in non_panel)}
for norm in (False, True):
    obs = pair_score(tuple(roles), non_panel, norm)
    sc = [pair_score(p, non_panel, norm) for p in itertools.permutations(roles)]
    res['outside_panel_' + ('normalized' if norm else 'exact')] = {
        'observed': obs, 'of': len(non_panel), 'permutation_mean': sum(sc) / 720, 'assignments_scoring_at_least_observed': f"{sum(s >= obs for s in sc)}/720"}
out['role_pair_sensitivity'] = res
json.dump(out, open(OUT, 'w', encoding='utf8'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
