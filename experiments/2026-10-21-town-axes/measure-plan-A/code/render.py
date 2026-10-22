"""Render one PDF page (zero-based index) at a given dpi, optionally cropping.

usage: python render.py PDF INDEX DPI OUT.png [x0 y0 x1 y1 in rendered pixels]
Prints the output size and SHA-256 of the PNG.
"""
import sys, fitz, hashlib
from PIL import Image
pdf, idx, dpi, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
d = fitz.open(pdf)
pg = d[idx]
z = dpi / 72.0
pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csRGB)
im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
if len(sys.argv) > 8:
    x0, y0, x1, y1 = map(int, sys.argv[5:9])
    im = im.crop((x0, y0, x1, y1))
im.save(out)
print(out, im.size, hashlib.sha256(open(out, 'rb').read()).hexdigest())
