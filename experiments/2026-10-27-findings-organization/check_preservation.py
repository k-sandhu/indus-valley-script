"""Check preserved card values, source snapshots and limited navigation edits."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import kb

def original(path):
    return subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'show','HEAD:'+path],cwd=ROOT,capture_output=True,check=True).stdout

def snapshot(path):
    b=(PACKAGE/'baseline'/path).read_bytes()
    return b.removeprefix(b'````markdown\n').removesuffix(b'\n````\n')

def check():
    errors=[];rows=[]
    for path in sorted((ROOT/'knowledge/findings').glob('F-*.md')):
        n=int(path.name[2:6])
        if n>38:continue
        relative=path.relative_to(ROOT).as_posix();before=original(relative);after=path.read_bytes()
        bf,bb=kb.frontmatter(before.decode('utf-8-sig'));af,ab=kb.frontmatter(after.decode('utf-8-sig'))
        same_fields=bf==af;same_body=bb==ab
        if not same_fields or not same_body:errors.append(relative+': changed card fields or body')
        if n<=35 and before!=after:errors.append(relative+': bytes changed outside allowed quoting set')
        if n>=36:
            expected=re.sub(rb'(?m)^(id|status_class|area|date): ([^"\r\n][^\r\n]*)',lambda m:m[1]+b': "'+m[2]+b'"',before)
            if after!=expected:errors.append(relative+': edit differs from four scalar-quoting changes')
        rows.append({'path':relative,'same_fields':same_fields,'same_body':same_body,'byte_identical':before==after})
    for name in ['INDEX.md','TIMELINE.md','WORKING-MODEL.md','retrospectives/README.md']:
        before=snapshot(name)
        if before!=original('knowledge/'+name):errors.append(name+': baseline differs from initial committed document')
    base=snapshot('WORKING-MODEL.md');model=(ROOT/'knowledge/WORKING-MODEL.md').read_bytes()
    if not model.startswith(base):errors.append('Working model original bytes are not an unchanged prefix')
    appended=model[len(base):].decode('utf-8')
    if re.findall(r'^## .+$',appended,re.M)!=['## Conjectures outside the integrated model']:errors.append('Working model append must have exactly one named section')
    if len(re.findall(r'^- 2026-10-27:',appended,re.M))!=1:errors.append('Working model must have one dated changelog line')
    links=re.findall(r'^- \[(C-\d{4})\]',appended,re.M)
    if len(links)!=14:errors.append('Working model must add fourteen conjecture links')
    if re.search(r'\bCredence\s+[0-9]',appended):errors.append('Model appendix triggers headline detector')
    for name in ['TIMELINE.md','retrospectives/README.md']:
        before=snapshot(name).decode('utf-8-sig').replace('\r\n','\n')
        after=(ROOT/'knowledge'/name).read_text(encoding='utf-8-sig')
        kept=before[before.index('# 2026-10-12'):] if name=='TIMELINE.md' else before.rstrip()
        if kept not in after:errors.append(name+': historical narrative changed')
    before=snapshot('INDEX.md').decode('utf-8-sig').replace('\r\n','\n')
    after=(ROOT/'knowledge/INDEX.md').read_text(encoding='utf-8-sig')
    # Every original narrative section body remains verbatim; headings may change level.
    for block in re.split(r'(?m)(?=^## )',before):
        if not block.startswith('## '):continue
        head,body=block.split('\n',1)
        if body.strip() not in after:errors.append('Index lost original narrative block: '+head)
    for path in json.loads((PACKAGE/'new-cards.json').read_text()):
        f,_=kb.frontmatter((ROOT/path).read_text(encoding='utf-8-sig'))
        attempt=json.loads((ROOT/'knowledge/registry/attempts'/(f['registry_ids'][0]+'.json')).read_text(encoding='utf-8-sig'))
        if f['authors']!=attempt['authors']:errors.append(path+': original author list differs')
    result={'status':'fail' if errors else 'pass','existing_cards':len(rows),'unchanged_card_fields':sum(r['same_fields'] for r in rows),'unchanged_card_bodies':sum(r['same_body'] for r in rows),'byte_identical_existing_cards':sum(r['byte_identical'] for r in rows),'quoting_only_cards':3,'new_card_author_lists':9,'model_links_added':len(links),'errors':errors,'cards':rows}
    return result

if __name__=='__main__':
    result=check();(PACKAGE/'preservation-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cards'},indent=2));sys.exit(bool(result['errors']))
