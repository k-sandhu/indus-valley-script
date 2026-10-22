"""Build one town file of the plan-A measurement from per-plan results.

usage: python compile_town.py TOWNCONFIG.json OUT.json

The town config lists the plan sources (citation, locator, files, north arrow
label and class) with the measurement result of each plan, written by
measure_lines.py. Structures are renamed <source>-<line id>. Lines are grouped
into systems separately for each source and each part of the town: within a
group, lines are sorted by deviation and a new system starts wherever the gap
to the previous line exceeds `gap_deg` (default 2.5 degrees), with the circular
wrap at +/-45 degrees handled by rotating the sort to start at the largest gap.
A system may also be given by hand in the config (`systems`), which then
replaces the automatic grouping for its source and part.

For each system we report the length-weighted mean deviation, the standard
deviation of the lines about it (length-weighted), and a standard error that
combines the scatter term sd/sqrt(n_eff), with n_eff = (sum L)^2 / sum L^2,
and the error common to all lines of the same plan (north arrow and rendering),
which does not average down.
"""
import sys, json, math, hashlib, datetime, os


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def wrapdiff(a, b):
    return ((a - b + 45.0) % 90.0) - 45.0


def system_stats(lines, common):
    w = [l["length_m"] or l["length_px"] for l in lines]
    ref = lines[0]["deviation_deg"]
    ds = [ref + wrapdiff(l["deviation_deg"], ref) for l in lines]
    W = sum(w)
    m = sum(wi * di for wi, di in zip(w, ds)) / W
    sd = math.sqrt(sum(wi * (di - m) ** 2 for wi, di in zip(w, ds)) / W) if len(ds) > 1 else 0.0
    neff = W ** 2 / sum(wi ** 2 for wi in w)
    if len(ds) > 1:
        scat = sd / math.sqrt(max(neff - 1.0, 1.0))
    else:
        scat = math.sqrt(max(lines[0]["sigma_deg"] ** 2 - common ** 2, 0.0))
    se = math.sqrt(scat ** 2 + common ** 2)
    m = ((m + 45.0) % 90.0) - 45.0
    return round(m, 2), round(se, 2), round(sd, 2), neff


def auto_groups(lines, gap):
    if len(lines) == 1:
        return [lines]
    s = sorted(lines, key=lambda l: l["deviation_deg"])
    ds = [l["deviation_deg"] for l in s]
    n = len(s)
    gaps = [(ds[(i + 1) % n] - ds[i]) % 90.0 for i in range(n)]
    start = (max(range(n), key=lambda i: gaps[i]) + 1) % n
    order = s[start:] + s[:start]
    groups = [[order[0]]]
    for a, b in zip(order, order[1:]):
        if (b["deviation_deg"] - a["deviation_deg"]) % 90.0 > gap:
            groups.append([b])
        else:
            groups[-1].append(b)
    return groups


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    gap = cfg.get("gap_deg", 2.5)
    town = {"town": cfg["town"], "role": "plan-A",
            "measured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "location": cfg["location"], "sources": [], "structures": [], "systems": []}
    sysn = 0
    for src in cfg["sources"]:
        rec = {k: src.get(k) for k in ("id", "kind", "citation_or_service", "locator", "file", "sha256",
                                         "north_reference", "north_label_text", "survey_year", "imagery_date")}
        rec["kind"] = "plan"
        if src.get("file") and os.path.exists(src["file"]) and not src.get("sha256"):
            rec["sha256"] = sha(src["file"])
        for k in ("pdf_page_index", "printed_page", "figure", "scale_bar", "measured_image",
                  "image_derivation",
                  "measured_image_sha256", "render_check", "arrow_measured", "measurable", "reason"):
            if k in src:
                rec[k] = src[k]
        if not src.get("result"):
            town["sources"].append(rec)
            continue
        res = json.load(open(src["result"], encoding="utf-8"))
        rec["measured_image"] = res["image"]
        rec["measured_image_sha256"] = res["image_sha256"]
        spec = json.load(open(res["spec"], encoding="utf-8"))
        if spec.get("image_derivation"):
            rec["image_derivation"] = spec["image_derivation"]
        rec["spec"] = res["spec"].replace("\\", "/")
        rec["result"] = src["result"]
        if spec.get("render_note"):
            rec["render_check"] = spec["render_note"]
        rec["arrow_note"] = spec["north"].get("note", "")
        rec["arrow_measured"] = {"image_azimuth_deg": res["north"]["azimuth_img_deg"],
                                 "length_px": res["north"]["length_px"],
                                 "sigma_deg": res["north"]["sigma_deg"]}
        if "scale" in res:
            rec["scale_measured"] = res["scale"]
        rec["render_sigma_deg"] = res.get("render_sigma_deg", 0.0)
        rec["frame_checks"] = [{"id": f["id"], "relative_to_north_deg": f["relative_to_north_deg"],
                                "length_px": f["length_px"]} for f in res.get("frame", [])]
        town["sources"].append(rec)
        common = math.hypot(res["north"]["sigma_deg"], res.get("render_sigma_deg", 0.0))
        meta = {l["id"]: l for l in src.get("line_meta", [])}
        mine = []
        for l in res["lines"]:
            if l["id"] in src.get("exclude", []):
                continue
            m = meta.get(l["id"], {})
            s = {"id": f'{src["id"]}-{l["id"]}', "source": src["id"],
                 "part": m.get("part", l.get("part")), "kind": m.get("kind", l.get("kind")),
                 "description": m.get("description", l.get("description")),
                 "endpoints": "image px (x, y) on the measured image: (%.1f, %.1f) to (%.1f, %.1f)" % (
                     l["p1_px"][0], l["p1_px"][1], l["p2_px"][0], l["p2_px"][1]),
                 "length_m": l["length_m"], "bearing_deg": l["bearing_deg"],
                 "deviation_deg": l["deviation_deg"], "sigma_deg": l["sigma_deg"],
                 "phase": m.get("phase", l.get("phase")),
                 "confidence": m.get("confidence", l.get("confidence", "medium"))}
            s["length_px"] = l["length_px"]
            mine.append(s)
        town["structures"].extend(mine)
        manual = [g for g in cfg.get("systems", []) if g["source"] == src["id"]]
        manual_parts = {g["part"] for g in manual}
        groups = []
        for g in manual:
            members = [s for s in mine if s["id"] in g["structures"]]
            groups.append((g["part"], members, g.get("note")))
        parts = []
        for s in mine:
            if s["part"] not in parts:
                parts.append(s["part"])
        for p in parts:
            if p in manual_parts:
                continue
            for grp in auto_groups([s for s in mine if s["part"] == p], gap):
                groups.append((p, grp, None))
        for part, members, note in groups:
            if not members:
                continue
            sysn += 1
            dev, se, sd, neff = system_stats(members, common)
            sy = {"id": f"sys{sysn}", "source": src["id"], "part": part,
                  "structures": [s["id"] for s in members], "deviation_deg": dev, "se_deg": se,
                  "sd_deg": sd, "total_length_m": round(sum(s["length_m"] or 0 for s in members), 1),
                  "n_lines": len(members)}
            if note:
                sy["note"] = note
            town["systems"].append(sy)
    for s in town["structures"]:
        s.pop("length_px", None)
    town["main_system"] = cfg.get("main_system")
    if cfg.get("main_system_structure"):
        for sy in town["systems"]:
            if cfg["main_system_structure"] in sy["structures"]:
                town["main_system"] = sy["id"]
    town["main_system_reason"] = cfg.get("main_system_reason")
    town["published_values"] = cfg.get("published_values", [])
    town["measurable"] = cfg.get("measurable", bool(town["structures"]))
    town["notes"] = cfg.get("notes", "")
    json.dump(town, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for sy in town["systems"]:
        print(sy["id"], sy["source"], sy["part"], sy["n_lines"], sy["total_length_m"], sy["deviation_deg"],
              sy["se_deg"], sy["sd_deg"], sy["structures"])


if __name__ == "__main__":
    main()
