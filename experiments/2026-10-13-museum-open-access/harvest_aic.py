"""Search the Art Institute of Chicago API for Indus objects.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_aic.py
The simple `q` parameter is a fuzzy search that returns most of the collection, so the
queries use the API's Elasticsearch `params` with phrase matching. Data are CC0.
"""
import csv
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, fetch_json, write_json  # noqa: E402
from classify import classify_record  # noqa: E402

API = "https://api.artic.edu/api/v1/artworks/search?params="
FIELDS = ("id,title,main_reference_number,place_of_origin,date_display,date_start,date_end,artwork_type_title,"
          "classification_title,medium_display,dimensions,is_public_domain,style_title,credit_line,inscriptions,"
          "provenance_text,publication_history,image_id,description")
TEXT_FIELDS = ["title", "place_of_origin", "style_title", "description", "term_titles", "subject_titles",
               "classification_titles", "inscriptions", "provenance_text", "publication_history", "medium_display",
               "date_display", "artist_display"]
PHRASES = ["Indus", "Harappan", "Harappa", "Mohenjo-daro", "Mohenjodaro", "Indus Valley", "Lothal", "Chanhu-daro",
           "Kalibangan", "Indus script"]


def phrase_query(p):
    return {"multi_match": {"query": p, "type": "phrase", "fields": TEXT_FIELDS}}


def south_asian_early_seals():
    return {"bool": {"must": [
        {"bool": {"should": [{"match_phrase": {"place_of_origin": c}} for c in ("Pakistan", "India", "Afghanistan")]}},
        {"range": {"date_start": {"lte": -1000}}}]}}


def main():
    out = PKG / "harvest"
    out.mkdir(exist_ok=True)
    queries = [(f"phrase:{p}", phrase_query(p)) for p in PHRASES]
    queries.append(("place Pakistan/India/Afghanistan and date_start <= -1000", south_asian_early_seals()))
    # controls showing that the place and date filters work (their hits are logged, not classified)
    controls = [("control: place Pakistan", {"match_phrase": {"place_of_origin": "Pakistan"}}),
                ("control: date_start <= -1000", {"range": {"date_start": {"lte": -1000}}})]
    qrows, hits = [], {}
    for label, q in queries + controls:
        params = {"query": q, "limit": 100, "fields": FIELDS}
        url = API + urllib.parse.quote(json.dumps(params, separators=(",", ":")))
        meta, d = fetch_json("aic", url)
        data = (d or {}).get("data") or []
        qrows.append({"query": label, "status": meta["status"], "total": ((d or {}).get("pagination") or {}).get("total"),
                      "rows_returned": len(data), "retrieved_utc": meta["retrieved_utc"], "sha256": meta["sha256"]})
        if label.startswith("control"):
            continue
        for a in data:
            hits.setdefault(a["id"], {"a": a, "queries": [], "meta": meta})["queries"].append(label)
    records = []
    for aid, h in sorted(hits.items()):
        a = h["a"]
        rec = {
            "museum": "Art Institute of Chicago", "record_id": str(aid), "accession": a.get("main_reference_number"),
            "url": f"https://www.artic.edu/artworks/{aid}", "title": a.get("title"),
            "object_name": a.get("artwork_type_title"), "classification": a.get("classification_title"),
            "culture": a.get("style_title") or "", "period": "", "date": a.get("date_display"),
            "date_begin": a.get("date_start"), "date_end": a.get("date_end"), "material": a.get("medium_display"),
            "dimensions_raw": a.get("dimensions"), "findspot_raw": a.get("place_of_origin") or "",
            "credit_line": a.get("credit_line"), "bibliography": [a.get("publication_history")] if a.get("publication_history") else [],
            "other_numbers": [], "inscription_note": a.get("inscriptions") or "", "description": a.get("description") or "",
            "image_urls": [f"https://www.artic.edu/iiif/2/{a['image_id']}/full/843,/0/default.jpg"] if a.get("image_id") else [],
            "image_licence": "public domain (AIC is_public_domain)" if a.get("is_public_domain") else "not public domain",
            "data_licence": "CC0", "is_public_domain": a.get("is_public_domain"),
            "raw_path": h["meta"]["path"], "raw_sha256": h["meta"]["sha256"], "queries": h["queries"],
        }
        rec.update(classify_record(rec))
        records.append(rec)
    write_json(RAW / "aic" / "records-extracted.json", records)
    with open(out / "aic-queries.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(qrows[0]))
        w.writeheader()
        w.writerows(qrows)
    tracked = []
    for r in records:
        t = {k: r.get(k) for k in ("museum", "record_id", "accession", "url", "title", "findspot_raw", "date", "object_name",
                                   "indus_attributed", "seal_like", "object_class", "in_scope", "exclusion_reason")}
        t["queries"] = r["queries"]
        tracked.append(t)
    write_json(out / "aic-records.json", tracked)
    for r in records:
        print(r["accession"], "|", r["title"], "|", r["findspot_raw"], "|", r["date"], "|", r["object_class"],
              "IN" if r["in_scope"] else "out", r["exclusion_reason"])
    print(len(records), "records;", sum(1 for r in records if r["in_scope"]), "in scope")


if __name__ == "__main__":
    main()
