"""Exact-frame substitutions with independent graphic-class safeguards.

Class compatibility is intersected pairwise; never made transitively equivalent.
Whole-corpus max-support p-values protect against selecting the best pair post hoc.
Held-out transfer remains a separate test of new contexts.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np

from conditional_structure import digest, frames, group_records, load_records, make_folds, pair_frames, shuffle_positions


def classification(pair, classes):
    left, right = set(classes.get(pair[0], [])), set(classes.get(pair[1], []))
    if left & right:
        return "shared_graphic_class"
    if left and right:
        return "known_distinct_graphic_classes"
    return "unmapped_or_partly_mapped"


def summary(rows, assignment, classes, folds=5):
    frame_map = frames(rows)
    edges = pair_frames(frame_map)
    by_category = defaultdict(list)
    for pair, contexts in edges.items():
        slots = []
        artifacts, sites, object_types = set(), set(), set()
        for key in contexts:
            slots.append("initial" if key[1] == 0 else "terminal" if key[1] == key[0] - 1 else "medial")
            for sign in pair:
                for row in frame_map[key][sign]:
                    artifacts.add(row["artifact"])
                    sites.add(row.get("site", "MISSING"))
                    object_types.add(row.get("object_type", "MISSING"))
        by_category[classification(pair, classes)].append({"pair": pair, "distinct_frames": len(contexts), "slots": sorted(set(slots)), "artifact_count": len(artifacts), "sites": sorted(sites), "object_types": sorted(object_types), "contexts": contexts, "independent_P_classes": {s: classes.get(s, []) for s in pair}})
    for values in by_category.values():
        values.sort(key=lambda item: (-item["distinct_frames"], item["pair"]))
    discoveries, tests, observed = [], [], defaultdict(int)
    confirmed = defaultdict(list)
    for fold in range(folds):
        train = [r for i, r in enumerate(rows) if assignment[i] != fold]
        test = [r for i, r in enumerate(rows) if assignment[i] == fold]
        train_frames = frames(train)
        discovered = {pair for pair, contexts in pair_frames(train_frames).items() if len(contexts) >= 2}
        test_edges = pair_frames({key: value for key, value in frames(test).items() if key not in train_frames})
        for pair in discovered & test_edges.keys():
            category = classification(pair, classes)
            observed[category] += len(test_edges[pair])
            confirmed[category].append({"fold": fold, "pair": pair, "new_frames": test_edges[pair]})
        discoveries.append((discovered, set(train_frames)))
        tests.append(test)
    return frame_map, edges, dict(by_category), discoveries, tests, dict(observed), dict(confirmed)


def main(args):
    start = time.monotonic()
    class_source = json.loads(Path(args.classes).read_text(encoding="utf-8"))
    classes = class_source["by_wells_id"]
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, excluded = load_records(args.input, args.min_length, args.unique, False, collapse)
    groups = group_records(rows)
    assignment, _ = make_folds(rows, groups, 5, args.seed)
    frame_map, edges, categories, discoveries, tests, observed, confirmed = summary(rows, assignment, classes)
    eligible = {pair for pair in edges if classification(pair, classes) == "known_distinct_graphic_classes"}
    max_observed = max([len(edges[pair]) for pair in eligible], default=0)
    result = {
        "design": "Exploratory class-aware substitution analysis with selection-aware max statistic and train-only new-frame transfer",
        "input_sha256": digest(args.input), "classes_sha256": digest(args.classes), "source_sha256": digest(__file__), "dependency_sha256": digest(Path(__file__).with_name("conditional_structure.py")),
        "parameters": vars(args), "records": len(rows), "groups": len(groups), "unique_sequences": len({r["seq"] for r in rows}), "excluded": excluded,
        "class_policy": class_source["sensitivity_rule"],
        "pairs_by_category": {category: {"pairs": len(values), "pairs_with_two_or_more_frames": sum(item["distinct_frames"] >= 2 for item in values), "top_pairs": values[:25]} for category, values in categories.items()},
        "transfer_counts_by_category": observed, "confirmed_transfers": confirmed,
        "maximum_known_distinct_class_pair_support": max_observed,
        "claims": "Graphic-class distinction rules out one particular catalogue's allographic grouping; it does not prove semantic difference or equivalence.",
    }
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    def save():
        result["elapsed_seconds"] = time.monotonic() - start
        (out / "substitution_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    save()
    print(json.dumps({"stage": "observed", "max_distinct_class_frames": max_observed, "transfer": observed, "top_distinct_class_pairs": [(item["pair"], item["distinct_frames"], item["slots"]) for item in categories.get("known_distinct_graphic_classes", [])[:10]]}), flush=True)
    for metadata, label in [(False, "position"), (True, "position_metadata")]:
        max_values, transfer_values = [], defaultdict(list)
        pair_supports = {pair: [] for pair in sorted(eligible)}
        for p in range(args.permutations):
            full_shuffled, mobility = shuffle_positions(rows, args.seed + p + (10000 if metadata else 0), metadata)
            null_edges = pair_frames(frames(full_shuffled))
            max_values.append(max([len(contexts) for pair, contexts in null_edges.items() if classification(pair, classes) == "known_distinct_graphic_classes"], default=0))
            for pair in pair_supports:
                pair_supports[pair].append(len(null_edges.get(pair, [])))
            counts = defaultdict(int)
            for fold, test in enumerate(tests):
                shuffled, _ = shuffle_positions(test, args.seed + 100000 * (1 + metadata) + p * 5 + fold, metadata)
                discovered, training_frames = discoveries[fold]
                test_edges = pair_frames({key: value for key, value in frames(shuffled).items() if key not in training_frames})
                for pair in discovered & test_edges.keys():
                    counts[classification(pair, classes)] += len(test_edges[pair])
            for category in ["shared_graphic_class", "known_distinct_graphic_classes", "unmapped_or_partly_mapped"]:
                transfer_values[category].append(counts[category])
            if (p + 1) % 100 == 0:
                result["null_" + label] = {"in_progress": True, "permutations": p + 1, "max_support_values": max_values}
                save()
                print(json.dumps({"stage": "permutation", "null": label, "done": p + 1, "total": args.permutations}), flush=True)
        def stats(values, point):
            return {"observed": point, "mean": float(np.mean(values)), "95pct_range": [float(x) for x in np.quantile(values, [0.025, 0.975])], "p_one_sided": (1 + sum(value >= point for value in values)) / (1 + len(values))}
        result["null_" + label] = {
            "permutations": len(max_values), "mobility": mobility,
            "max_support": stats(max_values, max_observed), "max_support_values": max_values,
            "new_frame_transfer": {category: stats(values, observed.get(category, 0)) for category, values in transfer_values.items()},
            "pair_support": [{"pair": pair, "distinct_frames": len(edges[pair]), "unadjusted_permutation_p": (1 + sum(value >= len(edges[pair]) for value in values)) / (1 + len(values)), "max_support_FWER_p": (1 + sum(value >= len(edges[pair]) for value in max_values)) / (1 + len(max_values)), "null_mean": float(np.mean(values)), "null_support_max": max(values)} for pair, values in pair_supports.items() if len(edges[pair]) >= 2],
        }
        save()
    print(json.dumps({"stage": "complete", "output": str(out), "seconds": time.monotonic() - start, "max_support": result["null_position_metadata"]["max_support"], "transfer": result["null_position_metadata"]["new_frame_transfer"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--classes", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-length", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--collapse")
    main(parser.parse_args())
