"""Find candidate straight wall bars (thick dark strokes) in a rendered plan, as a picking aid.

For each trial angle the dark-ink mask of a region is rotated so that the angle is horizontal, opened
with a rectangle of length --min-len and height --width (separable minimum and maximum filters), and the
surviving connected components are traced back to render coordinates as segments through the
component's principal axis. Thin lines (hatching, grid, text, arrows) do not survive a width of 4-5 px
at 200 dpi. Overlapping detections at neighbouring angles are merged by keeping the longest.

The output segments are only candidate picks. Each must be identified with a wall on the plan by eye
(overlay) before it is copied into a picks file, and measure_lines.py refines it on the original page.

Usage: wallcands.py <render.png> <out.json> --region x0 y0 x1 y1 [--thr 110] [--min-len 50]
       [--width 5] [--step 2] [--overlay out.png]
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

p = argparse.ArgumentParser()
p.add_argument('png'); p.add_argument('out')
p.add_argument('--region', type=int, nargs=4, required=True)
p.add_argument('--thr', type=float, default=110)
p.add_argument('--min-len', type=int, default=50)
p.add_argument('--width', type=int, default=5)
p.add_argument('--step', type=float, default=2)
p.add_argument('--overlay')
p.add_argument('--blur', type=float, default=0, help='Gaussian sigma (px) applied to the grey image before thresholding; 0 = none (default, as used for the Chanhu-daro plates)')
a = p.parse_args()
if Path(a.out).exists():
    raise SystemExit('output exists')
img = Image.open(a.png).convert('L')
x0, y0, x1, y1 = a.region
gray = np.asarray(img, float)[y0:y1, x0:x1]
if a.blur > 0:
    gray = ndi.gaussian_filter(gray, a.blur)
mask = gray < a.thr
H, W = mask.shape
cy, cx = (H - 1) / 2, (W - 1) / 2
segs = []
for ang in np.arange(0, 180, a.step):
    # rotate so that a line at angle `ang` (page coords, clockwise from +x since y is down) becomes horizontal
    rot = ndi.rotate(mask.astype(np.uint8), ang, reshape=True, order=0, mode='constant', cval=0).astype(bool)
    er = ndi.minimum_filter1d(rot.astype(np.uint8), a.min_len, axis=1)
    er = ndi.minimum_filter1d(er, a.width, axis=0)
    op = ndi.maximum_filter1d(er, a.min_len, axis=1)
    op = ndi.maximum_filter1d(op, a.width, axis=0).astype(bool) & rot
    lab, n = ndi.label(op)
    if not n:
        continue
    Hr, Wr = rot.shape
    rcy, rcx = (Hr - 1) / 2, (Wr - 1) / 2
    t = math.radians(ang)
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        ys, xs = np.nonzero(lab[sl] == k)
        ys = ys + sl[0].start; xs = xs + sl[1].start
        if xs.max() - xs.min() + 1 < a.min_len:
            continue
        # map rotated coords back to region coords. ndi.rotate(angle) rotates the image by +ang
        # (counter-clockwise in the displayed image); invert that rotation.
        dx = xs - rcx; dy = ys - rcy
        ox = cx + dx * math.cos(t) - dy * math.sin(t)
        oy = cy + dx * math.sin(t) + dy * math.cos(t)
        pts = np.c_[ox, oy]
        c = pts.mean(axis=0)
        u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
        v = vt[0]
        proj = (pts - c) @ v
        e0 = c + v * proj.min(); e1 = c + v * proj.max()
        length = float(proj.max() - proj.min())
        width = float(len(pts) / max(length, 1))
        segs.append(dict(angle=float(ang), length=length, width=width,
                         p0=[float(e0[0] + x0), float(e0[1] + y0)], p1=[float(e1[0] + x0), float(e1[1] + y0)]))
# merge: keep longest; drop segments whose midpoint lies within width+3 px of a kept segment with angle within 8 deg
segs.sort(key=lambda s: -s['length'])
kept = []
def dist_point_seg(pt, s):
    a_, b_ = np.array(s['p0']), np.array(s['p1']); v = b_ - a_
    tt = np.clip(np.dot(pt - a_, v) / max(np.dot(v, v), 1e-9), 0, 1)
    return float(np.linalg.norm(pt - a_ - tt * v))
def ang_of(s):
    d = np.array(s['p1']) - np.array(s['p0'])
    return math.degrees(math.atan2(d[1], d[0])) % 180
for s in segs:
    mid = (np.array(s['p0']) + np.array(s['p1'])) / 2
    dup = False
    for k in kept:
        da = abs((ang_of(s) - ang_of(k) + 90) % 180 - 90)
        if da < 8 and dist_point_seg(mid, k) < k['width'] + 4:
            dup = True; break
    if not dup:
        kept.append(s)
for i, s in enumerate(kept):
    s['cand'] = f'c{i:02d}'
Path(a.out).write_text(json.dumps(dict(source=a.png, region=a.region, thr=a.thr, blur=a.blur, min_len=a.min_len, width=a.width, step=a.step, candidates=kept), indent=1), encoding='utf-8')
print(len(segs), 'raw;', len(kept), 'kept')
if a.overlay:
    if Path(a.overlay).exists():
        raise SystemExit('overlay exists')
    ov = img.convert('RGB').crop((x0, y0, x1, y1))
    d = ImageDraw.Draw(ov)
    for s in kept:
        q0 = (s['p0'][0] - x0, s['p0'][1] - y0); q1 = (s['p1'][0] - x0, s['p1'][1] - y0)
        d.line([q0, q1], fill=(255, 0, 0), width=2)
        d.text(((q0[0] + q1[0]) / 2 + 3, (q0[1] + q1[1]) / 2 - 5), s['cand'], fill=(0, 0, 255), stroke_width=1, stroke_fill='white')
    ov.save(a.overlay)
