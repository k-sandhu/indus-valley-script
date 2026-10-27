"""Acquire alternate primary witnesses discovered after acquisition-v1."""
import concurrent.futures
import json
from datetime import datetime, timezone

from acquire_sources import acquire, HERE
from build_register import SOURCES

URLS = {
    "LT-S08": "https://zenodo.org/records/3385120/files/IAR%201957-58.pdf?download=1",
    "LT-S09": "https://zenodo.org/records/3386794/files/IAR%201975-76.pdf?download=1",
    "LT-S11": "https://zenodo.org/records/1408087/files/IAR%201962%20-%2063.pdf?download=1",
    "LT-S03": "https://icac.cat/recerca/produccio-cientifica/publicacio/reconstructing-long-term-settlement-histories-on-complex-alluvial-floodplains-by-integrating-historical-map-analysis-and-remote-sensing-an-archaeological-analysis-of-the-landscape-of-the-indus-river/",
}


def main():
    out = HERE / "acquisition-v2.json"
    if out.exists():
        raise SystemExit("Refusing to overwrite acquisition-v2.json")
    selections = [dict(s, url=URLS[s["id"]], alternate_urls=[], filename_tag="v2-")
                  for s in SOURCES if s["id"] in URLS]
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for attempts in pool.map(acquire, selections):
            records.extend(attempts)
    result = dict(schema_version="1.0", created_at=datetime.now(timezone.utc).isoformat(),
                  purpose="Alternate public primary scans for timed-out government routes, and institutional author metadata. v1 remains unchanged.", records=records)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(retrieved=sum(r["status"] == "retrieved" for r in records), failed=sum(r["status"] == "failed" for r in records))))


if __name__ == "__main__":
    main()
