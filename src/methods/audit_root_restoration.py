"""Read-only audit of root restoration: stronger baseline and equal-text weights.

Root files are never edited. All baseline choices use inner training folds;
the already-held-out local predictions are reused unchanged.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import time

import numpy as np

from conditional_structure import Model, digest, group_records, load_records, make_folds


GRID = [20, 100, 500, 2000]


def independent_predictions(rows, model):
    correct = Counter()
    output = {"U": [], "P": [], "PM": []}
    for row in rows:
        for i, actual in enumerate(row["seq"]):
            position, metadata, _ = model.distributions(len(row["seq"]), i, row["stratum"], None)
            for name, distribution in [("U", model.unigram), ("P", position), ("PM", metadata)]:
                prediction = model.signs[int(np.argmax(distribution))]
                success = prediction == actual
                correct[name] += success
                output[name].append({"record_id": row["record_id"], "slot": i, "top1": success, "length": len(row["seq"])})
    return correct, output


def tune_baseline(train, seed):
    groups = group_records(train)
    assignments, _ = make_folds(train, groups, 3, seed)
    totals = Counter()
    slots = 0
    for fold in range(3):
        fit = [r for i, r in enumerate(train) if assignments[i] != fold]
        test = [r for i, r in enumerate(train) if assignments[i] == fold]
        slots += sum(len(r["seq"]) for r in test)
        for alpha in GRID:
            counts, _ = independent_predictions(test, Model(fit, alpha))
            for name in ["P", "PM"]:
                totals[(name, alpha)] += counts[name]
            if alpha == 20:
                totals[("U", 20)] += counts["U"]
    priority = {"U": 0, "P": 1, "PM": 2}
    chosen = max(totals, key=lambda c: (totals[c], c[1], priority[c[0]]))
    return chosen, {f"{name}@{alpha}": count / slots for (name, alpha), count in totals.items()}


def equal_text(base, local, group_lookup, seed):
    by_text = defaultdict(lambda: [0.0, 0.0, 0])
    for a, b in zip(base, local):
        assert (a["record_id"], a["slot"]) == (b["record_id"], b["slot"])
        values = by_text[a["record_id"]]
        values[0] += a["top1"]
        values[1] += b["top1"]
        values[2] += 1
    groups = defaultdict(lambda: np.zeros(3))
    for record_id, (a, b, n) in by_text.items():
        groups[group_lookup[record_id]] += [a / n, b / n, 1]
    values = np.asarray(list(groups.values()))
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(5000):
        totals = values[rng.integers(0, len(values), len(values))].sum(axis=0)
        draws.append((totals[1] - totals[0]) / totals[2])
    totals = values.sum(axis=0)
    return {"texts": len(by_text), "groups": len(values), "baseline_top1": float(totals[0] / totals[2]), "local_top1": float(totals[1] / totals[2]), "gain_top1": float((totals[1] - totals[0]) / totals[2]), "95pct_group_bootstrap_gain_ci": [float(v) for v in np.quantile(draws, [.025, .975])], "estimand": "Uniform complete text, then a uniformly selected one-glyph mask within that text."}


def main(args):
    started = time.monotonic()
    root_output = Path(args.root_output)
    benchmark = json.loads((root_output / "benchmark.json").read_text(encoding="utf-8"))
    base = [json.loads(line) for line in (root_output / "baseline_slot_audit.jsonl").read_text(encoding="utf-8").splitlines()]
    local = [json.loads(line) for line in (root_output / "local_slot_audit.jsonl").read_text(encoding="utf-8").splitlines()]
    rows, _ = load_records("data/normalized/lipi_clean_rtl_singleline.jsonl", unique=True)
    groups = group_records(rows)
    assignments, loads = make_folds(rows, groups, 5, args.seed)
    record_lookup = {r["record_id"]: i for i, r in enumerate(rows)}
    group_lookup = {rows[i]["record_id"]: group for group, indices in enumerate(groups) for i in indices}
    assert all(assignments[record_lookup[s["record_id"]]] == s["fold"] for s in base), "Seed does not reproduce root outer folds."
    assert benchmark["model_dependency_sha256"] == digest(Path(__file__).with_name("conditional_structure.py")), "Shared predictive helper differs from benchmark hash."
    assert len(base) == len(local) == sum(len(r["seq"]) for r in rows)
    result = {"scope": "Read-only audit; no change to root benchmark or archaeological interpretation", "parameters": vars(args), "source_sha256": digest(__file__), "benchmark_sha256": digest(root_output / "benchmark.json"), "helper_sha256": digest(Path(__file__).with_name("conditional_structure.py")), "equal_text_original_baseline": equal_text(base, local, group_lookup, args.seed), "stronger_baseline_policy": "Select U20 or P/PM at alpha20/100/500/2000 on three inner training groups by exact all-slot top1; ties favor greater smoothing then PM>P>U.", "folds": []}
    stronger = []
    for fold in range(5):
        train = [r for i, r in enumerate(rows) if assignments[i] != fold]
        test = [r for i, r in enumerate(rows) if assignments[i] == fold]
        chosen, inner = tune_baseline(train, args.seed + fold)
        _, predictions = independent_predictions(test, Model(train, chosen[1]))
        stronger.extend(predictions[chosen[0]])
        result["folds"].append({"fold": fold, "chosen": chosen, "inner_accuracy": inner})
        print(json.dumps({"stage": "stronger_restoration_baseline", "fold": fold, "chosen": chosen}), flush=True)
    keyed = {(s["record_id"], s["slot"]): s for s in stronger}
    aligned = [keyed[(s["record_id"], s["slot"])] for s in local]
    result["stronger_baseline_slot_top1"] = float(np.mean([s["top1"] for s in aligned]))
    result["local_slot_top1"] = float(np.mean([s["top1"] for s in local]))
    result["equal_text_stronger_baseline"] = equal_text(aligned, local, group_lookup, args.seed)
    result["local_confidence_bins_from_root"] = benchmark["models"]["local"]["confidence_audit"]
    result["confidence_interpretation"] = "Compare mean model mass with exact held-out code accuracy. This is not calibration to archaeological truth and no calibrator was fitted on outer test predictions."
    result["elapsed_seconds"] = time.monotonic() - started
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"stage": "complete_root_restoration_audit", "output": str(output), "slot_baseline": result["stronger_baseline_slot_top1"], "slot_local": result["local_slot_top1"], "equal_text": result["equal_text_stronger_baseline"], "seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-output", default="results/restoration")
    parser.add_argument("--output", default="research/methods/root_restoration_audit.json")
    parser.add_argument("--seed", type=int, default=20261006)
    main(parser.parse_args())
