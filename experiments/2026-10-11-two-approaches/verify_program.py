"""Check preservation, file availability and JSON integrity of this program.

Package-specific statistical review is recorded separately; this does not
replace it with a count of files or a claim of semantic validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON number: {value}")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)


def check_program():
    checks = []
    warnings = []
    frozen = load(HERE / "baseline-v1.json")
    shared = load(HERE / "shared-revisions-v2.json")
    shared_by_path = {record["path"]: record for record in shared["changed_files"]}
    backups = ROOT / frozen["local_navigation_backup"]
    for record in frozen["files"]:
        path = ROOT / record["path"]
        unchanged = path.is_file() and sha(path) == record["sha256"]
        if record["navigation_may_be_extended"]:
            backup = backups / record["path"]
            preserved = backup.is_file() and sha(backup) == record["sha256"]
            checks.append({"check": "navigation_original_preserved", "path": record["path"],
                           "pass": preserved, "current_unchanged": unchanged})
        elif not unchanged and record["path"] in shared_by_path:
            revision = shared_by_path[record["path"]]
            copy = ROOT / revision["current_copy"]
            documented = (revision["baseline_sha256"] == record["sha256"]
                          and path.is_file() and sha(path) == revision["current_sha256"]
                          and copy.is_file() and sha(copy) == revision["current_sha256"])
            checks.append({"check": "shared_workspace_revision_recorded", "path": record["path"],
                           "pass": documented, "baseline_unchanged": False})
            if revision["baseline_recovered"]:
                original = ROOT / revision["baseline_copy"]
                checks.append({"check": "exact_start_version_recovered", "path": record["path"],
                               "pass": original.is_file() and sha(original) == record["sha256"]})
            else:
                warnings.append({"kind": "prior_start_version_unavailable", "path": record["path"],
                                 "baseline_sha256": record["sha256"],
                                 "detail": "A prior-program file changed in the shared workspace. Its initial hash and current bytes are preserved; exact initial bytes were not found in snapshots or Git objects."})
        else:
            checks.append({"check": "prior_endpoint_unchanged", "path": record["path"], "pass": unchanged})
    for path in sorted(HERE.rglob("*.json")):
        if path.name.startswith("verification-program-") or "coordinator-checks" in path.parts:
            continue
        try:
            load(path)
            ok, detail = True, None
        except (ValueError, OSError) as exc:
            ok, detail = False, str(exc)
        checks.append({"check": "strict_json", "path": path.relative_to(ROOT).as_posix(),
                       "pass": ok, "detail": detail})
    for name in ("REPORT.md", "README.md", "HYPOTHESIS-NOTE.md", "ANCHORS.md", "PROTOCOL.md"):
        checks.append({"check": "program_document_exists", "path": name, "pass": (HERE / name).is_file()})
    for package in ("grammar", "administrative", "literature"):
        for name in ("sources.json", "RETROSPECTIVE.md"):
            path = HERE / package / name
            checks.append({"check": "package_record_exists", "path": f"{package}/{name}", "pass": path.is_file()})
    for path in sorted(HERE.rglob("*.md")):
        content = path.read_text(encoding="utf-8-sig")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            target = target.strip("<>")
            if not target or target.startswith("#") or urlsplit(target).scheme:
                continue
            local = path.parent / unquote(target.split("#", 1)[0])
            checks.append({"check": "local_markdown_link_exists",
                           "path": path.relative_to(ROOT).as_posix(),
                           "target": target, "pass": local.exists()})
    registry = load(ROOT / "knowledge/experiments/registry.json")
    by_id = {entry["id"]: entry for entry in registry["experiments"]}
    for path in (HERE / "registry-entry.json", HERE / "grammar/registry-entry.json",
                 HERE / "administrative/registry-entry.json"):
        entry = load(path)
        checks.append({"check": "registered_entry_matches_package", "id": entry["id"],
                       "pass": by_id.get(entry["id"]) == entry})
        for evidence in entry["evidence"]:
            checks.append({"check": "registry_evidence_exists", "path": evidence,
                           "pass": (ROOT / evidence).exists()})
    return {"status": "program-integrity-checks-with-shared-history-limitations" if warnings else "program-integrity-checks", "checks": checks,
            "passed": sum(c["pass"] for c in checks),
            "failed": sum(not c["pass"] for c in checks),
            "preservation_warnings": warnings,
            "unchanged_prior_non_navigation_files": sum(c["check"] == "prior_endpoint_unchanged" and c["pass"] for c in checks),
            "recovered_prior_start_versions": sum(c["check"] == "exact_start_version_recovered" and c["pass"] for c in checks),
            "scope": "Available start versions, recorded shared-workspace revisions, file availability and numeric JSON syntax. Unavailable prior code/protocol versions remain disclosed history limitations; independent new-program statistical review is separate."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="verification-program-v1.json")
    args = parser.parse_args()
    output = HERE / args.out
    if output.exists():
        raise SystemExit("Output exists; choose a new version.")
    # Reserve this new run's report so documentation can link to its own
    # verification record. Only this newly created in-progress file is updated.
    with output.open("x", encoding="utf-8") as handle:
        json.dump({"status": "program-integrity-check-in-progress"}, handle)
    result = check_program()
    result["code_sha256"] = sha(Path(__file__))
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"], "output": str(output)}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
