"""Compare package C's public-source census numbers with the B1/B2 outputs they came from.

Run from the repository root:
    python experiments/2026-10-06-byproduct-inventory/review/check_b1_b2_dependence.py

Package C (PUBLIC-INDEX-COVERAGE) quotes numbers from packages B1
(experiments/2026-10-06-evidence-census/sites-and-publications) and B2
(.../collections-and-datasets), which were still being edited when C finished.
This script reads (never writes) those outputs, the opening lines C indexed from
them at about 00:09 on 2026-10-07 (data/raw/2026-10-06-byproduct-inventory/doc-openings.json)
and writes review/b1-b2-dependence.json.
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "2026-10-06-byproduct-inventory"
B1 = ROOT / "experiments" / "2026-10-06-evidence-census" / "sites-and-publications"
B2 = ROOT / "experiments" / "2026-10-06-evidence-census" / "collections-and-datasets"
OPENINGS = ROOT / "data" / "raw" / "2026-10-06-byproduct-inventory" / "doc-openings.json"
OUT = PACKAGE / "review" / "b1-b2-dependence.json"


def load(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def main():
    inv = load(PACKAGE / "inventory.json")
    cand = next(c for c in inv["candidates"] if c["id"] == "PUBLIC-INDEX-COVERAGE")
    claimed = cand["numbers"]

    collections = load(B2 / "collection-register.json")["collections"]
    datasets = load(B2 / "dataset-register.json")["datasets"]
    sites = load(B1 / "site-register.json")["sites"]
    summary = load(B1 / "coverage-summary.json")
    with open(B2 / "paired-sample-audit.csv", encoding="utf-8-sig", newline="") as stream:
        pairs = list(csv.DictReader(stream))
    statuses = {}
    for row in pairs:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1

    current = {
        "institution_rows": len(collections),
        "dataset_archive_rows": len(datasets),
        "site_name_rows": len(sites),
        "site_labels_in_lipi": summary["site_name_values_in_lipi"],
        "site_specific_report_sites": summary["site_specific_report_sites_identified"],
        "site_specific_report_volumes": summary["site_specific_report_volumes_identified"],
        "planned_pairs": len(pairs),
        "pair_status_counts": statuses,
        "validated_pairs": sum(1 for r in pairs if r["status"].lower().startswith("valid")),
        "fraction_all_reported_objects_in_indexes": summary["fraction_of_all_reported_objects_in_accessible_indexes"],
    }

    seen = {}
    openings = load(OPENINGS)
    for entry in openings:
        path = entry["path"].replace("\\", "/")
        if "evidence-census" not in path:
            continue
        text = entry["opening"]
        seen[path] = {
            "numbers_in_opening": re.findall(r"\b\d[\d,]*\b", text)[:12],
            "excerpt": text[:260],
        }

    comparison = [
        ("institution_rows", claimed["institution_rows"], current["institution_rows"]),
        ("dataset_archive_rows", claimed["dataset_archive_rows"], current["dataset_archive_rows"]),
        ("site_name_rows", claimed["site_name_rows"], current["site_name_rows"]),
        ("site_labels_in_lipi", claimed["site_labels_in_lipi"], current["site_labels_in_lipi"]),
        ("site_specific_report_titles (C) versus volumes (B1 now)", claimed["site_specific_report_titles"],
         current["site_specific_report_volumes"]),
        ("planned_pairs", claimed["planned_pairs"], current["planned_pairs"]),
        ("validated_pairs", claimed["validated_pairs"], current["validated_pairs"]),
    ]
    rows = [
        {"quantity": name, "package_C": c, "B1_B2_now": n, "same": c == n}
        for name, c, n in comparison
    ]
    result = {
        "note": "B1/B2 outputs read in their state at review time; C indexed them at about 00:09 on 2026-10-07.",
        "comparison": rows,
        "current_pair_audit_status_counts": statuses,
        "C_saw_in_B1_B2_openings": seen,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for row in rows:
        print(f"{row['quantity']:<62} C={row['package_C']!s:<6} B1/B2 now={row['B1_B2_now']!s:<6} same={row['same']}")
    print("paired-sample-audit status counts:", statuses)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
