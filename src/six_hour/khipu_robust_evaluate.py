"""Evaluate sealed consensus inferences against separately saved generated truth."""
from __future__ import annotations
import collections
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
from khipu_robust import ENDPOINT, CONDITIONS, digest, save

METHODS = ("all_relations", "three_quarter", "half")


def dot(row, values):
    return sum(Fraction(a)*b for a, b in zip(row, values))


def truth_in_consensus(result, truth):
    if any(list(map(Fraction, p["values"])) == truth for p in result["optimal_points"]):
        return True
    for family in result["optimal_families"]:
        if family.get("family") == "positive_plane" or dot(family["line"], truth) == 0:
            return True
    return False


def evaluate_decision(decision, key):
    values = None if decision["values"] is None else list(map(Fraction, decision["values"]))
    accepted = decision["status"] == "accepted_unique"
    answer = {"status": decision["status"], "values": decision["values"], "accepted_correct": False, "accepted_wrong": False}
    if not accepted:
        return answer
    assert values is not None and all(x > 0 for x in values)
    correct = values == key["true_weights"]
    relation_errors = [dot(row, values) for row in key["heldout_equations"]]
    count_errors = [dot(features, values)-q for features, q in zip(key["count_features"], key["count_values"])]
    quantity_errors = [dot(features, values)-q for features, q in zip(key["heldout_features"], key["heldout_quantities"])]
    excluded = [i for i, row in enumerate(key["training_equations"]) if dot(row, values) != 0]
    actual = key["actual_violations"]
    return answer | {"accepted_correct": correct, "accepted_wrong": not correct,
            "heldout_relation_residuals": list(map(str, relation_errors)), "heldout_count_residuals": list(map(str, count_errors)),
            "heldout_quantity_residuals": list(map(str, quantity_errors)),
            "passes_all_heldout_relations": not any(relation_errors), "passes_all_heldout_counts": not any(count_errors),
            "passes_all_heldout_quantities": not any(quantity_errors), "excluded_training_rows": excluded,
            "excluded_rows_match_actual_violations": excluded == actual,
            "excluded_true_positives": len(set(excluded) & set(actual)), "excluded_false_positives": len(set(excluded)-set(actual))}


def strict_decision(inferred):
    status = inferred["status"]
    return {"status": "accepted_unique" if status == "unique_positive" else
            "abstained_ambiguity" if status == "ambiguous_positive" else "rejected_infeasible",
            "values": inferred["witnesses"][0] if status == "unique_positive" else None}


def main():
    manifest = json.loads((ENDPOINT/"inference-manifest.json").read_text(encoding="utf-8"))
    assert digest(ENDPOINT/"inferences.jsonl") == manifest["inference_sha256"]
    keys = {}
    with (ENDPOINT/"evaluator-key.jsonl").open(encoding="utf-8") as f:
        for line in f:
            world = json.loads(line)
            keys[world["id"]] = world["key"]
    with (ENDPOINT/"component-inputs.jsonl").open(encoding="utf-8") as f:
        for line in f:
            world = json.loads(line)
            keys[world["id"]]["training_equations"] = world["component"]["equations"]
    destination = ENDPOINT/"evaluated-prefixes.jsonl"
    if destination.exists():
        raise FileExistsError(destination)
    buckets = collections.defaultdict(collections.Counter)
    trajectories = collections.defaultdict(list)
    optimal = collections.defaultdict(collections.Counter)
    examples = collections.defaultdict(list)
    with (ENDPOINT/"inferences.jsonl").open(encoding="utf-8") as f, destination.open("w", encoding="utf-8") as out:
        for line in f:
            record = json.loads(line)
            world_id, prefix = record["world_id"], record["prefix"]
            condition = world_id.split("-", 1)[1]
            key = keys[world_id]
            truth = key["true_weights"]
            retained = truth_in_consensus(record["consensus"], truth)
            best_status = record["consensus"]["status"]
            raw_unique_correct = best_status == "unique_positive" and list(map(Fraction, record["consensus"]["optimal_points"][0]["values"])) == truth
            output = {"world_id": world_id, "prefix": prefix, "true_support": sum(dot(row, truth) == 0 for row in record["equations"]),
                      "best_support": record["consensus"]["best_support"], "true_vector_in_best_set": retained,
                      "consensus_status": best_status, "raw_unique_correct": raw_unique_correct,
                      "raw_unique_wrong": best_status == "unique_positive" and not raw_unique_correct, "methods": {}}
            ob = optimal[(condition, prefix)]
            ob["records"] += 1
            ob["truth_retained"] += retained
            ob["unique_correct"] += raw_unique_correct
            ob["unique_wrong"] += output["raw_unique_wrong"]
            ob["ambiguous"] += best_status == "ambiguous_positive"
            ob["with_optimal_family"] += bool(record["consensus"]["optimal_families"])
            ob["with_multiple_optimal_points"] += len(record["consensus"]["optimal_points"]) > 1
            for method in METHODS:
                decision = strict_decision(record["all_relations"]) if method == "all_relations" else record[method]
                evaluated = evaluate_decision(decision, key)
                output["methods"][method] = evaluated
                bucket = buckets[(condition, method, prefix)]
                bucket["records"] += 1
                bucket[evaluated["status"]] += 1
                bucket["accepted_correct"] += evaluated["accepted_correct"]
                bucket["accepted_wrong"] += evaluated["accepted_wrong"]
                if evaluated["status"] == "accepted_unique":
                    for name in ("passes_all_heldout_relations", "passes_all_heldout_counts", "passes_all_heldout_quantities", "excluded_rows_match_actual_violations"):
                        bucket[name] += evaluated[name]
                    if evaluated["accepted_wrong"]:
                        bucket["wrong_passes_all_relations"] += evaluated["passes_all_heldout_relations"]
                        bucket["wrong_passes_all_counts"] += evaluated["passes_all_heldout_counts"]
                        bucket["wrong_passes_both"] += evaluated["passes_all_heldout_relations"] and evaluated["passes_all_heldout_counts"]
                trajectories[(world_id, method)].append({"prefix": prefix, **evaluated})
                if prefix == 8 and evaluated["accepted_wrong"] and len(examples[(condition, method, "wrong")]) < 3:
                    examples[(condition, method, "wrong")].append({"inference": record, "evaluation": output.copy()})
            if prefix == 8 and best_status == "ambiguous_positive" and len(examples[(condition, "consensus", "ambiguous")]) < 3:
                examples[(condition, "consensus", "ambiguous")].append({"inference": record, "evaluation": output.copy()})
            out.write(json.dumps(output, separators=(",", ":"))+"\n")
    history = collections.defaultdict(collections.Counter)
    first_correct = collections.defaultdict(collections.Counter)
    first_wrong = collections.defaultdict(collections.Counter)
    for (world_id, method), steps in trajectories.items():
        condition = world_id.split("-", 1)[1]
        counter = history[(condition, method)]
        counter["worlds"] += 1
        wrong = [x for x in steps if x["accepted_wrong"]]
        correct = [x for x in steps if x["accepted_correct"]]
        counter["ever_wrong_accepted"] += bool(wrong)
        counter["ever_correct_accepted"] += bool(correct)
        if wrong:
            first_wrong[(condition, method)][str(wrong[0]["prefix"])] += 1
            final = steps[-1]
            counter["wrong_then_final_correct"] += final["accepted_correct"]
            counter["wrong_then_final_wrong"] += final["accepted_wrong"]
            counter["wrong_then_final_abstained"] += final["status"] == "abstained_ambiguity"
            counter["wrong_then_final_rejected"] += final["status"].startswith("rejected")
        if correct:
            first_correct[(condition, method)][str(correct[0]["prefix"])] += 1
    actual_distribution = collections.defaultdict(collections.Counter)
    for world_id, key in keys.items():
        condition = world_id.split("-", 1)[1]
        actual_distribution[condition][str(len(key["actual_violations"]))] += 1
    aggregate = {"created_utc": datetime.now(timezone.utc).isoformat(), "scope": "Fresh synthetic worlds; exact maximum consensus and independent evaluator",
                 "worlds": len(keys), "base_seeds": 300, "prefix_states": manifest["prefix_records"], "methods": list(METHODS),
                 "rows": [{"condition": c, "method": m, "prefix": n, **dict(buckets[(c, m, n)])} for c in CONDITIONS for m in METHODS for n in range(1, 9)],
                 "optimal_sets": [{"condition": c, "prefix": n, **dict(optimal[(c, n)])} for c in CONDITIONS for n in range(1, 9)],
                 "trajectories": [{"condition": c, "method": m, **dict(history[(c, m)]), "first_correct_prefixes": dict(first_correct[(c, m)]),
                                   "first_wrong_prefixes": dict(first_wrong[(c, m)])} for c in CONDITIONS for m in METHODS],
                 "actual_violation_distributions": {c: dict(actual_distribution[c]) for c in CONDITIONS},
                 "inference_sha256": digest(ENDPOINT/"inferences.jsonl"), "evaluated_sha256": digest(destination),
                 "evaluator_key_sha256": digest(ENDPOINT/"evaluator-key.jsonl"), "code_sha256": digest(Path(__file__))}
    save(ENDPOINT/"aggregate.json", aggregate)
    save(ENDPOINT/"case-examples.json", {"selection": "First three final wrong/ambiguous cases per condition and method in ascending generator order",
                                       "cases": [{"condition": c, "method": m, "kind": kind, "records": values} for (c, m, kind), values in examples.items()]})
    print(json.dumps({"worlds": len(keys), "prefix_states": manifest["prefix_records"], "evaluated_bytes": destination.stat().st_size}))
    for row in aggregate["rows"]:
        if row["prefix"] == 8:
            print(json.dumps(row))


if __name__ == "__main__":
    main()
