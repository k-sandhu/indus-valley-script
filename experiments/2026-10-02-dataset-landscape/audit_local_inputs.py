"""Audit the existing inputs; write aggregate results, never inscription rows."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
MISSING = {"", "-", "--", "Unknown"}
INPUTS = [
    ("lipi", "data/normalized/lipi_observed_faces.jsonl", "data/normalized/lipi_summary.json"),
    ("mayig", "data/normalized/mayig_faces.jsonl", "data/normalized/mayig_summary.json"),
    ("older_export", "data/normalized/indus_website_observed.jsonl", "data/normalized/indus_website_summary.json"),
]


def pin(path):
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
            "sha256": sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New JSON result below this run")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(RUN) or output.exists():
        raise ValueError("Output must be a new file in this dated run")
    records = []
    checks = []
    for name, derivative, summary in INPUTS:
        path, summary_path = ROOT / derivative, ROOT / summary
        with path.open(encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        historical = json.loads(summary_path.read_text(encoding="utf-8"))
        sequences = [tuple(row["signs_visual_ltr"]) for row in rows]
        codes = {code for sequence in sequences for code in sequence}
        aggregate = {
            "source": name, "input": pin(path), "historical_summary": pin(summary_path),
            "records": len(rows),
            "provisional_source_families": len({r["object_family_id"] for r in rows}),
            "source_reported_token_positions": sum(r["length"] for r in rows),
            "distinct_codes_including_editorial_markers": len(codes),
            "distinct_whole_sequences": len(set(sequences)),
            "repeated_sequence_excess": len(rows) - len(set(sequences)),
            "record_id_collisions": sum(n-1 for n in Counter(r["record_id"] for r in rows).values()),
            "scope": "Counts within one pinned source; not additive archaeological discoveries.",
        }
        expected_rows = historical.get("rows", historical.get("faces"))
        comparisons = {"records": (len(rows), expected_rows),
                       "tokens": (aggregate["source_reported_token_positions"], historical["tokens"])}
        for metric, (actual, expected) in comparisons.items():
            checks.append({"source": name, "metric": metric,
                           "actual": actual, "expected": expected, "passed": actual == expected})
        if name == "lipi":
            fields = list(rows[0]["metadata"])
            missing = {field: sum(r["metadata"].get(field) in MISSING for r in rows)
                       for field in fields}
            aggregate["source_metadata_missing"] = {
                field: {"records": n, "percent": round(n / len(rows) * 100, 2)}
                for field, n in missing.items()}
            aggregate["missing_definition"] = sorted(MISSING)
            aggregate["dimension_zero_placeholders"] = {
                field: sum(r["metadata"].get(field) == "0" for r in rows)
                for field in ("horizontal(mm)", "vertical(mm)", "thickness(mm)")}
            aggregate["depth_dash_space_placeholder_records"] = sum(
                r["metadata"].get("depth") == "- -" for r in rows)
            aggregate["records_with_unknown_sign_marker"] = sum(r["has_unknown_sign"] for r in rows)
            for field, count in missing.items():
                expected = historical["metadata_missing"][field]
                checks.append({"source": name, "metric": "missing:" + field,
                               "actual": count, "expected": expected, "passed": count == expected})
        records.append(aggregate)
    chart_path = ROOT / "research/chart_reference/manual_numeric_reference.json"
    chart = json.loads(chart_path.read_text(encoding="utf-8"))
    harappa_path = ROOT / "experiments/2026-10-02-connections-and-priority/harappa-short-records/main-v2/results.json"
    harappa = json.loads(harappa_path.read_text(encoding="utf-8"))
    discovery_path = ROOT / "data/raw/2026-10-02-dataset-landscape/discovery-v1/acquisition.json"
    discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    search_results = []
    for index, query in enumerate(discovery["queries"]):
        path = discovery_path.parent / f"hf-search-{index}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        search_results.append({"query": query, "ids": [row["id"] for row in data], "input": pin(path)})
    result = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "study_date_local": "2026-10-02", "sources": records,
        "existing_reviewed_resources": {
            "chart": {"input": pin(chart_path), "cells": len(chart["rows"]),
                      "ambiguous_lower_code_cells": chart["lower_code_ambiguous_cells"],
                      "status": "Source-table annotations by AI readers; no expert certification."},
            "harappa_frame": {"input": pin(harappa_path), "objects": harappa["objects"],
                              "faces": harappa["faces"], "status": "Subset of existing sources; not additional corpus size."}},
        "discovery": {"manifest": pin(discovery_path), "queries": search_results,
                      "distinct_hf_ids": sorted({name for r in search_results for name in r["ids"]})},
        "checks": checks, "all_checks_passed": all(c["passed"] for c in checks),
        "limits": [
            "Provisional families are upstream groupings, not a complete museum identity audit.",
            "Repeated strings can belong to distinct objects; text identity does not merge physical identity.",
            "Cross-source sums would double-count objects and annotations.",
            "Missing counts use the historical source rule; zero dimensions and '- -' depth are separately exposed.",
            "No new bulk corpus, photographs or unverified semantic fields were made public.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": output.relative_to(ROOT).as_posix(),
                      "checks": len(checks), "all_checks_passed": result["all_checks_passed"],
                      "sources": [{k:r[k] for k in ("source", "records", "provisional_source_families", "source_reported_token_positions")}
                                  for r in records]}, indent=2))
    if not result["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
