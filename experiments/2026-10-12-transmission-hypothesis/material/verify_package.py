"""Verify frozen endpoints and source handling; write a fresh packaging audit.

This validates files and documentary consistency, not historical transmission.
Run from the repository root. Only this contributor's two directories are owned.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote


PACKAGE = Path("experiments/2026-10-12-transmission-hypothesis/material")
RAW = Path("data/raw/2026-10-12-transmission-hypothesis/material")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record(path, role):
    return {"path": path.as_posix(), "bytes": path.stat().st_size,
            "sha256": digest(path), "role": role}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--change-inventory", action="store_true")
    args = parser.parse_args()
    resolved = args.output_dir.resolve()
    if PACKAGE.resolve() not in resolved.parents:
        raise ValueError("Audit output must remain within the owned package")
    inventory_path = PACKAGE / "changed-paths.json"
    if args.change_inventory and inventory_path.exists():
        raise FileExistsError("Preserve the existing change inventory; write a later audit separately")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    checks = []

    def check(name, passed, detail):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    for name, expected in read_json(PACKAGE / "run-v1/input-hashes.json").items():
        p = Path(name)
        check("frozen-input-" + p.name, p.is_file() and digest(p) == expected, "Frozen analysis input hash")
    primary_checks = read_json(PACKAGE / "run-v1/checks.json")
    summary = read_json(PACKAGE / "run-v1/summary.json")
    check("primary-check-accounting", summary["checks"] == len(primary_checks)
          and summary["passed"] == sum(c["passed"] for c in primary_checks)
          and not summary["failed"], "Frozen integrity result accounting")
    observations = read_json(PACKAGE / "observations.json")["observations"]
    sources = read_json(PACKAGE / "sources.json")["sources"]
    comparisons = read_json(PACKAGE / "comparisons.json")["comparisons"]
    rows = [{"candidate_id": c["candidate_id"], "rival": r["rival"],
             "status": r["status"], "basis": r["basis"]}
            for c in comparisons for r in c["rivals"]]
    check("frozen-rival-matrix", rows == read_json(PACKAGE / "run-v1/rival-matrix.json"),
          "Rows follow the frozen qualitative comparisons")
    check("descriptive-counts", len(sources) == summary["sources"]
          and len(observations) == summary["observations"]
          and dict(Counter(r["status"] for r in rows)) == summary["statuses"],
          "Counts are documentary decisions, not independent evidence votes")

    for attempt in read_json(PACKAGE / "acquisition-index.json")["attempts"]:
        p = Path(attempt.get("path", ""))
        if attempt["status"] == "acquired":
            check("acquisition-" + attempt["filename"], p.is_file()
                  and p.stat().st_size == attempt["bytes"] and digest(p) == attempt["sha256"],
                  "Original acquired bytes and hash")
        else:
            check("acquisition-failure-" + attempt["filename"], bool(attempt.get("error")),
                  "Failed access is retained without an invented original witness")

    for manifest in sorted(RAW.glob("extract-*/manifest.json")):
        for row in read_json(manifest):
            check("extraction-" + Path(row["output_path"]).name,
                  digest(row["input_path"]) == row["input_sha256"]
                  and digest(row["output_path"]) == row["output_sha256"],
                  "Parent and text derivative hashes")
    for row in read_json(RAW / "html-caption-extract-v1/manifest.json"):
        check("caption-" + Path(row["path"]).name,
              digest(row["parent_path"]) == row["parent_sha256"]
              and digest(row["path"]) == row["sha256"], "HTML and caption derivative hashes")
    supplement = read_json(RAW / "supplement-extract-v1/supplement.json")
    check("supplement-parent", digest(supplement["parent_path"]) == supplement["parent_sha256"]
          and len(supplement["tables"]) == 3, "Three tables from the declared publisher DOCX")

    json_paths = sorted(PACKAGE.rglob("*.json"))
    for p in json_paths:
        read_json(p)
    check("package-json-readable", bool(json_paths), len(json_paths))
    link_count = 0
    for p in sorted(PACKAGE.glob("*.md")):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            local = target.split("#", 1)[0].strip("<>")
            check("link-" + p.name + "-" + str(link_count), (p.parent / unquote(local)).exists(), target)
            link_count += 1

    raw_files = sorted(p for p in RAW.rglob("*") if p.is_file())
    supplied = "\0".join(p.as_posix() for p in raw_files) + "\0"
    ignored = subprocess.run(["git", "check-ignore", "-z", "--stdin"], input=supplied,
                             capture_output=True, text=True, check=False)
    ignored_paths = set(ignored.stdout.split("\0")) - {""}
    check("raw-ignored", ignored.returncode == 0 and ignored_paths == {p.as_posix() for p in raw_files},
          {"files": len(raw_files), "all_covered": len(ignored_paths) == len(raw_files)})
    tracked = subprocess.run(["git", "ls-files", "-z", "--", RAW.as_posix()],
                             capture_output=True, text=True, check=False)
    check("raw-not-tracked", tracked.returncode == 0 and not tracked.stdout, "No raw source file in Git")
    authored = sorted(p for p in PACKAGE.rglob("*") if p.is_file())
    check("authored-formats", all(p.suffix in {".md", ".json", ".py"} for p in authored),
          "No downloaded PDF, HTML, DOCX, OCR text or image in the authored package")
    outcome = {"created_utc": datetime.now(timezone.utc).isoformat(), "checks": len(checks),
               "passed": sum(c["passed"] for c in checks),
               "failed": [c["check"] for c in checks if not c["passed"]],
               "local_links": link_count, "raw_files": len(raw_files),
               "scope": "File integrity, endpoint preservation, local references and source exclusion only."}
    write_json(args.output_dir / "checks.json", checks)
    write_json(args.output_dir / "summary.json", outcome)
    if args.change_inventory:
        authored = sorted(p for p in PACKAGE.rglob("*") if p.is_file())
        inventory = {"created_utc": datetime.now(timezone.utc).isoformat(),
                     "ownership": [PACKAGE.as_posix(), RAW.as_posix()],
                     "preserved": "Every older endpoint and other contributor's files",
                     "authored": [record(p, "own prose/code/metadata/aggregate") for p in authored],
                     "local_only": [record(p, "ignored source witness/derivative or acquisition metadata") for p in raw_files],
                     "self_path": inventory_path.as_posix(), "self_hash": None,
                     "self_hash_reason": "A file cannot include its own content hash; all other files are snapshotted."}
        write_json(inventory_path, inventory)
    print(json.dumps(outcome))
    if outcome["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
