"""Reviewer scan: personal identifiers, local absolute paths, e-mail addresses and tokens in staged files.
Run from the repository root:  python -B experiments/2026-10-08-hf-public-release/review/privacy_scan.py
"""
import collections
import glob
import json
import os
import re
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
os.chdir(REL)
pat = re.compile(r"(sandh|metbron|gmail|ksaw008|k-sandhu|indus[_-]valley|indus-research-data|data/raw|experiments/|knowledge/|research/|\.\./|C:\\|G:\\|file:///|[A-Za-z]:[\\/]+Users|OneDrive|/Users/|[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}|hf_[A-Za-z0-9]{20,})", re.I)
hits = collections.Counter()
ex = {}


def scan(name, s):
    for m in pat.finditer(s):
        k = (name, m.group(1).lower())
        hits[k] += 1
        ex.setdefault(k, s[max(0, m.start() - 50):m.end() + 60].replace("\n", " "))


for f in glob.glob("data/*.parquet"):
    for r in pq.read_table(f).to_pylist():
        for k, v in r.items():
            if isinstance(v, str):
                scan(f"{f}:{k}", v)
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str):
                        scan(f"{f}:{k}", x)
for dp, dn, fn in os.walk("."):
    for f in fn:
        if f.endswith((".md", ".json", ".cff", ".py", ".txt")) or f in ("LICENSE", "NOTICE", "LICENSE-MIT"):
            p = os.path.join(dp, f)
            scan(p.replace(os.sep, "/"), open(p, encoding="utf-8-sig", errors="replace").read())
out = [dict(where=k[0], match=k[1], count=v, example=ex[k][:160]) for k, v in sorted(hits.items())]
(ROOT / "experiments/2026-10-08-hf-public-release/review-0.3.0/privacy-scan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for o in out:
    print(o["count"], o["where"], o["match"], "|", o["example"][:130])
print("distinct hits:", len(out))
