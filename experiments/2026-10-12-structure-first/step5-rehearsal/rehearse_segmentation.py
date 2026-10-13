"""Step 5a: segmenter calibration on readable scripts at Indus scale.

Usage: python -X utf8 rehearse_segmentation.py --out <run_dir>

Word boundaries are hidden from the segmenters and used only for scoring.
Cohorts follow PROTOCOL step 5: all Ur III seal legends; Sumerian lines and
Egyptian glyph sentences subsampled to the IVS text count and length
distribution; Akkadian letter lines subsampled the same way.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
import segmenters as S  # noqa: E402


def gold_from(rec):
    """Return (units tuple, gold internal boundaries) or None if not segmentable."""
    wu = rec.get("word_units")
    if not wu or any(len(w) == 0 for w in wu):
        return None
    units, b = [], []
    for w in wu:
        units.extend(w)
        b.append(len(units))
    return tuple(units), b[:-1]


def matched_sample(pool, target_lengths, rng):
    """Sample texts from pool to reproduce the target length distribution (with replacement across lengths if short)."""
    by_len = collections.defaultdict(list)
    for item in pool:
        by_len[len(item[0])].append(item)
    out = []
    for L, k in sorted(collections.Counter(target_lengths).items()):
        cands = by_len.get(L, [])
        if not cands:
            continue
        if len(cands) >= k:
            out.extend(rng.sample(cands, k))
        else:
            out.extend(cands)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sweeps", type=int, default=2000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(common.SEED + 5)
    ivs = common.load_clean()
    ivs_lengths = [len(d["text"]) for d in ivs]
    recs = common.read_jsonl(common.BRONZE)
    cohorts = {}

    def pool(pred):
        seen, items = set(), []
        for r in recs:
            if not pred(r):
                continue
            g = gold_from(r)
            if g is None or len(g[0]) < 2 or g[0] in seen:
                continue
            if any(u.startswith("NUM:") for u in g[0]):
                pass
            seen.add(g[0])
            items.append(g)
        return items

    sum_seal = pool(lambda r: r["corpus"] == "sumerian" and r["kind"] == "seal")
    cohorts["sumerian_seals_all"] = sum_seal
    cohorts["sumerian_lines_matched"] = matched_sample(
        pool(lambda r: r["corpus"] == "sumerian" and r["kind"] == "natural_line"), ivs_lengths, rng)
    cohorts["egyptian_glyph_sentences_matched"] = matched_sample(
        pool(lambda r: r["corpus"] == "egyptian" and r["kind"] == "glyph_sentence"), ivs_lengths, rng)
    cohorts["akkadian_letter_lines_matched"] = matched_sample(
        pool(lambda r: r["corpus"] == "akkadian" and r["kind"] == "natural_line"), ivs_lengths, rng)

    summary = {"protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"),
               "records_sha256": common.sha256(common.BRONZE), "sweeps": args.sweeps, "cohorts": {}}
    for name, items in cohorts.items():
        texts = [t for t, _ in items]
        gold = [b for _, b in items]
        lens = collections.Counter(len(t) for t in texts)
        res = {"texts": len(texts), "units": sum(len(t) for t in texts),
               "mean_length": sum(len(t) for t in texts) / len(texts),
               "unit_types": len({u for t in texts for u in t}),
               "gold_mean_word_length": sum(len(t) for t in texts) / sum(len(b) + 1 for b in gold),
               "length_distribution": dict(sorted(lens.items()))}
        preds = {"branching_entropy": S.branching_entropy(texts), "greedy_ngram": S.greedy_ngram(texts),
                 "dp_unigram": S.dp_unigram(texts, sweeps=args.sweeps)}
        preds["all_boundaries"] = [list(range(1, len(t))) for t in texts]
        preds["no_boundaries"] = [[] for t in texts]
        res["scores"] = {k: S.boundary_scores(gold, p, texts) for k, p in preds.items()}
        res["alternation_gold"] = S.alternation([u for t, b in zip(texts, gold) for u in S.units(t, b)])
        res["alternation_pred"] = {k: S.alternation([u for t, b in zip(texts, p) for u in S.units(t, b)])
                                   for k, p in preds.items() if k in ("branching_entropy", "greedy_ngram", "dp_unigram")}
        res["alternation_whole_texts"] = S.alternation(texts)
        summary["cohorts"][name] = res
        print(name, json.dumps({k: round(v["boundary_f1"], 3) for k, v in res["scores"].items()}), flush=True)
    seg_names = ("branching_entropy", "greedy_ngram", "dp_unigram")
    mean_f1 = {k: sum(c["scores"][k]["boundary_f1"] for c in summary["cohorts"].values()) / len(summary["cohorts"])
               for k in seg_names}
    summary["mean_boundary_f1"] = mean_f1
    summary["chosen_segmenter"] = max(mean_f1, key=mean_f1.get)
    summary["choice_rule"] = "Highest mean boundary F1 across the rehearsal cohorts (PROTOCOL step 3)."
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print("chosen", summary["chosen_segmenter"], json.dumps(mean_f1))


if __name__ == "__main__":
    main()
