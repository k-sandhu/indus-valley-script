"""Reviewer sensitivity check: how do the headline match counts change when drawings are recoded?

Uses the package's matching rules (R1 = segments+loops, R2 = all integer fields, R3 = R2 + symmetry + orientation)
exactly as analyze.py defines them. Three coding conditions are crossed:
  queries:    primary rows (A) or reviewer rows (R) for the 42 Tamil Nadu drawings
  references: primary rows (A) or hybrid rows (reviewer where the reviewer coded the drawing, otherwise primary)
Also reports a field-level variant in which orientation is ignored (R3 without orientation).

Writes review/sensitivity.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'
HERE = Path(__file__).resolve().parent

INTEGER = ['segments', 'curved', 'loops', 'L', 'T', 'X', 'Y', 'other', 'terminals', 'components', 'dots']
FIELDS = INTEGER + ['symmetry', 'orientation']
RULES = {'R1': ['segments', 'loops'], 'R2': INTEGER, 'R3': FIELDS,
         'R3_no_orientation': INTEGER + ['symmetry']}

A = [r for r in json.loads((RAW / 'coder-a.json').read_text(encoding='utf-8')) if r.get('readable', True)]
R = {r['id']: r for r in json.loads((HERE / 'reviewer-coding.json').read_text(encoding='utf-8'))}
A_by = {r['id']: r for r in A}
inv_ids = {inv: [r['id'] for r in A if r['inventory'] == inv] for inv in ('tamil', 'indus', 'ogham', 'tifinagh')}


def sig(r, rule):
    return tuple(r[f] for f in RULES[rule])


def rows_for(inv, source):
    out = []
    for i in inv_ids[inv]:
        out.append(R[i] if (source == 'R' and i in R) else A_by[i])
    return out


def matched(queries, refs, rule):
    support = {sig(r, rule) for r in refs}
    return [q['id'] for q in queries if sig(q, rule) in support]


result = {}
for qsrc in ('A', 'R'):
    for rsrc in ('A', 'R'):
        key = 'queries=%s refs=%s' % (qsrc, 'primary' if rsrc == 'A' else 'hybrid')
        cell = {}
        for inv in ('indus', 'ogham', 'tifinagh'):
            cell[inv] = {}
            for rule in RULES:
                hits = matched(rows_for('tamil', qsrc), rows_for(inv, rsrc), rule)
                cell[inv][rule] = {'matched': len(hits), 'of': 42, 'ids': hits}
        result[key] = cell

# restricted comparison: only the reference drawings the reviewer coded, on both sides
sub = {}
for inv in ('indus', 'ogham', 'tifinagh'):
    ids = [i for i in inv_ids[inv] if i in R]
    sub[inv] = {'n_refs': len(ids)}
    for rule in ('R1', 'R2', 'R3'):
        sub[inv][rule + '_primary_queries_primary_refs'] = len(matched(rows_for('tamil', 'A'), [A_by[i] for i in ids], rule))
        sub[inv][rule + '_reviewer_queries_reviewer_refs'] = len(matched(rows_for('tamil', 'R'), [R[i] for i in ids], rule))
result['restricted_to_reviewer_coded_refs'] = sub

# R3 pair list under reviewer coding (queries and references both reviewer rows)
pairs = {}
for inv in ('indus', 'ogham', 'tifinagh'):
    refs = [R[i] for i in inv_ids[inv] if i in R]
    qs = rows_for('tamil', 'R')
    pairs[inv] = [(q['id'], [r['id'] for r in refs if sig(q, 'R3') == sig(r, 'R3')]) for q in qs if any(sig(q, 'R3') == sig(r, 'R3') for r in refs)]
result['R3_pairs_reviewer_vs_reviewer'] = pairs

# primary's pairs, for comparison
qm = json.loads((RAW / 'run-v1-query-matches.json').read_text(encoding='utf-8'))
result['R3_pairs_primary'] = {inv: [(x['query_id'], x['references']) for x in qm if x['inventory'] == inv and x['rule'] == 'R3' and x['matched']]
                              for inv in ('indus', 'ogham', 'tifinagh')}
(HERE / 'sensitivity.json').write_text(json.dumps(result, indent=1), encoding='utf-8')

for k, v in result.items():
    if k.startswith('queries='):
        print(k)
        for inv, rules in v.items():
            print('   ', inv, {r: '%d/42' % x['matched'] for r, x in rules.items()})
print()
print('restricted (reviewer-coded refs only):')
print(json.dumps(sub, indent=1))
print('R3 pairs reviewer vs reviewer:', json.dumps(pairs))
print('R3 pairs primary:', json.dumps(result['R3_pairs_primary']))
