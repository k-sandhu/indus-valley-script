"""Summarize every request made by this package and the terms witnesses into harvest/acquisition-record.json.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/acquisition_record.py
Reads data/raw/2026-10-13-museum-open-access/*/requests.jsonl and the Smithsonian bulk log.
"""
import json
from collections import Counter
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
RAW = ROOT / "data/raw/2026-10-13-museum-open-access"

TERMS = {
    "met": {"licence": "CC0 for objects with isPublicDomain true", "witness_url": "https://metmuseum.github.io/",
            "note": "The Met's API documentation states the CC0 waiver for its datasets; www.metmuseum.org/hubs/open-access returned HTTP 429."},
    "cleveland": {"licence": "CC0 (share_license_status per record)", "witness_url": "https://openaccess-api.clevelandart.org/"},
    "aic": {"licence": "CC0 for API data except the description field (CC BY 4.0); images by is_public_domain",
            "witness_url": "https://api.artic.edu/docs/"},
    "smithsonian": {"licence": "CC0 (Smithsonian Open Access); API needs an api.data.gov key, bulk bucket does not",
                    "witness_url": "s3://smithsonian-open-access (record field metadata_usage)"},
    "penn": {"licence": "Downloaded datasets CC BY 4.0; images for non-profit, education or personal use with credit",
             "witness_url": "https://collections.penn.museum/collections/objects/data.php",
             "note": "Image terms as recorded by the 12 October inventory (W19); the rights page returned HTTP 403/404 today."},
    "vam": {"licence": "V&A websites terms section 9: non-commercial use; no caching or storage of API content beyond four weeks",
            "witness_url": "https://www.vam.ac.uk/info/va-websites-terms-conditions", "delete_raw_by": "2026-11-10"},
    "bm": {"licence": "Website content CC BY-NC-SA 4.0 only where marked; robots.txt content signal search=yes, ai-train=no, use=reference",
           "witness_url": "https://www.britishmuseum.org/robots.txt",
           "note": "Collection search returned a Cloudflare challenge (HTTP 403); saved witnesses from 12 October used instead."},
}


def main():
    out = {"package": "experiments/2026-10-13-museum-open-access", "user_agent":
           "indus-valley-script-research/1.0 (+https://github.com/k-sandhu/indus-valley-script)", "routes": {}}
    for d in sorted(p for p in RAW.iterdir() if p.is_dir()):
        log = d / "requests.jsonl"
        if not log.exists():
            continue
        rows = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()]
        out["routes"][d.name] = {
            "requests": len(rows), "status_counts": dict(Counter(str(r["status"]) for r in rows)),
            "bytes": sum(r["bytes"] for r in rows),
            "first_utc": min(r["retrieved_utc"] for r in rows), "last_utc": max(r["retrieved_utc"] for r in rows),
            "terms": TERMS.get(d.name, {}),
        }
    bulk = RAW / "smithsonian" / "bulk-files.jsonl"
    if bulk.exists():
        rows = [json.loads(x) for x in bulk.read_text(encoding="utf-8").splitlines()]
        out["routes"].setdefault("smithsonian", {})["bulk_files"] = {
            "files": len(rows), "status_counts": dict(Counter(str(r["status"]) for r in rows)),
            "bytes": sum(r["bytes"] for r in rows), "records_scanned": sum(r["lines"] for r in rows),
            "matching_records": sum(r["matches"] for r in rows),
            "first_utc": min(r["retrieved_utc"] for r in rows), "last_utc": max(r["retrieved_utc"] for r in rows),
            "per_file_sha256": "data/raw/2026-10-13-museum-open-access/smithsonian/bulk-files.jsonl (local)"}
    penn_csv = [json.loads(x) for x in (RAW / "penn" / "requests.jsonl").read_text(encoding="utf-8").splitlines()
                if "Penn_Museum_Collections_Data.csv" in x]
    if penn_csv:
        out["key_files"] = {"penn_collections_csv": {k: penn_csv[0][k] for k in ("url", "retrieved_utc", "bytes", "sha256")}}
        out["key_files"]["penn_collections_csv"]["rows"] = 430871
    (PKG / "harvest" / "acquisition-record.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()
