"""Record hashes of the protocol, coding table and inputs before outcomes are computed.

Usage: python -X utf8 preserve_start.py <output.json>
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "experiments/2026-10-12-structure-first/PROTOCOL.md",
    "experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv",
    "knowledge/directions/structure-first-2026-10-12.md",
    "data/normalized/lipi_clean_rtl_singleline.jsonl",
    "data/normalized/lipi_observed_faces.jsonl",
    "data/normalized/lipi_observed_parts.jsonl",
    "data/normalized/mayig_sign_schema.json",
    "data/normalized/mayig_wells_class_crosswalk.json",
    "research/literature/copper_constraints.csv",
    "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl",
    "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/manifest.json",
    "knowledge/experiments/registry.json",
]


def main():
    out = Path(sys.argv[1])
    rows = []
    for f in FILES:
        p = ROOT / f
        rows.append({"path": f, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    rec = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "note": "Recorded after PROTOCOL.md and the first-coder table were written and before any step outcome.",
           "files": rows}
    out.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(out, len(rows))


if __name__ == "__main__":
    main()
