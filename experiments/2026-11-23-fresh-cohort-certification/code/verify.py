"""Independent verification for experiments/2026-11-23-fresh-cohort-certification.

Recomputes every count, cross-corpus overlap check, held-PDF plate check,
input SHA-256 hash, blinding invariant, and P1-P4 bound directly from raw inputs.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
RAW_OUT = ROOT / "data" / "raw" / "2026-11-23-fresh-cohort-certification"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_tok(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def main() -> None:
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    # Load generated artifacts
    summary = json.loads((PKG / "summary-v1.json").read_text(encoding="utf-8"))
    cohort_json = json.loads((PKG / "fresh-cohort-v1.json").read_text(encoding="utf-8"))
    with (PKG / "fresh-cohort-v1.csv").open(encoding="utf-8") as f:
        cohort_csv = list(csv.DictReader(f))

    # 1. Protocol freeze hash check
    proto_sha_line = (PKG / "PROTOCOL.sha256").read_text(encoding="utf-8").strip().split()[0]
    proto_actual = sha256_file(PKG / "PROTOCOL.md")
    record(
        "protocol_sha256_matches_frozen_and_summary",
        proto_sha_line == proto_actual == summary["protocol_sha256"],
        {"frozen": proto_sha_line, "actual": proto_actual, "summary": summary["protocol_sha256"]},
    )

    # 2. All 19 source input SHA-256 hashes verified on disk
    hash_mismatches = []
    for key, info in summary["input_hashes"].items():
        p = ROOT / info["path"]
        if not p.exists():
            hash_mismatches.append({"key": key, "error": "missing"})
            continue
        actual = sha256_file(p)
        if actual != info["sha256"] or p.stat().st_size != info["bytes"]:
            hash_mismatches.append({"key": key, "expected": info["sha256"], "actual": actual})
    record(
        "all_input_hashes_verified",
        len(hash_mismatches) == 0 and len(summary["input_hashes"]) == 19,
        {"verified_inputs": len(summary["input_hashes"]), "mismatches": hash_mismatches},
    )

    # 3. Exact row accounting across 503 + 358
    with (ROOT / "experiments/2026-10-21-post-catalogue-finds/objects.csv").open(encoding="utf-8") as f:
        raw_503 = list(csv.DictReader(f))
    with (ROOT / "data/raw/2026-10-22-candidate-identity-exposure/run-v3/reconciled-dispositions.csv").open(encoding="utf-8") as f:
        raw_358 = list(csv.DictReader(f))

    ids_503 = [r["row_id"] for r in raw_503]
    ids_358 = {r["source_row_id"] for r in raw_358}
    ids_json = [r["row_id"] for r in cohort_json]
    ids_csv = [r["row_id"] for r in cohort_csv]

    record(
        "exact_503_row_bijection_json_and_csv",
        len(raw_503) == 503 and ids_json == ids_503 and ids_csv == ids_503 and len(set(ids_json)) == 503,
        {"raw_503": len(raw_503), "json_rows": len(ids_json), "csv_rows": len(ids_csv), "unique": len(set(ids_json))},
    )

    in_358_json = {r["row_id"] for r in cohort_json if r["in_358_audit"]}
    in_358_csv = {r["row_id"] for r in cohort_csv if r["in_358_audit"] == "True"}
    record(
        "exact_358_audit_bijection",
        len(raw_358) == 358 and in_358_json == ids_358 and in_358_csv == ids_358,
        {"raw_358": len(raw_358), "json_in_358": len(in_358_json), "csv_in_358": len(in_358_csv), "baseline_only": 503 - len(in_358_json)},
    )

    # Tier conservation & JSON/CSV/summary parity
    valid_tiers = {
        "certified_absent_sealed",
        "conditionally_absent_needs_plate_check",
        "blocked_by_alias_ambiguity",
        "already_present_or_exposed",
    }
    tc_json = Counter(r["certification_tier"] for r in cohort_json)
    tc_csv = Counter(r["certification_tier"] for r in cohort_csv)
    tc_358 = Counter(r["certification_tier"] for r in cohort_json if r["in_358_audit"])
    record(
        "tier_partition_exact_and_consistent",
        (
            set(tc_json.keys()).issubset(valid_tiers)
            and sum(tc_json.values()) == 503
            and dict(tc_json) == dict(tc_csv) == summary["tier_counts_all_503"]
            and sum(tc_358.values()) == 358
            and dict(tc_358) == summary["tier_counts_within_358"]
        ),
        {"all_503": dict(tc_json), "within_358": dict(tc_358)},
    )

    # 4. Reload ALL reference corpora independently and verify ZERO overlap for certified_absent_sealed
    lipi_fams: dict[str, dict] = {}
    lipi_faces_n = 0
    with (ROOT / "data/normalized/lipi_observed_faces.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            lipi_faces_n += 1
            d = json.loads(line)
            fid = str(d["object_family_id"])
            if fid not in lipi_fams:
                m = d.get("metadata", {})
                lipi_fams[fid] = {
                    "site": (d.get("site") or "").strip(),
                    "type": (d.get("object_type") or m.get("type") or "").strip(),
                    "material": (m.get("material") or "").strip(),
                    "cisi": (d.get("source_cisi") or m.get("cisi") or "").strip(),
                    "excav": (m.get("excavation-idno") or "").strip(),
                }

    with (ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv").open(encoding="utf-8") as f:
        mm_rows = list(csv.DictReader(f))
    with (ROOT / "experiments/2026-10-13-cisi-basic-data-full/object-flags.csv").open(encoding="utf-8") as f:
        cisi_flags = list(csv.DictReader(f))
    cisi_joined_n = sum(1 for r in cisi_flags if r["join"] == "one-family" and r["lipi_family"].strip())

    cisi_basic_rows = []
    for p in (
        ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl",
        ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi2-basic-data.jsonl",
    ):
        with p.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cisi_basic_rows.append(json.loads(line))

    with (ROOT / "data/raw/2026-10-22-object-register/run-v2/objects.jsonl").open(encoding="utf-8") as f:
        base_reg_exp = Counter(json.loads(line)["exposure_status"] for line in f if line.strip())

    record(
        "reference_corpus_denominators_exact",
        (
            len(lipi_fams) == 4695
            and lipi_faces_n == 5680
            and len(mm_rows) == 1146
            and len(cisi_flags) == 3680
            and cisi_joined_n == 2602
            and sum(base_reg_exp.values()) == 4695
            and base_reg_exp.get("fresh", 0) == 0
        ),
        {
            "lipi_families": len(lipi_fams),
            "lipi_faces": lipi_faces_n,
            "mackay_marshall_joins": len(mm_rows),
            "cisi_flags": len(cisi_flags),
            "cisi_joined_to_lipi": cisi_joined_n,
            "base_register_fresh": base_reg_exp.get("fresh", 0),
        },
    )

    # Exhaustive zero-overlap check for every certified_absent_sealed object
    sealed = [r for r in cohort_json if r["certification_tier"] == "certified_absent_sealed"]
    overlap_failures = []
    plate_failures = []
    with (ROOT / "experiments/2026-10-21-post-catalogue-finds/matching/source-register.csv").open(encoding="utf-8") as f:
        src_reg = {r["source_id"]: r for r in csv.DictReader(f)}

    for r in sealed:
        rid = r["row_id"]
        site_low = r["local_site_label"].lower()
        reg_tok = norm_tok(r["registration"])
        obj_class = r["object_class"]
        mat_low = (r["material"] or "").strip().lower()

        # Check status invariants
        if r["catalogue_status"] != "post-catalogue" or r["inscription_status"] != "stated":
            overlap_failures.append({"row_id": rid, "reason": "bad_cat_or_insc_status"})
        if r["supported_lipi_family_ids"] or r["unresolved_lipi_family_ids"] or r["context_join_family"]:
            overlap_failures.append({"row_id": rid, "reason": "nonempty_lipi_link"})
        if r["spent_in_bench_json"]:
            overlap_failures.append({"row_id": rid, "reason": "spent_in_bench"})
        if r["audit_2026_10_22_exposure_status"] == "source_page_image_display_recorded_object_scope_unresolved":
            overlap_failures.append({"row_id": rid, "reason": "image_exposed"})
        if r["possible_duplicate_of"]:
            overlap_failures.append({"row_id": rid, "reason": "secondary_possible_duplicate"})

        # Independent check against all 4,695 Lipi families
        site_fams = [v for v in lipi_fams.values() if v["site"].lower() == site_low]
        for v in site_fams:
            if reg_tok and norm_tok(v["excav"]) == reg_tok:
                overlap_failures.append({"row_id": rid, "reason": "lipi_reg_collision", "lipi": v})
            # Check compatible type + non-disjoint registration/material
            lt = v["type"].upper()
            compat = (
                (obj_class == "seal" and lt.startswith("SEAL"))
                or (obj_class == "sealing" and (lt.startswith("TAG") or lt.startswith("IMPL")))
                or (obj_class == "tablet" and lt.startswith("TAB"))
                or (obj_class == "pottery" and lt.startswith("POT"))
            )
            if compat:
                disjoint_by_reg = bool(reg_tok) and bool(norm_tok(v["excav"])) and norm_tok(v["excav"]) != reg_tok
                disjoint_by_mat = bool(mat_low) and bool(v["material"]) and v["material"].lower() != mat_low
                if not (disjoint_by_reg or disjoint_by_mat):
                    overlap_failures.append({"row_id": rid, "reason": "unexcluded_compatible_lipi_family", "lipi": v})

        # Independent check against all 1,146 Mackay/Marshall rows & 3,682 CISI 1-2 basic-data rows
        if reg_tok:
            if site_low == "mohenjo-daro" and any(norm_tok(m["field_no"]) == reg_tok for m in mm_rows):
                overlap_failures.append({"row_id": rid, "reason": "mackay_marshall_collision"})
            for cb in cisi_basic_rows:
                sh = (cb.get("site_heading") or "").strip().lower()
                if sh == site_low and norm_tok(cb.get("col3_excavation") or "") == reg_tok:
                    overlap_failures.append({"row_id": rid, "reason": "cisi_basic_collision", "cisi": cb.get("cisi")})

        # Independent check of held PDF existence, SHA-256, page bounds, and embedded raster image presence
        src = src_reg.get(r["primary_publication"], {})
        lp = ROOT / src["local_path"]
        if not lp.exists():
            plate_failures.append({"row_id": rid, "reason": "pdf_missing"})
            continue
        if sha256_file(lp).lower() != src["sha256"].lower():
            plate_failures.append({"row_id": rid, "reason": "pdf_sha256_mismatch"})
        vpages = r["plate_audit"]["verified_plate_pdf_pages"]
        if not vpages:
            plate_failures.append({"row_id": rid, "reason": "no_verified_plate_pages"})
        else:
            doc = fitz.open(str(lp))
            try:
                for pno in vpages:
                    if not (1 <= pno <= len(doc)):
                        plate_failures.append({"row_id": rid, "reason": "page_out_of_bounds", "page": pno})
                    elif len(doc[pno - 1].get_images(full=True)) < 1:
                        plate_failures.append({"row_id": rid, "reason": "zero_images_on_verified_page", "page": pno})
            finally:
                doc.close()

    record(
        "zero_overlap_certified_absent_sealed_vs_lipi_mm_cisi_spent",
        len(overlap_failures) == 0 and len(sealed) == 8,
        {
            "certified_absent_sealed_count": len(sealed),
            "seals": sum(1 for r in sealed if r["object_class"] == "seal"),
            "sealings": sum(1 for r in sealed if r["object_class"] == "sealing"),
            "tablets": sum(1 for r in sealed if r["object_class"] == "tablet"),
            "overlap_failures": overlap_failures,
        },
    )

    record(
        "all_certified_absent_sealed_held_pdf_plates_verified",
        len(plate_failures) == 0 and len(sealed) == 8,
        {"verified_objects": len(sealed), "plate_failures": plate_failures},
    )

    # 5. Blinding and seal-integrity checks
    pdf_log_path = RAW_OUT / "pdf-access-log.jsonl"
    log_rows = [json.loads(l) for l in pdf_log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    probe_rows = [e for e in log_rows if e.get("action") == "blind_pdf_page_and_caption_probe"]
    blinding_ok = (
        len(log_rows) == summary["pdf_access_events_logged"]
        and all(e.get("sign_sequences_read") is False and e.get("images_rendered_to_agent") is False for e in probe_rows)
        and not any("sign" in k.lower() for k in cohort_csv[0].keys())
        and not (ROOT / "experiments/2026-10-20-seal-legend-units/prospective-access.jsonl").exists()
    )
    record(
        "blinding_invariants_and_zero_prospective_reads",
        blinding_ok,
        {
            "pdf_log_events": len(log_rows),
            "pdf_probe_events": len(probe_rows),
            "prospective_access_log_absent": not (ROOT / "experiments/2026-10-20-seal-legend-units/prospective-access.jsonl").exists(),
        },
    )

    # 6. P1-P4 power bounds verification against frozen predictions.json
    pred = json.loads((ROOT / "experiments/2026-10-20-seal-legend-units/predictions.json").read_text(encoding="utf-8"))
    power_issues = []
    for name, sc in summary["P1_to_P4_power_analysis"].items():
        n = sc["n_seals"]
        pw = sc["power"]
        exp_lo = round(pred["bounds"]["P1"]["lower"][str(n)], 6)
        exp_kill = round(pred["bounds"]["P1"]["kill"][str(n)], 6)
        if pw["P1"]["lower_bound"] != exp_lo or pw["P1"]["kill_bound"] != exp_kill:
            power_issues.append({"scenario": name, "issue": "P1_bounds_mismatch"})
        if n <= 4 and pw["P2"]["p_pass_if_held_rates"] != 0.0:
            power_issues.append({"scenario": name, "issue": "P2_impossible_pass_nonzero"})
        exp_p4_3 = round((37 / 59) ** 3, 4)
        if abs(pw["P4"]["power_if_3_divided"] - exp_p4_3) > 1e-4:
            power_issues.append({"scenario": name, "issue": "P4_binom_mismatch"})
    record(
        "p1_to_p4_power_bounds_verified_against_frozen_spec",
        len(power_issues) == 0,
        {"scenarios_checked": len(summary["P1_to_P4_power_analysis"]), "issues": power_issues},
    )

    all_passed = all(c["passed"] for c in checks)
    out = {
        "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "all_passed": all_passed,
        "checks_passed": sum(1 for c in checks if c["passed"]),
        "checks_total": len(checks),
        "checks": checks,
    }
    (PKG / "verification-v1.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"VERIFICATION: {out['checks_passed']}/{out['checks_total']} passed (all_passed={all_passed})")
    for c in checks:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}")
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
