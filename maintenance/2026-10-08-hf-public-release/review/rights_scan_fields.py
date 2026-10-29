"""Reviewer scan: which staged museum-join and census cells equal field values of the Lipi export?

Compares string cells in release/data/*.parquet with Lipi metadata values for identifier-type keys (cisi, excavation-idno, and
the Lipi source_cisi) and Mayig descriptions. Reports counts per table and column, never the Lipi record content itself.
Run from the repository root:
  python -B experiments/2026-10-08-hf-public-release/review/rights_scan_fields.py
"""
import collections
import json
import re
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
REL = PKG / "release"
NORM = ROOT / "data/normalized"

lipi = collections.defaultdict(set)
for fn in ("lipi_observed_faces.jsonl",):
    for line in (NORM / fn).open(encoding="utf-8"):
        r = json.loads(line)
        md = r.get("metadata", {})
        for key in ("cisi", "excavation-idno"):
            v = (md.get(key) or "").strip()
            if v and v not in ("-", "--"):
                lipi[key].add(v)
        v = (r.get("source_cisi") or "").strip()
        if v and v not in ("-", "--"):
            lipi["source_cisi"].add(v)
print({k: len(v) for k, v in lipi.items()})
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
lipi_norm = {k: {norm(x) for x in v} for k, v in lipi.items()}
mayig_desc = set()
for line in (NORM / "mayig_faces.jsonl").open(encoding="utf-8"):
    d = (json.loads(line).get("description") or "").strip()
    if len(d) >= 8:
        mayig_desc.add(d.lower())

out = collections.OrderedDict()
for pf in sorted((REL / "data").glob("*.parquet")):
    t = pq.read_table(pf).to_pylist()
    for col in (t[0].keys() if t else []):
        vals = [r[col] for r in t if isinstance(r[col], str)]
        hits = collections.Counter()
        for v in vals:
            n = norm(v)
            if len(n) < 3 or not re.search(r"\d", v):
                continue
            for key in lipi_norm:
                if n in lipi_norm[key]:
                    hits[key] += 1
            # tokens of composite identifiers
            for tok in re.split(r"[;/,]| / ", v):
                nt = norm(tok)
                if len(nt) >= 4 and re.search(r"\d", tok):
                    for key in ("excavation-idno",):
                        if nt in lipi_norm[key]:
                            hits[key + ":token"] += 1
        desc = sum(1 for v in vals if v.lower() in mayig_desc)
        if hits or desc:
            out[f"{pf.stem}.{col}"] = dict(cells=len(vals), lipi_equal_cells=dict(hits), mayig_description_equal=desc)
(PKG / "review/rights-scan-fields.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))

# museum joins: relation between join rows and Lipi identifiers
t = pq.read_table(REL / "data/evidence_museum_joins.parquet").to_pylist()
cisi_in = sum(1 for r in t if norm(r["cisi"]) in lipi_norm["source_cisi"] or norm(r["cisi"]) in lipi_norm["cisi"])
cisi_dash = sum(1 for r in t if r["cisi"] in ("-", ""))
print("museum_joins rows", len(t), "cisi equal to a Lipi cisi value", cisi_in, "cisi '-' placeholder", cisi_dash)
