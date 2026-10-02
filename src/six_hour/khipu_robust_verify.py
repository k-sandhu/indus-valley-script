"""Independent subset/RREF check of exact arrangement inferences and scores."""
from __future__ import annotations
import ast
import collections
from datetime import datetime, timezone
from fractions import Fraction
import itertools
import json
from math import gcd, lcm
from pathlib import Path

from khipu_control import exact_decoder
from khipu_robust import ENDPOINT, BASE, digest, save


def direct_sum(row, vector):
    answer = Fraction(0)
    for j in range(3):
        answer += Fraction(row[j])*Fraction(vector[j])
    return answer


def normalized_rational_line(row):
    common = lcm(*(x.denominator for x in row))
    integer = [int(x*common) for x in row]
    divisor = gcd(gcd(abs(integer[0]), abs(integer[1])), abs(integer[2]))
    integer = [x//divisor for x in integer]
    if next(x for x in integer if x) < 0:
        integer = [-x for x in integer]
    return tuple(integer)


def rref_family_line(classified):
    for saved in classified["rref"]:
        row = list(map(Fraction, saved))
        if row[0] == 0 and (row[1] or row[2]):
            return normalized_rational_line([-row[3], row[1], row[2]])
    raise AssertionError(classified)


def subsets(rows):
    classified = []
    witness_count = 0
    for mask in range(1 << len(rows)):
        subset = [row for i, row in enumerate(rows) if mask & (1 << i)]
        fit = exact_decoder(subset, [1, 0, 0])
        for witness in fit["witnesses"]:
            values = list(map(Fraction, witness))
            assert values[0] == 1 and all(x > 0 for x in values)
            assert all(direct_sum(row, values) == 0 for row in subset)
            witness_count += 1
        classified.append(fit)
    return classified, witness_count


def verify_consensus(rows, saved, classified):
    possible = [(mask.bit_count(), mask, fit) for mask, fit in enumerate(classified[:1 << len(rows)]) if fit["status"] != "no_positive_solution"]
    maximum = max(size for size, _, _ in possible)
    best = [(mask, fit) for size, mask, fit in possible if size == maximum]
    assert saved["best_support"] == maximum
    points, lines, plane = set(), set(), False
    for mask, fit in best:
        if fit["status"] == "unique_positive":
            points.add(tuple(map(Fraction, fit["witnesses"][0])))
        elif fit["rank_anchored"] == 1:
            plane = True
        elif fit["rank_anchored"] == 2:
            lines.add(rref_family_line(fit))
        else:
            raise AssertionError(fit)
    assert points == {tuple(map(Fraction, p["values"])) for p in saved["optimal_points"]}
    actual_lines = {tuple(f["line"]) for f in saved["optimal_families"] if "line" in f}
    actual_plane = any(f.get("family") == "positive_plane" for f in saved["optimal_families"])
    assert lines == actual_lines and plane == actual_plane
    expected_unique = len(points) == 1 and not lines and not plane
    assert saved["status"] == ("unique_positive" if expected_unique else "ambiguous_positive")
    witnesses = 0
    for point in saved["point_candidates"]:
        vector = list(map(Fraction, point["values"]))
        assert vector[0] == 1 and all(x > 0 for x in vector)
        matched = [i for i, row in enumerate(rows) if direct_sum(row, vector) == 0]
        assert matched == point["support_indices"] and len(matched) == point["support"]
        witnesses += 1
    for family in saved["optimal_families"]:
        assert len(family["witnesses"]) == 2 and family["witnesses"][0] != family["witnesses"][1]
        for vector in family["witnesses"]:
            assert all(Fraction(x) > 0 for x in vector) and Fraction(vector[0]) == 1
            assert sum(direct_sum(row, vector) == 0 for row in rows) == maximum
            if "line" in family:
                assert direct_sum(family["line"], vector) == 0
            witnesses += 1
    return witnesses, len(best)


def projection_check(world, key):
    component = world["component"]
    features, groups = component["features"], component["memberships"]
    quantities = key["training_quantities"]
    assert component["anchor"] == [1, 0, 0] and component["anchor_value"] == 1
    assert "true_weights" not in component and len(features) == len(quantities) == 32
    assert all(direct_sum(f, [1, 10, 100]) == q for f, q in zip(features, quantities))
    restored = [[8+3*i+j for j in range(3)] for i in range(8)]
    for operation in key["corruption_operations"]:
        if "parents" in operation:
            p, q = operation["parents"]
            first, second = operation["children"]
            pi, qi = restored[p].index(first), restored[q].index(second)
            restored[p][pi], restored[q][qi] = second, first
        else:
            restored[operation["parent"]].remove(operation["removed_child"])
    assert groups == restored
    rows = []
    for parent, children in enumerate(groups):
        row = list(features[parent])
        for child in children:
            for j in range(3):
                row[j] -= features[child][j]
        rows.append(row)
    assert rows == component["equations"]
    assert key["actual_violations"] == [i for i, row in enumerate(rows) if direct_sum(row, [1, 10, 100]) != 0]
    for f, q in zip(key["heldout_features"], key["heldout_quantities"]):
        assert direct_sum(f, [1, 10, 100]) == q
    for f, q in zip(key["count_features"], key["count_values"]):
        assert direct_sum(f, [1, 10, 100]) == q
    expected = []
    for parent, children in enumerate(key["heldout_memberships"]):
        row = list(key["heldout_features"][parent])
        for child in children:
            for j in range(3):
                row[j] -= key["heldout_features"][child][j]
        expected.append(row)
    assert expected == key["heldout_equations"]
    if world["condition"] != "ownership":
        assert all(direct_sum(row, [1, 10, 100]) == 0 for row in expected)
        for parent in range(8):
            assert quantities[parent] == sum(quantities[8+3*parent+j] for j in range(3))
    return rows


def evaluate_check(inference, evaluated, key):
    truth = key["true_weights"]
    rows = inference["equations"]
    assert evaluated["true_support"] == sum(direct_sum(row, truth) == 0 for row in rows)
    retained = any(list(map(Fraction, p["values"])) == truth for p in inference["consensus"]["optimal_points"])
    retained |= any(f.get("family") == "positive_plane" or direct_sum(f["line"], truth) == 0 for f in inference["consensus"]["optimal_families"])
    assert evaluated["true_vector_in_best_set"] == retained
    checked = 0
    for method in ("all_relations", "three_quarter", "half"):
        output = evaluated["methods"][method]
        if method == "all_relations":
            fit = inference[method]
            expected = "accepted_unique" if fit["status"] == "unique_positive" else "abstained_ambiguity" if fit["status"] == "ambiguous_positive" else "rejected_infeasible"
        else:
            n = inference["prefix"]
            threshold = (3*n+3)//4 if method == "three_quarter" else (n+1)//2
            assert inference[method]["threshold"] == threshold
            expected = "rejected_support" if inference["consensus"]["best_support"] < threshold else "abstained_ambiguity" if inference["consensus"]["status"] == "ambiguous_positive" else "accepted_unique"
        assert output["status"] == expected
        if expected != "accepted_unique":
            assert output["values"] is None and not output["accepted_correct"] and not output["accepted_wrong"]
            continue
        vector = list(map(Fraction, output["values"]))
        correct = vector == truth
        assert output["accepted_correct"] == correct and output["accepted_wrong"] == (not correct)
        relation = [direct_sum(row, vector) for row in key["heldout_equations"]]
        counts = [direct_sum(f, vector)-q for f, q in zip(key["count_features"], key["count_values"])]
        quantities = [direct_sum(f, vector)-q for f, q in zip(key["heldout_features"], key["heldout_quantities"])]
        for values, field, passed in [(relation, "heldout_relation_residuals", "passes_all_heldout_relations"),
                                      (counts, "heldout_count_residuals", "passes_all_heldout_counts"),
                                      (quantities, "heldout_quantity_residuals", "passes_all_heldout_quantities")]:
            assert list(map(Fraction, output[field])) == values and output[passed] == (not any(values))
            checked += len(values)
        excluded = [i for i, row in enumerate(key["training_equations"]) if direct_sum(row, vector) != 0]
        assert output["excluded_training_rows"] == excluded
        assert output["excluded_rows_match_actual_violations"] == (excluded == key["actual_violations"])
    return checked


def static_check():
    tree = ast.parse((ENDPOINT/"khipu_robust.py").read_text(encoding="utf-8"))
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for name in ("maximum_consensus", "line_family", "canonical", "support", "consensus_decision"):
        node = functions[name]
        for part in ast.walk(node):
            if isinstance(part, ast.Attribute):
                assert part.attr not in {"read_text", "read_bytes", "open", "write_text", "write_bytes"}
            if isinstance(part, ast.Name):
                assert part.id not in {"key", "true_weights", "ENDPOINT", "ROOT", "BASE", "CONDITIONS", "condition", "seed"}
    assert [a.arg for a in functions["maximum_consensus"].args.args] == ["rows"]
    return True


def main():
    generation = json.loads((ENDPOINT/"generation-manifest.json").read_text(encoding="utf-8"))
    for record in generation["files"]:
        assert digest(ENDPOINT/record["path"]) == record["sha256"]
    im = json.loads((ENDPOINT/"inference-manifest.json").read_text(encoding="utf-8"))
    assert digest(ENDPOINT/"inferences.jsonl") == im["inference_sha256"]
    worlds, keys = {}, {}
    for file, dest, field in [("component-inputs.jsonl", worlds, None), ("evaluator-key.jsonl", keys, "key")]:
        with (ENDPOINT/file).open(encoding="utf-8") as f:
            for line in f:
                value = json.loads(line)
                dest[value["id"]] = value if field is None else value[field]
    assert worlds.keys() == keys.keys() and len(worlds) == generation["worlds"]
    rows_by_world = {}
    for world_id, world in worlds.items():
        rows_by_world[world_id] = projection_check(world, keys[world_id])
        keys[world_id]["training_equations"] = rows_by_world[world_id]
    current, cached = None, None
    subset_states = subset_witnesses = arrangement_witnesses = inference_count = residuals = 0
    best_subsets = 0
    counter = collections.Counter()
    with (ENDPOINT/"inferences.jsonl").open(encoding="utf-8") as inf, (ENDPOINT/"evaluated-prefixes.jsonl").open(encoding="utf-8") as evf:
        for iline, eline in itertools.zip_longest(inf, evf):
            assert iline is not None and eline is not None
            inference, evaluated = json.loads(iline), json.loads(eline)
            world_id, prefix = inference["world_id"], inference["prefix"]
            assert evaluated["world_id"] == world_id and evaluated["prefix"] == prefix
            if world_id != current:
                current = world_id
                cached, count = subsets(rows_by_world[world_id])
                subset_states += len(cached)
                subset_witnesses += count
                if subset_states % (256*100) == 0:
                    print(f"Subset verification: {subset_states//256}/{len(worlds)} worlds.", flush=True)
            assert inference["equations"] == rows_by_world[world_id][:prefix]
            count, optimal_count = verify_consensus(inference["equations"], inference["consensus"], cached)
            arrangement_witnesses += count
            best_subsets += optimal_count
            strict = cached[(1 << prefix)-1]
            assert strict == inference["all_relations"]
            residuals += evaluate_check(inference, evaluated, keys[world_id])
            inference_count += 1
            counter[inference["consensus"]["status"]] += 1
    diagnostics = json.loads((ENDPOINT/"diagnostics.json").read_text(encoding="utf-8"))
    for name, record in diagnostics.items():
        classified, witnesses = subsets(record["equations"])
        verify_consensus(record["equations"], record["consensus"], classified)
        subset_states += len(classified)
        subset_witnesses += witnesses
    assert diagnostics["plane"]["consensus"]["optimal_families"][0]["family"] == "positive_plane"
    assert len(diagnostics["line"]["consensus"]["optimal_families"]) == 1
    assert len(diagnostics["competing_points"]["consensus"]["optimal_points"]) == 5
    assert diagnostics["competing_points"]["consensus"]["best_support"] == 4
    acquisition = json.loads((BASE/"source-acquisition.json").read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    for asset in acquisition["assets"]:
        assert digest(root/asset["local_path"]) == asset["sha256"]
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "passed": True, "worlds_checked": len(worlds),
              "inference_records_checked": inference_count, "subset_feasibility_states_checked": subset_states,
              "subset_positive_witnesses_checked": subset_witnesses, "arrangement_positive_witnesses_checked": arrangement_witnesses,
              "optimal_subsets_checked": best_subsets, "heldout_residuals_checked": residuals, "consensus_status_counts": dict(counter),
              "subset_method": "All 256 subsets per world, independently classified by rational row reduction and strict positivity",
              "projection_and_corruption_reconstruction": True, "source_hashes_checked": len(acquisition["assets"]),
              "constructed_plane_line_and_discrete_ties": True, "tested_functions_have_no_key_or_file_access": static_check(),
              "inference_sha256": digest(ENDPOINT/"inferences.jsonl"), "evaluated_sha256": digest(ENDPOINT/"evaluated-prefixes.jsonl"),
              "code_sha256": digest(Path(__file__))}
    save(ENDPOINT/"verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
