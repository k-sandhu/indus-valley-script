"""Reviewer check: recompute SHA256 of every staged file against provenance/file-manifest.json and table-manifest.json.
Run from the repository root:  python -B experiments/2026-10-08-hf-public-release/review/manifest_check.py
"""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
os.chdir(REL)
m = json.loads(Path("provenance/file-manifest.json").read_text(encoding="utf-8-sig"))
rows = m if isinstance(m, list) else m.get("files", m)
if isinstance(rows, dict):
    rows = [dict(path=k, **(v if isinstance(v, dict) else {"sha256": v})) for k, v in rows.items()]
bad = []
seen = set()
for r in rows:
    p = r["path"].replace("\\", "/")
    seen.add(p)
    if hashlib.sha256(Path(p).read_bytes()).hexdigest() != r["sha256"]:
        bad.append(p)
disk = {os.path.relpath(os.path.join(dp, f), ".").replace("\\", "/") for dp, dn, fn in os.walk(".") for f in fn}
t = json.loads(Path("provenance/table-manifest.json").read_text(encoding="utf-8-sig"))
bad2 = [k for k, v in t.items() if hashlib.sha256(Path(v["data_file"]).read_bytes()).hexdigest() != v["sha256"]]
out = dict(manifest_entries=len(rows), checksum_mismatches=bad, on_disk_not_in_manifest=sorted(disk - seen), in_manifest_not_on_disk=sorted(seen - disk),
           table_manifest_entries=len(t), table_checksum_mismatches=bad2, files_on_disk=len(disk))
(ROOT / "experiments/2026-10-08-hf-public-release/review-0.3.0/manifest-check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
