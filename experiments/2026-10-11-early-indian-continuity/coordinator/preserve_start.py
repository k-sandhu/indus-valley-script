"""Preserve selected starting bytes and hash the existing research inventory."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
PROGRAM = ROOT / "experiments/2026-10-11-early-indian-continuity"
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/coordinator/start-v1"
SELECTED = [
    "README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json",
    "knowledge/retrospectives/README.md", "knowledge/editorial/WRITING.md",
    "knowledge/provenance/REDISTRIBUTION.md", ".gitignore",
    "knowledge/retrospectives/2026-10-11-two-approaches.md",
    "experiments/2026-10-11-two-approaches/REPORT.md",
    "experiments/2026-10-11-two-approaches/REVIEW-RESPONSE.md",
    "experiments/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections/RETROSPECTIVE.md",
    "experiments/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections/REPORT.md",
    "knowledge/directions/archaeology-and-iconography.md",
]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def main() -> None:
    out = PROGRAM / "baseline-v1.json"
    if out.exists():
        raise SystemExit("Frozen starting manifest exists; do not overwrite it.")
    RAW.mkdir(parents=True, exist_ok=True)
    originals = []
    for name in SELECTED:
        src, dst = ROOT / name, RAW / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        originals.append({"path": name, "sha256": digest(src),
                          "snapshot": dst.relative_to(ROOT).as_posix()})
        assert digest(dst) == originals[-1]["sha256"]
    names = set(subprocess.check_output(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0")) - {""}
    files = []
    for name in sorted(names):
        if name.startswith("experiments/2026-10-11-early-indian-continuity/"):
            continue
        path = ROOT / name
        if path.is_file():
            files.append({"path": name, "sha256": digest(path),
                          "bytes": path.stat().st_size})
    result = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Exact bytes of selected inputs/navigation; hashes of other existing tracked or unignored files. Ignored raw corpora are outside the broad inventory.",
              "original_bytes": originals, "inventory": files,
              "git_status": subprocess.check_output(
                  ["git", "status", "--short"], cwd=ROOT).decode("utf-8")}
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"snapshots": len(originals), "inventory": len(files),
                      "manifest": str(out.relative_to(ROOT))}))

if __name__ == "__main__":
    main()
