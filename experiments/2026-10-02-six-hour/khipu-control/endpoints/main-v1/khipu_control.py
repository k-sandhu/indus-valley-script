"""Quantity-hidden positional accounting control and fixed source predictor.

Predictors accept supplied features only. Source quantities and evaluator keys
are prepared and scored in separate modules. Synthetic generation and decoding
are distinct steps; the decoder never receives generated numerical readings.
"""
from __future__ import annotations
import argparse
import collections
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/2026-10-02-six-hour/khipu-control"
RAW = ROOT / "data/six-hour/khipu/puruchuco-2026-10-02"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

def fraction_strings(items):
    return [str(x) for x in items]

def rref(matrix, columns):
    """Gauss-Jordan elimination over exact rationals; return pivots and rows."""
    rows = [[Fraction(x) for x in row] for row in matrix]
    next_row, pivots = 0, []
    for col in range(columns):
        match = next((i for i in range(next_row, len(rows)) if rows[i][col]), None)
        if match is None:
            continue
        rows[next_row], rows[match] = rows[match], rows[next_row]
        divisor = rows[next_row][col]
        rows[next_row] = [x / divisor for x in rows[next_row]]
        for i in range(len(rows)):
            if i != next_row and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [a-factor*b for a,b in zip(rows[i],rows[next_row])]
        pivots.append(col); next_row += 1
        if next_row == len(rows):
            break
    return rows, pivots

def exact_decoder(equations, anchor):
    """Return exact positive solutions for one or three positional features.

The supplied anchor is the counted object's feature vector, with observed value
one. No numerical dictionary or set of true weights enters this function.
"""
    dimension = len(anchor)
    assert dimension in (1,3) and anchor == [1] + [0]*(dimension-1)
    homogeneous, hpivots = rref(equations, dimension)
    augmented = [list(row)+[0] for row in equations] + [list(anchor)+[1]]
    reduced, pivots = rref(augmented, dimension)
    common = {"rank_homogeneous": len(hpivots), "rank_anchored": len(pivots),
              "dimension": dimension, "rref": [fraction_strings(row) for row in reduced],
              "pivots": pivots, "anchor": anchor}
    if any(not any(row[:dimension]) and row[dimension] for row in reduced):
        return common | {"status": "no_positive_solution", "reason": "inconsistent_count_anchor", "witnesses": []}
    free = [i for i in range(dimension) if i not in pivots]
    def solution(values):
        answer = [Fraction(0)] * dimension
        for i,v in zip(free, values):
            answer[i] = Fraction(v)
        for i,p in enumerate(pivots):
            answer[p] = reduced[i][dimension] - sum(reduced[i][j]*answer[j] for j in free)
        return answer
    if not free:
        answer = solution([])
        if all(x > 0 for x in answer):
            return common | {"status": "unique_positive", "reason": "full_anchored_rank", "witnesses": [fraction_strings(answer)]}
        return common | {"status": "no_positive_solution", "reason": "unique_affine_solution_is_not_positive", "witnesses": []}
    if len(free) == 2:
        assert len(pivots) == 1 and pivots == [0]
        witnesses = [solution([1,1]), solution([2,1])]
        assert all(x > 0 for w in witnesses for x in w)
        return common | {"status": "ambiguous_positive", "reason": "two_free_coordinates", "witnesses": [fraction_strings(w) for w in witnesses]}
    assert len(free) == 1
    base = solution([0]); slope = [b-a for a,b in zip(base,solution([1]))]
    lower, upper = None, None
    for constant, coefficient in zip(base, slope):
        if coefficient > 0:
            bound = -constant/coefficient
            lower = bound if lower is None else max(lower,bound)
        elif coefficient < 0:
            bound = -constant/coefficient
            upper = bound if upper is None else min(upper,bound)
        elif constant <= 0:
            return common | {"status": "no_positive_solution", "reason": "fixed_nonpositive_coordinate", "witnesses": []}
    if lower is not None and upper is not None and lower >= upper:
        return common | {"status": "no_positive_solution", "reason": "empty_open_positive_interval", "witnesses": [],
                         "free_interval": [str(lower),str(upper)]}
    if lower is not None and upper is not None:
        choices = [(2*lower+upper)/3, (lower+2*upper)/3]
    elif lower is not None:
        choices = [lower+1, lower+2]
    elif upper is not None:
        choices = [upper-1,upper-2]
    else:
        choices = [Fraction(0),Fraction(1)]
    witnesses = [solution([v]) for v in choices]
    assert witnesses[0] != witnesses[1]
    assert all(x > 0 for w in witnesses for x in w)
    return common | {"status": "ambiguous_positive", "reason": "open_positive_interval",
                     "free_coordinate": free[0], "free_interval": [None if lower is None else str(lower),None if upper is None else str(upper)],
                     "witnesses": [fraction_strings(w) for w in witnesses]}

def column_sum(rows):
    width = len(rows[0]); assert all(len(row)==width for row in rows)
    return [sum(row[j] for row in rows) for j in range(width)]

def source_predictions(rows):
    """Yield fixed representations without reading or receiving target values."""
    assert len(rows)==3 and all(len(row)==20 for row in rows)
    identity = [list(range(i*20,(i+1)*20)) for i in range(3)]
    bag = list(itertools.chain.from_iterable(rows))
    def prediction(method, replicate, orders):
        represented = [[bag[i] for i in row] for row in orders]
        return {"method": method, "replicate": replicate, "orders": orders, "prediction": column_sum(represented)}
    yield prediction("published_order",0,identity)
    yield prediction("ordered_flat_known_dimensions",0,identity)
    for flips in itertools.product((False,True),repeat=3):
        orders = [list(reversed(row)) if flip else list(row) for row,flip in zip(identity,flips)]
        yield prediction("within_row_reversal",list(map(int,flips)),orders)
    for shift_b,shift_c in itertools.product(range(20),repeat=2):
        orders = [identity[0],identity[1][shift_b:]+identity[1][:shift_b],identity[2][shift_c:]+identity[2][:shift_c]]
        yield prediction("relative_cyclic_shift",[shift_b,shift_c],orders)
    rng = random.Random(2026100201)
    for replicate in range(10000):
        orders = [list(row) for row in identity]
        for row in orders:
            rng.shuffle(row)
        yield prediction("within_row_shuffle",replicate,orders)
    rng = random.Random(2026100202)
    for replicate in range(10000):
        shuffled = list(range(60)); rng.shuffle(shuffled)
        yield prediction("unordered_bag_random_allocation",replicate,[shuffled[i:i+20] for i in (0,20,40)])
    orders = sorted(range(60),key=lambda i:(bag[i],i))
    yield prediction("unordered_bag_sorted_allocation",0,[orders[i:i+20] for i in (0,20,40)])

def source_run():
    destination = RAW / "source-predictions.jsonl"
    if destination.exists():
        raise FileExistsError(destination)
    input_path = RAW / "source-component-input.json"
    supplied = json.loads(input_path.read_text(encoding="utf-8"))
    rows = supplied["rows"]
    row_invariance = [column_sum(list(permutation))==column_sum(rows) for permutation in itertools.permutations(rows)]
    count = 0
    with destination.open("w",encoding="utf-8") as f:
        for record in source_predictions(rows):
            f.write(json.dumps(record,separators=(",",":"))+"\n"); count += 1
    assert all(row_invariance)
    write_json(OUT / "source-prediction-manifest.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(), "input_sha256": sha(input_path),
        "prediction_path": destination.relative_to(ROOT).as_posix(), "prediction_sha256": sha(destination),
        "predictions": count, "whole_row_permutations_checked": len(row_invariance),
        "whole_row_permutation_invariance": all(row_invariance),
        "predictor_received_target": False, "predictor_function": "source_predictions(rows)",
    })
    print("Saved " + str(count) + " local predictions; targets were not supplied to predictor.")

def digits(quantity):
    return [quantity%10,(quantity//10)%10,(quantity//100)%10]

def make_world(seed, condition):
    """Generator owns true numerical readings; decoding receives a projection."""
    rng = random.Random(seed)
    leaves = [[rng.randrange(300) for _ in range(3)] for _ in range(8)]
    parents = [sum(row) for row in leaves]
    if condition == "ownership":
        owners = random.Random(seed+1000000)
        parents = [owners.randrange(898) for _ in range(8)]
    features = [digits(x) for x in parents] + [digits(x) for row in leaves for x in row]
    quantities = parents + list(itertools.chain.from_iterable(leaves))
    memberships = [[8+3*i+j for j in range(3)] for i in range(8)]
    removed = []
    if condition == "incomplete":
        incomplete = random.Random(seed+2000000)
        accounts = incomplete.sample(range(8),4)
        for account in sorted(accounts):
            child = incomplete.choice(memberships[account]); memberships[account].remove(child)
            removed.append({"parent": account,"child": child})
    visible = {"features": features,"memberships": memberships,"parent_indices": list(range(8)),
               "anchor": [1,0,0], "anchor_value": 1}
    key = {"quantities": quantities,"true_weights": [1,10,100], "removed_memberships": removed,
           "generation_condition": condition,"seed": seed}
    return visible,key

def represent(visible, representation, seed):
    """Transform physical features and membership; quantity truth is absent."""
    features = [list(x) for x in visible["features"]]
    groups = [list(x) for x in visible["memberships"]]
    anchor = list(visible["anchor"])
    rng = random.Random(seed)
    if representation == "sibling_shuffle":
        for group in groups:
            rng.shuffle(group)
    elif representation == "membership_removed":
        groups = [[] for _ in groups]
    elif representation == "position_collapsed":
        features = [[sum(x)] for x in features]
        anchor = [sum(anchor)]
    elif representation == "membership_scrambled":
        flat = list(itertools.chain.from_iterable(groups)); rng.shuffle(flat)
        sizes = list(map(len,groups)); groups=[]; cursor=0
        for size in sizes:
            groups.append(flat[cursor:cursor+size]); cursor += size
        assert cursor == len(flat)
    elif representation != "full":
        raise ValueError(representation)
    equations=[]
    if representation != "membership_removed":
        for parent,group in zip(visible["parent_indices"],groups):
            equations.append([features[parent][j]-sum(features[child][j] for child in group) for j in range(len(anchor))])
    return {"features": features,"memberships": groups,"equations": equations,"anchor": anchor}

def synthetic_run():
    endpoint = OUT / "endpoints/main-v1"
    if endpoint.exists():
        raise FileExistsError(endpoint)
    endpoint.mkdir(parents=True)
    for filename in ("PROTOCOL.md","PROTOCOL_PREFIX.md","protocol-freeze.json","prefix-protocol-freeze.json"):
        shutil.copyfile(OUT/filename,endpoint/filename)
    for filename in ("khipu_control.py","khipu_source.py","khipu_acquire.py"):
        shutil.copyfile(Path(__file__).with_name(filename),endpoint/filename)
    worlds_path=endpoint/"generator-worlds.jsonl"
    inputs_path=endpoint/"component-inputs.jsonl"
    answers_path=endpoint/"evaluator-key.jsonl"
    inferred_path=endpoint/"inferred-prefixes.jsonl"
    conditions=("complete","incomplete","ownership")
    representations=("full","sibling_shuffle","membership_removed","position_collapsed","membership_scrambled")
    worlds,inputs,records=0,0,0
    with worlds_path.open("w",encoding="utf-8") as wf, inputs_path.open("w",encoding="utf-8") as inf, answers_path.open("w",encoding="utf-8") as kf, inferred_path.open("w",encoding="utf-8") as outf:
        for seed in range(2026100300,2026100600):
            for condition in conditions:
                visible,key=make_world(seed,condition)
                world_id=f"{seed}-{condition}"
                wf.write(json.dumps({"id":world_id,"visible":visible},separators=(",",":"))+"\n")
                kf.write(json.dumps({"id":world_id,"key":key},separators=(",",":"))+"\n")
                worlds += 1
                for rep_index,representation in enumerate(representations):
                    control_seed=seed+3000000+rep_index*100000
                    component=represent(visible,representation,control_seed)
                    input_id=f"{world_id}-{representation}"
                    inf.write(json.dumps({"id":input_id,"world_id":world_id,"representation":representation,"control_seed":control_seed,"component":component},separators=(",",":"))+"\n")
                    inputs += 1
                    for prefix in range(1,9):
                        supplied_equations=component["equations"][:prefix]
                        # The only decoder arguments are public equations and counted features.
                        inferred=exact_decoder(supplied_equations,component["anchor"])
                        outf.write(json.dumps({"input_id":input_id,"world_id":world_id,"representation":representation,"prefix":prefix,"supplied_equations":supplied_equations,"inferred":inferred},separators=(",",":"))+"\n")
                        records += 1
    write_json(endpoint/"run-manifest.json",{
        "created_utc": datetime.now(timezone.utc).isoformat(),"worlds":worlds,"inputs":inputs,"prefix_records":records,
        "generator_seeds": [2026100300,2026100599],"conditions":list(conditions),"representations":list(representations),
        "decoder_receives_truth":False,"exact_arithmetic":"Python fractions.Fraction",
        "files":[{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in (worlds_path,inputs_path,answers_path,inferred_path)],
        "code_sha256":sha(Path(__file__)),"python_version":__import__('sys').version,
    })
    print(f"Generated {worlds} worlds, {inputs} component inputs and {records} exact prefix inferences.")

if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=["source","synthetic"])
    args=parser.parse_args()
    (source_run if args.command=="source" else synthetic_run)()
