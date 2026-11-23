"""Acquire open public geospatial inputs for Harappa, Lakhanjo-Daro and Rupnagar.

Stores all downloaded rasters, mosaics and OSM extracts locally under
data/raw/2026-11-23-living-towns-footprints/ (junctioned to D:) and writes
an acquisition manifest with SHA-256 checksums, URLs and physical paths.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from PIL import Image, TiffImagePlugin

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw" / "2026-11-23-living-towns-footprints"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "indus-valley-script-research/1.0 (https://github.com/indus_valley_script; contact=research)",
    "Accept": "*/*",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record_file(path: Path, url: str, product: str, license_str: str, extra: dict | None = None) -> dict:
    rec = {
        "logical_path": path.relative_to(ROOT).as_posix(),
        "physical_path": os.path.realpath(str(path)),
        "url": url,
        "product": product,
        "license": license_str,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        rec.update(extra)
    return rec


def fetch_worldcover_cog_window(
    tile_code: str,
    bbox_w_s_e_n: tuple[float, float, float, float],
    out_tif: Path,
    out_meta: Path,
) -> dict:
    """Read only the intersecting 1024x1024 DEFLATE tiles of an ESA WorldCover 2021 v200 COG."""
    url = f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile_code}_Map.tif"
    r = requests.get(url, headers={**HEADERS, "Range": "bytes=0-32767"}, timeout=30)
    r.raise_for_status()
    hdr = r.content
    bo = "<" if hdr[:2] == b"II" else ">"
    magic = struct.unpack(bo + "H", hdr[2:4])[0]
    assert magic == 42, f"Expected classic TIFF, got magic={magic}"
    ifd_off = struct.unpack(bo + "I", hdr[4:8])[0]
    n_entries = struct.unpack(bo + "H", hdr[ifd_off : ifd_off + 2])[0]

    tags = {}
    for i in range(n_entries):
        off = ifd_off + 2 + i * 12
        tag, typ, cnt, val = struct.unpack(bo + "HHII", hdr[off : off + 12])
        tags[tag] = (typ, cnt, val)

    img_w = tags[256][2]
    img_h = tags[257][2]
    comp = tags[259][2]
    tile_w = tags[322][2]
    tile_h = tags[323][2]
    assert comp == 8, f"Expected DEFLATE compression (8), got {comp}"

    def read_range(start: int, length: int) -> bytes:
        if start + length <= len(hdr):
            return hdr[start : start + length]
        rr = requests.get(
            url,
            headers={**HEADERS, "Range": f"bytes={start}-{start + length - 1}"},
            timeout=30,
        )
        rr.raise_for_status()
        return rr.content

    scale = struct.unpack(bo + "3d", read_range(tags[33550][2], 24))
    tie = struct.unpack(bo + "6d", read_range(tags[33922][2], 48))
    sx, sy = scale[0], scale[1]
    origin_lon, origin_lat = tie[3], tie[4]

    n_tiles = tags[324][1]
    tile_offsets = struct.unpack(bo + f"{n_tiles}I", read_range(tags[324][2], n_tiles * 4))
    tile_counts = struct.unpack(bo + f"{n_tiles}I", read_range(tags[325][2], n_tiles * 4))

    w, s, e, n = bbox_w_s_e_n
    c0 = max(0, int(math.floor((w - origin_lon) / sx)))
    c1 = min(img_w, int(math.ceil((e - origin_lon) / sx)))
    r0 = max(0, int(math.floor((origin_lat - n) / sy)))
    r1 = min(img_h, int(math.ceil((origin_lat - s) / sy)))

    tiles_across = (img_w + tile_w - 1) // tile_w
    tc0, tc1 = c0 // tile_w, (c1 - 1) // tile_w
    tr0, tr1 = r0 // tile_h, (r1 - 1) // tile_h

    out = np.zeros((r1 - r0, c1 - c0), dtype=np.uint8)
    fetched_tiles = 0
    for tr in range(tr0, tr1 + 1):
        for tc in range(tc0, tc1 + 1):
            tidx = tr * tiles_across + tc
            raw_bytes = read_range(tile_offsets[tidx], tile_counts[tidx])
            arr = np.frombuffer(zlib.decompress(raw_bytes), dtype=np.uint8).reshape(tile_h, tile_w)
            fetched_tiles += 1

            # Intersect tile bounds with requested window
            tr_start, tc_start = tr * tile_h, tc * tile_w
            ir0 = max(r0, tr_start)
            ir1 = min(r1, tr_start + tile_h)
            ic0 = max(c0, tc_start)
            ic1 = min(c1, tc_start + tile_w)
            out[ir0 - r0 : ir1 - r0, ic0 - c0 : ic1 - c0] = arr[
                ir0 - tr_start : ir1 - tr_start, ic0 - tc_start : ic1 - tc_start
            ]

    win_lon = origin_lon + c0 * sx
    win_lat = origin_lat - r0 * sy

    # Write clean GeoTIFF with ModelPixelScaleTag (33550) & ModelTiepointTag (33922)
    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[33550] = (sx, sy, 0.0)
    ifd[33922] = (0.0, 0.0, 0.0, win_lon, win_lat, 0.0)
    ifd[34737] = "WGS 84|"
    im = Image.fromarray(out, mode="L")
    im.save(out_tif, format="TIFF", tiffinfo=ifd, compression="tiff_deflate")

    meta = {
        "tile_code": tile_code,
        "url": url,
        "shape": [int(out.shape[0]), int(out.shape[1])],
        "origin_lon": win_lon,
        "origin_lat": win_lat,
        "pixel_scale_deg": [sx, sy],
        "bounds_w_s_e_n": [win_lon, win_lat - out.shape[0] * sy, win_lon + out.shape[1] * sx, win_lat],
        "fetched_cog_tiles": fetched_tiles,
        "class_counts": {str(int(k)): int(v) for k, v in zip(*np.unique(out, return_counts=True))},
    }
    out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return record_file(out_tif, url, f"ESA WorldCover 10m 2021 v200 ({tile_code} window)", "CC BY 4.0", extra=meta)


def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def fetch_esri_mosaic(
    name: str,
    bbox_w_s_e_n: tuple[float, float, float, float],
    z: int,
    out_dir: Path,
) -> dict:
    """Fetch an Esri World Imagery slippy-tile mosaic and save PNG + georef JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    w, s, e, n = bbox_w_s_e_n
    x0, y0 = lonlat_to_tile(w, n, z)
    x1, y1 = lonlat_to_tile(e, s, z)
    cols = x1 - x0 + 1
    rows = y1 - y0 + 1
    base_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile"

    def fetch_one(xy):
        x, y = xy
        u = f"{base_url}/{z}/{y}/{x}"
        for attempt in range(3):
            try:
                rr = requests.get(u, headers=HEADERS, timeout=25)
                if rr.status_code == 200:
                    from io import BytesIO
                    return (x, y, Image.open(BytesIO(rr.content)).convert("RGB"))
            except Exception:
                time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"Failed tile {u}")

    coords = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
    mosaic = Image.new("RGB", (cols * 256, rows * 256))
    with ThreadPoolExecutor(max_workers=8) as ex:
        for x, y, tile_im in ex.map(fetch_one, coords):
            mosaic.paste(tile_im, ((x - x0) * 256, (y - y0) * 256))

    stem = f"{name}_z{z}_x{x0}-{x1}_y{y0}-{y1}"
    png_path = out_dir / f"{stem}.png"
    jpg_path = out_dir / f"{stem}_overview.jpg"
    json_path = out_dir / f"{stem}.json"

    mosaic.save(png_path, format="PNG")
    ov = mosaic.copy()
    ov.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    ov.save(jpg_path, format="JPEG", quality=88)

    meta = {
        "name": name,
        "service": "Esri World Imagery",
        "z": z,
        "x0": x0,
        "x1": x1,
        "y0": y0,
        "y1": y1,
        "width_px": cols * 256,
        "height_px": rows * 256,
        "global_px_x0": x0 * 256,
        "global_px_y0": y0 * 256,
        "tile_count": len(coords),
        "png_file": png_path.name,
    }
    json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return record_file(
        png_path,
        f"{base_url}/{z}/{{y}}/{{x}}",
        f"Esri World Imagery z{z} mosaic ({name})",
        "Esri World Imagery terms; local-only visual reference",
        extra=meta,
    )


def fetch_osm_overpass(name: str, bbox_w_s_e_n: tuple[float, float, float, float], out_path: Path) -> dict | None:
    """Fetch OpenStreetMap roads, buildings, landuse and landmarks via Overpass API."""
    w, s, e, n = bbox_w_s_e_n
    query = (
        f"[out:json][timeout:45];("
        f"way({s},{w},{n},{e})[highway];"
        f"way({s},{w},{n},{e})[landuse];"
        f"way({s},{w},{n},{e})[leisure];"
        f"way({s},{w},{n},{e})[natural];"
        f"way({s},{w},{n},{e})[historic];"
        f"way({s},{w},{n},{e})[amenity];"
        f"node({s},{w},{n},{e})[name];"
        f"way({s},{w},{n},{e})[name];"
        f");out body;>;out skel qt;"
    )
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]
    for ep in endpoints:
        try:
            r = requests.post(
                ep,
                data={"data": query},
                headers={
                    "User-Agent": "indus-valley-script-research/1.0",
                    "Accept": "application/json",
                },
                timeout=60,
            )
            if r.status_code == 200 and r.text.strip().startswith("{"):
                out_path.write_text(r.text, encoding="utf-8")
                d = json.loads(r.text)
                return record_file(
                    out_path,
                    ep,
                    f"OpenStreetMap Overpass extract ({name})",
                    "ODbL 1.0",
                    extra={"bbox_w_s_e_n": list(bbox_w_s_e_n), "element_count": len(d.get("elements", []))},
                )
            print(f"  Overpass {ep} returned {r.status_code} for {name}")
        except Exception as exc:
            print(f"  Overpass {ep} failed for {name}: {exc}")
        time.sleep(2.0)
    return None


def main():
    records = []

    # 1. ESA WorldCover 2021 v200 10m windows for Lakhanjo-Daro and Rupnagar
    wc_dir = RAW_DIR / "worldcover"
    wc_dir.mkdir(parents=True, exist_ok=True)
    print("Fetching ESA WorldCover 2021 v200 windows...")
    records.append(
        fetch_worldcover_cog_window(
            "N27E066",
            (68.820, 27.705, 68.875, 27.748),
            wc_dir / "ESA_WorldCover_2021_lakhanjo_daro_N27E066.tif",
            wc_dir / "ESA_WorldCover_2021_lakhanjo_daro_N27E066.json",
        )
    )
    records.append(
        fetch_worldcover_cog_window(
            "N30E075",
            (76.505, 30.945, 76.560, 30.990),
            wc_dir / "ESA_WorldCover_2021_rupnagar_N30E075.tif",
            wc_dir / "ESA_WorldCover_2021_rupnagar_N30E075.json",
        )
    )
    print("  WorldCover windows saved.")

    # 2. Esri World Imagery mosaics for Lakhanjo-Daro and Rupnagar
    mos_dir = RAW_DIR / "mosaics"
    print("Fetching Esri World Imagery mosaics...")
    records.append(fetch_esri_mosaic("lakhanjo_daro", (68.836, 27.717, 68.858, 27.734), 17, mos_dir))
    records.append(fetch_esri_mosaic("lakhanjo_daro", (68.840, 27.720, 68.855, 27.732), 18, mos_dir))
    records.append(fetch_esri_mosaic("rupnagar", (76.522, 30.958, 76.544, 30.975), 17, mos_dir))
    records.append(fetch_esri_mosaic("rupnagar", (76.526, 30.961, 76.539, 30.972), 18, mos_dir))
    print("  Esri mosaics saved.")

    # 3. OpenStreetMap Overpass extracts for all three sites
    osm_dir = RAW_DIR / "osm"
    osm_dir.mkdir(parents=True, exist_ok=True)
    print("Fetching OpenStreetMap Overpass extracts...")
    for sname, bbox in [
        ("harappa", (72.852, 30.620, 72.878, 30.640)),
        ("lakhanjo_daro", (68.835, 27.715, 68.860, 27.736)),
        ("rupnagar", (76.520, 30.957, 76.546, 30.976)),
    ]:
        rec = fetch_osm_overpass(sname, bbox, osm_dir / f"osm_{sname}.json")
        if rec:
            records.append(rec)
            print(f"  OSM {sname}: {rec['element_count']} elements")
        time.sleep(1.5)

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "logical_root": RAW_DIR.relative_to(ROOT).as_posix(),
        "physical_root": os.path.realpath(str(RAW_DIR)),
        "files": records,
    }
    mpath = RAW_DIR / "acquisition-manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Done. Wrote {len(records)} records to {mpath}")


if __name__ == "__main__":
    main()
