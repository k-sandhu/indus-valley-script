"""Acquire source-text extent, object identity and dates for the jar-label cohort."""
from pathlib import Path
import json

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
def payload(name):
    meta=json.loads((PACKAGE/'acquisition'/f'{name}.json').read_text(encoding='utf-8'))
    return json.loads((ROOT/meta['local_path']).read_bytes())
commit=payload('egyptian-aed-tree-v1')['sha']
records=payload('egyptian-aes-archive-v1')
texts=sorted({row['text'] for row in records.values() if row['date']=='OK & FIP'})
plan=[{'id':f'aed-text-{text.lower()}-v1',
       'url':f'https://raw.githubusercontent.com/simondschweitzer/aed-tei/{commit}/files/{text}.xml'} for text in texts]
with (PACKAGE/'acquisition-plan-v6.json').open('x',encoding='utf-8') as handle:
    json.dump(plan,handle,indent=2);handle.write('\n')
(PACKAGE/'egyptian-metadata-selection-v1.json').write_text(json.dumps({'commit':commit,'texts':len(texts),
    'selection':'Every source text represented by OK & FIP archive sentences; no score-based selection.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'texts':len(texts),'commit':commit}))
