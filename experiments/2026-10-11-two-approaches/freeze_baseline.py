"""Record prior endpoints and local working state without changing them."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-11-two-approaches/coordinator/baseline-v1"

DIRECTORIES = [
    "experiments/2026-10-11-bonta-adversarial",
    "experiments/2026-10-08-bonta-extension",
    "experiments/2026-10-08-bonta-review",
    "experiments/2026-10-06-field-recommendations",
    "experiments/2026-10-02-connections-and-priority/harappa-short-records",
]
FILES = [
    "README.md", "AGENTS.md", ".gitignore", "knowledge/INDEX.md",
    "knowledge/experiments/registry.json", "knowledge/editorial/WRITING.md",
    "knowledge/provenance/REDISTRIBUTION.md",
    "knowledge/retrospectives/methods.md",
    "knowledge/retrospectives/corpus-and-transcription.md",
    "knowledge/retrospectives/2026-10-11-bonta-adversarial.md",
    "src/methods/conditional_structure.py",
    "data/normalized/lipi_observed_faces.jsonl",
    "data/normalized/lipi_clean_rtl_singleline.jsonl",
]
NAVIGATION = {"README.md", ".gitignore", "knowledge/INDEX.md", "knowledge/experiments/registry.json"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    out = HERE / "baseline-v1.json"
    if out.exists() or RAW.exists():
        raise SystemExit("Baseline already exists; preserve it and select a new version.")
    paths = {ROOT / name for name in FILES}
    for directory in DIRECTORIES:
        paths.update(p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    records = []
    for path in sorted(paths):
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append({"path": rel, "sha256": sha(path), "bytes": path.stat().st_size,
                        "navigation_may_be_extended": rel in NAVIGATION})
    RAW.mkdir(parents=True, exist_ok=False)
    for name in NAVIGATION:
        target = RAW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    proc = subprocess.run(["git", "status", "--porcelain=v1"], cwd=ROOT,
                          capture_output=True, text=True, check=True)
    (RAW / "working-state.txt").write_text(proc.stdout, encoding="utf-8")
    result = {"status": "pre-integration-preservation-record", "date": "2026-10-11",
              "local_navigation_backup": RAW.relative_to(ROOT).as_posix(),
              "policy": "Earlier outputs are immutable. Navigation can be extended with separately preserved original bytes.",
              "files": records}
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"recorded_files": len(records), "manifest": out.relative_to(ROOT).as_posix()}))


if __name__ == "__main__":
    main()
