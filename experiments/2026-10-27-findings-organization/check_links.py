"""Check relative Markdown targets in the exact owned changed-path list.

Uses lexical path normalization, so checking a checkout link never enumerates
the bulk-data junction. Checks paths, Markdown anchors and JSON Pointers.
"""
import json
import os
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
from urllib.parse import unquote, urlsplit

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]

def targets(text):
    fenced=False
    for number,line in enumerate(text.splitlines(),1):
        if re.match(r'^\s*(```|~~~)',line):fenced=not fenced;continue
        if fenced:continue
        line=re.sub(r'`[^`]*`','',line)
        for m in re.finditer(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)',line):yield number,m[1].strip('<>')
        for m in re.finditer(r'!?\[[^\]]*\]\(',line):
            start=m.end();level=1;angle=False;escaped=False
            for i in range(start,len(line)):
                c=line[i]
                if escaped:escaped=False
                elif c=='\\':escaped=True
                elif c=='<':angle=True
                elif c=='>':angle=False
                elif not angle and c=='(':level+=1
                elif not angle and c==')':
                    level-=1
                    if level==0:
                        value=line[start:i].strip()
                        yield number,value[1:value.index('>')] if value.startswith('<') else re.split(r'\s+[\"\']',value)[0]
                        break

def anchor(text):
    seen={};out=set()
    for h in re.findall(r'(?m)^#{1,6}\s+(.+?)\s*#*$',text):
        h=re.sub(r'!?\[([^\]]+)\]\([^)]*\)',r'\1',h).replace('`','')
        slug=re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-')
        n=seen.get(slug,0);seen[slug]=n+1;out.add(slug+(f'-{n}' if n else ''))
    return out

def check(paths):
    errors=[];checked=0;external=0;rows=[]
    for relative in paths:
        p=ROOT/relative
        if p.suffix.lower()!='.md':continue
        text=p.read_text(encoding='utf-8-sig');count=0
        for line,value in targets(text):
            if urlsplit(value).scheme or value.startswith('//'):external+=1;continue
            file,_,fragment=value.partition('#');file=unquote(file.split('?',1)[0])
            target=Path(os.path.abspath(p.parent/file)) if file else p
            checked+=1;count+=1
            error=None
            if not target.exists():error='missing target'
            elif fragment and target.is_file() and target.suffix.lower()=='.md':
                if unquote(fragment) not in anchor(target.read_text(encoding='utf-8-sig')):error='missing Markdown anchor'
            elif fragment.startswith('/') and target.is_file() and target.suffix=='.json':
                try:
                    node=json.loads(target.read_text(encoding='utf-8-sig'))
                    for token in fragment[1:].split('/'):
                        token=unquote(token).replace('~1','/').replace('~0','~');node=node[int(token)] if isinstance(node,list) else node[token]
                except (KeyError,ValueError,IndexError,TypeError):error='missing JSON Pointer'
            if error:errors.append({'file':relative,'line':line,'target':value,'error':error})
        rows.append({'path':relative,'relative_links':count})
    return {'status':'fail' if errors else 'pass','markdown_files':len(rows),'relative_links':checked,'external_links_skipped':external,'errors':errors,'files':rows}

if __name__=='__main__':
    changed=json.loads((PACKAGE/'changed-paths.json').read_text(encoding='utf-8'))
    result=check(changed['paths'] if isinstance(changed,dict) else changed)
    (PACKAGE/'link-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False,indent=2))
    sys.exit(bool(result['errors']))
