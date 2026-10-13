"""Normal verified-TLS acquisition for independently authored method controls."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-12-transmission-hypothesis/coordinator/method-v1'
TARGETS = [
 ('diachenko2023.html','https://link.springer.com/article/10.1007/s10816-023-09623-8'),
 ('shennan2020.pdf','https://discovery.ucl.ac.uk/id/eprint/10107913/2/Shennan_Springer_paper_final_v2_with_added_citations_and_refs.pdf'),
 ('shennan2020-metadata.html','https://discovery.ucl.ac.uk/id/eprint/10107913/')]


def acquire(target):
    filename,url=target
    record={'requested_url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
            'tls_verification':True,'redistribution':'local-only'}
    try:
        response=requests.get(url,timeout=60)
        path=RAW/filename
        with path.open('xb') as stream:stream.write(response.content)
        record.update({'status_code':response.status_code,'final_url':response.url,
                       'content_type':response.headers.get('content-type'),
                       'path':path.relative_to(ROOT).as_posix(),'bytes':len(response.content),
                       'sha256':hashlib.sha256(response.content).hexdigest(),
                       'pdf_signature':response.content.startswith(b'%PDF')})
    except requests.RequestException as exc:record['error']=str(exc)
    return record


def main():
    out=RAW/'acquisition-v1.json'
    if out.exists() or any((RAW/name).exists() for name,url in TARGETS):
        raise SystemExit('Acquisition endpoint exists; no overwrite.')
    RAW.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(acquire,TARGETS))
    with out.open('x',encoding='utf-8') as stream:
        json.dump({'scope':'Two method works, with separate metadata and primary web render captures.',
                   'records':records},stream,indent=2);stream.write('\n')
    print(json.dumps(records,ensure_ascii=True))


if __name__=='__main__':main()
