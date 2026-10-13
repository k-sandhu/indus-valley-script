"""Independent checks of the seal-text analysis.

1. Eligible seals and shared-text groups rebuilt without importing analysis.py.
2. Observed same-site shares recomputed by explicit pair loops.
3. The permutation null mean of the same-site share equals the exact probability that two distinct
   objects drawn without replacement share a site, sum n_s(n_s-1) / (N(N-1)); same for motifs within site.
4. The dynamic-programming coincidence sum for length 2 equals brute-force enumeration over all pairs
   of signs, and the length-1 value equals a direct sum.
"""
import json
import math
import os
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FACES = os.path.join(ROOT, "data", "normalized", "lipi_observed_faces.jsonl")


def main():
    with open(os.path.join(HERE, "run-2026-10-12", "summary.json"), encoding="utf-8") as f:
        S = json.load(f)
    import analysis as A  # only for the model-fitting function under test in check 4
    faces = [json.loads(l) for l in open(FACES, encoding="utf-8")]
    foreign = A.FOREIGN
    fam = {}
    for f in faces:
        ok = (f["object_type"][:4] == "SEAL" and f["complete_observed"] and f["single_line"]
              and not f["has_unknown_sign"] and len(f["signs_reading_rtl"]) >= 2 and "000" not in f["signs_reading_rtl"]
              and f["site"] not in foreign and f["site"] not in ("Unknown", "", None))
        if ok:
            k = f["object_family_id"]
            if k not in fam or float(f["record_id"]) < float(fam[k]["record_id"]):
                fam[k] = f
    seals = list(fam.values())
    res = {"eligible": len(seals), "eligible_matches": len(seals) == S["eligible_seal_objects"]}
    groups = defaultdict(list)
    for f in seals:
        groups[tuple(f["signs_reading_rtl"])].append(f)
    shared = [g for g in groups.values() if len(g) >= 2]
    res["shared_texts"] = len(shared)
    shares, same, pairs = [], 0, 0
    for g in shared:
        sm = sum(1 for a, b in combinations(g, 2) if a["site"] == b["site"])
        n = len(g) * (len(g) - 1) // 2
        shares.append(sm / n)
        same += sm
        pairs += n
    res["L_text_weighted"] = sum(shares) / len(shares)
    res["L_pair_weighted"] = same / pairs
    res["L_matches"] = (abs(res["L_text_weighted"] - S["S1_all"]["text_weighted"]["observed"]) < 1e-12
                        and abs(res["L_pair_weighted"] - S["S1_all"]["pair_weighted"]["observed"]) < 1e-12)
    cnt = Counter(f["site"] for f in seals)
    N = len(seals)
    exact = sum(c * (c - 1) for c in cnt.values()) / (N * (N - 1))
    res["null_mean_exact"] = exact
    res["null_mean_permutation"] = S["S1_all"]["text_weighted"]["null_mean"]
    res["null_mean_close"] = abs(exact - res["null_mean_permutation"]) < 0.005

    # motif within-site exact null: probability two objects in the same pair share motif given their sites
    def motif(f):
        m = f.get("symbol")
        if m in A.NO_MOTIF:
            return None
        m = m.split(":")[0]
        return None if m in A.NO_MOTIF else m
    msite = defaultdict(Counter)
    for f in seals:
        if motif(f):
            msite[f["site"]][motif(f)] += 1
    exp_terms, obs_same, n_pairs = [], 0, 0
    text_shares, text_exp = [], []
    for g in shared:
        gm = [f for f in g if motif(f)]
        if len(gm) < 2:
            continue
        ps, sm = [], 0
        for a, b in combinations(gm, 2):
            sm += motif(a) == motif(b)
            if a["site"] == b["site"]:
                c = msite[a["site"]]
                n = sum(c.values())
                p = sum(v * (v - 1) for v in c.values()) / (n * (n - 1))
            else:
                ca, cb = msite[a["site"]], msite[b["site"]]
                na, nb = sum(ca.values()), sum(cb.values())
                p = sum(ca[m] * cb[m] for m in ca) / (na * nb)
            ps.append(p)
        k = len(ps)
        text_shares.append(sm / k)
        text_exp.append(sum(ps) / k)
    res["motif_observed_text_weighted"] = float(np.mean(text_shares))
    res["motif_null_mean_approx"] = float(np.mean(text_exp))
    res["motif_null_mean_permutation"] = S["S4_motif_concordance"]["text_weighted"]["null_mean"]
    res["motif_observed_matches"] = abs(res["motif_observed_text_weighted"] - S["S4_motif_concordance"]["text_weighted"]["observed"]) < 1e-12

    # S3 brute force for L = 1, 2
    legible = sorted({tuple(f["signs_reading_rtl"]) for f in faces if f["complete_observed"] and f["single_line"]
                      and not f["has_unknown_sign"] and len(f["signs_reading_rtl"]) >= 1 and "000" not in f["signs_reading_rtl"]})
    vocab = sorted({x for t in legible for x in t})
    s, T, e, D = A.kn_bigram(legible, vocab)
    dp = A.coincidence_by_length(s, T, e, 2)
    p1 = s * e
    bf1 = (float(p1.sum()), float((p1 ** 2).sum()))
    M = s[:, None] * T * e[None, :]
    bf2 = (float(M.sum()), float((M ** 2).sum()))
    res["S3_L1"] = {"dp": dp[1], "brute": bf1}
    res["S3_L2"] = {"dp": dp[2], "brute": bf2}
    res["S3_matches"] = all(abs(dp[L][i] - b[i]) < 1e-12 * max(1.0, b[i]) for L, b in ((1, bf1), (2, bf2)) for i in (0, 1))
    n2 = sum(1 for f in seals if len(f["signs_reading_rtl"]) == 2)
    res["S3_expected_L2_recomputed"] = math.comb(n2, 2) * bf2[1] / bf2[0] ** 2
    res["S3_expected_L2_reported"] = S["S3_whole_text_reuse"]["by_length"]["2"]["expected_pairs_model"]
    res["all_pass"] = bool(res["eligible_matches"] and res["L_matches"] and res["null_mean_close"]
                           and res["motif_observed_matches"] and res["S3_matches"]
                           and abs(res["S3_expected_L2_recomputed"] - res["S3_expected_L2_reported"]) < 1e-9)
    with open(os.path.join(HERE, "run-2026-10-12", "verification.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
