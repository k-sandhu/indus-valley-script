"""Harvest Cleveland Museum of Art Open Access records for Indus objects.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_cleveland.py
Open Access API, no key; records flagged share_license_status CC0.
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, fetch_json, requests, write_json  # noqa: E402
from classify import classify_record  # noqa: E402

API = "https://openaccess-api.clevelandart.org/api/artworks/"
QUERIES = ["q=Indus", "q=Indus%20Valley", "q=Harappan", "q=Harappa", "q=Mohenjo-daro", "q=Mohenjodaro",
           "q=Lothal", "q=Chanhu-daro", "q=Kalibangan", "q=Indus%20script", "type=Seals",
           "q=seal&limit=1000", "q=stamp%20seal&limit=1000"]
SOUTH_ASIA = re.compile(r"pakistan|india|indus|afghanistan|bactria|baluchistan", re.I)


def main():
    out = PKG / "harvest"
    out.mkdir(exist_ok=True)
    ids = {}
    qrows = []
    for qs in QUERIES:
        url = API + "?" + qs + ("" if "limit" in qs else "&limit=1000")
        meta, d = fetch_json("cleveland", url)
        data = (d or {}).get("data") or []
        kept = 0
        for a in data:
            cult = " ".join(a.get("culture") or [])
            # broad 'seal' queries are restricted to South Asian cultures before full records are fetched
            if qs.startswith(("q=seal", "q=stamp")) and not SOUTH_ASIA.search(cult):
                continue
            kept += 1
            ids.setdefault(a["id"], []).append(qs)
        qrows.append({"query": qs, "status": meta["status"], "total": ((d or {}).get("info") or {}).get("total"),
                      "rows_returned": len(data), "rows_kept": kept, "retrieved_utc": meta["retrieved_utc"],
                      "sha256": meta["sha256"]})
    records = []
    for aid in sorted(ids):
        meta, d = fetch_json("cleveland", API + str(aid))
        a = (d or {}).get("data") or {}
        if not a:
            records.append({"museum": "Cleveland Museum of Art", "record_id": str(aid), "fetch_status": meta["status"]})
            continue
        imgs = a.get("images") or {}
        image_urls = [v.get("url") for k, v in imgs.items() if isinstance(v, dict) and v.get("url")]
        for alt in a.get("alternate_images") or []:
            for k, v in alt.items():
                if isinstance(v, dict) and v.get("url"):
                    image_urls.append(v["url"])
        rec = {
            "museum": "Cleveland Museum of Art",
            "record_id": str(aid),
            "accession": a.get("accession_number"),
            "url": a.get("url"),
            "title": a.get("title"),
            "object_name": a.get("type"),
            "classification": a.get("type"),
            "department": a.get("department"),
            "culture": "; ".join(a.get("culture") or []),
            "period": "",
            "date": a.get("creation_date"),
            "date_begin": a.get("creation_date_earliest"),
            "date_end": a.get("creation_date_latest"),
            "material": a.get("technique"),
            "dimensions_raw": a.get("measurements"),
            "measurements_cm": a.get("dimensions"),
            "findspot_raw": "; ".join(str(x.get("description") or "") for x in (a.get("find_spot") or [])
                                      if isinstance(x, dict)) if isinstance(a.get("find_spot"), list) else (a.get("find_spot") or ""),
            "provenance_raw": [p.get("description") for p in (a.get("provenance") or []) if isinstance(p, dict)],
            "credit_line": a.get("creditline"),
            "bibliography": [c.get("citation") for c in (a.get("citations") or []) if isinstance(c, dict)],
            "other_numbers": [],
            "inscription_note": "; ".join(str(i.get("inscription") or "") for i in (a.get("inscriptions") or [])
                                          if isinstance(i, dict)),
            "description": a.get("description") or "",
            "did_you_know": a.get("did_you_know") or "",
            "tags": [],
            "image_urls": image_urls,
            "image_licence": "CC0 (Cleveland Open Access)" if a.get("share_license_status") == "CC0" else a.get("share_license_status"),
            "data_licence": "CC0" if a.get("share_license_status") == "CC0" else "CMA terms",
            "is_public_domain": a.get("share_license_status") == "CC0",
            "raw_path": meta["path"],
            "raw_sha256": meta["sha256"],
            "queries": ids[aid],
        }
        rec.update(classify_record(rec))
        records.append(rec)
    write_json(RAW / "cleveland" / "records-extracted.json", records)
    with open(out / "cleveland-queries.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(qrows[0]))
        w.writeheader()
        w.writerows(qrows)
    tracked = [dict(r) for r in records if r.get("indus_attributed") or r.get("seal_like")]
    for r in tracked:
        r.pop("queries", None)
    write_json(out / "cleveland-records.json", tracked)
    print(len(ids), "ids;", len(records), "records;", sum(1 for r in records if r.get("in_scope")), "in scope")


if __name__ == "__main__":
    main()
