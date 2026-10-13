"""Poppler renders; retain and correct the first manifest's availability note."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from render_selected import TARGETS
from acquire_controls import REPO, RAW

if __name__ == '__main__':
    binary = shutil.which('pdftoppm')
    if binary is None:
        raise RuntimeError('pdftoppm unavailable to this process')
    records = []
    for key, name, pages in TARGETS:
        path = REPO / name
        parent_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        for number in pages:
            prefix = RAW / f'{key}-pdf-page-{number:03d}-poppler'
            out = prefix.with_suffix('.png')
            if out.exists():
                raise FileExistsError(out)
            subprocess.run([binary, '-f', str(number), '-l', str(number), '-r', '120',
                            '-singlefile', '-png', str(path), str(prefix)], check=True,
                           capture_output=True)
            records.append({'parent_path': name, 'parent_sha256': parent_sha,
                            'pdf_page_one_based': number,
                            'path': out.relative_to(REPO).as_posix(),
                            'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                            'method': 'Poppler pdftoppm,120dpi', 'redistribution': 'local-only'})
    with (RAW / 'renders-v2.json').open('x', encoding='utf-8') as stream:
        json.dump({'created_utc': datetime.now(timezone.utc).isoformat(),
                   'correction': 'The earlier renders-v1 used PyMuPDF successfully but incorrectly said system pdftoppm was unavailable. Its outputs are preserved; these new renders use the observed Poppler binary.',
                   'preserved_first_manifest_sha256': hashlib.sha256((RAW / 'renders-v1.json').read_bytes()).hexdigest(),
                   'binary': binary, 'renders': records}, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({'renders': len(records), 'manifest': str(RAW / 'renders-v2.json')}))
