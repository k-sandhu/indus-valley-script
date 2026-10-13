"""Recompute frozen scores and audit splits without refitting models."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

from grammar import digest, read_jsonl, write_json
import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]


def main(run):
    out = PACKAGE / run
    local = ROOT / "data/raw/2026-10-11-two-approaches/grammar" / run
    target = out / "verification.json"
    if target.exists():
        raise FileExistsError("Preserve the existing verification endpoint.")
    manifest = json.loads((out / "manifest.json").read_text())
    completion = json.loads((out / "completion.json").read_text())
    result = json.loads((out / "results.json").read_text())
    assert completion["complete"] and completion["outer_folds"] == 5
    for name, expected in completion["tracked_output_sha256"].items():
        assert digest(out / name) == expected, name
    for name, expected in completion["local_only_output_sha256"].items():
        assert digest(local / name) == expected, name
    for name, expected in (("grammar.py", "code_sha256"), ("analyze.py", "runner_sha256"), ("PROTOCOL.md", "protocol_sha256")):
        assert digest(out / name) == manifest[expected]
    assert digest(ROOT / manifest["input"]) == manifest["input_sha256"]
    rows = read_jsonl(local / "fold-assignment.jsonl")
    lookup = {row["record_id"]: row for row in rows}
    assert len(lookup) == len(rows) == result["summary"]["texts"]
    group_fold, alias_fold, text_fold = defaultdict(set), defaultdict(set), defaultdict(set)
    for row in rows:
        group_fold[row["group"]].add(row["fold"])
        text_fold[tuple(row["seq"])].add(row["fold"])
        for alias in row["artifact_aliases"]:
            alias_fold[alias].add(row["fold"])
    assert all(len(values) == 1 for table in (group_fold, alias_fold, text_fold) for values in table.values())
    sums = defaultdict(float)
    tokens, oov = 0, 0
    checked_scores, maximum_forward_error = 0, 0.0
    fold_audits = []
    for fold in range(5):
        predicted = read_jsonl(local / f"fold-{fold}-predictions.jsonl")
        weights = np.load(local / f"fold-{fold}-model.npz", allow_pickle=False)
        signs = weights["signs"].tolist()
        vocabulary = {sign for row in rows if row["fold"] != fold for sign in row["seq"]}
        assert signs[:-1] == sorted(vocabulary) and signs[-1] == "__UNKNOWN__"
        index = {sign: j for j, sign in enumerate(signs)}
        emission = weights["emission"]
        assert np.allclose(emission.sum(axis=1), 1)
        assert np.allclose(weights["transition"].sum(axis=1), 1)
        assert np.isclose(weights["initial"].sum(), 1)
        for row in predicted:
            source = lookup[row["record_id"]]
            assert row["fold"] == fold == source["fold"]
            assert row["group"] == source["group"]
            assert row["sequence"] == source["seq"]
            known = [sign in vocabulary for sign in row["sequence"]]
            assert row["in_training_alphabet"] == known
            oov += sum(not flag for flag in known)
            length = len(row["sequence"])
            tokens += length
            for model, scores in row["log2_probabilities"].items():
                assert len(scores) == length and all(math.isfinite(score) and score <= 1e-12 for score in scores)
                sums[model] += sum(scores)
            initial_key = f"initial_L{length}"
            contextual = bool(weights["configuration"][2])
            state = weights[initial_key].copy() if contextual and initial_key in weights else weights["initial"].copy()
            recomputed = []
            for j, sign in enumerate(row["sequence"]):
                probabilities = state @ emission
                assert abs(float(probabilities.sum()) - 1) < 1e-10
                target_index = index.get(sign, len(signs) - 1)
                prob = probabilities[target_index]
                recomputed.append(math.log2(prob))
                state *= emission[:, target_index]
                state /= prob
                if j + 1 < length:
                    transition_key = f"transition_L{length}_j{j + 1}"
                    transition = weights[transition_key] if contextual and transition_key in weights else weights["transition"]
                    assert np.allclose(transition.sum(axis=1), 1)
                    state = state @ transition
            error = float(np.max(np.abs(np.array(recomputed) - row["log2_probabilities"]["GRAMMAR"])))
            assert error < 1e-10
            maximum_forward_error = max(maximum_forward_error, error)
            checked_scores += length
        selection = json.loads((out / f"fold-{fold}-selection.json").read_text())
        for family, losses in selection["inner_cross_entropy_bits"].items():
            chosen_key = json.dumps(selection["selected"][family], separators=(",", ":"))
            assert abs(losses[chosen_key] - min(losses.values())) < 1e-12
        fold_audits.append({"fold": fold, "test_texts": len(predicted), "training_vocabulary_types": len(vocabulary),
                            "inner_loss_selections_match_saved_minima": True})
    losses = {name: -score / tokens for name, score in sums.items()}
    assert tokens == result["summary"]["tokens"] == 8009
    assert oov == result["summary"]["OOV_tokens"]
    assert all(abs(losses[name] - saved) < 1e-12 for name, saved in result["summary"]["cross_entropy_bits_per_token"].items())
    audit = {"status": "verified-computation", "run": run, "input_snapshot_code_and_output_hashes_match": True,
             "record_predictions_match_assignment": True, "zero_cross_fold_group_alias_or_string_overlap": True,
             "training_only_vocabularies_verified": True, "selected_parameters_minimize_inner_losses": True,
             "recomputed_outer_cross_entropy_bits_per_token": losses,
             "grammar_forward_tokens_independently_recomputed": checked_scores,
             "maximum_saved_forward_log2_error": maximum_forward_error,
             "OOV_tokens": oov, "fold_audits": fold_audits,
             "scope": "Independent arithmetic from saved arrays and rows; it does not authenticate archaeological semantics.",
             "verification_script_sha256": digest(__file__)}
    write_json(target, audit)
    print(json.dumps(audit))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
