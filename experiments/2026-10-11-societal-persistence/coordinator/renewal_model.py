"""Exact invented service-renewal, dependency and accounting constructions."""
from __future__ import annotations
import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATES = tuple(product(range(3), range(3), range(4)))
SAFE = frozenset(s for s in STATES if s[0] > 0 and s[1] > 0)
TASKS = ("renew_A", "renew_B", "train")
SHOCKS = {"none": ((0, 0),), "focal": ((0, 0), (1, 0)),
          "common": ((0, 0), (1, 1)), "full": tuple(product(range(2), repeat=2))}
START = (2, 2, 3)

def powerset(values):
    return [tuple(items) for n in range(len(values) + 1) for items in combinations(values, n)]

def actions(state, budget):
    return [a for a in powerset(TASKS) if len(a) <= budget and (not a or state[2] > 0)]

def transition(state, action, shock, skill_age):
    a, b, k = state
    a = 2 if "renew_A" in action else max(0, a - 1)
    b = 2 if "renew_B" in action else max(0, b - 1)
    k = 3 if "train" in action else max(0, k - skill_age)
    return max(0, a - shock[0]), max(0, b - shock[1]), k

def predecessor(target, budget, skill_age, shocks, robust):
    out = set()
    for state in SAFE:
        for action in actions(state, budget):
            admitted = [transition(state, action, shock, skill_age) in target for shock in shocks]
            if all(admitted) if robust else any(admitted):
                out.add(state)
                break
    return frozenset(out)

def policies(target, budget, skill_age, shocks, robust):
    out = []
    for state in sorted(target):
        for action in actions(state, budget):
            next_states = [transition(state, action, shock, skill_age) for shock in shocks]
            if (all(s in target for s in next_states) if robust else any(s in target for s in next_states)):
                out.append({"state": list(state), "action": list(action),
                            "successors": [{"shock": list(d), "state": list(s), "in_kernel": s in target} for d, s in zip(shocks, next_states)]})
                break
    assert len(out) == len(target)
    return out

def solve(budget, skill_age, shock_name, robust):
    shocks = SHOCKS[shock_name]
    finite = [SAFE]
    for _ in range(12):
        finite.append(predecessor(finite[-1], budget, skill_age, shocks, robust))
    layers = [SAFE]
    while True:
        nxt = predecessor(layers[-1], budget, skill_age, shocks, robust)
        assert nxt <= layers[-1]
        if nxt == layers[-1]:
            break
        layers.append(nxt)
        assert len(layers) <= len(STATES) + 1
    kernel = layers[-1]
    max_horizon = None if START in kernel else max(h for h, values in enumerate(layers) if START in values)
    return {"quantifier": "exists_action_forall_shocks" if robust else "exists_action_exists_shock",
            "finite_horizons": [{"transitions": h, "states": [list(s) for s in sorted(values)],
                                 "count": len(values), "primary_viable": START in values} for h, values in enumerate(finite)],
            "fixed_point_layers": [{"iteration": h, "count": len(values), "states": [list(s) for s in sorted(values)]} for h, values in enumerate(layers)],
            "infinite_kernel": [list(s) for s in sorted(kernel)], "infinite_count": len(kernel),
            "primary": {"start": list(START), "infinite_viable": START in kernel,
                        "maximum_safe_transitions_if_finite": max_horizon},
            "infinite_policy": policies(kernel, budget, skill_age, shocks, robust)}

def dependency_case(shared):
    services = {"A": [["A1", "U" if shared else "U1"], ["A2", "U" if shared else "U2"]],
                "B": [["B1", "U" if shared else "U3"], ["B2", "U" if shared else "U4"]]}
    components = sorted({node for routes in services.values() for route in routes for node in route})
    failing = []
    for items in powerset(components):
        failed = set(items)
        lost = [service for service, routes in services.items() if not any(not failed.intersection(route) for route in routes)]
        if lost:
            failing.append((frozenset(items), lost))
    minimal = [(cut, lost) for cut, lost in failing if not any(other < cut for other, _ in failing)]
    return {"shared_input": shared, "services": services, "components": components,
            "failure_sets_enumerated": 2 ** len(components),
            "inclusion_minimal_service_failure_sets": [{"failed_components": sorted(cut), "lost_services": lost} for cut, lost in minimal],
            "minimum_failure_cardinality": min(len(cut) for cut, _ in minimal),
            "probabilities": None}

def inverse_bounds():
    records = [
        ("short_stock_covered", 1, 2, 0, 0),
        ("long_demand_known_bounds", 8, 2, 1, 0),
        ("large_initial_stock", 8, 10, 0, 0),
        ("unknown_import_upper_bound", 8, 2, None, 0),
        ("unknown_initial_stock_upper_bound", 8, None, 1, 0),
        ("exogenous_supply_closes_deficit", 8, 2, 1, 5),
        ("unresolved_occupation_minimum", 0, 2, 1, 0)]
    out = []
    for name, demand, stock, imported, exogenous in records:
        identified = all(x is not None for x in (stock, imported, exogenous))
        lower = max(0, demand - stock - imported - exogenous) if identified else 0
        out.append({"case": name, "minimum_cumulative_demand": demand,
                    "maximum_initial_usable_stock": stock, "maximum_imported_service": imported,
                    "maximum_nonrenewal_exogenous_supply": exogenous,
                    "additional_renewal_lower_bound": lower, "finite_supply_bounds_available": identified,
                    "mechanism_identified": False})
    return out

def run():
    worlds = []
    for budget, skill_age, shock_name in product(range(4), range(2), SHOCKS):
        worlds.append({"budget": budget, "skill_age": skill_age, "shock_support": shock_name,
                       "possible": solve(budget, skill_age, shock_name, False),
                       "robust": solve(budget, skill_age, shock_name, True)})
    assert len(worlds) == 32 and len(SAFE) == 16 and len(STATES) == 36
    for world in worlds:
        assert {tuple(s) for s in world["robust"]["infinite_kernel"]} <= {tuple(s) for s in world["possible"]["infinite_kernel"]}
    return {"status": "synthetic exact construction; no archaeological calibration or novelty claim",
            "protocol_sha256": hashlib.sha256((HERE / "MODEL-PROTOCOL.md").read_bytes()).hexdigest(),
            "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "state_count": len(STATES), "safe_state_count": len(SAFE), "worlds": worlds,
            "dependency_cases": [dependency_case(True), dependency_case(False)], "inverse_bound_controls": inverse_bounds(),
            "scope": "Viability under the declared transitions and controller; structural dependencies; ordinary accounting lower bounds. No empirical likelihood, institution identification, distributed implementation or historical duration."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Endpoint exists; use a fresh output path.")
    result = run()
    args.out.mkdir(parents=True)
    (args.out / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"worlds": len(result["worlds"]), "states": result["state_count"],
                      "dependency_minimum_cuts": [x["minimum_failure_cardinality"] for x in result["dependency_cases"]],
                      "renewal_bounds": [x["additional_renewal_lower_bound"] for x in result["inverse_bound_controls"]]}))

if __name__ == "__main__":
    main()
