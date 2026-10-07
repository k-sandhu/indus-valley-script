"""Independent check of the arithmetic behind candidate 1 (FULS-ARITHMETIC).

Run from the repository root:
    python experiments/2026-10-06-byproduct-inventory/review/check_fuls_arithmetic.py

The two equalities are taken as the saved audit states them
(research/methods/results/numerical_equalities/numerical_equalities_audit.json,
"assumed_equalities"): v = 2S - L and vL + 1 = 7S + 5. The script does not
verify that these equalities are what the source chapter prints; the source
reprint could not be opened by the reviewer (ResearchGate returns HTTP 403 and no
local copy matches the SHA-256 recorded in the audit).
"""

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research" / "methods" / "results" / "numerical_equalities" / "numerical_equalities_audit.json"


def solutions(l_max=5000, s_max=20000):
    found = []
    for L in range(1, l_max + 1):
        den = 2 * L - 7
        if den <= 0:
            continue
        num = L * L + 4
        if num % den:
            continue
        S = num // den
        v = 2 * S - L
        if S >= 1 and v > 0 and v * L + 1 == 7 * S + 5:
            found.append((L, S, v))
    return found


def brute(l_max=300, s_max=1000):
    found = []
    for L in range(1, l_max + 1):
        for S in range(1, s_max + 1):
            v = 2 * S - L
            if v > 0 and v * L + 1 == 7 * S + 5:
                found.append((L, S, v))
    return found


def main():
    audit = json.load(open(AUDIT, encoding="utf-8-sig"))
    saved = sorted((s["L"], s["S"], s["v"]) for s in audit["all_admissible_solutions"])
    divisor_form = sorted(solutions())
    brute_force = sorted(brute())
    print("saved audit, admissible (L,S,v):", saved)
    print("divisor enumeration, L up to 5000:", divisor_form)
    print("brute force, L<=300, S<=1000:     ", brute_force)
    print("all three agree:", saved == divisor_form == brute_force)
    in_range = [t for t in divisor_form if 8 <= t[0] <= 13]
    print("solutions with 8 <= L <= 13:", in_range)
    # Parity step: integer S = (v + L)/2 makes v and L share parity; it does not make S even.
    counterexample = (10, 9, 8)
    L, S, v = counterexample
    print("first equality alone, S odd:", counterexample, "v == 2S - L:", v == 2 * S - L, "S even:", S % 2 == 0)
    # Closed form with d = 2L - 7 dividing 65
    print("positive divisors of 65:", [d for d in range(1, 66) if 65 % d == 0],
          "-> S = (L^2+4)/(2L-7) integer for d in", [d for d in (1, 5, 13, 65)
                                                    if Fraction((((d + 7) // 2) ** 2 + 4), d).denominator == 1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
