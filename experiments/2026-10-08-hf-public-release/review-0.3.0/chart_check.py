"""Check release/data/chart_reference.parquet against package P's chart-reference-v2.1.json and the 0.2.0 table.

Usage (repository root): python -B experiments/2026-10-08-hf-public-release/review-0.3.0/chart_check.py
Writes review-0.3.0/chart-check.json.
"""
import hashlib, json
from collections import Counter
from pathlib import Path
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
P = ROOT / "experiments/2026-10-08-chart-reference-audit"
v21 = json.loads((P / "chart-reference-v2.1.json").read_text(encoding="utf-8-sig"))
new = pq.read_table(PKG / "release/data/chart_reference.parquet").to_pylist()
old = pq.read_table(PKG / "history/2026-10-08-release-v0.2.0/data/chart_reference.parquet").drop(["image"] if "image" in pq.read_schema(PKG / "history/2026-10-08-release-v0.2.0/data/chart_reference.parquet").names else []).to_pylist()

key = lambda r: (r["pdf_page"], r["column"], r["row"])
P_rows = {key(r): r for r in v21["rows"]}
N = {key(r): r for r in new}
O = {key(r): r for r in old}
out = {"p_rows": len(P_rows), "table_rows": len(N), "old_rows": len(O), "same_key_set": set(P_rows) == set(N) == set(O)}

# 1. every code, class, alternatives, confidence, dashed flag vs P v2.1
FIELDS = [("code", "code"), ("rank", "rank"), ("alternatives", "alternatives"), ("rank_alternatives", "rank_alternatives"),
          ("numeric_confidence", "numeric_confidence"), ("dashed_auxiliary", "dashed_auxiliary")]
mism = []
for k, pr in P_rows.items():
    n = N[k]
    for pf, nf in FIELDS:
        a, b = pr.get(pf), n.get(nf)
        if pf in ("alternatives", "rank_alternatives"):
            a, b = list(a or []), list(b or [])
        if a != b:
            mism.append({"cell": k, "field": pf, "p": a, "table": b})
out["p_vs_table_mismatches"] = mism[:30]
out["p_vs_table_mismatch_count"] = len(mism)
out["cell_id_pattern_ok"] = all(n["cell_id"] == f"p{k[0]}_c{k[1]}_r{k[2]}" for k, n in N.items())

# 2. previous-value columns and change notes against the 0.2.0 table and the P change_log
def first_old(row):
    d = {}
    for e in row.get("change_log", []):
        for f, v in e["fields"].items():
            d.setdefault(f, v["old"])
    return d
exp_changed = {k: first_old(r) for k, r in P_rows.items() if "change_log" in r}
out["P_change_log_cells"] = len(exp_changed)
col_map = {"code": "previous_code", "rank": "previous_rank", "alternatives": "previous_alternatives",
           "rank_alternatives": "previous_rank_alternatives", "numeric_confidence": "previous_numeric_confidence"}
diff_vs_old = {}   # fields whose value differs between 0.2.0 table and 0.3.0 table
for k in N:
    d = {}
    for f in col_map:
        a, b = O[k].get(f), N[k].get(f)
        if f in ("alternatives", "rank_alternatives"):
            a, b = list(a or []), list(b or [])
        if a != b:
            d[f] = a
    if d:
        diff_vs_old[k] = d
out["cells_differing_from_0.2.0_table"] = len(diff_vs_old)
out["diff_cells_equal_change_log_cells"] = set(diff_vs_old) == set(exp_changed)
out["cells_changed_fields_counter"] = Counter(f for d in diff_vs_old.values() for f in d)
prev_bad, cf_bad, note_bad = [], [], []
for k, n in N.items():
    d = diff_vs_old.get(k, {})
    for f, pc in col_map.items():
        v = n[pc]
        if f in d:
            exp = d[f]
            if f in ("alternatives", "rank_alternatives"):
                exp = list(exp or [])
                v = list(v or [])
            if v != exp:
                prev_bad.append((k, f, v, exp))
        else:
            if v is not None:
                prev_bad.append((k, f, "unexpected previous value", v))
    if sorted(n["changed_fields"] or []) != sorted(d):
        cf_bad.append((k, n["changed_fields"], sorted(d)))
    if bool(d) != bool(n["change_note"]):
        note_bad.append((k, n["change_note"]))
out["previous_value_errors"] = prev_bad[:20]
out["changed_fields_errors"] = cf_bad[:20]
out["change_note_presence_errors"] = note_bad[:20]
out["change_log_first_old_equals_0.2.0"] = all(
    all(({"alternatives": list(O[k][f] or [])} if f in ("alternatives", "rank_alternatives") else {f: O[k][f]}).get(f, O[k][f]) == (list(v or []) if f in ("alternatives", "rank_alternatives") else v)
        for f, v in fo.items()) for k, fo in exp_changed.items())
# change notes text for each changed cell
out["change_notes"] = {f"p{k[0]}_c{k[1]}_r{k[2]}": N[k]["change_note"] for k in sorted(diff_vs_old)}
out["change_note_matches_values"] = {}
for k, d in diff_vs_old.items():
    n = N[k]; note = n["change_note"]
    good = True
    for f, o in d.items():
        new_v = n[f]
        if str(o) not in note.replace("[", "[").replace("]", "]") and not (f in ("alternatives", "rank_alternatives")):
            good = False
        if f not in ("alternatives", "rank_alternatives") and str(new_v) not in note:
            good = False
    out["change_note_matches_values"][f"p{k[0]}_c{k[1]}_r{k[2]}"] = good
out["change_notes_all_mention_old_and_new"] = all(out["change_note_matches_values"].values())

# 3. counts quoted in the card
code_changes = [k for k, d in diff_vs_old.items() if "code" in d]
rank_changes = [k for k, d in diff_vs_old.items() if "rank" in d]
alt_changes = [k for k, d in diff_vs_old.items() if "alternatives" in d or "rank_alternatives" in d]
out["code_changes"] = [(f"p{k[0]}_c{k[1]}_r{k[2]}", diff_vs_old[k]["code"], N[k]["code"]) for k in code_changes]
out["rank_changes"] = [(f"p{k[0]}_c{k[1]}_r{k[2]}", diff_vs_old[k]["rank"], N[k]["rank"]) for k in rank_changes]
out["alternatives_changes"] = len(alt_changes)
out["confidence_counts_table"] = Counter(n["numeric_confidence"] for n in new)
out["confidence_counts_P"] = Counter(r["numeric_confidence"] for r in v21["rows"])
out["old_nonempty_alternatives"] = sum(1 for o in old if o["alternatives"])
out["new_nonempty_alternatives"] = sum(1 for n in new if n["alternatives"])
out["new_nonempty_rank_alternatives"] = sum(1 for n in new if n["rank_alternatives"])
out["status_values"] = Counter(n["status"] for n in new)
out["reference_version_values"] = Counter(n["reference_version"] for n in new)

# 4. images unchanged: embedded bytes equal the original atlas crops (output/chart_atlas/cells)
def sha(b): return hashlib.sha256(b).hexdigest()
tbl = pq.read_table(PKG / "release/data/chart_reference.parquet", columns=["cell_id", "image", "image_path"]).to_pylist()
atlas = ROOT / "output/chart_atlas/cells"
img_bad = []
for r in tbl:
    f = atlas / (r["cell_id"] + ".png")
    if not f.exists() or sha(f.read_bytes()) != sha(r["image"]["bytes"]):
        img_bad.append(r["cell_id"])
out["images_checked"] = len(tbl)
out["images_not_equal_to_atlas_crop"] = img_bad[:10]
out["images_not_equal_count"] = len(img_bad)
out["atlas_crop_files"] = len(list(atlas.glob("*.png")))
Path(__file__).with_name("chart-check.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
for k, v in out.items():
    if k not in ("change_notes", "change_note_matches_values"):
        print(k, "=", json.dumps(v, default=str)[:700])
