"""Acquire public witnesses into Package Q's local-only raw directory."""
from pathlib import Path
import argparse, hashlib, json, urllib.request, urllib.error
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'

def fetch(url, dest):
    row = {'url': url, 'access_utc': datetime.now(timezone.utc).isoformat(),
           'path': str(dest.relative_to(ROOT))}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'IndusResearchSourceAudit/1.0'})
        with urllib.request.urlopen(req, timeout=40) as response:
            payload = response.read()
            row.update(status=response.status, final_url=response.url,
                       content_type=response.headers.get('Content-Type'))
        dest.write_bytes(payload)
        row.update(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    except Exception as exc:
        row.update(status='failed', error=str(exc))
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='acquisition-2026-10-08-v1')
    args = parser.parse_args()
    directory = RAW / args.name
    directory.mkdir(parents=True, exist_ok=False)
    records = []
    api = 'https://api.github.com/repos/sanskrit-lexicon/csl-orig/commits/main'
    commit_row = fetch(api, directory / 'csl-commit.json')
    records.append(commit_row)
    if commit_row['status'] == 200:
        pin = json.loads((directory / 'csl-commit.json').read_text(encoding='utf-8'))['sha']
        for path, name in [('LICENSE', 'csl-LICENSE'), ('v02/mw/mw.txt', 'mw.txt'),
                           ('README.md', 'csl-README.md')]:
            records.append(fetch(f'https://raw.githubusercontent.com/sanskrit-lexicon/csl-orig/{pin}/{path}', directory/name))
    urls = [
        ('bonta-2023-id-requested.html', 'https://www.academia.edu/105134798'),
        ('bonta-2023-id-firstpass.html', 'https://www.academia.edu/105163460'),
        ('bonta-entering-wedge.html', 'https://www.academia.edu/12412747'),
        ('bonta-expectations.html', 'https://www.academia.edu/12412722'),
        ('bonta-2014-a.html', 'https://www.academia.edu/8691385'),
        ('bonta-2014-b.html', 'https://www.academia.edu/8691466'),
        ('kalyanaraman.html', 'https://www.academia.edu/113408961'),
        ('imsc-2015.pdf', 'https://www.imsc.res.in/annrep/Archive/2015.pdf'),
        ('language-log.html', 'https://languagelog.ldc.upenn.edu/nll/?p=68508'),
        ('mukhopadhyay-2019.html', 'https://www.nature.com/articles/s41599-019-0274-1'),
        ('parpola-interview.html', 'https://www.harappa.com/content/interview-asko-parpola'),
        ('bonta-letter.pdf', 'https://www.jefflindsay.com/Bonta-introductory-letter.pdf'),
    ]
    for name, url in urls:
        row = fetch(url, directory/name)
        records.append(row)
        print(name, row['status'], flush=True)
    (directory/'manifest.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'directory':str(directory.relative_to(ROOT)), 'responses':len(records)}, indent=2))

if __name__ == '__main__': main()
