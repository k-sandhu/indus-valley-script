"""Recompute the README/REPORT headline numbers from impact.json, comparison.json and chart-reference-v2.json.

Run from the repository root:  python experiments/2026-10-08-chart-reference-audit/review/check_numbers.py
Output: experiments/2026-10-08-chart-reference-audit/review/number-check.json
"""
import json
from collections import Counter, defaultdict

PK = 'experiments/2026-10-08-chart-reference-audit/'
imp = json.load(open(PK + 'impact.json', encoding='utf-8'))
cmp_ = json.load(open(PK + 'comparison.json', encoding='utf-8'))
v2 = json.load(open(PK + 'chart-reference-v2.json', encoding='utf-8'))
orig = json.load(open('research/chart_reference/manual_numeric_reference.json', encoding='utf-8'))

res = []


def chk(claim, source, observed, expected):
    res.append(dict(claim=claim, source=source, observed=observed, expected=expected, match=observed == expected))


S = cmp_['summary']
chk('8 primary code changes', 'comparison.summary.primary_code_changes', S['primary_code_changes'], 8)
chk('1 class change', 'comparison.summary.class_changes', S['class_changes'], 1)
chk('21 changed numeric rows', 'comparison.summary.changed_cells', S['changed_cells'], 21)
chk('16 ambiguities resolved', 'comparison.summary.ambiguities_resolved', S['ambiguities_resolved'], 16)
chk('classes 1-401', 'v2 rows rank', (min(r['rank'] for r in v2['rows']), max(r['rank'] for r in v2['rows']), len({r['rank'] for r in v2['rows']})), (1, 401, 401))
ranks = [r['rank'] for r in v2['rows']]
chk('class order nondecreasing', 'v2 rows rank', ranks == sorted(ranks), True)
chk('687 distinct codes', 'v2 rows code', len({r['code'] for r in v2['rows']}), 687)
chk('v2 rows with change_log', 'v2 rows', sum(1 for r in v2['rows'] if r.get('change_log')), 21)
chk('v2 rows with alternatives', 'v2 rows', sum(1 for r in v2['rows'] if r['alternatives']), 0)
chk('medium-confidence cells', 'v2 rows numeric_confidence', sorted(f"p{r['pdf_page']}_c{r['column']}_r{r['row']}" for r in v2['rows'] if r['numeric_confidence'] != 'high'), ['p21_c4_r22'])
chk('v2 top-level numeric_ambiguous_cells', 'v2', v2['numeric_ambiguous_cells'], 0)

M = imp['M_references']
for ver, rows, units, dr, du, strict, shape, pot in (('v1', 60, 267, 8, 11, 1, 11, 0), ('v2', 80, 352, 0, 0, 0, 0, 18), ('v3', 80, 369, 7, 8, 8, 8, 31)):
    s = M[ver]['summary']
    chk(f'M {ver} rows/units', f'impact.M_references.{ver}.summary', (s['rows'], s['units']), (rows, units))
    chk(f'M {ver} definite changed rows/units', f'impact.M_references.{ver}.summary', (s['definite_changed_rows'], s['definite_changed_units']), (dr, du))
    chk(f'M {ver} strict/shape changed units', f'impact.M_references.{ver}.summary', (s['strict_changed_units'], s['shape_changed_units']), (strict, shape))
    chk(f'M {ver} unlocated-candidate units', f'impact.M_references.{ver}.summary', s['potential_units_needing_identity_review'], pot)
v1 = M['v1']['unit_changes']
chk('v1 changed samples 1,5,7,8,23,32,36,39', 'impact.M_references.v1.unit_changes', sorted({u['sample_index'] for u in v1}), [1, 5, 7, 8, 23, 32, 36, 39])
v1_strict = [(u['sample_index'], u['unit_index'], u['old_codes'], u['new_codes']) for u in v1 if u['field'].startswith('strict')]
chk('v1 strict change is sample 36 unit 1, 506 to 508', 'impact.M_references.v1.unit_changes', v1_strict, [(36, 1, [506], [508])])
v3 = sorted({(u['sample_index'], u['unit_index']) for u in M['v3']['unit_changes']})
chk('v3 direct pairs', 'impact.M_references.v3.unit_changes', v3, [(15, 0), (31, 0), (32, 0), (32, 2), (39, 4), (51, 2), (60, 6), (67, 4)])
chk('v3 location conflicts: 58/0 vs 21:7:5', 'impact.M_v3_reported_location_conflicts',
    [(c['sample_index'], c['unit_index'], c['reported_card_cell'], c['stored_reference_cells']) for c in imp['M_v3_reported_location_conflicts']],
    [(58, 0, 'p20_c4_r1', ['p21_c7_r5'])])

T = imp['M_templates']
chk('21 template records', 'impact.M_templates', len(T), 21)
code_changed = sum('codes' in t['fields'] for t in T)
rank_changed = sum(('rank' in t['fields'] or 'rank_candidates' in t['fields']) for t in T)
chk('20 template records change code sets', 'impact.M_templates[*].fields.codes', code_changed, 20)
chk('1 template record changes only rank metadata', 'impact.M_templates[*].fields', sum(1 for t in T if 'codes' not in t['fields'] and ('rank' in t['fields'])), 1)
paths = defaultdict(set)
for t in T:
    for c in t['cards']:
        paths[c['path'].split('/blind/')[0] + '|' + c['path'].rsplit('/', 1)[-1]].add(c['path'])
v1sheets = {c['path'] for t in T for c in t['cards'] if '/blind/chart_sheets/' in c['path']}
chk('21 locations in eight original v1 sheets', 'impact.M_templates[*].cards', len(v1sheets), 8)
for folder in ('2026-10-07-v1', '2026-10-07-v2', '2026-10-08-v3'):
    sh = {c['path'] for t in T for c in t['cards'] if f'/repair/{folder}/' in c['path']}
    chk(f'nine sheets in repair {folder}', 'impact.M_templates[*].cards', len(sh), 9)
chk('v3 card code strips changed', 'impact.M_templates[*].cards', sum(c['code_strip_changes'] for t in T for c in t['cards'] if '2026-10-08-v3' in c['path']), 20)

N = imp['N_charts']
chk('N 105 placements', 'impact.N_charts', len(N), 105)
chk('N 100 code-strip placements', 'impact.N_charts[*].code_strip_changes', sum(r['code_strip_changes'] for r in N), 100)
chk('N all identical to M v2', 'impact.N_charts[*].identical_to_M_v2_card', all(r['identical_to_M_v2_card'] for r in N), True)
runs = Counter(r['path'].split('/')[3] + '/' + r['path'].split('/')[4] for r in N)
chk('N five deliveries of 21', 'impact.N_charts paths', sorted(runs.values()), [21] * 5)

chk('public chart rows changed', 'impact.public_chart_reference_changes', len(imp['public_chart_reference_changes']), 21)
P = imp['public_predictions']
for ver, ch_alt, ch_units, ch_rows, top1 in (('v1', 65, 41, 33, 5), ('v2', 88, 56, 42, 10)):
    s = P[ver]['summary']
    chk(f'public {ver} predictions', f'impact.public_predictions.{ver}.summary', (s['changed_alternatives'], s['changed_units'], s['changed_rows'], s['top1_changed_units']), (ch_alt, ch_units, ch_rows, top1))
code_alts = {v: sum('codes' in a['fields'] for a in P[v]['alternative_changes']) for v in ('v1', 'v2')}
rank_alts = {v: sum('ranks' in a['fields'] for a in P[v]['alternative_changes']) for v in ('v1', 'v2')}
rank_only = {v: sum(('codes' not in a['fields']) for a in P[v]['alternative_changes']) for v in ('v1', 'v2')}
chk('code-set changes 60 and 83', 'impact.public_predictions[*].alternative_changes[*].fields.codes', (code_alts['v1'], code_alts['v2']), (60, 83))
chk('rank-only changes 5 and 5', 'impact.public_predictions[*].alternative_changes[*].fields', (rank_only['v1'], rank_only['v2']), (5, 5))
PR = imp['public_readings']
rd = {}
for r in PR:
    rd[(r['benchmark'], r['reader'], r['kind'])] = r['summary']['definite_changed_units']
chk('public readings changed units: v1 A/B primary 6/5, v2 A 15, v2 B 0, v2 C 0', 'impact.public_readings[*].summary.definite_changed_units',
    (rd[('v1', 'A', 'primary')], rd[('v1', 'B', 'primary')], rd[('v2', 'A', 'independent')], rd[('v2', 'B', 'independent')], rd[('v2', 'C', 'adjudicated')]), (6, 5, 15, 0, 0))
pot = {(r['benchmark'], r['reader'], r['kind']): r['summary']['potential_units_needing_identity_review'] for r in PR}
chk('public readings v2 adjudicator C has 18 unlocated-candidate units, v2 B none', 'impact.public_readings[*].summary.potential_units_needing_identity_review',
    (pot[('v2', 'C', 'adjudicated')], pot[('v2', 'B', 'independent')]), (18, 0))
chk('public cards 42 entries on 17 sheet files', 'impact.public_cards', (len(imp['public_cards']), len({c['path'] for c in imp['public_cards']})), (42, 17))
E = imp['scorer_expectations']['expected_row_records_to_review']
chk('scorer rows to recheck 32 and 42', 'impact.scorer_expectations.expected_row_records_to_review', (E['v1']['rows'], E['v2']['rows']), (32, 42))
chk('no strict cardinality changes', 'impact.scorer_expectations.direct_strict_candidate_cardinality_changes', imp['scorer_expectations']['direct_strict_candidate_cardinality_changes'], {'v1': 0, 'v2': 0})

# duplicates of old primary codes: six old codes label two cells
cnt = Counter(r['code'] for r in orig['rows'])
dups = sorted(c for c, n in cnt.items() if n > 1)
chk('six old duplicate primary codes 205,360,385,465,506,579', 'original reference rows code', dups, [205, 360, 385, 465, 506, 579])

json.dump(dict(status='Verified computation (reviewer recomputation)', checks=res, n=len(res), n_match=sum(r['match'] for r in res)),
          open(PK + 'review/number-check.json', 'w'), indent=1)
for r in res:
    print('OK ' if r['match'] else 'XX ', r['claim'], '|', r['observed'] if not r['match'] or r['expected'] is None else '')
print(sum(r['match'] for r in res), '/', len(res))
