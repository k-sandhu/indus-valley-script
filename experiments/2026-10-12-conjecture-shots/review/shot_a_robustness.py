"""Exploratory review analysis: fragility of Shot A's P4 and P1a.

Recomputes P4 (seals whose last sign is 001, 595, 679 or 820 against the rest, residual
log face area, last signs permuted within type x site class x length class) on the
confirmation half under the variations listed below, and does the same on the discovery
half and the pooled halves for comparison. Also lists the metadata of every high-set seal
in both halves and probes whether P1a's between-sign ratio is specific to the last sign.

Nothing here changes Shot A's frozen verdicts. Outputs:
  review/shot-a-robustness.json            aggregate statistics and seal metadata
  data/raw/.../review/high-set-legends.json full legends of the high-set seals (local)
"""
import collections
import math

import numpy as np

from review_common import L, seal_table, load_discovery, load_confirmation_direct, write_json, write_raw, STATUS

HIGH = {"001", "595", "679", "820"}
NPERM = 4999
rng = np.random.default_rng(20261013 + 7)


def build(rows):
    by_rec = {r["record_id"]: r for r in rows}
    tab = seal_table(rows)
    for t in tab:
        r = by_rec[t["record_id"]]
        m = r["metadata"]
        t.update({"raw_h": m.get("h", ""), "raw_v": m.get("v", ""), "condition": m.get("condition"),
                  "area_section": m.get("area-section"), "direction": r.get("direction"), "dir_meta": m.get("dir."),
                  "text_class": m.get("class"), "cross_section": m.get("cross-section"),
                  "has_blank_space": r.get("has_blank_space"), "half": r["half"]})
    return tab


def frozen_population(tab):
    return L.representative(L.size_text_population(tab))


# ---------------------------------------------------------------- designs

def design_factor(rows, keys):
    cols = [np.ones(len(rows))]
    for k in keys:
        cols.append(L.onehot([k(t) for t in rows]))
    return np.column_stack(cols)


TYPE = lambda t: t["type"]
SITE = lambda t: L.site6(t["site"])
LENC = lambda t: L.len_class(t["length"])
LENX = lambda t: t["length"]


def residuals(rows, y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ b


def p4(rows, y=None, X=None, strata=None, high=HIGH, stat_transform=None, nperm=NPERM):
    if y is None:
        y = np.array([t["log_area"] for t in rows])
    if X is None:
        X = L.base_design(rows)
    if strata is None:
        strata = L.strata_of(rows)
    res = residuals(rows, y, X)
    if stat_transform == "rank":
        res = (np.argsort(np.argsort(res)) + 0.5) / len(res) - 0.5
    lab = ["H" if t["last"] in high else "O" for t in rows]
    out = L.contrast_test(lab, res, strata, {"H"}, {"O"}, nperm, rng)
    sp = L.StratPerm(strata)
    movable = set(i for g in sp.groups for i in g)
    out["high_seals_immovable"] = int(sum(1 for i, l in enumerate(lab) if l == "H" and i not in movable))
    out["population"] = len(rows)
    return {k: out[k] for k in ("population", "n_high", "mean_high", "mean_low", "difference", "null_mean",
                                "null_sd", "p_one_sided", "high_seals_immovable") if k in out}


def variants(pop):
    """All variations of P4 on one population (one seal per component unless stated)."""
    out = collections.OrderedDict()
    out["frozen_rules"] = p4(pop)

    # leave one high seal out (seal removed, model refitted)
    hi = [t for t in pop if t["last"] in HIGH]
    loo = []
    for h in hi:
        sub = [t for t in pop if t is not h]
        r = p4(sub)
        loo.append({"dropped": h["cisi"], "last": h["last"], "difference": r["difference"], "p_one_sided": r["p_one_sided"]})
    out["leave_one_seal_out"] = loo
    # drop the k largest-residual high seals
    res0 = residuals(pop, np.array([t["log_area"] for t in pop]), L.base_design(pop))
    order = sorted([i for i, t in enumerate(pop) if t["last"] in HIGH], key=lambda i: -res0[i])
    for k in (1, 2, 3):
        drop = set(order[:k])
        sub = [t for i, t in enumerate(pop) if i not in drop]
        r = p4(sub)
        out[f"drop_top_{k}_high_residual"] = dict(r, dropped=[pop[i]["cisi"] for i in order[:k]])
    # leave one sign out
    for s in sorted(HIGH):
        r_keep = p4(pop, high=HIGH - {s})
        r_drop = p4([t for t in pop if t["last"] != s], high=HIGH - {s})
        out[f"without_sign_{s}_seals_kept_as_other"] = r_keep
        out[f"without_sign_{s}_seals_removed"] = r_drop
    for s in sorted(HIGH):
        out[f"only_sign_{s}"] = p4(pop, high={s})

    # preservation
    out["complete_only"] = p4([t for t in pop if t["preservation"] in ("complete", "complsete")])
    out["exclude_chipped_keep_slightly"] = p4([t for t in pop if t["preservation"] != "chipped"])

    # size measures
    out["size_ln_longer_side"] = p4(pop, y=np.array([math.log(max(t["h"], t["v"])) for t in pop]))
    out["size_ln_shorter_side"] = p4(pop, y=np.array([math.log(min(t["h"], t["v"])) for t in pop]))
    out["size_area_mm2_untransformed"] = p4(pop, y=np.array([t["h"] * t["v"] for t in pop]))
    out["size_ln_area_rank_of_residual"] = p4(pop, stat_transform="rank")

    # length controls
    out["length_exact_factor"] = p4(pop, X=design_factor(pop, [TYPE, SITE, LENX]),
                                    strata=[(t["type"], L.site6(t["site"]), t["length"]) for t in pop])
    st_ts = [(t["type"], L.site6(t["site"])) for t in pop]
    lin = np.column_stack([design_factor(pop, [TYPE, SITE]), [t["length"] for t in pop]])
    out["length_linear_strata_type_site"] = p4(pop, X=lin, strata=st_ts)
    quad = np.column_stack([lin, [t["length"] ** 2 for t in pop]])
    out["length_quadratic_strata_type_site"] = p4(pop, X=quad, strata=st_ts)
    out["length_linear_with_frozen_strata"] = p4(pop, X=lin)
    out["no_length_control_strata_type_site"] = p4(pop, X=design_factor(pop, [TYPE, SITE]), strata=st_ts)

    # site
    md = [t for t in pop if t["site"] == "Mohenjo-daro"]
    out["mohenjo_daro_only"] = p4(md, X=design_factor(md, [TYPE, LENC]),
                                  strata=[(t["type"], L.len_class(t["length"])) for t in md])
    nmd = [t for t in pop if t["site"] != "Mohenjo-daro"]
    out["outside_mohenjo_daro"] = p4(nmd)
    sq = [t for t in pop if t["type"] == "SEAL:S"]
    out["square_only"] = p4(sq)

    # dimension provenance
    out["mm_source_only"] = p4([t for t in pop if t["dims_unit"] == "mm"])
    out["inch_source_only"] = p4([t for t in pop if t["dims_unit"] == "inch"])

    def coarse_inch(t):
        if t["dims_unit"] != "inch":
            return False
        vals = [x for x in (t["raw_h"], t["raw_v"]) if x and x.strip()]
        return all(len(x.split(".")[1]) <= 1 if "." in x else True for x in vals)
    out["exclude_inch_values_rounded_to_0.1in"] = p4([t for t in pop if not coarse_inch(t)])
    out["exclude_h_equals_v"] = p4([t for t in pop if t["h"] != t["v"]])
    out["exclude_one_inch_25.4mm_faces"] = p4([t for t in pop if not (abs(t["h"] - 25.4) < 0.05 or abs(t["v"] - 25.4) < 0.05)])
    out["steatite_only"] = p4([t for t in pop if (t["material"] or "").lower().startswith("steat")])
    out["population_counts"] = {
        "dims_unit": dict(collections.Counter(t["dims_unit"] for t in pop)),
        "coarse_inch_rounding": int(sum(coarse_inch(t) for t in pop)),
        "h_equals_v": int(sum(t["h"] == t["v"] for t in pop)),
        "material": dict(collections.Counter(t["material"] for t in pop).most_common(8)),
        "preservation": dict(collections.Counter(t["preservation"] for t in pop)),
    }
    return out


def all_seals_variant(tab):
    pop_all = L.size_text_population(tab)
    return p4(pop_all)


# ---------------------------------------------------------------- P1a specificity

def between_ratio(pop, labels, min_n=3, nperm=1999):
    res = residuals(pop, np.array([t["log_area"] for t in pop]), L.base_design(pop))
    r = L.between_ratio_test(labels, res, L.strata_of(pop), min_n, nperm, rng)
    return {k: r[k] for k in ("units", "seals_in_units", "ratio_to_null_mean", "p_one_sided")}


def p1a_probe(pop):
    out = {}
    pos = {
        "last": lambda s: s[-1],
        "penultimate": lambda s: s[-2],
        "first": lambda s: s[0],
        "second": lambda s: s[1],
        "third_from_end_if_len4plus": lambda s: s[-3] if len(s) >= 4 else None,
    }
    for name, f in pos.items():
        out[name] = between_ratio(pop, [f(t["signs"]) for t in pop])
    # a random sign of each text (fixed draw), as a position-free reference
    r2 = np.random.default_rng(99)
    out["random_sign_of_text"] = between_ratio(pop, [t["signs"][r2.integers(len(t["signs"]))] for t in pop])
    for mn in (5, 8):
        out[f"last_min_n_{mn}"] = between_ratio(pop, [t["last"] for t in pop], min_n=mn)
    res0 = residuals(pop, np.array([t["log_area"] for t in pop]), L.base_design(pop))
    top = set(np.argsort(-np.abs(res0))[:5])
    sub = [t for i, t in enumerate(pop) if i not in top]
    out["last_without_5_largest_abs_residuals"] = between_ratio(sub, [t["last"] for t in sub])
    out["first_without_5_largest_abs_residuals"] = between_ratio(sub, [t["first"] for t in sub])
    return out


# ---------------------------------------------------------------- metadata of high-set seals

def high_set_table(pop):
    res = residuals(pop, np.array([t["log_area"] for t in pop]), L.base_design(pop))
    strata = L.strata_of(pop)
    size_of_stratum = collections.Counter(strata)
    tracked, raw = [], []
    for t, r, s in zip(pop, res, strata):
        if t["last"] not in HIGH:
            continue
        row = {"half": t["half"], "cisi": t["cisi"], "family": t["family"], "site": t["site"], "type": t["type"],
               "h_mm": t["h"], "v_mm": t["v"], "inch_strings": [t["raw_h"], t["raw_v"]], "dims_unit": t["dims_unit"],
               "preservation": t["preservation"], "condition": t["condition"], "material": t["material"],
               "direction": t["direction"], "motif": t["symbol_full"], "cult": t["cult"], "boss": t["boss"],
               "text_class": t["text_class"], "area_section": t["area_section"], "period": t["period"],
               "length": t["length"], "last_two": t["signs"][-2:], "has_blank_space": t["has_blank_space"],
               "residual": round(float(r), 3), "stratum_size": size_of_stratum[s]}
        tracked.append(row)
        raw.append(dict(row, legend=t["signs"]))
    return tracked, raw


def context_rates(pop):
    """Base rates in the population for fields that look unusual among high-set seals."""
    md = [t for t in pop if t["site"] == "Mohenjo-daro"]
    area = collections.Counter((t["area_section"] or "")[:3] for t in md)
    return {"mohenjo_daro_area_prefix": dict(area.most_common(10)),
            "rectangular_share": float(np.mean([t["type"] == "SEAL:R" for t in pop])),
            "non_steatite": dict(collections.Counter(t["material"] for t in pop
                                                     if not (t["material"] or "").lower().startswith("steat")))}


def main():
    halves = {"discovery": build(load_discovery()), "confirmation": build(load_confirmation_direct())}
    out = {"status": STATUS, "permutations": NPERM, "high_set": sorted(HIGH)}
    tracked, raw = [], []
    pops = {}
    for h, tab in halves.items():
        pop = frozen_population(tab)
        pops[h] = pop
        out[h] = {"variants": variants(pop), "all_seals_not_one_per_component": all_seals_variant(tab),
                  "p1a_specificity": p1a_probe(pop), "context_rates": context_rates(pop)}
        a, b = high_set_table(pop)
        tracked += a
        raw += b
    # pooled halves: each half's components are disjoint, so one seal per component still holds
    pooled = pops["discovery"] + pops["confirmation"]
    out["pooled"] = {"frozen_rules": p4(pooled),
                     "only_820": p4(pooled, high={"820"}),
                     "without_820": p4(pooled, high=HIGH - {"820"}),
                     "mohenjo_daro_only": p4([t for t in pooled if t["site"] == "Mohenjo-daro"],
                                             X=design_factor([t for t in pooled if t["site"] == "Mohenjo-daro"], [TYPE, LENC]),
                                             strata=[(t["type"], L.len_class(t["length"])) for t in pooled if t["site"] == "Mohenjo-daro"])}
    out["high_set_seals"] = tracked
    write_json("shot-a-robustness.json", out)
    write_raw("high-set-legends.json", {"status": STATUS, "seals": raw})
    c = out["confirmation"]["variants"]
    for k, v in c.items():
        if isinstance(v, dict) and "difference" in v:
            print(f"{k:45s} n_high={v.get('n_high')} diff={v['difference']:.3f} p={v['p_one_sided']:.4f}")
        elif isinstance(v, list):
            for x in v:
                print("   LOO", x)
    print("pooled", out["pooled"])


if __name__ == "__main__":
    main()
