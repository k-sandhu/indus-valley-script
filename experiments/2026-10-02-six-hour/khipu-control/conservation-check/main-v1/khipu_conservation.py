"""Positive consensus with a separately observed collective constraint.

Homogeneous fitting normalizes u=1. Only the counted observation supplies an
absolute scale. All geometry receives rows and the public aggregate only.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import itertools
import json
from pathlib import Path
import random
import shutil
import sys

from khipu_robust import maximum_consensus, canonical, support, generate_world, digest, save

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/"experiments/2026-10-02-six-hour/khipu-control/conservation-check"
ENDPOINT = BASE/"main-v1"
CONDITIONS = ("complete", "two_swapped", "four_swapped", "local_missing_complete_pool",
              "missing_pool_declared", "missing_pool_misdeclared", "ownership")


def dot(row, vector):
    return sum(Fraction(a)*Fraction(b) for a, b in zip(row, vector))


def vector_at(base, slope, value):
    return [a+b*value for a, b in zip(base, slope)]


def clip_family(family, aggregate):
    """Intersect an open positive line with one closed linear halfspace."""
    base, slope = list(map(Fraction, family["base"])), list(map(Fraction, family["slope"]))
    lower = Fraction(family["lower"])
    upper = None if family["upper"] is None else Fraction(family["upper"])
    low_closed = high_closed = False
    constant, coefficient = dot(aggregate, base), dot(aggregate, slope)
    if coefficient > 0:
        bound = -constant/coefficient
        if bound > lower:
            lower, low_closed = bound, True
    elif coefficient < 0:
        bound = -constant/coefficient
        if upper is None or bound < upper:
            upper, high_closed = bound, True
    elif constant < 0:
        return {"feasible": False, "reason": "negative_fixed_collective_value"}
    if upper is not None and (lower > upper or lower == upper and not (low_closed and high_closed)):
        return {"feasible": False, "reason": "collective_interval_empty", "lower": str(lower), "upper": str(upper),
                "lower_closed": low_closed, "upper_closed": high_closed}
    if upper is not None and lower == upper:
        values = vector_at(base, slope, lower)
        assert all(x > 0 for x in values) and dot(aggregate, values) >= 0
        return {"feasible": True, "dimension": 0, "values": list(map(str, values))}
    choices = [lower+1, lower+2] if upper is None else [(2*lower+upper)/3, (lower+2*upper)/3]
    witnesses = [vector_at(base, slope, q) for q in choices]
    boundary = []
    if low_closed:
        boundary.append(vector_at(base, slope, lower))
    if high_closed:
        boundary.append(vector_at(base, slope, upper))
    assert all(all(x > 0 for x in witness) and dot(aggregate, witness) >= 0 for witness in witnesses+boundary)
    return {**family, "feasible": True, "dimension": 1, "lower": str(lower), "upper": None if upper is None else str(upper),
            "lower_closed": low_closed, "upper_closed": high_closed, "witnesses": [list(map(str, w)) for w in witnesses],
            "boundary_witnesses": [list(map(str, w)) for w in boundary]}


def halfspace_plane(aggregate):
    a, b, c = map(Fraction, aggregate)
    if b > 0:
        t = max(Fraction(1), (-a-c)/b+1)
        witnesses = [[Fraction(1), t, Fraction(1)], [Fraction(1), t+1, Fraction(1)]]
    elif c > 0:
        h = max(Fraction(1), (-a-b)/c+1)
        witnesses = [[Fraction(1), Fraction(1), h], [Fraction(1), Fraction(1), h+1]]
    elif not b and not c and a >= 0:
        witnesses = [[Fraction(1), Fraction(1), Fraction(1)], [Fraction(1), Fraction(2), Fraction(3)]]
    elif a > 0:
        epsilon = a/(2*(abs(b)+abs(c)+1))
        witnesses = [[Fraction(1), epsilon, epsilon], [Fraction(1), epsilon/2, epsilon]]
    else:
        return {"feasible": False, "reason": "collective_halfspace_misses_positive_plane"}
    assert all(all(x > 0 for x in w) and dot(aggregate, w) >= 0 for w in witnesses)
    return {"feasible": True, "family": "positive_halfspace", "dimension": 2,
            "witnesses": [list(map(str, w)) for w in witnesses]}


def collective_consensus(rows, aggregate, kind):
    """Return every local-support maximizer inside the collective domain."""
    assert kind in ("equality", "inequality") and len(aggregate) == 3
    arrangement = maximum_consensus(rows+[aggregate] if kind == "equality" else rows)
    point_map, families, rejected = {}, [], []
    for point in arrangement["point_candidates"]:
        vector = list(map(Fraction, point["values"]))
        collective = dot(aggregate, vector)
        if collective == 0 if kind == "equality" else collective >= 0:
            indices = support(rows, vector)
            point_map[tuple(vector)] = {"values": point["values"], "support": len(indices), "support_indices": indices}
    zero_indices = [i for i, row in enumerate(rows) if not any(row)]
    for original in arrangement["line_candidates"]:
        if not original["feasible"]:
            rejected.append({"line": original["line"], "reason": "line_not_positive"})
            continue
        base, slope = list(map(Fraction, original["base"])), list(map(Fraction, original["slope"]))
        if kind == "equality":
            if dot(aggregate, base) or dot(aggregate, slope):
                rejected.append({"line": original["line"], "reason": "line_not_inside_collective_equality"})
                continue
            family = {**original, "dimension": 1, "lower_closed": False, "upper_closed": False, "boundary_witnesses": []}
        else:
            family = clip_family(original, aggregate)
            if not family["feasible"]:
                rejected.append({"line": original["line"], **family})
                continue
        if family["dimension"] == 0:
            vector = tuple(map(Fraction, family["values"]))
            indices = support(rows, vector)
            point_map[vector] = {"values": family["values"], "support": len(indices), "support_indices": indices}
            continue
        fixed = sorted(zero_indices+[i for i, row in enumerate(rows) if any(row) and canonical(row) == tuple(original["line"])])
        families.append({**family, "family": "positive_line", "support": len(fixed), "support_indices": fixed})
    if kind == "equality":
        plane = {"feasible": not any(aggregate), "family": "positive_plane", "dimension": 2,
                 "witnesses": [["1", "1", "1"], ["1", "2", "3"]]}
    else:
        plane = halfspace_plane(aggregate)
    if plane["feasible"]:
        families.append({**plane, "support": len(zero_indices), "support_indices": zero_indices})
    points = [point_map[key] for key in sorted(point_map)]
    if not points and not families:
        return {"status": "no_positive_solution", "best_support": None, "optimal_points": [], "optimal_families": [],
                "point_candidates": [], "family_candidates": [], "rejected_families": rejected,
                "reason": "collective_domain_has_no_positive_values", "aggregate": aggregate, "kind": kind}
    best = max(r["support"] for r in points+families)
    optimal_points = [r for r in points if r["support"] == best]
    optimal_families = [r for r in families if r["support"] == best]
    for family in optimal_families:
        for witness in family["witnesses"]:
            assert len(support(rows, list(map(Fraction, witness)))) == best
    unique = len(optimal_points) == 1 and not optimal_families
    return {"status": "unique_positive" if unique else "ambiguous_positive", "best_support": best,
            "optimal_points": optimal_points, "optimal_families": optimal_families, "point_candidates": points,
            "family_candidates": families, "rejected_families": rejected, "aggregate": aggregate, "kind": kind}


def decision(inferred, prefix, numerator, denominator):
    threshold = (numerator*prefix+denominator-1)//denominator
    if inferred["status"] == "no_positive_solution":
        state = "rejected_collective"
    elif inferred["best_support"] < threshold:
        state = "rejected_support"
    elif inferred["status"] == "ambiguous_positive":
        state = "abstained_ambiguity"
    else:
        state = "accepted_unique_ray"
    return {"status": state, "threshold": threshold,
            "normalized_values": inferred["optimal_points"][0]["values"] if state == "accepted_unique_ray" else None}


def public_aggregate(features, parents, pool):
    coefficients = [0, 0, 0]
    for object_id in parents:
        for j in range(3):
            coefficients[j] += features[object_id][j]
    for object_id in pool:
        for j in range(3):
            coefficients[j] -= features[object_id][j]
    return coefficients


def generated(seed, condition):
    original = "two_incomplete" if condition in ("local_missing_complete_pool", "missing_pool_declared", "missing_pool_misdeclared") else condition
    component, key = generate_world(seed, original)
    full_features = [list(x) for x in component["features"]]
    pooled = list(range(8, 32))
    omitted = []
    if condition in ("missing_pool_declared", "missing_pool_misdeclared"):
        omitted = sorted(x["removed_child"] for x in key["corruption_operations"])
        pooled = [i for i in pooled if i not in omitted]
        for i in omitted:
            component["features"][i] = None
    aggregate = public_aggregate(component["features"], list(range(8)), pooled)
    physical_scale = random.Random(seed+8000000).randrange(1, 8)
    component["collective_observation"] = {"witness_id": f"collective-{seed}-{condition}", "parents": list(range(8)), "pool": pooled,
            "declared_complete": condition != "missing_pool_declared", "kind": "inequality" if condition == "missing_pool_declared" else "equality",
            "aggregate": aggregate, "operation_premises": "same quantity, units and event; parent records describe contents; pooling conserves quantity"}
    component.pop("anchor"); component.pop("anchor_value")
    component["scale_observations"] = {"unmeasured": None, "counted": {"object_id": f"unit-object-{seed}", "features": [1, 0, 0], "count": physical_scale}}
    key["full_training_features"] = full_features
    key["scale"] = physical_scale
    key["true_weights"] = [physical_scale, 10*physical_scale, 100*physical_scale]
    for field in ("training_quantities", "heldout_quantities", "count_values"):
        key[field] = [physical_scale*x for x in key[field]]
    key["omitted_pool_objects"] = omitted
    key["actual_pool_complete"] = not omitted
    key["actual_additive_function"] = condition != "ownership"
    key["actual_collective_residual"] = sum(a*b for a, b in zip(aggregate, key["true_weights"]))
    key["unit_object_actual_count"] = physical_scale
    return component, key


def generate():
    if ENDPOINT.exists():
        raise FileExistsError(ENDPOINT)
    ENDPOINT.mkdir(parents=True)
    for name in ("PROTOCOL.md", "protocol-freeze.json", "PROTOCOL_AVAILABILITY.md", "availability-protocol-freeze.json", "source-acquisition.json"):
        shutil.copyfile(BASE/name, ENDPOINT/name)
    for name in ("khipu_conservation.py", "khipu_conservation_evaluate.py", "khipu_conservation_verify.py", "khipu_robust.py", "khipu_control.py"):
        shutil.copyfile(Path(__file__).with_name(name), ENDPOINT/name)
    inputs, keys = ENDPOINT/"component-inputs.jsonl", ENDPOINT/"evaluator-key.jsonl"
    count = 0
    with inputs.open("w", encoding="utf-8") as inf, keys.open("w", encoding="utf-8") as kf:
        for seed in range(20261020000, 20261020200):
            for condition in CONDITIONS:
                component, key = generated(seed, condition)
                world_id = f"{seed}-{condition}"
                inf.write(json.dumps({"id": world_id, "seed": seed, "condition": condition, "component": component}, separators=(",", ":"))+"\n")
                kf.write(json.dumps({"id": world_id, "key": key}, separators=(",", ":"))+"\n")
                count += 1
    save(ENDPOINT/"generation-manifest.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "worlds": count,
         "base_seeds": 200, "conditions": list(CONDITIONS), "scale_observation_conditions": ["unmeasured", "counted"],
         "seeds": [20261020000, 20261020199], "python_version": sys.version,
         "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in (inputs, keys)],
         "code_sha256": digest(Path(__file__)), "baseline_code_sha256": digest(Path(__file__).with_name("khipu_robust.py"))})
    print(f"Generated {count} fresh operation worlds and separate evaluator keys.")


def infer():
    destination = ENDPOINT/"inferences.jsonl"
    if destination.exists():
        raise FileExistsError(destination)
    count = 0
    with (ENDPOINT/"component-inputs.jsonl").open(encoding="utf-8") as inf, destination.open("w", encoding="utf-8") as out:
        for line in inf:
            world = json.loads(line)
            component = world["component"]
            collective = component["collective_observation"]
            assert public_aggregate(component["features"], collective["parents"], collective["pool"]) == collective["aggregate"]
            for prefix in range(1, 9):
                rows = component["equations"][:prefix]
                baseline = maximum_consensus(rows)
                constrained = collective_consensus(rows, collective["aggregate"], collective["kind"])
                policies = {}
                for model, fitted in (("baseline", baseline), ("collective", constrained)):
                    policies[model+"_three_quarter"] = decision(fitted, prefix, 3, 4)
                    policies[model+"_half"] = decision(fitted, prefix, 1, 2)
                record = {"world_id": world["id"], "prefix": prefix, "rows": rows, "aggregate": collective["aggregate"], "kind": collective["kind"],
                          "baseline": baseline, "collective": constrained, "policies": policies,
                          "scale_observations": component["scale_observations"], "unmeasured_normalization_is_gauge": True}
                out.write(json.dumps(record, separators=(",", ":"))+"\n")
                count += 1
    diagnostics = {}
    cases = {"plane_to_line": ([[0, 0, 0]], [-10, -9, 1], "equality"),
             "line_to_point": ([[-10, 1, 0]], [0, -10, 1], "equality"),
             "closed_boundary": ([[-1, 0, 1]], [-2, 1, 0], "inequality"),
             "infeasible_collective": ([[0, 0, 0]], [1, 1, 1], "equality"),
             "infeasible_halfspace": ([[0, 0, 0]], [0, -1, -1], "inequality")}
    for name, (rows, aggregate, kind) in cases.items():
        diagnostics[name] = {"rows": rows, "aggregate": aggregate, "kind": kind, "inferred": collective_consensus(rows, aggregate, kind)}
    save(ENDPOINT/"diagnostics.json", diagnostics)
    save(ENDPOINT/"inference-manifest.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "prefix_records": count,
         "inferences_sha256": digest(destination), "component_inputs_sha256": digest(ENDPOINT/"component-inputs.jsonl"),
         "bytes": destination.stat().st_size, "evaluator_key_opened": False, "fitting_input": "rows, aggregate, equality/inequality kind",
         "normalization": "u=1 is gauge; absolute scale comes only from observed count", "code_sha256": digest(Path(__file__))})
    print(f"Saved {count} exact prefix fits with all evaluator targets unopened.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["generate", "infer"])
    args = parser.parse_args()
    (generate if args.command == "generate" else infer)()
