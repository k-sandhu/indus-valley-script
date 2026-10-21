"""Run after freeze: python -I code/compute.py. Test: python -I code/compute.py --synthetic OUTDIR."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse
import gzip
import hashlib
import json
from common import PACKAGE,LOCAL,RUN,CODE,ENTRY,TIPS,GROUPS,VALUES,read,write,sha,code_hashes
import numpy as np
from tree import load_mcc,random_yule,nodes,leaves,mrca,parse_newick,newick,match_tips
from recon import parsimony,mk1,mk2,simulate
from reference import draw,build_pool
from coding import KEYWORDS,CLASSES
from dedr_parse import head

def freeze_gate(path=None):
    path=Path(path) if path is not None else PACKAGE/'FREEZE.json'
    if not path.is_file(): raise RuntimeError('FREEZE.json is required before reading real codings')
    freeze=read(path)
    recorded=freeze.get('code_hashes',freeze.get('files',{}))
    if isinstance(recorded,list): recorded={r['path']:r['sha256'] for r in recorded}
    expected={}
    for key,value in recorded.items():
        key=key.replace('\\','/')
        if '/code/' in key: key=key.split('/code/',1)[1]
        elif key.startswith('code/'): key=key[5:]
        if isinstance(value,dict): value=value['sha256']
        expected[key]=value
    actual=code_hashes()
    if actual!=expected:
        raise RuntimeError('Freeze code hashes differ: '+', '.join(sorted(k for k in actual.keys()|expected.keys() if actual.get(k)!=expected.get(k))))
    return sha(path)

def states(coding): return {tip:row['state'] for tip,row in coding['tips'].items()}

def summarise(root,coding,model='Mk1',prior='flat'):
    if set(coding['tips'])!=set(TIPS): raise ValueError('Coding tip set mismatch')
    trait=states(coding)
    fitted=mk1(root,trait) if model=='Mk1' else mk2(root,trait,prior)
    sankoff=parsimony(root,trait)
    targets={'root':root,'North':mrca(root,GROUPS['North']),'South I':mrca(root,GROUPS['South I'])}
    counts={group:{str(v) if v is not None else 'missing':sum(trait.get(t)==v for t in tips)
                   for v in [1,0,None]} for group,tips in GROUPS.items()}
    return dict(entry=coding['entry'],tip_counts=counts,
                nodes={name:dict(node=n.id,age=n.age,probability=fitted['probabilities'][n.id],
                                 parsimony_score=sankoff['scores'][n.id],parsimony_set=sankoff['sets'][n.id]) for name,n in targets.items()},
                parsimony_cost=sankoff['cost'],q=fitted['q'],gain=fitted['gain'],loss=fitted['loss'],
                log_likelihood=fitted['log_likelihood'],root_prior=fitted['root_prior'],boundary=fitted['boundary'],
                observed_tips=fitted['observed_tips'],fewer_than_two_observed=fitted['fewer_than_two_observed'],
                oldest_above_half=fitted['oldest_above_half'],optimisation=fitted['optimisation'])

def evaluate(primary,codings,reference):
    star=primary['STAR']; root=star['nodes']['root']['probability']; north=star['nodes']['North']['probability']
    outside=any(codings['STAR']['tips'][t]['state']==1 for group in ['North','Central'] for t in GROUPS[group])
    p1=root>.5; p2=reference['all']['T']>reference['all']['mean_T_star'] and reference['all']['p_value']<=.05
    p3=north>.5; kill=not outside and root<.2
    if star['fewer_than_two_observed']:
        return dict(P1=None,P2=p2,P3=None,kill=None,credence=None,status='insufficient STAR observations')
    if p1 and p2: credence=.35 if not p3 or star['nodes']['root']['parsimony_score']==0 else .45
    elif p1: credence=.30
    elif kill: credence=.02
    elif outside and root<.2: credence=.08
    else: credence=.10
    return dict(P1=p1,P2=p2,P3=p3,kill=kill,STAR_in_Central_or_North=outside,
                credence=credence,status='dead' if kill else 'working',starting_credence=.15)

def posterior_summary(roots,codes):
    output={}
    for meaning,coding in codes.items():
        values={'root':[],'North':[]}; trait=states(coding)
        for root in roots:
            fit=mk1(root,trait)
            values['root'].append(fit['probabilities'][root.id])
            values['North'].append(fit['probabilities'][mrca(root,GROUPS['North']).id])
        output[meaning]={name:dict(mean=float(np.mean(v)),percentile_2_5=float(np.percentile(v,2.5)),
                                   percentile_97_5=float(np.percentile(v,97.5)),share_above_half=float(np.mean(np.array(v)>.5)),trees=len(v))
                         for name,v in values.items()}
    return output

def pipeline(root,variants,pools,posterior,detaildir):
    output={'primary':{},'sensitivities':{}}; details={}
    for variant,codes in variants.items():
        fits={m:summarise(root,c) for m,c in codes.items()}
        details[variant]={'codings':codes}
        record={'meanings':fits}
        if variant in pools:
            poolprob={}
            for key,pool in pools[variant].items():
                poolprob[key]={h:mk1(root,states(c))['probabilities'][root.id] for h,c in pool.items()}
            refs={m:list(poolprob[c['entry']].values()) for m,c in codes.items()}
            statistic=draw({m:f['nodes']['root']['probability'] for m,f in fits.items()},refs)
            record['reference']=statistic
            details[variant]['pool_probabilities']=poolprob
            record['evaluations']=evaluate(fits,codes,statistic)
        if variant=='primary': output['primary']=record
        else: output['sensitivities'][variant]=record
    output['sensitivities']['S2']={}
    for prior in ['flat','stationary']:
        output['sensitivities']['S2'][prior]={'meanings':{m:summarise(root,c,'Mk2',prior) for m,c in variants['primary'].items()}}
    output['sensitivities']['S5']=posterior_summary(posterior,variants['primary'])
    write(detaildir/'detail.json',details)
    return output

def input_hashes():
    paths=[PACKAGE/'PROTOCOL.md',PACKAGE/'ENTRIES.md',PACKAGE/'AMENDMENT-1.md',LOCAL/'mcc.json',
           LOCAL/'posterior/sample.jsonl.gz',RUN/'language-tip-map.json']
    paths.extend(RUN/name for name in ['sources-kolipakam.json','sources-dedr.json','sources-dravlex.json'])
    for folder in ['parsed','codings','reference']:
        paths.extend(sorted((LOCAL/folder).rglob('*.json')))
    if (LOCAL/'manual-recode.json').exists(): paths.append(LOCAL/'manual-recode.json')
    return {str(p.relative_to(PACKAGE.parent.parent)).replace('\\','/'):sha(p) for p in paths}

def real():
    frozen=freeze_gate()
    outdir=PACKAGE/'results-v1'
    detail=LOCAL.parent/'results-v1-detail'
    if outdir.exists() or detail.exists(): raise RuntimeError('Existing results directory; this endpoint is immutable')
    manual=LOCAL/'manual-recode.json'
    if manual.exists():
        from coding import main as prepare_codings
        prepare_codings(manual)
    root=parse_newick(read(LOCAL/'mcc.json')['newick']); match_tips(root)
    variants={p.stem:read(p) for p in sorted((LOCAL/'codings').glob('*.json'))}
    if not {'primary','S1','S6','S7','S4'}.issubset(variants): raise ValueError('Missing required coding variants')
    entries={k:read(LOCAL/'parsed'/(k+'.json')) for k in set(ENTRY.values())}
    pools={'primary':{k:read(LOCAL/'reference'/(k+'.json')) for k in entries}}
    for variant in ['S1','S6','S7']+(['S8'] if 'S8' in variants else []):
        used={m:c['entry'] for m,c in variants[variant].items()}
        predicates={m:(lambda s,k=KEYWORDS[m]:head(s)==k) if variant=='S6' else CLASSES[m] for m in used}
        pools[variant]={k:build_pool(entries[k],[m for m,e in used.items() if e==k],predicates,variant=='S1')[0]
                        for k in set(used.values())}
    posterior=[]
    with gzip.open(LOCAL/'posterior/sample.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream: posterior.append(parse_newick(json.loads(line)['newick']))
    if len(posterior)!=1000: raise ValueError('Expected 1000 posterior trees')
    hashes=input_hashes()
    # Reserve the result directory before work; a failed computation cannot be overwritten.
    outdir.mkdir(); detail.mkdir(parents=True)
    result=pipeline(root,variants,pools,posterior,detail)
    result.update(synthetic=False,code_hashes=code_hashes(),input_hashes=hashes,freeze_sha256=frozen,
                  skipped_sensitivities=[s for s in ['S3','S8'] if s not in variants])
    write(outdir/'results.json',result)

def fabricated(root,rng):
    variants={v:{} for v in ['primary','S1','S6','S7','S3','S4','S8']}
    pools={}
    for i,(meaning,key) in enumerate(ENTRY.items()):
        _,trait=simulate(root,rng,float(np.exp(rng.uniform(-3,1))),.25,root_state=i%2)
        coding=dict(entry=key,tips={t:dict(state=trait[t],evidence=[],forms=[]) for t in TIPS})
        for variant in ['primary','S1','S6','S7','S8']: variants[variant][meaning]=coding
        if meaning=='STAR': variants['S3']['STAR']=coding; variants['S4']['STAR']=coding
    for key in set(ENTRY.values()):
        pools[key]={}
        for i in range(3):
            _,trait=simulate(root,rng,float(np.exp(rng.uniform(-3,1))),.3)
            pools[key]['synthetic'+str(i)]=dict(entry=key,tips={t:dict(state=trait[t]) for t in TIPS})
    return variants,{v:pools for v in ['primary','S1','S6','S7','S8']}

def synthetic(outdir):
    outdir=outdir.resolve()
    if not outdir.is_relative_to(LOCAL.resolve()): raise ValueError('Synthetic output must be under codex-run1')
    if outdir.exists(): raise ValueError('Synthetic output already exists')
    rng=np.random.default_rng(20261021)
    outdir.mkdir(parents=True)
    output={}
    for name,root in [('MCC',load_mcc()),('Yule',random_yule(rng,20,TIPS))]:
        variants,pools=fabricated(root,rng)
        sample=[root,random_yule(rng,20,TIPS),random_yule(rng,20,TIPS)]
        output[name]=pipeline(root,variants,pools,sample,outdir/name)
    write(outdir/'results.json',dict(synthetic=True,seed=20261021,trees=output,code_hashes=code_hashes()))
    print('Synthetic pipeline completed on MCC and Yule trees')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--synthetic',type=Path)
    args=ap.parse_args()
    try:
        synthetic(args.synthetic) if args.synthetic else real()
    except (RuntimeError,ValueError) as exc:
        ap.exit(2,str(exc)+'\n')
