"""Label-permutation control for the held-out J (added after the protocol; exploratory).

Usage: python -P experiments/2026-10-20-seal-legend-units/label_permutation.py --run run-2026-10-20 --perms 200

Each permutation moves every face's divisions to positions drawn at random within the face
(keeping their number), refits the model fold by fold exactly as run_cv.py does, and records the
pooled held-out J on the plate-order and forward sets. The observed J is compared with this
distribution. No bench call is made; J is computed with the same counting rules.
"""
import argparse
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402


def cv_j(faces, cutsets):
    """cutsets[rid][order] -> list of cuts used as labels and as reference."""
    rows = {"plate_order": [], "forward": []}
    for k in range(U.FOLDS):
        train = [f for f in faces if f["fold"] != k]
        test = [f for f in faces if f["fold"] == k]
        obs, lab = [], []
        for f in train:
            orders = [(f["order"], 1.0)] if f["order"] else [("forward", 0.5), ("reverse", 0.5)]
            for o, w in orders:
                cuts = cutsets[f["record_id"]][o]
                for c in cuts:
                    obs.append((f[o]["X"], f[o]["Z"], c - 1, w))
                lab.append((f[o]["X"], {c - 1 for c in cuts}, w))
        m = U.BreakModel().fit(obs)
        m.choose_threshold([(m.unit_scores(X), ch, w) for X, ch, w in lab])
        for f in test:
            for name, o in (("plate_order", f["order"]), ("forward", "forward")):
                if not o:
                    continue
                gold = cutsets[f["record_id"]][o]
                rows[name].append(U.j_counts(gold, m.cuts(f[o]["X"]), len(f[o]["text"])))
    return {k: U.pooled_j(v)["j"] for k, v in rows.items() if v}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--perms", type=int, default=200)
    args = ap.parse_args()
    out = U.PKG / args.run / "label-permutation.json"
    if out.exists():
        raise SystemExit("exists")
    texts, faces, _, _ = U.load_inputs()
    H = U.held_components(texts)
    build = [d for d in texts if d["component"] not in H]
    faces = [f for f in faces if f["component"] not in H]
    stats = U.Stats((d["text"], d["component"]) for d in build)
    for f in faces:
        with stats.without(f["component"]):
            for o in ("forward", "reverse"):
                t = f[o]["text"]
                f[o]["X"] = stats.text_features(t)
                f[o]["Z"] = [U.layout(len(t), i) for i in range(1, len(t))]
    observed = cv_j(faces, {f["record_id"]: {o: f[o]["cuts"] for o in ("forward", "reverse")} for f in faces})
    rng = random.Random(f"{U.SEED}:label-permutation")
    null = {"plate_order": [], "forward": []}
    for _ in range(args.perms):
        cs = {}
        for f in faces:
            L = len(f["forward"]["text"])
            k = len(f["forward"]["cuts"])
            cs[f["record_id"]] = {o: sorted(rng.sample(range(1, L), k)) for o in ("forward", "reverse")}
        for k, v in cv_j(faces, cs).items():
            null[k].append(v)
    res = {"perms": args.perms, "observed_j": observed, "null": {}}
    for k, v in null.items():
        if not v:
            continue
        res["null"][k] = {"mean": float(np.mean(v)), "q95": float(np.quantile(v, 0.95)), "max": float(np.max(v)),
                          "p_value_one_sided": (1 + sum(x >= observed[k] for x in v)) / (1 + len(v))}
    U.write_json(out, res)
    print(U.json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
