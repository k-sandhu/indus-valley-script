"""Audit slot-inventory support bounds and the preserved nested allocation domain."""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
FOLDER = PARENT / "domain-support"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def physical_blocks(rows):
    adjacency = [set() for _ in rows]
    aliases = defaultdict(list)
    for index, row in enumerate(rows):
        for alias in row["artifact_aliases"]:
            aliases[alias].append(index)
    for indices in aliases.values():
        for index in indices[1:]:
            adjacency[indices[0]].add(index)
            adjacency[index].add(indices[0])
    unseen, result = set(range(len(rows))), []
    while unseen:
        first = min(unseen)
        connected, pending = {first}, [first]
        while pending:
            for index in adjacency[pending.pop()]:
                if index not in connected:
                    connected.add(index)
                    pending.append(index)
        unseen -= connected
        result.append(sorted(connected))
    return result


def block_string_premise(rows, blocks):
    return all(len({tuple(rows[index]["seq"]) for index in indices}) == 1 for indices in blocks)


def slot_inventory(rows):
    assert all(len(row["seq"]) == 3 for row in rows)
    return [len({row["seq"][slot] for row in rows}) for slot in range(3)]


def allocation_cases(output, helper, nested):
    cases = 0
    minimum = {"outer_train_components": 10**9, "inner_train_components": 10**9,
               "outer_test_components": 10**9, "inner_test_components": 10**9,
               "outer_train_records": 10**9, "inner_train_records": 10**9,
               "outer_test_noninitial": 10**9, "inner_test_noninitial": 10**9}
    with (output / "allocation_cases.jsonl").open("w", encoding="utf-8") as handle:
        for count in range(5, 9):
            size_vectors = itertools.product(range(1, 4), repeat=count)
            if count == 5:
                size_vectors = itertools.chain(size_vectors, [(36, 1, 1, 1, 1), (1, 36, 1, 1, 1), (1, 1, 1, 1, 36)])
            for sizes in size_vectors:
                rows, groups = [], []
                for group, size in enumerate(sizes):
                    indices = []
                    for _ in range(size):
                        indices.append(len(rows))
                        rows.append({"seq": (str(group),) * 3, "analysis_group": group})
                    groups.append(indices)
                for seed in [0, 20261001, 2026100209]:
                    assignments, loads = helper.make_folds(rows, groups, 5, seed)
                    assert all(load > 0 for load in loads)
                    per_case = {name: 10**9 for name in minimum}
                    for fold in range(5):
                        train = [row for index, row in enumerate(rows) if assignments[index] != fold]
                        test = [row for index, row in enumerate(rows) if assignments[index] == fold]
                        outer = {"outer_train_components": len({r["analysis_group"] for r in train}),
                                 "outer_test_components": len({r["analysis_group"] for r in test}),
                                 "outer_train_records": len(train),
                                 "outer_test_noninitial": sum(len(r["seq"]) - 1 for r in test)}
                        assert outer["outer_train_components"] >= 4 and outer["outer_test_components"] >= 1
                        inner_groups = nested.fixed_groups(train)
                        inner, inner_loads = helper.make_folds(train, inner_groups, 3, seed + fold)
                        assert all(load > 0 for load in inner_loads)
                        for part in range(3):
                            inner_train = [row for index, row in enumerate(train) if inner[index] != part]
                            inner_test = [row for index, row in enumerate(train) if inner[index] == part]
                            values = {**outer, "inner_train_components": len({r["analysis_group"] for r in inner_train}),
                                      "inner_test_components": len({r["analysis_group"] for r in inner_test}),
                                      "inner_train_records": len(inner_train),
                                      "inner_test_noninitial": sum(len(r["seq"]) - 1 for r in inner_test)}
                            assert values["inner_train_components"] >= 2 and values["inner_test_components"] >= 1
                            assert all(value > 0 for value in values.values())
                            per_case = {name: min(per_case[name], value) for name, value in values.items()}
                    minimum = {name: min(minimum[name], value) for name, value in per_case.items()}
                    handle.write(json.dumps({"component_sizes": sizes, "seed": seed, "minimum": per_case}, separators=(",", ":")) + "\n")
                    cases += 1
    assert cases == 29169
    return {"cases": cases, "outer_split_checks": cases * 5, "inner_split_checks": cases * 15, "minimum": minimum}


def run():
    source_results = PARENT / "main/results.json"
    verification = PARENT / "verification_main.json"
    state = json.loads(source_results.read_text())
    verified = json.loads(verification.read_text())
    assert state["status"] == "complete" and verified["passed"] and not verified["quick"] and not verified["prefix"]
    output = FOLDER / "support-bound"
    if output.exists():
        raise FileExistsError("Refusing an existing support-bound audit")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    old = load(PARENT / "main/code_snapshot.py", "support_bound_original")
    helper, joint, hashes = old.freeze_sources()
    nested = load(PARENT / "sources/nested_conditional.py", "support_bound_nested")
    assert nested.GRID == [5, 20, 100, 500, 2000]
    started = time.monotonic()
    summaries, input_hashes = [], {}
    totals = defaultdict(lambda: {"datasets": 0, "references": 0, "bound": [], "sampled_groups": [],
                                  "whole_string_physical_premise_violations": 0, "support_bound_applies": True})
    for family in ["independent_records", "unique_records", "physical_copies"]:
        for index in range(1000):
            path = PARENT / f"main/{family}/dataset_{index:04d}.json"
            trial = json.loads(path.read_text())
            rows = [dict(row, seq=tuple(row["seq"]), stratum=tuple(row["stratum"])) for row in trial["rows"]]
            input_hashes[str(path.relative_to(PARENT))] = digest(path)
            blocks = physical_blocks(rows)
            premise = block_string_premise(rows, blocks)
            inventory = slot_inventory(rows)
            bound = max(inventory)
            assert premise and bound >= 5 and all(len(r["seq"]) >= 2 for r in rows)
            if family != "physical_copies":
                assert all(len(block) == 1 for block in blocks)
            else:
                assert len(blocks) == 20 and all(len(block) == 2 for block in blocks)
            distinct = len({r["seq"] for r in rows})
            assert trial["observed"]["grouping"]["groups"] == distinct >= bound
            summary = {"family": family, "trial_index": index, "slot_inventory": inventory,
                       "component_lower_bound": bound, "observed_components": distinct, "reference_cases": {}}
            for name, record in trial["references"].items():
                case = f"{family}/{name}"
                total = totals[case]
                total["datasets"] += 1
                total["bound"].append(bound)
                violations = 0
                if family == "physical_copies":
                    for score in record["null"]:
                        seed = score["proposal_seed"]
                        proposed = old.block_shuffle(rows, seed, helper)[0] if name == "block_columns" else helper.shuffle_positions(rows, seed, True)[0]
                        assert slot_inventory(proposed) == inventory
                        copied = block_string_premise(proposed, blocks)
                        if name == "block_columns":
                            assert copied
                            assert score["grouping"]["groups"] == len({r["seq"] for r in proposed}) >= bound
                        else:
                            violations += not copied
                applies = case != "physical_copies/record_columns"
                total["support_bound_applies"] = applies
                total["whole_string_physical_premise_violations"] += violations
                groups = [score["grouping"]["groups"] for score in record["null"]]
                assert all(group >= 5 for group in groups)
                assert all(all(load > 0 for load in score["grouping"]["fold_loads"]) for score in record["null"])
                if applies:
                    assert min(groups) >= bound
                if family == "unique_records":
                    assert set(groups) == {40}
                total["sampled_groups"].extend(groups)
                total["references"] += len(groups)
                summary["reference_cases"][name] = {"support_bound_applies": applies, "sampled_group_range": [min(groups), max(groups)],
                                                    "whole_string_physical_premise_violations": violations}
            summaries.append(summary)
        print(json.dumps({"stage": "support_bound", "family": family, "datasets_checked": len(summaries), "elapsed_seconds": time.monotonic() - started}), flush=True)
    output_cases = {name: {**{key: value for key, value in record.items() if key not in ["bound", "sampled_groups"]},
                           "component_bound_range": [min(record["bound"]), max(record["bound"])],
                           "sampled_group_range": [min(record["sampled_groups"]), max(record["sampled_groups"])]}
                    for name, record in totals.items()}
    allocation = allocation_cases(output, helper, nested)
    witness = json.loads((FOLDER / "main-v2/results.json").read_text())
    witness_bound = max(slot_inventory(witness["connected_rows"]))
    assert witness_bound == 8 and witness["connected_components"] == 1
    (output / "trials.json").write_text(json.dumps(summaries, separators=(",", ":")) + "\n", encoding="utf-8")
    (output / "input_hashes.json").write_text(json.dumps(input_hashes, indent=2) + "\n", encoding="utf-8")
    result = {"status": "passed", "simulation": True, "datasets": 3000, "reference_groupings": 396000,
              "regenerated_copy_reference_tables": 198000, "reference_cases": output_cases, "allocation": allocation,
              "nonidentical_witness_inventory_bound_without_premise": witness_bound,
              "nonidentical_witness_actual_components": 1, "scores_refitted": 0,
              "source_sha256": digest(__file__), "protocol_sha256": digest(FOLDER / "SUPPORT_PROTOCOL.md"),
              "allocation_amendment_sha256": digest(FOLDER / "SUPPORT_ALLOCATION_AMENDMENT.md"),
              "input_main_sha256": digest(source_results), "input_verification_sha256": digest(verification),
              "preserved_method_hashes": hashes, "input_hashes_sha256": digest(output / "input_hashes.json"),
              "allocation_cases_sha256": digest(output / "allocation_cases.jsonl"), "elapsed_seconds": time.monotonic() - started}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    run()
