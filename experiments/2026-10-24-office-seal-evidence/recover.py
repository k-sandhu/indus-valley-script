from pathlib import Path
import fitz,json,hashlib,datetime
out=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-evidence')
sources={'rao1979':Path('data/raw/2026-10-21-town-axes/dating/lothal/rao1979lothal-part1.pdf'),'rao1985':Path('data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf'),'frenez2005':Path('data/six-hour/lothal/frenez-tosi2005.pdf')}
manifest=[]
for key,path in sources.items():
 d=fitz.open(path); pages=[]
 for i,p in enumerate(d):
  t=p.get_text()
  if i<5 or any(w in t.lower() for w in ['sealing','elephant','warehouse']):pages.append({'pdf_page':i+1,'text':t})
 (out/(key+'-candidates.json')).write_text(json.dumps(pages,indent=2),encoding='utf8')
 manifest.append({'id':key,'logical_path':str(path),'physical_path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'pdf_pages':len(d),'candidate_pages':[p['pdf_page'] for p in pages],'rights':'unresolved; local-only','accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 print(key,len(d),[(p['pdf_page'],len(p['text'])) for p in pages])
(out/'source-inventory.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
