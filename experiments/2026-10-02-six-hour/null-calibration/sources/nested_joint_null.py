"""Post-audit nested structural null rerunning the complete grouped fit.

Original null runs kept original groups/folds fixed. This sensitivity reexecutes
sequence-dependent grouping, allocation, inner smoothing selection and outer
prediction on every shuffled corpus. It avoids treating a data-selected group
partition as an externally fixed experimental partition.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np

from conditional_structure import digest, group_records, load_records, make_folds, shuffle_positions
from nested_conditional import crossvalidate


def fit(rows, seed, bootstrap=0):
    groups = group_records(rows)
    assignment, loads = make_folds(rows, groups, 5, seed)
    for group, indices in enumerate(groups):
        for index in indices:
            rows[index]["analysis_group"] = group
    score = crossvalidate(rows, assignment, 5, seed, bootstrap)
    return score, {"groups": len(groups), "largest_group": max(map(len, groups)), "fold_loads": loads}


def main(args):
    start = time.monotonic()
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, excluded = load_records(args.input, 3, args.unique, False, collapse)
    observed, grouping = fit(rows, args.seed)
    result = {"design": "Post-audit full-procedure grouped nested structural permutation sensitivity", "parameters": vars(args), "input_sha256": digest(args.input), "source_sha256": digest(__file__), "nested_source_sha256": digest(Path(__file__).with_name("nested_conditional.py")), "loader_source_sha256": digest(Path(__file__).with_name("conditional_structure.py")), "exclusions": excluded, "observed": observed, "observed_grouping": grouping, "scope": "All sequence-dependent grouping and model selection are rerun on each null corpus. Permutations reference the supplied transcription population and destroy duplicate cohort identity; unique-string sensitivity must still be considered."}
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    def save():
        result["elapsed_seconds"] = time.monotonic() - start
        (output / "joint_nested_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    save()
    print(json.dumps({"stage": "observed_joint_nested", "gain": observed["gain_bits_per_noninitial_sign"], "grouping": grouping}), flush=True)
    for metadata, label in [(False, "position"), (True, "position_metadata")]:
        values, group_counts, sizes = [], [], []
        permutations = args.position_permutations if not metadata else args.permutations
        for p in range(permutations):
            shuffled, mobility = shuffle_positions(rows, args.seed + p + (10000 if metadata else 0), metadata)
            score, info = fit(shuffled, args.seed)
            values.append(score["gain_bits_per_noninitial_sign"])
            group_counts.append(info["groups"])
            sizes.append(info["largest_group"])
            if (p + 1) % 25 == 0:
                result["null_" + label] = {"in_progress": True, "permutations": p + 1, "values": values}
                save()
                print(json.dumps({"stage": "joint_nested_null", "null": label, "done": p + 1, "total": permutations}), flush=True)
        result["null_" + label] = {"permutations": permutations, "mobility": mobility, "mean": float(np.mean(values)), "95pct_range": [float(v) for v in np.quantile(values, [.025, .975])], "p_one_sided": (1 + sum(v >= observed["gain_bits_per_noninitial_sign"] for v in values)) / (permutations + 1), "null_group_count_range": [min(group_counts), max(group_counts)], "null_largest_group_range": [min(sizes), max(sizes)], "values": values}
        save()
    print(json.dumps({"stage": "complete_joint_nested", "output": str(output), "metadata": {k: v for k, v in result["null_position_metadata"].items() if k != "values"}, "seconds": time.monotonic() - start}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--position-permutations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--collapse")
    main(parser.parse_args())
