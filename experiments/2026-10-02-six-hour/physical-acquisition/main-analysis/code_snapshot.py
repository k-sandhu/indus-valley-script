"""Derive paired cost, ambiguity and validation summaries from frozen acquisitions."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json
import statistics


POLICIES = ("information_rank", "random", "cost_availability", "information_overlap")


def ratio_width(record, world):
    state = record["final_state"]
    if not state["relative_unique"] or not state["absolute_units_observed"]:
        return None
    low, high = state["coordinate_ranges"][0]
    if "infinity" in low or "infinity" in high:
        return None
    # Evaluation only: divide by a true quantity so that the true scale is 1.
    return (F(high) - F(low)) / world["concealed_values"][0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir()
    worlds = {(w["condition"], w["seed"]): w for w in json.loads((args.run / "worlds.json").read_text())}
    records, hashes = [], {}
    for path in sorted(args.run.glob("*.json")):
        if any(path.name.endswith("-" + p + ".json") for p in POLICIES):
            records.append(json.loads(path.read_text()))
            hashes[path.name] = sha256(path.read_bytes()).hexdigest()
    rows, paired, cases = [], [], []
    conditions = sorted({r["condition"] for r in records})
    for condition in conditions:
        present_policies = [p for p in POLICIES if any(r["condition"] == condition and r["policy"] == p for r in records)]
        condition_worlds = [w for (c, _), w in worlds.items() if c == condition]
        no_count = sorted(w["seed"] for w in condition_worlds if not any(a["available"] and a["kind"] == "count" for a in w["public_actions"]))
        for policy in present_policies:
            selected = [r for r in records if r["condition"] == condition and r["policy"] == policy]
            widths = [(r["seed"], ratio_width(r, worlds[(condition, r["seed"])])) for r in selected]
            bounded_widths = [w for _, w in widths if w is not None]
            exact_costs = [r["first_correct_absolute_cost"] for r in selected if r["first_correct_absolute_cost"] is not None]
            ever_wrong = [r for r in selected if any(t["evaluation_after_selection"]["wrong_absolute_unique"] for t in r["trace"])]
            retract = [r for r in ever_wrong if r["final_state"]["classification"] == "positive_model_rejected"]
            counts = [sum(t["action"]["kind"] == "count" for t in r["trace"]) for r in selected]
            rows.append({"condition": condition, "policy": policy, "worlds": len(selected),
                         "no_available_count_seeds": no_count,
                         "correct_absolute_identified": len(exact_costs),
                         "first_absolute_cost_mean_given_identified": statistics.mean(exact_costs) if exact_costs else None,
                         "first_absolute_cost_median_given_identified": statistics.median(exact_costs) if exact_costs else None,
                         "ever_wrong_absolute": len(ever_wrong), "wrong_absolute_then_rejected": len(retract),
                         "count_actions_mean": statistics.mean(counts), "count_actions_distribution": dict(Counter(counts)),
                         "final_classifications": dict(Counter(r["final_state"]["classification"] for r in selected)),
                         "absolute_identification_by_paid_cost": {str(cost): sum(r["first_correct_absolute_cost"] is not None and r["first_correct_absolute_cost"] <= cost for r in selected) for cost in range(25)},
                         "bounded_identified_ratio_scale_widths_relative_to_truth": {str(seed): str(width) for seed, width in widths if width is not None},
                         "bounded_scale_worlds": len(bounded_widths),
                         "bounded_scale_width_mean": str(sum(bounded_widths, F(0)) / len(bounded_widths)) if bounded_widths else None,
                         "bounded_scale_width_median": str(statistics.median(bounded_widths)) if bounded_widths else None})
            for record in selected:
                for index, step in enumerate(record["trace"]):
                    evaluation = step["evaluation_after_selection"]
                    if evaluation["wrong_absolute_unique"] and evaluation["withheld_relations_pass"] and not evaluation["withheld_counts_pass"]:
                        world = worlds[(condition, record["seed"])]
                        vector = [F(v) for v in step["state"]["absolute_values"]]
                        truth = world["concealed_values"]
                        cases.append({"condition": condition, "policy": policy, "seed": record["seed"],
                                      "first_trace_index": index, "spent": step["spent"],
                                      "record": f"{condition}-{record['seed']}-{policy}.json",
                                      "true_values": truth, "inferred_values": [str(v) for v in vector],
                                      "scale_factors": [str(v / q) for v, q in zip(vector, truth)],
                                      "withheld_relation_residuals": [str(vector[o["code"]] - sum(vector[j] for j in o["children"])) for o in world["withheld_relations"]],
                                      "withheld_count_residuals": [str(vector[o["code"]] - o["quantity"]) for o in world["withheld_counts"]],
                                      "final_classification": record["final_state"]["classification"]})
                        break
        for comparison in present_policies:
            if comparison == "information_rank":
                continue
            by_seed = {r["seed"]: r for r in records if r["condition"] == condition and r["policy"] == "information_rank"}
            comparison_rows = [r for r in records if r["condition"] == condition and r["policy"] == comparison]
            pairs = [(by_seed[r["seed"]], r) for r in comparison_rows]
            both = [(a["first_correct_absolute_cost"], b["first_correct_absolute_cost"]) for a, b in pairs if a["first_correct_absolute_cost"] is not None and b["first_correct_absolute_cost"] is not None]
            paired.append({"condition": condition, "reference": "information_rank", "comparison": comparison,
                           "both_absolute_identified": len(both),
                           "reference_only_absolute_identified": sum(a["first_correct_absolute_cost"] is not None and b["first_correct_absolute_cost"] is None for a, b in pairs),
                           "comparison_only_absolute_identified": sum(b["first_correct_absolute_cost"] is not None and a["first_correct_absolute_cost"] is None for a, b in pairs),
                           "reference_minus_comparison_cost_mean_on_common_successes": statistics.mean(a - b for a, b in both) if both else None,
                           "reference_faster_on_common_successes": sum(a < b for a, b in both),
                           "comparison_faster_on_common_successes": sum(a > b for a, b in both),
                           "same_cost_on_common_successes": sum(a == b for a, b in both)})
    report = {"status": "derived-from-frozen-synthetic-records", "run": args.run.as_posix(),
              "analysis_status": "Post-run descriptive analysis; scale-width normalization reads the hidden answer only in evaluation.",
              "policy_records": len(records), "rows": rows, "paired": paired,
              "wrong_scale_passes_relations_fails_counts": cases,
              "input_record_hashes": hashes, "analysis_code_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps({"policy_records": len(records), "wrong_scale_cases": len(cases), "paired": paired}, indent=2))


if __name__ == "__main__":
    main()
