"""Compare the chart_correction_flags_json column of benchmark_readings (v1, v2) and benchmark_readings_v3 with package P's
impact-v2.1.json `public_readings` records, group by group (benchmark, reader, kind), and check the v3 readings independently from
the readings' own chart_locations / shape_only_chart_locations.
Writes review-0.3.0/readings-flag-check.json.
"""
import collections
import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
R = PKG / "release/data/"
imp = json.loads((ROOT / "experiments/2026-10-08-chart-reference-audit/impact-v2.1.json").read_text(encoding="utf-8-sig"))
v21 = json.loads((ROOT / "experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json").read_text(encoding="utf-8-sig"))
old = {(r["pdf_page"], r["column"], r["row"]): r for r in pq.read_table(PKG / "history/2026-10-08-release-v0.2.0/data/chart_reference.parquet",
       columns=["pdf_page", "column", "row", "code", "rank", "alternatives", "rank_alternatives", "numeric_confidence"]).to_pylist()}
changed = set()
for r in v21["rows"]:
    o = old[(r["pdf_page"], r["column"], r["row"])]
    if any((list(o[f] or []) != list(r[f] or [])) if "alt" in f else o[f] != r[f] for f in ("code", "rank", "alternatives", "rank_alternatives", "numeric_confidence")):
        changed.add("p%d_c%d_r%d" % (r["pdf_page"], r["column"], r["row"]))


def cells_of(unit):
    out = set()
    for field in ("chart_locations", "chart_references", "shape_only_chart_locations"):
        v = unit.get(field) or []
        vals = [x for z in v.values() for x in (z if isinstance(z, list) else [z])] if isinstance(v, dict) else v
        for x in vals:
            if isinstance(x, dict):
                out.add("p%d_c%d_r%d" % (x["pdf_page"], x["column"], x["row"]))
            elif isinstance(x, str) and len(x.split(":")) == 3:
                out.add("p%s_c%s_r%s" % tuple(x.split(":")))
    return out


agg = collections.defaultdict(collections.Counter)
for r in pq.read_table(R / "benchmark_readings.parquet").to_pylist():
    fl = json.loads(r["chart_correction_flags_json"])
    k = (r["benchmark"], r["reader"], r["kind"])
    a = agg[k]
    a["rows"] += 1
    a["units"] += len(fl)
    a["corrected_cell_units"] += sum(1 for f in fl if f["cells"])
    a["direct_candidate_change_units"] += sum(1 for f in fl if f["candidate_fields_would_change"])
    a["identity_review_units"] += sum(1 for f in fl if f["candidate_identity_review"])
    a["class_metadata_units"] += sum(1 for f in fl if any("rank" in x for x in f["changed_fields"].values()))
groups = []
for e in imp["public_readings"]:
    k = (e["benchmark"], e["reader"], e["kind"])
    s, a = e["summary"], agg[k]
    pairs = dict(corrected_cell_units=("affected_chart_location_units", a["corrected_cell_units"]),
                 direct_candidate_change_units=("definite_changed_units", a["direct_candidate_change_units"]),
                 identity_review_units=("potential_units_needing_identity_review", a["identity_review_units"]),
                 class_metadata_units=("class_metadata_units", a["class_metadata_units"]))
    diffs = {n: {"impact": s[f], "release": v} for n, (f, v) in pairs.items() if s[f] != v}
    groups.append({"group": "/".join(k), "units_impact": s["units"], "units_release": a["units"], "differences": diffs})
out = {"groups": groups,
       "groups_with_differences": [g["group"] for g in groups if g["differences"]],
       "impact_definite_reading_units": sum(g["differences"].get("direct_candidate_change_units", {}).get("impact", 0) for g in groups),
       "release_direct_candidate_change_units_all_reading_groups": sum(a["direct_candidate_change_units"] for a in agg.values())}

# v3 readings, independent derivation from the reading's own location fields
bad, n, flagged = [], 0, 0
rows3 = {r["sample_index"]: r for r in pq.read_table(R / "benchmark_rows_v3.parquet", columns=["sample_index", "reference_chart_correction_flags_json"]).to_pylist()}
eq_adj = tot_adj = 0
for i, r in enumerate(pq.read_table(R / "benchmark_readings_v3.parquet").to_pylist()):
    rd = json.loads(r["reading_json"])
    fl = json.loads(r["chart_correction_flags_json"])
    if len(fl) != len(rd.get("units", [])):
        bad.append((i, "length"))
        continue
    for u, f in zip(rd.get("units", []), fl):
        n += 1
        c = cells_of(u) & changed
        flagged += bool(f["cells"])
        if set(f["cells"]) != c:
            bad.append((i, f["unit_index"]))
    if r["kind"] == "adjudicated":
        tot_adj += 1
        eq_adj += fl == json.loads(rows3[r["sample_index"]]["reference_chart_correction_flags_json"])
out["v3_readings"] = {"units": n, "corrected_cell_units": flagged, "independent_mismatches": bad[:10],
                      "adjudicated_flags_equal_row_reference_flags": f"{eq_adj}/{tot_adj}",
                      "direct_candidate_change_units_in_independent_readings": sum(
                          1 for r in pq.read_table(R / "benchmark_readings_v3.parquet").to_pylist() if r["kind"] != "adjudicated"
                          for f in json.loads(r["chart_correction_flags_json"]) if f["candidate_fields_would_change"])}
Path(__file__).with_name("readings-flag-check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
