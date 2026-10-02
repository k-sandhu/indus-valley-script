"""Compare exact identity-acquisition policies with an isolated response oracle."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from itertools import permutations
from pathlib import Path
import time
import types
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT/'experiments/2026-10-02-six-hour/reference-uncertainty/main/code_snapshot.py'
module = types.ModuleType('reference_frozen')
module.__file__ = str(ROOT/'src/six_hour/reference_uncertainty.py')
exec(compile(HELPER.read_text(encoding='utf-8'),module.__file__,'exec'),module.__dict__)
K = 8

class IdentityOracle:
    def __init__(self, answers):
        self._answers = tuple(int(x) for x in answers)
        self.requests = []
    def reveal(self, code):
        self.requests.append(int(code))
        return self._answers[code]

def posterior(scores):
    weights = np.exp2(scores-scores.max())
    return weights/weights.sum()

def entropy(probabilities):
    nonzero = probabilities[probabilities>0]
    return float(-(nonzero*np.log2(nonzero)).sum())

def choose_query(policy, maps, weights, remaining, counts, rng):
    if policy=='random':
        return int(rng.choice(remaining))
    if policy=='frequency':
        return min(remaining,key=lambda code:(-counts[code],code))
    marginal_entropy = {code:entropy(np.bincount(maps[:,code],weights=weights,minlength=K)) for code in remaining}
    return min(remaining,key=lambda code:(-marginal_entropy[code],code))

def mechanism_checks(maps):
    rng=np.random.default_rng(481202610)
    scores=rng.normal(size=len(maps))
    weights=posterior(scores)
    chosen=choose_query('entropy',maps,weights,list(range(K)),np.ones(K),rng)
    conditional=0.0
    marginal=np.bincount(maps[:,chosen],weights=weights,minlength=K)
    for answer,mass in enumerate(marginal):
        subset=weights[maps[:,chosen]==answer]
        if mass:
            conditional += mass*entropy(subset/mass)
    checks={'mass_normalizes':bool(abs(weights.sum()-1)<1e-12),
            'entropy_query_matches_expected_map_information':abs(entropy(weights)-conditional-entropy(marginal))<1e-10,
            'all_permutations':len(maps)==math.factorial(K)}
    checks={key:bool(value) for key,value in checks.items()}
    json.dumps(checks)
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks

def run(args):
    started=time.perf_counter()
    output=ROOT/args.output
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    protocol=output.parent/'PROTOCOL.md'
    maps=np.asarray(list(permutations(range(K))),dtype=np.int8)
    checks=mechanism_checks(maps)
    records=[]
    reps=2 if args.pilot else args.repetitions
    refs=[40] if args.pilot else [40,400]
    sizes=[40] if args.pilot else [40,160]
    cases=0
    for family_i,family in enumerate(['transition','administrative_form']):
        for repeat in range(reps):
            seed=args.seed+100000*family_i+1000*repeat
            system=module.generator.system(seed,family)
            references=module.generator.sample(system,400,seed+1)
            encoding=np.random.default_rng(seed+4).permutation(K)
            truth=np.argsort(encoding)
            for shift in [0,.35,.7]:
                training=module.generator.encode(module.generator.sample(system,160,seed+2,shift),encoding)
                for ref_n in refs:
                    reference=module.generator.counts(references[:ref_n])
                    for n in sizes:
                        observed=module.generator.counts(training[:n])
                        scores=module.integrated_score(observed,reference,maps)
                        cases+=1
                        for policy in ['random','entropy','frequency']:
                            allowed=np.arange(len(maps))
                            oracle=IdentityOracle(truth)
                            revealed={}
                            rng=np.random.default_rng(seed+17+ref_n+n+int(shift*100))
                            for prefix in range(K+1):
                                compatible=maps[allowed]
                                weights=posterior(scores[allowed])
                                best=compatible[int(np.argmax(weights))]
                                assert len(allowed)==math.factorial(K-prefix)
                                assert all(best[a]==b for a,b in revealed.items())
                                remaining=[code for code in range(K) if code not in revealed]
                                # Selection receives no answer vector or oracle state.
                                query=choose_query(policy,compatible,weights,remaining,observed[2],rng) if remaining else None
                                records.append({'family':family,'seed':seed,'reference_texts':ref_n,'training_texts':n,
                                    'domain_shift':shift,'policy':policy,'observed_identities':prefix,
                                    'compatible_maps':len(allowed),'best_map':best.tolist(),'best_map_mass':float(weights.max()),
                                    'map_entropy_bits':entropy(weights),'exact_mapping_recovered':bool(np.array_equal(best,truth)),
                                    'symbol_mapping_accuracy':float(np.mean(best==truth)),
                                    'revealed':[[a,b] for a,b in revealed.items()],'next_query':query,
                                    'true_map':truth.tolist()})
                                if query is not None:
                                    answer=oracle.reveal(query)
                                    revealed[query]=answer
                                    allowed=allowed[maps[allowed,query]==answer]
                            assert np.array_equal(best,truth)
                            assert len(set(oracle.requests))==K
            print(json.dumps({'family':family,'systems_completed':repeat+1,'cases':cases}),flush=True)
    result={'experiment_id':'CRYPTO-04','status':'pilot' if args.pilot else 'declared-synthetic-grid',
        'parameters':vars(args),'systems':2*reps,'conditions':cases,'prefix_records':len(records),
        'mechanism_checks':checks,'elapsed_seconds':time.perf_counter()-started,
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_sha256':hashlib.sha256(HELPER.read_bytes()).hexdigest(),
        'generator_sha256':hashlib.sha256(module.FROZEN.read_bytes()).hexdigest(),
        'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'records':records}
    encoded_result=json.dumps(result,indent=2)+'\n'
    output.mkdir(parents=True)
    (output/'results.json').write_text(encoded_result,encoding='utf-8')
    (output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'conditions':cases,'records':len(records),'seconds':result['elapsed_seconds']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--repetitions',type=int,default=24)
    parser.add_argument('--seed',type=int,default=410261002)
    parser.add_argument('--output',default='experiments/2026-10-02-six-hour/active-identities/main')
    run(parser.parse_args())
