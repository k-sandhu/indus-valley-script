"""Known answers, nominal-rate simulations and sealed-loader failure cases."""
import math
from pathlib import Path
import tempfile

from .common import envelope, positive_int


def configure(ap):
    ap.add_argument("--directory", type=Path, help="New directory to retain synthetic shot fixtures")
    ap.add_argument("--permutations", type=positive_int, default=199)
    ap.add_argument("--trials", type=positive_int, default=100)


def run(args):
    from . import key_calibration, meaning_map, restoration, segmentation, shots
    key = key_calibration.synthetic(draws=args.permutations)
    rows, mapping, predictions = meaning_map.synthetic_data(1.5, 20261013)
    meaning = meaning_map.evaluate(rows, mapping, predictions, args.permutations)
    zero = meaning_map.evaluate(*meaning_map.synthetic_data(0., 20261013), draws=args.permutations)
    power = meaning_map.power((0., .25, .5, 1.5), args.trials, args.permutations)
    rate = power[0]["rate"]
    # Predeclared binomial sampling tolerance; the measured interval is also retained.
    tolerance = 3 * math.sqrt(.05 * .95 / args.trials) + 1 / args.trials
    calibrated = abs(rate - .05) <= tolerance
    meaning["zero_effect"] = zero
    meaning["power"] = power
    meaning["nominal_rate_check"] = {"nominal": .05, "rate": rate, "tolerance": tolerance, "pass": calibrated}
    meaning["pass"] = meaning["pass"] and not zero["pass"] and calibrated and power[-1]["rate"] >= .9
    if args.directory:
        shot = shots.synthetic_check(args.directory)
    else:
        with tempfile.TemporaryDirectory() as directory:
            shot = shots.synthetic_check(Path(directory) / "shots")
    results = {"key-calibration": key, "meaning-map": meaning, "shots": shot,
               "restoration": restoration.synthetic(), "segmentation": segmentation.synthetic()}
    return envelope("selftest", {"tasks": results, "pass": all(r["pass"] for r in results.values()),
                                 "permutations": args.permutations, "null_trials": args.trials}, True)
