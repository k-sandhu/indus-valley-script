"""Compare the reviewer's independent readings and whole-chart pixel check with the audit's v2 and the original reference.

Run from the repository root after independent-readings.json and pixel-check-all-cells.json exist:
    python experiments/2026-10-08-chart-reference-audit/review/compare_readings.py
Output: experiments/2026-10-08-chart-reference-audit/review/reading-comparison.json
"""
import json
from collections import Counter

PK = 'experiments/2026-10-08-chart-reference-audit/'
orig = json.load(open('research/chart_reference/manual_numeric_reference.json', encoding='utf-8'))
v2 = json.load(open(PK + 'chart-reference-v2.json', encoding='utf-8'))
ind = json.load(open(PK + 'review/independent-readings.json', encoding='utf-8'))
pix = json.load(open(PK + 'review/pixel-check-all-cells.json', encoding='utf-8'))['cells']
fp = json.load(open(PK + 'visual-readings.json', encoding='utf-8'))


def cid(r):
    return f"p{r['pdf_page']}_c{r['column']}_r{r['row']}"


O = {cid(r): r for r in orig['rows']}
V = {cid(r): r for r in v2['rows']}

rows = []
for c in ind['cells']:
    cell = c['cell']
    o, v = O[cell], V[cell]
    rows.append(dict(
        cell=cell, group=c['group'],
        mine_class=c['class_number'], mine_code=c['code'], mine_eye_pass_code=c['eye_pass_code'], mine_confidence=c['confidence'],
        v2_class=v['rank'], v2_code=v['code'], v2_confidence=v['numeric_confidence'],
        orig_class=o['rank'], orig_code=o['code'], orig_alternatives=o['alternatives'],
        class_agrees_v2=c['class_number'] == v['rank'], code_agrees_v2=c['code'] == v['code'],
        eye_pass_agrees_v2=c['eye_pass_code'] == v['code'],
        code_agrees_orig=c['code'] == o['code'], code_in_orig_set=c['code'] in ([o['code']] + o['alternatives']),
        v2_in_my_alternatives=v['code'] in c['alternatives_considered']))

summary = dict(
    cells_read=len(rows),
    class_disagree_v2=[r['cell'] for r in rows if not r['class_agrees_v2']],
    code_disagree_v2=[r['cell'] for r in rows if not r['code_agrees_v2']],
    eye_pass_disagree_v2=[r['cell'] for r in rows if not r['eye_pass_agrees_v2']],
    code_disagree_orig=[r['cell'] for r in rows if not r['code_agrees_orig']],
    code_outside_orig_set=[r['cell'] for r in rows if not r['code_in_orig_set']],
)
for grp in ('core', 'random'):
    g = [r for r in rows if r['group'] == grp]
    summary[grp] = dict(n=len(g), code_agree_v2=sum(r['code_agrees_v2'] for r in g), class_agree_v2=sum(r['class_agrees_v2'] for r in g),
                        code_agree_orig=sum(r['code_agrees_orig'] for r in g))

# whole-chart pixel check against v2 and original
whole = []
for cell, p in pix.items():
    v, o = V[cell], O[cell]
    pc, pk = p['class']['read'], p['code']['read']
    weak = [(k, i, d['best'], d['best_score'], d['second'], d['second_score']) for k in ('class', 'code') for i, d in enumerate(p[k]['digits'])
            if d['best_score'] < 0.6 or d['best_score'] - d['second_score'] < 0.08]
    whole.append(dict(cell=cell, pix_class=pc, pix_code=pk, v2_class=v['rank'], v2_code=v['code'], orig_class=o['rank'], orig_code=o['code'],
                      class_match_v2=pc == str(v['rank']), code_match_v2=pk == str(v['code']),
                      class_match_orig=pc == str(o['rank']), code_match_orig=pk == str(o['code']),
                      n_weak_digits=len(weak)))
cm = Counter()
for w in whole:
    cm['class_match_v2'] += w['class_match_v2']; cm['code_match_v2'] += w['code_match_v2']
    cm['class_match_orig'] += w['class_match_orig']; cm['code_match_orig'] += w['code_match_orig']
code_mismatch_v2 = [w for w in whole if not w['code_match_v2']]
class_mismatch_v2 = [w for w in whole if not w['class_match_v2']]
changed = set(x['cell'] for x in json.load(open(PK + 'comparison.json', encoding='utf-8'))['changes'])
summary_whole = dict(
    cells=len(whole), counts=dict(cm),
    code_mismatch_v2=len(code_mismatch_v2), class_mismatch_v2=len(class_mismatch_v2),
    code_mismatch_v2_in_changed_cells=sum(1 for w in code_mismatch_v2 if w['cell'] in changed),
    code_mismatch_v2_in_unchanged_cells=sum(1 for w in code_mismatch_v2 if w['cell'] not in changed),
)
json.dump(dict(status='Exploratory reviewer comparison', summary=summary, cells=rows, whole_chart_summary=summary_whole,
               whole_chart_code_mismatch_v2=code_mismatch_v2, whole_chart_class_mismatch_v2=class_mismatch_v2),
          open(PK + 'review/reading-comparison.json', 'w'), indent=1)
print(json.dumps(summary, indent=1))
print(json.dumps(summary_whole, indent=1))
