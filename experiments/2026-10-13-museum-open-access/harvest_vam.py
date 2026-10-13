"""Search the Victoria and Albert Museum Collections API v2 for Indus objects.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_vam.py
V&A API terms (websites terms and conditions, section 9): non-commercial personal and
educational use, at most one request per second, and API content may not be cached or
stored for more than four weeks. Raw responses therefore stay local and must be deleted by
2026-11-10; the tracked file keeps identifiers, URLs, field-presence flags and our
classification only.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, fetch_json, write_json  # noqa: E402
from classify import classify_record  # noqa: E402

SEARCH = "https://api.vam.ac.uk/v2/objects/search?page_size=100&"
OBJ = "https://api.vam.ac.uk/v2/object/"
QUERIES = ["q=Mohenjo-daro", "q=Mohenjo%20Daro", "q=Mohenjodaro", "q=Harappa", "q=Harappan", "q=Indus",
           "q=Indus%20Valley", "q=Indus%20script", "q=Lothal", "q=Chanhu-daro", "q=Kalibangan",
           "q=seal&q_place_name=Pakistan", "q=seal&q_place_name=India&year_made_to=-1000",
           "q=seal&year_made_to=-1500&q_place_name=Sind"]


def main():
    out = PKG / "harvest"
    out.mkdir(exist_ok=True)
    qrows, ids = [], {}
    for qs in QUERIES:
        meta, d = fetch_json("vam", SEARCH + qs)
        recs = (d or {}).get("records") or []
        qrows.append({"query": qs, "status": meta["status"], "total": ((d or {}).get("info") or {}).get("record_count"),
                      "rows_returned": len(recs), "retrieved_utc": meta["retrieved_utc"], "sha256": meta["sha256"]})
        for r in recs:
            ids.setdefault(r["systemNumber"], {"queries": [], "summary": r})["queries"].append(qs)
    records = []
    for sn, h in sorted(ids.items()):
        s = h["summary"]
        pre = {"museum": "Victoria and Albert Museum", "record_id": sn, "accession": s.get("accessionNumber"),
               "title": s.get("_primaryTitle"), "object_name": s.get("objectType"), "classification": s.get("objectType"),
               "findspot_raw": s.get("_primaryPlace") or "", "date": s.get("_primaryDate") or "", "culture": "",
               "period": "", "description": "", "material": ""}
        pre.update(classify_record(pre))
        rec = dict(pre)
        rec["url"] = f"https://collections.vam.ac.uk/item/{sn}/"
        rec["queries"] = h["queries"]
        # full records only for seal-like objects or records placed at an Indus site
        if pre["seal_like"] or pre["indus_attributed"]:
            meta, d = fetch_json("vam", OBJ + sn)
            rd = (d or {}).get("record") or {}
            if rd:
                dims = rd.get("dimensions") or []
                rec.update({
                    "title": "; ".join(t.get("title", "") for t in rd.get("titles") or []) or pre["title"],
                    "material": "; ".join(m.get("text", "") for m in rd.get("materials") or []),
                    "dimensions_raw": "; ".join(f"{x.get('dimension')} {x.get('value')} {x.get('unit')}" for x in dims),
                    "findspot_raw": "; ".join(p.get("place", {}).get("text", "") for p in rd.get("placesOfOrigin") or []),
                    "date": "; ".join(p.get("date", {}).get("text", "") for p in rd.get("productionDates") or []),
                    "description": " ".join(x for x in [rd.get("briefDescription"), rd.get("physicalDescription"),
                                                       rd.get("summaryDescription")] if x),
                    "bibliography": [rd.get("bibliographicReferences")] if rd.get("bibliographicReferences") else [],
                    "other_numbers": [f"{x.get('type', {}).get('text', '')}: {x.get('number')}" for x in rd.get("otherNumbers") or []],
                    "inscription_note": "; ".join(str(x.get("content", "")) for x in rd.get("marksAndInscriptions") or []),
                    "credit_line": rd.get("creditLine"),
                    "provenance_raw": rd.get("objectHistory"),
                    "image_urls": [f"{(d.get('meta') or {}).get('images', {}).get('_iiif_image', '')}"] if (d.get("meta") or {}).get("images") else [],
                    "image_licence": "V&A terms: non-commercial use; image URL to be used as returned (not an open licence)",
                    "data_licence": "V&A API terms (non-commercial; no storage beyond four weeks)",
                    "raw_path": meta["path"], "raw_sha256": meta["sha256"],
                })
                rec.update(classify_record(rec))
        records.append(rec)
    write_json(RAW / "vam" / "records-extracted.json", records)
    with open(out / "vam-queries.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(qrows[0]))
        w.writeheader()
        w.writerows(qrows)
    keep = ("museum", "record_id", "accession", "url", "indus_attributed", "seal_like", "object_class", "inscription_status",
            "originality", "in_scope", "exclusion_reason")
    tracked = []
    for r in records:
        if not (r["indus_attributed"] or r["seal_like"]):
            continue
        t = {k: r.get(k) for k in keep}
        t["fields_present"] = sorted(k for k in ("material", "dimensions_raw", "findspot_raw", "date", "bibliography",
                                                 "other_numbers", "inscription_note", "image_urls") if r.get(k))
        tracked.append(t)
    write_json(out / "vam-records.json", tracked)
    for r in records:
        if r["indus_attributed"] or r["seal_like"]:
            print(r["accession"], "|", r["title"], "|", r["object_name"], "|", r.get("findspot_raw"), "|", r.get("date"), "|",
                  r["object_class"], r["inscription_status"], r["originality"], "IN" if r["in_scope"] else "out", r["exclusion_reason"])
    print(len(records), "records;", sum(1 for r in records if r["in_scope"]), "in scope")


if __name__ == "__main__":
    main()
