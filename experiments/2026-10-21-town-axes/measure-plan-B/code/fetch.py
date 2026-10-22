"""Download a source file into the plan-B raw directory and log its acquisition record.

Usage: python .../code/fetch.py URL FILENAME [--referer URL]

Saves to data/raw/2026-10-21-town-axes/plan-B/downloads/FILENAME and appends a record
(URL, final URL, retrieval time UTC, HTTP status, content type, size, SHA-256) to
data/raw/2026-10-21-town-axes/plan-B/downloads.json.
"""
import datetime
import hashlib
import json
import os
import sys

import requests

RAW = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"


def main():
    url, fn = sys.argv[1], sys.argv[2]
    headers = {"User-Agent": UA, "Accept": "application/pdf,*/*"}
    if "--referer" in sys.argv:
        headers["Referer"] = sys.argv[sys.argv.index("--referer") + 1]
    os.makedirs(os.path.join(RAW, "downloads"), exist_ok=True)
    out = os.path.join(RAW, "downloads", fn)
    t = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = requests.get(url, headers=headers, timeout=(20, 110), stream=True, allow_redirects=True)
    h = hashlib.sha256()
    n = 0
    with open(out, "wb") as f:
        for chunk in r.iter_content(1 << 16):
            f.write(chunk)
            h.update(chunk)
            n += len(chunk)
    rec = dict(file=out.replace("\\", "/"), url=url, final_url=r.url, retrieved_utc=t, status=r.status_code,
               content_type=r.headers.get("Content-Type"), bytes=n, sha256=h.hexdigest())
    log = os.path.join(RAW, "downloads.json")
    recs = []
    if os.path.exists(log):
        with open(log, encoding="utf-8") as f:
            recs = json.load(f)
    recs.append(rec)
    with open(log, "w", encoding="utf-8") as f:
        json.dump(recs, f, indent=1)
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
