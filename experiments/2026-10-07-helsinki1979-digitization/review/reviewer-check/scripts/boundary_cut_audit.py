"""Reviewer: annotator-independent crop audit on the native 600 dpi page images.

For every glyph box the pipeline produced (60 frozen sample rows, or all 11,369 full-run rows) this counts
connected ink components of the unchanged scan that cross the box boundary. A component that crosses the right
(margin-side) edge is either a clipped glyph or the leading digit of the printed number. A component that crosses
the top or bottom edge is clipped ink from the same row (underline separated from its glyph is not detected) or from a neighbouring row.
No annotator judgment is used. Exploratory reviewer diagnostic.

  python boundary_cut_audit.py --rows sample|full --out <json>
"""
import argparse
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf as fitz
from PIL import Image

HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
PDF = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'
RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'
MIN_AREA = 40  # native px; ignores dust


def load_rows(which):
    if which == 'sample':
        sel = json.loads((HERE / 'blind/selection-source-only.json').read_text())['rows']
        pred = json.loads((RAW / 'frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']
        meta = {r['sample_index']: r for r in pred}
        rows = []
        for r in sel:
            m = meta[r['sample_index']]
            rows.append(dict(key=r['occurrence_key'], page=r['pdf_page'], column=r['pdf_column'], box=r['glyph_pdf_box'],
                             sample_index=r['sample_index'], margin_side=m['margin_side'], rotation=m['page_rotation']))
        return rows
    rows = []
    with (HERE / 'runs/2026-10-07-full-v1/occurrences.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            rows.append(dict(key=r['occurrence_key'], page=r['pdf_page'], column=r['pdf_column'], box=r['glyph_pdf_box'],
                             margin_side=r['margin_side'], rotation=r['page_rotation']))
    return rows


def page_ink(doc, p):
    page = doc[p - 1]
    xref = page.get_images(full=True)[0][0]
    info = doc.extract_image(xref)
    arr = np.array(Image.open(io.BytesIO(info['image'])).convert('L'))
    rect = page.get_image_rects(xref)[0]
    ink = (arr < 128).astype(np.uint8)
    sx = arr.shape[1] / rect.width
    sy = arr.shape[0] / rect.height
    return ink, rect, sx, sy


def audit_page(ink, rect, sx, sy, rows):
    n, labels, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
    areas = stats[:, cv2.CC_STAT_AREA]
    out = []
    H, W = ink.shape
    for r in rows:
        x0, y0, x1, y1 = r['box']
        px0 = int(round((x0 - rect.x0) * sx)); px1 = int(round((x1 - rect.x0) * sx))
        py0 = int(round((y0 - rect.y0) * sy)); py1 = int(round((y1 - rect.y0) * sy))
        px0, px1 = max(px0, 1), min(px1, W - 2)
        py0, py1 = max(py0, 1), min(py1, H - 2)
        res = dict(key=r['key'], sample_index=r.get('sample_index'), page=r['page'], column=r['column'])
        slices = dict(right=labels[py0:py1, px1 - 1:px1 + 1], left=labels[py0:py1, px0 - 1:px0 + 1],
                      top=labels[py0 - 1:py0 + 1, px0:px1], bottom=labels[py1 - 1:py1 + 1, px0:px1])
        for side, sl in slices.items():
            ids = np.unique(sl)
            ids = [int(i) for i in ids if i != 0 and areas[i] >= MIN_AREA]
            crossing = []
            for i in ids:
                bx, by, bw, bh, ar = stats[i]
                # crossing if the component has ink on both sides of the boundary within the box extent
                if side == 'right':
                    inside = bx < px1 - 1
                    outside = bx + bw > px1 + 1
                    reach = (bx + bw - px1) / sx
                    inner = (px1 - bx) / sx
                elif side == 'left':
                    inside = bx + bw > px0 + 1
                    outside = bx < px0 - 1
                    reach = (px0 - bx) / sx
                    inner = (bx + bw - px0) / sx
                elif side == 'top':
                    inside = by + bh > py0 + 1
                    outside = by < py0 - 1
                    reach = (py0 - by) / sy
                    inner = (by + bh - py0) / sy
                else:
                    inside = by < py1 - 1
                    outside = by + bh > py1 + 1
                    reach = (by + bh - py1) / sy
                    inner = (py1 - by) / sy
                if inside and outside:
                    crossing.append(dict(label=i, outside_pt=round(float(reach), 2), inside_pt=round(float(inner), 2), area_px=int(ar)))
            res[side] = dict(n_crossing=len(crossing), components=crossing)
        out.append(res)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rows', choices=['sample', 'full'], required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    rows = load_rows(a.rows)
    by_page = {}
    for r in rows:
        by_page.setdefault(r['page'], []).append(r)
    results = []
    with fitz.open(PDF) as doc:
        for k, p in enumerate(sorted(by_page)):
            ink, rect, sx, sy = page_ink(doc, p)
            results.extend(audit_page(ink, rect, sx, sy, by_page[p]))
            if k % 20 == 0:
                print('page', p, flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    if a.rows == 'full':
        # keep the output small: per-row counts and maximum outward reach per side
        compact = []
        for r in results:
            row = dict(key=r['key'], page=r['page'], column=r['column'])
            for side in ('right', 'left', 'top', 'bottom'):
                comps = r[side]['components']
                row[side] = [r[side]['n_crossing'], max([c['outside_pt'] for c in comps], default=0.0)]
            compact.append(row)
        results = compact
    a.out.write_text(json.dumps(dict(rows=a.rows, min_area_px=MIN_AREA, n=len(results), results=results)), encoding='utf-8')
    print('rows audited', len(results))


if __name__ == '__main__':
    main()
