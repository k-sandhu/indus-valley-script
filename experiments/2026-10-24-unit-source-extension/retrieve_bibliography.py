import json,hashlib,urllib.request
from pathlib import Path
from datetime import datetime,timezone
P=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension')
urls={'helsinki-cisi31':'https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-volume-3-new-material-untr/','harappa-cisi31':'https://www.harappa.com/content/corpus-indus-seals-and-inscriptions-vol-31','indology-cisi32':'https://list.indology.info/pipermail/indology/2020-January/051630.html'}
records=[]
for key,url in urls.items():
 r={'id':key,'url':url,'utc':datetime.now(timezone.utc).isoformat(),'rights':'rights-unverified','content_displayed':'bibliographic search snippets; downloaded HTML not displayed'}
 try:
  with urllib.request.urlopen(url,timeout=12) as f:payload=f.read(1000000);r['http_status']=f.status;r['final_url']=f.url
  path=P/(key+'.html');path.write_bytes(payload);r.update(physical_path=str(path),logical_path='data/raw/2026-10-24-unit-source-extension/'+path.name,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
 except Exception as e:r['error']=repr(e)
 records.append(r)
(P/'bibliographic-access.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print(json.dumps(records,indent=2))
