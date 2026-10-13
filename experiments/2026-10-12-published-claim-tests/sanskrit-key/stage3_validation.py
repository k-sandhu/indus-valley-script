"""Validation of the order-gain measure on real words (Amendment 1, item 2).

Scores random Monier-Williams headwords, the distinct word forms of the published glossing, and the
published reading skeletons by length, under the Stage 3 model.
"""
import csv
import json
import os
import re
from collections import defaultdict

import numpy as np

import stage3_fit as s3
from common import GLOSSING_CSV, HERE, MW_TXT, RAW, encode, slp1_skeleton


def main():
    s3.load_model()
    rng = np.random.default_rng(5)
    pat = re.compile(r"<k1>([^<]+)<k2>")
    hw = set()
    with open(MW_TXT, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<L>"):
                m = pat.search(line)
                if m:
                    hw.add(m.group(1))
    hw = sorted(hw)
    sel = [hw[i] for i in rng.choice(len(hw), 5000, replace=False)]
    out = {"mw_random_headwords_5000": s3._score_skeletons([tuple(encode(slp1_skeleton(w))) for w in sel])}
    with open(GLOSSING_CSV, encoding="utf-8") as f:
        forms = sorted({g["form"] for g in csv.DictReader(f)})
    out["glossing_distinct_forms"] = s3._score_skeletons([tuple(encode(slp1_skeleton(w))) for w in forms])
    by = defaultdict(list)
    with open(os.path.join(RAW, "sanskrit-key", "stage0_rows.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["reading_skeleton"]:
                by[min(len(r["reading_skeleton"]), 8)].append(tuple(encode(r["reading_skeleton"])))
    out["published_readings_by_skeleton_length"] = {
        ("8+" if L == 8 else str(L)): s3._score_skeletons(v) for L, v in sorted(by.items())}
    with open(os.path.join(HERE, "stage3", "validation.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: (v["G"] if "G" in v else {kk: round(vv["G"], 3) for kk, vv in v.items()})
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
