"""Show that the shipped coverage audit fails on a missing field and passes once it is supplied.

Run from the repository root:
    python experiments/2026-10-06-byproduct-inventory/review/simulate_audit_fix.py

The script loads inventory.json into memory, adds an empty "registry_ids" list to every
candidate that lacks the field, and applies the same checks as audit_coverage.py. It
writes nothing and does not modify inventory.json.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments" / "2026-10-06-byproduct-inventory"


def load(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def shipped_audit_result():
    run = subprocess.run(
        [sys.executable, str(PACKAGE / "audit_coverage.py")],
        capture_output=True, text=True, cwd=ROOT,
    )
    return run.returncode, (run.stdout + run.stderr).strip()


def audit_with_supplied_field(inventory, registry):
    required = {
        "title", "field", "audience", "established", "numbers", "evidence",
        "evidence_fields", "status", "novelty", "missing_validation",
        "smallest_form", "venues", "remaining_work", "registry_ids",
    }
    added = []
    for candidate in inventory["candidates"]:
        if "registry_ids" not in candidate:
            candidate["registry_ids"] = []
            added.append(candidate["id"])
    for candidate in inventory["candidates"]:
        missing = required - candidate.keys()
        if missing:
            return False, f"{candidate['id']} still missing {sorted(missing)}", added
    expected = {entry["id"] for entry in registry["experiments"]}
    items = inventory["registry_coverage"]["items"]
    mapped = [item["registry_id"] for item in items]
    if len(mapped) != len(set(mapped)) or set(mapped) != expected:
        return False, "registry coverage mismatch", added
    owners = {item["registry_id"]: item["candidate_id"] for item in items}
    for candidate in inventory["candidates"]:
        actual = {r for r, o in owners.items() if o == candidate["id"]}
        if set(candidate["registry_ids"]) != actual:
            return False, f"registry_ids disagree for {candidate['id']}", added
    return True, f"{len(expected)} registry entries mapped once across {len(inventory['candidates'])} candidates", added


def main():
    code, text = shipped_audit_result()
    print(f"shipped audit_coverage.py: exit {code}: {text}")
    inventory = load(PACKAGE / "inventory.json")
    registry = load(ROOT / "knowledge" / "experiments" / "registry.json")
    ok, message, added = audit_with_supplied_field(inventory, registry)
    print(f"same checks after supplying empty registry_ids for {added}: {'pass' if ok else 'fail'}: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
