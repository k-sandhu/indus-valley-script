"""Matched post-outcome positional backoff comparator, with immutable endpoints."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import shutil

from grammar import Position, SignCounts, audit_split, digest, folds, load_corpus, read_jsonl, write_json
from mixture import WEIGHTS, mixed_scores
from analyze import summarize
import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]


def main(run):
    out = PACKAGE / run
    local = ROOT / "data/raw/2026-10-11-two-approaches/grammar" / run
    if out.exists() or local.exists():
        raise FileExistsError("Preserve existing outputs and choose a new run.")
    out.mkdir()
    local.mkdir(parents=True)
    for filename in ("matched_mixtures.py", "AMENDMENT-V3.md"):
        shutil.copyfile(PACKAGE / filename, out / filename)
    primary = PACKAGE / "run-v1"
    prior = PACKAGE / "run-v2-mixture"
    primary_local = ROOT / "data/raw/2026-10-11-two-approaches/grammar/run-v1"
    prior_local = ROOT / "data/raw/2026-10-11-two-approaches/grammar/run-v2-mixture"
    old = json.loads((primary / "results.json").read_text())
    mixture = json.loads((prior / "results.json").read_text())
    seed = old["manifest"]["seed"]
    rows, _ = load_corpus(ROOT / old["manifest"]["input"])
    assigned, loads = folds(rows, 5, seed)
    assert loads == old["manifest"]["outer_fold_token_loads"]
    all_class, all_position, matched, results = [], [], [], []
    pooled_position_scores = Counter()
    for fold in range(5):
        train = [row for i, row in enumerate(rows) if assigned[i] != fold]
        test = [row for i, row in enumerate(rows) if assigned[i] == fold]
        audit_split(train, test)
        inner_assignment, _ = folds(train, 3, seed + fold)
        selected = json.loads((primary / f"fold-{fold}-selection.json").read_text())
        inner_saved = read_jsonl(prior_local / f"fold-{fold}-inner-predictions.jsonl")
        inner_lookup = {(row["record_id"], row["inner"]): row for row in inner_saved}
        scores = Counter()
        position_score = 0.0
        for inner in range(3):
            fit = [row for i, row in enumerate(train) if inner_assignment[i] != inner]
            validation = [row for i, row in enumerate(train) if inner_assignment[i] == inner]
            audit_split(fit, validation)
            model = Position(SignCounts(fit), selected["selected"]["POSITION"])
            for row in validation:
                saved = inner_lookup[(row["record_id"], inner)]
                assert saved["group"] == row["group"]
                first = np.array(saved["MARKOV_log2"])
                second = model.score(row)
                position_score += float(second.sum())
                for weight in WEIGHTS:
                    scores[weight] += float(mixed_scores(first, second, weight).sum())
        expected = -selected["inner_cross_entropy_bits"]["POSITION"][str(selected["selected"]["POSITION"])] * selected["validation_tokens"]
        assert abs(position_score - expected) < 1e-7
        chosen = max(WEIGHTS, key=lambda weight: scores[weight])
        pooled_position_scores.update(scores)
        class_rows = read_jsonl(prior_local / f"fold-{fold}-predictions.jsonl")
        position_rows = read_jsonl(primary_local / f"fold-{fold}-predictions.jsonl")
        for class_row, position_row in zip(class_rows, position_rows):
            assert (class_row["record_id"], class_row["group"]) == (position_row["record_id"], position_row["group"])
            p = position_row["log2_probabilities"]
            p["GRAMMAR"] = mixed_scores(np.array(p["MARKOV"]), np.array(p["POSITION"]), chosen).tolist()
            all_class.append(class_row)
            all_position.append(position_row)
            comparison = dict(class_row)
            comparison["log2_probabilities"] = {"POSITION": p["POSITION"], "MARKOV": p["GRAMMAR"],
                                               "GRAMMAR": class_row["log2_probabilities"]["GRAMMAR"]}
            matched.append(comparison)
        result = {"fold": fold, "class_grammar_weight": mixture["folds"][fold]["selected_grammar_weight"],
                  "position_weight": chosen,
                  "position_inner_cross_entropy_bits": {str(w): -score / selected["validation_tokens"] for w, score in scores.items()},
                  "class_minus_position_mixture_bits_per_token":
                      sum(sum(a["log2_probabilities"]["GRAMMAR"]) - sum(b["log2_probabilities"]["GRAMMAR"])
                          for a, b in zip(class_rows, position_rows)) / sum(len(r["sequence"]) for r in class_rows)}
        results.append(result)
        write_json(out / f"fold-{fold}.json", result)
    with (local / "matched-predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in matched:
            handle.write(json.dumps(row) + "\n")
    result = {"status": "exploratory-post-outcome-matched-control", "folds": results,
              "class_mixture_vs_markov": summarize(all_class, seed),
              "position_mixture_vs_markov": summarize(all_position, seed),
              "class_mixture_vs_position_mixture": summarize(matched, seed),
              "summary_label_mapping": {"class_mixture_vs_position_mixture": {"GRAMMAR": "Markov plus class grammar", "MARKOV": "Markov plus position"}},
              "carry_forward_position_weight_from_pooled_inner_scores": max(WEIGHTS, key=lambda w: pooled_position_scores[w]),
              "preserved_class_mixture_result_sha256": digest(prior / "results.json"),
              "primary_result_sha256": digest(primary / "results.json"),
              "amendment_sha256": digest(PACKAGE / "AMENDMENT-V3.md"), "code_sha256": digest(__file__),
              "checks": {"same_weight_grid_for_both_families": list(WEIGHTS), "position_inner_scores_reproduce_original": True,
                         "all_inner_and_outer_closure_audits_passed": True, "class_weights_preserved": True}}
    write_json(out / "results.json", result)
    write_json(out / "completion.json", {"complete": True,
                                        "tracked_output_sha256": {p.name: digest(p) for p in sorted(out.glob("*.json"))},
                                        "local_only_output_sha256": {p.name: digest(p) for p in sorted(local.glob("*.jsonl"))}})
    print(json.dumps({"class_gain_vs_markov": result["class_mixture_vs_markov"]["contrasts"]["GRAMMAR_minus_MARKOV"],
                      "position_gain_vs_markov": result["position_mixture_vs_markov"]["contrasts"]["GRAMMAR_minus_MARKOV"],
                      "class_gain_vs_position_mixture": result["class_mixture_vs_position_mixture"]["contrasts"]["GRAMMAR_minus_MARKOV"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
