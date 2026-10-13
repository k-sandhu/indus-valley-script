"""Capture named source URLs with native certificate validation on Windows."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = ROOT / 'data/raw/2026-10-12-bronze-age-comparison/acquisition'

def acquire(item):
    folder = LOCAL / item['id']
    folder.mkdir(parents=True, exist_ok=False)
    target = folder / 'response.bin'
    metadata = dict(item, started_utc=datetime.now(timezone.utc).isoformat(),
                    transport='curl-native-TLS-validation', rights_status='rights-unverified', handling='local-only')
    run = subprocess.run(['curl.exe', '--silent', '--show-error', '--location', '--connect-timeout', '8',
                          '--max-time', '60', '--output', str(target), '--write-out',
                          '%{http_code}\n%{url_effective}\n%{content_type}', item['url']],
                         capture_output=True, text=True, timeout=65)
    fields = run.stdout.splitlines()
    metadata.update({'exit_code':run.returncode, 'status_code':int(fields[0]) if fields and fields[0].isdigit() else None,
                     'final_url':fields[1] if len(fields)>1 else None, 'content_type':fields[2] if len(fields)>2 else None,
                     'status':'acquired' if run.returncode==0 and fields and fields[0]=='200' else 'failed',
                     'error':run.stderr.strip() or None, 'finished_utc':datetime.now(timezone.utc).isoformat()})
    if target.exists():
        payload=target.read_bytes()
        metadata.update({'bytes':len(payload), 'sha256':hashlib.sha256(payload).hexdigest(),
                         'local_path':str(target.relative_to(ROOT)).replace('\\','/')})
    (folder/'request.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    (PACKAGE/'acquisition').mkdir(exist_ok=True)
    (PACKAGE/'acquisition'/f"{item['id']}.json").write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    return metadata

if __name__=='__main__':
    plan=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(acquire,plan):
            print(json.dumps({k:r.get(k) for k in ['id','status','status_code','bytes','error']}),flush=True)
