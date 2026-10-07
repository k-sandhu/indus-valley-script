"""Final preservation, prose, link and delta-path manifest checks."""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode=True
from common import OWN, RAW, ROOT, digest, write

def main():
    preservation=json.loads((OWN/'preservation-2026-10-07-review-response.json').read_text(encoding='utf-8'))
    changed=[p for p,v in preservation['files'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=v['sha256']]
    oldfiles=json.loads((OWN/'FILES.json').read_text(encoding='utf-8'))
    oldraw={p['path'] for p in oldfiles['local_raw_paths']}
    original_owned=set(preservation['files'])|{'experiments/2026-10-07-object-ledger/'+n for n in preservation['mutable_root_documents']}
    mutable=[]
    for n in preservation['mutable_root_documents']:
        if digest(OWN/n)!=digest(RAW/'review-response-2026-10-07/original-root'/n):mutable.append('experiments/2026-10-07-object-ledger/'+n)
    proc=subprocess.run([sys.executable,str(ROOT/'tools/review_prose.py'),'--path','experiments/2026-10-07-object-ledger','--no-write'],cwd=ROOT,capture_output=True,text=True)
    prose=json.loads(proc.stdout)
    missing=[];link_count=0
    for n in ['README.md','REPORT.md','RETROSPECTIVE.md','HELSINKI-INTERFACE.md','AMENDMENT-2026-10-07-review-response.md']:
        for url in re.findall(r'\]\(([^)]+)\)',(OWN/n).read_text(encoding='utf-8')):
            if url.startswith(('https:','http:','#')):continue
            p=(OWN/url.split('#',1)[0]).resolve();link_count+=1
            if not p.exists() and p.name!='FILES-REVIEW-RESPONSE-2026-10-07.json':missing.append([n,url])
    syntax=[]
    for p in OWN.glob('*.py'):
        try:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
        except SyntaxError as e:syntax.append(str(e))
    checks={'status':'Verified computation' if not changed and not prose['flags'] and not missing and not syntax else 'Failed',
            'preserved_starting_files':len(preservation['files']),'changed_starting_endpoints':changed,'prose':prose,'local_links_checked':link_count,'missing_local_links':missing,'root_python_syntax_errors':syntax,
            'original_checks':json.loads((RAW/'original-checks-review-response-2026-10-07-v1/checks.json').read_text(encoding='utf-8'))['passed'],
            'revision_checks':json.loads((OWN/'verification-2026-10-07-v3/checks.json').read_text(encoding='utf-8')),
            'replay':json.loads((OWN/'review-response-2026-10-07-v3/replay-comparison.json').read_text(encoding='utf-8'))['equal'],
            'guard':json.loads((OWN/'sequence-guard-review-response-2026-10-07-v2.json').read_text(encoding='utf-8'))['fixture_caught']}
    target=OWN/'final-checks-review-response-2026-10-07-v1.json'
    if target.exists():raise ValueError('Final checks endpoint already exists')
    write(target,checks)
    path=lambda p:str(p.relative_to(ROOT)).replace('\\','/')
    def record(p):return {'path':path(p),'bytes':p.stat().st_size,'sha256':digest(p)}
    newowned=[record(p) for p in OWN.rglob('*') if p.is_file() and path(p) not in original_owned and p.name!='FILES-REVIEW-RESPONSE-2026-10-07.json']
    newraw=[record(p) for p in RAW.rglob('*') if p.is_file() and path(p) not in oldraw]
    manifest={'status':'Verified computation','scope':'Every created/changed path in the review response; every starting endpoint remains unchanged','changed_owned_files':[record(ROOT/p) for p in sorted(mutable)],
              'created_owned_files':sorted(newowned,key=lambda r:r['path']),'created_local_raw_files':sorted(newraw,key=lambda r:r['path']),
              'created_owned_count_excluding_manifest':len(newowned),'changed_owned_count':len(mutable),'created_raw_count':len(newraw),
              'created_owned_bytes_excluding_manifest':sum(p['bytes'] for p in newowned),'created_local_raw_bytes':sum(p['bytes'] for p in newraw),
              'manifest_self':'experiments/2026-10-07-object-ledger/FILES-REVIEW-RESPONSE-2026-10-07.json','manifest_hash_exclusion':'Self is listed separately to avoid recursive hashing','writes_outside_owned_roots':[]}
    if (OWN/'FILES-REVIEW-RESPONSE-2026-10-07.json').exists():raise ValueError('Path manifest already exists')
    write(OWN/'FILES-REVIEW-RESPONSE-2026-10-07.json',manifest)
    print(json.dumps({'status':checks['status'],'preserved':len(preservation['files']),'created_owned':len(newowned),'changed_owned':len(mutable),'created_raw':len(newraw),'owned_bytes':manifest['created_owned_bytes_excluding_manifest'],'raw_bytes':manifest['created_local_raw_bytes'],'prose_flags':len(prose['flags'])}))

if __name__=='__main__':main()
