"""Joint permutation reference for cross-validated exact-frame transfer.

Unlike the earlier conditional-per-fold diagnostics, every random corpus reruns
grouping, fold allocation, pair discovery, and entirely-new-frame validation.
This includes the search procedure in the statistic. Metadata-column nulls are
references for the supplied transcription population, not a language test.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np

from conditional_structure import digest, frames, group_records, load_records, make_folds, pair_frames, shuffle_positions
from substitution_validation import classification


CATEGORIES = ["shared_graphic_class", "known_distinct_graphic_classes", "unmapped_or_partly_mapped"]


def transfer(rows, classes, seed):
    groups = group_records(rows)
    assignment, loads = make_folds(rows, groups, 5, seed)
    total, confirmed = defaultdict(int), defaultdict(list)
    for fold in range(5):
        train = [r for i, r in enumerate(rows) if assignment[i] != fold]
        test = [r for i, r in enumerate(rows) if assignment[i] == fold]
        train_frames = frames(train)
        discovered = {pair for pair, contexts in pair_frames(train_frames).items() if len(contexts) >= 2}
        new_pairs = pair_frames({key: value for key, value in frames(test).items() if key not in train_frames})
        for pair in discovered & new_pairs.keys():
            category = classification(pair, classes)
            total[category] += len(new_pairs[pair])
            confirmed[category].append({"fold": fold, "pair": pair, "new_frames": new_pairs[pair]})
    return {c: total[c] for c in CATEGORIES}, dict(confirmed), {"groups": len(groups), "largest_group": max(map(len, groups)), "fold_loads": loads}


def main(args):
    if args.require_unique_null and not args.unique:
        raise ValueError("Uniqueness-conditioned null requires the unique-string population.")
    start = time.monotonic()
    classes = json.loads(Path(args.classes).read_text(encoding="utf-8"))["by_wells_id"]
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, excluded = load_records(args.input, 3, args.unique, False, collapse)
    observed, confirmed, grouping = transfer(rows, classes, args.seed)
    result = {
        "design": "Post-audit joint full-corpus column-permutation new-frame transfer reference, with discovery and grouping rerun on every null corpus",
        "parameters": vars(args), "input_sha256": digest(args.input), "classes_sha256": digest(args.classes),
        "source_sha256": digest(__file__), "dependency_sha256": digest(Path(__file__).with_name("conditional_structure.py")),
        "records": len(rows), "exclusions": excluded, "observed_transfer": observed,
        "confirmed_transfers": confirmed, "observed_grouping": grouping,
        "scope": "Each fold discovers pairs supported by >=2 training frames, then counts their entirely new held-out frames. The null destroys dependencies while preserving exact length/position marginals and optionally site/object-type marginals. Unique-string subset and derivative source remain sensitivities, not universal population sampling claims.",
    }
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    def save():
        result["elapsed_seconds"] = time.monotonic() - start
        (output / "joint_null_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    save()
    print(json.dumps({"stage": "observed_joint_transfer", "observed": observed, "grouping": grouping}), flush=True)
    for metadata, label in [(False, "position"), (True, "position_metadata")]:
        values = {c: [] for c in CATEGORIES}
        groups = []
        attempts, accepted_seeds = 0, []
        for p in range(args.permutations):
            while True:
                null_seed = args.seed + attempts + (10000 if metadata else 0)
                attempts += 1
                shuffled, mobility = shuffle_positions(rows, null_seed, metadata)
                if not args.require_unique_null or len({r["seq"] for r in shuffled}) == len(shuffled):
                    accepted_seeds.append(null_seed)
                    break
                if attempts >= args.max_attempts:
                    raise RuntimeError("Unique null rejection sampler exhausted declared attempt limit.")
            counts, _, group_info = transfer(shuffled, classes, args.seed)
            groups.append(group_info["groups"])
            for c in CATEGORIES:
                values[c].append(counts[c])
            if (p + 1) % 100 == 0:
                result["null_" + label] = {"in_progress": True, "permutations": p + 1, "attempts": attempts, "accepted_seeds": accepted_seeds, "values": values}
                save()
                print(json.dumps({"stage": "joint_null", "null": label, "done": p + 1, "total": args.permutations}), flush=True)
        result["null_" + label] = {
            "permutations": args.permutations, "mobility": mobility,
            "attempts": attempts, "accepted_seeds": accepted_seeds,
            "uniqueness_conditioned": args.require_unique_null,
            "null_group_count_range": [min(groups), max(groups)],
            "by_category": {c: {"observed": observed[c], "mean": float(np.mean(values[c])), "95pct_range": [float(v) for v in np.quantile(values[c], [.025, .975])], "p_one_sided": (1 + sum(v >= observed[c] for v in values[c])) / (args.permutations + 1), "values": values[c]} for c in CATEGORIES},
        }
        save()
    print(json.dumps({"stage": "complete_joint_null", "output": str(output), "metadata": {c: {k: v for k, v in s.items() if k != "values"} for c, s in result["null_position_metadata"]["by_category"].items()}, "seconds": time.monotonic() - start}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--classes", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--collapse")
    parser.add_argument("--require-unique-null", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=1000000)
    main(parser.parse_args())
