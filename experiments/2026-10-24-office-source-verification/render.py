import json,hashlib,datetime
from pathlib import Path
import fitz
pkg=Path('experiments/2026-10-24-office-source-verification');raw=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-source-verification')
m=json.loads(Path('experiments/2026-10-24-office-seal-evidence/source-manifest-v1.json').read_text());targets={'cisi1':[409],'rao1985':[70],'frenez2005':[16,17],'rao1979':[124]};out=[]
for src in m['sources']:
 p=Path(src['physical_path']); b=p.read_bytes(); assert hashlib.sha256(b).hexdigest()==src['sha256'];d=fitz.open(p)
 for n in targets[src['id']]:
  image=raw/f"{src['id']}-pdf{n}.png";assert not image.exists();d[n-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(image)
  (raw/f"{src['id']}-pdf{n}.txt").write_text(d[n-1].get_text(),encoding='utf-8')
 out.append({**src,'consulted_pdf_pages':targets[src['id']],'review_source_hash_matched':True})
artifacts=[{'physical_path':str(p),'logical_path':'data/raw/2026-10-24-office-source-verification/'+p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in raw.iterdir()]
(pkg/'source-manifest-v1.json').write_text(json.dumps({'sources':out,'review_time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'artifacts':artifacts,'raw_rights':'unresolved; local-only','protocol_sha256':hashlib.sha256((pkg/'PROTOCOL.md').read_bytes()).hexdigest()},indent=2)+'\n')
print('Four source hashes match; five pages rendered into D: review directory.')
