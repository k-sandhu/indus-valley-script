"""Check frozen synthetic mapping proposals using reserved identity observations."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from itertools import permutations, combinations
from pathlib import Path
import time
import types
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HELPER=ROOT/'experiments/2026-10-02-six-hour/active-identities/main/code_snapshot.py'
active=types.ModuleType('active_frozen')
active.__file__=str(ROOT/'src/six_hour/active_identities.py')
exec(compile(HELPER.read_text(encoding='utf-8'),active.__file__,'exec'),active.__dict__)
K=8

def passing_probability(u,m,k):
    return math.comb(u-m,k)/math.comb(u,k) if k<=u-m else 0.0

def audit_size(u,alpha=.05):
    if u<2:
        return 0
    return next(k for k in range(1,u+1) if passing_probability(u,2,k)<=alpha)

def select_audit(policy, maps, weights, remaining, rng):
    if policy=='uniform_bound':
        k=audit_size(len(remaining))
    else:
        k=min(int(policy.rsplit('_',1)[1]),len(remaining))
    if policy.startswith('uniform'):
        return [int(x) for x in rng.choice(remaining,size=k,replace=False)]
    entropies={code:active.entropy(np.bincount(maps[:,code],weights=weights,minlength=K)) for code in remaining}
    return sorted(remaining,key=lambda code:(-entropies[code],code))[:k]

def checks():
    enumerations=0
    for u in range(2,9):
        for m in range(2,u+1):
            for k in range(u+1):
                subsets=list(combinations(range(u),k))
                direct=sum(all(code>=m for code in subset) for subset in subsets)/len(subsets)
                assert abs(direct-passing_probability(u,m,k))<1e-15
                enumerations+=1
        assert passing_probability(u,2,audit_size(u))<=.05
    return {'exact_subset_formula_checked':True,'subset_conditions':enumerations,
            'five_percent_worst_case_rule_checked':True}

def run(args):
    started=time.perf_counter()
    output=ROOT/args.output
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    protocol=output.parent/'PROTOCOL.md'
    maps=np.asarray(list(permutations(range(K))),dtype=np.int8)
    integrity=checks()
    rows=[]
    histories=[]
    reps=2 if args.pilot else args.repetitions
    refs=[40] if args.pilot else [40,400]
    sizes=[40] if args.pilot else [40,160]
    for fi,family in enumerate(['transition','administrative_form']):
        for repeat in range(reps):
            seed=args.seed+100000*fi+1000*repeat
            system=active.module.generator.system(seed,family)
            reference_texts=active.module.generator.sample(system,400,seed+1)
            encoding=np.random.default_rng(seed+4).permutation(K)
            truth=np.argsort(encoding)
            for shift in [0,.35,.7]:
                texts=active.module.generator.encode(active.module.generator.sample(system,160,seed+2,shift),encoding)
                for ref_n in refs:
                    reference=active.module.generator.counts(reference_texts[:ref_n])
                    for n in sizes:
                        observed=active.module.generator.counts(texts[:n])
                        scores=active.module.integrated_score(observed,reference,maps)
                        allowed=np.arange(len(maps))
                        revealed={}
                        oracle=active.IdentityOracle(truth)
                        rng=np.random.default_rng(seed+19+ref_n+n+int(shift*100))
                        search=[]
                        while True:
                            compatible=maps[allowed]
                            weights=active.posterior(scores[allowed])
                            candidate=compatible[int(np.argmax(weights))].copy()
                            remaining=[code for code in range(K) if code not in revealed]
                            mass=float(weights.max())
                            if mass>=.95:
                                break
                            query=active.choose_query('entropy',compatible,weights,remaining,observed[2],rng)
                            answer=oracle.reveal(query)
                            search.append([query,answer,mass])
                            revealed[query]=answer
                            allowed=allowed[maps[allowed,query]==answer]
                        common={'family':family,'seed':seed,'reference_texts':ref_n,'training_texts':n,'domain_shift':shift,
                            'search_observations':len(revealed),'remaining_identities':len(remaining),
                            'proposal':candidate.tolist(),'proposal_mass':mass,'proposal_correct':bool(np.array_equal(candidate,truth)),
                            'true_map':truth.tolist(),'revealed':[[a,b] for a,b in revealed.items()]}
                        histories.append({**common,'search_history':search})
                        disagreements=int(sum(candidate[code]!=truth[code] for code in remaining))
                        assert disagreements==0 or disagreements>=2
                        for pi,policy in enumerate(['uniform_1','uniform_2','uniform_3','entropy_1','entropy_2','entropy_3','uniform_bound']):
                            vrng=np.random.default_rng(seed+6000000+10000*pi+ref_n+n+int(shift*100))
                            selected=select_audit(policy,compatible,weights,remaining,vrng)
                            # Answer access occurs only after the complete selection has been made.
                            responses=[oracle.reveal(code) for code in selected]
                            passes=all(candidate[code]==answer for code,answer in zip(selected,responses))
                            probability=passing_probability(len(remaining),disagreements,len(selected)) if not common['proposal_correct'] else 1.0
                            rows.append({**common,'policy':policy,'verification_codes':selected,'verification_responses':responses,
                                'additional_observations':len(selected),'total_observations':len(revealed)+len(selected),
                                'audit_passes':bool(passes),'wrong_acceptance':bool(passes and not common['proposal_correct']),
                                'correct_acceptance':bool(passes and common['proposal_correct']),
                                'proposal_disagreements':disagreements,
                                'uniform_conditional_pass_probability':probability if policy.startswith('uniform') else None,
                                'uniform_conditional_wrong_accept_probability':probability if policy.startswith('uniform') and not common['proposal_correct'] else (0.0 if policy.startswith('uniform') else None)})
                        assert all(row['audit_passes'] for row in rows[-7:] if row['proposal_correct'])
            print(json.dumps({'family':family,'systems_completed':repeat+1,'conditions':len(histories)}),flush=True)
    result={'experiment_id':'CRYPTO-05','created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'synthetic-pilot' if args.pilot else 'declared-synthetic-grid','parameters':vars(args),
        'systems':2*reps,'conditions':len(histories),'audit_records':len(rows),'integrity_checks':integrity,
        'elapsed_seconds':time.perf_counter()-started,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_sha256':hashlib.sha256(HELPER.read_bytes()).hexdigest(),
        'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'histories':histories,'records':rows}
    encoded=json.dumps(result,indent=2)+'\n'
    output.mkdir(parents=True)
    (output/'results.json').write_text(encoded,encoding='utf-8')
    (output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'conditions':len(histories),'records':len(rows),'seconds':result['elapsed_seconds']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--repetitions',type=int,default=24)
    parser.add_argument('--seed',type=int,default=510261002)
    parser.add_argument('--output',default='experiments/2026-10-02-six-hour/reserved-verification/main')
    run(parser.parse_args())
