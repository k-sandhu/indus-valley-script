"""Adversarial review, step 1 supplement: how many held-out tokens each grouping can affect.

Usage: python -X utf8 review_step1_coverage.py --out <new dir under data/raw/2026-10-12-structure-first/>

A class model can only change predictions for codes that share a class with another code.
This reports, for the frozen B_coder1 and modifier-signature groupings, the share of held-out
tokens whose target code is in a non-singleton group, and the mean gain per such token. It
also tests each modifier on its own (codes carrying that modifier grouped across bases, all
other codes singletons) with 200 random partitions, which the pooled signature test cannot show.
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
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import analyze_step1 as A  # noqa: E402
from review_step1 import null_test  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nulls", type=int, default=200)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    items = common.load_clean()
    texts = [d["text"] for d in items]
    folds = [d["fold"] for d in items]
    comp_idx = {c: i for i, c in enumerate(sorted({d["component"] for d in items}))}
    comp_of_text = [comp_idx[d["component"]] for d in items]
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    corpus_codes = sorted({s for t in texts for s in t})
    vocab = sorted(set(coding) | set(corpus_codes))
    inv = common.inventories(coding, vocab)
    modsig = common.modifier_signature(coding, vocab)
    data = A.Data(texts, folds, vocab)
    ev = A.Evaluator(data, comp_of_text)
    base_tok = np.concatenate([-np.log2(s["kn"]) for s in ev.splits])
    targets = np.concatenate([s["ce"] for s in ev.splits])
    res = {}
    for name, mp in (("B_coder1", inv["B"]), ("modifier_signature", modsig)):
        cls, ncls = A.class_array(data, mp)
        _, _, per_tok = ev.evaluate(cls, ncls, keep_tokens=True)
        sizes = collections.Counter(cls[:-1])
        grouped = np.array([sizes[cls[t]] > 1 for t in targets])
        res[name] = {"share_of_held_out_tokens_in_non_singleton_groups": float(grouped.mean()),
                     "mean_gain_bits_on_those_tokens": float((base_tok[grouped] - per_tok[grouped]).mean()),
                     "mean_gain_bits_on_other_tokens": float((base_tok[~grouped] - per_tok[~grouped]).mean())}
    rng = np.random.default_rng(common.SEED + 111)
    per_mod = {}
    for m in ("inner", "side", "double", "hatch", "top", "encl", "cap", "dots", "bar"):
        mp = {}
        for c in vocab:
            row = coding.get(c)
            ok = row is not None and row["base"] not in ("B001", "B031") and m in row["mods"]
            mp[c] = ("MOD:" + m) if ok else ("S" + c)
        r, _ = null_test(ev, data, mp, args.nulls, rng)
        r["codes"] = sum(v == "MOD:" + m for v in mp.values())
        per_mod[m] = r
        print(m, json.dumps(r), flush=True)
    res["single_modifier_groupings"] = per_mod
    print(json.dumps({k: res[k] for k in ("B_coder1", "modifier_signature")}, indent=1))
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
