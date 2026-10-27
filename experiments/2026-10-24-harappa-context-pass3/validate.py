import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/'source-manifest.json').read_text(encoding='utf8'))
checks={}
for i,f in enumerate(m['files']):
 x=Path(f['physical_path']); checks[f'file_{i}']=x.exists() and x.stat().st_size==f['bytes'] and hashlib.sha256(x.read_bytes()).hexdigest()==f['sha256']
for n,h in json.loads((p/'protocol-sha256.json').read_text()).items():checks[n]=hashlib.sha256((p/n).read_bytes()).hexdigest()==h
s=json.loads((p/'summary-v1.json').read_text()); checks['five_cases']=s['cases']==5; checks['context_gain']=s['cases_with_new_context_detail']==1;checks['no_independent_lineage']=s['new_independent_excavation_lineages']==0;checks['conflict_retained']=s['lot_conflicts_resolved']==0
checks['pages']=s['source_pages_visually_inspected']==6
out={'kind':'author source/accounting validation; no separate specialist review','checks':checks,'passed':all(checks.values())}
(p/'validation-v1.json').write_text(json.dumps(out,indent=2)+'\n')
assert out['passed']
print(json.dumps({'passed':out['passed'],'checks':len(checks)}))
