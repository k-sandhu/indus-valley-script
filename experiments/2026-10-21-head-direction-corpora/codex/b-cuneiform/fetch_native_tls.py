"""Acquire one source with native validated TLS, recording hashes with the standard library.

Usage: python -I fetch_native_tls.py --url URL --dest NEW --name NAME --record JSON
    --source-id ID --title TITLE --rights-status STATUS --rights-note NOTE

This fallback uses curl's Windows Schannel certificate handling. It retains TLS
validation and the same fresh-directory and acquisition-record requirements.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    ap = argparse.ArgumentParser()
    for arg in ('url', 'dest', 'name', 'record', 'source-id', 'title', 'rights-status', 'rights-note'):
        ap.add_argument('--' + arg, required=True)
    ap.add_argument('--curl-exe', default='curl.exe')
    a = ap.parse_args()
    dest, record = Path(a.dest), Path(a.record)
    if record.exists() or (dest.exists() and any(dest.iterdir())):
        raise ValueError('refusing populated destination or existing record')
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / a.name
    now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec = dict(source_id=a.source_id, title=a.title, url=a.url, retrieved_utc_start=now(),
               local_path=target.as_posix(), rights_status=a.rights_status, rights_note=a.rights_note,
               transport='stdlib-subprocess-native-curl-Schannel-validated-TLS')
    rec['executable'] = a.curl_exe
    result = subprocess.run([a.curl_exe, '--fail', '--silent', '--show-error', '--location',
        '--proto', '=https', '--max-time', '600', '--output', str(target), '--write-out',
        '%{http_code}\n%{url_effective}\n%{content_type}', a.url], capture_output=True, text=True)
    rec.update(retrieved_utc_end=now(), exit_code=result.returncode, error=result.stderr or None)
    details = result.stdout.splitlines()
    rec.update(http_status=details[0] if details else None, final_url=details[1] if len(details)>1 else None)
    rec['bytes'] = target.stat().st_size if target.exists() else 0
    if target.exists():
        with target.open('rb') as f:
            rec['sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
    rec['status'] = 'acquired' if result.returncode == 0 else 'failed'
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(rec, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(rec))
    if result.returncode:
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
