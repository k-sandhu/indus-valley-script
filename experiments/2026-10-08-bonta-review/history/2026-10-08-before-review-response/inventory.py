"""Inventory only the files created by Package Q, excluding supplied witnesses."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'

def main():
    rows=[]
    for base,kind in [(OWN,'owned'),(RAW,'local_raw')]:
        for p in sorted(base.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(base)
            if any(part.startswith('.') for part in rel.parts):continue
            if kind=='local_raw' and (rel.parts[0]=='captions' or rel.as_posix()=='papers/bonta-2024-partial-decipherment-2nd-ed.page-text.txt'):continue
            rows.append({'path':p.relative_to(ROOT).as_posix(),'category':kind,'action':'created',
              'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    # Self-hashing would be circular. The inventory has an explicit unhashed entry.
    target=OWN/'FILES.json';relative=target.relative_to(ROOT).as_posix()
    rows=[r for r in rows if r['path']!=relative]
    rows.append({'path':relative,'category':'owned','action':'created','sha256':None,'note':'Inventory itself; self-hash omitted'})
    x={'scope':'Every file created/changed by this package, excluding supplied unchanged captions and page text. No writes outside owned/local raw directories.',
       'owned_files':sum(r['category']=='owned' for r in rows),'local_raw_files':sum(r['category']=='local_raw' for r in rows),
       'files':rows}
    target.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in x.items() if k!='files'},indent=2))

if __name__=='__main__':main()
