"""Reviewer diagnosis of the 60-row frozen evaluation (post-outcome, Exploratory).

Reads the frozen predictions and the three primary references, aligns units with the package's own
`evaluate.align` (top-5 candidate sets), and attributes row-level and unit-level failures to stages.
All rules below were written after seeing outcomes and are labelled Exploratory in REVIEW.md.

Run from the repository root:
  python experiments/2026-10-07-helsinki1979-digitization/review/reviewer-check/scripts/diagnose_errors.py
"""
import json
import sys
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
from evaluate import align, wilson  # noqa: E402

ROOT = HERE.parents[1]
OUT = Path(__file__).resolve().parents[1] / 'diagnosis'
OUT.mkdir(exist_ok=True)
pred = json.loads((ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']
snap = json.loads((HERE / 'chart-snapshot.json').read_text(encoding='utf-8'))
code_ranks = collections.defaultdict(set)
for r in snap['rows']:
    for c in [r['code']] + r['alternatives']:
        code_ranks[int(c)].add(int(r['rank']))
        for ra in r.get('rank_alternatives', []):
            code_ranks[int(c)].add(int(ra))
refs, src = {}, {}
for n in 'abc':
    d = json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))
    for r in d['rows']:
        refs[r['sample_index']] = r
        src[r['sample_index']] = n.upper()


def codes_top(u, k):
    return {int(c) for a in u['alternatives'][:k] for c in a['codes']}


def ranks_top(u, k):
    out = set()
    for a in u['alternatives'][:k]:
        out |= {int(x) for x in a['ranks']}
    return out


def ranks_of(codes):
    out = set()
    for c in codes:
        out |= code_ranks.get(int(c), set())
    return out


PAGE37_ROTATED = {14, 15, 16}
SLIVER_W = 14  # px at 2x; edge units narrower than 2x this at the margin side count as number-field fragments
rows_out = []
unit_pairs = []
for row in pred:
    i = row['sample_index']
    ref = refs[i]
    units = ref['units']
    truth = [set(int(c) for c in u['strict_candidate_codes']) for u in units]
    g5 = [codes_top(u, 5) for u in row['units']]
    al = align(g5, truth)
    x0, y0, x1, y1 = row['glyph_xyxy_2x']
    W, H = x1 - x0, y1 - y0
    margin_right = row['margin_side'] == 'right'
    ins, dele = [], []
    for pi, ti in al['alignment']:
        if pi is None:
            dele.append(ti)
        elif ti is None:
            ins.append(pi)
        else:
            u = row['units'][pi]
            ru = units[ti]
            unit_pairs.append(dict(
                sample_index=i, pred_unit=pi, ref_unit=ti, annotator=src[i],
                ref_kind=ru.get('unit_kind'), ref_underline=bool(ru.get('uncertainty_underline')),
                is_aux=ru.get('unit_kind') != 'glyph',
                top1_code=bool(codes_top(u, 1) & truth[ti]), top5_code=bool(g5[pi] & truth[ti]),
                top1_rank=bool(ranks_top(u, 1) & ranks_of(truth[ti])), top5_rank=bool(ranks_top(u, 5) & ranks_of(truth[ti])),
                width=u['x_bounds'][1] - u['x_bounds'][0], rotated=i in PAGE37_ROTATED,
                equal_count=len(row['units']) == len(truth),
                ref_codes=sorted(truth[ti]), pred_top1=sorted(codes_top(u, 1))))
    ins_desc = []
    for pi in ins:
        u = row['units'][pi]
        xb = u['x_bounds']
        yb = u.get('y_bounds') or [0, 0]
        w = xb[1] - xb[0]
        at_margin_edge = (xb[1] >= W - 3) if margin_right else (xb[0] <= 3)
        at_top = yb[0] <= 2 and (yb[1] - yb[0]) <= 10
        at_bottom = yb[1] >= H - 2 and (yb[1] - yb[0]) <= 10
        if at_margin_edge and w <= 2 * SLIVER_W:
            kind = 'margin_edge_fragment'
        elif at_top or at_bottom:
            kind = 'neighbor_row_ink_at_strip_edge'
        else:
            kind = 'interior_or_other'
        ins_desc.append(dict(pred_unit=pi, x=xb, y=yb, width=w, kind=kind))
    rows_out.append(dict(sample_index=i, annotator=src[i], pdf_page=row['pdf_page'], pdf_column=row['pdf_column'],
                         ref_count=len(truth), pred_count=len(row['units']), count_ok=len(row['units']) == len(truth),
                         inserted=ins_desc, deleted_ref_units=dele, top5_edits=al['edits'],
                         crop_correct=ref.get('crop_correct'), crop_issue_types=ref.get('crop_issue_types'),
                         ref_number=str(ref['printed_inscription_id']), pred_number=row.get('inscription_number'),
                         ref_cls=ref['classification_literal'], pred_cls=row.get('classification_code'),
                         rotated_page=i in PAGE37_ROTATED, strip_W=W, strip_H=H))

# ---- Count-mismatch attribution
attrib = {}
for r in rows_out:
    if r['count_ok']:
        continue
    kinds = [x['kind'] for x in r['inserted']]
    if r['rotated_page']:
        a = 'page_orientation'
    elif 'margin_edge_fragment' in kinds:
        a = 'margin_field_fragment_in_glyph_strip'
    elif 'neighbor_row_ink_at_strip_edge' in kinds:
        a = 'neighbor_row_ink_at_strip_edge'
    elif r['deleted_ref_units'] and not r['inserted']:
        a = 'fewer_units_than_reference (right-edge clipping or merged units)'
    else:
        a = 'interior_segmentation_other'
    attrib[r['sample_index']] = a
cnt = collections.Counter(attrib.values())


def number_cat(r):
    ref, pr = r['ref_number'], r['pred_number']
    if pr == ref:
        return 'correct'
    if r['rotated_page']:
        return 'page_orientation'
    if pr is None:
        return 'unread_none'
    if ref.endswith(pr) and len(pr) < len(ref):
        return 'leading_digits_lost'
    if len(pr) == len(ref) and pr[1:] == ref[1:]:
        return 'leading_digit_misread'
    if ref.startswith(pr) and len(pr) < len(ref):
        return 'trailing_digit_lost'
    if len(pr) == len(ref):
        return 'inner_or_final_digit_misread'
    return 'other'


ncat = collections.Counter(number_cat(r) for r in rows_out)


def rate(sel, key):
    n = len(sel)
    k = sum(1 for p in sel if p[key])
    return dict(correct=k, total=n, rate=(k / n if n else None), wilson95=wilson(k, n)['ci95'] if n else None)


allp = unit_pairs
non_rot = [p for p in allp if not p['rotated']]
eq_nonrot = [p for p in non_rot if p['equal_count']]
res = {}
for name, sel in [('all_aligned_pairs', allp), ('aligned_pairs_excluding_page37_rotated', non_rot),
                  ('equal_count_rows_excluding_page37_rotated', eq_nonrot),
                  ('glyph_only_excluding_rotated', [p for p in non_rot if not p['is_aux']]),
                  ('auxiliary_only_excluding_rotated', [p for p in non_rot if p['is_aux']]),
                  ('underlined_glyph_excluding_rotated', [p for p in non_rot if p['ref_underline']]),
                  ('plain_glyph_excluding_rotated', [p for p in non_rot if not p['ref_underline'] and not p['is_aux']])]:
    res[name] = dict(n=len(sel), top1_code=rate(sel, 'top1_code'), top5_code=rate(sel, 'top5_code'),
                     top1_rank=rate(sel, 'top1_rank'), top5_rank=rate(sel, 'top5_rank'))

# ---- Counterfactual: drop margin-edge fragments (post-outcome, Exploratory)
cf_rows = []
for row, r in zip(pred, rows_out):
    i = row['sample_index']
    drop = {x['pred_unit'] for x in r['inserted'] if x['kind'] == 'margin_edge_fragment'}
    if not drop:
        continue
    units = [u for k, u in enumerate(row['units']) if k not in drop]
    truth = [set(int(c) for c in u['strict_candidate_codes']) for u in refs[i]['units']]
    ok = {}
    for k in (1, 5):
        g = [codes_top(u, k) for u in units]
        ok[k] = len(g) == len(truth) and align(g, truth)['edits'] == 0
    cf_rows.append(dict(sample_index=i, whole_row_top1=ok[1], whole_row_top5=ok[5]))
base = json.loads((HERE / 'evaluation/2026-10-07-frozen-v1/metrics.json').read_text())['rows']
b1 = {m['sample_index']: m['strict_top1']['whole_row_compatible'] for m in base}
b5 = {m['sample_index']: m['strict_top5']['whole_row_compatible'] for m in base}
gain1 = sum(1 for c in cf_rows if c['whole_row_top1'] and not b1[c['sample_index']])
gain5 = sum(1 for c in cf_rows if c['whole_row_top5'] and not b5[c['sample_index']])

result = dict(
    status='Exploratory (reviewer post-outcome diagnosis of frozen predictions)',
    count_mismatch_rows=sum(1 for r in rows_out if not r['count_ok']),
    count_mismatch_attribution=dict(cnt), count_mismatch_by_row=attrib,
    number_error_categories=dict(ncat), number_category_by_row={r['sample_index']: number_cat(r) for r in rows_out},
    unit_level=res,
    counterfactual_drop_margin_edge_fragments=dict(
        rows_affected=len(cf_rows), added_top1_whole_rows=gain1, added_top5_whole_rows=gain5,
        top1_whole_rows_after=13 + gain1, top5_whole_rows_after=24 + gain5, rows=cf_rows),
    rows=rows_out)
(OUT / 'diagnosis.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'count_mismatch_by_row', 'number_category_by_row')}, indent=1))
