"""Training-only, artifact/whole-text-held-out missing-slot glyph suggestion.

Catalogue IDs are graphic identifiers. No sound or meaning is assigned.
Real damaged sections do not necessarily contain exactly one sign.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from methods.conditional_structure import Model, UNKNOWN, load_records, group_records, make_folds

ROOT=Path(__file__).resolve().parents[1]
GRID=[20,100,500,2000]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Restorer:
    def __init__(self,rows,alpha):
        self.model=Model(rows,alpha)
        m=self.model
        self.ratio=np.asarray([m.smooth(m.bigram.get(i,{}),m.unigram)/m.unigram
                              for i in range(len(m.signs))])
        self.z={}

    def distribution(self,row,i,bidirectional=False):
        """The masked true sign at i is never inspected."""
        m=self.model; seq=row["seq"]; length=len(seq); stratum=row["stratum"]
        p,pm,pmb=m.distributions(length,i,stratum,seq[i-1] if i else None)
        if not bidirectional: return pm
        score=pmb.copy()
        if i+1<length:
            next_index=m.index.get(seq[i+1],m.index[UNKNOWN])
            key=(length,i+1,stratum)
            if key not in self.z:
                _,next_pm,_=m.distributions(length,i+1,stratum,None)
                self.z[key]=self.ratio@next_pm
            # next_pm[next_index] is common to every candidate and cancels.
            score*=self.ratio[:,next_index]/self.z[key]
        return score/score.sum()

    def score_rows(self,rows,bidirectional=False,details=False):
        output=[]
        m=self.model
        for r in rows:
            for i,actual in enumerate(r["seq"]):
                prob=self.distribution(r,i,bidirectional)
                rank=np.argsort(-prob,kind="stable")
                ordered=[m.signs[j] for j in rank]
                known=actual in m.index
                actual_index=m.index.get(actual,m.index[UNKNOWN])
                item={"record_id":r["record_id"],"artifact":r["artifact"],
                      "slot":i,"length":len(r["seq"]),"actual":actual,
                      "position":"initial" if i==0 else "final" if i==len(r["seq"])-1 else "internal",
                      "known_in_training":known,"top1":ordered[0]==actual,
                      "top5":actual in ordered[:5],"top10":actual in ordered[:10],
                      "model_top_mass":float(prob[rank[0]]),"top_is_unknown":ordered[0]==UNKNOWN,
                      "bucket_loss_bits":-math.log2(float(prob[actual_index]))}
                if details:
                    item["suggestions"]=[{"code":m.signs[j],"model_mass":float(prob[j])} for j in rank[:10]]
                    item["site"]=r.get("site");item["object_type"]=r.get("object_type")
                output.append(item)
        return output


def summary(scores):
    def subset(ss):
        return {"slots":len(ss),"top1":float(np.mean([s["top1"] for s in ss])),
                "top5":float(np.mean([s["top5"] for s in ss])),
                "top10":float(np.mean([s["top10"] for s in ss])),
                "unknown_true_rate":float(np.mean([not s["known_in_training"] for s in ss])),
                "unknown_prediction_rate":float(np.mean([s["top_is_unknown"] for s in ss])),
                "bucket_cross_entropy_bits":float(np.mean([s["bucket_loss_bits"] for s in ss]))}
    result=subset(scores)
    text_scores=defaultdict(list)
    for score in scores:text_scores[score['record_id']].append(score)
    result['equal_text_weight']={k:float(np.mean([np.mean([s[k] for s in ss])
                                    for ss in text_scores.values()])) for k in ['top1','top5','top10']}
    result['equal_text_weight']['texts']=len(text_scores)
    result["positions"]={p:subset([s for s in scores if s["position"]==p])
                         for p in ["initial","internal","final"]}
    bins=[(0.,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1.000001)]
    result["confidence_audit"]=[]
    for a,b in bins:
        ss=[s for s in scores if a<=s["model_top_mass"]<b]
        result["confidence_audit"].append({"mass_interval":[a,min(b,1.)],"slots":len(ss),
           "mean_model_mass":float(np.mean([s["model_top_mass"] for s in ss])) if ss else None,
           "exact_accuracy":float(np.mean([s["top1"] for s in ss])) if ss else None})
    return result


def choose_alpha(train,seed):
    groups=group_records(train);assignment,_=make_folds(train,groups,3,seed)
    counts={name:{alpha:[0,0] for alpha in GRID} for name in ["baseline","local"]}
    for f in range(3):
        fit=[r for i,r in enumerate(train) if assignment[i]!=f]
        test=[r for i,r in enumerate(train) if assignment[i]==f]
        for alpha in GRID:
            model=Restorer(fit,alpha)
            for name,bi in [("baseline",False),("local",True)]:
                scores=model.score_rows(test,bi)
                counts[name][alpha][0]+=sum(s["top1"] for s in scores)
                counts[name][alpha][1]+=len(scores)
    accuracy={name:{str(a):c[0]/c[1] for a,c in values.items()} for name,values in counts.items()}
    chosen={name:max(GRID,key=lambda a:(counts[name][a][0]/counts[name][a][1],a))
            for name in counts}
    return chosen,accuracy


def paired_ci(base,local,group_lookup,seed=142,repeats=10000,text_equal=False):
    sums=defaultdict(lambda:np.zeros(2))
    for a,b in zip(base,local):
        assert (a["record_id"],a["slot"])==(b["record_id"],b["slot"])
        weight=1/a['length'] if text_equal else 1.
        sums[group_lookup[a["record_id"]]]+=weight*np.asarray([int(b["top1"])-int(a["top1"]),1])
    arr=np.asarray(list(sums.values()));rng=np.random.default_rng(seed);samples=[]
    for start in range(0,repeats,250):
        ix=rng.integers(0,len(arr),size=(min(250,repeats-start),len(arr)))
        draws=arr[ix].sum(axis=1);samples.extend((draws[:,0]/draws[:,1]).tolist())
    return {"gain_accuracy":float(arr[:,0].sum()/arr[:,1].sum()),
            "cluster_bootstrap_95_ci":np.quantile(samples,[.025,.975]).tolist(),
            "clusters":len(arr),"bootstrap":repeats}


def external_audit(rows,seed,collapse=None):
    path=ROOT/"research/corpus/plate_audit/comparisons.json"
    if not path.exists(): return {"status":"no primary audit available"},{}
    audited=json.loads(path.read_text(encoding="utf-8"))
    identifiers={ident for item in audited if item.get("any_candidate_compatible")
                 for ident in item.get("compatible_lipi_ids",[])}
    # Unique dedup may have chosen another copy. Resolve primary IDs first.
    allrows,_=load_records(ROOT/"data/normalized/lipi_clean_rtl_singleline.jsonl",min_length=3,collapse=collapse)
    test=[r for r in allrows if r["record_id"] in identifiers]
    sequences={r["seq"] for r in test}; artifacts={r["artifact"] for r in test}
    # Conservatively remove connected artifact/text components containing a test text.
    groups=group_records(rows)
    excluded={i for g in groups if any(rows[i]["seq"] in sequences or
              set(rows[i].get("artifact_aliases",[rows[i]["artifact"]])) & artifacts
              for i in g) for i in g}
    train=[r for i,r in enumerate(rows) if i not in excluded]
    chosen,inner=choose_alpha(train,seed)
    scores={name:Restorer(train,chosen[name]).score_rows(test,name=="local",True)
            for name in ["baseline","local"]}
    result={"source_audit_cases":len(audited),"compatible_primary_texts_length3plus":len(test),
            "test_record_ids":[r["record_id"] for r in test],"training_unique_texts":len(train),
            "removed_training_texts":len(excluded),"chosen_alpha":chosen,"inner_accuracy":inner,
            "models":{name:summary(ss) for name,ss in scores.items()},
            "limitation":"Nonrandom primary-photo compatibility sample; catalogue-family compatibility is weaker than fine-glyph identity. This is a source check, not independent population validation."}
    assert not ({r["seq"] for r in train}&sequences)
    assert not ({a for r in train for a in r.get("artifact_aliases",[r["artifact"]])}&artifacts)
    return result,scores


def benchmark(args):
    started=time.monotonic();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
    inp=ROOT/"data/normalized/lipi_clean_rtl_singleline.jsonl"
    collapse=json.loads(Path(args.collapse).read_text())['mapping'] if args.collapse else None
    rows,exclusions=load_records(inp,min_length=3,unique=True,collapse=collapse)
    groups=group_records(rows); assignment,loads=make_folds(rows,groups,5,args.seed)
    lookup={rows[i]["record_id"]:g for g,ix in enumerate(groups) for i in ix}
    scores={"baseline":[],"local":[]};folds=[]
    for f in range(5):
        train=[r for i,r in enumerate(rows) if assignment[i]!=f]
        test=[r for i,r in enumerate(rows) if assignment[i]==f]
        chosen,inner=choose_alpha(train,args.seed+f)
        for name in scores:
            ss=Restorer(train,chosen[name]).score_rows(test,name=="local",True)
            for s in ss:s["fold"]=f;s["group"]=lookup[s["record_id"]]
            scores[name].extend(ss)
        folds.append({"fold":f,"train_texts":len(train),"test_texts":len(test),
                      "chosen_alpha":chosen,"inner_top1":inner})
        print(json.dumps({"stage":"restoration_fold","fold":f,"chosen_alpha":chosen,
                          "seconds":time.monotonic()-started}),flush=True)
    result={"interpretation":"Masked graphic-code prediction. No semantic or phonetic values.",
            "input_sha256":sha(inp),"source_sha256":sha(__file__),
            "model_dependency_sha256":sha(ROOT/"src/methods/conditional_structure.py"),
            "parameters":vars(args),"collapse_mapping":collapse,
            "unique_texts":len(rows),"artifact_text_groups":len(groups),"exclusions":exclusions,
            "smoothing_grid":GRID,"fold_token_loads":loads,"folds":folds,
            "models":{name:summary(ss) for name,ss in scores.items()},
            "paired_gain":paired_ci(scores["baseline"],scores["local"],lookup),
            "equal_text_weight_paired_gain":paired_ci(scores['baseline'],scores['local'],lookup,text_equal=True),
            "missing_slot_assumption":"Exactly one missing glyph with correct surviving transcription and line length.",
            "confidence_warning":"Normalized model masses are not calibrated probabilities of historical correctness.",
            "oov_warning":"Unseen fine glyphs count as failed predictions; descriptive cross-entropy pools them in UNKNOWN."}
    for name,ss in scores.items():
        (out/f"{name}_slot_audit.jsonl").write_text("\n".join(json.dumps(s) for s in ss),encoding="utf-8")
    (out/"benchmark.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    external,external_scores=external_audit(rows,args.seed+75,collapse)
    result["external_source_check"]=external;result["runtime_seconds"]=time.monotonic()-started
    (out/"benchmark.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    (out/"external_slot_audit.json").write_text(json.dumps(external_scores,indent=2),encoding="utf-8")
    print(json.dumps({"stage":"restoration_complete","models":result["models"],
                      "paired_gain":result["paired_gain"],"external":external,
                      "seconds":result["runtime_seconds"]}),flush=True)


def predict(args):
    if not args.sequence:raise ValueError('Supply --sequence with comma-separated codes and one ?')
    seq=[s.strip() for s in args.sequence.split(",")]
    if seq.count("?")!=1: raise ValueError("Supply exactly one known missing slot as '?' in reading order")
    if any(s in {"000","999"} for s in seq):
        raise ValueError("An eroded span or blank is not a verified one-glyph missing slot")
    rows,_=load_records(ROOT/"data/normalized/lipi_clean_rtl_singleline.jsonl",min_length=3,unique=True)
    forbidden=set(args.exclude_artifact)
    groups=group_records(rows)
    removed={i for g in groups if any(forbidden.intersection(rows[i].get('artifact_aliases',[rows[i]['artifact']]))
                                     for i in g) for i in g}
    rows=[r for i,r in enumerate(rows) if i not in removed]
    model=Restorer(rows,args.alpha)
    r={"seq":seq,"stratum":(args.site,args.type)}
    p=model.distribution(r,seq.index("?"),True);rank=np.argsort(-p,kind="stable")
    print(json.dumps({"assumption":"Exactly one missing glyph; remaining codes and reading order are correct.",
          "interpretation":"Graphic suggestions only. Model mass is not confidence in a decipherment.",
          "training":"All local unique complete RTL texts; query may overlap known texts, so suggestions are exploratory.",
          "excluded_artifact_ids":sorted(forbidden),"removed_training_texts":len(removed),
          "suggestions":[{"code":model.model.signs[j],"model_mass":float(p[j])} for j in rank[:10]]},indent=2))


def crosssite(args):
    inp=ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'
    unique,_=load_records(inp,min_length=3,unique=True)
    allrows,_=load_records(inp,min_length=3)
    groups=group_records(unique);output=[]
    for site in ['Mohenjo-daro','Harappa','Lothal']:
        source=[r for r in allrows if r.get('site')==site]
        site_sequences={r['seq'] for r in source}
        site_artifacts={r['artifact'] for r in source}
        forbidden={i for g in groups if any(unique[i]['seq'] in site_sequences or
                   site_artifacts.intersection(unique[i].get('artifact_aliases',[unique[i]['artifact']]))
                   for i in g) for i in g}
        test=[r for r in unique if r.get('site')==site]
        train=[r for i,r in enumerate(unique) if i not in forbidden]
        assert not({r['seq'] for r in train}&site_sequences)
        assert not({a for r in train for a in r['artifact_aliases']}&site_artifacts)
        chosen,inner=choose_alpha(train,args.seed)
        scores={name:Restorer(train,chosen[name]).score_rows(test,name=='local',True)
                for name in ['baseline','local']}
        lookup={unique[i]['record_id']:g for g,ix in enumerate(groups) for i in ix}
        result={'site':site,'test_texts':len(test),'all_source_records_from_site':len(source),
                'training_texts':len(train),'excluded_training_texts':len(forbidden),
                'chosen_alpha':chosen,'inner_accuracy':inner,
                'models':{name:summary(ss) for name,ss in scores.items()},
                'paired_gain':paired_ci(scores['baseline'],scores['local'],lookup),
                'equal_text_weight_paired_gain':paired_ci(scores['baseline'],scores['local'],lookup,text_equal=True)}
        output.append(result)
        print(json.dumps({'site':site,'test_texts':len(test),'gain':result['paired_gain']}),flush=True)
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
    (out/'crosssite.json').write_text(json.dumps({'input_sha256':sha(inp),'source_sha256':sha(__file__),
        'model_dependency_sha256':sha(ROOT/'src/methods/conditional_structure.py'),
        'definition':'Test unique representatives, excluding every training component touched by ANY raw record from held-out site.',
        'limitations':'Representative metadata can discard cross-site copies; observed site selection and fitted bootstrap are conditional.',
        'results':output},indent=2),encoding='utf-8')


def main():
    ap=argparse.ArgumentParser();ap.add_argument("mode",choices=["benchmark","predict","crosssite"])
    ap.add_argument("--out",default="results/restoration");ap.add_argument("--seed",type=int,default=20261006)
    ap.add_argument("--sequence");ap.add_argument("--site",default="Mohenjo-daro")
    ap.add_argument("--type",default="SEAL:S");ap.add_argument("--alpha",type=float,default=20)
    ap.add_argument('--collapse');ap.add_argument('--exclude-artifact',action='append',default=[])
    args=ap.parse_args()
    if args.mode=="benchmark":benchmark(args)
    elif args.mode=='crosssite':crosssite(args)
    else:predict(args)


if __name__=="__main__":main()
