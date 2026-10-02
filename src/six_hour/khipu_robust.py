"""Exact maximum-consensus geometry for fresh positional-account controls.

Fitting receives integer relation rows only. A counted unit fixes u=1.
Generation and inference are separate commands; evaluator keys stay unopened
during inference. Every best positive point or affine family is retained.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path
import random
import shutil
import sys

from khipu_control import exact_decoder

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/2026-10-02-six-hour/khipu-control/robust-decoder"
ENDPOINT = BASE / "main-v1"
CONDITIONS = ("complete", "two_swapped", "four_swapped", "two_incomplete", "ownership")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def canonical(row):
    divisor = 0
    for x in row:
        divisor = gcd(divisor, abs(x))
    if not divisor:
        return (0, 0, 0)
    answer = tuple(x // divisor for x in row)
    if next(x for x in answer if x) < 0:
        answer = tuple(-x for x in answer)
    return answer


def line_family(row):
    """Positive solutions of a+b*t+c*h=0, with exact open bounds."""
    a, b, c = row
    if not b and not c:
        return {"feasible": not a, "reason": "zero_row" if not a else "nonzero_constant"}
    if not c:
        fixed = Fraction(-a, b)
        if fixed <= 0:
            return {"feasible": False, "reason": "fixed_t_not_positive", "fixed_t": str(fixed)}
        return {"feasible": True, "parameter": "h", "lower": "0", "upper": None,
                "base": ["1", str(fixed), "0"], "slope": ["0", "0", "1"],
                "witnesses": [["1", str(fixed), "1"], ["1", str(fixed), "2"]]}
    intercept, slope = Fraction(-a, c), Fraction(-b, c)
    lower, upper = Fraction(0), None
    if slope > 0:
        lower = max(lower, -intercept / slope)
    elif slope < 0:
        upper = -intercept / slope
    elif intercept <= 0:
        return {"feasible": False, "reason": "fixed_h_not_positive", "fixed_h": str(intercept)}
    if upper is not None and upper <= lower:
        return {"feasible": False, "reason": "empty_positive_interval", "lower": str(lower), "upper": str(upper)}
    choices = [lower + 1, lower + 2] if upper is None else [(2*lower+upper)/3, (lower+2*upper)/3]
    witnesses = [["1", str(t), str(intercept + slope*t)] for t in choices]
    assert all(Fraction(x) > 0 for witness in witnesses for x in witness)
    return {"feasible": True, "parameter": "t", "lower": str(lower), "upper": None if upper is None else str(upper),
            "base": ["1", "0", str(intercept)], "slope": ["0", "1", str(slope)], "witnesses": witnesses}


def support(rows, vector):
    return [i for i, row in enumerate(rows) if sum(a*b for a, b in zip(row, vector)) == 0]


def maximum_consensus(rows):
    """Enumerate the complete exact positive line arrangement, retaining ties.

No condition label, numerical dictionary, evaluator key or file path enters.
"""
    assert all(len(row) == 3 and all(isinstance(x, int) for x in row) for row in rows)
    zero_indices = [i for i, row in enumerate(rows) if not any(row)]
    classes = sorted(set(canonical(row) for row in rows if any(row)))
    line_records, viable = [], []
    for line in classes:
        family = line_family(line)
        fixed_support = zero_indices + [i for i, row in enumerate(rows) if any(row) and canonical(row) == line]
        record = {"line": list(line), "support": len(fixed_support), "support_indices": sorted(fixed_support), **family}
        line_records.append(record)
        if family["feasible"] and (line[1] or line[2]):
            viable.append(line)
    pair_records, points = [], set()
    for first, second in itertools.combinations(classes, 2):
        a, b, c = first
        d, e, f = second
        det = b*f-c*e
        pair = {"first": list(first), "second": list(second), "determinant": det}
        if det:
            t, h = Fraction(c*d-a*f, det), Fraction(a*e-b*d, det)
            positive = t > 0 and h > 0
            pair.update({"t": str(t), "h": str(h), "positive": positive})
            if positive:
                points.add((t, h))
        pair_records.append(pair)
    point_records = []
    for t, h in sorted(points):
        indices = support(rows, [Fraction(1), t, h])
        point_records.append({"values": ["1", str(t), str(h)], "support": len(indices), "support_indices": indices})
    best = max([len(zero_indices)] + [r["support"] for r in line_records if r["feasible"]] + [r["support"] for r in point_records])
    best_points = [r for r in point_records if r["support"] == best]
    best_families = [r for r in line_records if r["feasible"] and r["support"] == best]
    plane = best == len(zero_indices)
    if plane:
        best_families.append({"family": "positive_plane", "support": best, "support_indices": zero_indices,
                              "witnesses": [["1", "1", "1"], ["1", "2", "3"]]})
    for family in best_families:
        assert len(family["witnesses"]) == 2 and family["witnesses"][0] != family["witnesses"][1]
        for witness in family["witnesses"]:
            assert len(support(rows, list(map(Fraction, witness)))) == best
    unique = len(best_points) == 1 and not best_families
    return {"best_support": best, "status": "unique_positive" if unique else "ambiguous_positive",
            "optimal_points": best_points, "optimal_families": best_families,
            "line_candidates": line_records, "point_candidates": point_records, "pair_checks": pair_records,
            "zero_indices": zero_indices}


def consensus_decision(inferred, count, numerator=3, denominator=4):
    threshold = (numerator*count+denominator-1)//denominator
    if inferred["best_support"] < threshold:
        status = "rejected_support"
    elif inferred["status"] == "ambiguous_positive":
        status = "abstained_ambiguity"
    else:
        status = "accepted_unique"
    return {"threshold": threshold, "status": status,
            "values": inferred["optimal_points"][0]["values"] if status == "accepted_unique" else None}


def digits(quantity):
    return [quantity % 10, (quantity // 10) % 10, (quantity // 100) % 10]


def accounts(seed, ownership=False):
    rng = random.Random(seed)
    leaves = [[rng.randrange(300) for _ in range(3)] for _ in range(8)]
    parents = [sum(row) for row in leaves]
    if ownership:
        independent = random.Random(seed + 700000)
        parents = [independent.randrange(898) for _ in range(8)]
    quantities = parents + list(itertools.chain.from_iterable(leaves))
    features = [digits(q) for q in quantities]
    groups = [[8+3*i+j for j in range(3)] for i in range(8)]
    return features, groups, quantities


def equations(features, groups):
    return [[features[parent][j]-sum(features[child][j] for child in group) for j in range(3)]
            for parent, group in enumerate(groups)]


def generate_world(seed, condition):
    features, groups, quantities = accounts(seed, condition == "ownership")
    affected, operations = [], []
    if condition in ("two_swapped", "four_swapped"):
        rng = random.Random(seed+100000 if condition == "two_swapped" else seed+200000)
        chosen = rng.sample(range(8), 2 if condition == "two_swapped" else 4)
        for p, q in zip(chosen[::2], chosen[1::2]):
            pi, qi = rng.randrange(3), rng.randrange(3)
            first, second = groups[p][pi], groups[q][qi]
            groups[p][pi], groups[q][qi] = second, first
            operations.append({"parents": [p, q], "children": [first, second]})
        affected = sorted(chosen)
    elif condition == "two_incomplete":
        rng = random.Random(seed+300000)
        affected = sorted(rng.sample(range(8), 2))
        for parent in affected:
            child = groups[parent].pop(rng.randrange(3))
            operations.append({"parent": parent, "removed_child": child})
    elif condition not in ("complete", "ownership"):
        raise ValueError(condition)
    rows = equations(features, groups)
    held_features, held_groups, held_quantities = accounts(seed+1000000, condition == "ownership")
    counted = random.Random(seed+2000000)
    count_values = [counted.randrange(898) for _ in range(3)]
    component = {"features": features, "memberships": groups, "equations": rows,
                 "anchor": [1, 0, 0], "anchor_value": 1}
    key = {"true_weights": [1, 10, 100], "training_quantities": quantities,
           "intended_affected_accounts": affected, "corruption_operations": operations,
           "actual_violations": [i for i, row in enumerate(rows) if sum(a*b for a, b in zip(row, [1, 10, 100])) != 0],
           "heldout_features": held_features, "heldout_memberships": held_groups,
           "heldout_quantities": held_quantities, "heldout_equations": equations(held_features, held_groups),
           "count_features": [digits(q) for q in count_values], "count_values": count_values}
    return component, key


def generate():
    if ENDPOINT.exists():
        raise FileExistsError(ENDPOINT)
    ENDPOINT.mkdir(parents=True)
    for name in ("PROTOCOL.md", "protocol-freeze.json", "source-acquisition.json"):
        shutil.copyfile(BASE/name, ENDPOINT/name)
    for name in ("khipu_robust.py", "khipu_robust_evaluate.py", "khipu_robust_verify.py", "khipu_control.py"):
        shutil.copyfile(Path(__file__).with_name(name), ENDPOINT/name)
    inputs, keys = ENDPOINT/"component-inputs.jsonl", ENDPOINT/"evaluator-key.jsonl"
    count = 0
    with inputs.open("w", encoding="utf-8") as inf, keys.open("w", encoding="utf-8") as kf:
        for seed in range(20261010000, 20261010300):
            for condition in CONDITIONS:
                component, key = generate_world(seed, condition)
                world_id = f"{seed}-{condition}"
                inf.write(json.dumps({"id": world_id, "seed": seed, "condition": condition, "component": component}, separators=(",", ":"))+"\n")
                kf.write(json.dumps({"id": world_id, "key": key}, separators=(",", ":"))+"\n")
                count += 1
    save(ENDPOINT/"generation-manifest.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "worlds": count,
          "seeds": [20261010000, 20261010299], "conditions": list(CONDITIONS), "training_accounts": 8,
          "withheld_accounts": 8, "withheld_counts": 3, "python_version": sys.version,
          "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in (inputs, keys)],
          "code_sha256": digest(Path(__file__)), "decoder_input_scope": "equations only; counted unit fixes u=1"})
    print(f"Generated {count} worlds and separate evaluator keys.")


def infer():
    destination = ENDPOINT/"inferences.jsonl"
    if destination.exists():
        raise FileExistsError(destination)
    count = 0
    with (ENDPOINT/"component-inputs.jsonl").open(encoding="utf-8") as inf, destination.open("w", encoding="utf-8") as outf:
        for line in inf:
            world = json.loads(line)
            assert world["component"]["anchor"] == [1, 0, 0] and world["component"]["anchor_value"] == 1
            for prefix in range(1, 9):
                rows = world["component"]["equations"][:prefix]
                robust = maximum_consensus(rows)
                strict = exact_decoder(rows, [1, 0, 0])
                record = {"world_id": world["id"], "prefix": prefix, "equations": rows,
                          "consensus": robust, "three_quarter": consensus_decision(robust, prefix),
                          "half": consensus_decision(robust, prefix, 1, 2), "all_relations": strict}
                outf.write(json.dumps(record, separators=(",", ":"))+"\n")
                count += 1
    diagnostics = {}
    cases = {"plane": [[0, 0, 0]]*8, "line": [[-10, -9, 1]]*8,
             "competing_points": [[-10, 1, 0]]*2+[[0, -10, 1]]*2+[[-2, 1, 0]]*2+[[-28, 0, 1]]*2}
    for name, rows in cases.items():
        fitted = maximum_consensus(rows)
        diagnostics[name] = {"equations": rows, "consensus": fitted,
                             "three_quarter": consensus_decision(fitted, 8), "half": consensus_decision(fitted, 8, 1, 2)}
    save(ENDPOINT/"diagnostics.json", diagnostics)
    save(ENDPOINT/"inference-manifest.json", {"created_utc": datetime.now(timezone.utc).isoformat(), "prefix_records": count,
          "component_input_sha256": digest(ENDPOINT/"component-inputs.jsonl"), "inference_sha256": digest(destination),
          "bytes": destination.stat().st_size, "fitting_receives_evaluator_key": False,
          "fitting_functions": ["maximum_consensus(rows)", "exact_decoder(rows, [1,0,0])"],
          "evaluator_key_opened_during_inference": False, "protocol_sha256": digest(BASE/"PROTOCOL.md")})
    print(f"Saved {count} exact prefix inferences; evaluator unopened.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["generate", "infer"])
    args = parser.parse_args()
    (generate if args.command == "generate" else infer)()
