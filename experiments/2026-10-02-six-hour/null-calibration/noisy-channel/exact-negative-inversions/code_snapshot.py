"""Rational absence probabilities and an independent category-mask recurrence."""
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration/noisy-channel"


def run():
    output = FOLDER / "exact-negative-inversions"
    if output.exists():
        raise FileExistsError("Refusing an existing absence-probability endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    p = [Fraction(x, 100) for x in [20, 16, 14, 12, 11, 10, 9, 8]]
    t = Fraction(1, 70)
    q = {}
    for mask in range(256):
        size = mask.bit_count()
        mass = sum(p[x] for x in range(8) if mask & (1 << x))
        q[mask] = mass * ((8 - size) * t) ** 2 + (1 - mass) * (1 - size * t) ** 2
    coverage = sum((-1) ** mask.bit_count() * probability ** 10 for mask, probability in q.items())
    absent = [q[1 << x] ** 10 for x in range(8)]
    mean_absent = sum(absent)
    variance_absent = sum(value * (1 - value) for value in absent)
    variance_absent += 2 * sum(q[(1 << a) | (1 << b)] ** 10 - absent[a] * absent[b] for a in range(8) for b in range(a + 1, 8))
    # Construct each ordered-pair probability from its latent alternatives.
    pair = {}
    increments = defaultdict(Fraction)
    for a in range(8):
        for b in range(8):
            value = sum(p[x] * (Fraction(9, 10) if x == a else t) * (Fraction(9, 10) if x == b else t) for x in range(8))
            pair[(a, b)] = value
            increments[(1 << a) | (1 << b)] += value
    assert sum(pair.values()) == 1
    assert sum(pair[(a, a)] for a in range(8)) == Fraction(142, 175)
    for mask in range(256):
        assert q[mask] == sum(value for (a, b), value in pair.items() if not (mask & (1 << a) or mask & (1 << b)))
    distribution = {0: Fraction(1)}
    for step in range(10):
        changed = defaultdict(Fraction)
        for mask, mass in distribution.items():
            for added, probability in increments.items():
                changed[mask | added] += mass * probability
        distribution = dict(changed)
        assert sum(distribution.values()) == 1
    assert distribution[255] == coverage
    assert sum((8 - mask.bit_count()) * mass for mask, mass in distribution.items()) == mean_absent
    assert sum((8 - mask.bit_count()) ** 2 * mass for mask, mass in distribution.items()) - mean_absent ** 2 == variance_absent
    values = {"cell_coverage_probability": coverage, "cell_affected_probability": 1 - coverage,
              "population_affected_probability": 1 - coverage ** 6,
              "expected_negative_components_per_population": 6 * mean_absent,
              "expected_affected_cells_per_population": 6 * (1 - coverage),
              "negative_component_variance_per_population": 6 * variance_absent}
    result = {"status": "passed", "simulation": True, "objects_per_cell": 10, "cells_per_population": 6,
              "exact_values": {name: str(value) for name, value in values.items()},
              "decimal_values": {name: float(value) for name, value in values.items()},
              "negative_components_mean_standard_error_for_1000_populations": math.sqrt(float(6 * variance_absent) / 1000),
              "singleton_absence_probabilities": [str(value) for value in absent],
              "category_mask_distribution": {str(mask): str(value) for mask, value in distribution.items()},
              "all_subset_absence_probabilities": {str(mask): str(value) for mask, value in q.items()},
              "independent_checks": ["64 ordered pair probabilities", "256 subset probabilities", "10 probability-preserving mask steps",
                                     "coverage probability", "first absence moment", "second absence moment"],
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "protocol_sha256": hashlib.sha256((FOLDER / "NEGATIVE_INVERSION_CHECK.md").read_bytes()).hexdigest()}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", **result["decimal_values"]}), flush=True)


if __name__ == "__main__":
    run()
