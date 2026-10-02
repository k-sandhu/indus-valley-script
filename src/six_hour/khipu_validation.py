"""Quantity-free projection and selection for a post-outcome validation study."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/2026-10-02-six-hour/khipu-control/validation-design"
RUN = BASE / "main-v1"
SOURCE = BASE.parent / "conservation-check/main-v1"
VIEWS = ("unmeasured", "counted")
BUDGETS = (0, 1, 2, 3)
POLICIES = ("account_first", "count_first", "greedy_rank")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def determinant(rows):
    a,b,c=rows
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])


def rank(rows):
    if any(determinant(selected) for selected in itertools.combinations(rows,3)):
        return 3
    if any(a[i]*b[j]-a[j]*b[i] for a,b in itertools.combinations(rows,2) for i,j in ((0,1),(0,2),(1,2))):
        return 2
    return int(any(any(row) for row in rows))


def select(checks, anchor_rows, budget, policy):
    remaining = list(range(len(checks)))
    if policy == "count_first":
        remaining.sort(key=lambda i: (checks[i]["kind"] != "count", i))
    selected = []; rows = list(anchor_rows)
    while len(selected) < budget:
        if policy == "greedy_rank":
            chosen = max(remaining, key=lambda i: (rank(rows + [checks[i]["row"]]) - rank(rows), -i))
        else:
            chosen = remaining[0]
        selected.append(chosen); rows.append(checks[chosen]["row"]); remaining.remove(chosen)
    return {"indices": selected, "ids": [checks[i]["id"] for i in selected], "rank": rank(rows)}


def project():
    RUN.mkdir(parents=True,exist_ok=False)
    names=("component-inputs.jsonl","evaluator-key.jsonl","inferences.jsonl","evaluated-prefixes.jsonl")
    pins=[{"source":"../conservation-check/main-v1/"+n,"bytes":(SOURCE/n).stat().st_size,"sha256":digest(SOURCE/n)} for n in names]
    with (SOURCE/"evaluator-key.jsonl").open(encoding="utf-8") as source, (RUN/"selector-inputs.jsonl").open("x",encoding="utf-8") as out, (RUN/"targets.jsonl").open("x",encoding="utf-8") as targets:
        for line in source:
            record=json.loads(line); key=record["key"]
            checks=[{"id":f"account-{i}","kind":"account","row":row} for i,row in enumerate(key["heldout_equations"])]
            checks += [{"id":f"count-{i}","kind":"count","row":row} for i,row in enumerate(key["count_features"])]
            out.write(json.dumps({"world_id":record["id"],"checks":checks,"anchor_rows":{"unmeasured":[],"counted":[[1,0,0]]}},separators=(",",":"))+"\n")
            targets.write(json.dumps({"world_id":record["id"],"rhs":[0]*8+key["count_values"],"true_absolute_values":key["true_weights"],"actual_additive_function":key["actual_additive_function"]},separators=(",",":"))+"\n")
    save(RUN/"source-pins.json",{"created_utc":datetime.now(timezone.utc).isoformat(),"scope":"Reused synthetic observations; analyst has seen KHI-04 outcomes and two failure examples","sources":pins,"projection":"Rows and kinds only in selector inputs; measured targets and truth separate"})


def selections():
    with (RUN/"selector-inputs.jsonl").open(encoding="utf-8") as source, (RUN/"selections.jsonl").open("x",encoding="utf-8") as out:
        records=0
        for line in source:
            world=json.loads(line)
            for view in VIEWS:
                for budget in BUDGETS:
                    result={p:select(world["checks"],world["anchor_rows"][view],budget,p) for p in POLICIES}
                    out.write(json.dumps({"world_id":world["world_id"],"view":view,"budget":budget,"policies":result},separators=(",",":"))+"\n");records+=1
    save(RUN/"random-subsets.json",{str(b):[list(s) for s in itertools.combinations(range(11),b)] for b in BUDGETS})
    save(RUN/"selection-manifest.json",{"sealed_utc":datetime.now(timezone.utc).isoformat(),"records":records,"selector_inputs_sha256":digest(RUN/"selector-inputs.jsonl"),"selections_sha256":digest(RUN/"selections.jsonl"),"targets_not_opened_by_selection":True,"decoders_not_opened_by_selection":True,"code_sha256":digest(Path(__file__))})
    print(f"Sealed {records} quantity-free selection records")


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("project","select"));args=parser.parse_args()
    (project if args.command=="project" else selections)()
