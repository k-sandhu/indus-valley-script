"""Rational two-observer identification and a uniform-frequency ambiguity."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration/noisy-channel"


def pair_distribution(p, first, second):
    return [[sum(p[x] * (1 - first if x == a else first / 7) * (1 - second if x == b else second / 7) for x in range(8))
             for b in range(8)] for a in range(8)]


def root(value):
    numerator, denominator = math.isqrt(value.numerator), math.isqrt(value.denominator)
    assert numerator ** 2 == value.numerator and denominator ** 2 == value.denominator
    return Fraction(numerator, denominator)


def run():
    output = FOLDER / "unequal-rates-limit"
    if output.exists():
        raise FileExistsError("Refusing an existing identification-limit endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    p = [Fraction(x, 100) for x in [20, 16, 14, 12, 11, 10, 9, 8]]
    rates = [Fraction(1, 10), Fraction(1, 5)]
    probability = pair_distribution(p, *rates)
    assert sum(map(sum, probability)) == 1
    marginals = [[sum(probability[a][b] for b in range(8)) for a in range(8)],
                 [sum(probability[a][b] for a in range(8)) for b in range(8)]]
    centered = [[value - Fraction(1, 8) for value in marginal] for marginal in marginals]
    ratio = next(a / b for a, b in zip(*centered) if b != 0)
    assert all(a == ratio * b for a, b in zip(*centered))
    agreement = sum(probability[x][x] for x in range(8))
    product = (8 * agreement - 1) / 7
    first, second = root(product * ratio), root(product / ratio)
    recovered = [(1 - attenuation) * Fraction(7, 8) for attenuation in [first, second]]
    recovered_p = [Fraction(1, 8) + value / first for value in centered[0]]
    assert recovered == rates and recovered_p == p
    alternative = [Fraction(7, 40), Fraction(143, 1120)]
    uniform = [Fraction(1, 8)] * 8
    first_uniform, second_uniform = pair_distribution(uniform, *rates), pair_distribution(uniform, *alternative)
    assert first_uniform == second_uniform
    assert rates != alternative
    assert all(sum(first_uniform[a]) == Fraction(1, 8) for a in range(8))
    result = {"status": "passed", "simulation": True, "limit_calculation": True,
              "nonuniform_rates": list(map(str, rates)), "recovered_rates": list(map(str, recovered)),
              "recovered_p": list(map(str, recovered_p)), "attenuation_ratio": str(ratio), "attenuation_product": str(product),
              "uniform_alternative_rates": list(map(str, alternative)), "uniform_joint_probability": [[str(value) for value in row] for row in first_uniform],
              "uniform_pair_entry_equalities_checked": 64,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "design_note_sha256": hashlib.sha256((FOLDER / "IDENTIFICATION.md").read_bytes()).hexdigest()}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "recovered_rates": result["recovered_rates"], "attenuation_product": str(product), "uniform_alternative_rates": result["uniform_alternative_rates"]}), flush=True)


if __name__ == "__main__":
    run()
