"""Independent arithmetic and input-isolation checks for khipu endpoints.

Rank uses Gram determinants, rather than the decoder's row reduction. Positive
witnesses and negative certificates are checked against the original equations.
"""
from __future__ import annotations
import argparse
import ast
import collections
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from html.parser import HTMLParser
import itertools
import json
import math
from pathlib import Path
import random
import shutil

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

def determinant(matrix):
    """Independent Leibniz determinant, with at most four rows."""
    n=len(matrix)
    if n==0:
        return 1
    answer=0
    for permutation in itertools.permutations(range(n)):
        inversions=sum(permutation[i]>permutation[j] for i in range(n) for j in range(i+1,n))
        product=math.prod(matrix[i][permutation[i]] for i in range(n))
        answer+=(-1 if inversions%2 else 1)*product
    return answer

def rank(matrix,columns):
    if not matrix:
        return 0
    integral=[]
    for row in matrix:
        values=[Fraction(x) for x in row]
        multiple=math.lcm(*(x.denominator for x in values))
        integral.append([int(x*multiple) for x in values])
    gram=[[sum(row[i]*row[j] for row in integral) for j in range(columns)] for i in range(columns)]
    for size in range(columns,0,-1):
        for subset in itertools.combinations(range(columns),size):
            minor=[[gram[i][j] for j in subset] for i in subset]
            if determinant(minor)!=0:
                return size
    return 0

def dot(row,vector):
    return sum(Fraction(a)*Fraction(b) for a,b in zip(row,vector))

def check_certificate(equations,anchor,inferred):
    dimension=len(anchor)
    augmented=[row+[0] for row in equations]+[anchor+[1]]
    reduced=[list(map(Fraction,row)) for row in inferred["rref"]]
    assert all(len(row)==dimension+1 for row in reduced)
    h_rank=rank(equations,dimension)
    a_rank=rank([row[:dimension] for row in augmented],dimension)
    ab_rank=rank(augmented,dimension+1)
    assert h_rank==inferred["rank_homogeneous"]
    assert a_rank==inferred["rank_anchored"]
    assert rank(reduced,dimension+1)==ab_rank
    assert rank(augmented+reduced,dimension+1)==ab_rank
    pivots=inferred["pivots"]
    assert len(pivots)==a_rank and pivots==sorted(pivots)
    for i,pivot in enumerate(pivots):
        assert reduced[i][pivot]==1
        assert all(reduced[j][pivot]==0 for j in range(len(reduced)) if j!=i)
    witnesses=[list(map(Fraction,row)) for row in inferred["witnesses"]]
    for witness in witnesses:
        assert all(x>0 for x in witness)
        assert all(dot(row,witness)==0 for row in equations)
        assert dot(anchor,witness)==1
    status=inferred["status"]
    if status=="unique_positive":
        assert a_rank==dimension and ab_rank==a_rank and len(witnesses)==1
    elif status=="ambiguous_positive":
        assert a_rank<dimension and ab_rank==a_rank and len(witnesses)==2 and witnesses[0]!=witnesses[1]
    elif status=="no_positive_solution":
        assert not witnesses
        reason=inferred["reason"]
        if reason=="inconsistent_count_anchor":
            assert ab_rank>a_rank
        elif reason=="unique_affine_solution_is_not_positive":
            assert a_rank==ab_rank==dimension
            solution=[Fraction(0)]*dimension
            for i,pivot in enumerate(pivots):
                solution[pivot]=reduced[i][dimension]
            assert all(dot(row,solution)==rhs for row,rhs in [(x[:dimension],x[dimension]) for x in augmented])
            assert any(x<=0 for x in solution)
        elif reason=="fixed_nonpositive_coordinate":
            free=[x for x in range(dimension) if x not in pivots]
            assert any(all(row[j]==0 for j in free) and row[dimension]<=0 for row in reduced[:len(pivots)])
        elif reason=="empty_open_positive_interval":
            assert ab_rank==a_rank and a_rank==dimension-1
            free=[x for x in range(dimension) if x not in pivots]
            assert len(free)==1
            coordinate=free[0]
            constants=[Fraction(0)]*dimension;slopes=[Fraction(0)]*dimension;slopes[coordinate]=1
            for i,pivot in enumerate(pivots):
                constants[pivot]=reduced[i][dimension];slopes[pivot]=-reduced[i][coordinate]
            lower=[-c/s for c,s in zip(constants,slopes) if s>0]
            upper=[-c/s for c,s in zip(constants,slopes) if s<0]
            assert lower and upper and max(lower)>=min(upper)
        else:
            raise AssertionError(reason)
    else:
        raise AssertionError(status)
    return h_rank,a_rank,ab_rank

class PreText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.blocks=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=="pre":
            assert self.current is None;self.current=[]
    def handle_endtag(self,tag):
        if tag=="pre" and self.current is not None:
            self.blocks.append("".join(self.current));self.current=None
    def handle_data(self,data):
        if self.current is not None:
            self.current.append(data)

def source_verify():
    inp=json.loads((RAW/"source-component-input.json").read_text(encoding="utf-8"))
    key=json.loads((RAW/"source-evaluator-key.json").read_text(encoding="utf-8"))
    parser=PreText();parser.feed((RAW/"kfg-puruchuco.html").read_text(encoding="utf-8"))
    matching=[x for x in parser.blocks if x.startswith("subunit_c  (20)")]
    assert len(matching)==1
    lines=matching[0].splitlines()[:3]
    recovered={line.split()[0].split("_")[1]:[int(x) for x in line.split(")",1)[1].strip().split(",")] for line in lines}
    assert inp["rows"]==[recovered[x] for x in "abc"]
    matching=[x for x in parser.blocks if x.startswith("(20)  0, 0, 1, 0, 19")]
    assert len(matching)==1
    assert key["targets"]==[int(x) for x in matching[0].splitlines()[0].split(")",1)[1].strip().split(",")]
    flat=[x for row in inp["rows"] for x in row]
    predictions=read_lines(RAW/"source-predictions.jsonl")
    scores=read_lines(RAW/"source-scores.jsonl")
    counts=collections.Counter();total_errors=set();published=None
    hist=collections.defaultdict(collections.Counter)
    records=0
    for prediction,score in itertools.zip_longest(predictions,scores):
        assert prediction is not None and score is not None
        assert prediction["method"]==score["method"] and prediction["replicate"]==score["replicate"]
        orders=prediction["orders"]
        assert len(orders)==3 and all(len(row)==20 for row in orders)
        assert sorted(x for row in orders for x in row)==list(range(60))
        output=[]
        for position in range(20):
            value=0
            for row in orders:
                value+=flat[row[position]]
            output.append(value)
        assert output==prediction["prediction"]
        residual=[output[i]-key["targets"][i] for i in range(20)]
        assert residual==score["residual"]
        expected={"exact_columns":20-sum(x!=0 for x in residual),"absolute_error":sum(abs(x) for x in residual),
                  "signed_total_error":sum(output)-sum(key["targets"]),"complete_vector_equal":output==key["targets"]}
        assert expected==score["scores"]
        if prediction["method"]=="published_order":
            published=output
        if prediction["method"]=="ordered_flat_known_dimensions":
            assert output==published
        counts[prediction["method"]]+=1;total_errors.add(expected["signed_total_error"])
        hist[prediction["method"]][expected["absolute_error"]]+=1
        records+=1
    aggregate=json.loads((OUT/"source-aggregate.json").read_text(encoding="utf-8"))
    for method,frequencies in hist.items():
        assert {str(k):v for k,v in frequencies.items()}==aggregate["methods"][method]["absolute_error_histogram"]
    assert records==20411 and sum(flat)==3498 and sum(key["targets"])==3482 and total_errors=={16}
    result={"created_utc":datetime.now(timezone.utc).isoformat(),"passed":True,"predictions_checked":records,
            "methods":dict(counts),"independent_source_parser":"stdlib HTMLParser; direct integer parsing",
            "independent_sum":"nested scalar loops over recorded permutations",
            "grand_total_source":sum(flat),"grand_total_target":sum(key["targets"]),
            "all_permutations_have_same_total_error":True,"known_dimension_flattening_invariance":True,
            "prediction_sha256":sha(RAW/"source-predictions.jsonl"),"score_sha256":sha(RAW/"source-scores.jsonl")}
    save(OUT/"source-verification.json",result);print(json.dumps(result,indent=2))

def static_isolation():
    tree=ast.parse((ROOT/"src/six_hour/khipu_control.py").read_text(encoding="utf-8"))
    functions={x.name:x for x in tree.body if isinstance(x,ast.FunctionDef)}
    allowed={"source_predictions","column_sum","exact_decoder","rref","fraction_strings","represent"}
    forbidden={"open","read_text","read_bytes","loads","load","make_world"}
    checked=[]
    for name in sorted(allowed):
        for node in ast.walk(functions[name]):
            if isinstance(node,ast.Call):
                if isinstance(node.func,ast.Name):
                    assert node.func.id not in forbidden,(name,node.func.id)
                elif isinstance(node.func,ast.Attribute):
                    assert node.func.attr not in forbidden,(name,node.func.attr)
        checked.append(name)
    decoder=functions["exact_decoder"]
    assert [x.arg for x in decoder.args.args]==["equations","anchor"]
    return {"checked_functions":checked,"decoder_arguments":["equations","anchor"],
            "file_or_key_reads_in_checked_predictors":False,"scope":"static call inspection plus saved input projection; no OS-level filesystem sandbox"}

def synthetic_verify():
    from scipy.optimize import linprog
    import numpy as np
    endpoint=OUT/"endpoints/main-v1"
    inputs={x["id"]:x for x in read_lines(endpoint/"component-inputs.jsonl")}
    keys={x["id"]:x["key"] for x in read_lines(endpoint/"evaluator-key.jsonl")}
    evaluations=read_lines(endpoint/"evaluated-prefixes.jsonl")
    rows=list(read_lines(endpoint/"inferred-prefixes.jsonl"))
    sample=set(random.Random(2026100203).sample(range(len(rows)),512))
    lp_counts=collections.Counter();ranks=collections.Counter();statuses=collections.Counter()
    sibling={};witness_count=0;checked=0
    for index,(record,evaluation) in enumerate(itertools.zip_longest(rows,evaluations)):
        assert record is not None and evaluation is not None
        component=inputs[record["input_id"]]["component"]
        equations=component["equations"][:record["prefix"]]
        assert equations==record["supplied_equations"]
        inferred=record["inferred"]
        rank_tuple=check_certificate(equations,component["anchor"],inferred)
        ranks[str(rank_tuple)]+=1;statuses[inferred["status"]]+=1
        witness_count+=len(inferred["witnesses"])
        assert record["input_id"]==evaluation["input_id"] and record["prefix"]==evaluation["prefix"]
        if inferred["status"]=="unique_positive":
            weights=list(map(Fraction,inferred["witnesses"][0]));quantities=keys[record["world_id"]]["quantities"]
            independently_correct=all(dot(features,weights)==qty for features,qty in zip(component["features"],quantities))
            assert independently_correct==evaluation["evaluation"]["correct_unique_decoder"]
            assert (not independently_correct)==evaluation["evaluation"]["false_unique_decoder"]
        else:
            assert not evaluation["evaluation"]["correct_unique_decoder"] and not evaluation["evaluation"]["false_unique_decoder"]
        if record["representation"] in ("full","sibling_shuffle"):
            pair=(record["world_id"],record["prefix"])
            fingerprint=(equations,inferred,evaluation["evaluation"])
            if record["representation"]=="full":
                sibling[pair]=fingerprint
            else:
                assert sibling[pair]==fingerprint
        if index in sample:
            d=len(component["anchor"])
            # Independent continuous feasibility: maximize a common positive margin.
            eq=np.array([row+[0] for row in equations]+[component["anchor"]+[0]],dtype=float)
            rhs=np.array([0]*len(equations)+[1],dtype=float)
            inequalities=[[-int(i==j) for i in range(d)]+[1] for j in range(d)]
            answer=linprog([0]*d+[-1],A_ub=inequalities,b_ub=[0]*d,A_eq=eq,b_eq=rhs,
                           bounds=[(0,None)]*(d+1),method="highs")
            positive=answer.success and answer.x[-1]>1e-8
            assert positive==(inferred["status"]!="no_positive_solution"),(record,answer.message)
            lp_counts[inferred["status"]]+=1
        checked+=1
    assert checked==36000
    result={"created_utc":datetime.now(timezone.utc).isoformat(),"passed":True,"prefix_records_checked":checked,
            "exact_rank_method":"Gram matrix principal minors; Leibniz determinants over integers",
            "row_space_check":"original augmented equations and saved reduced rows have identical exact rank and combined rank",
            "positive_witnesses_checked":witness_count,"negative_certificates":"inconsistent augmented rank, nonpositive fixed solution or empty strict interval",
            "status_counts":dict(statuses),"rank_counts":dict(ranks),"sibling_prefix_pairs_checked":len(sibling),
            "independent_lp_check":{"sample_size":512,"seed":2026100203,"statuses":dict(lp_counts),"scipy_version":__import__('scipy').__version__,"passed":True},
            "input_isolation":static_isolation(),"inferred_sha256":sha(endpoint/"inferred-prefixes.jsonl"),
            "evaluated_sha256":sha(endpoint/"evaluated-prefixes.jsonl")}
    save(endpoint/"verification.json",result);print(json.dumps(result,indent=2))

def freeze():
    source=OUT/"endpoints/source-v1"
    if source.exists():
        raise FileExistsError(source)
    source.mkdir(parents=True)
    files=("PROTOCOL.md","PROTOCOL_PREFIX.md","protocol-freeze.json","prefix-protocol-freeze.json","acquisition.json","acquisition-supplement-01.json","coverage-audit.json","source-input-manifest.json","source-prediction-manifest.json","source-aggregate.json","source-verification.json")
    for filename in files:
        shutil.copyfile(OUT/filename,source/filename)
    code=("khipu_acquire.py","khipu_source.py","khipu_control.py","khipu_evaluate.py","khipu_verify.py")
    for endpoint in (source,OUT/"endpoints/main-v1"):
        assert not (endpoint/"freeze-manifest.json").exists()
        assert (endpoint/("source-verification.json" if endpoint==source else "verification.json")).exists()
        for filename in code:
            destination=endpoint/filename
            original=ROOT/"src/six_hour"/filename
            if destination.exists():
                assert sha(destination)==sha(original)
            else:
                shutil.copyfile(original,destination)
        records=[{"path":p.relative_to(endpoint).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(endpoint.rglob('*')) if p.is_file()]
        save(endpoint/"freeze-manifest.json",{"frozen_utc":datetime.now(timezone.utc).isoformat(),"files":records,
              "files_count":len(records),"total_bytes":sum(x["bytes"] for x in records),
              "protocol_snapshot_links":"resolve against the original khipu-control protocol directory"})
        print(endpoint.name,len(records),sum(x["bytes"] for x in records))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("command",choices=["source","synthetic","freeze"]);a=p.parse_args()
    {"source":source_verify,"synthetic":synthetic_verify,"freeze":freeze}[a.command]()
