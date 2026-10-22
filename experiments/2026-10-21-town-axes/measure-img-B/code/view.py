"""Make inspection crops with a labelled pixel grid (role img-B).

Usage: python view.py <mosaic.png> <x0> <y0> <x1> <y1> <out.png> [grid_step] [scale]
Coordinates are mosaic pixel coordinates. Crops are written under the raw-data
directory because they are derived from third-party imagery.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def crop_grid(src, x0, y0, x1, y1, out, step=50, scale=1.0, lines=None, polys=None):
    if isinstance(src, Image.Image):
        im = src.convert("RGB")  # already cropped to (x0, y0, x1, y1)
    else:
        im = Image.open(src).convert("RGB").crop((x0, y0, x1, y1))
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    if step:
        gx = (x0 // step + 1) * step
        while gx < x1:
            X = (gx - x0) * scale
            d.line([(X, 0), (X, im.height)], fill=(0, 255, 255), width=1)
            d.text((X + 2, 2), str(gx), fill=(255, 255, 0))
            gx += step
        gy = (y0 // step + 1) * step
        while gy < y1:
            Y = (gy - y0) * scale
            d.line([(0, Y), (im.width, Y)], fill=(0, 255, 255), width=1)
            d.text((2, Y + 2), str(gy), fill=(255, 255, 0))
            gy += step
    for poly in polys or []:
        pts = [((px - x0) * scale, (py - y0) * scale) for px, py in poly]
        d.line(pts + [pts[0]], fill=(255, 0, 255), width=2)
    for ln in lines or []:
        (ax, ay), (bx, by) = ln[:2]
        col = ln[2] if len(ln) > 2 else (255, 0, 0)
        d.line([((ax - x0) * scale, (ay - y0) * scale), ((bx - x0) * scale, (by - y0) * scale)], fill=col, width=2)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    im.save(out, **({"quality": 88} if str(out).lower().endswith(".jpg") else {}))
    return out


if __name__ == "__main__":
    a = sys.argv
    step = int(a[7]) if len(a) > 7 else 50
    scale = float(a[8]) if len(a) > 8 else 1.0
    crop_grid(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]), a[6], step, scale)
