"""Post-outcome exact illustrations from the sealed conservation experiment.

This file extracts examples; it does not fit or select a decoder.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/2026-10-02-six-hour/khipu-control/conservation-check"
RUN = BASE / "main-v1"
TARGETS = ("20261020097-four_swapped", "20261020124-four_swapped")


def rank(rows):
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivot = 0
    for col in range(3):
        selected = next((i for i in range(pivot, len(matrix)) if matrix[i][col]), None)
        if selected is None:
            continue
        matrix[pivot], matrix[selected] = matrix[selected], matrix[pivot]
        divisor = matrix[pivot][col]
        matrix[pivot] = [value / divisor for value in matrix[pivot]]
        for i in range(len(matrix)):
            if i != pivot:
                multiplier = matrix[i][col]
                matrix[i] = [a - multiplier * b for a, b in zip(matrix[i], matrix[pivot])]
        pivot += 1
    return pivot


def dot(row, vector):
    return sum(Fraction(a) * Fraction(b) for a, b in zip(row, vector))


def read_selected(name, id_field):
    selected = {}
    with (RUN / name).open(encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            if item[id_field] in TARGETS and item.get("prefix", 8) == 8:
                selected[item[id_field]] = item
    assert set(selected) == set(TARGETS)
    return selected


def main():
    destination = BASE / "selected-case-arithmetic.json"
    if destination.exists():
        raise FileExistsError(destination)
    inputs = read_selected("component-inputs.jsonl", "id")
    keys = read_selected("evaluator-key.jsonl", "id")
    inferences = read_selected("inferences.jsonl", "world_id")
    evaluations = read_selected("evaluated-prefixes.jsonl", "world_id")
    examples = []
    for identifier in TARGETS:
        component = inputs[identifier]["component"]
        key = keys[identifier]["key"]
        inferred = inferences[identifier]
        evaluated = evaluations[identifier]
        policy = "collective_half" if identifier == TARGETS[0] else "baseline_half"
        values = inferred["policies"][policy]["normalized_values"]
        score = evaluated["policies"][policy]
        rows = component["equations"]
        residuals = [dot(row, values) for row in rows]
        assert [str(value) for value in [dot(row, values) for row in key["heldout_equations"]]] == score["heldout_normalized_relation_residuals"]
        absolute = score["absolute_values_counted"]
        counts = [dot(features, absolute) - count for features, count in zip(key["count_features"], key["count_values"])]
        assert [str(value) for value in counts] == score["heldout_counted_residuals"]
        examples.append({
            "world_id": identifier,
            "selection": "Post-outcome illustration of a saved failure, outside protocol scoring",
            "policy": policy,
            "normalized_values": values,
            "counted_absolute_values": absolute,
            "unit_count_observation": component["scale_observations"]["counted"],
            "true_normalized_values": ["1", "10", "100"],
            "true_absolute_values": key["true_weights"],
            "training_equations": rows,
            "training_residuals_at_wrong_values": [str(value) for value in residuals],
            "support_indices_at_wrong_values": [i for i, value in enumerate(residuals) if not value],
            "true_support_indices": [i for i, row in enumerate(rows) if not dot(row, (1, 10, 100))],
            "collective_observation": component["collective_observation"],
            "aggregate_residual_at_wrong_values": str(dot(inferred["aggregate"], values)),
            "aggregate_residual_at_true_values": str(dot(inferred["aggregate"], (1, 10, 100))),
            "heldout_equations": key["heldout_equations"],
            "heldout_equation_rank": rank(key["heldout_equations"]),
            "heldout_normalized_residuals": score["heldout_normalized_relation_residuals"],
            "heldout_count_features": key["count_features"],
            "heldout_count_values": key["count_values"],
            "heldout_count_feature_rank": rank(key["count_features"]),
            "heldout_counted_residuals": score["heldout_counted_residuals"],
            "unmeasured_ray_count_check": score["unmeasured_ray_count_check"],
            "all_saved_policy_decisions": inferred["policies"],
            "all_saved_policy_evaluations": evaluated["policies"],
        })
    record = {
        "scope": "Post-outcome arithmetic illustrations from unchanged sealed outputs",
        "source_files": [{"path": "main-v1/" + name, "sha256": hashlib.sha256((RUN / name).read_bytes()).hexdigest()} for name in ("component-inputs.jsonl", "evaluator-key.jsonl", "inferences.jsonl", "evaluated-prefixes.jsonl")],
        "examples": examples,
        "checks": {"exact_fraction_residuals_recomputed": True, "heldout_ranks_reduced_independently": True},
    }
    destination.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(destination), "bytes": destination.stat().st_size, "cases": [{"id": x["world_id"], "heldout_relation_rank": x["heldout_equation_rank"], "count_rank": x["heldout_count_feature_rank"], "wrong_aggregate_residual": x["aggregate_residual_at_wrong_values"]} for x in examples]}))


if __name__ == "__main__":
    main()
