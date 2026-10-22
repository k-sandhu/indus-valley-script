"""Esri World Imagery tiles for the img-A manual axis measurements.

Subcommands
  meta    LAT LON                      imagery acquisition metadata at a point (identify call)
  mosaic  SLUG TAG LAT LON HALF_M [--z 19]   fetch and stitch the tiles covering a square box
  crop    MOSAIC GX0 GY0 W H [--scale S] [--grid G] [--lines picks.json] [--out name]
          crop a mosaic in global pixel coordinates, optionally upscale, draw a labelled
          grid in global pixel coordinates and overlay picked lines for checking.

All coordinates are global Web Mercator pixel coordinates at the mosaic zoom:
x grows east, y grows south, one tile is 256 px. Tiles, mosaics and crops are
third-party imagery and are written only under data/raw/2026-10-21-town-axes/img-A/.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "data" / "raw" / "2026-10-21-town-axes" / "img-A"
TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
IDENTIFY_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/identify"
EARTH_CIRC = 2 * math.pi * 6378137.0
# md5 of the grey "Map data not yet available" tile served above the deepest real level
PLACEHOLDER_MD5 = "f27d9de7f80c13501f470595e327aa6d"
UA = {"User-Agent": "indus-town-axes img-A measurement (research; manual)"}


def lonlat_to_px(lon, lat, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180.0) / 360.0 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def px_to_lonlat(x, y, z):
    n = 256 * 2 ** z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def m_per_px(lat, z):
    return EARTH_CIRC * math.cos(math.radians(lat)) / (256 * 2 ** z)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get_tile(z, x, y, session):
    p = RAW / "tiles" / str(z) / str(y) / f"{x}.jpg"
    if p.exists() and p.stat().st_size > 0:
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            r = session.get(TILE_URL.format(z=z, y=y, x=x), timeout=60, headers=UA)
            if r.status_code == 200:
                p.write_bytes(r.content)
                return p
        except requests.RequestException:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"tile {z}/{y}/{x} failed")


def cmd_meta(a):
    lon, lat = a.lon, a.lat
    p = dict(geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", sr=4326, layers="all",
             tolerance=1, mapExtent=f"{lon-0.005},{lat-0.005},{lon+0.005},{lat+0.005}",
             imageDisplay="1000,1000,96", returnGeometry="false", f="json")
    r = requests.get(IDENTIFY_URL, params=p, timeout=60, headers=UA)
    j = r.json()
    keep = [res for res in j.get("results", []) if res["layerId"] in (0, 4)]
    out = {"query_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "url": r.url,
           "lat": lat, "lon": lon, "results": keep}
    if a.save:
        q = RAW / "meta" / f"{a.save}.json"
        q.write_text(json.dumps(out, indent=1))
        print("saved", q)
    for res in keep:
        at = res["attributes"]
        print(res["layerId"], at.get("SOURCE"), at.get("SOURCE_INFO"), at.get("DESCRIPTION"),
              "date", at.get("DATE (YYYYMMDD)") or at.get("DATE"), "res", at.get("RESOLUTION (M)"),
              "levels", at.get("MinMapLevel", at.get("FROM_CACHE_LEVEL")), at.get("MaxMapLevel", at.get("TO_CACHE_LEVEL")))


def cmd_mosaic(a):
    z = a.z
    cx, cy = lonlat_to_px(a.lon, a.lat, z)
    half_px = a.half_m / m_per_px(a.lat, z)
    tx0, tx1 = int((cx - half_px) // 256), int((cx + half_px) // 256)
    ty0, ty1 = int((cy - half_px) // 256), int((cy + half_px) // 256)
    s = requests.Session()
    W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
    img = Image.new("RGB", (W, H))
    n = 0
    n_blank = 0
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            p = get_tile(z, tx, ty, s)
            if hashlib.md5(p.read_bytes()).hexdigest() == PLACEHOLDER_MD5:
                n_blank += 1
            img.paste(Image.open(p).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
            n += 1
    name = f"{a.slug}_{a.tag}_z{z}_x{tx0}-{tx1}_y{ty0}-{ty1}"
    out = RAW / "mosaics" / f"{name}.png"
    img.save(out)
    rec = {"slug": a.slug, "tag": a.tag, "zoom": z, "tile_x": [tx0, tx1], "tile_y": [ty0, ty1],
           "origin_global_px": [tx0 * 256, ty0 * 256], "size_px": [W, H], "n_tiles": n, "n_placeholder_tiles": n_blank,
           "center_lonlat": [a.lon, a.lat], "m_per_px": m_per_px(a.lat, z),
           "file": str(out.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(out),
           "made_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "tile_url": TILE_URL}
    (RAW / "mosaics" / f"{name}.json").write_text(json.dumps(rec, indent=1))
    # overview for orientation
    ov = img.copy()
    ov.thumbnail((1000, 1000))
    ov.save(RAW / "mosaics" / f"{name}_overview.jpg", quality=88)
    print(json.dumps(rec, indent=1))


def load_mosaic(path):
    path = Path(path)
    rec = json.loads(path.with_suffix(".json").read_text())
    return Image.open(path).convert("RGB"), rec


def cmd_crop(a):
    img, rec = load_mosaic(a.mosaic)
    ox, oy = rec["origin_global_px"]
    x0, y0 = a.gx0 - ox, a.gy0 - oy
    box = (int(x0), int(y0), int(x0 + a.w), int(y0 + a.h))
    if box[0] < 0 or box[1] < 0 or box[2] > img.width or box[3] > img.height:
        raise SystemExit(f"crop box {box} lies outside the mosaic ({img.width} x {img.height})")
    c = img.crop(box)
    S = a.scale
    if S != 1:
        c = c.resize((int(a.w * S), int(a.h * S)), Image.LANCZOS if S < 1 else Image.BICUBIC)
    if a.enhance:
        from PIL import ImageOps
        c = ImageOps.autocontrast(c, cutoff=1)
    d = ImageDraw.Draw(c)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
    G = a.grid
    if G:
        gx = math.ceil(a.gx0 / G) * G
        while gx < a.gx0 + a.w:
            X = (gx - a.gx0) * S
            major = (gx % (G * 5) == 0)
            d.line([(X, 0), (X, c.height)], fill=(255, 255, 0) if major else (0, 255, 255), width=1)
            if (gx // G) % a.label_every == 0:
                d.text((X + 2, 2), str(gx % a.label_mod), fill=(255, 255, 0), font=font)
            gx += G
        gy = math.ceil(a.gy0 / G) * G
        while gy < a.gy0 + a.h:
            Y = (gy - a.gy0) * S
            major = (gy % (G * 5) == 0)
            d.line([(0, Y), (c.width, Y)], fill=(255, 255, 0) if major else (0, 255, 255), width=1)
            if (gy // G) % a.label_every == 0:
                d.text((2, Y + 2), str(gy % a.label_mod), fill=(255, 255, 0), font=font)
            gy += G
    if a.lines:
        picks = json.loads(Path(a.lines).read_text())
        for ln in picks.get("lines", []):
            pts = ln.get("points") or [ln["p1"], ln["p2"]]
            P = [((x - a.gx0) * S, (y - a.gy0) * S) for x, y in pts]
            if len(P) >= 2:
                d.line(P[:1] + P[-1:], fill=(255, 0, 0), width=1)
            for X, Y in P:
                d.ellipse([X - 2, Y - 2, X + 2, Y + 2], outline=(255, 0, 255))
            d.text((P[0][0] + 3, P[0][1] + 3), ln["id"], fill=(255, 80, 80), font=font)
    name = a.out or f"crop_{Path(a.mosaic).stem}_{a.gx0}_{a.gy0}_{a.w}x{a.h}_s{S}"
    out = RAW / "crops" / f"{name}.png"
    c.save(out)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("meta"); m.add_argument("lat", type=float); m.add_argument("lon", type=float)
    m.add_argument("--save")
    mo = sp.add_parser("mosaic"); mo.add_argument("slug"); mo.add_argument("tag")
    mo.add_argument("lat", type=float); mo.add_argument("lon", type=float); mo.add_argument("half_m", type=float)
    mo.add_argument("--z", type=int, default=19)
    c = sp.add_parser("crop"); c.add_argument("mosaic"); c.add_argument("gx0", type=float); c.add_argument("gy0", type=float)
    c.add_argument("w", type=int); c.add_argument("h", type=int); c.add_argument("--scale", type=float, default=1.0)
    c.add_argument("--grid", type=int, default=0); c.add_argument("--lines"); c.add_argument("--out")
    c.add_argument("--enhance", action="store_true")
    c.add_argument("--label-mod", type=int, default=10000, help="grid labels show the coordinate modulo this")
    c.add_argument("--label-every", type=int, default=1)
    a = ap.parse_args()
    {"meta": cmd_meta, "mosaic": cmd_mosaic, "crop": cmd_crop}[a.cmd](a)


if __name__ == "__main__":
    main()
