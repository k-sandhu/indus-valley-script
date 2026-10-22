"""Download one openly accessible plan scan; never execute acquired content."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import urllib.request,datetime,hashlib,json,shutil
url=sys.argv[1]; dest=Path(sys.argv[2]);dest.mkdir(parents=True,exist_ok=False)
record=dict(url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rights_status='rights-unverified',rights_notice='No reuse licence observed at the PDF endpoint. Kept local only.',free_bytes_before=shutil.disk_usage(dest).free)
try:
 if record['free_bytes_before']<1_000_000_000:raise RuntimeError('Less than 1 GB free')
 req=urllib.request.Request(url,headers={'User-Agent':'Indus-research plan measurement'})
 with urllib.request.urlopen(req,timeout=45) as response, (dest/'source.pdf').open('xb') as f:
  record['resolved_url']=response.url;record['content_type']=response.headers.get('Content-Type');n=0;digest=hashlib.sha256()
  while True:
   chunk=response.read(1024*1024)
   if not chunk:break
   if shutil.disk_usage(dest).free-len(chunk)<1_000_000_000:raise RuntimeError('Download stopped to retain 1 GB')
   n+=len(chunk)
   if n>150_000_000:raise RuntimeError('Scan exceeds 150 MB size limit')
   f.write(chunk);digest.update(chunk)
  record.update(bytes=n,sha256=digest.hexdigest(),status='downloaded')
except Exception as e:
 record.update(status='failed',error=str(e))
with (dest/'record.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
print(json.dumps(record))
