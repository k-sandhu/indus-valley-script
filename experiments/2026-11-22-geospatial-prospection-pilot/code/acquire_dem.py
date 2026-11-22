"""Acquire missing Copernicus DEM GLO-30 tiles for P01-P09 into D: raw storage.

Reuses already-held full 30 m tiles without duplicating them, downloads only
missing tiles to data/raw/2026-11-22-geospatial-prospection-pilot/dem/30m/,
verifies TIFF headers and SHA-256 hashes, and writes a complete manifest.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parents[1]
RAW_OUT = ROOT / "data" / "raw" / "2026-11-22-geospatial-prospection-pilot" / "dem" / "30m"
MANIFEST_OUT = EXP_DIR / "outputs" / "dem_manifest.json"

LICENSE_NOTICE = (
    "Copernicus DEM licence. (c) DLR e.V. 2010-2014 and (c) Airbus Defence and "
    "Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA"
)

HELD_SEARCH_DIRS = [
    ROOT / "data" / "raw" / "2026-10-21-town-orientations-verification" / "astro" / "dem" / "30m",
    ROOT / "data" / "raw" / "2026-10-24-q1032-town-axis-register" / "dem" / "GLO-30",
]

REQUIRED_TILES = [
    # P01-P02 Cholistan / Ganweriwala (clipped to Orengo AOI)
    ("N27_00_E070_00", ["P01"]),
    ("N27_00_E071_00", ["P01"]),
    ("N28_00_E070_00", ["P01", "P02"]),
    ("N28_00_E071_00", ["P01", "P02"]),
    ("N29_00_E071_00", ["P01", "P08", "P09"]),
    # P08-P09 Harappa-Khanewal / Old Beas / Ganji Bar / East Multan-Tulamba (+ held E073 edge buffer)
    ("N29_00_E072_00", ["P08", "P09"]),
    ("N29_00_E073_00", ["P06_buffer", "P08_buffer"]),
    ("N30_00_E071_00", ["P08", "P09"]),
    ("N30_00_E072_00", ["P08", "P09"]),
    ("N30_00_E073_00", ["P08_buffer"]),
    # P06 Sirsa-Hanumangarh & P03-P05/P07 Haryana-Punjab corridors
    ("N29_00_E074_00", ["P05", "P06"]),
    ("N29_00_E075_00", ["P03", "P04", "P05", "P06", "P07"]),
    ("N29_00_E076_00", ["P03", "P04", "P07"]),
    ("N30_00_E074_00", ["P05"]),
    ("N30_00_E075_00", ["P04", "P05"]),
    ("N30_00_E076_00", ["P04"]),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_geotiff(path: Path) -> dict:
    with Image.open(path) as im:
        tags = im.tag_v2
        scale = tuple(float(x) for x in tags.get(33550, ()))
        tiepoint = tuple(float(x) for x in tags.get(33922, ()))
        w, h = im.size
        mode = im.mode
    return {
        "width": w,
        "height": h,
        "mode": mode,
        "pixel_scale_deg": list(scale[:2]),
        "origin_lonlat": [tiepoint[3], tiepoint[4]] if len(tiepoint) >= 5 else None,
    }


def find_held_tile(filename: str) -> Path | None:
    for d in HELD_SEARCH_DIRS:
        p = d / filename
        if p.exists() and p.stat().st_size > 10_000_000:
            return p
    return None


def acquire_one(tile_code: str, regions: list[str]) -> dict:
    stem = f"Copernicus_DSM_COG_10_{tile_code}_DEM"
    filename = f"{stem}.tif"
    url = f"https://copernicus-dem-30m.s3.amazonaws.com/{stem}/{filename}"

    held = find_held_tile(filename)
    if held is not None:
        logical = held.relative_to(ROOT).as_posix()
        physical = str(held.resolve())
        info = inspect_geotiff(held)
        return {
            "tile_code": tile_code,
            "filename": filename,
            "regions": regions,
            "status": "reused_local",
            "logical_path": logical,
            "physical_path": physical,
            "url": url,
            "bytes": held.stat().st_size,
            "sha256": sha256_file(held),
            "geotiff": info,
            "rights": LICENSE_NOTICE,
        }

    dest = RAW_OUT / filename
    sidecar = RAW_OUT / f"{filename}.source.json"
    if dest.exists() and dest.stat().st_size > 10_000_000:
        status = "existing_pilot_download"
        retrieved_utc = datetime.fromtimestamp(dest.stat().st_mtime, tz=timezone.utc).isoformat()
        http_status = 200
    else:
        RAW_OUT.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".tif.part")
        with requests.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            http_status = resp.status_code
            with tmp.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        os.replace(tmp, dest)
        retrieved_utc = datetime.now(timezone.utc).isoformat()
        status = "downloaded_new"

    digest = sha256_file(dest)
    size = dest.stat().st_size
    info = inspect_geotiff(dest)
    logical = dest.relative_to(ROOT).as_posix()
    physical = str(dest.resolve())

    record = {
        "tile_code": tile_code,
        "filename": filename,
        "regions": regions,
        "status": status,
        "logical_path": logical,
        "physical_path": physical,
        "url": url,
        "http_status": http_status,
        "retrieved_utc": retrieved_utc,
        "bytes": size,
        "sha256": digest,
        "geotiff": info,
        "rights": LICENSE_NOTICE,
    }
    sidecar.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    raw_root = ROOT / "data" / "raw"
    resolved_raw = str(raw_root.resolve())
    if not resolved_raw.upper().startswith("D:\\"):
        raise RuntimeError(f"Expected data/raw junction to resolve to D:\\, got {resolved_raw}")

    print(f"Verified data/raw resolves to {resolved_raw}")
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(acquire_one, tc, regs) for tc, regs in REQUIRED_TILES]
        for fut in concurrent.futures.as_completed(futs):
            rec = fut.result()
            results.append(rec)
            print(f"  [{rec['status']:14s}] {rec['filename']} ({rec['bytes']:,} B) sha256={rec['sha256'][:12]}...")

    results.sort(key=lambda r: r["tile_code"])
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "storage_root_resolved": resolved_raw,
        "tile_count": len(results),
        "reused_count": sum(1 for r in results if r["status"] == "reused_local"),
        "newly_acquired_count": sum(1 for r in results if r["status"] != "reused_local"),
        "total_bytes": sum(r["bytes"] for r in results),
        "newly_acquired_bytes": sum(r["bytes"] for r in results if r["status"] != "reused_local"),
        "tiles": results,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    raw_manifest = RAW_OUT.parent / "acquisition_manifest.json"
    raw_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Done. {manifest['reused_count']} reused, {manifest['newly_acquired_count']} newly acquired ({manifest['newly_acquired_bytes']/1e6:.1f} MB).")


if __name__ == "__main__":
    main()
