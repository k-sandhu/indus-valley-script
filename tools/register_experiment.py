"""Append checked experiment entries to the manual research registry."""
from pathlib import Path
import argparse
import json

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('entry',help='JSON entry or list of entries, with repository-relative evidence paths')
    args=parser.parse_args()
    supplied=json.loads(Path(args.entry).read_text(encoding='utf-8'))
    entries=supplied if isinstance(supplied,list) else [supplied]
    registry_path=ROOT/'knowledge/experiments/registry.json'
    registry=json.loads(registry_path.read_text(encoding='utf-8'))
    current={row['id']:row for row in registry['experiments']}
    new=[]
    required=['id','theme','status','question','outcome','challenge','remedy','evidence','retry_when']
    for entry in entries:
        if any(key not in entry for key in required):
            raise ValueError('Missing registry fields: '+entry.get('id','unnamed'))
        for evidence in entry['evidence']:
            if not (ROOT/evidence).exists():
                raise ValueError('Missing evidence: '+evidence)
        if entry['id'] in current:
            if current[entry['id']]!=entry:
                raise ValueError('Existing entry differs; review a deliberate registry edit: '+entry['id'])
        else:
            current[entry['id']]=entry
            new.append(entry)
    registry['experiments'].extend(new)
    registry_path.write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'added':[row['id'] for row in new],'entries':len(registry['experiments'])}))

if __name__=='__main__':
    main()
