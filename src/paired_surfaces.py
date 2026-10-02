"""Observed physical-object surface relations and independently typed stroke counts."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import numpy as np
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
STROKES={"032":2,"033":3,"034":4}


def load():
    return [json.loads(x) for x in (ROOT/"data/normalized/lipi_observed_faces.jsonl")
            .read_text(encoding="utf-8").splitlines()]


def numeric(seq):
    if len(seq)==2 and seq[0] in STROKES and seq[1]=="700":
        return STROKES[seq[0]],"stroke_U"
    if len(seq)==2 and seq[1] in STROKES and seq[0]=="700":
        return STROKES[seq[1]],"U_stroke"
    return None


def number(raw):
    try:
        v=float(raw)
        return v if np.isfinite(v) and v>0 else None
    except (TypeError,ValueError):
        return None


def coefficient(y,x,strata):
    # Fixed stratum effects by centering; slopes use within-template variation.
    xc=x.copy().astype(float)
    yc=y.copy().astype(float)
    for ix in strata:
        xc[ix]-=xc[ix].mean()
        yc[ix]-=yc[ix].mean()
    denom=float(xc@xc)
    return float(xc@yc/denom) if denom>0 else float("nan")


def holm(p):
    order=np.argsort(p)
    adjusted=np.empty(len(p)); previous=0.
    for rank,i in enumerate(order):
        value=min(1.,(len(p)-rank)*p[i])
        previous=max(previous,value)
        adjusted[i]=previous
    return adjusted.tolist()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--permutations",type=int,default=9999)
    ap.add_argument("--out",default="results/paired")
    args=ap.parse_args()
    rows=load()
    usable=[r for r in rows if r["complete_observed"] and not r["has_unknown_sign"]
            and not r.get("has_blank_space",False) and r["single_line"]
            and r["signs_reading_rtl"] and r["direction"] in {"R/L","L/R","NR","SYM"}]
    objects=defaultdict(list)
    for r in usable: objects[r["object_family_id"]].append(r)
    edge_objects=defaultdict(list)
    numeric_objects=[]; multi_value_objects=[]; frame_count=defaultdict(Counter)
    numeric_face_exposure=Counter()
    exclusions=Counter()
    for oid,faces in objects.items():
        sequences={tuple(r["signs_reading_rtl"]) for r in faces}
        for pair in combinations(sorted(sequences),2):
            edge_objects[pair].append({"object":oid,"cisi":faces[0]["source_cisi"],
                                       "site":faces[0]["site"],"type":faces[0]["object_type"]})
        ns=[(r,numeric(r["signs_reading_rtl"])) for r in faces
            if numeric(r["signs_reading_rtl"]) is not None]
        if not ns: continue
        numeric_face_exposure[len(ns)]+=1
        values={v[0] for _,v in ns}
        if len(values)>1:
            multi_value_objects.append({"object":oid,"cisi":faces[0]["source_cisi"],
                                        "values":sorted(values),
                                        "all_faces":[r["signs_reading_rtl"] for r in faces]})
            exclusions["multiple_unequal_numeric_values"]+=1
            continue
        other=[r for r in faces if numeric(r["signs_reading_rtl"]) is None]
        if not other:
            exclusions["no_complete_other_face"]+=1
            continue
        main_face=sorted(other,key=lambda r:(-r["length"],r["record_id"]))[0]
        template=tuple(main_face["signs_reading_rtl"])
        nr, nv=ns[0]
        md=nr["metadata"]
        item={"object":oid,"cisi":nr["source_cisi"],"site":nr["site"],
              "type":nr["object_type"],"stroke_count":nv[0],
              "numeric_order":nv[1],"main_template":list(template),
              "numeric_faces":[r["record_id"] for r,_ in ns],
              "other_faces":[r["record_id"] for r in other],
              "dimensions":{k:number(md.get(k)) for k in
                            ["horizontal(mm)","vertical(mm)","thickness(mm)"]},
              "material":md.get("material"),"shape":md.get("shape")}
        numeric_objects.append(item)
        frame_count[(template,nr["object_type"])][nv[0]]+=1
    edges=[{"sequences":[list(x) for x in pair],"objects":len(obs),"records":obs}
           for pair,obs in sorted(edge_objects.items(),key=lambda x:(-len(x[1]),x[0]))]
    out=ROOT/args.out; out.mkdir(parents=True,exist_ok=True)
    (out/"surface_edges.json").write_text(json.dumps(edges,indent=2),encoding="utf-8")
    (out/"numeric_object_audit.json").write_text(json.dumps(numeric_objects,indent=2),encoding="utf-8")
    frames=[{"main_template":list(k[0]),"type":k[1],"stroke_counts":dict(v),
             "objects":sum(v.values()),"distinct_stroke_counts":len(v)}
            for k,v in sorted(frame_count.items(),key=lambda x:(-sum(x[1].values()),x[0]))]
    result={"usable_faces":len(usable),"physical_objects":len(objects),
            "objects_with_multiple_usable_faces":sum(len(v)>1 for v in objects.values()),
            "distinct_interface_edges":len(edges),"numeric_objects_with_other_face":len(numeric_objects),
            "numeric_stroke_counts":dict(Counter(r["stroke_count"] for r in numeric_objects)),
            "numeric_order":dict(Counter(r["numeric_order"] for r in numeric_objects)),
            "numeric_objects_by_number_of_numeric_faces":dict(numeric_face_exposure),
            "unequal_value_exposure_warning":"Zero unequal-value objects is not strong exclusion evidence: almost every object has only one qualifying numeric face.",
            "multiple_unequal_numeric_objects":multi_value_objects,
            "exclusions":dict(exclusions),"main_template_families":frames,"geometry_tests":[]}
    rng=np.random.default_rng(20261004)
    for dim in ["horizontal(mm)","vertical(mm)","thickness(mm)"]:
        valid=[r for r in numeric_objects if r["dimensions"][dim] is not None
               and .1<=r["dimensions"][dim]<=150.]
        strata_map=defaultdict(list)
        for i,r in enumerate(valid):
            strata_map[(tuple(r["main_template"]),r["type"],r["site"])].append(i)
        kept=[ix for ix in strata_map.values() if len(ix)>=5
              and len({valid[i]["stroke_count"] for i in ix})>1]
        keep=sorted(i for ix in kept for i in ix)
        selected=[valid[i] for i in keep]
        if not selected:
            result["geometry_tests"].append({"dimension":dim,"status":"insufficient data"})
            continue
        y=np.log(np.asarray([r["dimensions"][dim] for r in selected]))
        x=np.asarray([r["stroke_count"] for r in selected])
        ss=defaultdict(list)
        for i,r in enumerate(selected): ss[(tuple(r["main_template"]),r["type"],r["site"])].append(i)
        strata=[np.asarray(ix) for ix in ss.values()]
        observed=coefficient(y,x,strata)
        null=[]
        for j in range(args.permutations):
            xp=x.copy()
            for ix in strata: xp[ix]=rng.permutation(x[ix])
            null.append(coefficient(y,xp,strata))
        p=(1+sum(abs(v)>=abs(observed) for v in null))/(1+len(null))
        result["geometry_tests"].append({"dimension":dim,"objects":len(selected),
              "template_type_site_strata":len(strata),"slope_log_mm_per_stroke":observed,
              "dimension_ratio_per_extra_stroke":float(np.exp(observed)),
              "p_two_sided":p,"permutations":len(null),
              "null_95_interval":np.quantile(null,[.025,.975]).tolist(),
              "selected_objects":[r["object"] for r in selected],
              "by_stroke_dimension":{str(n):{"n":int(sum(x==n)),
                 "median_mm":float(np.median(np.exp(y[x==n])))} for n in sorted(set(x))}})
    done=[r for r in result["geometry_tests"] if "p_two_sided" in r]
    if done:
        for r,p in zip(done,holm([r["p_two_sided"] for r in done])): r["p_holm"]=p
    (out/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["usable_faces","physical_objects",
         "numeric_objects_with_other_face","multiple_unequal_numeric_objects","geometry_tests"]},indent=2))


if __name__=="__main__": main()
