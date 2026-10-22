"""Coordinator's registration run (PROTOCOL.md, sections 4 to 7).

Runs once, after CONTROL-FREEZE.json records the hashes of every control
point file. For each plan and registrar it fits the chain of links from the
plan to the map, applies the acceptance rules, combines the registrars,
turns the fitted rotation into the true bearing of the plan's north arrow,
converts the plan-B systems of that plan to true north, applies the town
rule and the validation rule, and writes one versioned JSON file.
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regfit  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
TA = ROOT / "experiments" / "2026-10-21-town-axes"
SIGMA_FLOOR_DEG = 0.3
DISCORDANCE_SIGMAS = 3.0
DISCORDANCE_MIN_DEG = 2.0
VALIDATION_Z = 2.0
# Imagery parts against which the validation towns are compared (PROTOCOL.md section 6).
VALIDATION = {"dholavira": "castle", "lothal": "dock"}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def relp(p):
    return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")


def convert_system(theta_sys, se_sys, arrow_sigma, alpha, sigma_phi):
    """True-north deviation of a plan system and its error (PROTOCOL.md section 5)."""
    theta = regfit.fold45(theta_sys + alpha)
    rest = max(se_sys ** 2 - arrow_sigma ** 2, 0.0)
    sigma = max(math.sqrt(rest + sigma_phi ** 2), SIGMA_FLOOR_DEG)
    return theta, sigma


def load_registrar(reg_dir):
    files = {}
    for f in sorted(glob.glob(str(Path(reg_dir) / "*.json"))):
        cf = json.loads(Path(f).read_text(encoding="utf-8"))
        files[cf["plan"]] = (f, cf)
    return files


def plans_with_aux(cf_all):
    plans = {p["id"]: p for p in json.loads((PKG / "plans-v1.json").read_text(encoding="utf-8"))["plans"]}
    for _, cf in cf_all.values():
        for p in cf.get("aux_plans", []):
            q = dict(p)
            sb = p.get("scale_bar")
            if sb:
                (x1, y1), (x2, y2) = sb["p1_px"], sb["p2_px"]
                q["scale_bar_m_per_px"] = sb["length_m"] / math.hypot(x2 - x1, y2 - y1)
            plans[p["id"]] = q
    return plans


def find_link(files, pid):
    """The link whose plan is pid, searched first in pid's own file, then in the registrar's other files."""
    order = ([files[pid]] if pid in files else []) + [v for k, v in files.items() if k != pid]
    for f, cf in order:
        for link in cf["links"]:
            if link["plan"] == pid:
                return f, cf, link
    return None, None, None


def chain(files, pid, plans, subset=None):
    """Fit the links from plan pid to the map. Returns a dict with the total rotation and error."""
    steps = []
    seen = set()
    cur = pid
    while True:
        if cur in seen:
            return {"accepted": False, "reasons": [f"link cycle at {cur}"], "steps": steps}
        seen.add(cur)
        f, cf, link = find_link(files, cur)
        if link is None:
            return {"accepted": False, "reasons": [f"no link from {cur}"], "steps": steps}
        mosaics = {}
        for p in link["points"]:
            if "mosaic" in p and p["mosaic"] not in mosaics:
                mosaics[p["mosaic"]] = json.loads((ROOT / p["mosaic"]).read_text())
        sub = subset if link["to"] == "map" else None
        r = regfit.fit_from_link(link, plans, mosaics, reveal_rotation=True, subset=sub)
        r.update(plan=cur, to=link["to"], file=relp(f), variant="without exposed masonry" if sub else "all points")
        steps.append(r)
        if not r.get("accepted"):
            return {"accepted": False, "reasons": [f"{cur} -> {link['to']}: " + "; ".join(r.get("reasons", []))],
                    "steps": steps}
        if link["to"] == "map":
            break
        cur = link["to"]
    phi = sum(s["phi_deg"] for s in steps)
    sig = math.sqrt(sum(s["sigma_phi_deg"] ** 2 for s in steps))
    return {"accepted": True, "phi_deg": regfit.wrap180(phi), "sigma_phi_deg": sig,
            "informative": sig <= regfit.MAX_SIGMA_PHI_DEG, "steps": steps}


def combine(values):
    """Combine registrars' rotations for one plan (PROTOCOL.md section 4)."""
    ok = [v for v in values if v.get("accepted") and v.get("informative")]
    if not ok:
        return None
    if len(ok) == 1:
        return {"phi_deg": ok[0]["phi_deg"], "sigma_phi_deg": ok[0]["sigma_phi_deg"], "n_registrars": 1,
                "discordant": False}
    ref = ok[0]["phi_deg"]
    w = [1 / v["sigma_phi_deg"] ** 2 for v in ok]
    d = [regfit.wrap180(v["phi_deg"] - ref) for v in ok]
    mean = ref + sum(wi * di for wi, di in zip(w, d)) / sum(w)
    sig_ivw = math.sqrt(1 / sum(w))
    half_range = (max(d) - min(d)) / 2
    sig = max(sig_ivw, half_range)
    disc = False
    if len(ok) == 2:
        diff = abs(d[1] - d[0])
        comb = math.hypot(ok[0]["sigma_phi_deg"], ok[1]["sigma_phi_deg"])
        disc = diff > DISCORDANCE_SIGMAS * comb and diff > DISCORDANCE_MIN_DEG
    return {"phi_deg": regfit.wrap180(mean), "sigma_phi_deg": sig, "n_registrars": len(ok), "discordant": disc,
            "registrar_difference_deg": d[1] - d[0] if len(ok) == 2 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registrars", nargs="+", required=True, help="control-point directories, one per registrar")
    ap.add_argument("--extra-towns", help="directory of plan-B-format town files measured in this package")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() or (out.parent / "towns.csv").exists():
        raise SystemExit(f"{out} or its towns.csv exists; write to a new path")

    regs = {}
    for d in a.registrars:
        files = load_registrar(d)
        name = Path(d).name
        regs[name] = files
    all_files = {}
    for name, files in regs.items():
        for k, v in files.items():
            all_files[f"{name}:{k}"] = v
    plans = plans_with_aux(all_files)
    base_plans = json.loads((PKG / "plans-v1.json").read_text(encoding="utf-8"))["plans"]
    town_dirs = {}
    if a.extra_towns:
        for f in sorted(Path(a.extra_towns).glob("*.json")):
            tf = json.loads(f.read_text(encoding="utf-8"))
            town_dirs[tf["town"]] = f
            for s in tf["sources"]:
                if not s.get("render"):
                    continue
                sb = s.get("scale_bar_measurement") or {}
                bp = {"id": f"{tf['town']}:{s['id']}", "town": tf["town"], "source_id": s["id"], "role": "target",
                      "render": s["render"], "scale_bar_m_per_px": sb.get("m_per_px")}
                base_plans.append(bp)
                plans.setdefault(bp["id"], bp)

    def town_file(town):
        return town_dirs.get(town, TA / "measure-plan-B" / "towns" / f"{town}.json")

    no_masonry = lambda p: not p.get("exposed_masonry")  # noqa: E731
    per_plan = {}
    for bp in base_plans:
        pid = bp["id"]
        rec = {"plan": pid, "town": bp["town"], "role": bp["role"], "registrars": {}}
        for name, files in regs.items():
            has_file = pid in files
            has_link = find_link(files, pid)[2] is not None
            if not (has_file or has_link):
                continue
            none = {"accepted": False, "reasons": ["no link from this plan"]}
            entry = {"status_declared": files[pid][1].get("status") if has_file else None,
                     "reason_declared": files[pid][1].get("reason") if has_file else None,
                     "all_points": chain(files, pid, plans) if has_link else none}
            if bp["role"] == "validation":
                entry["without_exposed_masonry"] = chain(files, pid, plans, subset=no_masonry) if has_link else none
            rec["registrars"][name] = entry
        rec["combined_all_points"] = combine([e["all_points"] for e in rec["registrars"].values()])
        if bp["role"] == "validation":
            rec["combined_without_exposed_masonry"] = combine(
                [e["without_exposed_masonry"] for e in rec["registrars"].values()])
        per_plan[pid] = rec

    # Arrow true bearings and system conversion.
    towns = {}
    for bp in base_plans:
        towns.setdefault(bp["town"], []).append(bp)
    systems_out = []
    town_values = {}
    for town, bps in towns.items():
        tf = json.loads(town_file(town).read_text(encoding="utf-8"))
        srcs = {s["id"]: s for s in tf["sources"]}
        main_sys = next((s for s in tf.get("systems", []) if s["id"] == tf.get("main_system")), None)
        conv = []
        for bp in bps:
            rp = per_plan[bp["id"]]
            variants = [("all points", rp["combined_all_points"])]
            if bp["role"] == "validation":
                variants.append(("without exposed masonry", rp["combined_without_exposed_masonry"]))
            src = srcs[bp["source_id"]]
            am = src.get("north_arrow_measurement") or {}
            if "page_azimuth_deg" not in am:
                continue
            arrow_sigma = math.hypot(am.get("pick_sigma_deg", 0.0), am.get("drafting_sigma_deg", 0.0))
            for vname, comb in variants:
                if comb is None:
                    continue
                alpha = regfit.wrap180(am["page_azimuth_deg"] - comb["phi_deg"])
                rp.setdefault("arrow_true_bearing", {})[vname] = {
                    "alpha_deg": alpha, "sigma_deg": comb["sigma_phi_deg"],
                    "arrow_page_azimuth_deg": am["page_azimuth_deg"], "north_reference_label": src.get("north_reference")}
                for s in tf.get("systems", []):
                    if s["source"] != bp["source_id"]:
                        continue
                    th, sg = convert_system(s["deviation_deg"], s["se_deg"], arrow_sigma, alpha, comb["sigma_phi_deg"])
                    row = {"town": town, "plan": bp["id"], "variant": vname, "system": s["id"], "part": s.get("part"),
                           "description": s.get("description"), "n_lines": s.get("n_lines"),
                           "total_length_m": s.get("total_length_m"), "theta_plan_deg": s["deviation_deg"],
                           "se_plan_deg": s["se_deg"], "arrow_sigma_deg": arrow_sigma, "alpha_deg": alpha,
                           "sigma_phi_deg": comb["sigma_phi_deg"], "theta_true_deg": th, "sigma_true_deg": sg,
                           "is_main_system": main_sys is not None and s["id"] == main_sys["id"]
                           and s["source"] == main_sys["source"]}
                    systems_out.append(row)
                    conv.append(row)
        # Town rule (PROTOCOL.md section 5).
        variant = "without exposed masonry" if bps[0]["role"] == "validation" else "all points"
        cands = [r for r in conv if r["variant"] == variant]
        if bps[0]["role"] == "validation" and not any(r["is_main_system"] for r in cands):
            variant = "all points"
            cands = [r for r in conv if r["variant"] == variant]
        chosen = next((r for r in cands if r["is_main_system"]), None)
        rule = "main system on its own plan"
        if chosen is None and main_sys is not None:
            same = [r for r in cands if r["part"] == main_sys.get("part")]
            if same:
                chosen = max(same, key=lambda r: r["total_length_m"] or 0)
                rule = "longest registered system of the main system's part on another plan"
        town_values[town] = {"town": town, "role": bps[0]["role"], "variant": variant if chosen else None,
                             "rule": rule if chosen else "not registered",
                             "theta_true_deg": chosen["theta_true_deg"] if chosen else None,
                             "sigma_true_deg": chosen["sigma_true_deg"] if chosen else None,
                             "plan": chosen["plan"] if chosen else None, "system": chosen["system"] if chosen else None,
                             "part": chosen["part"] if chosen else None,
                             "main_system_plan_B": {"id": main_sys["id"], "source": main_sys["source"],
                                                    "part": main_sys.get("part")} if main_sys else None}

    # Validation (PROTOCOL.md section 6).
    table = json.loads((TA / "table-v1" / "settlement-axes.json").read_text(encoding="utf-8"))
    trow = {r["town"]: r for r in table["towns"]}
    validation = {}
    for town, part in VALIDATION.items():
        tv = town_values.get(town)
        img = trow[town]
        v = {"imagery_theta_deg": img["theta_deg"], "imagery_sigma_deg": img["sigma_theta_deg"], "imagery_part": part}
        if tv and tv["theta_true_deg"] is not None:
            diff = regfit.wrap180(tv["theta_true_deg"] - img["theta_deg"])
            comb = math.hypot(tv["sigma_true_deg"], img["sigma_theta_deg"])
            v.update(registered_theta_deg=tv["theta_true_deg"], registered_sigma_deg=tv["sigma_true_deg"],
                     registered_part=tv["part"], variant=tv["variant"], difference_deg=diff, z=diff / comb,
                     passes=abs(diff / comb) <= VALIDATION_Z)
        else:
            v.update(passes=None, note="no registered value")
        validation[town] = v
    vals = [v["passes"] for v in validation.values()]
    validation_pass = all(x is True for x in vals) if all(x is not None for x in vals) else None

    # Secondary check: arrows labelled true or magnetic against their expected bearing.
    arrow_checks = []
    for bp in base_plans:
        rp = per_plan[bp["id"]]
        tr = trow.get(bp["town"], {})
        tf = json.loads(town_file(bp["town"]).read_text(encoding="utf-8"))
        src = next(s for s in tf["sources"] if s["id"] == bp["source_id"])
        am = src.get("north_arrow_measurement") or {}
        arrow_sigma = math.hypot(am.get("pick_sigma_deg", 0.0), am.get("drafting_sigma_deg", 0.0))
        ref = src.get("north_reference")
        expected = None
        if ref == "true":
            expected = 0.0
        elif ref == "magnetic":
            decs = [p.get("igrf_declination_deg") for p in tr.get("plans", []) if p.get("source") == bp["source_id"]]
            decs = [d for d in decs if d is not None]
            expected = decs[0] if decs else None
        for vname, ab in rp.get("arrow_true_bearing", {}).items():
            if expected is None:
                continue
            diff = regfit.wrap180(ab["alpha_deg"] - expected)
            comb = math.hypot(ab["sigma_deg"], arrow_sigma)
            arrow_checks.append({"plan": bp["id"], "variant": vname, "north_reference": ref, "expected_deg": expected,
                                 "alpha_deg": ab["alpha_deg"], "difference_deg": diff, "sigma_deg": comb,
                                 "z": diff / comb})

    # Dated towns with a true-north value.
    expl = json.loads((TA / "exploratory-v1" / "table.json").read_text(encoding="utf-8"))
    dated = {r["town"]: r.get("D_year") for r in expl["towns"]}
    imagery_towns = [r["town"] for r in table["towns"] if r.get("theta_deg") is not None]
    true_north = sorted(set(imagery_towns) | {t for t, v in town_values.items()
                                              if v["theta_true_deg"] is not None and v["role"] != "validation"})
    true_north_dated = [t for t in true_north if dated.get(t) is not None]

    inputs = {relp(PKG / "plans-v1.json"): sha256(PKG / "plans-v1.json"),
              relp(TA / "table-v1" / "settlement-axes.json"): sha256(TA / "table-v1" / "settlement-axes.json"),
              relp(TA / "exploratory-v1" / "table.json"): sha256(TA / "exploratory-v1" / "table.json")}
    for town in towns:
        p = town_file(town)
        inputs[relp(p)] = sha256(p)
    for f, _ in all_files.values():
        inputs[relp(f)] = sha256(f)
    code = {relp(Path(__file__)): sha256(__file__), relp(PKG / "code" / "regfit.py"): sha256(PKG / "code" / "regfit.py")}
    res = {
        "schema_version": "1.0",
        "task": "plan-registration",
        "synthetic": False,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "plans": per_plan,
        "systems": systems_out,
        "towns": town_values,
        "validation": validation,
        "validation_passes": validation_pass,
        "arrow_checks": arrow_checks,
        "true_north_towns": true_north,
        "true_north_dated_towns": true_north_dated,
        "n_true_north_dated": len(true_north_dated),
        "provenance": {"inputs": inputs, "code": code, "protocol_sha256": sha256(PKG / "PROTOCOL.md")},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    with open(out.parent / "towns.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["town", "role", "plan", "system", "part", "variant", "theta_true_deg", "sigma_true_deg", "rule"])
        for t, v in town_values.items():
            w.writerow([t, v["role"], v["plan"], v["system"], v["part"], v["variant"],
                        None if v["theta_true_deg"] is None else round(v["theta_true_deg"], 2),
                        None if v["sigma_true_deg"] is None else round(v["sigma_true_deg"], 2), v["rule"]])
    print("wrote", out)


if __name__ == "__main__":
    main()
