"""Trace a printed grid line (or frame line) across a rendered plan and report its local rotation.

Usage: python .../code/gridtrace.py IMAGE h|v POS START END [--step S] [--win W] [--tol T]

For a near-horizontal line at y = POS (or near-vertical at x = POS) between START and END,
we step along the line, find the thin dark run nearest the running prediction, and fit
straight pieces of WIN pixels. Each piece's rotation from the nominal direction (degrees,
positive clockwise) shows how the page is rotated locally; differences between pieces
measure the curvature and shear of the reproduction.
"""
import math
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def trace(g, orient, pos, start, end, step=4, tol=5, maxthick=6):
    pts = []
    pred = pos
    for t in range(int(start), int(end), step):
        if orient == "h":
            lo, hi = int(pred - tol), int(pred + tol + 1)
            col = g[lo:hi, t]
        else:
            lo, hi = int(pred - tol), int(pred + tol + 1)
            col = g[t, lo:hi]
        dark = col < 128
        runs = []
        i = 0
        while i < len(dark):
            if dark[i]:
                j = i
                while j < len(dark) and dark[j]:
                    j += 1
                runs.append((i, j))
                i = j
            else:
                i += 1
        runs = [r for r in runs if r[1] - r[0] <= maxthick and r[0] > 0 and r[1] < len(dark)]
        if not runs:
            continue
        c = min(runs, key=lambda r: abs(lo + (r[0] + r[1] - 1) / 2 - pred))
        v = lo + (c[0] + c[1]) / 2.0
        pts.append((t, v))
        if len(pts) >= 5:
            a = np.array(pts[-25:])
            k, b = np.polyfit(a[:, 0], a[:, 1], 1)
            pred = k * (t + step) + b
        else:
            pred = v
    return np.array(pts)


def pieces(pts, win, orient):
    out = []
    if len(pts) < 5:
        return out
    t0 = pts[0, 0]
    while t0 < pts[-1, 0]:
        sel = (pts[:, 0] >= t0) & (pts[:, 0] < t0 + win)
        a = pts[sel]
        if len(a) >= max(5, 0.4 * win / 4):
            k, b = np.polyfit(a[:, 0], a[:, 1], 1)
            res = a[:, 1] - (k * a[:, 0] + b)
            keep = np.abs(res) < 2.5 * max(0.5, res.std())
            k, b = np.polyfit(a[keep, 0], a[keep, 1], 1)
            rot = math.degrees(math.atan(k)) if orient == "h" else -math.degrees(math.atan(k))
            mid = t0 + win / 2
            out.append((mid, k * mid + b, rot, int(keep.sum()), float(np.std(a[keep, 1] - (k * a[keep, 0] + b)))))
        t0 += win
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    img, orient, pos, start, end = a[0], a[1], float(a[2]), float(a[3]), float(a[4])
    step = int(a[a.index("--step") + 1]) if "--step" in a else 4
    win = float(a[a.index("--win") + 1]) if "--win" in a else 300
    tol = float(a[a.index("--tol") + 1]) if "--tol" in a else 5
    g = np.asarray(Image.open(img).convert("L"), dtype=np.float32)
    pts = trace(g, orient, pos, start, end, step, tol)
    print("points", len(pts))
    for mid, v, rot, n, sd in pieces(pts, win, orient):
        if orient == "h":
            print("  piece at x=%.0f y=%.1f rot %+.3f deg n %d sd %.2f" % (mid, v, rot, n, sd))
        else:
            print("  piece at y=%.0f x=%.1f rot %+.3f deg n %d sd %.2f" % (mid, v, rot, n, sd))
    if len(pts) > 5:
        k, b = np.polyfit(pts[:, 0], pts[:, 1], 1)
        rot = math.degrees(math.atan(k)) if orient == "h" else -math.degrees(math.atan(k))
        print("  whole line rot %+.3f deg" % rot)
