"""Adversarial review, step 2 supplement: test 2d with seal objects as the unit.

Usage: python -X utf8 review_step2_objects.py --out <new dir under data/raw/2026-10-12-structure-first/>

The protocol counts "seal texts ... split by seal field animal" and permutes "field labels
among seals"; the frozen code counts distinct (text, animal) pairs. Here each single-animal
seal object is one unit (hit if any of its texts contains a class-specific n-gram), with the
frozen specificity rule and 10,000 label permutations among objects.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step2-image-text"))
import common  # noqa: E402
import analyze_step2 as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--perms", type=int, default=10000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    faces = common.read_jsonl(common.FACES)
    copper = A.objects(faces, {"TAB:C"})
    seals = A.objects(faces, {"SEAL", "SEAL:S", "SEAL:R", "SEAL:C", "SEAL:CY"})
    class_grams, all_grams = collections.defaultdict(set), collections.defaultdict(set)
    for o in copper.values():
        if not o["labels"]:
            continue
        for t in o["texts"]:
            g = A.ngrams(t, (2, 3))
            for lab in o["labels"]:
                class_grams[lab] |= g
            for x in g:
                all_grams[x] |= o["labels"]
    specific = {lab: {g for g in gs if all_grams[g] == {lab}} for lab, gs in class_grams.items()}
    objs = [(next(iter(o["labels"])), o["texts"]) for o in seals.values() if len(o["labels"]) == 1 and o["texts"]]
    labs = np.array([l for l, _ in objs])
    classes = sorted(c for c in specific if specific[c] and c in set(labs))
    hit = {c: np.array([any(A.ngrams(t, (2, 3)) & specific[c] for t in ts) for _, ts in objs]) for c in classes}

    def stat(lab):
        return sum(int((hit[c] & (lab == c)).sum()) for c in classes)

    rng = np.random.default_rng(common.SEED + 222)
    obs = stat(labs)
    null = np.array([stat(rng.permutation(labs)) for _ in range(args.perms)])
    res = {"seal_objects": len(objs), "shared_classes": classes, "matching_hits": obs,
           "null_mean": float(null.mean()), "p_value": float((1 + (null >= obs).sum()) / (1 + args.perms)),
           "per_class": {c: {"matching_objects": int((labs == c).sum()), "hits_matching": int((hit[c] & (labs == c)).sum()),
                             "hits_other": int((hit[c] & (labs != c)).sum())} for c in classes}}
    print(json.dumps(res, indent=1))
    (out / "summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
