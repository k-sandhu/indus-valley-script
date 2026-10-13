"""Select a deterministic, site-stratified Linear B availability cohort."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
record=json.loads((PACKAGE/'acquisition/liber-tablet-data-v1.json').read_text(encoding='utf-8'))
rows=json.loads((ROOT/record['local_path']).read_bytes())['data']
sites=defaultdict(list)
for row in rows:
    sites[row[2]].append(row)
selected=[]
for site in sorted(sites):
    selected.extend(sorted(sites[site], key=lambda r: hashlib.sha256(f'20261012:{r[1]}'.encode()).hexdigest())[:96])
plan=[{'id':f'liber-doc-{row[1]}-v1','url':f'https://liber.cnr.it/tablet/view/{row[1]}'} for row in selected if row[1]!=201]
plan.extend([
 {'id':'akkadian-rimanum-v1','url':'https://oracc.museum.upenn.edu/json/rimanum.zip'},
 {'id':'rimanum-docs-v1','url':'https://oracc.museum.upenn.edu/rimanum/'},
 {'id':'egyptian-aed-tree-v1','url':'https://api.github.com/repos/simondschweitzer/aed-tei/git/trees/master'},
 {'id':'egyptian-aed-readme-v1','url':'https://raw.githubusercontent.com/simondschweitzer/aed-tei/master/README.md'},
 {'id':'egyptian-archive-fixture-v1','url':'https://raw.githubusercontent.com/simondschweitzer/aed-tei/master/files/22QMKN7KS5CDNE7TCYA3AW4LC4.xml'},
 {'id':'egyptian-tomb-fixture-v1','url':'https://raw.githubusercontent.com/simondschweitzer/aed-tei/master/files/2235T5FM5VFNLFTZN7P3MXW46U.xml'},
])
destination=PACKAGE/'acquisition-plan-v5.json'
with destination.open('x',encoding='utf-8') as handle:
    json.dump(plan,handle,indent=2); handle.write('\n')
manifest={'catalogue_sha256':record['sha256'],'selection_rule':'first 96 per site by SHA256(20261012:id)',
          'sites':{s:len(sites[s]) for s in sorted(sites)},'selected_per_site':{s:min(96,len(sites[s])) for s in sorted(sites)},
          'selected_documents':len(selected),'preexisting_fixture_201_in_selected':any(r[1]==201 for r in selected)}
(PACKAGE/'cohort-selection-v1.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected_documents':len(selected),'requests':len(plan)}))
