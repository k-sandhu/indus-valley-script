"""Amendment 2 (exploratory): locality with merged sign variants and with a length-stratified null.

V1: every Wells code with exactly one Mayig class is replaced by that class, so variant spellings of
    one text count as identical; S1 is recomputed on the merged texts.
V2: S1 on exact texts with site labels permuted only among seals of the same text length.
"""
import json
import os
from collections import defaultdict

import numpy as np

import analysis as A

SEED = 20261012 + 202
N_PERM = 10000
CROSS = os.path.join(A.ROOT, "data", "normalized", "mayig_wells_class_crosswalk.json")


def groups_from(texts):
    g = defaultdict(list)
    for i, t in enumerate(texts):
        g[t].append(i)
    return [idx for idx in g.values() if len(idx) >= 2]


def main():
    rng = np.random.default_rng(SEED)
    seals = A.eligible_seals(A.load())
    sites = np.array([f["site"] for f in seals])
    with open(CROSS, encoding="utf-8") as f:
        cw = json.load(f)["by_wells_id"]
    merge = {w: v[0] for w, v in cw.items() if len(v) == 1}
    merged = [tuple(merge.get(x, x) for x in f["signs_reading_rtl"]) for f in seals]
    exact = [tuple(f["signs_reading_rtl"]) for f in seals]
    out = {"V1_mayig_merged": A.permutation_test(groups_from(merged), sites, rng, n=N_PERM)}
    lengths = np.array([len(t) for t in exact])
    out["V2_length_stratified_null"] = A.permutation_test(groups_from(exact), sites, rng, n=N_PERM, strata=lengths)
    with open(os.path.join(A.HERE, "run-2026-10-12", "sensitivity.json"), "w") as f:
        json.dump(out, f, indent=1)
    for k, v in out.items():
        t = v["text_weighted"]
        print(k, v["texts"], v["pairs"], "L %.3f null %.3f [%.3f, %.3f] p %.3f ratio %.2f | pair %.3f/%.3f" % (
            t["observed"], t["null_mean"], t["null_q025"], t["null_q975"], t["p_one_sided"], t["ratio_to_null_mean"],
            v["pair_weighted"]["observed"], v["pair_weighted"]["null_mean"]))


if __name__ == "__main__":
    main()
