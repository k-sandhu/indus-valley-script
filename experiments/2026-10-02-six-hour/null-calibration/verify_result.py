"""Read-only probability, grouping and saved-score checks for calibration runs."""
from collections import Counter, defaultdict
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
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_saved_module(folder):
    spec = importlib.util.spec_from_file_location("null_calibration_snapshot", folder / "code_snapshot.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    helper, joint, hashes = module.freeze_sources()
    return module, helper, joint, hashes


def graph_oracle(rows, seed):
    links = defaultdict(list)
    for i, row in enumerate(rows):
        for alias in row["artifact_aliases"]:
            links[("artifact", alias)].append(i)
        links[("text", tuple(row["seq"]))].append(i)
    visited = set()
    groups = []
    for i in range(len(rows)):
        if i in visited:
            continue
        pending, members = [i], set()
        while pending:
            node = pending.pop()
            if node in members:
                continue
            members.add(node)
            row = rows[node]
            for key in [("artifact", alias) for alias in row["artifact_aliases"]] + [("text", tuple(row["seq"]))]:
                pending.extend(links[key])
        visited.update(members)
        groups.append(sorted(members))
    order = list(range(len(groups)))
    random.Random(seed).shuffle(order)
    order.sort(key=lambda index: sum(len(rows[i]["seq"]) for i in groups[index]), reverse=True)
    loads = [0] * 5
    for group in order:
        destination = min(range(5), key=lambda fold: (loads[fold], fold))
        loads[destination] += sum(len(rows[i]["seq"]) for i in groups[group])
    return {"groups": len(groups), "largest_group": max(map(len, groups)), "fold_loads": loads}


def exact():
    folder = HERE / "exact"
    result = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    tables = json.loads((folder / "tables_and_sampler_counts.json").read_text(encoding="utf-8"))
    module, helper, joint, hashes = load_saved_module(folder)
    assert sha(folder / "code_snapshot.py") == result["source_sha256"]
    assert hashes == result["source_snapshots"]
    # Labeled permutation multiplicities provide a separate count construction.
    multiplicities = Counter(itertools.permutations([0, 0, 0, 1, 1, 1]))
    assert len(multiplicities) == 20 and set(multiplicities.values()) == {36}
    table_weights = {}
    for columns in itertools.product(multiplicities, repeat=3):
        key = tuple(zip(*columns))
        table_weights[key] = np.prod([multiplicities[column] for column in columns]).item()
    assert len(table_weights) == 8000 and set(table_weights.values()) == {46656}
    assert sum(table_weights.values()) == result["column_label_permutations"]
    assert {tuple(tuple(row) for row in table) for table in tables["tables"]} == set(table_weights)
    unique = [len(set(table)) == 6 for table in table_weights]
    assert sum(unique) == 2880
    assert result["unique_acceptance_probability"] == 2880 / 8000
    for table, marked, statistic in zip(tables["tables"], tables["whole_string_unique"], tables["integer_statistic"]):
        assert len(set(map(tuple, table))) == 6 if marked else len(set(map(tuple, table))) < 6
        assert all(sum(row[slot] for row in table) == 3 for slot in range(3))
        assert statistic == sum(row[0] == row[1] for row in table) + sum(row[1] == row[2] for row in table)
    records = json.loads((folder / "unique_nested_scores.json").read_text(encoding="utf-8"))
    values = np.array([record["gain"] for record in records])
    ordered = np.sort(values)
    tails = (len(values) - np.searchsorted(ordered, values, side="left")) / len(values)
    observed = result["space_summaries"]["unique_nested_full_procedure"]
    assert observed["tables"] == len(records) == 2880
    for alpha in [.01, .05, .1]:
        assert observed["exact_rejection_rates"][str(alpha)] == float(np.mean(tails <= alpha))
        assert np.mean(tails <= alpha) <= alpha
    sampled = sorted(set(np.linspace(0, len(records) - 1, 20, dtype=int).tolist() + [int(np.argmin(values)), int(np.argmax(values))]))
    for index in sampled:
        record = records[index]
        table = tables["tables"][record["table_index"]]
        rows = [{"record_id": str(i), "seq": tuple(map(str, row)), "artifact": str(i), "artifact_aliases": [str(i)], "stratum": ("s", "t")} for i, row in enumerate(table)]
        replay, _ = module.fit(rows, joint)
        normalized = json.loads(json.dumps(replay))
        assert all(normalized[key] == record[key] for key in replay)
        assert graph_oracle(rows, module.FIT_SEED) == record["grouping"]
    copy_columns = list(itertools.combinations(range(4), 2))
    copy_supported = {tuple(tuple(int(i in ones) for i in range(4) for copy in range(2)) for ones in columns) for columns in itertools.product(copy_columns, repeat=3)}
    assert len(copy_supported) == 216
    assert result["copy_space"]["ordinary_reference_probability_of_preserving_all_copy_pairs"] == 216 / 343000
    counts = np.array(tables["accepted_counts"])
    mask = np.array(tables["whole_string_unique"])
    assert not counts[~mask].any() and counts.sum() == result["rejection_sampler"]["accepted"] == 100000
    expected = counts.sum() / mask.sum()
    chi_square = float(((counts[mask] - expected) ** 2 / expected).sum())
    assert chi_square == result["rejection_sampler"]["chi_square_uniformity"]
    output = {"passed": True, "ordinary_tables_checked": 8000, "unique_nested_tails_checked": 2880,
              "nested_fits_replayed": len(sampled), "copy_supported_tables": len(copy_supported),
              "checks": ["labeled_permutation_multiplicity", "all_margin_counts", "all_uniqueness_flags", "all_integer_statistics", "all_exact_nested_p_values", "nested_fit_replay", "independent_graph_and_folds", "copy_space_support", "accepted_sampler_count_support"],
              "audit_source_sha256": sha(__file__)}
    return output


def main_study(prefix=False, quick=False):
    folder = HERE / "main"
    state = json.loads((folder / ("state.json" if prefix else "results.json")).read_text(encoding="utf-8"))
    module, helper, joint, hashes = load_saved_module(folder)
    assert hashes == state["snapshot_hashes"]
    assert sha(folder / "code_snapshot.py") == state["source_sha256"]
    assert sha(HERE / "MAIN_PROTOCOL.md") == state["protocol_sha256"]
    trials = []
    checked_nulls = checked_proposals = replayed_fits = 0
    group_ranges = defaultdict(list)
    copy_pairs = []
    for family_index, family in enumerate(module.FAMILIES):
        files = sorted((folder / family).glob("dataset_*.json")) if (folder / family).exists() else []
        files = [path for path in files if "." not in path.stem]
        if prefix:
            files = files[:max(0, state["completed_datasets"] - len(trials))]
        for path in files:
            trial = json.loads(path.read_text(encoding="utf-8"))
            assert trial["complete"] and trial["family"] == family
            rows, generation = module.synthetic_rows(family, trial["generation"]["seed"], 40)
            assert generation == trial["generation"]
            assert json.loads(json.dumps(rows)) == trial["rows"]
            assert graph_oracle(rows, module.FIT_SEED) == trial["observed"]["grouping"]
            if trial["trial_index"] in [0, 499, 999]:
                observed, _ = module.fit(rows, joint)
                assert json.loads(json.dumps(observed)) == trial["observed"]
                replayed_fits += 1
            for reference_name, record in trial["references"].items():
                values = [score["gain"] for score in record["null"]]
                assert len(values) == state["reference_draws"] == record["draws"]
                assert record["accepted_seeds"] == [score["proposal_seed"] for score in record["null"]]
                assert sum(value >= trial["observed"]["gain"] for value in values) == record["exceedances"]
                assert record["p_value"] == (record["exceedances"] + 1) / (len(values) + 1)
                accepted = []
                if quick:
                    proposals = [(i, score["proposal_seed"]) for i, score in enumerate(record["null"]) if i in [0, len(values) - 1]]
                else:
                    proposals = [(None, record["seed_base"] + attempt) for attempt in range(record["proposals"])]
                null_index = 0
                for requested_index, seed in proposals:
                    if reference_name == "block_columns":
                        proposed, _ = module.block_shuffle(rows, seed, helper)
                        blocks = defaultdict(list)
                        for row in proposed:
                            blocks[row["artifact"]].append(row["seq"])
                        assert all(len(set(copies)) == 1 for copies in blocks.values())
                    else:
                        proposed, _ = helper.shuffle_positions(rows, seed, True)
                    checked_proposals += 1
                    assert module.margins(proposed) == module.margins(rows)
                    valid = reference_name != "unique_record_columns" or len({row["seq"] for row in proposed}) == len(proposed)
                    if not valid:
                        continue
                    accepted.append(seed)
                    index = requested_index if quick else null_index
                    score = record["null"][index]
                    assert score["proposal_seed"] == seed
                    assert graph_oracle(proposed, module.FIT_SEED) == score["grouping"]
                    group_ranges[(family, reference_name)].append(score["grouping"]["groups"])
                    if trial["trial_index"] in [0, 499, 999] and index in [0, len(values) - 1]:
                        fitted, _ = module.fit(proposed, joint)
                        normalized = json.loads(json.dumps(fitted))
                        assert all(normalized[key] == score[key] for key in fitted)
                        replayed_fits += 1
                    checked_nulls += 1
                    null_index += 1
                if not quick:
                    assert accepted == record["accepted_seeds"]
                    assert null_index == len(values)
            if family == "physical_copies":
                copy_pairs.append((trial["references"]["record_columns"]["p_value"], trial["references"]["block_columns"]["p_value"]))
            trials.append(trial)
    if not prefix:
        assert state["status"] == "complete" and len(trials) == 3000
        assert module.aggregate(trials) == state["aggregate"]
        assert checked_nulls == state["total_fitted_reference_corpora"] if not quick else checked_nulls == 8000
    else:
        assert len(trials) == state["completed_datasets"]
        assert module.aggregate(trials) == state["aggregate"]
    discordances = {}
    for alpha in [.01, .05, .1]:
        pair_counts = Counter((a <= alpha, b <= alpha) for a, b in copy_pairs)
        discordances[str(alpha)] = {"both_reject": pair_counts[(True, True)], "record_only": pair_counts[(True, False)], "block_only": pair_counts[(False, True)], "neither": pair_counts[(False, False)]}
    return {"passed": True, "prefix": prefix, "quick": quick, "datasets_checked": len(trials),
            "reference_corpora_groupings_checked": checked_nulls, "proposal_tables_checked": checked_proposals,
            "observed_and_reference_fits_replayed": replayed_fits,
            "null_group_count_ranges": {f"{a}/{b}": [min(values), max(values)] for (a, b), values in group_ranges.items()},
            "copy_reference_disagreements": discordances,
            "checks": ["source_and_protocol_hashes", "every_observed_dataset_generation", "independent_observed_graphs", "exceedances_and_plus_one_values", "saved_accepted_seed_alignment", "margin_preservation", "first_and_last_reference_groupings" if quick else "every_proposal_and_accepted_seed_sequence", "independent_reference_graphs_and_fold_loads", "selected_score_replays", "checkpoint_prefix_aggregate" if prefix else "final_aggregate"] + (["copy_consistency"] if copy_pairs else []),
            "audit_source_sha256": sha(__file__)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["exact", "prefix", "main"])
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    report = exact() if args.phase == "exact" else main_study(args.phase == "prefix", args.quick)
    filename = "verification_exact.json" if args.phase == "exact" else f"verification_prefix_{report['datasets_checked']:04d}.json" if args.phase == "prefix" else "verification_main.json"
    destination = HERE / filename
    if destination.exists():
        raise FileExistsError("Refusing an existing verification record")
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
