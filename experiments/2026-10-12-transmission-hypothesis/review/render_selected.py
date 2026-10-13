"""Source inspection renders only; these remain local with their parent pins."""
from datetime import datetime, timezone
import hashlib
import json
import fitz
from acquire_controls import REPO, RAW

TARGETS = [
    ('oldavestan', 'data/raw/2026-10-12-transmission-hypothesis/review/oldavestan-lessons-lexicons.pdf', [35, 70, 123, 161, 162]),
    ('narasimhan', 'data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1/narasimhan2019-author.pdf', [9]),
    ('witzel', 'data/raw/2026-10-12-transmission-hypothesis/review/witzel1997-author-tls-exception.pdf', [3, 80]),
]

if __name__ == '__main__':
    records = []
    for key, name, pages in TARGETS:
        path = REPO / name
        parent_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        doc = fitz.open(path)
        for number in pages:
            out = RAW / f'{key}-pdf-page-{number:03d}.png'
            if out.exists():
                raise FileExistsError(out)
            doc[number - 1].get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(out)
            records.append({'parent_path': name, 'parent_sha256': parent_sha,
                            'pdf_page_one_based': number,
                            'path': out.relative_to(REPO).as_posix(),
                            'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                            'method': 'PyMuPDF render, matrix1.6; system pdftoppm unavailable',
                            'redistribution': 'local-only'})
    with (RAW / 'renders-v1.json').open('x', encoding='utf-8') as stream:
        json.dump({'created_utc': datetime.now(timezone.utc).isoformat(),
                   'renders': records}, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({'renders': len(records), 'manifest': str(RAW / 'renders-v1.json')}))
