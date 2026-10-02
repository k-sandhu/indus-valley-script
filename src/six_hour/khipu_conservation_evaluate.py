"""Score sealed collective fits, relative rays and observed absolute scales."""
from __future__ import annotations
import collections
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
from khipu_conservation import BASE, ENDPOINT, CONDITIONS, digest, save

POLICIES = ("baseline_three_quarter", "collective_three_quarter", "baseline_half", "collective_half")


def dot(row, vector):
    return sum(Fraction(a)*b for a, b in zip(row, vector))


def true_in_best(inferred, normalized_truth):
    if inferred["status"] == "no_positive_solution":
        return False
    if "aggregate" in inferred:
        residual = dot(inferred["aggregate"], normalized_truth)
        if inferred["kind"] == "equality" and residual != 0 or inferred["kind"] == "inequality" and residual < 0:
            return False
    if any(list(map(Fraction, p["values"])) == normalized_truth for p in inferred["optimal_points"]):
        return True
    for family in inferred["optimal_families"]:
        if "line" not in family or dot(family["line"], normalized_truth) == 0:
            return True
    return False


def count_ray_check(vector, features, measured):
    possible = None
    for mark, quantity in zip(features, measured):
        prediction = dot(mark, vector)
        if prediction == 0:
            if quantity != 0:
                return {"compatible": False, "scale_witness": None}
            continue
        candidate = Fraction(quantity)/prediction
        if candidate <= 0 or possible is not None and candidate != possible:
            return {"compatible": False, "scale_witness": None}
        possible = candidate
    return {"compatible": True, "scale_witness": "arbitrary_positive" if possible is None else str(possible)}


def score(decision, key, counted_observation):
    output = {"status": decision["status"], "normalized_values": decision["normalized_values"],
              "correct_relative": False, "wrong_relative": False, "correct_absolute_counted": False,
              "wrong_absolute_counted": False, "absolute_identified_unmeasured": False}
    if decision["status"] != "accepted_unique_ray":
        return output
    vector = list(map(Fraction, decision["normalized_values"]))
    truth = [Fraction(x, key["true_weights"][0]) for x in key["true_weights"]]
    correct = vector == truth
    measured_scale = counted_observation["count"]
    absolute = [measured_scale*x for x in vector]
    relation = [dot(row, vector) for row in key["heldout_equations"]]
    counted_errors = [dot(mark, absolute)-q for mark, q in zip(key["count_features"], key["count_values"])]
    ray_counts = count_ray_check(vector, key["count_features"], key["count_values"])
    return output | {"correct_relative": correct, "wrong_relative": not correct,
              "correct_absolute_counted": absolute == key["true_weights"], "wrong_absolute_counted": absolute != key["true_weights"],
              "absolute_values_counted": list(map(str, absolute)), "counted_scale": measured_scale,
              "unmeasured_scale_witnesses": [list(map(str, vector)), list(map(str, [2*x for x in vector]))],
              "unmeasured_scale_family": "all positive multiples of the normalized vector",
              "heldout_normalized_relation_residuals": list(map(str, relation)),
              "heldout_counted_residuals": list(map(str, counted_errors)),
              "passes_all_heldout_relations": not any(relation), "passes_all_counted_targets": not any(counted_errors),
              "unmeasured_ray_count_check": ray_counts}


def main():
    manifest = json.loads((ENDPOINT/"inference-manifest.json").read_text(encoding="utf-8"))
    assert digest(ENDPOINT/"inferences.jsonl") == manifest["inferences_sha256"]
    keys = {}
    with (ENDPOINT/"evaluator-key.jsonl").open(encoding="utf-8") as f:
        for line in f:
            x = json.loads(line); keys[x["id"]] = x["key"]
    destination = ENDPOINT/"evaluated-prefixes.jsonl"
    if destination.exists():
        raise FileExistsError(destination)
    buckets = collections.defaultdict(collections.Counter)
    optimal = collections.defaultdict(collections.Counter)
    histories = collections.defaultdict(list)
    examples = collections.defaultdict(list)
    with (ENDPOINT/"inferences.jsonl").open(encoding="utf-8") as f, destination.open("w", encoding="utf-8") as out:
        for line in f:
            inferred = json.loads(line)
            world_id, prefix = inferred["world_id"], inferred["prefix"]
            condition = world_id.split("-", 1)[1]
            key = keys[world_id]
            truth = [Fraction(x, key["true_weights"][0]) for x in key["true_weights"]]
            record = {"world_id": world_id, "prefix": prefix, "policies": {}, "models": {},
                      "actual_collective_residual": key["actual_collective_residual"], "scale": key["scale"]}
            for model in ("baseline", "collective"):
                fitted = inferred[model]
                retained = true_in_best(fitted, truth)
                unique = fitted["status"] == "unique_positive"
                correct = unique and list(map(Fraction, fitted["optimal_points"][0]["values"])) == truth
                record["models"][model] = {"status": fitted["status"], "best_support": fitted["best_support"], "truth_retained": retained,
                                           "unique_correct": correct, "unique_wrong": unique and not correct}
                ob = optimal[(condition, model, prefix)]
                ob["records"] += 1; ob["truth_retained"] += retained
                ob["unique_correct"] += correct; ob["unique_wrong"] += unique and not correct
                ob["ambiguous"] += fitted["status"] == "ambiguous_positive"
                ob["infeasible"] += fitted["status"] == "no_positive_solution"
                ob["with_family"] += bool(fitted["optimal_families"])
                ob["with_discrete_tie"] += len(fitted["optimal_points"]) > 1
            for policy in POLICIES:
                output = score(inferred["policies"][policy], key, inferred["scale_observations"]["counted"])
                record["policies"][policy] = output
                bucket = buckets[(condition, policy, prefix)]
                bucket["records"] += 1; bucket[output["status"]] += 1
                for name in ("correct_relative", "wrong_relative", "correct_absolute_counted", "wrong_absolute_counted", "absolute_identified_unmeasured"):
                    bucket[name] += output[name]
                if output["status"] == "accepted_unique_ray":
                    bucket["passes_all_relations"] += output["passes_all_heldout_relations"]
                    bucket["passes_all_counted_targets"] += output["passes_all_counted_targets"]
                    bucket["unmeasured_ray_compatible_with_counts"] += output["unmeasured_ray_count_check"]["compatible"]
                    if output["wrong_relative"]:
                        bucket["wrong_passes_relations"] += output["passes_all_heldout_relations"]
                        bucket["wrong_passes_counted_targets"] += output["passes_all_counted_targets"]
                        bucket["wrong_ray_compatible_with_counts"] += output["unmeasured_ray_count_check"]["compatible"]
                histories[(world_id, policy)].append({"prefix": prefix, **output})
                if prefix == 8 and output["wrong_relative"] and len(examples[(condition, policy)]) < 2:
                    examples[(condition, policy)].append({"inferred": inferred, "evaluated": record.copy()})
            out.write(json.dumps(record, separators=(",", ":"))+"\n")
    totals = collections.defaultdict(collections.Counter)
    first_correct, first_wrong = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for (world_id, policy), sequence in histories.items():
        condition = world_id.split("-", 1)[1]
        counter = totals[(condition, policy)]
        wrong = [x for x in sequence if x["wrong_relative"]]
        correct = [x for x in sequence if x["correct_relative"]]
        counter["worlds"] += 1; counter["ever_wrong"] += bool(wrong); counter["ever_correct"] += bool(correct)
        if wrong:
            first_wrong[(condition, policy)][str(wrong[0]["prefix"])] += 1
            final = sequence[-1]
            counter["wrong_then_correct"] += final["correct_relative"]
            counter["wrong_then_wrong"] += final["wrong_relative"]
            counter["wrong_then_ambiguous"] += final["status"] == "abstained_ambiguity"
            counter["wrong_then_rejected"] += final["status"].startswith("rejected")
        if correct:
            first_correct[(condition, policy)][str(correct[0]["prefix"])] += 1
    operation_counts = collections.defaultdict(collections.Counter)
    scale_counts = collections.Counter()
    for world_id, key in keys.items():
        condition = world_id.split("-", 1)[1]
        operation_counts[condition]["zero_collective_residual"] += key["actual_collective_residual"] == 0
        operation_counts[condition]["negative_collective_residual"] += key["actual_collective_residual"] < 0
        operation_counts[condition]["positive_collective_residual"] += key["actual_collective_residual"] > 0
        operation_counts[condition]["actual_incomplete_pools"] += not key["actual_pool_complete"]
        if condition == "complete": scale_counts[str(key["scale"])] += 1
    aggregate = {"created_utc": datetime.now(timezone.utc).isoformat(), "scope": "Fresh simulated collective observation; relative and counted-scale results separated",
                 "worlds": len(keys), "base_seeds": 200, "prefix_records": manifest["prefix_records"], "policy_decisions": manifest["prefix_records"]*4,
                 "scale_views": ["unmeasured", "counted"], "unmeasured_absolute_identifications": 0,
                 "rows": [{"condition": c, "policy": p, "prefix": n, **dict(buckets[(c, p, n)])} for c in CONDITIONS for p in POLICIES for n in range(1, 9)],
                 "optimal_sets": [{"condition": c, "model": m, "prefix": n, **dict(optimal[(c, m, n)])} for c in CONDITIONS for m in ("baseline", "collective") for n in range(1, 9)],
                 "trajectories": [{"condition": c, "policy": p, **dict(totals[(c, p)]), "first_correct_prefixes": dict(first_correct[(c, p)]),
                                   "first_wrong_prefixes": dict(first_wrong[(c, p)])} for c in CONDITIONS for p in POLICIES],
                 "collective_residual_distributions": {c: dict(operation_counts[c]) for c in CONDITIONS}, "scale_distribution": dict(scale_counts),
                 "input_hashes": {name: digest(ENDPOINT/name) for name in ("component-inputs.jsonl", "evaluator-key.jsonl", "inferences.jsonl", "evaluated-prefixes.jsonl")},
                 "code_sha256": digest(Path(__file__))}
    save(ENDPOINT/"aggregate.json", aggregate)
    save(ENDPOINT/"wrong-case-examples.json", {"selection": "First two final wrong rays per condition/policy in generator order",
                                               "cases": [{"condition": c, "policy": p, "records": v} for (c, p), v in examples.items()]})
    print(json.dumps({"worlds": len(keys), "prefix_records": manifest["prefix_records"], "evaluated_bytes": destination.stat().st_size}))
    for row in aggregate["rows"]:
        if row["prefix"] == 8:
            print(json.dumps(row))


if __name__ == "__main__":
    main()
