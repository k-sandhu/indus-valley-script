#!/usr/bin/env python3
"""Write data/MANIFEST.json from the source records below.

The records restate measured sizes from this package's run outputs and
earlier package records; each entry's `evidence` names its basis. The builder
checks that every recorded local path exists and that every recorded hash
matches the current local file, and reports problems without stopping.

    python -I experiments/2026-10-12-data-inventory/build_manifest.py [--check-only]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "MANIFEST.json"
RUN = "experiments/2026-10-12-data-inventory/run-2026-10-12"

STATUS = {
    "held": "A local copy with a recorded hash exists and matches the named edition.",
    "partly-held": "Only an excerpt, snapshot, one of several volumes or a derived table is local.",
    "not-held": "No local copy; the entry records the access route.",
    "project-output": "Produced by this project; tracked in Git or in the project's Hugging Face datasets.",
}
LOCATION = {
    "tracked": "Committed to the Git repository.",
    "local-only": "Present in the owner's working copy under an ignored path; not in Git.",
    "hf-private": "Backed up to a private Hugging Face dataset owned by the project.",
    "external": "Not held; available from the named institution or publisher.",
}
RIGHTS = ["own-work", "explicit-license", "permission-recorded", "rights-unverified", "mixed-assets"]


def http(url, filename, sha=None, size=None, steps=None):
    d = {"method": "http", "url": url, "filename": filename}
    if sha:
        d["sha256"] = sha
    if size:
        d["bytes"] = size
    if steps:
        d["steps"] = steps
    return d


def manual(*steps):
    return {"method": "manual", "steps": list(steps)}


def rebuild(*steps):
    return {"method": "rebuild", "steps": list(steps)}


S = []


def add(**kw):
    kw.setdefault("status", "held")
    kw.setdefault("location", "local-only")
    kw.setdefault("local_paths", [])
    kw.setdefault("hashes", {})
    kw.setdefault("evidence", [])
    kw.setdefault("questions", [])
    S.append(kw)


# ---------------------------------------------------------------------------
# Inscribed-object corpora and their project derivatives
# ---------------------------------------------------------------------------
add(
    id="lipi",
    title="Lipi inscription export and seal image crops (yajnadevam/lipi)",
    kind="corpus-export",
    local_paths=["data/lipi/"],
    version={"commit": "fc8813a52e183d19c441631dc26c33a4dccbea39"},
    size={"faces": 5680, "provisional_objects": 4695, "sites": 78, "image_files": 8722,
          "image_index_keys": 3318, "image_index_files": 6570},
    identifiers=["Lipi numeric family and face id", "CISI reference (raw string)", "excavation-idno (mixed registrations, citations, lots)"],
    metadata_fields=["cisi", "region", "site", "area-section", "block-house", "room-grid", "excavation-idno", "time",
                     "period", "phase", "depth", "boss", "material", "color", "shape", "cross-section",
                     "preservation", "symbol", "cult", "type", "sides", "condition", "complete", "dir.",
                     "h/v/th (inches)", "horizontal/vertical/thickness (mm)"],
    rights={"status": "rights-unverified", "licence": None,
            "detail": "No LICENSE at the pinned commit. Image crops reproduce CISI photographs whose owners are the holding institutions."},
    fetch={"method": "git", "url": "https://github.com/yajnadevam/lipi",
           "commit": "fc8813a52e183d19c441631dc26c33a4dccbea39",
           "verify": {"src/assets/data/inscriptions.csv": "c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c",
                      "src/assets/data/seal_id_and_image_mapping.json": "8069120d4ee271939adf096287762a3b83ecfd8f5dcb6f4fa014ae8e18f668d5"}},
    hashes={"data/lipi/src/assets/data/inscriptions.csv": "c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c",
            "data/lipi/src/assets/data/seal_id_and_image_mapping.json": "8069120d4ee271939adf096287762a3b83ecfd8f5dcb6f4fa014ae8e18f668d5"},
    evidence=["knowledge/provenance/SOURCES.md", f"{RUN}/summary.json", f"{RUN}/field-coverage-overall.csv"],
    questions=["Q-1004", "Q-1013", "Q-1028", "Q-1030"],
    notes="Interpretive columns (sanskrit, translation, notes) are excluded from the project's observational extraction.",
)
add(
    id="mayig",
    title="Mayig indus-valley-script-corpus (Mohenjo-daro unicorn seals)",
    kind="corpus-export",
    local_paths=["data/mayig/"],
    version={"commit": "ad2f1e218a34b8c33c57de0d6cb8d99272765bbb"},
    size={"faces": 179, "lines": 186, "tokens": 1003, "schema_classes": 396},
    identifiers=["CISI reference with side (M-1A)"],
    metadata_fields=["site", "description", "object_type", "line", "per-sign damage and uncertainty", "sign features"],
    rights={"status": "explicit-license", "licence": "MIT (Michael Carlson 2024)",
            "detail": "Photographs used for annotation have separate rights."},
    fetch={"method": "git", "url": "https://github.com/mayig/indus-valley-script-corpus",
           "commit": "ad2f1e218a34b8c33c57de0d6cb8d99272765bbb",
           "verify": {"LICENSE": "c8fde8f47c2a3e5c5ce4c2e42a836bf04607298e692f08f4af3d25fcb92688b6",
                      "corpus/m001_m099/m001.json": "11031b52f64a9ecba5594fc14c109613357ad22ffaa10800dbbae1f8bc15790f"}},
    hashes={"data/mayig/LICENSE": "c8fde8f47c2a3e5c5ce4c2e42a836bf04607298e692f08f4af3d25fcb92688b6",
            "data/mayig/corpus/m001_m099/m001.json": "11031b52f64a9ecba5594fc14c109613357ad22ffaa10800dbbae1f8bc15790f"},
    evidence=["knowledge/provenance/SOURCES.md", "LICENSES/Mayig-MIT.md"],
)
add(
    id="indus-website",
    title="Earlier Indus website export (yajnadevam/indus-website)",
    kind="corpus-export",
    local_paths=["data/indus_website/"],
    version={"commit": "2434249618b1e74de3f26d28b90dfde093c3dd94"},
    size={"records": 2543, "tokens": 11135, "records_with_museum_value": 299},
    identifiers=["SEALID", "CISI"],
    metadata_fields=["SITEID", "MATERIAL", "CISI", "MUSEUM", "WIDTH", "HEIGHT", "THICKNESS"],
    rights={"status": "explicit-license", "licence": "GPL-3.0 (repository)",
            "detail": "Coverage of imported corpus and image assets by the repository licence is unresolved."},
    fetch={"method": "git", "url": "https://github.com/yajnadevam/indus-website",
           "commit": "2434249618b1e74de3f26d28b90dfde093c3dd94",
           "verify": {"population-script.sql": "04d5a2c0f239458e4151d006b10c6ace638ee63f961083cf0331fd23309d2a24"}},
    hashes={"data/indus_website/population-script.sql": "04d5a2c0f239458e4151d006b10c6ace638ee63f961083cf0331fd23309d2a24"},
    evidence=["knowledge/provenance/SOURCES.md", f"{RUN}/cross-source.json"],
    notes="The SQL contains destructive statements; parse it as text.",
)
add(
    id="normalized-derivatives",
    title="Project normalized corpus files (data/normalized/)",
    kind="project-derivative",
    status="project-output",
    local_paths=["data/normalized/"],
    size={"files": 20, "lipi_faces": 5680, "lipi_parts": 5804, "mayig_faces": 179, "website_records": 2543},
    identifiers=["record_id", "object_family_id", "source_cisi"],
    metadata_fields=["Lipi metadata dict (33 keys)", "direction", "completeness flags", "single-line flag"],
    rights={"status": "mixed-assets", "licence": None,
            "detail": "Our transformations of unresolved-rights and GPL/MIT sources; record-level files stay local."},
    fetch=rebuild("Reacquire Lipi, Mayig and the website export at their pinned commits with --fetch.",
                  "Run research/corpus/normalize_lipi.py, normalize_mayig.py and normalize_indus_website.py with input paths pointed at the fresh clones; the scripts call git rev-parse, so run them on a real clone.",
                  "Compare outputs with the SHA256 values in knowledge/provenance/SOURCES.md before use."),
    hashes={"data/normalized/lipi_observed_faces.jsonl": "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db",
            "data/normalized/lipi_clean_rtl_singleline.jsonl": "9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8",
            "data/normalized/mayig_faces.jsonl": "033b8e40d4fdfa1f4a2c51390c8fd5f95eae35c6c835b47776c969ab947a19b7"},
    evidence=["knowledge/provenance/SOURCES.md", "research/corpus/normalize_lipi.py"],
)

# ---------------------------------------------------------------------------
# Printed corpora and concordances
# ---------------------------------------------------------------------------
add(
    id="helsinki-1979",
    title="Koskenniemi and Parpola 1979, Corpus of Texts in the Indus Script",
    kind="printed-corpus",
    local_paths=["research/corpus/primary/koskenniemi_parpola1979.pdf"],
    size={"pdf_pages": 180, "bytes": 16935355},
    identifiers=["1979 text numbers", "Finnish sign codes"],
    metadata_fields=["site and object reference per text", "drawn sign sequences"],
    rights={"status": "explicit-license", "licence": "CC BY 4.0 (official Helsinki entry)"},
    fetch=manual("Open http://hdl.handle.net/10138/342677 in a browser and download the PDF through HELDA; direct requests returned 403.",
                 "Save under a new data/raw/<date>-fetch/helsinki-1979/ directory and compare SHA256 7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27."),
    hashes={"research/corpus/primary/koskenniemi_parpola1979.pdf": "7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27"},
    evidence=["knowledge/provenance/SOURCES.md", "research/corpus/primary/koskenniemi_parpola1979_provenance.json"],
)
add(
    id="helsinki-1980",
    title="Koskenniemi and Parpola 1980, Documentation and Duplicates of the Texts in the Indus Script",
    kind="printed-corpus",
    local_paths=["research/corpus/primary/koskenniemi_parpola1980.pdf"],
    size={"pdf_pages": 98, "bytes": 8143483},
    identifiers=["1979 text numbers", "duplicate groups"],
    metadata_fields=["documentation of sources and duplicates"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=http("https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf", "koskenniemi_parpola1980.pdf",
               "0ced4102dc6197246df6c84e4b730ed380f41085a4a1ea8dd8a6459332da37d1", 8143483),
    hashes={"research/corpus/primary/koskenniemi_parpola1980.pdf": "0ced4102dc6197246df6c84e4b730ed380f41085a4a1ea8dd8a6459332da37d1"},
    evidence=["knowledge/provenance/SOURCES.md"],
)
add(
    id="helsinki-1982",
    title="Koskenniemi and Parpola 1982, A Concordance to the Texts in the Indus Script",
    kind="printed-concordance",
    local_paths=["research/corpus/primary/koskenniemi_parpola1982.pdf"],
    size={"pdf_pages": 201, "bytes": 16767043},
    identifiers=["1979 text numbers", "sign codes"],
    metadata_fields=["concordance lines (image-only PDF)"],
    rights={"status": "explicit-license", "licence": "CC BY 4.0 (official Helsinki entry)"},
    fetch=http("https://tuhat.helsinki.fi/ws/portalfiles/portal/209717802/indus_concordance_1982.pdf", "koskenniemi_parpola1982.pdf",
               "07d24564cd3abf23620a3cd9d417c9931c9d3e1aafb204d7c4fd49b4022d043c", 16767043),
    hashes={"research/corpus/primary/koskenniemi_parpola1982.pdf": "07d24564cd3abf23620a3cd9d417c9931c9d3e1aafb204d7c4fd49b4022d043c"},
    evidence=["knowledge/provenance/SOURCES.md"],
)
add(
    id="chart-atlas",
    title="687-cell Helsinki 1979 chart atlas and reviewed chart reference v2.1",
    kind="project-derivative",
    status="project-output",
    location="tracked",
    local_paths=["output/chart_atlas/index.html", "research/chart_reference/manual_numeric_reference.json"],
    size={"chart_cells": 687, "medium_confidence_cells": 33},
    identifiers=["(PDF page, column, row)", "upper class", "lower Finnish code"],
    metadata_fields=["crop rectangle", "class", "code", "confidence"],
    rights={"status": "explicit-license", "licence": "CC BY 4.0 (derived from the 1979 edition)"},
    fetch=rebuild("Tracked in Git; package P (experiments/2026-10-08-chart-reference-audit/) holds the v2.1 corrections."),
    evidence=["experiments/2026-10-08-chart-reference-audit/PROTOCOL.md", "THIRD_PARTY_NOTICES.md"],
)
add(
    id="helsinki-1979-transcription-proposals",
    title="Package M v3 machine transcription proposals for the 1979 corpus (quarantined)",
    kind="project-derivative",
    status="project-output",
    location="local-only",
    local_paths=["experiments/2026-10-07-helsinki1979-digitization/repair/"],
    size={"physical_line_proposals": 11769, "numbered_occurrences": 11702, "unit_windows": 54384, "released_rows": 0},
    identifiers=["1979 page, physical line and occurrence keys"],
    metadata_fields=["crop coordinates", "unit windows", "candidate codes"],
    rights={"status": "explicit-license", "licence": "CC BY 4.0 parent edition; proposals are our modification"},
    fetch=manual("The large JSONL files are listed in experiments/2026-10-07-helsinki1979-digitization/HOST-FILES.txt and backed up to the private Hugging Face dataset ksaw008/indus-research-data; restore with an authenticated owner session."),
    evidence=["experiments/2026-10-07-helsinki1979-digitization/README.md"],
    notes="All proposals fail the frozen release criteria and remain quarantined; none is a verified transcription.",
)
add(
    id="cisi-1",
    title="Joshi and Parpola 1987, Corpus of Indus Seals and Inscriptions. 1. Collections in India",
    kind="photographic-corpus",
    local_paths=["research/literature/sources/joshi_parpola_1987_cisi1.pdf"],
    size={"pdf_pages": 862, "book_pages_scanned": 431, "bytes": 31508998},
    identifiers=["CISI references (M-, H-, L-, K-, B- ...)", "museum and excavation numbers in the basic-data section"],
    metadata_fields=["photographs of each side and impression", "basic data: museum number, excavation number, findspot, material, dimensions"],
    rights={"status": "rights-unverified", "licence": None,
            "detail": "Copyright 1987 Suomalainen Tiedeakatemia; photographs belong to the holding institutions."},
    fetch=http("https://ignca.gov.in/Asi_data/76884.pdf", "joshi_parpola_1987_cisi1.pdf",
               "47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d", 31508998),
    hashes={"research/literature/sources/joshi_parpola_1987_cisi1.pdf": "47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d"},
    evidence=["knowledge/provenance/SOURCES.md", "research/literature/cisi1_counting_and_errata.md",
              "experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv"],
    questions=["Q-1001", "Q-1005", "Q-1007"],
    notes="The scan repeats one 431-page book scan at PDF offset 431. Several other local copies exist with the same or an alternate hash.",
)
add(
    id="cisi-2",
    title="Shah and Parpola 1991, Corpus of Indus Seals and Inscriptions. 2. Collections in Pakistan",
    kind="photographic-corpus",
    local_paths=["data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf"],
    size={"bytes": 60132087},
    identifiers=["CISI references (M-621 to M-1659, H-266 to H-1019 and other sites)", "museum and excavation numbers"],
    metadata_fields=["photographs", "basic data: museum number, excavation number, findspot, material, dimensions"],
    rights={"status": "rights-unverified", "licence": None,
            "detail": "Copyright 1991 Finnish Academy for the volume; photographs belong to the object owners."},
    fetch=http("https://archive.org/download/TheIndusScript.TextConcordanceAndTablesIravathanMahadevan/Corpus%20of%20Indus%20Seals%20and%20Inscriptions.%20Collections%20in%20Pakistan_text.pdf",
               "cisi2-archive.pdf", "5258071b08898ce4bb9e9a5ee675d182fbe4c1eb22ed2822f6838fdbd5f7e54b", 60132087),
    hashes={"data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf": "5258071b08898ce4bb9e9a5ee675d182fbe4c1eb22ed2822f6838fdbd5f7e54b"},
    evidence=["experiments/2026-10-06-evidence-census/synthesis/sources.json", "experiments/2026-10-06-evidence-census/synthesis/catalogue-coverage.csv"],
    questions=["Q-1001", "Q-1006", "Q-1007", "Q-1027"],
)
add(
    id="cisi-3-1-harappa-introduction",
    title="Kenoyer and Meadow 2010, Inscribed Objects from Harappa Excavations 1986-2007 (CISI 3.1 introductory chapter)",
    kind="photographic-corpus",
    status="partly-held",
    local_paths=["research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf",
                 "data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/kenoyer-meadow2010-published.pdf"],
    size={"excerpt_pages": 15, "bytes": 276900},
    identifiers=["HARP year/item numbers", "lot numbers", "CISI H-numbers"],
    metadata_fields=["excavation identifiers", "context and deposit qualifications"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=manual("Download https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf through a browser (direct requests returned 403).",
                 "The full CISI 3.1 volume is a separate acquisition; see cisi-3-1."),
    hashes={"research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf": "7a8fea92fbc7a8810ad9d47e5740a83e4896bc46facd1ec6eb7f51c329ecf2d9",
            "data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/kenoyer-meadow2010-published.pdf": "cf2316a49e6e0b85c28e55cecebfef97935fa52b3fc33c0edf696a0b7285f436"},
    evidence=["knowledge/provenance/SOURCES.md", "experiments/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/sources.json"],
)
add(
    id="cisi-3-3-excerpt",
    title="CISI 3.3 (2022) Indo-Iranian Borderlands: 40-page author excerpt (Desset)",
    kind="photographic-corpus",
    status="partly-held",
    local_paths=["data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/cisi33-excerpt2022.pdf"],
    size={"pdf_pages": 40, "bytes": 13875708},
    identifiers=["CISI 3.3 references"],
    metadata_fields=["contents, preface, essay and bibliography; no catalogue plates"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=http("https://orbi.uliege.be/bitstream/2268/333796/1/Desset%20F%202022%20in%20CISI%203.3%201763.pdf", "cisi33-excerpt2022.pdf",
               "cb832f6fe9525d26fba4fc2e74427741320d38b7becfd355da754051f9ca9e08", 13875708),
    hashes={"data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/cisi33-excerpt2022.pdf": "cb832f6fe9525d26fba4fc2e74427741320d38b7becfd355da754051f9ca9e08"},
    evidence=["experiments/2026-10-06-evidence-census/synthesis/sources.json"],
    questions=["Q-1010"],
)
add(
    id="mahadevan-1977",
    title="Mahadevan 1977, The Indus Script: Texts, Concordance and Tables (MASI 77)",
    kind="printed-concordance",
    local_paths=["data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/mahadevan1977-full.pdf"],
    size={"bytes": 36288883, "selected_objects": 2906, "card_catalogue_objects": 3455},
    identifiers=["M77 text numbers", "site and object references"],
    metadata_fields=["site", "object type", "text", "concordance", "site table"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=http("https://archive.org/download/TheIndusScript.TextConcordanceAndTablesIravathanMahadevan/The%20Indus%20Script.%20Text%2C%20Concordance%20and%20Tables%20-Iravathan%20Mahadevan.pdf",
               "mahadevan1977-full.pdf", "afa32284c375b4f501a4c38efba7806b64765f041db07b22ea2e56f7205f0f67", 36288883),
    hashes={"data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/mahadevan1977-full.pdf": "afa32284c375b4f501a4c38efba7806b64765f041db07b22ea2e56f7205f0f67"},
    evidence=["experiments/2026-10-06-evidence-census/synthesis/sources.json", "experiments/2026-10-06-evidence-census/synthesis/REPORT.md"],
    questions=["Q-1012", "Q-1013"],
)
add(
    id="fuls-2010-help",
    title="Fuls 2010, help for the online Indus database (ICIT), with a labelled example",
    kind="database-documentation",
    local_paths=["research/corpus/primary/fuls2010_help.pdf"],
    size={"pdf_pages": 16, "bytes": 827406},
    identifiers=["ICIT text numbers"],
    metadata_fields=["field definitions and display order"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=http("https://www.epigraphica.de/indus/help_onlinedatabase.pdf", "fuls2010_help.pdf",
               "800c650a88743eb53b9816fb42fdec517c4c5c5172059f69899c73d609fe6556", 827406),
    hashes={"research/corpus/primary/fuls2010_help.pdf": "800c650a88743eb53b9816fb42fdec517c4c5c5172059f69899c73d609fe6556"},
    evidence=["knowledge/provenance/SOURCES.md"],
)

# ---------------------------------------------------------------------------
# Project registers, ledgers and releases
# ---------------------------------------------------------------------------
add(
    id="evidence-census",
    title="October 6-7 evidence census: site, publication, collection, dataset and catalogue-coverage registers",
    kind="project-register",
    status="project-output",
    location="tracked",
    local_paths=["experiments/2026-10-06-evidence-census/"],
    size={"site_or_provenance_entities": 115, "catalogue_entries_measured": 3620, "museum_original_records": 114,
          "museum_confirmed_joins_lower_bound": 68, "bibliography_entries_synthesis": 21},
    identifiers=["site entity ids", "CISI ranges", "museum accession numbers"],
    metadata_fields=["site counts", "catalogue coverage", "museum field completeness"],
    rights={"status": "mixed-assets", "licence": None,
            "detail": "Registers and aggregates are project work; raw museum responses and source scans stay local."},
    fetch=rebuild("Tracked in Git. Raw museum records and scans are under data/raw/2026-10-06-evidence-census/ (local-only)."),
    evidence=["experiments/2026-10-06-evidence-census/synthesis/REPORT.md", "experiments/2026-10-06-evidence-census/synthesis/join-summary.json"],
    questions=["Q-1007", "Q-1018", "Q-1019"],
)
add(
    id="museum-records-2026-10-07",
    title="Saved museum collection records from the census focused pass (New Delhi, Kolkata, British Museum, Penn, Louvre, Met)",
    kind="museum-records",
    status="partly-held",
    local_paths=["data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/"],
    size={"original_object_records": 114, "confirmed_joins": 68, "unresolved": 46},
    identifiers=["museum accession numbers", "CISI concordance references"],
    metadata_fields=["accession", "material", "dimensions", "date label", "images", "bibliography (13 records)"],
    rights={"status": "mixed-assets", "licence": None,
            "detail": "Met eligible assets CC0, Penn downloadable data CC BY 4.0 and Louvre record data Etalab Open Licence 2.0 were recorded as policy routes by the census; image permissions differ by institution."},
    fetch=rebuild("Rerun the census collection scripts in experiments/2026-10-06-evidence-census/collections-and-datasets/ into a new raw directory."),
    evidence=["experiments/2026-10-06-evidence-census/synthesis/join-summary.json", "experiments/2026-10-06-evidence-census/synthesis/field-completeness.csv"],
    questions=["Q-1018", "Q-1019"],
)
add(
    id="object-ledger-pilot",
    title="Object ledger pilot: two 200-carrier ledgers with identities, context, museum joins and missingness reasons",
    kind="project-register",
    status="project-output",
    location="tracked",
    local_paths=["experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/"],
    size={"carriers_per_selection": 200, "assertions_original": 6991, "assertions_hash_ordered": 7004,
          "museum_joins_original": 26, "museum_joins_hash_ordered": 25},
    identifiers=["carrier id", "source-qualified aliases"],
    metadata_fields=["identity", "context", "dimensions", "dating interval", "museum join", "missingness reason"],
    rights={"status": "mixed-assets", "licence": None,
            "detail": "Tracked ledgers exclude transcription payloads and images; full registers stay in data/."},
    fetch=rebuild("Follow experiments/2026-10-07-object-ledger/README.md; required local inputs are listed in its review-response local-inputs.json."),
    evidence=["experiments/2026-10-07-object-ledger/README.md"],
    questions=["Q-1030"],
)
add(
    id="hf-reference-benchmarks",
    title="Hugging Face dataset ksaw008/indus-reference-benchmarks 0.3.1 (chart, row benchmarks, census tables)",
    kind="project-release",
    status="project-output",
    location="hf-private",
    local_paths=["experiments/2026-10-08-hf-public-release/release/"],
    size={"configurations": 23, "rows": 3308, "images": 1142, "files": 137, "bytes": 25292479},
    identifiers=["chart cell ids", "benchmark row ids", "census ids"],
    metadata_fields=["chart reference", "benchmark rows and readings", "evidence census tables", "metrology summaries"],
    rights={"status": "mixed-assets", "licence": "CC BY 4.0 edition content; CC0 1.0 project data and documentation; Unlicense code"},
    fetch=manual("The release folder is tracked under experiments/2026-10-08-hf-public-release/release/.",
                 "The hosted dataset returned HTTP 401 to an anonymous API request on 12 October 2026, so it is not public; visibility is an owner decision (experiments/2026-10-08-hf-public-release/RELEASE-CHECKLIST.md)."),
    evidence=["experiments/2026-10-08-hf-public-release/README.md", "experiments/2026-10-12-data-inventory/sources.json"],
)
add(
    id="hf-research-data",
    title="Hugging Face private backup ksaw008/indus-research-data (package A outputs, large frozen files)",
    kind="project-backup",
    status="project-output",
    location="hf-private",
    size={"package_A_files": 1034, "package_A_bytes_approx": 3090000000},
    identifiers=["repository paths"],
    metadata_fields=[],
    rights={"status": "mixed-assets", "licence": None, "detail": "Private; not a publication."},
    fetch=manual("Log in with python -m huggingface_hub.cli.hf auth login as the owner.",
                 "Run python experiments/2026-10-06-research-program/hf_host.py restore --repo ksaw008/indus-research-data; files are verified against experiments/2026-10-06-research-program/hf-hosting-manifest.json."),
    evidence=["REPRODUCING.md", "experiments/2026-10-06-research-program/hf-hosting-manifest.json"],
)
add(
    id="lothal-sealing-frame",
    title="Lothal sealing frame: Frenez and Tosi 2005 table coding with independent review",
    kind="source-frame",
    local_paths=["data/six-hour/lothal/"],
    size={"sealings": 93, "joined_objects": 68, "joined_faces": 86},
    identifiers=["CISI L-numbers", "Frenez and Tosi table rows"],
    metadata_fields=["impression counts", "attachment category", "context"],
    rights={"status": "mixed-assets", "licence": "Article reported CC BY 4.0 on Zenodo by the census reviewer; images need asset review"},
    fetch=http("https://zenodo.org/records/5514283", "zenodo-record.html", steps=["Download the PDF from the Zenodo record; the table coding is in experiments/2026-10-02-six-hour/lothal-physical-use/."]),
    evidence=["experiments/2026-10-02-six-hour/lothal-physical-use/README.md"],
    questions=["Q-1015"],
)
add(
    id="harappa-short-record-frame",
    title="Harappa tablets H2218-H2239 source frame (22 objects, 66 faces)",
    kind="source-frame",
    status="project-output",
    location="tracked",
    local_paths=["experiments/2026-10-02-six-hour/harappa-object-frame/"],
    size={"objects": 22, "faces": 66},
    identifiers=["CISI H-numbers", "HARP registrations"],
    metadata_fields=["face counts", "deposition keys", "engraver groups"],
    rights={"status": "mixed-assets", "licence": None},
    fetch=rebuild("Tracked frame; source PDFs are local-only (Meadow and Kenoyer 2000; Kenoyer and Meadow 2010)."),
    evidence=["experiments/2026-10-02-six-hour/harappa-object-frame/README.md"],
)
add(
    id="kanmer-frame",
    title="Kanmer excavation, scanner and source-history witnesses",
    kind="source-frame",
    status="partly-held",
    local_paths=["experiments/2026-10-02-six-hour/kanmer-physical-use/"],
    identifiers=["Kanmer registration numbers"],
    metadata_fields=["sealing contexts", "physical-use observations"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=manual("See experiments/2026-10-02-six-hour/kanmer-physical-use/SOURCES.md; final report pages 484-490, 749-760 and 827-832 and the accompanying disc are not held."),
    evidence=["experiments/2026-10-02-six-hour/kanmer-physical-use/SOURCES.md"],
)
add(
    id="tn-graffiti",
    title="Tamil Nadu graffiti portal snapshot (tngraffiti.in); Rajan and Sivanantham 2026, Inscribed Potsherds of Tamil Nadu: Graffiti and Tamili, vols I-II; Rajan and Sivanantham 2025, Indus signs and graffiti marks of Tamil Nadu: a morphological study",
    kind="comparative-corpus",
    status="partly-held",
    local_paths=["data/raw/2026-10-02-connections-and-priority/south-india/"],
    size={"portal_reads": 48, "base_forms": 42, "variants": 546, "composites": 1522, "summed_occurrences": 9345,
          "portal_stated_potsherds": 15184, "portal_stated_sites": 140, "portal_stated_recognised_graffiti": 9486},
    identifiers=["government sign ids", "RMRL internal numbers", "specimen registrations"],
    metadata_fields=["site", "habitation/burial context", "ware", "depth (aggregate margins)"],
    rights={"status": "rights-unverified", "licence": None},
    fetch=manual("Rerun experiments/2026-10-02-connections-and-priority/south-india/acquire_portal.py into a new raw directory.",
                 "Download the two volumes from tamildigitallibrary.in (records 062969 and 062968)."),
    hashes={"data/raw/2026-10-02-connections-and-priority/south-india/inscribed-potsherds-vol1-2026.pdf": "d1dbfefeccd41dc05fca9da9ec8bbaacaf250322201b9d3b0b15b84fe48a78a6",
            "data/raw/2026-10-02-connections-and-priority/south-india/inscribed-potsherds-vol2-2026.pdf": "4e845dd57bd1ef2433f30b74afd7cb6427e5acae2d6fe631a6510dd6b97d28dc",
            "data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf": "f42670932eb8328494d61de1d4652534ac94f4c3ab82684f8c3fff1c91954c52"},
    evidence=["experiments/2026-10-02-connections-and-priority/south-india/REPORT-reviewed-v1.md"],
    questions=["Q-1023"],
    notes="Graffiti marks on South Indian pottery; a comparative collection, not Indus inscribed objects.",
)

# ---------------------------------------------------------------------------
# Excavation reports and site publications held locally (selection)
# ---------------------------------------------------------------------------
REPORTS = [
    ("marshall-1931", "Marshall (ed.) 1931, Mohenjo-daro and the Indus Civilization (3 vols; seal tabulation in vol. II pp. 402-405)",
     "research/literature/sources/marshall_1931_govscan_14985.pdf", "163dd20937256470e3e652c5dcc0c8061c28d57bf75d0c0ae7ee1d42ef5d4600"),
    ("vats-1940-text", "Vats 1940, Excavations at Harappa (text volume)",
     "research/literature/sources/vats_1940_govscan_18220.pdf", "022fc5761c16f63c36bb83429a4ecf1cd23ff33b0b13d12f1c0445962f0614ec"),
    ("vats-1940-plates", "Vats 1940, Excavations at Harappa (plates volume)",
     "research/literature/sources/vats_1940_govscan_9842.pdf", "1855dc750a070c570eaecb78c8217dd350ad7e559a65898a57242545fb54a442"),
    ("mackay-1943", "Mackay 1943, Chanhu-daro Excavations 1935-36",
     "research/literature/sources/mackay_1943_chandaro.pdf", "93a76551ab048c6a455b4239730dce718b96cd5b3747852b025858d86b253ef0"),
    ("bisht-2015", "Dholavira Report (preliminary, Jan 2015), Internet Archive upload of 938 pages without a title page, used as a witness for Bisht 2015, Excavations at Dholavira (1989-90 to 2004-05); identity with the ASI publication unconfirmed",
     "data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf", "f1c23210b95c17ea68650522ca2b7f7ecd7503078d9dede6fbfec6bfe4fad374"),
    ("kalibangan-part-ii", "Lal, Joshi, Sharma, Madhu Bala and Ramachandran, Excavations at Kalibangan: The Harappans (1960-69), Part II (ASI PDF)",
     "data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/kalibangan_report2020.pdf", "47d861daedd595f4da4b75e1cd65594a34c2c46e4a0a3bc219c83fd3fbada56c"),
    ("rangpur-1963", "Rao 1963, Excavation at Rangpur and other explorations in Gujarat (Ancient India 18-19)",
     "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/RANGPUR1963.pdf", "92c996bf452c3f35721d893f87d0b63a071c71b531f4164cd744b6af983ec39c"),
    ("frenez-tosi-2005", "Frenez and Tosi 2005, The Lothal Sealings",
     "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/LOTHAL2005.pdf", "b0694314c9b91321dc85e90a9c66c1cf410fe46387efd0e2dffeb747fa7ddcd3"),
    ("nuhato-2018", "Excavation of Nuhato Site of Indus Valley Civilization (2018 report)",
     "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/NUHATO2018.pdf", "2fe2d677391a7525b609f1edefb88924da6ec37a05e8761b2362f9986913bc5e"),
    ("shikarpur-2009", "Shikarpur excavation report 2008-2009 (harappa.com PDF)",
     "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/SHIKARPUR2009.pdf", "b19286e37be4e17e172d44aaeb4c56bda13f8a77c4c9eec25f227f120f4ddc0f"),
    ("jansen-urban-1987", "Jansen and Urban 1987, Interim Reports vol. 2 (Mohenjo-daro)",
     "research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf", "e488536488de84426de6391764a8364275aa557613bc0efb82ff385e561e8c6f"),
    ("gadd-1932", "Gadd 1932, Seals of ancient Indian style found at Ur",
     "data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/gadd1932.pdf", "c16c2c3900f7cecc35ca843637087b0bdaf3fbf42b5100bcce0bdaa77803d881"),
    ("laursen-2010", "Laursen 2010, The westward transmission of Indus Valley sealing technology",
     "data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/laursen2010.pdf", "b28d81501f573fcf218d863092687caf47199b077969c14af965a6a2ac31ba57"),
    ("meadow-kenoyer-2000", "Meadow and Kenoyer 2000, tiny steatite seals from Harappa",
     "research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf", "967ebcb058e5611de4089facba852adac418108adfc36bf793d0588ba0d8b751"),
    ("parpola-2011", "Parpola 2011, unicorn study (author PDF)",
     "research/corpus/primary/parpola2011_unicorn.pdf", "a10b375beea210a5b2b8ae3a5930ecdf1c0e64a9d8b52b7b84be14a591fec468"),
    ("airavati-2008", "Airavati 2008 (Wells classification chapter printed pp. 275-288)",
     "research/literature/sources/airavati_2008.pdf", "2d30c6dcc426925b03da8e63dd7b861148c092f93e111f72ec9479c744f20503"),
    ("ascalone-2022", "Ascalone 2022 weight catalogue (source of the 2,058-entry metrology parse)",
     "data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf", "39e9c43c61eae694ff0d10cfb37f47b3ca7f12c42f25d2db12ec055a5d3e7efb"),
]
REPORT_QUESTIONS = {"marshall-1931": ["Q-1003"], "vats-1940-text": ["Q-1022"], "bisht-2015": ["Q-1014"],
                    "kalibangan-part-ii": ["Q-1016"], "frenez-tosi-2005": ["Q-1015"], "gadd-1932": ["Q-1024"],
                    "laursen-2010": ["Q-1024"], "mackay-1943": ["Q-1018"]}
for rid, title, path, digest in REPORTS:
    add(id=rid, title=title, kind="excavation-report-or-study", local_paths=[path],
        rights={"status": "rights-unverified", "licence": None},
        fetch=manual("See the acquisition record cited in evidence; most were public government or author scans downloaded unchanged."),
        hashes={path: digest},
        evidence=["experiments/2026-10-12-data-inventory/run-2026-10-12/holdings/holdings-summary.json"],
        questions=REPORT_QUESTIONS.get(rid, []))

for rec in S:
    if rec["id"] == "bisht-2015":
        rec["fetch"] = http("https://archive.org/download/dholavirareportpreliminaryjan2015_860_K/Dholavira%20Report%20%28preliminary%2C%20Jan%202015%29.pdf",
                            "dholavira-report-preliminary-jan-2015.pdf",
                            "f1c23210b95c17ea68650522ca2b7f7ecd7503078d9dede6fbfec6bfe4fad374", 127352282)
        rec["evidence"].append("experiments/2026-10-12-data-inventory/sources.json")

# ---------------------------------------------------------------------------
# Comparison corpora and other data
# ---------------------------------------------------------------------------
add(id="sproat-2014-corpora", title="Sproat 2014 non-linguistic symbol corpora (author archive)", kind="comparative-corpus",
    local_paths=["research/literature/sources/sproat_2014_corpora/"],
    size={"weather_forecasts": 10142, "totem_strings": 180},
    rights={"status": "explicit-license", "licence": "Apache 2.0 (notices in XML)"},
    fetch=http("https://richardsproat.com/data/non-linguistic-symbols/corpora.zip", "corpora.zip",
               "fb50ff5acb5221ba75e134cc7a36619e1d990b5680ad8681bcde5c447b6b8f73"),
    evidence=["knowledge/provenance/SOURCES.md"])
add(id="bronze-age-editions", title="ORACC epsd2/admin/ur3, obabat/atletters and rimanum JSON; AES and AED-TEI Egyptian corpora; LiBER Linear B catalogue and documents",
    kind="comparative-corpus", local_paths=["data/raw/2026-10-12-bronze-age-comparison/acquisition/"],
    size={"ur3_entries": 80181, "akkadian_letters": 121, "rimanum_entries": 378, "liber_catalogue_entries": 5638, "liber_documents_acquired": 512},
    rights={"status": "mixed-assets", "licence": "ORACC JSON CC0; AES and AED-TEI CC BY-SA 4.0; LiBER limited scholarly reuse"},
    fetch=manual("Rerun experiments/2026-10-12-bronze-age-comparison/acquire.py following its acquisition plans into a new raw directory."),
    evidence=["experiments/2026-10-12-bronze-age-comparison/SOURCES.md"])
add(id="language-corpora-2026-10-12", title="Digital Corpus of Sanskrit texts, Monier-Williams (Cologne csl-orig), Perseus Latin texts and a Sangam Tamil table",
    kind="comparative-corpus", local_paths=["data/raw/2026-10-12-decipherment-claim-tests/"],
    rights={"status": "mixed-assets", "licence": None, "detail": "Licences recorded in the published-claim-tests package; not re-verified here."},
    fetch=manual("See experiments/2026-10-12-published-claim-tests/README.md for commits and routes."),
    evidence=["experiments/2026-10-12-published-claim-tests/README.md"])
add(id="khipu-puruchuco", title="Puruchuco khipu repository and database snapshot (numerical control)", kind="comparative-corpus",
    local_paths=["data/six-hour/khipu/"],
    rights={"status": "mixed-assets", "licence": "Repository code and docs MIT; database licence unresolved"},
    fetch=manual("See experiments/2026-10-02-six-hour/khipu-control/acquisition.json."),
    evidence=["experiments/2026-10-02-six-hour/khipu-control/SOURCE_AUDIT.md"])
add(id="weights-metrology", title="Weight metrology parse: 2,058 catalogue entries (938 Greater Indus) and Gulf supplement",
    kind="project-derivative", status="project-output", location="tracked",
    local_paths=["experiments/2026-10-06-weight-metrology/extraction-v6.json"],
    size={"entries": 2058, "greater_indus": 938},
    rights={"status": "mixed-assets", "licence": None, "detail": "Parsed from Ascalone 2022; source PDF local-only."},
    fetch=rebuild("Follow experiments/2026-10-06-weight-metrology/README.md."),
    evidence=["experiments/2026-10-06-weight-metrology/README.md"])
add(id="settlement-registers", title="Settlement prospection source register, survey regions and satellite-prospection inputs (Copernicus DEM, ESA WorldCover, MAHSA queries)",
    kind="site-register", status="partly-held", local_paths=["data/raw/2026-10-11-settlement-prospection/", "data/raw/2026-10-12-satellite-prospection/"],
    size={"source_records": 72, "local_witnesses": 50, "editorial_regions": 21},
    rights={"status": "mixed-assets", "licence": "WorldCover CC BY 4.0; Copernicus DEM per ESA annex; MAHSA terms not obtained"},
    fetch=manual("See experiments/2026-10-11-settlement-prospection/README.md and experiments/2026-10-12-satellite-prospection/."),
    evidence=["experiments/2026-10-11-settlement-prospection/README.md"])
add(id="local-literature", title="Local literature collection: papers, excavation reports and scans acquired by earlier packages",
    kind="literature-collection", local_paths=["research/literature/sources/", "research/corpus/primary/", "data/raw/"],
    size={"pdf_files": 365, "distinct_pdfs": 299, "distinct_pdf_bytes": 2708409474},
    rights={"status": "mixed-assets", "licence": None, "detail": "Each witness keeps its own rights record; none is redistributed."},
    fetch=manual("Each acquisition record names its route; data/raw/2026-10-12-data-inventory/holdings-v1/pdf-hashes.jsonl lists every local PDF with its hash."),
    evidence=[f"{RUN}/holdings/holdings-summary.json", f"{RUN}/holdings/literature-harvest-summary.json"],
    questions=["Q-1029"])

# Not-held sources are appended from not_held.py so that web checks can update them.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from not_held import NOT_HELD  # noqa: E402

for rec in NOT_HELD:
    add(**rec)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    problems = []
    ids = set()
    for s in S:
        if s["id"] in ids:
            problems.append(f"duplicate id {s['id']}")
        ids.add(s["id"])
        if s["status"] not in STATUS:
            problems.append(f"{s['id']}: bad status")
        if s["location"] not in LOCATION:
            problems.append(f"{s['id']}: bad location")
        if s.get("rights", {}).get("status") not in RIGHTS:
            problems.append(f"{s['id']}: bad rights status")
        for p in s["local_paths"]:
            if not (ROOT / p).exists():
                problems.append(f"{s['id']}: local path missing {p}")
        for p, digest in s["hashes"].items():
            fp = ROOT / p
            if not fp.exists():
                problems.append(f"{s['id']}: hashed file missing {p}")
            elif sha256(fp) != digest:
                problems.append(f"{s['id']}: hash mismatch {p}")
        for e in s["evidence"]:
            if not (ROOT / e.split("#")[0]).exists():
                problems.append(f"{s['id']}: evidence path missing {e}")
    manifest = {
        "schema_version": 1,
        "updated": "2026-10-12",
        "description": "Every data source the Indus research project holds or knows of, with version, location, size, identifiers, rights and acquisition route. Human-readable account: knowledge/DATA.md. Tool: tools/fetch_data.py.",
        "status_values": STATUS,
        "location_values": LOCATION,
        "rights_status_values": RIGHTS,
        "fetch_methods": {
            "git": "Clone the URL and check out the pinned commit; verify listed file hashes.",
            "http": "Download one public file; verify its SHA256 when recorded.",
            "manual": "Follow the printed steps (browser download, purchase, library, permission request).",
            "rebuild": "Regenerate from tracked code and other manifest sources.",
        },
        "counts": {k: sum(1 for s in S if s["status"] == k) for k in STATUS},
        "sources": S,
    }
    print(json.dumps({"sources": len(S), "counts": manifest["counts"], "problems": problems}, indent=2))
    if not args.check_only:
        OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
