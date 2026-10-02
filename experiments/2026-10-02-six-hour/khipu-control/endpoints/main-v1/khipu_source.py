"""Local source audit and reference extraction, separate from tested inference."""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/six-hour/khipu/puruchuco-2026-10-02"
OUT = ROOT / "experiments/2026-10-02-six-hour/khipu-control"
NAMES = ("UR063", "UR064", "UR066", "UR067", "UR068", "UR073")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def audit():
    db = sqlite3.connect(RAW / "khipu.db")
    db.row_factory = sqlite3.Row
    raw_records, summaries = [], []
    schema = [dict(x) for x in db.execute("select name,sql from sqlite_master where type='table'")]
    concordance = {}
    with (RAW / "okr-kh-numbers.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            for name in NAMES:
                if name in [x.strip() for x in row["Other Names"].split(",")]:
                    concordance[name] = row
    for name in NAMES:
        mains = list(db.execute("select * from khipu_main where INVESTIGATOR_NUM=?", (name,)))
        assert len(mains) == 1
        main = dict(mains[0]); k = main["KHIPU_ID"]
        cords = [dict(x) for x in db.execute("select * from cord where KHIPU_ID=? order by CORD_LEVEL,CORD_ORDINAL", (k,))]
        clusters = [dict(x) for x in db.execute("select * from cord_cluster where KHIPU_ID=? order by CLUSTER_LEVEL,ORDINAL", (k,))]
        primaries = [dict(x) for x in db.execute("select * from primary_cord where KHIPU_ID=?", (k,))]
        colours = [dict(x) for x in db.execute("select * from ascher_cord_color where KHIPU_ID=?", (k,))]
        knots = [dict(x) for x in db.execute("select knot.* from knot join cord using(CORD_ID) where cord.KHIPU_ID=?", (k,))]
        knot_clusters = [dict(x) for x in db.execute("select knot_cluster.* from knot_cluster join cord using(CORD_ID) where cord.KHIPU_ID=?", (k,))]
        primary_ids = {x["PCORD_ID"] for x in primaries}
        cord_ids = {x["CORD_ID"] for x in cords}
        pendant = [x for x in cords if x["CORD_LEVEL"] == 1 and x["CORD_CLASSIFICATION"] != "M"]
        marker = [x for x in cords if x["CORD_CLASSIFICATION"] == "M"]
        parent_failures = [x["CORD_ID"] for x in cords if x["PENDANT_FROM"] not in primary_ids | cord_ids]
        colour_ids = {x["CORD_ID"] for x in colours if x["PCORD_FLAG"] == 0}
        numbers = [x["INVESTIGATOR_CORD_NUM"] for x in pendant]
        positions = [x["ATTACH_POS"] for x in pendant]
        summary = {
            "name": name, "okr_number": main["OKR_NUM"], "khipu_id": k,
            "concordance_matches": concordance[name]["OKR Number"] == main["OKR_NUM"],
            "museum_number": main["MUSEUM_NUM"], "region": main["REGION"], "provenance_field": main["PROVENANCE"],
            "cord_rows": len(cords), "pendants_excluding_markers": len(pendant), "marker_rows": len(marker),
            "level_counts": dict(collections.Counter(x["CORD_LEVEL"] for x in cords)),
            "recorded_primary_clusters": sum(x["CLUSTER_LEVEL"] == 1 for x in clusters),
            "pendant_attachment_positions": {"null": sum(x is None for x in positions), "zero": sum(x == 0 for x in positions), "nonzero": sum(x not in (0, None) for x in positions)},
            "colour_covered_pendants": sum(x["CORD_ID"] in colour_ids for x in pendant),
            "duplicate_pendant_numbers": len(numbers) - len(set(numbers)),
            "pendant_number_range": [min(numbers), max(numbers)],
            "unresolved_parent_links": len(parent_failures),
            "knot_rows": len(knots), "knot_cluster_rows": len(knot_clusters),
            "knot_cluster_total_value_nonzero": sum(x["TOTAL_VALUE"] not in (0,None) for x in knot_clusters),
            "knot_cluster_total_value_null": sum(x["TOTAL_VALUE"] is None for x in knot_clusters),
            "knot_value_type_null": sum(x["knot_value_type"] is None for x in knots),
            "knot_types": dict(collections.Counter(x["TYPE_CODE"] for x in knots)),
            "termination_codes": dict(collections.Counter(x["TERMINATION"] for x in pendant)),
            "created_on": main["CREATED_ON"], "changed_on": main["CHANGED_ON"],
        }
        summaries.append(summary)
        raw_records.append({"name": name, "main": main, "concordance": concordance[name], "primary_cord": primaries,
                            "cord": cords, "cord_cluster": clusters, "colour": colours, "knot": knots,
                            "knot_cluster": knot_clusters, "unresolved_parent_cord_ids": parent_failures})
    assert db.execute("select count(*) from khipu_main where INVESTIGATOR_NUM='CM009' or orig_inv_num='CM009'").fetchone()[0] == 0
    save(RAW / "bounded-source-records.json", {"schema": schema, "objects": raw_records})
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "database_sha256": sha(RAW / "khipu.db"),
        "source_record_path": "data/six-hour/khipu/puruchuco-2026-10-02/bounded-source-records.json",
        "source_record_sha256": sha(RAW / "bounded-source-records.json"), "objects": summaries,
        "cm009": {"okr_coverage": "absent", "field_guide_status": "reconstructed from Mackey's 1970 thesis pages251–254; knot locations and cord lengths conjectured or drawing-based; pale blue colour replaced with grey green"},
        "numeric_cluster_route": "TOTAL_VALUE is zero throughout all selected knot clusters. This route supplies no numerical cord reading; comparison stops at field coverage.",
        "source_geometry": "All selected pendant ATTACH_POS values are zero. Recorded cluster start/end positions exist; individual pendant positions cannot be treated as measured from this field.",
    }
    save(OUT / "coverage-audit.json", result)
    print(json.dumps({"objects": summaries, "cm009": "absent"}, indent=2))

def prepare():
    from bs4 import BeautifulSoup
    html = RAW / "kfg-puruchuco.html"
    pres = [x.get_text() for x in BeautifulSoup(html.read_text(encoding="utf-8"), "html.parser").find_all("pre")]
    row_block = [x for x in pres if x.startswith("subunit_c  (20)")]
    target_block = [x for x in pres if x.startswith("(20)  0, 0, 1, 0, 19")]
    assert len(row_block) == len(target_block) == 1
    rows = {}
    for line in row_block[0].splitlines()[:3]:
        match = re.fullmatch(r"subunit_([abc])  \(20\)  ([\d, ]+)", line)
        assert match
        rows[match[1]] = [int(x.strip()) for x in match[2].split(",")]
        assert len(rows[match[1]]) == 20
    target_line = target_block[0].splitlines()[0]
    target = [int(x.strip()) for x in target_line.split("  ",1)[1].split(",")]
    assert len(target) == 20
    p = RAW / "source-component-input.json"
    key = RAW / "source-evaluator-key.json"
    save(p, {"source_html_sha256": sha(html), "scope": "published reference quantities; analyst previously exposed",
             "rows": [rows[x] for x in "abc"], "row_ranges_one_based": [[14,33],[34,53],[54,73]],
             "source_name": "UR068", "source_okr": "KH0305", "width": 20})
    save(key, {"source_html_sha256": sha(html), "targets": target, "target_range_one_based": [13,32],
              "target_name": "UR067", "target_okr": "KH0304", "published_source_total": 3498, "published_target_total": 3482,
              "prior_exposure": "Published target values were displayed in the full-page source review before protocol freeze."})
    save(OUT / "source-input-manifest.json", {
        "input_path": p.relative_to(ROOT).as_posix(), "input_sha256": sha(p),
        "key_path": key.relative_to(ROOT).as_posix(), "key_sha256": sha(key),
        "parent_html_sha256": sha(html), "quantities_copied_from": "KFG notebook preformatted blocks11 and13; identified by exact labels and validated lengths",
        "redistribution": "raw reference vectors and detailed source predictions local-only",
    })
    print("Prepared local component inputs and separate evaluator key.")

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("command", choices=["audit", "prepare"])
    args=parser.parse_args()
    (audit if args.command == "audit" else prepare)()
