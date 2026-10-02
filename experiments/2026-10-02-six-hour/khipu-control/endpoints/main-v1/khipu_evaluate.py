"""Separate evaluator for frozen khipu control predictions and synthetic truth."""
from __future__ import annotations
import argparse
import collections
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"experiments/2026-10-02-six-hour/khipu-control"
RAW=ROOT/"data/six-hour/khipu/puruchuco-2026-10-02"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")

def read_lines(path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def source_score():
    key_path=RAW/"source-evaluator-key.json"
    prediction_path=RAW/"source-predictions.jsonl"
    key=json.loads(key_path.read_text(encoding="utf-8"));target=key["targets"]
    scored_path=RAW/"source-scores.jsonl"
    if scored_path.exists():
        raise FileExistsError(scored_path)
    methods=collections.defaultdict(list); reference=None
    with scored_path.open("w",encoding="utf-8") as f:
        for prediction in read_lines(prediction_path):
            residual=[p-t for p,t in zip(prediction["prediction"],target)]
            scores={"exact_columns":sum(x==0 for x in residual),"absolute_error":sum(abs(x) for x in residual),
                    "signed_total_error":sum(residual),"complete_vector_equal":all(x==0 for x in residual)}
            record={"method":prediction["method"],"replicate":prediction["replicate"],"scores":scores,"residual":residual}
            f.write(json.dumps(record,separators=(",",":"))+"\n")
            methods[prediction["method"]].append(scores)
            if prediction["method"]=="published_order":
                reference=scores
    assert reference is not None
    summaries={}
    for method,scores in methods.items():
        errors=[x["absolute_error"] for x in scores]; exacts=[x["exact_columns"] for x in scores]
        summaries[method]={
            "replicates":len(scores),"exact_columns_histogram":dict(sorted(collections.Counter(exacts).items())),
            "absolute_error_histogram":dict(sorted(collections.Counter(errors).items())),
            "mean_exact_columns":str(Fraction(sum(exacts),len(scores))),
            "mean_absolute_error":str(Fraction(sum(errors),len(scores))),
            "median_absolute_error":statistics.median(errors),"minimum_absolute_error":min(errors),"maximum_absolute_error":max(errors),
            "strictly_lower_absolute_error_than_published":sum(e<reference["absolute_error"] for e in errors),
            "equal_absolute_error_to_published":sum(e==reference["absolute_error"] for e in errors),
            "strictly_more_exact_columns_than_published":sum(e>reference["exact_columns"] for e in exacts),
            "equal_exact_columns_to_published":sum(e==reference["exact_columns"] for e in exacts),
            "signed_total_error_histogram":dict(collections.Counter(x["signed_total_error"] for x in scores)),
            "complete_vector_equal":sum(x["complete_vector_equal"] for x in scores),
        }
    result={"created_utc":datetime.now(timezone.utc).isoformat(),"scope":"published reference representation control; analyst previously exposed",
            "source_input_sha256":sha(RAW/"source-component-input.json"),"key_sha256":sha(key_path),
            "prediction_sha256":sha(prediction_path),"score_path":scored_path.relative_to(ROOT).as_posix(),"score_sha256":sha(scored_path),
            "published_alignment_scores":reference,"methods":summaries,"column_denominator":20}
    save(OUT/"source-aggregate.json",result)
    print(json.dumps({"published":reference,"methods":{k:{x:v[x] for x in ('replicates','mean_exact_columns','mean_absolute_error','minimum_absolute_error','strictly_lower_absolute_error_than_published')} for k,v in summaries.items()}},indent=2))

def synthetic_score():
    endpoint=OUT/"endpoints/main-v1"
    keys={r["id"]:r["key"] for r in read_lines(endpoint/"evaluator-key.jsonl")}
    inputs={r["id"]:r for r in read_lines(endpoint/"component-inputs.jsonl")}
    scored=endpoint/"evaluated-prefixes.jsonl"
    if scored.exists():
        raise FileExistsError(scored)
    summaries=collections.defaultdict(collections.Counter)
    per_path=collections.defaultdict(list)
    records=0
    with scored.open("w",encoding="utf-8") as f:
        for record in read_lines(endpoint/"inferred-prefixes.jsonl"):
            key=keys[record["world_id"]]; component=inputs[record["input_id"]]["component"]
            inferred=record["inferred"];status=inferred["status"]
            correct_unique=False; false_unique=False; decoded_errors=None
            if status=="unique_positive":
                weights=list(map(Fraction,inferred["witnesses"][0]))
                decoded=[sum(Fraction(x)*w for x,w in zip(features,weights)) for features in component["features"]]
                decoded_errors=[x-y for x,y in zip(decoded,key["quantities"])]
                correct_unique=all(x==0 for x in decoded_errors)
                false_unique=not correct_unique
            evaluation={"status":status,"correct_unique_decoder":correct_unique,"false_unique_decoder":false_unique,
                        "maximum_absolute_quantity_error":None if decoded_errors is None else str(max(map(abs,decoded_errors)))}
            out={"input_id":record["input_id"],"world_id":record["world_id"],"condition":key["generation_condition"],"representation":record["representation"],"prefix":record["prefix"],"evaluation":evaluation}
            f.write(json.dumps(out,separators=(",",":"))+"\n")
            group=(key["generation_condition"],record["representation"],record["prefix"])
            summaries[group][status]+=1
            summaries[group]["correct_unique_decoder"]+=int(correct_unique)
            summaries[group]["false_unique_decoder"]+=int(false_unique)
            summaries[group]["records"]+=1
            per_path[record["input_id"]].append(out)
            records += 1
    trajectories=collections.defaultdict(collections.Counter)
    for input_id,path in per_path.items():
        assert [x["prefix"] for x in path]==list(range(1,9))
        first=path[0];group=(first["condition"],first["representation"])
        ever_wrong=any(x["evaluation"]["false_unique_decoder"] for x in path)
        final_reject=path[-1]["evaluation"]["status"]=="no_positive_solution"
        trajectories[group]["paths"]+=1
        trajectories[group]["ever_false_unique"]+=int(ever_wrong)
        trajectories[group]["false_unique_then_final_rejection"]+=int(ever_wrong and final_reject)
        correct_prefix=next((x["prefix"] for x in path if x["evaluation"]["correct_unique_decoder"]),None)
        if correct_prefix is not None:
            trajectories[group]["first_correct_unique_prefix_"+str(correct_prefix)]+=1
    result={"created_utc":datetime.now(timezone.utc).isoformat(),"prefix_records":records,
            "summaries":[{"condition":c,"representation":r,"prefix":p,**dict(counts)} for (c,r,p),counts in sorted(summaries.items())],
            "trajectories":[{"condition":c,"representation":r,**dict(counts)} for (c,r),counts in sorted(trajectories.items())],
            "evaluated_path":scored.name,"evaluated_sha256":sha(scored),
            "key_sha256":sha(endpoint/"evaluator-key.jsonl"),"inferred_sha256":sha(endpoint/"inferred-prefixes.jsonl"),
            "definition":"A correct unique decoder reproduces all32 generated cord quantities. This score is separate from whether the parent–child accounting assumption is true."}
    save(endpoint/"aggregate.json",result)
    print(json.dumps({"final":[x for x in result["summaries"] if x["prefix"]==8],"trajectories":result["trajectories"]},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("command",choices=["source","synthetic"]);a=p.parse_args()
    (source_score if a.command=="source" else synthetic_score)()
