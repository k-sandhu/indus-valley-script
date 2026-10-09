"""Independent aggregate arithmetic and preserved-run comparison.

Run after a fresh analyze.py --run name. Outputs refuse replacement.
No imports from the analysis implementation are used.
"""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, math, re

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--replay',default='run-replay-2026-10-08-01')
    ap.add_argument('--output',default='verification.json');a=ap.parse_args()
    dest=OWN/a.output
    if dest.exists():raise FileExistsError(dest)
    checks=[]
    def check(name,ok,detail=None):
        checks.append(dict(name=name,passed=bool(ok),detail=detail))
        if not ok:print('FAIL',name,detail)
    base=OWN/'run-2026-10-08-v1';repeat=OWN/a.replay
    aggregate_names=[p.name for p in base.glob('*.json')]
    for name in aggregate_names:
        x=read(base/name);y=read(repeat/name)
        if name=='manifest.json':
            x={**x,'inputs':[i for i in x['inputs'] if not i['path'].endswith('/PROTOCOL.md')]}
            y={**y,'inputs':[i for i in y['inputs'] if not i['path'].endswith('/PROTOCOL.md')]}
        check('replay '+name,x==y)
    for p in (RAW/'run-2026-10-08-v1').glob('*.json'):
        check('local derivative replay '+p.name,sha(p)==sha(RAW/a.replay/p.name))
    for item in read(base/'manifest.json')['inputs']:
        p=ROOT/item['path']
        if item['path'].endswith('/PROTOCOL.md'):p=OWN/'PROTOCOL-registered.md'
        check('input '+item['path'],sha(p)==item['sha256'])
    clean=[json.loads(z) for z in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines() if z]
    selected={}
    for r in clean:
        key=r['object_family_id'];candidate=(r['length'],r['record_id'])
        if key not in selected or r['length']>selected[key]['length'] or (r['length']==selected[key]['length'] and r['record_id']<selected[key]['record_id']):selected[key]=r
    seqs=[r['signs_reading_rtl'] for r in selected.values()];d=read(base/'distributions.json')
    p=d['populations']['longest_eligible_object_faces']
    check('principal row/token bases',(len(seqs),sum(map(len,seqs)))==(p['rows'],p['tokens']))
    for sign,v in p['signs'].items():
        total=sum(s.count(sign) for s in seqs);final=sum(s[-1]==sign for s in seqs);initial=sum(s[0]==sign for s in seqs)
        check('positional counts '+sign,(total,final,initial)==(v['tokens'],v['final'],v['initial']))
        check('final fraction '+sign,math.isclose(final/total,v['final_fraction'],rel_tol=1e-12))
    refs=read(RAW/'run-2026-10-08-v1/position-references.json')
    for sign,values in refs['positions'].items():
        v=d['principal_reference_tests'][sign];obs=v['observed']
        tail=sum(t<=obs+1e-12 for t in values) if v['statistic']=='early' else sum(t>=obs-1e-12 for t in values)
        check('Monte Carlo tail '+sign,tail==v['tail_count'] and (tail+1)/(len(values)+1)==v['p'])
    # A separate character-class implementation verifies the lexicon scores.
    classes={'a':'aA','i':'iI','u':'uU','f':'fF','x':'xX','k':'kKgG','c':'cCjJ','Z':'wWqQ','t':'tTdD','p':'pPbB','s':'sSz','n':'nR'}
    convert={char:target for target,chars in classes.items() for char in chars}
    normalize=lambda word:''.join(convert.get(c,c) for c in word)
    check('normalization controls',normalize('BUDana')=='putana' and normalize('qana')=='Zana' and normalize('tana')=='tana')
    # Cologne's source format starts the next field with <k2>; it is not XML
    # with a closing </k1>. Parse field boundaries independently of the runner.
    words=[]
    for line in (RAW/'acquisition-2026-10-08-v1/mw.txt').read_text(encoding='utf-8').splitlines():
        if '<k1>' in line:words.append(line.split('<k1>',1)[1].split('<',1)[0])
    keys={word for word in words if word.isascii() and word.isalpha()}
    norms={normalize(k) for k in keys};s=read(OWN/'selection.json');names=list(s['values_slp1'])
    counts=collections.Counter();observed=None
    for assignment in itertools.permutations(names):
        mapping=dict(zip(names,assignment));ex=nh=0
        for row in s['panel']:
            alternatives=[s['values_slp1'][mapping[r]] for r in row['roles']]
            alternatives=[v if i==0 else [w for w in v if w not in ['maha','mahA']] for i,v in enumerate(alternatives)]
            forms={''.join(v) for v in itertools.product(*alternatives)}
            ex+=bool(forms&keys);nh+=any(normalize(w) in norms for w in forms)
        counts[(ex,nh)]+=1
        if assignment==tuple(names):observed=(ex,nh)
    l=read(base/'lexical.json')
    check('dictionary distinct headwords',len(keys)==l['distinct_alphabetic_headwords'])
    check('dictionary normalized classes',len(norms)==l['normalized_headword_classes'])
    check('observed lexical scores',observed==(l['exact']['observed'],l['normalized']['observed']))
    for i,label in enumerate(['exact','normalized']):
        hist=collections.Counter()
        for pair,n in counts.items():hist[pair[i]]+=n
        check('all 720 '+label+' scores',{str(k):v for k,v in hist.items()}==l[label]['null_histogram'])
        tail=sum(n for score,n in hist.items() if score>=observed[i])
        check('exhaustive tail '+label,tail==l[label]['tail_n'] and tail/720==l[label]['p'])
    claimrows=[json.loads(z) for z in (OWN/'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    known={s['id'] for s in read(OWN/'sources.json')['sources']}
    check('claim source identities',all(c['source_id'] in known for c in claimrows))
    check('claim IDs unique',len({c['id'] for c in claimrows})==len(claimrows))
    check('no direct quotation budget used',all(c['quotation'] is None for c in claimrows))
    audit=read(OWN/'validation-audit.json')
    check('manual audit partition',audit['confirmed_catalogue_object_overlaps']+audit['conflicting_label_overlaps']+audit['parser_false_overlaps']==audit['original_parser_object_overlaps'])
    summary={'status':'Verified computation' if all(c['passed'] for c in checks) else 'Failed',
      'passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,
      'numeric_scope':'Replay equality, input pins, independent counts, MC tails and all 720 lexical permutations. Does not certify source transcription or sign semantics.',
      'analysis_code_sha256':sha(OWN/'analyze.py'),'frozen_analysis_code_sha256':sha(OWN/'analyze-v1-frozen.py')}
    dest.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='checks'},indent=2))
    if summary['status']=='Failed':raise SystemExit(1)

if __name__=='__main__':main()
