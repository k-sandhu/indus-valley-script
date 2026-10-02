"""Extend a completed regrouped nested metadata null without repeating seeds."""
import argparse
import copy
import json
from pathlib import Path
import time

import numpy as np

from conditional_structure import digest, load_records, shuffle_positions
from nested_joint_null import fit


def main(args):
    started = time.monotonic()
    prior = json.loads(Path(args.prior).read_text(encoding="utf-8"))
    original = prior["parameters"]
    collapse = json.loads(Path(original["collapse"]).read_text(encoding="utf-8"))["mapping"] if original.get("collapse") else None
    rows, _ = load_records(original["input"], 3, original.get("unique", False), False, collapse)
    if digest(original["input"]) != prior["input_sha256"]:
        raise ValueError("Input changed since the prior completed null.")
    if prior["null_position_metadata"].get("in_progress"):
        raise ValueError("Only a completed prior run can be extended.")
    result = copy.deepcopy(prior)
    result["extension"] = {"prior_path": args.prior, "prior_sha256": digest(args.prior), "parameters": vars(args), "runner_sha256": digest(__file__), "fit_source_sha256": digest(Path(__file__).with_name("nested_joint_null.py")), "nested_source_sha256": digest(Path(__file__).with_name("nested_conditional.py")), "loader_source_sha256": digest(Path(__file__).with_name("conditional_structure.py")), "seed_policy": "Retain all completed prior seeds; append seed+10000+p beginning at prior count."}
    values = list(prior["null_position_metadata"]["values"])
    group_range = list(prior["null_position_metadata"]["null_group_count_range"])
    size_range = list(prior["null_position_metadata"]["null_largest_group_range"])
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    def save():
        result["extension"]["elapsed_seconds"] = time.monotonic() - started
        (output / "joint_nested_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    observed = prior["observed"]["gain_bits_per_noninitial_sign"]
    for p in range(len(values), args.permutations):
        shuffled, mobility = shuffle_positions(rows, original["seed"] + 10000 + p, True)
        score, info = fit(shuffled, original["seed"])
        values.append(score["gain_bits_per_noninitial_sign"])
        group_range = [min(group_range[0], info["groups"]), max(group_range[1], info["groups"])]
        size_range = [min(size_range[0], info["largest_group"]), max(size_range[1], info["largest_group"])]
        if (p + 1) % 25 == 0:
            result["null_position_metadata"] = {"in_progress": True, "permutations": len(values), "values": values}
            save()
            print(json.dumps({"stage": "extended_joint_nested_null", "done": p + 1, "total": args.permutations}), flush=True)
    result["null_position_metadata"] = {"permutations": len(values), "mobility": mobility, "mean": float(np.mean(values)), "95pct_range": [float(v) for v in np.quantile(values, [.025, .975])], "p_one_sided": (1 + sum(v >= observed for v in values)) / (len(values) + 1), "null_group_count_range": group_range, "null_largest_group_range": size_range, "values": values}
    result["extension"]["complete"] = True
    save()
    print(json.dumps({"stage": "complete_extended_joint_nested_null", "output": str(output), "seconds": time.monotonic() - started, "metadata": {k: v for k, v in result["null_position_metadata"].items() if k != "values"}}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--permutations", type=int, default=1000)
    main(parser.parse_args())
