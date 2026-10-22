"""Acquire the lexical sources of the rebus base-rate study with a provenance record.

Every request is logged as one JSON line: URL, HTTP status, byte count, SHA-256,
retrieval time (UTC) and local path. Pages are written under
data/raw/2026-10-21-rebus-base-rate/sources-v1/<source>/, which stays local.

    python experiments/2026-10-21-rebus-base-rate/code/acquire.py dedr
    python experiments/2026-10-21-rebus-base-rate/code/acquire.py cdial
    python experiments/2026-10-21-rebus-base-rate/code/acquire.py tamil-lex
    python experiments/2026-10-21-rebus-base-rate/code/acquire.py files
    python experiments/2026-10-21-rebus-base-rate/code/acquire.py tamil-lex 2400 4600   # a page range

The DSAL sources are paged; the script requests one page at a time with a pause,
skips pages already on disk with a logged hash, and stops the Tamil Lexicon run
at the first page that has no entries and no link to a next page.
"""

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1"
UA = "Mozilla/5.0 (compatible; indus-valley-script research knowledge base; rebus base-rate study; one request at a time)"
PAUSE = 0.6

DSAL = {
    "dedr": ("https://dsal.uchicago.edu/cgi-bin/app/burrow_query.py?page={}", 514),
    "cdial": ("https://dsal.uchicago.edu/cgi-bin/app/soas_query.py?page={}", 836),
    "tamil-lex": ("https://dsal.uchicago.edu/cgi-bin/app/tamil-lex_query.py?page={}", None),
}

# Single files: (source, name, url). Rights witnesses are the dictionaries' own front pages.
FILES = [
    ("rights", "dsal-burrow-index.html", "https://dsal.uchicago.edu/dictionaries/burrow/"),
    ("rights", "dsal-soas-index.html", "https://dsal.uchicago.edu/dictionaries/soas/"),
    ("rights", "dsal-tamil-lex-index.html", "https://dsal.uchicago.edu/dictionaries/tamil-lex/"),
    ("rights", "dsal-dictionaries-index.html", "https://dsal.uchicago.edu/dictionaries/"),
    ("concepticon", "concepticon.tsv", "https://raw.githubusercontent.com/concepticon/concepticon-data/v3.4.0/concepticondata/concepticon.tsv"),
    ("concepticon", "metadata.json", "https://raw.githubusercontent.com/concepticon/concepticon-data/v3.4.0/metadata.json"),
    ("norare", "Brysbaert-2014-Concreteness.tsv", "https://raw.githubusercontent.com/concepticon/norare-data/v1.1/datasets/Brysbaert-2014-Concreteness/Brysbaert-2014-Concreteness.tsv"),
    ("norare", "Brysbaert-2014-Concreteness.tsv-metadata.json", "https://raw.githubusercontent.com/concepticon/norare-data/v1.1/datasets/Brysbaert-2014-Concreteness/Brysbaert-2014-Concreteness.tsv-metadata.json"),
    ("norare", "LICENSE", "https://raw.githubusercontent.com/concepticon/norare-data/v1.1/LICENSE"),
    ("munda", "pMunda_cognate_set_2019-08-29.csv", "https://zenodo.org/api/records/3380874/files/pMunda_cognate_set_2019-08-29.csv/content"),
    ("munda", "zenodo-3380874.json", "https://zenodo.org/api/records/3380874"),
    ("backstrom", "backstromnorthernpakistan-v1.1.zip", "https://github.com/lexibank/backstromnorthernpakistan/archive/refs/tags/v1.1.zip"),
    ("sangam", "pmuni0028-Ainkurunuru.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0028.html"),
    ("sangam", "pmuni0038-Patirruppattu.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0038.html"),
    ("sangam", "pmuni0057-Purananuru.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0057.html"),
    ("sangam", "pmuni0063-Porunararruppatai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0063.html"),
    ("sangam", "pmuni0064-Cirupanarruppatai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0064.html"),
    ("sangam", "pmuni0067-Tirumurukarruppatai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0067.html"),
    ("sangam", "pmuni0069-Perumpanarruppatai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0069.html"),
    ("sangam", "pmuni0070-Netunalvatai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0070.html"),
    ("sangam", "pmuni0071-Maturaikkanci.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0071.html"),
    ("sangam", "pmuni0073-Kurincippattu.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0073.html"),
    ("sangam", "pmuni0077-Pattinappalai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0077.html"),
    ("sangam", "pmuni0078-Malaipatukatam.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0078.html"),
    ("sangam", "pmuni0087-Paripatal.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0087.html"),
    ("sangam", "pmuni0110-Kuruntokai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0110.html"),
    ("sangam", "pmuni0221-Kalittokai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0221.html"),
    ("sangam", "pmuni0229-Akananuru.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0229.html"),
    ("sangam", "pmuni0296-Narrinai.html", "https://www.projectmadurai.org/pm_etexts/utf8/pmuni0296.html"),
    ("sangam", "pmworks.html", "https://www.projectmadurai.org/pmworks.html"),
    ("epsd2", "epsd2.zip", "https://oracc.museum.upenn.edu/json/epsd2.zip"),
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


def log(source, record):
    path = RAW / source / "requests.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def done_pages(source):
    path = RAW / source / "requests.jsonl"
    seen = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:      # two page-range streams append to one log
                continue
            if rec.get("status") == 200 and rec.get("page") is not None:
                seen[rec["page"]] = rec
    return seen


def run_dsal(source, start=1, stop=None):
    pattern, total = DSAL[source]
    if stop is not None:
        total = stop
    seen = done_pages(source)
    page = start
    empty_run = 0
    while True:
        if total is not None and page > total:
            break
        local = RAW / source / f"page-{page:05d}.html"
        if page in seen and local.exists():
            body = local.read_bytes()
        else:
            url = pattern.format(page)
            started = now()
            status, final, ctype, body = fetch(url)
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(body)
            log(source, {
                "source": source, "page": page, "url": url, "final_url": final,
                "status": status, "content_type": ctype, "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(), "started_utc": started,
                "finished_utc": now(), "local_path": str(local.relative_to(ROOT)).replace("\\", "/"),
            })
            time.sleep(PAUSE)
        if total is None:
            text = body.decode("utf-8", errors="replace")
            entries = text.count("<hw>")
            has_next = f"page={page + 1}\"" in text
            if entries == 0 and not has_next:
                empty_run += 1
                if empty_run >= 2:
                    break
            else:
                empty_run = 0
        if page % 50 == 0:
            print(source, page, now(), flush=True)
        page += 1
    print(source, "finished at page", page, now(), flush=True)


def run_files():
    for source, name, url in FILES:
        local = RAW / source / name
        if local.exists():
            print("exists", local)
            continue
        started = now()
        try:
            status, final, ctype, body = fetch(url)
        except RuntimeError as exc:
            log(source, {"source": source, "name": name, "url": url, "status": None,
                         "error": str(exc), "started_utc": started, "finished_utc": now()})
            print("failed", url, exc)
            continue
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(body)
        log(source, {
            "source": source, "name": name, "url": url, "final_url": final, "status": status,
            "content_type": ctype, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
            "started_utc": started, "finished_utc": now(),
            "local_path": str(local.relative_to(ROOT)).replace("\\", "/"),
        })
        print(status, len(body), url, flush=True)
        time.sleep(PAUSE)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "files":
        run_files()
    else:
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        stop = int(sys.argv[3]) if len(sys.argv) > 3 else None
        run_dsal(what, start, stop)
