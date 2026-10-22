"""Download one open plan scan, retaining a local source record."""
import sys
sys.dont_write_bytecode=True
import urllib.request, datetime, hashlib, json, shutil
from pathlib import Path
url, directory, notice=sys.argv[1:]
p=Path(directory).resolve()
allowed=(Path.cwd()/'data/raw/2026-10-21-town-orientations-verification/measure-A').resolve()
if not p.is_relative_to(allowed):raise ValueError('outside owned raw directory')
if shutil.disk_usage(p.anchor).free<1_500_000_000:raise RuntimeError('less than 1.5 GB free')
p.mkdir(parents=True,exist_ok=False)
request=urllib.request.Request(url,headers={'User-Agent':'Indus-research-plan-measurement/1.0'})
try:
    with urllib.request.urlopen(request,timeout=45) as response, (p/'source.pdf').open('xb') as out:
        content_type=response.headers.get('Content-Type');final_url=response.url
        while block:=response.read(65536):
            if shutil.disk_usage(p).free<1_000_000_000:raise RuntimeError('less than 1 GB free; acquisition stopped')
            out.write(block)
    data=(p/'source.pdf').read_bytes()
    record=dict(url=url,final_url=final_url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),rights_notice=notice,rights_status='rights-unverified',content_type=content_type,path=str(p/'source.pdf'))
except Exception as e:
    record=dict(url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e),rights_notice=notice)
with (p/'source-record.json').open('x',encoding='utf-8') as out:json.dump(record,out,indent=2)
print(json.dumps(record))
