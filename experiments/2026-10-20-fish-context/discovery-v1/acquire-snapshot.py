"""Acquire a bounded set of primary witnesses without redistributing their contents."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-20-fish-context'

SOURCES = [
    {'id': 'parpola2010', 'title': 'A Dravidian solution to the Indus script problem',
     'authors': ['Asko Parpola'], 'year': 2010,
     'urls': ['https://www.harappa.com/sites/default/files/pdf/Parpola-2010-Coimbatore.pdf',
              'https://tuhat.helsinki.fi/ws/portalfiles/portal/127256525/Parpola_A_2010._A_Dravidian_solution_to_the_Indus_script_problem.pdf'],
     'format': 'pdf', 'rights_status': 'rights-unverified',
     'purpose': 'Published fish, numeral-fish and astronomical hypotheses; H-9 and H-902 examples.'},
    {'id': 'belcher1991', 'title': 'Fish Resources in an Early Urban Context at Harappa, Pakistan',
     'authors': ['William R. Belcher'], 'year': 1991,
     'urls': ['https://www.harappa.com/sites/default/files/pdf/Harappa1986-90_08_Belcher-Fish_0_1.pdf'],
     'format': 'pdf', 'rights_status': 'rights-unverified',
     'purpose': 'Independent fish-resource contexts; require an object-to-deposit join before connecting an inscription.'},
    {'id': 'mukhopadhyay2023',
     'title': 'Semantic scope of Indus inscriptions comprising taxation, trade and craft licensing, commodity control and access control: archaeological and script-internal evidence',
     'authors': ['Bahata Ansumali Mukhopadhyay'], 'year': 2023,
     'urls': ['https://www.nature.com/articles/s41599-023-02320-7.pdf',
              'https://www.nature.com/articles/s41599-023-02320-7'],
     'format': 'pdf-or-html', 'rights_status': 'rights-unverified',
     'purpose': 'Economic rival and its source-located critiques of numeral-fish readings.'},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='sources-v1')
    args = ap.parse_args()
    dest = RAW / args.run
    dest.mkdir(parents=True, exist_ok=False)
    records = []
    for source in SOURCES:
        item = dict(source, retrieved_utc=datetime.now(timezone.utc).isoformat(), attempts=[])
        for number, url in enumerate(source['urls']):
            attempt = {'url': url}
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Indus research source check; scholarly use'})
                with urllib.request.urlopen(req, timeout=40) as response:
                    body = response.read()
                    attempt.update(http_status=response.status, content_type=response.headers.get('Content-Type'),
                                   final_url=response.url)
                is_pdf = body.startswith(b'%PDF')
                ext = '.pdf' if is_pdf else '.html'
                path = dest / (source['id'] + f'-attempt{number + 1}' + ext)
                path.write_bytes(body)
                attempt.update(local_path=path.relative_to(ROOT).as_posix(), bytes=len(body),
                               sha256=hashlib.sha256(body).hexdigest(), verified_pdf=is_pdf)
                if is_pdf:
                    import fitz
                    with fitz.open(path) as doc:
                        attempt['pages'] = len(doc)
                        text = '\n'.join(page.get_text() for page in doc)
                    text_path = path.with_suffix('.txt')
                    text_path.write_text(text, encoding='utf-8')
                    attempt['text_path'] = text_path.relative_to(ROOT).as_posix()
                    attempt['rights_notice_seen'] = [line.strip() for line in text.splitlines()
                                                    if 'creativecommons.org' in line or 'Copyright' in line][:8]
                else:
                    sample = body.decode('utf-8', errors='replace')
                    attempt['challenge_page'] = any(t in sample.lower() for t in
                                                    ['just a moment', 'checking your browser', 'captcha'])
                item['attempts'].append(attempt)
                if is_pdf:
                    item['status'] = 'held-local-only'
                    break
            except Exception as exc:
                attempt['error'] = str(exc)
                item['attempts'].append(attempt)
        item.setdefault('status', 'not-acquired-as-pdf')
        records.append(item)
        print(source['id'], item['status'], flush=True)
    out = HERE / (args.run + '.json')
    with out.open('x', encoding='utf-8') as f:
        json.dump({'schema_version': '1.0', 'sources': records,
                   'handling': 'All acquired witnesses and extracted text remain local. Source notes and hashes are tracked.'},
                  f, indent=2)


if __name__ == '__main__':
    main()
