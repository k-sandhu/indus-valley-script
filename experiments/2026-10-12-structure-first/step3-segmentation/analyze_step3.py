"""Step 3b: segment IVS with the rehearsal-chosen segmenter and compare alternation.

Usage: python -X utf8 analyze_step3.py --rehearsal <step5 summary.json> --out <run_dir>

The segmenter is fixed by the step 5 rehearsal before IVS segments are examined
(PROTOCOL step 3). Alternation is computed on distinct units; comparison corpora
are subsampled to the IVS number of distinct units per unit length.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import segmenters as S  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "step5-rehearsal"))
from rehearse_segmentation import gold_from, matched_sample  # noqa: E402

SEGMENTERS = {"branching_entropy": S.branching_entropy, "greedy_ngram": S.greedy_ngram, "dp_unigram": S.dp_unigram}


def unit_types(texts, bounds):
    return {u for t, b in zip(texts, bounds) for u in S.units(t, b)}


def length_profile(types):
    return collections.Counter(len(u) for u in types)


def matched_types(pool_types, target_profile, rng):
    by_len = collections.defaultdict(list)
    for u in pool_types:
        by_len[len(u)].append(u)
    out = []
    for L, k in target_profile.items():
        c = by_len.get(L, [])
        out.extend(rng.sample(c, k) if len(c) >= k else c)
    return out


def summarize(vals):
    return {"mean": float(np.mean(vals)), "p2_5": float(np.quantile(vals, .025)), "p97_5": float(np.quantile(vals, .975))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehearsal", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=200)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    reh = json.loads(Path(args.rehearsal).read_text(encoding="utf-8"))
    chosen = reh["chosen_segmenter"]
    ivs = common.load_clean()
    texts = [d["text"] for d in ivs]
    seg = {name: (f(texts) if name != "dp_unigram" else f(texts, sweeps=reh["sweeps"])) for name, f in SEGMENTERS.items()}
    common.RAW.mkdir(parents=True, exist_ok=True)
    (common.RAW / "step3-ivs-segments.json").write_text(json.dumps(
        {name: [{"text": list(t), "bounds": b} for t, b in zip(texts, bs)] for name, bs in seg.items()}) + "\n",
        encoding="utf-8")
    summary = {"protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"), "chosen_segmenter": chosen,
               "rehearsal_summary_sha256": common.sha256(args.rehearsal), "ivs": {}}
    for name, bs in seg.items():
        types = unit_types(texts, bs)
        units_tok = [u for t, b in zip(texts, bs) for u in S.units(t, b)]
        summary["ivs"][name] = {"unit_tokens": len(units_tok), "unit_types": len(types),
                                "mean_unit_length_tokens": float(np.mean([len(u) for u in units_tok])),
                                "unit_type_length_profile": dict(sorted(length_profile(types).items())),
                                "alternation": S.alternation(types),
                                "top_units": [["-".join(u), c] for u, c in collections.Counter(
                                    u for u in units_tok if len(u) >= 2).most_common(25)]}
    summary["ivs_whole_texts_alternation"] = S.alternation(set(texts))
    ivs_types = unit_types(texts, seg[chosen])
    prof = length_profile(ivs_types)
    rng = random.Random(common.SEED + 3)
    recs = common.read_jsonl(common.BRONZE)
    pools = {
        "sumerian_seals": lambda r: r["corpus"] == "sumerian" and r["kind"] == "seal",
        "sumerian_lines": lambda r: r["corpus"] == "sumerian" and r["kind"] == "natural_line",
        "akkadian_letter_lines": lambda r: r["corpus"] == "akkadian" and r["kind"] == "natural_line",
        "egyptian_glyph_sentences": lambda r: r["corpus"] == "egyptian" and r["kind"] == "glyph_sentence",
    }
    ivs_lengths = [len(t) for t in texts]
    comp = {}
    for name, pred in pools.items():
        items = []
        seen = set()
        for r in recs:
            if not pred(r):
                continue
            g = gold_from(r)
            if g is None or len(g[0]) < 2 or g[0] in seen:
                continue
            seen.add(g[0])
            items.append(g)
        gold_types = {u for t, b in items for u in S.units(t, b)}
        res = {"texts": len(items), "gold_unit_types": len(gold_types),
               "gold_alternation_full": S.alternation(gold_types)}
        vals = collections.defaultdict(list)
        for _ in range(args.reps):
            a = S.alternation(matched_types(sorted(gold_types), prof, rng))
            for k in ("alternation_rate", "finals_involved", "top5_final_share", "stems"):
                vals[k].append(a[k])
        res["gold_matched_to_ivs"] = {k: summarize(v) for k, v in vals.items()}
        # predicted units from the chosen segmenter on a length-matched text sample
        sample = items if name == "sumerian_seals" else matched_sample(items, ivs_lengths, rng)
        st = [t for t, _ in sample]
        pb = SEGMENTERS[chosen](st) if chosen != "dp_unigram" else S.dp_unigram(st, sweeps=reh["sweeps"])
        ptypes = unit_types(st, pb)
        vals = collections.defaultdict(list)
        for _ in range(args.reps):
            a = S.alternation(matched_types(sorted(ptypes), prof, rng))
            for k in ("alternation_rate", "finals_involved", "top5_final_share", "stems"):
                vals[k].append(a[k])
        res["predicted_matched_to_ivs"] = {k: summarize(v) for k, v in vals.items()}
        res["predicted_full"] = S.alternation(ptypes)
        comp[name] = res
        print(name, json.dumps({"gold": res["gold_matched_to_ivs"]["alternation_rate"],
                                "pred": res["predicted_matched_to_ivs"]["alternation_rate"]}), flush=True)
    summary["comparisons"] = comp
    summary["ivs_chosen_alternation"] = summary["ivs"][chosen]["alternation"]
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print("ivs", chosen, json.dumps(summary["ivs_chosen_alternation"]))


if __name__ == "__main__":
    main()
