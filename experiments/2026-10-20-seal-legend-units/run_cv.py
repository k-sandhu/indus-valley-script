"""Q-0028: train the line-break model on catalogue divisions and score it on held-out faces.

Usage: python -P experiments/2026-10-20-seal-legend-units/run_cv.py --run run-2026-10-20

Writes bench reference and prediction files under data/raw/2026-10-20-seal-legend-units/<run>/,
scores every method with `python -m bench segmentation`, and writes the package summary
<run>/cv-summary.json. PROTOCOL.md sections 3 and 4.
"""
import argparse
import collections
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import legend_units as U  # noqa: E402
from bench import segmentation as BS  # noqa: E402

UNSUPERVISED = ["branching_entropy", "greedy_ngram", "dp_unigram"]
BOOT = 2000


def bench_score(refs, preds, out_json, raw_dir, name):
    ref_path = raw_dir / f"{name}-references.jsonl"
    pred_path = raw_dir / f"{name}-predictions.jsonl"
    U.write_jsonl(ref_path, refs)
    U.write_jsonl(pred_path, preds)
    cmd = [sys.executable, "-m", "bench", "segmentation", "--references", str(ref_path),
           "--predictions", str(pred_path), "--out", str(out_json)]
    subprocess.run(cmd, check=True, cwd=U.ROOT, stdout=subprocess.DEVNULL)
    return json.loads(Path(out_json).read_text(encoding="utf-8"))


def bootstrap(per_face, comps, keys, seed):
    """Component bootstrap of pooled J for each method key, and paired differences."""
    rng = random.Random(seed)
    groups = collections.defaultdict(list)
    for i, c in enumerate(comps):
        groups[c].append(i)
    glist = list(groups)
    draws = {k: [] for k in keys}
    for _ in range(BOOT):
        idx = [i for g in (rng.choice(glist) for _ in glist) for i in groups[g]]
        for k in keys:
            draws[k].append(U.pooled_j([per_face[k][i] for i in idx])["j"])
    return draws


def rel(path):
    try:
        return str(Path(path).relative_to(U.ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def q(xs, p):
    xs = sorted(x for x in xs if x == x)
    return xs[min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--sweeps", type=int, default=2000)
    args = ap.parse_args()
    out_dir = U.PKG / args.run
    raw_dir = U.RAW / args.run / "indus"
    (out_dir / "bench").mkdir(parents=True, exist_ok=False)
    raw_dir.mkdir(parents=True, exist_ok=False)

    texts, faces, excluded, _ = U.load_inputs()
    H = U.held_components(texts)
    build = [d for d in texts if d["component"] not in H]
    faces_h = [f for f in faces if f["component"] in H]
    faces = [f for f in faces if f["component"] not in H]
    stats = U.Stats((d["text"], d["component"]) for d in build)

    # features for each face and order, with the face's own component removed
    for f in faces:
        with stats.without(f["component"]):
            for o in ("forward", "reverse"):
                t = f[o]["text"]
                f[o]["X"] = stats.text_features(t)
                f[o]["Z"] = [U.layout(len(t), i) for i in range(1, len(t))]

    def training_obs(fs):
        obs, lab = [], []
        for f in fs:
            orders = [(f["order"], 1.0)] if f["order"] else [("forward", 0.5), ("reverse", 0.5)]
            for o, w in orders:
                for c in f[o]["cuts"]:
                    obs.append((f[o]["X"], f[o]["Z"], c - 1, w))
                lab.append((o, {c - 1 for c in f[o]["cuts"]}, w, f))
        return obs, lab

    preds = {o: {} for o in ("forward", "reverse")}
    scores = {o: {} for o in ("forward", "reverse")}
    layout_pred = {o: {} for o in ("forward", "reverse")}
    fold_models = []
    for k in range(U.FOLDS):
        train = [f for f in faces if f["fold"] != k]
        test = [f for f in faces if f["fold"] == k]
        obs, lab = training_obs(train)
        m = U.BreakModel().fit(obs)
        m.choose_threshold([(m.unit_scores(f[o]["X"]), chosen, w) for o, chosen, w, f in lab])
        fold_models.append({"fold": k, "train_faces": len(train), "test_faces": len(test), **m.to_json()})
        for f in test:
            for o in ("forward", "reverse"):
                X, Z = f[o]["X"], f[o]["Z"]
                preds[o][f["record_id"]] = m.cuts(X)
                scores[o][f["record_id"]] = m.unit_scores(X).tolist()
                lay = np.asarray(Z) @ m.w_layout
                layout_pred[o][f["record_id"]] = [int(np.argmax(lay)) + 1]

    # unsupervised methods run on the build corpus plus every joined face in one order
    corpus = [d["text"] for d in build]
    unsup = {o: {} for o in ("forward", "reverse")}
    for o in ("forward", "reverse"):
        joined = [f[o]["text"] for f in faces]
        for method in UNSUPERVISED:
            p = BS.predict(corpus + joined, method, args.sweeps)[len(corpus):]
            unsup[o][method] = {f["record_id"]: cuts for f, cuts in zip(faces, p)}

    methods = ["supervised", "layout_only"] + UNSUPERVISED + ["all_boundaries", "no_boundaries"]

    def method_cuts(method, o, f):
        if method == "supervised":
            return preds[o][f["record_id"]]
        if method == "layout_only":
            return layout_pred[o][f["record_id"]]
        if method == "all_boundaries":
            return list(range(1, len(f[o]["text"])))
        if method == "no_boundaries":
            return []
        return unsup[o][method][f["record_id"]]

    sets = {"plate_order": [(f, f["order"]) for f in faces if f["order"]],
            "forward": [(f, "forward") for f in faces],
            "reverse": [(f, "reverse") for f in faces]}
    summary = {"inputs": {"faces_file_sha256": U.sha256(U.FACES), "clean_file_sha256": U.sha256(U.CLEAN),
                          "protocol_sha256": U.sha256(U.PKG / "PROTOCOL.md"),
                          "audit_files": {p.name: U.sha256(p) for p in sorted(U.AUDIT.glob("verdicts-*.tsv"))}},
               "faces": {"usable": len(faces), "excluded": excluded, "held_set_components_excluded": len(faces_h),
                         "with_plate_order": len(sets["plate_order"]),
                         "plate_order_forward": sum(o == "forward" for f, o in sets["plate_order"]),
                         "divisions": sum(len(f["forward"]["cuts"]) for f in faces),
                         "by_type": dict(collections.Counter(f["type"] for f in faces)),
                         "by_site": dict(collections.Counter(f["site"] for f in faces))},
               "build_corpus_texts": len(build), "held_components": len(H),
               "fold_models": fold_models, "sets": {}}
    per_face_all = {}
    for name, items in sets.items():
        if not items:
            continue
        refs = [{"id": f["record_id"], "length": len(f[o]["text"]), "boundaries": f[o]["cuts"], "complete": False}
                for f, o in items]
        per_face = {}
        res = {"faces": len(items), "methods": {}}
        for method in methods:
            pr = [{"id": f["record_id"], "boundaries": method_cuts(method, o, f)} for f, o in items]
            bench_out = out_dir / "bench" / f"{name}-{method}.json"
            b = bench_score(refs, pr, bench_out, raw_dir, f"{name}-{method}")
            per_face[method] = [U.j_counts(f[o]["cuts"], method_cuts(method, o, f), len(f[o]["text"]))
                                for f, o in items]
            sc = b["scores"]
            res["methods"][method] = {"bench_output": rel(bench_out),
                                      "boundary_recall": sc["boundary_recall"],
                                      "boundary_rate_elsewhere": sc["boundary_rate_elsewhere"],
                                      "j": sc["boundary_recall"] - sc["boundary_rate_elsewhere"],
                                      "hits": sc["hits"], "required": sc["required_boundaries"]}
        comps = [f["component"] for f, o in items]
        draws = bootstrap(per_face, comps, methods, seed=f"{U.SEED}:{name}")
        for method in methods:
            res["methods"][method]["j_ci95"] = [q(draws[method], 0.025), q(draws[method], 0.975)]
        res["paired_difference_supervised_minus"] = {}
        for method in methods:
            if method == "supervised":
                continue
            d = [a - b for a, b in zip(draws["supervised"], draws[method])]
            res["paired_difference_supervised_minus"][method] = {
                "point": res["methods"]["supervised"]["j"] - res["methods"][method]["j"],
                "ci95": [q(d, 0.025), q(d, 0.975)], "share_of_draws_above_zero": sum(x > 0 for x in d) / len(d)}
        aucs = [U.auc_within(scores[o][f["record_id"]], {c - 1 for c in f[o]["cuts"]}) for f, o in items]
        aucs = [a for a in aucs if a is not None]
        res["supervised_within_face_auc"] = {"faces": len(aucs), "mean": sum(aucs) / len(aucs) if aucs else None}
        res["supervised_cuts_per_position"] = (sum(len(preds[o][f["record_id"]]) for f, o in items)
                                              / sum(len(f[o]["text"]) - 1 for f, o in items))
        summary["sets"][name] = res
        per_face_all[name] = (items, per_face)

    # conservative set: each face in the order less favourable to the scored method
    cons = {"faces": len(faces), "methods": {}}
    for method in methods:
        rows = []
        for f in faces:
            cand = [U.j_counts(f[o]["cuts"], method_cuts(method, o, f), len(f[o]["text"])) for o in ("forward", "reverse")]
            rows.append(min(cand, key=lambda r: (r["hits"] / r["required"]) - (r["other_cuts"] / r["other_slots"] if r["other_slots"] else 0)))
        cons["methods"][method] = U.pooled_j(rows)
        cons["methods"][method]["_rows"] = rows
    comps = [f["component"] for f in faces]
    draws = bootstrap({m: cons["methods"][m]["_rows"] for m in methods}, comps, methods, seed=f"{U.SEED}:conservative")
    for method in methods:
        cons["methods"][method]["j_ci95"] = [q(draws[method], 0.025), q(draws[method], 0.975)]
        del cons["methods"][method]["_rows"]
    cons["paired_difference_supervised_minus"] = {
        m: {"point": cons["methods"]["supervised"]["j"] - cons["methods"][m]["j"],
            "ci95": [q([a - b for a, b in zip(draws["supervised"], draws[m])], 0.025),
                     q([a - b for a, b in zip(draws["supervised"], draws[m])], 0.975)]}
        for m in methods if m != "supervised"}
    summary["sets"]["conservative"] = cons

    # descriptive: J by plate layout class on the plate-order set
    by_layout = collections.defaultdict(list)
    if "plate_order" in per_face_all:
        items, per_face = per_face_all["plate_order"]
        for (f, o), r in zip(items, per_face["supervised"]):
            by_layout[(f["audit"] or {}).get("layout", "none")].append(r)
    summary["plate_order_supervised_by_layout"] = {k: {"faces": len(v), **U.pooled_j(v)} for k, v in by_layout.items()}

    primary = "plate_order" if len(sets["plate_order"]) >= 25 else "conservative"
    s = summary["sets"][primary]["methods"]["supervised"]
    dp = summary["sets"][primary]["paired_difference_supervised_minus"]["dp_unigram"]
    summary["decision"] = {
        "primary_set": primary,
        "margin_rule": "pooled held-out J >= 0.25 and bootstrap 2.5% quantile > 0.10",
        "margin_pass": bool(s["j"] >= 0.25 and s["j_ci95"][0] > 0.10),
        "improvement_rule": "J(supervised) - J(dp_unigram) > 0 with bootstrap 2.5% quantile > 0",
        "improvement_pass": bool(dp["point"] > 0 and dp["ci95"][0] > 0)}
    U.write_json(out_dir / "cv-summary.json", summary)
    print(json.dumps(summary["decision"], indent=1))
    for name, res in summary["sets"].items():
        print(name, {m: round(v["j"], 3) for m, v in res["methods"].items()})


if __name__ == "__main__":
    main()
