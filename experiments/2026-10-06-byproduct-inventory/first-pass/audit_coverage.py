"""Check that the byproduct inventory covers the current experiment registry."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "experiments" / "2026-10-06-byproduct-inventory"


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def main() -> int:
    inventory = load_json(PACKAGE / "inventory.json")
    registry = load_json(ROOT / "knowledge" / "experiments" / "registry.json")
    candidates = inventory["candidates"]
    candidate_ids = {candidate["id"] for candidate in candidates}
    if len(candidate_ids) != len(candidates):
        raise SystemExit("duplicate candidate id")

    required = {
        "title", "field", "audience", "established", "numbers", "evidence",
        "evidence_fields", "status", "novelty", "missing_validation",
        "smallest_form", "venues", "remaining_work", "registry_ids",
    }
    for candidate in candidates:
        missing = sorted(required - candidate.keys())
        if missing:
            raise SystemExit(f"{candidate['id']} missing fields: {missing}")

    expected = {entry["id"] for entry in registry["experiments"]}
    items = inventory["registry_coverage"]["items"]
    mapped = [item["registry_id"] for item in items]
    if len(mapped) != len(set(mapped)):
        raise SystemExit("registry coverage contains duplicate ids")
    if set(mapped) != expected:
        absent = sorted(expected - set(mapped))
        extra = sorted(set(mapped) - expected)
        raise SystemExit(f"registry coverage mismatch; absent={absent}; extra={extra}")

    owners = {item["registry_id"]: item["candidate_id"] for item in items}
    for candidate in candidates:
        listed = set(candidate["registry_ids"])
        actual = {registry_id for registry_id, owner in owners.items() if owner == candidate["id"]}
        if listed != actual:
            raise SystemExit(f"registry_ids disagree for {candidate['id']}")
    if not set(owners.values()) <= candidate_ids:
        raise SystemExit("registry coverage names an unknown candidate")

    print(f"OK: {len(expected)} registry entries mapped once across {len(candidates)} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
