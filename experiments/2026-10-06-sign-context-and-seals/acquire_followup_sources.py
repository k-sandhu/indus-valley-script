"""Acquire new public source witnesses for the post-launch D2 amendment."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'
URLS = {
    'chao2014': 'https://harvardforest.fas.harvard.edu/sites/default/files/ellison-pubs/2014/Chao_etal_2014_EM.pdf',
    'kenoyer2005chronology': 'https://www.harappa.com/sites/default/files/pdf/Kenoyer%202005%20Faience%20Workshop.pdf',
    'salut2016': 'https://harappa.com/sites/default/files/pdf/Bronze-Age-Indus-Connections.pdf',
    'frenez2024summary': 'https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia',
    'yadav2010': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0009506',
    'chao2014author': 'https://www.robertkcolwell.org/publications/6842.pdf',
    'inextsource': 'https://raw.githubusercontent.com/JohnsonHsieh/iNEXT/master/R/iNEXT.r',
    'farmer2004': 'https://safarmer.com/files/fsw3.pdf',
    'frenez2023primary': 'https://oxfordre.com/asianhistory/view/10.1093/acrefore/9780190277727.001.0001/acrefore-9780190277727-e-595',
}


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', default='followup-sources-2026-10-07-01')
    ap.add_argument('--only', nargs='*')
    args = ap.parse_args()
    dest = RAW / args.batch
    dest.mkdir(parents=True, exist_ok=False)
    manifest = []
    for key, url in URLS.items():
        if args.only and key not in args.only:
            continue
        row = {'id': key, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
               'rights': 'rights-unverified; local-only witness'}
        try:
            r = requests.get(url, timeout=50)
            row.update(http_status=r.status_code, final_url=r.url)
            suffix = '.pdf' if r.content.startswith(b'%PDF') else '.html'
            file = dest / (key + suffix)
            file.write_bytes(r.content)
            row.update(path=file.relative_to(ROOT).as_posix(), bytes=len(r.content),
                       sha256=hashlib.sha256(r.content).hexdigest())
            row['success'] = bool(r.ok)
            if r.ok and suffix == '.pdf':
                reader = PdfReader(file)
                text = '\n'.join(f'\n=== PDF PAGE {i+1} ===\n{p.extract_text() or ""}'
                                 for i, p in enumerate(reader.pages))
                row['pdf_pages'] = len(reader.pages)
                file.with_suffix('.txt').write_text(text, encoding='utf-8')
            elif r.ok:
                file.with_suffix('.txt').write_text(BeautifulSoup(r.content, 'html.parser').get_text('\n'),
                                                   encoding='utf-8')
        except Exception as e:
            row.update(success=False, error=str(e))
        manifest.append(row)
        (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(key, row.get('http_status'), row.get('success'), flush=True)


if __name__ == '__main__':
    run()
