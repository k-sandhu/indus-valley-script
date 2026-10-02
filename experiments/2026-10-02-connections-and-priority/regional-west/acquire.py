"""Acquire named public witnesses locally and record their bytes. No raw assets are tracked."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib, json, requests, fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'experiments/2026-10-02-connections-and-priority/regional-west'
RAW = ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west'
SOURCES = [
    ('ascalone2022', 'https://airus.unisalento.it/retrieve/c39309c8-8dae-4dba-b990-86171612edf6/E.%20Ascalone%2C%20Bronze%20Age%20Weights%20from%20Mesopotamia%2C%20Iran%20and%20Greater%20Indus%20Valley_compressed.pdf'),
    ('kaniuth2010', 'https://www.vorderas-archaeologie.uni-muenchen.de/personen/wiss_mitarbeiter/kaniuth/publikationen/kaniuth-2010_amit-42.pdf'),
    ('margiana2016', 'https://static.iea.ras.ru/books/Margiana_vol_%206.pdf'),
    ('englund1998', 'https://is.muni.cz/el/1421/jaro2013/PAPVA_43/um/Englund_1998.pdf'),
]

def acquire(pair):
    key, url = pair
    rec = {'id': key, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'access_route': 'ordinary public HTTPS request', 'rights_status': 'rights-unverified', 'local_only': True}
    try:
        response = requests.get(url, timeout=75)
        rec.update(status=response.status_code, final_url=response.url, content_type=response.headers.get('Content-Type'))
        if response.status_code == 200 and response.content.startswith(b'%PDF'):
            path = RAW / (key + '.pdf')
            if path.exists():
                raise FileExistsError(path)
            path.write_bytes(response.content)
            rec.update(local_path=path.relative_to(ROOT).as_posix(), bytes=len(response.content), sha256=hashlib.sha256(response.content).hexdigest())
            doc = fitz.open(path)
            rec['page_count'] = len(doc)
            textpath = RAW / (key + '.txt')
            textpath.write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n' + p.get_text() for i,p in enumerate(doc)), encoding='utf-8')
            rec['text_derivative'] = {'path':textpath.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(textpath.read_bytes()).hexdigest(), 'method':'PyMuPDF page text, original page separators preserved'}
        else:
            rec['outcome'] = 'not an acquired PDF'
    except Exception as e:
        rec['error'] = f'{type(e).__name__}: {e}'
    return rec

if __name__ == '__main__':
    RAW.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(acquire, SOURCES))
    destination = OUT / 'source-acquisition-v1.json'
    if destination.exists():
        raise FileExistsError(destination)
    destination.write_text(json.dumps({'sources':records}, indent=2), encoding='utf-8')
    print(json.dumps(records, indent=2))
