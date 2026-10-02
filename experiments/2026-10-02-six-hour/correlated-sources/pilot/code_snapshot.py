"""Enumerate mapping posteriors with copied and coupled source reports."""
import argparse
from datetime import datetime,timezone
import hashlib
from itertools import permutations,combinations
import json
import math
from pathlib import Path
import time
import types
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HELPER=ROOT/'experiments/2026-10-02-six-hour/reference-uncertainty/main/code_snapshot.py'
module=types.ModuleType('reference_frozen')
module.__file__=str(ROOT/'src/six_hour/reference_uncertainty.py')
exec(compile(HELPER.read_text(encoding='utf-8'),module.__file__,'exec'),module.__dict__)
K=8
SWAPS=[]
for i,j in combinations(range(K),2):
    swap=np.arange(K);swap[i],swap[j]=swap[j],swap[i];SWAPS.append(swap)

def coupled_probability(maps,codes,responses,q):
    selected=maps[:,codes]
    values=(1-q)*np.all(selected==responses,axis=1).astype(float)
    for swap in SWAPS:
        values+=(q/len(SWAPS))*np.all(swap[selected]==responses,axis=1)
    return values

def independent_loglikelihood(maps,codes,responses,q):
    matches=maps[:,codes]==responses
    return np.where(matches,math.log2(1-q/4),math.log2(q/28)).sum(axis=1)

def channel_checks():
    g=np.array([[4,1,6,0,7,3,5,2]])
    normalization=[]
    marginal=[]
    for q in [.1,.5]:
        for n in [1,2]:
            codes=np.arange(n)
            total=sum(float(coupled_probability(g,codes,np.array(y),q)[0]) for y in permutations(range(K),n))
            normalization.append(abs(total-1)<1e-12)
        for y in range(K):
            p=float(coupled_probability(g,np.array([2]),np.array([y]),q)[0])
            marginal.append(abs(p-(1-q/4 if y==g[0,2] else q/28))<1e-12)
    if not all(normalization+marginal):
        raise AssertionError('Channel law')
    return {'latent_source_states':29,'one_and_two_code_channel_normalizes':True,'single_code_marginal_matches_independent_model':True}

def summarize(scores,maps,truth):
    finite=np.isfinite(scores)
    if not finite.any():
        return {'compatible_maps':0,'selected_map':None,'selected_map_mass':None,'true_map_mass':0.0,'exact_mapping_recovered':False,'confident_wrong_selection':False}
    best_index=int(np.argmax(scores))
    weights=np.exp2(scores-scores[best_index]);weights/=weights.sum()
    candidate=maps[best_index]
    correct=bool(np.array_equal(candidate,truth))
    true_index=np.flatnonzero(np.all(maps==truth,axis=1))[0]
    return {'compatible_maps':int(finite.sum()),'selected_map':candidate.tolist(),'selected_map_mass':float(weights[best_index]),
            'true_map_mass':float(weights[true_index]),'exact_mapping_recovered':correct,'confident_wrong_selection':bool(not correct and weights[best_index]>=.95)}

def run(args):
    start=time.perf_counter();output=ROOT/args.output
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    protocol=output.parent/'PROTOCOL.md'
    maps=np.asarray(list(permutations(range(K))),dtype=np.int8)
    checks=channel_checks();rows=[];systems=[];claims=[]
    reps=2 if args.pilot else args.repetitions
    sizes=[40] if args.pilot else [40,160]
    prefixes=[2,8] if args.pilot else [1,2,4,8]
    for fi,family in enumerate(['transition','administrative_form']):
        for repeat in range(reps):
            seed=args.seed+100000*fi+1000*repeat
            system=module.generator.system(seed,family)
            reference=module.generator.counts(module.generator.sample(system,400,seed+1))
            encoding=np.random.default_rng(seed+4).permutation(K);truth=np.argsort(encoding)
            rng=np.random.default_rng(seed+5)
            order=rng.permutation(K)
            source_swap=SWAPS[int(rng.integers(len(SWAPS)))]
            systems.append({'family':family,'seed':seed,'true_map':truth.tolist(),'report_code_order':order.tolist(),'source_swap':source_swap.tolist()})
            channels={}
            for source_state in ['correct','swapped']:
                report=truth if source_state=='correct' else source_swap[truth]
                for n in prefixes:
                    codes=order[:n];responses=report[codes]
                    claims.append({'family':family,'seed':seed,'source_state':source_state,'reported_codes':n,'codes':codes.tolist(),'source_a_responses':responses.tolist(),'source_b_correct_responses':truth[codes].tolist()})
                    for q in [.1,.5]:
                        channels[source_state,n,q]=(
                            independent_loglikelihood(maps,codes,responses,q),
                            coupled_probability(maps,codes,responses,q),
                            np.all(maps[:,codes]==responses,axis=1),
                            independent_loglikelihood(maps,codes,truth[codes],q),
                            coupled_probability(maps,codes,truth[codes],q),
                            np.all(maps[:,codes]==truth[codes],axis=1))
            for shift in [0,.35]:
                training=module.generator.encode(module.generator.sample(system,160,seed+2,shift),encoding)
                for train_n in sizes:
                    base=module.integrated_score(module.generator.counts(training[:train_n]),reference,maps)
                    for source_state in ['correct','swapped']:
                        for n in prefixes:
                            for q in [.1,.5]:
                                aind,acoupled,ahard,bind,bcoupled,bhard=channels[source_state,n,q]
                                for second in [False,True]:
                                    hard=ahard & bhard if second else ahard
                                    hard_scores=np.where(hard,base,-np.inf)
                                    once=base+aind+(bind if second else 0)
                                    probability=acoupled*(bcoupled if second else 1)
                                    log_probability=np.full(len(maps),-np.inf)
                                    positive=probability>0
                                    log_probability[positive]=np.log2(probability[positive])
                                    coupled=base+log_probability
                                    fixed={'hard':summarize(hard_scores,maps,truth),'independent_once':summarize(once,maps,truth),'coupled_source':summarize(coupled,maps,truth)}
                                    for copies in [1,3,10]:
                                        copied=base+copies*aind+(bind if second else 0)
                                        outcomes={**fixed,'independent_copied':summarize(copied,maps,truth)}
                                        for model,outcome in outcomes.items():
                                            rows.append({'family':family,'seed':seed,'training_texts':train_n,'reference_texts':400,
                                                'domain_shift':shift,'source_a_state':source_state,'second_correct_source':second,
                                                'reported_codes':n,'assumed_source_swap_probability':q,'source_a_copies':copies,'model':model,**outcome})
            print(json.dumps({'family':family,'systems_completed':repeat+1,'rows':len(rows)}),flush=True)
    result={'experiment_id':'CRYPTO-06','created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'synthetic-pilot' if args.pilot else 'declared-synthetic-grid','parameters':vars(args),'systems':systems,'source_claims':claims,
        'rows':rows,'integrity_checks':checks,'elapsed_seconds':time.perf_counter()-start,
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'helper_sha256':hashlib.sha256(HELPER.read_bytes()).hexdigest(),
        'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest()}
    payload=json.dumps(result,indent=2)+'\n';output.mkdir(parents=True)
    (output/'results.json').write_text(payload,encoding='utf-8');(output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'rows':len(rows),'seconds':result['elapsed_seconds']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--repetitions',type=int,default=24);parser.add_argument('--seed',type=int,default=610261002)
    parser.add_argument('--output',default='experiments/2026-10-02-six-hour/correlated-sources/main')
    run(parser.parse_args())
