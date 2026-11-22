"""Independent verification suite for the reconciled Indus site and survey-effort gazetteer (v1).

Re-reads upstream local registers and all generated outputs independently
(without importing build_gazetteer.py) and writes verification-v1.json.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]

VALID_UNIT_CLASSES = {"recorded_locality", "physical_mound_or_scatter", "regional_provenance_label"}
VALID_EXCAVATION_STATUSES = {
    "excavated",
    "surface_surveyed",
    "remote_proposal_unverified",
    "buried_under_living_town",
    "unknown",
}
VALID_PRECISION_CLASSES = {
    "surveyed_sub_100m",
    "image_located_site",
    "catalogued_arcsecond",
    "catalogued_arcminute",
    "approximate_regional_5km",
    "gazetteer_unquantified",
    "unlocated",
}
VALID_SURVEY_EFFORT_CLASSES = {
    "intensive_ground_survey",
    "targeted_excavation_and_local_survey",
    "historical_map_and_remote_screening",
    "reconnaissance_or_geomorphic_only",
    "undocumented_or_unacquired_survey_archive",
}

MANDATORY_ALIASES = [
    ("Morodharo", "kotada-lodrani"),
    ("Bagasra", "gola-dhoro-bagasra"),
    ("Gola Dhoro", "gola-dhoro-bagasra"),
    ("gola-dhoro", "gola-dhoro-bagasra"),
    ("Rupar", "ropar-rupar"),
    ("Rupnagar", "ropar-rupar"),
    ("Rupnagar / Ropar", "ropar-rupar"),
    ("Chanhujo-daro", "chanhu-daro"),
    ("Lakhian jo Daro", "lakhanjo-daro"),
    ("Sukkur", "lakhanjo-daro"),
    ("Desalpur", "desalpar"),
    ("desalpur", "desalpar"),
    ("Gharo Bhiro", "nuhato"),
    ("Valamio Timbo", "shikarpur"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return 2.0 * r * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def run_checks() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record_check(check_id: str, description: str, passed: bool, details: Any) -> None:
        checks.append(
            {
                "check_id": check_id,
                "description": description,
                "passed": bool(passed),
                "details": details,
            }
        )

    gaz = load_json(PKG / "gazetteer-v1.json")
    cov = load_json(PKG / "coverage-v1.json")
    se = load_json(PKG / "survey-effort-v1.json")
    with (PKG / "gazetteer-v1.csv").open(encoding="utf-8") as f:
        gaz_csv_rows = list(csv.DictReader(f))
    with (PKG / "aliases-v1.csv").open(encoding="utf-8") as f:
        alias_csv_rows = list(csv.DictReader(f))

    records = gaz["records"]
    by_id = {r["id"]: r for r in records}

    # Check 1: Input and output SHA-256 hash integrity
    hash_mismatches = []
    for k, meta in cov["inputs"].items():
        p = ROOT / meta["logical_path"]
        if not p.exists() or sha256_file(p) != meta["sha256"]:
            hash_mismatches.append({"kind": "input", "key": k, "path": meta["logical_path"]})
    for k, meta in cov["outputs"].items():
        p = ROOT / meta["logical_path"]
        if not p.exists() or sha256_file(p) != meta["sha256"]:
            hash_mismatches.append({"kind": "output", "key": k, "path": meta["logical_path"]})
    record_check(
        "V01_hash_integrity",
        "All upstream input hashes and generated output hashes (including local-only D: extract) match coverage-v1.json.",
        len(hash_mismatches) == 0,
        {"inputs_checked": len(cov["inputs"]), "outputs_checked": len(cov["outputs"]), "mismatches": hash_mismatches},
    )

    # Check 2: Zero entity loss across all upstream registers
    atlas_in = load_json(ROOT / "experiments/2026-10-26-indus-living-atlas/mapping/run-v2/atlas-data.json")
    q1032_in = load_json(ROOT / "experiments/2026-10-24-q1032-town-axis-register/run-v5/town-axis-table.json")
    lt_in = load_json(ROOT / "experiments/2026-10-26-indus-living-atlas/living-towns/towns.json")
    census_in = load_json(ROOT / "experiments/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/coverage.json")
    with (ROOT / "experiments/2026-10-21-post-catalogue-finds/sites.csv").open(encoding="utf-8") as f:
        pcf_in = [r for r in csv.DictReader(f) if r["site"] != "All sites"]
    with (ROOT / "experiments/2026-10-12-satellite-prospection/exports-v2/reconnaissance-register.csv").open(encoding="utf-8") as f:
        recon_in = list(csv.DictReader(f))

    missing_atlas = [s["id"] for s in atlas_in["sites"] if s["id"] not in by_id]
    q1032_matched = [r["id"] for r in records if r["q1032_register"] is not None]
    lt_matched = [r["id"] for r in records if r["living_town_review"] is not None]
    pcf_matched = [r["id"] for r in records if r["inscribed_corpus"]["post_catalogue"] is not None]
    recon_missing = [r["id"].lower() for r in recon_in if r["id"].lower() not in by_id]
    census_names_present = {r["name"] for r in records}
    missing_census = [s["site"] for s in census_in["sites"] if s["site"] not in census_names_present]

    v02_ok = (
        len(missing_atlas) == 0
        and len(missing_census) == 0
        and len(q1032_matched) == len(q1032_in["towns"])
        and len(lt_matched) == len(lt_in["records"])
        and len(pcf_matched) == len(pcf_in)
        and len(recon_missing) == 0
        and len(records) == len(by_id)
    )
    record_check(
        "V02_zero_entity_loss",
        "All 115 Atlas/Census entities, 34 Q-1032 towns, 18 Living Towns, 26 Post-Catalogue site rows, and 3 reconnaissance leads are reconciled without loss or duplicate IDs.",
        v02_ok,
        {
            "reconciled_records": len(records),
            "unique_ids": len(by_id),
            "missing_atlas": missing_atlas,
            "missing_census": missing_census,
            "q1032_matched": len(q1032_matched),
            "q1032_expected": len(q1032_in["towns"]),
            "living_towns_matched": len(lt_matched),
            "living_towns_expected": len(lt_in["records"]),
            "post_catalogue_matched": len(pcf_matched),
            "post_catalogue_expected": len(pcf_in),
            "missing_recon": recon_missing,
        },
    )

    # Check 3: Zero silent coordinate averaging and exact Haversine recomputation
    avg_violations = []
    spread_mismatches = []
    bad_precision = []
    for r in records:
        if r["primary_precision_class"] not in VALID_PRECISION_CLASSES:
            bad_precision.append(r["id"])
        assertions = r["coordinate_assertions"]
        if r["primary_lat"] is not None:
            matched_verbatim = any(
                abs(a["lat"] - r["primary_lat"]) < 1e-9 and abs(a["lon"] - r["primary_lon"]) < 1e-9
                for a in assertions
            )
            if not matched_verbatim:
                avg_violations.append(r["id"])
            prim_roles = [a for a in assertions if a["selection_role"] == "primary_retained"]
            if len(prim_roles) != 1:
                avg_violations.append(f"{r['id']}:primary_count={len(prim_roles)}")
        else:
            if len(assertions) != 0:
                avg_violations.append(f"{r['id']}:unlocated_has_assertions")

        if assertions:
            max_d = 0.0
            for i in range(len(assertions)):
                for j in range(i + 1, len(assertions)):
                    d = haversine_km(assertions[i]["lat"], assertions[i]["lon"], assertions[j]["lat"], assertions[j]["lon"])
                    if d > max_d:
                        max_d = d
            reported = r["coordinate_conflict"]["max_coord_spread_km"]
            if reported is None or abs(round(max_d, 3) - reported) > 0.002:
                spread_mismatches.append({"id": r["id"], "recomputed": round(max_d, 3), "reported": reported})

    record_check(
        "V03_no_silent_averaging_and_spread_accuracy",
        "Every primary coordinate matches a verbatim retained assertion (zero silent averaging), every precision class is valid, and all pairwise Haversine spreads match independent recomputation.",
        len(avg_violations) == 0 and len(spread_mismatches) == 0 and len(bad_precision) == 0,
        {
            "averaging_or_primary_violations": avg_violations,
            "spread_mismatches": spread_mismatches,
            "bad_precision": bad_precision,
            "checked_assertions": sum(len(r["coordinate_assertions"]) for r in records),
        },
    )

    # Check 4: Four-unit separation & excavation-status taxonomy
    unit_violations = []
    exc_violations = []
    for r in records:
        if r["unit_class"] not in VALID_UNIT_CLASSES:
            unit_violations.append(f"{r['id']}:unit_class={r['unit_class']}")
        if r["excavation_status"] not in VALID_EXCAVATION_STATUSES:
            exc_violations.append(f"{r['id']}:excavation_status={r['excavation_status']}")
        if r["domain_role"] == "remote_sensing_proposal":
            if r["unit_class"] != "physical_mound_or_scatter" or r["excavation_status"] != "remote_proposal_unverified":
                unit_violations.append(f"{r['id']}:remote_proposal_misclassified")
        if r["id"] in {"dilmun", "luristan"} and r["unit_class"] != "regional_provenance_label":
            unit_violations.append(f"{r['id']}:regional_label_misclassified")

    # Verify Ganweriwala preserves all 3 distinct area definitions and Kotada preserves 0.6 ha fortified enclosure separately
    gan_areas = sorted(pf["area_ha"] for pf in by_id["ganweriwala"]["phase_footprints"] if pf.get("area_ha") is not None)
    kot_areas = sorted(pf["area_ha"] for pf in by_id["kotada-lodrani"]["phase_footprints"] if pf.get("area_ha") is not None)
    if gan_areas != [33.0, 66.7, 81.5]:
        unit_violations.append(f"ganweriwala_areas={gan_areas}")
    if kot_areas != [0.6]:
        unit_violations.append(f"kotada_areas={kot_areas}")

    record_check(
        "V04_four_unit_and_status_separation",
        "All records enforce valid four-unit and excavation-status vocabularies; remote proposals stay separate from recorded localities; Ganweriwala and Kotada area definitions remain distinct.",
        len(unit_violations) == 0 and len(exc_violations) == 0,
        {
            "unit_violations": unit_violations,
            "excavation_status_violations": exc_violations,
            "ganweriwala_retained_areas_ha": gan_areas,
            "kotada_lodrani_retained_areas_ha": kot_areas,
        },
    )

    # Check 5: Alias integrity & homonym disambiguation
    alias_pairs = {(r["alias_string"], r["canonical_id"]) for r in alias_csv_rows}
    missing_mandatory = [pair for pair in MANDATORY_ALIASES if pair not in alias_pairs]
    # Every non-homonym normalized alias must map to exactly 1 canonical_id
    norm_map: dict[str, set[str]] = defaultdict(set)
    ambig_by_norm: dict[str, bool] = defaultdict(lambda: True)
    for r in alias_csv_rows:
        norm_map[r["normalized_alias"]].add(r["canonical_id"])
        if r["ambiguous_homonym"] != "true":
            ambig_by_norm[r["normalized_alias"]] = False
    unflagged_collisions = [
        {"normalized_alias": k, "canonical_ids": sorted(v)}
        for k, v in norm_map.items()
        if len(v) > 1 and not ambig_by_norm[k]
    ]
    kotada_rows = [r for r in alias_csv_rows if r["alias_string"] == "Kotada"]
    kotada_ok = len(kotada_rows) == 2 and all(r["ambiguous_homonym"] == "true" for r in kotada_rows)
    unknown_alias_targets = [r["canonical_id"] for r in alias_csv_rows if r["canonical_id"] not in by_id]

    record_check(
        "V05_alias_and_homonym_integrity",
        "All mandatory aliases resolve cleanly, zero unflagged cross-entity collisions exist, and homonymous Kotada entries are flagged.",
        len(missing_mandatory) == 0 and len(unflagged_collisions) == 0 and kotada_ok and len(unknown_alias_targets) == 0,
        {
            "total_alias_rows": len(alias_csv_rows),
            "missing_mandatory_aliases": missing_mandatory,
            "unflagged_collisions": unflagged_collisions,
            "kotada_homonym_rows": len(kotada_rows),
            "unknown_alias_targets": unknown_alias_targets,
        },
    )

    # Check 6: Survey-effort completeness & P01-P21 bounding-box containment recomputation
    cand_in = load_json(ROOT / "experiments/2026-10-11-settlement-prospection/candidates-v5.json")
    expected_wids = [t["id"] for t in cand_in["targets"]]
    actual_wids = [w["window_id"] for w in se["prospection_windows"]]
    bbox_mismatches = []
    bad_se_class = []
    for w in se["prospection_windows"]:
        if w["survey_effort_class"] not in VALID_SURVEY_EFFORT_CLASSES:
            bad_se_class.append(w["window_id"])
        bbox = w["bbox_lonlat"]
        min_lon, min_lat, max_lon, max_lat = bbox
        geo_ids = {
            r["id"]
            for r in records
            if r["primary_lat"] is not None
            and min_lon <= r["primary_lon"] <= max_lon
            and min_lat <= r["primary_lat"] <= max_lat
        }
        # Unlocated records explicitly assigned to this window by source provenance
        unloc_assigned = {
            r["id"]
            for r in records
            if r["primary_lat"] is None and w["window_id"] in r["prospection_window_ids"]
        }
        expected_ids = sorted(geo_ids | unloc_assigned)
        if expected_ids != w["matched_gazetteer_ids"]:
            bbox_mismatches.append(
                {
                    "window_id": w["window_id"],
                    "expected": expected_ids,
                    "actual": w["matched_gazetteer_ids"],
                }
            )

    record_check(
        "V06_survey_effort_and_window_containment",
        "All 21 prospection windows (P01-P21) have valid survey-effort classifications and exact independent bounding-box containment parity.",
        expected_wids == actual_wids and len(bbox_mismatches) == 0 and len(bad_se_class) == 0,
        {
            "windows_checked": len(actual_wids),
            "campaigns_recorded": len(se["campaigns"]),
            "bbox_mismatches": bbox_mismatches,
            "bad_survey_effort_classes": bad_se_class,
        },
    )

    # Check 7: CSV and JSON parity
    csv_ids = [r["id"] for r in gaz_csv_rows]
    json_ids = [r["id"] for r in records]
    csv_mismatches = []
    if csv_ids == json_ids:
        for cr, jr in zip(gaz_csv_rows, records):
            if cr["excavation_status"] != jr["excavation_status"]:
                csv_mismatches.append(f"{cr['id']}:exc_status")
            if cr["unit_class"] != jr["unit_class"]:
                csv_mismatches.append(f"{cr['id']}:unit_class")
            if cr["coord_conflict_tier"] != jr["coordinate_conflict"]["coord_conflict_tier"]:
                csv_mismatches.append(f"{cr['id']}:conflict_tier")
            if int(cr["coord_assertion_count"]) != jr["coordinate_conflict"]["assertion_count"]:
                csv_mismatches.append(f"{cr['id']}:assertion_count")
    parity_ok = (
        csv_ids == json_ids
        and len(csv_mismatches) == 0
        and len(records) == cov["totals"]["reconciled_records"]
        and len(alias_csv_rows) == cov["totals"]["total_alias_rows"]
    )
    record_check(
        "V07_csv_json_coverage_parity",
        "gazetteer-v1.csv, gazetteer-v1.json, aliases-v1.csv, and coverage-v1.json agree on every row ID, count, and key status column.",
        parity_ok,
        {
            "gazetteer_json_rows": len(records),
            "gazetteer_csv_rows": len(gaz_csv_rows),
            "aliases_csv_rows": len(alias_csv_rows),
            "field_mismatches": csv_mismatches,
        },
    )

    # Check 8: Redistribution hygiene (no raw MAHSA tiles or verbatim third-party page blocks in tracked outputs)
    hygiene_flags = []
    forbidden_markers = ['"nodegroup_id"', '"resourceinstance_id"', "Man and Environment XLX(2)"]
    for fname in ("gazetteer-v1.json", "gazetteer-v1.csv", "aliases-v1.csv", "survey-effort-v1.json", "coverage-v1.json"):
        text = (PKG / fname).read_text(encoding="utf-8")
        for m in forbidden_markers:
            if m in text:
                hygiene_flags.append({"file": fname, "marker": m})
    raw_extract = ROOT / "data/raw/2026-11-22-site-survey-gazetteer/raw-concordance-extract-v1.json"
    record_check(
        "V08_redistribution_hygiene",
        "Tracked outputs contain no raw third-party MAHSA tile payloads or verbatim page dumps, and local-only extract exists under data/raw/.",
        len(hygiene_flags) == 0 and raw_extract.exists(),
        {"hygiene_flags": hygiene_flags, "local_raw_extract_exists": raw_extract.exists()},
    )

    all_passed = all(c["passed"] for c in checks)
    report = {
        "schema_version": "1.0",
        "verified_date": "2026-11-22",
        "overall_passed": all_passed,
        "checks_passed": sum(1 for c in checks if c["passed"]),
        "checks_total": len(checks),
        "checks": checks,
    }
    out_path = PKG / "verification-v1.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run_checks()
    print(json.dumps({"overall_passed": result["overall_passed"], "checks_passed": result["checks_passed"], "checks_total": result["checks_total"]}, indent=2))
    for c in result["checks"]:
        status = "PASS" if c["passed"] else "FAIL"
        print(f"  [{status}] {c['check_id']}: {c['description']}")
    if not result["overall_passed"]:
        raise SystemExit(1)
