"""Independently bind saved uniqueness, evaluation and cost claims to observations."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json

from verify_run import check_certificate, independent_model, dot


def exact_rank(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    pivot = 0
    for column in range(6):
        candidates = [i for i in range(pivot, len(rows)) if rows[i][column] != 0]
        if not candidates:
            continue
        selected = candidates[0]
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        divisor = rows[pivot][column]
        rows[pivot] = [x / divisor for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot:
                factor = rows[i][column]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def membership_row(observation):
    row = [0] * 6
    row[observation["code"]] += 1
    for code in observation["children"]:
        row[code] -= 1
    return row


def check_uniqueness(state, observations):
    eq, rhs, ub, limits = independent_model(observations)
    absolute = any(o["kind"] == "count" for o in observations)
    membership = [membership_row(o) for o in observations
                  if o["kind"] == "membership" and o["complete"]]
    coefficient_rows = eq if absolute else eq[:-1]
    assert absolute == state["absolute_units_observed"]
    assert exact_rank(membership) == state["membership_equality_rank"]
    assert exact_rank(coefficient_rows) == state["observed_coefficient_rank"]
    if not state["strict_positive_feasible"]:
        assert state["classification"] == "positive_model_rejected"
        assert not state["relative_unique"] and not state["absolute_unique"]
        return
    point = [F(v) for v in state["positive_point"]]
    fixed_coordinates = all(low == high and "infinity" not in low
                            for low, high in state["coordinate_ranges"])
    fixed_relative = fixed_coordinates or exact_rank(membership) == 5
    tests = state.get("relative_tests", [])
    if absolute and not fixed_relative:
        fixed_relative = True
        for index, test in enumerate(tests, start=1):
            assert test["code"] == index
            objective = [F(0)] * 6
            objective[index] = point[0]
            objective[0] = -point[index]
            zero = True
            for side, multiplier in (("lower", 1), ("upper", -1)):
                proof = test[side]
                check_certificate(proof)
                expected = [multiplier * x for x in objective]
                if [[F(v) for v in row] for row in proof["ub"]] == ub:
                    assert [[F(v) for v in row] for row in proof["eq"]] == eq
                    assert [F(v) for v in proof["rhs"]] == rhs
                    assert [F(v) for v in proof["objective"]] == expected
                    assert [[F(v) for v in row] for row in proof["ub"]] == ub
                    assert [F(v) for v in proof["limits"]] == limits
                    zero &= F(proof["objective_value"]) == 0
                else:
                    # An unbounded functional has a nonnegative recession ray.
                    assert [[F(v) for v in row] for row in proof["eq"]] == eq
                    assert all(F(v) == 0 for v in proof["rhs"])
                    assert [[F(v) for v in row] for row in proof["ub"]] == ub + [expected]
                    assert [F(v) for v in proof["limits"]] == [0] * len(ub) + [-1]
                    zero = False
            if not zero:
                fixed_relative = False
                assert index == len(tests)
                break
        if fixed_relative:
            assert len(tests) == 5
    else:
        assert not tests
    assert state["relative_unique"] == fixed_relative
    assert state["absolute_unique"] == (absolute and fixed_coordinates)
    if fixed_relative:
        assert [F(v) for v in state["relative_values"]] == [v / sum(point) for v in point]
    expected = ("absolute_unique" if absolute and fixed_coordinates else
                "relative_unique_scale_interval" if fixed_relative and absolute else
                "relative_unique_scale_unfixed" if fixed_relative else "positive_ambiguity")
    assert state["classification"] == expected


def independent_evaluation(state, observations, world):
    result = {"classification": state["classification"], "relative_correct": False,
              "absolute_correct": False, "wrong_relative_unique": False,
              "wrong_absolute_unique": False, "withheld_relations_pass": None,
              "withheld_counts_pass": None}
    ownership = world["condition"] == "ownership"
    if not state["strict_positive_feasible"]:
        result["truth_retained"] = None if ownership else False
        return result
    truth = [F(v) for v in world["concealed_values"]]
    if ownership:
        result["truth_retained"] = None
    else:
        retained = True
        for observation in observations:
            if observation["kind"] == "count":
                retained &= observation["lower"] <= truth[observation["code"]] <= observation["upper"]
            else:
                residual = dot(membership_row(observation), truth)
                retained &= residual == 0 if observation["complete"] else residual >= 0
        result["truth_retained"] = bool(retained)
    if state["relative_unique"]:
        vector = [F(v) for v in state["relative_values"]]
        passes = all(dot(membership_row(o), vector) == 0 for o in world["withheld_relations"])
        correct = passes if ownership else vector == [v / sum(truth) for v in truth]
        result.update(withheld_relations_pass=passes, relative_correct=correct,
                      wrong_relative_unique=not correct)
    if state["absolute_unique"]:
        vector = [F(v) for v in state["absolute_values"]]
        passes = all(vector[o["code"]] == o["quantity"] for o in world["withheld_counts"])
        correct = passes and result["withheld_relations_pass"] if ownership else vector == truth
        result.update(withheld_counts_pass=passes, absolute_correct=correct,
                      wrong_absolute_unique=not correct)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    worlds = {(w["condition"], w["seed"]): w for w in json.loads((args.run / "worlds.json").read_text())}
    states, records, evaluations, hashes = 0, 0, 0, {}
    classifications = Counter()
    for path in sorted(args.run.glob("*.json")):
        if not any(path.name.endswith("-" + p + ".json") for p in ("information_rank", "random", "cost_availability", "information_overlap")):
            continue
        record = json.loads(path.read_text())
        world = worlds[(record["condition"], record["seed"])]
        observations = list(world["initial_observations"])
        check_uniqueness(record["initial_state"], observations)
        evaluation = independent_evaluation(record["initial_state"], observations, world)
        assert evaluation == record["initial_evaluation"]
        states += 1; evaluations += 1
        relative_cost = 0 if evaluation["relative_correct"] else None
        absolute_cost = 0 if evaluation["absolute_correct"] else None
        for step in record["trace"]:
            observations.append(step["response_after_selection"])
            check_uniqueness(step["state"], observations)
            evaluation = independent_evaluation(step["state"], observations, world)
            assert evaluation == step["evaluation_after_selection"]
            if relative_cost is None and evaluation["relative_correct"]:
                relative_cost = step["spent"]
            if absolute_cost is None and evaluation["absolute_correct"]:
                absolute_cost = step["spent"]
            states += 1; evaluations += 1
        final = record["trace"][-1]["state"] if record["trace"] else record["initial_state"]
        assert final == record["final_state"]
        assert independent_evaluation(final, observations, world) == record["final_evaluation"]
        assert relative_cost == record["first_correct_relative_cost"]
        assert absolute_cost == record["first_correct_absolute_cost"]
        classifications[final["classification"]] += 1
        hashes[path.name] = sha256(path.read_bytes()).hexdigest()
        records += 1
    report = {"status": "passed", "policy_records": records, "states_checked": states,
              "evaluations_checked": evaluations, "final_classifications": dict(classifications),
              "checks": ["exact independent equality ranks", "relative-functional certificate binding",
                         "relative and absolute uniqueness", "independent truth-retention evaluation",
                         "withheld relation/count evaluation", "first correct identification costs"],
              "record_hashes": hashes, "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "base_verifier_sha256": sha256(Path(__file__).with_name("verify_run.py").read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "record_hashes"}, indent=2))


if __name__ == "__main__":
    main()
