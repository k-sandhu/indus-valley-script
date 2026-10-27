"""Check hashes, source coordinates and record joins independently of the builder."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args(); run=Path(a.run); dest=Path(a.out)
    if dest.exists():raise SystemExit('Preserve the existing audit.')
    manifest=json.loads((run/'input-manifest.json').read_text(encoding='utf-8'))
    failures=[];cache={};refs=0
    for name,expected in manifest['inputs'].items():
        p=ROOT/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:failures.append('input hash: '+name)
    def visit(x):
        nonlocal refs
        if isinstance(x,dict):
            if set(['path','sha256','json_pointer']).issubset(x):
                refs+=1;p=ROOT/x['path']
                if x['path'] not in cache:
                    b=p.read_bytes();cache[x['path']]=(hashlib.sha256(b).hexdigest(),json.loads(b) if p.suffix=='.json' else None)
                actual,node=cache[x['path']]
                if actual!=x['sha256']:failures.append('reference hash: '+x['path'])
                if x['json_pointer']:
                    try:
                        for token in x['json_pointer'].strip('/').split('/'):
                            token=token.replace('~1','/').replace('~0','~')
                            node=node[int(token)] if isinstance(node,list) else node[token]
                    except (TypeError,ValueError,IndexError,KeyError):failures.append('pointer: '+x['path']+'#'+x['json_pointer'])
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
    rows={}
    for name in ['measurements','sources','chronology-parts','radiocarbon','horizons','absence-records']:
        rows[name]=[json.loads(l) for l in (run/(name+'.jsonl')).read_text(encoding='utf-8').splitlines()]
        visit(rows[name])
    table=json.loads((run/'town-axis-table.json').read_text(encoding='utf-8'));visit(table)
    source_ids={s['source_id'] for s in rows['sources']}
    dangling=[]
    for d in rows['radiocarbon']:
        if d.get('source_id') and d['source_id'] not in source_ids:dangling.append(d['source_id'])
    # Retain unresolved source keys as findings, rather than make a false source join.
    for s in table['towns']:
        if not isinstance(s['missing'],dict):failures.append('missingness map: '+s['town'])
    epochs=Counter((r['town'],r['values'].get('lab_no',r['values'].get('lab_code'))) for r in rows['radiocarbon'])
    new=[r for r in rows['measurements'] if r['cohort']=='new']
    if len(new)!=2 or any(r['sigma_reported_deg'] is not None for r in new):failures.append('new picks must retain unknown total sigma')
    for town in ['surkotada','farmana']:
        old=[h for h in rows['horizons'] if h['town']==town and h.get('exclusion_reason')]
        corrected=[h for h in rows['horizons'] if h['town']==town and h['usable_at_corrected_site']]
        if not old or not corrected:failures.append('horizon correction not preserved: '+town)
    value=dict(status='pass' if not failures else 'fail',failures=failures,input_files=len(manifest['inputs']),
        record_references_checked=refs,distinct_reference_files=len(cache),
        unresolved_radiocarbon_source_keys=sorted(set(dangling)),
        distinct_town_and_lab_labels=len(epochs),unlabelled_radiocarbon_assertions=sum(n for (town,lab),n in epochs.items() if not lab),
        note='Lab-label keys are not adjudicated samples. Repeated assertions and conflicting phase attributions remain separate.')
    with dest.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2)
    print(json.dumps(value,indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
