"""Check saved work and remove completed OCR renders within the owned root."""
import ast
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

owned, raw, package = [Path(x).resolve() for x in sys.argv[1:4]]
checks = []
for path in owned.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'))
    checks.append(path.name)
data = json.loads((raw / 'text-extraction.json').read_text(encoding='utf-8'))
empty = []
for rec in data:
    paths = list((raw / 'text' / rec['source_id']).glob('p*.txt'))
    assert len(paths) == rec['pages'], rec['source_id']
    empty.extend(str(p.relative_to(raw)) for p in paths if not p.read_text(encoding='utf-8').strip())
deleted = []
target = (raw / 'ocr-work').resolve()
assert target.is_relative_to(raw.resolve())
for path in target.rglob('*.png'):
    assert path.resolve().is_relative_to(target)
    page = raw / 'text' / path.parent.name / (path.stem + '.txt')
    assert page.exists()
    path.unlink()
    deleted.append(str(path.relative_to(raw)))
expected = (package / 'PROTOCOL.sha256').read_text().split()[0]
assert hashlib.sha256((package / 'PROTOCOL.md').read_bytes()).hexdigest() == expected
text = (raw / 'text/hrp-parpola-2019/p0002.txt').read_text(encoding='utf-8')
flat = re.sub(r'\s+', ' ', text)
m = re.search(r'one rod excavated at (.{1,40}?) by (.{1,40}?)\s*\(no\.?\s*(\d+)\)',flat)
rodpart = re.search(r'one rod.{0,320}',flat)
rod_at=flat.find('one rod')
entry_hint=re.findall(r'\bno\.?\s*(\d+)',flat[max(0,rod_at-100):rod_at]) if rod_at>=0 else []
rod_identity = {'place_terms':re.findall(r'\b(?:Mohenjo.daro|Harappa)\b',rodpart.group(),re.I),'proper_names':re.findall(r'\b[A-Z][a-z]{2,20}\b',rodpart.group()),'reference_numbers':re.findall(r'\bno\.?\s*(\d+)',rodpart.group())} if rodpart else None
catalogue_relations = re.findall(r'(H-311\s+to\s+H-318|H-796.{0,5}H-1125)', flat)
headers = {}
for sid, page in [('lkd-biagi-2022',13),('lkd-biagi-2022',18),('hrp-parpola-2019',2),('chn-didier-2017',25)]:
    txt=(raw / 'text' / sid / f'p{page:04}.txt').read_text(encoding='utf-8')
    lines=[x.strip() for x in txt.splitlines() if x.strip()]
    headers[f'{sid}:{page}'] = [re.findall(r'\b\d{1,4}\b',x) for x in lines[:1]+lines[-1:]]
print(json.dumps({'scripts_valid':checks,'page_text_count':sum(r['pages'] for r in data),'blank_pages':empty,'renders_removed':deleted,'protocol_hash':'pass','disk_free_bytes':shutil.disk_usage(raw).free,'extra_rod_identity':m.groups() if m else None}))
print(json.dumps({'range_relations':catalogue_relations,'margin_locator_digits':headers,'rod_identity_fields':rod_identity,'rod_entry_hint':entry_hint[-1:]}))
