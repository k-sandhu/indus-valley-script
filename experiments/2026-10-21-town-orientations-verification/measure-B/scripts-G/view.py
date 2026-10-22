"""Working views for measurer B, share G.

Crop and enlarge a rendered PNG, draw a labelled grid in the render's own pixel
coordinates, and optionally overlay picked and refined lines.  The input render
is never modified; the output is a new working image that refuses to overwrite.

Usage:
  python -I view.py <render.png> <out.png> [--region x0 y0 x1 y1] [--zoom 3]
                    [--grid 20] [--lines lines.json ...] [--picks picks.json ...]
                    [--label]
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("render")
    p.add_argument("output")
    p.add_argument("--region", type=float, nargs=4)
    p.add_argument("--zoom", type=int, default=1)
    p.add_argument("--grid", type=float, default=0)
    p.add_argument("--lines", nargs="*", default=[])
    p.add_argument("--picks", nargs="*", default=[])
    p.add_argument("--label", action="store_true")
    p.add_argument("--width", type=int, default=1)
    a = p.parse_args()
    out = Path(a.output)
    if out.exists():
        raise FileExistsError(out)
    im = Image.open(a.render).convert("RGB")
    x0, y0, x1, y1 = a.region if a.region else (0, 0, im.width, im.height)
    crop = im.crop((int(x0), int(y0), int(x1), int(y1)))
    z = a.zoom
    crop = crop.resize((crop.width * z, crop.height * z), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(crop)

    def tr(x, y):
        # integer render coordinates are pixel centres
        return ((x - int(x0) + 0.5) * z, (y - int(y0) + 0.5) * z)

    if a.grid:
        g = a.grid
        gx = (int(x0 // g) + 1) * g
        while gx < x1:
            q = tr(gx, y0)[0]
            d.line([(q, 0), (q, crop.height)], fill=(255, 0, 255), width=1)
            d.text((q + 2, 2), f"{gx:g}", fill=(255, 255, 0), stroke_width=1, stroke_fill="black")
            gx += g
        gy = (int(y0 // g) + 1) * g
        while gy < y1:
            q = tr(x0, gy)[1]
            d.line([(0, q), (crop.width, q)], fill=(255, 0, 255), width=1)
            d.text((2, q + 2), f"{gy:g}", fill=(255, 255, 0), stroke_width=1, stroke_fill="black")
            gy += g
    for path in a.picks:
        data = load(path)
        rows = data.get("lines", [])
        for r in rows:
            (ax, ay), (bx, by) = r["endpoints_px"]
            d.line([tr(ax, ay), tr(bx, by)], fill=(255, 140, 0), width=a.width)
            if a.label:
                d.text(tr(ax, ay), r["id"], fill=(255, 140, 0), stroke_width=1, stroke_fill="black")
    for path in a.lines:
        data = load(path)
        for r in data.get("lines", []):
            (ax, ay), (bx, by) = r["refined_endpoints_px"]
            d.line([tr(ax, ay), tr(bx, by)], fill=(0, 255, 255), width=a.width)
            if a.label:
                d.text(tr(bx, by), r["id"], fill=(0, 255, 255), stroke_width=1, stroke_fill="black")
        arrow = data.get("arrow")
        if arrow:
            (ax, ay), (bx, by) = arrow["refined_endpoints_px"]
            d.line([tr(ax, ay), tr(bx, by)], fill=(255, 0, 0), width=a.width)
    out.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out)
    print(out, crop.size)


if __name__ == "__main__":
    sys.exit(main())
