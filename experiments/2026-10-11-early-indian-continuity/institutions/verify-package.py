"""Verify frozen inputs, reproduction, refusal behavior and package links."""
from pathlib import Path
import ast
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RAW=ROOT/'data/raw/2026-10-11-early-indian-continuity/institutions'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,value):
    checks.append({'check':name,'passed':bool(value)})
    if not value:raise AssertionError(name)

for file in HERE.glob('*.py'):
    ast.parse(file.read_text(encoding='utf-8'));check('Python syntax: '+file.name,True)
for endpoint in ['run-v1','run-v2']:
    data=json.loads((HERE/endpoint/'audit.json').read_text(encoding='utf-8'))
    for name,digest in data['input_hashes'].items():check(endpoint+' frozen input: '+name,sha(HERE/name)==digest)

v2=json.loads((HERE/'run-v2/audit.json').read_text(encoding='utf-8'))
reproduction=json.loads((RAW/'audit-reproduction-v2/audit.json').read_text(encoding='utf-8'))
check('Reproduction matches all fields except creation time',
      {k:v for k,v in v2.items() if k!='created_utc'}=={k:v for k,v in reproduction.items() if k!='created_utc'})
before=sha(HERE/'run-v2/audit.json')
result=subprocess.run([sys.executable,'-B',str(HERE/'audit-v2.py'),'--output',str(HERE/'run-v2')],capture_output=True,text=True)
check('Preexisting output refused',result.returncode!=0 and 'Refusing preexisting output' in result.stderr)
check('Refusal preserves frozen output',before==sha(HERE/'run-v2/audit.json'))

for p in HERE.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if target=='verification.json':continue  # This invocation creates that result after checks.
        if not re.match(r'(https?://|#)',target):check(p.name+' relative link: '+target,(p.parent/target).exists())
for row in v2['rice_classification_sensitivity']['bounds']:
    check('Manual endpoint addition '+row['observation']+' '+row['context'],
          round(row['domesticated']+row['uncertain'],2)==row['domesticated_upper'])
check('Selected data counts',v2['counts']=={'sources':14,'observations':30,'claims':7,'witnesses_verified':31,'checks_passed':146})
check('Strict cross-domain requirement leaves none',not v2['sensitivity'][-1]['candidate_hypotheses_passing_declared_requirements'])
out=HERE/'verification.json'
if out.exists():raise FileExistsError(out)
out.write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,
                           'checks_passed':len(checks),'audit_checks_passed':146,
                           'scope':'Local package integrity and reproduction; independent source review is documented by the parent review package.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks_passed':len(checks),'audit_checks_passed':146}))
