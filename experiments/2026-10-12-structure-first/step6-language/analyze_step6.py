"""Step 6: structural profile of IVS and readable seal and record corpora.

Usage: python -X utf8 analyze_step6.py --segments <step3 segments json> --out <run_dir>

Implements PROTOCOL step 6 as amended in AMENDMENT-2026-10-12.md. No lexical or
phonetic fitting is performed.
"""
import argparse
import collections
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import segmenters as S  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "step5-rehearsal"))
from rehearse_segmentation import gold_from  # noqa: E402


def norm_entropy(counter, inv):
    n = sum(counter.values())
    h = -sum(v / n * math.log2(v / n) for v in counter.values())
    return h / math.log2(inv) if inv > 1 else 0.0


def edge_asymmetry(texts, rng, reps=1000):
    """Normalized entropy of initial units minus final units; shuffle reference permutes units within texts."""
    texts = [t for t in texts if len(t) >= 2]
    inv = len({u for t in texts for u in t})

    def stat(ts):
        first = collections.Counter(t[0] for t in ts)
        last = collections.Counter(t[-1] for t in ts)
        return norm_entropy(first, inv) - norm_entropy(last, inv), norm_entropy(first, inv), norm_entropy(last, inv)

    obs, hf, hl = stat(texts)
    null = []
    for _ in range(reps):
        sh = []
        for t in texts:
            l = list(t)
            rng.shuffle(l)
            sh.append(l)
        null.append(stat(sh)[0])
    null = np.array(null)
    return {"texts": len(texts), "inventory": inv, "initial_norm_entropy": hf, "final_norm_entropy": hl,
            "asymmetry_initial_minus_final": obs, "shuffle_mean": float(null.mean()),
            "shuffle_p2_5": float(np.quantile(null, .025)), "shuffle_p97_5": float(np.quantile(null, .975))}


def closed_class_position(texts, k=20, min_tok=20):
    tok = collections.Counter(u for t in texts for u in t)
    neigh = collections.defaultdict(set)
    pos = collections.defaultdict(list)
    for t in texts:
        n = len(t)
        for i, u in enumerate(t):
            neigh[u].add(t[i - 1] if i else "<s>")
            neigh[u].add(t[i + 1] if i + 1 < n else "</s>")
            if n > 1:
                pos[u].append(i / (n - 1))
    cands = [u for u, c in tok.items() if c >= min_tok and pos[u]]
    ranked = sorted(cands, key=lambda u: -len(neigh[u]) / tok[u])[:k]
    allpos = [p for u in cands for p in pos[u]]
    return {"eligible_types": len(cands), "selected": len(ranked),
            "mean_position_selected": float(np.mean([np.mean(pos[u]) for u in ranked])) if ranked else None,
            "mean_position_all_eligible_tokens": float(np.mean(allpos)) if allpos else None,
            "selected_units": [[str(u), tok[u], round(float(np.mean(pos[u])), 3)] for u in ranked[:10]]}


def mi(pairs):
    def h(c):
        n = sum(c.values())
        return -sum(v / n * math.log2(v / n) for v in c.values())
    a = collections.Counter(x for x, _ in pairs)
    b = collections.Counter(y for _, y in pairs)
    return h(a) + h(b) - h(collections.Counter(pairs))


def numeral_order(seqs, is_num, value, rng, perms=2000):
    nxt, prv = [], []
    for t in seqs:
        for i, u in enumerate(t):
            if is_num(u):
                n = t[i + 1] if i + 1 < len(t) else "</s>"
                p = t[i - 1] if i > 0 else "<s>"
                if is_num(n) or is_num(p):
                    continue
                nxt.append((value(u), n))
                prv.append((value(u), p))
    if len(nxt) < 30:
        return {"numeral_tokens": len(nxt), "note": "too few isolated numeral tokens"}
    vals = np.array([v for v, _ in nxt], dtype=object)
    res = {"numeral_tokens": len(nxt)}
    for name, pairs in (("following", nxt), ("preceding", prv)):
        obs = mi(pairs)
        items = [x for _, x in pairs]
        null = []
        for _ in range(perms):
            pv = rng.permutation(len(vals))
            null.append(mi(list(zip(vals[pv], items))))
        null = np.array(null)
        res[name] = {"mi_bits": obs, "null_mean": float(null.mean()), "excess_bits": float(obs - null.mean()),
                     "p_value": float((1 + (null >= obs).sum()) / (1 + perms))}
    res["following_minus_preceding_excess"] = res["following"]["excess_bits"] - res["preceding"]["excess_bits"]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", required=True)
    ap.add_argument("--chosen", default="dp_unigram")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(common.SEED + 6)
    nrng = np.random.default_rng(common.SEED + 6)
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    ivs_texts = [d["text"] for d in common.load_clean()]
    seals = {d["text"] for d in common.load_clean() if any(t.startswith("SEAL") for t in d["types"])}
    recs = common.read_jsonl(common.BRONZE)

    def corpus(pred):
        seen, out_ = set(), []
        for r in recs:
            if pred(r):
                g = gold_from(r)
                if g and len(g[0]) >= 2 and g[0] not in seen:
                    seen.add(g[0])
                    out_.append(g)
        return out_

    comps = {
        "sumerian_seals": corpus(lambda r: r["corpus"] == "sumerian" and r["kind"] == "seal"),
        "akkadian_seals": corpus(lambda r: r["corpus"] == "akkadian" and r["kind"] == "seal"),
        "egyptian_glyph_sentences": corpus(lambda r: r["corpus"] == "egyptian" and r["kind"] == "glyph_sentence"),
        "sumerian_tablets": corpus(lambda r: r["corpus"] == "sumerian" and r["kind"] == "whole_tablet"),
    }
    summary = {"protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"),
               "amendment_sha256": common.sha256(common.PROG / "step6-language/AMENDMENT-2026-10-12.md"),
               "typology_sha256": common.sha256(common.PROG / "step6-language/typology.json"), "profiles": {}}
    summary["profiles"]["ivs_all_clean"] = {"edge_asymmetry": edge_asymmetry(ivs_texts, rng),
                                            "closed_class_position": closed_class_position(ivs_texts)}
    summary["profiles"]["ivs_seals"] = {"edge_asymmetry": edge_asymmetry(sorted(seals), rng),
                                        "closed_class_position": closed_class_position(sorted(seals))}
    for name, items in comps.items():
        texts = [t for t, _ in items]
        words = [tuple(S.units(t, b)) for t, b in items]
        summary["profiles"][name] = {"sign_level": {"edge_asymmetry": edge_asymmetry(texts, rng),
                                                    "closed_class_position": closed_class_position(texts)},
                                     "word_level": {"edge_asymmetry": edge_asymmetry(words, rng),
                                                    "closed_class_position": closed_class_position(words)}}
    # segment-internal affix asymmetry (descriptive only, PROTOCOL step 5 rule)
    seg = json.loads(Path(args.segments).read_text(encoding="utf-8"))[args.chosen]
    units = [u for row in seg for u in S.units(tuple(row["text"]), row["bounds"]) if len(u) >= 2]
    inv = len({s for u in units for s in u})
    summary["ivs_segment_affix_asymmetry_descriptive"] = {
        "multi_sign_segments": len(units),
        "initial_norm_entropy": norm_entropy(collections.Counter(u[0] for u in units), inv),
        "final_norm_entropy": norm_entropy(collections.Counter(u[-1] for u in units), inv)}
    # numeral order, calibrated
    def ivs_num(u):
        r = coding.get(u)
        return bool(r and r["base"] in ("B001", "B031") and r["count"])
    summary["numeral_order"] = {
        "ivs_clean": numeral_order(ivs_texts, ivs_num, lambda u: int(coding[u]["count"]), nrng),
    }
    def words_of(pred):
        seqs = []
        for r in recs:
            if pred(r):
                seqs.append(tuple(zip(r["words"], r["gold"])))
        return seqs
    ur3 = words_of(lambda r: r["corpus"] == "sumerian" and r["kind"] == "whole_tablet")
    lb = words_of(lambda r: r["corpus"] == "mycenaean" and r["kind"] == "natural_line")
    num_ur3 = lambda u: u[1] == "NUMBER" and u[0].split("(")[0].isdigit()
    val_ur3 = lambda u: int(u[0].split("(")[0])
    num_lb = lambda u: u[1] == "NUMBER" and u[0].isdigit()
    val_lb = lambda u: int(u[0])
    summary["numeral_order"]["ur3_tablets"] = numeral_order([tuple(w for w in s) for s in ur3], num_ur3, val_ur3, nrng)
    summary["numeral_order"]["linear_b_lines"] = numeral_order([tuple(w for w in s) for s in lb], num_lb, val_lb, nrng)
    summary["typology"] = json.loads((common.PROG / "step6-language/typology.json").read_text(encoding="utf-8"))["candidates"]
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    for k, v in summary["profiles"].items():
        print(k, json.dumps(v, default=str)[:700])
    print(json.dumps(summary["numeral_order"], indent=0, default=str))
    print(json.dumps(summary["ivs_segment_affix_asymmetry_descriptive"]))


if __name__ == "__main__":
    main()
