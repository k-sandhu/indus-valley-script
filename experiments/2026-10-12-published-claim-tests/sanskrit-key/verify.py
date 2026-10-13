"""Independent recomputation of Study A headline numbers by separate code paths.

1. Key skeletons by an iterative ligature resolver written without common.resolve_values.
2. The key's order gain from a freshly trained Kneser-Ney model scored with logprob_seq rather than the
   dense table, choosing the best an/aṃ option by exhaustive enumeration rather than greedily.
3. The key's readable share (Monier-Williams, m = 1 and 2) by a recursive memoized check.
4. Ten Stage 3 permutation keys regenerated from their seeds and rescored.
5. Validation that real words do not receive negative order gain by construction.

Version 2 (review response): compares like with like at 1e-9. The greedy n/m choice is recomputed through
the freshly trained model's prob() calls and compared with Stage 3; the exhaustive choice is compared with
the exhaustive sensitivity; dense-table scores are compared with logprob_seq on sampled sequences.
Version 1 output is preserved as verification-v1.json.
"""
import csv
import itertools
import json
import math
import os
import re
from functools import lru_cache

import numpy as np

import stage3_fit as s3
from common import (CID, HERE, KEY_CSV, MW_TXT, NC, RAW, KneserNey, dcs_lines, dcs_split, encode,
                    frequency_strata, iast_skeleton, key_options, permuted_options, slp1_skeleton, unique_texts)


def independent_skeletons():
    with open(KEY_CSV, encoding="utf-8") as f:
        rows = {r["sign"]: r for r in csv.DictReader(f)}
    tokens = {}
    for _ in range(12):  # fixed-point iteration over ligature components
        for s, r in rows.items():
            if r["xlit"]:
                tokens[s] = [r["xlit"]]
            elif "-" in (r["canonical"] or ""):
                parts = r["canonical"].split("-")[::-1]
                if all(p in tokens for p in parts):
                    tokens[s] = [t for p in parts for t in tokens[p]]
            elif r["canonical"] and r["canonical"] != s and r["canonical"] in tokens:
                tokens[s] = tokens[r["canonical"]]
    out = {}
    for s, toks in tokens.items():
        if s in ("000", "999"):
            continue
        choices = [("n", "m") if t == "an" else (slp1_skeleton(t),) for t in toks]
        out[s] = tuple(sorted({"".join(c) for c in itertools.product(*choices)}))
    return out


def main():
    res = {}
    opts = key_options()
    ind = independent_skeletons()
    res["skeleton_mismatches"] = sorted(s for s in opts if ind.get(s, ("",)) != opts[s])

    texts = unique_texts(min_len=2)
    split = dcs_split()
    train = [encode(iast_skeleton(l)) for p in split["train"] for l in dcs_lines(p) if iast_skeleton(l)]
    model = KneserNey(5, NC).fit(train)
    uni = np.bincount([c for s in train for c in s], minlength=NC).astype(float)
    logu = np.log2(uni / uni.sum())

    def llr(seq):
        return model.logprob_seq(seq) - float(sum(logu[c] for c in seq))

    # greedy choice through prob() calls, as Stage 3 chooses with the dense table
    def greedy_llr(t):
        ctx = [NC] * 4
        a = 0.0
        k = 0
        for x in t:
            best = None
            for o in opts[x]:
                c = list(ctx)
                v = 0.0
                for ch in encode(o):
                    v += math.log2(model.prob(tuple(c), ch)) - logu[ch]
                    c = c[1:] + [ch]
                if best is None or v > best[0]:
                    best = (v, o)
            for ch in encode(best[1]):
                a += math.log2(model.prob(tuple(ctx), ch)) - logu[ch]
                ctx = ctx[1:] + [ch]
                k += 1
        return a, k

    ga = gn = 0.0
    for t in texts:
        a, k = greedy_llr(t)
        ga += a
        gn += k
    res["key_G_greedy_independent_path"] = ga / gn

    tot = n = 0.0
    for t in texts:
        combos = [""]
        for x in t:
            combos = [c + o for c in combos for o in opts[x]]
        best = max((llr(encode(c)), len(c)) for c in set(combos))
        tot += best[0]
        n += best[1]
    res["key_G_exhaustive_options"] = tot / n
    with open(os.path.join(HERE, "stage3", "summary.json")) as f:
        st3 = json.load(f)
    res["key_G_stage3_greedy"] = st3["key"]["all"]["G"]
    with open(os.path.join(HERE, "stage3", "sensitivity_exhaustive.json")) as f:
        res["key_G_exhaustive_sensitivity"] = json.load(f)["key_G_exhaustive"]
    # dense table against logprob_seq on sampled held-out and random sequences
    table = np.load(os.path.join(RAW, "sanskrit-key", "models", "skeleton_kn5.npz"))["table"]
    rs = np.random.default_rng(7)
    seqs = [list(rs.integers(NC, size=rs.integers(1, 12))) for _ in range(200)]
    seqs += [encode(iast_skeleton(l))[:12] for p in split["heldout"][:20] for l in dcs_lines(p)[:10] if iast_skeleton(l)]
    worst = 0.0
    for sq in seqs:
        ctx = 0
        for _ in range(4):
            ctx = ctx * (NC + 1) + NC
        d = 0.0
        for x in sq:
            d += table[ctx, x]
            ctx = (ctx * (NC + 1) + x) % (NC + 1) ** 4
        worst = max(worst, abs(d - model.logprob_seq(sq)))
    res["dense_vs_logprob_max_abs_diff"] = float(worst)
    res["dense_vs_logprob_sequences"] = len(seqs)

    # readability
    pat = re.compile(r"<k1>([^<]+)<k2>")
    mw = set()
    with open(MW_TXT, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<L>"):
                m = pat.search(line)
                if m and slp1_skeleton(m.group(1)):
                    mw.add(slp1_skeleton(m.group(1)))
    endings = ("", "s", "m", "n", "y", "t", "sy")

    def readable(sk, m):
        @lru_cache(maxsize=None)
        def stems(i):  # can sk[:i] be covered by >= 1 stems
            if i == 0:
                return True
            return any(stems(j) and sk[j:i] in mw for j in range(max(0, i - 12), i - m + 1))

        return any(len(sk) - len(e) > 0 and sk.endswith(e) and stems(len(sk) - len(e)) for e in endings)

    for m in (1, 2):
        ok = 0
        for t in texts:
            combos = [""]
            for x in t:
                combos = [c + o for c in combos for o in opts[x]]
            ok += any(readable(c, m) for c in set(combos) if c)
        res[f"key_readable_mw_m{m}"] = ok / len(texts)
    with open(os.path.join(HERE, "stage2", "summary.json"), encoding="utf-8") as f:
        st2 = json.load(f)
    res["stage2_key_readable"] = {k: st2["key_readable_share"][k] for k in ("mw_m1", "mw_m2")}

    # permutations regenerated from seeds
    s3.load_model()
    signs = sorted({x for t in texts for x in t})
    strata = frequency_strata(texts)
    arr = np.load(os.path.join(RAW, "sanskrit-key", "stage3_null_arrays.npz"))["n1"]
    diffs = []
    for i in range(10):
        perm = permuted_options(opts, signs, strata, np.random.default_rng(s3.SEED + i))
        g = s3.corpus_stats(texts, s3.to_int(perm))["G"]
        diffs.append(abs(g - arr[i, 0]))
    res["perm_regeneration_max_abs_diff"] = float(max(diffs))

    # validation: real words
    rng = np.random.default_rng(99)
    held = [l for p in split["heldout"] for l in dcs_lines(p)]
    words = [w for l in held for w in l.split() if iast_skeleton(w)]
    sel = [words[i] for i in rng.choice(len(words), 4000, replace=False)]
    lens = sum(len(iast_skeleton(w)) for w in sel)
    res["heldout_single_words_G_fresh_model"] = sum(llr(encode(iast_skeleton(w))) for w in sel) / lens
    res["checks_pass"] = bool(not res["skeleton_mismatches"]
                          and abs(res["key_G_greedy_independent_path"] - res["key_G_stage3_greedy"]) < 1e-9
                          and abs(res["key_G_exhaustive_options"] - res["key_G_exhaustive_sensitivity"]) < 1e-9
                          and res["dense_vs_logprob_max_abs_diff"] < 1e-9
                          and all(abs(res[f"key_readable_mw_m{m}"] - res["stage2_key_readable"][f"mw_m{m}"]) < 1e-3
                                  for m in (1, 2))
                          and res["perm_regeneration_max_abs_diff"] < 1e-9)
    with open(os.path.join(HERE, "verification.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
