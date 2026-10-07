"""Reviewer: show chart-atlas cells for given Finnish lower codes next to each other (temporary, local raw).

  python chart_cells.py --codes 597 599 13 106 --out <png> [--scale 2]
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
ATLAS = ROOT / 'output/chart_atlas'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--codes', type=int, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--scale', type=float, default=1.5)
    a = ap.parse_args()
    ref = json.loads((ATLAS / 'reference.json').read_text(encoding='utf-8'))['rows']
    cells = []
    for code in a.codes:
        hits = [r for r in ref if code == int(r['code']) or code in [int(x) for x in r['alternatives']]]
        for r in hits:
            p = ATLAS / 'cells' / f"p{r['pdf_page']}_c{r['column']}_r{r['row']}.png"
            cells.append((code, r, Image.open(p).convert('L')))
        if not hits:
            cells.append((code, None, None))
    w = max([c[2].width for c in cells if c[2] is not None] + [60])
    h = max([c[2].height for c in cells if c[2] is not None] + [40])
    cw, ch = int(w * a.scale) + 12, int(h * a.scale) + 40
    cols = min(len(cells), 6)
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new('L', (cols * cw, rows * ch), 255)
    d = ImageDraw.Draw(sheet)
    for k, (code, r, im) in enumerate(cells):
        x, y = (k % cols) * cw, (k // cols) * ch
        if im is not None:
            im2 = im.resize((int(im.width * a.scale), int(im.height * a.scale)))
            sheet.paste(im2, (x + 6, y + 4))
            d.text((x + 6, y + ch - 32), f"code {code} (cell code {r['code']} alt {r['alternatives']})", fill=0)
            d.text((x + 6, y + ch - 18), f"p{r['pdf_page']} c{r['column']} r{r['row']} rank {r['rank']} dashed={r['dashed_auxiliary']}", fill=0)
        else:
            d.text((x + 6, y + 4), f"code {code}: no chart cell", fill=0)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out)
    print(a.out, sheet.size, len(cells))


if __name__ == '__main__':
    main()
