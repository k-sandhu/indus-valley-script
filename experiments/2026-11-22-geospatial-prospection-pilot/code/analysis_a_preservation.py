"""Analysis A (Issue #13): 24-block buried-surface preservation stratification.

Implements PILOT-DESIGN-v4.md on Copernicus DEM GLO-30 across:
  1. Combined P08-P09 frame (Harappa-Khanewal / Old Beas / Ganji Bar / East Multan-Tulamba)
  2. Companion P06 frame (Sirsa-Hanumangarh valley flanks, anchored by Kalibangan & Singh 2017 cores)

Outputs deterministic 24-block pilot workloads (6 per stratum) with 3 ranked
replacements per stratum, spatially grouped 8-block held-out evaluation locks
with SHA-256 commitment hashes, GeoJSONs, CSVs, summary JSON, and maps.
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
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import numpy as np

from geo_utils import (
    EXP_DIR,
    ROOT,
    TMProjection,
    canonical_sha256,
    compute_hacf,
    compute_slope_deg,
    deterministic_seed,
    load_dem_metric_grid,
    load_tile_index,
    weighted_gaussian,
)

OUT_DIR = EXP_DIR / "outputs"
FIG_DIR = EXP_DIR / "figures"

STRATA_ORDER = [
    "S1_older_upland_bar",
    "S2_covered_bar_margin",
    "S3_young_alluvial_cover",
    "S4_active_channel_scour",
]

STRATUM_META = {
    "S1_older_upland_bar": {
        "label": "Older upland bar / stable interfluve",
        "coring_priority": "Shallow-to-moderate testing for near-surface or lightly capped target-age surfaces",
        "demotion_rule": "Demote if adequate dated profiles establish truncation or only post-Harappan terrestrial surfaces; older Pleistocene substrate alone leaves occupation unresolved.",
    },
    "S2_covered_bar_margin": {
        "label": "Covered bar margin / valley-flank transition",
        "coring_priority": "Primary flank-to-channel transect testing younger alluvial cover over older bar margins",
        "demotion_rule": "Demote covered-margin survival if adequate continuous transects establish complete lateral erosion or post-Harappan incision across the transition.",
    },
    "S3_young_alluvial_cover": {
        "label": "Young alluvial cover / leveled floodplain bench",
        "coring_priority": "Deep coring and OSL bracketing to test whether target-age surfaces survive beneath aggraded alluvium",
        "demotion_rule": "Demote only when cores reach below the target-age stratigraphic bracket and demonstrate absence or truncation; short cores that fail to reach target depth remain unresolved.",
    },
    "S4_active_channel_scour": {
        "label": "Active or recent channel scour belt",
        "coring_priority": "Negative geomorphic control for Holocene channel erosion and reworking",
        "demotion_rule": "Expected scour control; record whether deep Holocene scour completely removed pre-1900 BCE terrestrial units or left localized preserved islands.",
    },
}


def load_singh_cores() -> list[dict]:
    p = ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_SINGH_CORES_DERIVED.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    return [pt for pt in d["points"] if pt["name"].startswith("GS-")]


def frame_configs() -> list[dict]:
    singh_gs = load_singh_cores()
    p06_anchors = [
        {"id": "kalibangan", "name": "Kalibangan", "lat": 29.47388888888889, "lon": 74.12972222222223, "kind": "archaeological_site", "source": "Wikidata Q1722226 / sites-located-v1.json"},
        {"id": "sothi", "name": "Sothi", "lat": 29.1255, "lon": 74.7264, "kind": "archaeological_site", "source": "Wikidata Q48728244"},
        {"id": "karanpura", "name": "Karanpura", "lat": 29.108055555555556, "lon": 75.09722222222221, "kind": "archaeological_site", "source": "ASI IAR 2013-14 / sites-located-v1.json"},
    ]
    for pt in singh_gs:
        p06_anchors.append({
            "id": f"singh_{pt['name'].lower().replace('-', '_')}",
            "name": f"Singh2017 {pt['name']}",
            "lat": pt["lat"],
            "lon": pt["lon"],
            "kind": "dated_sediment_core",
            "source": "Singh et al. 2017 SI Table 1 (UTM 43N inferred)",
        })

    p08_p09_anchors = [
        {"id": "harappa", "name": "Harappa", "lat": 30.633333333333, "lon": 72.866666666667, "kind": "archaeological_site", "source": "Wikidata Q185562 / Uesugi 2010"},
        {"id": "harappa_doam", "name": "Harappa (DOAM)", "lat": 30.626363333, "lon": 72.866035111, "kind": "archaeological_site", "source": "DOAM Pakistan inventory / SPC03"},
        {"id": "tulamba", "name": "Tulamba", "lat": 30.525486111111, "lon": 72.239766666667, "kind": "archaeological_site", "source": "Wikidata Q7851908"},
    ]

    return [
        {
            "frame_id": "P08_P09",
            "title": "Harappa-Khanewal, Old Beas, Ganji Bar and East Multan-Tulamba (P08-P09)",
            "bbox": (71.3, 29.8, 73.0, 30.9),
            "subregions": {
                "P08": (71.5, 29.8, 73.0, 30.9),
                "P09": (71.3, 29.8, 72.6, 30.8),
            },
            "lon0": 72.0,
            "crs_label": "WGS84 Transverse Mercator (central meridian 72.0E, k0=0.9996)",
            "anchors": p08_p09_anchors,
            "calibration_buffer_m": 3000.0,
        },
        {
            "frame_id": "P06",
            "title": "Sirsa-Hanumangarh valley flanks (P06)",
            "bbox": (74.0, 29.1, 75.2, 29.9),
            "subregions": {
                "P06": (74.0, 29.1, 75.2, 29.9),
            },
            "lon0": 75.0,
            "crs_label": "WGS84 UTM Zone 43N (EPSG:32643)",
            "anchors": p06_anchors,
            "calibration_buffer_m": 3000.0,
        },
    ]


def classify_cell(stats: dict) -> str:
    """Apply locked PROTOCOL.md Section 2.2 classification rules."""
    if stats["roughness_tpi240_std_m"] > 2.0 or stats["slope_median_deg"] > 2.5:
        return "excluded_high_relief_or_urban"
    hacf = stats["hacf_median_m"]
    tpi5 = stats["tpi_5km_median_m"]
    slope = stats["slope_median_deg"]
    # 1. S4 active/recent channel scour
    if (hacf < 2.5 and tpi5 <= -1.0) or (stats["scour_pixel_frac"] >= 0.25):
        return "S4_active_channel_scour"
    # 2. S1 older upland bars / stable interfluve surfaces
    if tpi5 >= 1.25 and hacf >= 4.5 and slope <= 1.5:
        return "S1_older_upland_bar"
    # 3. S2 covered bar margins / valley-flank transitions
    if (-1.0 < tpi5 < 1.25 and hacf >= 2.5) or (stats["tpi_5km_p10_m"] <= -0.5 and stats["tpi_5km_p90_m"] >= 0.5):
        return "S2_covered_bar_margin"
    # 4. S3 young alluvial cover / leveled floodplain benches
    if tpi5 <= -0.5 or hacf < 4.5:
        return "S3_young_alluvial_cover"
    return "unclassified_residual"


def cell_polygon_wgs84(e0: float, n0: float, proj: TMProjection) -> list[list[float]]:
    corners_e = np.array([e0, e0 + 1000.0, e0 + 1000.0, e0, e0], dtype=np.float64)
    corners_n = np.array([n0, n0, n0 + 1000.0, n0 + 1000.0, n0], dtype=np.float64)
    lons, lats = proj.inverse(corners_e, corners_n)
    return [[round(float(lo), 6), round(float(la), 6)] for lo, la in zip(lons, lats)]


def run_frame(cfg: dict, tile_index: dict) -> dict:
    fid = cfg["frame_id"]
    print(f"\n=== Analysis A: {fid} ===")
    proj = TMProjection(cfg["lon0"])
    grid = load_dem_metric_grid(cfg["bbox"], proj, grid_m=30.0, buffer_m=9000.0, tile_index=tile_index)
    dem = grid["dem"]
    grid_m = grid["grid_m"]
    print(f"  DEM grid shape={dem.shape}, tiles={len(grid['used_tiles'])}, valid={np.isfinite(dem).mean()*100:.2f}%")

    # Compute pixel-level geomorphic layers
    slope = compute_slope_deg(dem, grid_m)
    z_smooth30 = weighted_gaussian(dem, 1.0)
    z_smooth240 = weighted_gaussian(dem, 8.0)
    tpi_240 = (z_smooth30 - z_smooth240).astype(np.float32)
    z_smooth5k = weighted_gaussian(dem, 5000.0 / grid_m)
    tpi_5km = (dem - z_smooth5k).astype(np.float32)
    hacf = compute_hacf(dem, grid_m=grid_m, radius_m=7500.0)
    scour_mask = np.isfinite(dem) & (hacf < 1.5) & (tpi_5km <= -1.0)

    # Project anchors
    anchor_en = []
    for a in cfg["anchors"]:
        ae, an = proj.forward(a["lon"], a["lat"])
        anchor_en.append((float(ae), float(an), a))

    # Build 1 km^2 cell grid strictly covering inner bounds
    e_starts = np.arange(grid["inner_e0"], grid["inner_e1"], 1000.0)
    n_starts = np.arange(grid["inner_n0"], grid["inner_n1"], 1000.0)
    n_cols_km = len(e_starts)
    n_rows_km = len(n_starts)

    # Raster map of cell classifications for visualization
    stratum_map = np.full((n_rows_km, n_cols_km), -1, dtype=np.int8)
    stratum_code_map = {
        "S1_older_upland_bar": 1,
        "S2_covered_bar_margin": 2,
        "S3_young_alluvial_cover": 3,
        "S4_active_channel_scour": 4,
        "calibration_excluded": 5,
        "excluded_high_relief_or_urban": 6,
        "unclassified_residual": 0,
    }

    w_box, s_box, e_box, n_box = cfg["bbox"]
    grid_e0 = grid["grid_e0"]
    grid_n1 = grid["grid_n1"]
    H, W = dem.shape

    cells = []
    counts = {k: 0 for k in stratum_code_map}
    subregion_counts = {sr: 0 for sr in cfg["subregions"]}
    overlap_count = 0

    for ir, n0 in enumerate(n_starts):
        # Row indices in DEM (row 0 = grid_n1)
        r_top = int(round((grid_n1 - (n0 + 1000.0)) / grid_m))
        r_bot = int(round((grid_n1 - n0) / grid_m))
        r_top_c = max(0, r_top)
        r_bot_c = min(H, r_bot)
        if r_bot_c <= r_top_c:
            continue
        # Centroids for entire row
        c_e = e_starts + 500.0
        c_n = np.full_like(c_e, n0 + 500.0)
        c_lon, c_lat = proj.inverse(c_e, c_n)

        for ic, e0 in enumerate(e_starts):
            lo = float(c_lon[ic])
            la = float(c_lat[ic])
            # Membership in editorial union box
            regs = []
            for sr_name, (sw, ss, se, sn) in cfg["subregions"].items():
                if sw <= lo <= se and ss <= la <= sn:
                    regs.append(sr_name)
            if not regs:
                continue

            c_left = int(round((e0 - grid_e0) / grid_m))
            c_right = int(round((e0 + 1000.0 - grid_e0) / grid_m))
            if c_left < 0 or c_right > W:
                continue

            sub_dem = dem[r_top_c:r_bot_c, c_left:c_right]
            valid = np.isfinite(sub_dem)
            vfrac = float(valid.mean())
            if vfrac < 0.95:
                continue

            sub_tpi5 = tpi_5km[r_top_c:r_bot_c, c_left:c_right][valid]
            sub_hacf = hacf[r_top_c:r_bot_c, c_left:c_right][valid]
            sub_slope = slope[r_top_c:r_bot_c, c_left:c_right][valid]
            sub_tpi240 = tpi_240[r_top_c:r_bot_c, c_left:c_right][valid]
            sub_scour = scour_mask[r_top_c:r_bot_c, c_left:c_right][valid]
            sub_z = sub_dem[valid]

            q25, q50, q75 = np.percentile(sub_z, [25.0, 50.0, 75.0])
            t10, t50, t90 = np.percentile(sub_tpi5, [10.0, 50.0, 90.0])

            stats = {
                "valid_fraction": round(vfrac, 4),
                "elev_median_m": round(float(q50), 2),
                "elev_iqr_m": round(float(q75 - q25), 2),
                "slope_median_deg": round(float(np.median(sub_slope)), 3),
                "tpi_5km_median_m": round(float(t50), 3),
                "tpi_5km_p10_m": round(float(t10), 3),
                "tpi_5km_p90_m": round(float(t90), 3),
                "hacf_median_m": round(float(np.median(sub_hacf)), 3),
                "scour_pixel_frac": round(float(sub_scour.mean()), 4),
                "roughness_tpi240_std_m": round(float(np.std(sub_tpi240)), 3),
            }
            geomorph_stratum = classify_cell(stats)

            # Check calibration buffer exclusion
            ce = float(c_e[ic])
            cn = float(c_n[ic])
            nearest_anchor_dist = float("inf")
            nearest_anchor_name = None
            for ae, an, aobj in anchor_en:
                d = math.hypot(ce - ae, cn - an)
                if d < nearest_anchor_dist:
                    nearest_anchor_dist = d
                    nearest_anchor_name = aobj["name"]

            is_calib = nearest_anchor_dist <= cfg["calibration_buffer_m"]
            final_status = "calibration_excluded" if is_calib else geomorph_stratum

            counts[final_status] += 1
            for sr in regs:
                subregion_counts[sr] += 1
            if len(regs) > 1:
                overlap_count += 1

            stratum_map[n_rows_km - 1 - ir, ic] = stratum_code_map[final_status]

            ekm = int(round(e0 / 1000.0))
            nkm = int(round(n0 / 1000.0))
            cells.append({
                "cell_id": f"{fid}_E{ekm:04d}_N{nkm:04d}",
                "frame_id": fid,
                "regions": regs,
                "easting_m": ce,
                "northing_m": cn,
                "e0_m": float(e0),
                "n0_m": float(n0),
                "lon": round(lo, 6),
                "lat": round(la, 6),
                "geomorph_stratum": geomorph_stratum,
                "status": final_status,
                "nearest_anchor": nearest_anchor_name,
                "nearest_anchor_dist_m": round(nearest_anchor_dist, 1),
                **stats,
            })

    print(f"  Total valid 1 km^2 cells in frame: {len(cells)}")
    for k, v in counts.items():
        print(f"    {k:32s}: {v:5d} ({v/max(len(cells),1)*100:5.2f}%)")

    # Anchor exact cell diagnostics (calibration sites & Singh cores)
    anchor_diagnostics = []
    for ae, an, aobj in anchor_en:
        ekm = int(math.floor(ae / 1000.0))
        nkm = int(math.floor(an / 1000.0))
        cid = f"{fid}_E{ekm:04d}_N{nkm:04d}"
        match = next((c for c in cells if c["cell_id"] == cid), None)
        anchor_diagnostics.append({
            "id": aobj["id"],
            "name": aobj["name"],
            "kind": aobj["kind"],
            "lat": aobj["lat"],
            "lon": aobj["lon"],
            "source": aobj["source"],
            "cell_id": cid,
            "geomorph_stratum": match["geomorph_stratum"] if match else None,
            "elev_median_m": match["elev_median_m"] if match else None,
            "tpi_5km_median_m": match["tpi_5km_median_m"] if match else None,
            "hacf_median_m": match["hacf_median_m"] if match else None,
            "slope_median_deg": match["slope_median_deg"] if match else None,
            "roughness_tpi240_std_m": match["roughness_tpi240_std_m"] if match else None,
        })

    # Cryptographic deterministic draw: 6 primary + 3 backup per stratum (min 5 km spacing within stratum)
    seed_label = f"indus_valley_script:2026-11-22:issue13:v1:{fid}"
    seed_hex, seed_int = deterministic_seed(seed_label)
    rng = np.random.Generator(np.random.PCG64(seed_int))

    holdout_label = f"indus_valley_script:2026-11-22:issue13:holdout:v1:{fid}"
    holdout_seed_hex, holdout_seed_int = deterministic_seed(holdout_label)
    holdout_side = "east" if (holdout_seed_int % 2 == 1) else "west"

    selected_primary = []
    selected_backups = []
    min_spacing_m = 5000.0

    for s_idx, stratum in enumerate(STRATA_ORDER, start=1):
        pool = sorted(
            [c for c in cells if c["status"] == stratum],
            key=lambda x: x["cell_id"],
        )
        if len(pool) < 9:
            raise RuntimeError(f"Stratum {stratum} in {fid} has only {len(pool)} eligible cells!")
        order = rng.permutation(len(pool))
        chosen = []
        for idx in order:
            cand = pool[int(idx)]
            if all(math.hypot(cand["easting_m"] - prev["easting_m"], cand["northing_m"] - prev["northing_m"]) >= min_spacing_m for prev in chosen):
                chosen.append(cand)
                if len(chosen) == 9:
                    break
        if len(chosen) < 9:
            raise RuntimeError(f"Could not place 9 spatially declustered (>=5 km) blocks in {fid}/{stratum}; got {len(chosen)}")

        prim = chosen[:6]
        baks = chosen[6:9]

        # Spatially grouped holdout: pick 2 of 6 primary blocks on the hash-selected side (eastmost or westmost)
        prim_sorted_spatial = sorted(
            prim,
            key=lambda c: c["easting_m"],
            reverse=(holdout_side == "east"),
        )
        holdout_ids = {c["cell_id"] for c in prim_sorted_spatial[:2]}

        for rank, c in enumerate(prim, start=1):
            rec = dict(c)
            rec["pilot_role"] = "holdout_evaluation" if c["cell_id"] in holdout_ids else "discovery_training"
            rec["pilot_block_id"] = f"{fid}-S{s_idx}-{rank:02d}"
            rec["backup_rank"] = 0
            rec["demotion_rule"] = STRATUM_META[stratum]["demotion_rule"]
            selected_primary.append(rec)

        for brank, c in enumerate(baks, start=1):
            rec = dict(c)
            rec["pilot_role"] = "backup_replacement"
            rec["pilot_block_id"] = f"{fid}-S{s_idx}-B{brank:02d}"
            rec["backup_rank"] = brank
            rec["demotion_rule"] = STRATUM_META[stratum]["demotion_rule"]
            selected_backups.append(rec)

    # Lock holdout commitment hash
    holdout_blocks = sorted(
        [b for b in selected_primary if b["pilot_role"] == "holdout_evaluation"],
        key=lambda b: b["pilot_block_id"],
    )
    holdout_canonical = [
        {
            "pilot_block_id": b["pilot_block_id"],
            "cell_id": b["cell_id"],
            "stratum": b["geomorph_stratum"],
            "regions": b["regions"],
            "lon": b["lon"],
            "lat": b["lat"],
            "easting_m": b["easting_m"],
            "northing_m": b["northing_m"],
            "tpi_5km_median_m": b["tpi_5km_median_m"],
            "hacf_median_m": b["hacf_median_m"],
        }
        for b in holdout_blocks
    ]
    holdout_commit_sha256 = canonical_sha256(holdout_canonical)
    print(f"  Selected 24 primary (8 held-out on {holdout_side} half, SHA-256={holdout_commit_sha256[:16]}...) + 12 backups")

    # Export CSV & GeoJSON
    all_export = selected_primary + selected_backups
    csv_path = OUT_DIR / f"analysis_a_{fid.lower()}_pilot_blocks.csv"
    fieldnames = [
        "pilot_block_id", "pilot_role", "backup_rank", "cell_id", "frame_id", "regions",
        "geomorph_stratum", "lon", "lat", "easting_m", "northing_m",
        "elev_median_m", "elev_iqr_m", "slope_median_deg",
        "tpi_5km_median_m", "tpi_5km_p10_m", "tpi_5km_p90_m",
        "hacf_median_m", "scour_pixel_frac", "roughness_tpi240_std_m",
        "nearest_anchor", "nearest_anchor_dist_m", "demotion_rule",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for b in all_export:
            row = {k: b[k] for k in fieldnames}
            row["regions"] = "|".join(b["regions"])
            w.writerow(row)

    features = []
    for b in all_export:
        poly = cell_polygon_wgs84(b["e0_m"], b["n0_m"], proj)
        props = {k: b[k] for k in fieldnames}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [poly]},
            "properties": props,
        })
    # Also include calibration anchors as Point features for reference
    for ad in anchor_diagnostics:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [ad["lon"], ad["lat"]]},
            "properties": {
                "pilot_role": "calibration_anchor",
                "anchor_id": ad["id"],
                "name": ad["name"],
                "kind": ad["kind"],
                "source": ad["source"],
                "cell_id": ad["cell_id"],
                "geomorph_stratum": ad["geomorph_stratum"],
                "tpi_5km_median_m": ad["tpi_5km_median_m"],
                "hacf_median_m": ad["hacf_median_m"],
            },
        })
    geojson_path = OUT_DIR / f"analysis_a_{fid.lower()}_pilot_blocks.geojson"
    geojson_path.write_text(
        json.dumps({"type": "FeatureCollection", "name": f"analysis_a_{fid.lower()}_pilot_blocks", "features": features}, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "frame_id": fid,
        "title": cfg["title"],
        "bbox_lonlat": list(cfg["bbox"]),
        "crs": cfg["crs_label"],
        "used_tiles": grid["used_tiles"],
        "total_valid_cells_1km2": len(cells),
        "subregion_cell_counts": subregion_counts,
        "overlap_cell_count": overlap_count,
        "stratum_counts": counts,
        "eligible_for_draw_total": sum(counts[s] for s in STRATA_ORDER),
        "seed_label": seed_label,
        "seed_sha256": seed_hex,
        "holdout_seed_label": holdout_label,
        "holdout_seed_sha256": holdout_seed_hex,
        "holdout_spatial_side": holdout_side,
        "holdout_commitment_sha256": holdout_commit_sha256,
        "primary_block_count": len(selected_primary),
        "holdout_block_count": len(holdout_blocks),
        "backup_block_count": len(selected_backups),
        "min_intra_stratum_spacing_m": min_spacing_m,
        "calibration_anchors": anchor_diagnostics,
        "holdout_blocks": holdout_canonical,
        "csv_path": csv_path.relative_to(ROOT).as_posix(),
        "geojson_path": geojson_path.relative_to(ROOT).as_posix(),
        # For plotting (stripped before JSON dump)
        "_plot": {
            "stratum_map": stratum_map,
            "extent_km": [
                grid["inner_e0"] / 1000.0,
                grid["inner_e1"] / 1000.0,
                grid["inner_n0"] / 1000.0,
                grid["inner_n1"] / 1000.0,
            ],
            "primary": selected_primary,
            "anchors": anchor_en,
        },
    }


def render_stratification_figure(results: list[dict]) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), dpi=180)
    # Color code: -1 outside, 0 unclassified, 1 S1 upland, 2 S2 margin, 3 S3 young cover, 4 S4 scour, 5 calib, 6 high-relief/urban
    colors = [
        "#f7f7f7",  # -1 outside
        "#cccccc",  # 0 unclassified
        "#d9a760",  # 1 S1 older upland bar
        "#8ab17d",  # 2 S2 covered bar margin
        "#6baed6",  # 3 S3 young alluvial cover
        "#2171b5",  # 4 S4 active channel scour
        "#b2abd2",  # 5 calibration buffer (3 km)
        "#737373",  # 6 excluded high-relief/urban
    ]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([-1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], cmap.N)

    for ax, res in zip(axes, results):
        p = res["_plot"]
        ax.imshow(p["stratum_map"], cmap=cmap, norm=norm, extent=p["extent_km"], origin="upper", interpolation="nearest")
        disc = [b for b in p["primary"] if b["pilot_role"] == "discovery_training"]
        hold = [b for b in p["primary"] if b["pilot_role"] == "holdout_evaluation"]

        ax.scatter(
            [b["easting_m"] / 1000.0 for b in disc],
            [b["northing_m"] / 1000.0 for b in disc],
            s=46, c="#ffffff", edgecolors="#111111", linewidths=1.2, marker="s", zorder=5,
            label="Discovery pilot block (16)",
        )
        ax.scatter(
            [b["easting_m"] / 1000.0 for b in hold],
            [b["northing_m"] / 1000.0 for b in hold],
            s=62, c="#d7191c", edgecolors="#111111", linewidths=1.2, marker="D", zorder=6,
            label=f"Locked holdout block (8, {res['holdout_spatial_side']} half)",
        )
        for ae, an, aobj in p["anchors"]:
            mk = "*" if aobj["kind"] == "archaeological_site" else "^"
            col = "#000000" if aobj["kind"] == "archaeological_site" else "#ffed6f"
            ax.scatter([ae / 1000.0], [an / 1000.0], s=75, c=col, edgecolors="#111111", linewidths=0.8, marker=mk, zorder=7)
            if aobj["kind"] == "archaeological_site" and aobj["id"] != "harappa_doam":
                ax.annotate(aobj["name"], (ae / 1000.0, an / 1000.0), xytext=(4, 4), textcoords="offset points", fontsize=8, fontweight="bold",
                            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75), zorder=8)

        ax.set_title(f"{res['frame_id']}: {res['total_valid_cells_1km2']:,} 1 km$^2$ cells", fontsize=11, fontweight="bold")
        ax.set_xlabel("Easting (km)")
        ax.set_ylabel("Northing (km)")
        ax.grid(alpha=0.25, linestyle="--", linewidth=0.5)
        ax.legend(loc="lower left", fontsize=8, framealpha=0.92)

    legend_handles = [
        Patch(facecolor="#d9a760", edgecolor="#444", label="S1: Older upland bar"),
        Patch(facecolor="#8ab17d", edgecolor="#444", label="S2: Covered bar margin"),
        Patch(facecolor="#6baed6", edgecolor="#444", label="S3: Young alluvial cover"),
        Patch(facecolor="#2171b5", edgecolor="#444", label="S4: Active channel scour"),
        Patch(facecolor="#b2abd2", edgecolor="#444", label="Calibration buffer (3 km excluded)"),
        Patch(facecolor="#737373", edgecolor="#444", label="Excluded high-relief / urban"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=3, fontsize=8.5, frameon=True, bbox_to_anchor=(0.5, 0.015))
    fig.suptitle("Analysis A: 1 km$^2$ Alluvial Preservation Stratification and Locked 24-Block Pilots (Copernicus GLO-30)", fontsize=12, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0.0, 0.13, 1.0, 0.94])
    out_png = FIG_DIR / "analysis_a_stratification_maps.png"
    fig.savefig(out_png, dpi=180)
    plt.close(fig)
    return out_png


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    tile_index = load_tile_index()
    results = [run_frame(cfg, tile_index) for cfg in frame_configs()]
    fig_path = render_stratification_figure(results)

    holdout_lock = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "experiments/2026-11-22-geospatial-prospection-pilot/PROTOCOL.md",
        "frames": {
            r["frame_id"]: {
                "seed_label": r["seed_label"],
                "seed_sha256": r["seed_sha256"],
                "holdout_seed_label": r["holdout_seed_label"],
                "holdout_seed_sha256": r["holdout_seed_sha256"],
                "holdout_spatial_side": r["holdout_spatial_side"],
                "holdout_commitment_sha256": r["holdout_commitment_sha256"],
                "holdout_blocks": r["holdout_blocks"],
            }
            for r in results
        },
    }
    (OUT_DIR / "analysis_a_holdout_lock.json").write_text(json.dumps(holdout_lock, indent=2) + "\n", encoding="utf-8")

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "experiments/2026-11-22-geospatial-prospection-pilot/PROTOCOL.md",
        "figure_path": fig_path.relative_to(ROOT).as_posix(),
        "frames": [{k: v for k, v in r.items() if k != "_plot"} for r in results],
    }
    (OUT_DIR / "analysis_a_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved Analysis A outputs and figure: {fig_path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
