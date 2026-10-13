"""Exploratory review analysis: split-half reliability of Shot B's per-sign effects.

Correlates each per-sign effect on the confirmation half (frozen output) with the same
effect computed by Shot B's frozen code on the discovery half with its real withheld
fields (review/shot-b-discovery-runs/discovery-real.json, written by shot_b_review.py).
A measure whose per-sign values do not agree between halves cannot carry a class contrast.
Also counts the preservation state of the confirmation seal faces with positive dimensions,
which Shot B's size units use without a preservation filter.
Output: review/shot-b-reliability.json.
"""
import json

import numpy as np

import collections

from review_common import HERE, PKG, write_json, STATUS, load_confirmation_direct


def main():
    conf = json.loads((PKG / "shot-b-reading/confirmation/results.json").read_text(encoding="utf-8"))["per_sign_effects"]
    disc = json.loads((HERE / "shot-b-discovery-runs/discovery-real.json").read_text(encoding="utf-8"))["per_sign_effects"]
    out = {"status": STATUS}
    for k in conf:
        common = [s for s in conf[k] if s in disc.get(k, {})]
        if len(common) < 6:
            out[k] = {"signs": len(common), "pearson": None}
            continue
        a = np.array([conf[k][s] for s in common])
        b = np.array([disc[k][s] for s in common])
        rank = lambda x: np.argsort(np.argsort(x))
        out[k] = {"signs": len(common), "pearson": round(float(np.corrcoef(a, b)[0, 1]), 3),
                  "spearman": round(float(np.corrcoef(rank(a), rank(b))[0, 1]), 3)}
    pres = collections.Counter()
    for r in load_confirmation_direct():
        if not r["object_type"].startswith("SEAL"):
            continue
        m = r["metadata"]
        try:
            h, v = float(m["horizontal(mm)"]), float(m["vertical(mm)"])
        except (TypeError, ValueError):
            continue
        if h > 0 and v > 0:
            pres[m.get("preservation")] += 1
    out["confirmation_sized_seal_faces_by_preservation"] = dict(pres.most_common())
    write_json("shot-b-reliability.json", out)
    print(out)


if __name__ == "__main__":
    main()
