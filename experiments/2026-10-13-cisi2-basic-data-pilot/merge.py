"""Merge adjudicated block files into one table and report gaps and duplicates.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/merge.py --out <merged.jsonl> \
      --range M-621:M-1659 [--range H-383:H-1019 ...] <block.final.txt> [...]

Each block file follows the pass format of PROCEDURE.md (first comment line naming
'p. NNN' and 'PDF NNN'). The script parses every block with parse.py, refuses duplicate
CISI numbers, and lists every number inside the given ranges that has no row, so that each
can be checked against the page and recorded as an absence.
"""
import argparse
import collections
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--range", action="append", default=[])
    ap.add_argument("blocks", nargs="+")
    args = ap.parse_args()
    rows = []
    for block in args.blocks:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_out = Path(tmp) / "b.jsonl"
            subprocess.run([sys.executable, str(HERE / "parse.py"), str(tmp_out), block], check=True,
                           stdout=subprocess.DEVNULL)
            for line in tmp_out.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                rec["block_file"] = Path(block).name
                rows.append(rec)
    counts = collections.Counter(r["cisi"] for r in rows)
    dups = sorted(k for k, v in counts.items() if v > 1)
    if dups:
        sys.exit("duplicate CISI numbers across blocks: %s" % ", ".join(dups))
    gaps = {}
    have = set(counts)
    for spec in args.range:
        lo, hi = spec.split(":")
        prefix = re.match(r"^([A-Za-z?]+)-", lo).group(1)
        a, b = int(lo.split("-")[1]), int(hi.split("-")[1])
        gaps[spec] = ["%s-%d" % (prefix, n) for n in range(a, b + 1) if "%s-%d" % (prefix, n) not in have]
    Path(args.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "blocks": len(args.blocks),
                      "missing_in_ranges": {k: {"count": len(v), "first": v[:20]} for k, v in gaps.items()}}, indent=1))


if __name__ == "__main__":
    main()
