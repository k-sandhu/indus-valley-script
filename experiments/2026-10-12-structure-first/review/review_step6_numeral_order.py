"""Adversarial review, step 6 supplement: does the Ur III numeral-order calibration fail because
of how the value is built?

Usage: python -X utf8 review_step6_numeral_order.py --out <new dir under data/raw/2026-10-12-structure-first/>

The frozen run takes the leading digit of each Ur III numeral token, so 1(u) = 10, 1(diš) = 1
and 1(barig) (a capacity unit) all have value 1. Here the frozen numeral_order function is
rerun with the value written as digit plus unit, and the IVS run with value = stroke family
plus count for symmetry.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step6-language"))
import common  # noqa: E402
import analyze_step6 as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    nrng = np.random.default_rng(common.SEED + 607)
    recs = common.read_jsonl(common.BRONZE)
    ur3 = [tuple(zip(r["words"], r["gold"])) for r in recs if r["corpus"] == "sumerian" and r["kind"] == "whole_tablet"]
    is_num = lambda u: u[1] == "NUMBER" and u[0].split("(")[0].isdigit()
    digit = lambda u: int(u[0].split("(")[0])
    digit_unit = lambda u: u[0].split(")")[0] + ")" if "(" in u[0] else u[0]
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    ivs = [d["text"] for d in common.load_clean()]
    ivs_num = lambda u: bool(coding.get(u) and coding[u]["base"] in ("B001", "B031") and coding[u]["count"])
    res = {"ur3_digit_frozen_definition": A.numeral_order(ur3, is_num, digit, nrng),
           "ur3_digit_and_unit": A.numeral_order(ur3, is_num, digit_unit, nrng),
           "ivs_family_and_count": A.numeral_order(ivs, ivs_num, lambda u: f"{coding[u]['base']}:{coding[u]['count']}", nrng)}
    print(json.dumps(res, indent=1))
    (out / "summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
