"""Derive per-museum counts from reviewed flags and saved acquisition logs.

Run apply_review_overrides.py first. Query logs supply acquisition denominators;
classification counts use the retained harvest rows. Penn's broader pattern-match
count is reported separately in the note, rather than as reviewed attribution.
This script reads local files only.
"""
import csv
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG / "joins"))
from decisions import D

H = PKG / "harvest"
RAW = PKG.parents[1] / "data/raw/2026-10-13-museum-open-access"
SOURCES = [
    ("met", "Metropolitan Museum of Art", "Collection API v1.1 search + v1 objects", "CC0"),
    ("cleveland", "Cleveland Museum of Art", "Open Access API", "CC0"),
    ("aic", "Art Institute of Chicago", "API search with phrase queries", "CC0 (description field CC BY 4.0)"),
    ("smithsonian", "Smithsonian Institution", "Open Access bulk bucket (API refused without key)", "CC0"),
    ("penn", "Penn Museum", "Collections data CSV (2026-10-07) + object pages", "CC BY 4.0"),
    ("vam", "Victoria and Albert Museum", "Collections API v2", "V&A API terms (non-commercial; 4-week storage)"),
    ("bm", "British Museum", "Saved search page (12 Oct) and saved observations; live site behind a challenge", "not open (identifiers only)"),
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows_csv(name):
    path = H / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    output = []
    for slug, museum, route, licence in SOURCES:
        document = read_json(H / f"{slug}-records.json")
        rows = document["records"] if isinstance(document, dict) else document
        queries = rows_csv(f"{slug}-queries.csv")
        query_count = len(queries)
        extracted = RAW / slug / "records-extracted.json"
        read_count = len(read_json(extracted)) if extracted.exists() else len(rows)
        if slug == "penn":
            read_count = sum(int(r["csv_rows"]) for r in queries)
        if slug == "smithsonian":
            queries = [r for r in queries if r["route"].startswith("s3://")]
            query_count = len(queries)
            read_count = sum(int(r["records_scanned"]) for r in queries)
        attributed = [r for r in rows if r.get("indus_attributed")]
        originals = [r for r in attributed if r.get("in_scope") and r.get("originality") == "original"]
        inscribed = sum(r.get("inscription_status") in {"inscribed", "inscribed-by-image"} for r in originals)
        uninscribed = sum(r.get("inscription_status") == "uninscribed" for r in originals)
        unstated = len(originals) - inscribed - uninscribed
        casts = sum(r.get("originality") in {"cast-or-replica", "modern-impression"} for r in attributed)
        notes = {
            "met": "Signs observed on cached CC0 photographs; later-period accessions excluded by the review ledger.",
            "cleveland": "Inscribed originals have CC0 photographs.",
            "aic": "Reviewed hits contain no Indus Civilization object.",
            "smithsonian": f"{len(attributed)} casts; {sum(bool(r.get('seal_like')) for r in attributed)} seal casts; bulk scope is the logged units.",
            "penn": "Retained seal-like rows reviewed; originals on loan from MFA Boston.",
            "vam": f"{len(attributed)} reviewed attributed records: IS.8:1-1951, IS.8A-1951, modern impression IS.8:2-1951 and figurine head IS.9-1951; the head is outside inscription scope.",
            "bm": f"{len(originals)} in-scope original seals; {inscribed} stated inscriptions; source observations recorded in review-overrides.json; BM 123208 has Ur-III attribution.",
        }
        if slug == "penn":
            notes[slug] = (f"{sum(int(r['rows_matching']) for r in queries)} broad pattern matches; "
                           f"{len(rows)} retained seal-like rows reviewed; originals on loan from MFA Boston.")
        output.append(dict(museum=museum, route=route, queries=query_count, records_read=read_count,
                           indus_attributed_records=len(attributed), inscribed_originals=inscribed,
                           uninscribed_originals=uninscribed, originals_inscription_not_stated=unstated,
                           casts_or_impressions=casts,
                           joined_exact_or_confirmed=sum(d["museum"] == museum and d["cls"] in {"exact", "confirmed"} for d in D),
                           data_licence=licence, note=notes[slug]))
    with (H / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
