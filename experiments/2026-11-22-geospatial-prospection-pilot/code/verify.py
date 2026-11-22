"""Independent verification suite for Analyses A and B (Issues #12 and #13).

Verifies raw Copernicus DEM GLO-30 hashes and GeoTIFF headers, WGS84 Transverse
Mercator geodetic accuracy, synthetic terrain invariance, Analysis A stratum/
spacing/exclusion/holdout SHA-256 commitments, and Analysis B calibration
statistics and blind-packet integrity.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.stats import mannwhitneyu

from geo_utils import (
    EXP_DIR,
    ROOT,
    TMProjection,
    canonical_sha256,
    compute_hacf,
    points_in_polygon,
    weighted_gaussian,
)

OUT_DIR = EXP_DIR / "outputs"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_dem_manifest() -> dict:
    mpath = OUT_DIR / "dem_manifest.json"
    m = json.loads(mpath.read_text(encoding="utf-8"))
    failures = []
    for rec in m["tiles"]:
        p = ROOT / rec["logical_path"]
        if not p.exists():
            failures.append(f"Missing {rec['logical_path']}")
            continue
        if p.stat().st_size != rec["bytes"]:
            failures.append(f"Size mismatch {rec['filename']}")
        digest = sha256_file(p)
        if digest != rec["sha256"]:
            failures.append(f"SHA256 mismatch {rec['filename']}")
        with Image.open(p) as im:
            if im.size != (3600, 3600) or im.mode != "F":
                failures.append(f"Unexpected GeoTIFF size/mode {rec['filename']}: {im.size}/{im.mode}")
    return {
        "name": "dem_manifest_and_hashes",
        "tiles_checked": len(m["tiles"]),
        "passed": len(failures) == 0 and len(m["tiles"]) == 16,
        "failures": failures,
    }


def check_projection_accuracy() -> dict:
    utm43 = TMProjection(75.0)
    singh = json.loads((ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_SINGH_CORES_DERIVED.json").read_text(encoding="utf-8"))
    max_err_mm = 0.0
    max_rt_mm = 0.0
    for pt in singh["points"]:
        e, n = utm43.forward(pt["lon"], pt["lat"])
        err_mm = math.hypot(e - pt["easting"], n - pt["northing"]) * 1000.0
        lo2, la2 = utm43.inverse(e, n)
        e2, n2 = utm43.forward(lo2, la2)
        rt_mm = math.hypot(e2 - e, n2 - n) * 1000.0
        max_err_mm = max(max_err_mm, err_mm)
        max_rt_mm = max(max_rt_mm, rt_mm)
    return {
        "name": "wgs84_tm_projection_vs_pyproj",
        "points_checked": len(singh["points"]),
        "max_error_mm": round(max_err_mm, 5),
        "max_roundtrip_mm": round(max_rt_mm, 5),
        "passed": max_err_mm < 0.1 and max_rt_mm < 0.1,
    }


def check_synthetic_terrain_invariance() -> dict:
    rr, cc = np.indices((161, 161))
    hill = (7.0 * np.exp(-((rr - 80) ** 2 + (cc - 80) ** 2) / (2.0 * 3.0**2))).astype(np.float32)
    tpi = weighted_gaussian(hill, 1.0) - weighted_gaussian(hill, 10.0)
    tpi_shift = weighted_gaussian(hill + 125.0, 1.0) - weighted_gaussian(hill + 125.0, 10.0)
    plane = (0.04 * rr - 0.02 * cc).astype(np.float32)
    tpi_plane = weighted_gaussian(hill + plane, 1.0) - weighted_gaussian(hill + plane, 10.0)
    core = np.s_[45:-45, 45:-45]
    offset_diff = float(np.nanmax(np.abs(tpi - tpi_shift)))
    plane_diff = float(np.nanmax(np.abs(tpi[core] - tpi_plane[core])))
    peak_at_center = bool(tpi[80, 80] == np.nanmax(tpi) and tpi[80, 80] > 5.0)

    # Synthetic valley-bar step for HACF check (6 m step on a 400x400 grid = 12 km x 12 km)
    step_dem = np.full((400, 400), 100.0, dtype=np.float32)
    step_dem[:, 200:] = 106.0
    hacf = compute_hacf(step_dem, grid_m=30.0, radius_m=7500.0)
    hacf_valley = float(np.median(hacf[:, 50:150]))
    hacf_bar = float(np.median(hacf[:, 220:320]))

    passed = (
        offset_diff < 1e-4
        and plane_diff < 1e-3
        and peak_at_center
        and abs(hacf_valley - 0.0) < 1e-3
        and abs(hacf_bar - 6.0) < 1e-3
    )
    return {
        "name": "synthetic_tpi_and_hacf_invariance",
        "offset_max_diff_m": offset_diff,
        "planar_trend_core_max_diff_m": plane_diff,
        "peak_at_center": peak_at_center,
        "synthetic_step_valley_hacf_m": round(hacf_valley, 4),
        "synthetic_step_bar_hacf_m": round(hacf_bar, 4),
        "passed": passed,
    }


def check_analysis_a() -> dict:
    summary = json.loads((OUT_DIR / "analysis_a_summary.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT_DIR / "analysis_a_holdout_lock.json").read_text(encoding="utf-8"))
    failures = []
    frame_checks = {}

    for fr in summary["frames"]:
        fid = fr["frame_id"]
        rows = list(csv.DictReader((ROOT / fr["csv_path"]).open(encoding="utf-8")))
        gj = json.loads((ROOT / fr["geojson_path"]).read_text(encoding="utf-8"))

        prim = [r for r in rows if r["pilot_role"] in ("discovery_training", "holdout_evaluation")]
        hold = [r for r in rows if r["pilot_role"] == "holdout_evaluation"]
        baks = [r for r in rows if r["pilot_role"] == "backup_replacement"]

        if len(prim) != 24 or len(hold) != 8 or len(baks) != 12:
            failures.append(f"{fid}: unexpected block counts prim={len(prim)} hold={len(hold)} bak={len(baks)}")

        # Per-stratum counts, spacing, calibration buffer, spatial holdout grouping
        strata = sorted({r["geomorph_stratum"] for r in prim})
        if len(strata) != 4:
            failures.append(f"{fid}: expected 4 strata, got {strata}")
        min_spacing_obs = float("inf")
        min_anchor_dist = float("inf")

        for st in strata:
            sp = [r for r in prim if r["geomorph_stratum"] == st]
            sh = [r for r in hold if r["geomorph_stratum"] == st]
            sd = [r for r in sp if r["pilot_role"] == "discovery_training"]
            sb = [r for r in baks if r["geomorph_stratum"] == st]
            if len(sp) != 6 or len(sh) != 2 or len(sb) != 3:
                failures.append(f"{fid}/{st}: bad counts sp={len(sp)} sh={len(sh)} sb={len(sb)}")
            s_all = sp + sb
            for i in range(len(s_all)):
                d_anc = float(s_all[i]["nearest_anchor_dist_m"])
                min_anchor_dist = min(min_anchor_dist, d_anc)
                if d_anc <= 3000.0:
                    failures.append(f"{fid}/{st}: block {s_all[i]['pilot_block_id']} violates 3 km anchor buffer ({d_anc} m)")
                for j in range(i + 1, len(s_all)):
                    dist = math.hypot(
                        float(s_all[i]["easting_m"]) - float(s_all[j]["easting_m"]),
                        float(s_all[i]["northing_m"]) - float(s_all[j]["northing_m"]),
                    )
                    min_spacing_obs = min(min_spacing_obs, dist)
                    if dist < 5000.0 - 1e-6:
                        failures.append(f"{fid}/{st}: spacing violation {dist:.1f} m")
            # Check spatial grouping of holdout vs discovery
            h_es = [float(r["easting_m"]) for r in sh]
            d_es = [float(r["easting_m"]) for r in sd]
            if fr["holdout_spatial_side"] == "west":
                if max(h_es) > min(d_es):
                    failures.append(f"{fid}/{st}: west holdout easting overlap")
            else:
                if min(h_es) < max(d_es):
                    failures.append(f"{fid}/{st}: east holdout easting overlap")

        # Recompute canonical holdout commitment SHA-256 directly from CSV
        hold_sorted = sorted(hold, key=lambda r: r["pilot_block_id"])
        hold_canon = [
            {
                "pilot_block_id": r["pilot_block_id"],
                "cell_id": r["cell_id"],
                "stratum": r["geomorph_stratum"],
                "regions": r["regions"].split("|"),
                "lon": float(r["lon"]),
                "lat": float(r["lat"]),
                "easting_m": float(r["easting_m"]),
                "northing_m": float(r["northing_m"]),
                "tpi_5km_median_m": float(r["tpi_5km_median_m"]),
                "hacf_median_m": float(r["hacf_median_m"]),
            }
            for r in hold_sorted
        ]
        recomputed_sha = canonical_sha256(hold_canon)
        if recomputed_sha != fr["holdout_commitment_sha256"] or recomputed_sha != lock["frames"][fid]["holdout_commitment_sha256"]:
            failures.append(f"{fid}: holdout commitment SHA-256 mismatch")

        poly_feats = [f for f in gj["features"] if f["geometry"]["type"] == "Polygon"]
        if len(poly_feats) != 36:
            failures.append(f"{fid}: expected 36 GeoJSON polygons, got {len(poly_feats)}")
        for pf in poly_feats:
            ring = pf["geometry"]["coordinates"][0]
            if len(ring) != 5 or ring[0] != ring[-1]:
                failures.append(f"{fid}: unclosed GeoJSON ring")

        frame_checks[fid] = {
            "primary_blocks": len(prim),
            "holdout_blocks": len(hold),
            "backup_blocks": len(baks),
            "min_intra_stratum_spacing_m": round(min_spacing_obs, 1),
            "min_calibration_anchor_dist_m": round(min_anchor_dist, 1),
            "holdout_commitment_sha256_verified": recomputed_sha,
        }

    return {
        "name": "analysis_a_pilot_and_holdout_integrity",
        "frames": frame_checks,
        "passed": len(failures) == 0,
        "failures": failures,
    }


def check_analysis_b() -> dict:
    summary = json.loads((OUT_DIR / "analysis_b_summary.json").read_text(encoding="utf-8"))
    lock = json.loads((OUT_DIR / "analysis_b_blind_key_lock.json").read_text(encoding="utf-8"))
    calib = list(csv.DictReader((OUT_DIR / "analysis_b_calibration_table.csv").open(encoding="utf-8")))
    pub = list(csv.DictReader((OUT_DIR / "analysis_b_blind_field_packet.csv").open(encoding="utf-8")))
    key = list(csv.DictReader((OUT_DIR / "analysis_b_blind_key.csv").open(encoding="utf-8")))
    gj = json.loads((OUT_DIR / "analysis_b_blind_field_packet.geojson").read_text(encoding="utf-8"))
    orengo_poly = json.loads((ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_ORENGO_SOURCE_AOI.geojson").read_text(encoding="utf-8"))["features"][0]["geometry"]["coordinates"][0]

    failures = []
    pos = [r for r in calib if r["label"] == "known_site"]
    neg = [r for r in calib if r["label"] == "negative_control"]
    if len(pos) != 12 or len(neg) != 200:
        failures.append(f"Expected 12 pos / 200 neg calibration rows, got {len(pos)}/{len(neg)}")

    # Recompute Mann-Whitney U, AUC, Cliff's delta for TPI_300, TPI_max, prominence
    recomp_stats = {}
    for col in ("disk500_max_tpi300_m", "disk500_max_tpimax_m", "disk500_peak_prominence_m"):
        pv = np.array([float(r[col]) for r in pos])
        nv = np.array([float(r[col]) for r in neg])
        u = mannwhitneyu(pv, nv, alternative="greater")
        auc = float(u.statistic) / (len(pv) * len(nv))
        cd = 2.0 * auc - 1.0
        ref = summary["calibration_metrics"][col]
        if abs(round(auc, 4) - ref["roc_auc"]) > 1e-6 or abs(round(cd, 4) - ref["cliffs_delta"]) > 1e-6:
            failures.append(f"Metric mismatch on {col}: got auc={auc:.4f} vs {ref['roc_auc']}")
        if abs(float(u.pvalue) - ref["p_value_one_sided"]) > 1e-9:
            failures.append(f"P-value mismatch on {col}")
        recomp_stats[col] = {"roc_auc": round(auc, 4), "cliffs_delta": round(cd, 4), "p_value": float(u.pvalue)}

    # Check operating points TP/FP
    op_checks = [
        (lambda r: float(r["disk500_max_tpi300_m"]) >= 2.0),
        (lambda r: float(r["disk500_max_tpi300_m"]) >= 3.0),
        (lambda r: float(r["disk500_max_tpi300_m"]) >= 4.0),
        (lambda r: float(r["disk500_max_tpimax_m"]) >= 3.5),
        (lambda r: float(r["disk500_max_tpimax_m"]) >= 5.0),
        (lambda r: float(r["disk500_peak_prominence_m"]) >= 3.0),
        (lambda r: r["disk500_has_compact_mound"] == "True"),
    ]
    for idx_op, fn in enumerate(op_checks):
        tp = sum(1 for r in pos if fn(r))
        fp = sum(1 for r in neg if fn(r))
        ref_op = summary["calibration_metrics"]["operating_points"][idx_op]
        if tp != ref_op["tp"] or fp != ref_op["fp"]:
            failures.append(f"Operating point {idx_op} mismatch: ({tp},{fp}) vs ({ref_op['tp']},{ref_op['fp']})")

    # Check blind packet non-leakage & integrity
    forbidden_pub = {"unit_type", "source_id", "peak_tpi300_m", "peak_tpimax_m", "annulus_prominence_m", "geometric_rank_score", "area_ha"}
    pub_cols = set(pub[0].keys())
    if pub_cols & forbidden_pub:
        failures.append(f"Blind packet leaks columns: {pub_cols & forbidden_pub}")
    if len(pub) != 72 or len(key) != 72 or len(gj["features"]) != 72:
        failures.append(f"Expected 72 blind units, got pub={len(pub)} key={len(key)} gj={len(gj['features'])}")

    n_cand = sum(1 for r in key if r["unit_type"] == "candidate_anomaly")
    n_neg = sum(1 for r in key if r["unit_type"] == "negative_control")
    if n_cand != 36 or n_neg != 36:
        failures.append(f"Expected 36 candidates / 36 negatives, got {n_cand}/{n_neg}")
    # Zero duplicate coordinates across all 72 blind units (shared-frame overlap guard)
    coord_set = {(round(float(r["lon"]), 6), round(float(r["lat"]), 6)) for r in key}
    if len(coord_set) != len(key):
        failures.append(f"Duplicate coordinates in blind packet: {len(coord_set)} unique vs {len(key)} total")

    # Verify Cholistan blind units strictly inside Orengo AOI and >5 km from both Ganweriwala points
    proj71 = TMProjection(71.0)
    g1_e, g1_n = proj71.forward(71.150000, 28.598889)
    g2_e, g2_n = proj71.forward(71.066667, 28.500000)
    p12_units = [r for r in key if r["corridor"] == "P01_P02"]
    for u in p12_units:
        lo, la = float(u["lon"]), float(u["lat"])
        if not bool(points_in_polygon(np.array([lo]), np.array([la]), orengo_poly)[0]):
            failures.append(f"P01_P02 unit {u['blind_id']} outside Orengo AOI")
        ue, un = proj71.forward(lo, la)
        if min(math.hypot(ue - g1_e, un - g1_n), math.hypot(ue - g2_e, un - g2_n)) <= 5000.0:
            failures.append(f"P01_P02 unit {u['blind_id']} violates 5 km Ganweriwala exclusion buffer")

    # Verify P03-P05 blind units >3 km from Haryana calibration sites
    proj75 = TMProjection(75.0)
    haryana_sites = [
        (75.620633, 29.333083), (75.392133, 29.598316), (75.565278, 29.554167),
        (75.683333, 29.500000), (76.114683, 29.293733),
    ]
    hs_en = [proj75.forward(lo, la) for lo, la in haryana_sites]
    p35_units = [r for r in key if r["corridor"] == "P03_P05_P07"]
    for u in p35_units:
        ue, un = proj75.forward(float(u["lon"]), float(u["lat"]))
        if min(math.hypot(ue - se, un - sn) for se, sn in hs_en) <= 3000.0:
            failures.append(f"P03_P05 unit {u['blind_id']} violates 3 km site exclusion buffer")

    # Verify blind key commitment SHA-256
    # Convert CSV string types back to match JSON canonical types
    def parse_key_row(r: dict) -> dict:
        out = {}
        for k, v in r.items():
            if v == "":
                out[k] = None
            elif k in ("lon", "lat", "easting_m", "northing_m", "area_ha", "peak_tpi300_m", "peak_tpimax_m",
                       "annulus_prominence_m", "axis_ratio", "compactness", "geometric_rank_score", "tpi_5km_m"):
                out[k] = float(v)
            else:
                out[k] = v
        return out

    key_sha = canonical_sha256([parse_key_row(r) for r in key])
    if key_sha != lock["blind_key_commitment_sha256"] or key_sha != summary["blind_packet"]["blind_key_commitment_sha256"]:
        failures.append(f"Blind key commitment SHA-256 mismatch: {key_sha} vs {lock['blind_key_commitment_sha256']}")

    return {
        "name": "analysis_b_calibration_and_blind_packet",
        "recomputed_metrics": recomp_stats,
        "blind_units_checked": len(pub),
        "p01_p02_units": len(p12_units),
        "p03_p05_units": len(p35_units),
        "blind_key_sha256_verified": key_sha,
        "passed": len(failures) == 0,
        "failures": failures,
    }


def main() -> None:
    checks = [
        check_dem_manifest(),
        check_projection_accuracy(),
        check_synthetic_terrain_invariance(),
        check_analysis_a(),
        check_analysis_b(),
    ]
    all_passed = all(c["passed"] for c in checks)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "all_passed": all_passed,
        "passed_count": sum(1 for c in checks if c["passed"]),
        "total_checks": len(checks),
        "checks": checks,
    }
    out_path = OUT_DIR / "verification.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        print(f"[{status}] {c['name']}")
        if not c["passed"]:
            print("   FAILURES:", c.get("failures"))
    print(f"\nVerification summary: {report['passed_count']}/{report['total_checks']} checks passed -> {out_path.relative_to(ROOT).as_posix()}")
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
