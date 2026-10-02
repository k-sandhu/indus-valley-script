"""Independent vector, graph, rank and rational-law audit for shared quality."""
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
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
FOLDER = PARENT / "shared-quality"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def pairs(rows):
    indices = defaultdict(list)
    for i, row in enumerate(rows):
        indices[row["artifact"]].append(i)
    return [sorted(items, key=lambda i: rows[i]["record_id"]) for _, items in sorted(indices.items())]


def joint_counts(rows, condition_quality):
    counts = defaultdict(Counter)
    for left, right in pairs(rows):
        a, b = rows[left], rows[right]
        assert a["quality"] == b["quality"] and a["stratum"] == b["stratum"]
        q = a["quality"] if condition_quality else ""
        for slot, (x, y) in enumerate(zip(a["seq"], b["seq"])):
            counts[(len(a["seq"]), tuple(a["stratum"]), q, slot)][(x, y)] += 1
    return dict(counts)


def scalar_counts(rows):
    counts = defaultdict(Counter)
    for row in rows:
        for slot, x in enumerate(row["seq"]):
            counts[(len(row["seq"]), tuple(row["stratum"]), slot)][x] += 1
    return dict(counts)


def oracle_shuffle(rows, seed, quality):
    groups = defaultdict(list)
    for pair in pairs(rows):
        row = rows[pair[0]]
        groups[(len(row["seq"]), tuple(row["stratum"]), row["quality"] if quality else "")].append(pair)
    rng = random.Random(seed)
    new = [list(row["seq"]) for row in rows]
    for (length, _, _), group in sorted(groups.items()):
        for slot in range(length):
            vectors = [(rows[a]["seq"][slot], rows[b]["seq"][slot]) for a, b in group]
            rng.shuffle(vectors)
            for (a, b), (x, y) in zip(group, vectors):
                new[a][slot], new[b][slot] = x, y
    return [dict(row, seq=tuple(value)) for row, value in zip(rows, new)]


def normalized(value):
    return json.loads(json.dumps(value))


def exact():
    result = json.loads((FOLDER / "exact/results.json").read_text())
    assert sha(FOLDER / "exact/code_snapshot.py") == result["source_sha256"]
    p = [Fraction(v, 100) for v in [20, 16, 14, 12, 11, 10, 9, 8]]
    probabilities = {}
    for q, e in [("low_error", Fraction(1, 40)), ("high_error", Fraction(3, 5))]:
        kernel = [[1 - e if observed == latent else e / 7 for observed in range(8)] for latent in range(8)]
        assert all(sum(row) == 1 for row in kernel)
        probabilities[q] = {(a, b): sum(p[x] * kernel[x][a] * kernel[x][b] for x in range(8)) for a in range(8) for b in range(8)}
        assert sum(probabilities[q].values()) == 1
    columns = sorted(set(itertools.permutations([(0, 0), (0, 0), (0, 1), (0, 1)])))
    weights = {c: probabilities["low_error"][c[0]] * probabilities["low_error"][c[1]] *
                  probabilities["high_error"][c[2]] * probabilities["high_error"][c[3]] for c in columns}
    z = sum(weights.values())
    assert [{"column": normalized(c), "probability": str(weights[c] / z)} for c in columns] == result["broad_column_probabilities"]
    assert len(set(weights.values())) > 1 and str(max(weights.values()) / min(weights.values())) == result["broad_max_min_probability_ratio"]
    selected = [c for c in columns if Counter(c[:2]) == Counter([(0, 0), (0, 1)])]
    restricted_mass = sum(weights[c] for c in selected)
    assert len(selected) == 4 and all(weights[c] / restricted_mass == Fraction(1, 4) for c in selected)
    tables = set(itertools.product(selected, repeat=3))
    expected_counts = {tuple(tuple(tuple(v) for v in c) for c in row["table"]): row["count"] for row in result["table_counts"]}
    assert len(tables) == 64 and tables == set(expected_counts)
    assert Fraction(1, 4)**3 == Fraction(result["quality_table_probability"])
    rows = [{"record_id": str(2 * obj + face), "artifact": str(obj), "artifact_aliases": [str(obj)],
             "seq": (str(vector[face]),) * 3, "quality": "low_error" if obj < 2 else "high_error", "stratum": ("site", "type")}
            for obj, vector in enumerate([(0, 0), (0, 1), (0, 0), (0, 1)]) for face in range(2)]
    counts = Counter()
    for draw in range(result["draws"]):
        proposed = oracle_shuffle(rows, result["seed_base"] + draw, True)
        assert joint_counts(proposed, True) == joint_counts(rows, True)
        table = tuple(tuple((int(proposed[2 * obj]["seq"][slot]), int(proposed[2 * obj + 1]["seq"][slot])) for obj in range(4)) for slot in range(3))
        counts[table] += 1
    assert dict(counts) == expected_counts and sum(counts.values()) == 20000
    return {"status": "pass", "broad_columns": 6, "broad_tables": 216, "uniform_quality_tables": 64,
            "rational_vector_probabilities_checked": 128, "independent_sampler_draws_replayed": 20000,
            "broad_probability_ratio": result["broad_max_min_probability_ratio"],
            "checks": ["normalized_rational_channel", "all_broad_conditional_weights", "all_quality_conditional_weights",
                       "table_correspondence", "full_independent_stream_replay"]}


def main_study():
    folder = FOLDER / "main"
    state = json.loads((folder / "results.json").read_text())
    assert state["status"] == "complete" and state["datasets"] == 300 and state["draws"] == 99
    assert sha(folder / "code_snapshot.py") == state["source_sha256"]
    assert sha(FOLDER / "PROTOCOL.md") == state["protocol_sha256"] and sha(FOLDER / "MAIN_BUDGET.md") == state["budget_sha256"]
    module = load(folder / "code_snapshot.py", "quality_main_snapshot")
    _, old, helper, joint, hashes = module.methods()
    assert state["snapshot_hashes"] == hashes
    graph = load(PARENT / "verify_result.py", "quality_graph_auditor")
    assert sha(PARENT / "verify_result.py") == "8499e1daea45ce5cbbefc245e852abb6b7715b4d2d246cffb7a319bcaf983e77"
    summaries, indicators, observed_groups, all_seeds = [], [], [], set()
    ref_groups, guards, changes = defaultdict(list), Counter(), Counter()
    quality_truth = defaultdict(Counter)
    replayed = reference_count = observed_guarded = 0
    started = time.monotonic()
    for index in range(300):
        trial = json.loads((folder / f"dataset_{index:04d}.json").read_text())
        assert trial["complete"] and trial["trial_index"] == index
        rows, generation = module.population(60261002 + 1009 * index)
        assert normalized(rows) == trial["rows"] and generation == trial["generation"]
        grouping = graph.graph_oracle(rows, old.FIT_SEED)
        assert grouping == trial["observed"]["grouping"]
        guarded = grouping["groups"] < 5
        assert trial["observed"]["guarded"] == guarded
        observed_guarded += guarded
        observed_groups.append(grouping["groups"])
        for obj, (pair, truth) in enumerate(zip(pairs(rows), generation["truth"])):
            q = "low_error" if obj % 10 < 5 else "high_error"
            assert truth["quality"] == q and all(rows[j]["quality"] == q for j in pair)
            assert all(rows[j]["stratum"] == (f"site_{obj // 10}", "SEAL:S") for j in pair)
            quality_truth[q]["objects"] += 1
            quality_truth[q]["agreeing_slots"] += sum(a == b for a, b in zip(rows[pair[0]]["seq"], rows[pair[1]]["seq"]))
            for face, j in zip(truth["faces"], pair):
                for changed, y, x in zip(face["replacement_indicators"], rows[j]["seq"], truth["latent_seq"]):
                    assert changed == (y != x)
                    quality_truth[q]["face_slots"] += 1
                    quality_truth[q]["replacements"] += changed
        if index in [0, 149, 299]:
            compact, _ = module.total_fit(rows, old, helper, joint)
            assert normalized(compact) == trial["observed"]
            replayed += 1
        if index == 0:
            compact, _ = module.total_fit([dict(row, quality="ignored") for row in rows], old, helper, joint)
            assert normalized(compact) == trial["observed"]
            replayed += 1
        indicator = []
        for name in ["broad_vectors", "quality_vectors"]:
            record = trial["references"][name]
            base = (60000000000 if name == "broad_vectors" else 80000000000) + index * 1000000
            assert record["seed_base"] == base and record["accepted_seeds"] == list(range(base, base + 99))
            assert not all_seeds.intersection(record["accepted_seeds"])
            all_seeds.update(record["accepted_seeds"])
            assert len(record["null"]) == 99
            for draw, score in enumerate(record["null"]):
                seed = base + draw
                assert score["proposal_seed"] == seed
                proposed = oracle_shuffle(rows, seed, name == "quality_vectors")
                assert normalized(proposed) == normalized(module.shuffle(rows, seed, name == "quality_vectors"))
                assert scalar_counts(proposed) == scalar_counts(rows) and joint_counts(proposed, False) == joint_counts(rows, False)
                assert all(all(before[key] == after[key] for key in before if key != "seq") for before, after in zip(rows, proposed))
                changed = joint_counts(proposed, True) != joint_counts(rows, True)
                assert score["quality_margin_changed"] == changed
                if name == "quality_vectors":
                    assert not changed
                changes[name] += changed
                grouping = graph.graph_oracle(proposed, old.FIT_SEED)
                assert grouping == score["grouping"] and score["guarded"] == (grouping["groups"] < 5)
                ref_groups[name].append(grouping["groups"])
                guards[name] += score["guarded"]
                assert np.isfinite(score["gain"])
                if score["guarded"]:
                    assert score["gain"] == 0 and score["chosen_models"] == [] and score["baseline_loss"] is None
                if index in [0, 149, 299] and draw in [0, 98]:
                    compact, _ = module.total_fit(proposed, old, helper, joint)
                    assert all(normalized(value) == score[key] for key, value in compact.items())
                    replayed += 1
                reference_count += 1
            values = [score["gain"] for score in record["null"]]
            gte = sum(value >= trial["observed"]["gain"] for value in values)
            assert record["exceedances"] == gte and record["p_value"] == (1 + gte) / 100
            assert record["abstained"] == guarded and record["reported_p_value"] == (1.0 if guarded else record["p_value"])
            indicator.append([int(not guarded and record["p_value"] <= alpha) for alpha in [.01, .05, .1]])
        indicators.append(indicator)
        summaries.append({"family": "shared_quality", "references": {name: {"p_value": record["reported_p_value"]} for name, record in trial["references"].items()}})
        if (index + 1) % 50 == 0:
            print(json.dumps({"stage": "quality_audit", "datasets": index + 1, "elapsed_seconds": time.monotonic() - started}), flush=True)
    assert old.aggregate(summaries) == state["aggregate"]
    assert reference_count == state["reference_corpora"] == 59400 and len(all_seeds) == 59400
    assert observed_guarded == state["observed_guarded"] and dict(guards) == state["reference_guarded"]
    indicators = np.asarray(indicators)
    differences = indicators[:, 0] - indicators[:, 1]
    rng = np.random.default_rng(2026100210)
    means = np.concatenate([differences[rng.integers(300, size=(1000, 300))].mean(axis=1) for _ in range(20)])
    intervals = np.quantile(means, [.025, .975], axis=0)
    paired = {}
    for j, alpha in enumerate([.01, .05, .1]):
        broad, quality = indicators[:, 0, j], indicators[:, 1, j]
        paired[str(alpha)] = {"both": int(np.sum((broad == 1) & (quality == 1))),
                              "broad_only": int(np.sum((broad == 1) & (quality == 0))),
                              "quality_only": int(np.sum((broad == 0) & (quality == 1))),
                              "neither": int(np.sum((broad == 0) & (quality == 0))),
                              "broad_minus_quality_rate": float(differences[:, j].mean()),
                              "paired_95_interval": intervals[:, j].tolist()}
    usable = 300 - observed_guarded
    usable_rates = {name: {str(alpha): float(indicators[:, k, j].sum() / usable) if usable else None for j, alpha in enumerate([.01, .05, .1])}
                    for k, name in enumerate(["broad_vectors", "quality_vectors"])}
    return {"status": "pass", "simulation": True, "datasets_checked": 300, "reference_tables_checked": reference_count,
            "complete_fit_replays": replayed, "distinct_reference_seeds": len(all_seeds), "observed_guarded": observed_guarded,
            "reference_guarded": dict(guards), "usable_observations": usable, "rates_given_usable_observation": usable_rates,
            "observed_group_range": [min(observed_groups), max(observed_groups)],
            "reference_group_ranges": {name: [min(values), max(values)] for name, values in ref_groups.items()},
            "quality_margin_changes": dict(changes), "quality_generation_counts": {q: dict(counts) for q, counts in quality_truth.items()},
            "paired_rejection": paired, "bootstrap_seed": 2026100210, "bootstrap_replicates": 20000,
            "input_results_sha256": sha(folder / "results.json"), "elapsed_seconds": time.monotonic() - started,
            "checks": ["hashes_and_generation", "truth_and_quality_correspondence", "independent_sampler_replay", "every_margin_and_metadata",
                       "independent_components_and_fold_loads", "total_guard_and_observed_abstention", "every_rank_p_value", "seed_uniqueness",
                       "selected_complete_fit_replays", "quality_field_ignored_by_fit", "final_aggregates", "paired_bootstrap"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["exact", "main"])
    args = parser.parse_args()
    destination = FOLDER / f"verification_{args.phase}.json"
    if destination.exists():
        raise FileExistsError("Refusing an existing shared-quality audit")
    result = exact() if args.phase == "exact" else main_study()
    result["audit_source_sha256"] = sha(__file__)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
