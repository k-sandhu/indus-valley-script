"""Check review coverage, original registry entries and preserved source witnesses."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def main():
    output = HERE / "review-v1"
    if output.exists():
        raise SystemExit("Review endpoint exists; preserve it and choose a new endpoint.")
    baseline = json.loads((HERE / "baseline-v1/inventory.json").read_text(encoding="utf-8"))
    original_bytes = (HERE / "baseline-v1/registry-input.json").read_bytes()
    original = json.loads(original_bytes)["experiments"]
    current = json.loads((ROOT / "knowledge/experiments/registry.json").read_text(encoding="utf-8"))["experiments"]
    current_by_id = {entry["id"]: entry for entry in current}
    ids = {entry["id"] for entry in original}
    checks = []

    def check(name, passed, detail=None):
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    check("baseline registry hash", sha(original_bytes) == baseline["registry_sha256"])
    check("baseline registry has 101 distinct entries", len(original) == len(ids) == 101)
    check("all original registry entry values preserved",
          all(current_by_id.get(entry["id"]) == entry for entry in original))
    check("all baseline indexed evidence exists",
          all((ROOT / row["path"]).exists() for row in baseline["evidence_occurrences"]))
    coverage_paths = {
        "corpus": ("corpus/inventory-final-2026-10-02/coverage.json", "registry_ids_read"),
        "computational": ("computational/coverage.json", "reviewed_registry_ids"),
        "physical": ("physical/coverage.json", "catalogue_read_ids"),
    }
    coverage_counts = {}
    for name, (relative, field) in coverage_paths.items():
        result = json.loads((HERE / relative).read_text(encoding="utf-8"))
        reviewed = result[field]
        check(name + " exact registry-ID coverage", len(reviewed) == len(set(reviewed)) == 101 and set(reviewed) == ids)
        coverage_counts[name] = len(reviewed)
    computational = json.loads((HERE / "computational/coverage.json").read_text(encoding="utf-8"))
    families = computational["family_counts"]
    check("capability-family partition", len(families) == 17 and sum(families.values()) == 101)
    source_results = []
    for witness in baseline["source_witnesses"]:
        name = witness["path"]
        current_matches = sha((ROOT / name).read_bytes()) == witness["sha256"]
        historic = subprocess.check_output(["git", "show", baseline["input_commit"] + ":" + name], cwd=ROOT)
        historical_matches = sha(historic) == witness["sha256"]
        check("preserved baseline source " + name, historical_matches)
        source_results.append({"path": name, "current_matches": current_matches,
                               "baseline_git_witness_matches": historical_matches})
    reports = ["README.md", "RETROSPECTIVE.md", "corpus/REPORT.md",
               "computational/REPORT.md", "physical/REPORT.md", "physical/ACQUISITION.md"]
    for name in reports:
        check("readable report exists " + name, (HERE / name).is_file())
    manifest = []
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            payload = path.read_bytes()
            manifest.append({"path": path.relative_to(ROOT).as_posix(),
                             "bytes": len(payload), "sha256": sha(payload)})
    reader_report = ROOT / "knowledge/directions/decipherment-readiness-2026-10-02.md"
    reader_bytes = reader_report.read_bytes()
    manifest.append({"path": reader_report.relative_to(ROOT).as_posix(),
                     "bytes": len(reader_bytes), "sha256": sha(reader_bytes)})
    result = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "pass": all(row["pass"] for row in checks), "checks": checks,
              "coverage_counts": coverage_counts, "source_preservation": source_results,
              "review_file_manifest": manifest,
              "scope": "Registry coverage, preserved original entry values, baseline Git/source bytes and review artifact presence. This is not a new semantic experiment or a rerun of the scientific models."}
    output.mkdir()
    (output / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "checks": len(checks),
                      "coverage": coverage_counts,
                      "failed": [row for row in checks if not row["pass"]]}))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
