"""Capture additional witnesses after named first-route access failures."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

import requests

from capture_sources import OUT, ROOT, capture


def main():
    out = OUT / "capture-v2.json"
    if out.exists():
        raise FileExistsError(out)
    results = []
    # The author PDF's bare hostname failed TLS hostname validation. The DOI is
    # an independently observed institutional route, not a verification bypass.
    for source_id, url in (
        ("witzel1997-doi", "https://doi.org/10.11588/xarep.00000110"),
        ("hultzsch1925-payer", "https://www.payer.de/quellenkunde/quellen031.htm"),
    ):
        try:
            results.append(capture((source_id, url)))
        except Exception as e:
            results.append({"source_id": source_id, "url": url, "error": str(e)})
    url = "https://archive.org/download/InscriptionsOfAsoka.NewEditionByE.Hultzsch/HultzschCorpusAsokaSearchable_djvu.txt"
    source_id = "hultzsch1925-ocr"
    try:
        r = requests.get(url, timeout=45)
        r.raise_for_status()
        path = OUT / (source_id + ".txt")
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(r.content)
        results.append({"source_id": source_id, "url": url, "final_url": r.url,
                        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                        "status_code": r.status_code, "content_type": r.headers.get("content-type"),
                        "local_path": path.relative_to(ROOT).as_posix(), "bytes": len(r.content),
                        "sha256": hashlib.sha256(r.content).hexdigest(),
                        "format": "Internet Archive OCR text of the 1925 critical edition",
                        "rights_status": "rights-unverified", "raw_handling": "local-only",
                        "facsimile_access": "not acquired or inspected"})
    except Exception as e:
        results.append({"source_id": source_id, "url": url, "error": str(e)})
    out.write_text(json.dumps({"sources": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps([{k: r.get(k) for k in ("source_id", "bytes", "page_count", "error")} for r in results]))


if __name__ == "__main__":
    main()
