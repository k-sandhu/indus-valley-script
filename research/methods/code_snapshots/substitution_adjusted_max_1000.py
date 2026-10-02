"""Frequency-adjusted permutation maxima over all distinct graphic-class pairs.

Pooled means include observed and randomized datasets symmetrically. Under the
column-permutation null, ranks of the resulting maximum scores are exchangeable.
The denominator sqrt(mean+1) is a declared stabilizer, not an assumed variance.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import time

import numpy as np

from conditional_structure import digest, frames, load_records, pair_frames, shuffle_positions
from substitution_validation import classification


def counts(rows, classes):
    return {pair: len(contexts) for pair, contexts in pair_frames(frames(rows)).items() if classification(pair, classes) == "known_distinct_graphic_classes"}


def main(args):
    start = time.monotonic()
    classes = json.loads(Path(args.classes).read_text(encoding="utf-8"))["by_wells_id"]
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, excluded = load_records(args.input, 3, args.unique, False, collapse)
    observed = counts(rows, classes)
    result = {"design": "Post-pilot frequency-adjusted full-universe max permutation sensitivity; distinct graphic classes only", "input_sha256": digest(args.input), "classes_sha256": digest(args.classes), "source_sha256": digest(__file__), "parameters": vars(args), "records": len(rows), "exclusions": excluded, "score": "(support - pooled_mean) / sqrt(pooled_mean+1); pooled mean includes observed dataset symmetrically", "selection_policy": "Maximum covers every pair present in any observed or randomized corpus; zero-support pairs have nonpositive scores and cannot change the maximum."}
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    for metadata, label in [(False, "position"), (True, "position_metadata")]:
        support_maps = [observed]
        pooled = Counter(observed)
        for p in range(args.permutations):
            shuffled, mobility = shuffle_positions(rows, args.seed + p + (10000 if metadata else 0), metadata)
            values = counts(shuffled, classes)
            support_maps.append(values)
            pooled.update(values)
            if (p + 1) % 500 == 0:
                print(json.dumps({"stage": "null", "type": label, "done": p + 1, "total": args.permutations}), flush=True)
        means = {pair: total / len(support_maps) for pair, total in pooled.items()}
        def score(pair, support):
            mean = means[pair]
            return (support - mean) / math.sqrt(mean + 1)
        maxima = [max([0.0] + [score(pair, support) for pair, support in values.items()]) for values in support_maps]
        ranked = sorted(observed, key=lambda pair: -score(pair, observed[pair]))
        result["null_" + label] = {"permutations": args.permutations, "mobility": mobility, "pair_universe_with_any_nonzero_support": len(means), "observed_max_score": maxima[0], "null_max_score_mean": float(np.mean(maxima[1:])), "null_max_score_95pct_range": [float(x) for x in np.quantile(maxima[1:], [0.025, 0.975])], "global_max_p": (1 + sum(value >= maxima[0] for value in maxima[1:])) / len(maxima), "null_max_values": maxima[1:], "top_pairs": [{"pair": pair, "distinct_frames": observed[pair], "pooled_mean": means[pair], "adjusted_score": score(pair, observed[pair]), "FWER_max_score_p": (1 + sum(value >= score(pair, observed[pair]) for value in maxima[1:])) / len(maxima)} for pair in ranked[:50]]}
        result["elapsed_seconds"] = time.monotonic() - start
        (output / "adjusted_max_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"stage": "complete", "output": str(output), "seconds": time.monotonic() - start, "position_p": result["null_position"]["global_max_p"], "metadata_p": result["null_position_metadata"]["global_max_p"], "top3": result["null_position_metadata"]["top_pairs"][:3]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--classes", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--collapse")
    main(parser.parse_args())
