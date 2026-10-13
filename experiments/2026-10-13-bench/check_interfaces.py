"""Small deterministic checks of input rejection, pairing and generated planting."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from bench import key_calibration as K, meaning_map as M, restoration as R, segmentation as S
from bench.common import envelope, null_summary, write_json


def main():
    out = ROOT / "experiments/2026-10-13-bench" / (sys.argv[1] if len(sys.argv) > 1 else "interfaces-v1.json")
    cases = {}
    def rejected(name, function):
        try:
            function()
        except (ValueError, AssertionError, FileExistsError):
            cases[name] = True
        else:
            cases[name] = False
    texts = [tuple("abcde")]
    rejected("duplicate boundary", lambda: S.score([[2]], [[2, 2]], texts))
    rejected("external boundary", lambda: S.score([[2]], [[5]], texts))
    rejected("missing segmentation row", lambda: S.score([[2]], [], texts))
    rejected("empty text", lambda: S.score([[]], [[]], [()]))
    row = {"id": "a", "slot": 0, "target": "s1", "predictions": [{"code": "s1", "probability": .8}, {"code": "s2", "probability": .2}]}
    rejected("duplicate mask query", lambda: R.known_slots([row, row]))
    reversed_row = deepcopy(row)
    reversed_row["predictions"].reverse()
    rejected("unranked probabilities", lambda: R.known_slots([reversed_row]))
    invalid = deepcopy(row)
    invalid["predictions"][0]["probability"] = float("nan")
    rejected("nonfinite probability", lambda: R.known_slots([invalid]))
    invalid = deepcopy(row)
    invalid["target"] = "s2"
    rejected("paired target mismatch", lambda: R.paired_comparison([row], [invalid]))
    same = R.paired_comparison([row], [row])
    cases["identical paired models have zero interval and fail"] = same["component_bootstrap_ci95"] == [0., 0.] and not same["pass_statistical"]
    cases["undefined rearrangements cannot win"] = not null_summary(1., [0., float("nan")])["pass"]
    rejected("empty key", lambda: K.normalize_key({}))
    rejected("bad alphabet", lambda: K.train_model({"alphabet": ["a", "a"], "training": ["a"]}))
    rows, mapping, predictions = M.synthetic_data(.5, 17)
    power = M.power_on_design(rows, mapping, predictions, (0., 1.5), trials=5, draws=99, seed=17)
    cases["design-shaped large effect passes"] = power[-1]["rate"] == 1.
    # A categorical case uses the same incidence and a stated background law.
    for i, r in enumerate(rows):
        r["properties"]["site"] = ["Harappa", "Lothal", "Dholavira"][i % 3]
    categorical = [{"id": "local", "variable": "site", "measure": "concentration", "site_policy": "exclude_mohenjo",
                    "positive": "official", "negative": "name", "criterion": "rank", "min_units": 4}]
    categorical_power = M.power_on_design(rows, mapping, categorical, (0., 3.), trials=5, draws=99, seed=17)
    cases["categorical planted effect passes"] = categorical_power[-1]["rate"] == 1.
    rejected("site policy omitted", lambda: M.evaluate(rows, mapping, [dict(categorical[0], site_policy=None)], draws=9))
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frozen.json"
        write_json(path, {"value": 1})
        rejected("existing output refused", lambda: write_json(path, {"value": 2}))
        cases["existing bytes preserved"] = json.loads(path.read_text())["value"] == 1
    result = envelope("interface-checks", {"cases": cases, "pass": all(cases.values()),
                                             "design_power": power, "categorical_power": categorical_power}, True,
                      ["bench/key_calibration.py", "bench/meaning_map.py", "bench/restoration.py", "bench/segmentation.py"])
    write_json(out, result)
    print(json.dumps({"cases": len(cases), "pass": result["pass"]}))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
