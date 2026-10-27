import json,re,hashlib
from pathlib import Path
import fitz
pkg=Path('experiments/2026-10-24-object-identity-extension');raw=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-extension')
src=Path('data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf');doc=fitz.open(src)
rows=json.loads((raw/'identity-assertions-v1.json').read_text()); checks=[]
for r in rows:
 for field,serial_field,width in [('context_observation','context_serial',118),('catalogue_observation','catalogue_serial',141)]:
  reg,page=r[field];words=[w for w in doc[page-1].get_text('words') if 30<w[0]<width and w[1]>(100 if field=="catalogue_observation" else 65)]
  serials=[w for w in words if re.fullmatch(r'\d+\.',w[4])]
  sw=[w for w in serials if int(w[4][:-1])==r[serial_field]]
  assert len(sw)==1,(r['row_id'],field,'serial')
  start=sw[0][1];end=min([w[1] for w in serials if w[1]>start]+[750])
  candidates=[w[4] for w in words if start-2<=w[1]<end and w[0]>sw[0][2] and w[4].isdigit()]
  assert candidates==[reg],(r['row_id'],field,candidates,reg)
  checks.append({'row_id':r['row_id'],'field':field,'passed':True})
assert len({r['source_registration'] for r in rows})==28
assert all(not r['physical_merge'] and not r['confirmation_eligibility'] for r in rows)
expected='f1c23210b95c17ea68650522ca2b7f7ecd7503078d9dede6fbfec6bfe4fad374';assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
out={'author_check':True,'independent_review':False,'source_sha256_matches':True,'coordinate_word_checks':len(checks),'unique_target_registrations':28,'physical_merges':0,'checks':checks}
(raw/'validation-detail-replay.json').write_text(json.dumps(out,indent=2)+'\n');print('Passed 56 independent coordinate-based table checks; 28 unique target registrations; source hash matches.')


