"""Independent subset/RREF, physical-inventory and scale verification."""
from __future__ import annotations
import ast
import collections
from datetime import datetime, timezone
from fractions import Fraction
import itertools
import json
from math import gcd, lcm
from pathlib import Path
from khipu_control import exact_decoder
from khipu_conservation import BASE, ENDPOINT, digest, save


def scalar(row, vector):
    answer = Fraction(0)
    for i in range(3):
        answer += Fraction(row[i])*Fraction(vector[i])
    return answer


def normalize(row):
    rational = list(map(Fraction, row))
    multiplier = lcm(*(x.denominator for x in rational))
    integer = [int(x*multiplier) for x in rational]
    divisor = gcd(gcd(abs(integer[0]), abs(integer[1])), abs(integer[2]))
    if not divisor:
        return (0, 0, 0)
    integer = [x//divisor for x in integer]
    if next(x for x in integer if x) < 0:
        integer = [-x for x in integer]
    return tuple(integer)


def affine_parameter(fit):
    free = next(i for i in range(3) if i not in fit["pivots"])
    rows = [list(map(Fraction, row)) for row in fit["rref"]]
    base, slope = [Fraction(0)]*3, [Fraction(0)]*3
    slope[free] = Fraction(1)
    for row, pivot in zip(rows, fit["pivots"]):
        base[pivot] = row[3]
        slope[pivot] = -row[free]
    return base, slope


def bounds(base, slope, aggregate=None):
    lower, upper = [], []
    conditions = [(a, b, False) for a, b in zip(base, slope)]
    if aggregate is not None:
        conditions.append((scalar(aggregate, base), scalar(aggregate, slope), True))
    for constant, coefficient, closed in conditions:
        if coefficient > 0:
            lower.append((-constant/coefficient, closed))
        elif coefficient < 0:
            upper.append((-constant/coefficient, closed))
        elif constant < 0 or constant == 0 and not closed:
            return None
    lo = max(value for value, _ in lower) if lower else None
    hi = min(value for value, _ in upper) if upper else None
    lo_closed = all(closed for value, closed in lower if value == lo) if lo is not None else False
    hi_closed = all(closed for value, closed in upper if value == hi) if hi is not None else False
    if lo is not None and hi is not None and (lo > hi or lo == hi and not (lo_closed and hi_closed)):
        return None
    return lo, hi, lo_closed, hi_closed


def plane_witnesses(aggregate):
    a, b, c = map(Fraction, aggregate)
    if max(b, c) > 0:
        index = 1 if b >= c else 2
        positive = b if index == 1 else c
        other = c if index == 1 else b
        value = max(Fraction(1), Fraction(-a-other, positive)+1)
        first, second = [Fraction(1)]*3, [Fraction(1)]*3
        first[index] = value; second[index] = value+1
        return [first, second]
    if a > 0:
        epsilon = min(Fraction(1), a/(3*(abs(b)+abs(c)+1)))
        return [[Fraction(1), epsilon, epsilon], [Fraction(1), epsilon/2, epsilon]]
    if a == 0 and b == 0 and c == 0:
        return [[Fraction(1)]*3, [Fraction(1), Fraction(2), Fraction(3)]]
    return None


def classification(rows, aggregate=None, kind=None):
    fit = exact_decoder(rows+([aggregate] if kind == "equality" else []), [1, 0, 0])
    if fit["status"] == "no_positive_solution":
        return {"status": "none", "witnesses": []}
    if fit["status"] == "unique_positive":
        vector = list(map(Fraction, fit["witnesses"][0]))
        if kind == "inequality" and scalar(aggregate, vector) < 0:
            return {"status": "none", "witnesses": []}
        return {"status": "point", "point": tuple(vector), "witnesses": [vector]}
    if fit["rank_anchored"] == 1:
        witnesses = plane_witnesses(aggregate) if kind == "inequality" else [[Fraction(1)]*3, [Fraction(1), Fraction(2), Fraction(3)]]
        if witnesses is None:
            return {"status": "none", "witnesses": []}
        return {"status": "plane", "witnesses": witnesses}
    assert fit["rank_anchored"] == 2
    base, slope = affine_parameter(fit)
    interval = bounds(base, slope, aggregate if kind == "inequality" else None)
    if interval is None:
        return {"status": "none", "witnesses": []}
    lo, hi, low_closed, high_closed = interval
    if lo is not None and hi is not None and lo == hi:
        vector = [a+b*lo for a, b in zip(base, slope)]
        return {"status": "point", "point": tuple(vector), "witnesses": [vector]}
    if lo is None and hi is None:
        choices = [Fraction(0), Fraction(1)]
    elif hi is None:
        choices = [lo+1, lo+2]
    elif lo is None:
        choices = [hi-1, hi-2]
    else:
        choices = [(2*lo+hi)/3, (lo+2*hi)/3]
    witnesses = [[a+b*t for a, b in zip(base, slope)] for t in choices]
    line = None
    for saved in fit["rref"]:
        row = list(map(Fraction, saved))
        if row[0] == 0 and (row[1] or row[2]):
            line = normalize([-row[3], row[1], row[2]])
            break
    assert line is not None
    return {"status": "line", "line": line, "witnesses": witnesses}


def subset_cache(rows, aggregate, kind):
    baseline, collective = [], []
    witnesses = 0
    for mask in range(1 << len(rows)):
        selected = [row for i, row in enumerate(rows) if mask & (1 << i)]
        for target, constraint, relation_kind in ((baseline, None, None), (collective, aggregate, kind)):
            fit = classification(selected, constraint, relation_kind)
            for vector in fit["witnesses"]:
                assert vector[0] == 1 and all(x > 0 for x in vector)
                assert all(scalar(row, vector) == 0 for row in selected)
                if relation_kind == "equality": assert scalar(constraint, vector) == 0
                if relation_kind == "inequality": assert scalar(constraint, vector) >= 0
                witnesses += 1
            target.append(fit)
    return baseline, collective, witnesses


def verify_union(rows, inferred, cached, aggregate=None, kind=None):
    possible = [(mask.bit_count(), fit) for mask, fit in enumerate(cached[:1 << len(rows)]) if fit["status"] != "none"]
    if not possible:
        assert inferred["status"] == "no_positive_solution" and inferred["best_support"] is None
        assert not inferred["optimal_points"] and not inferred["optimal_families"]
        return 0
    best = max(score for score, _ in possible)
    fit_sets = [fit for score, fit in possible if score == best]
    points = {fit["point"] for fit in fit_sets if fit["status"] == "point"}
    lines = {fit["line"] for fit in fit_sets if fit["status"] == "line"}
    plane = any(fit["status"] == "plane" for fit in fit_sets)
    assert inferred["best_support"] == best
    assert {tuple(map(Fraction, p["values"])) for p in inferred["optimal_points"]} == points
    assert {tuple(f["line"]) for f in inferred["optimal_families"] if "line" in f} == lines
    assert any("line" not in f for f in inferred["optimal_families"]) == plane
    unique = len(points) == 1 and not lines and not plane
    assert inferred["status"] == ("unique_positive" if unique else "ambiguous_positive")
    candidate_families = inferred.get("family_candidates", inferred.get("line_candidates", []))
    witness_count = 0
    for family in candidate_families:
        if not family.get("feasible", True): continue
        for field in ("witnesses", "boundary_witnesses"):
            for vector in family.get(field, []):
                assert all(Fraction(x) > 0 for x in vector) and Fraction(vector[0]) == 1
                if "line" in family: assert scalar(family["line"], vector) == 0
                if kind == "equality": assert scalar(aggregate, vector) == 0
                if kind == "inequality": assert scalar(aggregate, vector) >= 0
                witness_count += 1
        if "line" in family:
            base, slope = list(map(Fraction, family["base"])), list(map(Fraction, family["slope"]))
            interval = bounds(base, slope, aggregate if kind == "inequality" else None)
            assert interval is not None
            lo, hi, closed_low, closed_high = interval
            assert Fraction(family["lower"]) == lo
            assert family["upper"] is None if hi is None else Fraction(family["upper"]) == hi
            assert family.get("lower_closed", False) == closed_low
            assert family.get("upper_closed", False) == closed_high
    for candidate in inferred["point_candidates"]:
        vector = list(map(Fraction, candidate["values"]))
        expected = [i for i, row in enumerate(rows) if scalar(row, vector) == 0]
        assert candidate["support_indices"] == expected and candidate["support"] == len(expected)
        assert all(x > 0 for x in vector) and vector[0] == 1
        if kind == "equality": assert scalar(aggregate, vector) == 0
        if kind == "inequality": assert scalar(aggregate, vector) >= 0
        witness_count += 1
    for family in inferred["optimal_families"]:
        for vector in family["witnesses"]:
            assert sum(scalar(row, vector) == 0 for row in rows) == best
    return witness_count


def reconstruct(world, key):
    component = world["component"]
    assert "true_weights" not in component
    original = key["full_training_features"]
    observed = component["features"]
    assert len(original) == len(observed) == 32
    for i, row in enumerate(original):
        assert scalar(row, key["true_weights"]) == key["training_quantities"][i]
        assert observed[i] is None if i in key["omitted_pool_objects"] else observed[i] == row
    memberships = [[8+3*i+j for j in range(3)] for i in range(8)]
    for operation in key["corruption_operations"]:
        if "parents" in operation:
            left, right = operation["parents"]
            one, two = operation["children"]
            li, ri = memberships[left].index(one), memberships[right].index(two)
            memberships[left][li], memberships[right][ri] = two, one
        else:
            memberships[operation["parent"]].remove(operation["removed_child"])
    assert memberships == component["memberships"]
    rows = []
    for parent, members in enumerate(memberships):
        row = list(observed[parent])
        for child in members:
            assert observed[child] is not None
            for j in range(3): row[j] -= observed[child][j]
        rows.append(row)
    assert rows == component["equations"]
    collective = component["collective_observation"]
    assert collective["parents"] == list(range(8))
    assert collective["pool"] == [i for i in range(8, 32) if i not in key["omitted_pool_objects"]]
    aggregate = [0, 0, 0]
    for object_id in collective["parents"]:
        for j in range(3): aggregate[j] += observed[object_id][j]
    for object_id in collective["pool"]:
        assert observed[object_id] is not None
        for j in range(3): aggregate[j] -= observed[object_id][j]
    assert aggregate == collective["aggregate"]
    residual = sum(key["training_quantities"][i] for i in collective["parents"])-sum(key["training_quantities"][i] for i in collective["pool"])
    assert residual == key["actual_collective_residual"] == scalar(aggregate, key["true_weights"])
    if world["condition"] not in ("ownership", "missing_pool_declared", "missing_pool_misdeclared"):
        assert residual == 0
    if world["condition"] == "missing_pool_declared": assert residual >= 0
    visible_pool = sorted(itertools.chain.from_iterable(memberships))
    if visible_pool == collective["pool"]:
        assert [sum(row[j] for row in rows) for j in range(3)] == aggregate
    else:
        unassigned = set(collective["pool"])-set(visible_pool)
        difference = [sum(row[j] for row in rows)-sum(observed[i][j] for i in unassigned) for j in range(3)]
        assert difference == aggregate
    assert component["scale_observations"]["unmeasured"] is None
    measured = component["scale_observations"]["counted"]
    assert measured["features"] == [1, 0, 0]
    assert measured["count"] == key["unit_object_actual_count"] == key["scale"] == key["true_weights"][0]
    for field, quantities in (("heldout_features", "heldout_quantities"), ("count_features", "count_values")):
        assert all(scalar(f, key["true_weights"]) == q for f, q in zip(key[field], key[quantities]))
    held = []
    for parent, members in enumerate(key["heldout_memberships"]):
        row = list(key["heldout_features"][parent])
        for child in members:
            for j in range(3): row[j] -= key["heldout_features"][child][j]
        held.append(row)
    assert held == key["heldout_equations"]
    return rows, aggregate, collective["kind"]


def ray_counts(vector, features, counts):
    predicted = [scalar(f, vector) for f in features]
    if any(p == 0 and q != 0 for p, q in zip(predicted, counts)): return False, None
    active = [(p, q) for p, q in zip(predicted, counts) if p != 0]
    if not active: return True, "arbitrary_positive"
    first_p, first_q = active[0]
    if first_q/first_p <= 0: return False, None
    if any(first_q*p != q*first_p for p, q in active): return False, None
    return True, str(Fraction(first_q)/first_p)


def check_score(inferred, evaluated, key):
    assert evaluated["world_id"] == inferred["world_id"] and evaluated["prefix"] == inferred["prefix"]
    truth = [Fraction(x, key["true_weights"][0]) for x in key["true_weights"]]
    residual_checks = scale_witnesses = 0
    for model in ("baseline", "collective"):
        result = inferred[model]
        feasible_truth = model == "baseline" or (scalar(inferred["aggregate"], truth) == 0 if inferred["kind"] == "equality" else scalar(inferred["aggregate"], truth) >= 0)
        retained = False
        if feasible_truth:
            retained = any(list(map(Fraction, p["values"])) == truth for p in result["optimal_points"])
            retained |= any("line" not in f or scalar(f["line"], truth) == 0 for f in result["optimal_families"])
        assert evaluated["models"][model]["truth_retained"] == retained
        unique = result["status"] == "unique_positive"
        correct = unique and list(map(Fraction, result["optimal_points"][0]["values"])) == truth
        assert evaluated["models"][model]["status"] == result["status"]
        assert evaluated["models"][model]["best_support"] == result["best_support"]
        assert evaluated["models"][model]["unique_correct"] == correct
        assert evaluated["models"][model]["unique_wrong"] == (unique and not correct)
    for policy, output in evaluated["policies"].items():
        model = "baseline" if policy.startswith("baseline") else "collective"
        fit = inferred[model]
        n = inferred["prefix"]
        threshold = (3*n+3)//4 if policy.endswith("three_quarter") else (n+1)//2
        expected = "rejected_collective" if fit["status"] == "no_positive_solution" else "rejected_support" if fit["best_support"] < threshold else "abstained_ambiguity" if fit["status"] == "ambiguous_positive" else "accepted_unique_ray"
        assert output["status"] == expected and inferred["policies"][policy]["threshold"] == threshold
        assert output["absolute_identified_unmeasured"] is False
        if expected != "accepted_unique_ray":
            assert output["normalized_values"] is None and not output["correct_relative"] and not output["wrong_relative"]
            continue
        vector = list(map(Fraction, output["normalized_values"]))
        assert vector == list(map(Fraction, fit["optimal_points"][0]["values"]))
        correct = vector == truth
        assert output["correct_relative"] == correct and output["wrong_relative"] == (not correct)
        observed_scale = inferred["scale_observations"]["counted"]["count"]
        absolute = [observed_scale*x for x in vector]
        assert list(map(Fraction, output["absolute_values_counted"])) == absolute
        assert output["correct_absolute_counted"] == (absolute == key["true_weights"])
        assert output["wrong_absolute_counted"] == (absolute != key["true_weights"])
        relation = [scalar(row, vector) for row in key["heldout_equations"]]
        counted = [scalar(f, absolute)-q for f, q in zip(key["count_features"], key["count_values"])]
        assert list(map(Fraction, output["heldout_normalized_relation_residuals"])) == relation
        assert list(map(Fraction, output["heldout_counted_residuals"])) == counted
        assert output["passes_all_heldout_relations"] == (not any(relation))
        assert output["passes_all_counted_targets"] == (not any(counted))
        compatible, scale = ray_counts(vector, key["count_features"], key["count_values"])
        assert output["unmeasured_ray_count_check"] == {"compatible": compatible, "scale_witness": scale}
        expected_witnesses = [vector, [2*x for x in vector]]
        assert [list(map(Fraction, w)) for w in output["unmeasured_scale_witnesses"]] == expected_witnesses
        for witness in expected_witnesses:
            assert all(x > 0 for x in witness)
            assert sum(scalar(row, witness) == 0 for row in inferred["rows"]) == fit["best_support"]
            if model == "collective":
                r = scalar(inferred["aggregate"], witness)
                assert r == 0 if inferred["kind"] == "equality" else r >= 0
            scale_witnesses += 1
        residual_checks += len(relation)+len(counted)
    return residual_checks, scale_witnesses


def static_check():
    path = ENDPOINT/"khipu_conservation.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {x.name: x for x in tree.body if isinstance(x, ast.FunctionDef)}
    for name in ("collective_consensus", "clip_family", "halfspace_plane", "dot", "vector_at", "decision"):
        for part in ast.walk(functions[name]):
            if isinstance(part, ast.Attribute): assert part.attr not in {"read_text", "read_bytes", "open", "write_text", "write_bytes"}
            if isinstance(part, ast.Name):
                assert part.id not in {"true_weights", "scale", "seed", "condition", "ENDPOINT", "ROOT", "BASE"}
                if part.id == "key" and isinstance(part.ctx, ast.Load):
                    # The saved fitter's only `key` is a local coordinate tuple.
                    assert name == "collective_consensus"
                    assert any(isinstance(node, ast.comprehension) and isinstance(node.target, ast.Name)
                               and node.target.id == "key" for node in ast.walk(functions[name]))
    assert [a.arg for a in functions["collective_consensus"].args.args] == ["rows", "aggregate", "kind"]
    return True


def aggregate_check(evaluations, keys):
    aggregate = json.loads((ENDPOINT/"aggregate.json").read_text(encoding="utf-8"))
    buckets, optimal = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    histories = collections.defaultdict(list)
    for evaluated in evaluations:
        world_id, prefix = evaluated["world_id"], evaluated["prefix"]
        condition = world_id.split("-", 1)[1]
        for model, result in evaluated["models"].items():
            ob = optimal[(condition, model, prefix)]
            ob["records"] += 1; ob["truth_retained"] += result["truth_retained"]
            ob["unique_correct"] += result["unique_correct"]; ob["unique_wrong"] += result["unique_wrong"]
            ob["ambiguous"] += result["status"] == "ambiguous_positive"
            ob["infeasible"] += result["status"] == "no_positive_solution"
            ob["with_family"] += evaluated["_geometry"][model]["with_family"]
            ob["with_discrete_tie"] += evaluated["_geometry"][model]["with_discrete_tie"]
        for policy, output in evaluated["policies"].items():
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
            histories[(world_id, policy)].append((prefix, output))
    for row in aggregate["rows"]:
        expected = buckets[(row["condition"], row["policy"], row["prefix"])]
        actual = {k: v for k, v in row.items() if k not in ("condition", "policy", "prefix")}
        assert all(actual.get(k, 0) == expected.get(k, 0) for k in actual.keys() | expected.keys())
    for row in aggregate["optimal_sets"]:
        expected = optimal[(row["condition"], row["model"], row["prefix"])]
        for key, value in expected.items(): assert row[key] == value
    history_counts = collections.defaultdict(collections.Counter)
    first_correct, first_wrong = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for (world_id, policy), values in histories.items():
        assert [n for n, _ in values] == list(range(1, 9))
        condition = world_id.split("-", 1)[1]
        counter = history_counts[(condition, policy)]
        wrong = [n for n, v in values if v["wrong_relative"]]
        correct = [n for n, v in values if v["correct_relative"]]
        counter["worlds"] += 1; counter["ever_wrong"] += bool(wrong); counter["ever_correct"] += bool(correct)
        if wrong:
            first_wrong[(condition, policy)][str(min(wrong))] += 1
            last = values[-1][1]
            counter["wrong_then_correct"] += last["correct_relative"]; counter["wrong_then_wrong"] += last["wrong_relative"]
            counter["wrong_then_ambiguous"] += last["status"] == "abstained_ambiguity"
            counter["wrong_then_rejected"] += last["status"].startswith("rejected")
        if correct: first_correct[(condition, policy)][str(min(correct))] += 1
    for row in aggregate["trajectories"]:
        key = (row["condition"], row["policy"])
        expected = history_counts[key]
        actual = {k: v for k, v in row.items() if k not in ("condition", "policy", "first_correct_prefixes", "first_wrong_prefixes")}
        assert all(actual.get(k, 0) == expected.get(k, 0) for k in actual.keys() | expected.keys())
        assert row["first_correct_prefixes"] == dict(first_correct[key]) and row["first_wrong_prefixes"] == dict(first_wrong[key])
    assert aggregate["unmeasured_absolute_identifications"] == 0
    distributions, scales = collections.defaultdict(collections.Counter), collections.Counter()
    for world_id, key in keys.items():
        condition = world_id.split("-", 1)[1]
        distributions[condition]["zero_collective_residual"] += key["actual_collective_residual"] == 0
        distributions[condition]["negative_collective_residual"] += key["actual_collective_residual"] < 0
        distributions[condition]["positive_collective_residual"] += key["actual_collective_residual"] > 0
        distributions[condition]["actual_incomplete_pools"] += not key["actual_pool_complete"]
        if condition == "complete": scales[str(key["scale"])] += 1
    assert aggregate["collective_residual_distributions"] == {c: dict(v) for c, v in distributions.items()}
    assert aggregate["scale_distribution"] == dict(scales)
    return len(aggregate["rows"]), len(aggregate["optimal_sets"]), len(aggregate["trajectories"])


def main():
    generation = json.loads((ENDPOINT/"generation-manifest.json").read_text(encoding="utf-8"))
    for file in generation["files"]: assert digest(ENDPOINT/file["path"]) == file["sha256"]
    freeze = json.loads((BASE/"protocol-freeze.json").read_text(encoding="utf-8"))
    assert digest(ENDPOINT/"khipu_robust.py") == freeze["baseline_code_sha256"]
    im = json.loads((ENDPOINT/"inference-manifest.json").read_text(encoding="utf-8"))
    assert digest(ENDPOINT/"inferences.jsonl") == im["inferences_sha256"]
    worlds, keys = {}, {}
    for name, target, field in (("component-inputs.jsonl", worlds, None), ("evaluator-key.jsonl", keys, "key")):
        with (ENDPOINT/name).open(encoding="utf-8") as f:
            for line in f:
                x = json.loads(line); target[x["id"]] = x if field is None else x[field]
    assert worlds.keys() == keys.keys()
    reconstructed = {world_id: reconstruct(world, keys[world_id]) for world_id, world in worlds.items()}
    current = None
    subset_states = subset_witnesses = candidate_witnesses = residuals = scale_witnesses = records = 0
    evaluations = []
    with (ENDPOINT/"inferences.jsonl").open(encoding="utf-8") as inf, (ENDPOINT/"evaluated-prefixes.jsonl").open(encoding="utf-8") as evf:
        for iline, eline in itertools.zip_longest(inf, evf):
            assert iline and eline
            inferred, evaluated = json.loads(iline), json.loads(eline)
            world_id, prefix = inferred["world_id"], inferred["prefix"]
            rows, aggregate, kind = reconstructed[world_id]
            assert inferred["rows"] == rows[:prefix] and inferred["aggregate"] == aggregate and inferred["kind"] == kind
            if current != world_id:
                current = world_id
                baseline, collective, count = subset_cache(rows, aggregate, kind)
                subset_states += len(baseline)+len(collective); subset_witnesses += count
                if subset_states % (512*100) == 0: print(f"Independent subsets: {subset_states//512}/{len(worlds)} worlds.", flush=True)
            candidate_witnesses += verify_union(rows[:prefix], inferred["baseline"], baseline)
            candidate_witnesses += verify_union(rows[:prefix], inferred["collective"], collective, aggregate, kind)
            r, s = check_score(inferred, evaluated, keys[world_id]); residuals += r; scale_witnesses += s
            evaluated["_geometry"] = {m: {"with_family": bool(inferred[m]["optimal_families"]),
                                        "with_discrete_tie": len(inferred[m]["optimal_points"]) > 1} for m in ("baseline", "collective")}
            evaluations.append(evaluated); records += 1
    diagnostics = json.loads((ENDPOINT/"diagnostics.json").read_text(encoding="utf-8"))
    for name, case in diagnostics.items():
        _, collective, count = subset_cache(case["rows"], case["aggregate"], case["kind"])
        verify_union(case["rows"], case["inferred"], collective, case["aggregate"], case["kind"])
        subset_states += 2*len(collective); subset_witnesses += count
    assert diagnostics["plane_to_line"]["inferred"]["status"] == "ambiguous_positive"
    assert diagnostics["line_to_point"]["inferred"]["optimal_points"][0]["values"] == ["1", "10", "100"]
    closed = diagnostics["closed_boundary"]["inferred"]["optimal_families"][0]
    assert closed["lower"] == "2" and closed["lower_closed"]
    assert diagnostics["infeasible_collective"]["inferred"]["status"] == "no_positive_solution"
    assert diagnostics["infeasible_halfspace"]["inferred"]["status"] == "no_positive_solution"
    rows_checked, optimal_checked, histories_checked = aggregate_check(evaluations, keys)
    acquisition = json.loads((BASE/"source-acquisition.json").read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[2]
    assert digest(root/acquisition["source"]["local_path"]) == acquisition["source"]["sha256"]
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "passed": True, "worlds_checked": len(worlds),
              "prefix_records_checked": records, "subset_feasibility_states_checked": subset_states,
              "subset_positive_witnesses_checked": subset_witnesses, "candidate_positive_witnesses_checked": candidate_witnesses,
              "heldout_residuals_checked": residuals, "unmeasured_scale_witnesses_checked": scale_witnesses,
              "aggregate_rows_checked": rows_checked, "optimal_set_rows_checked": optimal_checked, "trajectory_rows_checked": histories_checked,
              "inventory_and_corruption_reconstruction": True, "coefficient_sum_invariance_checked": True,
              "counted_unit_actual_object_trace_checked": True, "unmeasured_absolute_identifications": 0,
              "all_ties_and_families_verified_by_subsets": True, "closed_inequality_boundaries_checked": True,
              "baseline_matches_frozen_code_hash": True, "tested_fit_functions_have_no_key_or_file_access": static_check(),
              "source_hashes_checked": 1, "inferences_sha256": digest(ENDPOINT/"inferences.jsonl"),
              "evaluated_sha256": digest(ENDPOINT/"evaluated-prefixes.jsonl"), "code_sha256": digest(Path(__file__))}
    review = BASE/"verification-v2"
    assert review.exists() and (review/"AUDIT_REPAIR.json").exists()
    result["audit_repair"] = "AUDIT_REPAIR.json"
    result["original_inference_endpoint"] = "../main-v1/"
    save(review/"verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
