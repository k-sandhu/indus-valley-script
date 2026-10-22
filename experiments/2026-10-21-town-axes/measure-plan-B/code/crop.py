"""Crop a rendered page and overlay a labelled coordinate grid in PAGE pixel coordinates.

Usage:
  python .../code/crop.py IMAGE X0 Y0 X1 Y1 [--grid STEP] [--scale S] [--out NAME] [--mark x,y ...] [--rot DEG]

The crop keeps page coordinates on the grid labels, so points read from the crop are
already page coordinates. --scale enlarges the crop (nearest neighbour) for fine picking.
--mark draws small red crosses at given page coordinates to check picked points.
--seg x1,y1,x2,y2 draws a thin green segment to check a line against the drawn wall.
Output goes to data/raw/2026-10-21-town-axes/plan-B/crops/.
"""
import os
import sys

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
OUT = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "crops")


def main():
    a = sys.argv[1:]
    img = a[0]
    x0, y0, x1, y1 = map(int, a[1:5])
    opts = a[5:]
    grid = 100
    scale = 1.0
    name = None
    marks, segs = [], []
    i = 0
    while i < len(opts):
        o = opts[i]
        if o == "--grid":
            grid = int(opts[i + 1]); i += 2
        elif o == "--scale":
            scale = float(opts[i + 1]); i += 2
        elif o == "--out":
            name = opts[i + 1]; i += 2
        elif o == "--mark":
            marks.append(tuple(map(float, opts[i + 1].split(",")))); i += 2
        elif o == "--seg":
            segs.append(tuple(map(float, opts[i + 1].split(",")))); i += 2
        else:
            raise SystemExit("unknown option " + o)
    im = Image.open(img).convert("RGB")
    W, H = im.size
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    c = im.crop((x0, y0, x1, y1))
    if scale != 1.0:
        c = c.resize((int(c.width * scale), int(c.height * scale)), Image.NEAREST)
    d = ImageDraw.Draw(c)
    if grid > 0:
        gx = (x0 // grid + 1) * grid
        while gx < x1:
            X = (gx - x0) * scale
            d.line([(X, 0), (X, c.height)], fill=(0, 160, 255), width=1)
            d.text((X + 2, 2), str(gx), fill=(0, 90, 255))
            d.text((X + 2, c.height - 12), str(gx), fill=(0, 90, 255))
            gx += grid
        gy = (y0 // grid + 1) * grid
        while gy < y1:
            Y = (gy - y0) * scale
            d.line([(0, Y), (c.width, Y)], fill=(0, 160, 255), width=1)
            d.text((2, Y + 2), str(gy), fill=(0, 90, 255))
            d.text((c.width - 40, Y + 2), str(gy), fill=(0, 90, 255))
            gy += grid
    for (mx, my) in marks:
        X, Y = (mx - x0) * scale, (my - y0) * scale
        d.line([(X - 6, Y), (X + 6, Y)], fill=(255, 0, 0), width=1)
        d.line([(X, Y - 6), (X, Y + 6)], fill=(255, 0, 0), width=1)
    for (ax, ay, bx, by) in segs:
        d.line([((ax - x0) * scale, (ay - y0) * scale), ((bx - x0) * scale, (by - y0) * scale)], fill=(0, 200, 0), width=1)
    os.makedirs(OUT, exist_ok=True)
    base = name or os.path.splitext(os.path.basename(img))[0] + f"_{x0}_{y0}_{x1}_{y1}"
    out = os.path.join(OUT, base + ".png")
    c.save(out)
    print(out, c.size)


if __name__ == "__main__":
    main()
