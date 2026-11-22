"""Analysis B (Issue #12): Multi-scale micro-relief calibration and blind anomaly screening.

Calibrates a Copernicus DEM GLO-30 multi-scale TPI and compact-mound prominence
detector on 12 documented archaeological coordinate records (11 localities) vs.
200 landform-matched random negative 1 km^2 control cells across P01-P09.
Cross-checks anomalies inside held Sentinel-2 + ESA WorldCover 2021 blocks
(B01 Ganweriwala, B02 Harappa, B04 Kalibangan), and produces a blind-testable
GeoJSON + CSV candidate and negative-control packet for P01-P02 and P03-P05.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as ndi
from scipy.stats import mannwhitneyu

from geo_utils import (
    EXP_DIR,
    ROOT,
    TMProjection,
    canonical_sha256,
    deterministic_seed,
    load_dem_metric_grid,
    load_tile_index,
    points_in_polygon,
    weighted_gaussian,
)

OUT_DIR = EXP_DIR / "outputs"
FIG_DIR = EXP_DIR / "figures"

KNOWN_SITES = [
    {"id": "ganweriwala_doam", "name": "Ganweriwala (DOAM)", "corridor": "P01_P02", "regions": ["P01", "P02"], "lat": 28.598889, "lon": 71.150000, "source": "DOAM Pakistan inventory (SPC01)"},
    {"id": "ganweriwala_gulzar", "name": "Ganweriwala (Gulzar/Wikidata)", "corridor": "P01_P02", "regions": ["P01", "P02"], "lat": 28.500000, "lon": 71.066667, "source": "Gulzar 2018 / Wikidata Q3095220 (SPC02)"},
    {"id": "agroha_mound", "name": "Agroha Mound", "corridor": "P03_P05_P07", "regions": ["P03"], "lat": 29.333083, "lon": 75.620633, "source": "Wikidata Q4694244 (Green et al. 2019)"},
    {"id": "banawali", "name": "Banawali", "corridor": "P03_P05_P07", "regions": ["P03"], "lat": 29.598316, "lon": 75.392133, "source": "Wikidata Q59635614 (sites-located-v1.json)"},
    {"id": "bhirrana", "name": "Bhirrana", "corridor": "P03_P05_P07", "regions": ["P03"], "lat": 29.554167, "lon": 75.565278, "source": "Wikidata Q4901824 (sites-located-v1.json)"},
    {"id": "kunal", "name": "Kunal", "corridor": "P03_P05_P07", "regions": ["P03"], "lat": 29.500000, "lon": 75.683333, "source": "Wikidata Q6444146 (sites-located-v1.json)"},
    {"id": "rakhigarhi", "name": "Rakhigarhi", "corridor": "P03_P05_P07", "regions": ["P07"], "lat": 29.293733, "lon": 76.114683, "source": "Wikidata Q59633503 (sites-located-v1.json)"},
    {"id": "kalibangan", "name": "Kalibangan", "corridor": "P06", "regions": ["P06"], "lat": 29.473889, "lon": 74.129722, "source": "Wikidata Q1722226 (sites-located-v1.json)"},
    {"id": "sothi", "name": "Sothi", "corridor": "P06", "regions": ["P06"], "lat": 29.125500, "lon": 74.726400, "source": "Wikidata Q48728244"},
    {"id": "karanpura", "name": "Karanpura", "corridor": "P06", "regions": ["P06"], "lat": 29.108056, "lon": 75.097222, "source": "ASI IAR 2013-14 (sites-located-v1.json)"},
    {"id": "harappa", "name": "Harappa", "corridor": "P08_P09", "regions": ["P08"], "lat": 30.633333, "lon": 72.866667, "source": "Wikidata Q185562 / Uesugi 2010"},
    {"id": "tulamba", "name": "Tulamba", "corridor": "P08_P09", "regions": ["P08", "P09"], "lat": 30.525486, "lon": 72.239767, "source": "Wikidata Q7851908"},
]

DEMOTION_RULES = {
    "P01": "Demote an excess-candidate hypothesis if adequately precise equal-effort blind checks show no excess of phase-supported archaeology over negative controls; reclassify individual natural dune, soil or later-period mounds.",
    "P02": "Demote an expanded occupation-footprint prediction where adequate margin tests establish natural deposits or deposits of another period.",
    "P03": "Demote the prediction that archaeology concentrates at mapped or elevated features if precise blind checks show no phase-supported excess; reclassify natural relief or later villages.",
    "P04": "Reject the archaeological interpretation of a tested feature when adequate observation supports a natural pond or dune; demote only the Indus attribution if archaeology belongs to another period.",
    "P05": "Demote a mound-history prediction if dated feature sequences support a recent embankment or earthwork, or if adequately precise blind checks show no candidate excess.",
}


def load_orengo_aoi() -> list[list[float]]:
    p = ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_ORENGO_SOURCE_AOI.geojson"
    g = json.loads(p.read_text(encoding="utf-8"))
    return g["features"][0]["geometry"]["coordinates"][0]


def annulus_prominence(dem: np.ndarray, r_peak: int, c_peak: int, area_ha: float, grid_m: float = 30.0) -> float:
    r_eq = math.sqrt(max(area_ha, 0.09) * 10000.0 / math.pi)
    r_in = max(180.0, r_eq + 90.0)
    r_out = r_in + 300.0
    k = int(math.ceil(r_out / grid_m))
    h, w = dem.shape
    r0 = max(0, r_peak - k)
    r1 = min(h, r_peak + k + 1)
    c0 = max(0, c_peak - k)
    c1 = min(w, c_peak + k + 1)
    rr, cc = np.indices((r1 - r0, c1 - c0))
    dist = np.hypot(rr + r0 - r_peak, cc + c0 - c_peak) * grid_m
    ring = (dist >= r_in) & (dist <= r_out)
    vals = dem[r0:r1, c0:c1][ring]
    vals = vals[np.isfinite(vals)]
    if vals.size < 10 or not np.isfinite(dem[r_peak, c_peak]):
        return float("nan")
    return float(dem[r_peak, c_peak] - np.median(vals))


def extract_components(
    dem: np.ndarray,
    tpi150: np.ndarray,
    tpi300: np.ndarray,
    tpi600: np.ndarray,
    tpimax: np.ndarray,
    tpi5k: np.ndarray,
    grid_meta: dict,
    proj: TMProjection,
    corridor_id: str,
    subregions: dict[str, tuple[float, float, float, float]],
    clip_poly: list[list[float]] | None = None,
) -> tuple[list[dict], np.ndarray]:
    """Extract compact micro-relief connected components from TPI_300 > 1.0 m."""
    grid_m = grid_meta["grid_m"]
    e0 = grid_meta["grid_e0"]
    n1 = grid_meta["grid_n1"]
    struct = np.ones((3, 3), dtype=np.uint8)

    hi_mask = np.isfinite(tpi300) & (tpi300 > 1.0)
    labels, n_comp = ndi.label(hi_mask, structure=struct)
    lo_mask = np.isfinite(tpi300) & (tpi300 > 0.5)
    lo_labels, _ = ndi.label(lo_mask, structure=struct)
    lo_counts = np.bincount(lo_labels.ravel())

    slices = ndi.find_objects(labels)
    compact_mask = np.zeros(dem.shape, dtype=bool)
    comps = []
    min_px = int(math.ceil(0.5 * 10000.0 / (grid_m * grid_m)))   # 6 px = 0.54 ha
    max_px = int(math.floor(40.0 * 10000.0 / (grid_m * grid_m)))  # 444 px = 39.96 ha

    for lab, slc in enumerate(slices, start=1):
        if slc is None:
            continue
        sub_l = labels[slc] == lab
        cnt = int(sub_l.sum())
        if cnt < min_px or cnt > max_px:
            continue

        r_off = slc[0].start
        c_off = slc[1].start
        rr, cc = np.where(sub_l)
        rr_g = rr + r_off
        cc_g = cc + c_off

        t300_vals = tpi300[rr_g, cc_g]
        best = int(np.argmax(t300_vals))
        rp = int(rr_g[best])
        cp = int(cc_g[best])

        pe = e0 + (cp + 0.5) * grid_m
        pn = n1 - (rp + 0.5) * grid_m
        # Check inner box first
        if not (grid_meta["inner_e0"] <= pe <= grid_meta["inner_e1"] and grid_meta["inner_n0"] <= pn <= grid_meta["inner_n1"]):
            continue
        plon, plat = proj.inverse(pe, pn)
        plon = float(plon)
        plat = float(plat)

        regs = [sr for sr, (sw, ss, se, sn) in subregions.items() if sw <= plon <= se and ss <= plat <= sn]
        if not regs:
            continue
        if clip_poly is not None:
            if not bool(points_in_polygon(np.array([plon]), np.array([plat]), clip_poly)[0]):
                continue

        area_ha = cnt * (grid_m * grid_m) / 10000.0
        # Axis ratio from pixel coordinate covariance (adding 1/12 pixel variance for stability)
        dr = rr.astype(np.float64) - rr.mean()
        dc = cc.astype(np.float64) - cc.mean()
        cov_rr = float(np.mean(dr * dr)) + 1.0 / 12.0
        cov_cc = float(np.mean(dc * dc)) + 1.0 / 12.0
        cov_rc = float(np.mean(dr * dc))
        tr = cov_rr + cov_cc
        det = max(0.0, cov_rr * cov_cc - cov_rc * cov_rc)
        disc = math.sqrt(max(0.0, tr * tr / 4.0 - det))
        lam1 = max(1e-6, tr / 2.0 + disc)
        lam2 = max(1e-6, tr / 2.0 - disc)
        axis_ratio = math.sqrt(lam1 / lam2)

        # Exposed pixel-edge perimeter (4-connected boundary edges)
        padded = np.pad(sub_l, 1, mode="constant", constant_values=False)
        edges = (
            int(np.sum(padded[1:-1, 1:-1] & ~padded[:-2, 1:-1]))
            + int(np.sum(padded[1:-1, 1:-1] & ~padded[2:, 1:-1]))
            + int(np.sum(padded[1:-1, 1:-1] & ~padded[1:-1, :-2]))
            + int(np.sum(padded[1:-1, 1:-1] & ~padded[1:-1, 2:]))
        )
        perim_m = edges * grid_m
        compactness = min(1.0, (4.0 * math.pi * cnt * grid_m * grid_m) / max(perim_m * perim_m, 1.0))

        lo_lab = int(lo_labels[rp, cp])
        lo_cnt = int(lo_counts[lo_lab]) if lo_lab > 0 else cnt
        expansion_ratio = lo_cnt / max(cnt, 1)

        prom = annulus_prominence(dem, rp, cp, area_ha, grid_m)
        if not math.isfinite(prom):
            continue

        passes_compact = (
            (0.5 <= area_ha <= 40.0)
            and (axis_ratio <= 3.5)
            and (compactness >= 0.15)
            and (expansion_ratio <= 4.5)
            and (prom >= 2.5)
        )
        if passes_compact:
            compact_mask[rr_g, cc_g] = True

        rank_score = prom * math.sqrt(compactness) / math.sqrt(axis_ratio) if prom > 0 else 0.0
        size_class = "small_0.5_5ha" if area_ha < 5.0 else ("medium_5_20ha" if area_ha < 20.0 else "large_20_40ha")

        comps.append({
            "comp_id": f"{corridor_id}-C{lab:06d}",
            "corridor": corridor_id,
            "regions": regs,
            "lon": round(plon, 6),
            "lat": round(plat, 6),
            "easting_m": round(pe, 1),
            "northing_m": round(pn, 1),
            "r_peak": rp,
            "c_peak": cp,
            "area_ha": round(area_ha, 2),
            "size_class": size_class,
            "peak_elev_m": round(float(dem[rp, cp]), 2),
            "peak_tpi150_m": round(float(tpi150[rp, cp]), 3),
            "peak_tpi300_m": round(float(tpi300[rp, cp]), 3),
            "peak_tpi600_m": round(float(tpi600[rp, cp]), 3),
            "peak_tpimax_m": round(float(tpimax[rp, cp]), 3),
            "tpi_5km_m": round(float(tpi5k[rp, cp]), 3) if np.isfinite(tpi5k[rp, cp]) else None,
            "annulus_prominence_m": round(prom, 3),
            "axis_ratio": round(axis_ratio, 3),
            "compactness": round(compactness, 3),
            "low_support_expansion_ratio": round(expansion_ratio, 3),
            "passes_compact_filter": bool(passes_compact),
            "geometric_rank_score": round(rank_score, 3),
        })

    return comps, compact_mask


def sample_disk_metrics(
    dem: np.ndarray,
    tpi150: np.ndarray,
    tpi300: np.ndarray,
    tpi600: np.ndarray,
    tpimax: np.ndarray,
    tpi5k: np.ndarray,
    compact_mask: np.ndarray,
    grid_meta: dict,
    e_center: float,
    n_center: float,
    radius_m: float = 500.0,
) -> dict:
    grid_m = grid_meta["grid_m"]
    rc = int(round((grid_meta["grid_n1"] - n_center) / grid_m - 0.5))
    cc = int(round((e_center - grid_meta["grid_e0"]) / grid_m - 0.5))
    k = int(math.ceil(radius_m / grid_m))
    h, w = dem.shape
    r0 = max(0, rc - k)
    r1 = min(h, rc + k + 1)
    c0 = max(0, cc - k)
    c1 = min(w, cc + k + 1)
    rr, ccol = np.indices((r1 - r0, c1 - c0))
    dist = np.hypot(rr + r0 - rc, ccol + c0 - cc) * grid_m
    disk = dist <= radius_m

    sub300 = tpi300[r0:r1, c0:c1]
    valid = disk & np.isfinite(sub300)
    if not np.any(valid):
        return {"valid": False}

    masked300 = np.where(valid, sub300, -1e9)
    flat_idx = int(np.argmax(masked300))
    dr, dc = divmod(flat_idx, sub300.shape[1])
    rp = r0 + dr
    cp = c0 + dc
    offset_m = float(math.hypot(rp - rc, cp - cc) * grid_m)

    prom = annulus_prominence(dem, rp, cp, area_ha=3.0, grid_m=grid_m)
    has_compact = bool(np.any(compact_mask[r0:r1, c0:c1][valid]))

    pt_tpi300 = float(tpi300[rc, cc]) if (0 <= rc < h and 0 <= cc < w and np.isfinite(tpi300[rc, cc])) else float("nan")
    pt_tpimax = float(tpimax[rc, cc]) if (0 <= rc < h and 0 <= cc < w and np.isfinite(tpimax[rc, cc])) else float("nan")

    return {
        "valid": True,
        "point_tpi300_m": round(pt_tpi300, 3) if math.isfinite(pt_tpi300) else None,
        "point_tpimax_m": round(pt_tpimax, 3) if math.isfinite(pt_tpimax) else None,
        "disk500_max_tpi150_m": round(float(np.nanmax(tpi150[r0:r1, c0:c1][valid])), 3),
        "disk500_max_tpi300_m": round(float(tpi300[rp, cp]), 3),
        "disk500_max_tpi600_m": round(float(np.nanmax(tpi600[r0:r1, c0:c1][valid])), 3),
        "disk500_max_tpimax_m": round(float(np.nanmax(tpimax[r0:r1, c0:c1][valid])), 3),
        "disk500_peak_prominence_m": round(prom, 3) if math.isfinite(prom) else None,
        "disk500_peak_offset_m": round(offset_m, 1),
        "disk500_has_compact_mound": has_compact,
        "center_tpi5km_m": round(float(tpi5k[rc, cc]), 3) if (0 <= rc < h and 0 <= cc < w and np.isfinite(tpi5k[rc, cc])) else None,
    }


def cross_check_held_worldcover() -> list[dict]:
    """Quantify built-up/cropland/bare composition of DEM anomalies inside held B01/B02/B04."""
    raw_dir = ROOT / "data/raw/2026-10-12-satellite-prospection"
    blocks = [
        ("B01", "Ganweriwala surroundings (P01-P02)", "SPATIAL_CONTROL_20261012T053309958546Z_B01_derived.npz", "processed-v1/B01.npz"),
        ("B02", "Harappa alluvial plain (P08)", "SPATIAL_CONTROL_20261012T053309958546Z_B02_derived.npz", "processed-v1/B02.npz"),
        ("B04", "Kalibangan-Pilibanga transect (P06)", "SPATIAL_CONTROL_20261012T053309958546Z_B04_derived.npz", "processed-v1/B04.npz"),
    ]
    out = []
    struct = np.ones((3, 3), dtype=np.uint8)
    for bid, label, ctrl_rel, proc_rel in blocks:
        cz = np.load(raw_dir / ctrl_rel)
        pz = np.load(raw_dir / proc_rel)
        res = cz["residual"]
        built = cz["WorldCover_fraction_built"]
        crop = cz["WorldCover_fraction_cropland"]
        water = cz["WorldCover_fraction_water"]
        ndvi_10m = pz["ndvi"]
        # Downsample 10 m NDVI to 30 m grid approximately via zoom
        ndvi_30m = ndi.zoom(np.nan_to_num(ndvi_10m, nan=0.0), (res.shape[0] / ndvi_10m.shape[0], res.shape[1] / ndvi_10m.shape[1]), order=1)

        labels, n_c = ndi.label(np.isfinite(res) & (res > 1.0), structure=struct)
        slices = ndi.find_objects(labels)
        total_ge_05ha = 0
        total_ge_2m = 0
        built_ge_10pct = 0
        crop_dom = 0
        bare_nonbuilt = 0
        ndvi_vals = []
        built_means = []

        for lab, slc in enumerate(slices, start=1):
            if slc is None:
                continue
            m = labels[slc] == lab
            cnt = int(m.sum())
            if cnt < 6:  # < 0.54 ha
                continue
            total_ge_05ha += 1
            peak_r = float(np.nanmax(res[slc][m]))
            if peak_r < 2.0:
                continue
            total_ge_2m += 1
            bf = float(np.nanmean(built[slc][m]))
            cf = float(np.nanmean(crop[slc][m]))
            wf = float(np.nanmean(water[slc][m]))
            nv = float(np.nanmean(ndvi_30m[slc][m]))
            built_means.append(bf)
            ndvi_vals.append(nv)
            if bf >= 0.10:
                built_ge_10pct += 1
            elif cf >= 0.50:
                crop_dom += 1
            elif wf < 0.10:
                bare_nonbuilt += 1

        out.append({
            "block_id": bid,
            "name": label,
            "anomalies_tpi_gt1m_ge05ha": total_ge_05ha,
            "anomalies_peak_ge2m": total_ge_2m,
            "built_contaminated_ge10pct": built_ge_10pct,
            "built_contaminated_frac": round(built_ge_10pct / max(total_ge_2m, 1), 4),
            "cropland_dominated_ge50pct": crop_dom,
            "bare_nonbuilt_unexplained": bare_nonbuilt,
            "mean_built_fraction_of_peaks": round(float(np.mean(built_means)), 4) if built_means else 0.0,
            "median_ndvi_of_peaks": round(float(np.median(ndvi_vals)), 4) if ndvi_vals else None,
        })
    return out


def compute_roc_and_stats(pos_vals: list[float], neg_vals: list[float]) -> dict:
    p = np.asarray(pos_vals, dtype=np.float64)
    n = np.asarray(neg_vals, dtype=np.float64)
    stat = mannwhitneyu(p, n, alternative="greater")
    u_val = float(stat.statistic)
    auc = u_val / (len(p) * len(n))
    cliffs_delta = 2.0 * auc - 1.0

    # Exact ROC curve points
    thresholds = sorted(set(np.concatenate([p, n]).tolist()), reverse=True)
    fprs, tprs = [0.0], [0.0]
    for thr in thresholds:
        tprs.append(float(np.mean(p >= thr)))
        fprs.append(float(np.mean(n >= thr)))
    fprs.append(1.0)
    tprs.append(1.0)
    return {
        "n_pos": int(len(p)),
        "n_neg": int(len(n)),
        "pos_median": round(float(np.median(p)), 3),
        "pos_iqr": [round(float(np.percentile(p, 25)), 3), round(float(np.percentile(p, 75)), 3)],
        "neg_median": round(float(np.median(n)), 3),
        "neg_iqr": [round(float(np.percentile(n, 25)), 3), round(float(np.percentile(n, 75)), 3)],
        "mann_whitney_u": round(u_val, 2),
        "p_value_one_sided": float(stat.pvalue),
        "roc_auc": round(auc, 4),
        "cliffs_delta": round(cliffs_delta, 4),
        "roc_fpr": fprs,
        "roc_tpr": tprs,
    }


def cell_polygon_1km(e_center: float, n_center: float, proj: TMProjection) -> list[list[float]]:
    e0 = e_center - 500.0
    n0 = n_center - 500.0
    ce = np.array([e0, e0 + 1000.0, e0 + 1000.0, e0, e0], dtype=np.float64)
    cn = np.array([n0, n0, n0 + 1000.0, n0 + 1000.0, n0], dtype=np.float64)
    lo, la = proj.inverse(ce, cn)
    return [[round(float(x), 6), round(float(y), 6)] for x, y in zip(lo, la)]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    tile_index = load_tile_index()
    orengo_poly = load_orengo_aoi()

    corridor_specs = [
        {
            "corridor_id": "P01_P02",
            "title": "Cholistan and Ganweriwala margins (P01-P02, clipped to Orengo 2020 AOI)",
            "bbox": (70.0, 27.8, 72.0, 29.8),
            "subregions": {
                "P01": (70.0, 27.8, 72.0, 29.8),
                "P02": (70.8, 28.3, 71.5, 29.0),
            },
            "lon0": 71.0,
            "clip_poly": orengo_poly,
            "excl_buffer_m": 5000.0,
            "build_blind_packet": True,
        },
        {
            "corridor_id": "P03_P05_P07",
            "title": "Haryana-Punjab mound corridors (P03, P04, P05 and P07 overlap)",
            "bbox": (74.7, 29.1, 76.3, 30.5),
            "subregions": {
                "P03": (75.3, 29.3, 76.2, 30.0),
                "P04": (75.8, 29.8, 76.3, 30.5),
                "P05": (74.7, 29.8, 75.5, 30.4),
                "P07": (75.7, 29.1, 76.2, 29.6),
            },
            "lon0": 75.0,
            "clip_poly": None,
            "excl_buffer_m": 3000.0,
            "build_blind_packet": True,
        },
        {
            "corridor_id": "P06",
            "title": "Sirsa-Hanumangarh valley flanks (P06)",
            "bbox": (74.0, 29.1, 75.2, 29.9),
            "subregions": {"P06": (74.0, 29.1, 75.2, 29.9)},
            "lon0": 75.0,
            "clip_poly": None,
            "excl_buffer_m": 3000.0,
            "build_blind_packet": False,
        },
        {
            "corridor_id": "P08_P09",
            "title": "Harappa-Khanewal and East Multan-Tulamba (P08-P09)",
            "bbox": (71.3, 29.8, 73.0, 30.9),
            "subregions": {
                "P08": (71.5, 29.8, 73.0, 30.9),
                "P09": (71.3, 29.8, 72.6, 30.8),
            },
            "lon0": 72.0,
            "clip_poly": None,
            "excl_buffer_m": 3000.0,
            "build_blind_packet": False,
        },
    ]

    calibration_rows = []
    corridor_summaries = []
    blind_candidates = []
    blind_negatives = []
    plot_data = {}

    for spec in corridor_specs:
        cid = spec["corridor_id"]
        print(f"\n=== Analysis B: {cid} ===")
        proj = TMProjection(spec["lon0"])
        gmeta = load_dem_metric_grid(spec["bbox"], proj, grid_m=30.0, buffer_m=6000.0, tile_index=tile_index)
        dem = gmeta["dem"]
        gm = gmeta["grid_m"]
        print(f"  DEM shape={dem.shape}, tiles={len(gmeta['used_tiles'])}, valid={np.isfinite(dem).mean()*100:.2f}%")

        z1 = weighted_gaussian(dem, 1.0)
        tpi150 = (z1 - weighted_gaussian(dem, 150.0 / gm)).astype(np.float32)
        tpi300 = (z1 - weighted_gaussian(dem, 300.0 / gm)).astype(np.float32)
        tpi600 = (z1 - weighted_gaussian(dem, 600.0 / gm)).astype(np.float32)
        tpimax = np.maximum(np.maximum(tpi150, tpi300), tpi600).astype(np.float32)
        tpi5k = (dem - weighted_gaussian(dem, 5000.0 / gm)).astype(np.float32)

        comps, compact_mask = extract_components(
            dem, tpi150, tpi300, tpi600, tpimax, tpi5k,
            gmeta, proj, cid, spec["subregions"], clip_poly=spec["clip_poly"],
        )
        compact_comps = [c for c in comps if c["passes_compact_filter"]]
        print(f"  Extracted {len(comps)} components (0.5-40 ha); {len(compact_comps)} pass compact-mound filter")

        # Known sites in this corridor
        c_sites = [s for s in KNOWN_SITES if s["corridor"] == cid]
        site_en = []
        for s in c_sites:
            se, sn = proj.forward(s["lon"], s["lat"])
            se, sn = float(se), float(sn)
            site_en.append((se, sn, s))
            m = sample_disk_metrics(dem, tpi150, tpi300, tpi600, tpimax, tpi5k, compact_mask, gmeta, se, sn, radius_m=500.0)
            calibration_rows.append({
                "record_id": s["id"],
                "name": s["name"],
                "label": "known_site",
                "corridor": cid,
                "regions": "|".join(s["regions"]),
                "lon": s["lon"],
                "lat": s["lat"],
                "easting_m": round(se, 1),
                "northing_m": round(sn, 1),
                "source": s["source"],
                **m,
            })
            print(f"    SITE {s['name']:30s}: pt_TPI300={m['point_tpi300_m']} m | 500m max_TPI300={m['disk500_max_tpi300_m']} m, prom={m['disk500_peak_prominence_m']} m, offset={m['disk500_peak_offset_m']} m, compact={m['disk500_has_compact_mound']}")

        # Build eligible 1 km^2 grid for stratified random negative controls (excluding known-site buffers)
        e_starts = np.arange(gmeta["inner_e0"], gmeta["inner_e1"], 1000.0)
        n_starts = np.arange(gmeta["inner_n0"], gmeta["inner_n1"], 1000.0)
        EE, NN = np.meshgrid(e_starts + 500.0, n_starts + 500.0)
        LON, LAT = proj.inverse(EE, NN)

        # Region mask
        in_reg = np.zeros(EE.shape, dtype=bool)
        for sw, ss, se_b, sn_b in spec["subregions"].values():
            in_reg |= (LON >= sw) & (LON <= se_b) & (LAT >= ss) & (LAT <= sn_b)
        if spec["clip_poly"] is not None:
            in_reg &= points_in_polygon(LON, LAT, spec["clip_poly"])

        # Exclude known-site buffers
        for se, sn, _ in site_en:
            in_reg &= (np.hypot(EE - se, NN - sn) > spec["excl_buffer_m"])

        # Check DEM validity and macro TPI_5km at cell centers
        rc_grid = np.round((gmeta["grid_n1"] - NN) / gm - 0.5).astype(np.int32)
        cc_grid = np.round((EE - gmeta["grid_e0"]) / gm - 0.5).astype(np.int32)
        in_bounds = (rc_grid >= 20) & (rc_grid < dem.shape[0] - 20) & (cc_grid >= 20) & (cc_grid < dem.shape[1] - 20)
        in_reg &= in_bounds
        elig_idx = np.argwhere(in_reg)
        elig_cells = []
        for ir, ic in elig_idx:
            r_c = int(rc_grid[ir, ic])
            c_c = int(cc_grid[ir, ic])
            if not (np.isfinite(dem[r_c, c_c]) and np.isfinite(tpi5k[r_c, c_c])):
                continue
            lo = float(LON[ir, ic])
            la = float(LAT[ir, ic])
            regs = [sr for sr, (sw, ss, se_b, sn_b) in spec["subregions"].items() if sw <= lo <= se_b and ss <= la <= sn_b]
            elig_cells.append({
                "easting_m": float(EE[ir, ic]),
                "northing_m": float(NN[ir, ic]),
                "lon": round(lo, 6),
                "lat": round(la, 6),
                "regions": regs,
                "tpi5k": float(tpi5k[r_c, c_c]),
            })

        # Stratify eligible negative cells into TPI_5km quartiles and draw 50 (12-13 per quartile)
        t5_vals = np.array([c["tpi5k"] for c in elig_cells])
        q_edges = np.percentile(t5_vals, [0, 25, 50, 75, 100])
        seed_hex, seed_int = deterministic_seed(f"indus_valley_script:2026-11-22:issue12:negatives:v1:{cid}")
        rng = np.random.Generator(np.random.PCG64(seed_int))

        neg_cells_drawn = []
        per_q = [13, 12, 13, 12]
        for qi in range(4):
            lo_q, hi_q = q_edges[qi], q_edges[qi + 1]
            q_pool = [c for c in elig_cells if (c["tpi5k"] >= lo_q and (c["tpi5k"] <= hi_q if qi == 3 else c["tpi5k"] < hi_q))]
            order = rng.permutation(len(q_pool))
            picked = 0
            for idx in order:
                cand = q_pool[int(idx)]
                if all(math.hypot(cand["easting_m"] - prev["easting_m"], cand["northing_m"] - prev["northing_m"]) >= 2000.0 for prev in neg_cells_drawn):
                    m = sample_disk_metrics(dem, tpi150, tpi300, tpi600, tpimax, tpi5k, compact_mask, gmeta, cand["easting_m"], cand["northing_m"], radius_m=500.0)
                    if m.get("valid"):
                        neg_cells_drawn.append({**cand, **m, "quartile": qi + 1})
                        picked += 1
                        if picked == per_q[qi]:
                            break

        for ni, nc in enumerate(neg_cells_drawn, start=1):
            calibration_rows.append({
                "record_id": f"{cid}_NEG_{ni:02d}",
                "name": f"{cid} matched negative control {ni:02d}",
                "label": "negative_control",
                "corridor": cid,
                "regions": "|".join(nc["regions"]),
                "lon": nc["lon"],
                "lat": nc["lat"],
                "easting_m": round(nc["easting_m"], 1),
                "northing_m": round(nc["northing_m"], 1),
                "source": f"Stratified random 1 km^2 negative (TPI5km Q{nc['quartile']})",
                **{k: nc[k] for k in [
                    "valid", "point_tpi300_m", "point_tpimax_m",
                    "disk500_max_tpi150_m", "disk500_max_tpi300_m", "disk500_max_tpi600_m",
                    "disk500_max_tpimax_m", "disk500_peak_prominence_m", "disk500_peak_offset_m",
                    "disk500_has_compact_mound", "center_tpi5km_m",
                ]},
            })

        # Build blind-testable packet candidates + matched negatives for P01_P02 and P03_P05_P07
        corridor_shortlist = []
        corridor_blind_neg = []
        if spec["build_blind_packet"]:
            # Exclude known-site buffers from compact candidates
            elig_cands = []
            for c in compact_comps:
                if any(math.hypot(c["easting_m"] - se, c["northing_m"] - sn) <= spec["excl_buffer_m"] for se, sn, _ in site_en):
                    continue
                if cid == "P03_P05_P07":
                    # Restrict blind packet strictly to P03, P04, P05 (not P07-only)
                    target_regs = [r for r in c["regions"] if r in ("P03", "P04", "P05")]
                    if not target_regs:
                        continue
                    c = dict(c)
                    c["primary_region"] = target_regs[0]
                else:
                    c = dict(c)
                    c["primary_region"] = "P02" if "P02" in c["regions"] else "P01"
                elig_cands.append(c)

            if cid == "P01_P02":
                # 6 per size class (small 0.5-5 ha, medium 5-20 ha, large 20-40 ha)
                for sclass in ["small_0.5_5ha", "medium_5_20ha", "large_20_40ha"]:
                    pool_s = sorted([c for c in elig_cands if c["size_class"] == sclass], key=lambda x: x["geometric_rank_score"], reverse=True)
                    added = 0
                    for cand in pool_s:
                        if all(math.hypot(cand["easting_m"] - prev["easting_m"], cand["northing_m"] - prev["northing_m"]) >= 2000.0 for prev in corridor_shortlist):
                            corridor_shortlist.append(cand)
                            added += 1
                            if added == 6:
                                break
                # Pair with 18 landform-matched negative controls from neg_cells_drawn (preferring non-compact negative cells)
                neg_pool = [nc for nc in neg_cells_drawn if not nc["disk500_has_compact_mound"]] + [nc for nc in neg_cells_drawn if nc["disk500_has_compact_mound"]]
                for nc in neg_pool[:len(corridor_shortlist)]:
                    r_p = "P02" if "P02" in nc["regions"] else "P01"
                    corridor_blind_neg.append({**nc, "primary_region": r_p, "proj_lon0": spec["lon0"]})
            else:
                # P03_P05_P07: 6 per corridor (P03, P04, P05), 2 per size class if available, else top ranked with >=2 km spacing
                for reg_target in ["P03", "P04", "P05"]:
                    reg_pool = [c for c in elig_cands if reg_target in c["regions"]]
                    picked_reg = []
                    for sclass in ["small_0.5_5ha", "medium_5_20ha", "large_20_40ha"]:
                        sp = sorted([c for c in reg_pool if c["size_class"] == sclass], key=lambda x: x["geometric_rank_score"], reverse=True)
                        cnt_s = 0
                        for cand in sp:
                            if all(math.hypot(cand["easting_m"] - prev["easting_m"], cand["northing_m"] - prev["northing_m"]) >= 2000.0 for prev in corridor_shortlist + picked_reg):
                                c_copy = dict(cand)
                                c_copy["primary_region"] = reg_target
                                picked_reg.append(c_copy)
                                cnt_s += 1
                                if cnt_s == 2:
                                    break
                    # Backfill up to 6 if a size class had < 2 candidates
                    if len(picked_reg) < 6:
                        rem = sorted(reg_pool, key=lambda x: x["geometric_rank_score"], reverse=True)
                        for cand in rem:
                            if all(math.hypot(cand["easting_m"] - prev["easting_m"], cand["northing_m"] - prev["northing_m"]) >= 2000.0 for prev in corridor_shortlist + picked_reg):
                                c_copy = dict(cand)
                                c_copy["primary_region"] = reg_target
                                picked_reg.append(c_copy)
                                if len(picked_reg) == 6:
                                    break
                    corridor_shortlist.extend(picked_reg)

                    # 6 negative controls specifically inside reg_target, strictly deduplicated across P03/P04/P05 overlaps
                    used_neg_coords = {(round(x["easting_m"], 1), round(x["northing_m"], 1)) for x in corridor_blind_neg}
                    neg_reg = [
                        nc for nc in neg_cells_drawn
                        if reg_target in nc["regions"] and (round(nc["easting_m"], 1), round(nc["northing_m"], 1)) not in used_neg_coords
                    ]
                    neg_reg_ord = [nc for nc in neg_reg if not nc["disk500_has_compact_mound"]] + [nc for nc in neg_reg if nc["disk500_has_compact_mound"]]
                    for nc in neg_reg_ord[:len(picked_reg)]:
                        corridor_blind_neg.append({**nc, "primary_region": reg_target, "proj_lon0": spec["lon0"]})

            for c in corridor_shortlist:
                c["proj_lon0"] = spec["lon0"]
                blind_candidates.append(c)
            blind_negatives.extend(corridor_blind_neg)
            print(f"  Blind packet contribution: {len(corridor_shortlist)} candidates + {len(corridor_blind_neg)} matched negatives")

            plot_data[cid] = {
                "cands": corridor_shortlist,
                "negs": corridor_blind_neg,
                "sites": c_sites,
                "bbox": spec["bbox"],
                "clip_poly": spec["clip_poly"],
            }

        corridor_summaries.append({
            "corridor_id": cid,
            "title": spec["title"],
            "used_tiles": gmeta["used_tiles"],
            "eligible_1km2_cells": len(elig_cells),
            "total_components_05_40ha": len(comps),
            "compact_mound_components": len(compact_comps),
            "known_sites_evaluated": len(c_sites),
            "matched_negatives_evaluated": len(neg_cells_drawn),
            "neg_draw_seed_sha256": seed_hex,
            "blind_candidates_selected": len(corridor_shortlist),
            "blind_negatives_selected": len(corridor_blind_neg),
        })

    # Overall calibration statistics: known sites (n=12) vs matched negative controls (n=200)
    pos_rows = [r for r in calibration_rows if r["label"] == "known_site"]
    neg_rows = [r for r in calibration_rows if r["label"] == "negative_control"]

    stats_tpi300 = compute_roc_and_stats(
        [r["disk500_max_tpi300_m"] for r in pos_rows],
        [r["disk500_max_tpi300_m"] for r in neg_rows],
    )
    stats_tpimax = compute_roc_and_stats(
        [r["disk500_max_tpimax_m"] for r in pos_rows],
        [r["disk500_max_tpimax_m"] for r in neg_rows],
    )
    stats_prom = compute_roc_and_stats(
        [r["disk500_peak_prominence_m"] for r in pos_rows if r["disk500_peak_prominence_m"] is not None],
        [r["disk500_peak_prominence_m"] for r in neg_rows if r["disk500_peak_prominence_m"] is not None],
    )

    # Operating points: True Positive Recall vs False Positive Rate
    operating_points = []
    for name, fn in [
        ("TPI_300 >= 2.0 m (500 m disk)", lambda r: r["disk500_max_tpi300_m"] >= 2.0),
        ("TPI_300 >= 3.0 m (500 m disk)", lambda r: r["disk500_max_tpi300_m"] >= 3.0),
        ("TPI_300 >= 4.0 m (500 m disk)", lambda r: r["disk500_max_tpi300_m"] >= 4.0),
        ("TPI_max >= 3.5 m (500 m disk)", lambda r: r["disk500_max_tpimax_m"] >= 3.5),
        ("TPI_max >= 5.0 m (500 m disk)", lambda r: r["disk500_max_tpimax_m"] >= 5.0),
        ("Annulus prominence >= 3.0 m", lambda r: (r["disk500_peak_prominence_m"] or -99) >= 3.0),
        ("Compact-mound filter (area 0.5-40 ha, AR<=3.5, C>=0.15, exp<=4.5, prom>=2.5 m)", lambda r: bool(r["disk500_has_compact_mound"])),
    ]:
        tp = sum(1 for r in pos_rows if fn(r))
        fp = sum(1 for r in neg_rows if fn(r))
        operating_points.append({
            "rule": name,
            "tp": tp,
            "n_pos": len(pos_rows),
            "recall": round(tp / len(pos_rows), 4),
            "fp": fp,
            "n_neg": len(neg_rows),
            "fpr": round(fp / len(neg_rows), 4),
        })

    print("\n=== CALIBRATION SUMMARY (12 known site records vs 200 matched negatives) ===")
    print(f"  TPI_300 ROC AUC = {stats_tpi300['roc_auc']:.4f}, Cliff's delta = {stats_tpi300['cliffs_delta']:.4f}, p = {stats_tpi300['p_value_one_sided']:.3e}")
    print(f"  TPI_max ROC AUC = {stats_tpimax['roc_auc']:.4f}, Cliff's delta = {stats_tpimax['cliffs_delta']:.4f}, p = {stats_tpimax['p_value_one_sided']:.3e}")
    print(f"  Prominence AUC  = {stats_prom['roc_auc']:.4f}, Cliff's delta = {stats_prom['cliffs_delta']:.4f}, p = {stats_prom['p_value_one_sided']:.3e}")
    for op in operating_points:
        print(f"  {op['rule']:75s} | Recall={op['tp']:2d}/{op['n_pos']} ({op['recall']*100:5.1f}%) | FPR={op['fp']:3d}/{op['n_neg']} ({op['fpr']*100:5.1f}%)")

    # Cross-check with held WorldCover + Sentinel-2 blocks
    wc_summary = cross_check_held_worldcover()
    print("\n=== HELD WORLDCOVER + SENTINEL-2 CROSS-CHECK (B01, B02, B04) ===")
    for row in wc_summary:
        print(f"  {row['block_id']} ({row['name']}): peak>=2m={row['anomalies_peak_ge2m']}, built>=10%={row['built_contaminated_ge10pct']} ({row['built_contaminated_frac']*100:.1f}%), crop>=50%={row['cropland_dominated_ge50pct']}, bare={row['bare_nonbuilt_unexplained']}, medNDVI={row['median_ndvi_of_peaks']}")

    # Assemble blind-testable packet (shuffled with SHA-256 seed)
    raw_units = []
    for c in blind_candidates:
        raw_units.append({
            "unit_type": "candidate_anomaly",
            "source_id": c["comp_id"],
            "corridor": c["corridor"],
            "primary_region": c["primary_region"],
            "regions": "|".join(c["regions"]),
            "lon": c["lon"],
            "lat": c["lat"],
            "easting_m": c["easting_m"],
            "northing_m": c["northing_m"],
            "proj_lon0": c["proj_lon0"],
            "size_class": c["size_class"],
            "area_ha": c["area_ha"],
            "peak_tpi300_m": c["peak_tpi300_m"],
            "peak_tpimax_m": c["peak_tpimax_m"],
            "annulus_prominence_m": c["annulus_prominence_m"],
            "axis_ratio": c["axis_ratio"],
            "compactness": c["compactness"],
            "geometric_rank_score": c["geometric_rank_score"],
            "tpi_5km_m": c["tpi_5km_m"],
            "demotion_rule": DEMOTION_RULES[c["primary_region"]],
        })
    for ni, nc in enumerate(blind_negatives, start=1):
        raw_units.append({
            "unit_type": "negative_control",
            "source_id": f"{nc['primary_region']}-NEG-{ni:03d}",
            "corridor": "P01_P02" if nc["primary_region"] in ("P01", "P02") else "P03_P05_P07",
            "primary_region": nc["primary_region"],
            "regions": "|".join(nc["regions"]),
            "lon": nc["lon"],
            "lat": nc["lat"],
            "easting_m": round(nc["easting_m"], 1),
            "northing_m": round(nc["northing_m"], 1),
            "proj_lon0": nc["proj_lon0"],
            "size_class": "matched_negative_1km2",
            "area_ha": 100.0,
            "peak_tpi300_m": nc["disk500_max_tpi300_m"],
            "peak_tpimax_m": nc["disk500_max_tpimax_m"],
            "annulus_prominence_m": nc["disk500_peak_prominence_m"],
            "axis_ratio": None,
            "compactness": None,
            "geometric_rank_score": None,
            "tpi_5km_m": nc["center_tpi5km_m"],
            "demotion_rule": DEMOTION_RULES[nc["primary_region"]],
        })

    blind_seed_label = "indus_valley_script:2026-11-22:issue12:blind:v1"
    blind_seed_hex, blind_seed_int = deterministic_seed(blind_seed_label)
    rng_b = np.random.Generator(np.random.PCG64(blind_seed_int))
    perm = rng_b.permutation(len(raw_units))

    blind_public_rows = []
    blind_key_rows = []
    blind_geojson_features = []

    for idx_b, orig_i in enumerate(perm, start=1):
        u = raw_units[int(orig_i)]
        bid = f"BLIND-{idx_b:03d}"
        pub = {
            "blind_id": bid,
            "corridor": u["corridor"],
            "primary_region": u["primary_region"],
            "regions": u["regions"],
            "lon": u["lon"],
            "lat": u["lat"],
            "tpi_5km_m": u["tpi_5km_m"],
            "survey_unit_note": "1 km^2 ground-check cell centered on target coordinate; candidate vs. negative status concealed",
            "demotion_rule": u["demotion_rule"],
        }
        blind_public_rows.append(pub)

        key_rec = {"blind_id": bid, **{k: v for k, v in u.items() if k != "proj_lon0"}}
        blind_key_rows.append(key_rec)

        proj_u = TMProjection(u["proj_lon0"])
        poly = cell_polygon_1km(u["easting_m"], u["northing_m"], proj_u)
        blind_geojson_features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [poly]},
            "properties": pub,
        })

    blind_key_sha256 = canonical_sha256(blind_key_rows)

    # Save calibration CSV
    calib_csv = OUT_DIR / "analysis_b_calibration_table.csv"
    calib_fields = [
        "record_id", "name", "label", "corridor", "regions", "lon", "lat", "easting_m", "northing_m",
        "source", "point_tpi300_m", "point_tpimax_m",
        "disk500_max_tpi150_m", "disk500_max_tpi300_m", "disk500_max_tpi600_m", "disk500_max_tpimax_m",
        "disk500_peak_prominence_m", "disk500_peak_offset_m", "disk500_has_compact_mound", "center_tpi5km_m",
    ]
    with calib_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=calib_fields)
        w.writeheader()
        for r in calibration_rows:
            w.writerow({k: r.get(k) for k in calib_fields})

    # Save blind field packet CSV & GeoJSON
    blind_csv = OUT_DIR / "analysis_b_blind_field_packet.csv"
    pub_fields = list(blind_public_rows[0].keys())
    with blind_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pub_fields)
        w.writeheader()
        w.writerows(blind_public_rows)

    blind_geojson = OUT_DIR / "analysis_b_blind_field_packet.geojson"
    blind_geojson.write_text(
        json.dumps({"type": "FeatureCollection", "name": "analysis_b_blind_field_packet", "features": blind_geojson_features}, indent=2) + "\n",
        encoding="utf-8",
    )

    # Save blind key CSV & lock JSON
    key_csv = OUT_DIR / "analysis_b_blind_key.csv"
    key_fields = list(blind_key_rows[0].keys())
    with key_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=key_fields)
        w.writeheader()
        w.writerows(blind_key_rows)

    (OUT_DIR / "analysis_b_blind_key_lock.json").write_text(
        json.dumps({
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "blind_seed_label": blind_seed_label,
            "blind_seed_sha256": blind_seed_hex,
            "total_units": len(blind_key_rows),
            "candidate_count": sum(1 for r in blind_key_rows if r["unit_type"] == "candidate_anomaly"),
            "negative_control_count": sum(1 for r in blind_key_rows if r["unit_type"] == "negative_control"),
            "blind_key_commitment_sha256": blind_key_sha256,
        }, indent=2) + "\n",
        encoding="utf-8",
    )

    # Render figure
    fig_path = render_analysis_b_figure(pos_rows, neg_rows, stats_tpi300, stats_tpimax, stats_prom, plot_data)

    # Save summary JSON (drop raw ROC point arrays from top-level summary? Keep compact!)
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "experiments/2026-11-22-geospatial-prospection-pilot/PROTOCOL.md",
        "corridors": corridor_summaries,
        "calibration_metrics": {
            "disk500_max_tpi300_m": {k: v for k, v in stats_tpi300.items() if k not in ("roc_fpr", "roc_tpr")},
            "disk500_max_tpimax_m": {k: v for k, v in stats_tpimax.items() if k not in ("roc_fpr", "roc_tpr")},
            "disk500_peak_prominence_m": {k: v for k, v in stats_prom.items() if k not in ("roc_fpr", "roc_tpr")},
            "operating_points": operating_points,
        },
        "held_worldcover_sentinel2_crosscheck": wc_summary,
        "blind_packet": {
            "total_units": len(blind_key_rows),
            "candidate_count": sum(1 for r in blind_key_rows if r["unit_type"] == "candidate_anomaly"),
            "negative_control_count": sum(1 for r in blind_key_rows if r["unit_type"] == "negative_control"),
            "blind_seed_sha256": blind_seed_hex,
            "blind_key_commitment_sha256": blind_key_sha256,
            "public_csv": blind_csv.relative_to(ROOT).as_posix(),
            "public_geojson": blind_geojson.relative_to(ROOT).as_posix(),
            "key_csv": key_csv.relative_to(ROOT).as_posix(),
        },
        "figure_path": fig_path.relative_to(ROOT).as_posix(),
    }
    (OUT_DIR / "analysis_b_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved Analysis B outputs and figure: {fig_path.relative_to(ROOT).as_posix()}")


def render_analysis_b_figure(pos_rows, neg_rows, stats_tpi300, stats_tpimax, stats_prom, plot_data) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.5), dpi=180)

    # Panel A: TPI_300 distribution (known sites vs 200 matched negative controls)
    ax = axes[0, 0]
    neg_v = [r["disk500_max_tpi300_m"] for r in neg_rows]
    pos_v = [r["disk500_max_tpi300_m"] for r in pos_rows]
    bins = np.linspace(0, max(max(pos_v), max(neg_v)) + 0.5, 28)
    ax.hist(neg_v, bins=bins, density=True, alpha=0.65, color="#6baed6", edgecolor="#2b5c8f", label=f"Matched negative 500 m disks (n={len(neg_v)}, med={stats_tpi300['neg_median']:.2f} m)")
    ax.hist(pos_v, bins=bins, density=True, alpha=0.70, color="#d95f02", edgecolor="#7f2704", label=f"Known archaeological sites (n={len(pos_v)}, med={stats_tpi300['pos_median']:.2f} m)")
    ax.axvline(2.0, color="#333333", linestyle="--", linewidth=1.1, label="TPI_300 = 2.0 m threshold")
    ax.axvline(3.0, color="#b2182b", linestyle=":", linewidth=1.3, label="TPI_300 = 3.0 m threshold")
    ax.set_xlabel("Max TPI (300 m background) inside 500 m search disk (m)")
    ax.set_ylabel("Density")
    ax.set_title("A. Known-Site vs. Negative-Control Relief Separation", fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)

    # Panel B: ROC curves
    ax = axes[0, 1]
    ax.plot(stats_tpi300["roc_fpr"], stats_tpi300["roc_tpr"], color="#d95f02", lw=2.2, label=f"Max TPI_300 (AUC = {stats_tpi300['roc_auc']:.3f})")
    ax.plot(stats_tpimax["roc_fpr"], stats_tpimax["roc_tpr"], color="#1b9e77", lw=2.0, linestyle="--", label=f"Multi-scale TPI_max (AUC = {stats_tpimax['roc_auc']:.3f})")
    ax.plot(stats_prom["roc_fpr"], stats_prom["roc_tpr"], color="#7570b3", lw=2.0, linestyle="-.", label=f"Annulus prominence (AUC = {stats_prom['roc_auc']:.3f})")
    ax.plot([0, 1], [0, 1], color="#888888", lw=1.0, linestyle=":")
    ax.set_xlabel("False Positive Rate (matched negative controls)")
    ax.set_ylabel("True Positive Recall (known documented sites)")
    ax.set_title("B. ROC Separation on Copernicus GLO-30 (n=12 vs. n=200)", fontweight="bold")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.grid(alpha=0.25)

    # Panel C: P01-P02 Cholistan blind packet map
    ax = axes[1, 0]
    p12 = plot_data["P01_P02"]
    poly = np.asarray(p12["clip_poly"])
    ax.plot(poly[:, 0], poly[:, 1], color="#444444", lw=1.2, label="Orengo et al. (2020) AOI")
    ax.scatter([x["lon"] for x in p12["negs"]], [x["lat"] for x in p12["negs"]], s=36, c="#3182bd", marker="s", alpha=0.85, label=f"Matched negatives ({len(p12['negs'])})")
    ax.scatter([x["lon"] for x in p12["cands"]], [x["lat"] for x in p12["cands"]], s=48, c="#e6550d", marker="^", edgecolors="#222", lw=0.6, label=f"Size-stratified candidates ({len(p12['cands'])})")
    for s in p12["sites"]:
        ax.scatter([s["lon"]], [s["lat"]], s=90, c="#000000", marker="*", zorder=6)
        ax.annotate(s["name"].replace("Ganweriwala ", "GNW "), (s["lon"], s["lat"]), xytext=(4, 4), textcoords="offset points", fontsize=7.5, fontweight="bold")
    ax.set_xlim(69.8, 72.6)
    ax.set_ylim(27.6, 29.8)
    ax.set_xlabel("Longitude (E)")
    ax.set_ylabel("Latitude (N)")
    ax.set_title("C. P01-P02 Cholistan Blind Field Units (36 units)", fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.25)

    # Panel D: P03-P05 Haryana-Punjab blind packet map
    ax = axes[1, 1]
    p35 = plot_data["P03_P05_P07"]
    # Draw editorial corridor boxes
    for rname, (sw, ss, se, sn), col in [
        ("P03", (75.3, 29.3, 76.2, 30.0), "#1b9e77"),
        ("P04", (75.8, 29.8, 76.3, 30.5), "#7570b3"),
        ("P05", (74.7, 29.8, 75.5, 30.4), "#e7298a"),
    ]:
        ax.plot([sw, se, se, sw, sw], [ss, ss, sn, sn, ss], color=col, lw=1.2, linestyle="--", label=f"{rname} bounds")
    ax.scatter([x["lon"] for x in p35["negs"]], [x["lat"] for x in p35["negs"]], s=36, c="#3182bd", marker="s", alpha=0.85, label=f"Matched negatives ({len(p35['negs'])})")
    ax.scatter([x["lon"] for x in p35["cands"]], [x["lat"] for x in p35["cands"]], s=48, c="#e6550d", marker="^", edgecolors="#222", lw=0.6, label=f"Corridor candidates ({len(p35['cands'])})")
    for s in p35["sites"]:
        ax.scatter([s["lon"]], [s["lat"]], s=90, c="#000000", marker="*", zorder=6)
        ax.annotate(s["name"].replace(" Mound", ""), (s["lon"], s["lat"]), xytext=(4, 3), textcoords="offset points", fontsize=7.5, fontweight="bold")
    ax.set_xlim(74.6, 76.4)
    ax.set_ylim(29.05, 30.55)
    ax.set_xlabel("Longitude (E)")
    ax.set_ylabel("Latitude (N)")
    ax.set_title("D. P03-P05 Haryana-Punjab Blind Field Units (36 units)", fontweight="bold")
    ax.legend(loc="lower left", fontsize=7.5, ncol=2)
    ax.grid(alpha=0.25)

    fig.suptitle("Analysis B: Multi-Scale GLO-30 Micro-Relief Calibration and Blind Prospection Packet", fontsize=12.5, fontweight="bold", y=0.985)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out_png = FIG_DIR / "analysis_b_calibration_and_candidates.png"
    fig.savefig(out_png, dpi=180)
    plt.close(fig)
    return out_png


if __name__ == "__main__":
    main()
