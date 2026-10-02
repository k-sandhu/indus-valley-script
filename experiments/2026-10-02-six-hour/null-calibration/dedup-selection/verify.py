"""Seven-draw seen-set recurrence and independent exact tail verification."""
from bisect import bisect_left
from collections import defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent


def main():
    result = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    for source in [HERE / "run.py", HERE / "code_snapshot.py"]:
        assert hashlib.sha256(source.read_bytes()).hexdigest() == result["source_sha256"]
    for name, expected in result["input_sha256"].items():
        assert hashlib.sha256((HERE.parent / "exact" / name).read_bytes()).hexdigest() == expected
    strings = list(itertools.product([0, 1], repeat=3))
    q = []
    for string in strings:
        probability = Fraction(1)
        for sign, p in zip(string, map(Fraction, result["slot_probabilities"])):
            probability *= p if sign else 1 - p
        q.append(probability)
    states = {0: Fraction(1)}
    for _ in range(7):
        changed = defaultdict(Fraction)
        for mask, mass in states.items():
            for index, probability in enumerate(q):
                changed[mask | (1 << index)] += mass * probability
        states = changed
    assert sum(states.values()) == 1
    valid = {mask: mass for mask, mass in states.items() if mask.bit_count() == 6
             and all(sum(strings[index][slot] for index in range(8) if mask & (1 << index)) == 3 for slot in range(3))}
    assert len(valid) == 4
    total = sum(valid.values())
    assert total == Fraction(result["raw_conditioning_event_probability"])
    table_source = json.loads((HERE.parent / "exact/tables_and_sampler_counts.json").read_text(encoding="utf-8"))
    for support in result["supports"]:
        mask = sum(1 << strings.index(tuple(string)) for string in support["retained"])
        assert valid[mask] == Fraction(support["raw_probability"])
        assert valid[mask] / total == Fraction(support["conditional_probability"])
    probabilities = []
    for row in result["tables"]:
        table = table_source["tables"][row["table_index"]]
        mask = sum(1 << strings.index(tuple(string)) for string in table)
        probability = valid[mask] / total / 720
        assert probability == Fraction(row["selected_probability"])
        probabilities.append(probability)
    assert sum(probabilities) == 1
    for name, score_field in [("integer_adjacency", "integer_score"), ("nested_full_procedure", "nested_gain")]:
        ordering = sorted(range(2880), key=lambda index: result["tables"][index][score_field])
        values = [result["tables"][index][score_field] for index in ordering]
        prefix = [Fraction(0)]
        for index in ordering:
            prefix.append(prefix[-1] + probabilities[index])
        for row in result["tables"]:
            lower = bisect_left(values, row[score_field])
            assert Fraction(row[name + "_uniform_p"]) == Fraction(2880 - lower, 2880)
            assert Fraction(row[name + "_selected_p"]) == 1 - prefix[lower]
        for law, reference, mass in [("uniform_reference_under_uniform_law", "uniform", [Fraction(1, 2880)] * 2880),
                                     ("uniform_reference_under_selected_law", "uniform", probabilities),
                                     ("selected_reference_under_selected_law", "selected", probabilities)]:
            p_values = [Fraction(row[name + "_" + reference + "_p"]) for row in result["tables"]]
            for threshold, expected in result["endpoints"][name][law]["rates"].items():
                actual = sum(probability for p, probability in zip(p_values, mass) if p <= Fraction(threshold))
                assert actual == Fraction(expected)
    verification = {"status": "pass", "raw_draw_steps": 7, "support_masks": 4,
                    "labeled_tables": 2880, "individual_tails_checked": 11520,
                    "rejection_endpoints_checked": 24,
                    "checks": ["seen_support_probability_recurrence", "conditional_support_weights",
                               "labeled_table_masses", "sorted_prefix_rational_tails", "rejection_probabilities",
                               "source_correspondence"]}
    destination = HERE / "verification.json"
    if destination.exists():
        raise FileExistsError("Frozen selection verification already exists")
    destination.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verification))


if __name__ == "__main__":
    main()
