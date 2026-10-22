"""Draw picked (yellow) and refined (red or cyan) line endpoints from a measure_lines result over a fresh copy of its render.

Usage: drawlines.py <render.png> <lines.json> <out.png> [--region x0 y0 x1 y1] [--zoom k]
The arrow result of a plan, when present, is drawn in green.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("render")
    p.add_argument("lines")
    p.add_argument("out")
    p.add_argument("--region", type=int, nargs=4)
    p.add_argument("--zoom", type=int, default=1)
    p.add_argument("--labels", action="store_true")
    a = p.parse_args()
    if Path(a.out).exists():
        raise FileExistsError(a.out)
    res = json.loads(Path(a.lines).read_text(encoding="utf-8"))
    im = Image.open(a.render).convert("RGB")
    x0, y0, x1, y1 = a.region or (0, 0, im.width, im.height)
    k = a.zoom
    crop = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(crop)

    def tr(pt):
        return ((pt[0] - x0 + 0.5) * k - 0.5, (pt[1] - y0 + 0.5) * k - 0.5)

    for line in res.get("lines", []):
        pk = [tr(q) for q in line["endpoints_px"]]
        rf = [tr(q) for q in line["refined_endpoints_px"]]
        d.line(pk, fill="yellow", width=1)
        d.line(rf, fill="red", width=2)
        if a.labels:
            d.text((rf[0][0] + 3, rf[0][1] + 3), line["id"], fill="cyan", stroke_width=1, stroke_fill="black")
    if res.get("arrow"):
        rf = [tr(q) for q in res["arrow"]["refined_endpoints_px"]]
        d.line(rf, fill=(0, 200, 0), width=2)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    crop.save(a.out)
    print(a.out, crop.size)


if __name__ == "__main__":
    main()
