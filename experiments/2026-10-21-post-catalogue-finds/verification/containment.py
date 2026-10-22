"""Check the baseline identities behind the six containment decisions."""
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,csvrows,inputpath,save,skip_value
from joins import registration

decoder=json.JSONDecoder()
def identity(s,start=0,nested=False):
    allowed={'excavation'} if nested else {'cisi','col3_excavation','printed_page'}
    i=start+1;out={}
    while True:
        while s[i].isspace() or s[i]==',':i+=1
        if s[i]=='}':return out,i+1
        key,i=decoder.raw_decode(s,i)
        while s[i].isspace() or s[i]==':':i+=1
        if key=='parsed' and not nested:out[key],i=identity(s,i,True)
        elif key in allowed:out[key],i=decoder.raw_decode(s,i)
        else:i=skip_value(s,i)

entries={};inputs=[]
for vol in (1,2):
    p=ROOT/f'data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi{vol}-basic-data.jsonl'
    if not p.exists():inputs.append({'volume':vol,'available':False});continue
    inputs.append({'volume':vol,'available':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    with p.open(encoding='utf-8-sig') as f:
        for line in f:
            d,_=identity(line)
            k=re.sub('[^a-z0-9]','',str(d.get('cisi','')).lower())
            entries[k]=d
rows={r['row_id']:r for r in csvrows(inputpath('objects.csv'))};checks=[]
for d in csvrows(inputpath('join-decisions.csv')):
    if d['match_basis']!='catalogue-containment':continue
    r=rows[d['row_id']];numbers=re.findall(r'\b[A-Z][a-z]*-\d+\b',r.get('cisi_in_baseline',''))
    found=[]
    for number in numbers:
        entry=entries.get(re.sub('[^a-z0-9]','',number.lower()))
        ev={'cisi':number,'basic_data_entry_found':bool(entry),'registration_tie':False}
        if entry:
            raw=[entry.get('col3_excavation',''),(entry.get('parsed') or {}).get('excavation','')]
            values=[]
            for v in raw:
                if isinstance(v,list):values.extend(str(x) for x in v)
                elif isinstance(v,str):values.append(v)
            a=registration(r['registration'])
            ev['registration_tie']=bool(a and any(registration(v)==a for v in values))
        found.append(ev)
    checks.append({'row_id':r['row_id'],'cited_baseline_ids':found,'row_has_registration':bool(r['registration']),'interpretation':'Baseline-number presence is checked separately from the identity tie to the reported object. No baseline excavation value is reproduced.'})
save('catalogue-containment-check.json',{'inputs':inputs,'decisions_checked':len(checks),'checks':checks,'projection':'Only CISI identifiers, excavation identities and printed-page metadata decoded. Other source values skipped.'})
print('BASELINE',len(checks),'decisions checked;',sum(x['basic_data_entry_found'] for r in checks for x in r['cited_baseline_ids']),'cited entries found')
