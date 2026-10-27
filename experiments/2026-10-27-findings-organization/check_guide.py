"""Validate the findings-guide contract and exact one-card-one-theme coverage."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import kb

def check():
    directory=ROOT/'knowledge/findings'
    cards={p.name[:6]:p for p in directory.glob('F-*.md')}
    guide=(directory/'README.md').read_text(encoding='utf-8')
    errors=[];counts=Counter();themes={};section=None;uncarded=0
    final='Results recorded in packages but not yet carded'
    if not guide.startswith('# Findings\n'):errors.append('Missing exact title')
    headings=re.findall(r'^## (.+)$',guide,re.M)
    if not headings or headings[-1]!=final or headings.count(final)!=1:errors.append('Final section missing, duplicated or misplaced')
    for line in guide.splitlines():
        if line.startswith('## '):
            section=line[3:]
            if section!=final:themes[section]=0
            continue
        if re.match(r'^#{3,}',line):errors.append('Unexpected nested heading: '+line)
        if re.match(r'^\s+[-*+] ',line):errors.append('Nested list: '+line)
        if line.startswith('- '):
            if section==final:
                m=re.fullmatch(r'- \[([^\]]+)\]\(([^)]+)\) .+ \*([\w-]+)\*, ([\w-]+)',line)
                if not m or m[1].startswith('F-'):errors.append('Malformed package line: '+line)
                else:
                    uncarded+=1
                    record=ROOT/'knowledge/registry/attempts'/(m[1]+'.json')
                    if not record.exists():errors.append('Unknown attempt '+m[1])
                    else:
                        f=json.loads(record.read_text(encoding='utf-8-sig'))
                        if m[3]!=f['status_class'] or m[4]!=(f.get('verification_tier') or 'unrecorded'):errors.append('Attempt status or tier differs: '+m[1])
                continue
            m=re.fullmatch(r'- \[(F-\d{4})\]\(([^/)]+\.md)\) .+ \*([\w-]+)\*',line)
            if not m or section not in themes:errors.append('Malformed card line: '+line);continue
            identifier,name,status=m.groups();counts[identifier]+=1;themes[section]+=1
            if identifier not in cards or cards[identifier].name!=name:errors.append('Card filename mismatch: '+identifier)
            elif kb.frontmatter(cards[identifier].read_text(encoding='utf-8-sig'))[0]['status_class']!=status:errors.append('Card status differs: '+identifier)
    for identifier in sorted(set(cards)|set(counts)):
        if counts[identifier]!=1:errors.append(f'{identifier}: {counts[identifier]} appearances')
    if not 7<=len(themes)<=10:errors.append('Expected seven to ten themes')
    return {'status':'fail' if errors else 'pass','cards':len(cards),'card_lines':sum(counts.values()),'themes':themes,'uncarded_attempts':uncarded,'errors':errors}

if __name__=='__main__':
    result=check();(PACKAGE/'guide-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
