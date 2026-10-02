"""Exact binomial masses for paired-face agreement and high-precision moments."""
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration/noisy-channel"


def run():
    output = FOLDER / "exact-agreement-estimator"
    if output.exists():
        raise FileExistsError("Refusing an existing agreement-estimator endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    h = Fraction(142, 175)
    masses = [math.comb(60, k) * h ** k * (1 - h) ** (60 - k) for k in range(61)]
    assert sum(masses) == 1
    assert sum(k * probability for k, probability in enumerate(masses)) == 60 * h
    assert sum((Fraction(k) - 60 * h) ** 2 * probability for k, probability in enumerate(masses)) == 60 * h * (1 - h)
    estimates = [7 / 8 * (1 - math.sqrt(max(0, (8 * k / 60 - 1) / 7))) for k in range(61)]
    mean = sum(float(mass) * value for mass, value in zip(masses, estimates))
    mae = sum(float(mass) * abs(value - .1) for mass, value in zip(masses, estimates))
    mse = sum(float(mass) * (value - .1) ** 2 for mass, value in zip(masses, estimates))
    variance = sum(float(mass) * (value - mean) ** 2 for mass, value in zip(masses, estimates))
    with localcontext() as context:
        context.prec = 70
        decimal_masses = [Decimal(value.numerator) / Decimal(value.denominator) for value in masses]
        decimal_estimates = [Decimal(7) / 8 * (1 - max(Decimal(0), (Decimal(8) * k / 60 - 1) / 7).sqrt()) for k in range(61)]
        decimal_mean = sum(mass * value for mass, value in zip(decimal_masses, decimal_estimates))
        decimal_mae = sum(mass * abs(value - Decimal('.1')) for mass, value in zip(decimal_masses, decimal_estimates))
        decimal_mse = sum(mass * (value - Decimal('.1')) ** 2 for mass, value in zip(decimal_masses, decimal_estimates))
        decimal_variance = sum(mass * (value - decimal_mean) ** 2 for mass, value in zip(decimal_masses, decimal_estimates))
    assert max(abs(a - float(b)) for a, b in [(mean, decimal_mean), (mae, decimal_mae), (mse, decimal_mse), (variance, decimal_variance)]) < 1e-14
    outside = sum(mass for k, mass in enumerate(masses) if Fraction(k, 60) < Fraction(1, 8))
    rows = [{"agreements": k, "probability_exact": str(mass), "probability_decimal": float(mass),
             "rate_estimate": estimates[k], "rate_estimate_high_precision": str(decimal_estimates[k])} for k, mass in enumerate(masses)]
    result = {"status": "passed", "simulation": True, "pairs": 60, "agreement_probability_exact": str(h),
              "true_epsilon": .1, "mean": mean, "bias": mean - .1, "mean_absolute_error": mae,
              "mean_squared_error": mse, "variance": variance, "standard_deviation": math.sqrt(variance),
              "mean_standard_error_for_1000_populations": math.sqrt(variance / 1000),
              "zero_rate_probability_exact": str(masses[60]), "zero_rate_probability": float(masses[60]),
              "outside_domain_probability_exact": str(outside), "outside_domain_probability": float(outside),
              "high_precision_moments": {"mean": str(decimal_mean), "mae": str(decimal_mae), "mse": str(decimal_mse), "variance": str(decimal_variance)},
              "distribution": rows, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "protocol_sha256": hashlib.sha256((FOLDER / "AGREEMENT_SAMPLING_CHECK.md").read_bytes()).hexdigest()}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["status", "mean", "bias", "mean_absolute_error", "mean_squared_error", "zero_rate_probability", "outside_domain_probability"]}), flush=True)


if __name__ == "__main__":
    run()
