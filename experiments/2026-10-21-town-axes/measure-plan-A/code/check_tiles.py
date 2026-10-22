"""Compose close-up tiles along each fitted line for visual checking.

usage: python check_tiles.py RESULT.json OVERLAY.png OUT.png [half] [ids...]
For every line in RESULT.json (or only the ids given), five crops of size
2*half pixels are taken from the overlay at 3, 25, 50, 75 and 97 percent of the
fitted segment and laid out in one row, labelled with the line id.
"""
import sys, json
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
res = json.load(open(sys.argv[1], encoding="utf-8"))
ov = Image.open(sys.argv[2]).convert("RGB")
out = sys.argv[3]
half = int(sys.argv[4]) if len(sys.argv) > 4 else 60
ids = set(sys.argv[5:])
lines = [l for l in res["lines"] if not ids or l["id"] in ids]
fr = [0.03, 0.25, 0.5, 0.75, 0.97]
T = 2 * half
W = Image.new("RGB", (60 + len(fr) * (T + 4), len(lines) * (T + 4)), "white")
d = ImageDraw.Draw(W)
for r, l in enumerate(lines):
    (x1, y1), (x2, y2) = l["p1_px"], l["p2_px"]
    d.text((2, r * (T + 4) + T // 2), l["id"], fill=(200, 0, 0))
    for k, f in enumerate(fr):
        cx, cy = x1 + f * (x2 - x1), y1 + f * (y2 - y1)
        c = ov.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half)))
        W.paste(c, (60 + k * (T + 4), r * (T + 4)))
W.save(out)
print(out, W.size)
