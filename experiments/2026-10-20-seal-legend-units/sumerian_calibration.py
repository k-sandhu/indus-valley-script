"""Readable-script calibration: train the line-break model on Ur III seal line divisions only.

Usage: python -P experiments/2026-10-20-seal-legend-units/sumerian_calibration.py --run run-2026-10-20

The model sees, as in the Indus case, one labelled line division in each of 75 training legends
and no word divisions. Held-out legends are scored against their complete edited word divisions
with `python -m bench segmentation`. PROTOCOL.md section 4.
"""
import argparse
import collections
import hashlib
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

LABELLED_LEGENDS = 75


def load_legends():
    rows = [r for r in U.read_jsonl(U.BRONZE) if r["corpus"] == "sumerian" and r["kind"] == "seal"]
    uf = U.UnionFind()
    seen, out = set(), []
    for r in rows:
        wu, refs = r.get("word_units"), r.get("source_word_refs")
        if not wu or not refs or len(wu) != len(refs) or any(len(w) == 0 for w in wu):
            continue
        units, words, lines = [], [], []
        for w, ref in zip(wu, refs):
            units.extend(w)
            words.append(len(units))
            lines.append(ref.split(".")[1])
        t = tuple(units)
        doc = "D:" + r["document"]
        for a in r.get("aliases", []):
            uf.union(doc, "A:" + a)
        uf.union(doc, "T:" + "␟".join(t))
        if len(t) < 2 or t in seen:
            continue
        seen.add(t)
        word_cuts = words[:-1]
        line_cuts = [words[k] for k in range(len(words) - 1) if lines[k] != lines[k + 1]]
        out.append({"id": r["id"], "doc": doc, "text": t, "words": word_cuts, "lines": line_cuts})
    for d in out:
        d["component"] = uf.find(d["doc"])
        d["fold"] = int(hashlib.sha256(f"{U.SEED}:sum:{d['component']}".encode()).hexdigest(), 16) % U.FOLDS
    return out


def run_bench(refs, preds, out_json, raw_dir, name):
    rp, pp = raw_dir / f"{name}-references.jsonl", raw_dir / f"{name}-predictions.jsonl"
    U.write_jsonl(rp, refs)
    U.write_jsonl(pp, preds)
    subprocess.run([sys.executable, "-m", "bench", "segmentation", "--references", str(rp), "--predictions", str(pp),
                    "--out", str(out_json)], check=True, cwd=U.ROOT, stdout=subprocess.DEVNULL)
    return json.loads(Path(out_json).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--sweeps", type=int, default=2000)
    args = ap.parse_args()
    out_dir = U.PKG / args.run / "sumerian"
    raw_dir = U.RAW / args.run / "sumerian"
    out_dir.mkdir(parents=True, exist_ok=False)
    raw_dir.mkdir(parents=True, exist_ok=False)
    legends = load_legends()
    stats = U.Stats((d["text"], d["component"]) for d in legends)
    for d in legends:
        with stats.without(d["component"]):
            d["X"] = stats.text_features(d["text"])
            d["Z"] = [U.layout(len(d["text"]), i) for i in range(1, len(d["text"]))]
    rng = random.Random(f"{U.SEED}:sumerian-labels")
    preds = {"primary": {}, "all_lines": {}}
    models = []
    for k in range(U.FOLDS):
        train = [d for d in legends if d["fold"] != k and d["lines"]]
        test = [d for d in legends if d["fold"] == k]
        chosen = rng.sample(train, min(LABELLED_LEGENDS, len(train)))
        variants = {"primary": [(d, [rng.choice(d["lines"])]) for d in chosen],
                    "all_lines": [(d, d["lines"]) for d in train]}
        for name, lab in variants.items():
            obs = [(d["X"], d["Z"], c - 1, 1.0) for d, cuts in lab for c in cuts]
            m = U.BreakModel().fit(obs)
            m.choose_threshold([(m.unit_scores(d["X"]), {c - 1 for c in cuts}, 1.0) for d, cuts in lab])
            models.append({"fold": k, "variant": name, "labelled_divisions": len(obs), **m.to_json()})
            for d in test:
                preds[name][d["id"]] = m.cuts(d["X"])
    corpus = [d["text"] for d in legends]
    unsup = {m: dict(zip([d["id"] for d in legends], BS.predict(corpus, m, args.sweeps)))
             for m in ("branching_entropy", "greedy_ngram", "dp_unigram")}
    methods = {"supervised_75_labels": preds["primary"], "supervised_all_line_labels": preds["all_lines"], **unsup,
               "all_boundaries": {d["id"]: list(range(1, len(d["text"]))) for d in legends},
               "no_boundaries": {d["id"]: [] for d in legends}}
    refs_words = [{"id": d["id"], "length": len(d["text"]), "boundaries": d["words"], "complete": True} for d in legends]
    refs_lines = [{"id": d["id"], "length": len(d["text"]), "boundaries": d["lines"], "complete": False}
                  for d in legends if d["lines"]]
    res = {"legends": len(legends), "legends_with_line_divisions": len(refs_lines),
           "word_divisions": sum(len(d["words"]) for d in legends),
           "line_divisions": sum(len(d["lines"]) for d in legends),
           "line_divisions_that_are_word_divisions": sum(len(set(d["lines"]) & set(d["words"])) for d in legends),
           "input_sha256": U.sha256(U.BRONZE), "models": models, "methods": {}}
    for name, p in methods.items():
        w = run_bench(refs_words, [{"id": r["id"], "boundaries": p[r["id"]]} for r in refs_words],
                      out_dir / f"words-{name}.json", raw_dir, f"words-{name}")
        ln = run_bench(refs_lines, [{"id": r["id"], "boundaries": p[r["id"]]} for r in refs_lines],
                       out_dir / f"lines-{name}.json", raw_dir, f"lines-{name}")
        res["methods"][name] = {"boundary_f1": w["scores"]["boundary_f1"],
                                "boundary_precision": w["scores"]["boundary_precision"],
                                "boundary_recall": w["scores"]["boundary_recall"],
                                "word_f1": w["scores"]["word_f1"],
                                "line_recall": ln["scores"]["boundary_recall"],
                                "line_rate_elsewhere": ln["scores"]["boundary_rate_elsewhere"],
                                "line_j": ln["scores"]["boundary_recall"] - ln["scores"]["boundary_rate_elsewhere"]}
    sup, every = res["methods"]["supervised_75_labels"], res["methods"]["all_boundaries"]
    res["decision"] = {"rule": "held-out boundary F1 of the 75-label model exceeds the everywhere baseline by >= 0.05",
                       "margin": sup["boundary_f1"] - every["boundary_f1"],
                       "pass": bool(sup["boundary_f1"] - every["boundary_f1"] >= 0.05)}
    U.write_json(U.PKG / args.run / "sumerian-summary.json", res)
    print(json.dumps(res["decision"], indent=1))
    for name, v in res["methods"].items():
        print(name, {k: round(x, 3) for k, x in v.items()})


if __name__ == "__main__":
    main()
