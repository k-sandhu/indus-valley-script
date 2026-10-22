"""Apparent horizon profiles east and west of each town from the Copernicus DEM (PROTOCOL.md, Horizon).

GLO-30 is sampled every 30 m from 2 to 20 km and GLO-90 every 90 m from 20 to 250 km along rays at
0.1 degree steps over azimuths 45-135 and 225-315. Raw tiles are read into
memory only (the URL, size and SHA-256 of every tile are recorded in the output); only the derived profiles are tracked.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import math

import numpy as np
import rasterio
import requests

from common import BASE, ROOT, finite, provenance, write_new

R_EARTH = 6371000.0
K_TERRESTRIAL = 0.13
R_EFF = R_EARTH / (1.0 - K_TERRESTRIAL)
EYE = 1.6
DEM_DIR = ROOT / "data/raw/2026-10-21-town-axes/dem"
SOURCES = {
    30: ("https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com", "Copernicus_DSM_COG_10_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM"),
    90: ("https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com", "Copernicus_DSM_COG_30_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM"),
}
AZIMUTHS = np.round(np.concatenate([np.arange(45.0, 135.0001, 0.1), np.arange(225.0, 315.0001, 0.1)]), 1)


def tile_name(res, lat, lon):
    return SOURCES[res][1].format(ns="N" if lat >= 0 else "S", lat=abs(lat), ew="E" if lon >= 0 else "W", lon=abs(lon))


def fetch_tile(res, lat, lon, log):
    """Download a tile into memory (the disk is not used); log its URL, size and SHA-256."""
    name = tile_name(res, lat, lon)
    url = f"{SOURCES[res][0]}/{name}/{name}.tif"
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=300)
            break
        except requests.RequestException as exc:
            err = str(exc)
    else:
        raise RuntimeError(f"{url}: {err}")
    rec = {"url": url, "utc": datetime.now(timezone.utc).isoformat(), "status": r.status_code}
    if r.status_code == 200:
        rec.update(bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest())
        log.append(rec)
        return r.content
    rec.update(note="no tile; treated as sea level (open water)")
    log.append(rec)
    return None


class Dem:
    """Bilinear sampler over cached 1x1 degree tiles; absent tiles are sea at 0 m."""

    def __init__(self, res, log):
        self.res, self.log, self.cache = res, log, {}

    def tile(self, lat, lon):
        key = (lat, lon)
        if key not in self.cache and len(self.cache) >= 48:
            self.cache.clear()  # bound memory; evicted tiles are downloaded again if needed
        if key not in self.cache:
            p = fetch_tile(self.res, lat, lon, self.log)
            if p is None:
                self.cache[key] = None
            else:
                with rasterio.MemoryFile(p) as mem, mem.open() as src:
                    arr = src.read(1).astype("float32")
                    nod = src.nodata
                    if nod is not None:
                        arr[arr == nod] = 0.0
                    self.cache[key] = (arr, ~src.transform)
        return self.cache[key]

    def sample(self, lat, lon):
        out = np.zeros(lat.shape)
        tl, tn = np.floor(lat).astype(int), np.floor(lon).astype(int)
        for key in set(zip(tl.ravel().tolist(), tn.ravel().tolist())):
            sel = (tl == key[0]) & (tn == key[1])
            t = self.tile(*key)
            if t is None:
                continue
            arr, inv = t
            col, row = inv * (lon[sel], lat[sel])
            col, row = np.asarray(col) - 0.5, np.asarray(row) - 0.5
            c0 = np.clip(np.floor(col).astype(int), 0, arr.shape[1] - 2)
            r0 = np.clip(np.floor(row).astype(int), 0, arr.shape[0] - 2)
            fc, fr = np.clip(col - c0, 0, 1), np.clip(row - r0, 0, 1)
            v = (arr[r0, c0] * (1 - fc) * (1 - fr) + arr[r0, c0 + 1] * fc * (1 - fr)
                 + arr[r0 + 1, c0] * (1 - fc) * fr + arr[r0 + 1, c0 + 1] * fc * fr)
            out[sel] = v
        return out


def destination(lat0, lon0, az, d):
    """Points at great-circle distance d (m) along azimuth az (deg) from (lat0, lon0)."""
    p1, l1 = math.radians(lat0), math.radians(lon0)
    a = np.radians(az)[:, None]
    delta = (d / R_EARTH)[None, :]
    p2 = np.arcsin(np.sin(p1) * np.cos(delta) + np.cos(p1) * np.sin(delta) * np.cos(a))
    l2 = l1 + np.arctan2(np.sin(a) * np.sin(delta) * np.cos(p1), np.cos(delta) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), np.degrees(l2)


def profile(lat0, lon0, dem30, dem90):
    dem30.cache.clear()  # near tiles are rarely shared between towns; far tiles are kept
    h0 = float(dem30.sample(np.array([lat0]), np.array([lon0]))[0]) + EYE
    best = np.full(AZIMUTHS.shape, -90.0)
    best_d = np.zeros(AZIMUTHS.shape)
    best_h = np.zeros(AZIMUTHS.shape)
    for dem, d in ((dem30, np.arange(2000.0, 20000.0 + 1, 30.0)), (dem90, np.arange(20000.0, 250000.0 + 1, 90.0))):
        for i0 in range(0, len(AZIMUTHS), 100):
            az = AZIMUTHS[i0:i0 + 100]
            la, lo = destination(lat0, lon0, az, d)
            h = dem.sample(la, lo)
            ang = np.degrees(np.arctan((h - h0) / d[None, :] - d[None, :] / (2 * R_EFF)))
            j = np.argmax(ang, axis=1)
            m = ang[np.arange(len(az)), j]
            upd = m > best[i0:i0 + 100]
            best[i0:i0 + 100][upd] = m[upd]
            best_d[i0:i0 + 100][upd] = d[j][upd]
            best_h[i0:i0 + 100][upd] = h[np.arange(len(az)), j][upd]
    return h0, best, best_d, best_h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--towns", required=True, help="JSON list of {slug, lat, lon, basis}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    towns = json.loads(Path(a.towns).read_text(encoding="utf-8"))
    log, results = [], []
    dem30, dem90 = Dem(30, log), Dem(90, log)
    for t in towns:
        h0, alt, dist, elev = profile(t["lat"], t["lon"], dem30, dem90)
        west = AZIMUTHS >= 180
        results.append({
            "town": t["slug"], "lat": t["lat"], "lon": t["lon"], "coordinate_basis": t.get("basis"),
            "observer_elevation_m": finite(h0, 2),
            "max_altitude_west_deg": finite(alt[west].max(), 3), "max_altitude_east_deg": finite(alt[~west].max(), 3),
            "altitude_at_270_deg": finite(alt[AZIMUTHS == 270.0][0], 3), "altitude_at_90_deg": finite(alt[AZIMUTHS == 90.0][0], 3),
            "profile": [{"az": float(z), "alt_deg": finite(v, 4), "distance_km": finite(d / 1000, 2), "terrain_m": finite(e, 1)}
                        for z, v, d, e in zip(AZIMUTHS, alt, dist, elev)],
        })
        print(t["slug"], round(h0, 1), round(float(alt[west].max()), 3), round(float(alt[~west].max()), 3), flush=True)
    result = {
        "schema_version": "1.0", "task": "town-axes-horizon", "synthetic": False,
        "model": {"dem_near": "Copernicus GLO-30, 2-20 km, 30 m steps", "dem_far": "Copernicus GLO-90, 20-250 km, 90 m steps",
                  "excluded_radius_km": 2.0, "observer_eye_m": EYE, "terrestrial_refraction_k": K_TERRESTRIAL,
                  "azimuth_step_deg": 0.1, "absent_tiles": "sea level", "tile_storage": "downloaded into memory, not written to disk"},
        "dem_tiles": [x for x in log if x.get("status") == 200],
        "dem_tiles_absent": [x["url"] for x in log if x.get("status") != 200],
        "dem_rights": "Copernicus DEM, produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; raw tiles local-only",
        "towns": results,
        "provenance": provenance([Path(a.towns)], [BASE / "horizon.py", BASE / "common.py"]),
    }
    print(write_new(a.out, result))


if __name__ == "__main__":
    main()
