"""Reviewer: do the reference's tick-pair codes 2 and 25 follow the chart's vertical-position convention?

Chart codes 2 (rank 122) and 25 (rank 119) are the same two short strokes; in the chart they differ by height (code 25 sits
at the top of the sign box, code 2 near its middle). This measures, in 2x pixels, where the tick pair sits relative to the
top of the tallest drawing in the same row for every reference unit labelled 2 or 25 (rows on the upright page 37 excluded,
unit merged with another drawing excluded), and compares with the chart geometry.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pymupdf as fitz

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
from evaluate import align  # noqa: E402

ROOT = HERE.parents[1]
doc = fitz.open(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf')


def render(p, scale=2):
    pix = doc[p - 1].get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()


snap = json.loads((HERE / 'chart-snapshot.json').read_text())
pages = {20: render(20), 21: render(21)}
chart = {}
for code in (2, 25):
    for r in snap['rows']:
        if code == r['code']:
            p, c, rr = r['pdf_page'], r['column'], r['row']
            x = (176 if p == 20 else 153) + 100.4 * c
            y = 152.6 + 40.1 * rr
            xy = [round(x - 20), round(y - 19.5), round(x + 31), round(y + 19.5)]
            ys, xs = np.where(pages[p][xy[1]:xy[3], xy[0]:xy[2]] < 190)
            chart[code] = (float(ys.min() + xy[1] - y), float(ys.max() + xy[1] - y))
# tallest chart glyph top for reference (code 204)
for r in snap['rows']:
    if r['code'] == 204:
        p, c, rr = r['pdf_page'], r['column'], r['row']
        x = (176 if p == 20 else 153) + 100.4 * c
        y = 152.6 + 40.1 * rr
        xy = [round(x - 20), round(y - 19.5), round(x + 31), round(y + 19.5)]
        ys, xs = np.where(pages[p][xy[1]:xy[3], xy[0]:xy[2]] < 190)
        tall_top = float(ys.min() + xy[1] - y)
chart_offsets = {code: v[0] - tall_top for code, v in chart.items()}  # tick top below the tall-glyph top, in 2x px

pred = {r['sample_index']: r for r in json.loads((ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']}
refs, who = {}, {}
for n in 'abc':
    for r in json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))['rows']:
        refs[r['sample_index']] = r
        who[r['sample_index']] = n.upper()
rows = []
for i, ref in sorted(refs.items()):
    if i in (14, 15, 16):
        continue
    row = pred[i]
    truth = [set(int(c) for c in u['strict_candidate_codes']) for u in ref['units']]
    g5 = [{int(c) for al in u['alternatives'][:5] for c in al['codes']} for u in row['units']]
    pair = {ti: pi for pi, ti in align(g5, truth)['alignment'] if pi is not None and ti is not None}
    tall_tops = [u['y_bounds'][0] for u in row['units'] if u.get('y_bounds') and (u['y_bounds'][1] - u['y_bounds'][0]) >= 24]
    if not tall_tops:
        continue
    row_top = min(tall_tops)
    for ti, u in enumerate(ref['units']):
        codes = set(u['strict_candidate_codes'])
        if codes & {2, 25, 231, 509} and ti in pair:
            pu = row['units'][pair[ti]]
            w = pu['x_bounds'][1] - pu['x_bounds'][0]
            h = pu['y_bounds'][1] - pu['y_bounds'][0]
            if h > 12 or w > 12:
                rows.append(dict(sample_index=i, annotator=who[i], reference_codes=sorted(codes), note='unit merged with other ink, excluded'))
                continue
            d = pu['y_bounds'][0] - row_top
            nearest = min(chart_offsets, key=lambda c: abs(chart_offsets[c] - d))
            rows.append(dict(sample_index=i, annotator=who[i], reference_codes=sorted(codes), tick_top_below_row_top_px=d, nearest_chart_code=nearest,
                             reference_matches_nearest=bool(codes & {nearest, 231 if nearest == 2 else 509})))
res = dict(chart_tick_top_below_tall_glyph_top_px={str(k): v for k, v in chart_offsets.items()}, units=rows)
out = Path(__file__).resolve().parents[1] / 'diagnosis' / 'tick-position-check.json'
out.write_text(json.dumps(res, indent=1), encoding='utf-8')
print(json.dumps(res, indent=1))
