"""Acquire normal public primary-source URLs into ignored local storage.

Reading scopes are recorded separately. Receiving bytes is not a full reading.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "data/raw/2026-10-11-societal-persistence/coordinator/sources-v1"
SOURCES = [
    ("C01", "martin2004.html", "https://ecologyandsociety.org/vol9/iss2/art8/inline.html"),
    ("C02", "smith2016.pdf", "https://escholarship.org/content/qt2m83d6mq/qt2m83d6mq_noSplash_1a1fa895e685c057e889b47a60cb2597.pdf"),
    ("C03", "jervis2024.html", "https://www.tandfonline.com/doi/full/10.1080/00438243.2024.2387660"),
    ("C04", "jervis2026.html", "https://link.springer.com/article/10.1007/s10816-026-09803-2"),
]

def main():
    if OUT.exists():
        raise SystemExit("Capture endpoint exists. Use a dated successor instead of overwriting.")
    OUT.mkdir(parents=True)
    records = []
    for source_id, filename, url in SOURCES:
        record = {"id": source_id, "requested_url": url, "attempt_utc": datetime.now(timezone.utc).isoformat()}
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 (research source preservation)"})
            with urlopen(request, timeout=35) as response:
                body = response.read()
                record.update(status=response.status, final_url=response.url, content_type=response.headers.get("Content-Type"))
            path = OUT / filename
            path.write_bytes(body)
            record.update(path=path.relative_to(ROOT).as_posix(), bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), transport="urllib normal public request")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            record.update(status="failed", error=type(error).__name__ + ": " + str(error))
        records.append(record)
    with (OUT / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump({"reading_not_implied_by_acquisition": True, "records": records}, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"sources": [{"id": r["id"], "status": r["status"], "bytes": r.get("bytes")} for r in records]}))

if __name__ == "__main__":
    main()
