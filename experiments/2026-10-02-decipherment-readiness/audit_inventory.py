"""Capture the existing registry and audit-source inventory without rerunning studies."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    output = HERE / "baseline-v1"
    if output.exists():
        raise SystemExit("Preserved baseline already exists; choose a new dated endpoint.")
    registry_bytes = (ROOT / "knowledge/experiments/registry.json").read_bytes()
    registry = json.loads(registry_bytes)
    entries = registry["experiments"]
    evidence = []
    for entry in entries:
        for name in entry["evidence"]:
            path = ROOT / name
            evidence.append({"entry": entry["id"], "path": name,
                             "exists": path.exists(),
                             "kind": "directory" if path.is_dir() else "file",
                             "bytes": path.stat().st_size if path.is_file() else None})
    sources = [
        "AGENTS.md", "README.md", "knowledge/INDEX.md",
        "knowledge/editorial/WRITING.md", "knowledge/retrospectives/six-hour-integration.md",
        "knowledge/research-contributions.md", "knowledge/directions/research-roadmap.md",
        "knowledge/directions/context-data-plan.md", "knowledge/directions/community-proposals.md",
        "knowledge/directions/cryptography.md", "knowledge/directions/archaeology-and-iconography.md",
        "research/literature/external_phonetic_anchor_audit.md",
        "research/literature/metrology/numerical_source_audit.md",
        "research/literature/metrology/source_and_identifiability_audit.json",
        "research/literature/metrology/source_capacity_table.csv",
        "research/literature/evidence_and_novelty_matrix.md", "research/NEXT_TESTS.md",
        "papers/001-artifact-aware-prediction/manuscript.md",
        "papers/002-conditional-reference-laws/manuscript.md",
        "papers/003-physical-observations/manuscript.md",
        "papers/004-reference-model-selection/manuscript.md",
    ]
    witnesses = []
    for name in sources:
        payload = (ROOT / name).read_bytes()
        witnesses.append({"path": name, "bytes": len(payload),
                          "sha256": hashlib.sha256(payload).hexdigest()})
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
        "registry_entries": len(entries), "registry_ids": [x["id"] for x in entries],
        "status_counts": dict(sorted(Counter(x["status"] for x in entries).items())),
        "evidence_occurrences": evidence, "source_witnesses": witnesses,
        "missing_evidence": [x for x in evidence if not x["exists"]],
        "scope": "Existing indexed work and selected source/manuscript bytes. Evidence existence is checked; numerical studies are not refitted and every output row is not re-audited.",
    }
    output.mkdir()
    (output / "registry-input.json").write_bytes(registry_bytes)
    (output / "inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("input_commit", "registry_entries", "registry_sha256", "missing_evidence")}))
    if result["missing_evidence"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
