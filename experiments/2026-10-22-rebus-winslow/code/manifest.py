"""Write SOURCES.json: the acquisition record of the Winslow pages, rebuilt from disk.

Every page on disk is listed with its hash, size and the log line of the request
that fetched it. A page whose hash differs from its logged hash, or that has no
log line, is reported, not silently accepted.

    python experiments/2026-10-22-rebus-winslow/code/manifest.py experiments/2026-10-22-rebus-winslow/SOURCES.json
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "data" / "raw" / "2026-10-22-rebus-winslow" / "sources-v1"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).relative_to(ROOT)).replace("\\", "/")


def main(out_path):
    out_path = Path(out_path)
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    logs = {}
    log_files = sorted((SRC / "winslow").glob("requests-*.jsonl")) + sorted((SRC / "rights").glob("requests-*.jsonl"))
    for lf in log_files:
        for line in lf.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            logs[rec["local_path"]] = dict(rec, log_file=rel(lf))
    pages = []
    problems = []
    digest = hashlib.sha256()
    for p in sorted((SRC / "winslow").glob("page-*.html")):
        h = sha(p)
        digest.update(bytes.fromhex(h))
        rec = logs.get(rel(p))
        text = p.read_text(encoding="utf-8")
        entry = {"page": int(p.stem.split("-")[1]), "bytes": p.stat().st_size, "sha256": h,
                 "entries": text.count("<hw>"), "placeholder": "Please click next to see digital content" in text}
        if rec is None:
            problems.append({"path": rel(p), "problem": "no log line"})
        else:
            entry.update(url=rec["url"], status=rec["status"], retrieved_utc=rec["finished_utc"], log_file=rec["log_file"])
            if rec["sha256"] != h:
                problems.append({"path": rel(p), "problem": "hash differs from log"})
        pages.append(entry)
    rights = []
    for p in sorted((SRC / "rights").glob("*.html")):
        rec = logs.get(rel(p), {})
        rights.append({"path": rel(p), "url": rec.get("url"), "bytes": p.stat().st_size, "sha256": sha(p),
                       "retrieved_utc": rec.get("finished_utc")})
    out = {
        "schema": "rebus-winslow sources v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "title": "A comprehensive Tamil and English dictionary of high and low Tamil",
            "author": "Miron Winslow", "publisher": "Madras: P. R. Hunt", "year": 1862,
            "edition": "Digital Dictionaries of South Asia (DSAL), University of Chicago; front matter states the errata "
                       "were applied and the data were last updated in October 2020",
            "query_url": "https://dsal.uchicago.edu/cgi-bin/app/winslow_query.py?page=N",
            "rights_observed": "The 1862 work is out of copyright; the DSAL pages carry no licence statement for the "
                               "digital edition. Raw pages and every derived table stay local.",
        },
        "pages": {"count": len(pages), "first": pages[0]["page"] if pages else None,
                  "last": pages[-1]["page"] if pages else None,
                  "with_entries": sum(1 for x in pages if x["entries"]),
                  "placeholders": [x["page"] for x in pages if x["placeholder"]],
                  "bytes": sum(x["bytes"] for x in pages), "digest_of_page_hashes": digest.hexdigest(),
                  "log_files": [rel(lf) for lf in log_files]},
        "problems": problems,
        "rights_files": rights,
        "page_records": pages,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out["pages"][k] for k in ("count", "first", "last", "with_entries", "bytes")} |
                     {"placeholders": len(out["pages"]["placeholders"]), "problems": len(problems)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
