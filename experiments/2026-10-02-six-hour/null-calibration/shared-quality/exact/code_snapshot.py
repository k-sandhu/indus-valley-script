"""Known-law calibration with an observed object quality shared across slots."""
from collections import Counter, defaultdict
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import shutil
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
FOLDER = PARENT / "shared-quality"
FACE_SOURCE = PARENT / "noisy-faces/main/code_snapshot.py"
FACE_HASH = "836c686a67e9fb4365e45485bf898863da05aaedfe50a3ca3e73dbf47cbb654a"
RATES = {"low_error": .025, "high_error": .60}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def methods():
    assert digest(FACE_SOURCE) == FACE_HASH
    spec = importlib.util.spec_from_file_location("quality_face_snapshot", FACE_SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    old, helper, joint, hashes = module.preserved_methods()
    return module, old, helper, joint, hashes


def population(seed):
    rng = np.random.default_rng(seed)
    p = np.array([.20, .16, .14, .12, .11, .10, .09, .08])
    rows, truth = [], []
    for index in range(20):
        site = index // 10
        quality = "low_error" if index % 10 < 5 else "high_error"
        latent = [int(rng.choice(8, p=np.roll(p, site + 2 * slot))) for slot in range(3)]
        artifact = f"artifact_{index:03d}"
        face_truth = []
        for face in range(2):
            observed, replaced = [], []
            for sign in latent:
                changed = bool(rng.random() < RATES[quality])
                value = int(rng.choice([code for code in range(8) if code != sign])) if changed else sign
                observed.append(f"{value + 1:03d}")
                replaced.append(changed)
            rows.append({"record_id": f"record_{len(rows):03d}", "seq": tuple(observed), "artifact": artifact,
                         "artifact_aliases": [artifact], "site": f"site_{site}", "object_type": "SEAL:S",
                         "quality": quality, "stratum": (f"site_{site}", "SEAL:S")})
            face_truth.append({"face": face, "replacement_indicators": replaced})
        truth.append({"artifact": artifact, "quality": quality, "latent_seq": [f"{sign + 1:03d}" for sign in latent],
                      "faces": face_truth})
    return rows, {"seed": seed, "latent_objects": 20, "rates": RATES, "truth": truth}


def vector_cells(rows, condition_quality):
    blocks = defaultdict(list)
    for index, row in enumerate(rows):
        blocks[row["artifact"]].append(index)
    cells = defaultdict(list)
    for _, indices in sorted(blocks.items()):
        pair = sorted(indices, key=lambda index: rows[index]["record_id"])
        assert len(pair) == 2
        left, right = [rows[index] for index in pair]
        assert left["quality"] == right["quality"] and left["stratum"] == right["stratum"]
        profile = (len(left["seq"]), tuple(left["stratum"]), left["quality"] if condition_quality else "")
        cells[profile].append(pair)
    return cells


def margins(rows, condition_quality):
    values = {}
    for profile, pairs in vector_cells(rows, condition_quality).items():
        for slot in range(profile[0]):
            values[(profile, slot)] = Counter(tuple(rows[index]["seq"][slot] for index in pair) for pair in pairs)
    return values


def shuffle(rows, seed, condition_quality):
    cells = vector_cells(rows, condition_quality)
    rng = random.Random(seed)
    values = [list(row["seq"]) for row in rows]
    for profile, pairs in sorted(cells.items()):
        for slot in range(profile[0]):
            vectors = [tuple(rows[index]["seq"][slot] for index in pair) for pair in pairs]
            rng.shuffle(vectors)
            for pair, vector in zip(pairs, vectors):
                for index, sign in zip(pair, vector):
                    values[index][slot] = sign
    return [dict(row, seq=tuple(value)) for row, value in zip(rows, values)]


def total_fit(rows, old, helper, joint):
    groups = helper.group_records(rows)
    if len(groups) >= 5:
        compact, full = old.fit(rows, joint)
        assert np.isfinite(compact["gain"])
        return dict(compact, guarded=False), full
    _, loads = helper.make_folds(rows, groups, 5, old.FIT_SEED)
    return {"gain": 0.0, "guarded": True, "grouping": {"groups": len(groups), "largest_group": max(map(len, groups)),
            "fold_loads": loads}, "chosen_models": [], "baseline_loss": None, "dependent_loss": None}, None


def run(args):
    _, old, helper, joint, hashes = methods()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Refusing an existing shared-quality endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    state = {"status": "running", "simulation": True, "mode": args.mode, "datasets": args.datasets, "draws": args.draws,
             "objects": 20, "records": 40, "slots": 3, "alphabet": 8, "rates": RATES,
             "outer_folds": 5, "inner_folds": 3, "smoothing_grid": [5, 20, 100, 500, 2000], "fit_seed": old.FIT_SEED,
             "source_sha256": digest(__file__), "protocol_sha256": digest(FOLDER / "PROTOCOL.md"),
             "budget_sha256": digest(FOLDER / "MAIN_BUDGET.md") if args.mode == "main" else None,
             "face_snapshot_sha256": FACE_HASH, "snapshot_hashes": hashes, "numpy_version": np.__version__,
             "python_version": sys.version, "completed_datasets": 0, "observed_guarded": 0,
             "reference_guarded": {name: 0 for name in ["broad_vectors", "quality_vectors"]}}
    started, summaries = time.monotonic(), []

    def save():
        state["elapsed_seconds"] = time.monotonic() - started
        state["completed_datasets"] = len(summaries)
        state["aggregate"] = old.aggregate(summaries) if summaries else {}
        (output / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    try:
        for index in range(args.datasets):
            generation_seed = (70261002 if args.mode == "pilot" else 60261002) + 1009 * index
            rows, generation = population(generation_seed)
            observed, full = total_fit(rows, old, helper, joint)
            state["observed_guarded"] += observed["guarded"]
            trial = {"complete": False, "family": "shared_quality", "trial_index": index, "rows": rows,
                     "generation": generation, "observed": observed, "observed_full_score": full, "references": {}}
            incomplete = output / f"dataset_{index:04d}.in_progress.json"
            incomplete.write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            target_broad, target_quality = margins(rows, False), margins(rows, True)
            target_record = old.margins(rows)
            for ref_index, name in enumerate(["broad_vectors", "quality_vectors"]):
                seed_base = (100000000000 if args.mode == "pilot" else 60000000000) + 20000000000 * ref_index + 1000000 * index
                values = []
                for draw in range(args.draws):
                    proposed = shuffle(rows, seed_base + draw, name == "quality_vectors")
                    assert margins(proposed, False) == target_broad and old.margins(proposed) == target_record
                    assert all(all(before[key] == after[key] for key in before if key != "seq") for before, after in zip(rows, proposed))
                    changed = margins(proposed, True) != target_quality
                    if name == "quality_vectors":
                        assert not changed
                    compact, _ = total_fit(proposed, old, helper, joint)
                    compact.update({"proposal_seed": seed_base + draw, "quality_margin_changed": changed})
                    state["reference_guarded"][name] += compact["guarded"]
                    values.append(compact)
                exceedances, p_value = old.plus_one(observed["gain"], [score["gain"] for score in values])
                trial["references"][name] = {"draws": args.draws, "proposals": args.draws, "seed_base": seed_base,
                                             "accepted_seeds": list(range(seed_base, seed_base + args.draws)), "null": values,
                                             "exceedances": exceedances, "p_value": p_value,
                                             "reported_p_value": 1.0 if observed["guarded"] else p_value,
                                             "abstained": observed["guarded"]}
                incomplete.write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            trial["complete"] = True
            (output / f"dataset_{index:04d}.json").write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            incomplete.unlink()
            summaries.append({"family": trial["family"], "references": {name: {"p_value": r["reported_p_value"]} for name, r in trial["references"].items()}})
            save()
            if args.mode == "pilot" or (index + 1) % 10 == 0:
                print(json.dumps({"stage": "shared_quality", "done": index + 1, "total": args.datasets,
                                  "elapsed_seconds": state["elapsed_seconds"], "observed_guarded": state["observed_guarded"]}), flush=True)
        state["status"] = "complete"
        state["reference_corpora"] = 2 * args.datasets * args.draws
        save()
        (output / "results.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "shared_quality_complete", "elapsed_seconds": state["elapsed_seconds"],
                          "observed_guarded": state["observed_guarded"], "reference_guarded": state["reference_guarded"],
                          "aggregate": state["aggregate"]}), flush=True)
    except Exception as error:
        state["status"] = "failed"
        state["failure"] = {"exception": type(error).__name__, "message": str(error)}
        save()
        raise


def rational_vector_probability(vector, epsilon):
    p = [Fraction(value, 100) for value in [20, 16, 14, 12, 11, 10, 9, 8]]
    def kernel(y, x):
        return 1 - epsilon if y == x else epsilon / 7
    return sum(p[x] * kernel(vector[0], x) * kernel(vector[1], x) for x in range(8))


def exact(args):
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Refusing an existing quality exact endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    vectors = [(0, 0), (0, 0), (0, 1), (0, 1)]
    columns = sorted(set(itertools.permutations(vectors)))
    probabilities = {q: {v: rational_vector_probability(v, epsilon) for v in set(vectors)}
                     for q, epsilon in [("low_error", Fraction(1, 40)), ("high_error", Fraction(3, 5))]}
    weights = {column: probabilities["low_error"][column[0]] * probabilities["low_error"][column[1]] *
                        probabilities["high_error"][column[2]] * probabilities["high_error"][column[3]] for column in columns}
    z = sum(weights.values())
    selected = [column for column in columns if Counter(column[:2]) == Counter([(0, 0), (0, 1)])]
    assert len(selected) == 4 and len({weights[column] for column in selected}) == 1
    rows = [{"record_id": str(2 * obj + face), "artifact": str(obj), "artifact_aliases": [str(obj)],
             "seq": (str(vector[face]),) * 3, "quality": "low_error" if obj < 2 else "high_error",
             "stratum": ("site", "type")} for obj, vector in enumerate([(0, 0), (0, 1), (0, 0), (0, 1)]) for face in range(2)]
    counts = Counter()
    for draw in range(20000):
        proposed = shuffle(rows, 140000000000 + draw, True)
        assert margins(proposed, True) == margins(rows, True)
        table = tuple(tuple((int(proposed[2 * obj]["seq"][slot]), int(proposed[2 * obj + 1]["seq"][slot])) for obj in range(4)) for slot in range(3))
        counts[table] += 1
    tables = list(itertools.product(selected, repeat=3))
    assert set(counts) == set(tables)
    result = {"simulation": True, "status": "complete", "source_sha256": digest(__file__),
              "protocol_sha256": digest(FOLDER / "PROTOCOL.md"), "broad_columns": len(columns), "broad_tables": len(columns)**3,
              "quality_columns": len(selected), "quality_tables": len(tables), "quality_table_probability": "1/64",
              "broad_column_probabilities": [{"column": c, "probability": str(weights[c] / z)} for c in columns],
              "quality_column_probabilities": [{"column": c, "probability": "1/4"} for c in selected],
              "broad_max_min_probability_ratio": str(max(weights.values()) / min(weights.values())),
              "draws": 20000, "seed_base": 140000000000,
              "table_counts": [{"table": t, "count": counts[t]} for t in tables]}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ["table_counts", "broad_column_probabilities", "quality_column_probabilities"]}))


def tests():
    _, old, helper, joint, _ = methods()
    rows, truth = population(71261002)
    assert population(71261002) == (rows, truth)
    fitted, _ = total_fit(rows, old, helper, joint)
    relabeled, _ = total_fit([dict(row, quality="ignored") for row in rows], old, helper, joint)
    assert fitted == relabeled and not fitted["guarded"]
    for condition in [False, True]:
        proposed = shuffle(rows, 141000000000, condition)
        assert margins(proposed, False) == margins(rows, False)
        if condition:
            assert margins(proposed, True) == margins(rows, True)
    guarded, full = total_fit([dict(row, seq=("001", "001", "001")) for row in rows], old, helper, joint)
    assert guarded["guarded"] and guarded["gain"] == 0 and full is None and guarded["grouping"]["groups"] == 1
    assert old.plus_one(2, [1, 2, 3]) == (2, .75)
    print(json.dumps({"status": "pass", "checks": ["generator_replay", "quality_ignored_by_statistic", "vector_margins", "one_component_total_guard", "inclusive_rank"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["test", "pilot", "main", "exact"])
    parser.add_argument("--output")
    parser.add_argument("--datasets", type=int, default=2)
    parser.add_argument("--draws", type=int, default=9)
    args = parser.parse_args()
    if args.mode == "test":
        tests()
    elif args.mode == "exact":
        exact(args)
    else:
        run(args)
