"""Rebuild review/cell-selection.json: the cells read independently by the reviewer.

Core cells: IDs in comparison.json `changes`, the 16 cells with `alternatives` in the original reference, and six named cells.
Random cells: 40 drawn with a fixed seed from the other cells. Only cell IDs are used here.

Run from the repository root:  python experiments/2026-10-08-chart-reference-audit/review/select_cells.py [--check]
"""
import json
import random
import sys

SEED = 20261008
PK = 'experiments/2026-10-08-chart-reference-audit/'
orig = json.load(open('research/chart_reference/manual_numeric_reference.json', encoding='utf-8'))
cid = lambda r: f"p{r['pdf_page']}_c{r['column']}_r{r['row']}"
ids = [cid(r) for r in orig['rows']]
chg = [x['cell'] for x in json.load(open(PK + 'comparison.json', encoding='utf-8'))['changes']]
alt = [cid(r) for r in orig['rows'] if r.get('alternatives')]
extra = ['p20_c4_r13', 'p21_c0_r21', 'p21_c4_r22', 'p20_c3_r16', 'p20_c4_r1', 'p21_c6_r31']
core = []
for x in chg + alt + extra:
    if x not in core:
        core.append(x)
rem = sorted(set(ids) - set(core))
rand = random.Random(SEED).sample(rem, 40)
sel = {'seed': SEED, 'method': 'random.Random(seed).sample(sorted(remaining_cell_ids), 40)', 'core': core, 'random': rand, 'n_remaining_pool': len(rem)}
path = PK + 'review/cell-selection.json'
if '--check' in sys.argv:
    print('identical to saved selection:', json.load(open(path)) == sel)
else:
    json.dump(sel, open(path, 'w'), indent=1)
    print(len(core), len(rand), len(rem))
