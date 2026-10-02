"""Known-null calibration of the preserved nested conditional reference."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib
import itertools
import json
import math
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "src/methods/conditional_structure.py").exists() and (parent / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
SOURCES = ["conditional_structure.py", "nested_conditional.py", "nested_joint_null.py", "nested_unique_conditioned.py"]
PROBABILITIES = np.array([.20, .16, .14, .12, .11, .10, .09, .08])
FAMILIES = ["independent_records", "unique_records", "physical_copies"]
FIT_SEED = 20261001


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_sources():
    folder = FOLDER / "sources"
    folder.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in SOURCES:
        original = ROOT / "src/methods" / name
        destination = folder / name
        if destination.exists():
            assert digest(destination) == digest(original), "Source changed after its first snapshot: " + name
        else:
            shutil.copyfile(original, destination)
        hashes[name] = digest(destination)
    sys.path.insert(0, str(folder))
    return importlib.import_module("conditional_structure"), importlib.import_module("nested_joint_null"), hashes


def synthetic_rows(family, seed, records=40):
    assert records % 4 == 0
    rng = np.random.default_rng(seed)
    attempts = 0
    while True:
        attempts += 1
        rows = []
        latent_count = records // 2 if family == "physical_copies" else records
        for latent in range(latent_count):
            stratum = 0 if latent < latent_count // 2 else 1
            sequence = tuple(f"{rng.choice(8, p=np.roll(PROBABILITIES, stratum + 2 * slot)) + 1:03d}" for slot in range(3))
            for copy in range(2 if family == "physical_copies" else 1):
                row_index = len(rows)
                artifact = f"artifact_{latent:03d}"
                rows.append({"record_id": f"record_{row_index:03d}", "seq": sequence,
                             "artifact": artifact, "artifact_aliases": [artifact],
                             "site": f"site_{stratum}", "object_type": "SEAL:S",
                             "stratum": (f"site_{stratum}", "SEAL:S")})
        if family != "unique_records" or len({row["seq"] for row in rows}) == len(rows):
            return rows, {"seed": seed, "whole_dataset_proposals": attempts, "records": records,
                          "latent_objects": latent_count, "whole_string_unique": family == "unique_records",
                          "copies_per_latent": 2 if family == "physical_copies" else 1}


def margins(rows):
    cells = defaultdict(Counter)
    for row in rows:
        for slot, sign in enumerate(row["seq"]):
            cells[(len(row["seq"]), slot, row["stratum"])][sign] += 1
    return {key: dict(value) for key, value in cells.items()}


def block_shuffle(rows, seed, helper):
    blocks = defaultdict(list)
    for row in rows:
        blocks[row["artifact"]].append(row)
    representatives = []
    for artifact, copies in sorted(blocks.items()):
        assert all(copy["seq"] == copies[0]["seq"] and copy["stratum"] == copies[0]["stratum"] for copy in copies)
        representatives.append(dict(copies[0]))
    changed, mobility = helper.shuffle_positions(representatives, seed, True)
    lookup = {row["artifact"]: row["seq"] for row in changed}
    return [dict(row, seq=lookup[row["artifact"]]) for row in rows], mobility


def fit(rows, joint):
    copied = [dict(row) for row in rows]
    score, grouping = joint.fit(copied, FIT_SEED, 0)
    return {"gain": score["gain_bits_per_noninitial_sign"], "grouping": grouping,
            "chosen_models": [[fold["chosen_baseline"], fold["chosen_dependent"]] for fold in score["folds"]],
            "baseline_loss": score["baseline_noninitial_cross_entropy_bits"],
            "dependent_loss": score["dependent_noninitial_cross_entropy_bits"]}, score


def references(family):
    return ["record_columns", "block_columns"] if family == "physical_copies" else ["unique_record_columns"] if family == "unique_records" else ["record_columns"]


def reference_draws(rows, name, draws, seed_base, helper, joint):
    target_margins = margins(rows)
    scores = []
    attempts = 0
    accepted_seeds = []
    for draw in range(draws):
        while True:
            seed = seed_base + attempts
            attempts += 1
            if name == "block_columns":
                proposed, mobility = block_shuffle(rows, seed, helper)
            else:
                proposed, mobility = helper.shuffle_positions(rows, seed, True)
            assert margins(proposed) == target_margins
            assert all(before["artifact_aliases"] == after["artifact_aliases"] and before["stratum"] == after["stratum"] for before, after in zip(rows, proposed))
            if name != "unique_record_columns" or len({row["seq"] for row in proposed}) == len(proposed):
                break
            if attempts >= 100000:
                raise RuntimeError("Declared conditional rejection budget exhausted")
        compact, _ = fit(proposed, joint)
        compact["proposal_seed"] = seed
        scores.append(compact)
        accepted_seeds.append(seed)
    return {"draws": draws, "proposals": attempts, "accepted_seeds": accepted_seeds,
            "null": scores, "last_mobility": mobility}


def plus_one(observed, values):
    exceedances = sum(value >= observed for value in values)
    return exceedances, (1 + exceedances) / (1 + len(values))


def wilson(successes, total, z=1.959963984540054):
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [0.0 if successes == 0 else max(0., center - radius),
            1.0 if successes == total else min(1., center + radius)]


def aggregate(trials):
    groups = defaultdict(list)
    for trial in trials:
        for reference, result in trial["references"].items():
            groups[(trial["family"], reference)].append(result["p_value"])
    return {f"{family}/{reference}": {"datasets": len(values),
             "rejections": {str(alpha): {"count": sum(value <= alpha for value in values),
                            "rate": sum(value <= alpha for value in values) / len(values),
                            "wilson_95_ci": wilson(sum(value <= alpha for value in values), len(values))} for alpha in [.01, .05, .10]},
             "p_value_mean": float(np.mean(values)), "p_value_deciles": np.quantile(values, np.arange(0, 1.01, .1)).tolist()}
            for (family, reference), values in sorted(groups.items())}


def run_study(args):
    helper, joint, hashes = freeze_sources()
    output = Path(args.output)
    protocol = FOLDER / ("PILOT_PROTOCOL.md" if args.mode == "pilot" else "MAIN_PROTOCOL.md")
    if output.exists():
        if not args.resume or (output / "results.json").exists():
            raise FileExistsError(f"Refusing existing endpoint: {output}")
        state = json.loads((output / "state.json").read_text(encoding="utf-8"))
        assert state["source_sha256"] == digest(__file__) and state["protocol_sha256"] == digest(protocol)
        assert state["datasets_per_family"] == args.datasets and state["reference_draws"] == args.draws
        elapsed_before = state["elapsed_seconds"]
    else:
        if args.resume:
            raise FileNotFoundError("No stopped checkpoint exists to resume")
        output.mkdir(parents=True)
        shutil.copyfile(__file__, output / "code_snapshot.py")
        elapsed_before = 0.0
    started = time.monotonic()
    state = {"mode": args.mode, "status": "running", "datasets_per_family": args.datasets,
             "reference_draws": args.draws, "records": args.records, "outer_folds": 5, "inner_folds": 3,
             "smoothing_grid": [5, 20, 100, 500, 2000], "source_sha256": digest(__file__),
             "protocol_sha256": digest(protocol), "snapshot_hashes": hashes, "fit_seed": FIT_SEED,
             "numpy_version": np.__version__, "python_version": sys.version, "completed_datasets": 0,
             "elapsed_seconds": elapsed_before}
    trials = []

    def checkpoint():
        state["elapsed_seconds"] = elapsed_before + time.monotonic() - started
        state["completed_datasets"] = len(trials)
        state["aggregate"] = aggregate(trials) if trials else {}
        (output / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    try:
        for family_index, family in enumerate(FAMILIES):
            family_folder = output / family
            family_folder.mkdir(exist_ok=True)
            for trial_index in range(args.datasets):
                trial_path = family_folder / f"dataset_{trial_index:04d}.json"
                if trial_path.exists():
                    trial = json.loads(trial_path.read_text(encoding="utf-8"))
                    assert trial["complete"] and trial["family"] == family and trial["trial_index"] == trial_index
                    trials.append(trial)
                    continue
                generation_seed = (20261002 if args.mode == "pilot" else 30261002) + family_index * 1000000 + trial_index * 1009
                rows, generation = synthetic_rows(family, generation_seed, args.records)
                compact, observed = fit(rows, joint)
                trial = {"complete": False, "family": family, "trial_index": trial_index, "generation": generation,
                         "rows": rows, "observed": compact, "observed_full_score": observed, "references": {}}
                incomplete = family_folder / f"dataset_{trial_index:04d}.in_progress.json"
                if incomplete.exists():
                    prior_hash = digest(incomplete)
                    incomplete.rename(family_folder / f"dataset_{trial_index:04d}.interrupted_{prior_hash[:10]}.json")
                incomplete.write_text(json.dumps(trial, indent=2) + "\n", encoding="utf-8")
                for reference_index, reference in enumerate(references(family)):
                    seed_base = (400000000 if args.mode == "pilot" else 700000000) + family_index * 100000000 + trial_index * 100000 + reference_index * 50000000
                    reference_result = reference_draws(rows, reference, args.draws, seed_base, helper, joint)
                    values = [score["gain"] for score in reference_result["null"]]
                    exceedances, p_value = plus_one(compact["gain"], values)
                    reference_result.update({"exceedances": exceedances, "p_value": p_value, "seed_base": seed_base})
                    trial["references"][reference] = reference_result
                    incomplete.write_text(json.dumps(trial, indent=2) + "\n", encoding="utf-8")
                trial["complete"] = True
                trial_path.write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
                incomplete.unlink()
                trials.append(trial)
                checkpoint()
                if args.mode == "pilot" or (trial_index + 1) % 10 == 0:
                    print(json.dumps({"stage": "calibration", "family": family, "done": trial_index + 1, "total": args.datasets,
                                      "elapsed_seconds": state["elapsed_seconds"], "last_p": {name: result["p_value"] for name, result in trial["references"].items()}}), flush=True)
        state["status"] = "complete"
        checkpoint()
        result = {**state, "aggregate": aggregate(trials), "trial_file_count": len(trials),
                  "total_fitted_reference_corpora": sum(result["draws"] for trial in trials for result in trial["references"].values()),
                  "total_rejection_proposals": sum(result["proposals"] for trial in trials for result in trial["references"].values())}
        (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "calibration_complete", "elapsed_seconds": state["elapsed_seconds"], "datasets": len(trials), "aggregate": result["aggregate"]}), flush=True)
    except Exception as error:
        state["status"] = "failed"
        state["failure"] = {"exception": type(error).__name__, "message": str(error)}
        checkpoint()
        raise


def exact_space(args):
    helper, joint, hashes = freeze_sources()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"Refusing existing endpoint: {output}")
    output.mkdir(parents=True)
    started = time.monotonic()
    shutil.copyfile(__file__, output / "code_snapshot.py")
    patterns = []
    for ones in itertools.combinations(range(6), 3):
        column = [0] * 6
        for index in ones:
            column[index] = 1
        patterns.append(column)
    tables = np.asarray([list(zip(*columns)) for columns in itertools.product(patterns, repeat=3)], dtype=np.int8)
    unique_mask = np.array([len({tuple(row) for row in table}) == 6 for table in tables])
    assert len(tables) == 8000 and int(unique_mask.sum()) == 2880
    statistics = np.sum(tables[:, :, :-1] == tables[:, :, 1:], axis=(1, 2))
    encoded = {table.tobytes(): i for i, table in enumerate(tables)}
    rows = [{"record_id": str(i), "seq": tuple(map(str, row)), "artifact": str(i), "artifact_aliases": [str(i)], "stratum": ("s", "t")} for i, row in enumerate(tables[np.flatnonzero(unique_mask)[0]])]
    counts = np.zeros(len(tables), dtype=int)
    attempts = accepted = 0
    while accepted < args.exact_samples:
        proposed, _ = helper.shuffle_positions(rows, 10000000 + attempts, True)
        attempts += 1
        assert margins(proposed) == margins(rows)
        index = encoded[np.asarray([list(map(int, row["seq"])) for row in proposed], dtype=np.int8).tobytes()]
        if unique_mask[index]:
            counts[index] += 1
            accepted += 1
    spaces = {}
    for name, selected in [("record_columns", np.ones(len(tables), dtype=bool)), ("unique_columns", unique_mask)]:
        scores = statistics[selected]
        p_values = np.array([np.mean(scores >= value) for value in scores])
        spaces[name] = {"tables": int(selected.sum()), "table_probability": 1 / int(selected.sum()),
                        "statistic_counts": {str(value): int((scores == value).sum()) for value in sorted(set(scores))},
                        "exact_rejection_rates": {str(alpha): float(np.mean(p_values <= alpha)) for alpha in [.01, .05, .10]},
                        "minimum_p_value": float(p_values.min())}
    for reference in [[1.0, 2.0, 3.0], [2.0, 2.0, 2.0], []]:
        exceedances, p_value = plus_one(2.0, reference)
        assert p_value == (1 + sum(value >= 2.0 for value in reference)) / (1 + len(reference))
        assert p_value > 0
    nested_values = []
    if args.exact_nested:
        for number, table_index in enumerate(np.flatnonzero(unique_mask)):
            table = tables[table_index]
            miniature = [{"record_id": str(i), "seq": tuple(map(str, row)), "artifact": str(i), "artifact_aliases": [str(i)], "stratum": ("s", "t")} for i, row in enumerate(table)]
            compact, _ = fit(miniature, joint)
            nested_values.append({"table_index": int(table_index), **compact})
            if (number + 1) % 200 == 0:
                print(json.dumps({"stage": "exact_nested", "done": number + 1, "total": 2880, "seconds": time.monotonic() - started}), flush=True)
        scores = np.array([record["gain"] for record in nested_values])
        p_values = np.array([np.mean(scores >= value) for value in scores])
        spaces["unique_nested_full_procedure"] = {"tables": len(scores), "minimum_p_value": float(p_values.min()),
                                                    "exact_rejection_rates": {str(alpha): float(np.mean(p_values <= alpha)) for alpha in [.01, .05, .10]},
                                                    "distinct_gain_values": len(set(scores)), "gain_min_max": [float(scores.min()), float(scores.max())]}
    ordinary_feasible = Counter(len({tuple(row) for row in table}) for table in tables)
    from scipy.stats import chi2
    unique_counts = counts[unique_mask]
    expected = args.exact_samples / unique_mask.sum()
    chi_square = float(np.sum((unique_counts - expected) ** 2 / expected))
    result = {"design": "Exact binary-column conditional-space and sampler audit", "source_sha256": digest(__file__), "source_snapshots": hashes,
              "space_summaries": spaces, "column_label_permutations": math.factorial(6) ** 3,
              "multiplicity_per_record_table": (math.factorial(3) ** 2) ** 3,
              "unique_acceptance_probability": 2880 / 8000,
              "rejection_sampler": {"accepted": accepted, "proposals": attempts, "seed_base": 10000000,
                                    "acceptance_rate": accepted / attempts, "chi_square_uniformity": chi_square,
                                    "chi_square_df": int(unique_mask.sum() - 1), "diagnostic_chi_square_p": float(chi2.sf(chi_square, unique_mask.sum() - 1))},
              "ordinary_space_distinct_string_counts": dict(sorted(ordinary_feasible.items())),
              "ordinary_space_too_few_groups_for_five_outer_folds": sum(count for groups, count in ordinary_feasible.items() if groups < 5),
              "copy_space": {"latent_objects": 4, "copies_per_object": 2, "balanced_binary_latent_column_tables": 6 ** 3,
                             "balanced_binary_record_column_tables": math.comb(8, 4) ** 3,
                             "ordinary_reference_probability_of_preserving_all_copy_pairs": 6 ** 3 / math.comb(8, 4) ** 3},
              "elapsed_seconds": time.monotonic() - started}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output / "tables_and_sampler_counts.json").write_text(json.dumps({"tables": tables.tolist(), "whole_string_unique": unique_mask.tolist(), "integer_statistic": statistics.tolist(), "accepted_counts": counts.tolist()}), encoding="utf-8")
    if nested_values:
        (output / "unique_nested_scores.json").write_text(json.dumps(nested_values), encoding="utf-8")
    print(json.dumps({"stage": "exact_complete", "seconds": result["elapsed_seconds"], "result": result}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pilot", "main", "exact"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--datasets", type=int, default=3)
    parser.add_argument("--draws", type=int, default=9)
    parser.add_argument("--records", type=int, default=40)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--exact-samples", type=int, default=100000)
    parser.add_argument("--exact-nested", action="store_true")
    args = parser.parse_args()
    if args.mode == "exact":
        exact_space(args)
    else:
        run_study(args)
