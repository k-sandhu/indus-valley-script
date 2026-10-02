"""Conditional calibration with correlated, nonidentical faces of latent objects."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import random
import shutil
import sys
import time

import numpy as np

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "knowledge").is_dir() and (parent / "src/methods").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
FOLDER = PARENT / "noisy-faces"
ORIGINAL = PARENT / "main/code_snapshot.py"
ORIGINAL_HASH = "5a313b3cd97dc4687cb8259a4f1e6e616ec3869b8ab54a0fee0969ca0b8032b5"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def preserved_methods():
    assert digest(ORIGINAL) == ORIGINAL_HASH
    spec = importlib.util.spec_from_file_location("preserved_null_calibration", ORIGINAL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    helper, joint, hashes = module.freeze_sources()
    return module, helper, joint, hashes


def population(seed, error_probability=.1, objects=20):
    assert objects % 2 == 0
    rng = np.random.default_rng(seed)
    rows, truth = [], []
    probabilities = np.array([.20, .16, .14, .12, .11, .10, .09, .08])
    for index in range(objects):
        stratum = 0 if index < objects // 2 else 1
        latent = tuple(int(rng.choice(8, p=np.roll(probabilities, stratum + 2 * slot))) for slot in range(3))
        artifact = f"artifact_{index:03d}"
        face_truth = []
        for face in range(2):
            observed, replaced = [], []
            for sign in latent:
                changed = bool(rng.random() < error_probability)
                value = int(rng.choice([code for code in range(8) if code != sign])) if changed else sign
                observed.append(f"{value + 1:03d}")
                replaced.append(changed)
            rows.append({"record_id": f"record_{len(rows):03d}", "seq": tuple(observed), "artifact": artifact,
                         "artifact_aliases": [artifact], "site": f"site_{stratum}", "object_type": "SEAL:S",
                         "stratum": (f"site_{stratum}", "SEAL:S")})
            face_truth.append({"face": face, "replacement_indicators": replaced})
        truth.append({"artifact": artifact, "latent_seq": [f"{sign + 1:03d}" for sign in latent], "faces": face_truth})
    return rows, {"seed": seed, "latent_objects": objects, "error_probability": error_probability, "truth": truth}


def ordered_blocks(rows):
    blocks = defaultdict(list)
    for index, row in enumerate(rows):
        blocks[row["artifact"]].append(index)
    ordered = []
    for artifact, indices in sorted(blocks.items()):
        indices.sort(key=lambda index: rows[index]["record_id"])
        assert len(indices) == 2
        left, right = [rows[index] for index in indices]
        assert left["stratum"] == right["stratum"] and len(left["seq"]) == len(right["seq"])
        assert left["artifact_aliases"] == right["artifact_aliases"]
        ordered.append((artifact, indices, (len(left["seq"]), tuple(left["stratum"]))))
    return ordered


def vector_margins(rows):
    cells = defaultdict(Counter)
    for _, indices, profile in ordered_blocks(rows):
        for slot in range(profile[0]):
            vector = tuple(rows[index]["seq"][slot] for index in indices)
            cells[(profile, slot)][vector] += 1
    return {cell: dict(counts) for cell, counts in cells.items()}


def vector_shuffle(rows, seed):
    rng = random.Random(seed)
    changed = [list(row["seq"]) for row in rows]
    cells = defaultdict(list)
    for _, indices, profile in ordered_blocks(rows):
        cells[profile].append(indices)
    for profile, blocks in sorted(cells.items()):
        for slot in range(profile[0]):
            vectors = [tuple(rows[index]["seq"][slot] for index in pair) for pair in blocks]
            rng.shuffle(vectors)
            for pair, vector in zip(blocks, vectors):
                for index, sign in zip(pair, vector):
                    changed[index][slot] = sign
    return [dict(row, seq=tuple(sequence)) for row, sequence in zip(rows, changed)]


def reference(rows, name, draws, seed_base, old, helper, joint):
    target = old.margins(rows)
    joint_target = vector_margins(rows)
    values = []
    changed_vectors = 0
    for index in range(draws):
        seed = seed_base + index
        proposed = vector_shuffle(rows, seed) if name == "face_vectors" else helper.shuffle_positions(rows, seed, True)[0]
        assert old.margins(proposed) == target
        assert all(all(before[key] == after[key] for key in before if key != "seq") for before, after in zip(rows, proposed))
        vector_changed = vector_margins(proposed) != joint_target
        changed_vectors += vector_changed
        if name == "face_vectors":
            assert not vector_changed
        compact, _ = old.fit(proposed, joint)
        compact["proposal_seed"] = seed
        compact["vector_margin_changed"] = vector_changed
        values.append(compact)
    return {"draws": draws, "proposals": draws, "seed_base": seed_base,
            "accepted_seeds": [seed_base + index for index in range(draws)], "null": values,
            "changed_vector_margin_draws": changed_vectors}


def run(args):
    old, helper, joint, hashes = preserved_methods()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Refusing an existing multi-face endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    protocol = FOLDER / ("PROTOCOL.md" if args.mode == "pilot" else "MAIN_BUDGET.md")
    state = {"status": "running", "mode": args.mode, "datasets": args.datasets, "draws": args.draws,
             "objects": 20, "records": 40, "error_probability": .1, "outer_folds": 5, "inner_folds": 3,
             "smoothing_grid": [5, 20, 100, 500, 2000], "fit_seed": old.FIT_SEED,
             "source_sha256": digest(__file__), "protocol_sha256": digest(protocol),
             "initial_protocol_sha256": digest(FOLDER / "PROTOCOL.md"),
             "preserved_null_calibration_sha256": ORIGINAL_HASH, "snapshot_hashes": hashes,
             "numpy_version": np.__version__, "python_version": sys.version,
             "completed_datasets": 0, "elapsed_seconds": 0.0}
    summaries = []
    started = time.monotonic()

    def checkpoint():
        state["completed_datasets"] = len(summaries)
        state["elapsed_seconds"] = time.monotonic() - started
        state["aggregate"] = old.aggregate(summaries) if summaries else {}
        (output / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    try:
        for index in range(args.datasets):
            seed = (50261002 if args.mode == "pilot" else 40261002) + 1009 * index
            rows, generation = population(seed)
            observed, full = old.fit(rows, joint)
            trial = {"complete": False, "family": "noisy_faces", "trial_index": index, "rows": rows,
                     "generation": generation, "observed": observed, "observed_full_score": full, "references": {}}
            incomplete = output / f"dataset_{index:04d}.in_progress.json"
            incomplete.write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            for reference_index, name in enumerate(["record_columns", "face_vectors"]):
                base = (6000000000 if args.mode == "pilot" else 2000000000) + 2000000000 * reference_index + 1000000 * index
                fitted = reference(rows, name, args.draws, base, old, helper, joint)
                fitted["exceedances"], fitted["p_value"] = old.plus_one(observed["gain"], [value["gain"] for value in fitted["null"]])
                trial["references"][name] = fitted
                incomplete.write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            trial["complete"] = True
            (output / f"dataset_{index:04d}.json").write_text(json.dumps(trial, separators=(",", ":")) + "\n", encoding="utf-8")
            incomplete.unlink()
            summaries.append({"family": "noisy_faces", "references": {name: {"p_value": record["p_value"]} for name, record in trial["references"].items()}})
            checkpoint()
            if args.mode == "pilot" or (index + 1) % 10 == 0:
                print(json.dumps({"stage": "multi_face_calibration", "done": index + 1, "total": args.datasets,
                                  "elapsed_seconds": state["elapsed_seconds"]}), flush=True)
        state["status"] = "complete"
        state["total_fitted_reference_corpora"] = 2 * args.datasets * args.draws
        checkpoint()
        (output / "results.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "multi_face_complete", "elapsed_seconds": state["elapsed_seconds"], "aggregate": state["aggregate"]}), flush=True)
    except Exception as error:
        state["status"] = "failed"
        state["failure"] = {"exception": type(error).__name__, "message": str(error)}
        checkpoint()
        raise


def exact(args):
    old, _, _, _ = preserved_methods()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("Refusing an existing face-vector enumeration")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    results = []
    from scipy.stats import chi2
    for case_index, vectors in enumerate([[(0, 0), (0, 1), (1, 0), (1, 1)], [(0, 0), (0, 0), (1, 1), (1, 1)]]):
        labeled = Counter(itertools.permutations(vectors))
        assert len(set(labeled.values())) == 1
        columns = list(labeled)
        tables = list(itertools.product(columns, repeat=3))
        rows = []
        for artifact, vector in enumerate(vectors):
            for face in range(2):
                rows.append({"record_id": str(len(rows)), "seq": (str(vector[face]),) * 3,
                             "artifact": str(artifact), "artifact_aliases": [str(artifact)], "stratum": ("site", "type")})
        target, vector_target = old.margins(rows), vector_margins(rows)
        counts = Counter()
        seed_base = 2026100205 + case_index
        for draw in range(100000):
            changed = vector_shuffle(rows, seed_base + 100 * draw)
            assert old.margins(changed) == target and vector_margins(changed) == vector_target
            encoded = tuple(tuple((changed[2 * artifact]["seq"][slot], changed[2 * artifact + 1]["seq"][slot]) for artifact in range(4)) for slot in range(3))
            counts[encoded] += 1
        table_rows = []
        expected = 100000 / len(tables)
        statistic = 0.0
        for table in tables:
            encoded = tuple(tuple(tuple(map(str, vector)) for vector in column) for column in table)
            count = counts[encoded]
            statistic += (count - expected) ** 2 / expected
            table_rows.append({"columns": table, "samples": count})
        assert sum(row["samples"] for row in table_rows) == 100000
        results.append({"vectors": vectors, "distinct_columns": len(columns), "tables": len(tables),
                        "labeled_column_permutations": sum(labeled.values()), "column_multiplicity": next(iter(labeled.values())),
                        "table_probability": f"1/{len(tables)}", "samples": 100000, "seed_base": seed_base, "seed_step": 100,
                        "chi_square": statistic, "degrees_of_freedom": len(tables) - 1,
                        "diagnostic_p": float(chi2.sf(statistic, len(tables) - 1)), "table_counts": table_rows})
    result = {"source_sha256": digest(__file__), "cases": results,
              "checks": ["complete_vector_column_enumeration", "equal_permutation_multiplicity",
                         "expanded_record_margins", "joint_vector_margins", "draw_count"]}
    (output / "results.json").write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"stage": "vector_exact_complete", "cases": [{key: value for key, value in case.items() if key != "table_counts"} for case in results]}))


def tests():
    old, _, _, _ = preserved_methods()
    for probability in [0., .1, 1.]:
        rows, truth = population(20261002, probability)
        assert population(20261002, probability) == (rows, truth)
        for artifact in truth["truth"]:
            copies = [row for row in rows if row["artifact"] == artifact["artifact"]]
            for row, face in zip(copies, artifact["faces"]):
                assert all(changed == (observed != latent) for changed, observed, latent in zip(face["replacement_indicators"], row["seq"], artifact["latent_seq"]))
                if probability == 0:
                    assert row["seq"] == tuple(artifact["latent_seq"])
                if probability == 1:
                    assert all(face["replacement_indicators"])
        proposed = vector_shuffle(rows, 82)
        assert old.margins(proposed) == old.margins(rows)
        assert vector_margins(proposed) == vector_margins(rows)
        assert all(all(before[key] == after[key] for key in before if key != "seq") for before, after in zip(rows, proposed))
    assert old.plus_one(2, [1, 2, 3]) == (2, .75)
    print(json.dumps({"status": "pass", "generator_error_settings": [0, .1, 1],
                      "checks": ["generator_replay", "latent_truth_correspondence", "face_vector_margins", "record_margins", "metadata", "plus_one_ties"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["test", "exact", "pilot", "main"])
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
