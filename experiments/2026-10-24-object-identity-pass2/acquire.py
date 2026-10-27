from pathlib import Path
import json,urllib.request,urllib.error,hashlib,datetime
raw=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-pass2');records=[]
assert not (raw/'acquisition-v1.json').exists(), 'Frozen acquisition record exists'
for label,url in [('icit','https://indus.epigraphica.de/'),('epigraphica-menu','https://www.epigraphica.de/indus/menueindus.htm'),('asi-final','https://asi.nic.in/pdf_data/dholavira_excavation_report_new.pdf'),('asi-cover','https://asi.nic.in/pdf/dholavira_excavation_report_cover.pdf')]:
 rec={'label':label,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rights':'unverified; local-only'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as response:
   data=response.read(160000001); assert len(data)<=160000000
   path=raw/(label+('.pdf' if data.startswith(b'%PDF') else '.html'));path.write_bytes(data)
   rec.update(status=response.status,resolved_url=response.url,physical_path=str(path),logical_path='data/raw/2026-10-24-object-identity-pass2/'+path.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=response.headers.get('Content-Type'))
 except Exception as e:rec.update(error_type=type(e).__name__,error=str(e))
 records.append(rec)
(raw/'acquisition-v1.json').write_text(json.dumps(records,indent=2)+'\n')
print(*[{k:v for k,v in r.items() if k in ['label','status','error','bytes','content_type']} for r in records],sep='\n')
