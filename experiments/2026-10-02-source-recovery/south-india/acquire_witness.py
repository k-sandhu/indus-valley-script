"""Save a named public witness and a separate byte-level acquisition record."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[3]

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--name", required=True)
args = parser.parse_args()
if Path(args.name).name != args.name:
    raise ValueError("Supply a filename without directory components")
raw = ROOT / "data/raw/2026-10-02-source-recovery/south-india"
dest = raw / args.name
manifest = Path(__file__).parent / (args.name + ".acquisition.json")
if dest.exists() or manifest.exists():
    raise FileExistsError("Choose a new witness name; existing endpoints are preserved")
raw.mkdir(parents=True, exist_ok=True)
start = dt.datetime.now(dt.timezone.utc).isoformat()
response = requests.get(args.url, timeout=60)
dest.write_bytes(response.content)
record = {
    "source_url": args.url, "final_url": response.url,
    "retrieval_started_utc": start,
    "retrieval_finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "http_status": response.status_code,
    "content_type": response.headers.get("Content-Type"),
    "local_path": dest.relative_to(ROOT).as_posix(),
    "bytes": len(response.content),
    "sha256": hashlib.sha256(response.content).hexdigest(),
    "rights_status": "rights-unverified; local-only",
}
manifest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record))
