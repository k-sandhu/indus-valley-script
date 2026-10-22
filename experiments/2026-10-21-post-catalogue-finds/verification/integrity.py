"""Validate saved records and source text after a service interruption."""
import csv
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,RAW,save,csvrows,page_index

records=[];failures=[]
for p in sorted(OUT.rglob('*')):
    if not p.is_file() or p.name=='resume-integrity.json':continue
    r={'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix=='.json':
        try:json.loads(p.read_text(encoding='utf-8-sig'));r['valid_json']=True
        except (json.JSONDecodeError,UnicodeDecodeError):r['valid_json']=False;failures.append(r['file'])
    elif p.suffix=='.csv':
        with p.open(encoding='utf-8-sig',newline='') as f:
            data=list(csv.reader(f,strict=True))
        r['data_rows']=len(data)-1;r['whole_rows']=bool(data) and all(len(x)==len(data[0]) for x in data)
        if not r['whole_rows']:failures.append(r['file'])
    records.append(r)
sampling=json.loads((OUT/'sampling.json').read_text(encoding='utf-8'))
revision=json.loads((OUT/'input-revision.json').read_text(encoding='utf-8')) if (OUT/'input-revision.json').exists() else {}
known={r['input']:r['sha256'] for r in revision.get('inputs',[])}
inputs=[]
for name,sha in sampling['inputs'].items():
    p=ROOT/name;actual=hashlib.sha256(p.read_bytes()).hexdigest();documented=known.get(name)==actual
    inputs.append({'file':name,'unchanged':actual==sha,'documented_revision':documented,'sha256':actual})
    if actual!=sha and not documented:failures.append(name)
freeze=json.loads((OUT/'blind-freeze.json').read_text(encoding='utf-8'))
frozen_ok=hashlib.sha256((OUT/freeze['file']).read_bytes()).hexdigest()==freeze['sha256']
idx=page_index();page_records=[]
import re
for kind,name in [('blind','blind-assignments.csv'),('omission','omission-assignments.csv')]:
    for r in csvrows(OUT/name):
        source=r.get('primary_publication',r.get('source_id'))
        for n in re.findall(r'\d+',r['pdf_page']):
            paths=idx.get((source,int(n)),[])
            page_records.append({'sample':kind,'source_id':source,'pdf_page':int(n),'files':len(paths),'nonempty_files':sum(bool(p.read_text(encoding='utf-8-sig',errors='replace').strip()) for p in paths)})
output={'records':records,'input_hash_checks':inputs,'blind_freeze_unchanged':frozen_ok,'sampled_page_text':page_records,'failures':failures,'empty_sample_pages':[r for r in page_records if not r['nonempty_files']],'resume':'The model service interruption did not require a source conversion to be repeated. Empty text witnesses are retained as review limitations rather than treated as proof that a page contains no objects.'}
save('resume-integrity.json',output)
print('INTEGRITY',len(records),'files; failures',len(failures),'frozen unchanged',frozen_ok,'empty sampled pages',len(output['empty_sample_pages']))
