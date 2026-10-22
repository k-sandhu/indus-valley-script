"""Esri World Imagery tile download, mosaicking and imagery metadata (role img-B).

Tiles are cached under data/raw/2026-10-21-town-axes/img-B/tiles/{z}/{y}/{x}.jpg,
which Git ignores. Global pixel coordinates follow the Web Mercator tile scheme:
x grows east, y grows south, 256 px per tile, origin at (-180 deg, +85.05 deg).
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "data" / "raw" / "2026-10-21-town-axes" / "img-B"
TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
IDENTIFY_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/identify"
ATTRIBUTION = "Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community"
UA = {"User-Agent": "indus-town-axes-research/1.0 (img-B measurer)"}


def lonlat_to_px(lon: float, lat: float, z: int) -> tuple[float, float]:
    n = 256 * 2 ** z
    x = (lon + 180.0) / 360.0 * n
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def px_to_lonlat(x: float, y: float, z: int) -> tuple[float, float]:
    n = 256 * 2 ** z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def m_per_px(lat: float, z: int) -> float:
    return 156543.03392804097 * math.cos(math.radians(lat)) / 2 ** z


def fetch_tile(z: int, x: int, y: int, session: requests.Session | None = None) -> Path:
    p = RAW / "tiles" / str(z) / str(y) / f"{x}.jpg"
    if p.exists() and p.stat().st_size > 0:
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    s = session or requests
    url = TILE_URL.format(z=z, y=y, x=x)
    for attempt in range(5):
        try:
            r = s.get(url, headers=UA, timeout=40)
            if r.status_code == 200 and r.content:
                p.write_bytes(r.content)
                return p
        except requests.RequestException:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"tile failed {url}")


def mosaic(name: str, z: int, x0: int, y0: int, x1: int, y1: int) -> dict:
    """Mosaic tiles x0..x1, y0..y1 inclusive at zoom z; save PNG under RAW/mosaics.

    Returns a record with path, SHA-256 and the global pixel origin.
    """
    out = RAW / "mosaics" / f"{name}_z{z}_x{x0}-{x1}_y{y0}-{y1}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        W = (x1 - x0 + 1) * 256
        H = (y1 - y0 + 1) * 256
        img = Image.new("RGB", (W, H))
        sess = requests.Session()
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                tp = fetch_tile(z, tx, ty, sess)
                t = Image.open(tp).convert("RGB")
                img.paste(t, ((tx - x0) * 256, (ty - y0) * 256))
        img.save(out)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    return {"path": str(out.relative_to(ROOT)).replace("\\", "/"), "sha256": sha, "zoom": z,
            "tile_range": {"x": [x0, x1], "y": [y0, y1]},
            "origin_px": [x0 * 256, y0 * 256]}


def mosaic_around(name: str, lon: float, lat: float, z: int, half_m: float) -> dict:
    x, y = lonlat_to_px(lon, lat, z)
    h = half_m / m_per_px(lat, z)
    x0, x1 = int((x - h) // 256), int((x + h) // 256)
    y0, y1 = int((y - h) // 256), int((y + h) // 256)
    return mosaic(name, z, x0, y0, x1, y1)


def load_mosaic(rec: dict) -> np.ndarray:
    return np.asarray(Image.open(ROOT / rec["path"]).convert("RGB"))


def identify(lon: float, lat: float) -> dict:
    """Ask the World_Imagery service which imagery block covers a point."""
    cache = RAW / "identify" / f"{lon:.5f}_{lat:.5f}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    p = dict(geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", sr=4326, layers="all",
             tolerance=1, mapExtent=f"{lon-0.005},{lat-0.005},{lon+0.005},{lat+0.005}",
             imageDisplay="800,800,96", returnGeometry="false", f="json")
    r = requests.get(IDENTIFY_URL, params=p, headers=UA, timeout=40)
    r.raise_for_status()
    d = r.json()
    d["_retrieved_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    d["_url"] = r.url
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(d, indent=1))
    return d


def imagery_summary(lon: float, lat: float) -> dict:
    d = identify(lon, lat)
    out = {"retrieved_utc": d.get("_retrieved_utc"), "layers": []}
    for res in d.get("results", []):
        a = res.get("attributes", {})
        out["layers"].append({
            "layer": res.get("layerName"),
            "date": a.get("DATE (YYYYMMDD)") or a.get("SRC_DATE"),
            "resolution_m": a.get("RESOLUTION (M)"),
            "source": a.get("SOURCE"), "source_info": a.get("SOURCE_INFO"),
            "description": a.get("DESCRIPTION"),
            "min_level": a.get("MinMapLevel"), "max_level": a.get("MaxMapLevel"),
            "block": a.get("BlockName"), "release": a.get("ReleaseName")})
    return out


if __name__ == "__main__":
    import sys
    lon, lat = float(sys.argv[1]), float(sys.argv[2])
    print(json.dumps(imagery_summary(lon, lat), indent=1))


# ---------------------------------------------------------------------------
# Esri World Imagery Wayback: archived releases of the same World Imagery map.
# Used only where the current release does not show the architecture clearly.
WB_CONFIG_URL = "https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json"
WB_TILE_URL = "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/{rel}/{z}/{y}/{x}"


def wb_config() -> dict:
    p = RAW / "wayback" / "waybackconfig.json"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(WB_CONFIG_URL, headers=UA, timeout=60)
        r.raise_for_status()
        p.write_bytes(r.content)
    return json.loads(p.read_text())


def wb_releases() -> list[tuple[str, str]]:
    """(release number, release date) sorted newest first."""
    cfg = wb_config()
    out = []
    for k, v in cfg.items():
        t = v["itemTitle"]
        date = t[t.find("Wayback ") + 8:].rstrip(")")
        out.append((k, date))
    out.sort(key=lambda r: r[1], reverse=True)
    return out


def wb_fetch_tile(rel: str, z: int, x: int, y: int, session=None) -> Path:
    p = RAW / "wayback" / "tiles" / rel / str(z) / str(y) / f"{x}.jpg"
    if p.exists() and p.stat().st_size > 0:
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    s = session or requests
    url = WB_TILE_URL.format(rel=rel, z=z, y=y, x=x)
    for attempt in range(5):
        try:
            r = s.get(url, headers=UA, timeout=40)
            if r.status_code == 200 and r.content:
                p.write_bytes(r.content)
                return p
            if r.status_code == 404:
                raise FileNotFoundError(url)
        except requests.RequestException:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"wayback tile failed {url}")


WB_TILEMAP_URL = "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tilemap/{rel}/{z}/{y}/{x}"


def wb_scan(lon: float, lat: float, z: int = 18) -> list[dict]:
    """List the distinct imagery versions of the tile containing a point.

    For every release the tilemap endpoint says whether the tile exists and,
    when the release reuses an older tile, which release holds it ("select").
    Distinct holding releases are distinct images; we fetch one tile of each.
    """
    x, y = lonlat_to_px(lon, lat, z)
    tx, ty = int(x // 256), int(y // 256)
    cache = RAW / "wayback" / f"scan_z{z}_{tx}_{ty}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    sess = requests.Session()
    holders = {}
    for rel, date in wb_releases():
        try:
            r = sess.get(WB_TILEMAP_URL.format(rel=rel, z=z, y=ty, x=tx), headers=UA, timeout=30)
            if r.status_code != 200:
                continue
            d = r.json()
        except Exception:
            continue
        if not d.get("data") or d["data"][0] != 1:
            continue
        hold = str(d["select"][0]) if d.get("select") else rel
        holders.setdefault(hold, []).append((rel, date))
    rel_dates = dict(wb_releases())
    out = []
    for hold, users in holders.items():
        try:
            p = wb_fetch_tile(hold, z, tx, ty, sess)
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            size = p.stat().st_size
        except (RuntimeError, FileNotFoundError):
            sha, size = None, None
        users.sort(key=lambda r: r[1])
        out.append({"holding_release": hold, "holding_release_date": rel_dates.get(hold), "tile": [z, tx, ty],
                    "used_by_releases": [users[0], users[-1]], "n_releases": len(users), "sha256": sha, "bytes": size})
    out.sort(key=lambda r: r["holding_release_date"] or "")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out, indent=1))
    return out


def wb_metadata(rel: str, lon: float, lat: float, z: int = 18) -> dict:
    """Query the release's metadata layer for the imagery date at a point."""
    cfg = wb_config()[rel]
    base = cfg["metadataLayerUrl"]
    # layers 4, 5 and 6 are the 30 cm, 60 cm and 1.2 m metadata layers; each
    # feature states the zoom range (MinMapLevel..MaxMapLevel) it serves
    out = {}
    for layer in (4, 5, 6):
        u = f"{base}/{layer}/query"
        try:
            r = requests.get(u, params={"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
                                        "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "false",
                                        "f": "json"}, headers=UA, timeout=40)
            d = r.json()
        except Exception:
            continue
        feats = d.get("features") or []
        if feats:
            out[str(layer)] = feats[0]["attributes"]
    return {"release": rel, "metadata_url": base, "by_layer": out}


def wb_mosaic(name: str, rel: str, z: int, x0: int, y0: int, x1: int, y1: int) -> dict:
    out = RAW / "mosaics" / f"{name}_wb{rel}_z{z}_x{x0}-{x1}_y{y0}-{y1}.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", ((x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256))
        sess = requests.Session()
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                t = Image.open(wb_fetch_tile(rel, z, tx, ty, sess)).convert("RGB")
                img.paste(t, ((tx - x0) * 256, (ty - y0) * 256))
        img.save(out)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    return {"path": str(out.relative_to(ROOT)).replace("\\", "/"), "sha256": sha, "zoom": z, "wayback_release": rel,
            "tile_range": {"x": [x0, x1], "y": [y0, y1]}, "origin_px": [x0 * 256, y0 * 256]}
