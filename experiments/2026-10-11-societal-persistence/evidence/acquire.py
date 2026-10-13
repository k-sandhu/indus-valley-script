"""Acquire local-only documentary witnesses into a new, never-reused directory."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    requests = json.loads(args.request_file.read_text(encoding="utf-8"))
    if len({r["filename"] for r in requests}) != len(requests):
        raise ValueError("Duplicate target filenames")

    def get(row: dict) -> dict:
        result = dict(row)
        result["retrieved_utc"] = datetime.now(timezone.utc).isoformat()
        result["redistribution"] = "local-only documentary witness"
        try:
            req = urllib.request.Request(row["url"], headers={"User-Agent": "Mozilla/5.0 (scholarly source inspection)"})
            bound = row.get("max_bytes", 120_000_000)
            with urllib.request.urlopen(req, timeout=90) as response:
                payload = response.read(bound + 1)
                if len(payload) > bound:
                    raise ValueError(f"Witness exceeds {bound} byte acquisition bound")
                result["resolved_url"] = response.url
                result["content_type"] = response.headers.get("Content-Type")
            target = args.output_dir / row["filename"]
            target.write_bytes(payload)
            result.update(status="acquired", bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), path=target.as_posix(), signature=payload[:12].hex())
        except Exception as exc:
            result.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        return result

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(get, requests))
    (args.output_dir / "acquisition.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in results:
        print(row["filename"], row["status"], row.get("bytes", row.get("error")))


if __name__ == "__main__":
    main()
