"""Reviewer check of package C structure: registry coverage, per-candidate fields, evidence paths.

Run from the repository root:
    python experiments/2026-10-06-byproduct-inventory/review/check_structure.py

It reads inventory.json and knowledge/experiments/registry.json, writes
review/structure-check.json, and prints a summary. It changes nothing else.
"""

import collections
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "2026-10-06-byproduct-inventory"
OUT = PACKAGE / "review" / "structure-check.json"


def load(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def main():
    inv = load(PACKAGE / "inventory.json")
    registry = load(ROOT / "knowledge" / "experiments" / "registry.json")["experiments"]
    reg = {entry["id"]: entry for entry in registry}
    candidates = inv["candidates"]
    items = inv["registry_coverage"]["items"]
    owner = {item["registry_id"]: item["candidate_id"] for item in items}
    result = {}

    mapped = [item["registry_id"] for item in items]
    result["registry_entries"] = len(reg)
    result["mapped_items"] = len(mapped)
    result["mapped_unique"] = len(set(mapped))
    result["absent_from_mapping"] = sorted(set(reg) - set(mapped))
    result["extra_in_mapping"] = sorted(set(mapped) - set(reg))

    required = {
        "title", "field", "audience", "established", "numbers", "evidence",
        "evidence_fields", "status", "novelty", "missing_validation",
        "smallest_form", "venues", "remaining_work", "registry_ids",
    }
    per_candidate = []
    for candidate in candidates:
        actual = sorted(r for r, o in owner.items() if o == candidate["id"])
        listed = candidate.get("registry_ids")
        per_candidate.append({
            "rank": candidate.get("rank"),
            "id": candidate["id"],
            "missing_required_fields": sorted(required - candidate.keys()),
            "registry_ids_listed": None if listed is None else len(listed),
            "registry_ids_in_mapping": len(actual),
            "registry_ids_agree": listed is not None and sorted(listed) == actual,
        })
    result["candidates"] = per_candidate
    result["candidates_with_no_registry_entries_in_mapping"] = [
        row["id"] for row in per_candidate if row["registry_ids_in_mapping"] == 0
    ]
    result["candidates_missing_registry_ids_field"] = [
        row["id"] for row in per_candidate if row["registry_ids_listed"] is None
    ]
    share = collections.Counter(owner.values())
    top_id, top_n = share.most_common(1)[0]
    result["largest_bundle"] = {"candidate": top_id, "entries": top_n,
                                "share_of_registry": round(top_n / len(reg), 3)}

    null_ids = sorted(r for r in reg if r.startswith("NULL-"))
    result["null_calibration_entries_and_owner"] = {r: owner[r] for r in null_ids}

    missing_paths = []
    n_paths = 0
    for candidate in candidates:
        for path in candidate["evidence"]:
            n_paths += 1
            if not (ROOT / path.split("#")[0]).exists():
                missing_paths.append({"candidate": candidate["id"], "path": path})
    result["evidence_paths_checked"] = n_paths
    result["evidence_paths_missing"] = missing_paths

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "candidates"}, indent=2))
    # The shipped audit exits at the first candidate that lacks registry_ids.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
