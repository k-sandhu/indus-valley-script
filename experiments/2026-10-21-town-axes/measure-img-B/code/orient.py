"""Dominant line orientation inside polygons from image gradients (role img-B).

Conventions. Mosaic pixel coordinates have x east and y south. The gradient
vector (gx, gy) has azimuth atan2(gx, -gy) clockwise from north. An edge runs
at right angles to its gradient, so modulo 90 degrees the edge bearing equals
the gradient azimuth. We fold every gradient azimuth to a deviation in
[-45, +45), positive clockwise, build a magnitude-weighted circular histogram,
smooth it, and take the peak with parabolic sub-bin interpolation.
"""
from __future__ import annotations

import math

import cv2
import numpy as np
from scipy import ndimage

BIN = 0.25          # histogram bin width, degrees
SMOOTH = 1.0        # Gaussian smoothing of the folded histogram, degrees (sigma)
GRAD_SIGMA = 1.0    # derivative-of-Gaussian scale, pixels


def luminance(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def gradients(gray: np.ndarray, sigma: float = GRAD_SIGMA):
    g = gray.astype(np.float64)
    gx = ndimage.gaussian_filter(g, sigma, order=(0, 1))
    gy = ndimage.gaussian_filter(g, sigma, order=(1, 0))
    mag = np.hypot(gx, gy)
    dev = np.degrees(np.arctan2(gx, -gy))
    dev = (dev + 45.0) % 90.0 - 45.0
    bear180 = (np.degrees(np.arctan2(gx, -gy)) + 90.0) % 180.0  # edge bearing 0..180
    return mag, dev, bear180


def poly_mask(shape, polys, holes=()) -> np.ndarray:
    m = np.zeros(shape, np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.round(np.asarray(p, float)).astype(np.int32)], 1)
    for h in holes:
        cv2.fillPoly(m, [np.round(np.asarray(h, float)).astype(np.int32)], 0)
    return m.astype(bool)


def hist_folded(dev, w, bin_w=BIN):
    nb = int(round(90 / bin_w))
    idx = np.floor((dev + 45.0) / bin_w).astype(int) % nb
    return np.bincount(idx.ravel(), weights=w.ravel(), minlength=nb)


def smooth_circ(h, sigma_deg=SMOOTH, bin_w=BIN):
    s = sigma_deg / bin_w
    return ndimage.gaussian_filter1d(h, s, mode="wrap")


def peak_of(hs, bin_w=BIN, lo=-45.0):
    nb = len(hs)
    i = int(np.argmax(hs))
    a, b, c = hs[(i - 1) % nb], hs[i], hs[(i + 1) % nb]
    den = a - 2 * b + c
    off = 0.5 * (a - c) / den if den != 0 else 0.0
    return float(lo + (i + 0.5 + off) * bin_w)


def wrap90(d):
    return (d + 45.0) % 90.0 - 45.0


def local_peaks(hs, bin_w=BIN, min_rel=0.1, min_sep=3.0):
    """Local maxima of a circular histogram with height above floor >= min_rel of the main peak."""
    nb = len(hs)
    floor = float(np.min(hs))
    top = float(np.max(hs)) - floor
    out = []
    for i in range(nb):
        if hs[i] >= hs[(i - 1) % nb] and hs[i] > hs[(i + 1) % nb]:
            rel = (hs[i] - floor) / top if top > 0 else 0
            if rel >= min_rel:
                a, b, c = hs[(i - 1) % nb], hs[i], hs[(i + 1) % nb]
                den = a - 2 * b + c
                off = 0.5 * (a - c) / den if den != 0 else 0.0
                out.append({"deviation_deg": round(float(-45 + (i + 0.5 + off) * bin_w), 2), "rel_height": round(float(rel), 3)})
    out.sort(key=lambda r: -r["rel_height"])
    kept = []
    for r in out:
        if all(abs(wrap90(r["deviation_deg"] - k["deviation_deg"])) >= min_sep for k in kept):
            kept.append(r)
    return kept


def peak_contrast(hs):
    """Main peak height above floor, relative to floor (a signal-to-background figure)."""
    floor = float(np.min(hs))
    return (float(np.max(hs)) - floor) / floor if floor > 0 else float("inf")


def crop_to(rgb, polys, holes=(), margin=24):
    allp = np.concatenate([np.asarray(p, float) for p in polys])
    x0, y0 = np.maximum(np.floor(allp.min(0)).astype(int) - margin, 0)
    x1 = min(int(np.ceil(allp[:, 0].max())) + margin, rgb.shape[1])
    y1 = min(int(np.ceil(allp[:, 1].max())) + margin, rgb.shape[0])
    sh = np.array([x0, y0], float)
    return (rgb[y0:y1, x0:x1], [np.asarray(p, float) - sh for p in polys],
            [np.asarray(h, float) - sh for h in holes])


def analyse(rgb, polys, holes=(), m_per_px=0.5, block_m=30.0, n_boot=1000, thresh_pct=60.0,
            sigma=GRAD_SIGMA, seed=12345, crop=True):
    if crop:
        rgb, polys, holes = crop_to(rgb, polys, holes)
    gray = luminance(rgb.astype(np.float64))
    mag, dev, bear = gradients(gray, sigma)
    mask = poly_mask(gray.shape, polys, holes)
    if mask.sum() < 100:
        raise ValueError("polygon too small")
    thr = np.percentile(mag[mask], thresh_pct)
    use = mask & (mag > thr)
    w = np.where(use, mag, 0.0)
    h = hist_folded(dev[use], w[use])
    hs = smooth_circ(h)
    pk = peak_of(hs)
    peaks = local_peaks(hs)
    # 4-fold vector mean within +-10 deg of the peak
    near = use & (np.abs(wrap90(dev - pk)) < 10)
    z = np.sum(w[near] * np.exp(1j * np.radians(4 * dev[near])))
    vmean = math.degrees(np.angle(z)) / 4
    # unfolded edge-bearing histogram (0..180) to show both perpendicular families
    nb180 = int(180 / 1.0)
    h180 = np.bincount(np.floor(bear[use]).astype(int) % nb180, weights=w[use], minlength=nb180)
    h180s = ndimage.gaussian_filter1d(h180, 1.5, mode="wrap")
    fam = {}
    for name, c in (("near_north", 0.0 + pk), ("near_east", 90.0 + pk)):
        cc = c % 180
        idx = (np.arange(nb180) + 0.5)
        sel = np.abs(((idx - cc + 90) % 180) - 90) <= 5
        fam[name] = float(h180[sel].sum())
    tot = fam["near_north"] + fam["near_east"]
    fam_share = {k: round(v / tot, 3) for k, v in fam.items()} if tot else fam
    # block bootstrap
    bpx = max(8, int(round(block_m / m_per_px)))
    ys, xs = np.nonzero(use)
    bid = (ys // bpx) * 100000 + (xs // bpx)
    uniq, inv = np.unique(bid, return_inverse=True)
    nbins = len(h)
    idxbin = (np.floor((dev[ys, xs] + 45.0) / BIN).astype(int)) % nbins
    H = np.zeros((len(uniq), nbins))
    np.add.at(H, (inv, idxbin), w[ys, xs])
    rng = np.random.default_rng(seed)
    nblk = len(uniq)
    boots = []
    for _ in range(n_boot):
        s = rng.integers(0, nblk, nblk)
        hb = smooth_circ(H[s].sum(0))
        boots.append(peak_of(hb))
    boots = np.array(boots)
    bdev = wrap90(boots - pk)
    se = float(np.std(bdev))
    # per-block peaks: dispersion of local directions (blocks with a clear peak)
    blk = []
    cnt = np.bincount(inv, minlength=nblk)
    for k in range(nblk):
        hk = smooth_circ(H[k], 1.5)
        if H[k].sum() <= 0 or cnt[k] < 0.1 * bpx * bpx:
            continue
        if peak_contrast(hk) > 0.6:
            blk.append(wrap90(peak_of(hk) - pk))
    blk = np.array(blk)
    # subarea split: halves along x and y of the mask's bounding box
    halves = {}
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    for name, sel in (("west", xs < (x0 + x1) / 2), ("east", xs >= (x0 + x1) / 2),
                      ("north", ys < (y0 + y1) / 2), ("south", ys >= (y0 + y1) / 2)):
        if sel.sum() > 500:
            hh = smooth_circ(np.bincount(idxbin[sel], weights=w[ys[sel], xs[sel]], minlength=nbins))
            halves[name] = round(float(peak_of(hh)), 2)
    pk = float(pk)
    return {
        "peak_deviation_deg": round(pk, 3),
        "vector_mean_deviation_deg": round(vmean, 3),
        "bootstrap_se_deg": round(se, 3),
        "bootstrap_ci95_deg": [round(pk + float(np.percentile(bdev, 2.5)), 2), round(pk + float(np.percentile(bdev, 97.5)), 2)],
        "n_blocks": int(nblk), "block_m": block_m,
        "block_peak_sd_deg": round(float(np.std(blk)), 2) if len(blk) > 2 else None,
        "n_blocks_with_clear_peak": int(len(blk)),
        "peak_contrast": round(peak_contrast(hs), 3),
        "secondary_peaks": peaks[1:6],
        "all_peaks": peaks[:6],
        "family_share": fam_share,
        "halves": halves,
        "mask_area_m2": round(float(mask.sum()) * m_per_px ** 2, 1),
        "used_pixels": int(use.sum()),
        "grad_sigma_px": sigma, "threshold_percentile": thresh_pct,
        "_hist": hs.tolist(),
    }


def rotation_test(rgb, polys, holes=(), angle=17.0, **kw):
    """Rotate the image content by +angle (clockwise on the ground) and re-measure.

    A pixel-grid bias in the operator would not follow the rotation; the true
    direction moves by exactly +angle.
    """
    rgb, polys, holes = crop_to(rgb, polys, holes, margin=80)
    H, W = rgb.shape[:2]
    c = (W / 2, H / 2)
    # cv2 positive angle = counter-clockwise in image; we want clockwise => -angle
    M = cv2.getRotationMatrix2D(c, -angle, 1.0)
    rot = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

    def tr(p):
        p = np.asarray(p, float)
        return (np.c_[p, np.ones(len(p))] @ M.T)
    rp = [tr(p) for p in polys]
    rh = [tr(p) for p in holes]
    r = analyse(rot, rp, rh, n_boot=50, crop=False, **kw)
    return round(wrap90(r["peak_deviation_deg"] - angle), 3)


def line_bearing(x0, y0, x1, y1):
    """Bearing 0..180 and deviation of a line from global pixel endpoints."""
    b = math.degrees(math.atan2(x1 - x0, -(y1 - y0))) % 180.0
    d = wrap90(b)
    return b, d


def refine_line(gray, p0, p1, search=4, step=3.0, sigma=1.0):
    """Refine a hand-picked edge: along the line, find the strongest gradient
    across it within +-search px, then fit a straight line (total least squares)."""
    g = ndimage.gaussian_filter(gray.astype(np.float64), sigma)
    gx = ndimage.sobel(g, axis=1)
    gy = ndimage.sobel(g, axis=0)
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    L = np.linalg.norm(p1 - p0)
    t = (p1 - p0) / L
    n = np.array([-t[1], t[0]])
    pts = []
    for s in np.arange(0, L + 1e-9, step):
        c = p0 + s * t
        offs = np.arange(-search, search + 0.01, 0.25)
        q = c[None, :] + offs[:, None] * n[None, :]
        vx = ndimage.map_coordinates(gx, [q[:, 1], q[:, 0]], order=1)
        vy = ndimage.map_coordinates(gy, [q[:, 1], q[:, 0]], order=1)
        proj = np.abs(vx * n[0] + vy * n[1])
        k = int(np.argmax(proj))
        if proj[k] > 0 and 0 < k < len(offs) - 1:
            pts.append((q[k], proj[k]))
    if len(pts) < 5:
        return None
    P = np.array([p for p, _ in pts])
    Wt = np.array([v for _, v in pts])
    keep = Wt > np.percentile(Wt, 25)
    P = P[keep]
    c = P.mean(0)
    U, S, Vt = np.linalg.svd(P - c)
    d = Vt[0]
    if np.dot(d, t) < 0:
        d = -d
    res = (P - c) @ Vt[1]
    s_proj = (P - c) @ d
    span = s_proj.max() - s_proj.min()
    rms = float(np.sqrt(np.mean(res ** 2)))
    # slope standard error for a line fit: rms / sqrt(sum (s - mean)^2)
    se_rad = rms / math.sqrt(np.sum((s_proj - s_proj.mean()) ** 2))
    a = c + d * s_proj.min()
    b = c + d * s_proj.max()
    return {"p0": a.tolist(), "p1": b.tolist(), "n_pts": int(len(P)), "rms_px": round(rms, 3),
            "span_px": round(float(span), 1), "slope_se_deg": round(math.degrees(se_rad), 3)}


def jpeg_pull_test(rgb, polys, holes=(), angles=(-5.0, -2.0, 2.0, 5.0), quality=75, **kw):
    """Rotate the content by a small angle, re-encode as JPEG with axis-aligned
    8x8 blocks, and re-measure. If compression or the pixel grid pulled peaks
    towards the cardinal directions, the recovered rotation would fall short of
    the applied one. Returns the shortfall (recovered minus expected) per angle."""
    import io
    from PIL import Image as _I
    rgb, polys, holes = crop_to(rgb, polys, holes, margin=80)
    base = analyse(rgb, polys, holes, n_boot=1, crop=False, **kw)["peak_deviation_deg"]
    H, W = rgb.shape[:2]
    c = (W / 2, H / 2)
    out = {}
    for a in angles:
        M = cv2.getRotationMatrix2D(c, -a, 1.0)
        rot = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        buf = io.BytesIO()
        _I.fromarray(rot).save(buf, format="JPEG", quality=quality)
        rj = np.asarray(_I.open(io.BytesIO(buf.getvalue())).convert("RGB"))

        def tr(p):
            p = np.asarray(p, float)
            return np.c_[p, np.ones(len(p))] @ M.T
        r = analyse(rj, [tr(p) for p in polys], [tr(h) for h in holes], n_boot=1, crop=False, **kw)
        out[str(a)] = round(float(wrap90(r["peak_deviation_deg"] - base - a)), 3)
    return out
