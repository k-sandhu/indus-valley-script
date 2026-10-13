"""Exploratory post-outcome combination; keeps primary grammar failure intact."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from grammar import Grammar, Markov, SignCounts, audit_split, digest, folds, load_corpus, read_jsonl, write_json
from analyze import summarize
import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
WEIGHTS = (0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.00)


def mixed_scores(first, second, weight):
    return np.log2((1 - weight) * np.exp2(first) + weight * np.exp2(second))


def main(run, primary):
    out = PACKAGE / run
    local = ROOT / "data/raw/2026-10-11-two-approaches/grammar" / run
    source = PACKAGE / primary
    source_local = ROOT / "data/raw/2026-10-11-two-approaches/grammar" / primary
    if out.exists() or local.exists():
        raise FileExistsError("An output already exists; choose a fresh run name.")
    out.mkdir()
    local.mkdir(parents=True)
    for filename in ("mixture.py", "grammar.py", "POST-OUTCOME-PROTOCOL.md"):
        shutil.copyfile(PACKAGE / filename, out / filename)
    saved = json.loads((source / "results.json").read_text())
    seed = saved["manifest"]["seed"]
    rows, census = load_corpus(ROOT / saved["manifest"]["input"])
    assignment, loads = folds(rows, 5, seed)
    assert loads == saved["manifest"]["outer_fold_token_loads"]
    toy = np.array([0.2, 0.3, 0.5])
    other = np.array([0.6, 0.25, 0.15])
    toy_sums = {}
    for weight in WEIGHTS:
        total = float(np.exp2(mixed_scores(np.log2(toy), np.log2(other), weight)).sum())
        assert abs(total - 1) < 1e-12
        toy_sums[str(weight)] = total
    predictions, results = [], []
    pooled_inner = Counter()
    max_inner_score_error = 0.0
    for fold in range(5):
        train = [row for i, row in enumerate(rows) if assignment[i] != fold]
        test = [row for i, row in enumerate(rows) if assignment[i] == fold]
        audit_split(train, test)
        selected = json.loads((source / f"fold-{fold}-selection.json").read_text())
        inner_assignment, _ = folds(train, 3, seed + fold)
        weight_scores = Counter()
        inner_counts = Counter()
        inner_rows = []
        for inner in range(3):
            fit = [row for i, row in enumerate(train) if inner_assignment[i] != inner]
            validation = [row for i, row in enumerate(train) if inner_assignment[i] == inner]
            audit_split(fit, validation)
            counts = SignCounts(fit)
            markov = Markov(counts, *selected["selected"]["MARKOV"])
            grammar = Grammar(fit, *selected["selected"]["GRAMMAR"], seed=seed + fold + inner * 1009)
            assert markov.alphabet.signs == grammar.alphabet.signs
            for row in validation:
                first, second = markov.score(row), grammar.score(row)
                inner_counts["MARKOV"] += float(first.sum())
                inner_counts["GRAMMAR"] += float(second.sum())
                inner_rows.append({"record_id": row["record_id"], "group": row["group"], "inner": inner,
                                   "MARKOV_log2": first.tolist(), "GRAMMAR_log2": second.tolist()})
                for weight in WEIGHTS:
                    weight_scores[weight] += float(mixed_scores(first, second, weight).sum())
        for family in ("MARKOV", "GRAMMAR"):
            configuration = json.dumps(selected["selected"][family], separators=(",", ":"))
            expected = -selected["inner_cross_entropy_bits"][family][configuration] * selected["validation_tokens"]
            error = abs(expected - inner_counts[family])
            assert error < 1e-7, (fold, family, error)
            max_inner_score_error = max(max_inner_score_error, error)
        with (local / f"fold-{fold}-inner-predictions.jsonl").open("w", encoding="utf-8") as handle:
            for row in inner_rows:
                handle.write(json.dumps(row) + "\n")
        chosen = max(WEIGHTS, key=lambda weight: weight_scores[weight])
        pooled_inner.update(weight_scores)
        scored = read_jsonl(source_local / f"fold-{fold}-predictions.jsonl")
        for row in scored:
            scores = row["log2_probabilities"]
            first, second = np.array(scores["MARKOV"]), np.array(scores["GRAMMAR"])
            zero = mixed_scores(first, second, 0)
            assert np.allclose(zero, first, atol=1e-12)
            scores["PRIMARY_GRAMMAR"] = scores["GRAMMAR"]
            scores["GRAMMAR"] = mixed_scores(first, second, chosen).tolist()
        summary = summarize(scored, seed + fold)
        predictions += scored
        result = {"fold": fold, "selected_grammar_weight": chosen, "validation_tokens": selected["validation_tokens"],
                  "inner_cross_entropy_bits": {str(weight): -score / selected["validation_tokens"] for weight, score in weight_scores.items()},
                  "outer_summary": summary}
        results.append(result)
        write_json(out / f"fold-{fold}.json", result)
        with (local / f"fold-{fold}-predictions.jsonl").open("w", encoding="utf-8") as handle:
            for row in scored:
                handle.write(json.dumps(row) + "\n")
        print(json.dumps({"stage": "mixture_fold_complete", "fold": fold, "weight": chosen,
                          "gain": summary["contrasts"]["GRAMMAR_minus_MARKOV"]["bits_per_token"]}), flush=True)
    summary = summarize(predictions, seed)
    chosen_full = max(WEIGHTS, key=lambda weight: pooled_inner[weight])
    result = {"status": "exploratory-post-outcome-completed", "source_endpoint": primary,
              "post_outcome_protocol_sha256": digest(PACKAGE / "POST-OUTCOME-PROTOCOL.md"),
              "code_sha256": digest(__file__), "grammar_code_sha256": digest(PACKAGE / "grammar.py"),
              "primary_results_sha256": digest(source / "results.json"), "census": census,
              "model_label_GRAMMAR_in_summary_means": "Convex Markov/class-grammar mixture; PRIMARY_GRAMMAR records the frozen original constituent.",
              "summary": summary, "folds": results, "carry_forward_weight_from_pooled_inner_scores": chosen_full,
              "verification": {"all_registered_toy_mixtures_normalized": toy_sums,
                               "maximum_reproduced_inner_constituent_score_error_bits": max_inner_score_error,
                               "zero_weight_reproduces_original_outer_markov": True,
                               "training_only_weight_selection": True, "all_inner_and_outer_closure_audits_passed": True}}
    write_json(out / "results.json", result)
    write_json(out / "completion.json", {"complete": True, "outer_folds": 5,
                                        "tracked_output_sha256": {p.name: digest(p) for p in sorted(out.glob("*.json"))},
                                        "local_only_output_sha256": {p.name: digest(p) for p in sorted(local.glob("*.jsonl"))}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--primary", default="run-v1")
    args = parser.parse_args()
    main(args.run, args.primary)
