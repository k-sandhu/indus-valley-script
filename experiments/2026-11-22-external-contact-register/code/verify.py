"""Independent verification for the external contact register (Issue #22).

Does NOT import build_register.py. Independently re-reads raw source files,
recomputes SHA-256 digests, checks schema completeness, enforces zero conflation
between Cohort 1 and Cohort 2, checks every CDLI P-number against cdli_cat.csv
(and ORACC archives when absent from the 2022 CDLI CSV), checks exclusion
integrity, and recomputes all summary counts of personal names, titles,
commodities, and associated seals.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments" / "2026-11-22-external-contact-register"
RAW_OUT_DIR = ROOT / "data" / "raw" / "2026-11-22-external-contact-register"

REQUIRED_FIELDS = [
    "record_id",
    "cohort",
    "region",
    "carrier",
    "is_composite",
    "museum_accession",
    "cdli_or_bdtn_id",
    "excavated_locus",
    "date_period",
    "script_and_language",
    "primary_edition",
    "edited_transliteration_status",
    "goods_and_units",
    "personal_names",
    "titles_and_offices",
    "associated_seals",
    "indus_contact_evidence_class",
    "source_dependence",
    "source_sha256",
]

COHORT_1_CLASSES = {
    "explicit_meluhha_mention",
    "susa_sealed_transaction",
    "gulf_indus_style_seal",
    "dilmun_named_seal",
}
COHORT_2_CLASSES = {"later_control"}
FORBIDDEN_COHORT_1_PERIODS = (
    "Neo-Assyrian",
    "Neo-Babylonian",
    "Middle Babylonian",
    "Achaemenid",
    "Roman period",
    "Early Historic",
)
EXCLUDED_FALSE_POSITIVE_PIDS = {"P135796", "P257207", "P346234"}
EXCLUDED_LATER_SAMPLE_PIDS = {"P313081", "P348413", "P285444", "P511661", "P511663"}
EXCLUDED_COMPOSITE_SEAL_PIDS = {
    "P454287", "P454462", "P454557", "P455175", "P455176", "P455398",
    "P456915", "P456940", "P458223", "P458495", "P458515", "P458708",
    "P507624", "P507625", "P507626", "P507627",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    register = json.loads((EXP_DIR / "register-v1.json").read_text(encoding="utf-8"))
    summary = json.loads((EXP_DIR / "summary-v1.json").read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = register["records"]

    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    # 1. Independently recompute all source SHA-256 hashes and byte counts
    recomputed_hashes: dict[str, str] = {}
    hash_mismatches: list[str] = []
    for key, info in summary["source_inputs"].items():
        rel = info["logical_path"]
        fp = ROOT / rel
        if not fp.exists():
            hash_mismatches.append(f"missing:{rel}")
            continue
        actual_bytes = fp.stat().st_size
        actual_sha = sha256_file(fp)
        recomputed_hashes[rel] = actual_sha
        if actual_bytes != info["bytes"] or actual_sha != info["sha256"]:
            hash_mismatches.append(f"mismatch:{rel}")

    record_hash_errors: list[str] = []
    for rec in records:
        smap = rec.get("source_sha256", {})
        if not smap:
            record_hash_errors.append(f"empty_source_sha256:{rec.get('record_id')}")
        for rel, digest in smap.items():
            if recomputed_hashes.get(rel) != digest:
                record_hash_errors.append(f"bad_record_hash:{rec.get('record_id')}:{rel}")

    add_check(
        "source_sha256_integrity",
        len(hash_mismatches) == 0 and len(record_hash_errors) == 0,
        {
            "sources_checked": len(summary["source_inputs"]),
            "source_mismatches": hash_mismatches,
            "record_hash_errors": record_hash_errors[:10],
        },
    )

    # 2. Schema completeness and unique IDs
    missing_fields: list[str] = []
    seen_ids: set[str] = set()
    dup_ids: list[str] = []
    for rec in records:
        rid = rec.get("record_id", "")
        if rid in seen_ids:
            dup_ids.append(rid)
        seen_ids.add(rid)
        for field in REQUIRED_FIELDS:
            if field not in rec:
                missing_fields.append(f"{rid}:{field}")

    add_check(
        "schema_and_unique_ids",
        len(missing_fields) == 0 and len(dup_ids) == 0 and len(records) > 0,
        {
            "total_records": len(records),
            "missing_fields": missing_fields[:10],
            "duplicate_ids": dup_ids,
        },
    )

    # 3. Strict Cohort 1 vs Cohort 2 separation (zero conflation)
    cohort_violations: list[str] = []
    for rec in records:
        rid = rec["record_id"]
        cohort = rec["cohort"]
        eclass = rec["indus_contact_evidence_class"]
        per = rec["date_period"]
        if cohort == "cohort_1_contemporary":
            if eclass not in COHORT_1_CLASSES:
                cohort_violations.append(f"{rid}:c1_bad_class:{eclass}")
            for forb in FORBIDDEN_COHORT_1_PERIODS:
                if forb.lower() in per.lower():
                    cohort_violations.append(f"{rid}:c1_forbidden_period:{forb}")
        elif cohort == "cohort_2_later_control":
            if eclass not in COHORT_2_CLASSES:
                cohort_violations.append(f"{rid}:c2_bad_class:{eclass}")
        else:
            cohort_violations.append(f"{rid}:unknown_cohort:{cohort}")

    add_check(
        "cohort_1_vs_cohort_2_zero_conflation",
        len(cohort_violations) == 0,
        {"violations": cohort_violations},
    )

    # 4. Exact CDLI P-number verification against cdli_cat.csv (and ORACC Ur III if newer than 2022 dump)
    cdli_pids_in_register: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for rec in records:
        cid = rec.get("cdli_or_bdtn_id") or ""
        for m in re.findall(r"\bP\d{6}\b", cid):
            cdli_pids_in_register[m].append(rec)

    cat_path = ROOT / "data/raw/2026-10-21-head-direction-corpora/src-cdli-data-cat-v1/cdli_cat.csv"
    found_in_cdli_cat: dict[str, dict[str, str]] = {}
    with cat_path.open("r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            id_text = row.get("id_text", "").strip()
            if id_text.isdigit():
                pid = "P" + id_text.zfill(6)
                if pid in cdli_pids_in_register:
                    found_in_cdli_cat[pid] = row

    missing_from_cdli_cat = sorted(set(cdli_pids_in_register.keys()) - set(found_in_cdli_cat.keys()))
    found_in_oracc_fallback: list[str] = []
    truly_missing_pids: list[str] = []
    if missing_from_cdli_cat:
        ur3_zip = ROOT / "data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin"
        with zipfile.ZipFile(ur3_zip) as z:
            ur3_cat = json.loads(z.read("epsd2/admin/ur3/catalogue.json")).get("members", {})
        for pid in missing_from_cdli_cat:
            if pid in ur3_cat:
                found_in_oracc_fallback.append(pid)
            else:
                truly_missing_pids.append(pid)

    # Verify Susa P-numbers really have Susa + Ur III in cdli_cat, and Dilmun P-numbers really have Bahrain/Dilmun
    metadata_mismatches: list[str] = []
    for pid, recs in cdli_pids_in_register.items():
        crow = found_in_cdli_cat.get(pid)
        if not crow:
            continue
        for rec in recs:
            if rec["indus_contact_evidence_class"] == "susa_sealed_transaction":
                if "Susa" not in crow.get("provenience", "") or "Ur III" not in crow.get("period", ""):
                    metadata_mismatches.append(f"{pid}:not_susa_ur3")
            elif rec["indus_contact_evidence_class"] == "dilmun_named_seal":
                if "Bahrain" not in crow.get("provenience", "") and "Dilmun" not in crow.get("provenience", ""):
                    metadata_mismatches.append(f"{pid}:not_dilmun_bahrain")
            elif pid == "P525331":
                if crow.get("museum_no") != "AO 22310":
                    metadata_mismatches.append(f"{pid}:museum_no_mismatch")

    add_check(
        "cdli_pnumber_and_metadata_lookup",
        len(truly_missing_pids) == 0 and len(metadata_mismatches) == 0,
        {
            "total_unique_cdli_pids": len(cdli_pids_in_register),
            "verified_in_cdli_cat": len(found_in_cdli_cat),
            "verified_in_oracc_ur3_fallback": found_in_oracc_fallback,
            "missing_pids": truly_missing_pids,
            "metadata_mismatches": metadata_mismatches,
        },
    )

    # 5. Exclusion and anti-double-counting checks
    all_pids = set(cdli_pids_in_register.keys())
    all_cat_strings = " ".join((r.get("cdli_or_bdtn_id") or "") for r in records)
    fp_leaks = sorted(all_pids & EXCLUDED_FALSE_POSITIVE_PIDS)
    later_leaks = sorted(all_pids & EXCLUDED_LATER_SAMPLE_PIDS)
    comp_leaks = sorted(all_pids & EXCLUDED_COMPOSITE_SEAL_PIDS)
    dup_6000_leak = "Lipi 6000.1" in all_cat_strings

    add_check(
        "exclusion_and_deduplication_integrity",
        len(fp_leaks) == 0 and len(later_leaks) == 0 and len(comp_leaks) == 0 and not dup_6000_leak,
        {
            "false_positive_leaks": fp_leaks,
            "later_period_sample_leaks": later_leaks,
            "composite_seal_or_dilmun_composite_leaks": comp_leaks,
            "lipi_6000_1_duplicate_leak": dup_6000_leak,
        },
    )

    # 6. Independent recomputation of all counts and CSV consistency
    c1 = [r for r in records if r["cohort"] == "cohort_1_contemporary"]
    c2 = [r for r in records if r["cohort"] == "cohort_2_later_control"]
    mel = [r for r in c1 if r["indus_contact_evidence_class"] == "explicit_meluhha_mention"]
    recomputed_counts = {
        "total_records": len(records),
        "cohort_1_contemporary_total": len(c1),
        "cohort_1_contemporary_physical": sum(1 for r in c1 if not r["is_composite"]),
        "cohort_1_contemporary_composite_editions": sum(1 for r in c1 if r["is_composite"]),
        "cohort_2_later_control_total": len(c2),
        "by_evidence_class_total": dict(collections.Counter(r["indus_contact_evidence_class"] for r in records)),
        "by_evidence_class_physical": dict(collections.Counter(r["indus_contact_evidence_class"] for r in records if not r["is_composite"])),
        "by_evidence_class_composite": dict(collections.Counter(r["indus_contact_evidence_class"] for r in records if r["is_composite"])),
        "cohort_1_records_with_associated_seals": sum(1 for r in c1 if r["associated_seals"]),
        "meluhha_records_with_associated_seals": sum(1 for r in mel if r["associated_seals"]),
        "cohort_1_unique_goods_and_units": len({g for r in c1 for g in r["goods_and_units"]}),
        "cohort_1_unique_titles_and_offices": len({t for r in c1 for t in r["titles_and_offices"]}),
        "cohort_1_unique_personal_names": len({p for r in c1 for p in r["personal_names"]}),
        "meluhha_unique_goods_and_units": len({g for r in mel for g in r["goods_and_units"]}),
        "meluhha_unique_titles_and_offices": len({t for r in mel for t in r["titles_and_offices"]}),
        "meluhha_unique_personal_names": len({p for r in mel for p in r["personal_names"]}),
    }
    count_mismatches = {}
    for k, v in recomputed_counts.items():
        if summary["counts"].get(k) != v:
            count_mismatches[k] = {"summary": summary["counts"].get(k), "recomputed": v}

    with (EXP_DIR / "meluhha-commodities-titles-v1.csv").open("r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    csv_ids = {r["record_id"] for r in csv_rows}
    mel_ids = {r["record_id"] for r in mel}
    csv_match = len(csv_rows) == len(mel) and csv_ids == mel_ids

    add_check(
        "aggregate_counts_and_csv_consistency",
        len(count_mismatches) == 0 and csv_match,
        {
            "recomputed_counts": recomputed_counts,
            "count_mismatches": count_mismatches,
            "meluhha_csv_rows": len(csv_rows),
            "meluhha_csv_matches_register": csv_match,
        },
    )

    # 7. Verify local-only D: derivative files exist
    expected_local = [
        "atf-excerpts-local-v1.jsonl",
        "excluded-records-audit-v1.json",
        "source-hashes-v1.json",
    ]
    local_status = {}
    for fname in expected_local:
        fp = RAW_OUT_DIR / fname
        local_status[fname] = {
            "exists": fp.exists(),
            "bytes": fp.stat().st_size if fp.exists() else 0,
            "physical_path": str(fp.resolve()),
        }
    local_ok = all(v["exists"] and v["bytes"] > 0 for v in local_status.values())
    add_check("local_raw_derivatives_on_d_drive", local_ok, local_status)

    all_passed = all(c["passed"] for c in checks)
    output = {
        "schema_version": "1.0",
        "date": "2026-11-22",
        "all_passed": all_passed,
        "checks_passed": sum(1 for c in checks if c["passed"]),
        "checks_total": len(checks),
        "checks": checks,
    }
    (EXP_DIR / "verification-v1.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Verification complete: {output['checks_passed']}/{output['checks_total']} passed (all_passed={all_passed})")
    for c in checks:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}")
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
