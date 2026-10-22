"""Build the settlement-axis table from the four measurers, the dates and the horizons (PROTOCOL.md, Data).

python combine.py --dates dates-v1/dates.json --horizons horizon-v1/horizons.json --out table-v1/settlement-axes.json
Writes the JSON table and a CSV beside it; prints only counts.
"""
from pathlib import Path
import argparse
import csv
import glob
import json
import math
import re

from common import BASE, finite, provenance, write_new

ROLES = {"A": "measure-img-A", "B": "measure-img-B", "pA": "measure-plan-A", "pB": "measure-plan-B"}
DISCOVERY = ("mohenjo-daro", "harappa", "kalibangan")
FLOOR = 0.3
SAME_PART_M = 200.0
LONLAT = re.compile(r"\(\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*\)")


def load_role(role):
    out = {}
    for f in sorted(glob.glob(str(BASE / ROLES[role] / "towns" / "*.json"))):
        j = json.loads(Path(f).read_text(encoding="utf-8"))
        out[j.get("town") or Path(f).stem] = (j, f)
    return out


def points_of_structure(s):
    """Longitude-latitude points of a structure: polygon vertices or endpoints written as (lon, lat)."""
    pts = []
    for ring in s.get("polygon_lonlat") or []:
        for p in ring:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                pts.append((float(p[0]), float(p[1])))
    ep = s.get("endpoints")
    if isinstance(ep, str) and "lon" in ep.lower():
        tail = ep[ep.lower().index("lon"):]
        for lo, la in LONLAT.findall(tail):
            lo, la = float(lo), float(la)
            if abs(la) <= 90 and abs(lo) <= 180 and 5 < la < 40 and 55 < lo < 85:
                pts.append((lo, la))
    return pts


def system_points(j, sys):
    ids = set(sys.get("structures") or [])
    pts = []
    for s in j.get("structures", []):
        if s.get("id") in ids:
            pts.extend(points_of_structure(s))
    return pts


def dist_m(p, q):
    lat = math.radians((p[1] + q[1]) / 2)
    dx = math.radians(q[0] - p[0]) * math.cos(lat) * 6371000.0
    dy = math.radians(q[1] - p[1]) * 6371000.0
    return math.hypot(dx, dy)


def near(pa, pb):
    if not pa or not pb:
        return None
    return min(dist_m(p, q) for p in pa for q in pb) <= SAME_PART_M


def main_system(j):
    if not j or not j.get("measurable", True):
        return None
    mid = j.get("main_system")
    for s in j.get("systems", []):
        if s.get("id") == mid and s.get("deviation_deg") is not None:
            return s
    return None


def source_of(j, sys):
    for s in j.get("sources", []):
        if s.get("id") == sys.get("source"):
            return s
    return {}


def wmean(vals):
    """Inverse-variance mean of (value, se) pairs; returns (mean, propagated se)."""
    vals = [(v, max(se or FLOOR, 1e-3)) for v, se in vals]
    w = [1 / se ** 2 for _, se in vals]
    m = sum(v * wi for (v, _), wi in zip(vals, w)) / sum(w)
    return m, 1 / math.sqrt(sum(w))


def imagery_value(jA, jB):
    sA, sB = main_system(jA), main_system(jB)
    rec = {"theta_img_A": finite(sA["deviation_deg"], 4) if sA else None, "se_img_A": finite(sA.get("se_deg"), 4) if sA else None,
           "theta_img_B": finite(sB["deviation_deg"], 4) if sB else None, "se_img_B": finite(sB.get("se_deg"), 4) if sB else None,
           "main_system_A": sA.get("id") if sA else None, "main_system_B": sB.get("id") if sB else None}
    if sA and sB:
        pa, pb = system_points(jA, sA), system_points(jB, sB)
        same = near(pa, pb)
        whole = any("whole" in (s.get("part") or "").lower() for s in (sA, sB))
        rec["same_part_test"] = "within 200 m" if same else ("whole town declared" if whole else ("no coordinates" if same is None else "different parts"))
        if same or whole or same is None:
            useA, useB = sA, sB
        else:
            totals = []
            for ref in (pa, pb):
                tot = 0.0
                for j in (jA, jB):
                    for s in j.get("systems", []):
                        if near(system_points(j, s), ref):
                            tot += s.get("total_length_m") or 0.0
                totals.append(tot)
            ref = pa if totals[0] >= totals[1] else pb
            rec["part_totals_m"] = [finite(t, 1) for t in totals]

            def best_in(j):
                cands = [s for s in j.get("systems", []) if s.get("deviation_deg") is not None and near(system_points(j, s), ref)]
                return max(cands, key=lambda s: s.get("total_length_m") or 0.0) if cands else None
            useA, useB = best_in(jA), best_in(jB)
            rec["systems_used"] = [useA.get("id") if useA else None, useB.get("id") if useB else None]
        vals = [(s["deviation_deg"], s.get("se_deg")) for s in (useA, useB) if s]
        m, se = wmean(vals)
        half = abs(vals[0][0] - vals[1][0]) / 2 if len(vals) == 2 else 0.0
        if len(vals) == 2:
            seab = math.hypot(max(vals[0][1] or FLOOR, 1e-3), max(vals[1][1] or FLOOR, 1e-3))
            rec["discordant"] = bool(abs(vals[0][0] - vals[1][0]) > 3 * seab and abs(vals[0][0] - vals[1][0]) > 1.5)
        rec.update(theta_deg=m, sigma_theta_deg=max(se, half, FLOOR), theta_basis="imagery A and B" if len(vals) == 2 else "imagery, one measurer in the chosen part",
                   part=(useA or useB).get("part"))
        return rec
    s, j = (sA, jA) if sA else (sB, jB)
    if s:
        rec.update(theta_deg=s["deviation_deg"], sigma_theta_deg=max(s.get("se_deg") or FLOOR, FLOOR),
                   theta_basis="imagery " + ("A" if sA else "B") + " only", part=s.get("part"))
    return rec


def declination(lat, lon, year):
    try:
        import ppigrf
        from datetime import datetime
        be, bn, bu = ppigrf.igrf(lon, lat, 0.0, datetime(int(year), 7, 1))
        return math.degrees(math.atan2(float(be.squeeze()), float(bn.squeeze())))
    except Exception:
        return None


def plan_values(jpA, jpB, lat, lon):
    vals, true_vals = [], []
    for role, j in (("plan-A", jpA), ("plan-B", jpB)):
        if not j:
            continue
        main = j.get("main_system")
        for s in j.get("systems", []):
            if s.get("deviation_deg") is None:
                continue
            src = source_of(j, s)
            ref = (src.get("north_reference") or "unspecified").lower()
            rec = {"role": role, "system": s.get("id"), "is_main": s.get("id") == main, "part": s.get("part"),
                   "source": src.get("citation_or_service"), "locator": src.get("locator"), "north_reference": ref,
                   "deviation_deg": finite(s["deviation_deg"], 4), "se_deg": finite(s.get("se_deg"), 4), "survey_year": src.get("survey_year")}
            if ref == "magnetic" and src.get("survey_year") and int(src["survey_year"]) >= 1900:
                dec = declination(lat, lon, src["survey_year"])
                rec["igrf_declination_deg"] = finite(dec, 3)
                rec["deviation_true_igrf_deg"] = finite(s["deviation_deg"] + dec, 4) if dec is not None else None
            vals.append(rec)
            if rec["is_main"] and ref in ("true", "grid"):
                se = math.hypot(s.get("se_deg") or FLOOR, 0.5 if ref == "grid" else 0.0)
                true_vals.append((s["deviation_deg"], se))
    out = {"plans": vals}
    if true_vals:
        m, se = wmean(true_vals)
        half = abs(true_vals[0][0] - true_vals[1][0]) / 2 if len(true_vals) == 2 else 0.0
        out.update(theta_plan_true=finite(m, 4), sigma_plan_true=finite(max(se, half, FLOOR), 4))
    return out


def all_systems(role, j, dates_parts, town_date):
    out = []
    for s in (j or {}).get("systems", []):
        if s.get("deviation_deg") is None:
            continue
        rec = {"role": role, "id": s.get("id"), "part": s.get("part"), "deviation_deg": finite(s["deviation_deg"], 4),
               "se_deg": finite(s.get("se_deg"), 4), "total_length_m": finite(s.get("total_length_m"), 1), "n_lines": s.get("n_lines")}
        label = (s.get("part") or "").lower()
        for key in ("citadel", "lower town", "middle town", "castle", "bailey", "fortif"):
            if key in label:
                for p in dates_parts:
                    if key in (p.get("part") or "").lower() and p.get("D_year") is not None:
                        rec["D_year"], rec["sigma_D"], rec["date_part"] = p["D_year"], p.get("sigma_D"), p.get("part")
                        break
            if "D_year" in rec:
                break
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", required=True); ap.add_argument("--horizons", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    roles = {r: load_role(r) for r in ROLES}
    dates = {d["town"]: d for d in json.loads(Path(a.dates).read_text(encoding="utf-8"))["towns"]}
    hz = {t["town"]: t for t in json.loads(Path(a.horizons).read_text(encoding="utf-8"))["towns"]}
    slugs = sorted(set().union(*[set(v) for v in roles.values()]) | set(dates))
    towns, inputs = [], [Path(a.dates), Path(a.horizons)]
    for r in roles.values():
        inputs += [Path(f) for _, f in r.values()]
    for slug in slugs:
        jA, jB = (roles["A"].get(slug) or (None,))[0], (roles["B"].get(slug) or (None,))[0]
        jpA, jpB = (roles["pA"].get(slug) or (None,))[0], (roles["pB"].get(slug) or (None,))[0]
        locs = [j["location"] for j in (jA, jB) if j and j.get("location") and j["location"].get("lat") is not None]
        if not locs:
            locs = [j["location"] for j in (jpA, jpB) if j and j.get("location") and j["location"].get("lat") is not None]
        lat = sum(l["lat"] for l in locs) / len(locs) if locs else None
        lon = sum(l["lon"] for l in locs) / len(locs) if locs else None
        rec = {"town": slug, "role": "discovery" if slug in DISCOVERY else "confirmation", "lat": finite(lat, 5), "lon": finite(lon, 5)}
        img = imagery_value(jA, jB)
        rec.update(img)
        plans = plan_values(jpA, jpB, lat, lon) if lat is not None else {"plans": []}
        rec.update(plans)
        if rec.get("theta_deg") is None and plans.get("theta_plan_true") is not None:
            rec.update(theta_deg=plans["theta_plan_true"], sigma_theta_deg=plans["sigma_plan_true"], theta_basis="plans with true or grid north")
        rec["theta_deg"] = finite(rec.get("theta_deg"), 4)
        rec["sigma_theta_deg"] = finite(rec.get("sigma_theta_deg"), 4)
        d = dates.get(slug, {})
        for k in ("D_year", "sigma_D", "date_tier", "date_part", "date_source", "D_14C_year", "sigma_D_14C", "D_first_occupation_year"):
            rec[k] = d.get(k)
        rec["systems_all"] = all_systems("img-A", jA, d.get("parts", []), d) + all_systems("img-B", jB, d.get("parts", []), d)
        h = hz.get(slug)
        rec["horizon"] = {k: h.get(k) for k in ("observer_elevation_m", "max_altitude_west_deg", "max_altitude_east_deg", "altitude_at_270_deg", "altitude_at_90_deg")} if h else None
        rec["measured_by"] = [r for r, j in (("img-A", jA), ("img-B", jB), ("plan-A", jpA), ("plan-B", jpB)) if j]
        rec["scored"] = rec["theta_deg"] is not None and rec["D_year"] is not None and h is not None
        towns.append(rec)
    out = {"schema_version": "1.0", "task": "town-axes-table", "synthetic": False,
           "rules": "PROTOCOL.md, Data: town deviation and layout date", "towns": towns,
           "provenance": provenance(inputs, [BASE / "combine.py", BASE / "common.py"])}
    digest = write_new(a.out, out)
    cols = ["town", "role", "lat", "lon", "theta_deg", "sigma_theta_deg", "theta_basis", "part", "discordant", "theta_img_A", "se_img_A",
            "theta_img_B", "se_img_B", "theta_plan_true", "sigma_plan_true", "D_year", "sigma_D", "date_tier", "date_part", "D_14C_year",
            "D_first_occupation_year", "scored", "measured_by"]
    csv_path = Path(a.out).with_suffix(".csv")
    if csv_path.exists():
        raise FileExistsError(csv_path)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols + ["horizon_west_max_deg", "horizon_east_max_deg"])
        for t in towns:
            w.writerow([";".join(t[c]) if isinstance(t.get(c), list) else t.get(c) for c in cols]
                       + [(t["horizon"] or {}).get("max_altitude_west_deg"), (t["horizon"] or {}).get("max_altitude_east_deg")])
    print(digest, len(towns), "towns,", sum(t["scored"] for t in towns), "scored")


if __name__ == "__main__":
    main()
