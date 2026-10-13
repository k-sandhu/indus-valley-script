"""Adversarial review, step 1: what drives the base-family gain?

Usage: python -X utf8 review_step1.py --out <new dir under data/raw/2026-10-12-structure-first/>

Reuses the frozen step 1 model code unchanged and evaluates additional groupings:
1. Coder-1 families with the stroke-numeral families (B001, B031) split into singletons.
2. Coder-1 families with only the numeral families kept (every other code a singleton).
3. Random contiguous partitions of the Wells number line with the same number of groups
   as coder 1 (no visual judgement; tests whether catalogue order alone carries the gain).
4. The frozen baseline and B_coder1 model with an end-of-text symbol added, as the
   protocol specifies ("with start and end symbols").
Also reports how far each coder's families follow Wells order.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step1-signs"))
import common  # noqa: E402
import analyze_step1 as A  # noqa: E402


def null_test(ev, data, mapping, nulls, rng, fixed=()):
    cls, ncls = A.class_array(data, mapping)
    bits, lams, per_tok = ev.evaluate(cls, ncls, keep_tokens=True)
    gain = ev.base_bits - bits
    free = np.array([i for i in range(len(cls) - 1) if data.vocab[i] not in fixed])
    null = []
    for _ in range(nulls):
        rc = cls.copy()
        rc[free] = rng.permutation(cls[free])
        b, _, _ = ev.evaluate(rc, ncls)
        null.append(ev.base_bits - b)
    null = np.array(null)
    return {"groups": int(ncls - 1), "gain_bits": float(gain), "lambda_by_fold": lams,
            "null_mean": float(null.mean()), "null_p95": float(np.quantile(null, .95)),
            "p_value": float((1 + (null >= gain).sum()) / (1 + nulls)),
            "passes": bool(gain > 0 and gain > np.quantile(null, .95))}, per_tok


class DataEnd(A.Data):
    """Same as the frozen Data class but with an end-of-text target appended to every text."""

    def __init__(self, texts, folds, vocab):
        vocab = list(vocab) + ["</s>"]
        super().__init__([tuple(t) + ("</s>",) for t in texts], folds, vocab)


def contiguity(coding, codes):
    pos = {c: i for i, c in enumerate(codes)}
    fam = collections.defaultdict(list)
    for c in codes:
        fam[coding[c]["base"]].append(pos[c])
    runs = sum(1 + sum(1 for a, b in zip(sorted(v), sorted(v)[1:]) if b != a + 1) for v in fam.values())
    single = sum(1 for v in fam.values() if all(b == a + 1 for a, b in zip(sorted(v), sorted(v)[1:])))
    adj = sum(coding[a]["base"] == coding[b]["base"] for a, b in zip(codes, codes[1:]))
    return {"families": len(fam), "contiguous_runs_in_wells_order": runs,
            "families_forming_one_run": single, "adjacent_pairs_same_family": adj, "adjacent_pairs": len(codes) - 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nulls", type=int, default=200)
    ap.add_argument("--contiguous", type=int, default=100)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)

    items = common.load_clean()
    texts = [d["text"] for d in items]
    folds = [d["fold"] for d in items]
    comp_names = sorted({d["component"] for d in items})
    comp_idx = {c: i for i, c in enumerate(comp_names)}
    comp_of_text = [comp_idx[d["component"]] for d in items]
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    coder2 = common.load_coding(common.PROG / "step1-signs/second-coder/components_coder2.tsv")
    corpus_codes = sorted({s for t in texts for s in t})
    vocab = sorted(set(coding) | set(corpus_codes))
    inv = common.inventories(coding, vocab)
    B = inv["B"]
    tok = collections.Counter(s for t in texts for s in t)

    res = {"note": "Review rerun; frozen step 1 code imported unchanged except where stated.",
           "contiguity_attested": {"coder1": contiguity(coding, corpus_codes),
                                   "coder2": contiguity(coder2, corpus_codes)}}
    # agreement on cut points between adjacent attested codes
    cut1 = [coding[a]["base"] != coding[b]["base"] for a, b in zip(corpus_codes, corpus_codes[1:])]
    cut2 = [coder2[a]["base"] != coder2[b]["base"] for a, b in zip(corpus_codes, corpus_codes[1:])]
    res["cut_point_kappa_adjacent_attested"] = A.kappa(cut1, cut2)
    res["cut_points"] = {"coder1": sum(cut1), "coder2": sum(cut2), "both": sum(a and b for a, b in zip(cut1, cut2))}

    data = A.Data(texts, folds, vocab)
    ev = A.Evaluator(data, comp_of_text)
    rng = np.random.default_rng(common.SEED + 101)
    res["baseline_bits"] = ev.base_bits

    no_num = {c: ("S" + c if B[c] in ("B001", "B031") else B[c]) for c in vocab}
    only_num = {c: (B[c] if B[c] in ("B001", "B031") else "S" + c) for c in vocab}
    tests = {}
    for name, mp in (("B_coder1_frozen_rerun", B), ("B_coder1_numerals_split", no_num),
                     ("numeral_families_only", only_num)):
        r, per_tok = null_test(ev, data, mp, args.nulls, rng)
        tests[name] = r
        print(name, json.dumps(r), flush=True)
    res["grouping_tests"] = tests

    # random contiguous partitions of the Wells number line (all 722 vocabulary codes)
    ngroups = len(set(B[c] for c in vocab))
    gains = []
    crng = np.random.default_rng(common.SEED + 102)
    for _ in range(args.contiguous):
        cuts = np.sort(crng.choice(np.arange(1, len(vocab)), ngroups - 1, replace=False))
        lab = np.searchsorted(cuts, np.arange(len(vocab)), side="right")
        mp = {c: f"K{lab[i]}" for i, c in enumerate(vocab)}
        cls, ncls = A.class_array(data, mp)
        b, _, _ = ev.evaluate(cls, ncls)
        gains.append(ev.base_bits - b)
    gains = np.array(gains)
    res["random_contiguous_wells_partitions"] = {
        "partitions": args.contiguous, "groups": ngroups, "gain_mean": float(gains.mean()),
        "gain_p5": float(np.quantile(gains, .05)), "gain_p95": float(np.quantile(gains, .95)),
        "gain_max": float(gains.max()),
        "share_above_frozen_B_null_p95_0.00609": float((gains > 0.006089476741500688).mean()),
        "share_at_or_above_B_coder1_gain": float((gains >= tests["B_coder1_frozen_rerun"]["gain_bits"]).mean())}
    print("contiguous", json.dumps(res["random_contiguous_wells_partitions"]), flush=True)

    # end symbol, as written in the protocol
    dend = DataEnd(texts, folds, vocab)
    eve = A.Evaluator(dend, comp_of_text)
    mpe = dict(B)
    mpe["</s>"] = "END"
    r, _ = null_test(eve, dend, mpe, min(args.nulls, 100), np.random.default_rng(common.SEED + 103),
                     fixed=("</s>",))
    res["with_end_symbol"] = {"baseline_bits": eve.base_bits, "held_out_targets": int(eve.n), "B_coder1": r}
    print("end", json.dumps(res["with_end_symbol"]), flush=True)
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
