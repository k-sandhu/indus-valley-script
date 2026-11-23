"""Build georeferenced four-layer archaeological footprints and survey windows
for Harappa, Lakhanjo-Daro (Sukkur) and Rupnagar (Ropar).

Implements the frozen rules of PROTOCOL.md:
- WGS 84 UTM metric registration (EPSG:32643 for Harappa and Rupnagar;
  EPSG:32642 for Lakhanjo-Daro) with weighted least-squares similarity fits.
- Four explicit GeoJSON layers per site:
    1. layer_1_published_archaeology
    2. layer_2_modern_footprint
    3. layer_3_concealed_overlap
    4. layer_4_survey_windows
- Deterministic priority scoring (0-100) and explicit demotion rules (D1-D6)
  from ESA WorldCover 2021 v200 (10 m), Copernicus GLO-30 (30 m) and Layer 1
  Harappan proximity.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parents[1]
RAW_NEW = ROOT / "data" / "raw" / "2026-11-23-living-towns-footprints"
FIG_DIR = EXP_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# WGS84 ellipsoid constants
WGS84_A = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = 2.0 * WGS84_F - WGS84_F * WGS84_F
WGS84_EP2 = WGS84_E2 / (1.0 - WGS84_E2)
R_SPHERE_AUTHALIC = 6371007.1809
MERC_R = 6378137.0
MERC_CIRC = 2.0 * math.pi * MERC_R


class TMProjection:
    """Exact WGS84 Transverse Mercator projection (Snyder / USGS)."""

    def __init__(self, lon0_deg: float, k0: float = 0.9996, false_easting: float = 500000.0):
        self.lon0_deg = float(lon0_deg)
        self.lon0_rad = math.radians(lon0_deg)
        self.k0 = float(k0)
        self.fe = float(false_easting)

    def forward(self, lon_deg, lat_deg):
        lon = np.radians(np.asarray(lon_deg, dtype=np.float64))
        lat = np.radians(np.asarray(lat_deg, dtype=np.float64))
        e2, ep2, a = WGS84_E2, WGS84_EP2, WGS84_A
        sin_lat, cos_lat, tan_lat = np.sin(lat), np.cos(lat), np.tan(lat)
        N = a / np.sqrt(1.0 - e2 * sin_lat * sin_lat)
        T = tan_lat * tan_lat
        C = ep2 * cos_lat * cos_lat
        A = cos_lat * (lon - self.lon0_rad)
        e4, e6 = e2 * e2, e2 * e2 * e2
        M = a * (
            (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0) * lat
            - (3.0 * e2 / 8.0 + 3.0 * e4 / 32.0 + 45.0 * e6 / 1024.0) * np.sin(2.0 * lat)
            + (15.0 * e4 / 256.0 + 45.0 * e6 / 1024.0) * np.sin(4.0 * lat)
            - (35.0 * e6 / 3072.0) * np.sin(6.0 * lat)
        )
        A2 = A * A
        A3, A4, A5, A6 = A2 * A, A2 * A2, A2 * A2 * A, A2 * A2 * A2
        easting = self.fe + self.k0 * N * (
            A + (1.0 - T + C) * A3 / 6.0 + (5.0 - 18.0 * T + T * T + 72.0 * C - 58.0 * ep2) * A5 / 120.0
        )
        northing = self.k0 * (
            M
            + N
            * tan_lat
            * (
                A2 / 2.0
                + (5.0 - T + 9.0 * C + 4.0 * C * C) * A4 / 24.0
                + (61.0 - 58.0 * T + T * T + 600.0 * C - 330.0 * ep2) * A6 / 720.0
            )
        )
        return easting, northing

    def inverse(self, easting_m, northing_m):
        x = np.asarray(easting_m, dtype=np.float64) - self.fe
        y = np.asarray(northing_m, dtype=np.float64)
        e2, ep2, a = WGS84_E2, WGS84_EP2, WGS84_A
        e4, e6 = e2 * e2, e2 * e2 * e2
        e1 = (1.0 - math.sqrt(1.0 - e2)) / (1.0 + math.sqrt(1.0 - e2))
        M = y / self.k0
        mu = M / (a * (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0))
        phi1 = (
            mu
            + (3.0 * e1 / 2.0 - 27.0 * (e1 ** 3) / 32.0) * np.sin(2.0 * mu)
            + (21.0 * (e1 ** 2) / 16.0 - 55.0 * (e1 ** 4) / 32.0) * np.sin(4.0 * mu)
            + (151.0 * (e1 ** 3) / 96.0) * np.sin(6.0 * mu)
            + (1097.0 * (e1 ** 4) / 512.0) * np.sin(8.0 * mu)
        )
        sin_p, cos_p, tan_p = np.sin(phi1), np.cos(phi1), np.tan(phi1)
        C1, T1 = ep2 * cos_p * cos_p, tan_p * tan_p
        N1 = a / np.sqrt(1.0 - e2 * sin_p * sin_p)
        R1 = a * (1.0 - e2) / np.power(1.0 - e2 * sin_p * sin_p, 1.5)
        D = x / (N1 * self.k0)
        D2 = D * D
        D3, D4, D5, D6 = D2 * D, D2 * D2, D2 * D2 * D, D2 * D2 * D2
        lat = phi1 - (N1 * tan_p / R1) * (
            D2 / 2.0
            - (5.0 + 3.0 * T1 + 10.0 * C1 - 4.0 * C1 * C1 - 9.0 * ep2) * D4 / 24.0
            + (61.0 + 90.0 * T1 + 298.0 * C1 + 45.0 * T1 * T1 - 252.0 * ep2 - 3.0 * C1 * C1) * D6 / 720.0
        )
        lon = self.lon0_rad + (
            D
            - (1.0 + 2.0 * T1 + C1) * D3 / 6.0
            + (5.0 - 2.0 * C1 + 28.0 * T1 - 3.0 * C1 * C1 + 8.0 * ep2 + 24.0 * T1 * T1) * D5 / 120.0
        ) / cos_p
        return np.degrees(lon), np.degrees(lat)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mosaic_px_to_lonlat(mx: float, my: float, meta: dict) -> tuple[float, float]:
    if "origin_global_px" in meta:
        x0, y0 = meta["origin_global_px"]
        z = meta["zoom"]
    else:
        x0, y0 = meta["global_px_x0"], meta["global_px_y0"]
        z = meta["z"]
    n = 256.0 * (2 ** z)
    E = ((x0 + mx) / n - 0.5) * MERC_CIRC
    N = (0.5 - (y0 + my) / n) * MERC_CIRC
    lon = math.degrees(E / MERC_R)
    lat = math.degrees(math.atan(math.sinh(N / MERC_R)))
    return lon, lat


def lonlat_to_mosaic_px(lon: float, lat: float, meta: dict) -> tuple[float, float]:
    if "origin_global_px" in meta:
        x0, y0 = meta["origin_global_px"]
        z = meta["zoom"]
    else:
        x0, y0 = meta["global_px_x0"], meta["global_px_y0"]
        z = meta["z"]
    n = 256.0 * (2 ** z)
    E = math.radians(lon) * MERC_R
    N = MERC_R * math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))
    return (E / MERC_CIRC + 0.5) * n - x0, (0.5 - N / MERC_CIRC) * n - y0


def signed_area_xy(ring_xy: list[tuple[float, float]]) -> float:
    """Shoelace signed area (positive for CCW rings)."""
    pts = ring_xy if ring_xy[0] == ring_xy[-1] else ring_xy + [ring_xy[0]]
    s = 0.0
    for i in range(len(pts) - 1):
        s += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return 0.5 * s


def ensure_ccw_closed(ring_xy: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = list(ring_xy)
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    if signed_area_xy(pts) < 0.0:
        pts = list(reversed(pts))
    return pts


def utm_ring_to_lonlat(ring_xy: list[tuple[float, float]], proj: TMProjection) -> list[list[float]]:
    ccw = ensure_ccw_closed(ring_xy)
    xs = np.array([p[0] for p in ccw], dtype=np.float64)
    ys = np.array([p[1] for p in ccw], dtype=np.float64)
    lons, lats = proj.inverse(xs, ys)
    coords = [[round(float(lo), 7), round(float(la), 7)] for lo, la in zip(lons, lats)]
    coords[-1] = coords[0]
    return coords


def lonlat_ring_to_utm(ring_ll: list[list[float]], proj: TMProjection) -> list[tuple[float, float]]:
    lons = np.array([p[0] for p in ring_ll], dtype=np.float64)
    lats = np.array([p[1] for p in ring_ll], dtype=np.float64)
    es, ns = proj.forward(lons, lats)
    return [(float(e), float(n)) for e, n in zip(es, ns)]


def fit_similarity_wls(
    plan_xy: list[tuple[float, float]],
    target_en: list[tuple[float, float]],
    sigmas_m: list[float],
    expected_scale_m_per_px: float | None = None,
) -> dict:
    """4-parameter similarity fit Q = [[a,-b],[b,a]] P + t in right-handed (x, -y) frame."""
    P = np.array([[p[0], -p[1]] for p in plan_xy], dtype=np.float64)
    Q = np.array(target_en, dtype=np.float64)
    sig = np.array(sigmas_m, dtype=np.float64)
    w = 1.0 / (sig ** 2)
    N = len(P)

    def _solve(p_arr, q_arr, w_arr):
        n = len(p_arr)
        A = np.zeros((2 * n, 4), dtype=np.float64)
        y = np.zeros(2 * n, dtype=np.float64)
        A[0::2, 0] = p_arr[:, 0]
        A[0::2, 1] = -p_arr[:, 1]
        A[0::2, 2] = 1.0
        A[1::2, 0] = p_arr[:, 1]
        A[1::2, 1] = p_arr[:, 0]
        A[1::2, 3] = 1.0
        y[0::2] = q_arr[:, 0]
        y[1::2] = q_arr[:, 1]
        W = np.repeat(w_arr, 2)
        cov = np.linalg.inv((A.T * W) @ A)
        params = cov @ ((A.T * W) @ y)
        res = (y - A @ params).reshape(n, 2)
        return params, cov, res

    params, cov, res = _solve(P, Q, w)
    dists = np.hypot(res[:, 0], res[:, 1])
    rmse_m = float(np.sqrt(np.mean(dists ** 2)))
    chi2 = float(np.sum((dists ** 2) * w))
    dof = 2 * N - 4
    s = math.hypot(params[0], params[1])
    phi_deg = math.degrees(math.atan2(params[1], params[0]))

    # Leave-one-out errors
    loo_m = []
    for i in range(N):
        mask = np.arange(N) != i
        pk, _, _ = _solve(P[mask], Q[mask], w[mask])
        pe = pk[0] * P[i, 0] - pk[1] * P[i, 1] + pk[2]
        pn = pk[1] * P[i, 0] + pk[0] * P[i, 1] + pk[3]
        loo_m.append(float(math.hypot(Q[i, 0] - pe, Q[i, 1] - pn)))

    # Mirror check
    Pm = P.copy()
    Pm[:, 1] = -Pm[:, 1]
    _, _, res_m = _solve(Pm, Q, w)
    chi2_mirror = float(np.sum((res_m ** 2).sum(axis=1) * w))

    sv = np.linalg.svd(Q - Q.mean(axis=0), compute_uv=False)
    sv_ratio = float(sv[1] / sv[0]) if sv[0] > 0 else 0.0

    scale_ratio = float(s / expected_scale_m_per_px) if expected_scale_m_per_px else None
    return {
        "n_points": N,
        "dof": dof,
        "params": [float(x) for x in params],
        "scale_m_per_px": float(s),
        "expected_scale_m_per_px": expected_scale_m_per_px,
        "scale_ratio": scale_ratio,
        "rotation_ccw_deg": float(phi_deg),
        "rmse_m": rmse_m,
        "max_residual_m": float(dists.max()),
        "loo_max_m": float(max(loo_m)),
        "loo_errors_m": [round(x, 3) for x in loo_m],
        "residuals_m": [round(float(x), 3) for x in dists],
        "chi2": chi2,
        "chi2_per_dof": chi2 / dof if dof > 0 else float("nan"),
        "chi2_mirror": chi2_mirror,
        "singular_value_ratio": sv_ratio,
    }


def apply_similarity(plan_x: float, plan_y: float, params: list[float]) -> tuple[float, float]:
    a, b, tx, ty = params
    px, py = float(plan_x), -float(plan_y)
    return a * px - b * py + tx, b * px + a * py + ty


def load_worldcover_tif(path: Path) -> dict:
    with Image.open(path) as im:
        arr = np.array(im, dtype=np.uint8)
        scale = im.tag_v2[33550]
        tie = im.tag_v2[33922]
    return {
        "arr": arr,
        "sx": float(scale[0]),
        "sy": float(scale[1]),
        "lon0": float(tie[3]),
        "lat0": float(tie[4]),
    }


def load_dem_tile(path: Path, lat_floor: int, lon_floor: int) -> dict:
    with Image.open(path) as im:
        arr = np.array(im, dtype=np.float32)
    return {
        "arr": arr,
        "lat_top": float(lat_floor + 1),
        "lon_left": float(lon_floor),
    }


def sample_worldcover_on_utm_grid(wc: dict, e_grid: np.ndarray, n_grid: np.ndarray, proj: TMProjection) -> np.ndarray:
    lon, lat = proj.inverse(e_grid, n_grid)
    col = np.floor((lon - wc["lon0"]) / wc["sx"]).astype(np.int32)
    row = np.floor((wc["lat0"] - lat) / wc["sy"]).astype(np.int32)
    h, w = wc["arr"].shape
    valid = (row >= 0) & (row < h) & (col >= 0) & (col < w)
    out = np.zeros(e_grid.shape, dtype=np.uint8)
    out[valid] = wc["arr"][row[valid], col[valid]]
    return out


def sample_dem_on_utm_grid(dem: dict, e_grid: np.ndarray, n_grid: np.ndarray, proj: TMProjection) -> np.ndarray:
    lon, lat = proj.inverse(e_grid, n_grid)
    f_col = (lon - dem["lon_left"]) * 3600.0
    f_row = (dem["lat_top"] - lat) * 3600.0
    h, w = dem["arr"].shape
    valid = (f_row >= 0.0) & (f_row <= h - 1.001) & (f_col >= 0.0) & (f_col <= w - 1.001)
    out = np.full(e_grid.shape, np.nan, dtype=np.float32)
    if np.any(valid):
        rf, cf = f_row[valid], f_col[valid]
        ri, ci = np.floor(rf).astype(np.int32), np.floor(cf).astype(np.int32)
        dr, dc = (rf - ri).astype(np.float32), (cf - ci).astype(np.float32)
        a = dem["arr"]
        out[valid] = (
            a[ri, ci] * (1.0 - dr) * (1.0 - dc)
            + a[ri, ci + 1] * (1.0 - dr) * dc
            + a[ri + 1, ci] * dr * (1.0 - dc)
            + a[ri + 1, ci + 1] * dr * dc
        )
    return out


def compute_local_plain_baseline(dem: dict, center_e: float, center_n: float, proj: TMProjection) -> float:
    """15th percentile elevation in a 1.5 km radius annulus (300 m to 1500 m)."""
    step = 30.0
    xs = np.arange(center_e - 1500.0, center_e + 1501.0, step)
    ys = np.arange(center_n - 1500.0, center_n + 1501.0, step)
    ee, nn = np.meshgrid(xs, ys)
    r = np.hypot(ee - center_e, nn - center_n)
    ann = (r >= 300.0) & (r <= 1500.0)
    z = sample_dem_on_utm_grid(dem, ee[ann], nn[ann], proj)
    z = z[np.isfinite(z)]
    return float(np.percentile(z, 15))


def rasterize_polygon_utm(ring_xy: list[tuple[float, float]], e0: float, n1: float, res_m: float, shape_hw: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape_hw, dtype=np.uint8)
    pts = np.array(
        [[int(round((x - e0) / res_m - 0.5)), int(round((n1 - y) / res_m - 0.5))] for x, y in ring_xy],
        dtype=np.int32,
    )
    cv2.fillPoly(mask, [pts], 1)
    return mask.astype(bool)


def _segments_intersect(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return ((o1 > 1e-12 and o2 < -1e-12) or (o1 < -1e-12 and o2 > 1e-12)) and (
        (o3 > 1e-12 and o4 < -1e-12) or (o3 < -1e-12 and o4 > 1e-12)
    )


def _ring_self_intersects(ring_xy: list[tuple[float, float]]) -> bool:
    pts = ring_xy[:-1] if ring_xy[0] == ring_xy[-1] else ring_xy
    n = len(pts)
    if n <= 3:
        return False
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if _segments_intersect(a, b, pts[j], pts[(j + 1) % n]):
                return True
    return False


def vectorize_mask_utm(
    mask: np.ndarray,
    e0: float,
    n1: float,
    res_m: float,
    min_area_m2: float = 200.0,
    eps_px: float = 1.5,
) -> list[list[tuple[float, float]]]:
    """Extract clean, strictly simple exterior polygons (UTM rings) from a boolean raster mask."""
    # Remove single-pixel diagonal bridges that can create contour pinches
    clean = ndi.binary_opening(mask, structure=np.ones((2, 2), dtype=bool))
    u8 = (clean.astype(np.uint8) * 255)
    contours, _ = cv2.findContours(u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rings = []
    for cnt in contours:
        if len(cnt) < 3:
            continue
        chosen = None
        for eps in (eps_px, eps_px * 0.5, 0.25, 0.0):
            approx = cv2.approxPolyDP(cnt, epsilon=eps, closed=True) if eps > 0.0 else cnt
            if len(approx) < 3:
                continue
            ring = [
                (e0 + (float(pt[0]) + 0.5) * res_m, n1 - (float(pt[1]) + 0.5) * res_m)
                for pt in approx[:, 0, :]
            ]
            ring = ensure_ccw_closed(ring)
            if not _ring_self_intersects(ring):
                chosen = ring
                break
        if chosen is None:
            continue
        area = abs(signed_area_xy(chosen))
        if area >= min_area_m2:
            rings.append(chosen)
    return rings


def polyline_to_corridor_polygon(pts_xy: list[tuple[float, float]], half_width_m: float) -> tuple[list[tuple[float, float]], float]:
    """Create a clean non-self-intersecting ribbon polygon along a polyline."""
    arr = np.asarray(pts_xy, dtype=np.float64)
    seg_lens = np.hypot(np.diff(arr[:, 0]), np.diff(arr[:, 1]))
    total_len = float(seg_lens.sum())
    n = len(arr)
    left_pts, right_pts = [], []
    for i in range(n):
        if i == 0:
            v = arr[1] - arr[0]
        elif i == n - 1:
            v = arr[-1] - arr[-2]
        else:
            v1 = arr[i] - arr[i - 1]
            v2 = arr[i + 1] - arr[i]
            v1 = v1 / (np.linalg.norm(v1) + 1e-12)
            v2 = v2 / (np.linalg.norm(v2) + 1e-12)
            v = v1 + v2
            if np.linalg.norm(v) < 1e-6:
                v = v1
        v = v / (np.linalg.norm(v) + 1e-12)
        normal = np.array([-v[1], v[0]])
        left_pts.append((float(arr[i, 0] + half_width_m * normal[0]), float(arr[i, 1] + half_width_m * normal[1])))
        right_pts.append((float(arr[i, 0] - half_width_m * normal[0]), float(arr[i, 1] - half_width_m * normal[1])))
    ring = left_pts + list(reversed(right_pts))
    return ensure_ccw_closed(ring), total_len


def score_and_classify_window(
    win_spec: dict,
    ring_xy: list[tuple[float, float]],
    e0: float,
    n1: float,
    res_m: float,
    wc_grid: np.ndarray,
    dem_grid: np.ndarray,
    z_base: float,
    harappan_dist_m: np.ndarray,
) -> dict:
    """Compute Protocol Section 6 priority score and D1-D6 demotion rules."""
    mask = rasterize_polygon_utm(ring_xy, e0, n1, res_m, wc_grid.shape)
    n_px = int(mask.sum())
    area_m2 = abs(signed_area_xy(ring_xy))
    area_ha = area_m2 / 10000.0

    wc_vals = wc_grid[mask] if n_px > 0 else np.array([], dtype=np.uint8)
    def frac(code: int) -> float:
        return float(np.mean(wc_vals == code)) if len(wc_vals) > 0 else 0.0

    f_tree = frac(10)
    f_shrub = frac(20)
    f_grass = frac(30)
    f_crop = frac(40)
    f_built = frac(50)
    f_bare = frac(60)
    f_water = frac(80) + frac(90)
    f_open_clean = f_grass + f_crop + f_bare + 0.5 * f_shrub

    z_vals = dem_grid[mask]
    z_vals = z_vals[np.isfinite(z_vals)]
    z_mean = float(np.mean(z_vals)) if len(z_vals) > 0 else float(z_base)
    dz_m = z_mean - z_base

    d_vals = harappan_dist_m[mask]
    min_dist_m = float(np.min(d_vals)) if len(d_vals) > 0 else 9999.0

    wtype = win_spec["window_type"]
    length_m = win_spec.get("corridor_length_m")
    if wtype == "geophysical_open_parcel":
        score_clearance = 40.0 * f_open_clean * min(1.0, area_ha / 0.50)
    else:
        score_clearance = 35.0 * min(1.0, float(length_m or 0.0) / 300.0)

    score_topo = 30.0 * float(np.clip(dz_m / 6.0, 0.0, 1.0))
    score_prox = 30.0 * max(0.0, 1.0 - max(0.0, min_dist_m - 50.0) / 350.0)
    raw_score = score_clearance + score_topo + score_prox

    # Evaluate explicit demotion rules D1-D6
    hard_demotions = []
    soft_demotions = []
    if wtype == "geophysical_open_parcel" and f_built > 0.70:
        hard_demotions.append("D1_standing_structure_cover")
    if wtype == "geophysical_open_parcel" and f_tree > 0.60:
        soft_demotions.append("D2_gpr_obstructed_canopy")
    if f_water > 0.15 or dz_m < -1.0:
        hard_demotions.append("D3_water_or_sink_attenuation")
    if win_spec.get("industrial_clutter_flag", False):
        soft_demotions.append("D4_ferrous_clutter_or_disturbed_topsoil")
    if win_spec.get("heritage_sacred_flag", False):
        hard_demotions.append("D5_heritage_or_sacred_restricted")
    if (wtype == "geophysical_open_parcel" and area_ha < 0.10) or min_dist_m > 400.0:
        hard_demotions.append("D6_below_scale_or_distance_threshold")

    # Initial tier from score
    if raw_score >= 70.0:
        base_tier = 1
    elif raw_score >= 50.0:
        base_tier = 2
    else:
        base_tier = 3

    if hard_demotions:
        final_tier = 3
    elif soft_demotions:
        final_tier = min(3, base_tier + 1)
    else:
        final_tier = base_tier

    # Recommended field method based on type and flags
    if hard_demotions:
        if "D1_standing_structure_cover" in hard_demotions:
            method = "excluded_open_grid_use_street_rescue_only"
        elif "D3_water_or_sink_attenuation" in hard_demotions:
            method = "excluded_wet_or_sink_gpr_attenuated"
        elif "D5_heritage_or_sacred_restricted" in hard_demotions:
            method = "non_contact_surface_archive_only"
        else:
            method = "low_priority_defer"
    elif wtype == "rescue_corridor":
        method = "municipal_trench_watching_and_wheeled_gpr_transect"
    elif "D4_ferrous_clutter_or_disturbed_topsoil" in soft_demotions:
        method = "deep_ert_and_targeted_salvage_coring"
    elif "D2_gpr_obstructed_canopy" in soft_demotions:
        method = "fluxgate_gradiometry_or_canopy_gap_ert"
    else:
        method = "high_density_gpr_and_fluxgate_gradiometry"

    return {
        "area_ha": round(area_ha, 4),
        "corridor_length_m": round(float(length_m), 1) if length_m is not None else None,
        "wc_built_frac": round(f_built, 4),
        "wc_open_clean_frac": round(f_open_clean, 4),
        "wc_tree_frac": round(f_tree, 4),
        "wc_water_frac": round(f_water, 4),
        "dem_mean_m": round(z_mean, 2),
        "rel_elev_m": round(dz_m, 2),
        "dist_to_harappan_m": round(min_dist_m, 1),
        "score_clearance": round(score_clearance, 2),
        "score_topography": round(score_topo, 2),
        "score_proximity": round(score_prox, 2),
        "priority_score": round(raw_score, 2),
        "base_tier": base_tier,
        "final_tier": final_tier,
        "demoted": bool(hard_demotions or soft_demotions),
        "hard_demotions": hard_demotions,
        "soft_demotions": soft_demotions,
        "demotion_reasons": hard_demotions + soft_demotions,
        "recommended_method": method,
    }


def build_site_package(
    site_id: str,
    site_name: str,
    utm_epsg: int,
    proj: TMProjection,
    frame_utm: tuple[float, float, float, float],
    wc_path: Path,
    dem_path: Path,
    dem_tile_lat_lon: tuple[int, int],
    layer1_defs: list[dict],
    layer4_defs: list[dict],
    registration_info: dict,
    bg_mosaic_path: Path | None,
    bg_mosaic_meta: dict | None,
    out_geojson: Path,
    fig_path: Path,
) -> tuple[dict, list[dict]]:
    """Run deterministic 2 m rasterization, overlap bounds, window scoring, GeoJSON and figure export."""
    e0, n0, e1, n1 = frame_utm
    res_m = 2.0
    ncols = int(round((e1 - e0) / res_m))
    nrows = int(round((n1 - n0) / res_m))
    xs = e0 + (np.arange(ncols, dtype=np.float64) + 0.5) * res_m
    ys = n1 - (np.arange(nrows, dtype=np.float64) + 0.5) * res_m
    ee, nn = np.meshgrid(xs, ys)

    wc = load_worldcover_tif(wc_path)
    dem = load_dem_tile(dem_path, dem_tile_lat_lon[0], dem_tile_lat_lon[1])
    wc_grid = sample_worldcover_on_utm_grid(wc, ee, nn, proj)
    dem_grid = sample_dem_on_utm_grid(dem, ee, nn, proj)

    cx, cy = 0.5 * (e0 + e1), 0.5 * (n0 + n1)
    z_base = compute_local_plain_baseline(dem, cx, cy, proj)

    # Layer 2: Modern built-up mask (ESA WorldCover class 50)
    l2_built = (wc_grid == 50)
    px_to_ha = (res_m * res_m) / 10000.0

    # Layer 1 union mask + uncertainty-perturbed masks (eroded / dilated by each feature's uncertainty buffer)
    l1_union = np.zeros((nrows, ncols), dtype=bool)
    l1_inner = np.zeros((nrows, ncols), dtype=bool)
    l1_outer = np.zeros((nrows, ncols), dtype=bool)
    l1_harappan_core = np.zeros((nrows, ncols), dtype=bool)

    features = []
    l1_summary = []

    for item in layer1_defs:
        ring = ensure_ccw_closed(item["ring_utm"])
        area_ha = abs(signed_area_xy(ring)) / 10000.0
        m = rasterize_polygon_utm(ring, e0, n1, res_m, (nrows, ncols))
        u_px = max(1, int(round(item["positional_uncertainty_m"] / res_m)))
        # Approximate circular structuring element via Euclidean distance transform
        m_inner = ndi.distance_transform_edt(m) >= u_px
        m_outer = ndi.distance_transform_edt(~m) <= u_px
        if item.get("include_in_site_union", True):
            l1_union |= m
            l1_inner |= m_inner
            l1_outer |= m_outer
        if item.get("is_harappan_context", True):
            l1_harappan_core |= m

        z_vals = dem_grid[m]
        z_vals = z_vals[np.isfinite(z_vals)]
        z_mean = float(np.mean(z_vals)) if len(z_vals) else z_base
        zone_built_ha = float((m & l2_built).sum()) * px_to_ha
        zone_area_ras_ha = float(m.sum()) * px_to_ha
        zone_built_pct = (100.0 * zone_built_ha / zone_area_ras_ha) if zone_area_ras_ha > 0 else 0.0
        props = {
            "id": item["id"],
            "site_id": site_id,
            "layer": "layer_1_published_archaeology",
            "name": item["name"],
            "sub_type": item["sub_type"],
            "evidence_grade": item["evidence_grade"],
            "source_citation": item["source_citation"],
            "positional_uncertainty_m": item["positional_uncertainty_m"],
            "area_ha": round(area_ha, 4),
            "wc_built_overlap_ha": round(zone_built_ha, 4),
            "wc_built_overlap_pct": round(zone_built_pct, 2),
            "dem_mean_m": round(z_mean, 2),
            "rel_elev_m": round(z_mean - z_base, 2),
            "include_in_site_union": item.get("include_in_site_union", True),
            "notes": item.get("notes", ""),
        }
        features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "Polygon", "coordinates": [utm_ring_to_lonlat(ring, proj)]},
            }
        )
        l1_summary.append(props)

    l2_rings = vectorize_mask_utm(l2_built, e0, n1, res_m, min_area_m2=600.0, eps_px=2.0)
    l2_area_ha = float(l2_built.sum()) * px_to_ha
    for idx, r in enumerate(l2_rings, 1):
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"{site_id.upper()}-L2-BUILT-{idx:02d}",
                    "site_id": site_id,
                    "layer": "layer_2_modern_footprint",
                    "name": f"{site_name} modern built-up polygon {idx}",
                    "sub_type": "worldcover_built_up_class_50",
                    "source_citation": "ESA WorldCover 10 m 2021 v200 (class 50 Built-up, CC BY 4.0)",
                    "positional_uncertainty_m": 10.0,
                    "area_ha": round(abs(signed_area_xy(r)) / 10000.0, 4),
                },
                "geometry": {"type": "Polygon", "coordinates": [utm_ring_to_lonlat(r, proj)]},
            }
        )

    # Layer 3: Concealed overlap (Layer 1 union intersected with Layer 2 built-up)
    l3_nom = l1_union & l2_built
    l3_low = l1_inner & l2_built
    l3_high = l1_outer & l2_built

    px_to_ha = (res_m * res_m) / 10000.0
    l1_union_ha = float(l1_union.sum()) * px_to_ha
    l3_nom_ha = float(l3_nom.sum()) * px_to_ha
    l3_low_ha = float(l3_low.sum()) * px_to_ha
    l3_high_ha = float(l3_high.sum()) * px_to_ha
    overlap_pct = (100.0 * l3_nom_ha / l1_union_ha) if l1_union_ha > 0 else 0.0
    overlap_pct_low = (100.0 * l3_low_ha / l1_union_ha) if l1_union_ha > 0 else 0.0
    overlap_pct_high = min(100.0, (100.0 * l3_high_ha / l1_union_ha)) if l1_union_ha > 0 else 0.0

    l3_rings = vectorize_mask_utm(l3_nom, e0, n1, res_m, min_area_m2=250.0, eps_px=1.5)
    for idx, r in enumerate(l3_rings, 1):
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"{site_id.upper()}-L3-OVERLAP-{idx:02d}",
                    "site_id": site_id,
                    "layer": "layer_3_concealed_overlap",
                    "name": f"{site_name} concealed archaeological overlap zone {idx}",
                    "sub_type": "buried_beneath_modern_built_up",
                    "source_citation": "Intersection of Layer 1 published archaeological footprint and Layer 2 ESA WorldCover 2021 class 50",
                    "area_ha": round(abs(signed_area_xy(r)) / 10000.0, 4),
                },
                "geometry": {"type": "Polygon", "coordinates": [utm_ring_to_lonlat(r, proj)]},
            }
        )

    # Distance to nearest Harappan context in metres
    harappan_dist_m = ndi.distance_transform_edt(~l1_harappan_core) * res_m

    # Layer 4: Prioritized geophysical open parcels & rescue corridors
    win_rows = []
    l4_draw = []
    for w in layer4_defs:
        if w["window_type"] == "rescue_corridor":
            ring, length_m = polyline_to_corridor_polygon(w["line_utm"], w.get("half_width_m", 12.0))
            w = {**w, "corridor_length_m": length_m}
        else:
            ring = ensure_ccw_closed(w["ring_utm"])
        metrics = score_and_classify_window(w, ring, e0, n1, res_m, wc_grid, dem_grid, z_base, harappan_dist_m)
        cx_w = float(np.mean([p[0] for p in ring[:-1]]))
        cy_w = float(np.mean([p[1] for p in ring[:-1]]))
        clon, clat = proj.inverse(cx_w, cy_w)
        props = {
            "id": w["id"],
            "site_id": site_id,
            "site_name": site_name,
            "layer": "layer_4_survey_windows",
            "name": w["name"],
            "window_type": w["window_type"],
            "center_lat": round(float(clat), 6),
            "center_lon": round(float(clon), 6),
            "source_basis": w["source_basis"],
            **metrics,
            "notes": w.get("notes", ""),
        }
        features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "Polygon", "coordinates": [utm_ring_to_lonlat(ring, proj)]},
            }
        )
        win_rows.append(props)
        l4_draw.append((ring, props))

    # Sort window rows by final_tier ascending, then priority_score descending
    win_rows.sort(key=lambda r: (r["final_tier"], -r["priority_score"], r["id"]))

    fc = {
        "type": "FeatureCollection",
        "name": f"{site_id}-windows-v1",
        "crs_note": "WGS 84 (EPSG:4326, RFC 7946 lon/lat); metric computations in EPSG:" + str(utm_epsg),
        "metadata": {
            "site_id": site_id,
            "site_name": site_name,
            "utm_epsg": utm_epsg,
            "utm_frame_e0_n0_e1_n1": [e0, n0, e1, n1],
            "raster_resolution_m": res_m,
            "local_plain_baseline_m": round(z_base, 2),
            "layer_1_union_area_ha": round(l1_union_ha, 3),
            "layer_2_built_area_ha": round(l2_area_ha, 3),
            "layer_3_concealed_overlap_ha": round(l3_nom_ha, 3),
            "layer_3_concealed_overlap_lower_ha": round(l3_low_ha, 3),
            "layer_3_concealed_overlap_upper_ha": round(l3_high_ha, 3),
            "layer_3_concealed_pct_of_l1": round(overlap_pct, 2),
            "layer_3_concealed_pct_lower": round(overlap_pct_low, 2),
            "layer_3_concealed_pct_upper": round(overlap_pct_high, 2),
            "registration": registration_info,
        },
        "features": features,
    }
    out_geojson.write_text(json.dumps(fc, indent=2), encoding="utf-8")

    # Render diagnostic 4-layer map figure
    fig, ax = plt.subplots(figsize=(9, 8), dpi=160)
    if bg_mosaic_path and bg_mosaic_meta and bg_mosaic_path.exists():
        bg = np.array(Image.open(bg_mosaic_path).convert("RGB"))
        # Compute UTM extent of background mosaic corners
        h_bg, w_bg = bg.shape[:2]
        lon_w, lat_n = mosaic_px_to_lonlat(0, 0, bg_mosaic_meta)
        lon_e, lat_s = mosaic_px_to_lonlat(w_bg, h_bg, bg_mosaic_meta)
        be0, bn1 = proj.forward(lon_w, lat_n)
        be1, bn0 = proj.forward(lon_e, lat_s)
        ax.imshow(bg, extent=[float(be0), float(be1), float(bn0), float(bn1)], alpha=0.82)
    else:
        ax.imshow(dem_grid, extent=[e0, e1, n0, n1], cmap="terrain", alpha=0.6)

    # Layer 2 built-up overlay (subtle red tint)
    built_rgba = np.zeros((nrows, ncols, 4), dtype=np.float32)
    built_rgba[l2_built] = [0.9, 0.2, 0.2, 0.22]
    ax.imshow(built_rgba, extent=[e0, e1, n0, n1])

    # Layer 3 concealed overlap overlay (bright magenta hatch/tint)
    ov_rgba = np.zeros((nrows, ncols, 4), dtype=np.float32)
    ov_rgba[l3_nom] = [1.0, 0.0, 0.85, 0.45]
    ax.imshow(ov_rgba, extent=[e0, e1, n0, n1])

    # Layer 1 outlines (gold)
    for item in layer1_defs:
        r = ensure_ccw_closed(item["ring_utm"])
        poly = MplPolygon(r, closed=True, facecolor="none", edgecolor="#FFD700", linewidth=1.8, linestyle="-")
        ax.add_patch(poly)

    # Layer 4 windows (Tier 1 bright cyan, Tier 2 lime, Tier 3 orange dashed)
    tier_styles = {
        1: ("#00FFFF", "-", 2.2),
        2: ("#7CFC00", "-", 1.8),
        3: ("#FF8C00", "--", 1.4),
    }
    for ring, p in l4_draw:
        col, ls, lw = tier_styles[p["final_tier"]]
        poly = MplPolygon(ring, closed=True, facecolor=col, edgecolor=col, alpha=0.22, linewidth=lw, linestyle=ls)
        ax.add_patch(poly)
        poly_e = MplPolygon(ring, closed=True, facecolor="none", edgecolor=col, linewidth=lw, linestyle=ls)
        ax.add_patch(poly_e)
        cx_l = float(np.mean([pt[0] for pt in ring[:-1]]))
        cy_l = float(np.mean([pt[1] for pt in ring[:-1]]))
        ax.text(
            cx_l,
            cy_l,
            f"{p['id']}\nT{p['final_tier']} ({p['priority_score']:.0f})",
            color="white",
            fontsize=6.5,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="black", alpha=0.65, edgecolor=col, linewidth=0.7),
        )

    ax.set_xlim(e0, e1)
    ax.set_ylim(n0, n1)
    ax.set_aspect("equal")
    ax.set_xlabel(f"UTM Easting (m, EPSG:{utm_epsg})")
    ax.set_ylabel(f"UTM Northing (m, EPSG:{utm_epsg})")
    ax.set_title(
        f"{site_name}: L1 {l1_union_ha:.1f} ha | Concealed L3 {l3_nom_ha:.1f} ha ({overlap_pct:.1f}%)\n"
        f"Gold=L1 Archaeology | Magenta=L3 Concealed Overlap | Cyan=T1, Green=T2, Orange=T3 Windows",
        fontsize=9.5,
    )
    fig.tight_layout()
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)

    summary = {
        "site_id": site_id,
        "site_name": site_name,
        "utm_epsg": utm_epsg,
        "geojson_path": out_geojson.relative_to(ROOT).as_posix(),
        "figure_path": fig_path.relative_to(ROOT).as_posix(),
        "local_plain_baseline_m": round(z_base, 2),
        "layer_1_feature_count": len(layer1_defs),
        "layer_1_union_area_ha": round(l1_union_ha, 3),
        "layer_2_built_area_ha": round(l2_area_ha, 3),
        "layer_3_concealed_overlap_ha": round(l3_nom_ha, 3),
        "layer_3_concealed_overlap_bounds_ha": [round(l3_low_ha, 3), round(l3_high_ha, 3)],
        "layer_3_concealed_pct_of_l1": round(overlap_pct, 2),
        "layer_3_concealed_pct_bounds": [round(overlap_pct_low, 2), round(overlap_pct_high, 2)],
        "layer_4_window_count": len(win_rows),
        "layer_4_tier_counts": {
            "tier_1": sum(1 for r in win_rows if r["final_tier"] == 1),
            "tier_2": sum(1 for r in win_rows if r["final_tier"] == 2),
            "tier_3": sum(1 for r in win_rows if r["final_tier"] == 3),
        },
        "layer_4_demoted_count": sum(1 for r in win_rows if r["demoted"]),
        "registration": registration_info,
        "layer_1_zones": l1_summary,
    }
    return summary, win_rows


def build_harappa() -> tuple[dict, list[dict]]:
    proj43 = TMProjection(75.0)
    hrp18_meta_p = ROOT / "data/raw/2026-10-21-plan-registration/R1-G1/mosaics/harappa_z18_cur_z18_x184123-184135_y107617-107629.json"
    hrp16_meta_p = ROOT / "data/raw/2026-10-21-town-axes/img-A/mosaics/harappa_ov_z16_x46030-46034_y26903-26907.json"
    hrp16_png_p = ROOT / "data/raw/2026-10-21-town-axes/img-A/mosaics/harappa_ov_z16_x46030-46034_y26903-26907.png"
    hrp18_meta = json.loads(hrp18_meta_p.read_text(encoding="utf-8"))
    hrp16_meta = json.loads(hrp16_meta_p.read_text(encoding="utf-8"))

    # 1. Primary registration: Kenoyer (1991, Fig. 4.2) -> Esri World Imagery z18 (6 permanent landmarks)
    # Grid bar on kenoyer1991_p5_fig4_2.png (200 dpi render):
    #   E1400..E2800 = 1358 px for 1400 m (1.0309 m/px); N0800..N2000 = 1169 px for 1200 m (1.0265 m/px); mean = 1.0287 m/px.
    ken_cps = [
        {"id": "cp1_granary_ctr",    "class": "B", "sigma_m": 6.0, "plan_px": [740.0, 322.0],   "z18_px": [1344.0, 712.0],  "feature": "Mound F Great Granary centre"},
        {"id": "cp2_workmen_q_ctr",  "class": "A", "sigma_m": 3.0, "plan_px": [734.0, 488.0],   "z18_px": [1325.0, 1043.0], "feature": "Mound F Workmen's Quarters conserved block centre"},
        {"id": "cp3_muslim_tomb",    "class": "A", "sigma_m": 3.0, "plan_px": [958.0, 598.0],   "z18_px": [1752.0, 1278.0], "feature": "Mound AB Muslim tomb centre"},
        {"id": "cp4_mound_ab_vats",  "class": "B", "sigma_m": 6.0, "plan_px": [942.0, 779.0],   "z18_px": [1712.0, 1656.0], "feature": "Mound AB Vats central walled excavation enclosure"},
        {"id": "cp5_harappa_museum", "class": "A", "sigma_m": 3.0, "plan_px": [1208.0, 1175.0], "z18_px": [2235.0, 2475.0], "feature": "Harappa Museum main building"},
        {"id": "cp6_rest_house",     "class": "B", "sigma_m": 6.0, "plan_px": [1070.0, 1200.0], "z18_px": [1960.0, 2500.0], "feature": "Harappa Rest House compound"},
    ]
    P_ken = [tuple(c["plan_px"]) for c in ken_cps]
    Q_ken = [tuple(map(float, proj43.forward(*mosaic_px_to_lonlat(c["z18_px"][0], c["z18_px"][1], hrp18_meta)))) for c in ken_cps]
    sig_ken = [c["sigma_m"] for c in ken_cps]
    ken_fit = fit_similarity_wls(P_ken, Q_ken, sig_ken, expected_scale_m_per_px=1.0287)

    # 2. Cross-check registration: Wheeler (1947, Pl. XV) audited R1 (12 pts) & R2 (9 pts)
    wheeler_checks = {}
    for reg_name in ("control-R1", "control-R2"):
        cp_file = ROOT / f"experiments/2026-10-21-plan-registration/{reg_name}/harappa__wheeler1947-pl15.json"
        cp_data = json.loads(cp_file.read_text(encoding="utf-8"))
        pts = cp_data["links"][0]["points"]
        m_meta = json.loads((ROOT / pts[0]["mosaic"]).read_text(encoding="utf-8"))
        Pw = [tuple(pt["plan_px"]) for pt in pts]
        Qw = [tuple(map(float, proj43.forward(*mosaic_px_to_lonlat(pt["mosaic_px"][0], pt["mosaic_px"][1], m_meta)))) for pt in pts]
        sw = [3.0 if pt["class"] == "A" else 6.0 for pt in pts]
        wheeler_checks[reg_name] = fit_similarity_wls(Pw, Qw, sw, expected_scale_m_per_px=0.5957)

    # Helper: convert HARP metric grid (E, N) -> Kenoyer 1991 Fig 4.2 pixels -> UTM 43N
    # Measured grid ticks on kenoyer1991_p5_fig4_2.png:
    #   E1400 -> x=417.0, E2800 -> x=1775.0 (0.9700 px/m)
    #   N2000 -> y=199.0, N0800 -> y=1368.0 (0.97417 px/m)
    def harp_grid_to_utm(E_val: float, N_val: float) -> tuple[float, float]:
        px = 417.0 + (E_val - 1400.0) * (1358.0 / 1400.0)
        py = 199.0 + (2000.0 - N_val) * (1169.0 / 1200.0)
        return apply_similarity(px, py, ken_fit["params"])

    def harp_poly(pts_en: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [harp_grid_to_utm(e, n) for e, n in pts_en]

    u_plan = round(max(10.0, 1.5 * ken_fit["rmse_m"]), 1)

    layer1_defs = [
        {
            "id": "HRP-L1-MOUND-F",
            "name": "Mound F (Great Granary and Workmen's Quarters walled sector)",
            "sub_type": "walled_mound_sector",
            "evidence_grade": "registered_plan",
            "source_citation": "Kenoyer 1991 Fig. 4.2 (p. 31); Kenoyer 2008 Fig. 3 (p. 28); Wheeler 1947 Pl. XV",
            "positional_uncertainty_m": u_plan,
            "ring_utm": harp_poly([(1640, 1950), (1860, 1955), (1950, 1870), (1940, 1690), (1690, 1690), (1640, 1780)]),
            "notes": "Conserved Mature Harappan granary, circular working platforms and workmen's quarters.",
        },
        {
            "id": "HRP-L1-MOUND-AB",
            "name": "Mound AB (Citadel defences and high mound)",
            "sub_type": "walled_mound_sector",
            "evidence_grade": "registered_plan",
            "source_citation": "Wheeler 1947 Pl. XV; Kenoyer 1991 Fig. 4.2 (p. 31); Kenoyer 2008 Fig. 3 (p. 28)",
            "positional_uncertainty_m": u_plan,
            "ring_utm": harp_poly([(1740, 1680), (1980, 1665), (2055, 1300), (2025, 1235), (1835, 1245), (1755, 1450)]),
            "notes": "Fortified mud-brick perimeter wall, Vats and Wheeler excavations, HARP Operation 2.",
        },
        {
            "id": "HRP-L1-MOUND-E",
            "name": "Mound E (Urban sector, kilns and southern gateway)",
            "sub_type": "walled_mound_sector",
            "evidence_grade": "registered_plan",
            "source_citation": "Kenoyer 1991 Fig. 4.2 (p. 31); Kenoyer 2008 Fig. 3 (p. 28)",
            "positional_uncertainty_m": u_plan,
            "ring_utm": harp_poly([(2060, 1405), (2425, 1395), (2495, 1185), (2355, 1055), (2170, 1110), (2065, 1240)]),
            "notes": "HARP Operation 3 kilns, revetment wall, Early-to-Mature perimeter wall #30 and gateway #84.",
        },
        {
            "id": "HRP-L1-MOUND-ET",
            "name": "Mound ET (Eastern walled suburb and Old Police Station)",
            "sub_type": "walled_mound_sector",
            "evidence_grade": "registered_plan",
            "source_citation": "Kenoyer 2008 Fig. 3 (p. 28); Kenoyer 1991 Fig. 4.2 (p. 31)",
            "positional_uncertainty_m": u_plan,
            "ring_utm": harp_poly([(2450, 1380), (2710, 1355), (2770, 1245), (2660, 1155), (2485, 1145)]),
            "notes": "Walled eastern suburb with southern gateway linking to Mound E.",
        },
        {
            "id": "HRP-L1-NE-TOWN-SECTOR",
            "name": "Northeastern Walled Sector beneath Modern Harappa Town",
            "sub_type": "concealed_walled_sector",
            "evidence_grade": "registered_plan",
            "source_citation": "Kenoyer 1991 p. 57 ('approximately one quarter of the total area of the site'); Kenoyer 2008 Fig. 3 (p. 28, shaded sector '? = Walls not excavated')",
            "positional_uncertainty_m": 15.0,
            "ring_utm": harp_poly([(2180, 1840), (2480, 1895), (2665, 1815), (2625, 1405), (2210, 1410), (2165, 1620)]),
            "notes": "Shaded walled sector in Kenoyer 2008 Fig. 3 directly beneath modern Harappa town; perimeter walls unexcavated.",
        },
        {
            "id": "HRP-L1-LOW-WESTERN",
            "name": "Low Western Mound",
            "sub_type": "outer_mound_sector",
            "evidence_grade": "registered_plan",
            "source_citation": "Kenoyer 1991 Fig. 4.2 (p. 31); Kenoyer 2008 Fig. 3 (p. 28)",
            "positional_uncertainty_m": u_plan,
            "ring_utm": harp_poly([(1645, 1350), (1750, 1360), (1765, 1170), (1655, 1165)]),
            "notes": "Lower western occupation rise tested by HARP test pits.",
        },
        {
            "id": "HRP-L1-CEMETERY-H-R37",
            "name": "Cemetery H and Cemetery R37 mortuary zone",
            "sub_type": "cemetery_zone",
            "evidence_grade": "registered_plan",
            "source_citation": "Wheeler 1947 Pl. XV; Kenoyer 1991 Fig. 4.2 (p. 31, HARP Operation 1)",
            "positional_uncertainty_m": u_plan,
            "ring_utm": harp_poly([(1835, 1230), (2135, 1225), (2130, 1045), (1860, 1005)]),
            "notes": "Mature Harappan Cemetery R37 and Late Harappan Cemetery H south of Mound AB.",
        },
        {
            "id": "HRP-L1-AREA-G-SE",
            "name": "Area G / Vats southeastern archaeological zone",
            "sub_type": "outer_excavation_zone",
            "evidence_grade": "registered_plan",
            "source_citation": "Kenoyer 2008 Fig. 3 (p. 28, labeled 'Vats'); Vats 1940",
            "positional_uncertainty_m": 15.0,
            "ring_utm": harp_poly([(2470, 1120), (2710, 1140), (2715, 860), (2495, 865)]),
            "notes": "Southern scatter and Vats excavation area south of the Chichawatni-Sahiwal road.",
        },
    ]

    layer4_defs = [
        {
            "id": "HRP-W01",
            "name": "Central Inter-Mound Clearing (West Edge of Harappa Town)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z16/z18, ESA WorldCover 2021, Kenoyer 2008 Fig. 3 ('?' wall edge)",
            "ring_utm": harp_poly([(2105, 1625), (2215, 1625), (2215, 1465), (2105, 1465)]),
            "notes": "Broad treeless bare-earth clearing straddling the inferred western perimeter wall of the concealed town sector between Mound AB and modern Harappa town.",
        },
        {
            "id": "HRP-W02",
            "name": "South Town to Mound E/ET Transition Clearing",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z16/z18, ESA WorldCover 2021, Kenoyer 2008 Fig. 3",
            "ring_utm": harp_poly([(2260, 1455), (2500, 1450), (2500, 1365), (2260, 1370)]),
            "notes": "Open unbuilt strip between the southern margin of modern Harappa town and the northern perimeter of Mounds E and ET.",
        },
        {
            "id": "HRP-W03",
            "name": "Low Western Mound Open Terrace",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, Kenoyer 1991 Fig. 4.2",
            "ring_utm": harp_poly([(1650, 1340), (1755, 1340), (1755, 1175), (1650, 1175)]),
            "notes": "Open bare/scrub western mound margin suitable for continuous GPR and magnetometry grids.",
        },
        {
            "id": "HRP-W04",
            "name": "Cemetery H to Mound AB South Open Ground",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, Wheeler 1947 Pl. XV",
            "ring_utm": harp_poly([(1845, 1215), (2025, 1215), (2025, 1100), (1845, 1100)]),
            "notes": "Open grassy/bare ground south of Mound AB rampart wall; non-invasive mapping of Late Harappan and post-Harappan deposits.",
        },
        {
            "id": "HRP-W05",
            "name": "Northwest Town Edge Dry Terrace (East of Mound F)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z16/z18, ESA WorldCover 2021",
            "ring_utm": harp_poly([(2000, 1850), (2135, 1850), (2135, 1730), (2000, 1730)]),
            "notes": "Open agricultural/bare apron between Mound F eastern edge and the modern town pond.",
        },
        {
            "id": "HRP-W06",
            "name": "Harappa Town Northwest Pond / Depression Basin",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z16/z18 (green standing pond), ESA WorldCover 2021, Copernicus GLO-30",
            "ring_utm": harp_poly([(2180, 1935), (2290, 1935), (2290, 1815), (2180, 1815)]),
            "notes": "Algae-covered pond/basin at NW edge of modern Harappa town; WorldCover 2021 misclassifies eutrophic algae as vegetation (water=0.0) while Copernicus DEM confirms a -0.56 m local depression.",
        },
        {
            "id": "HRP-W07",
            "name": "Mound AB Muslim Tomb & Protected Citadel Core (Heritage Control)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Wheeler 1947 Pl. XV, Esri z18",
            "ring_utm": harp_poly([(1860, 1630), (1995, 1630), (1995, 1500), (1860, 1500)]),
            "heritage_sacred_flag": True,
            "notes": "Active religious shrine (Muslim tomb) and protected tree-covered citadel core; Rule D5 heritage/sacred exclusion control.",
        },
        {
            "id": "HRP-W08",
            "name": "Harappa Town West & South Perimeter Street Rescue Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Esri z16/z18, OpenStreetMap Harappa streets, Kenoyer 2008 Fig. 3",
            "line_utm": harp_poly([(2210, 1760), (2225, 1560), (2340, 1455), (2550, 1410), (2690, 1390)]),
            "half_width_m": 12.0,
            "notes": "Public street and utility corridor tracing the western and southern flanks of modern Harappa town across the concealed NE walled sector.",
        },
        {
            "id": "HRP-W09",
            "name": "Chichawatni-Sahiwal Road Archaeological Frontage Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Esri z16/z18, OpenStreetMap Harappa Road, Kenoyer 1991 Fig. 4.2",
            "line_utm": harp_poly([(1880, 885), (2160, 965), (2420, 1055), (2680, 1165), (2880, 1255)]),
            "half_width_m": 14.0,
            "notes": "Regional highway corridor bordering Cemetery R37, Harappa Museum, Mound E southern gateway, Mound ET and Area G.",
        },
        {
            "id": "HRP-W10",
            "name": "Eastern Harappa Town Open Sports / Vacant Margin",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z16, ESA WorldCover 2021",
            "ring_utm": harp_poly([(2795, 1565), (2910, 1565), (2910, 1415), (2795, 1415)]),
            "notes": "Open unbuilt ground east of modern Harappa town testing whether the buried NE urban sector extends beyond E2700.",
        },
    ]

    # Define 2.0 km x 1.7 km UTM frame covering HARP E1350..E3050, N0750..N2150
    c_sw = harp_grid_to_utm(1380, 760)
    c_ne = harp_grid_to_utm(3020, 2120)
    frame_utm = (math.floor(c_sw[0] / 10.0) * 10.0, math.floor(c_sw[1] / 10.0) * 10.0,
                 math.ceil(c_ne[0] / 10.0) * 10.0, math.ceil(c_ne[1] / 10.0) * 10.0)

    reg_info = {
        "primary_plan": "Kenoyer 1991 Fig. 4.2 (p. 31) & Kenoyer 2008 Fig. 3 (p. 28), HARP metric grid",
        "method": "4-parameter weighted least-squares similarity transform to Esri World Imagery z18 (UTM 43N)",
        "control_points": ken_cps,
        "fit_metrics": ken_fit,
        "cross_check_wheeler1947_pl15": wheeler_checks,
        "uncertainty_buffer_m": u_plan,
    }

    return build_site_package(
        site_id="harappa",
        site_name="Harappa",
        utm_epsg=32643,
        proj=proj43,
        frame_utm=frame_utm,
        wc_path=ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONTROL_20261012T053309958546Z_B02_WorldCover_N30E072.tif",
        dem_path=ROOT / "data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N30_00_E072_00_DEM.tif",
        dem_tile_lat_lon=(30, 72),
        layer1_defs=layer1_defs,
        layer4_defs=layer4_defs,
        registration_info=reg_info,
        bg_mosaic_path=hrp16_png_p,
        bg_mosaic_meta=hrp16_meta,
        out_geojson=EXP_DIR / "harappa-windows-v1.geojson",
        fig_path=FIG_DIR / "harappa_4layer_map.png",
    )


def build_lakhanjo_daro() -> tuple[dict, list[dict]]:
    proj42 = TMProjection(69.0)
    lj_meta_p = RAW_NEW / "mosaics/lakhanjo_daro_z18_x181199-181210_y110040-110050.json"
    lj_png_p = RAW_NEW / "mosaics/lakhanjo_daro_z18_x181199-181210_y110040-110050.png"
    lj_meta = json.loads(lj_meta_p.read_text(encoding="utf-8"))

    def z18_to_utm(mx: float, my: float) -> tuple[float, float]:
        lon, lat = mosaic_px_to_lonlat(mx, my, lj_meta)
        e, n = proj42.forward(lon, lat)
        return float(e), float(n)

    # Primary registration: Biagi & Vidale (2022, Fig. 3, Asian Perspectives 61(1):6) -> Esri World Imagery z18
    # 6 sharp road intersections & compound wall corners along Road 7, Road 8 and Road 3 around Mound D
    lj_cps = [
        {"id": "cp1_rd7_x_rd8",        "class": "A", "sigma_m": 3.0, "plan_px": [485.0, 577.0], "z18_px": [1470.0, 1425.0], "feature": "Road No. 7 x Road No. 8 intersection centre"},
        {"id": "cp2_rd7_x_rd3",        "class": "A", "sigma_m": 3.0, "plan_px": [380.0, 804.0], "z18_px": [1238.0, 1957.0], "feature": "Road No. 7 x Road No. 3 intersection centre"},
        {"id": "cp3_moundD_plot_nw",   "class": "A", "sigma_m": 3.0, "plan_px": [585.0, 588.0], "z18_px": [1698.0, 1445.0], "feature": "Mound D plot NW wall corner on Road No. 8"},
        {"id": "cp4_factory_rd8_nw",   "class": "A", "sigma_m": 3.0, "plan_px": [682.0, 591.0], "z18_px": [1925.0, 1450.0], "feature": "Factory block NW corner east of Mound D on Road No. 8"},
        {"id": "cp5_rd3_mid_factory",  "class": "A", "sigma_m": 3.0, "plan_px": [746.0, 814.0], "z18_px": [2075.0, 1972.0], "feature": "Industrial lane x Road No. 3 junction south of factory"},
        {"id": "cp6_rd8_east_factory", "class": "A", "sigma_m": 3.0, "plan_px": [888.0, 594.0], "z18_px": [2400.0, 1458.0], "feature": "East industrial compound corner on Road No. 8"},
    ]
    P_lj = [tuple(c["plan_px"]) for c in lj_cps]
    Q_lj = [z18_to_utm(c["z18_px"][0], c["z18_px"][1]) for c in lj_cps]
    sig_lj = [c["sigma_m"] for c in lj_cps]

    # Independent road-network scale check from OSM Road 8 -> Road 3 separation (285.3 m / 234 px = 1.2192 m/px)
    lj_fit = fit_similarity_wls(P_lj, Q_lj, sig_lj, expected_scale_m_per_px=1.2192)

    # Project Biagi & Vidale Fig. 3 white box around Mound D (585..675, 594..666) and black rectangle (602..634, 616..636)
    mound_d_ring = [
        apply_similarity(585.0, 594.0, lj_fit["params"]),
        apply_similarity(675.0, 594.0, lj_fit["params"]),
        apply_similarity(675.0, 666.0, lj_fit["params"]),
        apply_similarity(585.0, 666.0, lj_fit["params"]),
    ]
    md_e, md_n = apply_similarity(618.0, 626.0, lj_fit["params"])
    md_lon, md_lat = proj42.inverse(md_e, md_n)
    # Audit caption printed coordinate discrepancy (27°43'44"N, 68°50'55"E vs registered 27°43'29"N, 68°50'54"E)
    cap_lat = 27.0 + 43.0 / 60.0 + 44.0 / 3600.0
    cap_lon = 68.0 + 50.0 / 60.0 + 55.0 / 3600.0
    cap_e, cap_n = proj42.forward(cap_lon, cap_lat)
    caption_offset_m = float(math.hypot(md_e - float(cap_e), md_n - float(cap_n)))

    # Printed 0-200 m bar on Biagi Fig. 3 spans 418 px -> implies 0.4785 m/px vs true 1.2194 m/px (factor 2.55x)
    printed_bar_px = 418.0
    printed_bar_true_m = printed_bar_px * lj_fit["scale_m_per_px"]

    # Layer 1 polygons:
    # 1. Registered Mound D / Trench C plot (Biagi & Vidale 2022 Fig. 3, ~1.0 ha, registered_plan)
    # 2. Central-West Core Salvage Block anchored on DOAM (27.723889, 68.846431) & Shar & Shah (27.724167, 68.847500)
    # 3. Published ~50 ha Sukkur SITE limestone-terrace envelope (ul-Haq & Ali 2001:29; Sindh Directorate 2022)
    #    bounded cleanly along the flood-free terrace (>= 61.5 m) between Road 7/west, Road 8/north terrace, east mounds, and south edge
    layer1_defs = [
        {
            "id": "LKD-L1-MOUND-D-TRENCH-C",
            "name": "Mound D / Trench C (Plots D9-D11 south of Road No. 8)",
            "sub_type": "registered_excavation_zone",
            "evidence_grade": "registered_plan",
            "source_citation": "Biagi and Vidale 2022, Asian Perspectives 61(1):6, Fig. 3 (white outline around Mound D Trench C); GrN-23123 charcoal date",
            "positional_uncertainty_m": 15.0,
            "ring_utm": mound_d_ring,
            "include_in_site_union": True,
            "notes": f"Registered from Fig. 3 (RMSE {lj_fit['rmse_m']:.2f} m) to ({float(md_lat):.6f}N, {float(md_lon):.6f}E); printed caption latitude 27d43'44\"N sits {caption_offset_m:.0f} m north of the drawn box.",
        },
        {
            "id": "LKD-L1-CENTRAL-WEST-CORE",
            "name": "Central and Western Salvage Mound Core (DOAM / Shar & Shah Anchor)",
            "sub_type": "documented_mound_core",
            "evidence_grade": "topographic_source_envelope",
            "source_citation": "DOAM site inventory (27.723889N, 68.846431E); Shar and Shah 2022 (27d43'27\"N, 68d50'51\"E); Directorate of Antiquities Sindh 2022 (central & western mounds)",
            "positional_uncertainty_m": 25.0,
            "ring_utm": [
                z18_to_utm(1470, 1435),
                z18_to_utm(1870, 1445),
                z18_to_utm(1865, 1965),
                z18_to_utm(1245, 1955),
            ],
            "include_in_site_union": True,
            "notes": "Block bounded by Road No. 7, Road No. 8 and Road No. 3 containing Mound D, the DOAM anchor and Shar & Shah's main mound coordinate.",
        },
        {
            "id": "LKD-L1-SITE-50HA-ENVELOPE",
            "name": "Lakhanjo-Daro Sukkur SITE Published ~50 ha Terrace Envelope (Mounds A-D)",
            "sub_type": "source_bounded_site_envelope",
            "evidence_grade": "topographic_source_envelope",
            "source_citation": "ul-Haq and Ali 2001:29 (quoted in Biagi and Vidale 2022:5, 'originally covered nearly 50 hectares of the SITE area'); Directorate of Antiquities Sindh 2022 (western, central and eastern mounds); Copernicus GLO-30 terrace",
            "positional_uncertainty_m": 50.0,
            "ring_utm": [
                z18_to_utm(1250, 960),
                z18_to_utm(2480, 1020),
                z18_to_utm(2860, 1450),
                z18_to_utm(2840, 2120),
                z18_to_utm(1140, 2100),
                z18_to_utm(990, 1650),
            ],
            "include_in_site_union": True,
            "notes": "Bounded to ~50 ha on the flood-free Sukkur SITE limestone terrace (61.5-72 m MSL), excluding the NW flooded basin (<60 m) and rejecting the unauthenticated 300 ha claim. No unmapped trench polygons are fabricated for Mounds A-C.",
        },
    ]

    layer4_defs = [
        {
            "id": "LKD-W01",
            "name": "Mound D Vacant Industrial Plot (Plots D9-D11 South of Road 8)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Biagi & Vidale 2022 Fig. 3 (registered), Esri z18, ESA WorldCover 2021",
            "ring_utm": [z18_to_utm(1698, 1448), z18_to_utm(1872, 1452), z18_to_utm(1868, 1695), z18_to_utm(1695, 1690)],
            "notes": "Unbuilt sandy plot directly containing Mound D / Trench C; highest-urgency GPR and ERT target before industrial infill.",
        },
        {
            "id": "LKD-W02",
            "name": "Central-West Unbuilt Scrub & Bare Plots (DOAM / Shar & Shah Core)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, DOAM & Shar & Shah 2022 coordinates",
            "ring_utm": [z18_to_utm(1475, 1450), z18_to_utm(1695, 1455), z18_to_utm(1860, 1700), z18_to_utm(1855, 1950), z18_to_utm(1450, 1945)],
            "notes": "Large contiguous unbuilt parcels immediately west and south of Mound D spanning both DOAM and Shar & Shah site coordinates.",
        },
        {
            "id": "LKD-W03",
            "name": "North-of-Road-8 Open Walled Industrial Plots",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021",
            "ring_utm": [z18_to_utm(1640, 1080), z18_to_utm(2260, 1110), z18_to_utm(2240, 1410), z18_to_utm(1520, 1405)],
            "notes": "Contiguous vacant walled plots immediately across Road No. 8 north of Mound D on the elevated limestone terrace.",
        },
        {
            "id": "LKD-W04",
            "name": "Road No. 8 East-West Industrial & Utility Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Biagi & Vidale 2022 Fig. 3, Esri z18, OpenStreetMap, ul-Haq & Ali 2001:29",
            "line_utm": [z18_to_utm(1465, 1425), z18_to_utm(1930, 1438), z18_to_utm(2400, 1445), z18_to_utm(2880, 1455)],
            "half_width_m": 12.0,
            "notes": "Metalled arterial bordering Mound D; utility conduit and sewerage cuts expose lower in-situ Harappan strata.",
        },
        {
            "id": "LKD-W05",
            "name": "Road No. 3 East-West Southern Spine Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Biagi & Vidale 2022 Fig. 3, Esri z18, OpenStreetMap",
            "line_utm": [z18_to_utm(1100, 1955), z18_to_utm(1650, 1965), z18_to_utm(2250, 1978), z18_to_utm(2865, 1995)],
            "half_width_m": 12.0,
            "notes": "Southern metalled road bounding the central and eastern mound sectors; suitable for wheeled GPR transects and trench watching.",
        },
        {
            "id": "LKD-W06",
            "name": "Road No. 7 Western Craft-Sector Spine Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Biagi & Vidale 2022 Fig. 3, Esri z18, OpenStreetMap",
            "line_utm": [z18_to_utm(1650, 960), z18_to_utm(1470, 1425), z18_to_utm(1240, 1957), z18_to_utm(1080, 2220)],
            "half_width_m": 12.0,
            "notes": "Northeast-southwest metalled artery crossing the western craft-production zone.",
        },
        {
            "id": "LKD-W07",
            "name": "Active Factory Complex East of Mound D (Industrial Clutter Control)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021",
            "ring_utm": [z18_to_utm(1925, 1460), z18_to_utm(2520, 1468), z18_to_utm(2510, 1950), z18_to_utm(1920, 1945)],
            "industrial_clutter_flag": True,
            "notes": "Dense active industrial sheds and metallic yards; tests Rule D1 (built-up >70%) and Rule D4 (ferrous industrial clutter) demotion.",
        },
        {
            "id": "LKD-W08",
            "name": "Eastern Disturbed Pond & Refuse Pit Zone (Disturbance Control)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, Directorate of Antiquities Sindh 2022 (eastern mound disturbed & garbage-covered)",
            "ring_utm": [z18_to_utm(2690, 1465), z18_to_utm(2865, 1470), z18_to_utm(2855, 1740), z18_to_utm(2680, 1735)],
            "industrial_clutter_flag": True,
            "notes": "Green standing pit and disturbed eastern mound fill; tests Rule D4 (disturbed/garbage fill) demotion to deep ERT / coring.",
        },
        {
            "id": "LKD-W09",
            "name": "Northwest Floodplain Wetland & Ponds (Off-Terrace Negative Control)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, Copernicus GLO-30 (<59 m MSL)",
            "ring_utm": [z18_to_utm(200, 350), z18_to_utm(760, 350), z18_to_utm(760, 950), z18_to_utm(200, 950)],
            "notes": "Low flooded basin off the Sukkur SITE limestone terrace; tests Rule D3 (water/sink) and Rule D6 (>400 m) hard demotion.",
        },
    ]

    # UTM frame covering the entire z18 mosaic (about 1.6 km x 1.5 km)
    sw_e, sw_n = z18_to_utm(120, 2680)
    ne_e, ne_n = z18_to_utm(2980, 140)
    frame_utm = (math.floor(sw_e / 10.0) * 10.0, math.floor(sw_n / 10.0) * 10.0,
                 math.ceil(ne_e / 10.0) * 10.0, math.ceil(ne_n / 10.0) * 10.0)

    reg_info = {
        "primary_plan": "Biagi and Vidale 2022, Asian Perspectives 61(1):6, Fig. 3 (Sukkur SITE / Mound D Trench C)",
        "method": "4-parameter weighted least-squares similarity transform to Esri World Imagery z18 (UTM 42N)",
        "control_points": lj_cps,
        "fit_metrics": lj_fit,
        "registered_mound_d_latlon": [round(float(md_lat), 6), round(float(md_lon), 6)],
        "source_audit_findings": {
            "printed_caption_coord_latlon": [round(cap_lat, 6), round(cap_lon, 6)],
            "caption_offset_from_drawn_mound_d_m": round(caption_offset_m, 1),
            "printed_scale_bar_label_m": 200.0,
            "printed_scale_bar_true_ground_m": round(printed_bar_true_m, 1),
            "scale_bar_discrepancy_factor": round(printed_bar_true_m / 200.0, 2),
            "note": "Independent OSM and Esri road-grid distance between Road 8 and Road 3 (285.3 m) confirms the true figure scale (1.219 m/px); the printed 200 m bar spans 418 px (~510 m on ground) and the printed latitude 27d43'44\"N sits 455 m north of the drawn Mound D rectangle (27d43'29\"N).",
        },
        "uncertainty_buffer_m": {"mound_d": 15.0, "central_west_core": 25.0, "site_50ha_envelope": 50.0},
    }

    return build_site_package(
        site_id="lakhanjo_daro",
        site_name="Lakhanjo-Daro (Sukkur SITE)",
        utm_epsg=32642,
        proj=proj42,
        frame_utm=frame_utm,
        wc_path=RAW_NEW / "worldcover/ESA_WorldCover_2021_lakhanjo_daro_N27E066.tif",
        dem_path=ROOT / "data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N27_00_E068_00_DEM.tif",
        dem_tile_lat_lon=(27, 68),
        layer1_defs=layer1_defs,
        layer4_defs=layer4_defs,
        registration_info=reg_info,
        bg_mosaic_path=lj_png_p,
        bg_mosaic_meta=lj_meta,
        out_geojson=EXP_DIR / "lakhanjo-daro-windows-v1.geojson",
        fig_path=FIG_DIR / "lakhanjo_daro_4layer_map.png",
    )


def build_rupnagar() -> tuple[dict, list[dict]]:
    proj43 = TMProjection(75.0)
    rpr_meta_p = RAW_NEW / "mosaics/rupnagar_mound_z18_x186791-186800_y107329-107338.json"
    rpr_png_p = RAW_NEW / "mosaics/rupnagar_mound_z18_x186791-186800_y107329-107338.png"
    rpr_meta = json.loads(rpr_meta_p.read_text(encoding="utf-8"))

    def z18_to_utm(mx: float, my: float) -> tuple[float, float]:
        lon, lat = mosaic_px_to_lonlat(mx, my, rpr_meta)
        e, n = proj43.forward(lon, lat)
        return float(e), float(n)

    # Published (0, 0) metric datum: NE corner of pavement of Nalagarh Kothi (Prabhakar, IAR 2011-12, p. 73)
    datum_z18 = (1007.0, 1046.0)
    datum_lon, datum_lat = mosaic_px_to_lonlat(datum_z18[0], datum_z18[1], rpr_meta)
    de, dn = proj43.forward(datum_lon, datum_lat)
    de, dn = float(de), float(dn)

    # Audit printed IAR 2011-12 coordinate (30.9664, 76.5331) offset from actual Nalagarh Kothi mound
    iar_e, iar_n = proj43.forward(76.5331, 30.9664)
    gazetteer_offset_m = float(math.hypot(de - float(iar_e), dn - float(iar_n)))

    # Sensitivity of farthest trench (N20W190, r=191.05 m) under +-3 deg grid azimuth uncertainty
    max_trench_r_m = math.hypot(20.0, 190.0)
    rot_3deg_disp_m = 2.0 * max_trench_r_m * math.sin(math.radians(1.5))

    def trench_box_envelope(coords_ne: list[tuple[float, float]]) -> list[tuple[float, float]]:
        # Bounding rectangle of 5m x 5m trenches whose NW pegs are at (de + e_off, dn + n_off)
        es = [e for _, e in coords_ne]
        ns = [n for n, _ in coords_ne]
        e_min, e_max = de + min(es), de + max(es) + 5.0
        n_min, n_max = dn + min(ns) - 5.0, dn + max(ns)
        return [(e_min, n_min), (e_max, n_min), (e_max, n_max), (e_min, n_max)]

    ne_trenches = [(45, 120), (45, 125), (45, 130), (45, 135), (45, 140), (45, 145), (50, 140), (50, 145)]
    gully_trenches = [(5, 20), (5, 25), (5, 30)]
    ssw_trenches = [(-65, -20), (-65, -10), (-65, 0), (-70, -25), (-70, -15), (-70, -5)]
    west_trenches = [(-20, -175), (-20, -170), (20, -190), (20, -185)]

    # Layer 1:
    # - 4 exact 2011-12 datum-projected trench zones (IAR 2011-12, p. 73)
    # - Protected Northern/Central/Western ASI Mound (visible on z18 + OSM Ropar Harappan Site + DEM >283 m)
    # - Southern Mound beneath dense old Rupnagar town (IAR 2011-12 p. 72 + DEM crest 293.83 m at 30.9697N, 76.5264E)
    layer1_defs = [
        {
            "id": "RPR-L1-TRENCHES-2011-NE",
            "name": "2011-12 Northeastern Slope Harappan/Bara Trenches (N45E120-N50E145)",
            "sub_type": "datum_grid_trench_cluster",
            "evidence_grade": "datum_grid_trench",
            "source_citation": "Prabhakar, Indian Archaeology 2011-2012 - A Review, pp. 73-74 (8 trenches of 5x5 m from Nalagarh Kothi NE pavement datum)",
            "positional_uncertainty_m": 6.0,
            "ring_utm": trench_box_envelope(ne_trenches),
            "include_in_site_union": True,
            "is_harappan_context": True,
            "notes": "Exposed Harappan/Bara habitation at 0.50 m depth over a 0.22 m NW-SE mud platform and Sutlej silt, plus a lakhauri brick kiln.",
        },
        {
            "id": "RPR-L1-TRENCHES-2011-GULLY",
            "name": "2011-12 Central-East Rain Gully Trenches (N5E20-N5E30)",
            "sub_type": "datum_grid_trench_cluster",
            "evidence_grade": "datum_grid_trench",
            "source_citation": "Prabhakar, Indian Archaeology 2011-2012 - A Review, pp. 73, 76 (3 trenches of 5x5 m)",
            "positional_uncertainty_m": 6.0,
            "ring_utm": trench_box_envelope(gully_trenches),
            "include_in_site_union": True,
            "is_harappan_context": False,
            "notes": "Dug to 6.3 m depth in the N-S rain gully east of Nalagarh Kothi; exposed Gupta and Post-Gupta brick structures.",
        },
        {
            "id": "RPR-L1-TRENCHES-2011-SSW",
            "name": "2011-12 South-Southwest Slope Trenches (S65W20-S70W5)",
            "sub_type": "datum_grid_trench_cluster",
            "evidence_grade": "datum_grid_trench",
            "source_citation": "Prabhakar, Indian Archaeology 2011-2012 - A Review, pp. 73, 75-76 (6 trenches of 5x5 m)",
            "positional_uncertainty_m": 6.0,
            "ring_utm": trench_box_envelope(ssw_trenches),
            "include_in_site_union": True,
            "is_harappan_context": False,
            "notes": "Dug to 6.65 m in S70W5; Medieval hearths and eroded deposits overlying stray Painted Grey Ware at base.",
        },
        {
            "id": "RPR-L1-TRENCHES-2011-WEST",
            "name": "2011-12 Westernmost Cemetery-Mound Trenches (S20W175-N20W185)",
            "sub_type": "datum_grid_trench_cluster",
            "evidence_grade": "datum_grid_trench",
            "source_citation": "Prabhakar, Indian Archaeology 2011-2012 - A Review, pp. 73, 76 (4 trenches of 5x5 m)",
            "positional_uncertainty_m": 6.0,
            "ring_utm": trench_box_envelope(west_trenches),
            "include_in_site_union": True,
            "is_harappan_context": True,
            "notes": "Probed western mound where Y. D. Sharma exposed the Harappan Cemetery; PGW layers encountered on eastern periphery.",
        },
        {
            "id": "RPR-L1-PROTECTED-MOUND",
            "name": "Protected Ropar ASI Mound Complex (Northern, Nalagarh Kothi & Western Cemetery Mounds)",
            "sub_type": "protected_mound_zone",
            "evidence_grade": "topographic_source_envelope",
            "source_citation": "Prabhakar, IAR 2011-12, p. 72 (~12 ha four-mound complex rising ~21 m); ASI site card LT-S13; OSM Ropar Harappan Site; Esri z18",
            "positional_uncertainty_m": 15.0,
            "ring_utm": [
                z18_to_utm(570, 910),
                z18_to_utm(880, 880),
                z18_to_utm(1260, 900),
                z18_to_utm(1475, 970),
                z18_to_utm(1435, 1110),
                z18_to_utm(1220, 1210),
                z18_to_utm(920, 1225),
                z18_to_utm(770, 1150),
                z18_to_utm(585, 1115),
            ],
            "include_in_site_union": True,
            "is_harappan_context": True,
            "notes": "Unbuilt ASI protected reserve containing Nalagarh Kothi (293.1 m MSL), the 2011-12 trenches and western cemetery rise.",
        },
        {
            "id": "RPR-L1-SOUTHERN-MOUND-TOWN",
            "name": "Southern Mound Concealed beneath Old Rupnagar Town (293.8 m MSL Crest)",
            "sub_type": "concealed_mound_sector",
            "evidence_grade": "topographic_source_envelope",
            "source_citation": "Prabhakar, IAR 2011-12, p. 72 ('the southern one is densely occupied and partly excavated by Y. D. Sharma', total site ~12 ha); Copernicus GLO-30 DEM (>284 m MSL peak 293.83 m at 30.9697N, 76.5264E)",
            "positional_uncertainty_m": 25.0,
            "ring_utm": [
                z18_to_utm(770, 1155),
                z18_to_utm(920, 1225),
                z18_to_utm(1220, 1210),
                z18_to_utm(1435, 1110),
                z18_to_utm(1640, 1125),
                z18_to_utm(1685, 1340),
                z18_to_utm(1480, 1520),
                z18_to_utm(1140, 1560),
                z18_to_utm(890, 1440),
                z18_to_utm(740, 1290),
            ],
            "include_in_site_union": True,
            "is_harappan_context": True,
            "notes": "Elevated topographic mound mass directly beneath dense old Rupnagar streets; unexcavated Y. D. Sharma RPR-1/RPR-2 trench outlines are not fabricated.",
        },
    ]

    layer4_defs = [
        {
            "id": "RPR-W01",
            "name": "Nehru Stadium Bare Southern Playfield (North Foot of Mound)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, 50 m north of 2011-12 Harappan/Bara trenches",
            "ring_utm": [z18_to_utm(935, 745), z18_to_utm(1195, 745), z18_to_utm(1195, 885), z18_to_utm(935, 885)],
            "notes": "Treeless flat bare-earth field directly abutting the northern mound foot near trenches N45E120-N50E145.",
        },
        {
            "id": "RPR-W02",
            "name": "Nehru Stadium Athletics Track and Cricket Turf",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021",
            "ring_utm": [z18_to_utm(755, 515), z18_to_utm(1195, 515), z18_to_utm(1195, 740), z18_to_utm(755, 740)],
            "notes": "Open municipal turf grounds immediately north of the Harappan mound testing northern settlement or terrace limits.",
        },
        {
            "id": "RPR-W03",
            "name": "Nalagarh Kothi Plateau Open Lawns (Protected Mound Crest)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, IAR 2011-12",
            "ring_utm": [z18_to_utm(870, 990), z18_to_utm(1170, 990), z18_to_utm(1170, 1145), z18_to_utm(870, 1145)],
            "notes": "High-elevation (+19 m) open grass clearing on the ASI mound crest between Nalagarh Kothi and the eastern pavilion; suitable for non-invasive GPR/ERT to trace sub-Historical Harappan levels.",
        },
        {
            "id": "RPR-W04",
            "name": "Government College and ASI Museum Open Grounds (NW of Cemetery Mound)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021, ANCHOR_ROPAR.html",
            "ring_utm": [z18_to_utm(560, 565), z18_to_utm(715, 565), z18_to_utm(715, 795), z18_to_utm(560, 795)],
            "notes": "Open institutional courtyard and lawn immediately north of the ASI Museum and western Harappan Cemetery mound.",
        },
        {
            "id": "RPR-W05",
            "name": "Protected Mound Northern Wooded Flank (Canopy Control)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021 (class 10 Tree cover)",
            "ring_utm": [z18_to_utm(620, 895), z18_to_utm(1320, 905), z18_to_utm(1320, 985), z18_to_utm(620, 980)],
            "notes": "Heavily forested northern slope of the protected mound; demonstrates automatic Rule D2 canopy soft-demotion.",
        },
        {
            "id": "RPR-W06",
            "name": "Southern Mound Old-Town Contact Street Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Esri z18, OpenStreetMap Rupnagar streets, IAR 2011-12 p. 72",
            "line_utm": [z18_to_utm(610, 1110), z18_to_utm(820, 1190), z18_to_utm(1160, 1235), z18_to_utm(1470, 1115), z18_to_utm(1720, 1080)],
            "half_width_m": 10.0,
            "notes": "Public street line skirting the contact between the protected mound and the densely built 293.8 m southern mound.",
        },
        {
            "id": "RPR-W07",
            "name": "College Road Western Cemetery Margin Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Esri z18, OpenStreetMap Rupnagar streets",
            "line_utm": [z18_to_utm(520, 520), z18_to_utm(555, 860), z18_to_utm(585, 1150), z18_to_utm(630, 1480)],
            "half_width_m": 10.0,
            "notes": "Main north-south municipal street immediately west of the Harappan Cemetery mound and ASI Museum.",
        },
        {
            "id": "RPR-W08",
            "name": "Old Rupnagar Southern Mound Crest Bazaar Street Corridor",
            "window_type": "rescue_corridor",
            "source_basis": "Esri z18, OpenStreetMap Rupnagar streets, Copernicus GLO-30 crest",
            "line_utm": [z18_to_utm(840, 1340), z18_to_utm(1180, 1380), z18_to_utm(1460, 1330), z18_to_utm(1760, 1290)],
            "half_width_m": 10.0,
            "notes": "Central arterial crossing the concealed 293.8 m southern mound beneath old Rupnagar; key utility-cut watching corridor to test whether the post-Harappan hiatus is town-wide.",
        },
        {
            "id": "RPR-W09",
            "name": "Dense Old Rupnagar Bazaar Block on Southern Mound (Built-Up Control)",
            "window_type": "geophysical_open_parcel",
            "source_basis": "Esri z18, ESA WorldCover 2021 (class 50 Built-up)",
            "ring_utm": [z18_to_utm(1140, 1230), z18_to_utm(1560, 1230), z18_to_utm(1560, 1480), z18_to_utm(1140, 1480)],
            "notes": "Continuous dense masonry housing over the southern mound crest; demonstrates Rule D1 (>70% built-up) hard demotion.",
        },
    ]

    # UTM frame covering 1.15 km x 1.05 km around Ropar mound & old town
    sw_e, sw_n = z18_to_utm(320, 1850)
    ne_e, ne_n = z18_to_utm(2150, 320)
    frame_utm = (math.floor(sw_e / 10.0) * 10.0, math.floor(sw_n / 10.0) * 10.0,
                 math.ceil(ne_e / 10.0) * 10.0, math.ceil(ne_n / 10.0) * 10.0)

    reg_info = {
        "primary_plan": "Prabhakar, Indian Archaeology 2011-2012 - A Review, pp. 72-76 (21 trenches on 5x5 m Nalagarh Kothi datum grid)",
        "method": "Exact metric datum projection from NE corner of Nalagarh Kothi pavement (Esri z18 pixel 1007, 1046) in UTM 43N",
        "datum_nalagarh_kothi_ne_latlon": [round(float(datum_lat), 6), round(float(datum_lon), 6)],
        "datum_nalagarh_kothi_ne_utm43n": [round(de, 2), round(dn, 2)],
        "trench_count_projected": 21,
        "datum_uncertainty_m": 6.0,
        "rotation_3deg_max_displacement_m": round(rot_3deg_disp_m, 2),
        "source_audit_findings": {
            "printed_iar2011_12_coord_latlon": [30.9664, 76.5331],
            "offset_from_physical_mound_m": round(gazetteer_offset_m, 1),
            "asi_card_lt_s13_note": "ASI Chandigarh Circle site card (LT-S13) prints latitude 30d28'N, inconsistent with Rupnagar (~30d58'N); rejected as a coordinate.",
            "note": "All four 2011-12 trench clusters align directly with physical mound topography (N-S rain gully at E20-E30, NE slope at N45E120-N50E145, SSW slope above houses at S65-S70, western mound at W170-W190).",
        },
        "uncertainty_buffer_m": {"trenches_2011": 6.0, "protected_mound": 15.0, "southern_mound_town": 25.0},
    }

    return build_site_package(
        site_id="rupnagar",
        site_name="Rupnagar (Ropar)",
        utm_epsg=32643,
        proj=proj43,
        frame_utm=frame_utm,
        wc_path=RAW_NEW / "worldcover/ESA_WorldCover_2021_rupnagar_N30E075.tif",
        dem_path=ROOT / "data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N30_00_E076_00_DEM.tif",
        dem_tile_lat_lon=(30, 76),
        layer1_defs=layer1_defs,
        layer4_defs=layer4_defs,
        registration_info=reg_info,
        bg_mosaic_path=rpr_png_p,
        bg_mosaic_meta=rpr_meta,
        out_geojson=EXP_DIR / "rupnagar-windows-v1.geojson",
        fig_path=FIG_DIR / "rupnagar_4layer_map.png",
    )


def collect_input_hashes() -> list[dict]:
    inputs = [
        "experiments/2026-11-23-living-towns-footprints/PROTOCOL.md",
        "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONTROL_20261012T053309958546Z_B02_WorldCover_N30E072.tif",
        "data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N30_00_E072_00_DEM.tif",
        "data/raw/2026-10-21-town-orientations-verification/astro/dem/30m/Copernicus_DSM_COG_10_N27_00_E068_00_DEM.tif",
        "data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/Copernicus_DSM_COG_10_N30_00_E076_00_DEM.tif",
        "data/raw/2026-10-21-plan-registration/R1-G1/mosaics/harappa_z18_cur_z18_x184123-184135_y107617-107629.json",
        "data/raw/2026-10-21-town-axes/img-A/mosaics/harappa_ov_z16_x46030-46034_y26903-26907.json",
        "data/raw/2026-10-21-town-axes/dating/harappa/kenoyer1991urban.pdf",
        "data/raw/2026-10-21-town-axes/dating/harappa/kenoyer2008urbanism.pdf",
        "data/raw/2026-10-21-town-axes/dating/lakhanjo-daro/biagi2022lakhan.pdf",
        "data/raw/2026-10-11-settlement-prospection/SINDH2022.html",
        "data/raw/2026-10-21-post-catalogue-finds/run1b/sources/iar-2011-12/iar-2011-12.pdf",
        "data/raw/2026-11-23-living-towns-footprints/worldcover/ESA_WorldCover_2021_lakhanjo_daro_N27E066.tif",
        "data/raw/2026-11-23-living-towns-footprints/worldcover/ESA_WorldCover_2021_rupnagar_N30E075.tif",
        "data/raw/2026-11-23-living-towns-footprints/mosaics/lakhanjo_daro_z18_x181199-181210_y110040-110050.json",
        "data/raw/2026-11-23-living-towns-footprints/mosaics/rupnagar_mound_z18_x186791-186800_y107329-107338.json",
        "data/raw/2026-11-23-living-towns-footprints/osm/osm_harappa.json",
        "data/raw/2026-11-23-living-towns-footprints/osm/osm_lakhanjo_daro.json",
        "data/raw/2026-11-23-living-towns-footprints/osm/osm_rupnagar.json",
    ]
    out = []
    for rel in inputs:
        p = ROOT / rel
        out.append(
            {
                "logical_path": rel,
                "physical_path": os.path.realpath(str(p)),
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
        )
    return out


def main():
    print("Building Harappa four-layer footprint...")
    hrp_sum, hrp_wins = build_harappa()
    print(f"  Harappa: L1={hrp_sum['layer_1_union_area_ha']:.2f} ha, Concealed L3={hrp_sum['layer_3_concealed_overlap_ha']:.2f} ha ({hrp_sum['layer_3_concealed_pct_of_l1']:.1f}%), RMSE={hrp_sum['registration']['fit_metrics']['rmse_m']:.2f} m")

    print("Building Lakhanjo-Daro (Sukkur SITE) four-layer footprint...")
    lkd_sum, lkd_wins = build_lakhanjo_daro()
    print(f"  Lakhanjo-Daro: L1={lkd_sum['layer_1_union_area_ha']:.2f} ha, Concealed L3={lkd_sum['layer_3_concealed_overlap_ha']:.2f} ha ({lkd_sum['layer_3_concealed_pct_of_l1']:.1f}%), RMSE={lkd_sum['registration']['fit_metrics']['rmse_m']:.2f} m")

    print("Building Rupnagar (Ropar) four-layer footprint...")
    rpr_sum, rpr_wins = build_rupnagar()
    print(f"  Rupnagar: L1={rpr_sum['layer_1_union_area_ha']:.2f} ha, Concealed L3={rpr_sum['layer_3_concealed_overlap_ha']:.2f} ha ({rpr_sum['layer_3_concealed_pct_of_l1']:.1f}%)")

    all_wins = hrp_wins + lkd_wins + rpr_wins
    csv_path = EXP_DIR / "windows-v1.csv"
    fieldnames = [
        "id", "site_id", "site_name", "name", "window_type",
        "final_tier", "base_tier", "priority_score",
        "score_clearance", "score_topography", "score_proximity",
        "demoted", "demotion_reasons", "recommended_method",
        "area_ha", "corridor_length_m", "center_lat", "center_lon",
        "wc_built_frac", "wc_open_clean_frac", "wc_tree_frac", "wc_water_frac",
        "dem_mean_m", "rel_elev_m", "dist_to_harappan_m", "source_basis",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in all_wins:
            out_r = {k: row.get(k) for k in fieldnames}
            out_r["demotion_reasons"] = ";".join(row["demotion_reasons"])
            w.writerow(out_r)

    summary = {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_path": "experiments/2026-11-23-living-towns-footprints/PROTOCOL.md",
        "protocol_sha256": sha256_file(EXP_DIR / "PROTOCOL.md"),
        "sites": {
            "harappa": hrp_sum,
            "lakhanjo_daro": lkd_sum,
            "rupnagar": rpr_sum,
        },
        "totals": {
            "layer_1_union_area_ha": round(
                hrp_sum["layer_1_union_area_ha"] + lkd_sum["layer_1_union_area_ha"] + rpr_sum["layer_1_union_area_ha"], 3
            ),
            "layer_3_concealed_overlap_ha": round(
                hrp_sum["layer_3_concealed_overlap_ha"] + lkd_sum["layer_3_concealed_overlap_ha"] + rpr_sum["layer_3_concealed_overlap_ha"], 3
            ),
            "layer_4_windows_total": len(all_wins),
            "tier_1_windows": sum(1 for r in all_wins if r["final_tier"] == 1),
            "tier_2_windows": sum(1 for r in all_wins if r["final_tier"] == 2),
            "tier_3_windows": sum(1 for r in all_wins if r["final_tier"] == 3),
            "demoted_windows": sum(1 for r in all_wins if r["demoted"]),
        },
        "input_hashes": collect_input_hashes(),
    }
    sum_path = EXP_DIR / "summary-v1.json"
    sum_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {sum_path} and {csv_path} ({len(all_wins)} windows).")


if __name__ == "__main__":
    main()
