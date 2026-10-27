import urllib.request,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
p=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension'); r={'url':'https://ignca.gov.in/Asi_data/76884.pdf','utc':datetime.now(timezone.utc).isoformat(),'limit_seconds':55,'rights':'rights-unverified'}; t=time.monotonic()
try:
 with urllib.request.urlopen(r['url'],timeout=15) as response, (p/'cisi3-retrieval.pdf').open('xb') as f:
  r['status']=response.status; r['headers']=dict(response.headers)
  while time.monotonic()-t<55:
   b=response.read(262144)
   if not b:r['complete']=True;break
   f.write(b)
except Exception as e:r['error']=repr(e)
q=p/'cisi3-retrieval.pdf'
if q.exists():r.update(bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
(p/'retrieval.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
