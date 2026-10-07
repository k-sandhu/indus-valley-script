"""Reviewer: gallery of unit-level disagreements between the primary reference and the pipeline's top-1 code.

For each aligned (pipeline unit, reference unit) pair whose top-1 candidate set does not intersect the strict reference set
(page-37 rotated rows excluded), draw: the source unit from the unchanged PDF at 6x (strip height plus margin, so
underlines show), the chart-atlas cell for each strict reference code, and the cells for the pipeline's top-1 and top-2
templates. Temporary images go to the local raw directory.

  python gallery.py --out <dir> [--per-sheet 8]
"""
import argparse
import json
import sys
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
from evaluate import align  # noqa: E402

ROOT = HERE.parents[1]
ATLAS = ROOT / 'output/chart_atlas'
PDF = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'


def cell_for_code(ref_rows, code):
    for r in ref_rows:
        if code == int(r['code']) or code in [int(x) for x in r['alternatives']]:
            return Image.open(ATLAS / 'cells' / f"p{r['pdf_page']}_c{r['column']}_r{r['row']}.png").convert('L')
    return None


def cell_for_key(key):
    p, c, r = key.split(':')
    return Image.open(ATLAS / 'cells' / f'p{p}_c{c}_r{r}.png').convert('L')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--per-sheet', type=int, default=8)
    ap.add_argument('--scale', type=float, default=6)
    ap.add_argument('--mode', choices=['top1', 'top5'], default='top1')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pred = json.loads((ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']
    refs = {}
    for n in 'abc':
        for r in json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))['rows']:
            refs[r['sample_index']] = r
    chart = json.loads((ATLAS / 'reference.json').read_text(encoding='utf-8'))['rows']
    pairs = []
    for row in pred:
        i = row['sample_index']
        if i in (14, 15, 16):
            continue
        truth = [set(int(c) for c in u['strict_candidate_codes']) for u in refs[i]['units']]
        g5 = [{int(c) for al in u['alternatives'][:5] for c in al['codes']} for u in row['units']]
        al = align(g5, truth)
        for pi, ti in al['alignment']:
            if pi is None or ti is None:
                continue
            u = row['units'][pi]
            top1 = {int(c) for c in u['alternatives'][0]['codes']} if u['alternatives'] else set()
            top5 = g5[pi]
            bad = not (top1 & truth[ti]) if a.mode == 'top1' else not (top5 & truth[ti])
            if bad:
                pairs.append((i, pi, ti, row, u, sorted(truth[ti])))
    print('pairs', len(pairs))
    index = []
    sheets = [pairs[k:k + a.per_sheet] for k in range(0, len(pairs), a.per_sheet)]
    with fitz.open(PDF) as doc:
        for s, group in enumerate(sheets):
            rows_img = []
            for (i, pi, ti, row, u, truthc) in group:
                x0, y0, x1, y1 = row['glyph_xyxy_2x']
                ux0, ux1 = u['x_bounds']
                clip = fitz.Rect((x0 + ux0 - 6) / 2, (y0 - 4) / 2, (x0 + ux1 + 6) / 2, (y1 + 10) / 2)
                page = doc[row['pdf_page'] - 1]
                pix = page.get_pixmap(matrix=fitz.Matrix(a.scale, a.scale), clip=clip, colorspace=fitz.csGRAY)
                crop = Image.frombytes('L', (pix.width, pix.height), pix.samples)
                cells = []
                labels = []
                for c in truthc:
                    im = cell_for_code(chart, c)
                    if im is not None:
                        cells.append(im)
                        labels.append(f'REF {c}')
                for k, al in enumerate(u['alternatives'][:2]):
                    cells.append(cell_for_key(al['template_key']))
                    labels.append(f"PRED#{k + 1} {al['codes']}")
                H = 130
                W = crop.width + 20 + sum(c.width + 6 for c in cells)
                canvas = Image.new('L', (max(W, 400), H), 255)
                d = ImageDraw.Draw(canvas)
                cy = max(0, (H - crop.height) // 2)
                canvas.paste(crop, (0, min(cy, H - crop.height) if crop.height < H else 0))
                x = crop.width + 20
                for c, lab in zip(cells, labels):
                    canvas.paste(c, (x, 8))
                    d.text((x + 2, 0), lab, fill=0)
                    x += c.width + 6
                rows_img.append((f'sample {i} unit {pi}/ref {ti}', canvas))
                index.append(dict(sheet=s, sample_index=i, pred_unit=pi, ref_unit=ti, ref_codes=truthc,
                                  pred_top2=[al['codes'] for al in u['alternatives'][:2]]))
            Wm = max(c.width for _, c in rows_img)
            Hs = sum(c.height + 16 for _, c in rows_img)
            sheet = Image.new('L', (Wm, Hs), 255)
            d = ImageDraw.Draw(sheet)
            y = 0
            for lab, c in rows_img:
                d.text((2, y + 2), lab, fill=0)
                sheet.paste(c, (0, y + 14))
                y += c.height + 16
            sheet.save(a.out / f'gallery_{a.mode}_{s:02d}.png')
    (a.out / f'gallery_{a.mode}_index.json').write_text(json.dumps(index, indent=1))
    print('sheets', len(sheets))


if __name__ == '__main__':
    main()
