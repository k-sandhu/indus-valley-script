"""Acquire pinned primary-source witnesses for the local-only khipu control.

This helper downloads text, a database and an author manuscript. It calculates
no numerical relation and keeps every acquired byte under data/six-hour/khipu.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/six-hour/khipu/puruchuco-2026-10-02"
OUT = ROOT / "experiments/2026-10-02-six-hour/khipu-control"
PIN = "4039ca51f4de661d80d0160596309c983a62a9c7"
REPO = "https://raw.githubusercontent.com/khipulab/open-khipu-repository/" + PIN

SOURCES = [
    ("okr-commit.json", "https://api.github.com/repos/khipulab/open-khipu-repository/commits/" + PIN,
     "version witness", "GitHub API metadata; local source witness"),
    ("okr-tree.json", "https://api.github.com/repos/khipulab/open-khipu-repository/git/trees/" + PIN + "?recursive=1",
     "coverage witness", "GitHub API metadata; local source witness"),
    ("okr-README.md", REPO + "/README.md", "repository description", "repository MIT declaration; data scope under review"),
    ("okr-LICENSE", REPO + "/LICENSE", "license witness", "MIT license document; scope recorded separately"),
    ("okr-kh-numbers.csv", REPO + "/data/okr-kh-numbers.csv", "identifier concordance", "data rights under review; local-only"),
    ("khipu.db", REPO + "/data/khipu.db", "cord and knot records", "data rights under review; local-only"),
    ("kfg-puruchuco.html", "https://khipufieldguide.com/notebook/appendix/notebooks/12%20-%20Replicating%20Purucucho.html",
     "author replication", "site content rights under review; local-only"),
    ("urton-2005-khipu-archives.pdf", "https://dash.harvard.edu/server/api/core/bitstreams/7312037e-6b09-6bd4-e053-0100007fdf3b/content",
     "author manuscript and object group witness", "Harvard Other Posted Material; local-only"),
]

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "acquisition.json"
    if manifest_path.exists():
        raise FileExistsError("Acquisition manifest already exists; use a fresh dated acquisition.")
    records = []
    for filename, url, role, rights in SOURCES:
        path = RAW / filename
        if path.exists():
            raise FileExistsError(path)
        request = urllib.request.Request(url, headers={"User-Agent": "Indus research source audit"})
        started = now()
        with urllib.request.urlopen(request, timeout=180) as response:
            blob = response.read()
            headers = dict(response.headers.items())
            status = response.status
            final_url = response.url
        path.write_bytes(blob)
        records.append({
            "id": filename, "source_url": url, "final_url": final_url,
            "local_path": path.relative_to(ROOT).as_posix(), "role": role,
            "started_utc": started, "completed_utc": now(), "http_status": status,
            "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
            "etag": headers.get("ETag"), "last_modified": headers.get("Last-Modified"),
            "content_type": headers.get("Content-Type"), "rights_note": rights,
            "redistribution": "local-only",
        })
        print(json.dumps({"id": filename, "bytes": len(blob), "sha256": records[-1]["sha256"]}))
    manifest = {
        "created_utc": now(), "repository_pin": PIN,
        "purpose": "Acquisition and source audit; numerical outcomes have not been computed by this helper.",
        "raw_policy": "All acquired assets remain local-only pending source-specific review.",
        "sources": records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Saved " + manifest_path.relative_to(ROOT).as_posix())

if __name__ == "__main__":
    main()
