"""Finite distinction between two declared prototype sampling procedures.

All symbols and carriers are invented. No Indus source data are embedded.
"""
from collections import Counter
from itertools import permutations
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def selected_bundles(slots):
    return tuple(sorted({tuple(sorted(slots[i:i + 2])) for i in range(0, len(slots), 2)}))


def main(out_name):
    full_slots = ("A", "B", "A", "B", "C", "D")
    observed_prototypes = selected_bundles(full_slots)
    prototype_bag = Counter(x for bundle in observed_prototypes for x in bundle)
    original_allocations = set(permutations(full_slots))
    induced = Counter()
    for slots in original_allocations:
        selected = selected_bundles(slots)
        if len(selected) == 2 and Counter(x for pair in selected for x in pair) == prototype_bag:
            induced[selected] += 1
    prototype_allocations = set(permutations(tuple(prototype_bag.elements())))
    declared = Counter()
    for slots in prototype_allocations:
        selected = selected_bundles(slots)
        if len(selected) == 2:
            declared[selected] += 1
    n_induced, n_declared = sum(induced.values()), sum(declared.values())
    all_states = sorted(set(induced) | set(declared))
    rows = [{"invented_prototype_bundles": state,
             "original_bag_permute_then_select_conditional_probability": induced[state] / n_induced,
             "selected_bag_permute_with_uniqueness_probability": declared[state] / n_declared}
            for state in all_states]
    variation = 0.5 * sum(abs(row["original_bag_permute_then_select_conditional_probability"] -
                              row["selected_bag_permute_with_uniqueness_probability"]) for row in rows)
    assert len(original_allocations) == 180 and n_induced == 24
    assert len(prototype_allocations) == 24 and n_declared == 24
    assert len(induced) == 1 and len(declared) == 3
    assert abs(variation - 2 / 3) < 1e-12
    result = {"status": "synthetic finite counterexample",
              "original_carriers": [["A", "B"], ["A", "B"], ["C", "D"]],
              "allocation_cell": "one common site, type, two-face count and (1,1) length profile",
              "selection": "retain one representative per exact unordered bundle",
              "conditioning_for_induced_law": "two retained prototypes with selected module bag A,B,C,D",
              "original_distinct_labeled_slot_allocations": len(original_allocations),
              "original_allocations_satisfying_condition": n_induced,
              "selected_bag_distinct_labeled_slot_allocations": len(prototype_allocations),
              "distributions": rows, "total_variation_distance": variation,
              "conclusion": "Uniqueness-conditioned allocation of the selected prototype bag is a valid separately declared reference law. It need not equal the induced law from allocating the original copy-weighted bag and then selecting prototypes. This counterexample challenges an interpretation of the law, not the calculation of tails under the stated law."}
    output = HERE / out_name
    if output.exists():
        raise FileExistsError("Preserve the earlier enumeration and choose a fresh --out file")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"original_allocations": 180, "conditioning_event_allocations": 24,
                      "induced_states": 1, "selected_bag_states": 3,
                      "total_variation": variation}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="prototype-counterexample-recheck.json")
    main(parser.parse_args().out)
