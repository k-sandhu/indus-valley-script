"""Exact conditional audit of two proposed Fuls2020 numerical equalities.

This does not validate the proposed graphic readings, positional multipliers,
same-quantity assumptions, or any linguistic value. Arithmetic uses integers
and Fraction; an exhaustive divisor argument makes enumeration unbounded.
"""
from fractions import Fraction
import json
from pathlib import Path

from conditional_structure import digest


SOURCE_URL = "https://www.researchgate.net/profile/Andreas-Fuls/publication/373522958_Ancient_Writing_and_Modern_Technologies_-_Structural_Analysis_of_Numerical_Indus_Inscriptions/links/64f04b160f7ab20a8667db0b/Ancient-Writing-and-Modern-Technologies-Structural-Analysis-of-Numerical-Indus-Inscriptions.pdf"


def exact_solutions():
    # d=2L-7. 4(L^2+4)=d(2L+7)+65, so d divides 65.
    # Every integer solution is therefore among these eight signed divisors.
    divisors = sorted({sign * d for sign in [-1, 1] for d in [1, 5, 13, 65]})
    result = []
    for d in divisors:
        L = Fraction(d + 7, 2)
        S = (L * L + 4) / d
        v = 2 * S - L
        if all(x.denominator == 1 for x in [L, S, v]):
            L, S, v = int(L), int(S), int(v)
            assert v == 2*S-L and v*L+1 == 7*S+5
            result.append({"L": L, "S": S, "v": v, "d": d})
    return sorted(result, key=lambda r: r["L"])


def main():
    all_solutions = exact_solutions()
    admissible = [r for r in all_solutions if r["L"] > 0 and r["S"] >= 8 and r["v"] > 0]
    # Independent bounded brute force checks the proof implementation and
    # covers every positive divisor-generated solution, without being the
    # basis of the unbounded completeness claim.
    brute = []
    for L in range(1, 1001):
        for S in range(8, 1001):
            v = 2*S-L
            if v > 0 and v*L+1 == 7*S+5:
                brute.append({"L": L, "S": S, "v": v, "d": 2*L-7})
    assert brute == admissible
    ranges = {f"L_{a}_to_{b}": [r for r in admissible if a <= r["L"] <= b]
              for a, b in [(8, 13), (8, 18), (8, 35), (8, 36), (1, 1000)]}
    parity_counterexample = {"L": 10, "S": 9, "v": 8}
    assert parity_counterexample["v"] == 2*parity_counterexample["S"]-parity_counterexample["L"]
    assert parity_counterexample["S"] % 2 == 1
    result = {
        "scope": "Exact conditional arithmetic constraint audit; no new decoded numeral or priority claim.",
        "source_sha256": digest(__file__), "source_url": SOURCE_URL,
        "source_editions": {"original_chapter": "Fuls2020, bibliographic pp57-90", "verified_author_posted_reprint": "2023 posting, printed pp15-48; all following coordinates refer to this linked PDF"},
        "source_locations": {"bangle_range": "2023 reprint printed pp28-29, PDF pages14-15 (1-indexed), Fig15/Eq1", "first_equality": "2023 reprint printed p30, PDF page16, Fig16/Eq2", "sum_relation": "2023 reprint printed p32, PDF page18, Fig18"},
        "variables": {"L": "hypothesized value/base multiplier of a long stroke", "S": "hypothesized higher-position multiplier of a short stroke", "v": "hypothesized unit value of W900"},
        "assumed_equalities": ["v=2*S-L", "v*L+1=7*S+5"],
        "derived_relation": "S=(L^2+4)/(2*L-7)",
        "unbounded_completeness_argument": [
            "Set d=2*L-7. Integer L makes d odd and nonzero.",
            "4*(L^2+4)=d*(2*L+7)+65. Integer S therefore requires d to divide 65.",
            "All signed divisors are -65,-13,-5,-1,1,5,13,65; each is explicitly tested with Fraction arithmetic.",
            "S>0 implies d>0 because L^2+4 is positive. Thus only four positive divisors remain.",
        ],
        "all_integer_solutions": all_solutions,
        "admissibility": "L positive integer, S integer at least8, v positive integer; no even/prime restriction",
        "all_admissible_solutions": admissible,
        "range_sensitivities": ranges,
        "digit_maximum_assumption_L_at_least10": [r for r in admissible if r["L"] >= 10],
        "redundant_assumptions_in_exact_joint_system": [
            "All positive-integer solutions already have S>=8 and v>0.",
            "All four admissible L values are composite; excluding prime bases adds no restriction here.",
            "Both L8..13 and the wider L8..18 leave exactly (L,S,v)=(10,8,6).",
        ],
        "first_equality_parity_audit": {
            "correct_implication": "Integer S=(v+L)/2 implies v and L share parity, not that S is even.",
            "odd_S_counterexample": parity_counterexample,
            "note": "The four positive joint-system solutions happen to have even S as a result, not a premise.",
        },
        "source_assumption_chain": [
            "ICIT3786: assign coefficients3 and2 to long-stroke groups,2 to the higher-position short group, and v to W900; equate quantities on two faces bearing different other glyphs.",
            "M331: assign five stacked strokes to5, four short strokes to4*S, three short strokes to3*S, W900+one short stroke to v*L+1; equate the latter to the sum of the first two expressions.",
            "M1383: associate 017/031 with7+L and identify that expression with a reconstructed bangle total, yielding assumed L8..13 or a stated wider range.",
        ],
        "source_cautions": [
            "The source describes three long strokes on ICIT3786 while labelling them032; that code/count discrepancy requires source-image adjudication.",
            "ICIT3786 is the published paper's identifier, not a safely matched current Lipi numeric ID; its physical/CISI identity remains unresolved in this audit.",
            "Physical grouping and surviving stroke counts do not establish equal quantities, positional ranks, addition or the bangle referent.",
            "Without a range or other independently grounded restriction, the exact equations leave four positive solutions, not a uniquely decoded decimal base.",
            "These equations and their selected solution are published prior. Removing unnecessary prime/parity premises is an arithmetic audit, not semantic decipherment.",
        ],
        "falsifiable_followup": [
            "Freeze graphic coefficients, positional assignments and equal-quantity rules before reading an independent object.",
            "Validate ICIT3786's three-versus-two group and every M331 physical side/line against accessible source images.",
            "Test an independently identified total/parts object with the same fixed units and operations, and report exceptions without changing multipliers or referents.",
        ],
        "brute_force_check": {"L_range": [1, 1000], "S_range": [8, 1000], "matches_proven_solution_set": True},
    }
    out = Path("research/methods/results/numerical_equalities")
    out.mkdir(parents=True, exist_ok=True)
    (out / "numerical_equalities_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"admissible": admissible, "ranges": ranges, "parity_counterexample": parity_counterexample}, indent=2))


if __name__ == "__main__":
    main()
