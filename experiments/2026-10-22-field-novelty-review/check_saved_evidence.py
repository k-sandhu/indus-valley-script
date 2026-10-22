"""Audit already saved evidence for the 2026-10-22 publication review."""
from pathlib import Path
import hashlib
import json
import platform
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

original_path = ROOT / "experiments/2026-10-20-seal-legend-units/run-2026-10-20/bench/plate_order-supervised.json"
replay_path = HERE / "segmentation-replay.json"
original, replay = read_json(original_path), read_json(replay_path)
provenance = []
for entry in original["provenance"]:
    path = ROOT / entry["path"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    provenance.append({"path": entry["path"], "expected_sha256": entry["sha256"],
                       "actual_sha256": actual, "matches": actual == entry["sha256"]})
broken_links = []
checked_links = 0
for path in HERE.glob("*.md"):
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" in target or target.startswith("#"):
            continue
        checked_links += 1
        if not (path.parent / target.split("#")[0]).exists():
            broken_links.append({"file": path.name, "target": target})
result = {
    "status_class": "source-review",
    "python": platform.python_version(),
    "git_head_at_review": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "scope": "Saved-input scorer replay and file-hash verification; no training rerun or source-label adjudication.",
    "segmentation_json_identical": original == replay,
    "segmentation_scores": replay["scores"],
    "derived_recall_minus_elsewhere_rate": replay["scores"]["boundary_recall"] - replay["scores"]["boundary_rate_elsewhere"],
    "provenance_checks": provenance,
    "relative_links_checked": checked_links,
    "broken_relative_links": broken_links,
    "inputs": [{"path": str(p.relative_to(ROOT)).replace(chr(92), "/"), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in (original_path, replay_path)],
}
out = HERE / "EVIDENCE-CHECKS.json"
if out.exists():
    raise SystemExit("Refusing to overwrite existing check endpoint")
out.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
print(json.dumps({"identical": result["segmentation_json_identical"],
                  "provenance_match": all(r["matches"] for r in provenance),
                  "links_checked": checked_links, "broken_links": broken_links}, indent=2))

