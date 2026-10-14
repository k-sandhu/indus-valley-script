"""Derive relay trajectories for the renewal-model visualization from frozen endpoints.

Reads the baseline results (coordinator/run-v1) and the shared-operation results
(review/co-production-v1) of experiments/2026-10-11-societal-persistence. Transition
and action laws are imported from the two frozen implementations, not rewritten.
Every derived trajectory is checked against the recorded primary outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments" / "2026-10-11-societal-persistence"
BASELINE = SOURCE / "coordinator" / "run-v1" / "results.json"
SHARED = SOURCE / "review" / "co-production-v1" / "results.json"
HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "relay.template.html"
HORIZON = 12
INF = 10 ** 6


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("renewal_model", SOURCE / "coordinator" / "renewal_model.py")
CO = load_module("co_production", SOURCE / "review" / "co_production.py")
TASKS = BASE.TASKS
START = tuple(BASE.START)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_law(budget, skill_age):
    def acts(state):
        return [tuple(a) for a in BASE.actions(state, budget)]

    def step(state, action, shock):
        return BASE.transition(state, action, shock, skill_age)

    def cost(action):
        return len(action)
    return acts, step, cost


def shared_law(budget):
    def to_mask(action):
        return tuple(int(t in action) for t in TASKS)

    def acts(state):
        return [tuple(TASKS[i] for i in range(3) if u[i]) for u in CO.choices(state, budget)]

    def step(state, action, shock):
        return CO.step(state, to_mask(action), shock)

    def cost(action):
        return CO.cost(to_mask(action))
    return acts, step, cost


def ranks(record):
    """Largest fixed-point iteration containing each safe state; kernel states get INF."""
    out = {}
    layers = record["fixed_point_layers"]
    for layer in layers:
        for s in layer["states"]:
            out[tuple(s)] = layer["iteration"]
    for s in record["infinite_kernel"]:
        out[tuple(s)] = INF
    return out


def trajectory(record, shocks, acts, step, cost):
    """Robust play: the controller maximises the guaranteed horizon, the shock minimises it.

    Inside the infinite kernel the controller follows the frozen policy witness.
    Ties between shocks go to the larger shock. Ties between actions keep the
    implementation's own action order.
    """
    rank = ranks(record)
    policy = {tuple(p["state"]): tuple(p["action"]) for p in record["infinite_policy"]}

    def r(s):
        return rank.get(s, -1)

    def worst(state, action):
        options = [(r(step(state, action, w)), -sum(w), w) for w in shocks]
        return min(options)

    state = START
    steps = []
    for t in range(HORIZON):
        if state in policy:
            action = policy[state]
        else:
            action = max(acts(state), key=lambda a: worst(state, a)[0])
        guaranteed, _, shock = worst(state, action)
        nxt = step(state, action, shock)
        steps.append({"t": t, "state": list(state), "action": list(action), "cost": cost(action),
                      "shock": list(shock), "next": list(nxt), "next_safe": nxt[0] > 0 and nxt[1] > 0,
                      "rank_before": None if r(state) == INF else r(state)})
        state = nxt
        if not steps[-1]["next_safe"]:
            break
    return steps


def world_summary(regime, budget, skill_age, support, record, possible, law):
    acts, step, cost = law
    steps = trajectory(record, BASE.SHOCKS[support], acts, step, cost)
    primary = record["primary"]
    infinite = primary["infinite_viable"]
    safe_transitions = sum(1 for s in steps if s["next_safe"])
    if infinite:
        assert safe_transitions == HORIZON, (regime, budget, support)
    else:
        assert safe_transitions == primary["maximum_safe_transitions_if_finite"], (regime, budget, support, steps)
    rank = ranks(record)
    trainings = [s["t"] for s in steps if "train" in s["action"]]
    for s in steps:
        assert s["cost"] <= budget
    return {"regime": regime, "budget": budget, "skill_age": skill_age, "shock_support": support,
            "infinite": infinite, "safe_transitions": None if infinite else safe_transitions,
            "robust_infinite_count": record["infinite_count"], "possible_infinite_count": possible["infinite_count"],
            "ranks": {f"{a}{b}{k}": (None if v == INF else v) for (a, b, k), v in sorted(rank.items())},
            "trainings": trainings, "steps": steps}


def build():
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    shared = json.loads(SHARED.read_text(encoding="utf-8"))
    worlds = []
    for w in base["worlds"]:
        regime = "fixed_skill" if w["skill_age"] == 0 else "separate"
        worlds.append(world_summary(regime, w["budget"], w["skill_age"], w["shock_support"],
                                    w["robust"], w["possible"], baseline_law(w["budget"], w["skill_age"])))
    for w in shared["worlds"]:
        assert w["skill_age"] == 1
        worlds.append(world_summary("shared", w["budget"], 1, w["shock_support"],
                                    w["robust"], w["possible"], shared_law(w["budget"])))
    assert len(worlds) == 48
    return {"status": "Derived presentation data. Invented finite model; no archaeological calibration.",
            "sources": {"baseline_results": {"path": str(BASELINE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(BASELINE)},
                        "shared_operation_results": {"path": str(SHARED.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(SHARED)},
                        "derivation_code_sha256": sha256(Path(__file__))},
            "start": list(START), "horizon": HORIZON,
            "play_rule": "Robust quantifier. Controller maximises guaranteed horizon (frozen policy inside the kernel); "
                         "the supported shock minimises it, ties to the larger shock.",
            "worlds": worlds}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Endpoint exists; use a fresh output path.")
    data = build()
    args.out.mkdir(parents=True)
    payload = json.dumps(data, separators=(",", ":"))
    (args.out / "relay-data.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    if TEMPLATE.exists():
        page = TEMPLATE.read_text(encoding="utf-8").replace("/*__RELAY_DATA__*/null", payload)
        (args.out / "index.html").write_text(page, encoding="utf-8")
    print(json.dumps({"worlds": len(data["worlds"]),
                      "infinite": sum(w["infinite"] for w in data["worlds"])}))


if __name__ == "__main__":
    main()
