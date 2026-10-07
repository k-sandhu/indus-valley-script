"""Acquire shared primary source witnesses into the package's ignored raw directory."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from urllib.parse import quote
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests
import fitz

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[3]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision'
RAW.mkdir(parents=True, exist_ok=True)
for name in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[name] = str(RAW / 'tmp')
(RAW / 'tmp').mkdir(exist_ok=True)

TARGETS = {
    'mahadevan1977-excerpt': 'https://kashmirasitis.com/wp-content/uploads/2020/10/Indus-scriptdarend.pdf',
    'fuls2022-preview': 'https://www.researchgate.net/profile/Andreas-Fuls/publication/373522666_Corpus_of_Indus_Inscriptions/links/64f044280f7ab20a86674daa/Corpus-of-Indus-Inscriptions.pdf',
    'mahadevan1977-archive-metadata': 'https://archive.org/metadata/TheIndusScript.TextConcordanceAndTablesIravathanMahadevan',
}
ARCHIVE_BASE = 'https://archive.org/download/TheIndusScript.TextConcordanceAndTablesIravathanMahadevan/'
ARCHIVE_TARGETS = {
    'cisi2-archive': ARCHIVE_BASE + quote('Corpus of Indus Seals and Inscriptions. Collections in Pakistan_text.pdf'),
    'mahadevan1977-full': ARCHIVE_BASE + quote('The Indus Script. Text, Concordance and Tables -Iravathan Mahadevan.pdf'),
    'mahadevan1977-ocr': ARCHIVE_BASE + quote('The Indus Script. Text, Concordance and Tables -Iravathan Mahadevan_djvu.txt'),
}
DISCOVERY_TARGETS = {
    'sib-ri-santoni-report': 'https://safarmer.com/Indo-Eurasian/Sibri.pdf',
    'balochistan-research2018': 'https://ph.hu.edu.pk/public/uploads/vol-10/45-60.pdf',
    'miri-qalat-whitelevy': 'https://whitelevy.fas.harvard.edu/site-miri-qalat-and-kech-makran-balochistan-pakistan-during-second-half-3rd-millennium-bc-0',
    'miri-qalat-persee1992': 'https://www.persee.fr/doc/paleo_0153-9345_1992_num_18_1_4567',
    'miri-qalat-cnrs-archive': 'https://archives.mshmondes.cnrs.fr/index.php/informationobject/browse?collection=157053&levels=199&limit=10&sort=referenceCode&sortDir=asc&topLod=0&view=table',
}


def acquire(item):
    name, url = item
    record = {'id': name, 'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'reuse_status': 'rights-unverified'}
    try:
        response = requests.get(url, timeout=55)
        record.update(status_code=response.status_code, final_url=response.url, content_type=response.headers.get('Content-Type'))
        response.raise_for_status()
        payload = response.content
        suffix = '.pdf' if payload.startswith(b'%PDF') else '.json' if 'json' in response.headers.get('Content-Type', '') else '.txt' if url.endswith('.txt') else '.html'
        path = RAW / (name + suffix)
        path.write_bytes(payload)
        record.update(path=str(path.relative_to(ROOT)), bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), success=True)
        if suffix == '.pdf':
            doc = fitz.open(path)
            record['pages'] = len(doc)
            (RAW / (name + '.pages.json')).write_text(json.dumps([{'pdf_page': i + 1, 'text': page.get_text()} for i, page in enumerate(doc)], ensure_ascii=False, indent=2), encoding='utf-8')
            (RAW / (name + '.txt')).write_text('\n'.join(f'\nPDF PAGE {i+1}\n{page.get_text()}' for i, page in enumerate(doc)), encoding='utf-8')
    except Exception as error:
        record.update(success=False, error=f'{type(error).__name__}: {error}')
    return record


if __name__ == '__main__':
    targets = DISCOVERY_TARGETS if '--discovery' in sys.argv else ARCHIVE_TARGETS if '--archive' in sys.argv else TARGETS
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(acquire, targets.items()))
    manifest = 'acquisition-discovery.json' if '--discovery' in sys.argv else 'acquisition-archive.json' if '--archive' in sys.argv else 'acquisition.json'
    (RAW / manifest).write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for record in records:
        print(record['id'], record['success'], record.get('pages'), record.get('error', ''))
