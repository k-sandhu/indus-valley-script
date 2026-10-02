"""Sequential physical observations with positive-set and exact LP certificates."""

from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
import argparse
import copy
import json
import random
import shutil
import time

import numpy as np
import scipy
from scipy.optimize import linprog


N = 6
CONDITIONS = ("complete_exact", "incomplete", "valid_intervals", "undercovered_counts", "ownership")
POLICIES = ("information_rank", "random", "cost_availability")
PUBLIC_FIELDS = {"id", "kind", "code", "visible_children", "complete_record", "available", "cost", "declared_radius", "object_id"}


def dot(row, vector):
    return sum(F(a) * F(v) for a, v in zip(row, vector))


def fractionize(values, denominator=1000000):
    return [F(float(v)).limit_denominator(denominator) for v in values]


def rank(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    if not rows:
        return 0
    cursor = 0
    for column in range(len(rows[0])):
        target = next((i for i in range(cursor, len(rows)) if rows[i][column]), None)
        if target is None:
            continue
        rows[cursor], rows[target] = rows[target], rows[cursor]
        value = rows[cursor][column]
        rows[cursor] = [x / value for x in rows[cursor]]
        for i in range(cursor + 1, len(rows)):
            if rows[i][column]:
                multiple = rows[i][column]
                rows[i] = [x - multiple * y for x, y in zip(rows[i], rows[cursor])]
        cursor += 1
        if cursor == len(rows):
            break
    return cursor


def row_for(parent, children):
    row = [0] * N
    row[parent] = 1
    for code in children:
        row[code] -= 1
    return row


class CertifiedLP:
    def __init__(self):
        self.calls = 0
        self.certificates = 0
        self.digest = sha256()

    def _verify_optimum(self, c, eq, rhs, ub, limits, result):
        for denominator in (1000000, 1000000000):
            x = fractionize(result.x, denominator)
            lam = fractionize(result.ineqlin.marginals, denominator)
            mu = fractionize(result.eqlin.marginals, denominator)
            lower = fractionize(result.lower.marginals, denominator)
            valid = (
                all(v >= 0 for v in x)
                and all(dot(row, x) == F(b) for row, b in zip(eq, rhs))
                and all(dot(row, x) <= F(b) for row, b in zip(ub, limits))
                and all(v <= 0 for v in lam)
                and all(v >= 0 for v in lower)
                and all(F(c[j]) == sum(F(row[j]) * v for row, v in zip(ub, lam))
                        + sum(F(row[j]) * v for row, v in zip(eq, mu)) + lower[j]
                        for j in range(len(c)))
                and dot(c, x) == dot(limits, lam) + dot(rhs, mu)
            )
            if valid:
                certificate = {
                    "objective": [str(F(v)) for v in c],
                    "eq": [[str(F(v)) for v in row] for row in eq],
                    "rhs": [str(F(v)) for v in rhs],
                    "ub": [[str(F(v)) for v in row] for row in ub],
                    "limits": [str(F(v)) for v in limits],
                    "primal": [str(v) for v in x],
                    "inequality_dual": [str(v) for v in lam],
                    "equality_dual": [str(v) for v in mu],
                    "nonnegative_bound_dual": [str(v) for v in lower],
                    "objective_value": str(dot(c, x)),
                }
                self.certificates += 1
                self.digest.update(json.dumps(certificate, sort_keys=True).encode())
                return {"status": "optimal", "value": dot(c, x), "point": x, "certificate": certificate}
        raise ArithmeticError("Numerical optimum failed exact primal/dual verification")

    def minimum(self, c, eq, rhs, ub, limits, recurse=True):
        self.calls += 1
        result = linprog(
            list(map(float, c)),
            A_eq=np.asarray(eq, dtype=float) if eq else None,
            b_eq=np.asarray(rhs, dtype=float) if eq else None,
            A_ub=np.asarray(ub, dtype=float) if ub else None,
            b_ub=np.asarray(limits, dtype=float) if ub else None,
            bounds=[(0, None)] * len(c), method="highs-ds",
        )
        if result.status == 0:
            return self._verify_optimum(c, eq, rhs, ub, limits, result)
        if result.status == 2 and recurse:
            relaxed_rows = [list(row) + [-1] for row in ub]
            relaxed_limits = list(limits)
            for row, b in zip(eq, rhs):
                relaxed_rows.extend([list(row) + [-1], [-F(v) for v in row] + [-1]])
                relaxed_limits.extend([b, -F(b)])
            phase = self.minimum([0] * len(c) + [1], [], [], relaxed_rows, relaxed_limits, recurse=False)
            if phase["status"] != "optimal" or phase["value"] <= 0:
                raise ArithmeticError("Infeasibility did not receive a positive exact phase-one certificate")
            return {"status": "infeasible", "phase_one_certificate": phase["certificate"]}
        if result.status == 3 and recurse:
            ray = self.minimum([0] * len(c), eq, [0] * len(eq),
                               list(ub) + [list(c)], [0] * len(ub) + [-1], recurse=False)
            if ray["status"] != "optimal":
                raise ArithmeticError("Unboundedness did not receive a feasible recession certificate")
            assert dot(c, ray["point"]) <= -1
            return {"status": "unbounded", "ray": ray["point"], "ray_certificate": ray["certificate"]}
        raise ArithmeticError(f"Uncertified LP status {result.status}: {result.message}")


def model_for(observations):
    eq, rhs, ub, limits, membership_eq = [], [], [], [], []
    absolute = False
    for observation in observations:
        if observation["kind"] == "membership":
            row = row_for(observation["code"], observation["children"])
            if observation["complete"]:
                eq.append(row); rhs.append(0); membership_eq.append(row)
            else:
                ub.append([-x for x in row]); limits.append(0)
        else:
            absolute = True
            row = [0] * N; row[observation["code"]] = 1
            if observation["lower"] == observation["upper"]:
                eq.append(row); rhs.append(observation["lower"])
            else:
                ub.extend([row, [-x for x in row]])
                limits.extend([observation["upper"], -observation["lower"]])
    real_eq = list(eq)
    if not absolute:
        eq.append([1] * N); rhs.append(1)
    return {"eq": eq, "rhs": rhs, "ub": ub, "limits": limits, "absolute": absolute, "real_eq": real_eq,
            "membership_rank": rank(membership_eq), "observed_coefficient_rank": rank(real_eq)}


def strict_positive(lp, model):
    eq = [list(row) + [0] for row in model["eq"]]
    ub = [list(row) + [0] for row in model["ub"]]
    limits = list(model["limits"])
    for j in range(N):
        row = [0] * (N + 1); row[j] = -1; row[-1] = 1
        ub.append(row); limits.append(0)
    ub.append([0] * N + [1]); limits.append(1)
    result = lp.minimum([0] * N + [-1], eq, model["rhs"], ub, limits)
    if result["status"] == "infeasible":
        return False, None, result["phase_one_certificate"]
    positive = result["value"] < 0
    return positive, result["point"][:N] if positive else None, result["certificate"]


def bounds_for(lp, model, objective):
    lower = lp.minimum(objective, model["eq"], model["rhs"], model["ub"], model["limits"])
    upper = lp.minimum([-F(v) for v in objective], model["eq"], model["rhs"], model["ub"], model["limits"])
    assert lower["status"] in ("optimal", "unbounded") and upper["status"] in ("optimal", "unbounded")
    return lower, upper


def analyze(lp, observations):
    model = model_for(observations)
    positive, point, certificate = strict_positive(lp, model)
    state = {
        "strict_positive_feasible": positive,
        "absolute_units_observed": model["absolute"],
        "membership_equality_rank": model["membership_rank"],
        "observed_coefficient_rank": model["observed_coefficient_rank"],
        "strict_positive_certificate": certificate,
        "coordinate_ranges": [],
        "absolute_unique": False,
        "relative_unique": False,
        "positive_point": [str(v) for v in point] if point else None,
        "range_certificates": [],
    }
    if not positive:
        state["classification"] = "positive_model_rejected"
        return state, model
    coordinates = []
    for j in range(N):
        objective = [0] * N; objective[j] = 1
        low, high = bounds_for(lp, model, objective)
        lower = low["value"] if low["status"] == "optimal" else None
        upper = -high["value"] if high["status"] == "optimal" else None
        coordinates.append((lower, upper))
        state["coordinate_ranges"].append([str(lower) if lower is not None else "-infinity",
                                            str(upper) if upper is not None else "infinity"])
        state["range_certificates"].append({"lower": low.get("certificate", low.get("ray_certificate")),
                                            "upper": high.get("certificate", high.get("ray_certificate"))})
    coordinate_unique = all(low is not None and high is not None and low == high for low, high in coordinates)
    absolute_unique = model["absolute"] and coordinate_unique
    relative_unique = coordinate_unique or model["membership_rank"] == N - 1
    state["relative_tests"] = []
    if model["absolute"] and not relative_unique:
        relative_unique = True
        for j in range(1, N):
            objective = [F(0)] * N; objective[j] = point[0]; objective[0] = -point[j]
            low, high = bounds_for(lp, model, objective)
            state["relative_tests"].append({"code": j, "lower": low.get("certificate", low.get("ray_certificate")),
                                            "upper": high.get("certificate", high.get("ray_certificate"))})
            if low["status"] != "optimal" or high["status"] != "optimal" or low["value"] != 0 or high["value"] != 0:
                relative_unique = False
                break
    state["relative_unique"] = bool(relative_unique)
    state["absolute_unique"] = bool(absolute_unique)
    state["absolute_values"] = [str(low) for low, _ in coordinates] if absolute_unique else None
    state["relative_values"] = [str(v / sum(point)) for v in point] if relative_unique else None
    if absolute_unique:
        state["classification"] = "absolute_unique"
    elif relative_unique:
        state["classification"] = "relative_unique_scale_interval" if model["absolute"] else "relative_unique_scale_unfixed"
    else:
        state["classification"] = "positive_ambiguity"
    return state, model


def possible_rows(action):
    visible = Counter(action["visible_children"])
    sizes = (2, 3) if action["complete_record"] else (1, 2)
    result = []
    for size in sizes:
        for children in combinations_with_replacement(range(N), size):
            counts = Counter(children)
            if all(counts[k] >= v for k, v in visible.items()):
                # A parent among its own children cannot satisfy a positive
                # quantity equality; retain inequalities for incomplete groups.
                if action["complete_record"] and action["code"] in children:
                    continue
                result.append(row_for(action["code"], children))
    return result


def membership_score(lp, model, state, action, cache):
    signature = (action["code"], tuple(action["visible_children"]), action["complete_record"])
    if signature in cache:
        return cache[signature]
    if state["relative_unique"]:
        vector = [F(v) for v in state["relative_values"]]
        menu = possible_rows(action)
        compatible = sum(dot(row, vector) == 0 if action["complete_record"] else dot(row, vector) >= 0
                         for row in menu)
        result = {"potential": F(0), "compatible_outcomes": compatible, "tested_outcomes": len(menu),
                  "uniform_compatible_outcome_prior": True, "identified_ratio_substitution": True}
        cache[signature] = result
        return result
    scores = []; compatible = 0; tested = 0
    for row in possible_rows(action):
        tested += 1
        low, high = bounds_for(lp, model, row)
        lower = low["value"] if low["status"] == "optimal" else None
        upper = -high["value"] if high["status"] == "optimal" else None
        if action["complete_record"]:
            if lower is not None and lower > 0 or upper is not None and upper < 0:
                continue
            if lower == 0 and upper == 0:
                compatible += 1; scores.append(F(0)); continue
            probe = {**model, "eq": list(model["eq"]) + [row], "rhs": list(model["rhs"]) + [0]}
            feasible, _, _ = strict_positive(lp, probe)
            if feasible:
                compatible += 1
                scores.append(F(int(rank(model["eq"] + [row]) > rank(model["eq"]))))
        else:
            if upper is not None and upper < 0:
                continue
            probe = {**model, "ub": list(model["ub"]) + [[-x for x in row]], "limits": list(model["limits"]) + [0]}
            feasible, _, _ = strict_positive(lp, probe)
            if feasible:
                compatible += 1
                scores.append(F(1, 4) if lower is None or lower < 0 else F(0))
    score = sum(scores, F(0)) / len(scores) if scores else F(0)
    result = {"potential": score, "compatible_outcomes": compatible, "tested_outcomes": tested,
              "uniform_compatible_outcome_prior": True}
    cache[signature] = result
    return result


def count_score(model, state, action):
    code = action["code"]
    row = [0] * N; row[code] = 1
    radius = action["declared_radius"]
    if radius == 0:
        return F(int(rank(model["real_eq"] + [row]) > rank(model["real_eq"])))
    if not model["absolute"]:
        if state["relative_unique"]:
            values = [F(v) for v in state["relative_values"]]
            return values[code] / max(values)
        return F(1)
    lower, upper = state["coordinate_ranges"][code]
    if upper == "infinity":
        return F(1)
    width = F(upper) - F(lower)
    return max(F(0), F(1) - F(2 * radius) / width) if width else F(0)


def select_action(policy, actions, acquired, remaining, observations, state, model, lp, rng):
    assert all(set(action).issubset(PUBLIC_FIELDS) for action in actions)
    choices = [a for a in actions if a["available"] and a["id"] not in acquired and a["cost"] <= remaining]
    if not choices:
        return None, {"reason": "no_affordable_available_action"}
    cost_order = lambda a: (a["cost"], not a["complete_record"], a["id"])
    public_hash = sha256(json.dumps({"actions": actions, "acquired": sorted(acquired), "remaining": remaining,
                                   "observations": observations}, sort_keys=True).encode()).hexdigest()
    if policy == "random":
        chosen = choices[rng.randrange(len(choices))]
        return chosen, {"public_input_hash": public_hash, "eligible_actions": len(choices)}
    if policy == "cost_availability" or not state["strict_positive_feasible"]:
        chosen = min(choices, key=cost_order)
        return chosen, {"public_input_hash": public_hash, "fallback_after_positive_rejection": policy == "information_rank"}
    cache, scoring = {}, []
    for action in choices:
        if action["kind"] == "count":
            potential = count_score(model, state, action)
            details = {"potential": str(potential), "declared_radius": action["declared_radius"]}
        else:
            result = membership_score(lp, model, state, action, cache)
            potential = result["potential"]
            details = {k: str(v) if isinstance(v, F) else v for k, v in result.items()}
        scoring.append({"action_id": action["id"], "score": str(potential / action["cost"]), **details})
    maximum = max(F(s["score"]) for s in scoring)
    if maximum == 0:
        chosen = min(choices, key=cost_order)
        fallback = True
    else:
        best = {s["action_id"] for s in scoring if F(s["score"]) == maximum}
        chosen = min((a for a in choices if a["id"] in best), key=lambda a: a["id"])
        fallback = False
    return chosen, {"public_input_hash": public_hash, "scores": scoring, "zero_score_cost_fallback": fallback}


def make_world(seed, condition):
    rng = random.Random(seed)
    unit, a = rng.choice((1, 2, 3)), rng.choice((2, 3))
    semantic = [unit * v for v in (1, a, a + 1, 2 * a, 3 * a, 4 * a)]
    order = list(range(N)); rng.shuffle(order)
    values = [0] * N
    for j, code in enumerate(order): values[code] = semantic[j]
    compositions = []
    for size in (2, 3):
        for children in combinations_with_replacement(range(N), size):
            total = sum(values[j] for j in children)
            if total in values: compositions.append((values.index(total), list(children)))
    objects, relations = [], []
    for i in range(30):
        parent, children = rng.choice(compositions)
        identifier = f"W{seed}-R{i:02d}"
        parent_id = identifier + "-P"
        child_ids = [identifier + f"-C{j}" for j in range(len(children))]
        relation = {"parent": parent_id, "children_ids": child_ids, "code": parent, "children": children}
        relations.append(relation)
        objects.append({"id": parent_id, "quantity_code": parent, "quantity": values[parent]})
        objects.extend({"id": identifier, "quantity_code": code, "quantity": values[code]}
                       for identifier, code in zip(child_ids, children))
    frequencies = Counter(obj["quantity_code"] for obj in objects)
    target = max(frequencies.values())
    for code in range(N):
        for i in range(target - frequencies[code]):
            objects.append({"id": f"W{seed}-U{code}-{i}", "quantity_code": code, "quantity": values[code]})
    labels = [obj["quantity_code"] for obj in objects]
    if condition == "ownership": rng.shuffle(labels)
    label_by_id = {obj["id"]: code for obj, code in zip(objects, labels)}
    object_by_id = {obj["id"]: obj for obj in objects}
    assert len(object_by_id) == len(objects)
    assert len(set(Counter(label_by_id.values()).values())) == 1
    def observed(relation):
        return {"kind": "membership", "code": label_by_id[relation["parent"]],
                "children": [label_by_id[i] for i in relation["children_ids"]], "complete": True}
    initial = [observed(r) for r in relations[:2]]
    actions, responses = [], {}
    for i, relation in enumerate(relations[2:20]):
        complete = condition != "incomplete" or rng.random() >= .4
        response = observed(relation)
        visible = []
        if not complete:
            removed = rng.randrange(len(response["children"]))
            response["children"] = [v for j, v in enumerate(response["children"]) if j != removed]
            response["complete"] = False
            visible = [response["children"][0]]
            initial.append({"kind": "membership", "code": response["code"], "children": visible, "complete": False})
        action = {"id": f"inspect-{i:02d}", "kind": "membership", "code": response["code"],
                  "visible_children": visible, "complete_record": complete, "available": rng.random() < .75,
                  "cost": rng.choice((1, 2, 3, 4)), "declared_radius": None, "object_id": relation["parent"]}
        actions.append(action); responses[action["id"]] = response
    for code in range(N):
        selected = next(obj for obj in objects if label_by_id[obj["id"]] == code)
        actual = selected["quantity"]
        if condition == "valid_intervals": error, radius = rng.choice((-1, 0, 1)), 1
        elif condition == "undercovered_counts": error, radius = rng.choice((-2, -1, 1, 2)), 0
        else: error, radius = 0, 0
        measured = max(0, actual + error)
        response = {"kind": "count", "code": code, "lower": max(0, measured - radius), "upper": measured + radius,
                    "counted_object_id": selected["id"]}
        action = {"id": f"count-{code}", "kind": "count", "code": code, "visible_children": [],
                  "complete_record": True, "available": rng.random() < .5,
                  "cost": rng.choice((5, 6, 8)), "declared_radius": radius, "object_id": selected["id"]}
        actions.append(action); responses[action["id"]] = response
        if condition == "valid_intervals": assert response["lower"] <= actual <= response["upper"]
    heldout_relations = [observed(r) for r in relations[20:]]
    heldout_counts = []
    for i in range(2):
        original_code = rng.randrange(N)
        badge = rng.randrange(N) if condition == "ownership" else original_code
        heldout_counts.append({"object_id": f"W{seed}-HC{i}", "code": badge, "quantity": values[original_code]})
    return {"seed": seed, "condition": condition, "concealed_values": values, "concealed_unit": unit,
            "concealed_parameter": a, "objects": objects, "observed_label_by_object": label_by_id,
            "initial_observations": initial, "public_actions": actions, "oracle_responses": responses,
            "withheld_relations": heldout_relations, "withheld_counts": heldout_counts}


def evaluate(state, observations, world):
    result = {"classification": state["classification"], "relative_correct": False, "absolute_correct": False,
              "wrong_relative_unique": False, "wrong_absolute_unique": False,
              "withheld_relations_pass": None, "withheld_counts_pass": None}
    if not state["strict_positive_feasible"]:
        result["truth_retained"] = False if world["condition"] != "ownership" else None
        return result
    true_values = list(map(F, world["concealed_values"]))
    retained = True
    if world["condition"] != "ownership":
        for observation in observations:
            if observation["kind"] == "membership":
                value = dot(row_for(observation["code"], observation["children"]), true_values)
                retained &= value == 0 if observation["complete"] else value >= 0
            else:
                retained &= observation["lower"] <= true_values[observation["code"]] <= observation["upper"]
    result["truth_retained"] = bool(retained) if world["condition"] != "ownership" else None
    if state["relative_unique"]:
        vector = [F(v) for v in state["relative_values"]]
        relation_pass = all(dot(row_for(r["code"], r["children"]), vector) == 0 for r in world["withheld_relations"])
        result["withheld_relations_pass"] = relation_pass
        correct = vector == [v / sum(true_values) for v in true_values] if world["condition"] != "ownership" else relation_pass
        result["relative_correct"] = bool(correct)
        result["wrong_relative_unique"] = not correct
    if state["absolute_unique"]:
        vector = [F(v) for v in state["absolute_values"]]
        count_pass = all(vector[c["code"]] == c["quantity"] for c in world["withheld_counts"])
        result["withheld_counts_pass"] = count_pass
        correct = vector == true_values if world["condition"] != "ownership" else count_pass and result["withheld_relations_pass"]
        result["absolute_correct"] = bool(correct)
        result["wrong_absolute_unique"] = not correct
    return result


def run_policy(world, policy, lp):
    actions = copy.deepcopy(world["public_actions"])
    assert all(set(action) <= PUBLIC_FIELDS for action in actions)
    observations = copy.deepcopy(world["initial_observations"])
    acquired, spent, trace = set(), 0, []
    rng = random.Random(world["seed"] + 90000 + POLICIES.index(policy))
    state, model = analyze(lp, observations)
    initial_evaluation = evaluate(state, observations, world)
    first_relative = 0 if initial_evaluation["relative_correct"] else None
    first_absolute = 0 if initial_evaluation["absolute_correct"] else None
    boundary_checks = 0
    while True:
        rng_before = rng.getstate()
        action, selection = select_action(policy, actions, acquired, 24 - spent, observations, state, model, lp, rng)
        # Oracle and hidden answer never appear in this call's signature. This
        # replay uses only public data and the same policy randomness.
        replay_rng = random.Random(); replay_rng.setstate(rng_before)
        if policy != "information_rank":
            replay, _ = select_action(policy, copy.deepcopy(actions), set(acquired), 24 - spent,
                                      copy.deepcopy(observations), copy.deepcopy(state), model, lp, replay_rng)
            assert (replay["id"] if replay else None) == (action["id"] if action else None)
            boundary_checks += 1
        if action is None:
            break
        response = copy.deepcopy(world["oracle_responses"][action["id"]])
        spent += action["cost"]; acquired.add(action["id"])
        assert spent <= 24
        observations.append(response)
        state, model = analyze(lp, observations)
        evaluation = evaluate(state, observations, world)
        if first_relative is None and evaluation["relative_correct"]: first_relative = spent
        if first_absolute is None and evaluation["absolute_correct"]: first_absolute = spent
        trace.append({"spent": spent, "action": action, "selection": selection,
                      "response_after_selection": response, "state": state, "evaluation_after_selection": evaluation})
    return {"seed": world["seed"], "condition": world["condition"], "policy": policy,
            "initial_state": analyze(lp, world["initial_observations"])[0], "initial_evaluation": initial_evaluation,
            "spent": spent, "actions_acquired": len(acquired), "first_correct_relative_cost": first_relative,
            "first_correct_absolute_cost": first_absolute,
            "final_state": state, "final_evaluation": evaluate(state, observations, world),
            "trace": trace, "public_boundary_replay_checks": boundary_checks,
            "policy_signature_excludes_oracle_and_answer": True}


def summarize(records):
    result = []
    for condition in CONDITIONS:
        for policy in POLICIES:
            rows = [r for r in records if r["condition"] == condition and r["policy"] == policy]
            relative = [r["first_correct_relative_cost"] for r in rows if r["first_correct_relative_cost"] is not None]
            absolute = [r["first_correct_absolute_cost"] for r in rows if r["first_correct_absolute_cost"] is not None]
            result.append({"condition": condition, "policy": policy, "worlds": len(rows),
                           "final_classifications": dict(Counter(r["final_state"]["classification"] for r in rows)),
                           "correct_relative_worlds": sum(r["final_evaluation"]["relative_correct"] for r in rows),
                           "correct_absolute_worlds": sum(r["final_evaluation"]["absolute_correct"] for r in rows),
                           "ever_wrong_relative_unique_worlds": sum(any(t["evaluation_after_selection"]["wrong_relative_unique"] for t in r["trace"]) for r in rows),
                           "ever_wrong_absolute_unique_worlds": sum(any(t["evaluation_after_selection"]["wrong_absolute_unique"] for t in r["trace"]) for r in rows),
                           "correct_relative_cost_mean_given_identified": float(np.mean(relative)) if relative else None,
                           "correct_absolute_cost_mean_given_identified": float(np.mean(absolute)) if absolute else None,
                           "mean_paid_cost": float(np.mean([r["spent"] for r in rows])) if rows else None})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--worlds", type=int, default=24)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--condition", choices=CONDITIONS)
    args = parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    source = Path(__file__).resolve()
    protocol = Path("experiments/2026-10-02-six-hour/physical-acquisition/PROTOCOL.md")
    shutil.copy2(source, args.output / "code_snapshot.py")
    shutil.copy2(protocol, args.output / "protocol_snapshot.md")
    repair = Path("experiments/2026-10-02-six-hour/physical-acquisition/PILOT_REPAIR_01.md")
    shutil.copy2(repair, args.output / "pilot_repair_snapshot.md")
    lp = CertifiedLP(); records, worlds = [], []
    start = time.perf_counter()
    conditions = (args.condition,) if args.condition else CONDITIONS
    try:
        for condition in conditions:
            for i in range(args.worlds):
                seed = (910000 if args.pilot else 2026100200) + CONDITIONS.index(condition) * 1000 + i
                world = make_world(seed, condition); worlds.append(world)
                for policy in POLICIES:
                    result = run_policy(world, policy, lp); records.append(result)
                    name = f"{condition}-{seed}-{policy}.json"
                    (args.output / name).write_text(json.dumps(result, indent=2) + "\n")
                    print(json.dumps({"condition": condition, "seed": seed, "policy": policy,
                                      "classification": result["final_state"]["classification"],
                                      "lp_calls": lp.calls}), flush=True)
        summary = {"status": "synthetic-completed", "pilot": args.pilot,
                   "generated_utc": datetime.now(timezone.utc).isoformat(),
                   "worlds_per_condition": args.worlds, "conditions": list(conditions),
                   "code_sha256": sha256(source.read_bytes()).hexdigest(),
                   "protocol_sha256": sha256(protocol.read_bytes()).hexdigest(),
                   "pilot_repair_sha256": sha256(repair.read_bytes()).hexdigest(),
                   "numpy_version": np.__version__, "scipy_version": scipy.__version__,
                   "certified_lp_calls": lp.calls, "exact_optimality_certificates": lp.certificates,
                   "certificate_digest": lp.digest.hexdigest(), "seconds": time.perf_counter() - start,
                   "summary": summarize(records)}
        (args.output / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
        (args.output / "worlds.json").write_text(json.dumps(worlds, indent=2) + "\n")
    except Exception as error:
        failure = {"status": "failed-execution-preserved", "error_type": type(error).__name__, "error": str(error),
                   "completed_policy_records": len(records), "lp_calls": lp.calls,
                   "code_sha256": sha256(source.read_bytes()).hexdigest(),
                   "generated_utc": datetime.now(timezone.utc).isoformat()}
        (args.output / "failure.json").write_text(json.dumps(failure, indent=2) + "\n")
        (args.output / "worlds-before-failure.json").write_text(json.dumps(worlds, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
