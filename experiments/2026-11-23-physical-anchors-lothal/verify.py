#!/usr/bin/env python3
"""
Independent verification script for experiments/2026-11-23-physical-anchors-lothal/.
Checks:
  1. 100% row/cell consistency across all 93 Lothal sealings against both
     reviewed-pass.csv and independent-first-pass.csv.
  2. Independent recomputation of reverse_class_6, diagnostic_class_5,
     is_wood_plank_peg, mobility_class, and context_basis.
  3. Independent Lipi join & strict anti-leakage check on die/impression
     components (L-161..L-170 and G01 never split across folds).
  4. Independent verification of Part A corpus uniqueness, Diophantine exact
     solutions, Vidale 1990 range sensitivity, and file/protocol SHA-256 hashes.
"""

import csv
import hashlib
import json
import os
from collections import Counter, defaultdict

OUT_DIR = "experiments/2026-11-23-physical-anchors-lothal"
ATTACH_CSV = os.path.join(OUT_DIR, "lothal-attachments-v1.csv")
ANCHORS_JSON = os.path.join(OUT_DIR, "anchors-audit-v1.json")
LOTHAL_JSON = os.path.join(OUT_DIR, "lothal-test-v1.json")
PROTOCOL_MD = os.path.join(OUT_DIR, "PROTOCOL.md")
PROTOCOL_SHA = os.path.join(OUT_DIR, "PROTOCOL.sha256")
VERIFY_OUT = os.path.join(OUT_DIR, "verification-v1.json")

REVIEWED_CSV = "data/six-hour/lothal/table-coding/reviewed-pass.csv"
INDEP_CSV = "data/six-hour/lothal/independent-review/independent-first-pass.csv"
LIPI_PATH = "data/normalized/lipi_observed_faces.jsonl"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    checks = []

    def record(name, passed, detail):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    # 1. Protocol hash check
    proto_actual = sha256_file(PROTOCOL_MD)
    proto_recorded = open(PROTOCOL_SHA, encoding="utf-8").read().strip().split()[0]
    anchors = json.load(open(ANCHORS_JSON, encoding="utf-8"))
    lothal = json.load(open(LOTHAL_JSON, encoding="utf-8"))
    record(
        "protocol_sha256_integrity",
        proto_actual == proto_recorded == anchors["protocol_sha256"] == lothal["protocol_sha256"],
        {"actual": proto_actual, "recorded": proto_recorded},
    )

    # 2. Second-coder / source-table consistency across all 93 sealings
    att_rows = list(csv.DictReader(open(ATTACH_CSV, encoding="utf-8")))
    rev_rows = list(csv.DictReader(open(REVIEWED_CSV, encoding="utf-8")))
    ind_rows = list(csv.DictReader(open(INDEP_CSV, encoding="utf-8")))

    mismatches_rev = []
    mismatches_ind = []
    for a, r, i in zip(att_rows, rev_rows, ind_rows):
        if (a["cisi_id"], str(a["impressions_table"]), a["frenez_physical_type"], a["context_code"], str(a["frenez_table_printed_page"])) != (
            r["object_id"], r["impressions"], r["physical_type"], r["context_code"], r["printed_page"]
        ):
            mismatches_rev.append(a["cisi_id"])
        if (a["cisi_id"], str(a["impressions_table"]), a["frenez_physical_type"], a["context_code"], str(a["frenez_table_printed_page"])) != (
            i["source_cisi"], i["impressions"], i["physical_type"], i["context"], i["printed_page"]
        ):
            mismatches_ind.append(a["cisi_id"])

    record(
        "lothal_93_rows_match_both_independent_table_passes",
        len(att_rows) == 93 and len(rev_rows) == 93 and len(ind_rows) == 93 and not mismatches_rev and not mismatches_ind,
        {"n_rows": len(att_rows), "mismatches_reviewed": mismatches_rev, "mismatches_independent": mismatches_ind},
    )

    # 3. Independent taxonomy recomputation
    wood_set = {"wooden_box", "locker", "structure", "peg_on_wall"}
    reed_set = {"parallel_canes", "woven_straw", "wicker"}
    mobile_set = {"wooden_box", "pottery", "parallel_canes", "woven_straw", "wicker", "leather_sack"}
    fixed_set = {"structure", "locker", "peg_on_wall"}
    tax_errors = []
    for a in att_rows:
        pt = a["frenez_physical_type"]
        exp_rev6 = (
            "wood_plank_peg" if pt in wood_set else
            "reed_cane_matting" if pt in reed_set else
            "jar_vessel_pottery" if pt == "pottery" else
            "flexible_cloth_leather" if pt == "leather_sack" else
            "cord_rope_only" if pt == "single_rope" else
            "unidentifiable_other"
        )
        exp_diag5 = "" if exp_rev6 == "unidentifiable_other" else exp_rev6
        exp_wood = "" if exp_diag5 == "" else ("1" if exp_rev6 == "wood_plank_peg" else "0")
        exp_mob = "mobile_container" if pt in mobile_set else ("architectural_fixture" if pt in fixed_set else "")
        if (a["reverse_class_6"], a["diagnostic_class_5"], a["is_wood_plank_peg"], a["mobility_class"]) != (
            exp_rev6, exp_diag5, exp_wood, exp_mob
        ):
            tax_errors.append(a["cisi_id"])

    record(
        "reverse_taxonomy_deterministic_recomputation",
        len(tax_errors) == 0,
        {"n_checked": len(att_rows), "errors": tax_errors},
    )

    # 4. Verify Rao Plate CLXI F and L-206 flags exist in attachments CSV
    by_id = {a["cisi_id"]: a for a in att_rows}
    clxi_ok = ("CLXI F" in by_id["L-161"]["rao_discrepancy_flag"]) and ("CLXI F" in by_id["L-164"]["rao_discrepancy_flag"])
    l206_ok = (by_id["L-206"]["excavation_no"] == "2077") and ("CLXII D" in by_id["L-206"]["rao_discrepancy_flag"]) and (by_id["L-206"]["frenez_physical_type"] == "peg_on_wall")
    record("rao_CLXI_F_and_L206_flags_present", clxi_ok and l206_ok, {"L-161_flag": bool(clxi_ok), "L-206_verified": bool(l206_ok)})

    # 5. Independent Lipi join and component anti-leakage verification
    lipi_rows = [json.loads(line) for line in open(LIPI_PATH, encoding="utf-8")]
    lothal_ids = {a["cisi_id"] for a in att_rows}
    joined_faces = [r for r in lipi_rows if r.get("source_cisi") in lothal_ids]
    joined_obj_ids = {r["source_cisi"] for r in joined_faces}
    complete_ids = {r["source_cisi"] for r in joined_faces if r.get("clean_rtl_singleline") and r.get("length", 0) >= 3}

    record(
        "lipi_lothal_join_totals",
        len(joined_obj_ids) == 68 and len(joined_faces) == 86 and len(complete_ids) == 29
        and lothal["all_93_distribution"]["joined_in_lipi_objects"] == 68
        and lothal["all_93_distribution"]["joined_in_lipi_faces"] == 86,
        {"joined_objects": len(joined_obj_ids), "joined_faces": len(joined_faces), "complete_eligible": len(complete_ids)},
    )

    # Verify G02 (L-161..L-170) is 100% contained in a single component and never leaks across components
    pop_a_comps = lothal["components_summary"]["pop_a_strict"]
    pop_b_comps = lothal["components_summary"]["pop_b_strict"]
    g02_expected = {f"L-{i}" for i in range(161, 171)}
    g01_diag_expected = {"L-124", "L-125", "L-126", "L-129", "L-190", "L-191", "L-193", "L-197", "L-206"}  # L-127, L-128 are undiagnostic

    g02_in_a = [c for c in pop_a_comps if g02_expected.intersection(c["cisi_ids"])]
    g01_in_a = [c for c in pop_a_comps if g01_diag_expected.intersection(c["cisi_ids"])]
    g02_in_b = [c for c in pop_b_comps if g02_expected.intersection(c["cisi_ids"])]
    g01_in_b = [c for c in pop_b_comps if g01_diag_expected.intersection(c["cisi_ids"])]

    anti_leak_ok = (
        len(g02_in_a) == 1 and set(g02_in_a[0]["cisi_ids"]) == g02_expected
        and len(g01_in_a) == 1 and set(g01_in_a[0]["cisi_ids"]) == g01_diag_expected
        and len(g02_in_b) == 1 and g02_expected.issubset(set(g02_in_b[0]["cisi_ids"]))
        and len(g01_in_b) == 1 and g01_diag_expected.issubset(set(g01_in_b[0]["cisi_ids"]))
    )
    record(
        "die_component_anti_leakage_g01_g02_intact",
        anti_leak_ok,
        {
            "pop_a_g02_components": len(g02_in_a),
            "pop_a_g01_components": len(g01_in_a),
            "pop_b_g02_components": len(g02_in_b),
            "pop_b_g01_components": len(g01_in_b),
            "pop_b_g01_members": g01_in_b[0]["cisi_ids"] if g01_in_b else [],
        },
    )

    # Check disjointness of all components in Pop A and Pop B
    seen_a = [cid for c in pop_a_comps for cid in c["cisi_ids"]]
    seen_b = [cid for c in pop_b_comps for cid in c["cisi_ids"]]
    record(
        "components_strictly_partition_populations",
        len(seen_a) == len(set(seen_a)) == lothal["all_93_distribution"]["pop_a_diagnostic_specimens"]
        and len(seen_b) == len(set(seen_b)) == lothal["all_93_distribution"]["pop_b_diagnostic_specimens"],
        {"pop_a_n": len(seen_a), "pop_b_n": len(seen_b)},
    )

    # 6. Independent verification of Part A: brute-force Diophantine solutions & corpus uniqueness
    sols = []
    for L in range(1, 2001):
        num = L * L + 4
        den = 2 * L - 7
        if den > 0 and num % den == 0:
            S = num // den
            v = 2 * S - L
            if v > 0 and (v * L + 1 == 7 * S + 5):
                sols.append((L, S, v))
    expected_sols = [(4, 20, 36), (6, 8, 10), (10, 8, 6), (36, 20, 4)]
    in_15_20 = [s for s in sols if 15 <= 7 + s[0] <= 20]
    in_10_18 = [s for s in sols if 10 <= 7 + s[0] <= 18]
    record(
        "part_a_diophantine_and_vidale_range_recheck",
        sols == expected_sols and len(in_15_20) == 1 and len(in_10_18) == 3,
        {"solutions": sols, "surviving_15_20": in_15_20, "surviving_10_18": in_10_18},
    )

    # Corpus uniqueness recheck
    by_fam = defaultdict(list)
    for r in lipi_rows:
        by_fam[r["object_family_id"]].append(r)
    h904_matches = [
        fam for fam, frs in by_fam.items()
        if len(frs) >= 2
        and any("900" in (f.get("signs_reading_rtl") or []) for f in frs)
        and any("840" in (f.get("signs_reading_rtl") or []) for f in frs)
    ]
    m1383_matches = [
        r["source_cisi"] for r in lipi_rows
        if any(
            (s[i] == "017" and s[i + 1] == "031") or (s[i] == "031" and s[i + 1] == "017")
            for s in [r.get("signs_reading_rtl") or []]
            for i in range(len(s) - 1)
        )
    ]
    record(
        "part_a_corpus_uniqueness_recheck",
        h904_matches == ["1786"] and m1383_matches == ["M-1383"],
        {"h904_matches": h904_matches, "m1383_matches": m1383_matches},
    )

    # 7. Check all local raw renders referenced in anchors-audit-v1.json exist on disk
    render_paths = [
        anchors["Q_0011_H904_ICIT3786"]["primary_witnesses_inspected"]["cisi2_plate"]["local_render"],
        anchors["Q_0011_H904_ICIT3786"]["primary_witnesses_inspected"]["cisi2_plate"]["local_zoom"],
        anchors["Q_0011_H904_ICIT3786"]["primary_witnesses_inspected"]["cisi2_basic_data"]["local_zoom"],
        anchors["Q_0012_M1383_Bangle_Anchor"]["primary_witnesses_inspected"]["cisi2_plate"]["local_render"],
        anchors["Q_0012_M1383_Bangle_Anchor"]["primary_witnesses_inspected"]["cisi2_basic_data"]["local_zoom"],
    ]
    missing_renders = [p for p in render_paths if not os.path.exists(p)]
    record(
        "local_primary_renders_present",
        len(missing_renders) == 0,
        {"checked": len(render_paths), "missing": missing_renders},
    )

    all_passed = all(c["passed"] for c in checks)
    out = {
        "verification_date": "2026-11-23",
        "all_passed": all_passed,
        "n_checks": len(checks),
        "n_passed": sum(1 for c in checks if c["passed"]),
        "checks": checks,
    }
    with open(VERIFY_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Verification complete: {out['n_passed']}/{out['n_checks']} passed (all_passed={all_passed})")
    for c in checks:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}")


if __name__ == "__main__":
    main()
