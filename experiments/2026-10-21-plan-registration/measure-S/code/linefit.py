"""Sub-pixel straight-line fits on a plan render, for the measure-S package.

A line is given as one or more collinear pieces (x1, y1, x2, y2) in render pixels, hand-picked
from gridded crops. Along each piece we take perpendicular intensity profiles every pixel,
dropping a fraction `trim` at both ends to stay clear of corners. Each profile gives one
sub-pixel point:

  mode "ink"   the intensity-weighted centre of the dark trough nearest the pick
               (for thin drawn lines and grid lines);
  mode "edge"  the crossing of intensity level `level` met first when walking in from the
               white side (`white` = +1 when white lies on the +normal side, -1 otherwise),
               for the boundary of a grey fill against white paper.

Profiles whose trough or crossing is missing are dropped. A total-least-squares line is fitted
to the points of all pieces, points beyond max(1 px, 3 x MAD) are rejected and the fit repeated.
The picked end points are projected on the fitted line to give the line's end points.

Page azimuth is atan2(dx, -dy) in degrees, clockwise from page-up, x right and y down.
"""
import json
import math
import sys

import numpy as np
from PIL import Image


def load_gray(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float64)


def bilinear(g, x, y):
    h, w = g.shape
    x = np.clip(x - 0.5, 0, w - 1.001)
    y = np.clip(y - 0.5, 0, h - 1.001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    return (g[y0, x0] * (1 - fx) * (1 - fy) + g[y0, x0 + 1] * fx * (1 - fy)
            + g[y0 + 1, x0] * (1 - fx) * fy + g[y0 + 1, x0 + 1] * fx * fy)


def az(dx, dy):
    return math.degrees(math.atan2(dx, -dy)) % 360.0


def piece_points(g, piece, mode, half=4.0, trim=0.1, level=207.0, white=1, depth=40.0):
    """Pixel centres are at integer + 0.5 in this frame: pixel (i, j) covers [i, i+1) x [j, j+1)."""
    x1, y1, x2, y2 = piece
    L = math.hypot(x2 - x1, y2 - y1)
    u = np.array([(x2 - x1) / L, (y2 - y1) / L]); n = np.array([-u[1], u[0]])
    ts = np.arange(-half, half + 1e-9, 0.25)
    pts = []
    for s in np.arange(trim * L, (1 - trim) * L + 1e-9, 1.0):
        c = np.array([x1, y1]) + s * u
        px = c[0] + ts * n[0]; py = c[1] + ts * n[1]
        v = bilinear(g, px, py)
        if mode == "ink":
            bg = np.percentile(v, 90)
            wgt = np.clip(bg - v, 0, None)
            if wgt.max() < depth:
                continue
            k = int(np.argmax(wgt))
            # contiguous trough around the minimum
            lo = k
            while lo > 0 and wgt[lo - 1] > 0.25 * wgt[k]:
                lo -= 1
            hi = k
            while hi < len(ts) - 1 and wgt[hi + 1] > 0.25 * wgt[k]:
                hi += 1
            t = float(np.sum(ts[lo:hi + 1] * wgt[lo:hi + 1]) / np.sum(wgt[lo:hi + 1]))
        else:
            # walk in from the white side; ink met before any white (e.g. a grid line just
            # outside the edge) is skipped, and the first white-to-dark crossing after white is used
            order = list(range(len(ts) - 1, 0, -1)) if white > 0 else list(range(0, len(ts) - 1))
            t = None
            for i in order:
                j = i - 1 if white > 0 else i + 1
                if v[i] >= level > v[j]:
                    t = float(ts[i] + (ts[j] - ts[i]) * (v[i] - level) / (v[i] - v[j]))
                    break
            if t is None:
                continue
        pts.append(c + t * n)
    return np.array(pts).reshape(-1, 2)


def tls(P):
    m = P.mean(0)
    _, _, Vt = np.linalg.svd(P - m, full_matrices=False)
    return m, Vt[0]


def fit_line(g, pieces, mode="edge", half=4.0, trim=0.1, level=207.0, white=1):
    P = np.concatenate([piece_points(g, p, mode, half, trim, level, white) for p in pieces])
    if len(P) < 5:
        raise ValueError("too few points")
    keep = np.ones(len(P), bool)
    for _ in range(3):
        m, d = tls(P[keep])
        nrm = np.array([-d[1], d[0]])
        r = (P - m) @ nrm
        mad = np.median(np.abs(r[keep] - np.median(r[keep]))) * 1.4826
        new = np.abs(r) <= max(1.0, 3 * mad)
        if (new == keep).all():
            break
        keep = new
    m, d = tls(P[keep])
    a0 = np.array(pieces[0][:2], float); a1 = np.array(pieces[-1][2:], float)
    if d @ (a1 - a0) < 0:
        d = -d
    nrm = np.array([-d[1], d[0]])
    rms = float(np.sqrt(np.mean(((P[keep] - m) @ nrm) ** 2)))
    p1 = m + ((a0 - m) @ d) * d; p2 = m + ((a1 - m) @ d) * d
    return {"p1": [round(float(p1[0]), 3), round(float(p1[1]), 3)], "p2": [round(float(p2[0]), 3), round(float(p2[1]), 3)],
            "length_px": round(float(np.hypot(*(p2 - p1))), 2), "page_azimuth_deg": round(az(d[0], d[1]), 3),
            "pick_azimuth_deg": round(az(*(a1 - a0)), 3), "rms_px": round(rms, 3), "n_points": int(keep.sum()),
            "n_rejected": int((~keep).sum()), "mode": mode, "level": level if mode == "edge" else None,
            "pieces": [list(map(float, p)) for p in pieces]}


if __name__ == "__main__":
    spec = json.loads(sys.argv[2])
    g = load_gray(sys.argv[1])
    print(json.dumps(fit_line(g, **spec), indent=1))
