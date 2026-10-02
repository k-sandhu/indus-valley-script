"""Acquire public Kanmer witnesses and retain transport/identity evidence locally."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--targets', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+', args.endpoint):
        raise ValueError('Use a simple endpoint name.')
    endpoint = BASE / args.endpoint
    raw = BASE / 'local-witness' / args.endpoint
    if endpoint.exists() or raw.exists():
        raise RuntimeError('Preserve prior acquisition endpoints.')
    endpoint.mkdir(parents=True)
    raw.mkdir(parents=True)
    records = []
    targets = json.loads(args.targets.read_text(encoding='utf-8'))
    for target in targets:
        record = {'id': target['id'], 'requested_url': target['url'],
                  'route': 'ordinary public HTTPS requests.get',
                  'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                  'discovery': target.get('discovery')}
        try:
            response = requests.get(target['url'], timeout=45)
            content = response.content
            record.update({'http_status': response.status_code, 'final_url': response.url,
                           'content_type': response.headers.get('Content-Type'),
                           'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
            suffix = ('.pdf' if content[:4] == b'%PDF' else '.png' if content[:8] == b'\x89PNG\r\n\x1a\n'
                      else '.jpg' if content[:3] == b'\xff\xd8\xff'
                      else '.html' if b'<html' in content[:2000].lower() else '.bin')
            path = raw / (target['id'] + suffix)
            path.write_bytes(content)
            record['local_path'] = path.relative_to(ROOT).as_posix()
            if suffix == '.html':
                soup = BeautifulSoup(content, 'html.parser')
                record['html_title'] = soup.title.get_text(' ', strip=True) if soup.title else None
                links = [{'text': a.get_text(' ', strip=True), 'url': urljoin(response.url, a['href'])}
                         for a in soup.find_all('a', href=True)]
                images = [{'alt': a.get('alt'), 'url': urljoin(response.url, a['src'])}
                          for a in soup.find_all('img', src=True)]
                (raw / (target['id'] + '-links.json')).write_text(json.dumps({'links': links, 'images': images}, indent=2) + '\n', encoding='utf-8')
                (raw / (target['id'] + '-text.txt')).write_text(soup.get_text('\n', strip=True), encoding='utf-8')
            record['rights'] = 'unverified; witness local-only'
        except requests.RequestException as error:
            record.update({'error': type(error).__name__ + ': ' + str(error), 'status': 'not-acquired'})
        records.append(record)
        print(json.dumps({key: record.get(key) for key in ('id', 'http_status', 'bytes', 'html_title', 'error')}, ensure_ascii=True), flush=True)
        (endpoint / 'access.json').write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (endpoint / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    summary = {'protocol_sha256': hashlib.sha256((BASE / 'PROTOCOL.md').read_bytes()).hexdigest(),
               'targets_sha256': hashlib.sha256(args.targets.read_bytes()).hexdigest(),
               'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'targets': len(records), 'transport_200': sum(record.get('http_status') == 200 for record in records)}
    (endpoint / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
