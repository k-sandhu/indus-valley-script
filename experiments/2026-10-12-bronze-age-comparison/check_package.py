"""Audit final source bytes, displayed Greek markup and package links."""
from pathlib import Path
import hashlib
import json
import re
import sys
import unicodedata
from bs4 import BeautifulSoup

P=Path(__file__).resolve().parent;ROOT=P.parents[1]
LOCAL=ROOT/'data/raw/2026-10-12-bronze-age-comparison'
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
checks=[]
def check(name,value,detail=None):checks.append({'name':name,'passed':bool(value),'detail':detail})
for path in sorted((P/'acquisition').glob('*.json')):
    item=load(path)
    if item.get('local_path'):
        witness=ROOT/item['local_path']
        check('source witness '+item['id'],witness.exists() and digest(witness)==item['sha256'])

records=[json.loads(line) for line in (LOCAL/'normalized-v4/records.jsonl').read_text(encoding='utf-8').splitlines()]
cache={};tested=set()
for row in records:
    if row['corpus']!='mycenaean':continue
    if row['source'] not in cache:
        metadata=load(P/'acquisition'/f"{row['source']}.json")
        soup=BeautifulSoup((ROOT/metadata['local_path']).read_bytes(),'html.parser')
        cache[row['source']]={a.get('data-pk'):a for a in soup.select('table.table-text a[data-pk]')}
    for ref in row['source_word_refs']:
        if (row['source'],ref) in tested:continue
        tested.add((row['source'],ref));anchor=cache[row['source']][ref]
        text=anchor.get_text('',strip=True)
        bad=set('[]?#⸢⸣⸤⸥〈〉⟨⟩…<>•↓↑→←↵')
        valid=bool(text.strip()) and not any(c in bad or unicodedata.combining(c) for c in unicodedata.normalize('NFD',text))
        check('retained Greek printed certainty '+row['source']+':'+str(ref),valid)

for directory in ['run-v1','run-v2']:
    for name,expected in load(P/directory/'output-hashes.json').items():check('frozen '+directory+'/'+name,digest(P/directory/name)==expected)
for run in ['run-v1','run-v2']:
    manifest=load(P/run/'manifest.json')
    code=P/'analyze.py' if run=='run-v2' else P/'history/statistical-endpoint-v1/analyze.py'
    parser=P/'reference_sources.py' if run=='run-v2' else P/'history/statistical-endpoint-v1/reference_sources.py'
    check(run+' code snapshot',digest(code)==manifest['analysis_code_sha256'])
    check(run+' parser snapshot',digest(parser)==manifest['parser_code_sha256'])
for source in load(P/'baseline-v1.json')['files'][5:]:check('starting non-navigation '+source['path'],digest(ROOT/source['path'])==source['sha256'])

for item in load(P/'CLAIM-EVIDENCE.json'):
    for name in item['evidence']:
        if name=='category-replay-verification-v2.json' and not (P/name).exists():check(item['id']+' replay finished',False)
        else:check(item['id']+' evidence '+name,(P/name).is_file())
for path in P.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        target=target.strip('<>').split('#')[0]
        if not target or target.startswith(('https:','http:','mailto:')):continue
        if target=='package-verification.json':continue  # This check writes its own final report afterwards.
        check('local link '+path.name+' -> '+target,(path.parent/target).exists())
for name in ['run-v2/verification.json','sign-control-v2/verification.json','category-replay-verification-v2.json']:
    check(name+' passes',load(P/name)['status']=='passed')
check('primary prose flags',load(P/'prose-review-v1.json')['flags']==[])
integration=P/'integration-v1.json'
if integration.exists():
    registry=load(ROOT/'knowledge/experiments/registry.json')
    ids={entry['id'] for entry in registry['experiments']}
    record=load(integration)
    for identity in record['new_registry_ids']:check('research registry '+identity,identity in ids)
    for rel in ['README.md','knowledge/INDEX.md','knowledge/retrospectives/README.md']:
        check('research navigation '+rel,'2026-10-12-bronze-age-comparison' in (ROOT/rel).read_text(encoding='utf-8'))

summary={'status':'passed' if all(c['passed'] for c in checks) else 'failed','checks':len(checks),
         'passed':sum(c['passed'] for c in checks),'failed':[c for c in checks if not c['passed']],
         'source_witnesses_checked':sum(c['name'].startswith('source witness ') for c in checks),
         'Greek_displayed_tokens_checked':len(tested),'scope':'source byte integrity, displayed certainty, evidence pointers and named preservation scope'}
name=sys.argv[1] if len(sys.argv)>1 else 'package-verification.json'
with (P/name).open('x',encoding='utf-8') as handle:json.dump(summary,handle,indent=2);handle.write('\n')
print(json.dumps(summary))
assert summary['status']=='passed'
