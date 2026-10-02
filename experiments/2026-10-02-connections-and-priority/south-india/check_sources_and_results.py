"""Verify local source bytes and the saved Tamil Nadu analysis endpoints.

This checker reads existing witnesses. It never changes an analysis endpoint.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import py_compile
import tempfile

import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-02-connections-and-priority/south-india"
checks = []


def check(name, passed, detail=None):
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


pdfs = [
    ("morphological-study-2025.pdf", 8, "morphological-acquisition.json",
     "2025 morphological-study brochure; full 145-page book not acquired"),
    ("inscribed-potsherds-vol1-2026.pdf", 740,
     "inscribed-potsherds-vol1-2026.pdf.acquisition.json", "2026 catalogue Volume I"),
    ("inscribed-potsherds-vol2-2026.pdf", 712,
     "volume2-acquisition.json", "2026 catalogue Volume II"),
    ("cict-tamil-epigraphy-book30.pdf", 57,
     "cict-tamil-epigraphy-book30.pdf.acquisition.json", "2020 epigraphy book preview"),
]
witnesses = []
for name, pages, acquisition, scope in pdfs:
    path = RAW / name
    with fitz.open(path) as doc:
        actual = len(doc)
    record = read(HERE / acquisition)
    check(f"{name}: bytes", path.stat().st_size == record["bytes"])
    check(f"{name}: hash", sha(path) == record["sha256"])
    check(f"{name}: PDF page count", actual == pages, actual)
    witnesses.append({"local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                      "sha256": sha(path), "bytes": path.stat().st_size,
                      "pdf_pages": actual, "scope": scope,
                      "acquisition_record": acquisition,
                      "rights_status": "third-party witness; local-only"})

for relative, source in [
    ("tngraffiti-home.html", "https://tngraffiti.in/"),
    ("tngraffiti-index.js", "https://tngraffiti.in/assets/index-D7vrsNCw.js"),
]:
    path = RAW / relative
    witnesses.append({"local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                      "source_url": source, "sha256": sha(path),
                      "bytes": path.stat().st_size,
                      "retrieval_time": "not recorded in a contemporaneous manifest",
                      "rights_status": "third-party witness; local-only"})

for manifest in ["portal-v1/acquisition.json", "additional-api-acquisition.json",
                 "concordance39-acquisition.json"]:
    obj = read(HERE / manifest)
    rows = obj if isinstance(obj, list) else obj.get("reads", [obj])
    for row in rows:
        if "local_path" not in row:
            continue
        path = ROOT / row["local_path"]
        check(f"{manifest}: {path.name}: hash", sha(path) == row["sha256"])
        if "bytes" in row:
            check(f"{manifest}: {path.name}: bytes", path.stat().st_size == row["bytes"])

aggregate = read(HERE / "aggregate-v1/results.json")
for name, digest in aggregate["input_hashes"].items():
    check(f"aggregate input: {name}", sha(RAW / "portal-v1" / name) == digest)
check("42 families", aggregate["family_count"] == 42)
check("form counts", aggregate["catalogue_form_counts"] ==
      {"Base": 42, "Variant": 546, "Composite": 1522})
check("family occurrence sum", sum(aggregate["family_route_occurrences"].values()) ==
      aggregate["family_route_occurrence_total"] == 9345)
check("site total and residual", aggregate["site_route_occurrence_total"] == 9349 and
      sum(r["sites_route"] - r["family_route"] for r in
          aggregate["cross_route_cells_differing"]) == 4)
check("all within-form margins agree", not aggregate["within_form_margin_discrepancies"])

membership = read(HERE / "stroke-membership-v2/results.json")
for name, digest in membership["inputs"].items():
    check(f"membership input: {name}", sha(RAW / name) == digest)
props = membership["own_form_properties"]
check("194 resolved compounds", len(props) ==
      membership["resolved_compounds_with_explicit_plain_strokes"] == 194)
check("209 compound keys", len(props) + len(membership["opaque"]) ==
      membership["compound_keys"] == 209)
check("consistent repeated representations", not membership["inconsistent"])
check("491 resolved occurrences", sum(p["reported_occurrences"] for p in props) ==
      membership["resolved_reported_occurrences"] == 491)
check("142 simple forms", sum(p["simple_pair"] for p in props) ==
      membership["simple_pair_forms"] == 142)
check("413 simple-form occurrences", sum(p["reported_occurrences"] for p in props
      if p["simple_pair"]) == membership["simple_pair_reported_occurrences"] == 413)
check("13 separated stroke-block forms", sum(p["stroke_blocks"] > 1 for p in props) ==
      membership["split_stroke_block_forms"] == 13)
check("40 multi-other-component forms", sum(p["other_components"] > 1 for p in props) ==
      membership["forms_with_several_other_components"] == 40)
check("component length histogram", {str(k): v for k, v in
      sorted(Counter(p["component_count"] for p in props).items())} ==
      membership["component_length_form_counts"])
for p in props:
    check(f"{p['form']}: components", p["stroke_components"] + p["other_components"] ==
          p["component_count"])
    check(f"{p['form']}: block bounds", 1 <= p["stroke_blocks"] <= p["stroke_components"])
check("source disagreements retained", [r["form"] for r in
      membership["printed_source_checks"] if not r["agrees"]] == ["4.19C"])

for run, script in [("aggregate-v1", "analyze_portal.py"),
                    ("stroke-context-v1", "analyze_stroke_contexts.py"),
                    ("stroke-membership-v2", "analyze_stroke_membership.py")]:
    check(f"{run}: code snapshot", (HERE / run / "code_snapshot.py").read_bytes() ==
          (HERE / script).read_bytes())
with tempfile.TemporaryDirectory(prefix="indus-south-syntax-") as temp:
    for path in sorted(HERE.glob("*.py")):
        try:
            py_compile.compile(str(path), cfile=str(Path(temp) / (path.stem + ".pyc")),
                               doraise=True)
            check(f"{path.name}: syntax", True)
        except py_compile.PyCompileError as exc:
            check(f"{path.name}: syntax", False, str(exc))

manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "witnesses": witnesses,
            "API_manifest": "portal-v1/acquisition.json",
            "source_page_coordinates": {
                "volI_stroke_descriptions": {"printed_pages": [387, 388], "pdf_pages": [426, 427]},
                "volI_stroke_plate": {"printed_page": 684, "pdf_page": 723},
                "volI_shared_graffiti_Tamili_examples": {"printed_pages": [250, 251, 252],
                                                         "pdf_pages": [289, 290, 291]},
                "volII_compound_checks": membership["printed_source_checks"]},
            "release_scope": "Own summaries and hashes tracked; all acquired pixels, PDFs, client maps and raw responses local-only"}
(HERE / "source-witnesses.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
result = {"created_utc": datetime.now(timezone.utc).isoformat(),
          "status": "pass" if all(c["passed"] for c in checks) else "fail",
          "checks_total": len(checks), "failed": [c for c in checks if not c["passed"]],
          "scope": "Source integrity, saved-output arithmetic and code syntax; printed comparisons were visually observed and are separately reviewed",
          "checks": checks}
(HERE / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "checks"}))
raise SystemExit(0 if result["status"] == "pass" else 1)
