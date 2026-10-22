"""Frozen scorer for the birth-star predictions on fresh seal texts (PREDICTIONS.json, SCORING.md).

Input: a JSONL file of faces in the schema of data/normalized/lipi_observed_faces.jsonl
(signs_reading_rtl, object_type, clean_rtl_singleline, source_cisi, site), each with a
`fresh_source` field naming the publication and page. Faces already in the pinned corpus, by
CISI number or by identical full text, are refused and counted. Only seal faces score.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import birthstar as bs  # noqa: E402

PINNED = ROOT / "data/normalized/lipi_observed_faces.jsonl"
PINNED_SHA256 = "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db"
REFERENCE = HERE / "frozen-reference.json"
MIN_RUNS = 40
DRAWS = 9999
SEED = 20261021


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cisi_key(value):
    m = re.match(r"^\s*([A-Za-z]+)\s*-\s*(\d+)", str(value or ""))
    return f"{m.group(1).upper()}-{int(m.group(2))}" if m else None


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def fresh_legends(rows, pinned_rows):
    pinned_cisi = {cisi_key(r.get("source_cisi")) for r in pinned_rows} - {None}
    pinned_texts = {tuple(bs.norm(s) for s in r["signs_reading_rtl"]) for r in pinned_rows}
    kept, refused = [], Counter()
    for r in rows:
        key = cisi_key(r.get("source_cisi"))
        seq = tuple(bs.norm(s) for s in r.get("signs_reading_rtl", []))
        if key and key in pinned_cisi:
            refused["cisi_in_pinned_corpus"] += 1
        elif seq in pinned_texts:
            refused["full_text_in_pinned_corpus"] += 1
        elif not r.get("fresh_source"):
            refused["no_fresh_source"] += 1
        else:
            kept.append(r)
    return bs.legends(kept), refused


def reference_range(counts, n, key, draws=999, seed=SEED):
    """95% range of a statistic for samples of size n from the frozen Brahmi asterism class.

    Samples are drawn with replacement: the Brahmi counts stand for the generating distribution
    of a birth-star naming system, and a fresh sample is a new draw from it.
    """
    tokens = [k for k, v in counts.items() for _ in range(v)]
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        sample = rng.choice(np.array(tokens, dtype=object), size=n, replace=True)
        v = bs.stats(list(sample)).get(key)
        if v is not None:
            vals.append(v)
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


PROFILE_KEYS = ("normalised_entropy", "top_share")


def profile_check(tokens, counts, seed=SEED):
    """Compare a fish-run sample with the Brahmi class at n* = min(sample size, Brahmi size).

    A larger fish sample is subsampled without replacement to n* 999 times and the median of each
    statistic is used; the Brahmi range is the 95% range of bootstrap samples of size n*.
    """
    n_star = min(len(tokens), sum(counts.values()))
    rng = np.random.default_rng(seed + 3)
    if len(tokens) > n_star:
        vals = {k: [] for k in PROFILE_KEYS}
        arr = np.array(tokens, dtype=object)
        for _ in range(999):
            st = bs.stats(list(rng.choice(arr, size=n_star, replace=False)))
            for k in PROFILE_KEYS:
                vals[k].append(st[k])
        profile = {k: float(np.median(v)) for k, v in vals.items()}
    else:
        st = bs.stats(tokens)
        profile = {k: st[k] for k in PROFILE_KEYS}
    ranges = {k: reference_range(counts, n_star, k, seed=seed) for k in PROFILE_KEYS}
    return profile, ranges, n_star


def score(legs, ref, table):
    fish, strokes = bs.families(table)
    out = {"fresh_seal_legends": len(legs)}
    t0_fish, t0_open, _ = bs.collect(legs, fish, strokes, "T0", False)
    t1_fish, t1_open, _ = bs.collect(legs, fish, strokes, "T1", False)
    out["name_position_fish_runs"] = len(t0_fish)
    if len(t0_fish) < MIN_RUNS:
        out["scorable"] = False
        out["reason"] = f"fewer than {MIN_RUNS} name-position fish runs"
        return out
    out["scorable"] = True
    preds = {}
    # P1, direction-note N1 as written, on prefix-plus-run compounds.
    s1 = bs.stats(t1_fish)
    m1 = bs.matched(t1_open, len(t1_fish), DRAWS, SEED) if len(t1_open) > len(t1_fish) else None
    open_share = float(np.mean(m1["chao1"] > 45)) if m1 is not None else None
    preds["P1_literal_N1"] = {"chao1": s1["chao1"], "S": s1["S"], "N": s1["N"],
                              "matched_opening_chao1_above_45_share": open_share,
                              "pass": bool(24 <= s1["chao1"] <= 45 and open_share is not None and open_share >= 0.95)}
    # P2, closure: fresh fish runs rarely fall outside the frozen discovery inventory.
    inventory = set(ref["discovery_T0_inventory"])
    novel = sum(t not in inventory for t in t0_fish)
    share = novel / len(t0_fish)
    preds["P2_closure"] = {"novel_tokens": novel, "tokens": len(t0_fish), "novel_share": share,
                           "wilson95": bs.wilson(novel, len(t0_fish)), "pass": share <= 0.15}
    # P3, profile within the Brahmi asterism range, compared at the smaller of the two sizes.
    fresh_profile, ranges, n_star = profile_check(t0_fish, ref["brahmi_asterism_counts"])
    inside = {k: ranges[k][0] <= fresh_profile[k] <= ranges[k][1] for k in ranges}
    preds["P3_brahmi_profile"] = {"n_compared": n_star, "fresh": fresh_profile, "brahmi_95_range": ranges,
                                  "brahmi_variant": ref["brahmi_variant"], "inside": inside, "pass": all(inside.values())}
    # P4, pan-regional stability of the dominant runs.
    top = ref["discovery_T0_top4"]
    cover = sum(t in top for t in t0_fish) / len(t0_fish)
    preds["P4_stable_dominant_runs"] = {"top4": top, "coverage": cover, "pass": 0.50 <= cover <= 0.85}
    # P5, direction-note N3 as written.
    signs = Counter(c for lg in legs for u in bs.units(lg["seq"], fish, strokes)
                    if u["kind"] == "fish" and not u["final"] for c in u["run"])
    mp = bs.modifier_pairs(signs, table)
    three = [m for m, v in mp["contrasts"].items() if v["bases"] == 3]
    preds["P5_literal_N3"] = {"contrasts_with_three_bases": three, "detail": mp,
                              "pass": len(three) == 1 and mp["contrasts"][three[0]]["all_ratios_within_third_to_three"]}
    out["predictions"] = preds
    out["joint_credence"] = joint(preds)
    return out


def joint(p):
    """The frozen joint credence rule for C-0010 (see PREDICTIONS.json)."""
    if not p["P2_closure"]["pass"]:
        value = 0.005
    else:
        passes = p["P3_brahmi_profile"]["pass"] + p["P4_stable_dominant_runs"]["pass"]
        value = {2: 0.06, 1: 0.03, 0: 0.01}[passes]
    if p["P1_literal_N1"]["pass"] and p["P5_literal_N3"]["pass"] and p["P2_closure"]["pass"]:
        value = min(value + 0.04, 0.12)
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    if sha256(PINNED) != PINNED_SHA256:
        raise SystemExit("The pinned corpus changed; freshness cannot be checked against it")
    ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
    legs, refused = fresh_legends(read_jsonl(args.fresh), read_jsonl(PINNED))
    result = {"fresh_input": str(args.fresh), "fresh_sha256": sha256(args.fresh), "refused": dict(refused),
              "scorer_sha256": sha256(__file__), "library_sha256": sha256(HERE / "birthstar.py"),
              "reference_sha256": sha256(REFERENCE), "coding_sha256": sha256(bs.CODING),
              "sites": dict(Counter(lg["site"] for lg in legs))}
    result.update(score(legs, ref, bs.coding()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps({k: result[k] for k in ("refused", "fresh_seal_legends", "name_position_fish_runs", "scorable")}, indent=2))


if __name__ == "__main__":
    main()
