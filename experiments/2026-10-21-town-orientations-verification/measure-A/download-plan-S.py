"""Acquire one open plan into a new directory, preserving acquisition metadata."""
import sys, json, hashlib, shutil, datetime, urllib.request
from pathlib import Path
url,directory,filename,rights=sys.argv[1:]
if shutil.disk_usage('C:/').free < 1073741824:raise RuntimeError('Below 1 GiB free')
d=Path(directory);d.mkdir(parents=True,exist_ok=False)
req=urllib.request.Request(url,headers={'User-Agent':'Indus research plan measurement / open scan acquisition'})
with urllib.request.urlopen(req,timeout=90) as response:
    data=response.read(100_000_001)
    if len(data)>100_000_000:raise RuntimeError('File exceeds download limit')
    final=response.url
(d/filename).write_bytes(data)
record=dict(url=url,final_url=final,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),rights_notice=rights,path=str(d/filename),untrusted_download=True)
with (d/'acquisition.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
print(json.dumps(record))
