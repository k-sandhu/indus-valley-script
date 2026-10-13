"""Audit documentary integrity, chronology labels and explicitly missing quantities.

No statistical hypothesis test, historical probability or capacity estimate is computed.
Fresh run directories are mandatory. Run from the repository root.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
import fitz

PACKAGE = Path("experiments/2026-10-11-societal-persistence/evidence")
RAW = Path("data/raw/2026-10-11-societal-persistence/evidence")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    source_data = json.loads((PACKAGE / "sources.json").read_text(encoding="utf-8"))
    obs = json.loads((PACKAGE / "observations.json").read_text(encoding="utf-8"))["observations"]
    attempts = json.loads((PACKAGE / "acquisition-index.json").read_text(encoding="utf-8"))["attempts"]
    works = source_data["included_primary_works"]
    checks = []

    def check(label, passed, detail):
        checks.append({"check": label, "passed": bool(passed), "detail": detail})

    source_map = {s["source_id"]: s for s in works}
    check("unique-source-ids", len(source_map) == len(works), len(works))
    check("unique-observation-ids", len({o["observation_id"] for o in obs}) == len(obs), len(obs))
    for s in works:
        check(f"{s['source_id']}-scope", all(s.get(k) for k in ["title", "citation", "reading_scope", "evidence_lineage", "publication_dates"]), "Required bibliographic, inspection and dependence fields present")
        for w in s["witnesses"]:
            p = Path(w["path"])
            okay = p.is_file() and digest(p) == w["sha256"] and p.stat().st_size == w["bytes"]
            check(f"{s['source_id']}-witness-{p.name}", okay, "Existence, bytes and SHA256 match frozen ledger")
            if p.suffix == ".pdf":
                check(f"{s['source_id']}-pdf-signature-{p.name}", p.read_bytes()[:4] == b"%PDF", "Included PDF is a PDF rather than a download challenge")
    missing_keys = ["measured_service_delivery", "task_duration_bounds", "task_window", "demand_lower_bound", "initial_delivery_upper_bound", "imports_upper_bound"]
    for o in obs:
        s = source_map.get(o["source_id"])
        check(f"{o['observation_id']}-source-join", bool(s) and o["witness_hash"] in [w["sha256"] for w in s["witnesses"]], "Observation refers to an inspected source witness")
        check(f"{o['observation_id']}-unit-and-locus", all(o.get(k) for k in ["locus", "site", "context", "phase", "dating_basis", "observation_type", "outcome_unit"]), "Exact locus and chronological/outcome units retained")
        check(f"{o['observation_id']}-unmeasured-gate", all(o.get(k) is None for k in missing_keys), "Unmeasured historical service/schedule quantities remain null")
        check(f"{o['observation_id']}-lineage-join", s and o["evidence_lineage"] == s["evidence_lineage"], "Edition or format is not a new evidence lineage")
    for i, a in enumerate(attempts):
        if a["status"] == "acquired":
            p = Path(a["path"])
            okay = p.is_file() and digest(p) == a["sha256"] and p.stat().st_size == a["bytes"]
        else:
            okay = bool(a.get("error"))
        check(f"acquisition-{i+1}", okay, {"filename": a["filename"], "status": a["status"]})
    derivatives = []
    for manifest in sorted(RAW.glob("extract-v*/manifest.json")):
        for row in json.loads(manifest.read_text(encoding="utf-8")):
            okay = digest(row["input_path"]) == row["input_sha256"] and digest(row["output_path"]) == row["output_sha256"]
            check(f"derivative-{len(derivatives)+1}", okay, row["method"])
            derivatives.append(row)

    anchors = [
        ("Harappa-clog", "acquisition-v1/meadow-kenoyer1997.pdf", 8, "totally clogged"),
        ("Harappa-replacement", "acquisition-v1/meadow-kenoyer1997.pdf", 8, "was dug farther"),
        ("Dholavira-interruption", "acquisition-v1/asi1991-1992.pdf", 38, "after a brief desertion"),
        ("Dholavira-retention", "acquisition-v1/asi1991-1992.pdf", 38, "some of the reservoirs"),
        ("Dholavira-salvage", "acquisition-v1/asi1991-1992.pdf", 38, "stones were robbed"),
        ("East-bank-repair", "acquisition-v5/bisht2015-preliminary-original.pdf", 178, "repaired during stage iv"),
        ("East-water-function-ended", "acquisition-v5/bisht2015-preliminary-original.pdf", 180, "ceased to be a water structure"),
        ("East-episodic-use", "acquisition-v5/bisht2015-preliminary-original.pdf", 181, "no regular and continuous occupation"),
        ("Drill-production-waste", "acquisition-v1/kenoyer-vidale1992.pdf", 9, "manufacturing sequence"),
        ("Jansen-flow-unresolved", "acquisition-v3/jansen2011.pdf", 24, "none was found completely intact"),
    ]
    for label, rel, page, fragment in anchors:
        text = fitz.open(RAW / rel)[page-1].get_text()
        check(label, fragment in normalized(text), {"path": (RAW / rel).as_posix(), "pdf_page": page, "check_type": "short source-location anchor; interpretation still requires reading"})

    xml = BeautifulSoup((RAW / "acquisition-v2/suryanarayan2021-full.xml").read_bytes(), "xml")
    table = next(t for t in xml.find_all("table-wrap") if t.find("label") and t.find("label").get_text(strip=True) == "Table 4")
    tr = next(r for r in table.find_all("tr") if "Total number of samples analysed" in r.get_text(" ", strip=True))
    table_counts = [int(x.get_text(strip=True)) for x in tr.find_all("td")[1:]]
    check("S12-table-count-exception-preserved", table_counts == [15, 31, 30, 28, 7, 30, 30] and sum(table_counts) == 171,
          "Text reports 172; Table 4 row gives 171. This check confirms the discrepancy, not a resolution.")
    am = xml.find("article-meta")
    check("S12-volume-identity", am.find("volume").get_text(strip=True) == "125", "Final article is in volume 125")
    old_ocr = Path("data/raw/2026-10-11-early-indian-continuity/institutions/kenoyer1998-craft-pdf2.txt").read_text(encoding="utf-8")
    check("S09-issue-year", "July-December, 1996" in old_ocr, "Inspected issue header controls 1998 hosted filename")

    viewed = [
        ("S03", "acquisition-v1/meadow-kenoyer1997.pdf", 8),
        ("S04", "acquisition-v1/asi1991-1992.pdf", 36),
        ("S04", "acquisition-v1/asi1991-1992.pdf", 38),
        ("S08", "acquisition-v1/kenoyer-vidale1992.pdf", 8),
        ("S08", "acquisition-v1/kenoyer-vidale1992.pdf", 9),
        ("S08", "acquisition-v1/kenoyer-vidale1992.pdf", 10),
        ("S12", "acquisition-v1/suryanarayan2021.pdf", 7),
        ("S12", "acquisition-v1/suryanarayan2021.pdf", 10),
        ("S05", "acquisition-v5/bisht2015-preliminary-original.pdf", 121),
        ("S05", "acquisition-v5/bisht2015-preliminary-original.pdf", 178),
        ("S05", "acquisition-v5/bisht2015-preliminary-original.pdf", 179),
        ("S05", "acquisition-v5/bisht2015-preliminary-original.pdf", 180),
    ]
    images = []
    for sid, rel, n in viewed:
        stem = Path(rel).stem
        short = "bisht2015" if sid == "S05" else stem
        if sid == "S02": short = "jansen2011"
        im = RAW / "inspection-v1" / f"{short}-pdf{n}.png"
        check(f"visual-witness-{sid}-{n}", im.is_file(), "Page was emitted and visually inspected during research; this is an inspection record, not automated interpretation")
        images.append({"source_id": sid, "source_path": (RAW / rel).as_posix(), "source_sha256": digest(RAW / rel), "pdf_page": n, "render_path": im.as_posix(), "render_sha256": digest(im), "inspection": "visually inspected by researcher", "render_method": "PyMuPDF raster rendering; images remain local-only"})

    lineage_counts = Counter(s["evidence_lineage"] for s in works)
    gate_eligible = [o["observation_id"] for o in obs if all(o[k] is not None for k in ["measured_service_delivery", "demand_lower_bound", "initial_delivery_upper_bound", "imports_upper_bound"])]
    summary = {"audit_type": "documentary integrity and source-scope checks; not statistical or historical validation",
               "included_primary_works": len(works), "excluded_candidates": len(source_data["excluded_candidates"]),
               "observations": len(obs), "acquisition_attempts": len(attempts), "acquisition_statuses": dict(Counter(a["status"] for a in attempts)),
               "verified_text_derivatives": len(derivatives), "current_visually_inspected_pages": len(images),
               "source_lineage_labels": dict(lineage_counts), "lineage_warning": "Labels are descriptive provenance groups; partial overlap also exists across different labels. They are not an effective independent sample size.",
               "observation_types": dict(Counter(o["observation_type"] for o in obs)),
               "missing_quantities": {k: sum(o[k] is None for o in obs) for k in missing_keys},
               "eligible_quantitative_reconstructions": gate_eligible,
               "gate_interpretation": "Zero eligibility follows from explicitly unmeasured quantities; no historical bound was estimated or tested.",
               "checks": len(checks), "passed": sum(c["passed"] for c in checks), "failed": [c["check"] for c in checks if not c["passed"]],
               "source_exceptions": [{"source_id": "S12", "text_sample_count": 172, "table4_counts": table_counts, "table4_sum": sum(table_counts), "status": "unresolved source inconsistency; no new statistical fit"}]}
    for name, value in [("checks.json", checks), ("summary.json", summary), ("source-page-inspection.json", images)]:
        (args.output_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    inputs = {p.as_posix(): digest(p) for p in [PACKAGE / "PROTOCOL.md", PACKAGE / "sources.json", PACKAGE / "observations.json", PACKAGE / "acquisition-index.json", PACKAGE / "build_ledger.py", PACKAGE / "audit.py"]}
    (args.output_dir / "input-hashes.json").write_text(json.dumps(inputs, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["included_primary_works", "observations", "acquisition_attempts", "checks", "passed", "failed", "current_visually_inspected_pages"]}))
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
