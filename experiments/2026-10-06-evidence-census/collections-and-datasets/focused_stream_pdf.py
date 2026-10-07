"""Retry the official CISI volume as a streamed download, preserving partial data."""
import datetime, hashlib, json, urllib.request
from focused_fetch import RAW
target=RAW/'cisi3-stream.pdf'
if target.exists(): raise SystemExit('Preserved stream already exists')
log={'url':'https://ignca.gov.in/Asi_data/76884.pdf','requested_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'GET','complete':False}
try:
    req=urllib.request.Request(log['url'],headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=60) as response, target.open('wb') as output:
        log.update(http_status=response.status,headers=dict(response.headers))
        while True:
            chunk=response.read(262144)
            if not chunk: break
            output.write(chunk)
        log['complete']=True
except Exception as error: log['error']=repr(error)
log['bytes']=target.stat().st_size if target.exists() else 0
if target.exists(): log['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
(RAW/'cisi3-stream.request.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf8')
print(json.dumps(log))
