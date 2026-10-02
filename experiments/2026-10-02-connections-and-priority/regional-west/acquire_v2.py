"""Acquire a bounded set of public source witnesses; preserve all outcomes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import fitz
import requests

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
RAW = ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west'
SOURCES = [
    ('louvre-sb13677', 'https://collections.louvre.fr/ark:/53355/cl010186254.json', 'json'),
    ('capitoline-gonur', 'https://www.museicapitolini.org/sites/default/files/f_file/Vetrina%201%20sottosezione%20B.pdf', 'pdf'),
    ('englund2006', 'https://www.cdli.earth/files-up/publications/englund2006a.pdf', 'pdf'),
    ('bonora2014-page', 'https://www.persee.fr/doc/paleo_0153-9345_2014_num_40_1_5616', 'html'),
]


def acquire(spec):
    name, url, kind = spec
    row = dict(id=name, url=url, retrieved_utc=datetime.now(timezone.utc).isoformat(),
               access_route='ordinary public HTTPS request', rights_status='rights-unverified', local_only=True)
    try:
        response = requests.get(url, timeout=45)
        row.update(status=response.status_code, final_url=response.url,
                   content_type=response.headers.get('Content-Type'))
        valid = response.status_code == 200
        if kind == 'pdf':
            valid = valid and response.content.startswith(b'%PDF')
        if kind == 'json' and valid:
            response.json()
        if not valid:
            row['outcome'] = 'not an acquired witness of the requested format'
            return row
        target = RAW / f'{name}.{kind}'
        if target.exists():
            raise FileExistsError(str(target))
        target.write_bytes(response.content)
        row.update(local_path=target.relative_to(ROOT).as_posix(), bytes=len(response.content),
                   sha256=sha256(response.content).hexdigest())
        if kind == 'pdf':
            doc = fitz.open(target)
            body = '\n'.join(f'=== PDF PAGE {i + 1} ===\n{page.get_text()}' for i, page in enumerate(doc))
            derivative = target.with_suffix('.txt')
            derivative.write_text(body, encoding='utf-8')
            row.update(page_count=len(doc), text_derivative=dict(
                path=derivative.relative_to(ROOT).as_posix(), sha256=sha256(derivative.read_bytes()).hexdigest(),
                method='PyMuPDF page text, original page separators preserved'))
        row['outcome'] = 'acquired'
    except Exception as error:
        row.update(outcome='failed', error=f'{type(error).__name__}: {error}')
    return row


if __name__ == '__main__':
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = RUN / 'source-acquisition-v2.json'
    if manifest.exists():
        raise FileExistsError(str(manifest))
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(acquire, SOURCES))
    manifest.write_text(json.dumps(dict(sources=rows), indent=2) + '\n', encoding='utf-8')
    print(json.dumps([dict(id=r['id'], outcome=r['outcome'], bytes=r.get('bytes')) for r in rows]))
