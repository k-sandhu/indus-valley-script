"""Capture public catalogue responses; all acquired payloads stay local."""
import argparse, concurrent.futures, datetime, hashlib, json, re, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07'
RAW.mkdir(parents=True, exist_ok=True)

def fetch(item):
    name, url = item
    target = RAW / (name + '.body')
    if target.exists():
        raise ValueError('Preserved response exists: ' + name)
    row = dict(name=name, url=url, requested_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), method='GET')
    request = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (public catalogue research)', 'Accept':'text/html,application/json,application/pdf;q=0.9,*/*;q=0.8'})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read()
            row.update(http_status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type'))
    except urllib.error.HTTPError as error:
        body = error.read()
        row.update(http_status=error.code, error=str(error))
    except Exception as error:
        body = b''
        row.update(http_status=None, error=repr(error))
    target.write_bytes(body)
    row.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), body=str(target.relative_to(ROOT)))
    (RAW / (name + '.request.json')).write_text(json.dumps(row, indent=2)+'\n', encoding='utf8')
    return row

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pairs', nargs='+', help='NAME=URL')
    args = parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(fetch, [s.split('=', 1) for s in args.pairs]):
            print(json.dumps(row))
