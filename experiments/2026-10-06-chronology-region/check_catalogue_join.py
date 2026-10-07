"""Reproduce the bounded CISI-base check; no third-party rows are exported."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent


def compute():
    path = ROOT / "data/normalized/lipi_observed_faces.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def base(value):
        match = re.fullmatch(r"([A-Za-z]+)-?(\d+)(?:[A-Za-z])?", str(value).strip())
        return f"{match[1].upper()}-{int(match[2])}" if match else None

    checks = [{"target": target, "matching_faces": sum(base(row.get("source_cisi")) == target for row in rows)}
              for target in ["H-1537", "H-1539"]]
    return {
        "status": "Verified computation",
        "question": "Do the two contextual cautions in Kenoyer and Meadow 2010 join this export by source_cisi base?",
        "source_location": {
            "title": "Inscribed Objects from Harappa Excavations 1986–2007",
            "authors": ["Jonathan Mark Kenoyer", "Richard H. Meadow"], "year": 2010,
            "printed_page": "xlvii", "pdf_page_one_based": 6,
            "url": "https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf"
        },
        "input_path": path.relative_to(ROOT).as_posix(),
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows_checked": len(rows), "field": "source_cisi",
        "normalization": r"Trim; fullmatch ([A-Za-z]+)-?(\d+)(?:[A-Za-z])?; uppercase prefix and integer base; strip final letter only. Same normalization as analyze.py.",
        "checks": checks,
        "limitation": "A failed exact-base join does not prove the objects are absent under another identifier or transcription."
    }


def owned_file(name):
    path = (OWN / name).resolve()
    if path.parent != OWN or path.suffix != ".json":
        raise ValueError("Use a JSON filename in the owned directory.")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--check", help="Compare with an existing owned JSON file; write nothing.")
    choice.add_argument("--output", default="source-join-check.json", help="Fresh owned JSON filename.")
    args = parser.parse_args()
    result = compute()
    if args.check:
        expected = json.loads(owned_file(args.check).read_text(encoding="utf-8"))
        if expected != result:
            raise AssertionError("The recorded join check differs from the current computation.")
        print(json.dumps({"check": "passed", "rows_checked": result["rows_checked"], "checks": result["checks"]}))
    else:
        output = owned_file(args.output)
        if output.exists():
            raise FileExistsError("Choose a fresh output filename.")
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result["checks"]))


if __name__ == "__main__":
    main()
