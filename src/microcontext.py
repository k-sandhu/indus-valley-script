"""Within-area/period/length permutation test for different-sequence local similarity."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import numpy as np
from context_study import load_rows, principal_rows

ROOT=Path(__file__).resolve().parents[1]


def clean_field(value):
    return value not in {None,"","-","--","None","Unknown","?"}


def prepare(rows, unique=False, collapse=False, known_period=False):
    rr=[r.copy() for r in rows if r["site"]=="Mohenjo-daro"
        and r["object_type"].startswith("SEAL") and r["length"]>=3
        and clean_field(r["metadata"].get("block-house"))
        and clean_field(r["metadata"].get("area-section"))]
    if known_period:
        rr = [r for r in rr if clean_field(r["metadata"].get("period"))]
    if collapse:
        mapping={"861":"817","405":"390","706":"705"}
        for r in rr: r["signs_reading_rtl"]=[mapping.get(s,s) for s in r["signs_reading_rtl"]]
    freq=Counter(tuple(r["signs_reading_rtl"]) for r in rr)
    if unique: rr=[r for r in rr if freq[tuple(r["signs_reading_rtl"])]==1]
    freq=Counter(tuple(r["signs_reading_rtl"]) for r in rr)
    strata=defaultdict(list)
    for r in rr:
        md=r["metadata"]
        strata[(md["area-section"],md.get("period","-"),r["length"])].append(r)
    groups=[]
    for key,rs in sorted(strata.items()):
        if len(rs)<3: continue
        seq=np.asarray([r["signs_reading_rtl"] for r in rs])
        labels=np.asarray([r["metadata"]["block-house"] for r in rs])
        counts=Counter(labels)
        if max(counts.values())<2 or len(counts)<2: continue
        similarity=np.mean(seq[:,None,:]==seq[None,:,:],axis=2)
        exact=np.all(seq[:,None,:]==seq[None,:,:],axis=2)
        upper=np.triu(np.ones((len(rs),len(rs)),dtype=bool),1)&~exact
        weights=np.asarray([1./freq[tuple(r["signs_reading_rtl"])] for r in rs])
        pairweights=weights[:,None]*weights[None,:]*upper
        groups.append({"key":key,"rows":rs,"labels":labels,"similarity":similarity,
                       "pairweights":pairweights})
    return rr,groups


def score(groups,labels=None):
    within_sum=between_sum=within_weight=between_weight=0.
    for i,g in enumerate(groups):
        lab=g["labels"] if labels is None else labels[i]
        same=lab[:,None]==lab[None,:]
        pw=g["pairweights"]; sim=g["similarity"]
        a=pw*same; b=pw*~same
        within_sum+=float((sim*a).sum()); within_weight+=float(a.sum())
        between_sum+=float((sim*b).sum()); between_weight+=float(b.sum())
    if within_weight == 0 or between_weight == 0:
        raise ValueError("No positive weight for both different-text within and between comparisons")
    return {"difference":within_sum/within_weight-between_sum/between_weight,
            "within_mean":within_sum/within_weight,"between_mean":between_sum/between_weight,
            "within_weight":within_weight,"between_weight":between_weight}


def run(rows,permutations,unique,collapse,known_period=False):
    selected,groups=prepare(rows,unique,collapse,known_period)
    try:
        observed=score(groups)
    except ValueError as exc:
        return {"status": "insufficient comparable data", "reason": str(exc),
                "selected_objects": len(selected), "strata": len(groups),
                "known_period_only": known_period,
                "single_observation_sequences_only": unique,
                "three_allographs_collapsed": collapse}
    rng=np.random.default_rng(20261005)
    null=[]
    for j in range(permutations):
        null.append(score(groups,[rng.permutation(g["labels"]) for g in groups])["difference"])
    p=(1+sum(v>=observed["difference"] for v in null))/(1+len(null))
    result={"single_observation_sequences_only":unique,"three_allographs_collapsed":collapse,
            "known_period_only":known_period,
            "interpretation":"Recorded excavation blocks, not asserted households; period metadata is curatorial. Unique sensitivity discards all repeated texts, rather than selecting one representative.",
            "selected_objects":len(selected),"analyzed_objects":sum(len(g["rows"]) for g in groups),
            "strata":len(groups),"observed":observed,"permutations":len(null),
            "p_one_sided":p,"null_mean":float(np.mean(null)),
            "null_95_interval":np.quantile(null,[.025,.975]).tolist(),
            "stratum_audit":[{"key":g["key"],"objects":len(g["rows"]),
                              "blocks":dict(Counter(g["labels"])),
                              "record_ids":[r["record_id"] for r in g["rows"]]}
                             for g in groups]}
    return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--permutations",type=int,default=9999)
    ap.add_argument("--out",default="results/microcontext")
    ap.add_argument("--known-period",action="store_true")
    args=ap.parse_args()
    rows=principal_rows(load_rows(ROOT/"data/normalized/lipi_clean_rtl_singleline.jsonl"))
    out=ROOT/args.out; out.mkdir(parents=True,exist_ok=True)
    for unique,collapse in [(False,False),(True,False),(False,True),(True,True)]:
        r=run(rows,args.permutations,unique,collapse,args.known_period)
        name=f"unique{int(unique)}_collapse{int(collapse)}"
        (out/f"{name}.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
        print(json.dumps({k:v for k,v in r.items() if k!="stratum_audit"}),flush=True)


if __name__=="__main__": main()
