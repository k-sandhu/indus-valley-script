"""Compare the v3 configurations (rows, readings, count pages, count readings, chart cards) and every image with package M's
frozen v3 files in experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-08-v3/.

Run from the repository root with the indus-ml Python: python -B experiments/2026-10-08-hf-public-release/review-0.3.0/v3_content_check.py
Writes review-0.3.0/v3-content-check.json.
"""
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
D = PKG / "release/data"
V3 = ROOT / "experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-08-v3"
B = V3 / "blind"


def L(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


out = {}
sel = {r["sample_index"]: r for r in L(B / "selection.json")["rows"]}
rows = pq.read_table(D / "benchmark_rows_v3.parquet").to_pylist()
out["rows"] = len(rows)
out["sample_indices_0_79"] = sorted(r["sample_index"] for r in rows) == list(range(80))
img_ctx_bad, img_ex_bad, path_bad, loc_bad, sec_bad = [], [], [], [], []
for r in rows:
    s = sel[r["sample_index"]]
    ctx = (B / s["source_crop"]).read_bytes()
    ex = (B / s["exact_crop"]).read_bytes()
    if r["context_image"]["bytes"] != ctx:
        img_ctx_bad.append(r["sample_index"])
    if r["exact_image"]["bytes"] != ex:
        img_ex_bad.append(r["sample_index"])
    if r["context_image_path"] != "images/v3/" + s["source_crop"] or r["exact_image_path"] != "images/v3/" + s["exact_crop"]:
        path_bad.append(r["sample_index"])
    loc = json.loads(r["locator_json"])
    for k in ("context_pdf_box", "source_crop_sha256", "exact_crop_sha256", "pdf_column", "pdf_page", "section"):
        want = s["pdf_column"] if k == "pdf_column" else s[k] if k in s else None
        if want is not None and loc.get(k) != want:
            loc_bad.append((r["sample_index"], k))
    if r["section"] != s["section"] or r["pdf_page"] != s["pdf_page"]:
        sec_bad.append(r["sample_index"])
    if sha(ctx) != s["source_crop_sha256"] or sha(ex) != s["exact_crop_sha256"]:
        loc_bad.append((r["sample_index"], "M crop hash vs selection"))
out["context_image_bytes_not_equal_M"] = img_ctx_bad
out["exact_image_bytes_not_equal_M"] = img_ex_bad
out["image_path_columns_not_equal_expected"] = path_bad
out["locator_mismatches"] = loc_bad[:10]
out["section_or_page_mismatches"] = sec_bad
out["sections"] = {k: sum(1 for r in rows if r["section"] == k) for k in ("number_order", "end_sorted", "beginning_sorted")}
out["status_values"] = sorted({r["status"] for r in rows})
out["reference_kind_values"] = sorted({r["reference_kind"] for r in rows})

# readings
rd = pq.read_table(D / "benchmark_readings_v3.parquet").to_pylist()
a_rows = {r["sample_index"]: r for p in ("rows-part1.json", "rows-part2.json") for r in L(B / "reader-a" / p)["rows"]}
b_files = sorted((B / "reader-b").glob("*.json"))
b_rows = {}
for f in b_files:
    j = L(f)
    if isinstance(j, dict) and "rows" in j:
        for r in j["rows"]:
            b_rows[r["sample_index"]] = r
adj = {r["sample_index"]: r for r in L(B / "adjudicated-reference.json")["rows"]}
out["M_reader_a_rows"], out["M_reader_b_rows"], out["M_adjudicated_rows"] = len(a_rows), len(b_rows), len(adj)
out["M_reader_b_files"] = [f.name for f in b_files]
cmp = {"A": (a_rows, 0), "B": (b_rows, 0), "C": (adj, 0)}
bad = {"A": 0, "B": 0, "C": 0}
cnt = {"A": 0, "B": 0, "C": 0}
for r in rd:
    src = cmp[r["reader"]][0]
    cnt[r["reader"]] += 1
    if json.loads(r["reading_json"]) != src.get(r["sample_index"]):
        bad[r["reader"]] += 1
out["readings_rows"] = len(rd)
out["readings_by_reader"] = cnt
out["readings_not_equal_M"] = bad
out["readings_kind"] = {r["reader"]: r["kind"] for r in rd}

# count pages
cp = pq.read_table(D / "benchmark_count_pages_v3.parquet").to_pylist()
det = {p["pdf_page"]: p for p in L(V3 / "count-page-detections.json")["pages"]}
adjc = {p["pdf_page"]: p for p in L(B / "adjudicated-counts.json")["pages"]}
stored_keys = set()
cp_bad = {"image": [], "reference": [], "detections": [], "frame": []}
sel_all = L(B / "selection.json")
rand = set(sel_all["random_count_pages"]) if isinstance(sel_all["random_count_pages"], list) else set()
stress = set(sel_all["stress_pages"]) if isinstance(sel_all["stress_pages"], list) else set()
out["M_random_pages"], out["M_stress_pages"] = len(rand), len(stress)
for r in cp:
    pg = r["pdf_page"]
    f = B / "page-count-source" / f"pdf{pg}.png"
    # the table stores loose PNGs: compare the loose file in release/images/counts
    loose = PKG / "release" / r["image_paths"][0]
    if not loose.exists() or loose.read_bytes() != f.read_bytes():
        cp_bad["image"].append(pg)
    if json.loads(r["reference_json"]) != adjc.get(pg):
        cp_bad["reference"].append(pg)
    stored = json.loads(r["detections_json"])
    m_rows = det[pg]["rows"]
    # the stored detections keep a subset of M's fields (box geometry, line kind, anchor); compare those fields entry by entry
    if len(stored) != len(m_rows) or any(any(m_rows[i].get(k) != v for k, v in e.items()) for i, e in enumerate(stored)):
        cp_bad["detections"].append(pg)
    stored_keys.update(k for e in stored for k in e)
    want = "random" if pg in rand else "stress" if pg in stress else "?"
    if r["frame"] != want:
        cp_bad["frame"].append(pg)
out["count_pages"] = len(cp)
out["stored_detection_keys"] = sorted(stored_keys)
out["count_pages_mismatches"] = cp_bad
out["count_pages_set_equal_M"] = {r["pdf_page"] for r in cp} == set(adjc) == set(det)

# count readings
cr = pq.read_table(D / "benchmark_count_readings_v3.parquet").to_pylist()
ca = {p["pdf_page"]: p for p in L(B / "reader-a/counts.json")["pages"]}
cb = {p["pdf_page"]: p for p in L(B / "reader-b/counts.json")["pages"]}
cr_bad = [(r["reader"], r["pdf_page"]) for r in cr if json.loads(r["reading_json"]) != (ca if r["reader"] == "A" else cb).get(r["pdf_page"])]
out["count_readings"] = len(cr)
out["count_readings_not_equal_M"] = cr_bad

# chart cards
cc = [r for r in pq.read_table(D / "benchmark_chart_cards.parquet").to_pylist() if r["benchmark"] == "v3"]
cc_bad = []
for r in cc:
    src = B / "position-chart" / (r["card_id"] + ".png")
    loose = PKG / "release" / r["image_path"]
    if not src.exists() or not loose.exists() or src.read_bytes() != loose.read_bytes():
        cc_bad.append(r["card_id"])
out["v3_cards"] = len(cc)
out["v3_cards_not_equal_M"] = cc_bad
out["M_position_chart_files"] = len(list((B / "position-chart").glob("*.png")))

# image_assets sha column against files
ia = pq.read_table(D / "image_assets.parquet").to_pylist()
ia_bad = []
for r in ia:
    if r["storage"] == "loose_png":
        b = (PKG / "release" / r["image_path"]).read_bytes()
    else:
        continue
    if sha(b) != r["sha256"] or len(b) != r["bytes"]:
        ia_bad.append(r["image_path"])
out["image_assets_loose_checked"] = sum(1 for r in ia if r["storage"] == "loose_png")
out["image_assets_loose_hash_bad"] = ia_bad
Path(__file__).with_name("v3-content-check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
