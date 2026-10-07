"""Acquire local witnesses and extract PDF text; run from repository root."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'
RAW.mkdir(parents=True, exist_ok=True)
for name in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[name] = str(RAW / 'tmp')
(RAW / 'tmp').mkdir(exist_ok=True)
import requests
import fitz

URLS = {
    'morphology-live.pdf': 'https://www.tamildigitallibrary.in/admin/assets/book/TVA_BOK_0065888/TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study.pdf',
    'tifinagh.pdf': 'https://www.unicode.org/Public/17.0.0/charts/blocks/U2D30.pdf',
    'ogham.pdf': 'https://www.unicode.org/Public/17.0.0/charts/blocks/U1680.pdf',
    'unicode-terms.html': 'https://www.unicode.org/copyright.html',
    'changizi.pdf': 'https://www.changizi.com/ChangiziAmNat2006.pdf',
    'portal-home.html': 'https://tngraffiti.in/',
}

def main():
    manifest = []
    for name, url in URLS.items():
        record = dict(url=url, local_path=str((RAW / name).relative_to(ROOT)), retrieved_utc=datetime.now(timezone.utc).isoformat())
        try:
            r = requests.get(url, timeout=90)
            record.update(status_code=r.status_code, final_url=r.url, content_type=r.headers.get('Content-Type'))
            (RAW / name).write_bytes(r.content)
            record.update(bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest())
            if r.status_code == 200 and name.endswith('.pdf'):
                p = fitz.open(stream=r.content, filetype='pdf')
                record['pages'] = len(p)
                (RAW / (name + '.pages.json')).write_text(json.dumps([{'pdf_page':i+1,'text':pg.get_text()} for i,pg in enumerate(p)],ensure_ascii=False,indent=2), encoding='utf-8')
                for i in range(min(len(p), 8)):
                    p[i].get_pixmap(matrix=fitz.Matrix(1.3, 1.3)).save(RAW / f'{Path(name).stem}-page-{i+1}.png')
        except Exception as e:
            record['failure'] = repr(e)
        manifest.append(record)
        print(json.dumps(record, ensure_ascii=True))
    old = ROOT / 'data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf'
    p = fitz.open(old)
    (RAW / 'morphology-old.pages.json').write_text(json.dumps([{'pdf_page':i+1,'text':pg.get_text()} for i,pg in enumerate(p)],ensure_ascii=False,indent=2),encoding='utf-8')
    manifest.append(dict(local_path=str(old.relative_to(ROOT)),reused=True,pages=len(p),sha256=hashlib.sha256(old.read_bytes()).hexdigest()))
    (RAW / 'acquisition.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

if __name__ == '__main__':
    main()
