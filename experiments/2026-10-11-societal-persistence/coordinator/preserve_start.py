"""Save selected starting bytes and the pre-existing research inventory."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "experiments/2026-10-11-societal-persistence"
RAW = ROOT / "data/raw/2026-10-11-societal-persistence/coordinator/start-v1"
SELECTED = ["README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json",
            "knowledge/retrospectives/README.md", "knowledge/editorial/WRITING.md",
            "knowledge/provenance/REDISTRIBUTION.md", ".gitignore",
            "experiments/2026-10-11-early-indian-continuity/REPORT.md",
            "experiments/2026-10-11-early-indian-continuity/MANUSCRIPT.md",
            "experiments/2026-10-11-early-indian-continuity/RETROSPECTIVE.md",
            "experiments/2026-10-11-early-indian-continuity/verification.json",
            "experiments/2026-10-11-settlement-prospection/README.md"]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def main():
    out = PACKAGE / "baseline-v1.json"
    if out.exists() or RAW.exists():
        raise SystemExit("Starting preservation exists; no overwrite.")
    RAW.mkdir(parents=True)
    originals = []
    for name in SELECTED:
        dst = RAW / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dst)
        originals.append({"path": name, "sha256": digest(ROOT / name), "snapshot": dst.relative_to(ROOT).as_posix()})
        assert digest(dst) == originals[-1]["sha256"]
    paths = set(subprocess.check_output(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT).decode("utf-8").split("\0")) - {""}
    inventory = []
    for name in sorted(paths):
        if name.startswith(PACKAGE.relative_to(ROOT).as_posix() + "/"):
            continue
        path = ROOT / name
        if path.is_file():
            inventory.append({"path": name, "bytes": path.stat().st_size, "sha256": digest(path)})
    out.write_text(json.dumps({"created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Selected exact-byte snapshots and hashes of tracked/unignored pre-existing files; ignored corpora are outside the inventory.",
        "original_bytes": originals, "inventory": inventory}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"snapshots": len(originals), "inventory": len(inventory)}))

if __name__ == "__main__":
    main()
