"""Local-only text derivatives; acquisition is distinct from selected reading."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import fitz
from bs4 import BeautifulSoup
from acquire_controls import REPO, RAW

INPUTS = [
    ('jamison2014-1-15', 'data/raw/2026-10-11-early-indian-continuity/review/jamison2014-2-15.pdf'),
    ('jamison2014-13-22', 'data/raw/2026-10-11-early-indian-continuity/review/jamison2014-13-22.pdf'),
    ('oldavestan2006', 'data/raw/2026-10-12-transmission-hypothesis/review/oldavestan-lessons-lexicons.pdf'),
    ('witzel1997', 'data/raw/2026-10-12-transmission-hypothesis/review/witzel1997-author-tls-exception.pdf'),
    ('narasimhan2019', 'data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1/narasimhan2019-author.pdf'),
    ('boyce2003', 'data/raw/2026-10-11-early-indian-continuity/review/haoma-rituals.html'),
    ('skjaervo-kayanian', 'data/raw/2026-10-12-transmission-hypothesis/review/skjaervo-kayanian.html'),
]


if __name__ == '__main__':
    records = []
    for key, name in INPUTS:
        path = REPO / name
        body = path.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        if path.suffix == '.pdf':
            doc = fitz.open(path)
            pages = [{'pdf_page_one_based': i + 1, 'text': page.get_text()}
                     for i, page in enumerate(doc)]
            value = {'parent_path': name, 'parent_sha256': digest,
                     'page_count': len(doc), 'pdf_metadata': doc.metadata, 'pages': pages}
            out = RAW / f'{key}-pages.json'
            payload = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
            method = 'PyMuPDF page.get_text; no source-language glyph normalization'
        else:
            soup = BeautifulSoup(body, 'html.parser')
            for element in soup.select('script,style,nav,header,footer'):
                element.decompose()
            out = RAW / f'{key}-text.txt'
            payload = soup.get_text('\n', strip=True) + '\n'
            method = 'BeautifulSoup text after script/style/nav/header/footer removal'
        with out.open('x', encoding='utf-8') as stream:
            stream.write(payload)
        records.append({'source_key': key, 'parent_path': name, 'parent_sha256': digest,
                        'path': out.relative_to(REPO).as_posix(),
                        'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                        'method': method, 'redistribution': 'local-only'})
    with (RAW / 'extraction-v1.json').open('x', encoding='utf-8') as stream:
        json.dump({'created_utc': datetime.now(timezone.utc).isoformat(),
                   'derivatives': records}, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps([{'source': r['source_key'], 'derivative': r['path']} for r in records], indent=2))
