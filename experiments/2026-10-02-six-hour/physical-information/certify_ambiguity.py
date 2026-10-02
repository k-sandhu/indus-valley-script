"""Post-run certificates for the rational ambiguity retained by missing data."""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import json


def dot(row, vector):
    return sum(a * v for a, v in zip(row, vector))


def primitive(vector):
    denominator = lcm(*(v.denominator for v in vector))
    values = [int(v * denominator) for v in vector]
    divisor = gcd(*values)
    return [v // divisor for v in values]


def main():
    folder = Path("experiments/2026-10-02-six-hour/physical-information")
    output = folder / "ambiguity-certificates.json"
    if output.exists():
        raise FileExistsError(output)
    results = json.loads((folder / "main/results.json").read_text())
    worlds = {w["seed"]: w for w in json.loads((folder / "main/worlds.json").read_text())}
    certificates = []
    for record in results["records"]:
        if record["scenario"] != "incomplete_recorded" or record["training_relations"] != 12 or record["rational"]["rank"] >= 5:
            continue
        truth = [Fraction(v) for v in worlds[record["seed"]]["concealed_values_by_code"]]
        anchor = record["rational"]["anchor"]["code"]
        basis = [[Fraction(x) for x in row] for row in record["rational"]["rational_nullspace_basis"]]
        direction = next((row for row in basis if row[anchor] == 0), None)
        if direction is None:
            for first, second in combinations(basis, 2):
                candidate = [a * second[anchor] - b * first[anchor] for a, b in zip(first, second)]
                if any(candidate):
                    direction = candidate
                    break
        assert direction is not None and any(direction) and direction[anchor] == 0
        bounds = [v / -d for v, d in zip(truth, direction) if d < 0]
        for row in record["training_inequality_matrix"]:
            slack, change = dot(row, truth), dot(row, direction)
            assert slack > 0
            if change < 0:
                bounds.append(slack / -change)
        step = min([Fraction(1)] + [bound / 2 for bound in bounds])
        alternative = [v + step * d for v, d in zip(truth, direction)]
        assert all(v > 0 for v in alternative)
        assert alternative[anchor] == truth[anchor]
        assert all(dot(row, alternative) == 0 for row in record["training_equality_matrix"])
        assert all(dot(row, alternative) >= 0 for row in record["training_inequality_matrix"])
        integer_ray = primitive(alternative)
        assert integer_ray != primitive(truth)
        assert all(dot(row, integer_ray) == 0 for row in record["training_equality_matrix"])
        assert all(dot(row, integer_ray) >= 0 for row in record["training_inequality_matrix"])
        certificates.append({
            "seed": record["seed"],
            "equality_rank": record["rational"]["rank"],
            "finite_known_bag_candidates": record["finite"]["training_compatible_maps"],
            "answer_values": [str(v) for v in truth],
            "anchor_code": anchor,
            "anchor_preserving_direction": [str(v) for v in direction],
            "positive_step": str(step),
            "alternative_positive_rational_values_with_same_anchor": [str(v) for v in alternative],
            "alternative_positive_integer_relative_ray": integer_ray,
            "all_equalities_and_inequalities_pass": True,
            "all_withheld_relations_pass_for_alternative": all(dot(row, alternative) == 0 for row in record["withheld_equality_matrix"]),
        })
    report = {
        "status": "post-outcome-exact-certificates",
        "purpose": "Exhibit alternatives for every underidentified full-prefix incomplete-content world.",
        "scope": "The anchored alternatives use positive rational quantities. Their primitive integer rays demonstrate different unanchored relative assignments. Integer-only anchored uniqueness is not tested here.",
        "certificate_count": len(certificates),
        "certificates": certificates,
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "certificates": len(certificates), "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
