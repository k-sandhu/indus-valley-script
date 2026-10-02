"""Preserve original-source crops for post-comparison numerical adjudication.

No OCR, predicted code, rank sequence, or uniqueness constraint is used.
Historical reference JSON is left untouched.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import fitz

BASE = Path(__file__).resolve().parent
PDF = BASE.parent / "koskenniemi_parpola1979.pdf"
DOC = fitz.open(PDF)
CELLS = [
    (2, 1, [156, 81, 190, 111], 369, "high", [], 359),
    (4, 13, [260, 321, 294, 353], 360, "high", [], 350),
    (4, 21, [260, 481, 294, 514], 486, "medium", [465, 485], 486),
]
rows = []
for col, row, clip, code, confidence, alternatives, previous in CELLS:
    name = f"subsequent_pdf20_c{col}_r{row}_16x.png"
    out = BASE / name
    DOC[19].get_pixmap(matrix=fitz.Matrix(16, 16), clip=fitz.Rect(clip)).save(out)
    rows.append({
        "pdf_page_1based": 20, "column_0based": col, "row_0based": row,
        "previous_preferred_code": previous,
        "subsequent_preferred_code": code, "confidence": confidence,
        "alternatives": alternatives, "candidate_codes": sorted([code] + alternatives),
        "exact_source_clip_pdf_points": clip, "render_scale": 16,
        "source_crop": name, "crop_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "note": ("Literature prefers465. This annotator still favours486 but does not resolve open/broken numerical-font loops; preserve465/485/486 without uniqueness inference." if (col,row)==(4,21) else "Concurs with literature's subsequent original-source reading."),
    })
payload = {
    "purpose": "Subsequent original-source manual adjudication; not a fresh blind benchmark",
    "source_pdf": "research/corpus/primary/koskenniemi_parpola1979.pdf",
    "source_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
    "historical_gold_preserved": True,
    "historical_gold_sha256": hashlib.sha256((BASE / "manual_columns1_4.json").read_bytes()).hexdigest(),
    "selection": "Parent flagged duplicate numerical labels; literature supplied independent proposed readings. Reinspection is therefore post-comparison.",
    "method": "Original PDF enlarged images only. No uniqueness constraint or machine predictions used. No earlier font-pilot assignment changed.",
    "rows": rows,
    "created_utc": datetime.now(timezone.utc).isoformat(),
}
(BASE / "subsequent_adjudication.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"cells": len(rows), "historical_gold_preserved": True}))
