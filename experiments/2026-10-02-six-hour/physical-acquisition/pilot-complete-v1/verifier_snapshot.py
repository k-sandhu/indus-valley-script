"""Check saved arithmetic proofs, action boundaries and object measurements."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json


def dot(a, b):
    return sum(F(x) * F(y) for x, y in zip(a, b))


def check_certificate(certificate):
    c, eq, rhs, ub, limits, x, lam, mu, lower = (
        certificate[key] for key in ("objective", "eq", "rhs", "ub", "limits", "primal",
                                     "inequality_dual", "equality_dual", "nonnegative_bound_dual"))
    assert all(F(v) >= 0 for v in x)
    assert all(dot(row, x) == F(b) for row, b in zip(eq, rhs))
    assert all(dot(row, x) <= F(b) for row, b in zip(ub, limits))
    assert all(F(v) <= 0 for v in lam) and all(F(v) >= 0 for v in lower)
    for j in range(len(c)):
        assert F(c[j]) == sum(F(row[j]) * F(v) for row, v in zip(ub, lam)) + sum(F(row[j]) * F(v) for row, v in zip(eq, mu)) + F(lower[j])
    assert dot(c, x) == dot(limits, lam) + dot(rhs, mu) == F(certificate["objective_value"])


def walk_certificates(value):
    if isinstance(value, dict):
        if "objective" in value and "primal" in value:
            yield value
        else:
            for child in value.values(): yield from walk_certificates(child)
    elif isinstance(value, list):
        for child in value: yield from walk_certificates(child)


def independent_model(observations):
    eq, rhs, ub, limits = [], [], [], []
    absolute = False
    for observation in observations:
        row = [0] * 6; row[observation["code"]] = 1
        if observation["kind"] == "membership":
            for code in observation["children"]: row[code] -= 1
            if observation["complete"]: eq.append(row); rhs.append(0)
            else: ub.append([-x for x in row]); limits.append(0)
        else:
            absolute = True
            if observation["lower"] == observation["upper"]:
                eq.append(row); rhs.append(observation["lower"])
            else:
                ub.extend([row, [-x for x in row]])
                limits.extend([observation["upper"], -observation["lower"]])
    if not absolute: eq.append([1] * 6); rhs.append(1)
    return eq, rhs, ub, limits


def check_state(state, observations):
    eq, rhs, ub, limits = independent_model(observations)
    strict_eq = [row + [0] for row in eq]
    strict_ub = [row + [0] for row in ub]
    strict_limits = list(limits)
    for code in range(6):
        row = [0] * 7; row[code] = -1; row[-1] = 1
        strict_ub.append(row); strict_limits.append(0)
    strict_ub.append([0] * 6 + [1]); strict_limits.append(1)
    strict_certificate = state["strict_positive_certificate"]
    convert = lambda rows: [[F(v) for v in row] for row in rows]
    if len(strict_certificate["objective"]) == 7:
        assert convert(strict_certificate["eq"]) == strict_eq
        assert list(map(F, strict_certificate["rhs"])) == rhs
        assert convert(strict_certificate["ub"]) == strict_ub
        assert list(map(F, strict_certificate["limits"])) == strict_limits
        assert list(map(F, strict_certificate["objective"])) == [0] * 6 + [-1]
    else:
        phase_ub = [row + [-1] for row in strict_ub]
        phase_limits = list(strict_limits)
        for row, b in zip(strict_eq, rhs):
            phase_ub.extend([row + [-1], [-v for v in row] + [-1]])
            phase_limits.extend([b, -b])
        assert not strict_certificate["eq"]
        assert convert(strict_certificate["ub"]) == phase_ub
        assert list(map(F, strict_certificate["limits"])) == phase_limits
        assert list(map(F, strict_certificate["objective"])) == [0] * 7 + [1]
    if not state["strict_positive_feasible"]:
        certificate = state["strict_positive_certificate"]
        assert (F(certificate["objective_value"]) > 0 if F(certificate["objective"][-1]) == 1 else F(certificate["objective_value"]) == 0)
        return
    point = [F(v) for v in state["positive_point"]]
    assert all(v > 0 for v in point)
    assert all(dot(row, point) == F(b) for row, b in zip(eq, rhs))
    assert all(dot(row, point) <= F(b) for row, b in zip(ub, limits))
    for code, (interval, proofs) in enumerate(zip(state["coordinate_ranges"], state["range_certificates"])):
        for side, bound in zip(("lower", "upper"), interval):
            certificate = proofs[side]
            if "infinity" in bound:
                ray = [F(v) for v in certificate["primal"]]
                assert all(dot(row, ray) == 0 for row in eq)
                assert all(dot(row, ray) <= 0 for row in ub)
                assert (ray[code] >= 1 if side == "upper" else ray[code] <= -1)
                assert convert(certificate["eq"]) == eq
                assert all(F(v) == 0 for v in certificate["rhs"])
                expected_objective = [0] * 6; expected_objective[code] = -1 if side == "upper" else 1
                assert convert(certificate["ub"]) == ub + [expected_objective]
                assert list(map(F, certificate["limits"])) == [0] * len(ub) + [-1]
            else:
                objective = [F(v) for v in certificate["objective"]]
                expected = [0] * 6; expected[code] = 1 if side == "lower" else -1
                assert objective == expected
                assert F(certificate["objective_value"]) == (F(bound) if side == "lower" else -F(bound))
                assert convert(certificate["eq"]) == eq and list(map(F, certificate["rhs"])) == rhs
                assert convert(certificate["ub"]) == ub and list(map(F, certificate["limits"])) == limits
    if state["absolute_unique"]:
        assert all(low == high for low, high in state["coordinate_ranges"])
        assert state["absolute_values"] == [low for low, _ in state["coordinate_ranges"]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    result = json.loads((args.run / "results.json").read_text())
    worlds = {(w["condition"], w["seed"]): w for w in json.loads((args.run / "worlds.json").read_text())}
    assert sha256((args.run / "code_snapshot.py").read_bytes()).hexdigest() == result["code_sha256"]
    assert sha256((args.run / "protocol_snapshot.md").read_bytes()).hexdigest() == result["protocol_sha256"]
    if "pilot_repair_sha256" in result:
        assert sha256((args.run / "pilot_repair_snapshot.md").read_bytes()).hexdigest() == result["pilot_repair_sha256"]
    if "base_protocol_sha256" in result:
        assert sha256((args.run / "base_protocol_snapshot.md").read_bytes()).hexdigest() == result["base_protocol_sha256"]
    files = sorted(p for p in args.run.glob("*.json") if any(p.name.endswith("-" + policy + ".json") for policy in ("information_rank", "random", "cost_availability", "information_overlap")))
    certificates, states, actions, duplicates = 0, 0, 0, set()
    hashes = {}
    for path in files:
        record = json.loads(path.read_text())
        world = worlds[(record["condition"], record["seed"])]
        objects = {o["id"]: o for o in world["objects"]}
        for certificate in walk_certificates(record):
            key = sha256(json.dumps(certificate, sort_keys=True).encode()).hexdigest()
            if key not in duplicates:
                check_certificate(certificate); duplicates.add(key); certificates += 1
        observed = list(world["initial_observations"])
        acquired, spent = set(), 0
        check_state(record["initial_state"], observed); states += 1
        for step in record["trace"]:
            action = step["action"]
            public = next(a for a in world["public_actions"] if a["id"] == action["id"])
            assert action == public and action["available"] and action["id"] not in acquired
            assert action["cost"] <= 24 - spent
            expected_hash = sha256(json.dumps({"actions": world["public_actions"], "acquired": sorted(acquired),
                                              "remaining": 24 - spent, "observations": observed}, sort_keys=True).encode()).hexdigest()
            assert expected_hash == step["selection"]["public_input_hash"]
            choices = [a for a in world["public_actions"] if a["available"] and a["id"] not in acquired and a["cost"] <= 24 - spent]
            if record["policy"] == "cost_availability" or step["selection"].get("zero_score_cost_fallback") or step["selection"].get("fallback_after_positive_rejection"):
                assert action == min(choices, key=lambda a: (a["cost"], not a["complete_record"], a["id"]))
            elif record["policy"] in ("information_rank", "information_overlap"):
                scores = step["selection"]["scores"]
                maximum = max(F(s["score"]) for s in scores)
                assert action["id"] == min(s["action_id"] for s in scores if F(s["score"]) == maximum)
            response = step["response_after_selection"]
            assert response == world["oracle_responses"][action["id"]]
            if action["kind"] == "count":
                identifier = response["counted_object_id"]
                assert identifier == action["object_id"] and world["observed_label_by_object"][identifier] == action["code"]
                if record["condition"] in ("complete_exact", "incomplete", "ownership"):
                    assert response["lower"] == response["upper"] == objects[identifier]["quantity"]
                if record["condition"] == "valid_intervals":
                    assert response["lower"] <= objects[identifier]["quantity"] <= response["upper"]
            spent += action["cost"]; acquired.add(action["id"]); observed.append(response)
            assert spent == step["spent"]
            check_state(step["state"], observed); states += 1; actions += 1
        assert spent == record["spent"] and len(acquired) == record["actions_acquired"]
        hashes[path.name] = sha256(path.read_bytes()).hexdigest()
    report = {"status": "passed", "policy_records": len(files), "states_checked": states,
              "actions_checked": actions, "distinct_exact_certificates_checked": certificates,
              "checks": ["code/protocol snapshot hashes", "exact primal/dual optimality", "positive points and coordinate range proofs", "unbounded recession directions", "positive rejection objective", "public action input hashes", "policy tie rules", "budget and availability", "oracle acquired only after choice", "counted object and observed label", "valid interval coverage"],
              "record_hashes": hashes, "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "record_hashes"}, indent=2))


if __name__ == "__main__": main()
