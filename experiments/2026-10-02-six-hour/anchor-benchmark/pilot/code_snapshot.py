"""Exact mapping search against a known synthetic reference and supplied anchors."""
from __future__ import annotations
import argparse
from itertools import permutations
from pathlib import Path
import hashlib
import json
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
K = 8

def system(seed, family):
    rng = np.random.default_rng(seed)
    if family == "transition":
        start = rng.dirichlet(np.full(K, .7))
        trans = rng.dirichlet(np.full(K, .35), size=K)
        trans += .45 * np.roll(np.eye(K), 1, axis=1)
        trans /= trans.sum(axis=1, keepdims=True)
        return {"family": family, "start": start, "trans": trans}
    slot = rng.dirichlet(np.full(K, .18), size=(2,3))
    for office in range(2):
        for phase, preferred in enumerate(((0,1,2),(3,4,5),(6,7))):
            slot[office, phase, list(preferred)] += .3
    slot /= slot.sum(axis=2, keepdims=True)
    return {"family": family, "slot": slot}

def sample(spec, n, seed, shift=0.0):
    rng = np.random.default_rng(seed)
    texts = []
    noise = np.arange(1,K+1,dtype=float)
    noise /= noise.sum()
    for _ in range(n):
        length = int(rng.integers(3,8))
        if spec["family"] == "transition":
            p = (1-shift)*spec["start"] + shift*noise
            text = [int(rng.choice(K,p=p))]
            for _ in range(length-1):
                p = (1-shift)*spec["trans"][text[-1]] + shift*noise
                text.append(int(rng.choice(K,p=p)))
        else:
            office = int(rng.integers(2))
            text = []
            for pos in range(length):
                phase = 0 if pos == 0 else 2 if pos == length-1 else 1
                p = (1-shift)*spec["slot"][office,phase] + shift*noise
                text.append(int(rng.choice(K,p=p)))
        texts.append(text)
    return texts

def counts(texts):
    starts = np.zeros(K)
    pairs = np.zeros((K,K))
    unigram = np.zeros(K)
    for text in texts:
        starts[text[0]] += 1
        for sign in text:
            unigram[sign] += 1
        for first,second in zip(text,text[1:]):
            pairs[first,second] += 1
    return starts,pairs,unigram

def fit(texts):
    starts,pairs,unigram = counts(texts)
    return (np.log2((starts+1)/(starts.sum()+K)),
            np.log2((pairs+1)/(pairs.sum(axis=1,keepdims=True)+K)),
            np.log2((unigram+1)/(unigram.sum()+K)))

def score_maps(observed, reference, maps, kind):
    starts,pairs,unigram = observed
    ls,lp,lu = reference
    values = np.zeros(len(maps))
    for first in range(K):
        if kind == "unigram":
            values += unigram[first] * lu[maps[:,first]]
        else:
            values += starts[first] * ls[maps[:,first]]
            for second in range(K):
                if pairs[first,second]:
                    values += pairs[first,second] * lp[maps[:,first],maps[:,second]]
    return values

def encode(texts, encoding):
    return [[int(encoding[sign]) for sign in text] for text in texts]

def run(args):
    started = time.perf_counter()
    all_maps = np.asarray(list(permutations(range(K))),dtype=np.int8)
    rows = []
    sizes = [40,160] if args.pilot else [40,160,640]
    repetitions = 2 if args.pilot else args.repetitions
    for family_i,family in enumerate(("transition","administrative_form")):
        for repeat in range(repetitions):
            seed = args.seed + family_i*100000 + repeat*1000
            spec = system(seed,family)
            wrong = system(seed+701,family)
            ref = fit(sample(spec,4000,seed+1))
            wrong_ref = fit(sample(wrong,4000,seed+2))
            rng = np.random.default_rng(seed+3)
            encoding = rng.permutation(K)
            truth = np.argsort(encoding)
            anchor_order = rng.permutation(K)
            for shift in (0.0,.35):
                test = encode(sample(spec,400,seed+4,shift),encoding)
                test_counts = counts(test)
                for n in sizes:
                    training = encode(sample(spec,n,seed+5+n,shift),encoding)
                    train_counts = counts(training)
                    for anchor_count in (0,1,2,4):
                        anchors = anchor_order[:anchor_count]
                        valid = np.all(all_maps[:,anchors] == truth[anchors],axis=1) if anchor_count else np.ones(len(all_maps),dtype=bool)
                        maps = all_maps[valid]
                        assert len(maps) == int(np.math.factorial(K-anchor_count)) if hasattr(np,"math") else len(maps) == __import__('math').factorial(K-anchor_count)
                        for kind in ("unigram","markov"):
                            scores = score_maps(train_counts,ref,maps,kind)
                            order = np.argsort(-scores,kind="stable")
                            best = maps[order[0]]
                            truth_index = int(np.flatnonzero(np.all(maps == truth,axis=1))[0])
                            true_score = float(scores[truth_index])
                            wrong_scores = score_maps(train_counts,wrong_ref,maps,kind)
                            wrong_best = maps[int(np.argmax(wrong_scores))]
                            heldout = float(score_maps(test_counts,ref,best[None,:],kind)[0])
                            wrong_heldout = float(score_maps(test_counts,wrong_ref,wrong_best[None,:],kind)[0])
                            row = {"family":family,"repeat":repeat,"seed":seed,"training_texts":n,"test_texts":400,
                                   "reference_texts":4000,"domain_shift":shift,"anchors":anchor_count,"model":kind,
                                   "compatible_maps":len(maps),"observed_training_symbols":int(np.count_nonzero(train_counts[2])),
                                   "symbol_mapping_accuracy":float(np.mean(best == truth)),"exact_mapping_recovered":bool(np.all(best == truth)),
                                   "true_mapping_rank_min":int(np.count_nonzero(scores > true_score+1e-10)+1),
                                   "true_mapping_rank_max":int(np.count_nonzero(scores >= true_score-1e-10)),
                                   "training_margin_bits":float(scores[order[0]]-scores[order[1]]) if len(order)>1 else None,
                                   "heldout_bits_per_sign":-heldout/sum(map(len,test)),
                                   "correct_reference_beats_wrong_on_holdout":heldout > wrong_heldout,
                                   "reference_heldout_gain_bits_per_sign":(heldout-wrong_heldout)/sum(map(len,test)),
                                   "best_map":best.tolist(),"true_map":truth.tolist(),
                                   "anchor_pairs":[[int(i),int(truth[i])] for i in anchors]}
                            rows.append(row)
        print(json.dumps({"completed_family":family,"trials":len(rows)}),flush=True)
    grouped = {}
    for row in rows:
        key = f"{row['family']}|n={row['training_texts']}|shift={row['domain_shift']}|anchors={row['anchors']}|{row['model']}"
        grouped.setdefault(key,[]).append(row)
    summary = []
    for key,group in grouped.items():
        summary.append({"condition":key,"repetitions":len(group),
                        "exact_mapping_rate":float(np.mean([r["exact_mapping_recovered"] for r in group])),
                        "mean_symbol_mapping_accuracy":float(np.mean([r["symbol_mapping_accuracy"] for r in group])),
                        "mean_true_rank_min":float(np.mean([r["true_mapping_rank_min"] for r in group])),
                        "correct_reference_selection_rate":float(np.mean([r["correct_reference_beats_wrong_on_holdout"] for r in group])),
                        "mean_heldout_gain_bits_per_sign":float(np.mean([r["reference_heldout_gain_bits_per_sign"] for r in group]))})
    result = {"experiment_id":"CRYPTO-02","status":"synthetic-pilot" if args.pilot else "declared-synthetic-grid",
              "parameters":vars(args),"symbol_count":K,"trial_count":len(rows),"elapsed_seconds":time.perf_counter()-started,
              "code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"trials":rows,"summary":summary,
              "assumptions":"Eight synthetic identities, bijective encoding, supplied known reference, correct external anchors; arithmetic scores and identity recovery are testable here."}
    output = ROOT / args.output
    output.mkdir(parents=True,exist_ok=True)
    target = output/"results.json"
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite completed endpoint: {target}")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"trials":len(rows),"seconds":result["elapsed_seconds"],"output":str(target)}),flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    parser.add_argument("--seed",type=int,default=20261002)
    parser.add_argument("--repetitions",type=int,default=12)
    parser.add_argument("--output",default="experiments/2026-10-02-six-hour/anchor-benchmark/main")
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()
