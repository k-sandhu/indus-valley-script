"""Exact deduplicated-selection law using frozen unique-space fit scores."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil

HERE = Path(__file__).parent
EXACT = HERE.parent / "exact"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational_tails(values, probabilities):
    mass = Counter()
    for value, probability in zip(values, probabilities):
        mass[value] += probability
    tails, cumulative = {}, Fraction(0)
    for value in sorted(mass, reverse=True):
        cumulative += mass[value]
        tails[value] = cumulative
    assert cumulative == 1
    return [tails[value] for value in values]


def calibration(p_values, probabilities):
    distribution = Counter()
    for p, mass in zip(p_values, probabilities):
        distribution[p] += mass
    cumulative, greatest = Fraction(0), {"departure": Fraction(-1)}
    for p in sorted(distribution):
        cumulative += distribution[p]
        if cumulative - p > greatest["departure"]:
            greatest = {"departure": cumulative - p, "cutoff": p, "rejection_probability": cumulative}
    return {"rates": {str(float(alpha)): str(sum(mass for p, mass in zip(p_values, probabilities) if p <= alpha))
                      for alpha in [Fraction(1, 100), Fraction(1, 20), Fraction(1, 10), Fraction(1, 4)]},
            "greatest_attainable_excess": {key: str(value) for key, value in greatest.items()}}


def main():
    destination = HERE / "results.json"
    if destination.exists():
        raise FileExistsError("Frozen selection endpoint already exists")
    inputs = {name: sha(EXACT / name) for name in ["results.json", "tables_and_sampler_counts.json", "unique_nested_scores.json"]}
    tables = json.loads((EXACT / "tables_and_sampler_counts.json").read_text(encoding="utf-8"))
    nested = json.loads((EXACT / "unique_nested_scores.json").read_text(encoding="utf-8"))
    slot_p = [Fraction(1, 5), Fraction(3, 10), Fraction(2, 5)]
    strings = list(itertools.product([0, 1], repeat=3))
    q = {string: math.prod(p if sign else 1 - p for p, sign in zip(slot_p, string)) for string in strings}
    assert sum(q.values()) == 1
    supports = []
    for retained in itertools.combinations(strings, 6):
        if all(sum(string[slot] for string in retained) == 3 for slot in range(3)):
            raw = []
            for duplicated in retained:
                probability = Fraction(math.factorial(7), 2) * math.prod(q[string] for string in retained) * q[duplicated]
                raw.append({"duplicated_string": duplicated, "raw_orderings": math.factorial(7) // 2,
                            "probability": probability})
            probability = sum(row["probability"] for row in raw)
            formula = Fraction(math.factorial(7), 2) * math.prod(q[string] for string in retained) * sum(q[string] for string in retained)
            assert probability == formula
            supports.append({"retained": retained, "omitted": tuple(string for string in strings if string not in retained),
                             "raw_probability": probability, "raw_occupancies": raw,
                             "sum_member_probabilities": sum(q[string] for string in retained)})
    assert len(supports) == 4
    normalization = sum(row["raw_probability"] for row in supports)
    by_support = {frozenset(row["retained"]): row["raw_probability"] / normalization for row in supports}
    indices = [index for index, selected in enumerate(tables["whole_string_unique"]) if selected]
    assert len(indices) == 2880 and {row["table_index"] for row in nested} == set(indices)
    gain_lookup = {row["table_index"]: row["gain"] for row in nested}
    probabilities, integer, gains, rows = [], [], [], []
    for index in indices:
        table = tuple(tuple(row) for row in tables["tables"][index])
        probability = by_support[frozenset(table)] / math.factorial(6)
        probabilities.append(probability)
        integer.append(tables["integer_statistic"][index])
        gains.append(gain_lookup[index])
        rows.append({"table_index": index, "selected_probability": str(probability), "integer_score": integer[-1], "nested_gain": gains[-1]})
    assert sum(probabilities) == 1
    uniform = [Fraction(1, len(indices))] * len(indices)
    endpoints = {}
    for name, values in [("integer_adjacency", integer), ("nested_full_procedure", gains)]:
        uniform_tails = rational_tails(values, uniform)
        selected_tails = rational_tails(values, probabilities)
        endpoints[name] = {"uniform_reference_under_uniform_law": calibration(uniform_tails, uniform),
                           "uniform_reference_under_selected_law": calibration(uniform_tails, probabilities),
                           "selected_reference_under_selected_law": calibration(selected_tails, probabilities)}
        assert Fraction(endpoints[name]["selected_reference_under_selected_law"]["greatest_attainable_excess"]["departure"]) <= 0
        for row, uniform_p, selected_p in zip(rows, uniform_tails, selected_tails):
            row[name + "_uniform_p"] = str(uniform_p)
            row[name + "_selected_p"] = str(selected_p)
    for support in supports:
        support["conditional_probability"] = by_support[frozenset(support["retained"])]
    def serialize(value):
        if isinstance(value, Fraction):
            return str(value)
        raise TypeError(type(value))
    source = Path(__file__)
    shutil.copyfile(source, HERE / "code_snapshot.py")
    output = {"source_sha256": sha(source), "input_sha256": inputs, "raw_draws": 7, "retained_distinct_strings": 6,
              "slot_probabilities": list(map(str, slot_p)), "raw_conditioning_event_probability": str(normalization),
              "raw_occupancy_vectors": sum(len(support["raw_occupancies"]) for support in supports),
              "raw_ordered_datasets": sum(row["raw_orderings"] for support in supports for row in support["raw_occupancies"]),
              "supports": supports, "tables": rows, "endpoints": endpoints,
              "checks": ["complete_support_occupancy_enumeration", "deduplication_probability_formula",
                         "uniform_labeling", "source_table_correspondence", "rational_tail_counting",
                         "matched_selected_tail_validity"]}
    destination.write_text(json.dumps(output, indent=2, default=serialize) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key not in ["tables", "supports"]}))


if __name__ == "__main__":
    main()
