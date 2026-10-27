from pathlib import Path
import re, json, os
from urllib.parse import urlsplit, unquote
root=Path(__file__).resolve().parents[2]
files=[root/x for x in ['README.md','AGENTS.md','CONTRIBUTING.md','REPRODUCING.md','LOCAL_STORAGE.md','llms.txt','data/README.md','bench/README.md']]+sorted((root/'templates').glob('*.md'))+sorted((root/'.claude/skills').glob('*/SKILL.md'))+sorted(p for p in (root/'experiments/2026-10-27-documentation-cleanup').glob('*.md') if p.name not in ('PROMPT.md', 'final.md') and not p.name.lower().startswith('launch'))
links=[]
for f in files:
 text=f.read_text(encoding='utf-8'); text=re.sub(r'(?ms)^\s*(`{3,}|~{3,}).*?^\s*\1\s*$', '', text)
 text=re.sub(r'`[^`\n]+`', '', text)
 patterns=[r'\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)',r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)']
 for pat in patterns:
  for m in re.finditer(pat,text,re.M):
   target=m.group(1).strip('<>'); u=urlsplit(target)
   if u.scheme or target.startswith('//') or target.startswith('/') or not u.path: continue
   path=Path(os.path.abspath(f.parent / unquote(u.path)))
   record={'file':f.relative_to(root).as_posix(),'target':target}
   # Check ancestors before the target so a junction is never followed.
   parts=[]; q=path
   while q != q.parent and q != root: parts.append(q); q=q.parent
   blocked=any(os.path.isjunction(str(a)) or os.path.islink(str(a)) for a in reversed(parts))
   record['status']='unverified-local-link' if blocked else ('ok' if path.exists() else 'missing')
   links.append(record)
counts={k:sum(x['status']==k for x in links) for k in ('ok','missing','unverified-local-link')}
out={'scope':'relative Markdown link destinations in assigned entry documents; anchors and external URLs are not checked','counts':counts,'links':links}
(root/'experiments/2026-10-27-documentation-cleanup/link-check.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(counts)); print('\n'.join(str(x) for x in links if x['status']!='ok'))
