"""Save openly served article page HTML and displayed images without PDF form submission."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez'
OUT = RAW / 'quivron1980-pages'
URL = 'https://www.persee.fr/doc/paleo_0153-9345_1980_num_6_1_4281'

def recover(page):
    url = URL + '?pageId=T1_' + str(page)
    record = {'page': page, 'url': url, 'accessed_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        r = requests.get(url, timeout=60)
        (OUT / f'p{page}.html').write_bytes(r.content)
        record.update(http_status=r.status_code, sha256=hashlib.sha256(r.content).hexdigest())
        s = BeautifulSoup(r.content, 'html.parser')
        body = s.find('div', class_='text', itemprop='articleBody')
        record['text'] = body.get_text(' ', strip=True) if body else ''
        img = s.find('img', alt=f'Page {page}')
        if img:
            record['image_url'] = img['src']
            ir = requests.get(img['src'], timeout=60)
            record['image_status'] = ir.status_code
            if ir.ok and ir.headers.get('content-type', '').startswith('image/'):
                (OUT / f'p{page}.jpg').write_bytes(ir.content)
                record['image_sha256'] = hashlib.sha256(ir.content).hexdigest()
    except requests.RequestException as e:
        record['error'] = str(e)
    return record

def main():
    if OUT.exists():
        raise SystemExit('Witness directory already exists; do not overwrite.')
    OUT.mkdir()
    for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
        os.environ[key] = str(RAW / 'tmp')
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(recover, range(269, 281)))
    (OUT / 'pages.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'pages_requested': len(rows), 'html_ok': sum(r.get('http_status') == 200 for r in rows),
                      'images_ok': sum('image_sha256' in r for r in rows),
                      'failures': [r['page'] for r in rows if r.get('http_status') != 200]}))

if __name__ == '__main__':
    main()
