"""Preserve ordinary public source requests and their access outcomes locally."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / 'data/raw/2026-10-02-source-recovery/physical-views'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--title', required=True)
    args = parser.parse_args()
    if Path(args.name).name != args.name:
        raise ValueError('Use one basename within the owned raw directory')
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / args.name
    if path.exists():
        raise FileExistsError(path)
    entry = {'requested_url': args.url, 'title': args.title,
             'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'method': 'ordinary public requests.get with default headers',
             'rights_status': 'rights-unverified; downloaded witness local-only'}
    try:
        response = requests.get(args.url, timeout=40)
        entry.update(final_url=response.url, http_status=response.status_code,
                     content_type=response.headers.get('Content-Type'))
        response.raise_for_status()
        data = response.content
        path.write_bytes(data)
        entry.update(path=path.relative_to(ROOT).as_posix(), bytes=len(data),
                     sha256=hashlib.sha256(data).hexdigest(), status='acquired')
    except Exception as exc:
        entry.update(status='failed', error_type=type(exc).__name__, error=str(exc))
    log = HERE / 'access-log.json'
    entries = json.loads(log.read_text(encoding='utf8')) if log.exists() else []
    entries.append(entry)
    log.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(entry, ensure_ascii=False))


if __name__ == '__main__':
    main()
