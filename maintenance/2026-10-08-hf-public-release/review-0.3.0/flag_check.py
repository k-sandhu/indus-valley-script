"""Check the per-unit chart-correction flags in benchmark_rows_v1/v2/v3 against package P's impact-v2.1.json.

Reference flags: compared with M_references[v] (unit_changes, potential_mappings, affected_chart_locations,
class_metadata_locations) and M_v3_reported_location_conflicts. Prediction flags: recomputed independently by joining
every alternative's template_key to the changed cells of chart-reference-v2.1.json, and compared with the stored flags;
for v1 and v2 the totals are also compared with impact-v2.1.json public_predictions.
Also checks that reference_json and prediction_json are identical to the 0.2.0 table (v1, v2) and to package M's
frozen files (v3), so the flags are additions and the frozen payloads keep their card-label vocabulary.
Writes review-0.3.0/flag-check.json.
"""
import json
from collections import defaultdict
from pathlib import Path
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
P = ROOT / "experiments/2026-10-08-chart-reference-audit"
M = ROOT / "experiments/2026-10-07-helsinki1979-digitization"
impact = json.loads((P / "impact-v2.1.json").read_text(encoding="utf-8-sig"))
v21 = json.loads((P / "chart-reference-v2.1.json").read_text(encoding="utf-8-sig"))


def cid(r):
    return "p%s_c%s_r%s" % (r["pdf_page"], r["column"], r["row"])


# net changed fields: P v2.1 row against the 0.2.0 table (a cell edited and then edited back is not a net change)
old_tbl = {(r["pdf_page"], r["column"], r["row"]): r for r in pq.read_table(PKG / "history/2026-10-08-release-v0.2.0/data/chart_reference.parquet", columns=["pdf_page", "column", "row", "rank", "code", "alternatives", "rank_alternatives", "numeric_confidence"]).to_pylist()}
changed = {}
for r in v21["rows"]:
    o = old_tbl[(r["pdf_page"], r["column"], r["row"])]
    fs = set()
    for f in ("rank", "code", "alternatives", "rank_alternatives", "numeric_confidence"):
        a_, b_ = o[f], r[f]
        if f in ("alternatives", "rank_alternatives"):
            a_, b_ = list(a_ or []), list(b_ or [])
        if a_ != b_:
            fs.add(f)
    if fs:
        changed[cid(r)] = fs
assert len(changed) == 36, len(changed)


def tk2cell(tk):
    return "p%s_c%s_r%s" % tuple(tk.split(":"))


def read_rows(v):
    cols = [f.name for f in pq.read_schema(PKG / ("release/data/benchmark_rows_%s.parquet" % v))]
    keep = [c for c in cols if c not in ("context_image", "exact_image")]
    return pq.read_table(PKG / ("release/data/benchmark_rows_%s.parquet" % v), columns=keep).to_pylist()


out = {}
for v in ("v1", "v2", "v3"):
    rows = read_rows(v)
    rec = {"rows": len(rows)}
    flags = {}
    for r in rows:
        for f in json.loads(r["reference_chart_correction_flags_json"]):
            flags[(r["sample_index"], f["unit_index"])] = f
    ref_units = {(r["sample_index"], i) for r in rows for i, u in enumerate(json.loads(r["reference_json"])["units"])}
    rec["reference_units"] = len(ref_units)
    rec["flag_units"] = len(flags)
    rec["flag_units_equal_reference_units"] = set(flags) == ref_units
    mr = impact["M_references"][v]
    exp_dir = defaultdict(set)
    for c in mr["unit_changes"]:
        exp_dir[(c["sample_index"], c["unit_index"])].add(c["field"])
    got_dir = {k: set(f["candidate_fields_would_change"]) for k, f in flags.items() if f["candidate_fields_would_change"]}
    rec["direct_units_expected"] = len(exp_dir)
    rec["direct_units_stored"] = len(got_dir)
    rec["direct_units_equal"] = dict(exp_dir) == got_dir
    rec["direct_unit_diffs"] = [str(k) for k in set(exp_dir) ^ set(got_dir)][:10]
    exp_pot = defaultdict(dict)
    for c in mr["potential_mappings"]:
        exp_pot[(c["sample_index"], c["unit_index"])].setdefault(c["field"], {})[c["old_code"]] = c["possible_cell_mappings"]
    got_pot = {k for k, f in flags.items() if f["candidate_identity_review"]}
    rec["identity_review_units_expected"] = len(exp_pot)
    rec["identity_review_units_stored"] = len(got_pot)
    rec["identity_review_units_equal"] = set(exp_pot) == got_pot
    pm_bad = 0
    for k, f in flags.items():
        pm = f["potential_mappings"]
        if bool(pm) != (k in exp_pot):
            pm_bad += 1
        elif pm:
            n_exp = sum(len(x) for x in exp_pot[k].values())
            if len(pm) != n_exp:
                pm_bad += 1
    rec["potential_mapping_payload_mismatches"] = pm_bad
    exp_cells = {(c["sample_index"], c["unit_index"]): set(c["cells"]) for c in mr["affected_chart_locations"]}
    got_cells = {k: set(f["cells"]) for k, f in flags.items() if f["cells"]}
    rec["corrected_cell_units_expected"] = len(exp_cells)
    rec["corrected_cell_units_stored"] = len(got_cells)
    rec["corrected_cell_units_equal"] = exp_cells == got_cells
    rec["corrected_cell_flag_matches_cells"] = all(f["corrected_cell"] == bool(f["cells"]) for f in flags.values())
    cf_bad = [(str(k), c) for k, f in flags.items() for c, fs in f["changed_fields"].items() if set(fs) != changed.get(c, None)]
    rec["changed_fields_mismatches"] = cf_bad[:10]
    exp_cls = {(c["sample_index"], c["unit_index"]) for c in mr["class_metadata_locations"]}
    got_cls = {k for k, f in flags.items() if any("rank" in fs for fs in f["changed_fields"].values())}
    rec["class_metadata_units_expected"] = len(exp_cls)
    rec["class_metadata_units_from_flags"] = len(got_cls)
    rec["class_metadata_units_equal"] = exp_cls == got_cls
    exp_conf = {(c["sample_index"], c["unit_index"]) for c in impact["M_v3_reported_location_conflicts"]} if v == "v3" else set()
    got_conf = {k for k, f in flags.items() if f["locator_conflict"]}
    rec["locator_conflicts_expected"] = sorted(exp_conf)
    rec["locator_conflicts_stored"] = sorted(got_conf)
    rec["locator_conflicts_equal"] = exp_conf == got_conf

    pred_bad, ch_alt, ch_units, ch_rows, top1_units = [], 0, set(), set(), set()
    for r in rows:
        pj = json.loads(r["prediction_json"])
        pf = {f["unit_index"]: f for f in json.loads(r["prediction_chart_correction_flags_json"])}
        units = pj["units"]
        if set(pf) != set(range(len(units))):
            pred_bad.append((r["sample_index"], "unit set"))
        for ui, u in enumerate(units):
            exp = []
            for ai, a in enumerate(u["alternatives"]):
                c = tk2cell(a["template_key"])
                if c in changed:
                    exp.append({"alternative_index": ai, "cell": c, "changed_fields": sorted(changed[c])})
                    ch_alt += 1
                    if ai == 0:
                        top1_units.add((r["sample_index"], ui))
            got = pf.get(ui, {})
            got_alts = [{"alternative_index": x["alternative_index"], "cell": x["cell"], "changed_fields": sorted(x["changed_fields"])} for x in got.get("alternatives", [])]
            if sorted(exp, key=lambda x: x["alternative_index"]) != sorted(got_alts, key=lambda x: x["alternative_index"]) or got.get("corrected_cell") != bool(exp):
                pred_bad.append((r["sample_index"], ui))
            if exp:
                ch_units.add((r["sample_index"], ui))
                ch_rows.add(r["sample_index"])
    rec["prediction_flag_mismatches"] = pred_bad[:10]
    rec["prediction_changed_alternatives"] = ch_alt
    rec["prediction_changed_units"] = len(ch_units)
    rec["prediction_changed_rows"] = len(ch_rows)
    rec["prediction_top1_changed_units"] = len(top1_units)
    code_aff = rank_only = conf_only = 0
    for r in rows:
        for f in json.loads(r["prediction_chart_correction_flags_json"]):
            for a in f["alternatives"]:
                fs = set(a["changed_fields"])
                if fs & {"code", "alternatives"}:
                    code_aff += 1
                elif "rank" in fs:
                    rank_only += 1
                else:
                    conf_only += 1
    rec["flagged_alternatives_code_affecting"] = code_aff
    rec["flagged_alternatives_rank_only"] = rank_only
    rec["flagged_alternatives_confidence_only"] = conf_only
    if v in impact["public_predictions"]:
        s = impact["public_predictions"][v]["summary"]
        rec["impact_public_predictions"] = {k: s[k] for k in ("changed_rows", "changed_units", "changed_alternatives", "top1_changed_units")}
        by = {}
        for a in impact["public_predictions"][v]["alternative_changes"]:
            key = "codes" if "codes" in a["fields"] else "ranks"
            by[key] = by.get(key, 0) + 1
        rec["impact_alternative_changes_by_field"] = by
        rec["impact_codes_equals_code_affecting"] = by.get("codes") == code_aff
        rec["impact_ranks_equals_rank_only"] = by.get("ranks") == rank_only
    out[v] = rec


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


pres = {}
for v in ("v1", "v2"):
    cols = ["sample_index", "reference_json", "prediction_json", "locator_json"]
    new = {r["sample_index"]: r for r in pq.read_table(PKG / ("release/data/benchmark_rows_%s.parquet" % v), columns=cols).to_pylist()}
    old = {r["sample_index"]: r for r in pq.read_table(PKG / ("history/2026-10-08-release-v0.2.0/data/benchmark_rows_%s.parquet" % v), columns=cols).to_pylist()}
    pres[v] = {f: sum(1 for k in new if new[k][f] == old[k][f]) for f in ("reference_json", "prediction_json", "locator_json")}
    pres[v]["rows"] = len(new)
new3 = {r["sample_index"]: r for r in pq.read_table(PKG / "release/data/benchmark_rows_v3.parquet", columns=["sample_index", "reference_json", "prediction_json"]).to_pylist()}
v3dir = M / "repair/2026-10-08-v3"
adj = read(v3dir / "blind/adjudicated-reference.json")
pred = read(v3dir / "predictions.json")
adj_rows = adj["rows"] if isinstance(adj, dict) and "rows" in adj else adj
pred_rows = pred["rows"] if isinstance(pred, dict) and "rows" in pred else pred
pres["v3"] = {"rows": len(new3),
              "reference_json_equal_M": sum(json.loads(new3[r["sample_index"]]["reference_json"]) == r for r in adj_rows),
              "prediction_json_equal_M": sum(json.loads(new3[r["sample_index"]]["prediction_json"]) == r for r in pred_rows),
              "M_reference_rows": len(adj_rows), "M_prediction_rows": len(pred_rows)}
out["payload_preservation"] = pres
Path(__file__).with_name("flag-check.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(json.dumps(out, indent=1, default=str))
