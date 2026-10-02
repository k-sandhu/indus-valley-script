"""Preserve new Kanmer source coordinates and independently check acquired bytes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use/source-continuation-2026-10-02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    endpoint = BASE / 'inspection-v3'
    raw = BASE / 'local-witness/inspection-v3'
    if endpoint.exists() or raw.exists():
        raise RuntimeError('Preserve prior endpoints.')
    endpoint.mkdir(parents=True)
    raw.mkdir(parents=True)
    targets = [
        ('acquisition-final-leads', 'parpola2018-authorproof', None),
        ('acquisition-institutional', 'rhin-annual2009', [3, 64, 183]),
        ('acquisition-followed', 'rhin-annual2011', [52]),
        ('acquisition-public-header-retry', 'journal39-contents', [2]),
    ]
    sources = []
    checks = []
    for folder, source_id, fixed_pages in targets:
        path = BASE / 'local-witness' / folder / (source_id + '.pdf')
        acquisition = next(x for x in json.loads((BASE / folder / 'access.json').read_text(encoding='utf-8')) if x['id'] == source_id)
        checks.append(dict(check=f'{source_id}: acquisition byte hash', passed=sha(path) == acquisition['sha256']))
        with fitz.open(path) as doc:
            pages = [dict(pdf_page=i + 1, text=p.get_text()) for i, p in enumerate(doc)]
            (raw / (source_id + '-pages.json')).write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            selected = fixed_pages or [p['pdf_page'] for p in pages if 'Kanmer' in p['text'] or '487' in p['text']]
            rendered = []
            for page in selected:
                outfile = raw / f'{source_id}-pdf{page}.png'
                doc[page - 1].get_pixmap(matrix=fitz.Matrix(2, 2)).save(outfile)
                rendered.append(dict(pdf_page=page, png=outfile.relative_to(ROOT).as_posix(), sha256=sha(outfile)))
            sources.append(dict(id=source_id, bytes=path.stat().st_size, sha256=sha(path), pdf_pages=len(doc), rendered=rendered))
    (endpoint / 'source-coordinates.json').write_text(json.dumps(sources, indent=2) + '\n', encoding='utf-8')
    (endpoint / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
    (endpoint / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (endpoint / 'summary.json').write_text(json.dumps(dict(completed_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=sha(BASE / 'PROTOCOL.md'), code_sha256=sha(Path(__file__)), checks_passed=sum(c['passed'] for c in checks), checks_total=len(checks)), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(sources, indent=2))


if __name__ == '__main__':
    main()
