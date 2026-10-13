"""Post-outcome component and selected-code summaries; no model refitting."""
from collections import Counter, defaultdict
import json
from pathlib import Path

from grammar import digest, read_jsonl, write_json
from mixture import mixed_scores
import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
LOCAL = ROOT / "data/raw/2026-10-11-two-approaches/grammar"


def main():
    target = PACKAGE / "post-outcome-diagnostics.json"
    if target.exists():
        raise FileExistsError("Preserve the saved diagnostic endpoint.")
    rows = read_jsonl(LOCAL / "run-v1/fold-assignment.jsonl")
    group_weights, group_texts = Counter(), Counter()
    positions = defaultdict(Counter)
    selected = {"817", "820", "861", "002", "060", "740", "520", "400", "090", "390", "407", "527"}
    late_pairs = Counter()
    for row in rows:
        seq = row["seq"]
        group_weights[row["group"]] += len(seq)
        group_texts[row["group"]] += 1
        for j, code in enumerate(seq):
            if code in selected:
                positions[code]["initial" if j == 0 else "final" if j + 1 == len(seq) else "internal"] += 1
        for j, (left, right) in enumerate(zip(seq[:-1], seq[1:])):
            if left in {"740", "520"} and right in {"400", "090"}:
                late_pairs[f"{left}->{right}"] += 1
                if j + 2 == len(seq):
                    late_pairs[f"{left}->{right}_right_is_final"] += 1
    largest = max(group_weights, key=group_weights.get)
    mixture = json.loads((PACKAGE / "run-v2-mixture/results.json").read_text())
    matched = json.loads((PACKAGE / "run-v3-matched-mixtures/results.json").read_text())
    score_errors = []
    reduced = Counter()
    for fold in range(5):
        first = read_jsonl(LOCAL / f"run-v1/fold-{fold}-predictions.jsonl")
        second = read_jsonl(LOCAL / f"run-v2-mixture/fold-{fold}-predictions.jsonl")
        assert len(first) == len(second)
        for a, b in zip(first, second):
            assert a["record_id"] == b["record_id"] and a["group"] == b["group"]
            score = a["log2_probabilities"]
            expected = mixed_scores(np.array(score["MARKOV"]), np.array(score["GRAMMAR"]), mixture["folds"][fold]["selected_grammar_weight"])
            error = float(np.max(np.abs(expected - b["log2_probabilities"]["GRAMMAR"])))
            score_errors.append(error)
            assert error < 1e-12
            if a["group"] != largest:
                reduced["tokens"] += len(a["sequence"])
                reduced["primary_grammar_minus_markov_bits"] += sum(score["GRAMMAR"]) - sum(score["MARKOV"])
                reduced["class_mixture_minus_markov_bits"] += float(expected.sum()) - sum(score["MARKOV"])
    scored = read_jsonl(LOCAL / "run-v3-matched-mixtures/matched-predictions.jsonl")
    for row in scored:
        if row["group"] != largest:
            reduced["class_mixture_minus_position_mixture_bits"] += sum(row["log2_probabilities"]["GRAMMAR"]) - sum(row["log2_probabilities"]["MARKOV"])
    assert len({row["record_id"] for row in scored}) == len(rows)
    weights = np.array(list(group_weights.values()), dtype=float)
    result = {"status": "exploratory-post-outcome-descriptive-audit", "primary_group_count": len(weights),
              "token_weight_effective_component_count": float(weights.sum() ** 2 / (weights ** 2).sum()),
              "largest_component_texts": group_texts[largest], "largest_component_tokens": group_weights[largest],
              "largest_component_token_share": group_weights[largest] / sum(group_weights.values()),
              "fixed_prediction_sensitivity_excluding_largest_component": {
                  "remaining_tokens": int(reduced["tokens"]),
                  "primary_grammar_minus_markov_bits_per_token": reduced["primary_grammar_minus_markov_bits"] / reduced["tokens"],
                  "class_mixture_minus_markov_bits_per_token": reduced["class_mixture_minus_markov_bits"] / reduced["tokens"],
                  "class_mixture_minus_position_mixture_bits_per_token": reduced["class_mixture_minus_position_mixture_bits"] / reduced["tokens"],
                  "models_refit": False},
              "maximum_recomputed_outer_mixture_log2_error": max(score_errors),
              "selected_code_positions": {code: dict(positions[code]) for code in sorted(selected)},
              "selected_late_attachment_pairs": dict(late_pairs),
              "selection_scope": "Codes and late-attachment pairs chosen after inspecting descriptive learned classes; no significance test or semantic identification.",
              "input_and_run_pins": {"raw_corpus": digest(ROOT / "data/normalized/lipi_observed_faces.jsonl"),
                                     "primary_results": digest(PACKAGE / "run-v1/results.json"),
                                     "class_mixture_results": digest(PACKAGE / "run-v2-mixture/results.json"),
                                     "matched_mixture_results": digest(PACKAGE / "run-v3-matched-mixtures/results.json")},
              "code_sha256": digest(__file__)}
    write_json(target, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
