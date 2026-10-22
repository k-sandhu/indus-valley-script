"""Acquire Parpola's published sign identifications as local-only witnesses.

Every request is logged with URL, status, bytes, SHA-256 and UTC time. PDF text is
extracted with PyMuPDF beside the PDF. Nothing acquired here is tracked in git.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / 'data/raw/2026-10-22-rebus-blind-templates'

SOURCES = [
    {'id': 'parpola1997', 'year': 1997,
     'title': 'Dravidian and the Indus script: On the interpretation of some pivotal signs',
     'container': 'Studia Orientalia 82: 167-192',
     'urls': ['https://journal.fi/store/article/download/45117/22657',
              'https://journal.fi/store/article/view/45117/22657']},
    {'id': 'parpola2005', 'year': 2005,
     'title': 'Study of the Indus script',
     'container': 'Transactions of the International Conference of Eastern Studies 50: 28-66 (Tokyo: Toho Gakkai)',
     'urls': ['https://www.harappa.com/sites/default/files/pdf/indusscript%282%29.pdf']},
    {'id': 'parpola2008', 'year': 2008,
     'title': 'Is the Indus script indeed not a writing system?',
     'container': 'Airavati: Felicitation volume in honour of Iravatham Mahadevan, 111-131 (Chennai: Varalaaru.com)',
     'urls': ['https://www.harappa.com/sites/default/files/pdf/indus-writing.pdf']},
    {'id': 'parpola2009', 'year': 2009,
     'title': "'Hind leg' + 'fish': towards further understanding of the Indus script",
     'container': 'Scripta 1: 37-76 (Seoul: Hunmin jeongeum Society)',
     'urls': ['https://www.harappa.com/sites/default/files/pdf/script-indus-parpola.pdf']},
]


def fetch(source, dest):
    item = dict(source, attempts=[])
    for number, url in enumerate(source['urls']):
        attempt = {'url': url, 'utc': datetime.now(timezone.utc).isoformat()}
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Indus research source check; scholarly use'})
            with urllib.request.urlopen(req, timeout=60) as response:
                body = response.read()
                attempt.update(http_status=response.status, content_type=response.headers.get('Content-Type'),
                               final_url=response.url)
        except Exception as exc:  # logged, not raised: a failed source is a recorded outcome
            attempt['error'] = str(exc)
            item['attempts'].append(attempt)
            continue
        is_pdf = body.startswith(b'%PDF')
        path = dest / f"{source['id']}-attempt{number + 1}{'.pdf' if is_pdf else '.html'}"
        path.write_bytes(body)
        attempt.update(local_path=path.relative_to(ROOT).as_posix(), bytes=len(body),
                       sha256=hashlib.sha256(body).hexdigest(), verified_pdf=is_pdf)
        if is_pdf:
            import fitz
            with fitz.open(path) as doc:
                attempt['pages'] = len(doc)
                text = '\n'.join(f'<<page {i + 1}>>\n' + page.get_text() for i, page in enumerate(doc))
            text_path = path.with_suffix('.txt')
            text_path.write_text(text, encoding='utf-8')
            attempt['text_path'] = text_path.relative_to(ROOT).as_posix()
            attempt['text_sha256'] = hashlib.sha256(text_path.read_bytes()).hexdigest()
            attempt['rights_notice_seen'] = [line.strip() for line in text.splitlines()
                                            if 'creativecommons' in line.lower() or 'copyright' in line.lower()][:8]
        item['attempts'].append(attempt)
        if is_pdf:
            item['status'] = 'held-local-only'
            return item
    item['status'] = 'not-obtained'
    return item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='sources-v1')
    args = ap.parse_args()
    dest = RAW / args.run
    dest.mkdir(parents=True, exist_ok=False)
    records = [fetch(source, dest) for source in SOURCES]
    out = dest / 'requests.json'
    out.write_text(json.dumps({'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'sources': records},
                              ensure_ascii=False, indent=2), encoding='utf-8')
    for r in records:
        last = r['attempts'][-1]
        print(r['id'], r['status'], last.get('bytes'), last.get('pages'), last.get('error', ''))


if __name__ == '__main__':
    main()
