"""Preserve a bounded set of public HARP witnesses without overwriting files."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-20-archaeological-setting"
OUT = Path(__file__).resolve().parent / "acquisition.json"
SOURCES = [
    ("three-clay-sealings", "https://www.harappa.com/slide/three-clay-sealings"),
    ("unicorn-sealing", "https://www.harappa.com/slide/unicorn-sealing"),
    ("recent-discoveries-part3", "https://www.harappa.com/indus4/e3.html"),
    ("recent-discoveries-part4", "https://www.harappa.com/indus4/e4.html"),
    ("recent-discoveries-part5", "https://www.harappa.com/indus4/e5.html"),
]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    RAW.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in SOURCES:
        record = {
            "id": name,
            "url": url,
            "accessed_utc": datetime.now(timezone.utc).isoformat(),
            "method": "ordinary HTTPS GET",
            "rights_status": "rights-unverified",
            "handling": "local-only",
        }
        try:
            request = Request(url, headers={"User-Agent": "Indus research source audit"})
            with urlopen(request, timeout=40) as response:
                content = response.read()
                record.update(http_status=response.status, final_url=response.url,
                              content_type=response.headers.get("Content-Type"))
            path = RAW / f"{name}.html"
            with path.open("xb") as stream:
                stream.write(content)
            record.update(path=path.relative_to(ROOT).as_posix(), bytes=len(content),
                          sha256=hashlib.sha256(content).hexdigest())
        except Exception as exc:
            record["failure"] = f"{type(exc).__name__}: {exc}"
            if isinstance(exc, HTTPError):
                record["http_status"] = exc.code
        records.append(record)
    with OUT.open("x", encoding="utf-8") as stream:
        json.dump({"records": records}, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"success": sum("sha256" in x for x in records), "attempts": len(records)}))


if __name__ == "__main__":
    main()
