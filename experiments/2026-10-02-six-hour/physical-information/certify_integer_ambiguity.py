"""Post-outcome integer witnesses; preserve the preceding rational review."""

from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
import json


def dot(row, vector):
    return sum(a * v for a, v in zip(row, vector))


def main():
    folder = Path("experiments/2026-10-02-six-hour/physical-information")
    output = folder / "integer-ambiguity-certificates.json"
    if output.exists():
        raise FileExistsError(output)
    preceding = json.loads((folder / "ambiguity-certificates.json").read_text())
    results = json.loads((folder / "main/results.json").read_text())
    certificates = []
    for witness in preceding["certificates"]:
        record = next(r for r in results["records"] if r["seed"] == witness["seed"]
                      and r["scenario"] == "incomplete_recorded" and r["training_relations"] == 12)
        truth = [int(x) for x in witness["answer_values"]]
        direction = [Fraction(x) for x in witness["anchor_preserving_direction"]]
        denominator = lcm(*(x.denominator for x in direction))
        integers = [int(x * denominator) for x in direction]
        divisor = gcd(*integers)
        integers = [x // divisor for x in integers]
        alternatives = []
        for step in (-2, -1, 1, 2):
            values = [v + step * d for v, d in zip(truth, integers)]
            if (all(v > 0 for v in values)
                    and all(dot(row, values) == 0 for row in record["training_equality_matrix"])
                    and all(dot(row, values) >= 0 for row in record["training_inequality_matrix"])):
                assert values[witness["anchor_code"]] == truth[witness["anchor_code"]]
                assert values != truth
                alternatives.append({
                    "integer_values": values,
                    "direction_step": step,
                    "also_passes_all_withheld_relations": all(dot(row, values) == 0 for row in record["withheld_equality_matrix"]),
                })
        assert alternatives
        certificates.append({
            "seed": witness["seed"],
            "answer_values": truth,
            "anchor_code": witness["anchor_code"],
            "observed_anchor_count": truth[witness["anchor_code"]],
            "alternative_positive_integer_assignments": alternatives,
            "finite_known_value_bag_candidates": record["finite"]["training_compatible_maps"],
            "all_candidates_obey_training_equalities_inequalities_and_count": True,
        })
    report = {
        "status": "post-outcome-exact-integer-certificates",
        "method": "Integerize each preceding nullspace direction and check steps -2, -1, 1, 2 exactly.",
        "scope": "Constructive counterexamples for the seven retained cases; the listed alternatives are not an exhaustive integer solution count.",
        "certificate_count": len(certificates),
        "certificates": certificates,
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "certificates": len(certificates), "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
