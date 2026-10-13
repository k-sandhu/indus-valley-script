"""Exploratory review analysis: rank-based versions of P4 for the full set and for 820 alone.

The frozen P4 statistic is a difference of mean residuals, which a few very large seals can
carry. Here the residuals of the frozen base model are replaced by their ranks (scaled to
-0.5..0.5) before the same within-stratum permutation. Output: review/shot-a-rank-checks.json.
"""
from review_common import load_all, write_json, STATUS
from shot_a_robustness import build, frozen_population, p4, HIGH


def main():
    tab = build(load_all())
    pops = {h: frozen_population([t for t in tab if t["half"] == h]) for h in ("discovery", "confirmation")}
    pops["pooled"] = pops["discovery"] + pops["confirmation"]
    out = {"status": STATUS}
    for h, pop in pops.items():
        out[h] = {"set_rank": p4(pop, stat_transform="rank"),
                  "820_mean": p4(pop, high={"820"}),
                  "820_rank": p4(pop, high={"820"}, stat_transform="rank"),
                  "set_without_820_rank": p4(pop, high=HIGH - {"820"}, stat_transform="rank")}
    write_json("shot-a-rank-checks.json", out)
    for h, v in out.items():
        if h != "status":
            print(h, {k: (x["n_high"], round(x["difference"], 3), x["p_one_sided"]) for k, x in v.items()})


if __name__ == "__main__":
    main()
