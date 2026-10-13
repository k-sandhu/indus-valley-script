"""Acquire a population-history control once; raw contents remain local-only."""
from __future__ import annotations
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1"
TARGETS = [
    ("narasimhan2019-pmc.html", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6822619/"),
    ("narasimhan2019-author.pdf", "https://www.eva.mpg.de/documents/AAAS/Narasimhan_Formation_Science_2019_3166350.pdf")
]


def acquire(target):
    filename, url = target
    record = {"requested_url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "tls_verification": True, "redistribution": "local-only",
              "rights_status": "rights-unverified pending inspected notice"}
    try:
        response = requests.get(url, timeout=60)
        path = RAW / filename
        with path.open("xb") as stream:
            stream.write(response.content)
        record.update({"status_code": response.status_code, "final_url": response.url,
                       "content_type": response.headers.get("content-type"),
                       "path": path.relative_to(ROOT).as_posix(), "bytes": len(response.content),
                       "sha256": hashlib.sha256(response.content).hexdigest(),
                       "pdf_signature": response.content.startswith(b"%PDF"),
                       "challenge_detected": any(s in response.content.lower() for s in
                                                 [b"checking your browser", b"recaptcha"])
                                                 if filename.endswith(".html") else False})
    except requests.RequestException as exc:
        record["error"] = str(exc)
    return record


def main():
    if RAW.exists():
        raise SystemExit("Acquisition endpoint exists; use a new version.")
    RAW.mkdir(parents=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(acquire, TARGETS))
    with (RAW / "acquisition.json").open("x", encoding="utf-8") as stream:
        json.dump({"scope": "Two access routes to one work, not independent scientific observations.",
                   "records": records}, stream, indent=2)
        stream.write("\n")
    print(json.dumps(records, ensure_ascii=True))


if __name__ == "__main__":
    main()
