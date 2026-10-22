"""Crop a rendered PNG and enlarge it with a grid labelled in the ORIGINAL render's pixel coordinates.

The crop is a viewing aid for reading endpoint coordinates; picks are always given in the
coordinates of the original render whose sidecar is passed to measure_lines.py.
Optional --lines draws picked or refined lines (original coordinates) for checking.

Usage: zoomgrid.py <render.png> <out.png> x0 y0 x1 y1 [--zoom 4] [--step 10]
       [--lines lines.json] [--picks picks.json]
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

p = argparse.ArgumentParser()
p.add_argument('src'); p.add_argument('out')
p.add_argument('box', type=float, nargs=4)
p.add_argument('--zoom', type=int, default=4)
p.add_argument('--step', type=float, default=10)
p.add_argument('--lines', help='measure_lines output: draws refined endpoints in red')
p.add_argument('--picks', help='picks file: draws picked endpoints in blue')
p.add_argument('--label-every', type=int, default=1)
a = p.parse_args()
if Path(a.out).exists():
    raise SystemExit('output exists')
im = Image.open(a.src).convert('RGB')
x0, y0, x1, y1 = a.box
crop = im.crop((int(x0), int(y0), int(x1), int(y1)))
z = a.zoom
crop = crop.resize((crop.width * z, crop.height * z), Image.Resampling.NEAREST)
d = ImageDraw.Draw(crop)
ox, oy = int(x0), int(y0)

def to(px, py):
    # integer coordinates are pixel centres: centre of pixel k maps to (k-ox+0.5)*z
    return ((px - ox + 0.5) * z, (py - oy + 0.5) * z)

import math
k = 0
gx = math.ceil(x0 / a.step) * a.step
while gx < x1:
    X = to(gx, 0)[0]
    d.line([(X, 0), (X, crop.height)], fill=(0, 200, 255), width=1)
    if k % a.label_every == 0:
        d.text((X + 2, 2), f'{gx:g}', fill=(255, 0, 255), stroke_width=1, stroke_fill='white')
    gx += a.step; k += 1
k = 0
gy = math.ceil(y0 / a.step) * a.step
while gy < y1:
    Y = to(0, gy)[1]
    d.line([(0, Y), (crop.width, Y)], fill=(0, 200, 255), width=1)
    if k % a.label_every == 0:
        d.text((2, Y + 2), f'{gy:g}', fill=(255, 0, 255), stroke_width=1, stroke_fill='white')
    gy += a.step; k += 1
if a.picks:
    pk = json.loads(Path(a.picks).read_text(encoding='utf-8'))
    items = list(pk.get('lines', []))
    if pk.get('north'):
        items.append(dict(id='north', endpoints_px=pk['north']['line']['endpoints_px']))
    for ln in items:
        (ax, ay), (bx, by) = ln['endpoints_px']
        d.line([to(ax, ay), to(bx, by)], fill=(0, 0, 255), width=1)
        d.text(to(ax, ay), ln['id'], fill=(0, 0, 255), stroke_width=1, stroke_fill='white')
if a.lines:
    res = json.loads(Path(a.lines).read_text(encoding='utf-8'))
    items = list(res.get('lines', []))
    if res.get('arrow'):
        items.append(dict(id='north', refined_endpoints_px=res['arrow']['refined_endpoints_px']))
    for ln in items:
        (ax, ay), (bx, by) = ln['refined_endpoints_px']
        d.line([to(ax, ay), to(bx, by)], fill=(255, 0, 0), width=1)
        d.text(to(bx, by), ln['id'], fill=(255, 0, 0), stroke_width=1, stroke_fill='white')
crop.save(a.out)
print(a.out, crop.size)
