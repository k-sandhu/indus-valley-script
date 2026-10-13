"""Append this program's research memory and freeze an own-work file manifest.

This performs local documentation integration only. It does not stage, commit,
push, change repository visibility, or package ignored input payloads.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-11-two-approaches"
KNOWLEDGE_CHANGES = [
    "README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json",
    "knowledge/retrospectives/README.md",
    "knowledge/retrospectives/2026-10-11-two-approaches.md",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def integrate_registry():
    registry_path = ROOT / "knowledge/experiments/registry.json"
    original = read(registry_path)
    entries = [read(HERE / package / "registry-entry.json")
               for package in ("grammar", "administrative")]
    entries.append(read(HERE / "registry-entry.json"))
    known = {entry["id"]: entry for entry in original["experiments"]}
    if len(known) != len(original["experiments"]):
        raise ValueError("Existing registry has duplicate identifiers")
    additions = []
    for entry in entries:
        if entry["id"] in known:
            if known[entry["id"]] != entry:
                raise ValueError(f"Existing entry differs: {entry['id']}")
        else:
            additions.append(entry)
            known[entry["id"]] = entry
    preserved = list(original["experiments"])
    original["experiments"].extend(additions)
    if additions:
        registry_path.write_text(json.dumps(original, indent=2, ensure_ascii=False,
                                             allow_nan=False) + "\n", encoding="utf-8")
    final = read(registry_path)
    assert final["experiments"][:len(preserved)] == preserved
    baseline = read(RAW / "coordinator/baseline-v1/knowledge/experiments/registry.json")
    baseline_by_id = {entry["id"]: entry for entry in baseline["experiments"]}
    final_by_id = {entry["id"]: entry for entry in final["experiments"]}
    assert set(baseline_by_id).issubset(final_by_id)
    # Navigation may already have acquired revisions before this program's
    # append. Preserve current entries and the original baseline separately.
    drift = [{"id": identifier,
              "changed_fields": sorted(key for key in set(entry) | set(final_by_id[identifier])
                                       if entry.get(key) != final_by_id[identifier].get(key))}
             for identifier, entry in baseline_by_id.items() if entry != final_by_id[identifier]]
    return {"added_ids_this_invocation": [entry["id"] for entry in additions],
            "program_entry_ids": [entry["id"] for entry in entries],
            "prior_entries_preserved": len(preserved),
            "baseline_entry_ids_retained": len(baseline["experiments"]),
            "preexisting_navigation_revisions_since_baseline": drift,
            "original_baseline_bytes_preserved": "data/raw/2026-10-11-two-approaches/coordinator/baseline-v1/knowledge/experiments/registry.json",
            "new_total": len(final["experiments"])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integrate-registry", action="store_true")
    parser.add_argument("--out", default="manifest-program-v1.json")
    args = parser.parse_args()
    output = HERE / args.out
    if output.exists():
        raise SystemExit("Manifest exists; select a new version.")
    registry_result = integrate_registry() if args.integrate_registry else None
    paths = [path for path in HERE.rglob("*")
             if path.is_file() and "__pycache__" not in path.parts
             and path.suffix not in (".pyc", ".pyo") and path != output]
    paths.extend(ROOT / name for name in KNOWLEDGE_CHANGES)
    records = [{"path": path.relative_to(ROOT).as_posix(),
                "sha256": sha(path), "bytes": path.stat().st_size}
               for path in sorted(set(paths))]
    raw_files = [path for path in RAW.rglob("*") if path.is_file()]
    # NUL-delimited bytes avoid Windows text-mode CRLF conversion being
    # interpreted by Git as a carriage return at the end of a filename.
    ignore_input = ("\0".join(path.relative_to(ROOT).as_posix() for path in raw_files) + "\0").encode("utf-8")
    ignored = subprocess.run(["git", "check-ignore", "-z", "--stdin"], cwd=ROOT,
                             input=ignore_input, capture_output=True, check=False)
    ignored_paths = set(ignored.stdout.decode("utf-8").split("\0"))
    raw_not_ignored = [path.relative_to(ROOT).as_posix() for path in raw_files
                       if path.relative_to(ROOT).as_posix() not in ignored_paths]
    if ignored.returncode not in (0, 1) or raw_not_ignored:
        raise ValueError("Raw payload ignore check failed")
    result = {"status": "local-research-package-manifest",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "files": records, "own_work_and_navigation_files": len(records),
              "extensions": dict(Counter(Path(r["path"]).suffix for r in records)),
              "registry_integration": registry_result,
              "raw_payload_files_checked": len(raw_files),
              "raw_payload_files_not_ignored": raw_not_ignored,
              "raw_payload_location": RAW.relative_to(ROOT).as_posix(),
              "publication_actions": [],
              "scope": "Own-work files and navigation hashes; ignored source payloads are not included."}
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(records), "raw_files_ignored": len(raw_files),
                      "registry": registry_result, "output": str(output)}))


if __name__ == "__main__":
    main()
