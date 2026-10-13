"""Stage 3f v2 (review response, Amendment 4): local ranks by log-likelihood and by order gain.

Version 1 ranked by raw log-likelihood, which favours frequent classes; ranking by order gain favours
rare ones. Both rankings are reported for the key and 20 permuted keys; v1 output is unchanged.

Original description: local likelihood rank of each key value.

For every sign whose key value is a single consonant class, hold all other signs at their key values
and compute the total order-5 log-likelihood of the texts containing that sign under each of the
fifteen classes. Rank 1 means the key's value is the most Sanskrit-likely choice for that sign.
The same ranks are computed for frequency-stratified permuted keys and for one annealed key.
"""
import json
import os

import numpy as np

import stage3_fit as s3
from common import CID, CLASSES, HERE, NC, RAW, frequency_strata, key_options, permuted_options, unique_texts

SEED = 20261012 + 31337


METRIC = {"ll": 1, "llr": 0}
_IDX = [1]


def text_ll(text, opts_int):
    return s3.score_text(text, opts_int)[_IDX[0]]


def ranks_for(texts, opts_int, signs):
    where = {s: [] for s in signs}
    for i, t in enumerate(texts):
        for x in set(t):
            if x in where:
                where[x].append(i)
    out = {}
    for s in signs:
        cur = opts_int[s]
        if len(cur) != 1 or len(cur[0]) != 1:
            continue
        own = cur[0][0]
        lls = np.zeros(NC)
        for c in range(NC):
            opts_int[s] = ((c,),)
            lls[c] = sum(text_ll(texts[k], opts_int) for k in where[s])
        opts_int[s] = cur
        rank = 1 + int((lls > lls[own] + 1e-12).sum())
        out[s] = {"rank": rank, "deficit_bits": float(lls.max() - lls[own]), "best": CLASSES[int(lls.argmax())],
                  "own": CLASSES[own], "texts": len(where[s])}
    return out


def summarize(r, freq):
    ranks = np.array([v["rank"] for v in r.values()])
    out = {"signs": int(len(ranks)), "mean_rank": float(ranks.mean()), "share_rank1": float((ranks == 1).mean()),
           "share_rank_le3": float((ranks <= 3).mean()), "mean_deficit_bits": float(np.mean([v["deficit_bits"] for v in r.values()]))}
    by = {}
    for lo, hi in ((1, 2), (3, 9), (10, 49), (50, 10 ** 9)):
        sel = [v["rank"] for s, v in r.items() if lo <= freq[s] <= hi]
        if sel:
            by[f"{lo}-{hi if hi < 10**9 else 'max'}"] = {"signs": len(sel), "mean_rank": float(np.mean(sel)),
                                                        "share_rank1": float(np.mean(np.array(sel) == 1))}
    out["by_text_frequency"] = by
    return out


def main():
    s3.load_model()
    texts = unique_texts(min_len=2)
    options = key_options()
    signs = sorted({x for t in texts for x in t})
    strata = frequency_strata(texts)
    freq = {}
    for t in texts:
        for x in set(t):
            freq[x] = freq.get(x, 0) + 1
    key_int = s3.to_int(options)
    key_r = ranks_for(texts, dict(key_int), signs)
    res = {"key": summarize(key_r, freq)}
    perm_summ = []
    for i in range(20):
        perm = permuted_options(options, signs, strata, np.random.default_rng(SEED + i))
        pr = ranks_for(texts, s3.to_int(perm), signs)
        perm_summ.append(summarize(pr, freq))
    res["N1_20_keys"] = {"mean_rank": float(np.mean([p["mean_rank"] for p in perm_summ])),
                         "sd_mean_rank": float(np.std([p["mean_rank"] for p in perm_summ])),
                         "share_rank1": float(np.mean([p["share_rank1"] for p in perm_summ])),
                         "share_rank_le3": float(np.mean([p["share_rank_le3"] for p in perm_summ]))}
    path = os.path.join(RAW, "sanskrit-key", "stage3_assignments.json")
    with open(path, encoding="utf-8") as f:
        ann = json.load(f)
    best = max((a for a in ann if a["label"] == "real"), key=lambda a: a["G_fit"])
    ann_opts = {x: tuple(tuple(CID[c] for c in o) for o in v) for x, v in best["assignment"].items()}
    for x in key_int:
        ann_opts.setdefault(x, key_int[x])
    res["annealed_best_real"] = summarize(ranks_for(texts, ann_opts, signs), freq)
    res["key_examples_most_frequent"] = sorted(
        ({"sign": x, **v} for x, v in key_r.items()), key=lambda v: -v["texts"])[:25]
    return res


def run_both():
    out = {}
    for name, idx in METRIC.items():
        _IDX[0] = idx
        r = main()
        out[name] = {k: v for k, v in r.items() if k != "key_examples_most_frequent"}
    os.makedirs(os.path.join(HERE, "stage3f"), exist_ok=True)
    with open(os.path.join(HERE, "stage3f", "summary-v2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    for name, r in out.items():
        print(name, "key", round(r["key"]["mean_rank"], 2), round(r["key"]["share_rank1"], 3),
              "perm", round(r["N1_20_keys"]["mean_rank"], 2), round(r["N1_20_keys"]["sd_mean_rank"], 2),
              round(r["N1_20_keys"]["share_rank1"], 3))


if __name__ == "__main__":
    run_both()
