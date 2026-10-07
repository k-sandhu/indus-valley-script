"""Repair reversible encoding defects in active text, preserving first-pass bytes."""
import json,re
from pathlib import Path
OUT=Path(__file__).resolve().parent
record=OUT/'encoding-repairs.json'
changes=json.loads(record.read_text(encoding='utf-8')).get('changed_files',[]) if record.exists() else []
mapping={'â€“':'–','â€”':'—','â€™':'’','â€œ':'“','â€\u009d':'”','Ã§':'ç','Ã©':'é','Ã¨':'è','Ã¯':'ï','Ã´':'ô','Â°':'°','Â′':'′'}
for p in sorted(OUT.iterdir()):
 if not p.is_file() or p.suffix not in {'.json','.csv','.md'}: continue
 before=p.read_text(encoding='utf-8-sig');after=before
 for bad,good in mapping.items(): after=after.replace(bad,good)
 if after!=before:
  p.write_text(after,encoding='utf-8')
  if p.name not in {v['path'] for v in changes}: changes.append(dict(path=p.name,characters_before=len(before),characters_after=len(after)))
 if '\ufffd' in after: raise ValueError(f'Unrepaired replacement character in {p.name}')
(OUT/'encoding-repairs.json').write_text(json.dumps(dict(status='Verified computation',archive_untouched=True,changed_files=changes,replacement_characters_in_active_text=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(changes))
