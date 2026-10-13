"""Check whether the CISI 2 FC number encodes the Mackay 1938 or Marshall 1931 catalogue number.

Reads the CISI 2 pilot's local final table and the Mackay/Marshall join table. Writes counts and
CISI numbers only (no transcribed CISI values) to the output JSON given as the first argument.
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(sys.argv) < 3 else Path(sys.argv[2])
FINAL = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot/final.jsonl"
JOIN = ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv"


def main(out):
    fc = {}
    for line in FINAL.open(encoding="utf-8"):
        row = json.loads(line)
        fc[row["cisi"]] = row["parsed"]["fc_number"]
    counts = collections.Counter()
    differ = []
    for row in csv.DictReader(JOIN.open(encoding="utf-8")):
        value = fc.get(row["cisi"])
        if value is None:
            continue
        source = row["source"]
        if "[" in value:
            counts[f"{source}|fc-uncertain"] += 1
            continue
        prefix, tail = value[0], value[1:].lstrip("0")
        catalogue = re.sub(r"[^0-9A-Za-z]", "", row["catalogue_no"]).lstrip("0")
        expected = {"marshall1931": "1", "mackay1938": "2"}[source]
        ok = prefix == expected and tail.lower() == catalogue.lower()
        counts[f"{source}|{'match' if ok else 'differ'}"] += 1
        if not ok:
            differ.append({"cisi": row["cisi"], "lipi_family_id": row["lipi_family_id"], "source": source,
                           "catalogue_no": row["catalogue_no"], "fc_prefix": prefix})
    result = {
        "rule": "FC number = 1000 + Marshall 1931 catalogue number, or 2000 + Mackay 1938 catalogue number",
        "inputs": {"cisi2_final": FINAL.relative_to(ROOT).as_posix(), "join_table": JOIN.relative_to(ROOT).as_posix()},
        "counts": dict(sorted(counts.items())),
        "differ": differ,
        "note": "The objects listed under differ belong to two pairs whose CISI 2 basic-data rows are crossed; measured on the CISI 2 plates, each seal fits the size of the excavator's row in Lipi's pairing (swap-check.md).",
    }
    Path(out).write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
