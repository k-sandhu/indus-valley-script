"""Exact synthetic mapping search with finite-reference uncertainty and bad anchors."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from itertools import permutations
import json
import math
from pathlib import Path
import time
import numpy as np
from scipy.special import gammaln

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "experiments/2026-10-02-six-hour/anchor-benchmark/main/code_snapshot.py"
spec = importlib.util.spec_from_file_location("crypto02_frozen", FROZEN)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
K = generator.K

def fixed_fit(reference_counts):
    starts,pairs,_ = reference_counts
    return (np.log2((starts+1)/(starts.sum()+K)),
            np.log2((pairs+1)/(pairs.sum(axis=1,keepdims=True)+K)), None)

def integrated_score(observed, reference, maps):
    starts,pairs,_ = observed
    rs,rp,_ = reference
    values = np.full(len(maps),gammaln(rs.sum()+K)-gammaln(rs.sum()+starts.sum()+K))
    for first in range(K):
        mapped = maps[:,first]
        values += gammaln(rs[mapped]+starts[first]+1)-gammaln(rs[mapped]+1)
        total = pairs[first].sum()
        if not total:
            continue
        row_totals = rp.sum(axis=1)
        values += gammaln(row_totals[mapped]+K)-gammaln(row_totals[mapped]+total+K)
        for second in range(K):
            count = pairs[first,second]
            if count:
                prior = rp[mapped,maps[:,second]]+1
                values += gammaln(prior+count)-gammaln(prior)
    return values / math.log(2)

def direct_predictive(texts, reference, mapping):
    starts,pairs,_ = (arr.copy() for arr in reference)
    score = 0.0
    for text in texts:
        mapped = [int(mapping[i]) for i in text]
        first = mapped[0]
        score += math.log2((starts[first]+1)/(starts.sum()+K))
        starts[first] += 1
        for a,b in zip(mapped,mapped[1:]):
            score += math.log2((pairs[a,b]+1)/(pairs[a].sum()+K))
            pairs[a,b] += 1
    return score

def update_reference(reference, observed, mapping):
    rs,rp,ru = (arr.copy() for arr in reference)
    starts,pairs,uni = observed
    rs[mapping] += starts
    ru[mapping] += uni
    rp[np.ix_(mapping,mapping)] += pairs
    return rs,rp,ru

def checks(maps):
    system = generator.system(680391,"transition")
    reference = generator.counts(generator.sample(system,71,680392))
    texts = generator.sample(system,19,680393)
    chosen = maps[[0,146,17319,40291]]
    vector = integrated_score(generator.counts(texts),reference,chosen)
    direct = np.asarray([direct_predictive(texts,reference,mapping) for mapping in chosen])
    rename = np.array([2,5,0,7,1,6,4,3])
    transformed = integrated_score(generator.counts(generator.encode(texts,rename)),reference,chosen[:,np.argsort(rename)])
    updated = update_reference(reference,generator.counts(texts),chosen[1])
    tests = generator.sample(system,7,680394)
    held = integrated_score(generator.counts(tests),updated,chosen[1:2])[0]
    compound = direct_predictive(texts+tests,reference,chosen[1])-direct_predictive(texts,reference,chosen[1])
    scores = integrated_score(generator.counts(texts),reference,maps)
    mass = np.exp2(scores-scores.max()); mass /= mass.sum()
    out = {"integrated_vector_equals_direct_sequential_prediction":bool(np.allclose(vector,direct,rtol=0,atol=1e-9)),
           "consistent_observed_renaming_preserves_score":bool(np.allclose(vector,transformed,rtol=0,atol=1e-9)),
           "mapped_count_update_matches_complete_predictive_score":bool(abs(held-compound)<1e-9),
           "mapping_mass_normalizes":bool(abs(mass.sum()-1)<1e-12),
           "all_eight_symbol_permutations_enumerated":len(maps)==math.factorial(K)}
    if not all(out.values()):
        raise AssertionError(out)
    return out

def run(args):
    start = time.perf_counter()
    output = ROOT/args.output
    target = output/"results.json"
    if target.exists():
        raise RuntimeError(f"Refusing completed endpoint: {target}")
    protocol = output.parent/"PROTOCOL.md"
    if not protocol.is_file():
        raise RuntimeError("Copy the protocol into the fresh output directory's parent before running.")
    maps = np.asarray(list(permutations(range(K))),dtype=np.int8)
    verification = checks(maps)
    reps = 2 if args.pilot else args.repetitions
    ref_sizes = [40,400] if args.pilot else [40,400,4000]
    train_sizes = [40,160] if args.pilot else [40,160,640]
    rows = []
    for family_i,family in enumerate(("transition","administrative_form")):
        for repeat in range(reps):
            seed = args.seed + 100000*family_i + 1000*repeat
            system = generator.system(seed,family)
            reference_texts = generator.sample(system,4000,seed+1)
            references = {n:generator.counts(reference_texts[:n]) for n in ref_sizes}
            rng = np.random.default_rng(seed+4)
            encoding = rng.permutation(K)
            truth = np.argsort(encoding)
            order = rng.permutation(K)
            bad = truth.copy()
            bad[order[1]],bad[order[2]] = bad[order[2]],bad[order[1]]
            conditions = {"none":maps,
                          "two_correct":maps[np.all(maps[:,order[:2]]==truth[order[:2]],axis=1)],
                          "one_correct_one_wrong":maps[np.all(maps[:,order[:2]]==bad[order[:2]],axis=1)]}
            assert len(conditions["two_correct"]) == len(conditions["one_correct_one_wrong"]) == math.factorial(K-2)
            assert not np.any(np.all(conditions["one_correct_one_wrong"]==truth,axis=1))
            for shift in (0.0,.35):
                training_texts = generator.encode(generator.sample(system,640,seed+2,shift),encoding)
                test_texts = generator.encode(generator.sample(system,400,seed+3,shift),encoding)
                test_counts = generator.counts(test_texts)
                test_tokens = sum(map(len,test_texts))
                for train_n in train_sizes:
                    train = generator.counts(training_texts[:train_n])
                    for ref_n,reference in references.items():
                        fixed = fixed_fit(reference)
                        for condition,permitted in conditions.items():
                            for model in ("plugin","integrated"):
                                scores = generator.score_maps(train,fixed,permitted,"markov") if model=="plugin" else integrated_score(train,reference,permitted)
                                ranked = np.argsort(-scores,kind="stable")
                                best = permitted[ranked[0]]
                                denominator = float(np.exp2(scores-scores[ranked[0]]).sum())
                                allowed = np.flatnonzero(np.all(permitted==truth,axis=1))
                                true_score = float(scores[allowed[0]]) if len(allowed) else None
                                if model == "plugin":
                                    held = float(generator.score_maps(test_counts,fixed,best[None,:],"markov")[0])
                                else:
                                    held = float(integrated_score(test_counts,update_reference(reference,train,best),best[None,:])[0])
                                rows.append({"family":family,"repeat":repeat,"seed":seed,"reference_texts":ref_n,
                                             "training_texts":train_n,"test_texts":400,"domain_shift":shift,"anchor_condition":condition,
                                             "model":model,"permitted_maps":len(permitted),"truth_permitted":bool(len(allowed)),
                                             "exact_mapping_recovered":bool(np.array_equal(best,truth)),"symbol_mapping_accuracy":float(np.mean(best==truth)),
                                             "best_map_mass":1/denominator,"true_map_mass":float(np.exp2(true_score-scores[ranked[0]])/denominator) if len(allowed) else 0.0,
                                             "true_mapping_rank_min":int(np.count_nonzero(scores>true_score+1e-9)+1) if len(allowed) else None,
                                             "training_margin_bits":float(scores[ranked[0]]-scores[ranked[1]]),
                                             "heldout_bits_per_sign":-held/test_tokens,"best_map":best.tolist(),"true_map":truth.tolist(),
                                             "anchor_pairs":[] if condition=="none" else [[int(i),int((truth if condition=="two_correct" else bad)[i])] for i in order[:2]]})
            print(json.dumps({"family":family,"systems_completed":repeat+1,"rows":len(rows)}),flush=True)
    result = {"experiment_id":"CRYPTO-03","status":"synthetic-pilot" if args.pilot else "declared-synthetic-grid",
              "parameters":vars(args),"integrity_checks":verification,"generated_systems":2*reps,"trial_count":len(rows),
              "elapsed_seconds":time.perf_counter()-start,"code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "generator_sha256":hashlib.sha256(FROZEN.read_bytes()).hexdigest(),"protocol_sha256":hashlib.sha256(protocol.read_bytes()).hexdigest(),
              "trials":rows,"sample_structure":"Reference/training sizes are nested prefixes; shifts, anchors and models share generated systems and test streams."}
    output.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    (output/"code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps({"output":str(target),"rows":len(rows),"seconds":result["elapsed_seconds"]}),flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    parser.add_argument("--repetitions",type=int,default=12)
    parser.add_argument("--seed",type=int,default=310261002)
    parser.add_argument("--output",default="experiments/2026-10-02-six-hour/reference-uncertainty/main")
    run(parser.parse_args())
