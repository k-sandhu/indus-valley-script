"""Extract the printed 225-row Dholavira context table, without sign strings.

The row table is local-only. Printed rows are not independently verified objects.
Coordinates use the 792 by 612 point landscape pages in the held preliminary PDF.
"""
from pathlib import Path
import collections
import hashlib
import json
import re

import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/inscriptions")
SOURCE = ROOT / "data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf"
COLUMNS = {"accession": (65, 117), "grid": (117, 202), "stratum": (202, 252), "depth_as_printed": (252, 343), "motif_as_printed": (455, 554), "inscription_as_printed": (554, 613), "area_as_printed": (613, 684), "stage_as_printed": (684, 741)}


def text_cell(words, xmin, xmax, ymin, ymax):
    selected = [w for w in words if xmin <= w[0] < xmax and ymin <= w[1] < ymax]
    return " ".join(w[4] for w in selected).strip()


def main():
    assert (ROOT / "data/raw").resolve() == Path("D:/projects/indus_valley_script/data/raw")
    document = fitz.open(SOURCE)
    records = []
    carry = None
    for page_number in range(264, 277):
        page = document[page_number - 1]
        words = page.get_text("words")
        serials = sorted((int(w[4][:-1]), w[1]) for w in words if 30 < w[0] < 58 and w[1] > 95 and re.fullmatch(r"\d+\.", w[4]))
        if carry is not None:
            end = serials[0][1] - 0.2 if serials else 550
            continuations = {}
            for column, (xmin, xmax) in COLUMNS.items():
                text = text_cell(words, xmin, xmax, 96, end)
                if text:
                    carry[column] = (carry[column] + " " + text).strip()
                    continuations[column] = text
            if continuations:
                carry["continuation"] = {"pdf_page": page_number, "fields": continuations}
        for k, (serial, y) in enumerate(serials):
            end = serials[k + 1][1] - 0.2 if k + 1 < len(serials) else 550
            record = {"table_serial": serial, "pdf_page": page_number, "printed_page": page_number - 17, "y_start": y, "y_end": end}
            record.update({column: text_cell(words, xmin, xmax, y - 0.2, end) for column, (xmin, xmax) in COLUMNS.items()})
            records.append(record)
        carry = records[-1]
    assert [r["table_serial"] for r in records] == list(range(1, 226))
    for record in records:
        record["field_missing_reasons"] = {}
        for column in COLUMNS:
            value = record[column]
            if not value:
                record["field_missing_reasons"][column] = "The printed cell is empty in the inspected table; no value inferred from neighbouring rows."
            elif value.strip() == "-":
                record["field_missing_reasons"][column] = "The printed cell contains a dash placeholder; the report supplies no usable value here."
            elif value.strip() == "?":
                record["field_missing_reasons"][column] = "The source explicitly leaves the field uncertain."
            elif value.strip() == "Missing":
                record["field_missing_reasons"][column] = "The catalogue explicitly records Missing; the missing attribute is not recoded as an ancient absence."
            elif column == "stage_as_printed" and ("?" in value or "Indeter" in value or value == "Unst"):
                record["field_missing_reasons"][column] = "The published stage is qualified or indeterminate; no single unqualified phase is assigned."
    accession_counts = collections.Counter(r["accession"] for r in records)
    duplicates = {a: [r["table_serial"] for r in records if r["accession"] == a] for a, n in accession_counts.items() if n > 1 and a}
    stage_counts = dict(collections.Counter(r["stage_as_printed"] or "[blank]" for r in records))
    area_counts = dict(collections.Counter(r["area_as_printed"] or "[blank]" for r in records))
    inscription_counts = dict(collections.Counter(r["inscription_as_printed"] or "[blank]" for r in records))
    payload = {"source_id": "BISHT2015-PRELIM", "method": "author coordinate extraction; exact raw labels; no sign strings", "rows": records}
    target = RAW / "dholavira-context-table-v1.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"population": "225 printed seal-context rows, including noninscribed, damaged and unidentified cases", "rows": len(records), "stage_raw_counts": stage_counts, "area_raw_counts": area_counts, "inscription_raw_counts": inscription_counts, "repeated_accession_strings": duplicates, "physical_objects_added": 0, "counts_are_independent_objects": False, "dating_basis": "published recovery-stage assertions; no manufacture-date or sample join added", "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "detailed_logical_path": "data/raw/2026-10-24-urban-form-and-inscription-ecology/inscriptions/dholavira-context-table-v1.json", "detailed_physical_path": str(target), "detailed_sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "author_validation": "serials 1..225 occur exactly once; labels and cross-page carry inspected separately"}
    (HERE / "context-table-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
