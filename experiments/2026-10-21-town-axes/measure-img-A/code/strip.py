"""Rectified strips along picked lines, for reading edge offsets by eye.

usage:
  python strip.py one MOSAIC X1 Y1 X2 Y2 [--half 8] [--sx 4] [--sy 12] [--ext 10] [--out NAME]
  python strip.py picks PICKS.json [--ids S1,S2,...] [--corrected] [--half 8] [--out NAME]

X1 Y1 X2 Y2 are global pixel coordinates of a provisional line picked on a crop.
The strip resamples the mosaic along that line: columns run from P1 (left) to
P2 (right) at one native pixel per column (magnified sx times), rows run across
the line from -half to +half native pixels at 1/sy pixel steps. Positive offsets
point to the right-hand side of the direction P1->P2 in the image (for a line
picked from south to north, positive is east; for a line picked from west to
east, positive is south). A straight edge lying exactly on the provisional line
appears as a horizontal feature on the 0 row. Two side panels plot the mean grey
level across the line over the first and the last quarter of its length, which
makes the position of a dark band or a step in brightness easier to read. We
read the edge's offset o1 at the P1 end and o2 at the P2 end by eye and record
them in the picks file; the measured endpoints are then P1 + o1*n and P2 + o2*n.
With --corrected the strips are drawn along the corrected endpoints, so a good
reading shows the edge flat on the 0 row.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "data" / "raw" / "2026-10-21-town-axes" / "img-A"
_CACHE = {}

try:
    FONT = ImageFont.truetype("arial.ttf", 11)
except OSError:
    FONT = ImageFont.load_default()


def load(mpath):
    mpath = Path(mpath)
    if not mpath.is_absolute():
        mpath = ROOT / mpath
    if mpath not in _CACHE:
        rec = json.loads(mpath.with_suffix(".json").read_text())
        img = np.asarray(Image.open(mpath).convert("RGB")).astype(float)
        _CACHE[mpath] = (img, rec)
    return _CACHE[mpath]


def corrected(line):
    (x1, y1), (x2, y2) = line["p1"], line["p2"]
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    o1, o2 = line.get("o1", 0.0), line.get("o2", 0.0)
    return [x1 + o1 * nx, y1 + o1 * ny], [x2 + o2 * nx, y2 + o2 * ny]


def render(mosaic, p1, p2, half=8, sx=4, sy=12, ext=10, label=""):
    img, rec = load(mosaic)
    ox, oy = rec["origin_global_px"]
    x1, y1, x2, y2 = p1[0] - ox, p1[1] - oy, p2[0] - ox, p2[1] - oy
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    t = np.arange(-ext, L + ext + 1e-9, 1.0)
    o = np.arange(-half, half + 1e-9, 1.0 / sy)
    T, O = np.meshgrid(t, o)
    X = x1 + T * ux + O * nx
    Y = y1 + T * uy + O * ny
    out = np.stack([map_coordinates(img[..., k], [Y, X], order=1, mode="nearest") for k in range(3)], -1)
    grey = out.mean(-1)
    im = ImageOps.autocontrast(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), cutoff=1)
    W = int(len(t) * sx)
    im = im.resize((W, im.height), Image.BICUBIC)
    pad, PW, top = 40, 90, 16
    canvas = Image.new("RGB", (W + 2 * pad + 2 * PW, im.height + top), (30, 30, 30))
    canvas.paste(im, (pad, top))
    d = ImageDraw.Draw(canvas)
    inside = np.where((t >= 0) & (t <= L))[0]
    nq = max(3, len(inside) // 4)
    for side, cols in (("L", inside[:nq]), ("R", inside[-nq:])):
        prof = grey[:, cols].mean(1)
        lo, hi = prof.min(), prof.max()
        x0 = W + 2 * pad + (PW if side == "R" else 0)
        for k, ov in enumerate(o):
            if abs(ov - round(ov)) < 1e-9:
                d.line([(x0 + 2, top + k), (x0 + PW - 2, top + k)],
                       fill=(120, 40, 40) if round(ov) == 0 else (55, 55, 55))
        pts = [(x0 + 4 + (v - lo) / max(hi - lo, 1e-6) * (PW - 8), top + k) for k, v in enumerate(prof)]
        d.line(pts, fill=(255, 255, 255) if side == "L" else (180, 255, 180))
        d.text((x0 + 4, 0), "P1 quarter" if side == "L" else "P2 quarter", fill=(200, 200, 200), font=FONT)
    for k, ov in enumerate(o):
        if abs(ov - round(ov)) < 1e-9:
            Yp = top + k
            r = int(round(ov))
            col = (255, 60, 60) if r == 0 else ((255, 255, 0) if r % 5 == 0 else (0, 200, 200))
            tick = 14 if r == 0 else (10 if r % 5 == 0 else 6)
            d.line([(pad - tick, Yp), (pad - 1, Yp)], fill=col)
            d.line([(pad + W, Yp), (pad + W + tick - 1, Yp)], fill=col)
            if r % 2 == 0:
                d.text((2, Yp - 6), f"{r:+d}", fill=col, font=FONT)
                d.text((pad + W + 15, Yp - 6), f"{r:+d}", fill=col, font=FONT)
            if r == 0:
                for Xp in range(pad, pad + W, 10):
                    d.point((Xp, Yp), fill=col)
    step = 10 if L < 200 else (25 if L < 500 else 50)
    for tv in np.arange(0, L + 1e-9, step):
        Xp = pad + (tv + ext) * sx
        d.line([(Xp, 0), (Xp, 12)], fill=(255, 255, 255))
        d.text((Xp + 2, 0), f"{int(tv)}", fill=(255, 255, 255), font=FONT)
    for tv in (0, L):
        Xp = pad + (tv + ext) * sx
        d.line([(Xp, 0), (Xp, 15)], fill=(255, 0, 255), width=3)
    if label:
        d.text((pad + 4, top + 2), label, fill=(255, 0, 255), font=FONT)
    return canvas, L, (nx, ny)


def stack(images, gap=6):
    W = max(i.width for i in images)
    H = sum(i.height for i in images) + gap * (len(images) - 1)
    c = Image.new("RGB", (W, H), (0, 0, 0))
    y = 0
    for i in images:
        c.paste(i, (0, y))
        y += i.height + gap
    return c


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a1 = sp.add_parser("one")
    a1.add_argument("mosaic")
    for k in ("x1", "y1", "x2", "y2"):
        a1.add_argument(k, type=float)
    a2 = sp.add_parser("picks")
    a2.add_argument("picks")
    a2.add_argument("--ids")
    a2.add_argument("--corrected", action="store_true")
    for p in (a1, a2):
        p.add_argument("--half", type=float, default=8)
        p.add_argument("--sx", type=float, default=0, help="0 = choose from length")
        p.add_argument("--sy", type=int, default=12)
        p.add_argument("--ext", type=float, default=10)
        p.add_argument("--out")
    a = ap.parse_args()

    def sx_for(L):
        return a.sx or max(1.0, min(6.0, 800.0 / (L + 2 * a.ext)))

    if a.cmd == "one":
        L = math.hypot(a.x2 - a.x1, a.y2 - a.y1)
        c, L, n = render(a.mosaic, (a.x1, a.y1), (a.x2, a.y2), a.half, sx_for(L), a.sy, a.ext)
        name = a.out or f"strip_{int(a.x1)}_{int(a.y1)}"
        p = RAW / "crops" / f"{name}.png"
        c.save(p)
        print(p, f"L={L:.1f}px n=({n[0]:+.3f},{n[1]:+.3f})")
        return
    picks = json.loads(Path(a.picks).read_text())
    ids = a.ids.split(",") if a.ids else None
    ims = []
    for ln in picks["lines"]:
        if ids and ln["id"] not in ids:
            continue
        p1, p2 = corrected(ln) if a.corrected else (ln["p1"], ln["p2"])
        L = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        n = (-(p2[1] - p1[1]) / L, (p2[0] - p1[0]) / L)
        mos = picks["mosaics"][ln["mosaic"]]
        c, L, n = render(mos, p1, p2, a.half, sx_for(L), a.sy, a.ext,
                         label=f"{ln['id']} {'corrected' if a.corrected else 'provisional'} L={L:.0f}px n=({n[0]:+.2f},{n[1]:+.2f})")
        ims.append(c)
        print(ln["id"], f"L={L:.1f}px n=({n[0]:+.3f},{n[1]:+.3f})")
    name = a.out or (Path(a.picks).stem + ("_corr" if a.corrected else "_prov"))
    p = RAW / "crops" / f"{name}.png"
    stack(ims).save(p)
    print(p)


if __name__ == "__main__":
    main()
