"""Freeze the read-only public routes used by the graffiti portal client."""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
BASE = "https://api.tamilknowledgecampus.in/graffiti/"


def acquire(route, raw):
    url = BASE + route
    dest = raw / (route.replace("/", "-") + ".json")
    if dest.exists():
        raise FileExistsError(dest)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        response = requests.get(url, timeout=45)
        dest.write_bytes(response.content)
        return {
            "url": url, "retrieved_utc": now, "final_url": response.url,
            "http_status": response.status_code,
            "local_path": str(dest.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(response.content),
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "content_type": response.headers.get("Content-Type"),
            "rights_status": "rights-unverified; local-only",
        }
    except requests.RequestException as error:
        return {"url": url, "retrieved_utc": now, "error": str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--families", action="store_true")
    args = parser.parse_args()
    raw = ROOT / "data/raw/2026-10-02-connections-and-priority/south-india" / args.run
    out = Path(__file__).parent / args.run
    raw.mkdir(parents=True, exist_ok=False)
    out.mkdir(parents=True, exist_ok=False)
    routes = ["base-sign", "sites", "options", "indus", "concordance", "fields-symbols"]
    if args.families:
        routes.extend(f"sign/{i}" for i in range(1, 43))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda route: acquire(route, raw), routes))
    manifest = {
        "source": "Tamil Nadu State Department of Archaeology / RMRL graffiti portal",
        "client_url": "https://tngraffiti.in/assets/index-D7vrsNCw.js",
        "route_basis": "Public deployed client configuration and its GET requests",
        "reads": records,
    }
    (out / "acquisition.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": args.run, "reads": len(records),
                      "http_200": sum(r.get("http_status") == 200 for r in records),
                      "bytes": sum(r.get("bytes", 0) for r in records)}))


if __name__ == "__main__":
    main()
