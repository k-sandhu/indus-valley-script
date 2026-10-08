"""Compare the Hub snapshot (downloaded to a short path) with the local release folder, byte for byte.

Usage: python -B hub_file_compare.py --snapshot C:/hfc030/snap --out hub-file-compare.json
"""
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
ap = argparse.ArgumentParser()
ap.add_argument("--snapshot", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
snap = Path(a.snapshot)

def files(base):
    return {p.relative_to(base).as_posix(): p for p in base.rglob("*") if p.is_file() and ".cache" not in p.relative_to(base).parts}

L, H = files(REL), files(snap)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
only_local = sorted(set(L) - set(H))
only_hub = sorted(set(H) - set(L))
diff = [k for k in sorted(set(L) & set(H)) if sha(L[k]) != sha(H[k])]
out = {"local_files": len(L), "hub_files": len(H), "only_local": only_local, "only_hub": only_hub,
       "different_bytes": diff, "identical": len(set(L) & set(H)) - len(diff),
       "bytes_local": sum(p.stat().st_size for p in L.values()), "bytes_hub": sum(p.stat().st_size for p in H.values())}
Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
