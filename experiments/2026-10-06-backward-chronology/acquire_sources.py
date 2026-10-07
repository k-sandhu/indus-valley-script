"""Preserve public source witnesses locally; never write outside Package E roots."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-backward-chronology'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--id', required=True)
    p.add_argument('--url')
    p.add_argument('--local', help='Reuse an existing repository-relative source')
    p.add_argument('--keywords', default='graffiti|inscri|radiocarbon|Beta|Porunthal|Kodumanal|Keeladi|Lal|Cemetery|Jhukar|Pirak|Daimabad|Navdatoli|Prakash')
    p.add_argument('--render', help='Comma-separated one-based PDF pages')
    p.add_argument('--ocr', help='Comma-separated one-based PDF pages; tesseract required')
    a = p.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+', a.id):
        p.error('id must be a safe lowercase filename')
    RAW.mkdir(parents=True, exist_ok=True)
    temp = RAW / 'tmp'
    temp.mkdir(exist_ok=True)
    for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
        os.environ[key] = str(temp)
    manifest = RAW / f'{a.id}.acquisition.json'
    if manifest.exists() and a.url:
        p.error('Witness already exists. Use a new id for a new acquisition.')
    if manifest.exists() and a.local:
        manifest = RAW / f'{a.id}.processing.json'
        if manifest.exists():
            p.error('Processing record already exists. Use a new id for another pass.')
    record = {'id': a.id, 'accessed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'rights_status': 'rights-unverified', 'handling': 'local-only', 'url': a.url}
    if a.local:
        path = (ROOT / a.local).resolve()
        path.relative_to(ROOT)
        record['reuse'] = a.local
    elif a.url:
        try:
            r = requests.get(a.url, timeout=90, headers={'User-Agent': 'IndusResearchSourceAssembly/1.0'})
            record.update(http_status=r.status_code, final_url=r.url, content_type=r.headers.get('Content-Type'))
            suffix = '.pdf' if r.content.startswith(b'%PDF') else '.html'
            path = RAW / f'{a.id}{suffix}'
            path.write_bytes(r.content)
            record['download_success'] = r.ok
        except requests.RequestException as exc:
            record['error'] = str(exc)
            manifest.write_text(json.dumps(record, indent=2), encoding='utf-8')
            print(json.dumps(record)); return
    else:
        p.error('Supply --url or --local')
    payload = path.read_bytes()
    record.update(local_path=path.relative_to(ROOT).as_posix(), bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    if payload.startswith(b'%PDF'):
        import fitz
        doc = fitz.open(path)
        record['pages'] = len(doc)
        pages = [pg.get_text() for pg in doc]
        (RAW / f'{a.id}.pages.json').write_text(json.dumps(pages, ensure_ascii=False), encoding='utf-8')
        hits = []
        pat = re.compile(a.keywords, re.I)
        for n, t in enumerate(pages, 1):
            if pat.search(t):
                hits.append({'pdf_page': n, 'text': t})
        (RAW / f'{a.id}.hits.json').write_text(json.dumps(hits, ensure_ascii=False), encoding='utf-8')
        record['keyword_hit_pages'] = [h['pdf_page'] for h in hits]
        if a.render:
            for n in map(int, a.render.split(',')):
                doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(RAW / f'{a.id}-p{n}.png')
        if a.ocr:
            import subprocess
            from concurrent.futures import ThreadPoolExecutor
            selected = list(map(int, a.ocr.split(',')))
            for n in selected:
                doc[n-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(RAW / f'{a.id}-ocr-p{n}.png')
            def read_page(n):
                image = RAW / f'{a.id}-ocr-p{n}.png'
                result = subprocess.run(['tesseract', str(image), 'stdout', '-l', 'eng'],
                                        capture_output=True, check=True, encoding='utf-8')
                return {'pdf_page': n, 'text': result.stdout}
            with ThreadPoolExecutor(max_workers=4) as executor:
                ocr = list(executor.map(read_page, selected))
            (RAW / f'{a.id}.ocr.json').write_text(json.dumps(ocr, ensure_ascii=False), encoding='utf-8')
            record['ocr_pages'] = selected
    else:
        from bs4 import BeautifulSoup
        text = BeautifulSoup(payload, 'html.parser').get_text(' ', strip=True)
        (RAW / f'{a.id}.text.txt').write_text(text, encoding='utf-8')
    manifest.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k != 'keyword_hit_pages'}))
    if 'keyword_hit_pages' in record:
        print('Hit pages:', record['keyword_hit_pages'])

if __name__ == '__main__':
    main()
