"""Exploratory checks written after the T1-T3 outcomes were seen (not part of the frozen protocol).

E1  Which target signs carry T1's internal advantage? Per-sign sums of (internal minus matched)
    surprisal over all held-out events, bigram and unigram, using T1's own matched sets.
E2  T1 with every stroke-count sign (Wells 001-056) merged into one symbol, to see whether the
    shared inventory is a stroke-numeral effect.
E3  Sign frequencies: share of sign tokens in the T1 round seals and in the matched pool.
Output: run-2026-10-12/exploratory.json
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter, defaultdict

import numpy as np

import analysis as A

STROKES = {f"{n:03d}" for n in range(1, 57)}


def contributions():
    objs = A.tests()["T1"][1]
    flat = [u for o in objs for u in o]
    rng = random.Random(f"{A.SEED_MATCH}-T1")
    cache = {}
    sets = [A.draw_matched(flat, rng, frozenset(), cache) for _ in range(A.D_MATCHED)]
    V = A.data()["V"]
    big, uni, count = defaultdict(float), defaultdict(float), Counter()
    for obj in objs:
        codes = {u["code"] for u in obj}
        fam = obj[0]["family"]
        idx = [j for j, u in enumerate(flat) if u["family"] != fam and u["code"] not in codes]
        m_int = A.fit([flat[j] for j in idx], V)
        m_mat = [A.fit([s[j] for j in idx if s[j]["code"] not in codes], V) for s in sets]
        for u in obj:
            n = len(u["events"])
            for a, b in u["events"]:
                d = -math.log2(m_int.p(a, b)) + float(np.mean([math.log2(m.p(a, b)) for m in m_mat]))
                du = -math.log2(m_int.p_uni(b)) + float(np.mean([math.log2(m.p_uni(b)) for m in m_mat]))
                big[b] += d / n / len(obj)
                uni[b] += du / n / len(obj)
                count[b] += 1
    n_obj = sum(1 for o in objs if any(u["events"] for u in o))
    rows = [{"target": w, "events": count[w], "bigram_share_of_mean_delta": big[w] / n_obj,
             "unigram_share_of_mean_delta": uni[w] / n_obj} for w in count]
    rows.sort(key=lambda r: r["unigram_share_of_mean_delta"])
    stroke_sum = sum(r["unigram_share_of_mean_delta"] for r in rows if r["target"] in STROKES)
    return {"per_target": rows, "unigram_from_stroke_signs": stroke_sum,
            "unigram_total": sum(r["unigram_share_of_mean_delta"] for r in rows),
            "bigram_total": sum(r["bigram_share_of_mean_delta"] for r in rows)}


def merged_strokes():
    """Rerun T1 (observed value only) with stroke signs merged into one symbol."""
    def merge_unit(u):
        f = lambda s: "STK" if s in STROKES else s
        ev = [(f(a), f(b)) for a, b in u["events"]]
        return dict(u, events=ev, ss=[(a, b) for a, b in ev if a != A.BOS and b != A.EOS])
    orig_window = A.window_unit

    def window_merged(u, k, tag):
        return merge_unit(orig_window(u, k, tag))
    A.window_unit = window_merged
    try:
        objs = [[merge_unit(u) for u in o] for o in A.tests()["T1"][1]]
        res = A.evaluate_loo(objs, random.Random(f"{A.SEED_MATCH}-T1-merged"))
    finally:
        A.window_unit = orig_window
    return A.aggregate(res)


def frequencies():
    objs = A.tests()["T1"][1]
    rc = Counter(t for o in objs for u in o for t in A.C.known_signs(u["text"]))
    pc = Counter(t for p in A.data()["pool"] for t in p["tokens"])
    rn, pn = sum(rc.values()), sum(pc.values())
    rows = [{"sign": s, "round_tokens": rc[s], "round_share": rc[s] / rn, "pool_share": pc[s] / pn}
            for s in rc]
    rows.sort(key=lambda r: -r["round_tokens"])
    strokes_round = sum(rc[s] for s in rc if s in STROKES) / rn
    strokes_pool = sum(pc[s] for s in pc if s in STROKES) / pn
    return {"round_tokens": rn, "pool_tokens": pn, "top_round_signs": rows[:20],
            "stroke_share_round": strokes_round, "stroke_share_pool": strokes_pool,
            "share_740_round": rc["740"] / rn, "share_740_pool": pc["740"] / pn}


def shared_pair():
    """E4: unique texts in the whole export containing the reading-order pair 140-592, which links
    two Mohenjo-daro circular seals in the T1 per-object table."""
    seen, hits = set(), []
    for f in A.data()["faces"]:
        code = f["face"]["text_code_visual_ltr"]
        if code in seen:
            continue
        seen.add(code)
        if any((a, b) == ("140", "592") for ln in f["text"]["lines"] for a, b in zip(ln, ln[1:])):
            hits.append({"record_id": f["record_id"], "site": f["face"]["site"],
                         "type": f["face"]["object_type"], "cisi": f["face"]["source_cisi"]})
    faces_592 = sum(1 for f in A.data()["faces"] if "592" in A.C.known_signs(f["text"]))
    return {"unique_texts_with_pair": hits, "faces_with_592": faces_592}


def main():
    out = {"label": "exploratory, computed after the T1-T3 outcomes", "E1": contributions(),
           "E2_strokes_merged": merged_strokes(), "E3": frequencies(), "E4": shared_pair()}
    (A.RUN / "exploratory.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    e1 = out["E1"]
    print("E1 totals", round(e1["bigram_total"], 3), round(e1["unigram_total"], 3),
          "strokes", round(e1["unigram_from_stroke_signs"], 3))
    for r in e1["per_target"][:12]:
        print(r)
    print("E2", out["E2_strokes_merged"])
    e3 = out["E3"]
    print("E3 strokes", round(e3["stroke_share_round"], 3), round(e3["stroke_share_pool"], 3),
          "740", round(e3["share_740_round"], 3), round(e3["share_740_pool"], 3))
    for r in e3["top_round_signs"][:12]:
        print(r)


if __name__ == "__main__":
    main()
