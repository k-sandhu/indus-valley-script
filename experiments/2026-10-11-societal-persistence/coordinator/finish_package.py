"""Verify source/output joins and preservation, then freeze delivered-file records.

This validates the research package and its declared dependencies. Historical
calibration and the prospective archaeological tests are outside its scope.
"""
from __future__ import annotations
import ast
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
RAW = ROOT / "data/raw/2026-10-11-societal-persistence"
NAV = ("README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json",
       "knowledge/retrospectives/README.md")
POINTER = ROOT / "knowledge/retrospectives/2026-10-11-societal-persistence.md"
FINAL = ("changed-paths.json", "manifest.json", "verification.json")
CHECKS: list[dict] = []
WARNINGS: list[dict] = []
HASH_CACHE: dict[Path, str] = {}


def sha(path: Path) -> str:
    path = path.resolve()
    if path not in HASH_CACHE:
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                h.update(block)
        HASH_CACHE[path] = h.hexdigest()
    return HASH_CACHE[path]


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check(name: str, condition: bool, details=None) -> None:
    CHECKS.append({"check": name, "passed": bool(condition), "details": details})


def pin(path: Path, expected: str, label: str, size=None) -> None:
    check(label, path.is_file() and sha(path) == expected and
          (size is None or path.stat().st_size == size), rel(path))


def write(path: Path, value) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def pointer(value, address: str):
    if not address:
        return value
    for token in address.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def frozen_checks(name: str, count: int, rows="checks", total="checks_passed"):
    result = read(PACKAGE / name)
    records = result[rows]
    check("Frozen assertions all pass: " + name,
          len(records) == count and result[total] == count and
          all(record["passed"] for record in records))
    return result


def ledger_pins(value, seen: set[tuple[str, str]]) -> None:
    if isinstance(value, list):
        for item in value:
            ledger_pins(item, seen)
    elif isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            item = (value["path"], value["sha256"])
            if item not in seen:
                seen.add(item)
                pin(ROOT / item[0], item[1], "Source witness or derivative pin", value.get("bytes"))
        for item in value.values():
            ledger_pins(item, seen)


def main() -> None:
    if any((PACKAGE / name).exists() for name in FINAL):
        raise SystemExit("A final endpoint exists. No overwrite; use a dated successor.")
    files = sorted(path for path in PACKAGE.rglob("*") if path.is_file() and
                   "__pycache__" not in path.parts and path.suffix != ".pyc")
    planned = {(PACKAGE / name).resolve() for name in FINAL}
    for path in files:
        if path.suffix == ".json":
            try:
                read(path)
                check("JSON parses: " + rel(path), True)
            except (ValueError, UnicodeError) as exc:
                check("JSON parses: " + rel(path), False, str(exc))
        elif path.suffix == ".py":
            try:
                compile(ast.parse(path.read_text(encoding="utf-8")), str(path), "exec")
                check("Python compiles: " + rel(path), True)
            except (SyntaxError, UnicodeError) as exc:
                check("Python compiles: " + rel(path), False, str(exc))
    check("No raw binary publication payload in research package",
          not any(path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
                  for path in files))
    check("No CI or deployment scaffolding in this package",
          not any(".github" in path.parts or path.name in {"Dockerfile", "Procfile"} for path in files))

    link_count = 0
    markdown = [path for path in files if path.suffix == ".md"] + [POINTER]
    for path in markdown:
        for match in re.finditer(r"\[[^\n]*?\]\((?:<([^>\n]+)>|([^\n)]+))\)",
                                 path.read_text(encoding="utf-8")):
            target = (match.group(1) or match.group(2)).strip()
            if re.match(r"(?:https?://|mailto:|codex:|#)", target):
                continue
            target = unquote(target.split("#", 1)[0])
            local = (path.parent / target).resolve()
            link_count += 1
            check("Local Markdown link: " + rel(path), local.exists() or local in planned, target)

    claims = read(PACKAGE / "CLAIM-EVIDENCE.json")["claims"]
    check("Fifteen distinct synthesis claims", len(claims) == len({c["id"] for c in claims}) == 15)
    output_joins = 0
    for claim in claims:
        for reference in claim["observations"]:
            observations = read(ROOT / reference["file"])["observations"]
            ids = {item.get("id", item.get("observation_id")) for item in observations}
            check("Claim observation join: " + claim["id"], set(reference["ids"]) <= ids, reference)
        for output in claim["outputs"]:
            try:
                value = pointer(read(ROOT / output["file"]), output["pointer"])
                passed = ("equals" not in output or value == output["equals"]) and (
                    "excludes" not in output or output["excludes"] not in value)
                check("Claim exact output join: " + claim["id"], passed, output)
            except (KeyError, IndexError, ValueError, TypeError) as exc:
                check("Claim exact output join: " + claim["id"], False, str(exc))
            output_joins += 1
        for key in ("discussion", "test", "independent_check"):
            check("Claim prose reference: " + claim["id"], (ROOT / claim[key]).is_file(), claim[key])

    final_review = frozen_checks("review/reviewer-final-v1/checks.json", 280)
    check("No unresolved substantive review blocker", final_review["no_unresolved_blockers"] is True)
    for key in ("reviewed_file_sha256", "supporting_file_sha256"):
        for name, expected in final_review[key].items():
            pin(ROOT / name, expected, "Independent review final pin")
    pin(PACKAGE / "review/FINAL-REVIEW-PROTOCOL.md", final_review["protocol_sha256"], "Final review protocol pin")
    pin(PACKAGE / "review/check_final.py", final_review["checker_sha256"], "Final review code pin")

    baseline_model = read(HERE / "run-v1/results.json")
    pin(HERE / "MODEL-PROTOCOL.md", baseline_model["protocol_sha256"], "Baseline model protocol pin")
    pin(HERE / "renewal_model.py", baseline_model["code_sha256"], "Baseline model code pin")
    check("Baseline state space and world census", baseline_model["state_count"] == 36 and
          baseline_model["safe_state_count"] == 16 and len(baseline_model["worlds"]) == 32)
    reconstruction = frozen_checks("review/model-checks-v1/checks.json", 5218)
    pin(HERE / "run-v1/results.json", reconstruction["root_results_sha256"], "Independent baseline output pin")
    pin(PACKAGE / "review/CHECKER-PROTOCOL.md", reconstruction["review_protocol_sha256"], "Independent baseline protocol pin")
    pin(PACKAGE / "review/check_model.py", reconstruction["checker_sha256"], "Independent baseline code pin")
    copro = frozen_checks("review/co-production-v1/results.json", 1133)
    pin(PACKAGE / "review/CO-PRODUCTION-PROTOCOL.md", copro["protocol_sha256"], "Shared-operation protocol pin")
    pin(PACKAGE / "review/co_production.py", copro["code_sha256"], "Shared-operation code pin")
    pin(HERE / "run-v1/results.json", copro["baseline_results_sha256"], "Shared-operation baseline pin")
    pin(PACKAGE / "review/model-checks-v1/checks.json", copro["baseline_independent_check_sha256"], "Shared-operation prior check pin")
    independent_copro = frozen_checks("coordinator/co-production-checks-v1/checks.json", 1968)
    pin(PACKAGE / "review/co-production-v1/results.json", independent_copro["reviewer_output_sha256"], "Second shared-operation output pin")
    pin(HERE / "check_coproduction.py", independent_copro["checker_sha256"], "Second shared-operation code pin")
    examples = read(PACKAGE / "review/counterexamples-v1/counterexamples.json")
    check("Six declared counterexample assertions pass", len(examples["assertions"]) == 6 and
          all(examples["assertions"].values()))
    for name, expected in examples["input_hashes"].items():
        pin(PACKAGE / "review" / name, expected, "Counterexample frozen input")

    source_review = frozen_checks("review/source-checks-v3/checks.json", 90)
    for filename, key in (("sources.json", "source_ledger_sha256"), ("claims.json", "claims_sha256"),
                          ("falsifiers.json", "falsifiers_sha256"), ("source_audit_v3.py", "code_sha256")):
        pin(PACKAGE / "review" / filename, source_review[key], "Independent source audit input")
    review_integrity = frozen_checks("review/verification.json", 50)
    for name, expected in review_integrity["own_files_sha256"].items():
        pin(PACKAGE / "review" / name, expected, "Reviewer owned artifact pin")
    archaeological_audit = read(PACKAGE / "evidence/run-v2/summary.json")
    archaeological_checks = read(PACKAGE / "evidence/run-v2/checks.json")
    check("Archaeological source audit passes", archaeological_audit["checks"] ==
          archaeological_audit["passed"] == len(archaeological_checks) == 275 and
          not archaeological_audit["failed"] and all(row["passed"] for row in archaeological_checks))
    for name, expected in read(PACKAGE / "evidence/run-v2/input-hashes.json").items():
        pin(ROOT / name, expected, "Archaeological audit frozen input")
    frozen_checks("evidence/verification-v3/verification.json", 16, "details", "passed")
    literature_audit = frozen_checks("literature/source-checks-v1.json", 312, "results", "passed")
    for name, expected in literature_audit["input_hashes"].items():
        pin(PACKAGE / "literature" / name, expected, "Literature source audit input")
    pin(PACKAGE / "literature/audit_sources.py", literature_audit["checker_sha256"], "Literature source audit code")
    literature_inventory = read(PACKAGE / "literature/changed-paths.json")
    for key in ("authored_artifact_hashes", "local_only_raw_paths", "ignored_local_generated_helpers",
                "unmodified_collaborator_dependencies"):
        for record in literature_inventory[key]:
            pin(ROOT / record["path"], record["sha256"], "Literature final inventory pin", record["bytes"])
    evidence_inventory = read(PACKAGE / "evidence/changed-paths.json")
    for key in ("authored_files", "raw_local_only_files"):
        for record in evidence_inventory[key]:
            pin(ROOT / record["path"], record["sha256"], "Evidence final inventory pin", record["bytes"])
    review_supplement = read(PACKAGE / "review/changed-paths-final-v1.json")
    pin(PACKAGE / "review/reviewer-final-v1/checks.json", review_supplement["final_review_result_sha256"], "Final reviewer delivery pin")
    check("Reviewer supplemental inventory contains current owned files",
          set(review_supplement["review_paths"]) ==
          {rel(path) for path in files if path.is_relative_to(PACKAGE / "review") and
           path.name != "changed-paths-final-v1.json"})

    seen: set[tuple[str, str]] = set()
    for name in ("literature/SOURCES.json", "evidence/sources.json", "review/sources.json", "coordinator/SOURCES.json"):
        ledger_pins(read(PACKAGE / name), seen)
    summary = read(HERE / "source-summary-v1.json")
    for name, expected in summary["input_sha256"].items():
        pin(PACKAGE / name, expected, "Source census frozen input")
    check("Independent census equals synthesis census", final_review["reconstructed_source_summary"] ==
          {key: summary[key] for key in ("literature", "archaeological_application", "shared_operation_variant")})
    anchor_review = read(PACKAGE / "review/final-source-controls.json")
    pin(PACKAGE / "evidence/sources.json", anchor_review["sources_ledger_sha256"], "Direct archaeological review source pin")
    pin(PACKAGE / "evidence/observations.json", anchor_review["observations_ledger_sha256"], "Direct archaeological review observation pin")
    for record in anchor_review["records"]:
        pin(ROOT / record["witness_path"], record["witness_sha256"], "Direct archaeological witness pin")
    for name in ("review/source-checks-v1/failure.json", "review/source-checks-v2/failure.json",
                 "review/integrity-checks-v1/failure.json", "evidence/run-v1/summary.json",
                 "evidence/audit-v1.py", "evidence/verification-v1/verification.json"):
        check("Earlier attempt retained", (PACKAGE / name).is_file(), name)
    prose = read(HERE / "prose-scan-v2.json")
    prose_review = read(HERE / "prose-review-v2.json")
    check("Final prose flags reviewed as exact source titles", prose["files_scanned"] == len(markdown) == 33 and
          len(prose["flags"]) == 2 and prose_review["flags"] == 2 and
          not prose_review["unresolved_editorial_flags"] and
          all(flag["pattern"] == "em_dash" and "Indian Archaeology" in flag["text"] for flag in prose["flags"]))

    baseline = read(PACKAGE / "baseline-v1.json")
    for record in baseline["original_bytes"]:
        pin(ROOT / record["snapshot"], record["sha256"], "Selected exact starting-byte snapshot")
    baseline_changes = []
    unchanged = 0
    for record in baseline["inventory"]:
        path = ROOT / record["path"]
        current = sha(path) if path.is_file() else None
        if current == record["sha256"]:
            unchanged += 1
        else:
            category = ("this program navigation" if record["path"] in NAV else
                        "this program owned path" if path.is_relative_to(PACKAGE) else
                        "shared workspace change outside this program ownership")
            baseline_changes.append({"path": record["path"], "start_sha256": record["sha256"],
                                     "current_sha256": current, "classification": category})
    outside = [item for item in baseline_changes if item["classification"].startswith("shared")]
    if outside:
        WARNINGS.append({"type": "shared-workspace-baseline-changes", "count": len(outside),
                         "scope": "Observed differences outside ownership were retained. Attribution and whole-file byte backups are not implied.",
                         "paths": [item["path"] for item in outside]})
    integration = read(HERE / "navigation-integration-v1.json")
    for record in integration["files"]:
        pin(ROOT / record["snapshot"], record["before_sha256"], "Current navigation pre-edit snapshot")
        pin(ROOT / record["path"], record["after_sha256"], "Navigation additions pin")
    old_registry = read(ROOT / next(record["snapshot"] for record in integration["files"] if record["path"] == NAV[2]))
    current_registry = read(ROOT / NAV[2])
    additions = read(HERE / "registry-additions.json")
    check("All prior registry objects retained in order", current_registry["experiments"] ==
          old_registry["experiments"] + additions and len(additions) == 4)
    for entry in additions:
        for name in entry["evidence"]:
            check("Registry evidence target: " + entry["id"], (ROOT / name).is_file(), name)

    raw_paths = sorted(rel(path) for path in RAW.rglob("*") if path.is_file())
    helpers = sorted(rel(path) for path in PACKAGE.rglob("*.pyc"))
    ignored_inputs = raw_paths + helpers
    result = subprocess.run(["git", "check-ignore", "--no-index", "-z", "--stdin"], cwd=ROOT,
                            input=b"\0".join(name.encode("utf-8") for name in ignored_inputs) + b"\0", capture_output=True)
    ignored = {name.decode("utf-8").replace("\\", "/") for name in result.stdout.split(b"\0") if name}
    check("All raw sources and generated helpers Git-ignored", result.returncode == 0 and
          ignored == set(ignored_inputs), {"files": len(ignored_inputs), "ignored": len(ignored)})
    tracked = subprocess.run(["git", "ls-files", "-z", "--", rel(RAW)], cwd=ROOT, capture_output=True, check=True)
    check("No acquired raw source tracked", not tracked.stdout)
    failures = [record for record in CHECKS if not record["passed"]]
    if failures:
        attempt = {"status": "failed before final-output creation", "failures": failures}
        # Failed packaging attempts remain visible without replacing any endpoint.
        failure_dir = HERE / "packaging-attempts"
        failure_dir.mkdir(exist_ok=True)
        write(failure_dir / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + ".json"), attempt)
        print(json.dumps(attempt, ensure_ascii=True, indent=2))
        raise SystemExit(1)

    planned_paths = sorted({rel(path) for path in files + [POINTER]} | {rel(PACKAGE / name) for name in FINAL})
    write(PACKAGE / "changed-paths.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "ownership": "Coordinator owns root/coordinator and navigation additions. Literature, evidence and review contributors own their distinct subdirectories.",
        "repository_paths_created": planned_paths, "navigation_paths_modified": list(NAV),
        "local_only_paths_created": raw_paths, "ignored_generated_helpers_retained": helpers,
        "baseline_changes_observed": baseline_changes,
        "no_commit_push_publication_or_automation": True
    })
    manifest_files = sorted([path for path in PACKAGE.rglob("*") if path.is_file() and
                             "__pycache__" not in path.parts and path.suffix != ".pyc"] +
                            [POINTER] + [ROOT / name for name in NAV])
    write(PACKAGE / "manifest.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Delivered own research files and current navigation; raw source contents remain local and their hashes remain in source ledgers.",
        "self_and_verification_excluded_to_avoid_recursive_hashing": [rel(PACKAGE / "manifest.json"), rel(PACKAGE / "verification.json")],
        "files": [{"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path)} for path in manifest_files]
    })
    manifest = read(PACKAGE / "manifest.json")
    for record in manifest["files"]:
        pin(ROOT / record["path"], record["sha256"], "Delivered manifest pin", record["bytes"])
    write(PACKAGE / "verification.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(), "status": "passed",
        "scope": "File integrity, declared source and exact output joins, previous-work preservation and local source disposition. Separate numerical and substantive reviews are pinned; this does not confirm historical applicability.",
        "checks_passed": sum(record["passed"] for record in CHECKS),
        "checks_failed": sum(not record["passed"] for record in CHECKS),
        "local_links_checked": link_count, "synthesis_claims": len(claims), "exact_output_joins": output_joins,
        "source_witness_pins": len(seen), "local_only_raw_files": len(raw_paths),
        "baseline": {"files_compared": len(baseline["inventory"]), "unchanged": unchanged,
                     "changes": baseline_changes, "selected_exact_byte_snapshots": len(baseline["original_bytes"]),
                     "ignored_inputs_outside_start_inventory": True},
        "warnings": WARNINGS, "independent_review": final_review["verification_totals"],
        "literature_integrity_checks": 312, "evidence_final_packaging_checks": 16,
        "prose_scan": {"files": 33, "source_title_exemptions": 2, "unresolved_flags": 0},
        "manifest_sha256": sha(PACKAGE / "manifest.json"), "checks": CHECKS
    })
    print(json.dumps({"status": "passed", "checks": len(CHECKS), "warnings": len(WARNINGS),
                      "manifest_files": len(manifest["files"]), "raw_files": len(raw_paths),
                      "baseline_unchanged": unchanged, "baseline_changed": len(baseline_changes)}))


if __name__ == "__main__":
    main()
