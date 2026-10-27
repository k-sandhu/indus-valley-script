"""Preserve two official methodological pages locally with access and byte hashes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import urllib.request

P = Path(__file__).resolve().parent
OUT = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/methods-v1')
SOURCES = [
    ('QGIS344', 'QGIS Documentation 3.44: Georeferencer',
     'https://docs.qgis.org/3.44/en/docs/user_manual/managing_data_source/georeferencer.html',
     'Entering ground control points; available transformation algorithms; transformation report and RMS errors'),
    ('HE-BAYESIAN', 'Historic England: Radiocarbon Dating and Chronological Modelling, The Bayesian Process',
     'https://historicengland.org.uk/images-books/publications/radiocarbon-dating-chronological-modelling/the-bayesian-process/',
     'Sections 3.1, 3.2 and 3.3, problem definition, suitable samples and simulation'),
]


def main():
    OUT.mkdir(exist_ok=False)
    rows = []
    for key, title, url, locator in SOURCES:
        row = dict(source_id=key, title=title, url=url, locator=locator,
                   access_date_local='2026-10-24', retrieved_utc=datetime.now(timezone.utc).isoformat(),
                   rights_status='rights-unverified', handling='local-only HTML witness; authored methods summaries in package')
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research source audit)'})
            with urllib.request.urlopen(req, timeout=45) as response:
                content = response.read()
                row.update(final_url=response.url, content_type=response.headers.get('Content-Type'))
            path = OUT / (key.lower() + '.html')
            path.write_bytes(content)
            row.update(status='held', physical_path=str(path),
                       logical_path='data/raw/2026-10-24-shared-infrastructure-plan-test/methods-v1/' + path.name,
                       sha256=hashlib.sha256(content).hexdigest(), bytes=len(content))
        except Exception as error:
            row.update(status='failed', error=repr(error))
        rows.append(row)
    (P / 'methods-sources-v1.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps([{'id':r['source_id'], 'status':r['status'], 'bytes':r.get('bytes')} for r in rows], indent=2))


if __name__ == '__main__':
    main()
