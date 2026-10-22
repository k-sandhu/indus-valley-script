"""Measure line directions on a plan image relative to the plan's north arrow.

usage: python measure_lines.py SPEC.json OUT.json [OVERLAY.png]

The spec names an image and gives, for the north arrow, the scale bar, optional
frame or grid lines, and each architectural line, two approximate endpoints read
by eye from a gridded crop. Each line is refined by sampling profiles across it
every `step` pixels, taking the weighted centroid of "ink" (dark, coloured or
non-white pixels, as chosen by `mode`) within `w` pixels of the provisional line,
and fitting a straight line to the centroids by total least squares with
iterative outlier rejection. The refit is repeated about the fitted line.

Directions in the image are azimuths clockwise from image-up, computed as
atan2(dx, -dy) with x to the right and y down. The north arrow is fitted the same
way, oriented from `p1` (tail) to `p2` (head), unless `fit` is false, in which
case the two given points are used as they stand. A line's bearing relative to
plan north is (line azimuth - arrow azimuth) mod 180, and its deviation is that
bearing folded to the nearest cardinal direction, in [-45, +45).

Each line's one-sigma error combines in quadrature: the statistical slope error of
the fit, an endpoint-reading floor of `endpoint_px` pixels at each end, the north
arrow's own error, and a rendering term (`render_sigma_deg` in the spec, set from
the frame or grid checks). Frame lines are reported with their azimuths so that
skew and departures from orthogonality can be read off.
"""
import json, math, sys, hashlib
import numpy as np
from PIL import Image, ImageDraw


def load(spec):
    im = Image.open(spec["image"]).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    return im, a


def ink_map(a, mode, rgb=None, tol=60.0, thr=None):
    if mode == "dark":
        g = a.mean(axis=2)
        t = thr if thr is not None else 140.0
        return np.clip((t - g) / t, 0, 1)
    if mode == "nonwhite":
        g = a.min(axis=2)
        t = thr if thr is not None else 200.0
        return np.clip((t - g) / t, 0, 1)
    if mode == "color":
        d = np.sqrt(((a - np.array(rgb, dtype=np.float32)) ** 2).sum(axis=2))
        return np.clip(1.0 - d / tol, 0, 1)
    raise ValueError(mode)


def bilinear(m, xs, ys):
    h, w = m.shape
    xs = np.clip(xs, 0, w - 1.001)
    ys = np.clip(ys, 0, h - 1.001)
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = xs - x0
    fy = ys - y0
    return (m[y0, x0] * (1 - fx) * (1 - fy) + m[y0, x0 + 1] * fx * (1 - fy)
            + m[y0 + 1, x0] * (1 - fx) * fy + m[y0 + 1, x0 + 1] * fx * fy)


def tls(pts):
    c = pts.mean(axis=0)
    u, s, vt = np.linalg.svd(pts - c)
    d = vt[0]
    n = vt[1]
    r = (pts - c) @ n
    t = (pts - c) @ d
    return c, d, n, r, t


def refine(m, p1, p2, w, step=2.0, margin=0.06, iters=3, minw=0.15, side=0, wsched=None):
    p1 = np.array(p1, float)
    p2 = np.array(p2, float)
    info = {}
    ws = list(wsched) if wsched else [w] * iters
    for it, w in enumerate(ws):
        v = p2 - p1
        L = np.linalg.norm(v)
        d = v / L
        n = np.array([-d[1], d[0]])
        ts = np.arange(margin * L, (1 - margin) * L + 1e-9, step)
        offs = np.arange(-w, w + 1e-9, 0.5)
        P = p1[None, :] + ts[:, None] * d[None, :]
        X = P[:, 0:1] + offs[None, :] * n[0]
        Y = P[:, 1:2] + offs[None, :] * n[1]
        V = bilinear(m, X, Y)
        if side:
            # edge mode: weight by the positive step of ink towards the inked side
            G = np.gradient(V, axis=1) * side
            V = np.clip(G, 0, None)
            minw_eff = 0.02
        else:
            minw_eff = minw * 0.1
        tot = V.sum(axis=1)
        ok = tot > minw_eff * (V.shape[1] if not side else 1.0)
        if ok.sum() < 5:
            return None
        oc = (V * offs[None, :]).sum(axis=1) / np.maximum(tot, 1e-9)
        pts = P[ok] + oc[ok, None] * n[None, :]
        keep = np.ones(len(pts), bool)
        for _ in range(5):
            c, dd, nn, r, t = tls(pts[keep])
            s = r.std()
            rr = (pts - c) @ nn
            nk = np.abs(rr) <= max(2.5 * s, 0.3)
            if nk.sum() == keep.sum():
                break
            keep = nk
        c, dd, nn, r, t = tls(pts[keep])
        if dd @ d < 0:
            dd = -dd
        tmin, tmax = ((p1 - c) @ dd), ((p2 - c) @ dd)
        p1 = c + tmin * dd
        p2 = c + tmax * dd
        sig = r.std(ddof=2) if len(r) > 3 else 1.0
        St = ((t - t.mean()) ** 2).sum()
        info = dict(n_samples=int(len(pts)), n_used=int(keep.sum()),
                    resid_px=float(sig),
                    slope_sigma_deg=float(math.degrees(sig / math.sqrt(St))) if St > 0 else 90.0,
                    coverage=float(ok.mean()))
    return p1, p2, info


def az(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(dx, -dy)) % 360.0


def fold(b):
    return ((b + 45.0) % 90.0) - 45.0


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    ov = sys.argv[3] if len(sys.argv) > 3 else None
    im, a = load(spec)
    sha = hashlib.sha256(open(spec["image"], "rb").read()).hexdigest()
    cache = {}

    def m_for(e):
        key = (e.get("mode", "dark"), tuple(e.get("rgb", []) or []), e.get("tol", 60.0), e.get("thr"),
               e.get("blur", 0))
        if key not in cache:
            m = ink_map(a, key[0], e.get("rgb"), e.get("tol", 60.0), e.get("thr"))
            if e.get("blur", 0):
                import cv2
                m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), float(e["blur"]))
            cache[key] = m
        return cache[key]

    def do(e):
        if e.get("fit", True) is False:
            return np.array(e["p1"], float), np.array(e["p2"], float), {"fit": False}
        r = refine(m_for(e), e["p1"], e["p2"], e.get("w", 4), e.get("step", 2.0),
                   e.get("margin", 0.06), side=e.get("side", 0), wsched=e.get("wsched"))
        if r is None:
            raise RuntimeError("fit failed for %s" % e.get("id"))
        return r

    res = {"spec": sys.argv[1], "image": spec["image"], "image_sha256": sha,
           "image_size": [im.width, im.height]}
    N = spec["north"]
    q1, q2, ninfo = do(N)
    north_az = az(q1, q2)
    nlen = float(np.linalg.norm(q2 - q1))
    ep = spec.get("endpoint_px", 1.0)
    north_sig = math.hypot(ninfo.get("slope_sigma_deg", 0.0),
                           math.degrees(math.sqrt(2) * N.get("endpoint_px", ep) / nlen))
    north_sig = math.hypot(north_sig, N.get("drawn_sigma_deg", 0.0))
    res["north"] = {"p1": q1.round(2).tolist(), "p2": q2.round(2).tolist(),
                    "azimuth_img_deg": round(north_az, 3), "length_px": round(nlen, 1),
                    "sigma_deg": round(north_sig, 3), "fit": ninfo,
                    "note": N.get("note", "")}
    mpp = None
    if "scale" in spec:
        S = spec["scale"]
        s1, s2 = np.array(S["p1"], float), np.array(S["p2"], float)
        mpp = S["metres"] / float(np.linalg.norm(s2 - s1))
        res["scale"] = {"p1": S["p1"], "p2": S["p2"], "metres": S["metres"],
                        "m_per_px": round(mpp, 5), "note": S.get("note", "")}
    render_sig = spec.get("render_sigma_deg", 0.0)
    res["frame"] = []
    for F in spec.get("frame", []):
        f1, f2, finfo = do(F)
        res["frame"].append({"id": F.get("id"), "azimuth_img_deg": round(az(f1, f2) % 180.0, 3),
                             "relative_to_north_deg": round((az(f1, f2) - north_az) % 180.0, 3),
                             "length_px": round(float(np.linalg.norm(f2 - f1)), 1), "fit": finfo,
                             "p1": f1.round(2).tolist(), "p2": f2.round(2).tolist()})
    res["render_sigma_deg"] = render_sig
    res["lines"] = []
    for e in spec["lines"]:
        try:
            l1, l2, info = do(e)
        except RuntimeError as err:
            print("SKIPPED", e.get("id"), err)
            continue
        L = float(np.linalg.norm(l2 - l1))
        laz = az(l1, l2) % 180.0
        b = (laz - north_az) % 180.0
        epf = math.degrees(math.sqrt(2) * e.get("endpoint_px", ep) / L)
        sig = math.sqrt(info.get("slope_sigma_deg", 0.0) ** 2 + epf ** 2 + north_sig ** 2
                        + render_sig ** 2 + e.get("extra_sigma_deg", 0.0) ** 2)
        rec = {k: e[k] for k in ("id", "part", "kind", "description", "phase", "confidence") if k in e}
        rec.update({"p1_px": l1.round(2).tolist(), "p2_px": l2.round(2).tolist(),
                    "length_px": round(L, 1),
                    "length_m": round(L * mpp, 1) if mpp else None,
                    "azimuth_img_deg": round(laz, 3), "bearing_deg": round(b, 2),
                    "deviation_deg": round(fold(b), 2), "sigma_deg": round(sig, 2),
                    "fit": info})
        res["lines"].append(rec)
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    if ov:
        o = im.copy()
        dr = ImageDraw.Draw(o)
        dr.line([tuple(q1), tuple(q2)], fill=(0, 200, 0), width=max(3, im.width // 1200))
        for f in res["frame"]:
            dr.line([tuple(f["p1"]), tuple(f["p2"])], fill=(0, 120, 255), width=2)
        for r in res["lines"]:
            dr.line([tuple(r["p1_px"]), tuple(r["p2_px"])], fill=(255, 0, 255), width=max(2, im.width // 1500))
            mx = (r["p1_px"][0] + r["p2_px"][0]) / 2
            my = (r["p1_px"][1] + r["p2_px"][1]) / 2
            dr.text((mx + 3, my + 3), r["id"], fill=(200, 0, 120))
        o.save(ov)
    for r in res["lines"]:
        print(r["id"], r["length_px"], r["length_m"], r["bearing_deg"], r["deviation_deg"],
              r["sigma_deg"], r["fit"].get("resid_px"), r["fit"].get("n_used"), r["fit"].get("coverage"))
    print("north", res["north"]["azimuth_img_deg"], res["north"]["sigma_deg"], res["north"]["fit"])
    for f in res["frame"]:
        print("frame", f["id"], f["azimuth_img_deg"], f["fit"].get("resid_px"))


if __name__ == "__main__":
    main()
