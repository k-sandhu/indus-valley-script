"""Reviewer overlays for the v3 spot checks.

Renders, for each requested sample index, the original-PDF context (plain) and the same
context with the frozen proposal windows (red, numbered) and the glyph box (blue).
Header lines list the adjudicated strict reference sets and the top-one proposal codes.
Reads only frozen files; writes PNGs to a new directory under review-v3/.
"""
import argparse
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
RUN = PKG / 'repair/2026-10-08-v3'
PDF = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'
SCALE = 8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--rows', type=int, nargs='+', required=True)
    ap.add_argument('--pad', type=float, default=3.0)
    args = ap.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise SystemExit('output exists')
    out.mkdir(parents=True)
    pred = {r['sample_index']: r for r in json.loads((RUN / 'predictions.json').read_text())['rows']}
    ref = {r['sample_index']: r for r in json.loads((RUN / 'blind/adjudicated-reference.json').read_text())['rows']}
    sel = {r['sample_index']: r for r in json.loads((RUN / 'blind/selection.json').read_text())['rows']}
    doc = fitz.open(PDF)
    for i in args.rows:
        p = pred[i]
        s = sel[i]
        g = s['target_glyph_pdf_box']
        f = s['target_field_pdf_box']
        x0 = min(g[0], f[0]) - args.pad
        x1 = max(g[2], f[2]) + args.pad
        clip = fitz.Rect(x0, g[1] - 14, x1, g[3] + 14)
        pix = doc[p['pdf_page'] - 1].get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), clip=clip, alpha=False)
        src = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        head = 70
        img = Image.new('RGB', (src.width, src.height * 2 + head * 2 + 10), 'white')
        img.paste(src, (0, head))
        img.paste(src, (0, src.height + head * 2 + 10))
        d = ImageDraw.Draw(img)
        refs = [u['strict_candidate_codes'] for u in ref[i]['units']]
        top1 = [u['alternatives'][0]['codes'] if u['alternatives'] else None for u in p['units']]
        d.text((4, 4), f'sample {i}  PDF {p["pdf_page"]}  section {p["section"]}  crop_correct(adjudicated)={ref[i]["crop_correct"]}', fill='black')
        d.text((4, 20), f'reference strict: {refs}', fill='black')
        d.text((4, 36), f'proposal top1:    {top1}', fill='black')
        d.text((4, 52), 'plain source above; frozen unit windows (red) and glyph box (blue) below', fill='black')
        off = src.height + head * 2 + 10

        def rect(box, color, label=None):
            xy = [(box[0] - clip.x0) * SCALE, (box[1] - clip.y0) * SCALE + off,
                  (box[2] - clip.x0) * SCALE, (box[3] - clip.y0) * SCALE + off]
            d.rectangle(xy, outline=color, width=2)
            if label is not None:
                d.text((xy[0] + 3, xy[1] + 3), str(label), fill=color)
        rect(g, 'blue')
        rect(f, 'green')
        for j, u in enumerate(p['units']):
            rect(u['unit_pdf_box'], 'red', j)
        img.save(out / f'row_{i:03d}_pdf{p["pdf_page"]}.png', optimize=True)
        print(i, p['pdf_page'], img.size)


if __name__ == '__main__':
    main()
