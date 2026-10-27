from pathlib import Path
import json
P=Path('experiments/2026-10-24-unit-source-pass2')
def fix(v):
 if isinstance(v,dict):
  for k,x in list(v.items()):
   if k=='logical_path' and x.startswith('D:'):
    v[k]=x.replace('\\','/').removeprefix('D:/projects/indus_valley_script/')
   else:fix(x)
 elif isinstance(v,list):
  for x in v:fix(x)
for stem in ['SOURCE-MANIFEST','results']:
 x=json.load(open(P/(stem+'-v1.json')));fix(x);x['repair']='v2 repairs Windows logical-path normalization; v1 preserved, scientific dispositions unchanged'
 with (P/(stem+'-v2.json')).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
code=(P/'verify.py').read_text().replace('SOURCE-MANIFEST-v1','SOURCE-MANIFEST-v2').replace('results-v1','results-v2').replace('verification-v1','verification-v2').replace("checks={'seven_unique_targets'","checks={'logical_paths_relative':all(not x['logical_path'].startswith('D:') for x in m['local_derivatives']),'seven_unique_targets'")
(P/'verify_v2.py').write_text(code)
for name in ['REPORT.md','DATA-UPDATE.md']:
 s=(P/name).read_text().replace('results-v1.json','results-v2.json').replace('SOURCE-MANIFEST-v1.json','SOURCE-MANIFEST-v2.json')
 (P/name).write_text(s)
