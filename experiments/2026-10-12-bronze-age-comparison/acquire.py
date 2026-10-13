"""Capture named public source URLs, preserving successful and failed attempts."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import requests

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = ROOT / 'data/raw/2026-10-12-bronze-age-comparison/acquisition'

def acquire(item):
    name, url = item['id'], item['url']
    assert re.fullmatch(r'[a-z0-9_-]+', name)
    folder = LOCAL / name
    folder.mkdir(parents=True, exist_ok=False)
    metadata = {'id': name, 'url': url, 'started_utc': datetime.now(timezone.utc).isoformat(),
                'rights_status': 'rights-unverified', 'handling': 'local-only'}
    try:
        with requests.get(url, timeout=(8, 35), stream=True,
                          headers={'User-Agent': 'IndusResearch/1.0 (source-linked scholarly comparison)'}) as response:
            data = bytearray()
            for chunk in response.iter_content(1024 * 1024):
                data.extend(chunk)
                if len(data) > 160 * 1024 * 1024:
                    raise ValueError('Response exceeds the declared 160 MiB acquisition bound')
            payload = bytes(data)
            suffix = '.zip' if payload[:2] == b'PK' else '.pdf' if payload[:4] == b'%PDF' else '.json' if 'json' in response.headers.get('Content-Type', '') else '.html' if b'<html' in payload[:1000].lower() or b'<!doctype html' in payload[:1000].lower() else '.bin'
            witness = folder / ('response' + suffix)
            witness.write_bytes(payload)
            metadata.update({'status_code': response.status_code, 'final_url': response.url,
                             'content_type': response.headers.get('Content-Type'), 'bytes': len(payload),
                             'sha256': hashlib.sha256(payload).hexdigest(),
                             'local_path': str(witness.relative_to(ROOT)).replace('\\', '/'),
                             'status': 'acquired' if response.ok else 'http-error'})
    except Exception as error:
        metadata.update({'status': 'failed', 'error': str(error)})
    metadata['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (folder / 'request.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    public = PACKAGE / 'acquisition'
    public.mkdir(exist_ok=True)
    (public / (name + '.json')).write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    return metadata

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('plan', type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(acquire, plan):
            print(json.dumps({key: result.get(key) for key in ['id', 'status', 'status_code', 'bytes', 'error']}, ensure_ascii=False), flush=True)
