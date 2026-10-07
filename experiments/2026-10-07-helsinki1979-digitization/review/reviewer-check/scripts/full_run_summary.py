"""Reviewer: population-level view of the full provisional extraction (all 11,369 rows), Exploratory.

Combines (1) the native-resolution boundary-cut audit, (2) the pipeline's own trailing/leading narrow units next to the
number field, (3) the pages the orientation heuristic rotated, and (4) page-level row counts, by corpus section.
"""
import json
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[3]
DIAG = Path(__file__).resolve().parents[1] / 'diagnosis'
cut = {r['key']: r for r in json.loads((DIAG / 'boundary-cut-full.json').read_text())['results']}
cov = json.loads((HERE / 'runs/2026-10-07-full-v1/coverage.json').read_text())
rot_pages = {p['pdf_page'] for p in cov['pages'] if p['layout']['rotation'] == 180}
sections = {'number_order': (22, 78), 'end_sorted': (79, 130), 'beginning_sorted': (131, 180)}


def section(p):
    for k, (a, b) in sections.items():
        if a <= p <= b:
            return k


agg = collections.defaultdict(collections.Counter)
by_page = collections.defaultdict(collections.Counter)
with (HERE / 'runs/2026-10-07-full-v1/occurrences.jsonl').open(encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        p = r['pdf_page']
        sec = section(p)
        k = r['occurrence_key']
        side = r['margin_side']
        c = cut[k]
        # strip geometry in 2x px; margin side edge of the oriented strip
        x0, y0, x1, y1 = r['glyph_xyxy_2x']
        W = x1 - x0
        rotated = r['page_rotation'] == 180
        # In the oriented frame the margin sits at the right edge for side 'right' and at the left edge for 'left'.
        # The native audit used PDF coordinates (unrotated frame), so for rotated pages the oriented right edge is the PDF left edge.
        if rotated:
            edge_key = 'left' if side == 'right' else 'right'
        else:
            edge_key = 'right' if side == 'right' else 'left'
        crossing = c[edge_key][0] > 0
        frag = False
        units = r['units']
        if units:
            u = units[-1] if side == 'right' else units[0]
            xb = u['x_bounds']
            w = xb[1] - xb[0]
            yb = u.get('y_bounds') or [0, 0]
            near_edge = (xb[1] >= W - 8) if side == 'right' else (xb[0] <= 8)
            frag = near_edge and w <= 28 and yb[0] >= 10
        number_none = r['inscription_number'] is None
        cls_none = r['classification_code'] is None
        for key, flag in (('rows', True), ('margin_edge_crossing', crossing), ('narrow_edge_unit_in_number_band', frag),
                          ('either_edge_test', crossing or frag), ('rotated_page', rotated), ('number_none', number_none),
                          ('classification_none', cls_none),
                          ('any_defect_incl_rotation', crossing or frag or rotated)):
            agg[sec][key] += int(flag)
            agg['ALL'][key] += int(flag)
            by_page[p][key] += int(flag)
out = {s: dict(v) for s, v in agg.items()}
for s, v in out.items():
    n = v['rows']
    v['fractions'] = {k: round(x / n, 4) for k, x in v.items() if k not in ('rows', 'fractions')}
pages_bad = sorted(p for p, v in by_page.items() if v['either_edge_test'] / v['rows'] > 0.5)
out['pages_with_over_half_rows_flagged'] = dict(count=len(pages_bad), pages=pages_bad)
out['rotated_pages'] = sorted(rot_pages)
(DIAG / 'full-run-summary.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
