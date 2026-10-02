"""Training-only model selection for a stronger conditional-structure comparison.

This is a post-pilot robustness analysis, not the original fixed-alpha endpoint.
The candidate baseline includes unigram, position, and position+metadata models.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import time

import numpy as np

from conditional_structure import Model, digest, group_records, load_records, make_folds, shuffle_positions

GRID = [5, 20, 100, 500, 2000]


def fixed_groups(rows):
    values = defaultdict(list)
    for i, row in enumerate(rows):
        values[row["analysis_group"]].append(i)
    return list(values.values())


def tune(rows, seed, inner_folds=3):
    groups = fixed_groups(rows)
    assignment, _ = make_folds(rows, groups, inner_folds, seed)
    totals = Counter()
    count = 0
    for fold in range(inner_folds):
        train = [row for i, row in enumerate(rows) if assignment[i] != fold]
        test = [row for i, row in enumerate(rows) if assignment[i] == fold]
        count += sum(len(row["seq"]) - 1 for row in test)
        for alpha in GRID:
            model = Model(train, alpha)
            for row in test:
                scores, _ = model.score(row)
                for name in scores:
                    totals[(name, alpha)] += sum(scores[name][1:])
    baseline_candidates = [("U", 20)] + [(name, alpha) for name in ["P", "PM"] for alpha in GRID]
    dependent_candidates = [("PMB", alpha) for alpha in GRID]
    baseline = max(baseline_candidates, key=lambda c: totals[c])
    dependent = max(dependent_candidates, key=lambda c: totals[c])
    return baseline, dependent, {f"{name}@{alpha}": -totals[(name, alpha)] / count for name, alpha in baseline_candidates + dependent_candidates}


def crossvalidate(rows, assignments, folds=5, seed=20261001, bootstrap=0):
    per_group = defaultdict(lambda: [0.0, 0])
    results, total_baseline, total_dep, total_count = [], 0.0, 0.0, 0
    for fold in range(folds):
        train = [row for i, row in enumerate(rows) if assignments[i] != fold]
        test = [row for i, row in enumerate(rows) if assignments[i] == fold]
        baseline, dependent, tuning = tune(train, seed + fold)
        models = {alpha: Model(train, alpha) for alpha in {baseline[1], dependent[1]}}
        baseline_total, dependent_total, count = 0.0, 0.0, 0
        for row in test:
            baseline_scores, _ = models[baseline[1]].score(row)
            dep_scores, _ = models[dependent[1]].score(row)
            b = sum(baseline_scores[baseline[0]][1:])
            d = sum(dep_scores[dependent[0]][1:])
            n = len(row["seq"]) - 1
            baseline_total += b
            dependent_total += d
            count += n
            per_group[row["analysis_group"]][0] += d - b
            per_group[row["analysis_group"]][1] += n
        total_baseline += baseline_total
        total_dep += dependent_total
        total_count += count
        results.append({"fold": fold, "train_records": len(train), "test_records": len(test), "chosen_baseline": baseline, "chosen_dependent": dependent, "inner_noninitial_cross_entropy_bits": tuning, "gain_bits": (dependent_total - baseline_total) / count, "noninitial_tokens": count})
    ci = None
    if bootstrap:
        rng = np.random.default_rng(seed)
        values = np.array(list(per_group.values()), dtype=float)
        draws = np.empty(bootstrap)
        for n in range(bootstrap):
            sample = values[rng.integers(0, len(values), len(values))]
            draws[n] = sample[:, 0].sum() / sample[:, 1].sum()
        ci = [float(x) for x in np.quantile(draws, [0.025, 0.975])]
    gain = (total_dep - total_baseline) / total_count
    return {"records": len(rows), "groups": len(per_group), "noninitial_tokens": total_count, "gain_bits_per_noninitial_sign": gain, "gain_95pct_group_bootstrap_ci": ci, "relative_perplexity": 2 ** (-gain), "baseline_noninitial_cross_entropy_bits": -total_baseline / total_count, "dependent_noninitial_cross_entropy_bits": -total_dep / total_count, "folds": results}


def leave_site_out(rows, min_records=60, seed=20261001):
    sites = Counter(row.get("site", "MISSING") for row in rows)
    results = []
    for site, records in sites.most_common():
        if records < min_records or site in {"Unknown", "MISSING"}:
            continue
        test = [r for r in rows if r.get("site") == site]
        test_seqs = {r["seq"] for r in test}
        test_artifacts = {artifact for r in test for artifact in r.get("artifact_aliases", [r["artifact"]])}
        other = [r for r in rows if r.get("site") != site]
        train = [r for r in other if r["seq"] not in test_seqs and test_artifacts.isdisjoint(r.get("artifact_aliases", [r["artifact"]]))]
        baseline, dependent, tuning = tune(train, seed)
        models = {alpha: Model(train, alpha) for alpha in {baseline[1], dependent[1]}}
        btotal, dtotal, count, oov = 0.0, 0.0, 0, 0
        for row in test:
            bs, boov = models[baseline[1]].score(row)
            ds, _ = models[dependent[1]].score(row)
            btotal += sum(bs[baseline[0]][1:])
            dtotal += sum(ds[dependent[0]][1:])
            count += len(row["seq"]) - 1
            oov += boov
        results.append({"heldout_site": site, "test_records": len(test), "test_unique_sequences": len(test_seqs), "train_records": len(train), "removed_exact_sequence_or_artifact_overlap": len(other) - len(train), "noninitial_tokens": count, "oov_tokens": oov, "baseline": baseline, "dependent": dependent, "gain_bits_per_noninitial_sign": (dtotal - btotal) / count, "baseline_cross_entropy_bits": -btotal / count, "dependent_cross_entropy_bits": -dtotal / count, "inner_scores": tuning})
    return results


def main(args):
    start = time.monotonic()
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, exclusions = load_records(args.input, args.min_length, args.unique, args.reverse, collapse)
    groups = group_records(rows)
    assignment, loads = make_folds(rows, groups, 5, args.seed)
    for group, indices in enumerate(groups):
        for index in indices:
            rows[index]["analysis_group"] = group
    result = {"design": "Post-pilot training-only nested model-selection robustness", "input_sha256": digest(args.input), "source_sha256": digest(__file__), "dependency_source_sha256": digest(Path(__file__).with_name("conditional_structure.py")), "parameters": vars(args), "smoothing_grid": GRID, "inner_folds": 3, "outer_folds": 5, "exclusions": exclusions, "group_sizes": sorted([len(g) for g in groups], reverse=True), "fold_loads": loads}
    result["observed"] = crossvalidate(rows, assignment, 5, args.seed, args.bootstrap)
    print(json.dumps({"stage": "observed_nested", "records": len(rows), "gain": result["observed"]["gain_bits_per_noninitial_sign"], "CI": result["observed"]["gain_95pct_group_bootstrap_ci"], "baseline": [f["chosen_baseline"] for f in result["observed"]["folds"]], "dependent": [f["chosen_dependent"] for f in result["observed"]["folds"]]}), flush=True)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    def save():
        result["elapsed_seconds"] = time.monotonic() - start
        (output / "nested_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    save()
    for metadata, label in [(False, "position"), (True, "position_metadata")]:
        values, mobility = [], None
        permutations = args.position_permutations if not metadata and args.position_permutations is not None else args.permutations
        for p in range(permutations):
            shuffled, mobility = shuffle_positions(rows, args.seed + p + (10000 if metadata else 0), metadata)
            score = crossvalidate(shuffled, assignment, 5, args.seed, 0)
            values.append(score["gain_bits_per_noninitial_sign"])
            if (p + 1) % 25 == 0:
                result["null_" + label] = {"in_progress": True, "permutations": len(values), "values": values}
                save()
                print(json.dumps({"stage": "nested_null", "null": label, "done": p + 1, "total": permutations}), flush=True)
        observed = result["observed"]["gain_bits_per_noninitial_sign"]
        result["null_" + label] = {"permutations": len(values), "mobility": mobility, "mean": float(np.mean(values)) if values else None, "95pct_range": [float(x) for x in np.quantile(values, [0.025, 0.975])] if values else None, "p_one_sided": (1 + sum(v >= observed for v in values)) / (1 + len(values)) if values else None, "values": values}
        save()
    result["leave_site_out"] = leave_site_out(rows, seed=args.seed)
    save()
    print(json.dumps({"stage": "complete_nested", "output": str(output), "seconds": time.monotonic() - start, "site_gains": [{"site": r["heldout_site"], "gain": r["gain_bits_per_noninitial_sign"], "n": r["test_records"]} for r in result["leave_site_out"]]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-length", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--position-permutations", type=int)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--collapse")
    main(parser.parse_args())
