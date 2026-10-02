"""Independent face-vector permutation and full known-law calibration audit."""
from collections import Counter, defaultdict
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

import numpy as np

HERE = Path(__file__).parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def pairs(rows):
    blocks = defaultdict(list)
    for i, row in enumerate(rows):
        blocks[row["artifact"]].append(i)
    return [sorted(indices, key=lambda i: rows[i]["record_id"]) for _, indices in sorted(blocks.items())]


def joint_counts(rows):
    counts = defaultdict(Counter)
    for pair in pairs(rows):
        assert len(pair) == 2
        left, right = [rows[i] for i in pair]
        assert left["stratum"] == right["stratum"] and len(left["seq"]) == len(right["seq"])
        for slot in range(len(left["seq"])):
            counts[(len(left["seq"]), tuple(left["stratum"]), slot)][(left["seq"][slot], right["seq"][slot])] += 1
    return dict(counts)


def oracle_shuffle(rows, seed):
    groups = defaultdict(list)
    for pair in pairs(rows):
        groups[(len(rows[pair[0]]["seq"]), tuple(rows[pair[0]]["stratum"]))].append(pair)
    values = [list(row["seq"]) for row in rows]
    rng = random.Random(seed)
    for profile in sorted(groups):
        indices = groups[profile]
        for column in range(profile[0]):
            source = [(rows[pair[0]]["seq"][column], rows[pair[1]]["seq"][column]) for pair in indices]
            rng.shuffle(source)
            for pair, vector in zip(indices, source):
                values[pair[0]][column], values[pair[1]][column] = vector
    return [dict(row, seq=tuple(value)) for row, value in zip(rows, values)]


def exact():
    result = json.loads((HERE / "exact/results.json").read_text(encoding="utf-8"))
    assert sha(HERE / "exact/code_snapshot.py") == result["source_sha256"]
    for case in result["cases"]:
        vectors = list(map(tuple, case["vectors"]))
        permutations = Counter(itertools.permutations(vectors))
        assert len(permutations) == case["distinct_columns"]
        assert set(permutations.values()) == {case["column_multiplicity"]}
        assert sum(permutations.values()) == case["labeled_column_permutations"] == 24
        assert Fraction(case["column_multiplicity"], 24) ** 3 == Fraction(case["table_probability"])
        observed = {tuple(tuple(tuple(vector) for vector in column) for column in row["columns"]): row["samples"] for row in case["table_counts"]}
        assert set(observed) == set(itertools.product(permutations, repeat=3))
        rows = [{"record_id": str(2 * artifact + face), "artifact": str(artifact), "artifact_aliases": [str(artifact)],
                 "seq": (str(vector[face]),) * 3, "stratum": ("site", "type")}
                for artifact, vector in enumerate(vectors) for face in range(2)]
        counted = Counter()
        for draw in range(case["samples"]):
            changed = oracle_shuffle(rows, case["seed_base"] + case["seed_step"] * draw)
            table = tuple(tuple((int(changed[2 * artifact]["seq"][slot]), int(changed[2 * artifact + 1]["seq"][slot])) for artifact in range(4)) for slot in range(3))
            counted[table] += 1
        assert dict(counted) == {table: count for table, count in observed.items() if count}
        expected = case["samples"] / case["tables"]
        statistic = sum((count - expected) ** 2 / expected for count in observed.values())
        assert abs(statistic - case["chi_square"]) < 1e-7
    return {"status": "pass", "cases": 2, "enumerated_tables": 14040, "independent_stream_draws_replayed": 200000,
            "checks": ["permutation_multiplicity", "exact_table_probability", "table_space_correspondence",
                       "full_independent_sampler_stream_replay", "sample_count_diagnostics"]}


def main_study():
    folder = HERE / "main"
    state = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    assert state["status"] == "complete" and state["datasets"] == 1000 and state["draws"] == 99
    assert sha(folder / "code_snapshot.py") == state["source_sha256"]
    assert sha(HERE / "MAIN_BUDGET.md") == state["protocol_sha256"]
    assert sha(HERE / "PROTOCOL.md") == state["initial_protocol_sha256"]
    module = load(folder / "code_snapshot.py", "noisy_face_snapshot")
    old, helper, joint, hashes = module.preserved_methods()
    assert hashes == state["snapshot_hashes"]
    independent = load(HERE.parent / "verify_result.py", "independent_group_audit")
    summaries, indicator, seed_uses = [], [], set()
    reference_count = fit_replays = 0
    equal_slots = equal_strings = replaced_slots = total_face_slots = 0
    observed_groups, reference_groups = [], defaultdict(list)
    choices, changed_vectors = defaultdict(Counter), Counter()
    for i in range(1000):
        trial = json.loads((folder / f"dataset_{i:04d}.json").read_text(encoding="utf-8"))
        assert trial["complete"] and trial["trial_index"] == i
        rows, generation = module.population(40261002 + 1009 * i)
        assert json.loads(json.dumps(rows)) == trial["rows"] and generation == trial["generation"]
        assert independent.graph_oracle(rows, old.FIT_SEED) == trial["observed"]["grouping"]
        observed_groups.append(trial["observed"]["grouping"]["groups"])
        original_joint = joint_counts(rows)
        for pair, truth in zip(pairs(rows), generation["truth"]):
            left, right = [rows[index] for index in pair]
            equal_strings += left["seq"] == right["seq"]
            equal_slots += sum(a == b for a, b in zip(left["seq"], right["seq"]))
            for face, index in zip(truth["faces"], pair):
                for replaced, observed, latent in zip(face["replacement_indicators"], rows[index]["seq"], truth["latent_seq"]):
                    assert replaced == (observed != latent)
                    replaced_slots += replaced
                    total_face_slots += 1
        if i in [0, 499, 999]:
            fitted, _ = old.fit(rows, joint)
            assert json.loads(json.dumps(fitted)) == trial["observed"]
            fit_replays += 1
        for name, result in trial["references"].items():
            values = [score["gain"] for score in result["null"]]
            assert len(values) == result["draws"] == 99
            base = (20000000000 if name == "record_columns" else 40000000000) + i * 1000000
            assert result["seed_base"] == base and result["accepted_seeds"] == list(range(base, base + 99))
            assert not seed_uses.intersection(result["accepted_seeds"])
            seed_uses.update(result["accepted_seeds"])
            assert old.plus_one(trial["observed"]["gain"], values) == (result["exceedances"], result["p_value"])
            changes = 0
            for draw, score in enumerate(result["null"]):
                seed = base + draw
                assert score["proposal_seed"] == seed
                proposed = oracle_shuffle(rows, seed) if name == "face_vectors" else helper.shuffle_positions(rows, seed, True)[0]
                assert old.margins(proposed) == old.margins(rows)
                assert all(all(before[key] == after[key] for key in before if key != "seq") for before, after in zip(rows, proposed))
                changed = joint_counts(proposed) != original_joint
                changes += changed
                assert changed == score["vector_margin_changed"]
                if name == "face_vectors":
                    assert not changed
                assert independent.graph_oracle(proposed, old.FIT_SEED) == score["grouping"]
                reference_groups[name].append(score["grouping"]["groups"])
                for baseline, dependent in score["chosen_models"]:
                    choices[name + "/baseline"][json.dumps(baseline, sort_keys=True)] += 1
                    choices[name + "/dependent"][json.dumps(dependent, sort_keys=True)] += 1
                if i in [0, 499, 999] and draw in [0, 98]:
                    fitted, _ = old.fit(proposed, joint)
                    assert all(json.loads(json.dumps(value)) == score[key] for key, value in fitted.items())
                    fit_replays += 1
                reference_count += 1
            assert changes == result["changed_vector_margin_draws"]
            changed_vectors[name] += changes
        summaries.append({"family": "noisy_faces", "references": {name: {"p_value": result["p_value"]} for name, result in trial["references"].items()}})
        indicator.append([[int(trial["references"][name]["p_value"] <= alpha) for alpha in [.01, .05, .1]] for name in ["record_columns", "face_vectors"]])
    assert old.aggregate(summaries) == state["aggregate"]
    assert reference_count == state["total_fitted_reference_corpora"] == 198000
    indicator = np.asarray(indicator)
    differences = indicator[:, 0] - indicator[:, 1]
    rng = np.random.default_rng(2026100204)
    means = np.concatenate([differences[rng.integers(1000, size=(1000, 1000))].mean(axis=1) for _ in range(20)])
    intervals = np.quantile(means, [.025, .975], axis=0)
    paired = {}
    for j, alpha in enumerate([.01, .05, .1]):
        record, vector = indicator[:, 0, j], indicator[:, 1, j]
        paired[str(alpha)] = {"both": int(np.sum((record == 1) & (vector == 1))),
                              "record_only": int(np.sum((record == 1) & (vector == 0))),
                              "vector_only": int(np.sum((record == 0) & (vector == 1))),
                              "neither": int(np.sum((record == 0) & (vector == 0))),
                              "rate_difference": float(differences[:, j].mean()), "paired_95_interval": intervals[:, j].tolist()}
    return {"status": "pass", "datasets_checked": 1000, "reference_corpora_checked": reference_count,
            "complete_fits_replayed": fit_replays, "distinct_reference_seeds": len(seed_uses),
            "observed_group_range": [min(observed_groups), max(observed_groups)],
            "reference_group_ranges": {name: [min(values), max(values)] for name, values in reference_groups.items()},
            "reference_changed_joint_vector_draws": dict(changed_vectors),
            "equal_face_slots": equal_slots, "total_object_slots": 60000, "equal_face_strings": equal_strings,
            "total_objects": 20000, "replaced_face_slots": replaced_slots, "total_face_slots": total_face_slots,
            "chosen_model_counts": {name: dict(counts) for name, counts in choices.items()}, "paired_rejection": paired,
            "bootstrap_seed": 2026100204, "bootstrap_replicates": 20000,
            "checks": ["source_hashes", "all_observed_generation_and_latent_truth", "independent_vector_shuffle",
                       "all_record_and_joint_vector_margins", "metadata_preservation", "independent_groups_and_fold_loads",
                       "plus_one_p_values", "all_reference_seed_uniqueness", "selected_full_fit_replays", "aggregate",
                       "paired_rejections_and_bootstrap"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["exact", "main"])
    args = parser.parse_args()
    result = exact() if args.phase == "exact" else main_study()
    result["audit_source_sha256"] = sha(Path(__file__))
    destination = HERE / f"verification_{args.phase}.json"
    if destination.exists():
        raise FileExistsError("Refusing an existing noisy-face verification record")
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "chosen_model_counts"}, indent=2))
