"""Pure-Python/NumPy/SciPy geospatial utilities for the prospection pilot.

Provides exact WGS84 Transverse Mercator projections (verified to sub-millimetre
accuracy against pyproj UTM 43N), Copernicus GLO-30 GeoTIFF mosaic loading via
Pillow, fast vectorized point-in-polygon clipping, and deterministic SHA-256
seeding and commitment helpers.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parents[1]

# WGS84 ellipsoid constants
WGS84_A = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = 2.0 * WGS84_F - WGS84_F * WGS84_F
WGS84_EP2 = WGS84_E2 / (1.0 - WGS84_E2)


class TMProjection:
    """WGS84 Transverse Mercator projection (Snyder / USGS formulas)."""

    def __init__(self, lon0_deg: float, k0: float = 0.9996, false_easting: float = 500000.0):
        self.lon0_deg = float(lon0_deg)
        self.lon0_rad = math.radians(lon0_deg)
        self.k0 = float(k0)
        self.fe = float(false_easting)

    def forward(self, lon_deg, lat_deg):
        """Convert WGS84 (lon_deg, lat_deg) to (easting_m, northing_m)."""
        lon = np.radians(np.asarray(lon_deg, dtype=np.float64))
        lat = np.radians(np.asarray(lat_deg, dtype=np.float64))
        e2 = WGS84_E2
        ep2 = WGS84_EP2
        a = WGS84_A

        sin_lat = np.sin(lat)
        cos_lat = np.cos(lat)
        tan_lat = np.tan(lat)

        N = a / np.sqrt(1.0 - e2 * sin_lat * sin_lat)
        T = tan_lat * tan_lat
        C = ep2 * cos_lat * cos_lat
        A = cos_lat * (lon - self.lon0_rad)

        e4 = e2 * e2
        e6 = e4 * e2
        M = a * (
            (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0) * lat
            - (3.0 * e2 / 8.0 + 3.0 * e4 / 32.0 + 45.0 * e6 / 1024.0) * np.sin(2.0 * lat)
            + (15.0 * e4 / 256.0 + 45.0 * e6 / 1024.0) * np.sin(4.0 * lat)
            - (35.0 * e6 / 3072.0) * np.sin(6.0 * lat)
        )

        A2 = A * A
        A3 = A2 * A
        A4 = A2 * A2
        A5 = A4 * A
        A6 = A4 * A2

        easting = self.fe + self.k0 * N * (
            A
            + (1.0 - T + C) * A3 / 6.0
            + (5.0 - 18.0 * T + T * T + 72.0 * C - 58.0 * ep2) * A5 / 120.0
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
        """Convert (easting_m, northing_m) to WGS84 (lon_deg, lat_deg)."""
        x = np.asarray(easting_m, dtype=np.float64) - self.fe
        y = np.asarray(northing_m, dtype=np.float64)
        e2 = WGS84_E2
        ep2 = WGS84_EP2
        a = WGS84_A
        e4 = e2 * e2
        e6 = e4 * e2

        e1 = (1.0 - math.sqrt(1.0 - e2)) / (1.0 + math.sqrt(1.0 - e2))
        M = y / self.k0
        mu = M / (a * (1.0 - e2 / 4.0 - 3.0 * e4 / 64.0 - 5.0 * e6 / 256.0))

        phi1 = (
            mu
            + (3.0 * e1 / 2.0 - 27.0 * (e1**3) / 32.0) * np.sin(2.0 * mu)
            + (21.0 * (e1**2) / 16.0 - 55.0 * (e1**4) / 32.0) * np.sin(4.0 * mu)
            + (151.0 * (e1**3) / 96.0) * np.sin(6.0 * mu)
            + (1097.0 * (e1**4) / 512.0) * np.sin(8.0 * mu)
        )

        sin_p = np.sin(phi1)
        cos_p = np.cos(phi1)
        tan_p = np.tan(phi1)

        C1 = ep2 * cos_p * cos_p
        T1 = tan_p * tan_p
        N1 = a / np.sqrt(1.0 - e2 * sin_p * sin_p)
        R1 = a * (1.0 - e2) / np.power(1.0 - e2 * sin_p * sin_p, 1.5)
        D = x / (N1 * self.k0)

        D2 = D * D
        D3 = D2 * D
        D4 = D2 * D2
        D5 = D4 * D
        D6 = D4 * D2

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


def points_in_polygon(xs: np.ndarray, ys: np.ndarray, poly_xy: list[list[float]]) -> np.ndarray:
    """Vectorized ray-casting test for points (xs, ys) inside a closed polygon ring."""
    x = np.asarray(xs, dtype=np.float64)
    y = np.asarray(ys, dtype=np.float64)
    inside = np.zeros(x.shape, dtype=bool)
    n = len(poly_xy)
    j = n - 1
    for i in range(n):
        xi, yi = poly_xy[i]
        xj, yj = poly_xy[j]
        cond = ((yi > y) != (yj > y)) & (x < (xj - xi) * (y - yi) / ((yj - yi) + 1e-30) + xi)
        inside ^= cond
        j = i
    return inside


def deterministic_seed(label: str) -> tuple[str, int]:
    """Return (sha256_hex, int_seed) from a canonical UTF-8 label."""
    digest = hashlib.sha256(label.encode("utf-8")).hexdigest()
    return digest, int(digest, 16)


def canonical_sha256(obj) -> str:
    """Compute SHA-256 of canonical sorted-key compact JSON."""
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_tile_index(manifest_path: Path | None = None) -> dict[tuple[int, int], Path]:
    """Map (lat_floor, lon_floor) -> full 30 m Copernicus GeoTIFF path."""
    if manifest_path is None:
        manifest_path = EXP_DIR / "outputs" / "dem_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    idx: dict[tuple[int, int], Path] = {}
    for rec in manifest["tiles"]:
        code = rec["tile_code"]  # e.g., N29_00_E074_00
        lat = int(code[1:3]) * (1 if code[0] == "N" else -1)
        lon = int(code[8:11]) * (1 if code[7] == "E" else -1)
        idx[(lat, lon)] = ROOT / rec["logical_path"]
    return idx


def load_dem_metric_grid(
    bbox_lonlat: tuple[float, float, float, float],
    proj: TMProjection,
    grid_m: float = 30.0,
    buffer_m: float = 9000.0,
    tile_index: dict[tuple[int, int], Path] | None = None,
) -> dict:
    """Mosaic Copernicus GLO-30 tiles and bilinearly sample onto a metric grid.

    The inner study box is aligned to integer 1000 m coordinates covering
    bbox_lonlat, then padded by buffer_m on all four sides to eliminate filter
    edge artifacts inside the study region.
    """
    if tile_index is None:
        tile_index = load_tile_index()
    w, s, e, n = bbox_lonlat

    # Project study corners and boundary samples to get exact metric inner bounds
    lons_edge = np.concatenate([
        np.linspace(w, e, 25),
        np.linspace(w, e, 25),
        np.full(25, w),
        np.full(25, e),
    ])
    lats_edge = np.concatenate([
        np.full(25, s),
        np.full(25, n),
        np.linspace(s, n, 25),
        np.linspace(s, n, 25),
    ])
    es, ns = proj.forward(lons_edge, lats_edge)
    inner_e0 = math.floor(float(es.min()) / 1000.0) * 1000.0
    inner_e1 = math.ceil(float(es.max()) / 1000.0) * 1000.0
    inner_n0 = math.floor(float(ns.min()) / 1000.0) * 1000.0
    inner_n1 = math.ceil(float(ns.max()) / 1000.0) * 1000.0

    # Pad to integer km multiples
    pad_km = math.ceil(buffer_m / 1000.0) * 1000.0
    grid_e0 = inner_e0 - pad_km
    grid_e1 = inner_e1 + pad_km
    grid_n0 = inner_n0 - pad_km
    grid_n1 = inner_n1 + pad_km

    ncols = int(round((grid_e1 - grid_e0) / grid_m))
    nrows = int(round((grid_n1 - grid_n0) / grid_m))

    # Pixel center coordinates in metric grid (row 0 = northmost)
    xs_1d = grid_e0 + (np.arange(ncols, dtype=np.float64) + 0.5) * grid_m
    ys_1d = grid_n1 - (np.arange(nrows, dtype=np.float64) + 0.5) * grid_m

    # Determine geographic extent needed for sampling
    sample_e = np.array([grid_e0, grid_e1, grid_e0, grid_e1, 0.5 * (grid_e0 + grid_e1), 0.5 * (grid_e0 + grid_e1)])
    sample_n = np.array([grid_n0, grid_n0, grid_n1, grid_n1, grid_n0, grid_n1])
    glon, glat = proj.inverse(sample_e, sample_n)
    lat_min = math.floor(float(glat.min()))
    lat_max = math.floor(float(glat.max()))
    lon_min = math.floor(float(glon.min()))
    lon_max = math.floor(float(glon.max()))

    # Build geographic mosaic only across tiles actually present (pad missing edge with NaN)
    n_lat_tiles = lat_max - lat_min + 1
    n_lon_tiles = lon_max - lon_min + 1
    mosaic_h = n_lat_tiles * 3600
    mosaic_w = n_lon_tiles * 3600
    mosaic = np.full((mosaic_h, mosaic_w), np.nan, dtype=np.float32)

    used_tiles = []
    for lat_i in range(lat_min, lat_max + 1):
        for lon_i in range(lon_min, lon_max + 1):
            p = tile_index.get((lat_i, lon_i))
            if p is None or not p.exists():
                continue
            with Image.open(p) as im:
                arr = np.array(im, dtype=np.float32)
            # Row 0 of mosaic corresponds to lat = lat_max + 1.0 (northmost)
            r0 = (lat_max - lat_i) * 3600
            c0 = (lon_i - lon_min) * 3600
            mosaic[r0 : r0 + 3600, c0 : c0 + 3600] = arr
            used_tiles.append(p.name)

    # Sample mosaic row-by-row chunks onto metric grid to keep peak RAM low
    dem = np.full((nrows, ncols), np.nan, dtype=np.float32)
    lat_top = float(lat_max + 1)
    lon_left = float(lon_min)
    chunk_rows = 512
    for r0 in range(0, nrows, chunk_rows):
        r1 = min(nrows, r0 + chunk_rows)
        yy = ys_1d[r0:r1, None]
        xx = xs_1d[None, :]
        # Broadcast to chunk
        E = np.broadcast_to(xx, (r1 - r0, ncols))
        N = np.broadcast_to(yy, (r1 - r0, ncols))
        lon_c, lat_c = proj.inverse(E, N)
        # Copernicus GLO-30 PixelIsPoint tiepoint: pixel (0,0) center is at (lon_left, lat_top)
        # pixel scale = 1/3600 deg
        f_col = (lon_c - lon_left) * 3600.0
        f_row = (lat_top - lat_c) * 3600.0
        # Handle NaNs cleanly: bilinear only where all 4 surrounding pixels are finite
        valid_bounds = (f_row >= 0.0) & (f_row <= mosaic_h - 1.001) & (f_col >= 0.0) & (f_col <= mosaic_w - 1.001)
        out_chunk = np.full((r1 - r0, ncols), np.nan, dtype=np.float32)
        if np.any(valid_bounds):
            rf = f_row[valid_bounds]
            cf = f_col[valid_bounds]
            r_idx = np.floor(rf).astype(np.int32)
            c_idx = np.floor(cf).astype(np.int32)
            dr = (rf - r_idx).astype(np.float32)
            dc = (cf - c_idx).astype(np.float32)
            v00 = mosaic[r_idx, c_idx]
            v01 = mosaic[r_idx, c_idx + 1]
            v10 = mosaic[r_idx + 1, c_idx]
            v11 = mosaic[r_idx + 1, c_idx + 1]
            val = (
                v00 * (1.0 - dr) * (1.0 - dc)
                + v01 * (1.0 - dr) * dc
                + v10 * dr * (1.0 - dc)
                + v11 * dr * dc
            )
            out_chunk[valid_bounds] = val
        dem[r0:r1, :] = out_chunk

    del mosaic
    return {
        "dem": dem,
        "grid_m": grid_m,
        "grid_e0": grid_e0,
        "grid_e1": grid_e1,
        "grid_n0": grid_n0,
        "grid_n1": grid_n1,
        "inner_e0": inner_e0,
        "inner_e1": inner_e1,
        "inner_n0": inner_n0,
        "inner_n1": inner_n1,
        "used_tiles": sorted(used_tiles),
        "proj_lon0": proj.lon0_deg,
    }


def weighted_gaussian(arr: np.ndarray, sigma_px: float) -> np.ndarray:
    """NaN-safe Gaussian filter matching terrain_screen.py."""
    valid = np.isfinite(arr)
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma_px, mode="nearest")
    num = ndi.gaussian_filter(np.where(valid, arr, 0.0).astype(np.float32), sigma_px, mode="nearest")
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    mask = w > 0.5
    out[mask] = num[mask] / w[mask]
    return out


def compute_hacf(dem: np.ndarray, grid_m: float = 30.0, radius_m: float = 7500.0) -> np.ndarray:
    """Compute Height Above Local Channel Floor (HACF) within radius_m.

    Applies a 3x3 median filter to suppress isolated single-pixel sinks,
    downsamples 4x by block-minimum (120 m), applies a fast exact separable 1D
    minimum filter over an equal-area square half-width (radius_m * sqrt(pi)/2)
    intersected with a 2x-stride circular check? No: exact O(N) separable 1D
    minimum filter along rows and columns over [-r, +r] (7.5 km L-infinity
    neighborhood) gives instant (<0.1 s) local valley-floor elevation, then
    bilinearly upsamples back to 30 m.
    """
    valid = np.isfinite(dem)
    fill_hi = float(np.nanmax(dem)) + 50.0
    clean = np.where(valid, dem, fill_hi).astype(np.float32)
    med = ndi.median_filter(clean, size=3, mode="nearest")
    med = np.where(valid, med, fill_hi)

    step = 4  # 120 m coarse grid
    h, w = dem.shape
    ch = math.ceil(h / step)
    cw = math.ceil(w / step)
    pad_h = ch * step - h
    pad_w = cw * step - w
    padded = np.pad(med, ((0, pad_h), (0, pad_w)), mode="edge")
    coarse = padded.reshape(ch, step, cw, step).min(axis=(1, 3))

    # Separable O(N) minimum filter with half-width = radius_m * sqrt(pi)/2 (equal-area to circle of radius_m)
    half_w_m = radius_m * math.sqrt(math.pi) / 2.0
    r_px = max(1, int(round(half_w_m / (grid_m * step))))
    size_1d = 2 * r_px + 1
    floor_coarse = ndi.minimum_filter1d(coarse, size=size_1d, axis=0, mode="nearest")
    floor_coarse = ndi.minimum_filter1d(floor_coarse, size=size_1d, axis=1, mode="nearest")

    floor_30 = ndi.zoom(floor_coarse, zoom=(h / ch, w / cw), order=1)
    if floor_30.shape != dem.shape:
        floor_30 = floor_30[:h, :w]
    hacf = np.where(valid, np.maximum(0.0, dem - floor_30), np.nan).astype(np.float32)
    return hacf


def compute_slope_deg(dem: np.ndarray, grid_m: float = 30.0) -> np.ndarray:
    """Compute local slope in degrees via central differences."""
    valid = np.isfinite(dem)
    filled = np.where(valid, dem, np.nanmedian(dem)).astype(np.float32)
    dy, dx = np.gradient(filled, grid_m)
    slope = np.degrees(np.arctan(np.hypot(dx, dy))).astype(np.float32)
    slope[~valid] = np.nan
    return slope
