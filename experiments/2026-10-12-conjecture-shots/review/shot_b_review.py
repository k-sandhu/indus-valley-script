"""Exploratory review analysis of Shot B (working reading).

1. Band structure. For P1 (local against pan) and P2 (official against other), counts how
   many eligible signs sit in frequency x position cells that contain both groups; only
   those signs move under the rearrangement null.
2. How much of each per-sign effect is position and frequency. Share of variance of the
   frozen confirmation per-sign effects explained by the twelve band cells.
3. The post-outcome locality pattern (titles and determinatives site-concentrated, names
   spread). The contrast mean(TITLE, DET) - mean(NAME) of per-sign site concentration is
   tested against Shot B's own within-band rearrangement null on the confirmation half and
   on the discovery half, with all sites, with Mohenjo-daro units removed, and with sites
   collapsed to Mohenjo-daro against the rest. The same is done for final-band signs
   against the rest with a frequency-band null, to see whether position alone carries it.
4. Power and replication. Shot B's frozen scoring code is run on the discovery half with its
   real withheld fields (the discovery site and size fields were explored by Shot A, so this
   is a second look, not a fresh test), and with planted size effects of realistic magnitude
   on legends carrying an official sign.
5. The `class` metadata field: its distribution over object types and its relation to the
   field animal, to judge the leakage report.

Outputs: review/shot-b-review.json and review/shot-b-discovery-runs/*.json.
"""
import collections
import importlib.util
import io
import json
import contextlib
import math

import numpy as np

from review_common import HERE, PKG, load_discovery, load_confirmation_direct, load_all, write_json, STATUS

SHOTB = PKG / "shot-b-reading"
spec = importlib.util.spec_from_file_location("shotb_confirm", SHOTB / "confirm.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

GM = json.loads((SHOTB / "GLOSS-MAP.json").read_text(encoding="utf-8"))
RECS = GM["signs"]
CODES = [x["code"] for x in RECS]
CLS = {x["code"]: x["class"] for x in RECS}
CELL = {x["code"]: (x["band"]["frequency"], x["band"]["position"]) for x in RECS}
OFFICIAL = {x["code"]: x["official"] for x in RECS}
LOCAL = {x["code"]: x["locality"] == "local" for x in RECS}
RES = json.loads((SHOTB / "confirmation" / "results.json").read_text(encoding="utf-8"))
rng = np.random.default_rng(8080)


def mixed_cells(eff, group):
    by = collections.defaultdict(lambda: [0, 0])
    for s in eff:
        by[CELL[s]][0 if group(s) else 1] += 1
    mixed = {c: v for c, v in by.items() if v[0] and v[1]}
    return {"eligible_signs": len(eff), "cells": len(by), "mixed_cells": len(mixed),
            "signs_in_mixed_cells": int(sum(sum(v) for v in mixed.values())),
            "group_a_in_mixed_cells": int(sum(v[0] for v in mixed.values())),
            "per_cell": {f"{c[0]}|{c[1]}": {"a": v[0], "b": v[1]} for c, v in sorted(by.items())}}


def band_r2(eff):
    s = list(eff)
    y = np.array([eff[k] for k in s])
    cells = sorted({CELL[k] for k in s})
    X = np.column_stack([[1.0 if CELL[k] == c else 0.0 for k in s] for c in cells])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b
    pos = sorted({CELL[k][1] for k in s})
    Xp = np.column_stack([[1.0 if CELL[k][1] == c else 0.0 for k in s] for c in pos])
    bp, *_ = np.linalg.lstsq(Xp, y, rcond=None)
    rp = y - Xp @ bp
    return {"signs": len(s), "r2_twelve_cells": float(1 - r.var() / y.var()),
            "r2_position_band_only": float(1 - rp.var() / y.var()),
            "mean_by_position_band": {c: float(np.mean([eff[k] for k in s if CELL[k][1] == c])) for c in pos}}


def within_band_contrast(eff, a, b, cell_key=CELL, nperm=10000):
    """mean(eff over signs labelled a) - mean(eff over b); labels (classes) rearranged within cells."""
    s = [k for k in CODES if k in eff]
    e = np.array([eff[k] for k in s])
    lab = np.array([CLS[k] for k in s], dtype=object)
    cells = collections.defaultdict(list)
    for i, k in enumerate(s):
        cells[cell_key[k]].append(i)
    cells = [np.array(v) for v in cells.values()]

    def T(l):
        ma = np.isin(l, list(a))
        mb = np.isin(l, list(b))
        if not ma.any() or not mb.any():
            return np.nan
        return e[ma].mean() - e[mb].mean()

    obs = T(lab)
    null = []
    for _ in range(nperm):
        l = lab.copy()
        for c in cells:
            l[c] = l[c][rng.permutation(len(c))]
        null.append(T(l))
    null = np.array(null)
    null = null[~np.isnan(null)]
    return {"T": float(obs), "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "z": float((obs - null.mean()) / null.std()), "p_one_sided": float((1 + (null >= obs).sum()) / (1 + len(null))),
            "n_a": int(sum(CLS[k] in a for k in s)), "n_b": int(sum(CLS[k] in b for k in s))}


def final_band_contrast(eff, nperm=10000):
    """Final-band signs minus the rest, with position labels rearranged within frequency bands."""
    s = [k for k in CODES if k in eff]
    e = np.array([eff[k] for k in s])
    fin = np.array([CELL[k][1] == "final" for k in s])
    freq = collections.defaultdict(list)
    for i, k in enumerate(s):
        freq[CELL[k][0]].append(i)
    freq = [np.array(v) for v in freq.values()]
    obs = e[fin].mean() - e[~fin].mean()
    null = []
    for _ in range(nperm):
        f = fin.copy()
        for c in freq:
            f[c] = f[c][rng.permutation(len(c))]
        null.append(e[f].mean() - e[~f].mean())
    null = np.array(null)
    return {"T": float(obs), "z": float((obs - null.mean()) / null.std()),
            "p_one_sided": float((1 + (null >= obs).sum()) / (1 + nperm)), "final_signs": int(fin.sum())}


def site_effects(rows, mode):
    fams = B.families(rows)
    seals = [f for f in fams if f["group"] == "SEAL"]
    units = B.categorical_units(seals, "site")
    if mode == "without_md":
        units = [(v, s) for v, s in units if v != "Mohenjo-daro"]
        e, n, d = B.concentration_effect(units, CODES, 10, B.MIN_UNITS)
    elif mode == "md_vs_rest":
        units = [("MD" if v == "Mohenjo-daro" else "rest", s) for v, s in units]
        e, n, d = B.concentration_effect(units, CODES, B.MIN_SITE_UNITS, B.MIN_UNITS)
    else:
        e, n, d = B.concentration_effect(units, CODES, B.MIN_SITE_UNITS, B.MIN_UNITS)
    return e, n, d


def run_shot_b(rows, name, nperm=2000):
    B.N_PERM = nperm
    dest = HERE / "shot-b-discovery-runs" / f"{name}.json"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = B.run(rows, dest, f"review: {name}")
    c = r["components"]
    return {"S": r["primary"]["S"], "distance_sd": r["primary"]["distance_sd"], "percentile": r["primary"]["percentile_of_S"],
            "pass": r["primary"]["pass"], "kill_condition_met": r["verdict"]["kill_condition_met"],
            "z": {k: c[k].get("z") for k in c}, "rearrangements": nperm, "output": str(dest.relative_to(PKG))}


def plant_size(rows, factor):
    """Multiply both face dimensions of seals whose family carries an official sign by sqrt(factor)."""
    fam_signs = collections.defaultdict(set)
    for r in rows:
        fam_signs[r["object_family_id"]].update(r["signs_reading_rtl"])
    off = {f for f, s in fam_signs.items() if any(OFFICIAL.get(x) for x in s)}
    out = []
    k = math.sqrt(factor)
    for r in rows:
        if r["object_family_id"] in off and r["object_type"].startswith("SEAL"):
            md = dict(r["metadata"])
            for key in ("horizontal(mm)", "vertical(mm)"):
                v = B.mm(md.get(key))
                if v:
                    md[key] = f"{v * k:.3f}"
            r = dict(r, metadata=md)
        out.append(r)
    return out, len(off)


def main():
    out = {"status": STATUS}
    eff = RES["per_sign_effects"]
    # 1 and 2
    out["band_structure_confirmation"] = {
        "P1_local_vs_pan": mixed_cells(eff["site"], lambda s: LOCAL[s]),
        "P2_official_vs_other": mixed_cells(eff["size"], lambda s: OFFICIAL[s]),
        "class_by_cell": {f"{c[0]}|{c[1]}": dict(collections.Counter(CLS[k] for k in CODES if CELL[k] == c))
                          for c in sorted(set(CELL.values()))},
    }
    out["band_r2_confirmation"] = {k: band_r2(eff[k]) for k in ("site", "size", "unicorn", "harappa")}

    # 3. locality pattern
    conf = load_confirmation_direct()
    disc = load_discovery()
    loc = {}
    for half, rows in (("confirmation", conf), ("discovery", disc)):
        for mode in ("all_sites", "without_md", "md_vs_rest"):
            e, n, d = site_effects(rows, mode)
            loc[f"{half}|{mode}"] = {
                "units": d["units"], "categories": d["categories"],
                "title_det_minus_name": within_band_contrast(e, {"TITLE", "DET"}, {"NAME"}),
                "local_minus_pan_P1": within_band_contrast(e, {"NAME", "COMM"}, {"NUM", "LINK", "AFF", "TITLE", "DET"}),
                "final_band_minus_rest": final_band_contrast(e),
                "class_means": {c: round(float(np.mean([v for k, v in e.items() if CLS[k] == c])), 4)
                                for c in sorted(set(CLS[k] for k in e))},
                "corr_effect_with_log_units": float(np.corrcoef([e[k] for k in e], [math.log(n[k]) for k in e])[0, 1]),
            }
    out["locality_pattern"] = loc
    # does the confirmation pattern hold up on discovery sign by sign?
    ec, _, _ = site_effects(conf, "all_sites")
    ed, _, _ = site_effects(disc, "all_sites")
    common = [k for k in ec if k in ed]
    out["site_effect_correlation_between_halves"] = {
        "signs": len(common), "pearson": float(np.corrcoef([ec[k] for k in common], [ed[k] for k in common])[0, 1])}

    # 4. Shot B's frozen code on the discovery half, real and planted
    runs = {"discovery_real_fields": run_shot_b(disc, "discovery-real")}
    for f in (1.2, 1.5):
        rows_p, nfam = plant_size(disc, f)
        runs[f"discovery_planted_area_x{f}_official_legends"] = dict(run_shot_b(rows_p, f"discovery-planted-area-x{f}"),
                                                                     families_with_official_sign=nfam)
    out["shot_b_code_on_discovery"] = runs
    syn = json.loads((SHOTB / "discovery" / "synthetic_dryrun_planted.json").read_text(encoding="utf-8"))
    out["shot_b_planted_dry_run_reference"] = {
        "note": "Shot B's own planted run: each name-bearing family's site drawn with +0.6 probability on one of three sites; official legends 1.25x linear size (1.56x area)",
        "z": {k: v.get("z") for k, v in syn["components"].items()}, "S_distance_sd": syn["primary"]["distance_sd"]}

    # 5. the class field
    allrows = load_all()
    seal_rows = [r for r in allrows if r["object_type"].startswith("SEAL")]
    by_type = collections.defaultdict(collections.Counter)
    for r in allrows:
        by_type[r["metadata"].get("class")][r["object_type"].split(":")[0]] += 1
    uni = lambda r: (r.get("symbol") or "").startswith("Bull1")
    cls_uni = collections.defaultdict(lambda: [0, 0])
    for r in seal_rows:
        cls_uni[r["metadata"].get("class")][0] += 1
        cls_uni[r["metadata"].get("class")][1] += uni(r)
    out["class_field"] = {
        "UC_faces_by_object_type": dict(by_type["UC"].most_common()),
        "seal_faces_unicorn_share_overall": round(sum(uni(r) for r in seal_rows) / len(seal_rows), 3),
        "seal_faces_unicorn_share_by_class": {k: {"seal_faces": v[0], "unicorn_share": round(v[1] / v[0], 3)}
                                               for k, v in sorted(cls_uni.items(), key=lambda kv: -kv[1][0])[:12]},
        "two_and_three_line_codes": {k: sum(by_type[k].values()) for k in ("2L", "3L")},
    }
    write_json("shot-b-review.json", out)
    print(json.dumps({k: out[k] for k in ("band_structure_confirmation",)}, indent=0)[:1500])
    print(json.dumps(out["band_r2_confirmation"], indent=0))
    for k, v in loc.items():
        print(k, "TD-N", {x: round(y, 4) if isinstance(y, float) else y for x, y in v["title_det_minus_name"].items()},
              "final", v["final_band_minus_rest"], "P1", round(v["local_minus_pan_P1"]["z"], 2))
        print("   ", v["class_means"], "corr logn", round(v["corr_effect_with_log_units"], 3))
    print(out["site_effect_correlation_between_halves"])
    print(json.dumps(runs, indent=0))
    print(json.dumps(out["class_field"], indent=0))


if __name__ == "__main__":
    main()
