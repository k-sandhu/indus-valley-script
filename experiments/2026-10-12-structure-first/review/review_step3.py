"""Adversarial review, step 3 line breaks: independence of faces and edge effects.

Usage: python -X utf8 review_step3.py --out <new dir under data/raw/2026-10-12-structure-first/>

1. The frozen per-face rows are re-derived with the frozen helpers and the sign test is
   repeated (a) with identical faces counted once and (b) without faces that have a line
   made only of stroke-numeral codes (B001/B031), a layout that recurs in one seal series.
2. Shifted-break null: for each two-line face, the same line/straddle statistic is computed
   for every other cut position of the same joined text. If the observed advantage of lines
   comes from the fact that lines contain text edges, other cuts do as well.
3. Virtual breaks: clean single-line texts of the same total length receive a break at the
   same position as a real two-line face. Lines are then text prefixes and suffixes with no
   scribal break.
Only frozen helpers (lines_of, contains) are imported; nothing in the run directories is written.
"""
import argparse
import collections
import json
import random
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step3-segmentation"))
import common  # noqa: E402
from linebreaks import contains, lines_of  # noqa: E402


def sign_p(better, worse):
    n = better + worse
    return min(1.0, 2 * sum(comb(n, k) for k in range(max(better, worse), n + 1)) / 2 ** n) if n else None


def two_line_stats(A, B, ref, fam, skip_text=None):
    """Line and straddle found rates for one break, joined in the order A then B."""
    r = [x for x in ref if x[0] != skip_text] if skip_text is not None else ref
    lf = [contains(r, L, fam) for L in (A, B) if len(L) >= 2]
    joined, cut = A + B, len(A)
    sf = []
    for m in {len(A), len(B)}:
        if m < 2:
            continue
        for i in range(max(0, cut - m + 1), min(cut, len(joined) - m + 1)):
            if i < cut < i + m:
                sf.append(contains(r, joined[i:i + m], fam))
    if not lf or not sf:
        return None
    return sum(lf) / len(lf), sum(sf) / len(sf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--virtual", type=int, default=10)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    clean = common.load_clean()
    ref = [(d["text"], d["families"]) for d in clean]
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    frozen = json.loads((common.RAW / "step3-linebreak-faces.json").read_text(encoding="utf-8"))
    faces = {f["record_id"]: f for f in common.read_jsonl(common.FACES)}
    res = {}

    # 1. independence and the stroke-line series
    def numeral_line(ls):
        return any(all(coding.get(s, {}).get("base") in ("B001", "B031") for s in L) for L in ls)

    seen = set()
    variants = {"frozen": [], "identical_faces_once": [], "without_numeral_only_lines": []}
    for r in frozen:
        f = faces[r["face"]]
        ls = tuple(lines_of(f))
        sign = (r["line_rate"] > r["straddle_rate_best_order"]) - (r["line_rate"] < r["straddle_rate_best_order"])
        variants["frozen"].append(sign)
        if ls not in seen:
            variants["identical_faces_once"].append(sign)
        seen.add(ls)
        if not numeral_line(ls):
            variants["without_numeral_only_lines"].append(sign)
    res["sign_tests_best_order"] = {}
    for k, v in variants.items():
        b, w = v.count(1), v.count(-1)
        res["sign_tests_best_order"][k] = {"faces": len(v), "line_higher": b, "straddle_higher": w,
                                          "ties": v.count(0), "p_two_sided": sign_p(b, w)}
    sites = collections.Counter(faces[r["face"]]["site"] for r in frozen if numeral_line(lines_of(faces[r["face"]])))
    res["numeral_only_line_faces_by_site"] = dict(sites)
    print(json.dumps(res, indent=0), flush=True)

    # 2. shifted-break null on two-line faces, each line order separately
    two = [(r["face"], lines_of(faces[r["face"]])) for r in frozen if len(lines_of(faces[r["face"]])) == 2]
    shifted = {}
    for order in ("forward", "reverse"):
        rows = []
        for rid, (A, B) in two:
            fam = faces[rid]["object_family_id"]
            first, second = (A, B) if order == "forward" else (B, A)
            joined = first + second
            obs = two_line_stats(first, second, ref, fam)
            if obs is None:
                continue
            alt = []
            for c in range(1, len(joined)):
                if c == len(first):
                    continue
                s = two_line_stats(joined[:c], joined[c:], ref, fam)
                if s is not None:
                    alt.append(s[0] - s[1])
            if not alt:
                continue
            rows.append({"obs": obs[0] - obs[1], "alt": alt})
        frac_above = np.mean([np.mean([r["obs"] > a for a in r["alt"]]) for r in rows])
        frac_below = np.mean([np.mean([r["obs"] < a for a in r["alt"]]) for r in rows])
        obs_sum = sum(r["obs"] for r in rows)
        rng = np.random.default_rng(common.SEED + 303)
        null = np.array([sum(r["alt"][rng.integers(len(r["alt"]))] for r in rows) for _ in range(10000)])
        shifted[order] = {"faces": len(rows), "mean_obs_line_minus_straddle": obs_sum / len(rows),
                          "mean_alt_line_minus_straddle": float(np.mean([np.mean(r["alt"]) for r in rows])),
                          "mean_share_of_other_cuts_with_lower_difference": float(frac_above),
                          "mean_share_of_other_cuts_with_higher_difference": float(frac_below),
                          "p_one_sided_sum_vs_random_other_cut": float((1 + (null >= obs_sum).sum()) / 10001)}
        print(order, json.dumps(shifted[order]), flush=True)
    res["shifted_break_null_two_line_faces"] = shifted

    # 3. virtual breaks in single-line texts with the same total length and cut position
    rng = random.Random(common.SEED + 304)
    by_len = collections.defaultdict(list)
    for d in clean:
        by_len[len(d["text"])].append(d)
    real, virt = [], []
    for rid, (A, B) in two:
        fam = faces[rid]["object_family_id"]
        s = two_line_stats(A, B, ref, fam)
        if s is None:
            continue
        real.append(s)
        pool = by_len.get(len(A) + len(B), [])
        for d in rng.sample(pool, min(args.virtual, len(pool))):
            t = d["text"]
            fams = d["families"]
            vf = next(iter(fams))
            # exclude the text itself and every reference text sharing one of its families
            r2 = [x for x in ref if x[0] != t and not (x[1] & fams)]
            v = two_line_stats(t[:len(A)], t[len(A):], r2, "__none__")
            if v is not None:
                virt.append(v)

    def summ(rows):
        b = sum(a > c for a, c in rows)
        w = sum(a < c for a, c in rows)
        return {"faces": len(rows), "mean_line_rate": float(np.mean([a for a, _ in rows])),
                "mean_straddle_rate_forward_order": float(np.mean([c for _, c in rows])),
                "line_higher": b, "straddle_higher": w, "ties": len(rows) - b - w,
                "share_line_higher_among_decided": b / (b + w) if b + w else None}

    res["virtual_breaks"] = {"real_two_line_faces_forward_order": summ(real),
                             "single_line_texts_same_length_and_cut": summ(virt),
                             "virtual_per_face": args.virtual}
    print(json.dumps(res["virtual_breaks"], indent=0), flush=True)
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
