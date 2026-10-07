"""Reviewer: render source rows from the unchanged PDF at high resolution for independent reading.

Output goes to the local raw directory (temporary; deleted after use). Each image shows the pipeline's glyph
box extended to the right so the printed number field and classification line are visible, with the
neighbouring rows above and below. No predictions or reference values are drawn on the images.

  python render_rows.py --rows 5 13 14 --scale 5 --out <dir> [--sheet]
"""
import argparse
import json
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
PDF = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'


def render_row(doc, row, scale, pad_x0=6, pad_x1=64, pad_y=16):
    page = doc[row['pdf_page'] - 1]
    x0, y0, x1, y1 = row['glyph_pdf_box']
    clip = fitz.Rect(max(0, x0 - pad_x0), max(0, y0 - pad_y), min(page.rect.width, x1 + pad_x1), min(page.rect.height, y1 + pad_y))
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, colorspace=fitz.csGRAY)
    im = Image.frombytes('L', (pix.width, pix.height), pix.samples)
    return im, clip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rows', type=int, nargs='+', required=True)
    ap.add_argument('--scale', type=float, default=5)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--sheet', action='store_true', help='stack all rows into one image')
    ap.add_argument('--pad-x1', type=float, default=64)
    a = ap.parse_args()
    sel = {r['sample_index']: r for r in json.loads((HERE / 'blind/selection-source-only.json').read_text())['rows']}
    a.out.mkdir(parents=True, exist_ok=True)
    ims = []
    with fitz.open(PDF) as doc:
        for i in a.rows:
            im, clip = render_row(doc, sel[i], a.scale, pad_x1=a.pad_x1)
            canvas = Image.new('L', (im.width, im.height + 22), 255)
            canvas.paste(im, (0, 22))
            d = ImageDraw.Draw(canvas)
            d.text((4, 4), f"sample {i}  pdf page {sel[i]['pdf_page']}  box {[round(v, 1) for v in clip]}", fill=0)
            ims.append(canvas)
            if not a.sheet:
                canvas.save(a.out / f'row_{i:02d}.png')
    if a.sheet:
        W = max(i.width for i in ims)
        H = sum(i.height for i in ims) + 6 * (len(ims) - 1)
        sheet = Image.new('L', (W, H), 255)
        y = 0
        for im in ims:
            sheet.paste(im, (0, y))
            y += im.height + 6
        name = 'sheet_' + '_'.join(str(i) for i in a.rows) + '.png'
        sheet.save(a.out / name)
        print(a.out / name, sheet.size)


if __name__ == '__main__':
    main()
