"""Exact hypothetical anchor calculation for four equivalent interpretations.

This is a constructed information experiment, with no archaeological data or
estimated probabilities. The two external anchors are assumed to implement
balanced, independently verified partitions of four interpretations. A real
contextual observation must justify its partition before this calculation can
be used for planning. Earlier source-dependence work is acknowledged in the note.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYPOTHESES = ((0, 0), (0, 1), (1, 0), (1, 1))


def entropy(probabilities):
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


def exact_gain(features, error):
    """Each feature is measured once with independent symmetric observation error."""
    expected_entropy = 0.0
    outcome_mass = 0.0
    posterior_checks = []
    for answers in itertools.product((0, 1), repeat=len(features)):
        mass = []
        for hypothesis in HYPOTHESES:
            likelihood = math.prod((1 - error) if hypothesis[f] == y else error
                                   for f, y in zip(features, answers))
            mass.append(likelihood / 4)
        probability = sum(mass)
        if probability == 0:
            continue
        posterior = [p / probability for p in mass]
        posterior_checks.append(abs(sum(posterior) - 1) < 1e-12)
        expected_entropy += probability * entropy(posterior)
        outcome_mass += probability
    assert abs(outcome_mass - 1) < 1e-12
    assert all(posterior_checks)
    return {"expected_remaining_entropy_bits": expected_entropy,
            "expected_information_bits": 2 - expected_entropy,
            "outcome_probability_sum": outcome_mass}


def calculate():
    rows = []
    for error in (0.0, 0.05, 0.1, 0.2, 0.35):
        channel = 1 - entropy((error, 1 - error))
        one = exact_gain((0,), error)
        two = exact_gain((0, 1), error)
        repeated_independent = exact_gain((0, 0), error)
        # An exact copy of the first answer supplies the same information once.
        repeated_shared = dict(one)
        # If copies are wrongly treated as independent, the two identical
        # answers produce this nominal probability of an erroneous bit.
        naive_error = error**2 / (error**2 + (1 - error)**2)
        naive_entropy = 1 + entropy((naive_error, 1 - naive_error))
        rows.append({"assumed_symmetric_error": error,
                     "one_validated_partition": one,
                     "two_distinct_independent_partitions": two,
                     "two_independent_witnesses_for_same_partition": repeated_independent,
                     "two_copies_of_one_witness": repeated_shared,
                     "copy_treated_as_independent_nominal_remaining_entropy_bits": naive_entropy,
                     "copy_treated_as_independent_nominal_wrong_bit_probability": naive_error,
                     "actual_wrong_bit_probability_after_a_copied_answer": error,
                     "binary_channel_information_upper_bound_bits": channel})
        assert abs(one["expected_information_bits"] - channel) < 1e-12
        assert abs(two["expected_information_bits"] - 2 * channel) < 1e-12
        assert repeated_independent["expected_information_bits"] <= 1 + 1e-12
        assert repeated_shared == one
    return {"status": "Synthetic exact enumeration",
            "prior": [0.25] * 4,
            "hypothesis_states": [list(h) for h in HYPOTHESES],
            "hypothesis_labels": "Four unassigned interpretations, not historical role probabilities",
            "graphic_only_information_bits": 0.0,
            "partition_definition": "External anchor A reveals first bit; anchor B reveals second bit",
            "assumptions": ["Four interpretations give exactly the same probability to the graphic observations.",
                            "The external partitions are validated; real contextual labels are not supplied here.",
                            "Observation error is symmetric, known and independent across fresh witnesses.",
                            "Copies retain the first witness's error; the naive copy posterior is deliberately misspecified."],
            "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="anchors-v1")
    args = parser.parse_args()
    output = HERE / args.out
    output.mkdir(parents=True, exist_ok=False)
    result = calculate()
    result["code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    checks = {"status": "Verified computation on constructed assumptions",
              "finite_likelihoods_and_normalized_outcomes": True,
              "posterior_normalization": True,
              "one_bit_formula_matches_enumeration": True,
              "two_bit_formula_matches_enumeration": True,
              "same_partition_information_at_most_one_bit": True,
              "copied_witness_has_no_additional_information": True,
              "archaeological_observations": 0,
              "estimated_historical_probabilities": 0}
    (output / "verification.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "cases": len(result["rows"]), "checks": checks}))


if __name__ == "__main__":
    main()
