"""Render low-resolution thumbnails of PDF pages into labelled contact sheets.

usage: python contact.py PDF OUTDIR [first last] [cols rows thumbw]
Page labels are zero-based PDF page indices.
"""
import sys, os, fitz
from PIL import Image, ImageDraw

pdf, out = sys.argv[1], sys.argv[2]
d = fitz.open(pdf)
first = int(sys.argv[3]) if len(sys.argv) > 3 else 0
last = min(int(sys.argv[4]) if len(sys.argv) > 4 else d.page_count - 1, d.page_count - 1)
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 6
rows = int(sys.argv[6]) if len(sys.argv) > 6 else 5
tw = int(sys.argv[7]) if len(sys.argv) > 7 else 200
os.makedirs(out, exist_ok=True)
per = cols * rows
th = int(tw * 1.4)
base = os.path.splitext(os.path.basename(pdf))[0]
for s in range(first, last + 1, per):
    sheet = Image.new("RGB", (cols * tw, rows * (th + 14)), "white")
    dr = ImageDraw.Draw(sheet)
    for k, i in enumerate(range(s, min(s + per, last + 1))):
        pg = d[i]
        z = tw / max(pg.rect.width, pg.rect.height / 1.4)
        pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csRGB)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        x, y = (k % cols) * tw, (k // cols) * (th + 14)
        sheet.paste(im, (x, y + 14))
        dr.text((x + 3, y + 1), str(i), fill=(255, 0, 0))
    sheet.save(os.path.join(out, f"{base}_{s:04d}.png"))
    print(os.path.join(out, f"{base}_{s:04d}.png"))
