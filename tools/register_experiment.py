"""Create checked per-entry records, then regenerate navigation with kb.py."""
from pathlib import Path
import argparse
import json
import re
import kb

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('entry',help='JSON entry or list of entries, with repository-relative evidence paths')
    args=parser.parse_args()
    supplied=json.loads(Path(args.entry).read_text(encoding='utf-8-sig'))
    entries=supplied if isinstance(supplied,list) else [supplied]
    attempt_dir=kb.ROOT/'knowledge/registry/attempts'
    current={path.stem:json.loads(path.read_text(encoding='utf-8')) for path in attempt_dir.glob('*.json')}
    new=[]
    required=list(kb.ATTEMPT_FIELDS)
    for entry in entries:
        # Historical integrated package entries lack the added navigation fields.
        # An identical supplied subset is a no-op, never a replacement.
        if entry.get('id') in current:
            existing=current[entry['id']]
            if not all(key in existing and existing[key]==value for key,value in entry.items()):
                raise ValueError('Existing entry differs; review a deliberate registry edit: '+entry['id'])
            if any(key not in entry for key in required if key not in ('status_class','area')):
                raise ValueError('Missing registry fields: '+entry['id'])
            continue
        if any(key not in entry for key in required):
            raise ValueError('Missing registry fields: '+entry.get('id','unnamed'))
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',entry['id']):
            raise ValueError('Invalid experiment ID')
        if entry['area'] not in kb.AREAS or entry['status_class'] not in kb.STATUSES:
            raise ValueError('Invalid area or status class: '+entry['id'])
        if not isinstance(entry['evidence'],list):
            raise ValueError('Evidence must be a list')
        for evidence in entry['evidence']:
            path=(kb.ROOT/evidence.split('#',1)[0]).resolve()
            if not path.is_relative_to(kb.ROOT) or not path.exists():
                raise ValueError('Missing evidence: '+evidence)
        if entry['id'] in current:
            if current[entry['id']]!=entry:
                raise ValueError('Existing entry differs; review a deliberate registry edit: '+entry['id'])
        else:
            if 'registry_order' in entry:
                raise ValueError('New entries omit registry_order: '+entry['id'])
            current[entry['id']]=entry
            new.append(entry)
    # Validate the complete input before writing any entry. Refuse replacement.
    attempt_dir.mkdir(parents=True,exist_ok=True)
    for entry in new:
        with (attempt_dir/(entry['id']+'.json')).open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(kb.json_text(entry))
    changed=kb.build()
    print(json.dumps({'added':[row['id'] for row in new],'entries':len(current),'generated_changed':changed}))

if __name__=='__main__':
    main()
