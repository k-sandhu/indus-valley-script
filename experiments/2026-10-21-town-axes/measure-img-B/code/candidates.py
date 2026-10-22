"""Propose candidate check lines inside each polygon of a town (role img-B).

Usage: python .../code/candidates.py <slug> [min_len_m]

We run the OpenCV line-segment detector (LSD) on the mosaic inside every
polygon, merge collinear pieces of the same edge, and keep merged lines longer
than min_len_m. Each candidate is drawn with its number on an enlarged crop
(written under the raw-data views directory) so that we can accept or reject
it by eye. Accepted candidates are copied into the town configuration as
check lines with their endpoints.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import orient  # noqa: E402
import tiles  # noqa: E402
from measure import load_cfg, load_source  # noqa: E402

VIEWS = tiles.RAW / "views"


def lsd_segments(gray_u8, mask):
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    lines = lsd.detect(gray_u8)[0]
    if lines is None:
        return np.zeros((0, 4))
    seg = lines[:, 0, :]
    keep = []
    for s in seg:
        mx, my = (s[0] + s[2]) / 2, (s[1] + s[3]) / 2
        iy, ix = int(round(my)), int(round(mx))
        if 0 <= iy < mask.shape[0] and 0 <= ix < mask.shape[1] and mask[iy, ix]:
            keep.append(s)
    return np.array(keep) if keep else np.zeros((0, 4))


def seg_angle(s):
    return math.degrees(math.atan2(s[2] - s[0], -(s[3] - s[1]))) % 180.0


def merge(segs, ang_tol=2.5, perp_tol=2.0, gap_tol=12.0):
    L = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
    order = np.argsort(-L)
    ANG = np.degrees(np.arctan2(segs[:, 2] - segs[:, 0], -(segs[:, 3] - segs[:, 1]))) % 180.0
    used = np.zeros(len(segs), bool)
    out = []
    for i in order:
        if used[i] or L[i] < 6:
            continue
        members = [i]
        used[i] = True
        changed = True
        while changed:
            changed = False
            P = np.concatenate([[segs[k, :2], segs[k, 2:]] for k in members])
            c = P.mean(0)
            _, _, Vt = np.linalg.svd(P - c)
            d, n = Vt[0], Vt[1]
            a_ref = math.degrees(math.atan2(d[0], -d[1])) % 180
            proj = (P - c) @ d
            lo, hi = proj.min(), proj.max()
            cand = (~used) & (L >= 4)
            if not cand.any():
                break
            dk = np.abs(((ANG - a_ref) + 90) % 180 - 90)
            cand &= dk <= ang_tol
            e0 = segs[:, :2] - c
            e1 = segs[:, 2:] - c
            cand &= np.maximum(np.abs(e0 @ n), np.abs(e1 @ n)) <= perp_tol
            p0, p1 = e0 @ d, e1 @ d
            cand &= ~((np.minimum(p0, p1) > hi + gap_tol) | (np.maximum(p0, p1) < lo - gap_tol))
            new = np.nonzero(cand)[0]
            if len(new):
                members.extend(int(k) for k in new)
                used[new] = True
                changed = True
        # fit through points sampled along member segments
        pts = []
        for k in members:
            n_s = max(2, int(L[k] / 2))
            for t in np.linspace(0, 1, n_s):
                pts.append(segs[k, :2] * (1 - t) + segs[k, 2:] * t)
        P = np.array(pts)
        c = P.mean(0)
        _, _, Vt = np.linalg.svd(P - c)
        d = Vt[0]
        if d[1] > 0:
            d = -d  # point north
        proj = (P - c) @ d
        res = (P - c) @ Vt[1]
        a, b = c + d * proj.min(), c + d * proj.max()
        span = proj.max() - proj.min()
        cover = float(sum(L[k] for k in members) / span) if span > 0 else 0
        rms = float(np.sqrt(np.mean(res ** 2)))
        out.append({"p0": [round(float(a[0]), 2), round(float(a[1]), 2)], "p1": [round(float(b[0]), 2), round(float(b[1]), 2)],
                    "len_px": round(float(span), 1), "n_pieces": len(members), "coverage": round(min(cover, 1.0), 2),
                    "rms_px": round(rms, 2)})
    return out


def run(slug, min_len_m=15.0):
    cfg = load_cfg(slug)
    z = cfg["zoom"]
    sdefs = cfg.get("sources") or [dict(cfg["mosaic"], id="src1")]
    loaded = {sd["id"]: load_source(cfg, sd, z) for sd in sdefs}
    first = sdefs[0]["id"]
    mpp = tiles.m_per_px(cfg["location"]["lat"], z)
    allc = {}
    for P in cfg["parts"]:
        if P.get("no_candidates"):
            continue
        rgb = loaded[P.get("source", first)][1]
        gray = orient.luminance(rgb.astype(float)).astype(np.uint8)
        mask = orient.poly_mask(gray.shape, P["polys"], P.get("holes", []))
        segs = lsd_segments(gray, mask)
        merged = [c for c in merge(segs) if c["len_px"] * mpp >= min_len_m]
        merged.sort(key=lambda c: -c["len_px"])
        for j, c in enumerate(merged):
            b, dv = orient.line_bearing(*c["p0"], *c["p1"])
            c.update({"id": f"{P['id']}-{j + 1}", "len_m": round(c["len_px"] * mpp, 1), "bearing": round(b, 2), "deviation": round(dv, 2)})
        allc[P["id"]] = merged
        # drawing
        allp = np.concatenate([np.asarray(p, float) for p in P["polys"]])
        x0, y0 = np.maximum(allp.min(0).astype(int) - 20, 0)
        x1, y1 = allp.max(0).astype(int) + 20
        sc = max(1.0, min(4.0, 1000.0 / max(x1 - x0, y1 - y0)))
        im = Image.fromarray(rgb[y0:y1, x0:x1]).resize((int((x1 - x0) * sc), int((y1 - y0) * sc)), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        for c in merged:
            a = ((c["p0"][0] - x0) * sc, (c["p0"][1] - y0) * sc)
            bb = ((c["p1"][0] - x0) * sc, (c["p1"][1] - y0) * sc)
            d.line([a, bb], fill=(255, 0, 0), width=2)
            mx, my = (a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2
            d.text((mx + 3, my + 3), c["id"].split("-")[1], fill=(255, 255, 0))
        for p in P["polys"]:
            q = [((u - x0) * sc, (v - y0) * sc) for u, v in p]
            d.line(q + [q[0]], fill=(255, 0, 255), width=1)
        out = VIEWS / slug / f"{P['id']}_candidates.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, quality=88)
    (VIEWS / slug / "candidates.json").write_text(json.dumps(allc, indent=1))
    return allc


if __name__ == "__main__":
    ml = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
    res = run(sys.argv[1], ml)
    for k, v in res.items():
        print(k, len(v))
        for c in v:
            print("  ", c["id"], c["len_m"], c["deviation"], c["n_pieces"], c["coverage"], c["rms_px"], c["p0"], c["p1"])
