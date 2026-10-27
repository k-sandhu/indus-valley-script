"""Acquire only the named primary-source routes for the western plan audit."""
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west")
ROUTES = [
    ("harappa-tr54-top.html", "https://www.harappa.com/slide/trench-54-top-plan"),
    ("harappa-tr54-section.html", "https://www.harappa.com/slide/trench-54-section-plan"),
    ("harappa-tr54-detail.html", "https://www.harappa.com/slide/trench-54-detail-plan"),
    ("harappa-inside-wall250.html", "https://www.harappa.com/slide/structures-inside-perimeter-wall"),
    ("harappa-tr54-west-section.html", "https://www.harappa.com/slide/section-view-walls-and-platforms"),
    ("harappa-tr54-detail.jpg", "https://www.harappa.com/sites/default/files/slides/trench-54-detail-plan-harappa.jpg"),
    ("harappa-inside-wall250.jpg", "https://www.harappa.com/sites/default/files/slides/85_3.jpg"),
    ("harappa-tr54-west-section.jpg", "https://www.harappa.com/sites/default/files/slides/harappa-mound-e-section-walls.jpg"),
    ("lothal-archive-search.json", "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": "title:(Lothal) AND creator:(Rao)", "output": "json", "rows": 30, "fl[]": "identifier,title,creator"})),
    ("lothal-held-archive-metadata.json", "https://archive.org/metadata/masi78lothalaharappanporttownraos.r.part1platesmissing_443_k"),
]
ROUTES_V2 = [
    ("harappa-tr54-top.png", "https://www.harappa.com/sites/default/files/slides/46m.png"),
    ("harappa-tr54-section.jpg", "https://www.harappa.com/sites/default/files/slides/trench-54-section-plan-harappa.jpg"),
    ("harappa-mound-e-et.html", "https://www.harappa.com/slide/harappa-1993-2001-mound-eet-plan"),
    ("harappa-mound-e-et.jpg", "https://www.harappa.com/sites/default/files/slides/72_3.jpg"),
    ("harappa-tr39-period2.html", "https://www.harappa.com/slide/plan-kot-diji-phase-levels"),
    ("harappa-tr39-period3.html", "https://www.harappa.com/slide/plan-harappa-phase-remains"),
    ("harappa-tr39-period2.jpg", "https://www.harappa.com/sites/default/files/slides/26_3.jpg"),
    ("harappa-tr39-period3.jpg", "https://www.harappa.com/sites/default/files/slides/63_3.jpg"),
    ("lothal-archive-search-broad.json", "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": "title:lothal", "output": "json", "rows": 50, "fl[]": "identifier,title,creator"})),
]


def acquire(route):
    name, url = route
    path = LOCAL / "acquired" / name
    if path.exists():
        raise FileExistsError(path)
    row = dict(url=url, requested_utc=datetime.now(timezone.utc).isoformat(), rights_status="rights-unverified", handling="local-only")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research source audit"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read()
            row.update(status="acquired", http_status=response.status, final_url=response.url,
                       content_type=response.headers.get("content-type"), bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
        path.write_bytes(body)
        row.update(physical_path=str(path), logical_path=f"data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west/acquired/{name}")
    except (urllib.error.URLError, TimeoutError) as exc:
        row.update(status="failed", error=str(exc), http_status=getattr(exc, "code", None))
    return row


if __name__ == "__main__":
    (LOCAL / "acquired").mkdir(exist_ok=True)
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    assert version in {"v1", "v2"}
    target = LOCAL / f"acquisition-routes-{version}.json"
    if target.exists():
        raise FileExistsError(target)
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(acquire, ROUTES if version == "v1" else ROUTES_V2))
    target.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{"url": r["url"], "status": r["status"], "http_status": r.get("http_status"), "bytes": r.get("bytes")} for r in rows]))
