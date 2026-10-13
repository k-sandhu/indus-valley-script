"""Adversarial review, step 1 supplement: gain of the class model with no grouping at all.

Usage: python -X utf8 review_step1_identity.py --out <new dir under data/raw/2026-10-12-structure-first/>

With every code in its own class, the frozen class model reduces to an interpolation of the
Kneser-Ney bigram with an add-0.5 bigram. Its gain over the baseline is the part of every
reported "gain" that does not depend on grouping. The random-partition null controls for this
part; the reported gains do not subtract it.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step1-signs"))
import common  # noqa: E402
import analyze_step1 as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    items = common.load_clean()
    texts = [d["text"] for d in items]
    folds = [d["fold"] for d in items]
    comp_idx = {c: i for i, c in enumerate(sorted({d["component"] for d in items}))}
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    vocab = sorted(set(coding) | {s for t in texts for s in t})
    data = A.Data(texts, folds, vocab)
    ev = A.Evaluator(data, [comp_idx[d["component"]] for d in items])
    cls, ncls = A.class_array(data, {c: c for c in vocab})
    bits, lams, _ = ev.evaluate(cls, ncls)
    res = {"identity_partition_gain_bits": ev.base_bits - bits, "lambda_by_fold": lams}
    print(json.dumps(res))
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
