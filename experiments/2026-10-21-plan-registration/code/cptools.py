"""Tools for the registrars of the plan-registration package.

Subcommands
  meta     LAT LON                          imagery source and date at a point (Esri identify)
  releases LAT LON [--z 18]                 Wayback releases holding distinct imagery at that tile
  mosaic   --reg R --name N LAT LON HALF_M [--z 18] [--release REL]
                                            fetch and stitch Esri World Imagery (or a Wayback release)
  grid     IMAGE X0 Y0 W H [--scale S] [--step G] [--points FILE --side plan|image] [--enhance]
                                            crop any image and draw a grid labelled in that image's pixels
  px2ll    MOSAIC_JSON X Y                  mosaic pixel to longitude and latitude
  ll2px    MOSAIC_JSON LON LAT              longitude and latitude to mosaic pixel
  check    CONTROL_FILE                     fit every link with the frozen error model; the rotation is not printed
  overlay  CONTROL_FILE --reg R --link I --mosaic MOSAIC_JSON [--crop X0 Y0 W H]
                                            draw the plan's ink, warped by the fitted transform, over the imagery
  render   PDF PAGE_INDEX --reg R --name N [--dpi D]
                                            render one PDF page (for an auxiliary plan) to a PNG

Mosaics, crops and overlays are third-party imagery and plan reproductions
and are written only under data/raw/2026-10-21-plan-registration/<registrar>/.
Run from the repository root.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regfit  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "2026-10-21-plan-registration"
TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
IDENTIFY_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/identify"
WB_CONFIG_URL = "https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json"
WB_TILE_URL = "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/{rel}/{z}/{y}/{x}"
WB_TILEMAP_URL = "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tilemap/{rel}/{z}/{y}/{x}"
PLACEHOLDER_MD5 = "f27d9de7f80c13501f470595e327aa6d"
UA = {"User-Agent": "indus plan-registration (research; manual control points)"}


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lonlat_to_px(lon, lat, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180.0) / 360.0 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def px_to_lonlat(x, y, z):
    n = 256 * 2 ** z
    return x / n * 360.0 - 180.0, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))


def font(size=12):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def get(url, session, tries=4):
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=60, headers=UA)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def tile(z, x, y, session, release=None):
    sub = f"wayback/{release}" if release else "current"
    p = RAW / "tiles" / sub / str(z) / str(y) / f"{x}.jpg"
    if p.exists() and p.stat().st_size > 0:
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    url = WB_TILE_URL.format(rel=release, z=z, y=y, x=x) if release else TILE_URL.format(z=z, y=y, x=x)
    p.write_bytes(get(url, session).content)
    return p


def cmd_meta(a):
    lon, lat = a.lon, a.lat
    p = dict(geometry=f"{lon},{lat}", geometryType="esriGeometryPoint", sr=4326, layers="all", tolerance=1,
             mapExtent=f"{lon-0.005},{lat-0.005},{lon+0.005},{lat+0.005}", imageDisplay="1000,1000,96",
             returnGeometry="false", f="json")
    r = requests.get(IDENTIFY_URL, params=p, timeout=60, headers=UA)
    for res in r.json().get("results", []):
        if res["layerId"] in (0, 4):
            at = res["attributes"]
            print(at.get("SOURCE"), at.get("SOURCE_INFO"), "date", at.get("DATE (YYYYMMDD)") or at.get("DATE"),
                  "res", at.get("RESOLUTION (M)"), "accuracy", at.get("ACCURACY (M)"))


def wb_releases(session):
    p = RAW / "tiles" / "waybackconfig.json"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(get(WB_CONFIG_URL, session).content)
    cfg = json.loads(p.read_text())
    out = []
    for k, v in cfg.items():
        title = v.get("itemTitle", "")
        date = title.split("Wayback")[-1].strip() if "Wayback" in title else title
        out.append((k, date))
    out.sort(key=lambda r: r[1], reverse=True)
    return out


def cmd_releases(a):
    s = requests.Session()
    x, y = lonlat_to_px(a.lon, a.lat, a.z)
    tx, ty = int(x // 256), int(y // 256)
    seen = {}
    for rel_id, date in wb_releases(s):
        try:
            j = get(WB_TILEMAP_URL.format(rel=rel_id, z=a.z, y=ty, x=tx), s).json()
        except RuntimeError:
            continue
        if not j.get("data") or j["data"][0] != 1:
            continue
        hold = str(j.get("select", [rel_id])[0]) if j.get("select") else rel_id
        seen.setdefault(hold, []).append((rel_id, date))
    for hold, users in sorted(seen.items(), key=lambda kv: kv[1][-1][1]):
        print(f"holding release {hold}: used by {len(users)} releases from {users[-1][1]} to {users[0][1]}")


def cmd_mosaic(a):
    z = a.z
    cx, cy = lonlat_to_px(a.lon, a.lat, z)
    gm = regfit.ground_m_per_px(a.lat, z)
    half = a.half_m / gm
    tx0, tx1 = int((cx - half) // 256), int((cx + half) // 256)
    ty0, ty1 = int((cy - half) // 256), int((cy + half) // 256)
    if (tx1 - tx0 + 1) * (ty1 - ty0 + 1) > 400:
        raise SystemExit("more than 400 tiles; use a smaller box or a lower zoom")
    s = requests.Session()
    W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
    img = Image.new("RGB", (W, H))
    blank = 0
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            p = tile(z, tx, ty, s, a.release)
            if hashlib.md5(p.read_bytes()).hexdigest() == PLACEHOLDER_MD5:
                blank += 1
            img.paste(Image.open(p).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
    d = RAW / a.reg / "mosaics"
    d.mkdir(parents=True, exist_ok=True)
    tag = f"wb{a.release}" if a.release else "cur"
    name = f"{a.name}_{tag}_z{z}_x{tx0}-{tx1}_y{ty0}-{ty1}"
    out = d / f"{name}.png"
    img.save(out)
    rec = {"name": a.name, "zoom": z, "tile_x": [tx0, tx1], "tile_y": [ty0, ty1],
           "origin_global_px": [tx0 * 256, ty0 * 256], "size_px": [W, H], "n_placeholder_tiles": blank,
           "center_lonlat": [a.lon, a.lat], "ground_m_per_px": gm,
           "service": "Esri World Imagery Wayback" if a.release else "Esri World Imagery",
           "wayback_release": a.release, "tile_url": WB_TILE_URL if a.release else TILE_URL,
           "file": rel(out), "sha256": sha256(out), "made_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (d / f"{name}.json").write_text(json.dumps(rec, indent=1))
    ov = img.copy()
    ov.thumbnail((1200, 1200))
    ov.save(d / f"{name}_overview.jpg", quality=88)
    print(json.dumps(rec, indent=1))
    print("overview:", rel(d / f"{name}_overview.jpg"), "(overview scale factor", round(ov.width / W, 4), ")")


def load_mosaic(path):
    path = Path(path)
    if path.suffix != ".json":
        path = path.with_suffix(".json")
    return json.loads(path.read_text())


def cmd_px2ll(a):
    m = load_mosaic(a.mosaic)
    ox, oy = m["origin_global_px"]
    print("%.7f %.7f" % px_to_lonlat(ox + a.x, oy + a.y, m["zoom"]))


def cmd_ll2px(a):
    m = load_mosaic(a.mosaic)
    ox, oy = m["origin_global_px"]
    gx, gy = lonlat_to_px(a.lon, a.lat, m["zoom"])
    print("%.2f %.2f" % (gx - ox, gy - oy))


def out_dir(reg, kind):
    d = RAW / reg / kind
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_grid(a):
    img = Image.open(ROOT / a.image if not Path(a.image).is_absolute() else a.image).convert("RGB")
    box = (int(a.x0), int(a.y0), int(a.x0 + a.w), int(a.y0 + a.h))
    box = (max(0, box[0]), max(0, box[1]), min(img.width, box[2]), min(img.height, box[3]))
    c = img.crop(box)
    S = a.scale
    if S != 1:
        c = c.resize((max(1, int(c.width * S)), max(1, int(c.height * S))), Image.LANCZOS if S < 1 else Image.BICUBIC)
    if a.enhance:
        c = ImageOps.autocontrast(c, cutoff=1)
    d = ImageDraw.Draw(c)
    f = font(12)
    G = a.step
    if G:
        g = math.ceil(box[0] / G) * G
        while g < box[2]:
            X = (g - box[0]) * S
            d.line([(X, 0), (X, c.height)], fill=(255, 200, 0) if g % (5 * G) == 0 else (0, 200, 255), width=1)
            d.text((X + 2, 2), str(g), fill=(255, 0, 0), font=f)
            g += G
        g = math.ceil(box[1] / G) * G
        while g < box[3]:
            Y = (g - box[1]) * S
            d.line([(0, Y), (c.width, Y)], fill=(255, 200, 0) if g % (5 * G) == 0 else (0, 200, 255), width=1)
            d.text((2, Y + 2), str(g), fill=(255, 0, 0), font=f)
            g += G
    if a.points:
        cf = json.loads(Path(a.points).read_text())
        for link in cf["links"]:
            for p in link["points"]:
                if a.side == "plan":
                    if rel(ROOT / a.image) != plan_render(cf, link["plan"]):
                        continue
                    x, y = p["plan_px"]
                elif a.side == "target":
                    x, y = p.get("target_px", (None, None))
                    if x is None:
                        continue
                else:
                    if "mosaic" not in p or rel(ROOT / p["mosaic"].replace(".json", ".png")) != rel(ROOT / a.image):
                        continue
                    x, y = p["mosaic_px"]
                X, Y = (x - box[0]) * S, (y - box[1]) * S
                d.ellipse([X - 4, Y - 4, X + 4, Y + 4], outline=(255, 0, 255), width=2)
                d.text((X + 6, Y - 6), p["id"], fill=(255, 0, 255), font=font(14))
    name = a.out or f"{Path(a.image).stem}_{box[0]}_{box[1]}_{box[2]-box[0]}x{box[3]-box[1]}_s{S}"
    out = out_dir(a.reg, "crops") / f"{name}.png"
    c.save(out)
    print(rel(out), "size", c.size)


def load_plans(cf=None):
    plans = {p["id"]: p for p in json.loads((PKG / "plans-v1.json").read_text())["plans"]}
    if cf:
        for p in cf.get("aux_plans", []):
            q = dict(p)
            sb = p.get("scale_bar")
            if sb:
                (x1, y1), (x2, y2) = sb["p1_px"], sb["p2_px"]
                q["scale_bar_m_per_px"] = sb["length_m"] / math.hypot(x2 - x1, y2 - y1)
            plans[p["id"]] = q
    return plans


def plan_render(cf, pid):
    return load_plans(cf)[pid]["render"]


def load_mosaics(cf):
    out = {}
    for link in cf["links"]:
        for p in link["points"]:
            if "mosaic" in p and p["mosaic"] not in out:
                out[p["mosaic"]] = load_mosaic(ROOT / p["mosaic"])
    return out


def cmd_check(a):
    cf = json.loads(Path(a.control).read_text())
    plans = load_plans(cf)
    mosaics = load_mosaics(cf)
    for i, link in enumerate(cf["links"]):
        for label, subset in (("all points", None), ("without exposed masonry", lambda p: not p.get("exposed_masonry"))):
            if subset is not None and not any(p.get("exposed_masonry") for p in link["points"]):
                continue
            r = regfit.fit_from_link(link, plans, mosaics, subset=subset)
            print(f"link {i}: {link['plan']} -> {link['to']} ({label})")
            for k in ("n_points", "dof", "chi2_per_dof", "fitted_m_per_px", "scale_bar_m_per_px", "scale_ratio",
                      "singular_value_ratio", "chi2", "chi2_mirror", "sigma_phi_prior_deg", "sigma_phi_deg",
                      "informative", "accepted"):
                if k in r:
                    v = r[k]
                    print(f"   {k}: {round(v, 4) if isinstance(v, float) else v}")
            if r.get("reasons"):
                print("   reasons:", "; ".join(r["reasons"]))
            pts = [p for p in link["points"] if subset is None or subset(p)]
            for p, rm, nr in zip(pts, r.get("residuals_m", []), r.get("normalised_residuals", [])):
                print(f"   {p['id']:>8} class {p['class']} residual {math.hypot(*rm):7.2f} m  normalised {nr:5.2f}")


def link_affine_to_mosaic(link, plans, mosaics, m):
    """2x3 matrix from plan pixels of the link's plan to pixels of mosaic m (map links only)."""
    P, Q, sig, _ = regfit.link_arrays(link, plans, mosaics)
    params, _, _ = regfit._solve(P, Q, 1 / sig ** 2)
    a_, b_, tx, ty = params
    EN = []
    for p in link["points"]:
        mz = mosaics[p["mosaic"]]
        ox, oy = mz["origin_global_px"]
        EN.append(regfit.global_px_to_merc(ox + p["mosaic_px"][0], oy + p["mosaic_px"][1], mz["zoom"]))
    EN = np.array(EN)
    c = EN.mean(axis=0)
    cl = math.cos(math.radians(regfit.merc_to_lonlat(c[0], c[1])[1]))
    n = 256.0 * 2 ** m["zoom"]
    ox, oy = m["origin_global_px"]

    def f(x, y):
        X, Y = x, -y
        qx, qy = a_ * X - b_ * Y + tx, b_ * X + a_ * Y + ty
        E, N = qx / cl + c[0], qy / cl + c[1]
        return (E / regfit.CIRC + 0.5) * n - ox, (0.5 - N / regfit.CIRC) * n - oy

    src = np.float32([[0, 0], [1000, 0], [0, 1000]])
    dst = np.float32([f(*s) for s in src])
    import cv2
    return cv2.getAffineTransform(src, dst)


def cmd_overlay(a):
    import cv2
    cf = json.loads(Path(a.control).read_text())
    plans = load_plans(cf)
    mosaics = load_mosaics(cf)
    link = cf["links"][a.link]
    if link["to"] != "map":
        raise SystemExit("overlay works on links to the map")
    m = load_mosaic(ROOT / a.mosaic)
    M = link_affine_to_mosaic(link, plans, mosaics, m)
    base = np.array(Image.open(ROOT / m["file"]).convert("RGB"))
    plan = np.array(Image.open(ROOT / plans[link["plan"]]["render"]).convert("L"))
    if a.invert:
        plan = 255 - plan
    ink = (plan < a.ink).astype(np.uint8) * 255
    warped = cv2.warpAffine(ink, M, (base.shape[1], base.shape[0]), flags=cv2.INTER_NEAREST)
    out = base.copy()
    out[warped > 0] = (0.35 * out[warped > 0] + 0.65 * np.array([255, 0, 0])).astype(np.uint8)
    img = Image.fromarray(out)
    d = ImageDraw.Draw(img)
    mk = rel(ROOT / a.mosaic)
    for p in link["points"]:
        X, Y = M @ np.array([p["plan_px"][0], p["plan_px"][1], 1.0])
        d.ellipse([X - 5, Y - 5, X + 5, Y + 5], outline=(255, 255, 0), width=2)
        if rel(ROOT / p["mosaic"]) == mk:
            x2, y2 = p["mosaic_px"]
            d.line([(X, Y), (x2, y2)], fill=(0, 255, 255), width=2)
            d.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], outline=(0, 255, 255), width=2)
        d.text((X + 7, Y - 7), p["id"], fill=(255, 255, 0), font=font(14))
    if a.crop:
        x0, y0, w, h = a.crop
        img = img.crop((x0, y0, x0 + w, y0 + h))
    name = a.out or f"overlay_{Path(a.control).stem}_link{a.link}"
    out_p = out_dir(a.reg, "overlays") / f"{name}.png"
    img.save(out_p)
    print(rel(out_p), "size", img.size, "(yellow: plan points after the fit; cyan: imagery points)")


def cmd_render(a):
    import fitz
    pdf = ROOT / a.pdf if not Path(a.pdf).is_absolute() else Path(a.pdf)
    doc = fitz.open(pdf)
    page = doc[a.page]
    pix = page.get_pixmap(dpi=a.dpi)
    out = out_dir(a.reg, "renders") / f"{a.name}_p{a.page:04d}_{a.dpi}dpi.png"
    if out.exists():
        raise SystemExit(f"{rel(out)} exists")
    pix.save(out)
    print(json.dumps({"render": rel(out), "render_sha256": sha256(out), "publication_file": rel(pdf),
                      "publication_sha256": sha256(pdf), "pdf_page_index": a.page, "dpi": a.dpi,
                      "size_px": [pix.width, pix.height]}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("meta"); m.add_argument("lat", type=float); m.add_argument("lon", type=float)
    r = sp.add_parser("releases"); r.add_argument("lat", type=float); r.add_argument("lon", type=float)
    r.add_argument("--z", type=int, default=18)
    mo = sp.add_parser("mosaic"); mo.add_argument("--reg", required=True); mo.add_argument("--name", required=True)
    mo.add_argument("lat", type=float); mo.add_argument("lon", type=float); mo.add_argument("half_m", type=float)
    mo.add_argument("--z", type=int, default=18); mo.add_argument("--release")
    g = sp.add_parser("grid"); g.add_argument("image"); g.add_argument("x0", type=float); g.add_argument("y0", type=float)
    g.add_argument("w", type=float); g.add_argument("h", type=float); g.add_argument("--scale", type=float, default=1.0)
    g.add_argument("--step", type=int, default=50); g.add_argument("--points"); g.add_argument("--side", default="plan",
                   choices=["plan", "image", "target"])
    g.add_argument("--enhance", action="store_true"); g.add_argument("--reg", required=True); g.add_argument("--out")
    p1 = sp.add_parser("px2ll"); p1.add_argument("mosaic"); p1.add_argument("x", type=float); p1.add_argument("y", type=float)
    p2 = sp.add_parser("ll2px"); p2.add_argument("mosaic"); p2.add_argument("lon", type=float); p2.add_argument("lat", type=float)
    c = sp.add_parser("check"); c.add_argument("control")
    o = sp.add_parser("overlay"); o.add_argument("control"); o.add_argument("--link", type=int, default=0)
    o.add_argument("--reg", required=True)
    o.add_argument("--mosaic", required=True); o.add_argument("--crop", type=int, nargs=4)
    o.add_argument("--ink", type=int, default=110); o.add_argument("--invert", action="store_true"); o.add_argument("--out")
    rn = sp.add_parser("render"); rn.add_argument("pdf"); rn.add_argument("page", type=int)
    rn.add_argument("--reg", required=True); rn.add_argument("--name", required=True); rn.add_argument("--dpi", type=int, default=200)
    a = ap.parse_args()
    {"render": cmd_render, "meta": cmd_meta, "releases": cmd_releases, "mosaic": cmd_mosaic, "grid": cmd_grid, "px2ll": cmd_px2ll,
     "ll2px": cmd_ll2px, "check": cmd_check, "overlay": cmd_overlay}[a.cmd](a)


if __name__ == "__main__":
    main()
