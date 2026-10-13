"""Check joins and preservation, then save one final package manifest and check record.

This checks delivered files and declared references. It does not assess historical truth.
"""
from __future__ import annotations
import ast
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity"
NAV = ("README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json", "knowledge/retrospectives/README.md")
POINTER = ROOT / "knowledge/retrospectives/2026-10-11-early-indian-continuity.md"
FINAL = ("changed-paths.json", "manifest.json", "verification.json")
CHECKS: list[dict] = []
WARNINGS: list[dict] = []

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def check(label: str, condition: bool, details=None) -> None:
    CHECKS.append({"check": label, "passed": bool(condition), "details": details})

def write(path: Path, data) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

def pointer(data, value: str):
    for token in value.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        data = data[int(token)] if isinstance(data, list) else data[token]
    return data

def main() -> None:
    if any((PACKAGE / p).exists() for p in FINAL):
        raise SystemExit("Final output exists; inspect it, or implement a dated successor. No overwrite.")
    files = sorted(p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    planned = {(PACKAGE / p).resolve() for p in FINAL}
    for path in files:
        if path.suffix == ".json":
            try:
                read(path)
                check("JSON parses: " + rel(path), True)
            except (ValueError, UnicodeError) as exc:
                check("JSON parses: " + rel(path), False, str(exc))
        if path.suffix == ".py":
            try:
                compile(ast.parse(path.read_text(encoding="utf-8")), str(path), "exec")
                check("Python compiles: " + rel(path), True)
            except (SyntaxError, UnicodeError) as exc:
                check("Python compiles: " + rel(path), False, str(exc))
    check("Repository package has no raw binary publication payloads", not any(p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pyc"} for p in files))

    link_count = 0
    md_files = [p for p in files if p.suffix == ".md"] + [POINTER]
    for path in md_files:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\n]*?\]\((?:<([^>\n]+)>|([^\n)]+))\)", text):
            target = (match.group(1) or match.group(2)).strip()
            if re.match(r"(?:https?://|mailto:|codex:|#)", target):
                continue
            target = unquote(target.split("#", 1)[0])
            local = (path.parent / target).resolve()
            link_count += 1
            check("Local Markdown link: " + rel(path), local.exists() or local in planned, target)

    claims = read(PACKAGE / "CLAIM-EVIDENCE.json")["claims"]
    check("Coordinator claim IDs unique", len({c["id"] for c in claims}) == len(claims))
    for claim in claims:
        for reference in claim.get("observations", []):
            observations = read(ROOT / reference["file"])
            if isinstance(observations, dict):
                observations = observations["observations"]
            ids = {row["id"] for row in observations}
            check("Claim observation IDs: " + claim["id"], set(reference["ids"]) <= ids, reference)
        for output in claim.get("outputs", []):
            try:
                pointer(read(ROOT / output["file"]), output["pointer"])
                check("Claim output pointer: " + claim["id"], True, output)
            except (KeyError, IndexError, ValueError) as exc:
                check("Claim output pointer: " + claim["id"], False, str(exc))
        for key in ("discussion", "test", "independent_check"):
            if key in claim:
                check("Claim reference: " + claim["id"], (ROOT / claim[key]).is_file(), claim[key])

    review = read(PACKAGE / "review/review-checks.json")
    check("Independent review has no unresolved blocker", review["status"] == "complete_no_unresolved_blocker" and not review["unresolved_blockers"])
    for path, expected in review["reviewed_file_sha256"].items():
        check("Reviewed file pin: " + path, sha(ROOT / path) == expected)
    for subdir, key in (("institutions", "repository_artifacts"), ("memory", "prepared_paths")):
        for record in read(PACKAGE / subdir / "changed-paths.json")[key]:
            check("Contributor artifact pin: " + record["path"], sha(ROOT / record["path"]) == record["sha256"])

    # Frozen inputs remain pinned. Current reporting files are outside those input hashes.
    for subdir, output, key in (("institutions", "run-v1/audit.json", "input_hashes"),
                               ("institutions", "run-v2/audit.json", "input_hashes"),
                               ("memory", "run-v1/summary.json", "input_sha256")):
        for name, expected in read(PACKAGE / subdir / output)[key].items():
            check("Frozen input: " + subdir + "/" + name, sha(PACKAGE / subdir / name) == expected)
    model = read(PACKAGE / "coordinator/run-v1/retention.json")
    check("Retention code pin", sha(HERE / "retention_model.py") == model["source_code_sha256"])
    check("Retention protocol pin", sha(HERE / "MODEL-PROTOCOL.md") == model["protocol_sha256"])

    baseline = read(PACKAGE / "baseline-v1.json")
    for record in baseline["original_bytes"]:
        check("Exact starting-byte snapshot: " + record["path"], sha(ROOT / record["snapshot"]) == record["sha256"])
    baseline_changes = []
    unchanged = 0
    for record in baseline["inventory"]:
        path = ROOT / record["path"]
        current = sha(path) if path.is_file() else None
        if current == record["sha256"]:
            unchanged += 1
        else:
            category = ("this program navigation over current pre-edit snapshot" if record["path"] in NAV else
                        "this program owned file" if path.is_relative_to(PACKAGE) else
                        "concurrent workspace change outside this program ownership")
            baseline_changes.append({"path": record["path"], "start_sha256": record["sha256"], "current_sha256": current, "classification": category})
    outside = [r for r in baseline_changes if r["classification"].startswith("concurrent")]
    if outside:
        WARNINGS.append({"type": "shared-workspace-baseline-changes", "count": len(outside), "scope": "Observed differences outside this program's ownership. Existing current work was retained; attribution and whole-file byte backups are not implied.", "paths": [r["path"] for r in outside]})

    integration = read(HERE / "navigation-integration-v1.json")
    for record in integration["files"]:
        check("Pre-integration snapshot: " + record["path"], sha(ROOT / record["snapshot"]) == record["before_sha256"])
        check("Navigation addition pin: " + record["path"], sha(ROOT / record["path"]) == record["after_sha256"])
    before_registry = read(ROOT / next(r["snapshot"] for r in integration["files"] if r["path"] == NAV[2]))
    current_registry = read(ROOT / NAV[2])
    new_entries = read(HERE / "registry-additions.json")
    check("All prior registry objects retained in order", current_registry["experiments"] == before_registry["experiments"] + new_entries)
    for entry in new_entries:
        for path in entry["evidence"]:
            check("New registry evidence: " + entry["id"], (ROOT / path).is_file(), path)

    raw_paths = sorted(rel(p) for p in RAW.rglob("*") if p.is_file())
    result = subprocess.run(["git", "check-ignore", "-z", "--stdin"], cwd=ROOT,
                            input=b"\0".join(p.encode("utf-8") for p in raw_paths) + b"\0", capture_output=True)
    ignored = {p.decode("utf-8").replace("\\", "/") for p in result.stdout.split(b"\0") if p}
    check("All local raw witnesses and derivatives Git-ignored", result.returncode == 0 and ignored == set(raw_paths), {"raw_files": len(raw_paths), "ignored_files": len(ignored)})
    tracked = subprocess.run(["git", "ls-files", "-z", "--", rel(RAW)], cwd=ROOT, capture_output=True, check=True)
    check("No acquired raw witness tracked", not tracked.stdout)

    if any(not c["passed"] for c in CHECKS):
        print(json.dumps({"status": "failed before final-output creation", "failures": [c for c in CHECKS if not c["passed"]]}, ensure_ascii=True, indent=2))
        raise SystemExit(1)

    planned_files = sorted(set(rel(p) for p in files + [POINTER]) | {rel(PACKAGE / p) for p in FINAL})
    write(PACKAGE / "changed-paths.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "ownership": "Whole dated package is partitioned among coordinator, institutions, memory and review; navigation additions are coordinator-owned.",
        "repository_paths_created": planned_files, "navigation_paths_modified": list(NAV),
        "local_only_paths_created": raw_paths,
        "ignored_generated_helpers_retained": [rel(p) for p in PACKAGE.rglob("*.pyc")],
        "baseline_changes_observed": baseline_changes,
        "no_commit_push_publication_or_automation": True
    })
    manifest_files = sorted([p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts] + [POINTER] + [ROOT / p for p in NAV])
    write(PACKAGE / "manifest.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Final delivered research files plus current navigation; raw witnesses are pinned by their local source ledgers.",
        "self_and_verification_excluded_to_avoid_recursive_hashing": [rel(PACKAGE / "manifest.json"), rel(PACKAGE / "verification.json")],
        "files": [{"path": rel(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in manifest_files]
    })
    manifest = read(PACKAGE / "manifest.json")
    for record in manifest["files"]:
        check("Final manifest pin: " + record["path"], sha(ROOT / record["path"]) == record["sha256"])
    write(PACKAGE / "verification.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(), "status": "passed",
        "scope": "Delivered-file integrity, source/claim joins, preservation and raw disposition. Mathematical/source review results are separately pinned; this is not a historical-truth check.",
        "checks_passed": sum(c["passed"] for c in CHECKS), "checks_failed": sum(not c["passed"] for c in CHECKS),
        "local_links_checked": link_count, "coordinator_claims": len(claims),
        "baseline": {"files_compared": len(baseline["inventory"]), "unchanged": unchanged, "changes": baseline_changes,
                     "selected_exact_byte_snapshots": len(baseline["original_bytes"]), "ignored_inputs_outside_start_inventory": True},
        "warnings": WARNINGS, "independent_review": review["final_capsule_totals"],
        "manifest_sha256": sha(PACKAGE / "manifest.json"), "checks": CHECKS
    })
    print(json.dumps({"status": "passed", "checks": len(CHECKS), "warnings": len(WARNINGS),
                      "manifest_files": len(manifest["files"]), "raw_files": len(raw_paths),
                      "baseline_unchanged": unchanged, "baseline_changed": len(baseline_changes)}))

if __name__ == "__main__":
    main()
