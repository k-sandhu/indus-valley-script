"""Run the img-B measurement for one town from its configuration file.

Usage: python experiments/2026-10-21-town-axes/measure-img-B/code/measure.py <slug> [--quick]

The configuration (code/configs/<slug>.json) holds everything we decided by
eye: the imagery sources and mosaic extent, the polygons around exposed
Harappan architecture (mosaic pixel coordinates), holes for modern or
non-Harappan features, an optional control polygon on bare ground, and the
check lines accepted by eye. This script computes the gradient-orientation
peaks, the resampling and sensitivity errors and the check-line bearings,
writes inspection overlays under the raw-data directory, and writes the town
file towns/<slug>.json.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import orient  # noqa: E402
import tiles  # noqa: E402

HERE = Path(__file__).resolve().parent
ROLE = HERE.parent
VIEWS = tiles.RAW / "views"


def load_cfg(slug):
    return json.loads((HERE / "configs" / f"{slug}.json").read_text(encoding="utf-8"))


def to_global(pts, origin):
    return [[p[0] + origin[0], p[1] + origin[1]] for p in pts]


def lonlat_poly(pts_local, origin, z):
    out = []
    for x, y in to_global(pts_local, origin):
        lon, lat = tiles.px_to_lonlat(x, y, z)
        out.append([round(lon, 7), round(lat, 7)])
    return out


def relpath(p):
    return str(Path(p).relative_to(tiles.ROOT)).replace("\\", "/")


def overlay(rgb, polys, holes, dev, out, lines=(), pad=40, hist=None, label=""):
    allp = np.concatenate([np.asarray(p, float) for p in polys])
    x0, y0 = np.maximum(allp.min(0).astype(int) - pad, 0)
    x1, y1 = allp.max(0).astype(int) + pad
    x1 = min(x1, rgb.shape[1]); y1 = min(y1, rgb.shape[0])
    sc = max(1.0, min(3.0, 900.0 / max(x1 - x0, y1 - y0)))
    im = Image.fromarray(rgb[y0:y1, x0:x1].copy())
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    W, H = im.size
    hh = 140 if hist is not None else 0
    canvas = Image.new("RGB", (max(W, 720), H + hh), (0, 0, 0))
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas)
    t = math.radians(dev)
    for base in (t, t + math.pi / 2):
        ux, uy = math.sin(base), -math.cos(base)
        nx, ny = -uy, ux
        L = W + H
        for k in range(-L, L, 80):
            cx, cy = W / 2 + k * nx, H / 2 + k * ny
            d.line([(cx - L * ux, cy - L * uy), (cx + L * ux, cy + L * uy)], fill=(255, 255, 0), width=1)
    d.rectangle([0, H, canvas.width, H + hh], fill=(0, 0, 0))
    for p in polys:
        q = [((a - x0) * sc, (b - y0) * sc) for a, b in p]
        d.line(q + [q[0]], fill=(255, 0, 255), width=2)
    for p in holes:
        q = [((a - x0) * sc, (b - y0) * sc) for a, b in p]
        d.line(q + [q[0]], fill=(0, 255, 255), width=2)
    for (a, b), (c, e) in lines:
        d.line([((a - x0) * sc, (b - y0) * sc), ((c - x0) * sc, (e - y0) * sc)], fill=(255, 0, 0), width=2)
    if hist is not None:
        h = np.asarray(hist)
        hw = 720
        hn = (h - h.min()) / (h.max() - h.min() + 1e-12)
        pts = [(i * hw / len(h), H + hh - 15 - hn[i] * (hh - 35)) for i in range(len(h))]
        for v in range(-45, 46, 5):
            X = (v + 45) / 90 * hw
            d.line([(X, H + 15), (X, H + hh - 15)], fill=(70, 70, 70) if v % 15 else (150, 150, 150))
            if v % 15 == 0:
                d.text((X + 2, H + hh - 13), str(v), fill=(200, 200, 200))
        d.line(pts, fill=(0, 255, 0), width=2)
        d.text((3, H + 2), label + f"  (crop x{x0}-{x1}, y{y0}-{y1}, scale {sc:.2f})", fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=88)


def load_source(cfg, sdef, z):
    """Build one imagery source record and load its mosaic."""
    rel = sdef.get("wayback_release")
    x, y = sdef["x"], sdef["y"]
    lat0, lon0 = cfg["location"]["lat"], cfg["location"]["lon"]
    if rel:
        mrec = tiles.wb_mosaic(sdef["name"], rel, z, x[0], y[0], x[1], y[1])
        meta = tiles.wb_metadata(rel, lon0, lat0, z)
        lay = {}
        for k in ("4", "5", "6"):  # finest metadata layer whose zoom range covers z
            v = meta["by_layer"].get(k)
            if v and (v.get("MinMapLevel") or 0) <= z <= (v.get("MaxMapLevel") or 99):
                lay = v
                break
        d = str(lay.get("SRC_DATE") or "")
        img_date = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else None
        rel_date = dict(tiles.wb_releases()).get(rel)
        service = ("Esri World Imagery Wayback, release " + rel + f" (World Imagery as published {rel_date}), "
                   + tiles.WB_TILE_URL.replace("{rel}", rel) + "; " + tiles.ATTRIBUTION)
        imeta = {"source_info": lay.get("NICE_NAME"), "source": lay.get("NICE_DESC"), "description": lay.get("SRC_DESC"),
                 "resolution_m": lay.get("SRC_RES"), "metadata_layer_url": meta["metadata_url"], "wayback_release": rel,
                 "wayback_release_date": rel_date,
                 "metadata_layers": {k: {"SRC_DATE": v.get("SRC_DATE"), "SRC_DESC": v.get("SRC_DESC"), "MinMapLevel": v.get("MinMapLevel"),
                                         "MaxMapLevel": v.get("MaxMapLevel")} for k, v in meta["by_layer"].items()}}
    else:
        mrec = tiles.mosaic(sdef["name"], z, x[0], y[0], x[1], y[1])
        meta = tiles.imagery_summary(lon0, lat0)
        top = meta["layers"][0] if meta["layers"] else {}
        d = top.get("date") or ""
        img_date = f"{d[:4]}-{d[4:6]}-{d[6:]}" if (len(d) == 8 and d.isdigit()) else None
        service = "Esri World Imagery tile service, " + tiles.TILE_URL + "; " + tiles.ATTRIBUTION
        imeta = {k: top.get(k) for k in ("source", "source_info", "description", "resolution_m", "max_level", "block", "release")}
        imeta["identify_retrieved_utc"] = meta["retrieved_utc"]
    mpp = tiles.m_per_px(lat0, z)
    src = {
        "id": sdef["id"], "kind": "imagery", "citation_or_service": service,
        "locator": f"zoom {z}, tiles x {x[0]}-{x[1]}, y {y[0]}-{y[1]}",
        "file": mrec["path"], "sha256": mrec["sha256"],
        "north_reference": "true", "north_label_text": "Web Mercator grid north (true north at every point; north up)",
        "survey_year": None, "imagery_date": img_date, "imagery_metadata": imeta,
        "mosaic_pixel_origin_global": mrec["origin_px"], "m_per_px": round(mpp, 4),
        "role_in_measurement": sdef.get("role", "measured"),
    }
    rgb = tiles.load_mosaic(mrec)
    return src, rgb, mrec["origin_px"], mpp


def run(slug, quick=False):
    cfg = load_cfg(slug)
    z = cfg["zoom"]
    sdefs = cfg.get("sources") or [dict(cfg["mosaic"], id="src1")]
    S_ = {sd["id"]: load_source(cfg, sd, z) for sd in sdefs}
    first = sdefs[0]["id"]
    structures, systems, diag = [], [], {}
    nboot = 200 if quick else 1000
    control = None
    if cfg.get("control"):
        c = cfg["control"]
        src, rgb, origin, mpp = S_[c.get("source", first)]
        rc = orient.analyse(rgb, [c["poly"]], m_per_px=mpp, n_boot=50)
        hs = np.asarray(rc["_hist"])
        zero_bin = int(45 / orient.BIN)
        control = {"source": c.get("source", first), "description": c["description"],
                   "polygon_lonlat": lonlat_poly(c["poly"], origin, z),
                   "peak_deviation_deg": rc["peak_deviation_deg"], "peak_contrast": rc["peak_contrast"],
                   "cardinal_excess": round(float((hs[zero_bin] - hs.min()) / hs.min()), 3) if hs.min() > 0 else None,
                   "peaks": rc["all_peaks"][:3]}
    part_results = {}
    for P in cfg["parts"]:
        sid = P.get("source", first)
        src, rgb, origin, mpp = S_[sid]
        polys, holes = P["polys"], P.get("holes", [])
        r = orient.analyse(rgb, polys, holes, m_per_px=mpp, n_boot=nboot, block_m=P.get("block_m", 30.0))
        variants = []
        rot = rot2 = jpull = None
        if not quick:
            for sg in (0.7, 1.0, 1.5):
                for th in (40.0, 60.0, 80.0):
                    if sg == 1.0 and th == 60.0:
                        continue
                    rv = orient.analyse(rgb, polys, holes, m_per_px=mpp, n_boot=1, sigma=sg, thresh_pct=th)
                    variants.append({"grad_sigma_px": sg, "threshold_pct": th, "peak": rv["peak_deviation_deg"]})
            rot = orient.rotation_test(rgb, polys, holes, angle=17.0, m_per_px=mpp)
            rot2 = orient.rotation_test(rgb, polys, holes, angle=-29.0, m_per_px=mpp)
            jpull = orient.jpeg_pull_test(rgb, polys, holes, m_per_px=mpp)
        jp = [r["peak_deviation_deg"] + v for v in (jpull or {}).values()]
        vp = np.array([v["peak"] for v in variants] + [x for x in (rot, rot2) if x is not None] + jp + [r["peak_deviation_deg"]])
        vdev = orient.wrap90(vp - r["peak_deviation_deg"])
        sens_sd = float(np.std(vdev)) if len(vdev) > 1 else 0.0
        se_total = math.sqrt(r["bootstrap_se_deg"] ** 2 + sens_sd ** 2)
        hist = r.pop("_hist")
        part_results[P["id"]] = (r, se_total)
        out = VIEWS / slug / f"{P['id']}_overlay.jpg"
        overlay(rgb, polys, holes, r["peak_deviation_deg"], out, hist=hist, label=f"{P['id']} peak {r['peak_deviation_deg']:+.2f}")
        diag[P["id"]] = {"source": sid, "analysis": r, "sensitivity": variants, "sensitivity_sd_deg": round(sens_sd, 3),
                         "sensitivity_note": "standard deviation of the peak about the default peak over eight parameter variants, two rotation tests and four rotate-and-recompress tests",
                         "rotation_test_recovered_deg": [rot, rot2], "jpeg_pull_test_shortfall_deg": jpull,
                         "overlay": relpath(out)}
        structures.append({
            "id": P["id"], "source": sid, "part": P["part"], "kind": "area orientation (gradient histogram)",
            "description": P["description"],
            "endpoints": "polygon; see polygon_lonlat",
            "polygon_lonlat": [lonlat_poly(p, origin, z) for p in polys],
            "holes_lonlat": [lonlat_poly(p, origin, z) for p in holes],
            "holes_note": P.get("holes_note"),
            "length_m": None,
            "area_m2": r["mask_area_m2"],
            "bearing_deg": round(r["peak_deviation_deg"] % 90.0, 2),
            "bearing_perpendicular_deg": round(r["peak_deviation_deg"] % 90.0 + 90.0, 2),
            "deviation_deg": round(r["peak_deviation_deg"], 2),
            "sigma_deg": round(se_total, 2),
            "secondary_peaks": r["secondary_peaks"],
            "family_share": r["family_share"],
            "phase": P.get("phase"), "confidence": P.get("confidence", "medium"),
            "eye_check": P.get("eye_check"),
        })
    lines_by_sys = {}
    for C in cfg.get("check_lines", []):
        sid = C.get("source", first)
        src, rgb, origin, mpp = S_[sid]
        p0, p1 = C["p0"], C["p1"]
        bh, dh = orient.line_bearing(*p0, *p1)
        ref = None
        if not C.get("no_refine"):
            gray = orient.luminance(rgb.astype(np.float64))
            ref = orient.refine_line(gray, p0, p1, search=C.get("search", 4))
        Lh = math.dist(p0, p1)
        use_ref = False
        if ref:
            br, dr = orient.line_bearing(*ref["p0"], *ref["p1"])
            if abs(orient.wrap90(dr - dh)) < max(3.0, 3 * math.degrees(math.sqrt(2) * 1.5 / Lh)) and ref["span_px"] > 0.6 * Lh:
                use_ref = True
        if use_ref:
            a, b = ref["p0"], ref["p1"]
            L = math.dist(a, b)
            bear, devi = orient.line_bearing(*a, *b)
            se_pix = math.degrees(math.sqrt(2) * 1.0 / L)
            sig = math.sqrt((2 * ref["slope_se_deg"]) ** 2 + se_pix ** 2)
            how = f"refined edge fit ({ref['n_pts']} points, rms {ref['rms_px']} px) from hand-picked endpoints"
        else:
            a, b = p0, p1
            L = Lh
            bear, devi = bh, dh
            e_px = C.get("endpoint_sigma_px", 1.5)
            sig = math.degrees(math.sqrt(2) * e_px / L)
            how = C.get("method") or "hand-picked endpoints (edge refinement not used)"
        ga, gb = to_global([a], origin)[0], to_global([b], origin)[0]
        lla, llb = tiles.px_to_lonlat(*ga, z), tiles.px_to_lonlat(*gb, z)
        structures.append({
            "id": C["id"], "source": sid, "part": C["part"], "kind": C["kind"], "description": C["description"],
            "endpoints": {"global_px_z%d" % z: [[round(ga[0], 1), round(ga[1], 1)], [round(gb[0], 1), round(gb[1], 1)]],
                          "lonlat": [[round(lla[0], 7), round(lla[1], 7)], [round(llb[0], 7), round(llb[1], 7)]],
                          "method": how} | ({"bearing_before_refinement_deg": round(bh, 2)} if use_ref else {}),
            "length_m": round(L * mpp, 1), "bearing_deg": round(bear, 2), "deviation_deg": round(devi, 2),
            "sigma_deg": round(sig, 2), "phase": C.get("phase"), "confidence": C.get("confidence", "medium"),
        })
        lines_by_sys.setdefault(C["system"], []).append((devi, sig, L * mpp, C["id"]))
        out = VIEWS / slug / f"{C['id']}_line.jpg"
        overlay(rgb, [[p0, p1, [p1[0] + 1, p1[1] + 1]]], [], 0, out, lines=[(tuple(a), tuple(b))], pad=60)
    for S in cfg["systems"]:
        part_id = S.get("auto_part")
        ls = lines_by_sys.get(S["id"], [])
        sid = S.get("source") or next((P.get("source", first) for P in cfg["parts"] if P["id"] == part_id), first)
        rec = {"id": S["id"], "source": sid, "part": S["part"], "structures": ([part_id] if part_id else []) + [l[3] for l in ls]}
        if ls:
            dv = np.array([l[0] for l in ls])
            wl = np.array([l[2] for l in ls])
            ref_dev = part_results[part_id][0]["peak_deviation_deg"] if part_id else dv[np.argmax(wl)]
            dv = ref_dev + orient.wrap90(dv - ref_dev)
            wm = float(np.sum(dv * wl) / np.sum(wl))
            sd = float(np.sqrt(np.sum(wl * (dv - wm) ** 2) / np.sum(wl))) if len(dv) > 1 else None
            neff = (wl.sum() ** 2) / np.sum(wl ** 2)
            sig_each = np.array([l[1] for l in ls])
            se_meas = float(np.sqrt(np.sum((wl * sig_each) ** 2)) / wl.sum())
            se_l = max(sd / math.sqrt(neff), se_meas) if (sd is not None and len(dv) > 2) else se_meas
            rec["check_lines"] = {"weighted_mean_deviation_deg": round(wm, 2), "se_deg": round(se_l, 2),
                                  "sd_deg": round(sd, 2) if sd is not None else None,
                                  "total_length_m": round(float(wl.sum()), 1), "n_lines": len(ls)}
        if part_id:
            r, se_total = part_results[part_id]
            rec.update({"basis": "automatic gradient-histogram peak of " + part_id,
                        "deviation_deg": round(r["peak_deviation_deg"], 2), "se_deg": round(se_total, 2),
                        "sd_deg": rec.get("check_lines", {}).get("sd_deg"),
                        "sd_basis": "standard deviation of the check lines in this system about their weighted mean",
                        "block_peak_sd_deg": r["block_peak_sd_deg"],
                        "total_length_m": rec.get("check_lines", {}).get("total_length_m", 0.0),
                        "n_lines": rec.get("check_lines", {}).get("n_lines", 0)})
        else:
            cl = rec["check_lines"]
            rec.update({"basis": "lines measured from endpoints only (no automatic polygon)",
                        "deviation_deg": cl["weighted_mean_deviation_deg"], "se_deg": cl["se_deg"], "sd_deg": cl["sd_deg"],
                        "total_length_m": cl["total_length_m"], "n_lines": cl["n_lines"]})
        if S.get("note"):
            rec["note"] = S["note"]
        systems.append(rec)
    town = {
        "town": slug, "role": "img-B",
        "measured_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": cfg["location"],
        "sources": [S_[sd["id"]][0] for sd in sdefs],
        "structures": structures,
        "systems": systems,
        "main_system": cfg.get("main_system"), "main_system_reason": cfg.get("main_system_reason"),
        "published_values": cfg.get("published_values", []),
        "measurable": cfg.get("measurable", True),
        "notes": cfg.get("notes", ""),
        "diagnostics": {"control_area": control, "parts": diag,
                        "method": "see METHOD.md; deviation peaks from magnitude-weighted gradient-direction histograms folded modulo 90 degrees"},
    }
    (ROLE / "towns").mkdir(parents=True, exist_ok=True)
    (ROLE / "towns" / f"{slug}.json").write_text(json.dumps(town, indent=1, ensure_ascii=False), encoding="utf-8")
    return town


if __name__ == "__main__":
    t = run(sys.argv[1], quick="--quick" in sys.argv)
    for s in t["structures"]:
        print(s["id"], s["source"], s["kind"], s.get("deviation_deg"), s.get("sigma_deg"), s.get("length_m"), s.get("secondary_peaks", ""))
    for s in t["systems"]:
        print(s["id"], s["deviation_deg"], s["se_deg"], s.get("check_lines"))
    print(json.dumps(t["diagnostics"]["control_area"]))
    for k, v in t["diagnostics"]["parts"].items():
        print(k, v["analysis"]["halves"], v["analysis"]["family_share"], v["sensitivity_sd_deg"], v["rotation_test_recovered_deg"],
              v["jpeg_pull_test_shortfall_deg"], v["analysis"]["peak_contrast"], v["analysis"]["block_peak_sd_deg"])
