"""Download one openly available file into data/raw/2026-10-21-plan-registration/S/downloads/
and append its provenance (URL, final URL, UTC time, HTTP status, bytes, SHA-256) to
experiments/2026-10-21-plan-registration/measure-S/fetch_log.json.

usage: python -P experiments/2026-10-21-plan-registration/measure-S/code/fetch.py URL OUT_NAME [--note TEXT]
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[4]
DL = ROOT / "data" / "raw" / "2026-10-21-plan-registration" / "S" / "downloads"
LOG = ROOT / "experiments" / "2026-10-21-plan-registration" / "measure-S" / "fetch_log.json"
UA = {"User-Agent": "Mozilla/5.0 (indus plan-registration research; manual reading of open publications)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    DL.mkdir(parents=True, exist_ok=True)
    out = DL / a.out
    if out.exists():
        raise SystemExit(f"{out} exists")
    t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    r = requests.get(a.url, headers=UA, timeout=180, allow_redirects=True)
    rec = {"url": a.url, "final_url": r.url, "retrieved_utc": t, "http_status": r.status_code,
           "content_type": r.headers.get("Content-Type"), "note": a.note}
    if r.status_code == 200:
        out.write_bytes(r.content)
        rec.update(file=str(out.relative_to(ROOT)).replace("\\", "/"), bytes=len(r.content),
                   sha256=hashlib.sha256(r.content).hexdigest())
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    log.append(rec)
    LOG.write_text(json.dumps(log, indent=1))
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
