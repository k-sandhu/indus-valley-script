"""Post-result independent validation of the reviewer's shared-operation output.

No reviewer or baseline model functions are imported. This is validation after
the reported result, not a preregistered discovery experiment.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent / "review"
OUTPUT = HERE / "co-production-checks-v1"
TASKS = ("renew_A", "renew_B", "train")
S = list(product(range(3), range(3), range(4)))
K = {s for s in S if s[0] and s[1]}
SHOCKS = {"none": [(0,0)], "focal": [(0,0),(1,0)],
          "common": [(0,0),(1,1)], "full": list(product(range(2), repeat=2))}
ALL_ACTIONS = [set(v) for n in range(4) for v in combinations(TASKS,n)]

def cost(action):
    repairs = len(action & {"renew_A", "renew_B"})
    return repairs + (1 if "train" in action and repairs == 0 else 0)

def transition(state, action, disturbance):
    output = []
    for index, name in enumerate(TASKS):
        reset = 3 if index == 2 else 2
        value = reset if name in action else state[index]-1
        output.append(max(0,value))
    output[0] = max(0,output[0]-disturbance[0])
    output[1] = max(0,output[1]-disturbance[1])
    return tuple(output)

def next_set(target,budget,support,robust):
    accepted = set()
    for state in K:
        for action in ALL_ACTIONS:
            if cost(action)>budget or (action and state[2]==0):
                continue
            reached = {transition(state,action,w) for w in SHOCKS[support]}
            if reached <= target if robust else bool(reached & target):
                accepted.add(state)
                break
    return accepted

def main():
    if OUTPUT.exists():
        raise SystemExit("Validation endpoint exists; do not overwrite.")
    path = REVIEW / "co-production-v1/results.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    checks=[]
    def check(label, condition):
        checks.append({"check":label,"passed":bool(condition)})
    check("16 worlds",len(result["worlds"])==16)
    check("all reviewer checks pass",result["checks_passed"]==1133 and all(r["passed"] for r in result["checks"]))
    for world in result["worlds"]:
        budget,support=world["budget"],world["shock_support"]
        for mode in ("possible","robust"):
            record=world[mode]; robust=mode=="robust"; target=set(K)
            for h in range(13):
                check(f"{budget}/{support}/{mode}/h{h}",target=={tuple(s) for s in record["finite_horizons"][h]["states"]})
                target=next_set(target,budget,support,robust)
            while True:
                nxt=next_set(target,budget,support,robust)
                if nxt==target: break
                check("descending",nxt<=target); target=nxt
            check(f"{budget}/{support}/{mode}/infinite",target=={tuple(s) for s in record["infinite_kernel"]})
            for row in record["infinite_policy"]:
                state=tuple(row["state"]); action=set(row["action"])
                check("policy eligible",cost(action)<=budget and (not action or state[2]>0))
                reached=[]
                for successor in row["successors"]:
                    actual=transition(state,action,tuple(successor["shock"]))
                    check("policy transition",actual==tuple(successor["state"]))
                    check("policy membership",successor["in_kernel"]==(actual in target))
                    reached.append(actual in target)
                check("policy quantifier",all(reached) if robust else any(reached))
    failure=[r for r in checks if not r["passed"]]
    if failure:
        print(json.dumps(failure)); raise SystemExit(1)
    OUTPUT.mkdir()
    output={"status":"passed","scope":__doc__,"reviewer_output_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "checker_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "checks_passed":len(checks),"checks_failed":len(failure),"checks":checks}
    (OUTPUT/"checks.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"passed","checks":len(checks)}))

if __name__=="__main__": main()
