"""Direct aggregate, candidate-certificate and trajectory review of saved outputs."""
from __future__ import annotations
import collections
from datetime import datetime, timezone
from fractions import Fraction
import itertools
import json
from math import gcd, lcm
from pathlib import Path
import shutil
from khipu_robust import ENDPOINT, digest, save


def normalize(row):
    values = list(map(Fraction, row))
    multiplier = lcm(*(x.denominator for x in values))
    integer = [int(x*multiplier) for x in values]
    divisor = gcd(gcd(abs(integer[0]), abs(integer[1])), abs(integer[2]))
    if not divisor:
        return (0, 0, 0)
    integer = [x//divisor for x in integer]
    if next(x for x in integer if x) < 0:
        integer = [-x for x in integer]
    return tuple(integer)


def dot(row, vector):
    total = Fraction(0)
    for a, b in zip(row, vector):
        total += Fraction(a)*Fraction(b)
    return total


def certificates(rows, result):
    line_count = point_count = witness_count = pair_count = 0
    distinct = set(normalize(row) for row in rows if any(row))
    assert distinct == {tuple(x["line"]) for x in result["line_candidates"]}
    for line in result["line_candidates"]:
        normalized = tuple(line["line"])
        expected = [i for i, row in enumerate(rows) if not any(row) or normalize(row) == normalized]
        assert expected == line["support_indices"] and len(expected) == line["support"]
        if line["feasible"]:
            base, slope = list(map(Fraction, line["base"])), list(map(Fraction, line["slope"]))
            assert dot(normalized, base) == 0 and dot(normalized, slope) == 0
            lower = upper = None
            for constant, coefficient in zip(base, slope):
                if coefficient > 0:
                    bound = -constant/coefficient
                    lower = bound if lower is None else max(lower, bound)
                elif coefficient < 0:
                    bound = -constant/coefficient
                    upper = bound if upper is None else min(upper, bound)
                else:
                    assert constant > 0
            assert lower is not None and (upper is None or lower < upper)
            assert Fraction(line["lower"]) == lower
            assert line["upper"] is None if upper is None else Fraction(line["upper"]) == upper
            for witness in line["witnesses"]:
                values = list(map(Fraction, witness))
                assert values[0] == 1 and all(x > 0 for x in values)
                assert dot(normalized, values) == 0
                witness_count += 1
        else:
            a, b, c = normalized
            if not b and not c:
                assert a != 0
            elif not c:
                assert Fraction(-a, b) <= 0
            else:
                constant, coefficient = Fraction(-a, c), Fraction(-b, c)
                assert coefficient == 0 and constant <= 0 or coefficient < 0 and constant <= 0
        line_count += 1
    combinations = list(itertools.combinations(sorted(distinct), 2))
    assert len(combinations) == len(result["pair_checks"])
    positive_points = set()
    for (left, right), checked in zip(combinations, result["pair_checks"]):
        assert tuple(checked["first"]) == left and tuple(checked["second"]) == right
        a, b, c = left
        d, e, f = right
        det = b*f-c*e
        assert det == checked["determinant"]
        if det:
            t, h = Fraction(c*d-a*f, det), Fraction(a*e-b*d, det)
            assert Fraction(checked["t"]) == t and Fraction(checked["h"]) == h
            positive = t > 0 and h > 0
            assert checked["positive"] == positive
            if positive:
                positive_points.add((Fraction(1), t, h))
        pair_count += 1
    assert positive_points == {tuple(map(Fraction, p["values"])) for p in result["point_candidates"]}
    for candidate in result["point_candidates"]:
        matched = [i for i, row in enumerate(rows) if dot(row, candidate["values"]) == 0]
        assert matched == candidate["support_indices"] and len(matched) == candidate["support"]
        point_count += 1
    return line_count, pair_count, witness_count, point_count


def main():
    keys = {}
    with (ENDPOINT/"evaluator-key.jsonl").open(encoding="utf-8") as f:
        for line in f:
            world = json.loads(line)
            keys[world["id"]] = world["key"]
    aggregate = json.loads((ENDPOINT/"aggregate.json").read_text(encoding="utf-8"))
    buckets = collections.defaultdict(collections.Counter)
    histories = collections.defaultdict(list)
    optimal = collections.defaultdict(collections.Counter)
    geometry_counts = [0, 0, 0, 0]
    records = 0
    with (ENDPOINT/"inferences.jsonl").open(encoding="utf-8") as f, (ENDPOINT/"evaluated-prefixes.jsonl").open(encoding="utf-8") as ef:
        for line, eval_line in itertools.zip_longest(f, ef):
            assert line and eval_line
            inferred, evaluated = json.loads(line), json.loads(eval_line)
            world_id, prefix = inferred["world_id"], inferred["prefix"]
            condition = world_id.split("-", 1)[1]
            result = inferred["consensus"]
            counts = certificates(inferred["equations"], result)
            geometry_counts = [a+b for a, b in zip(geometry_counts, counts)]
            unique = result["status"] == "unique_positive"
            correct = unique and list(map(Fraction, result["optimal_points"][0]["values"])) == keys[world_id]["true_weights"]
            assert evaluated["raw_unique_correct"] == correct and evaluated["raw_unique_wrong"] == (unique and not correct)
            ob = optimal[(condition, prefix)]
            for name, value in {"records": 1, "truth_retained": evaluated["true_vector_in_best_set"], "unique_correct": correct,
                                "unique_wrong": unique and not correct, "ambiguous": not unique,
                                "with_optimal_family": bool(result["optimal_families"]),
                                "with_multiple_optimal_points": len(result["optimal_points"]) > 1}.items():
                ob[name] += value
            for method, decision in evaluated["methods"].items():
                bucket = buckets[(condition, method, prefix)]
                bucket["records"] += 1
                bucket[decision["status"]] += 1
                for name in ("accepted_correct", "accepted_wrong"):
                    bucket[name] += decision[name]
                if decision["status"] == "accepted_unique":
                    for name in ("passes_all_heldout_relations", "passes_all_heldout_counts", "passes_all_heldout_quantities", "excluded_rows_match_actual_violations"):
                        bucket[name] += decision[name]
                    if decision["accepted_wrong"]:
                        bucket["wrong_passes_all_relations"] += decision["passes_all_heldout_relations"]
                        bucket["wrong_passes_all_counts"] += decision["passes_all_heldout_counts"]
                        bucket["wrong_passes_both"] += decision["passes_all_heldout_relations"] and decision["passes_all_heldout_counts"]
                histories[(world_id, method)].append((prefix, decision))
            records += 1
    for row in aggregate["rows"]:
        expected = buckets[(row["condition"], row["method"], row["prefix"])]
        actual = {k: v for k, v in row.items() if k not in ("condition", "method", "prefix")}
        assert all(actual.get(k, 0) == expected.get(k, 0) for k in actual.keys() | expected.keys())
    for row in aggregate["optimal_sets"]:
        expected = optimal[(row["condition"], row["prefix"])]
        actual = {k: v for k, v in row.items() if k not in ("condition", "prefix")}
        assert all(actual.get(k, 0) == expected.get(k, 0) for k in actual.keys() | expected.keys())
    history_totals = collections.defaultdict(collections.Counter)
    first_correct, first_wrong = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for (world_id, method), sequence in histories.items():
        assert [n for n, _ in sequence] == list(range(1, 9))
        condition = world_id.split("-", 1)[1]
        wrong = [n for n, d in sequence if d["accepted_wrong"]]
        correct = [n for n, d in sequence if d["accepted_correct"]]
        total = history_totals[(condition, method)]
        total["worlds"] += 1
        total["ever_wrong_accepted"] += bool(wrong)
        total["ever_correct_accepted"] += bool(correct)
        if wrong:
            first_wrong[(condition, method)][str(min(wrong))] += 1
            final = sequence[-1][1]
            total["wrong_then_final_correct"] += final["accepted_correct"]
            total["wrong_then_final_wrong"] += final["accepted_wrong"]
            total["wrong_then_final_abstained"] += final["status"] == "abstained_ambiguity"
            total["wrong_then_final_rejected"] += final["status"].startswith("rejected")
        if correct:
            first_correct[(condition, method)][str(min(correct))] += 1
    for row in aggregate["trajectories"]:
        key = (row["condition"], row["method"])
        expected = history_totals[key]
        actual = {k: v for k, v in row.items() if k not in ("condition", "method", "first_correct_prefixes", "first_wrong_prefixes")}
        assert all(actual.get(k, 0) == expected.get(k, 0) for k in actual.keys() | expected.keys())
        assert row["first_correct_prefixes"] == dict(first_correct[key]) and row["first_wrong_prefixes"] == dict(first_wrong[key])
    distributions = collections.defaultdict(collections.Counter)
    for world_id, key in keys.items():
        distributions[world_id.split("-", 1)[1]][str(len(key["actual_violations"]))] += 1
    assert aggregate["actual_violation_distributions"] == {k: dict(v) for k, v in distributions.items()}
    shutil.copyfile(Path(__file__), ENDPOINT/Path(__file__).name)
    save(ENDPOINT/"aggregate-review.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "passed": True,
         "prefix_records_checked": records, "decision_records_checked": records*3, "aggregate_rows_checked": len(aggregate["rows"]),
         "optimal_set_rows_checked": len(aggregate["optimal_sets"]), "trajectory_rows_checked": len(aggregate["trajectories"]),
         "line_candidates_checked": geometry_counts[0], "pair_certificates_checked": geometry_counts[1],
         "all_line_candidate_witnesses_checked": geometry_counts[2], "point_candidates_checked": geometry_counts[3],
         "corruption_histograms_checked": True, "aggregate_sha256": digest(ENDPOINT/"aggregate.json"),
         "code_sha256": digest(Path(__file__))})
    print("Saved independent candidate-certificate and aggregate review.")


if __name__ == "__main__":
    main()
