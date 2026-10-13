"""Write manifest-additions.json: proposed new and changed entries for data/MANIFEST.json.

Usage (from the repository root, after the harvest scripts and build_joins.py):
    python experiments/2026-10-13-museum-open-access/write_manifest_additions.py
"""
import json
import csv
from pathlib import Path

PKG = Path(__file__).resolve().parent
R = "data/raw/2026-10-13-museum-open-access/"
P = "experiments/2026-10-13-museum-open-access/"


def main():
    acq = json.loads((PKG / "harvest/acquisition-record.json").read_text(encoding="utf-8"))
    summ = json.loads((PKG / "coverage/summary.json").read_text(encoding="utf-8"))
    coverage = json.loads((PKG / "coverage/museum-coverage.json").read_text(encoding="utf-8"))
    with (PKG / "harvest/summary.csv").open(encoding="utf-8", newline="") as handle:
        harvest = {r["museum"]: r for r in csv.DictReader(handle)}
    penn = acq["key_files"]["penn_collections_csv"]
    ev = [P + "README.md", P + "harvest/summary.csv", P + "joins/join-table.csv", P + "coverage/summary.json",
          P + "REVIEW-CHANGES.md", P + "harvest/review-overrides.json", P + "verification/independent-check.md",
          "experiments/2026-10-13-data-round-1-verification/REPORT.md"]
    entries = [
        {"id": "met-open-access", "change": "update", "status": "partly-held", "location": "tracked",
         "title": "Metropolitan Museum of Art Collection API (v1.1 search, v1 objects): Indus seals 49.40.1-4 and 1984.482",
         "kind": "museum-records", "local_paths": [R + "met/"],
         "tracked_paths": [P + "harvest/met-records.json", P + "harvest/met-queries.csv"],
         "size": {"queries": 20, "object_records_read": 176, "indus_inscribed_originals": 5, "joined": 0},
         "identifiers": ["Met objectID", "accession number"],
         "metadata_fields": ["accessionNumber", "title", "objectName", "culture", "period", "objectDate", "medium",
                             "dimensions", "measurements", "region/subregion", "creditLine", "primaryImage",
                             "additionalImages", "isPublicDomain"],
         "rights": {"status": "explicit-license", "licence": "CC0 for objects with isPublicDomain true",
                    "detail": "All five Indus seals are flagged public domain; image URLs recorded; images kept local for comparison only."},
         "fetch": {"method": "rebuild", "steps": [
             "python experiments/2026-10-13-museum-open-access/harvest_met.py (new cache; about 2 s between requests)"]},
         "evidence": ev, "questions": ["Q-1018", "Q-1019"], "web_checks": ["W17"], "hashes": {}},
        {"id": "cleveland-open-access", "change": "update", "status": "partly-held", "location": "tracked",
         "title": "Cleveland Museum of Art Open Access API: Indus seals 1964.104, 1973.160, 1973.161",
         "kind": "museum-records", "local_paths": [R + "cleveland/"],
         "tracked_paths": [P + "harvest/cleveland-records.json", P + "harvest/cleveland-queries.csv"],
         "size": {"queries": 13, "records_read": 23, "indus_inscribed_originals": 3, "joined": 0},
         "identifiers": ["CMA id", "accession_number"],
         "metadata_fields": ["title", "type", "technique", "measurements", "culture", "creation_date", "provenance",
                             "citations", "images", "share_license_status"],
         "rights": {"status": "explicit-license", "licence": "CC0", "detail": "share_license_status CC0 on all three records"},
         "fetch": {"method": "rebuild", "steps": ["python experiments/2026-10-13-museum-open-access/harvest_cleveland.py"]},
         "evidence": ev, "questions": ["Q-1018"], "web_checks": ["W24"], "hashes": {}},
        {"id": "aic-open-access", "change": "new", "status": "not-held", "location": "external",
         "title": "Art Institute of Chicago API: no Indus object found (13 October 2026)",
         "kind": "museum-records", "local_paths": [R + "aic/"],
         "tracked_paths": [P + "harvest/aic-records.json", P + "harvest/aic-queries.csv"],
         "size": {"queries": 13, "indus_objects": 0},
         "rights": {"status": "explicit-license", "licence": "API data CC0 except the description field (CC BY 4.0)",
                    "detail": "Stated in https://api.artic.edu/docs/ (saved 13 October)"},
         "fetch": {"method": "rebuild", "steps": ["python experiments/2026-10-13-museum-open-access/harvest_aic.py"]},
         "evidence": ev, "questions": ["Q-1018"], "hashes": {}},
        {"id": "smithsonian-open-access", "change": "new", "status": "not-held", "location": "external",
         "title": "Smithsonian Open Access metadata (bulk bucket s3://smithsonian-open-access): Indus casts only",
         "kind": "museum-records", "local_paths": [R + "smithsonian/"],
         "tracked_paths": [P + "harvest/smithsonian-records.json", P + "harvest/smithsonian-queries.csv"],
         "size": {"bulk_files_scanned": 770, "bytes_scanned": 1204328192, "records_scanned": 539615,
                  "indus_records": 20, "indus_seal_casts": 5, "originals": 0},
         "rights": {"status": "explicit-license", "licence": "CC0",
                    "detail": "The API needs an api.data.gov key and was not used; the public bucket needs none."},
         "fetch": {"method": "rebuild", "steps": [
             "python experiments/2026-10-13-museum-open-access/harvest_smithsonian.py nmnhanthro fsg nmaa",
             "python experiments/2026-10-13-museum-open-access/harvest_smithsonian.py --summarize"]},
         "evidence": ev, "questions": ["Q-1018"], "web_checks": ["W23"], "hashes": {},
         "notes": "Only matching lines are kept locally; per-file SHA256 values are in bulk-files.jsonl."},
        {"id": "penn-collections-data", "change": "update", "status": "held", "location": "local-only",
         "title": "Penn Museum collections data download (full metadata CSV, updated 2026-10-07)",
         "kind": "museum-records", "local_paths": [R + "penn/cache/2be92ad456f8d4de582e22ba.body"],
         "tracked_paths": [P + "harvest/penn-records.json", P + "harvest/penn-queries.csv"],
         "version": {"last_updated": "2026-10-07", "retrieved_utc": penn["retrieved_utc"]},
         "size": {"bytes": penn["bytes"], "rows": 430871, "indus_pattern_rows": 942, "seal_like_indus_rows": 47,
                  "inscribed_originals": 5, "uninscribed_originals": 4, "casts_or_impressions": 38},
         "identifiers": ["identifier (object number)", "Record URL"],
         "metadata_fields": ["objectName", "title", "creditLine", "description", "placeName", "siteName", "culture",
                             "period", "material", "inscriptionMarkLanguage", "dateMade", "earlyDate", "lateDate",
                             "length", "width", "height", "thickness", "weight", "measurementUnit"],
         "rights": {"status": "explicit-license",
                    "licence": "Data CC BY 4.0 (download page); images for non-profit, education or personal use with credit",
                    "detail": "The CSV lacks Other Number and Bibliography; those come from the object pages of the nine originals."},
         "fetch": {"method": "http", "url": penn["url"], "sha256": penn["sha256"], "bytes": penn["bytes"]},
         "hashes": {R + "penn/cache/2be92ad456f8d4de582e22ba.body": penn["sha256"]},
         "evidence": ev, "questions": ["Q-1018"], "web_checks": ["W19"],
         "notes": "The museum replaces the file in place; the hash identifies the 2026-10-07 edition."},
        {"id": "va-collections", "change": "update", "status": "partly-held", "location": "local-only",
         "title": "Victoria and Albert Museum Collections API v2: seal IS.8:1-1951 (CISI M-1727), fragment IS.8A-1951, impression IS.8:2-1951",
         "kind": "museum-records", "local_paths": [R + "vam/"],
         "tracked_paths": [P + "harvest/vam-records.json", P + "harvest/vam-queries.csv"],
         "size": {"queries": int(harvest["Victoria and Albert Museum"]["queries"]),
                  "records_read": int(harvest["Victoria and Albert Museum"]["records_read"]),
                  "reviewed_indus_attributed_records": int(harvest["Victoria and Albert Museum"]["indus_attributed_records"]),
                  "indus_originals": int(harvest["Victoria and Albert Museum"]["inscribed_originals"]),
                  "modern_impressions": int(harvest["Victoria and Albert Museum"]["casts_or_impressions"]),
                  "joined": int(harvest["Victoria and Albert Museum"]["joined_exact_or_confirmed"])},
         "rights": {"status": "rights-unverified",
                    "licence": "V&A websites terms section 9: non-commercial use; API content may not be stored beyond four weeks",
                    "detail": "Delete data/raw/2026-10-13-museum-open-access/vam/ by 2026-11-10; tracked files hold identifiers, flags and joins only."},
         "fetch": {"method": "rebuild", "steps": ["python experiments/2026-10-13-museum-open-access/harvest_vam.py"]},
         "evidence": ev, "questions": ["Q-1018"], "web_checks": ["W28"], "hashes": {}},
        {"id": "british-museum-collection", "change": "update", "status": "not-held", "location": "external",
         "title": "British Museum Collection Online: 27 stamp-seals labelled Indus Valley Civilisation in the 'indus seal' listing",
         "kind": "museum-records", "local_paths": [R + "bm/"], "tracked_paths": [P + "harvest/bm-records.json"],
         "size": {"listing_results": 59, "indus_stamp_seals": 27, "inscription_stated": 7, "cast_sets": 2, "joined": 6},
         "rights": {"status": "mixed-assets", "licence": "CC BY-NC-SA 4.0 only for content marked with the CC logo",
                    "detail": ("Scripted access returned a Cloudflare challenge on 13 October; robots.txt content signal "
                               "search=yes, ai-train=no, use=reference. Identifiers and Miscellaneous numbers only are tracked.")},
         "fetch": {"method": "manual", "steps": [
             "Open https://www.britishmuseum.org/collection/search?keyword=indus%20seal in a browser and record the "
             "Museum number and Miscellaneous number of each seal."]},
         "evidence": ev, "questions": ["Q-1018", "Q-1019"], "web_checks": ["W18"], "hashes": {}},
        {"id": "museum-open-access-2026-10-13", "change": "new", "status": "project-output", "location": "tracked",
         "title": "Museum open-access harvest and joins, 13 October 2026 (Q-1018, Q-1019)",
         "kind": "project-register", "local_paths": [P, R],
         "size": {"records_decided": summ["records_decided"],
                  "exact_or_confirmed": summ["joins"]["exact_or_confirmed_records"],
                  "new_joins": summ["joins"]["new_vs_census"], "q1019_confirmed": summ["q1019"]["new_confirmed_or_exact"],
                  "museum_join_lower_bound": 68 + summ["joins"]["new_vs_census"],
                  "census_scope_join_lower_bound": summ["joins"]["census_lower_bound_after"],
                  "objects_with_museum_accession": coverage["website_or_census_or_this_package"]["objects"],
                  "families_gaining_first_museum_number": summ["coverage_gains_new_joins"]["families_gaining_museum_accession"],
                  "candidate_additions": len(summ["candidate_additions"])},
         "identifiers": ["museum accession", "Lipi family", "CISI number"],
         "metadata_fields": ["join class", "method", "evidence locator", "conflicts", "candidate counts",
                             "field-presence and coverage-gain flags"],
         "rights": {"status": "mixed-assets", "licence": None,
                    "detail": ("Project tables CC0; CC0 museum metadata (Met, Cleveland, AIC, Smithsonian) and CC BY 4.0 "
                               "Penn metadata tracked with attribution; values from other museums stay local.")},
         "fetch": {"method": "rebuild", "steps": ["See experiments/2026-10-13-museum-open-access/README.md, 'Reproducing'."]},
         "evidence": ev, "questions": ["Q-1018", "Q-1019"], "hashes": {}},
    ]
    out = {"package": P.rstrip("/"),
           "schema": "data/MANIFEST.json schema_version 1; 'change' and 'tracked_paths' are proposal fields to drop on integration",
           "counts_change": {"held": "+1 (penn-collections-data)",
                             "partly-held": "+3 (met-open-access, cleveland-open-access, va-collections)",
                             "not-held": "-4 then +2 new (aic-open-access, smithsonian-open-access): net -2",
                             "project-output": "+1 (museum-open-access-2026-10-13)",
                             "sources_total": "85 -> 88"},
           "entries": entries}
    (PKG / "manifest-additions.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(entries), "entries")


if __name__ == "__main__":
    main()
