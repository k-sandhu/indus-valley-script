"""Verify reviewer witnesses, source locators and the coordinator's control scope."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/review"
CHECKS = []


def check(identifier, passed, **detail):
    CHECKS.append({"id": identifier, "pass": bool(passed), **detail})


def compact(source_id):
    return re.sub(r"\s+", " ", (RAW / (source_id + ".txt")).read_text(encoding="utf-8"))


def main():
    output = HERE / "source-checks-v1.json"
    if output.exists():
        raise FileExistsError(output)
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
    chronology = json.loads((HERE / "chronology.json").read_text(encoding="utf-8"))
    ids = [s["id"] for s in sources["sources"]]
    check("source-identifiers-unique", len(ids) == len(set(ids)) == 15)
    check("chronology-source-references", all(set(c["source_ids"]) <= set(ids) for c in chronology["records"]))
    axes = {"archaeological_or_physical", "composition", "collection_or_redaction", "extant_witness", "narrated_time"}
    check("five-date-axes-all-records", all(set(c["date_axes"]) == axes for c in chronology["records"]))
    successful = []
    for manifest in sorted(RAW.glob("capture-v*.json")):
        for rec in json.loads(manifest.read_text(encoding="utf-8"))["sources"]:
            if "local_path" not in rec:
                check("failed-access-preserved-" + rec["source_id"], bool(rec.get("error")))
                continue
            successful.append(rec)
            p = ROOT / rec["local_path"]
            check("witness-hash-" + rec["source_id"], hashlib.sha256(p.read_bytes()).hexdigest() == rec["sha256"])
            check("witness-size-" + rec["source_id"], p.stat().st_size == rec["bytes"])
            check("raw-handling-" + rec["source_id"], rec["raw_handling"] == "local-only")
            if "page_count" in rec:
                check("pdf-pages-" + rec["source_id"], len(fitz.open(p)) == rec["page_count"])
            if "extraction" in rec:
                ex = rec["extraction"]
                check("extraction-hash-" + rec["source_id"], hashlib.sha256((ROOT / ex["path"]).read_bytes()).hexdigest() == ex["sha256"])
                check("extraction-parent-" + rec["source_id"], ex["parent_sha256"] == rec["sha256"])
    probes = [
        ("jb-composition-estimate", "jamison2014-2-15", "1400–1000 BCE", "printed p.5"),
        ("jb-inherited-poetic-conventions", "jamison2014-2-15", "poetic conventions", "printed p.5"),
        ("jb-family-core", "jamison2014-2-15", "The core of the", "printed p.10"),
        ("jb-sponsored-assembly-attribution", "jamison2014-13-22", "Michael Witzel", "printed pp.14–15"),
        ("jb-phonetic-change", "jamison2014-13-22", "phonetics of the text", "printed p.17"),
        ("jb-understanding-not-unbroken", "jamison2014-13-22", "unbroken", "printed p.18"),
        ("jb-misunderstanding-author-assessment", "jamison2014-13-22", "distorts or misunderstands", "printed p.18"),
        ("allon-actual-publication", "allon2021", "2022 Jan 26;50(4):523–556", "article header"),
        ("allon-limited-permission", "allon2021", "duration of the World Health Organization", "copyright notice"),
        ("allon-narrative-variation", "allon2021", "narrative portions", "comparative changes discussion"),
        ("allon-sanctioned-editions", "allon2021", "formal “editions” sanctioned by the community", "comparison discussion"),
        ("wiles-oldest-canonical-witness-report", "wiles2006", "eleventh to twelfth centuries CE", "printed p.61"),
        ("wiles-date-source-limits", "wiles2006", "None of the sources before", "printed p.74"),
        ("wiles-ambiguous-dated-event", "wiles2006", "What the dates refer to is not clear", "printed p.74"),
        ("haoma-related-control", "haoma-rituals", "establish their common origin", "opening comparison"),
        ("gnoli-elements-not-organic-system", "indo-iranian-religion", "reconstruct an organic system", "opening comparative-method paragraph"),
        ("loc-object-manuscript-range", "loc-gandhara", "first century BCE and first century CE", "holding description"),
        ("lmu-population-manuscript-range", "lmu-gandhara", "1st c. BCE to the 4th c. CE", "project overview"),
        ("hultzsch-audiences", "hultzsch1925-ocr", "groups of monks", "printed pp.173–174, OCR/transcription scope"),
        ("hultzsch-discourse-title", "hultzsch1925-ocr", "Vinaya-samukase", "printed p.173"),
        ("sb11-quotation-locus", "sb11-gretil", "11.5.1.[6]", "SB11.5.1.6"),
        ("sb11-explanatory-return", "sb11-gretil", "11.5.1.[10]", "SB11.5.1.10"),
        ("sb11-named-wood-configurations", "sb11-gretil", "śamīmayīmadharāraṇiṃ", "SB11.5.1.15"),
        ("sb11-prescribed-final-configuration", "sb11-gretil", "11.5.1.[17]", "SB11.5.1.17"),
        ("sb01-descent-compound", "sb01-gretil", "manoravasarpaṇamityaugho", "SB1.8.1.6"),
    ]
    for identifier, source_id, needle, locator in probes:
        check(identifier, needle in compact(source_id), source_id=source_id, locator=locator,
              method="locator/text-presence check after reviewer reading; not independent authentication of the represented event")
    kenoyer = fitz.open(RAW / "kenoyer2006.pdf")
    check("kenoyer-image-only-not-automated-reading", sum(len(p.get_text().strip()) for p in kenoyer) == 0)
    rendered = []
    for i in range(1, 5):
        p = RAW / f"kenoyer2006-page-{i}.png"
        rendered.append({"local_path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                         "parent_sha256": hashlib.sha256((RAW / "kenoyer2006.pdf").read_bytes()).hexdigest(),
                         "transformation": f"PyMuPDF rasterization of PDF page{i} at matrix1.7; visually inspected"})
    by_source = {s["id"]: s for s in sources["sources"]}
    check("witzel-limited-access-explicit", "metadata" in by_source["WIT1997"]["inspected"] and "No successful full-text" in by_source["WIT1997"]["inspected"])
    check("museum-search-only-explicit", "Search-returned" in by_source["BM1880-21"]["inspected"])
    root_sources = json.loads((HERE.parent / "coordinator/sources.json").read_text(encoding="utf-8"))
    root_obs = json.loads((HERE.parent / "coordinator/observations.json").read_text(encoding="utf-8"))
    root_ids = {s["id"] for s in root_sources["sources"]}
    check("coordinator-observation-source-links", all(o["source"] in root_ids for o in root_obs["observations"]))
    check("coordinator-two-sb-editions-one-group", len({s["dependency_group"] for s in root_sources["sources"] if s["id"].startswith("SB11")}) == 1)
    result = {"status": "source witnesses and selected source-control locators checked; manual interpretation scope recorded separately",
              "passed": sum(c["pass"] for c in CHECKS), "failed": sum(not c["pass"] for c in CHECKS),
              "checks": CHECKS, "rendered_witnesses_local_only": rendered}
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("passed", "failed")}))
    if result["failed"]:
        print(json.dumps([c for c in CHECKS if not c["pass"]], ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
