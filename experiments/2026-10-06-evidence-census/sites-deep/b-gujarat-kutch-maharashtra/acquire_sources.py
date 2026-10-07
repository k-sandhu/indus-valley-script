"""Acquire public witnesses or copy existing local witnesses, preserving provenance."""
from pathlib import Path
import argparse, concurrent.futures, datetime, hashlib, json, os, shutil
import requests
import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[4]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra'
RAW.mkdir(parents=True, exist_ok=True)
TMP = RAW / 'tmp'
TMP.mkdir(exist_ok=True)
for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[key] = str(TMP)

def acquire(item):
    previous = RAW / (item['id']+'.acquisition.json')
    if previous.exists():
        old = json.loads(previous.read_text(encoding='utf-8'))
        return {k:old.get(k) for k in ('id','status','http_status','bytes','pages','text_characters','error')}
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    target = RAW / item['filename']
    record = dict(item, retrieved_at=stamp, rights='rights-unverified', status='failed')
    try:
        if 'reuse' in item:
            source = ROOT / item['reuse']
            shutil.copy2(source, target)
            record['route'] = 'reused local witness; byte copy'
        else:
            response = requests.get(item['url'], timeout=(15, 50), headers={'User-Agent':'Indus research source census/1.0'})
            record.update(http_status=response.status_code, final_url=response.url, content_type=response.headers.get('Content-Type'))
            response.raise_for_status()
            target.write_bytes(response.content)
        payload = target.read_bytes()
        record.update(status='acquired', bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), local_path=str(target.relative_to(ROOT)))
        if payload[:5] == b'%PDF-':
            doc = fitz.open(target)
            pages = [{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]
            (RAW / (item['id']+'.pages.json')).write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            record['pages'] = len(doc)
            record['text_characters'] = sum(len(p['text']) for p in pages)
        elif target.suffix.lower() in ('.html','.htm'):
            soup = BeautifulSoup(payload,'html.parser')
            for tag in soup(['script','style','nav']): tag.decompose()
            txt=soup.get_text('\n',strip=True)
            (RAW/(item['id']+'.txt')).write_text(txt,encoding='utf-8')
            record['text_characters']=len(txt)
    except Exception as exc:
        record['error']=type(exc).__name__+': '+str(exc)
    (RAW / (item['id']+'.acquisition.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:record.get(k) for k in ('id','status','http_status','bytes','pages','text_characters','error')}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('plan', type=Path)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(acquire,plan): print(json.dumps(result,ensure_ascii=False),flush=True)
