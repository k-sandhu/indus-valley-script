"""Independent support, graph, rank and score-replay checks for finite guards."""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def graph_components(rows):
    unseen, components = set(range(len(rows))), []
    while unseen:
        origin = min(unseen)
        pending, seen = [origin], {origin}
        while pending:
            a = pending.pop()
            for b in unseen:
                same_word = tuple(rows[a]["seq"]) == tuple(rows[b]["seq"])
                shared_alias = set(rows[a]["artifact_aliases"]) & set(rows[b]["artifact_aliases"])
                if b not in seen and (same_word or shared_alias):
                    seen.add(b)
                    pending.append(b)
        unseen -= seen
        components.append(sorted(seen))
    return components


def tails(scores):
    frequencies = Counter(scores)
    suffix, result = 0, {}
    for value in sorted(frequencies, reverse=True):
        suffix += frequencies[value]
        result[value] = suffix
    return result


def run():
    endpoint = HERE / "verification.json"
    if endpoint.exists():
        raise FileExistsError("Refusing an existing guard verification")
    witness = json.loads((HERE / "main-v2/results.json").read_text())
    faces = load(PARENT / "noisy-faces/verify.py", "face_witness_oracle")
    a, b = witness["connected_rows"], witness["feasible_rows"]
    assert len(graph_components(a)) == 1 and len(graph_components(b)) == 20
    assert faces.joint_counts(a) == faces.joint_counts(b)
    replay = faces.oracle_shuffle(a, witness["search_attempts"][-1]["seed"])
    assert json.loads(json.dumps(replay)) == b
    old = load(PARENT / "main/code_snapshot.py", "guard_check_original")
    helper, joint, _ = old.freeze_sources()
    try:
        old.fit([dict(row, seq=tuple(row["seq"]), stratum=tuple(row["stratum"])) for row in a], joint)
    except Exception as error:
        assert {"exception": type(error).__name__, "message": str(error)} == witness["connected_fit_failure"]
    else:
        raise AssertionError("The saved support failure did not replay")
    finite = HERE / "guard-exact"
    result = json.loads((finite / "results.json").read_text())
    assert result["status"] == "complete" and result["source_sha256"] == digest(finite / "code_snapshot.py")
    records = json.loads((finite / "scores_and_tails.json").read_text())
    tables = json.loads((PARENT / "exact/tables_and_sampler_counts.json").read_text())["tables"]
    columns = [tuple(1 if index in chosen else 0 for index in range(6)) for chosen in itertools.combinations(range(6), 3)]
    table_set = {tuple(tuple(row) for row in zip(*cols)) for cols in itertools.product(columns, repeat=3)}
    assert table_set == {tuple(tuple(row) for row in table) for table in tables}
    assert len(table_set) == len(tables) == len(records) == 8000
    full_tails = tails([record["gain"] for record in records])
    feasible_records = [record for record in records if record["components"] >= 5]
    feasible_tails = tails([record["gain"] for record in feasible_records])
    replays = 0
    origins = defaultdict(list)
    for index, (table, record) in enumerate(zip(tables, records)):
        rows = [{"record_id": str(i), "seq": tuple(map(str, row)), "artifact": str(i), "artifact_aliases": [str(i)], "stratum": ("s", "t")} for i, row in enumerate(table)]
        assert record["table_index"] == index and record["components"] == len(graph_components(rows))
        assert record["full_exceedances"] == full_tails[record["gain"]]
        assert record["full_tail"] == record["full_exceedances"] / 8000
        if record["components"] < 5:
            assert record["gain"] == 0 and record["observed_action"] == "abstain" and record["feasible_tail"] is None
        else:
            assert record["observed_action"] == "test"
            assert record["feasible_exceedances"] == feasible_tails[record["gain"]]
            assert record["feasible_tail"] == record["feasible_exceedances"] / 5760
        origins[record["origin"]].append(index)
    assert len(origins["declared_guard"]) == 2240 and len(feasible_records) == 5760
    for origin in ["frozen_unique_score", "new_five_component_fit"]:
        indices = origins[origin]
        for index in [indices[0], indices[len(indices) // 2], indices[-1]]:
            rows = [{"record_id": str(i), "seq": tuple(map(str, row)), "artifact": str(i), "artifact_aliases": [str(i)], "stratum": ("s", "t")} for i, row in enumerate(tables[index])]
            score, _ = old.fit(rows, joint)
            expected = {key: value for key, value in records[index]["score"].items() if key != "table_index"}
            assert json.loads(json.dumps(score)) == expected
            replays += 1
    for alpha, endpoints in result["endpoints"].items():
        threshold = float(alpha)
        full_reject = sum(record["components"] >= 5 and record["full_tail"] <= threshold for record in records)
        conditional_reject = sum(record["feasible_tail"] <= threshold for record in feasible_records)
        for name, count, denominator in [
            ("extended_law_full_population", full_reject, 8000),
            ("extended_law_given_feasible_observation", full_reject, 5760),
            ("feasibility_conditioned_law", conditional_reject, 5760),
            ("conditioned_law_full_population_with_abstention", conditional_reject, 8000)]:
            assert endpoints[name] == {"rejections": count, "denominator": denominator, "rate": count / denominator}
        assert full_reject / 8000 <= threshold and conditional_reject / 5760 <= threshold
    report = {"status": "passed", "witness_graphs": 2, "witness_sampler_replay": 1, "witness_failure_replay": 1,
              "enumerated_table_identities": 8000, "independent_graph_counts": 8000, "full_tail_checks": 8000,
              "conditional_tail_checks": 5760, "score_replays": replays, "endpoint_checks": 12,
              "input_results_sha256": digest(finite / "results.json"), "witness_sha256": digest(HERE / "main-v2/results.json"),
              "verification_source_sha256": digest(__file__)}
    endpoint.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    run()
