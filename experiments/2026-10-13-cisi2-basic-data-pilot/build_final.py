"""Apply the adjudicated sample and the targeted recheck to the frozen first pass.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/build_final.py

Reads the local pass1-p435.txt and pass1-p436.txt, adjudication.json (sample),
adjudication-full.json (Amendment 1, if present) and recheck/recheck.json, and writes
final-p435.txt, final-p436.txt and final.jsonl in
data/raw/2026-10-13-cisi2-basic-data-pilot/ (local only), plus changes.json there listing
every cell changed and why. The first-pass files are not modified.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot"
COLS = ["col1", "col2_fc", "col3_excavation", "col4_museum", "col5_photographs"]


def main():
    adj = json.loads((LOCAL / "adjudication.json").read_text(encoding="utf-8"))
    rec = json.loads((LOCAL / "recheck" / "recheck.json").read_text(encoding="utf-8"))["items"]
    full_path = LOCAL / "adjudication-full.json"
    adj_full = json.loads(full_path.read_text(encoding="utf-8")) if full_path.exists() else []
    fixes = {}
    decided = set()
    for a in adj:  # blind sample adjudication first
        key = (a["cisi"], a["column"])
        decided.add(key)
        if a["outcome"] in ("second-pass-right", "both-wrong", "undecidable"):
            fixes[key] = (a["adjudicated"], "sample-" + a["outcome"])
    for a in adj_full:  # Amendment 1: full second reading
        key = (a["cisi"], a["column"])
        if key in decided:
            continue
        decided.add(key)
        if a["outcome"] in ("second-pass-right", "both-wrong", "undecidable"):
            fixes[key] = (a["adjudicated"], "full-" + a["outcome"])
    for r in rec:  # Lipi-prompted recheck: only cells no blind adjudication decided
        key = (r["cisi"], r["column"])
        if key in decided:
            continue
        if r["final"] != r["pass1"]:
            fixes[key] = (r["final"], "recheck-" + r["outcome"])
    changes = []
    outs = []
    for page in ("p435", "p436"):
        lines = []
        for line in (LOCAL / ("pass1-%s.txt" % page)).read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or not line.strip():
                lines.append(line.replace("pass 1", "final (pass 1 with adjudicated sample and recheck)", 1))
                continue
            cells = [c.strip() for c in line.split(" | ")]
            cisi = cells[0].split(" ")[0]
            for i, col in enumerate(COLS):
                if (cisi, col) in fixes:
                    new, why = fixes[(cisi, col)]
                    if new != cells[i]:
                        changes.append({"cisi": cisi, "column": col, "pass1": cells[i], "final": new, "reason": why})
                        cells[i] = new
            lines.append(" | ".join(cells))
        out = LOCAL / ("final-%s.txt" % page)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        outs.append(str(out))
    (LOCAL / "changes.json").write_text(json.dumps(changes, indent=1, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(HERE / "parse.py"), str(LOCAL / "final.jsonl")] + outs, check=True)
    print(len(changes), "cells changed")


if __name__ == "__main__":
    main()
