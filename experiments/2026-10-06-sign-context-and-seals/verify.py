"""Check frozen hashes, repeatability, aggregate counts and reference invariants."""
import argparse, json, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
import analyze as main

def run():
    ap=argparse.ArgumentParser(); ap.add_argument('--original',default='run-2026-10-07-01')
    ap.add_argument('--replicate',default='verification-2026-10-07-01'); ap.add_argument('--output',default='checks-2026-10-07-01.json')
    args=ap.parse_args(); dest=main.OWN/args.output
    if dest.exists(): raise FileExistsError('Use a new checks output filename.')
    load=lambda n: json.loads((main.OWN/args.original/(n+'.json')).read_text(encoding='utf-8'))
    summary=load('input-summary'); checks=[]
    def check(name,condition,detail=None):
        checks.append({'check':name,'passed':bool(condition),'detail':detail})
        if not condition: raise AssertionError(name)
    for key,path in [('input_sha256',main.INPUT),('protocol_sha256',main.OWN/'PROTOCOL.md'),
                     ('site_table_sha256',main.OWN/'site-table.json'),('code_sha256',main.OWN/'analyze.py')]:
        check(key,main.sha(path)==summary[key])
    for file,h in summary['outputs'].items():
        check('frozen output hash '+file,main.sha(main.OWN/args.original/file)==h)
        check('deterministic rerun '+file,main.sha(main.OWN/args.replicate/file)==h)
    rows=[json.loads(l) for l in main.INPUT.read_text(encoding='utf-8').splitlines()]
    token=Counter(s for r in rows for s in r['signs_reading_rtl'])
    check('known corpus totals',(len(rows),sum(token.values()),token['740'],token['000'])==(5680,19946,1928,1879))
    check('site 740 numerators sum',sum(v['count'] for v in load('site-frequencies') if v['sign']=='740')==1928)
    check('site readable denominators sum',sum(v['readable_positions'] for v in load('site-frequencies') if v['sign']=='740')==18067)
    # Independently choose numeric-family representatives: the alias audit says
    # this export has no components that combine different numeric families.
    families={}
    for r in rows: families.setdefault(r['object_family_id'],[]).append(r)
    select=lambda rs:min(rs,key=lambda r:(-len(r['signs_reading_rtl']),r['record_id']))
    seals=[select([r for r in rs if r['object_type'].startswith('SEAL')]) for rs in families.values() if any(r['object_type'].startswith('SEAL') for r in rs)]
    sq=[r for r in seals if r['object_type']=='SEAL:S']
    conc=load('motif-concentration'); global_sq=next(v for v in conc if v['population']=='square_seals' and v['level']=='global')
    known=[r for r in sq if r['symbol'] not in main.MISSING_MOTIFS]
    unicorn=sum(r['symbol'].startswith('Bull1') for r in known)
    check('square motif counts independently reconstructed',(len(sq),len(known),unicorn)==(1736,1609,1246))
    cat=Counter('unicorn' if r['symbol'].startswith('Bull1') else r['symbol'] for r in known)
    check('square HHI independently reconstructed',abs(sum((v/len(known))**2 for v in cat.values())-global_sq['hhi'])<1e-12)
    dim=load('dimensions'); complete=[]
    for r in sq:
        try: h=float(r['metadata']['horizontal(mm)']); v=float(r['metadata']['vertical(mm)'])
        except (ValueError,TypeError): continue
        if h>0 and v>0 and r['metadata'].get('preservation')=='complete': complete.append((h*v)**.5)
    global_dim=next(v for v in dim['groups'] if v['population']=='complete_square' and v['level']=='global')['characteristic_size_mm']
    check('complete dimensions independently reconstructed',len(complete)==1027)
    check('dimension CV independently reconstructed',abs(np.std(complete,ddof=1)/np.mean(complete)-global_dim['cv'])<1e-12)
    raw=main.RAW/args.original; ma=load('motif-association'); sign=load('sign-analysis'); tested=0
    def verify_tails(ts,nu,absolute_flags):
        nonlocal tested
        for j,t in enumerate(ts):
            e=np.count_nonzero(np.abs(nu[:,j])>=abs(t['observed'])-1e-12) if absolute_flags[j] else np.count_nonzero(nu[:,j]>=t['observed']-1e-12)
            check('tail '+str(tested),int(e)==t['exceedances'] and (int(e)+1)/(len(nu)+1)==t['p']); tested+=1
    with np.load(raw/'sign_nulls.npz') as ns:
        verify_tails(sign['site_omnibus']['tests'],ns['site'],[False]*10)
        for j,key in enumerate(['reference','min','max','exclude_two_cities']):
            verify_tails(sign['size_comparisons'][key]['tests'],ns['size'][j],[True]*10)
    for key in ['primary_rare','all_nonunicorn_sensitivity']:
        verify_tails(ma[key]['tests'],np.load(raw/(key+'_motif_null.npy')),[False]*3+[True]*3)
    for site,vs in ma['by_site'].items():
        import re
        verify_tails(vs['tests'],np.load(raw/(re.sub(r'[^A-Za-z0-9]','_',site)+'_motif_null.npy')),[False]*3+[True]*3)
    for t,name in zip(dim['tests'],['dimension_cv_null.npy','dimension_length_null.npy']):
        verify_tails([t],np.load(raw/name).reshape(-1,1),[True])
    # Check that the reference implementation retains blockwise label counts.
    rng=np.random.default_rng(77); y=np.array([1,1,0,0,1,0]); bs=[np.array([0,1,2]),np.array([3,4,5])]
    check('block label counts preserved in 1000 references',all(all(main.shuffle(y,bs,rng)[ix].sum()==y[ix].sum() for ix in bs) for _ in range(1000)))
    assert np.allclose(np.load(main.RAW/'exploratory-2026-10-07-01/motif_length_conditioned_null.npy')[:,-1],ma['primary_rare']['tests'][-1]['observed'],rtol=0,atol=1e-12)
    check('exact length conditioning invariant',True)
    # Check transitive aliases without any corpus text or file mutation.
    mock=[{'object_family_id':'A','source_cisi':'H-1A','record_id':'a','signs_reading_rtl':['x'],'object_type':'SEAL:S','site':'s'},
          {'object_family_id':'B','source_cisi':'H-1B','record_id':'b','signs_reading_rtl':['y'],'object_type':'SEAL:S','site':'s'},
          {'object_family_id':'B','source_cisi':'H-2A','record_id':'c','signs_reading_rtl':['z'],'object_type':'SEAL:S','site':'s'}]
    gs,_,_,_=main.grouping(mock); check('side aliases and family links close transitively',len(gs)==1 and len(gs[0])==3)
    main.write(dest,{'status':'Verified computation','checks':checks,'passed':len(checks),'failed':0,
                     'tail_probabilities_recomputed':tested,'original':args.original,'replicate':args.replicate,
                     'scope':'Deterministic rerun plus arithmetic/identity invariants; external source and independent reviewer checks remain separate.'})
    print(len(checks),'checks passed;',tested,'tail probabilities recomputed')

if __name__=='__main__': run()
