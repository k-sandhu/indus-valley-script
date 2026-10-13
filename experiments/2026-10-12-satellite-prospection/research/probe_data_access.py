"""Bounded unsigned catalogue, document and TIFF-header access probes.

The probe reads metadata and at most 512 bytes of each raster asset. It neither
extracts image windows nor computes a prospection score. Replays require a new
report path; acquired witnesses use a fresh SPATIAL_DATA_ timestamp prefix.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

EXPERIMENT = Path(__file__).resolve().parents[1]
ROOT = EXPERIMENT.parents[1]
RAW = ROOT / "data/raw/2026-10-12-satellite-prospection"
PREFIX = "SPATIAL_DATA_"
V1 = "https://earth-search.aws.element84.com/v1"
V2 = "https://earth-search.aws.element84.com/v2"
BOX = [71.10, 28.55, 71.20, 28.65]
DOCUMENTS = [
    ("D01", "earth-search-readme", "https://raw.githubusercontent.com/Element84/earth-search/main/README.md", ".md"),
    ("D02", "earth-search-sentinel2", "https://raw.githubusercontent.com/Element84/earth-search/main/docs/collections/sentinel-2-l2a.md", ".md"),
    ("D03", "earth-search-copdem", "https://raw.githubusercontent.com/Element84/earth-search/main/docs/collections/cop-dem.md", ".md"),
    ("D04", "sentiwiki-products", "https://sentiwiki.copernicus.eu/web/s2-products", ".html"),
    ("D05", "sentiwiki-processing", "https://sentiwiki.copernicus.eu/web/s2-processing", ".html"),
    ("D06", "sentinel-legal-notice", "https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice", ".pdf"),
    ("D07", "aws-sentinel-cogs", "https://registry.opendata.aws/sentinel-2-l2a-cogs/", ".html"),
    ("D08", "aws-copdem", "https://registry.opendata.aws/copernicus-dem/", ".html"),
    ("D09", "aws-copdem-readme", "https://copernicus-dem-30m.s3.amazonaws.com/readme.html", ".html"),
    ("D10", "cdse-copdem", "https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM", ".html"),
    ("D11", "copdem-handbook", "https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf", ".pdf"),
    ("D12", "copdem-license-annex", "https://s3.waw3-1.cloudferro.com/swift/v1/portal_uploads_prod/CSCDA_ESA_Mission-specific_Annex_31_Oct_22_latest.pdf", ".pdf"),
    ("D13", "worldcover-data", "https://esa-worldcover.org/en/data-access", ".html"),
    ("D14", "worldcover-manual", "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf", ".pdf"),
    ("D15", "worldcover-validation", "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PVR_V2.0.pdf", ".pdf"),
    ("D16", "aws-worldcover", "https://registry.opendata.aws/esa-worldcover/", ".html"),
    ("D17", "earth-search-offset-issue", "https://api.github.com/repos/Element84/earth-search/issues/66", ".json"),
    ("D18", "raster-extension", "https://raw.githubusercontent.com/stac-extensions/raster/v1.1.0/README.md", ".md"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def request(label, url, *, params=None, cap=1048576, suffix=".json", headers=None, save=True, stamp=""):
    start = time.monotonic()
    record = {"id": label, "method": "GET", "url": url, "params": params,
              "unsigned": True, "authentication_sent": False, "response_cap_bytes": cap}
    session = requests.Session()
    # Avoid netrc credentials and implicit AWS signing. No credentials are read.
    session.trust_env = False
    session.headers.update({"User-Agent": "Indus-research-bounded-metadata-probe/2026-10-12"})
    try:
        with session.get(url, params=params, headers=headers, timeout=(10, 25), stream=True) as response:
            record.update(status_code=response.status_code, final_url=response.url,
                          response_headers={k: response.headers.get(k) for k in
                                            ["Content-Type", "Content-Length", "Content-Range", "Accept-Ranges", "ETag", "Last-Modified"]})
            data = bytearray()
            for chunk in response.iter_content(chunk_size=min(8192, cap + 1)):
                data.extend(chunk)
                if len(data) > cap:
                    break
            oversized = len(data) > cap
            data = bytes(data[:cap])
            record.update(bytes_read=len(data), cap_exceeded=oversized, body_sha256=sha(data))
            if save and not oversized:
                filename = f"{PREFIX}{stamp}_{label}{suffix}"
                target = RAW / filename
                with target.open("xb") as stream:
                    stream.write(data)
                record["raw_witness"] = {"path": relative(target), "bytes": len(data), "sha256": sha(data),
                                          "handling": "ignored local-only metadata or source document"}
            if suffix == ".json" and not oversized:
                try:
                    decoded = json.loads(data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    decoded = None
            else:
                decoded = None
            record["elapsed_seconds"] = round(time.monotonic() - start, 3)
            return record, decoded, data
    except requests.RequestException as exc:
        record.update(error_type=type(exc).__name__, error=str(exc), elapsed_seconds=round(time.monotonic() - start, 3))
        return record, None, b""
    finally:
        session.close()


def item_summary(item):
    props = item.get("properties", {})
    retained = {k: v for k, v in props.items() if k.startswith(("s2:", "eo:", "proj:", "earthsearch:", "storage:"))
                or k in ["datetime", "created", "updated", "platform", "gsd", "grid:code"]}
    asset_fields = ["href", "type", "title", "roles", "eo:bands", "raster:bands", "bands", "raster:scale", "raster:offset",
                    "raster:nodata", "raster:data_type", "proj:shape", "proj:transform", "proj:epsg", "proj:code",
                    "storage:refs", "storage:requester_pays"]
    wanted = {"red", "blue", "green", "nir", "nir08", "swir16", "swir22", "scl", "cloud", "cloud_probability", "data"}
    return {"item_id": item.get("id"), "collection": item.get("collection"), "stac_version": item.get("stac_version"),
            "bbox": item.get("bbox"), "properties": retained, "asset_keys": list(item.get("assets", {})),
            "assets": {k: {f: v[f] for f in asset_fields if f in v} for k, v in item.get("assets", {}).items() if k in wanted},
            "self_url": next((l["href"] for l in item.get("links", []) if l.get("rel") == "self"), None)}


def public_https(href):
    if href.startswith("https://"):
        return href
    parsed = urlparse(href)
    if parsed.scheme == "s3" and parsed.netloc == "copernicus-dem-30m":
        return f"https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com{parsed.path}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=EXPERIMENT / "research/data-access-probe.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Report exists. Preserve it and replay to a new path.")
    RAW.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    records = []
    documents = []
    jobs = [dict(label=d[0], url=d[2], cap=5 * 1048576, suffix=d[3], stamp=stamp) for d in DOCUMENTS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for record, _, _ in pool.map(lambda job: request(**job), jobs):
            documents.append(record)
    basic_jobs = [("API-v1", V1), ("API-v2", V2), ("collections-v1", V1 + "/collections"), ("collections-v2", V2 + "/collections")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        basic = list(pool.map(lambda job: request(job[0], job[1], stamp=stamp), basic_jobs))
    catalogues = []
    for record, decoded, _ in basic:
        records.append(record)
        if decoded:
            catalogues.append({"probe_id": record["id"], "stac_version": decoded.get("stac_version"),
                               "collection_ids": [c["id"] for c in decoded.get("collections", [])],
                               "collections": [{"id": c["id"], "license": c.get("license"),
                                                "license_links": [l for l in c.get("links", []) if l.get("rel") == "license"]}
                                               for c in decoded.get("collections", [])],
                               "conforms_to": decoded.get("conformsTo", [])})
    years = {2019: "2019-01-01T00:00:00Z/2019-12-31T23:59:59Z", 2024: "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
             2026: "2026-01-01T00:00:00Z/2026-10-11T23:59:59Z"}
    searches = []
    for api, collection, year in [(V1, "sentinel-2-c1-l2a", 2019), (V1, "sentinel-2-c1-l2a", 2024),
                                  (V1, "sentinel-2-c1-l2a", 2026), (V1, "sentinel-2-l2a", 2019),
                                  (V1, "sentinel-2-l2a", 2024), (V1, "sentinel-2-pre-c1-l2a", 2019),
                                  (V2, "sentinel-2-l2a", 2024)]:
        label = ("v2" if api == V2 else "v1") + "-" + collection + "-" + str(year)
        searches.append((label, api, {"collections": collection, "bbox": ",".join(map(str, BOX)), "datetime": years[year],
                                      "limit": 2, "query": json.dumps({"eo:cloud_cover": {"lt": 5}})}))
    for label, box in [("ganweriwala", BOX), ("kirthar", [67.4, 26.35, 67.6, 26.55]), ("kalibangan", [74.0, 29.35, 74.3, 29.65])]:
        searches.append(("dem-" + label, V1, {"collections": "cop-dem-glo-30", "bbox": ",".join(map(str, box)), "limit": 2}))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        search_responses = list(pool.map(lambda job: request(job[0], job[1] + "/search", params=job[2], stamp=stamp), searches))
    search_summaries = []
    range_jobs = []
    for record, decoded, _ in search_responses:
        records.append(record)
        items = decoded.get("features", []) if isinstance(decoded, dict) else []
        summary = {"probe_id": record["id"], "returned_count": len(items), "number_matched": decoded.get("numberMatched") if decoded else None,
                   "items": [item_summary(item) for item in items]}
        search_summaries.append(summary)
        if items:
            item = items[0]
            keys = ["data"] if record["id"].startswith("dem-") else ["red"]
            if record["id"] == "v1-sentinel-2-c1-l2a-2024":
                keys += ["nir", "swir16", "scl"]
            for key in keys:
                asset = item.get("assets", {}).get(key)
                href = public_https(asset["href"]) if asset else None
                if href:
                    range_jobs.append((record["id"] + "-" + key, href, item["id"], key))
    for tile in ["N27E069", "N24E066"]:
        range_jobs.append(("worldcover-" + tile, "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_" + tile + "_Map.tif", tile, "Map"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        ranges = list(pool.map(lambda job: request(job[0], job[1], cap=512, suffix=".bin", headers={"Range": "bytes=0-511"}, stamp=stamp), range_jobs))
    range_summaries = []
    for job, (record, _, prefix) in zip(range_jobs, ranges, strict=True):
        records.append(record)
        marker = prefix[:4]
        range_summaries.append({"probe_id": record["id"], "item_id": job[2], "asset_key": job[3], "url": job[1],
                                "status_code": record.get("status_code"), "content_range": record.get("response_headers", {}).get("Content-Range"),
                                "bytes_read": len(prefix), "tiff_magic_hex": marker.hex(),
                                "range_read_verified": record.get("status_code") == 206 and len(prefix) == 512 and marker in
                                [b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"],
                                "cap_exceeded": record.get("cap_exceeded"), "raw_witness": record.get("raw_witness")})
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "status": "bounded unsigned access observation",
              "environment": {"python": platform.python_version(), "requests": requests.__version__},
              "script": {"path": relative(Path(__file__).resolve()), "sha256": sha(Path(__file__).read_bytes())},
              "probe_bbox_lonlat": BOX, "selection": "Small box near a known settlement anchor; at most two catalogue items per search and 512-byte raster headers. No archaeological candidate evaluation.",
              "document_requests": documents, "catalogue_summaries": catalogues, "search_summaries": search_summaries,
              "range_read_summaries": range_summaries, "requests": records,
              "summary": {"document_requests": len(documents), "document_200": sum(r.get("status_code") == 200 and not r.get("cap_exceeded") for r in documents),
                          "catalogue_search_requests": len(records) - len(range_summaries), "range_requests": len(range_summaries),
                          "verified_range_reads": sum(r["range_read_verified"] for r in range_summaries),
                          "raster_bytes_read": sum(r["bytes_read"] for r in range_summaries)},
              "limits": "Catalogue availability and TIFF-header access do not verify pixel reflectance, local cloud-free coverage, DEM accuracy or archaeological interpretation. The collection license field is recorded separately from provider license terms."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": relative(args.output.resolve()), **report["summary"]}))


if __name__ == "__main__":
    main()
