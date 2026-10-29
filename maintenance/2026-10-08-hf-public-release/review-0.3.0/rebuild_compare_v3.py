"""Compare a fresh build of the 0.3.0 release (made from a scratch copy of the package's build code, so nothing in the package
directory is written) with release/ byte for byte, in both directions.

Usage: python -B rebuild_compare_v3.py --rebuild <dir>
Writes review-0.3.0/rebuild-comparison.json.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "experiments/2026-10-08-hf-public-release/release"
ap = argparse.ArgumentParser()
ap.add_argument("--rebuild", required=True)
B = Path(ap.parse_args().rebuild)


def files(base):
    return {p.relative_to(base).as_posix(): p for p in base.rglob("*") if p.is_file()}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


FA, FB = files(A), files(B)
both = sorted(set(FA) & set(FB))
unequal = [k for k in both if sha(FA[k]) != sha(FB[k])]
by_kind = {}
for k in both:
    top = k.split("/")[0] if "/" in k else "root"
    d = by_kind.setdefault(top, {"files": 0, "equal": 0})
    d["files"] += 1
    d["equal"] += k not in unequal
out = {"release_files": len(FA), "rebuilt_files": len(FB), "equal": len(both) - len(unequal),
       "only_in_release": sorted(set(FA) - set(FB)), "only_in_rebuild": sorted(set(FB) - set(FA)),
       "unequal": unequal, "by_top_folder": by_kind,
       "bytes_release": sum(p.stat().st_size for p in FA.values()), "bytes_rebuild": sum(p.stat().st_size for p in FB.values())}
Path(__file__).with_name("rebuild-comparison.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
