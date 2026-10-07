"""Reviewer check of numbers quoted in README.md and REPORT.md against saved endpoints.

Reads only the package's saved aggregate outputs. Each check states the quoted value
(as printed in the document), the field it should come from, and the value found.
Run from the repository root:
  python -B experiments/2026-10-06-chronology-region/review/check_numbers.py
Prints one line per check and a summary.
"""
import json, csv, math, re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
M = PKG / 'main-2026-10-07-v1'
X = PKG / 'exploratory-2026-10-07-v1'
P = PKG / 'post-launch-2026-10-07-v1'
C = PKG / 'post-launch-coverage-2026-10-07-v1'

def J(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def T(p):
    with open(p, encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

results = []
def _eq(c, a, decimals):
    if isinstance(c, (list, tuple)) or isinstance(a, (list, tuple)):
        c, a = list(c), list(a)
        return len(c) == len(a) and all(_eq(x, y, decimals) for x, y in zip(c, a))
    if isinstance(c, dict) and isinstance(a, dict):
        return c.keys() == a.keys() and all(_eq(c[k], a[k], decimals) for k in c)
    if isinstance(c, (str, bool)) or isinstance(a, (str, bool)) or c is None or a is None:
        return c == a
    if isinstance(c, int) and isinstance(a, int):
        return c == a
    if decimals is not None:
        return abs(a - c) <= 0.5 * 10 ** (-decimals) + 1e-12
    return abs(a - c) <= 1e-9

def chk(where, label, claimed, actual, decimals=None):
    """claimed: value as printed in the document; actual: value computed from the saved file.
    decimals: printed precision. Sequence elements that are floats use the same precision (default 5)."""
    if decimals is None and isinstance(claimed, (list, tuple, dict)): decimals = 5
    ok = _eq(claimed, actual, decimals)
    results.append((ok, where, label, claimed, actual))
    return ok

# ---------------------------------------------------------------- inputs
audit = J(M / 'audit.json')
pop = audit['population']
chk('README para 2', 'faces', 5680, pop['faces'])
chk('README para 2', 'known tokens', 18067, pop['known_tokens'])
chk('README para 2', 'unreadable slots', 1879, pop['unreadable_tokens'])
chk('README para 2', 'observed slots', 19946, pop['observed_slots'])
chk('README para 2', 'physical families (object_family_id count)', 4695, len({json.loads(l)['object_family_id'] for l in open(PKG.parents[1] / 'data/normalized/lipi_observed_faces.jsonl', encoding='utf-8')}))
chk('REPORT corpus', 'known graphic codes', 713, audit['vocabulary_known_signs'])
chk('REPORT corpus', 'clear ordered faces', 2930, pop['clear_faces'])
chk('REPORT corpus', 'largest physical component (faces)', 7, audit['largest_physical_component'])
chk('REPORT corpus', 'largest text closure component (faces)', 1038, audit['largest_text_component'])
chk('README', 'main elapsed seconds', 375.22, audit['elapsed_seconds'], decimals=2)
actual_fold = J(X / 'actual_fold_counts.json')
ct = [f['clear_tokens'] for f in actual_fold]
chk('REPORT corpus', 'clear tokens per fold min', 2331, min(ct)); chk('REPORT corpus', 'clear tokens per fold max', 2455, max(ct))

# region table (REPORT 'Corpus and selection')
rt = T(M / 'region_type_strata.csv')
reg = {}
for r in rt:
    d = reg.setdefault(r['region'], dict(faces=0, known=0, unread=0, clear=0))
    d['faces'] += int(r['faces']); d['known'] += int(r['known_tokens']); d['unread'] += int(r['unreadable_tokens']); d['clear'] += int(r['clear_faces'])
claimed_region = {'Inter-Riverine': (2950, 7734, 913, 1418), 'Lower Indus': (2098, 8431, 588, 1286), 'Gujarat/Kutch': (489, 1450, 320, 164),
                  'Eastern Headwaters': (65, 168, 25, 28), 'Upper Indus': (6, 9, 0, 0), 'Persian Gulf': (17, 57, 4, 7), 'Mesopotamia': (11, 42, 9, 4),
                  'Iranian Plateau': (11, 38, 6, 3), 'Central Asia': (3, 12, 0, 2), 'Other': (28, 124, 12, 18), 'South India': (2, 2, 2, 0)}
for k, v in claimed_region.items():
    d = reg[k]
    chk('REPORT region table', k, v, (d['faces'], d['known'], d['unread'], d['clear']))

# Harappa label groups
ht = T(M / 'harappa_major_type_strata.csv')
hg = {}
for r in ht:
    d = hg.setdefault(r['major'], dict(faces=0, known=0, unread=0, clear=0))
    d['faces'] += int(r['faces']); d['known'] += int(r['known_tokens']); d['unread'] += int(r['unreadable_tokens']); d['clear'] += int(r['clear_faces'])
claimed_h = {'1': (2, 4, 1, 0), '2': (30, 36, 8, 2), '3A': (1, 1, 0, 0), '3B': (201, 461, 57, 82), '3C': (574, 1849, 151, 321), '4': (27, 89, 13, 14), '5': (9, 32, 2, 5),
             'interval': (1095, 2691, 268, 589), 'undated': (778, 2015, 296, 348)}
for k, v in claimed_h.items():
    d = hg[k]; chk('REPORT Harappa label table', k, v, (d['faces'], d['known'], d['unread'], d['clear']))
pm = {r['label']: r['faces'] for r in J(M / 'period_mapping.json')}
chk('REPORT 1', '3B/C face count', 873, pm['Period 3B/C']); chk('REPORT records', 'broad Period 3 faces', 222, pm['Period 3'])
alls = T(M / 'all_site_time_strata.csv')
nonH = sum(int(r['faces']) for r in alls if r['site'] != 'Harappa' and r['time'] not in ('-', ''))
chk('REPORT 1', 'non-Harappa faces with time values', 1128, nonH)

# ---------------------------------------------------------------- time
tc = {x['comparison']: x for x in J(M / 'time_comparisons.json')}
t = tc['3B__3C']
chk('REPORT 1', '3B faces readable', 191, t['a']['faces']); chk('REPORT 1', '3B families', 115, t['a']['physical_components'])
chk('REPORT 1', '3C faces readable', 561, t['b']['faces']); chk('REPORT 1', '3C families', 442, t['b']['physical_components'])
chk('REPORT 1', 'common support faces 3B', 186, t['common_support_a']['faces']); chk('REPORT 1', 'common support faces 3C', 451, t['common_support_b']['faces'])
chk('REPORT 1', 'common support tokens 3B', 455, t['common_support_a']['known_tokens']); chk('REPORT 1', 'common support tokens 3C', 1547, t['common_support_b']['known_tokens'])
chk('REPORT 1', 'common types', ['SEAL:S', 'TAB:B', 'TAB:I'], t['common_types'])
chk('REPORT 1/README', 'raw JS', 0.20208, t['raw']['frequency_js_bits']['effect'], 5)
chk('REPORT 1', 'raw JS common support', 0.19223, t['raw_common_support']['frequency_js_bits']['effect'], 5)
chk('REPORT 1/README', 'equal-type JS', 0.19048, t['type_adjusted']['frequency_js_bits']['effect'], 5)
chk('REPORT 1', 'raw length increase', 0.88376, t['raw']['mean_length_b_minus_a']['effect'], 5)
chk('REPORT 1', 'raw length CI low', 0.62465, t['raw']['mean_length_b_minus_a']['ci95'][0], 5); chk('REPORT 1', 'raw length CI high', 1.13957, t['raw']['mean_length_b_minus_a']['ci95'][1], 5)
chk('REPORT 1', 'adjusted length increase', 0.72395, t['type_adjusted']['mean_length_b_minus_a']['effect'], 5)
chk('REPORT 1', 'adjusted length CI low', 0.36473, t['type_adjusted']['mean_length_b_minus_a']['ci95'][0], 5); chk('REPORT 1', 'adjusted length CI high', 1.04572, t['type_adjusted']['mean_length_b_minus_a']['ci95'][1], 5)
chk('REPORT 1', 'clear faces 3B', 82, t['a']['clear_faces']); chk('REPORT 1', 'clear faces 3C', 321, t['b']['clear_faces'])
chk('REPORT 1', 'raw initial JS', 0.43713, t['raw']['initial_js_bits']['effect'], 5); chk('REPORT 1', 'raw terminal JS', 0.20262, t['raw']['terminal_js_bits']['effect'], 5)
chk('REPORT 1', 'equal-type initial JS', 0.40179, t['type_adjusted']['initial_js_bits']['effect'], 5); chk('REPORT 1', 'equal-type terminal JS', 0.17349, t['type_adjusted']['terminal_js_bits']['effect'], 5)
chk('REPORT 1', 'positional types', ['TAB:B', 'TAB:I'], t['positional_common_types'])
chk('REPORT 1', 'frozen percentile interval adjusted JS low', 0.20486, t['type_adjusted']['frequency_js_bits']['ci95'][0], 5)
chk('REPORT 1', 'frozen percentile interval adjusted JS high', 0.27897, t['type_adjusted']['frequency_js_bits']['ci95'][1], 5)
pt = J(M / 'permutation_tests.json')
def ptest(cmp_, unit): return next(x for x in pt if x['comparison'] == cmp_ and x['unit'] == unit)
a = ptest('3B__3C', 'physical_component')
chk('REPORT 1', 'family p', 0.022, a['p'], 3); chk('REPORT 1/README', 'family Holm', 0.044, a['holm_p'], 3)
chk('REPORT 1', 'family test faces/families 3B', (186, 110), (a['a']['faces'], a['a']['physical_components'])); chk('REPORT 1', 'families 3C (permutation population)', 335, a['b']['physical_components'])
b = ptest('3B__3C', 'full_text_closure')
chk('REPORT 1', 'text closure 3B faces', 89, b['a']['faces']); chk('REPORT 1', 'text closure 3C faces', 148, b['b']['faces'])
chk('REPORT 1', 'text closure JS', 0.30164, b['effect_js_bits'], 5); chk('REPORT 1/README', 'text closure p', 0.068, b['p'], 3); chk('REPORT 1', 'text closure Holm', 0.068, b['holm_p'], 3)
c2 = ptest('2__3C', 'physical_component')
chk('REPORT 1', '2-3C faces', (29, 13), (c2['a']['faces'], c2['b']['faces'])); chk('REPORT 1', '2-3C JS', 0.61781, c2['effect_js_bits'], 5); chk('REPORT 1', '2-3C Holm', 0.044, c2['holm_p'], 3)
chk('REPORT 1', '2-3B common types empty', [], ptest('2__3B', 'physical_component')['common_types'])
sx = X / 'sequence_summary.json'
if sx.exists():
    ss = J(sx)
    per = {p['period']: p for p in ss['periods']}
    chk('REPORT 1', 'conditional bigram entropy 3B', 0.89853, per['3B']['raw']['conditional_bigram_entropy_bits'], 5)
    chk('REPORT 1', 'conditional bigram entropy 3C', 1.88940, per['3C']['raw']['conditional_bigram_entropy_bits'], 5)
    chk('REPORT 1', 'equal-type entropy 3B', 0.59844, per['3B']['equal_type_mean_conditional_bigram_entropy_bits'], 5)
    chk('REPORT 1', 'equal-type entropy 3C', 0.83227, per['3C']['equal_type_mean_conditional_bigram_entropy_bits'], 5)
ti = {x['comparison']: x for x in J(X / 'time_intervals.json')}['3B__3C']
chk('REPORT 1', 'basic interval adjusted JS low', 0.11003, ti['type_adjusted']['frequency_js_bits']['basic_centered_interval95'][0], 5)
chk('REPORT 1', 'basic interval adjusted JS high', 0.17814, ti['type_adjusted']['frequency_js_bits']['basic_centered_interval95'][1], 5)
chk('REPORT 1', 'basic interval initial low', 0.24914, ti['type_adjusted']['initial_js_bits']['basic_centered_interval95'][0], 5)
chk('REPORT 1', 'basic interval initial high', 0.41986, ti['type_adjusted']['initial_js_bits']['basic_centered_interval95'][1], 5)
chk('REPORT 1', 'basic interval terminal low', 0.03712, ti['type_adjusted']['terminal_js_bits']['basic_centered_interval95'][0], 5)
chk('REPORT 1', 'basic interval terminal high', 0.19070, ti['type_adjusted']['terminal_js_bits']['basic_centered_interval95'][1], 5)

ints = J(M / 'interval_sensitivity.json')
chk('REPORT interval', 'all 3B/C to 3B JS', 0.13475, ints['all_3BC_to_3B']['effects']['frequency_js_bits'], 5)
chk('REPORT interval', 'all 3B/C to 3C JS', 0.18036, ints['all_3BC_to_3C']['effects']['frequency_js_bits'], 5)
env = ints['uniform_allocation']['metric_envelopes']['frequency_js_bits']
chk('REPORT interval', 'uniform allocation min', 0.09727, env['min'], 5); chk('REPORT interval', 'uniform allocation max', 0.14236, env['max'], 5)
chk('REPORT interval', 'allocation draws', 100, ints['uniform_allocation']['draws'])

att = T(M / 'harappa_attestation_bounds.csv')
chk('REPORT attestation', 'signs in attestation table', 368, len(att))
chk('REPORT attestation', 'earliest unresolved', 209, sum(r['earliest_observed_lo'] != r['earliest_observed_hi'] for r in att))
chk('REPORT attestation', 'latest unresolved', 89, sum(r['latest_observed_lo'] != r['latest_observed_hi'] for r in att))
chk('REPORT attestation', 'first appear unambiguously in 3C', 88, sum(r['earliest_observed_lo'] == r['earliest_observed_hi'] == '3C' for r in att))
last3b = [r for r in att if r['latest_observed_lo'] == r['latest_observed_hi'] == '3B']
chk('REPORT attestation', 'last appear in 3B', ['062', '074', '222', '242', '327'], sorted(r['sign'] for r in last3b))
chk('REPORT attestation', 'families for those five', [1, 1, 2, 2, 1], [int(r['physical_components_bearing_sign']) for r in sorted(last3b, key=lambda r: r['sign'])])
pres = T(M / 'harappa_component_presence.csv')
r015 = next(r for r in pres if r['sign'] == '015' and r['period'] == '3B')
chk('REPORT attestation', '015 absent in 3B families (n)', 115, int(r015['components'])); chk('REPORT attestation', '015 3B one-sided bound %', 2.5713, 100 * float(r015['zero_count_one_sided95_upper']), 4)
r015a = next(r for r in pres if r['sign'] == '015' and r['period'] == '3A')
chk('REPORT attestation', '015 3A bound %', 95.0, round(100 * float(r015a['zero_count_one_sided95_upper']), 1))

st = T(M / 'sign_tests.csv')
tm = [s for s in st if s['theme'] == 'time']; rg = [s for s in st if s['theme'] == 'region']
chk('README', 'time sign tests', 24, len(tm)); chk('README', 'regional sign tests', 314, len(rg)); chk('README/brief', 'total sign tests', 338, len(st))
chk('README', 'sign tests with BH q<.05 (time)', 0, sum(float(s['bh_q']) < .05 for s in tm)); chk('README', 'sign tests with BH q<.05 (region)', 0, sum(float(s['bh_q']) < .05 for s in rg))
chk('REPORT 1', 'smallest time q', 0.072, min(float(s['bh_q']) for s in tm), 3)
low = sorted(s['sign'] for s in tm if abs(float(s['bh_q']) - min(float(x['bh_q']) for x in tm)) < 1e-9)
chk('REPORT 1', 'signs with smallest q', ['034', '390'], low)
s034 = next(s for s in tm if s['sign'] == '034')
chk('REPORT 1', '034 equal-type change (percentage points)', -2.3405, 100 * float(s034['type_adjusted_b_minus_a']), 4)
chk('REPORT 1', '034 CI low', -3.8178, 100 * float(s034['ci95_low']), 4); chk('REPORT 1', '034 CI high', -0.9469, 100 * float(s034['ci95_high']), 4)

# ---------------------------------------------------------------- region
rc = {x['comparison']: x for x in J(M / 'region_comparisons.json')}
rows = [('Inter-Riverine__Lower Indus', 1896, 1709, .14980, .15155, .26829, .012, .240),
        ('Inter-Riverine__Gujarat/Kutch', 1761, 416, .20194, .22092, .31997, .012, .060),
        ('Inter-Riverine__Eastern Headwaters', 748, 45, .33003, .40308, .53201, .012, .072),
        ('Lower Indus__Gujarat/Kutch', 1525, 268, .12475, .18556, .28458, .076, .162),
        ('Lower Indus__Eastern Headwaters', 1275, 45, .28811, .42717, .41888, .012, .012),
        ('Gujarat/Kutch__Eastern Headwaters', 181, 45, .29668, .44717, .42438, .076, .240)]
for name, fa, fb, raw, eq, st_, hf, ht_ in rows:
    r = rc[name]
    chk('REPORT 2 table', name + ' faces A/B', (fa, fb), (r['common_support_a']['faces'], r['common_support_b']['faces']))
    chk('REPORT 2 table', name + ' raw JS', raw, r['raw']['frequency_js_bits']['effect'], 5)
    chk('REPORT 2 table', name + ' equal-type JS', eq, r['type_adjusted']['frequency_js_bits']['effect'], 5)
    chk('REPORT 2 table', name + ' site/type JS', st_, r['site_type_adjusted']['frequency_js_bits']['effect'], 5)
    chk('REPORT 2 table', name + ' family Holm', hf, ptest(name, 'physical_component')['holm_p'], 3)
    chk('REPORT 2 table', name + ' text-closure Holm', ht_, ptest(name, 'full_text_closure')['holm_p'], 3)
fam_pass = [n for n, *_ in rows if ptest(n, 'physical_component')['holm_p'] < .05]; txt_pass = [n for n, *_ in rows if ptest(n, 'full_text_closure')['holm_p'] < .05]
chk('README', 'family-reference regional pairs passing Holm .05', 4, len(fam_pass)); chk('README', 'text-closure regional pairs passing Holm .05', 1, len(txt_pass))
chk('REPORT 2', 'only pair passing both', ['Lower Indus__Eastern Headwaters'], sorted(set(fam_pass) & set(txt_pass)))
frozen_valid = [rc[n]['site_type_adjusted']['frequency_js_bits']['valid_bootstraps'] for n, *_ in rows]
chk('REPORT 2', 'frozen site-balanced valid draws, first/second/fourth', (3, 1, 1), (frozen_valid[0], frozen_valid[1], frozen_valid[3]))
ri = {x['comparison']: x for x in J(X / 'region_intervals.json')}
claimed_basic = {'Inter-Riverine__Lower Indus': (0.20110, 0.26414), 'Inter-Riverine__Gujarat/Kutch': (0.25593, 0.31671), 'Inter-Riverine__Eastern Headwaters': (0.43880, 0.55751),
                 'Lower Indus__Gujarat/Kutch': (0.21456, 0.28101), 'Lower Indus__Eastern Headwaters': (0.30932, 0.43145), 'Gujarat/Kutch__Eastern Headwaters': (0.30920, 0.44662)}
for n, (lo, hi) in claimed_basic.items():
    v = ri[n]['site_type_adjusted']['frequency_js_bits']['basic_centered_interval95']
    chk('REPORT 2', n + ' basic interval low', lo, v[0], 5); chk('REPORT 2', n + ' basic interval high', hi, v[1], 5)
rar = {x['comparison']: x for x in J(M / 'rarefaction.json')}
ir = rar['Inter-Riverine__Lower Indus']['type_adjusted']
chk('REPORT 2', 'IR-LI rarefied mean JS', 0.17591, ir['mean_js_bits'], 5); chk('REPORT 2', 'IR-LI rarefaction low', 0.16224, ir['simulation_interval95'][0], 5); chk('REPORT 2', 'IR-LI rarefaction high', 0.18962, ir['simulation_interval95'][1], 5)
bud = list(ir['token_budgets'].values()); chk('REPORT 2', 'IR-LI type budgets min', 35, min(bud)); chk('REPORT 2', 'IR-LI type budgets max', 1457, max(bud))
eh = rar['Inter-Riverine__Eastern Headwaters']['type_adjusted']['token_budgets']
chk('REPORT 2', 'EH budgets (pottery, square seal)', (29, 79), (eh['POT:T:g'], eh['SEAL:S']))
# positional table
claimed_pos = {'Inter-Riverine__Lower Indus': (861, 1037, .35525, .31988, .34892, .21410, .50049, .36455),
               'Inter-Riverine__Gujarat/Kutch': (292, 127, .45212, .44888, .49917, .41510, .53196, .46096),
               'Inter-Riverine__Eastern Headwaters': (215, 19, .67062, .48678, .66765, .36800, .61696, .53169),
               'Lower Indus__Gujarat/Kutch': (954, 114, .34906, .24709, .34567, .26159, .57432, .32568),
               'Lower Indus__Eastern Headwaters': (825, 19, .57424, .36596, .64898, .39956, .67119, .47004),
               'Gujarat/Kutch__Eastern Headwaters': (80, 19, .58242, .39023, .73355, .39894, .68167, .23318)}
for n, v in claimed_pos.items():
    r = rc[n]; pa = r['positional_common_types']
    # adjusted clear faces: clear faces within positional common types
    import numpy as np
    chk('REPORT 2 positional', n + ' raw initial/terminal', (v[2], v[3]), (round(r['raw']['initial_js_bits']['effect'], 5), round(r['raw']['terminal_js_bits']['effect'], 5)))
    chk('REPORT 2 positional', n + ' eq-type initial/terminal', (v[4], v[5]), (round(r['type_adjusted']['initial_js_bits']['effect'], 5), round(r['type_adjusted']['terminal_js_bits']['effect'], 5)))
    chk('REPORT 2 positional', n + ' site/type initial/terminal', (v[6], v[7]), (round(r['site_type_adjusted']['initial_js_bits']['effect'], 5), round(r['site_type_adjusted']['terminal_js_bits']['effect'], 5)))
ri1 = ri['Inter-Riverine__Lower Indus']['site_type_adjusted']
chk('REPORT 2', 'IR-LI initial basic interval', (0.36632, 0.51662), tuple(round(x, 5) for x in ri1['initial_js_bits']['basic_centered_interval95']))
chk('REPORT 2', 'IR-LI terminal basic interval', (0.24891, 0.43690), tuple(round(x, 5) for x in ri1['terminal_js_bits']['basic_centered_interval95']))
chk('REPORT 2', 'regional sign tests passing', 0, sum(float(s['bh_q']) < .05 for s in rg))

# ---------------------------------------------------------------- models
rm = {x['region']: x for x in J(M / 'regional_models.json')}
mi = {x['region']: x for x in J(X / 'model_intervals.json')}
claimed_models = {'Inter-Riverine': (861, 668, 6.65469, 7.29329, 0.63860, (0.53459, 0.75535), 0.26346, (0.09530, 0.37548)),
                  'Lower Indus': (1037, 1008, 7.10144, 7.37572, 0.27428, (0.11884, 0.44392), 0.18223, (0.03222, 0.33147)),
                  'Gujarat/Kutch': (114, 114, 7.58400, 6.51644, -1.06756, (-1.48527, -0.62911), -0.03030, (-0.18635, 0.15856))}
for n, v in claimed_models.items():
    r = rm[n]['adjusted']; i = mi[n]['losses']
    chk('REPORT held-out', n + ' faces', v[0], r['test']['faces']); chk('REPORT held-out', n + ' families', v[1], r['test']['physical_components'])
    chk('REPORT held-out', n + ' within bits', v[2], r['losses']['type_within']['mean'], 5); chk('REPORT held-out', n + ' other bits', v[3], r['losses']['type_other']['mean'], 5)
    chk('REPORT held-out/README', n + ' excess', v[4], r['losses']['type_excess']['mean'], 5)
    chk('REPORT held-out', n + ' interval', v[5], tuple(round(x, 5) for x in i['type_excess']['ci95']))
    chk('REPORT held-out/README', n + ' size-matched excess', v[6], r['losses']['size_excess']['mean'], 5)
    chk('REPORT held-out', n + ' size-matched interval', v[7], tuple(round(x, 5) for x in i['size_excess']['ci95']))
claimed_raw = {'Inter-Riverine': 0.22941, 'Lower Indus': 0.68615, 'Gujarat/Kutch': -0.58101}
for n, v in claimed_raw.items(): chk('REPORT held-out', n + ' raw token-weighted excess', v, rm[n]['raw']['losses']['raw_excess']['token_weighted_mean'], 5)
ls = {s['site']: s for s in rm['Inter-Riverine']['within_region_leave_site_out'] + rm['Lower Indus']['within_region_leave_site_out']}
chk('REPORT held-out', 'Harappa leave-site-out type-model bits', 8.01667, ls['Harappa']['type_mean_bits'], 5); chk('REPORT held-out', 'Harappa faces', 188, ls['Harappa']['test']['faces']); chk('REPORT held-out', 'Harappa training faces', 47, ls['Harappa']['train']['faces'])
chk('REPORT held-out', 'Mohenjo-daro bits', 7.51130, ls['Mohenjo-daro']['type_mean_bits'], 5); chk('REPORT held-out', 'Mohenjo-daro faces', 770, ls['Mohenjo-daro']['test']['faces']); chk('REPORT held-out', 'Mohenjo-daro training faces', 65, ls['Mohenjo-daro']['train']['faces'])

# ---------------------------------------------------------------- external (original)
em = J(M / 'external_models.json')
chk('REPORT 3', 'external faces', 42, em['external_all']['faces']); chk('REPORT 3', 'external known tokens', 149, em['external_all']['known_tokens']); chk('REPORT 3', 'external unreadable slots', 19, em['external_all']['unreadable_tokens'])
chk('REPORT 3', 'clear external faces', 16, em['external_eligible']['faces']); chk('REPORT 3/README', 'matched faces', 7, em['matched_faces']); chk('REPORT 3', 'excluded faces', 9, em['excluded_faces'])
byr = {x['region']: x['faces'] for x in em['by_region']}
chk('REPORT 3', 'matched by region', {'Persian Gulf': 3, 'Mesopotamia': 1, 'Iranian Plateau': 1, 'Central Asia': 2}, byr)
res = em['results']
chk('REPORT 3', 'pooled external bits', 7.47287, res['raw_loss']['mean'], 5); chk('REPORT 3', 'pooled matched-core bits', 7.55918, res['raw_core_loss']['mean'], 5)
chk('REPORT 3', 'pooled excess', -0.08632, res['raw_excess']['mean'], 5); chk('REPORT 3', 'pooled excess CI', (-2.20257, 2.22760), tuple(round(x, 5) for x in res['raw_excess']['ci95']))
chk('REPORT 3', 'exact-type external bits', 7.87617, res['type_loss']['mean'], 5); chk('REPORT 3', 'exact-type core bits', 7.22528, res['type_core_loss']['mean'], 5)
chk('REPORT 3/README', 'exact-type excess', 0.65090, res['type_excess']['mean'], 5); chk('REPORT 3/README', 'exact-type excess CI', (-0.37986, 1.85719), tuple(round(x, 5) for x in res['type_excess']['ci95']))
chk('REPORT 3', 'sign-flip p', 0.380, res['type_excess']['sign_flip_p'], 3); chk('REPORT 3', 'Holm', 1.000, res['type_excess']['holm_p'], 3)
chk('REPORT 3', 'leave-one-out range', (0.22658, 0.98220), tuple(round(x, 5) for x in res['type_excess']['leave_one_component_out_range']))
chk('REPORT 3', 'bigram novelty excess', 0.05269, res['type_novel2_excess']['mean'], 5); chk('REPORT 3', 'bigram CI', (-0.17347, 0.27994), tuple(round(x, 5) for x in res['type_novel2_excess']['ci95']))
chk('REPORT 3', 'trigram novelty excess', 0.10629, res['type_novel3_excess']['mean'], 5); chk('REPORT 3', 'trigram CI', (-0.10270, 0.26747), tuple(round(x, 5) for x in res['type_novel3_excess']['ci95']))
chk('REPORT 3', 'trigram objects', 4, res['type_novel3_excess']['faces']); chk('REPORT 3', 'bigram objects', 7, res['type_novel2_excess']['faces'])

# ---------------------------------------------------------------- post-launch
tcnt = T(P / 'external_target_counts.csv')
def trow(pop_, target): return next(r for r in tcnt if r['population'] == pop_ and r['target'] == target)
chk('README/REPORT PL', '090 external tokens', 7, int(trow('external_all', 'man_090')['target_tokens'])); chk('README/REPORT PL', 'external known tokens', 149, int(trow('external_all', 'man_090')['known_tokens']))
chk('README/REPORT PL', '090 core tokens', 184, int(trow('core_all', 'man_090')['target_tokens'])); chk('README/REPORT PL', 'core known tokens', 17792, int(trow('core_all', 'man_090')['known_tokens']))
chk('README/REPORT PL', '090 external %', 4.69799, 100 * 7 / 149, 5); chk('README/REPORT PL', '090 core %', 1.03417, 100 * 184 / 17792, 5)
chk('README/REPORT PL', '091 external tokens', 5, int(trow('external_all', 'twins_091')['target_tokens'])); chk('README/REPORT PL', '091 core tokens', 22, int(trow('core_all', 'twins_091')['target_tokens']))
chk('README/REPORT PL', '091 external %', 3.35570, 100 * 5 / 149, 5); chk('README/REPORT PL', '091 core %', 0.12365, 100 * 22 / 17792, 5)
chk('REPORT PL', 'union external', 12, int(trow('external_all', 'primary_union')['target_tokens'])); chk('REPORT PL', 'union core', 206, int(trow('core_all', 'primary_union')['target_tokens']))
chk('REPORT PL', 'expanded union external', 14, int(trow('external_all', 'expanded_union')['target_tokens'])); chk('REPORT PL', 'expanded union core', 231, int(trow('core_all', 'expanded_union')['target_tokens']))
chk('REPORT PL', 'core faces/known/unreadable', (5608, 17792, 1846), (int(trow('core_all', 'man_090')['faces']), int(trow('core_all', 'man_090')['known_tokens']), int(trow('core_all', 'man_090')['unreadable_tokens'])))
chk('REPORT PL', 'core families', 4624, int(trow('core_all', 'man_090')['physical_components']))
ef = J(P / 'external_frequency.json')
chk('README/REPORT PL', 'matched external faces', 7, ef['matched_external']['faces']); chk('README/REPORT PL', 'matched external tokens', 30, ef['matched_external']['known_tokens'])
chk('REPORT PL', 'matched core faces', 958, ef['matched_core']['faces']); chk('REPORT PL', 'matched core families', 881, ef['matched_core']['physical_components']); chk('REPORT PL', 'matched core tokens', 3042, ef['matched_core']['known_tokens'])
chk('REPORT PL', 'target tokens in matched external', 0, sum(int(trow('external_matched', t)['target_tokens']) for t in ['man_090', 'twins_091', 'primary_union', 'modified_man', 'expanded_twins', 'expanded_union']))
r090 = ef['results']['man_090']; r091 = ef['results']['twins_091']
chk('README/REPORT PL', '090 raw matched excess pp', -0.47174, 100 * r090['raw_excess'], 5); chk('README/REPORT PL', '090 type excess pp', -0.28739, 100 * r090['type_excess'], 5)
chk('REPORT PL', '090 interval pp', (-0.55029, -0.06202), tuple(round(100 * x, 5) for x in r090['intervals95']['type_excess']))
chk('REPORT PL', '091 raw matched excess pp', -0.01842, 100 * r091['raw_excess'], 5); chk('README/REPORT PL', '091 type excess pp', -0.01228, 100 * r091['type_excess'], 5)
chk('REPORT PL', '091 interval pp', (-0.07366, 0.0), tuple(round(100 * x, 5) for x in r091['intervals95']['type_excess']))
refs = {x['unit']: x for x in ef['grouped_references']}
chk('REPORT PL', 'physical reference 7 vs 950', (7, 950), (refs['physical']['a']['faces'], refs['physical']['b']['faces'])); chk('REPORT PL', 'text reference 7 vs 630', (7, 630), (refs['text']['a']['faces'], refs['text']['b']['faces']))
chk('README/REPORT PL', 'primary targets Holm p (physical, text)', (1.0, 1.0, 1.0, 1.0), tuple(round(refs[u]['tests'][t]['holm_p'], 3) for u in ['physical', 'text'] for t in ['man_090', 'twins_091']))
chk('REPORT PL', 'all four alternative sensitivities Holm 1.0', True, all(round(refs[u]['tests'][t]['holm_p'], 3) == 1.0 for u in ['physical', 'text'] for t in ['primary_union', 'modified_man', 'expanded_twins', 'expanded_union']))
sel = T(C / 'external_selection_counts.csv')
circ = [r for r in sel if r['type'] == 'SEAL:C']
chk('README/REPORT PL', 'all 090 tokens on SEAL:C', 7, sum(int(r['target_tokens']) for r in circ if r['sign'] == '090')); chk('README/REPORT PL', 'all 091 tokens on SEAL:C', 5, sum(int(r['target_tokens']) for r in circ if r['sign'] == '091'))
chk('README/REPORT PL', 'all external 090 tokens (selection table)', 7, sum(int(r['target_tokens']) for r in sel if r['sign'] == '090')); chk('README/REPORT PL', 'all external 091 tokens (selection table)', 5, sum(int(r['target_tokens']) for r in sel if r['sign'] == '091'))

mc = J(P / 'media_comparison.json'); eff = mc['effects']
chk('README/REPORT PL', 'family counts 3B/3C', (115, 444), (mc['family_counts']['3B'], mc['family_counts']['3C'])); chk('README/REPORT PL', 'common budget', 115, mc['family_budget'])
chk('REPORT PL', 'raw richness diff', 9, eff['raw_richness_difference']['effect']); chk('REPORT PL', 'raw richness interval', (6, 10), tuple(eff['raw_richness_difference']['interval95']))
chk('REPORT PL', 'raw Shannon diff', 0.96728, eff['raw_shannon_difference_bits']['effect'], 5); chk('REPORT PL', 'raw Shannon interval', (0.73868, 1.20538), tuple(round(x, 5) for x in eff['raw_shannon_difference_bits']['interval95']))
chk('README/REPORT PL', 'rarefied richness diff', 4.59846, eff['rarefied_richness_difference']['effect'], 5); chk('README/REPORT PL', 'rarefied richness interval', (3.19136, 6.14341), tuple(round(x, 5) for x in eff['rarefied_richness_difference']['interval95']))
chk('README/REPORT PL', 'richness Holm p', 0.0145, eff['rarefied_richness_difference']['holm_p'], 4); chk('REPORT PL', 'richness one-sided p', 0.0145, eff['rarefied_richness_difference']['one_sided_p'], 4)
chk('README/REPORT PL', 'rarefied Shannon diff', 0.90105, eff['rarefied_shannon_difference_bits']['effect'], 5); chk('README/REPORT PL', 'Shannon interval', (0.67707, 1.14435), tuple(round(x, 5) for x in eff['rarefied_shannon_difference_bits']['interval95']))
chk('README/REPORT PL', 'Shannon Holm p', 0.001, eff['rarefied_shannon_difference_bits']['holm_p'], 3); chk('REPORT PL', 'Shannon one-sided p', 0.0005, eff['rarefied_shannon_difference_bits']['one_sided_p'], 4)
sens = mc['sensitivities']
chk('REPORT PL', 'broad classes richness/entropy', (1.36929, 0.84439), (round(sens['broad_media_classes']['effects']['rarefied_richness_difference'], 5), round(sens['broad_media_classes']['effects']['rarefied_shannon_difference_bits'], 5)))
chk('REPORT PL', 'excluding MISC/SEAL families', (114, 437), (sens['excluding_uncertain_types']['a_families'], sens['excluding_uncertain_types']['b_families']))
chk('REPORT PL', 'excluding MISC/SEAL effects', (4.31981, 0.87710), (round(sens['excluding_uncertain_types']['effects']['rarefied_richness_difference'], 5), round(sens['excluding_uncertain_types']['effects']['rarefied_shannon_difference_bits'], 5)))
chk('REPORT PL', 'readable families', (115, 442), (sens['readable_families_only']['a_families'], sens['readable_families_only']['b_families']))
chk('REPORT PL', 'readable families effects', (4.41908, 0.89114), (round(sens['readable_families_only']['effects']['rarefied_richness_difference'], 5), round(sens['readable_families_only']['effects']['rarefied_shannon_difference_bits'], 5)))
msum = {r['period']: r for r in T(P / 'media_period_summary.csv')}
claimed_media = {'1': (2, 2, 4, 1, 1, 0.0), '2': (30, 30, 36, 8, 2, 0.21084), '3A': (1, 1, 1, 0, 1, 0.0), '3B': (115, 201, 461, 57, 5, 1.56323), '3C': (444, 574, 1849, 151, 14, 2.53051),
                 '4': (22, 27, 89, 13, 5, 1.83837), '5': (7, 9, 32, 2, 3, 1.55666), 'interval': (696, 1095, 2691, 268, 13, 2.13667), 'undated': (604, 778, 2015, 296, 18, 2.71609)}
for k, v in claimed_media.items():
    r = msum[k]
    chk('REPORT PL media table', k, v, (int(r['physical_families']), int(r['faces']), int(r['known_tokens']), int(r['unreadable_tokens']), int(r['type_richness']), round(float(r['shannon_bits']), 5)))
chk('REPORT PL', 'face-weighted entropies 3B/3C', (1.36965, 2.43094), (round(float(msum['3B']['face_weighted_shannon_bits']), 5), round(float(msum['3C']['face_weighted_shannon_bits']), 5)))
al = T(P / 'media_interval_allocations.csv')
u = [r for r in al if r['scenario'].startswith('uniform_')]
chk('README/REPORT PL', 'uniform allocations', 200, len(u)); chk('README/REPORT PL', 'all positive rarefied differences', True, all(float(r['rarefied_richness_difference']) > 0 and float(r['rarefied_shannon_difference_bits']) > 0 for r in u))
chk('REPORT PL', 'allocation richness range', (0.31791, 6.03857), (round(min(float(r['rarefied_richness_difference']) for r in u), 5), round(max(float(r['rarefied_richness_difference']) for r in u), 5)))
chk('REPORT PL', 'allocation entropy range', (0.34160, 0.67971), (round(min(float(r['rarefied_shannon_difference_bits']) for r in u), 5), round(max(float(r['rarefied_shannon_difference_bits']) for r in u), 5)))
sc = {r['scenario']: r for r in al}
chk('REPORT PL', 'all 3B/C -> 3B richness', 2.97206, float(sc['all_3BC_to_3B']['rarefied_richness_difference']), 5); chk('REPORT PL', 'all 3B/C -> 3C richness', 3.95976, float(sc['all_3BC_to_3C']['rarefied_richness_difference']), 5)

ei = J(P / 'early_inventory.json'); rf = ei['raw_family_reference']
chk('README/REPORT PL', 'early families', 31, rf['early_physical_families']); chk('README/REPORT PL', 'early known tokens', 37, rf['early']['known_tokens']); chk('README/REPORT PL', 'early faces', 31, rf['early']['faces'])
chk('README/REPORT PL', 'early signs', 18, rf['early_inventory']); chk('REPORT PL', 'early unreadable slots', 8, rf['early']['unreadable_tokens']); chk('REPORT PL', 'early clear faces', 2, rf['early']['clear_faces'])
chk('REPORT PL', 'later families', 557, rf['later_physical_families']); chk('REPORT PL', 'later faces', 773, rf['later']['faces']); chk('REPORT PL', 'later tokens', 2310, rf['later']['known_tokens']); chk('REPORT PL', 'later unreadable', 206, rf['later']['unreadable_tokens'])
chk('REPORT PL', 'early/later text components', (22, 375), (rf['early']['text_components'], rf['later']['text_components']))
chk('README/REPORT PL', 'later sample mean inventory', 63.01051, rf['later_sample_mean_inventory'], 5); chk('REPORT PL', 'exact expectation', 62.81308, rf['later_exact_expected_inventory'], 5)
chk('REPORT PL', 'sampling spread', (52, 74.05), tuple(round(x, 2) for x in rf['later_sample_interval95'])); chk('REPORT PL', 'deviation', -45.01051, rf['early_minus_later_sample_mean'], 5)
chk('REPORT PL', 'plus-one lower-tail fraction', 0.0005, rf['lower_tail_fraction_plus_one'], 4)
chk('README/REPORT PL', 'later sample known tokens mean', 128.97599, rf['later_sample_known_token_mean'], 5); chk('REPORT PL', 'token spread', (105, 155), tuple(rf['later_sample_known_token_interval95']))
tr = ei['token_rarefaction']; chk('REPORT PL', 'token budget', 37, tr['known_token_budget']); chk('REPORT PL', 'token-rarefied inventories', (18.0, 26.61569), (round(tr['expected_inventories']['early'], 5), round(tr['expected_inventories']['later'], 5)))
ad = ei['adjusted']
chk('REPORT PL', 'type adjust early/later families', (29, 17), (ad['type']['selected_early_families'], ad['type']['selected_later_families']))
chk('REPORT PL', 'type adjust expected', (12.61970, 20.0), (round(ad['type']['expected_early_inventory'], 5), round(ad['type']['expected_later_inventory'], 5)))
chk('REPORT PL', 'type adjust diff/interval', (-7.38030, -8.37439, 1.90768), (round(ad['type']['early_minus_later'], 5), round(ad['type']['interval95'][0], 5), round(ad['type']['interval95'][1], 5)))
chk('REPORT PL', 'type adjust p/Holm', (0.0215, 0.043), (round(ad['type']['one_sided_p'], 4), round(ad['type']['holm_p'], 3)))
tl_ = ad['type_length']
chk('README/REPORT PL', 'type-length families', (27, 12), (tl_['selected_early_families'], tl_['selected_later_families'])); chk('README/REPORT PL', 'type-length budget', 12, tl_['total_sample_budget'])
chk('README/REPORT PL', 'type-length expected', (10.12019, 10.0), (round(tl_['expected_early_inventory'], 5), round(tl_['expected_later_inventory'], 5)))
chk('README/REPORT PL', 'type-length diff', (0.12019, -1.43545, 4.16580), (round(tl_['early_minus_later'], 5), round(tl_['interval95'][0], 5), round(tl_['interval95'][1], 5)))
chk('README/REPORT PL', 'type-length p/Holm', (0.5335, 0.5335), (round(tl_['one_sided_p'], 4), round(tl_['holm_p'], 4)))
chk('REPORT PL', 'type lost early/later', (2, 540), (ad['type']['lost_early_families'], ad['type']['lost_later_families'])); chk('REPORT PL', 'type-length lost early/later', (4, 545), (tl_['lost_early_families'], tl_['lost_later_families']))
chk('REPORT PL', 'text-component sensitivity type', (20, 12, -6.49195, 0.157), (ad['type']['text_component_sensitivity']['early_families'], ad['type']['text_component_sensitivity']['later_families'], round(ad['type']['text_component_sensitivity']['effect'], 5), round(ad['type']['text_component_sensitivity']['holm_p'], 3)))
chk('REPORT PL', 'text-component sensitivity type-length', (18, 7, 0.10159, 0.646), (tl_['text_component_sensitivity']['early_families'], tl_['text_component_sensitivity']['later_families'], round(tl_['text_component_sensitivity']['effect'], 5), round(tl_['text_component_sensitivity']['holm_p'], 3)))
p1 = ei['period1_added']; chk('REPORT PL', 'Period 1 added families/inventory', (33, 19), (p1['early_families'], p1['early_inventory']))
ea = T(P / 'early_interval_allocations.csv'); sca = {r['scenario']: r for r in ea}
chk('REPORT PL', 'broad Period 3 -> 3A families/inventory', (190, 105), (int(sca['all_broad3_to_3A']['early_families']), int(sca['all_broad3_to_3A']['early_inventory'])))
chk('REPORT PL', 'broad Period 3 -> 3C families/inventory', (31, 18), (int(sca['all_broad3_to_3C']['early_families']), int(sca['all_broad3_to_3C']['early_inventory'])))
uni = [r for r in ea if r['scenario'].startswith('uniform_')]
chk('REPORT PL', 'uniform early families range', (71, 102), (min(int(r['early_families']) for r in uni), max(int(r['early_families']) for r in uni)))
chk('REPORT PL', 'uniform early inventory range', (41, 73), (min(int(r['early_inventory']) for r in uni), max(int(r['early_inventory']) for r in uni)))
chk('REPORT PL', 'uniform deviation range', (-65.21993, -33.49715), (round(min(float(r['early_minus_expected_later']) for r in uni), 5), round(max(float(r['early_minus_expected_later']) for r in uni), 5)))
chk('README', 'post-launch elapsed seconds', 51.10, J(P / 'audit.json')['elapsed_seconds'], decimals=2)

# ---------------------------------------------------------------- additional derived quantities
claimed_pos_faces = {'Inter-Riverine__Lower Indus': (861, 1037), 'Inter-Riverine__Gujarat/Kutch': (292, 127), 'Inter-Riverine__Eastern Headwaters': (215, 19),
                     'Lower Indus__Gujarat/Kutch': (954, 114), 'Lower Indus__Eastern Headwaters': (825, 19), 'Gujarat/Kutch__Eastern Headwaters': (80, 19)}
for n, v in claimed_pos_faces.items():
    chk('REPORT 2 positional table', n + ' adjusted clear faces A/B', v, (rc[n]['sensitivity']['clear']['a']['faces'], rc[n]['sensitivity']['clear']['b']['faces']))
chk('README PL', 'expected 3C richness at 115 families (5 + 4.59846)', 9.59846, 5 + eff['rarefied_richness_difference']['effect'], 5)
chk('REPORT PL', 'expected 3C Shannon at 115 families (1.56323 + 0.90105)', 2.46428, float(msum['3B']['shannon_bits']) + eff['rarefied_shannon_difference_bits']['effect'], 5)
chk('REPORT PL', 'union percentages 090+091 external/core', (8.05369, 1.15782), (100 * 12 / 149, 100 * 206 / 17792), 5)
chk('REPORT PL', 'expanded union percentages external/core', (9.39597, 1.29834), (100 * 14 / 149, 100 * 231 / 17792), 5)
chk('REPORT PL', 'media bootstrap draws saved', 999, len(J(PKG.parents[1] / 'data/raw/2026-10-06-chronology-region/post-launch-2026-10-07-v1/media_draws.json')['bootstrap']))
chk('REPORT PL', 'media permutation allocations saved', 1999, len(J(PKG.parents[1] / 'data/raw/2026-10-06-chronology-region/post-launch-2026-10-07-v1/media_draws.json')['permutation']))
chk('REPORT PL', 'external bootstrap draws saved', 1999, len(J(PKG.parents[1] / 'data/raw/2026-10-06-chronology-region/post-launch-2026-10-07-v1/external_bootstrap_draws.json')['draws']))
vp = J(PKG / 'verification-post-launch-2026-10-07-v1.json')
chk('README/REPORT PL', 'verification assertions', 395653, vp['checks_total']); chk('README/REPORT PL', 'immutable prior files verified', 81, vp['original_immutable_files_preserved'])
chk('REPORT PL', 'Harappa families rebuilt', 1921, vp['harappa_families_rebuilt']); chk('REPORT PL', 'media period/type counts checked', 248, vp['checks']['media_type_count'])
chk('REPORT PL', 'rarefaction curve rows checked', 44, vp['checks']['media_curve_combination_check']); chk('REPORT PL', 'explicit-subset cases', 20, vp['checks']['explicit_subset_rarefaction'])
chk('REPORT PL', 'permutation allocations asserted by the assay (7 x 1999)', 13993, 7 * 1999)
vm = J(PKG / 'verification-2026-10-07-v1.json')
chk('REPORT verification', 'permutation margin assertions', 7485, vm['permutation_margin_assertions_checked']); chk('REPORT verification', 'divergence effects recomputed', 23, vm['js_effects_independently_recomputed'])
chk('REPORT verification', 'regional/external model replays', (104, 14), (vm['regional_prediction_models_independently_replayed'], vm['external_prediction_models_independently_replayed']))
chk('REPORT verification', 'payload hashes', 10, vm['source_payload_hashes_checked'])

# ---------------------------------------------------------------- print
fail = [r for r in results if not r[0]]
for ok, where, label, claimed, actual in results:
    print(('PASS ' if ok else 'FAIL ') + f'[{where}] {label}: quoted {claimed!r}; file {actual!r}')
print(f'\nSUMMARY: {len(results) - len(fail)} of {len(results)} checks pass; {len(fail)} fail')

# write the full list for the review record
tsv = Path(__file__).with_name('number_checks.tsv')
with open(tsv, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='	')
    w.writerow(['result', 'document_location', 'quantity', 'quoted_value', 'value_in_saved_output'])
    for ok, where, label, claimed, actual in results:
        w.writerow(['confirmed' if ok else 'DISCREPANCY', where, label, repr(claimed), repr(actual)])
