"""Turn a picks file into the town record of the img-A measurement.

usage: python calc.py PICKS.json [--write]

For every picked line the measured endpoints are the provisional endpoints P1, P2
moved across the line by the offsets o1, o2 read on the rectified strip
(see strip.py). From the measured endpoints in global Web Mercator pixels
(x east, y south) we compute

  bearing   = atan2(dx, -dy) folded to [0, 180)        (true north; Mercator is conformal)
  deviation = bearing folded to the nearest cardinal, in [-45, +45), clockwise positive
  length    = pixel length * ground metres per pixel at the line's latitude and zoom
  sigma     = sqrt( (sqrt(2) * sigma_px / L_px)^2 + floor^2 )  in degrees

where sigma_px is the one-sigma perpendicular uncertainty we assign to each
endpoint from the sharpness of the edge, and the floor covers residual
distortion of the orthomosaic over the length of one structure.

A system is a list of lines given in the picks file. Its deviation is the
length-weighted mean of the line deviations (unwrapped around the first line),
sd_deg is the unweighted sample standard deviation of the line deviations, and
se_deg is the larger of the scatter-based error of the weighted mean
(weighted SD / sqrt(n_eff), n_eff = (sum w)^2 / sum w^2) and the propagated
measurement error sqrt(sum w^2 sigma^2) / sum w.
"""
import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tiles import ROOT, m_per_px, px_to_lonlat  # noqa: E402
from strip import corrected  # noqa: E402

FLOOR_DEG = 0.2
OUTDIR = Path(__file__).resolve().parents[1] / "towns"


def fold_dev(b):
    return ((b + 45.0) % 90.0) - 45.0


def line_metrics(ln, mosaics):
    rec = json.loads((ROOT / mosaics[ln["mosaic"]]).with_suffix(".json").read_text())
    z = rec["zoom"]
    (x1, y1), (x2, y2) = corrected(ln)
    dx, dy = x2 - x1, y2 - y1
    Lpx = math.hypot(dx, dy)
    b = math.degrees(math.atan2(dx, -dy)) % 180.0
    lon_m, lat_m = px_to_lonlat((x1 + x2) / 2, (y1 + y2) / 2, z)
    Lm = Lpx * m_per_px(lat_m, z)
    s = math.degrees(math.sqrt(2) * ln["sigma_px"] / Lpx)
    sig = math.hypot(s, FLOOR_DEG)
    lo1, la1 = px_to_lonlat(x1, y1, z)
    lo2, la2 = px_to_lonlat(x2, y2, z)
    return dict(z=z, p1=(x1, y1), p2=(x2, y2), Lpx=Lpx, length_m=Lm, bearing=b, dev=fold_dev(b), sigma=sig,
                lonlat=((lo1, la1), (lo2, la2)))


def system_stats(devs, ws, sigs):
    ref = devs[0]
    u = [ref + fold_dev(d - ref) for d in devs]
    W = sum(ws)
    mean = sum(w * d for w, d in zip(ws, u)) / W
    n = len(u)
    if n > 1:
        sd = math.sqrt(sum((d - sum(u) / n) ** 2 for d in u) / (n - 1))
        wvar = sum(w * (d - mean) ** 2 for w, d in zip(ws, u)) / W * n / (n - 1)
        neff = W ** 2 / sum(w * w for w in ws)
        se_scatter = math.sqrt(wvar / neff)
    else:
        sd, se_scatter = 0.0, 0.0
    se_meas = math.sqrt(sum((w * s) ** 2 for w, s in zip(ws, sigs))) / W
    return fold_dev(mean), max(se_scatter, se_meas), sd, W, n


def imagery_meta(names):
    """Summarise the identify records we saved for the measured parts of a town."""
    recs = []
    for n in names:
        j = json.loads((ROOT / "data/raw/2026-10-21-town-axes/img-A/meta" / f"{n}.json").read_text())
        for r in j["results"]:
            at = r["attributes"]
            if r["layerId"] == 0:
                d = at.get("DATE (YYYYMMDD)")
                recs.append(dict(point=n, date=None if d in (None, "Null") else f"{d[:4]}-{d[4:6]}-{d[6:]}",
                                 source=at.get("SOURCE"), product=at.get("SOURCE_INFO"), sensor=at.get("DESCRIPTION"),
                                 res=at.get("RESOLUTION (M)"), max_level=at.get("MaxMapLevel")))
    return recs


def build_sources(P):
    out = []
    for key, mpath in P["mosaics"].items():
        rec = json.loads((ROOT / mpath).with_suffix(".json").read_text())
        metas = imagery_meta(P.get("imagery_meta", {}).get(key, []))
        dates = sorted({m["date"] for m in metas if m["date"]})
        desc = "; ".join(sorted({f"{m['source']} {m['product']} ({m['sensor']}), source resolution {m['res']} m, "
                                 f"deepest real zoom {m['max_level']}" for m in metas}))
        out.append({
            "id": P["mosaic_source"][key], "kind": "imagery",
            "citation_or_service": ("Esri World Imagery tile service, " + rec["tile_url"] +
                                    "; Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community. "
                                    + (f"Imagery under the measured structures (World_Imagery/MapServer identify): {desc}." if desc else "")),
            "locator": (f"zoom {rec['zoom']}, tiles x {rec['tile_x'][0]}-{rec['tile_x'][1]}, y {rec['tile_y'][0]}-{rec['tile_y'][1]}; "
                        f"mosaic origin at global pixel ({rec['origin_global_px'][0]}, {rec['origin_global_px'][1]}), "
                        f"{rec['size_px'][0]} x {rec['size_px'][1]} px; retrieved {rec['made_utc']}"),
            "file": rec["file"], "sha256": rec["sha256"], "north_reference": "true",
            "north_label_text": "no label; Web Mercator (EPSG:3857) tile grid, whose columns run to true north",
            "survey_year": None,
            "imagery_date": (dates[0] if len(dates) == 1 else ("; ".join(dates) if dates else None)),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("picks")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    P = json.loads(Path(a.picks).read_text())
    mos = P["mosaics"]
    structures = []
    M = {}
    for ln in P["lines"]:
        m = line_metrics(ln, mos)
        M[ln["id"]] = m
        (lo1, la1), (lo2, la2) = m["lonlat"]
        structures.append({
            "id": ln["id"], "source": P["mosaic_source"][ln["mosaic"]], "part": ln["part"], "kind": ln["kind"],
            "description": ln["description"],
            "endpoints": (f"z{m['z']} global px P1=({m['p1'][0]:.1f}, {m['p1'][1]:.1f}) P2=({m['p2'][0]:.1f}, {m['p2'][1]:.1f}); "
                          f"lon-lat P1=({lo1:.6f}, {la1:.6f}) P2=({lo2:.6f}, {la2:.6f})"),
            "length_m": round(m["length_m"], 1), "bearing_deg": round(m["bearing"], 2),
            "deviation_deg": round(m["dev"], 2), "sigma_deg": round(m["sigma"], 2),
            "phase": ln.get("phase"), "confidence": ln["confidence"],
        })
        if not a.quiet:
            print(f"{ln['id']:5s} {ln['part'][:22]:22s} L={m['length_m']:6.1f}m  sig={m['sigma']:.2f}  "
                  f"conf={ln['confidence']}")
    systems = []
    for sy in P.get("systems", []):
        ids = sy["structures"]
        st = system_stats([M[i]["dev"] for i in ids], [M[i]["length_m"] for i in ids], [M[i]["sigma"] for i in ids])
        systems.append({"id": sy["id"], "source": sy.get("source", "src1"), "part": sy["part"], "structures": ids,
                        "deviation_deg": round(st[0], 2), "se_deg": round(st[1], 2), "sd_deg": round(st[2], 2),
                        "total_length_m": round(st[3], 1), "n_lines": st[4]})
        if not a.quiet:
            print(f"{sy['id']:6s} {sy['part'][:30]:30s} n={st[4]:2d} L={st[3]:7.1f}m")
    out = {
        "town": P["town"], "role": "img-A",
        "measured_utc": P.get("measured_utc") or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": P["location"], "sources": P.get("sources") or build_sources(P), "structures": structures, "systems": systems,
        "main_system": P.get("main_system"), "main_system_reason": P.get("main_system_reason", ""),
        "published_values": P.get("published_values", []),
        "measurable": P.get("measurable", bool(structures)), "notes": P.get("notes", ""),
    }
    if a.write:
        OUTDIR.mkdir(exist_ok=True)
        q = OUTDIR / f"{P['town']}.json"
        q.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", q)


if __name__ == "__main__":
    main()
