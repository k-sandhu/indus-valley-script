"""Save public source witnesses locally; never weaken TLS or access controls."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from build_register import SOURCES, HERE

RAW = Path("D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/living-towns")
LOGICAL = "data/raw/2026-10-26-indus-living-atlas/living-towns"
MAX_BYTES = 64 * 1024 * 1024


def acquire(s):
    attempts = []
    for i, url in enumerate([s["url"], *s["alternate_urls"]]):
        record = dict(source_id=s["id"], url=url, retrieved_at=datetime.now(timezone.utc).isoformat())
        try:
            with urlopen(Request(url, headers={"User-Agent": "IndusResearchSourceReview/1.0"}), timeout=35) as response:
                payload = response.read(MAX_BYTES + 1)
                if len(payload) > MAX_BYTES:
                    raise ValueError("Source exceeds 64 MiB cap; no payload saved")
                ctype = response.headers.get("Content-Type", "")
            suffix = ".pdf" if payload.startswith(b"%PDF") else ".html" if "html" in ctype else ".bin"
            dest = RAW / f'{s["id"]}-{s.get("filename_tag", "")}{i + 1}{suffix}'
            if dest.exists():
                old = hashlib.sha256(dest.read_bytes()).hexdigest()
                new = hashlib.sha256(payload).hexdigest()
                if old != new:
                    raise ValueError("Existing local witness differs; preserve it and use a new acquisition version")
            else:
                dest.write_bytes(payload)
            record.update(status="retrieved", bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(),
                          content_type=ctype, logical_path=f"{LOGICAL}/{dest.name}", physical_path=dest.as_posix(),
                          rights_status=s["rights"]["status"], handling="local-only")
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        attempts.append(record)
    return attempts


def main():
    if not Path("D:/projects/indus_valley_script").is_dir():
        raise SystemExit("D: project root is missing")
    junction = Path("data/raw").resolve()
    if str(junction).lower().replace("\\", "/") != "d:/projects/indus_valley_script/data/raw":
        raise SystemExit(f"Unexpected raw-data junction target: {junction}")
    out = HERE / "acquisition-v1.json"
    if out.exists():
        raise SystemExit("Refusing to overwrite acquisition-v1.json")
    RAW.mkdir(parents=True, exist_ok=True)
    all_records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for attempts in pool.map(acquire, [s for s in SOURCES if s["download"]]):
            all_records.extend(attempts)
            print(json.dumps(dict(source=attempts[0]["source_id"], statuses=[a["status"] for a in attempts])), flush=True)
    result = dict(schema_version="1.0", created_at=datetime.now(timezone.utc).isoformat(),
                  physical_root=RAW.as_posix(), logical_root=LOGICAL,
                  storage_check="D: mounted; 920 GB free before acquisition; data/raw resolves to D: raw tree",
                  policy="Only public URLs; certificate verification unchanged; acquired payloads remain local-only. HTTP retrieval alone does not verify that an HTML response is the source article.",
                  records=all_records)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(retrieved=sum(r["status"] == "retrieved" for r in all_records), failed=sum(r["status"] == "failed" for r in all_records))))


if __name__ == "__main__":
    main()
