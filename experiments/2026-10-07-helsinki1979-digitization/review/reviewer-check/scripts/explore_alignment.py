"""Reviewer exploration: align frozen predictions with the primary reference and print per-row unit detail."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
from evaluate import align

ROOT = HERE.parents[1]
pred = json.loads((ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']
refs = {}
src = {}
for n in 'abc':
    d = json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))
    for r in d['rows']:
        refs[r['sample_index']] = r
        src[r['sample_index']] = n.upper()

def topk(u, k):
    return {int(c) for a in u['alternatives'][:k] for c in a['codes']}

for row in pred:
    i = row['sample_index']
    ref = refs[i]
    truth = [set(int(c) for c in u['strict_candidate_codes']) for u in ref['units']]
    g5 = [topk(u, 5) for u in row['units']]
    out = align(g5, truth)
    x0, y0, x1, y1 = row['glyph_xyxy_2x']
    W, H = x1 - x0, y1 - y0
    cnt_ok = len(row['units']) == len(truth)
    if len(sys.argv) > 1 and sys.argv[1] == 'mismatch' and cnt_ok:
        continue
    print(f"--- sample {i} annot {src[i]} page {row['pdf_page']} c{row['pdf_column']} r{row['row_index']} side={row['margin_side']} rot={row['page_rotation']} strip W={W} H={H} refN={len(truth)} predN={len(row['units'])} ref#='{ref['printed_inscription_id']}' pred#='{row['inscription_number']}' crop_issue={ref.get('crop_issue_types')}")
    for pi, ti in out['alignment']:
        if pi is None:
            print(f"   DEL ref unit {ti}: {sorted(truth[ti])}")
        elif ti is None:
            u = row['units'][pi]
            xb = u['x_bounds']; yb = u.get('y_bounds')
            top = u['alternatives'][0]['codes'] if u['alternatives'] else None
            print(f"   INS pred unit {pi}: x={xb} w={xb[1]-xb[0]} y={yb} kind={u['unit_kind']} top1={top} conf={u['confidence']}")
        else:
            u = row['units'][pi]
            xb = u['x_bounds']; yb = u.get('y_bounds')
            m5 = bool(g5[pi] & truth[ti]); m1 = bool(topk(u, 1) & truth[ti])
            print(f"   {'ok1' if m1 else ('ok5' if m5 else 'SUB')} pred {pi} x={xb} w={xb[1]-xb[0]} y={yb} ~ ref {ti} {sorted(truth[ti])} top1={sorted(topk(u,1))}")
