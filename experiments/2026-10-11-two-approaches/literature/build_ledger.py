"""Build and verify our source summaries and recommendation-to-extension ledger."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-11-two-approaches/literature"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    prior_path = ROOT / "experiments/2026-10-06-field-recommendations/sources.json"
    previous = {row["id"]: row for row in read(prior_path)}
    acquisition = {row["id"]: row for row in read(RAW / "acquisition-log.json")}
    groups = {
        "G-RYM": ["RAO-2009", "YADAV-NGRAMS-2009-2010", "YADAV-2013", "VAHIA-2025", "GANESAN-ETAL-2010", "RAO-2018"],
        "G-MUK": ["MUKHOPADHYAY-2019", "MUKHOPADHYAY-2023"],
        "G-PAR": ["PARPOLA-2008"], "G-FRE": ["FRENEZ-2018"],
        "G-WF": ["WELLS-2015", "FULS-NUMERICAL-2020-2023"],
        "G-FSW": ["FSW-2004", "SPROAT-2013"],
        "G-KM": ["KHANNA-MERRIAM-2025", "MERRIAM-2026"],
        "G-NAIR": ["NAIR-2026"], "G-RAG": ["RAGHAVENDRA-2026"], "G-SHARM": ["SHARMAN-2026"],
        "G-TIWARI": ["TIWARI-2026"],
    }
    other_prior_records = {
        "YADAV-NGRAMS-2009-2010": "research/literature/source_identity_index.json; research/literature/evidence_and_novelty_matrix.md, Entropy and n-grams",
        "MUKHOPADHYAY-2019": "research/literature/source_identity_index.json; experiments/2026-10-06-field-recommendations/first-pass/sources.json",
        "FULS-NUMERICAL-2020-2023": "research/literature/metrology/numerical_source_premises.json; research/literature/report_source_review_final.md",
        "KHANNA-MERRIAM-2025": "research/literature/2026-10-08-bonta-follow-ups/assessment.json; research/literature/evidence_and_novelty_matrix.md",
        "MERRIAM-2026": "research/literature/2026-10-08-bonta-follow-ups/assessment.json",
        "NAIR-2026": "research/literature/evidence_and_novelty_matrix.md, Nair2026v1",
        "RAGHAVENDRA-2026": "research/literature/evidence_and_novelty_matrix.md, Raghavendra2026",
        "TIWARI-2026": "research/literature/source_identity_index.json; research/literature/evidence_and_novelty_matrix.md, Tiwari2026",
    }
    sources = []
    for note in read(OUT / "source-notes.json"):
        old = previous.get(note.get("prior_id"), {})
        source = {key: old[key] for key in ("title", "authors", "year", "venue", "url") if key in old}
        source.update(note)
        source["reviewed_date"] = "2026-10-11"
        source.setdefault("publication_status", "published source; exact edition and access described in reused record")
        source.setdefault("access", "existing local primary-source witness and selected extract")
        source.setdefault("rights_status", "rights-unverified")
        source["source_payload_disposition"] = "local-only"
        source["summary_status"] = "own-work; source interpretations are attributed, not authenticated readings"
        source["author_group"] = next(group for group, ids in groups.items() if source["id"] in ids)
        if old:
            source["prior_record"] = prior_path.relative_to(ROOT).as_posix() + "#" + old["id"]
        elif source["id"] in other_prior_records:
            source["prior_record"] = other_prior_records[source["id"]]
        source["prior_index_status"] = (
            "already indexed in project memory before this run"
            if old or source["id"] in other_prior_records
            else "not found in the searched project literature/index records; recovered in this run"
        )
        source["this_run_reading_status"] = (
            "new direct full-source acquisition, with only the stated pages substantively read"
            if source["id"] == "SHARMAN-2026"
            else "new indexed-primary-text inspection, with the stated passages read"
            if source["id"] in {"FULS-NUMERICAL-2020-2023", "MERRIAM-2026"}
            else "earlier local primary witness reused; the stated pages/sections rechecked"
        )
        record = acquisition[source["id"]]
        source["acquisition"] = record
        indexed = RAW / (source["id"].lower() + ".web-witness.json")
        if indexed.exists():
            source["indexed_primary_witness"] = {"path": indexed.relative_to(ROOT).as_posix(), "sha256": sha(indexed), "bytes": indexed.stat().st_size, "format": "JSON wrapping tool-indexed primary text; no original figure pixels"}
        supplemental = []
        if source["id"] == "MERRIAM-2026":
            path = RAW / "merriam-2026-conclusion.web-witness.json"
            supplemental.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "role": "Indexed printed20 conclusion and recommendations"})
        if source["id"] == "SHARMAN-2026":
            for filename in ("sharman-2026-paper.pdf", "sharman-2026-paper.extract.json", "sharman-2026-paper.acquisition.json"):
                path = RAW / filename
                supplemental.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "role": "Directly acquired paper / extraction / transport record"})
        if supplemental:
            source["supplemental_witnesses"] = supplemental
        if source["id"] == "FULS-NUMERICAL-2020-2023":
            source["acquisition"]["role"] = "Earlier project premise table is a secondary reading record; indexed_primary_witness is the newly inspected primary text."
        sources.append(source)
    write(OUT / "sources.json", sources)

    retained = {"F05", "F06", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "F25", "F26", "F29", "F30", "F36", "F37", "F38", "F39", "F47", "F48"}
    old_rows = read(ROOT / "experiments/2026-10-06-field-recommendations/recommendations.json")
    source_by_id = {source["id"]: source for source in sources}
    extensions = {
        "F05": "Compare learned boundaries and transitions across sites after type and length conditioning; preserve unsupported small-site predictions.",
        "F06": "Prepare a dated-object boundary analysis after consistent excavation/period joins are acquired. Current chronology results are reused.",
        "F18": "Fit an unsupervised latent-field sequence model on training objects; compare held-out likelihood with first/second-order and position references.",
        "F19": "Evaluate learned modules separately by site and carrier class; site/type covariation must be controlled in either predictive direction.",
        "F20": "Keep inventory identities until original images support a split or merge; report class stability under existing qualified crosswalks.",
        "F21": "Estimate modules from sequences, then evaluate their relations with independently recorded site, artifact and motif observations.",
        "F22": "Specify graphic components from images before testing their distributional effect; later rebus searches require matched lexical alternatives.",
        "F23": "Separate rare-code uncertainty, single physical witnesses and repeated manufacturing copies; model rare code coverage explicitly.",
        "F24": "Test motif and sequence channels on physical carrier groups; catalogue or accession proximity is not a direct user/workshop relation.",
        "F25": "Retain existing chronological endpoints; a new longitudinal model requires narrower secure dates and common recovery frames.",
        "F26": "Compare authority/identity hypotheses with quantity and entitlement models, stating the extra observations needed to distinguish their social claims.",
        "F29": "Use valid attested corpora where independent splits exist, and simulated workflow/compositional rivals with fully recorded generation rules.",
        "F30": "Condition model comparisons on text length and examine new recombinations of trained fields; evaluate on known-language and nonphonetic controls.",
        "F36": "Convert semantic-scope proposals into competing observed constraints: stable identity, quantity-dependent content, and fixed authorization or fee slabs.",
        "F37": "Freeze code/motif predictions before measuring new stamped goblet capacities and production traces; current source-fit examples supply no independent unit.",
        "F38": "Use opposed physical faces, manufacturing repetition and carrier/media predictions; exact labor/ration meanings require measured content or securely observed use.",
        "F39": "Test whether motif/text channels share or partition observable information at fixed site/type/length; elite legal monopolies require separate social evidence.",
        "F47": "Test sign modifiers against matched contexts and motifs, with graphic definitions fixed independently of those outcomes.",
        "F48": "Treat a base-plus-modifier field as an image-linked hypothesis; compare fused and serial renderings on fresh physical cases.",
    }
    selected_ids = {"F18", "F19", "F21", "F29", "F30", "F36", "F38", "F39"}
    rows = []
    for old in old_rows:
        if old["id"] not in retained:
            continue
        source = source_by_id[old["source_id"]]
        rows.append({
            "id": old["id"], "source_id": old["source_id"], "source_title": source["title"],
            "author_prescription": old["recommendation"], "source_locator": old["source_locator"],
            "kind": "actual source prescription or stated priority",
            "short_anchor": old["anchor"]["text"],
            "earlier_row": "experiments/2026-10-06-field-recommendations/recommendations.json#" + old["id"],
            "our_extension": extensions[old["id"]], "extension_status": "proposed in literature selection; empirical outcome belongs to the selected package",
            "selected_for_two_packages": old["id"] in selected_ids,
        })
    rows.extend([
        {"id": "K25-01", "source_id": "KHANNA-MERRIAM-2025", "author_prescription": "Apply context expansion to more specific semantic categories, use site/type/temporal restrictions and continuous exclusivity, and seek external comparisons.", "source_locator": "Printed 22/PDF 4; printed 21/PDF 3", "kind": "actual source prescription", "short_anchor": "more specific semantic categories", "our_extension": "Fit category-neutral modules first and test observational roles across carrier types; compare substitution-resistant pairs with nonphonetic category-pair controls.", "selected_for_two_packages": True},
        {"id": "M26-01", "source_id": "MERRIAM-2026", "author_prescription": "Extend candidate-pair analysis to Near Eastern inscriptions and constrain repeated signs across pairings, with independent archaeological, epigraphic and linguistic tests.", "source_locator": "Printed 20, Discussion and Conclusion", "kind": "actual source prescription", "short_anchor": "systems of equations", "our_extension": "Require registered object and graphic correspondences before cross-region pairing; test competing interpretations with the same candidate budget.", "selected_for_two_packages": False},
        {"id": "R26-01", "source_id": "RAGHAVENDRA-2026", "author_prescription": "Fix values and predictions before tests, use held-out inscriptions and matched alternatives, evaluate resample stability and external facts.", "source_locator": "HTML §7, Stronger evidence for decipherment", "kind": "actual source prescription", "short_anchor": "recovers stable values across resamples", "our_extension": "Build latent-module stability, source-group closure and matched nonphonetic rivals into both selected packages; keep semantic label equivalence visible.", "selected_for_two_packages": True},
    ])
    for row in rows:
        row.setdefault("extension_status", "proposed in literature selection; empirical outcome belongs to the selected package")
        row.setdefault("source_title", source_by_id[row["source_id"]]["title"])
    write(OUT / "recommendations.json", rows)

    checks = []
    for source in sources:
        acquisition_record = source["acquisition"]
        if "extract_path" in acquisition_record:
            path = ROOT / acquisition_record["extract_path"]
            checks.append({"check": "extract hash", "id": source["id"], "pass": sha(path) == acquisition_record["extract_sha256"]})
        if "indexed_primary_witness" in source:
            record = source["indexed_primary_witness"]
            checks.append({"check": "indexed witness hash", "id": source["id"], "pass": sha(ROOT / record["path"]) == record["sha256"]})
        for record in source.get("supplemental_witnesses", []):
            checks.append({"check": "supplemental witness hash", "id": source["id"], "pass": sha(ROOT / record["path"]) == record["sha256"]})
    for row in rows:
        source = source_by_id[row["source_id"]]
        payload = ""
        if "extract_path" in source["acquisition"]:
            extract = read(ROOT / source["acquisition"]["extract_path"])
            payload = "\n".join(item["text"] for item in extract)
        if source.get("indexed_primary_witness"):
            payload += (ROOT / source["indexed_primary_witness"]["path"]).read_text(encoding="utf-8")
        # Tool-indexed JSON wraps a string containing escaped line endings.
        if source["id"] == "MERRIAM-2026":
            indexed_data = read(ROOT / source["indexed_primary_witness"]["path"])
            payload += str(indexed_data["result"])
            for record in source.get("supplemental_witnesses", []):
                payload += str(read(ROOT / record["path"])["result"])
        checks.append({"check": "short anchor appears in inspected witness", "id": row["id"], "pass": norm(row["short_anchor"]) in norm(payload)})
    validation = {"sources": len(sources), "recommendations": len(rows), "author_groups": len(groups), "source_coverage_complete": len(sources) == len(source_by_id) == 20, "checks": checks, "passed": sum(item["pass"] for item in checks), "failed": sum(not item["pass"] for item in checks), "scope": "Mechanical source/anchor checks; attribution and extension judgments remain manual."}
    write(OUT / "validation.json", validation)
    print(json.dumps({key: value for key, value in validation.items() if key != "checks"}))


if __name__ == "__main__":
    main()
