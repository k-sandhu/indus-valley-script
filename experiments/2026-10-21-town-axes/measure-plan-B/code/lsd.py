"""Detect straight segments in a region of a rendered plan to help pick walls.

Usage:
  python .../code/lsd.py IMAGE X0 Y0 X1 Y1 [--min PX] [--out NAME] [--blur K] [--scale S]

Runs OpenCV's line segment detector on the crop, keeps segments longer than --min pixels,
merges nothing, and writes (1) a crop with the segments drawn and numbered and (2) a JSON
list of the segments in page pixels with their page azimuth (0-180, clockwise from up).
The candidates are only an aid: we choose which detected edges are Harappan walls, drains
or street edges by reading the plan, and every chosen line is re-fitted with refine.py.
"""
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
OUT = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "crops")


def main():
    a = sys.argv[1:]
    img = a[0]
    x0, y0, x1, y1 = map(int, a[1:5])
    opts = a[5:]
    mn, name, blur, scale = 60.0, None, 0, 1.0
    i = 0
    while i < len(opts):
        if opts[i] == "--min":
            mn = float(opts[i + 1]); i += 2
        elif opts[i] == "--out":
            name = opts[i + 1]; i += 2
        elif opts[i] == "--blur":
            blur = int(opts[i + 1]); i += 2
        elif opts[i] == "--scale":
            scale = float(opts[i + 1]); i += 2
        else:
            raise SystemExit("bad option " + opts[i])
    g = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    sub = g[y0:y1, x0:x1]
    if blur:
        sub = cv2.GaussianBlur(sub, (blur, blur), 0)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    lines = lsd.detect(sub)[0]
    segs = []
    if lines is not None:
        for l in lines[:, 0, :]:
            ax, ay, bx, by = map(float, l)
            L = math.hypot(bx - ax, by - ay)
            if L < mn:
                continue
            az = math.degrees(math.atan2(bx - ax, -(by - ay))) % 180
            segs.append(dict(p1=[ax + x0, ay + y0], p2=[bx + x0, by + y0], len_px=L, az=az))
    segs.sort(key=lambda s: -s["len_px"])
    for k, s in enumerate(segs):
        s["id"] = k
    im = Image.open(img).convert("RGB").crop((x0, y0, x1, y1))
    if scale != 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)))
    d = ImageDraw.Draw(im)
    for s in segs:
        p = [((s["p1"][0] - x0) * scale, (s["p1"][1] - y0) * scale), ((s["p2"][0] - x0) * scale, (s["p2"][1] - y0) * scale)]
        d.line(p, fill=(255, 0, 0), width=1)
        mx, my = (p[0][0] + p[1][0]) / 2, (p[0][1] + p[1][1]) / 2
        d.text((mx + 2, my - 5), str(s["id"]), fill=(0, 0, 255))
    base = name or "lsd"
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, base + ".png"))
    with open(os.path.join(OUT, base + ".json"), "w") as f:
        json.dump(segs, f, indent=0)
    print(os.path.join(OUT, base + ".png"), len(segs))
    for s in segs[:80]:
        print("%3d len %6.1f az %7.2f  (%.0f,%.0f)-(%.0f,%.0f)" % (s["id"], s["len_px"], s["az"], *s["p1"], *s["p2"]))


if __name__ == "__main__":
    main()
