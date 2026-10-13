"""Acquire a named source witness with native TLS validation and no replacement."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = ROOT / 'data/raw/2026-10-12-semantic-sign-comparison'

def acquire(spec):
    directory = LOCAL / 'acquisition' / spec['id']
    directory.mkdir(parents=True, exist_ok=False)
    response = directory / 'response.bin'
    now = lambda: datetime.now(timezone.utc).isoformat()
    record = {**spec, 'started_utc': now(), 'handling': 'local-only',
              'rights_status': spec.get('rights_status', 'rights-unverified'),
              'transport': 'curl-native-TLS-validation'}
    command = ['curl.exe', '-L', '--connect-timeout', '10', '--max-time', '60',
               '--silent', '--show-error', '--output', str(response),
               '--write-out', '%{http_code}\n%{url_effective}\n%{content_type}', spec['url']]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    fields = result.stdout.splitlines()
    record.update(exit_code=result.returncode, status_code=int(fields[0]) if fields else 0,
                  final_url=fields[1] if len(fields) > 1 else None,
                  content_type=fields[2] if len(fields) > 2 else None,
                  finished_utc=now(), error=result.stderr.strip() or None)
    if response.exists():
        record.update(bytes=response.stat().st_size,
                      sha256=hashlib.sha256(response.read_bytes()).hexdigest(),
                      local_path=response.relative_to(ROOT).as_posix())
    record['status'] = 'acquired' if result.returncode == 0 and record['status_code'] == 200 else 'failed'
    out = PACKAGE / 'acquisition'
    out.mkdir(exist_ok=True)
    (out / (spec['id'] + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {k:record[k] for k in ['id', 'status', 'status_code']}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('plan')
    args = parser.parse_args()
    specs = json.loads(Path(args.plan).read_text(encoding='utf-8'))
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(acquire, specs):
            print(json.dumps(result))

if __name__ == '__main__':
    main()
