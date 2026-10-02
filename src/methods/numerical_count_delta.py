"""Exact sensitivity to the ICIT3786 long-stroke coefficient difference.

The selected numerical interpretation is assumed throughout. Hypothetical
coefficients are not asserted as independently verified graphic readings.
"""
from fractions import Fraction
import json
from pathlib import Path

from conditional_structure import digest


def solutions(delta):
    # v=2S-delta*L and vL+1=7S+5 imply
    # (2L-7)S=delta*L^2+4.
    # 4(delta*L^2+4)=delta*(2L-7)*(2L+7)+49delta+16.
    n = 49*delta+16
    output = []
    for d in range(1, n+1, 2):
        if n % d:
            continue
        L = Fraction(d+7, 2)
        S = (delta*L*L+4)/d
        v = 2*S-delta*L
        if all(x.denominator == 1 for x in [L, S, v]) and S > 0 and v > 0:
            L, S, v = int(L), int(S), int(v)
            assert v == 2*S-delta*L and v*L+1 == 7*S+5
            output.append({"L": L, "S": S, "v": v})
    return output


def main():
    cases = {}
    for delta in [0, 1, 2]:
        all_positive = solutions(delta)
        eligible = [r for r in all_positive if r["S"] >= 8]
        cases[str(delta)] = {
            "hypothetical_first_side_long_strokes": 2+delta,
            "second_side_long_strokes": 2,
            "first_relation": f"v=2*S-{delta}*L",
            "all_positive_integer_solutions": all_positive,
            "S_at_least8": eligible,
            "L8_to13_and_S_at_least8": [r for r in eligible if 8 <= r["L"] <= 13],
            "L8_to18_and_S_at_least8": [r for r in eligible if 8 <= r["L"] <= 18],
        }
    result = {
        "scope": "Hypothetical graphic-coefficient sensitivity; no graphic adjudication or decoded value.",
        "source_sha256": digest(__file__),
        "fixed_second_relation": "v*L+1=7*S+5",
        "general_relation": "(2*L-7)*S=delta*L^2+4",
        "completeness": "For nonnegative delta and S>0, d=2L-7>0 and divides49*delta+16; every positive odd divisor is explicitly checked.",
        "cases": cases,
        "interpretation": "A count2-versus3 premise changes existence/values of the selected-range solution. The original paper's W032 label versus three-stroke description must be resolved physically before interpreting its arithmetic constraint.",
    }
    output = Path("research/methods/results/numerical_equalities/numerical_count_delta_sensitivity.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
