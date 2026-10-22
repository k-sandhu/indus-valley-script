"""Contact sheet of PDF pages for locating plans; refuses the excluded Jansen pages.

Usage: contact.py <source.pdf> <output.png> <first> <last> [cols] [tile_w]
"""
import sys
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

src, out, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 6
tw = int(sys.argv[6]) if len(sys.argv) > 6 else 260
s = Path(src).resolve().as_posix().lower()
if '2026-10-21-town-axes' in s or '/measure-a/' in s:
    raise SystemExit('excluded path')
if Path(out).exists():
    raise SystemExit('output exists')
th = int(tw * 1.35)
tiles = []
with fitz.open(src) as d:
    for n in range(first, min(last, len(d)) + 1):
        if 'jansen_urban1987_interim2_govscan_77275' in s and 36 <= n <= 47:
            continue
        pg = d[n - 1]
        z = min(tw / pg.rect.width, (th - 22) / pg.rect.height)
        pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
        im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        im.thumbnail((tw - 6, th - 22))
        t = Image.new('RGB', (tw, th), 'white')
        t.paste(im, (3, 20))
        ImageDraw.Draw(t).text((4, 3), f'p{n}', fill='red')
        tiles.append(t)
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * th), (180, 180, 180))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
Path(out).parent.mkdir(parents=True, exist_ok=True)
sheet.save(out)
print(out, len(tiles))
