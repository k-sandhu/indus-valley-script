"""Exploratory review analysis: what the export can say about Shot A's rivals.

1. Reading direction. If a high-set legend were catalogued in the wrong direction, its
   first sign would tend to be a sign that usually closes texts. For every seal in the
   frozen size population of both halves, the first sign's opening share (initial count
   over initial + final count, one face per family over all complete single-line seal
   texts of two or more signs in the full export) is compared between high-set seals and
   the rest.
2. Layout. If the final high-set sign were an extra sign placed on a large face, the legend
   without it would look like a complete legend: its own last sign (the penultimate sign)
   would usually be a closing sign, and the shortened legend might occur as a complete
   text elsewhere. Both are compared with other seals of the population.
3. Workshop, excavation area and period. P4 is recomputed with the Mohenjo-daro excavation
   area (first three characters of area-section), the `time` and `period` fields, the
   field animal and the unicorn variant added to the base model, on each half and pooled.

Outputs: review/shot-a-rivals.json (aggregates) and data/raw/.../review/high-set-layout.json
(legends and their shortened forms; local).
"""
import collections
import math

import numpy as np

from review_common import L, load_all, write_json, write_raw, STATUS
from shot_a_robustness import build, frozen_population, p4, design_factor, TYPE, SITE, LENC, HIGH

rng = np.random.default_rng(4242)


def position_counts(rows):
    """Initial and final counts per sign, one face per family, complete single-line seal texts."""
    best = {}
    for r in rows:
        if not r["object_type"].startswith("SEAL"):
            continue
        if not (r["complete_observed"] and not r["has_unknown_sign"] and r["single_line"] and r["length"] >= 2):
            continue
        f = r["object_family_id"]
        if f not in best or r["length"] > best[f]["length"]:
            best[f] = r
    ini, fin = collections.Counter(), collections.Counter()
    for r in best.values():
        s = r["signs_reading_rtl"]
        ini[s[0]] += 1
        fin[s[-1]] += 1
    return ini, fin


def all_complete_texts(rows):
    t = collections.Counter()
    for r in rows:
        if r["complete_observed"] and not r["has_unknown_sign"]:
            t["-".join(r["signs_reading_rtl"])] += 1
    return t


def opening_share(sign, ini, fin):
    a, b = ini[sign], fin[sign]
    return (a + 0.5) / (a + b + 1.0)


def summarise(vals):
    vals = np.array(vals, dtype=float)
    return {"n": int(len(vals)), "mean": float(vals.mean()) if len(vals) else None,
            "median": float(np.median(vals)) if len(vals) else None}


def perm_mean_diff(a, b, nperm=9999, greater=True):
    a, b = np.array(a, float), np.array(b, float)
    allv = np.concatenate([a, b])
    obs = a.mean() - b.mean()
    cnt = 0
    for _ in range(nperm):
        p = rng.permutation(len(allv))
        d = allv[p[:len(a)]].mean() - allv[p[len(a):]].mean()
        cnt += (d >= obs) if greater else (d <= obs)
    return {"difference": float(obs), "p_one_sided": float((1 + cnt) / (1 + nperm)),
            "direction_tested": "high > rest" if greater else "high < rest"}


def main():
    rows = load_all()
    ini, fin = position_counts(rows)
    texts = all_complete_texts(rows)
    tab = build(rows)
    out = {"status": STATUS}
    out["sign_position_counts_full_export"] = {s: {"initial": ini[s], "final": fin[s]} for s in sorted(HIGH)}

    pops = {}
    for h in ("discovery", "confirmation"):
        pops[h] = frozen_population([t for t in tab if t["half"] == h])
    pooled = pops["discovery"] + pops["confirmation"]

    # 1. direction
    hi = [t for t in pooled if t["last"] in HIGH]
    rest = [t for t in pooled if t["last"] not in HIGH]
    out["direction"] = {
        "first_sign_opening_share_high": summarise([opening_share(t["first"], ini, fin) for t in hi]),
        "first_sign_opening_share_rest": summarise([opening_share(t["first"], ini, fin) for t in rest]),
        "test_high_first_signs_less_opening": perm_mean_diff([opening_share(t["first"], ini, fin) for t in hi],
                                                             [opening_share(t["first"], ini, fin) for t in rest], greater=False),
        "high_seals_first_sign_opening_share_below_0.5": int(sum(opening_share(t["first"], ini, fin) < 0.5 for t in hi)),
        "rest_first_sign_opening_share_below_0.5_share": float(np.mean([opening_share(t["first"], ini, fin) < 0.5 for t in rest])),
        "direction_field_high": dict(collections.Counter(t["direction"] for t in hi)),
        "direction_field_rest": dict(collections.Counter(t["direction"] for t in rest).most_common(6)),
        "per_seal": [{"cisi": t["cisi"], "half": t["half"], "last": t["last"], "first_sign_opening_share":
                      round(opening_share(t["first"], ini, fin), 3)} for t in hi],
    }

    # 2. layout
    def closing_share(sign):
        a, b = ini[sign], fin[sign]
        return (b + 0.5) / (a + b + 1.0)

    def shortened(t):
        return "-".join(t["signs"][:-1])

    layout_rows = []
    for t in hi:
        layout_rows.append({"cisi": t["cisi"], "half": t["half"], "legend": t["signs"], "shortened": shortened(t),
                            "shortened_occurs_as_complete_text": texts.get(shortened(t), 0),
                            "penultimate": t["signs"][-2], "penultimate_closing_share": round(closing_share(t["signs"][-2]), 3)})
    rest_pen = [closing_share(t["signs"][-2]) for t in rest]
    out["layout"] = {
        "penultimate_closing_share_high": summarise([r["penultimate_closing_share"] for r in layout_rows]),
        "penultimate_closing_share_rest": summarise(rest_pen),
        "test_high_penultimate_more_closing": perm_mean_diff([r["penultimate_closing_share"] for r in layout_rows], rest_pen),
        "high_with_penultimate_740": int(sum(t["signs"][-2] == "740" for t in hi)),
        "rest_with_penultimate_740_share": float(np.mean([t["signs"][-2] == "740" for t in rest])),
        "high_shortened_legend_found_as_complete_text_anywhere": int(sum(r["shortened_occurs_as_complete_text"] > 0 for r in layout_rows)),
        "rest_shortened_legend_found_as_complete_text_share": float(np.mean([texts.get(shortened(t), 0) > 0 for t in rest])),
        "per_seal": [{k: r[k] for k in ("cisi", "half", "penultimate", "penultimate_closing_share",
                                        "shortened_occurs_as_complete_text")} for r in layout_rows],
        "note": "high-set seals whose own last sign is in HIGH and whose penultimate sign is also in HIGH are counted as they stand",
    }
    write_raw("high-set-layout.json", {"status": STATUS, "seals": layout_rows})

    # 3. covariates for workshop, area and period
    def area(t):
        a = (t["area_section"] or "").strip()
        if t["site"] != "Mohenjo-daro":
            return "notMD"
        for p in ("DK", "HR", "VS", "SD"):
            if a.startswith(p):
                return p
        return "MDother"

    def time_(t):
        v = (t.get("period") or "-").strip()
        w = (t.get("time") or "-").strip()
        if v not in ("-", ""):
            return "period:" + v
        if w not in ("-", ""):
            return "time:" + w
        return "none"

    def animal(t):
        return t["animal"] if t["animal"] in ("Bull1", "None", "Gaur", "Zebu", "Elep", "Rhin", "Bull") else "otherimg"

    def variant(t):
        return "W" if t["symbol_full"] == "Bull1:W" else "notW"

    res = {}
    for name, pop in (("discovery", pops["discovery"]), ("confirmation", pops["confirmation"]), ("pooled", pooled)):
        r = {"frozen": p4(pop)}
        r["plus_md_area"] = p4(pop, X=design_factor(pop, [TYPE, SITE, LENC, area]))
        r["plus_md_area_strata_include_area"] = p4(pop, X=design_factor(pop, [TYPE, SITE, LENC, area]),
                                                   strata=[(t["type"], L.site6(t["site"]), L.len_class(t["length"]), area(t)) for t in pop])
        r["plus_period_field"] = p4(pop, X=design_factor(pop, [TYPE, SITE, LENC, time_]))
        r["plus_animal_and_unicorn_variant"] = p4(pop, X=design_factor(pop, [TYPE, SITE, LENC, animal, variant]))
        r["plus_all_covariates"] = p4(pop, X=design_factor(pop, [TYPE, SITE, LENC, area, time_, animal, variant]))
        md = [t for t in pop if t["site"] == "Mohenjo-daro"]
        r["md_only_plus_area"] = p4(md, X=design_factor(md, [TYPE, LENC, area]),
                                    strata=[(t["type"], L.len_class(t["length"])) for t in md])
        r["high_set_area_counts_md"] = dict(collections.Counter(area(t) for t in md if t["last"] in HIGH))
        r["population_area_counts_md"] = dict(collections.Counter(area(t) for t in md))
        res[name] = r
    out["covariates"] = res

    # 4. does a large face carry extra closers generally? last-sign rarity against residual
    fin_all = fin
    def rare_closer(t):
        return fin_all[t["last"]] < 25
    for name, pop in (("discovery", pops["discovery"]), ("confirmation", pops["confirmation"])):
        rr = pop
        y = np.array([t["log_area"] for t in rr])
        X = L.base_design(rr)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        e = y - X @ b
        q = np.quantile(e, [0.5, 0.9])
        out.setdefault("rare_closer_by_residual", {})[name] = {
            "share_last_sign_rare_closer_top_decile": float(np.mean([rare_closer(t) for t, x in zip(rr, e) if x >= q[1]])),
            "share_last_sign_rare_closer_bottom_half": float(np.mean([rare_closer(t) for t, x in zip(rr, e) if x < q[0]])),
            "definition": "rare closer: sign closes fewer than 25 complete single-line seal legends in the full export",
            "rare_closer_without_high_set": p4(rr, high={t["last"] for t in rr if rare_closer(t)} - HIGH),
        }
    write_json("shot-a-rivals.json", out)
    print({k: out["direction"][k] for k in ("first_sign_opening_share_high", "first_sign_opening_share_rest",
                                            "test_high_first_signs_less_opening", "high_seals_first_sign_opening_share_below_0.5",
                                            "rest_first_sign_opening_share_below_0.5_share", "direction_field_high")})
    print({k: v for k, v in out["layout"].items() if k != "per_seal"})
    for n, r in res.items():
        print(n, {k: (v.get("n_high"), round(v["difference"], 3), v["p_one_sided"]) for k, v in r.items() if isinstance(v, dict) and "difference" in v})
        print("  areas", r["high_set_area_counts_md"], r["population_area_counts_md"])
    print(out["rare_closer_by_residual"])


if __name__ == "__main__":
    main()
