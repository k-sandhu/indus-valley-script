"""Reviewer check: FIELD-DEFINITIONS.md against the actual Parquet schemas, and card configuration table against actual rows.
Run from the repository root:  python -B experiments/2026-10-08-hf-public-release/review/field_definitions_check.py
"""
import json
import re
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
text = (REL / "FIELD-DEFINITIONS.md").read_text(encoding="utf-8")
sections = re.split(r"^## ", text, flags=re.M)[1:]
doc = {}
for s in sections:
    name, _, body = s.partition("\n")
    name = name.strip()
    rows = {}
    for m in re.finditer(r"^\| `([^`]+)` \| `([^`]+)` \| (.*?) \|$", body, re.M):
        rows[m.group(1)] = (m.group(2).replace("item:", "element:"), m.group(3))
    if rows:
        doc[name] = rows
out = {"tables_documented": len(doc), "problems": []}
for pf in sorted((REL / "data").glob("*.parquet")):
    n = pf.stem
    schema = {f.name: str(f.type) for f in pq.read_schema(pf)}
    if n not in doc:
        out["problems"].append(f"{n}: no field table")
        continue
    d = doc[n]
    for k, t in schema.items():
        if k not in d:
            out["problems"].append(f"{n}.{k}: not documented")
        elif d[k][0] != t:
            out["problems"].append(f"{n}.{k}: documented type {d[k][0]} vs schema {t}")
    for k in d:
        if k not in schema:
            out["problems"].append(f"{n}.{k}: documented but not in schema")
# generic definitions reused across tables: record those whose text names another table
cross = []
for n, rows in doc.items():
    for k, (t, definition) in rows.items():
        if n == "benchmark_rows_v2" and "Null for v1" in definition:
            cross.append(f"{n}.{k}: shared definition mentions v1")
        if n in ("benchmark_count_pages", "weight_chance_controls") and k == "frame":
            cross.append(f"{n}.{k}: one definition covering two tables")
out["shared_definition_notes"] = cross
(REL.parent / "review/field-definitions-check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
