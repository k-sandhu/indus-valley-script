"""Refine a hand-picked line on a rendered plan by fitting the drawn ink near it.

Usage:
  python .../code/refine.py IMAGE x1 y1 x2 y2 [--band PX] [--trim FRAC] [--mode ink|edge] [--thr T] [--show]

The segment from (x1, y1) to (x2, y2) in page pixels is the hand pick. We take the ink
pixels (gray below a threshold; Otsu by default) or Canny edge pixels lying within BAND
pixels of the segment, drop the TRIM fraction at both ends to stay clear of corners and
junctions, and fit a total-least-squares line. Two passes are made, the second with half
the band around the first fit. Prints the page azimuth of the fitted line (clockwise from
page-up, 0-180), the hand-pick azimuth, the perpendicular RMS of the fitted pixels and the
pixel count. --show writes a check crop with the fitted line drawn in red.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None


def az(dx, dy):
    """Azimuth clockwise from page-up of a direction (dx right, dy down), folded to 0-180."""
    a = math.degrees(math.atan2(dx, -dy)) % 180.0
    return a


def load_gray(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32)


def otsu(vals):
    hist, edges = np.histogram(vals, bins=256, range=(0, 256))
    w = hist.astype(float)
    p = w / w.sum()
    omega = np.cumsum(p)
    mu = np.cumsum(p * np.arange(256))
    mt = mu[-1]
    sb = (mt * omega - mu) ** 2 / (omega * (1 - omega) + 1e-12)
    return float(np.argmax(sb))


def fit(gray, x1, y1, x2, y2, band=4.0, trim=0.08, mode="ink", thr=None):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    pad = int(band + 3)
    xa, xb = int(max(0, min(x1, x2) - pad)), int(min(gray.shape[1], max(x1, x2) + pad + 1))
    ya, yb = int(max(0, min(y1, y2) - pad)), int(min(gray.shape[0], max(y1, y2) + pad + 1))
    sub = gray[ya:yb, xa:xb]
    if mode == "edge":
        import cv2
        e = cv2.Canny(sub.astype(np.uint8), 50, 150)
        mask = e > 0
    else:
        t = otsu(sub.ravel()) if thr is None else thr
        mask = sub <= t
    yy, xx = np.nonzero(mask)
    X = xx + xa + 0.5
    Y = yy + ya + 0.5
    cx, cy, cux, cuy, cnx, cny = x1, y1, ux, uy, nx, ny
    res = None
    for b in (band, band, band / 2.0):
        s = (X - cx) * cux + (Y - cy) * cuy
        t_ = (X - cx) * cnx + (Y - cy) * cny
        Ls = L
        sel = (np.abs(t_) <= b) & (s >= trim * Ls) & (s <= (1 - trim) * Ls)
        if sel.sum() < 10:
            break
        P = np.stack([X[sel], Y[sel]], 1)
        m = P.mean(0)
        U, S, Vt = np.linalg.svd(P - m, full_matrices=False)
        d = Vt[0]
        if d[0] * ux + d[1] * uy < 0:
            d = -d
        nrm = np.array([-d[1], d[0]])
        perp = (P - m) @ nrm
        rms = float(np.sqrt(np.mean(perp ** 2)))
        # re-anchor: project the hand endpoints on the fitted line
        s1 = (np.array([x1, y1]) - m) @ d
        s2 = (np.array([x2, y2]) - m) @ d
        p1 = m + s1 * d
        p2 = m + s2 * d
        cx, cy = p1
        cux, cuy = d
        cnx, cny = nrm
        L = float(abs(s2 - s1))
        res = dict(az_fit=az(d[0], d[1]), az_pick=az(x2 - x1, y2 - y1), rms=rms, n=int(sel.sum()),
                   p1=(float(p1[0]), float(p1[1])), p2=(float(p2[0]), float(p2[1])), length_px=L, pts=P)
    return res


def fit_multi(gray, segs, band=4.0, trim=0.08, mode="ink", thr=None):
    """Fit one straight line to the ink of several collinear pieces (e.g. a line broken by text).

    segs is a list of (x1, y1, x2, y2) hand picks along the same drawn line, ordered from one
    end to the other. Each piece is refined separately; the selected pixels of all pieces are
    pooled for one total-least-squares fit."""
    pts = []
    for (x1, y1, x2, y2) in segs:
        r = fit(gray, x1, y1, x2, y2, band, trim, mode, thr)
        if r is None:
            raise ValueError("piece %s gave no fit" % ((x1, y1, x2, y2),))
        pts.append(r["pts"])
    P = np.concatenate(pts)
    m = P.mean(0)
    U, S, Vt = np.linalg.svd(P - m, full_matrices=False)
    d = Vt[0]
    a0 = np.array(segs[0][:2], float)
    a1 = np.array(segs[-1][2:], float)
    if d @ (a1 - a0) < 0:
        d = -d
    nrm = np.array([-d[1], d[0]])
    rms = float(np.sqrt(np.mean(((P - m) @ nrm) ** 2)))
    p1 = m + ((a0 - m) @ d) * d
    p2 = m + ((a1 - m) @ d) * d
    return dict(az_fit=az(d[0], d[1]), az_pick=az(*(a1 - a0)), rms=rms, n=len(P),
                p1=(float(p1[0]), float(p1[1])), p2=(float(p2[0]), float(p2[1])),
                length_px=float(np.hypot(*(p2 - p1))), pts=P)


def main():
    a = sys.argv[1:]
    img = a[0]
    x1, y1, x2, y2 = map(float, a[1:5])
    opts = a[5:]
    band, trim, mode, thr, show = 4.0, 0.08, "ink", None, False
    i = 0
    while i < len(opts):
        o = opts[i]
        if o == "--band":
            band = float(opts[i + 1]); i += 2
        elif o == "--trim":
            trim = float(opts[i + 1]); i += 2
        elif o == "--mode":
            mode = opts[i + 1]; i += 2
        elif o == "--thr":
            thr = float(opts[i + 1]); i += 2
        elif o == "--show":
            show = True; i += 1
        else:
            raise SystemExit("unknown option " + o)
    g = load_gray(img)
    r = fit(g, x1, y1, x2, y2, band, trim, mode, thr)
    if r is None:
        print("no fit (too few pixels)")
        return
    print("az_fit %.3f az_pick %.3f diff %.3f rms %.2f n %d len_px %.1f p1 %.1f,%.1f p2 %.1f,%.1f" % (
        r["az_fit"], r["az_pick"], ((r["az_fit"] - r["az_pick"] + 90) % 180) - 90, r["rms"], r["n"], r["length_px"],
        r["p1"][0], r["p1"][1], r["p2"][0], r["p2"][1]))
    if show:
        im = Image.open(img).convert("RGB")
        pad = 40
        xa, ya = int(min(x1, x2) - pad), int(min(y1, y2) - pad)
        xb, yb = int(max(x1, x2) + pad), int(max(y1, y2) + pad)
        c = im.crop((max(0, xa), max(0, ya), xb, yb))
        d = ImageDraw.Draw(c)
        ox, oy = max(0, xa), max(0, ya)
        d.line([(r["p1"][0] - ox, r["p1"][1] - oy), (r["p2"][0] - ox, r["p2"][1] - oy)], fill=(255, 0, 0), width=1)
        out = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "crops", "refine_check.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if max(c.size) > 1400:
            c.thumbnail((1400, 1400))
        c.save(out)
        print(out)


if __name__ == "__main__":
    main()
