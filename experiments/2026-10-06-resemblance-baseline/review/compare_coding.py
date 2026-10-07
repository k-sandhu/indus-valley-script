"""Compare the reviewer's independent coding with the package's primary (A) and repeat (B) rows.

Run after reviewer_coding.py. Reads the preserved local rows in data/raw/2026-10-06-resemblance-baseline/.
Writes review/coding-agreement.json and prints a per-drawing difference list.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'
HERE = Path(__file__).resolve().parent

INTEGER = ['segments', 'curved', 'loops', 'L', 'T', 'X', 'Y', 'other', 'terminals', 'components', 'dots']
FIELDS = INTEGER + ['symmetry', 'orientation']
RULES = {'R1': ['segments', 'loops'], 'R2': INTEGER, 'R3': FIELDS}

R = {r['id']: r for r in json.loads((HERE / 'reviewer-coding.json').read_text(encoding='utf-8'))}
A = {r['id']: r for r in json.loads((RAW / 'coder-a.json').read_text(encoding='utf-8'))}
B = {r['id']: r for r in json.loads((RAW / 'coder-b.json').read_text(encoding='utf-8'))}


def compare(X, Y, ids, label):
    ids = [i for i in ids if i in X and i in Y and X[i].get('readable', True) and Y[i].get('readable', True)]
    out = {'pair': label, 'n': len(ids), 'ids': ids, 'fields': {}, 'rules': {}}
    for f in FIELDS:
        out['fields'][f] = sum(X[i][f] == Y[i][f] for i in ids)
    for rule, fs in RULES.items():
        out['rules'][rule] = sum(all(X[i][f] == Y[i][f] for f in fs) for i in ids)
    out['complete_vector'] = sum(all(X[i][f] == Y[i][f] for f in FIELDS) for i in ids)
    out['integer_vector'] = sum(all(X[i][f] == Y[i][f] for f in INTEGER) for i in ids)
    out['complete_without_orientation'] = sum(all(X[i][f] == Y[i][f] for f in FIELDS if f != 'orientation') for i in ids)
    return out


result = {}
all_ids = sorted(R)
result['R_vs_A_all'] = compare(R, A, all_ids, 'reviewer vs primary, all reviewer-coded drawings')
for inv in ('tamil', 'tifinagh', 'ogham', 'indus'):
    ids = [i for i in all_ids if R[i]['inventory'] == inv]
    result['R_vs_A_' + inv] = compare(R, A, ids, 'reviewer vs primary, ' + inv)
b_ids = sorted(B)
result['R_vs_B_sample'] = compare(R, B, b_ids, 'reviewer vs repeat coder B, B sample')
result['A_vs_B_sample_reviewer_overlap'] = compare(A, B, [i for i in b_ids if i in R], 'primary vs B on B-sample drawings the reviewer also coded')
result['R_vs_A_on_B_sample'] = compare(R, A, [i for i in b_ids if i in R], 'reviewer vs primary on B-sample drawings')
result['A_vs_B_full'] = compare(A, B, b_ids, 'primary vs B, all assigned (package figure)')
(HERE / 'coding-agreement.json').write_text(json.dumps(result, indent=1), encoding='utf-8')

for k, v in result.items():
    print(k, 'n=%d' % v['n'], 'complete=%d' % v['complete_vector'], 'without_orientation=%d' % v['complete_without_orientation'], 'integer=%d' % v['integer_vector'], v['rules'])
    print('   fields', v['fields'])

print()
print('Per-drawing differences, reviewer vs primary (fields that differ):')
diffs = defaultdict(list)
for i in all_ids:
    if not A[i].get('readable', True):
        print(i, 'primary excluded')
        continue
    d = [(f, R[i][f], A[i][f]) for f in FIELDS if R[i][f] != A[i][f]]
    if d:
        diffs[i] = d
        print(i, ' '.join('%s:%s/%s' % x for x in d))
print('drawings with any difference:', len(diffs), 'of', len(all_ids))
