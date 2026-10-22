"""Acquire Winslow's Tamil-English dictionary (1862) from DSAL with a provenance record.

The request logging follows experiments/2026-10-21-rebus-base-rate/code/acquire.py:
every request is one JSON line with URL, HTTP status, byte count, SHA-256,
retrieval time (UTC) and local path. Each page-range stream writes its own log
file, requests-<start>-<stop>.jsonl, so that two streams never append to one
file. Pages go to data/raw/2026-10-22-rebus-winslow/sources-v1/winslow/, which
stays local.

    python experiments/2026-10-22-rebus-winslow/code/acquire.py files
    python experiments/2026-10-22-rebus-winslow/code/acquire.py winslow 1 400

The script requests one page at a time with a pause, skips pages already on
disk with a logged hash in any stream's log, and stops at the end of the range
or after two consecutive pages that have neither entries nor a link to
the next page.
"""

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "2026-10-22-rebus-winslow" / "sources-v1"
UA = "Mozilla/5.0 (compatible; indus-valley-script research knowledge base; Winslow rebus study; one request at a time)"
PAUSE = 0.6
PAGE_URL = "https://dsal.uchicago.edu/cgi-bin/app/winslow_query.py?page={}"

FILES = [
    ("rights", "dsal-winslow-index.html", "https://dsal.uchicago.edu/dictionaries/winslow/"),
    ("rights", "dsal-dictionaries-index.html", "https://dsal.uchicago.edu/dictionaries/"),
    ("rights", "dsal-winslow-frontmatter.html", "https://dsal.uchicago.edu/dictionaries/winslow/new_frontmatter.html"),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch(url, tries=4):
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.status, resp.geturl(), resp.headers.get("Content-Type"), resp.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (404, 410):
                return exc.code, url, None, exc.read() if hasattr(exc, "read") else b""
        except Exception as exc:  # network errors are retried and then logged
            last = exc
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url}: {last!r}")


def log(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def done_pages(source):
    seen = {}
    for path in sorted((RAW / source).glob("requests-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec.get("status") == 200 and rec.get("page") is not None:
                seen[rec["page"]] = rec
    return seen


def run_pages(start, stop):
    source = "winslow"
    logfile = RAW / source / f"requests-{start:05d}-{stop:05d}.jsonl"
    seen = done_pages(source)
    empty_run = 0
    for page in range(start, stop + 1):
        local = RAW / source / f"page-{page:05d}.html"
        if page in seen and local.exists():
            body = local.read_bytes()
        else:
            url = PAGE_URL.format(page)
            started = now()
            status, final, ctype, body = fetch(url)
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(body)
            log(logfile, {
                "source": source, "page": page, "url": url, "final_url": final,
                "status": status, "content_type": ctype, "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(), "started_utc": started,
                "finished_utc": now(), "local_path": str(local.relative_to(ROOT)).replace("\\", "/"),
            })
            time.sleep(PAUSE)
        # some pages are image-only placeholders ("Please click next to see digital
        # content for this page"); stop only at pages with no entries and no next link
        if b"<hw>" not in body and f"page={page + 1}\"".encode() not in body:
            empty_run += 1
            if empty_run >= 2:
                print(source, "two pages without entries or next link, stopping at", page, now(), flush=True)
                return
        else:
            empty_run = 0
        if page % 50 == 0:
            print(source, page, now(), flush=True)
    print(source, "finished range", start, stop, now(), flush=True)


def run_files():
    logfile = RAW / "rights" / "requests-files.jsonl"
    for source, name, url in FILES:
        local = RAW / source / name
        if local.exists():
            print("exists", local)
            continue
        started = now()
        try:
            status, final, ctype, body = fetch(url)
        except RuntimeError as exc:
            log(logfile, {"source": source, "name": name, "url": url, "status": None,
                          "error": str(exc), "started_utc": started, "finished_utc": now()})
            print("failed", url, exc)
            continue
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(body)
        log(logfile, {
            "source": source, "name": name, "url": url, "final_url": final, "status": status,
            "content_type": ctype, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
            "started_utc": started, "finished_utc": now(),
            "local_path": str(local.relative_to(ROOT)).replace("\\", "/"),
        })
        print(status, len(body), url, flush=True)
        time.sleep(PAUSE)


if __name__ == "__main__":
    if sys.argv[1] == "files":
        run_files()
    else:
        run_pages(int(sys.argv[2]), int(sys.argv[3]))
