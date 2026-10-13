"""Capture the declared source routes without replacing previous witnesses."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import requests

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / 'data/raw/2026-10-12-transmission-hypothesis/review'
ROUTES = [
    ('oldavestan-official', 'https://sites.fas.harvard.edu/~iranian/OldAvestan/'),
    ('oldavestan-primer', 'https://zoroastrian.org/wp-content/uploads/2025/01/oldavestanprimer.pdf'),
    ('witzel1997-author', 'https://michaelwitzel.org/wp-content/uploads/2014/06/canon.pdf'),
    ('pollock1985-jstor', 'https://www.jstor.org/stable/pdf/601525.pdf'),
    ('pollock-papers-index', 'https://www.columbia.edu/itc/mealac/pollock/sks/papers/'),
]


def capture(route):
    key, url = route
    meta_path = RAW / f'{key}.acquisition.json'
    if meta_path.exists():
        raise FileExistsError(meta_path)
    meta = {'route_id': key, 'requested_url': url,
            'retrieved_utc': datetime.now(timezone.utc).isoformat(),
            'tls_verification': True, 'rights_status': 'rights-unverified',
            'redistribution': 'local-only'}
    try:
        response = requests.get(url, timeout=25,
                                headers={'User-Agent': 'Mozilla/5.0 research-source-check'})
        body = response.content
        ext = '.pdf' if body.startswith(b'%PDF') else '.html'
        body_path = RAW / f'{key}{ext}'
        with body_path.open('xb') as stream:
            stream.write(body)
        meta.update({'resolved_url': response.url, 'status_code': response.status_code,
                     'content_type': response.headers.get('Content-Type'),
                     'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(),
                     'path': body_path.relative_to(REPO).as_posix(),
                     'format_signature': body[:12].hex(),
                     'successful_pdf': response.status_code == 200 and ext == '.pdf'})
    except requests.RequestException as exc:
        meta.update({'error': str(exc), 'successful_pdf': False})
    with meta_path.open('x', encoding='utf-8') as stream:
        json.dump(meta, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return meta


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    RAW.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        acquired = list(pool.map(capture, ROUTES))
    with (RAW / 'acquisition-v1.json').open('x', encoding='utf-8') as stream:
        json.dump(acquired, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps(acquired, indent=2, ensure_ascii=False))
