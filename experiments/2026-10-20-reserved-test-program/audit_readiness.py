"""Audit legacy freezes without reading the new reserved collection."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGENDS = ROOT / "experiments/2026-10-20-seal-legend-units"
FISH = ROOT / "experiments/2026-10-20-fish-context"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(path: Path, expected: str | None = None) -> dict:
    path = path.resolve()
    relative = path.relative_to(ROOT).as_posix()
    # This tool is intentionally incapable of accepting new collection paths.
    if "fresh-test-collection" in relative or "foreign-script" in relative:
        raise ValueError("Reserved or unrelated observations are outside this audit")
    exists = path.is_file()
    actual = digest(path) if exists else None
    return {"path": relative, "exists": exists, "sha256": actual,
            "expected_sha256": expected,
            "matches": actual == expected if expected else None}


def run() -> dict:
    checks = []
    manifest = LEGENDS / "PREDICTIONS.sha256"
    checks.append(check(manifest))
    freeze_note = None
    if manifest.exists():
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                freeze_note = line[1:].strip()
            elif line.strip():
                expected, name = line.split(None, 1)
                name = name.strip()
                path = ROOT / name if name.startswith("data/") else LEGENDS / name
                checks.append(check(path, expected))
    fish_freeze = json.loads((FISH / "freeze-v1.json").read_text(encoding="utf-8"))
    frozen = fish_freeze["frozen"]
    fish_checks = [check(FISH / "PREDICTIONS.json", frozen["predictions_sha256"])]
    for name, expected in frozen["artifacts"].items():
        fish_checks.append(check(Path(name), expected))
    legend_payload = json.loads((LEGENDS / "predictions.json").read_text(encoding="utf-8"))
    required = {"statistic_families", "predictions", "joint_credence_rule"}
    result = {
        "schema_version": "1.0", "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Legacy prediction files and hashes only; no reserved payload read",
        "seal_structure": {
            "source_freeze_note": freeze_note, "checks": checks,
            "all_hashes_match": bool(checks) and all(c["exists"] and c["matches"] is not False for c in checks),
            "direct_shots_registration_missing_fields": sorted(required - set(legend_payload)),
            "note": "Prospective rules and joint credence are in PREDICTIONS.md. A shared-loader registration wrapper must cite their unchanged hashes before release."
        },
        "fish": {
            "source_freeze_utc": frozen["utc"], "checks": fish_checks,
            "all_hashes_match": all(c["exists"] and c["matches"] for c in fish_checks),
            "note": "Historical rule and model are frozen. An external-population registration must specify applicability and preserve the original result."
        },
        "real_confirmation_reads_by_this_tool": 0,
        "reserved_payload_files_opened_by_this_tool": 0,
        "release_authorized": False,
        "release_requirements": [
            "Complete acquisition frame and custody manifest frozen",
            "Physical aliases and prior object/text exposure reviewed",
            "All participants, eligible population, pass rules and joint interpretation registered",
            "All source and scorer hashes rechecked",
            "Shared shots loader used with versioned private ledger and complete access log"
        ]
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Use a new output path; previous endpoints are preserved")
    output = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"out": str(args.out), "seal_hashes_match": output["seal_structure"]["all_hashes_match"],
                      "fish_hashes_match": output["fish"]["all_hashes_match"],
                      "real_confirmation_reads": 0}))
