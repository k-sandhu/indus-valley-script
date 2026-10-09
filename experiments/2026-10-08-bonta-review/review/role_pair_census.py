"""Reviewer census of ordered adjacent pairs among the six Package Q roles (Exploratory, post-outcome).

Counts objects in the package's principal population (longest eligible clean face per object) in which
one role immediately follows another in reading order, using the Wells candidate sets from the package
concordance, and records whether Bonta's own values give an exact dictionary headword. Aggregate output only.
Refuses to overwrite review/role-pair-census.json.
"""
import json, collections, itertools, re
from pathlib import Path
ROOT=Path(r'C:/Users/sandh/OneDrive/Projects/indus_valley_script')
rows=[json.loads(l) for l in open(ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl',encoding='utf8')]
best={}
for r in rows:
    g=r['object_family_id']; k=(-len(r['signs_reading_rtl']), r['record_id'])
    if g not in best or k<best[g][0]: best[g]=(k,r)
sel=[v[1] for v in best.values()]
roles={'MA':{'704','705','706','707'},'TRA':{'033'},'PALA':{'390','392','405','406','407','408'},'DHANA':{'125','126'},'PU':{'590'},'PATI':{'817','861'}}
inv={c:r for r,cs in roles.items() for c in cs}
pair_obj=collections.defaultdict(set); pair_tok=collections.Counter(); trip_obj=collections.defaultdict(set)
for r in sel:
    s=[inv.get(x) for x in r['signs_reading_rtl']]
    for i in range(len(s)-1):
        if s[i] and s[i+1]:
            pair_obj[(s[i],s[i+1])].add(r['object_family_id']); pair_tok[(s[i],s[i+1])]+=1
    for i in range(len(s)-2):
        if s[i] and s[i+1] and s[i+2]: trip_obj[(s[i],s[i+1],s[i+2])].add(r['object_family_id'])
panel={('MA','TRA'),('DHANA','PALA'),('PU','PALA'),('PU','MA'),('PU','DHANA'),('PU','TRA'),('DHANA','PATI'),('PALA','PATI'),('PU','PATI')}
vals=json.load(open(ROOT/'experiments/2026-10-08-bonta-review/selection.json',encoding='utf8'))['values_slp1']
heads=set()
for line in open(ROOT/'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt',encoding='utf8'):
    i=line.find('<k1>')
    if i>=0:
        h=line[i+4:line.find('<',i+4)]
        if re.fullmatch(r'[A-Za-z]+',h): heads.add(h)
def match(a,b):
    A=vals[a]; B=[v for v in vals[b] if not v.lower().startswith('maha')]
    return any(x+y in heads for x in A for y in B)
print('ordered role pairs attested in principal population (objects):')
tot=0;hit=0
out=[]
for (a,b),objs in sorted(pair_obj.items(), key=lambda kv:-len(kv[1])):
    m=match(a,b); out.append((a,b,len(objs),pair_tok[(a,b)],m,(a,b) in panel))
    print(f'  {a}-{b}: {len(objs)} objects, {pair_tok[(a,b)]} tokens; in Bonta panel: {(a,b) in panel}; exact dictionary match under his values: {m}')
print('triples attested:',{k:len(v) for k,v in trip_obj.items()})
na=len(out); np_=sum(1 for o in out if o[5]); 
print('attested ordered pair types',na,'; of these in panel',np_,'; not in panel',na-np_)
print('exact match among panel pairs',sum(1 for o in out if o[5] and o[4]),'/',np_, '; among attested non-panel pairs',sum(1 for o in out if (not o[5]) and o[4]),'/',na-np_)
print('panel pairs not attested in this population:',[p for p in panel if p not in pair_obj])
import sys
if (ROOT/'experiments/2026-10-08-bonta-review/review/role-pair-census.json').exists(): sys.exit('refusing to overwrite')
json.dump([dict(first=a,second=b,objects=o,tokens=t,exact_match=m,in_panel=p) for a,b,o,t,m,p in out], open(ROOT/'experiments/2026-10-08-bonta-review/review/role-pair-census.json','w'),indent=1)
