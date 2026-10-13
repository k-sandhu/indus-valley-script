"""Harvest Metropolitan Museum of Art records for Indus objects (Collection API v1.1 search, v1 objects).

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_met.py
Writes data/raw/2026-10-13-museum-open-access/met/ (cache, request log, full extraction)
and experiments/2026-10-13-museum-open-access/harvest/met-queries.csv, met-records.json.
Met Open Access: objects with isPublicDomain true are CC0; the tracked file keeps
metadata only for those and identifiers only for the rest.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, ROOT, fetch_json, requests, write_json  # noqa: E402
from classify import classify_record  # noqa: E402

SEARCH = "https://collectionapi.metmuseum.org/public/collection/v1.1/search?"
OBJ = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
QUERIES = [
    "q=Indus", "q=Harappan", "q=Harappa", "q=Mohenjo-daro", "q=Mohenjodaro", "q=Mohenjo%20Daro",
    "q=Indus%20Valley", "q=Indus%20civilization", "q=Lothal", "q=Chanhu-daro", "q=Chanhudaro",
    "q=Kalibangan", "q=Dholavira", "q=Indus%20script", "q=Mature%20Harappan",
    "q=seal&geoLocation=Pakistan", "q=seal&geoLocation=India", "q=seal&geoLocation=Afghanistan",
    "q=stamp%20seal&geoLocation=Pakistan", "q=stamp%20seal&geoLocation=India",
]

EXTRA_IDS = [324066, 324068]


def main():
    out = PKG / "harvest"
    out.mkdir(exist_ok=True)
    ids = {}
    qrows = []
    for qs in QUERIES:
        meta, d = fetch_json("met", SEARCH + qs, delay=2.0)
        got = (d or {}).get("objectIDs") or []
        qrows.append({"query": qs, "status": meta["status"], "total": (d or {}).get("total"),
                      "ids_returned": len(got), "retrieved_utc": meta["retrieved_utc"], "sha256": meta["sha256"]})
        for i in got:
            ids.setdefault(i, []).append(qs)
    # accession neighbours 49.40.5 and 49.40.7 of the Dodge Fund group, checked directly
    for oid in EXTRA_IDS:
        ids.setdefault(oid, []).append("direct: accession neighbour of 49.40.1-4")
    records = []
    blocked = 0
    for oid in sorted(ids):
        meta, d = fetch_json("met", OBJ + str(oid), delay=2.0)
        if meta["status"] != 200 or d is None:
            blocked += 1
            records.append({"museum": "Metropolitan Museum of Art", "record_id": str(oid), "fetch_status": meta["status"],
                            "queries": ids[oid]})
            if meta["status"] == 403 and blocked >= 3:
                print("stopping: repeated 403", file=sys.stderr)
                break
            continue
        dims = {}
        for m in d.get("measurements") or []:
            for k, v in (m.get("elementMeasurements") or {}).items():
                dims[f"{m.get('elementName')}:{k}"] = v
        rec = {
            "museum": "Metropolitan Museum of Art",
            "record_id": str(oid),
            "accession": d.get("accessionNumber"),
            "url": d.get("objectURL"),
            "title": d.get("title"),
            "object_name": d.get("objectName"),
            "classification": d.get("classification"),
            "department": d.get("department"),
            "culture": d.get("culture"),
            "period": d.get("period"),
            "date": d.get("objectDate"),
            "date_begin": d.get("objectBeginDate"),
            "date_end": d.get("objectEndDate"),
            "material": d.get("medium"),
            "dimensions_raw": d.get("dimensions"),
            "measurements_cm": dims,
            "findspot_raw": "; ".join(x for x in [d.get("region"), d.get("subregion"), d.get("locale"), d.get("locus"),
                                                  d.get("excavation"), d.get("country")] if x),
            "credit_line": d.get("creditLine"),
            "bibliography": [],
            "other_numbers": [],
            "inscription_note": "",
            "description": "",
            "tags": [t.get("term") for t in (d.get("tags") or [])],
            "image_urls": [u for u in [d.get("primaryImage")] + (d.get("additionalImages") or []) if u],
            "image_licence": "CC0 (Met Open Access, isPublicDomain true)" if d.get("isPublicDomain") else "not open access",
            "data_licence": "CC0" if d.get("isPublicDomain") else "Met terms (not open access)",
            "is_public_domain": d.get("isPublicDomain"),
            "metadata_date": d.get("metadataDate"),
            "raw_path": meta["path"],
            "raw_sha256": meta["sha256"],
            "queries": ids[oid],
        }
        rec.update(classify_record(rec))
        records.append(rec)
    write_json(RAW / "met" / "records-extracted.json", records)
    with open(out / "met-queries.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(qrows[0]))
        w.writeheader()
        w.writerows(qrows)
    tracked = [r for r in records if r.get("indus_attributed") or r.get("seal_like")]
    tracked = [r if r.get("is_public_domain") else {k: r.get(k) for k in ("museum", "record_id", "accession", "url",
               "indus_attributed", "object_class", "in_scope", "exclusion_reason", "data_licence")} for r in tracked]
    for r in tracked:
        r.pop("queries", None)
    write_json(out / "met-records.json", tracked)
    print(len(ids), "ids;", len(records), "records;", sum(1 for r in records if r.get("in_scope")), "in scope")


if __name__ == "__main__":
    main()
