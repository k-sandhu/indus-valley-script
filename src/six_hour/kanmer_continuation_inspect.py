"""Extract local source text and render bibliography witnesses without changing inputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use/source-continuation-2026-10-02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    endpoint = BASE / 'inspection-v1'
    raw = BASE / 'local-witness' / 'inspection-v1'
    if endpoint.exists() or raw.exists():
        raise RuntimeError('Preserve prior endpoints.')
    endpoint.mkdir(parents=True)
    raw.mkdir(parents=True)
    src = Path('C:/Users/sandh/Downloads/HansmukhSeth.docx')
    dest = raw / 'seth-public-cv.docx'
    shutil.copyfile(src, dest)
    with ZipFile(dest) as archive:
        tree = ET.fromstring(archive.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = [''.join(p.itertext()) for p in tree.findall('.//w:p', ns)]
    (raw / 'seth-public-cv-paragraphs.json').write_text(json.dumps(paragraphs, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    selected = [dict(paragraph=i, text=t) for i, t in enumerate(paragraphs, 1) if 'Kanmer' in t or '749-760' in t]
    (raw / 'seth-kanmer-citation-paragraphs.json').write_text(json.dumps(selected, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    records = [dict(id='seth-public-cv', url='https://independent.academia.edu/HansmukhSeth/CurriculumVitae',
                    download_url='https://www.academia.edu/attachments/132937215/download_file',
                    route='Normal Chrome public Download link through cua_repl downloadMedia',
                    original_download_path=str(src), local_path=dest.relative_to(ROOT).as_posix(),
                    bytes=dest.stat().st_size, sha256=sha(dest), paragraphs=len(paragraphs),
                    citation_paragraphs=[r['paragraph'] for r in selected], rights='unverified; local-only')]
    for folder, name in [('acquisition-institutional', 'rhin-annual2009'),
                         ('acquisition-followed', 'rhin-annual2011'),
                         ('acquisition-public-header-retry', 'journal39-contents')]:
        path = BASE / 'local-witness' / folder / (name + '.pdf')
        doc = fitz.open(path)
        pages = [dict(pdf_page=i+1, text=p.get_text()) for i, p in enumerate(doc)]
        (raw / (name + '-pages.json')).write_text(json.dumps(pages, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        hits = [p['pdf_page'] for p in pages if 'Kanmer' in p['text']]
        for page in hits:
            doc[page-1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(raw / f'{name}-pdf{page}.png')
        records.append(dict(id=name, local_path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                            sha256=sha(path), pdf_pages=len(doc), kanmer_hit_pdf_pages=hits))
        doc.close()
    (endpoint / 'source-inspection.json').write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (endpoint / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (endpoint / 'summary.json').write_text(json.dumps(dict(
        completed_utc=datetime.now(timezone.utc).isoformat(),
        protocol_sha256=sha(BASE / 'PROTOCOL.md'), code_sha256=sha(Path(__file__)),
        original_sources=len(records)), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(records, indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
