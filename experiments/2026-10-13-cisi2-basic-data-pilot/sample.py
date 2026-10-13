"""Freeze the first pass and draw the second-pass sample.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/sample.py

Hashes the local first-pass files, then draws max(25, ceil(10% of rows)) CISI numbers
with random.Random(20261013) from the frozen row order. Writes sample.json in this
directory (CISI numbers, pages and file hashes only; no transcribed values).
"""
import hashlib
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot"
FILES = ["pass1-p435.txt", "pass1-p436.txt", "pass1.jsonl"]
SEED = 20261013


def main():
    hashes = {f: hashlib.sha256((LOCAL / f).read_bytes()).hexdigest() for f in FILES}
    rows = [json.loads(line) for line in (LOCAL / "pass1.jsonl").read_text(encoding="utf-8").splitlines()]
    n = max(25, math.ceil(0.10 * len(rows)))
    picked = random.Random(SEED).sample(range(len(rows)), n)
    sample = [{"cisi": rows[i]["cisi"], "printed_page": rows[i]["printed_page"], "pdf_page": rows[i]["pdf_page"]}
              for i in sorted(picked)]
    out = {"frozen_first_pass_sha256": hashes, "rows": len(rows), "seed": SEED, "n": n, "sample": sample}
    (HERE / "sample.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(n, [s["cisi"] for s in sample])


if __name__ == "__main__":
    main()
