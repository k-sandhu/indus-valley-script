"""Adversarial review, step 6: what the edge asymmetry measures.

Usage: python -X utf8 review_step6.py --out <new dir under data/raw/2026-10-12-structure-first/>

1. IVS: share of texts ending in the commonest final sign, and the asymmetry after removing
   texts that end in it (one sign versus a closing class).
2. Ur III seal legends: sign-level asymmetry with the divine determinative removed, to see
   whether the contrast with IVS depends on that writing convention.
3. All comparison corpora: sign-level and word-level asymmetry side by side, from the frozen
   step 6 summary.
Imports the frozen step 6 functions unchanged.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step6-language"))
sys.path.insert(0, str(HERE.parents[1] / "step5-rehearsal"))
import common  # noqa: E402
import analyze_step6 as A  # noqa: E402
from rehearse_segmentation import gold_from  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(common.SEED + 606)
    texts = [d["text"] for d in common.load_clean() if len(d["text"]) >= 2]
    last = collections.Counter(t[-1] for t in texts)
    top, n_top = last.most_common(1)[0]
    res = {"ivs": {"texts": len(texts), "commonest_final": top, "share_ending_in_it": n_top / len(texts),
                   "top3_final_share": sum(v for _, v in last.most_common(3)) / len(texts),
                   "frozen": A.edge_asymmetry(texts, rng, 200),
                   "without_texts_ending_in_commonest_final": A.edge_asymmetry([t for t in texts if t[-1] != top], rng, 200)}}
    recs = common.read_jsonl(common.BRONZE)
    seals = []
    seen = set()
    for r in recs:
        if r["corpus"] == "sumerian" and r["kind"] == "seal":
            g = gold_from(r)
            if g and len(g[0]) >= 2 and g[0] not in seen:
                seen.add(g[0])
                seals.append(g[0])
    first = collections.Counter(t[0] for t in seals)
    res["ur3_seals"] = {"texts": len(seals), "commonest_initial": first.most_common(3),
                        "share_initial_d": first.get("d", 0) / len(seals),
                        "sign_level_frozen": A.edge_asymmetry(seals, rng, 200),
                        "sign_level_without_divine_determinative":
                            A.edge_asymmetry([tuple(u for u in t if u != "d") for t in seals], rng, 200)}
    frozen = json.loads((common.PROG / "step6-language/run-2026-10-12/summary.json").read_text(encoding="utf-8"))
    res["frozen_sign_vs_word_level"] = {
        k: {lvl: round(v[lvl]["edge_asymmetry"]["asymmetry_initial_minus_final"], 3) for lvl in ("sign_level", "word_level")}
        for k, v in frozen["profiles"].items() if "sign_level" in v}
    res["frozen_ur3_word_closed_class"] = frozen["profiles"]["sumerian_seals"]["word_level"]["closed_class_position"]
    print(json.dumps(res, indent=1, ensure_ascii=False))
    (out / "summary.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
