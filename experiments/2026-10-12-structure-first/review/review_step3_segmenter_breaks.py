"""Adversarial review, step 3: the protocol output "each segmenter's agreement with line breaks".

Usage: python -X utf8 review_step3_segmenter_breaks.py --out <new dir under data/raw/2026-10-12-structure-first/>

The frozen run never computed this. Each frozen segmenter is run on the distinct clean texts
plus the joined multi-line faces used in step 3 (both line orders added as separate texts).
For the joined faces, the rate at which a boundary is placed at a line break is compared with
the segmenter's boundary rate at all other internal positions of the same joined texts.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step3-segmentation"))
import common  # noqa: E402
import segmenters as S  # noqa: E402
from linebreaks import lines_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sweeps", type=int, default=2000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    clean = [d["text"] for d in common.load_clean()]
    frozen = json.loads((common.RAW / "step3-linebreak-faces.json").read_text(encoding="utf-8"))
    faces = {f["record_id"]: f for f in common.read_jsonl(common.FACES)}
    joined, breaks, order = [], [], []
    for r in frozen:
        ls = lines_of(faces[r["face"]])
        for o, seq in (("forward", ls), ("reverse", ls[::-1])):
            t, cuts = [], []
            for L in seq:
                t.extend(L)
                cuts.append(len(t))
            joined.append(tuple(t))
            breaks.append(set(cuts[:-1]))
            order.append(o)
    texts = clean + joined
    segs = {"branching_entropy": S.branching_entropy(texts), "greedy_ngram": S.greedy_ngram(texts),
            "dp_unigram": S.dp_unigram(texts, sweeps=args.sweeps)}
    res = {"clean_texts": len(clean), "joined_faces_per_order": len(frozen)}
    for name, bs in segs.items():
        res[name] = {}
        for o in ("forward", "reverse"):
            at = at_n = other = other_n = 0
            for k, (t, br) in enumerate(zip(joined, breaks)):
                if order[k] != o:
                    continue
                pred = set(bs[len(clean) + k])
                for i in range(1, len(t)):
                    if i in br:
                        at_n += 1
                        at += i in pred
                    else:
                        other_n += 1
                        other += i in pred
            res[name][o] = {"breaks": at_n, "boundary_at_break_rate": at / at_n,
                            "boundary_rate_elsewhere": other / other_n}
        print(name, json.dumps(res[name]), flush=True)
    (out / "summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
