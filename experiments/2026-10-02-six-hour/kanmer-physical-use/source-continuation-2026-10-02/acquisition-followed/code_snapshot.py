"""Preserve bounded public source routes for the Kanmer continuation."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use/source-continuation-2026-10-02'


def acquire(target, raw):
    rec = dict(id=target['id'], requested_url=target['url'], discovery=target['discovery'],
               retrieved_utc=datetime.now(timezone.utc).isoformat(),
               route='ordinary public HTTPS requests.get', rights='unverified; witness local-only')
    try:
        response = requests.get(target['url'], timeout=40)
        content = response.content
        suffix = '.pdf' if content[:4] == b'%PDF' else '.html' if b'<html' in content[:4000].lower() else '.bin'
        path = raw / (target['id'] + suffix)
        path.write_bytes(content)
        rec.update(http_status=response.status_code, final_url=response.url,
                   content_type=response.headers.get('Content-Type'), bytes=len(content),
                   sha256=hashlib.sha256(content).hexdigest(), local_path=path.relative_to(ROOT).as_posix())
        if suffix == '.html':
            soup = BeautifulSoup(content, 'html.parser')
            rec['html_title'] = soup.title.get_text(' ', strip=True) if soup.title else None
            links = [dict(text=a.get_text(' ', strip=True), url=urljoin(response.url, a['href']))
                     for a in soup.find_all('a', href=True)]
            (raw / (target['id'] + '-links.json')).write_text(json.dumps(links, indent=2) + '\n', encoding='utf-8')
            (raw / (target['id'] + '-text.txt')).write_text(soup.get_text('\n', strip=True), encoding='utf-8')
    except requests.RequestException as error:
        rec.update(error=type(error).__name__ + ': ' + str(error), status='not-acquired')
    print(json.dumps({key: rec.get(key) for key in ['id', 'http_status', 'bytes', 'html_title', 'error']}, ensure_ascii=True), flush=True)
    return rec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--targets', required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch('[a-z0-9-]+', args.endpoint):
        raise ValueError('Use a simple endpoint name.')
    endpoint, raw = BASE / args.endpoint, BASE / 'local-witness' / args.endpoint
    if endpoint.exists() or raw.exists():
        raise RuntimeError('Preserve prior acquisition endpoints.')
    endpoint.mkdir(parents=True)
    raw.mkdir(parents=True)
    targets = json.loads(args.targets.read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda target: acquire(target, raw), targets))
    (endpoint / 'access.json').write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (endpoint / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (endpoint / 'summary.json').write_text(json.dumps(dict(
        protocol_sha256=hashlib.sha256((BASE / 'PROTOCOL.md').read_bytes()).hexdigest(),
        targets_sha256=hashlib.sha256(args.targets.read_bytes()).hexdigest(),
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        targets=len(records), transport_200=sum(r.get('http_status') == 200 for r in records)), indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
