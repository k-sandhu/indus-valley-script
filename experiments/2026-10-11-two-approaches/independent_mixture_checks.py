"""Recount mixture selection and predictions without refitting the grammar."""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = HERE / "grammar"
RAW = ROOT / "data/raw/2026-10-11-two-approaches/grammar"
WEIGHTS = (0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def lines(path):
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s]


def mixed(first, second, weight):
    return np.log2((1 - weight) * np.exp2(first) + weight * np.exp2(second))


def positional_scores(train, row, strength):
    """Independent counter reconstruction of the declared positional prior."""
    total = Counter(s for r in train for s in r["seq"])
    signs = sorted(total) + ["__UNKNOWN__"]
    index = {s: j for j, s in enumerate(signs)}
    unigram = np.array([total[s] + 0.5 for s in signs], float)
    unigram /= unigram.sum()
    cells = defaultdict(Counter)
    for r in train:
        for slot, code in enumerate(r["seq"]):
            cells[(len(r["seq"]), slot)][code] += 1
    scores = []
    for slot, code in enumerate(row["seq"]):
        counts = cells[(len(row["seq"]), slot)]
        target = index.get(code, len(signs) - 1)
        value = (counts[signs[target]] + strength * unigram[target]) / (sum(counts.values()) + strength)
        scores.append(np.log2(value))
    return np.array(scores)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="coordinator-checks/mixtures-v1.json")
    args = parser.parse_args()
    output = HERE / args.out
    if output.exists():
        raise SystemExit("Output exists; choose a fresh path.")
    spec = importlib.util.spec_from_file_location("frozen_fold_helper", BASE / "run-v1/grammar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assignment = lines(RAW / "run-v1/fold-assignment.jsonl")
    checks, class_total, position_total, markov_total, token_total = [], 0.0, 0.0, 0.0, 0
    def record(name, passed, **details):
        checks.append({"check": name, "pass": bool(passed), **details})
    max_outer_error = 0.0
    for fold in range(5):
        selection = read(BASE / f"run-v1/fold-{fold}-selection.json")
        class_result = read(BASE / f"run-v2-mixture/fold-{fold}.json")
        matched_result = read(BASE / f"run-v3-matched-mixtures/fold-{fold}.json")
        train = [r for r in assignment if r["fold"] != fold]
        inner_folds, _ = module.folds(train, 3, 20261011 + fold)
        lookup = {(r["record_id"], inner_folds[i]): r for i, r in enumerate(train)}
        inner = lines(RAW / f"run-v2-mixture/fold-{fold}-inner-predictions.jsonl")
        class_scores, position_scores = Counter(), Counter()
        fits = {i: [r for j, r in enumerate(train) if inner_folds[j] != i] for i in range(3)}
        for saved in inner:
            row = lookup[(saved["record_id"], saved["inner"])]
            fit = fits[saved["inner"]]
            assert row["group"] not in {r["group"] for r in fit}
            first, second = np.array(saved["MARKOV_log2"]), np.array(saved["GRAMMAR_log2"])
            position = positional_scores(fit, row, selection["selected"]["POSITION"])
            for weight in WEIGHTS:
                class_scores[weight] += float(mixed(first, second, weight).sum())
                position_scores[weight] += float(mixed(first, position, weight).sum())
        chosen_class, chosen_position = (max(WEIGHTS, key=s.get) for s in (class_scores, position_scores))
        record("inner_class_weight_independently_selected", chosen_class == class_result["selected_grammar_weight"], fold=fold, weight=chosen_class)
        record("inner_position_weight_independently_selected", chosen_position == matched_result["position_weight"], fold=fold, weight=chosen_position)
        record("same_weight_grid", set(map(float, class_result["inner_cross_entropy_bits"])) == set(map(float, matched_result["position_inner_cross_entropy_bits"])) == set(WEIGHTS), fold=fold)
        nval = class_result["validation_tokens"]
        max_class_error = max(abs(-class_scores[w] / nval - class_result["inner_cross_entropy_bits"][str(w)]) for w in WEIGHTS)
        max_position_error = max(abs(-position_scores[w] / nval - matched_result["position_inner_cross_entropy_bits"][str(w)]) for w in WEIGHTS)
        record("inner_grid_scores_independently_recounted", max(max_class_error, max_position_error) < 1e-11, fold=fold, max_error=max(max_class_error, max_position_error))
        original = lines(RAW / f"run-v1/fold-{fold}-predictions.jsonl")
        amended = lines(RAW / f"run-v2-mixture/fold-{fold}-predictions.jsonl")
        for first, second in zip(original, amended):
            assert first["record_id"] == second["record_id"] and first["sequence"] == second["sequence"]
            p = first["log2_probabilities"]
            class_probability = mixed(np.array(p["MARKOV"]), np.array(p["GRAMMAR"]), chosen_class)
            position_probability = mixed(np.array(p["MARKOV"]), np.array(p["POSITION"]), chosen_position)
            max_outer_error = max(max_outer_error, float(np.max(np.abs(class_probability - second["log2_probabilities"]["GRAMMAR"]))))
            class_total += float(class_probability.sum())
            position_total += float(position_probability.sum())
            markov_total += sum(p["MARKOV"])
            token_total += len(first["sequence"])
    record("outer_class_probabilities_independently_recounted", max_outer_error < 1e-11, tokens=token_total, max_error=max_outer_error)
    final = read(BASE / "run-v3-matched-mixtures/results.json")
    published = final["class_mixture_vs_position_mixture"]["cross_entropy_bits_per_token"]
    class_loss, position_loss, markov_loss = (-s / token_total for s in (class_total, position_total, markov_total))
    record("matched_losses_independently_recounted", abs(class_loss - published["GRAMMAR"]) < 1e-11 and abs(position_loss - published["MARKOV"]) < 1e-11,
           class_loss=class_loss, position_loss=position_loss, markov_loss=markov_loss, increment_bits_per_token=position_loss-class_loss)
    result = {"status": "coordinator-independent-mixture-audit", "checks": checks,
              "passed": sum(c["pass"] for c in checks), "failed": sum(not c["pass"] for c in checks),
              "scope": "Independent positional counter reconstruction, inner weight selection and outer mixture rescoring. Same exposed corpus; no new archaeological validation.",
              "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"], "losses": [class_loss, position_loss, markov_loss], "output": str(output)}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
