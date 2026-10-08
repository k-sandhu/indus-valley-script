"""Reviewer check: compare the reviewer's fresh build (review/rebuild) with the staged release byte for byte, then delete the copy.
Compared: data/*.parquet, images/**/*.png, code/*.py, benchmark/*.json and benchmark/CONVENTIONS.md where the rebuild produced them.
Run from the repository root:  python -B experiments/2026-10-08-hf-public-release/review/rebuild_compare.py [--keep]
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
A = PKG / "release"
B = PKG / "review/rebuild"
rows = []
for f in sorted(B.rglob("*")):
    if not f.is_file():
        continue
    rel = f.relative_to(B).as_posix()
    a = A / rel
    rows.append(dict(path=rel, staged_exists=a.exists(), equal=a.exists() and a.read_bytes() == f.read_bytes()))
by_kind = {}
for r in rows:
    k = r["path"].split("/")[0] if "/" in r["path"] else "root"
    d = by_kind.setdefault(k, dict(files=0, equal=0, missing_in_staged=0))
    d["files"] += 1
    d["equal"] += r["equal"]
    d["missing_in_staged"] += not r["staged_exists"]
unequal = [r["path"] for r in rows if not r["equal"]]
out = dict(rebuilt_files=len(rows), equal=sum(r["equal"] for r in rows), by_top_folder=by_kind, unequal_paths=unequal)
(PKG / "review/rebuild-comparison.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
if "--keep" not in sys.argv:
    shutil.rmtree(B)
    print("removed review/rebuild")
