"""Acquire public source witnesses. Raw downloads remain local-only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import requests

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-02-source-recovery/susa'
OUT = Path(__file__).resolve().parent

def acquire(source_id, url, suffix, rights='rights-unverified', notice=None):
    RAW.mkdir(parents=True, exist_ok=True)
    entry = dict(id=source_id, url=url,
                 retrieved_utc=datetime.now(timezone.utc).isoformat(),
                 access_route='ordinary public HTTPS request',
                 rights_status=rights, rights_notice=notice, local_only=True)
    try:
        response = requests.get(url, timeout=45)
        entry.update(status=response.status_code, final_url=response.url,
                     content_type=response.headers.get('Content-Type'))
        response.raise_for_status()
        expected_pdf = suffix.lower() == '.pdf'
        if expected_pdf and not response.content.startswith(b'%PDF'):
            entry.update(outcome='wrong-format response',
                         error='Requested PDF returned a non-PDF response; no requested document acquired')
            raise ValueError(entry['error'])
        path = RAW / (source_id + suffix)
        path.write_bytes(response.content)
        entry.update(local_path=path.relative_to(ROOT).as_posix(),
                     bytes=len(response.content),
                     sha256=hashlib.sha256(response.content).hexdigest(),
                     outcome='acquired')
    except Exception as error:
        entry.update(outcome='failed', error=str(error))
    log = OUT / 'source-acquisition.json'
    entries = json.loads(log.read_text(encoding='utf-8')) if log.exists() else []
    entries.append(entry)
    log.write_text(json.dumps(entries, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(entry, ensure_ascii=False))
    return entry

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('url')
    parser.add_argument('suffix')
    args = parser.parse_args()
    acquire(args.id, args.url, args.suffix)
