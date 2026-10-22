"""Crop an image and overlay a labelled pixel grid so coordinates can be read by eye.

usage: python grid.py IMAGE OUT.png x0 y0 x1 y1 [step] [scale]
Coordinates on the overlay are those of the full source image, so points read
from the crop can be used directly in a measurement spec.
"""
import sys
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
step = int(sys.argv[7]) if len(sys.argv) > 7 else 50
scale = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
im = Image.open(src).convert("RGB")
x0, y0 = max(0, x0), max(0, y0)
x1, y1 = min(im.width, x1), min(im.height, y1)
c = im.crop((x0, y0, x1, y1))
if scale != 1.0:
    c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
dr = ImageDraw.Draw(c, "RGBA")
gx = (x0 // step + 1) * step
while gx < x1:
    X = (gx - x0) * scale
    dr.line([(X, 0), (X, c.height)], fill=(0, 160, 255, 110), width=1)
    dr.text((X + 2, 2), str(gx), fill=(0, 90, 200, 255))
    gx += step
gy = (y0 // step + 1) * step
while gy < y1:
    Y = (gy - y0) * scale
    dr.line([(0, Y), (c.width, Y)], fill=(0, 160, 255, 110), width=1)
    dr.text((2, Y + 2), str(gy), fill=(0, 90, 200, 255))
    gy += step
c.save(out)
print(out, c.size)
