"""Capture query responses for supported public museum endpoints.

Run from repository root: python experiments/2026-10-06-evidence-census/collections-and-datasets/depth_queries.py
Raw response bodies and status records are written only to the package's ignored data/raw directory.
"""
from __future__ import annotations

import datetime as dt
import concurrent.futures
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/2026-10-06-evidence-census/collections-and-datasets/depth-pass"
RAW.mkdir(parents=True, exist_ok=True)
TERMS = ["Indus", "Harappa", "Mohenjo-daro", "Lothal", "Indus seal", "Harappan seal"]
HEADERS = {"User-Agent": "Indus-evidence-census/1.0 (research; public catalogue query)"}

ROUTES = {
    "Metropolitan Museum of Art": ("https://collectionapi.metmuseum.org/public/collection/v1/search?q={q}", "met"),
    "Cleveland Museum of Art": ("https://openaccess-api.clevelandart.org/api/artworks/?q={q}", "cleveland"),
    "Art Institute of Chicago comparator": ("https://api.artic.edu/api/v1/artworks/search?q={q}", "aic"),
    "Smithsonian comparator": ("https://api.si.edu/openaccess/api/v1.0/search?q={q}&api_key=DEMO_KEY", "smithsonian"),
}

PAGE_ROUTES = {
    "Louvre Indus search": "https://collections.louvre.fr/en/recherche?q=Indus",
    "Louvre SB 2425 object JSON": "https://collections.louvre.fr/ark:/53355/cl010176471.json",
    "Met seal with Ox record": "https://www.metmuseum.org/art/collection/search/38287",
    "Met Indus stamp seal record": "https://www.metmuseum.org/art/collection/search/324062",
    "British Museum Indus Valley Civilisation term": "https://www.britishmuseum.org/collection/term/x46239",
    "National Museum of India Harappan collection": "https://www.nationalmuseumindia.gov.in/en/harappan-civilization",
    "Museums of India Indian Museum collection": "https://museumsofindia.gov.in/repository/collection/ObjectType?museum=im_kol",
    "NMMA Lothal seals and sealings": "https://nmma.nic.in/nmma/exploreMuseum.do?museum=ASM-KML",
    "NMMA Kalibangan seal object category": "https://nmma.nic.in/nmma/exploreMusObject.do?musname=GM-KAM&object=32",
    "CSMVS Harappan seal record": "https://networksofthepast.csmvs.in/object/sealing/",
    "Lahore Museum search/collection page": "https://lahoremuseum.punjab.gov.pk/",
    "National Museum of Pakistan official page": "https://doam.gov.pk/public/heritage-sites/792",
    "Allahabad Museum collection overview": "https://theallahabadmuseum.com/pdf/centralhallnew.pdf",
    "Ashmolean object record": "https://jameelcentre.ashmolean.org/collection/4/6739/6740/all/per_page/50/offset/0/sort_by/seqn/object/11120",
    "MFA Boston search": "https://collections.mfa.org/search/objects/*/Indus",
    "Penn Museum seal search record": "https://collections.penn.museum/collections/object/329820",
}

def fetch(url: str) -> tuple[int | None, bytes, str | None]:
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=18) as response:
            return response.status, response.read(), None
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, exc.read(), f"HTTPError: {exc.reason}"
        except Exception:
            return exc.code, b"", f"HTTPError: {exc.reason}"
    except Exception as exc:
        return None, b"", f"{type(exc).__name__}: {exc}"

def parse_count(kind: str, payload: bytes) -> tuple[int | None, list[str]]:
    try:
        obj = json.loads(payload)
    except Exception:
        return None, []
    if kind == "met":
        ids = obj.get("objectIDs") or []
        return obj.get("total", len(ids)), [str(x) for x in ids]
    if kind == "cleveland":
        rows = obj.get("data") or []
        return obj.get("info", {}).get("total", len(rows)), [str(x.get("id")) for x in rows if x.get("id") is not None]
    if kind == "aic":
        rows = obj.get("data") or []
        return obj.get("pagination", {}).get("total", len(rows)), [str(x.get("id")) for x in rows if x.get("id") is not None]
    if kind == "smithsonian":
        rows = obj.get("response", {}).get("rows") or []
        return obj.get("response", {}).get("rowCount"), [str(x.get("id")) for x in rows if x.get("id")]
    return None, []

def main() -> None:
    captured = {"date": dt.date.today().isoformat(), "note": "Exact public API response body saved per attempt; result totals are endpoint hits, not automatically Indus-inscription counts.", "attempts": []}
    for institution, (template, kind) in ROUTES.items():
        per_term_ids: dict[str, set[str]] = {}
        for term in TERMS:
            url = template.format(q=urllib.parse.quote(term, safe=""))
            status, body, error = fetch(url)
            name = institution.lower().replace(" ", "-")
            path = RAW / f"{name}-{urllib.parse.quote(term, safe='').replace('%', '_')}.body"
            path.write_bytes(body)
            count, ids = parse_count(kind, body) if status == 200 else (None, [])
            basis = "API total field; not an inscription count" if count is not None else "No parseable API total"
            if kind == "aic" and status == 200:
                basis = "API repeated total 133120 across all terms and returned unrelated top hits; total is not interpretable as query-specific evidence"
            per_term_ids[term] = set(ids)
            captured["attempts"].append({
                "institution": institution, "term": term, "url": url, "date": captured["date"],
                "http_status": status, "response_file": path.name, "response_bytes": len(body),
                "endpoint_total": count, "returned_ids": ids[:100], "returned_id_count": len(ids),
                "error": error, "count_basis": basis,
            })
    def fetch_page(item: tuple[str, str]) -> dict:
        label, url = item
        status, body, error = fetch(url)
        safe_label = "-".join("".join(ch if ch.isalnum() else "-" for ch in label.lower()).split("-"))
        filename = "page-" + safe_label + ".body"
        (RAW / filename).write_bytes(body)
        return {"institution_or_route": label, "url": url, "date": captured["date"], "http_status": status, "response_file": filename, "response_bytes": len(body), "error": error, "count_basis": "Page witness only; extract a count only where the page explicitly displays one"}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        captured["page_attempts"] = list(pool.map(fetch_page, PAGE_ROUTES.items()))
    # The query list is bounded and each endpoint is permitted to cap returned IDs. Deduplicate only explicit IDs.
    for institution in ROUTES:
        attemptset = [x for x in captured["attempts"] if x["institution"] == institution]
        ids = set(v for x in attemptset for v in x["returned_ids"])
        captured.setdefault("deduplicated", []).append({
            "institution": institution, "unique_returned_object_ids": len(ids),
            "basis": "union of explicit API object IDs returned across the six query terms; excludes unreturned/capped records",
        })
    (RAW / "query-log.json").write_text(json.dumps(captured, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"attempts": len(captured["attempts"]), "status_counts": {str(s): sum(a["http_status"] == s for a in captured["attempts"]) for s in sorted({a["http_status"] for a in captured["attempts"]}, key=str)}, "deduplicated": captured["deduplicated"], "raw": str(RAW)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
