"""Turn a plan-B measurement spec into the town JSON required by the brief.

Usage: python .../code/build_town.py SLUG [SLUG ...]   (or --all)

Reads experiments/2026-10-21-town-axes/measure-plan-B/code/specs/<slug>.json and writes
experiments/2026-10-21-town-axes/measure-plan-B/towns/<slug>.json.

Geometry. All picks are in page pixels of the named render (x right, y down). The page
azimuth of a direction (dx, dy) is atan2(dx, -dy), clockwise from page-up. The plan north
is the page azimuth of the arrow shaft from tail to tip. A line's bearing relative to plan
north is (line azimuth - arrow azimuth) mod 180, and its deviation is that bearing folded to
the nearest cardinal direction, ((b + 45) mod 90) - 45.

Errors. A line's picking error is atan(sqrt(2) * e / L), where L is its length in pixels
and e the endpoint uncertainty in pixels: the larger of the stated pick sigma and the RMS
scatter of the ink about the fitted line. The arrow gets the same picking term from its
shaft length, plus a drafting term stated in the spec. The rendering term comes from the
page's own frame or grid: a rigid rotation of the scan rotates arrow and lines together and
cancels, so only shear and curvature matter, which we estimate as the RSS of half the
angle between the two frame lines of each pair and the departure of the frame from a right
angle. The line sigma is the RSS of its picking, arrow and rendering terms. A system's
standard error is the RSS of the length-weighted scatter divided by the square root of the
effective number of lines and the common arrow and rendering error, which does not average
down across lines of one plan.
"""
import datetime
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROLE = os.path.dirname(HERE)
SPECS = os.path.join(HERE, "specs")
TOWNS = os.path.join(ROLE, "towns")
sys.path.insert(0, HERE)
import refine as R  # noqa: E402

_gray_cache = {}
_sha_cache = {}


def gray(path):
    if path not in _gray_cache:
        _gray_cache[path] = R.load_gray(path)
    return _gray_cache[path]


def sha(path):
    if path not in _sha_cache:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        _sha_cache[path] = h.hexdigest()
    return _sha_cache[path]


def page_az(p1, p2, directed=False):
    a = math.degrees(math.atan2(p2[0] - p1[0], -(p2[1] - p1[1])))
    return a % 360.0 if directed else a % 180.0


def measure_segment(render, seg, default_pick=1.0):
    """Return azimuth (0-180), length px, pick sigma deg, fitted endpoints, note."""
    p1, p2 = seg.get("p1"), seg.get("p2")
    pick = seg.get("pick_px", default_pick)
    ref = seg.get("refine")
    note = "hand pick"
    rms = 0.0
    if ref and seg.get("pieces"):
        r = R.fit_multi(gray(render), seg["pieces"], band=ref.get("band", 4.0), trim=ref.get("trim", 0.05),
                        mode=ref.get("mode", "ink"), thr=ref.get("thr"))
        p1, p2 = seg["pieces"][0][:2], seg["pieces"][-1][2:]
    elif ref:
        r = R.fit(gray(render), p1[0], p1[1], p2[0], p2[1], band=ref.get("band", 4.0), trim=ref.get("trim", 0.08),
                  mode=ref.get("mode", "ink"), thr=ref.get("thr"))
    if ref:
        if r is None:
            raise SystemExit("refine failed for %s" % seg.get("id"))
        d = ((r["az_fit"] - page_az(p1, p2) + 90) % 180) - 90
        if abs(d) > ref.get("max_diff", 4.0):
            raise SystemExit("refine moved %s by %.2f deg; check the pick" % (seg.get("id"), d))
        az = r["az_fit"]
        rms = r["rms"]
        q1, q2 = r["p1"], r["p2"]
        L = r["length_px"]
        note = "fitted to %d %s pixels within %.1f px (RMS %.2f px)" % (r["n"], ref.get("mode", "ink"), ref.get("band", 4.0), rms)
    else:
        az = page_az(p1, p2)
        q1, q2 = p1, p2
        L = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    e = max(pick, rms)
    sig = math.degrees(math.atan(math.sqrt(2) * e / L))
    return az, L, sig, q1, q2, note


def fold(b):
    return ((b + 45.0) % 90.0) - 45.0


def frame_term(render, frame):
    """Return (skew_deg, distortion_sigma_deg, text)."""
    if not frame:
        return None, None, None
    az = {}
    for k in ("top", "bottom", "left", "right", "h1", "h2", "v1", "v2"):
        if k in frame:
            seg = {"p1": frame[k][0], "p2": frame[k][1], "refine": frame.get("refine")}
            a, L, s, _, _, _ = measure_segment(render, seg)
            az[k] = a
    hs = [az[k] for k in ("top", "bottom", "h1", "h2") if k in az]
    vs = [((az[k] + 90) % 180) - 90 for k in ("left", "right", "v1", "v2") if k in az]
    parts = []
    terms = []
    skew = []
    for h in hs:
        skew.append(((h - 90 + 90) % 180) - 90)
    for v in vs:
        skew.append(((v + 90) % 180) - 90)
    if len(hs) >= 2:
        dh = ((hs[0] - hs[1] + 90) % 180) - 90
        terms.append(dh / 2)
        parts.append("horizontal pair differ by %.2f deg" % dh)
    if len(vs) >= 2:
        dv = ((vs[0] - vs[1] + 90) % 180) - 90
        terms.append(dv / 2)
        parts.append("vertical pair differ by %.2f deg" % dv)
    if hs and vs:
        orth = ((np.mean(hs) - np.mean(vs) - 90 + 90) % 180) - 90
        terms.append(orth)
        parts.append("frame departs from a right angle by %.2f deg" % orth)
    sk = float(np.mean(skew)) if skew else None
    dist = float(math.sqrt(sum(t * t for t in terms))) if terms else None
    txt = "page skew %.2f deg (rigid, cancels); " % sk + "; ".join(parts) if sk is not None else None
    return sk, dist, txt


def build(slug):
    with open(os.path.join(SPECS, slug + ".json"), encoding="utf-8") as f:
        spec = json.load(f)
    out_sources = []
    src_geo = {}
    for s in spec["sources"]:
        o = {k: s.get(k) for k in ("id", "kind", "citation_or_service", "locator", "file", "sha256", "north_reference",
                                    "north_label_text", "survey_year", "imagery_date")}
        o["kind"] = "plan"
        if s.get("file") and os.path.exists(s["file"]) and not s.get("sha256"):
            o["sha256"] = sha(s["file"])
        o["pdf_page_index"] = s.get("pdf_page_index")
        o["printed_page"] = s.get("printed_page")
        o["render"] = s.get("render")
        if s.get("render"):
            o["render_sha256"] = sha(s["render"])
        o["render_dpi"] = s.get("render_dpi")
        o["scale_bar"] = s.get("scale_bar_text")
        geo = {}
        if s.get("arrow"):
            arr = s["arrow"]
            seg = {"p1": arr["tail"], "p2": arr["tip"], "refine": arr.get("refine"), "pick_px": arr.get("pick_px", 1.0),
                   "pieces": arr.get("pieces")}
            a, L, sig, q1, q2, note = measure_segment(s["render"], seg)
            # direction from tail to tip
            d360 = page_az(arr["tail"], arr["tip"], directed=True)
            if abs(((a - d360) + 90) % 180 - 90) > 5:
                raise SystemExit("arrow fit disagrees with pick")
            a_dir = a if abs(((a - d360 + 180) % 360) - 180) < 90 else (a + 180) % 360
            draft = arr.get("drafting_sigma_deg", 0.5)
            geo["arrow_az"] = a_dir
            geo["arrow_sigma"] = math.sqrt(sig ** 2 + draft ** 2)
            o["north_arrow_measurement"] = {
                "tail_px": arr["tail"], "tip_px": arr["tip"], "page_azimuth_deg": round(a_dir, 3),
                "shaft_length_px": round(L, 1), "pick_sigma_deg": round(sig, 3), "drafting_sigma_deg": draft,
                "method": note, "description": arr.get("description")}
        sk, dist, txt = frame_term(s["render"], s.get("frame"))
        if dist is None:
            dist = s.get("render_sigma_default", 0.3)
            txt = s.get("render_note", "no frame or grid measured; assumed %.2f deg for shear and curvature of the scan" % dist)
        geo["render_sigma"] = max(dist, s.get("render_sigma_min", 0.05))
        o["rendering_check"] = {"skew_deg": None if sk is None else round(sk, 3), "distortion_sigma_deg": round(geo["render_sigma"], 3), "note": txt}
        if s.get("scale_bar"):
            sb = s["scale_bar"]
            Lpx = math.hypot(sb["p2"][0] - sb["p1"][0], sb["p2"][1] - sb["p1"][1])
            geo["m_per_px"] = sb["length_m"] / Lpx
            o["scale_bar_measurement"] = {"p1_px": sb["p1"], "p2_px": sb["p2"], "length_m": sb["length_m"], "m_per_px": round(geo["m_per_px"], 5)}
        elif s.get("m_per_px"):
            geo["m_per_px"] = s["m_per_px"]
        for k in ("notes", "acquisition"):
            if s.get(k):
                o[k] = s[k]
        src_geo[s["id"]] = geo
        out_sources.append(o)

    structs = []
    by_id = {}
    for st in spec.get("structures", []):
        src = next(s for s in spec["sources"] if s["id"] == st["source"])
        geo = src_geo[st["source"]]
        a, L, sig, q1, q2, note = measure_segment(src["render"], st, st.get("pick_px", src.get("pick_px", 1.0)))
        b = (a - geo["arrow_az"]) % 180.0
        dev = fold(b)
        sigma = math.sqrt(sig ** 2 + geo["arrow_sigma"] ** 2 + geo["render_sigma"] ** 2)
        length_m = L * geo["m_per_px"] if geo.get("m_per_px") else None
        o = {"id": st["id"], "source": st["source"], "part": st.get("part"), "kind": st.get("kind"),
             "description": st.get("description"),
             "endpoints": "page px on %s: (%.1f, %.1f) to (%.1f, %.1f); %s" % (os.path.basename(src["render"]), q1[0], q1[1], q2[0], q2[1], note),
             "length_m": None if length_m is None else round(length_m, 1),
             "bearing_deg": round(b, 2), "deviation_deg": round(dev, 2), "sigma_deg": round(sigma, 2),
             "phase": st.get("phase"), "confidence": st.get("confidence", "medium")}
        if st.get("notes"):
            o["notes"] = st["notes"]
        structs.append(o)
        by_id[st["id"]] = (o, sig, geo)

    systems = []
    for sy in spec.get("systems", []):
        ids = sy["structures"]
        devs = np.array([by_id[i][0]["deviation_deg"] for i in ids], float)
        ref = devs[0]
        devs = ref + (((devs - ref) + 45) % 90 - 45)
        Ls = np.array([by_id[i][0]["length_m"] or 1.0 for i in ids], float)
        w = Ls / Ls.sum()
        m = float((w * devs).sum())
        n = len(ids)
        if n > 1:
            var = float((w * (devs - m) ** 2).sum()) * n / (n - 1)
            sd = math.sqrt(var)
            neff = Ls.sum() ** 2 / (Ls ** 2).sum()
        else:
            sd, neff = 0.0, 1.0
        geo = by_id[ids[0]][2]
        common = math.sqrt(geo["arrow_sigma"] ** 2 + geo["render_sigma"] ** 2)
        pick_terms = np.array([by_id[i][1] for i in ids])
        pick_se = math.sqrt(float((w ** 2 * pick_terms ** 2).sum()))
        scatter_se = sd / math.sqrt(neff) if n > 1 else 0.0
        se = math.sqrt(max(scatter_se, pick_se) ** 2 + common ** 2)
        tot = float(sum(by_id[i][0]["length_m"] or 0.0 for i in ids))
        systems.append({"id": sy["id"], "source": sy["source"], "part": sy.get("part"), "structures": ids,
                        "deviation_deg": round(fold(m), 2), "se_deg": round(se, 2), "sd_deg": round(sd, 2),
                        "total_length_m": round(tot, 1), "n_lines": n, "description": sy.get("description")})
    town = {"town": slug, "role": "plan-B",
            "measured_utc": spec.get("measured_utc") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location": spec["location"], "sources": out_sources, "structures": structs, "systems": systems,
            "main_system": spec.get("main_system"), "main_system_reason": spec.get("main_system_reason"),
            "published_values": spec.get("published_values", []), "measurable": spec.get("measurable", bool(structs)),
            "notes": spec.get("notes", "")}
    os.makedirs(TOWNS, exist_ok=True)
    with open(os.path.join(TOWNS, slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(town, f, indent=1, ensure_ascii=False)
    print("wrote", slug, len(structs), "lines", len(systems), "systems")
    return town


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--all"]:
        args = sorted(os.path.splitext(f)[0] for f in os.listdir(SPECS) if f.endswith(".json"))
    for s in args:
        build(s)
