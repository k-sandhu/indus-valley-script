"""Recreate the selected source-page witnesses into a new local-only directory."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import fitz

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/synthesis'
BASE = 'data/raw/2026-10-06-evidence-census/sites-deep/'
PLANS = [
    ('IM77', BASE + 'a-pakistan-afghanistan/common-revision/mahadevan1977-full.pdf', [17]),
    ('CISI2', BASE + 'a-pakistan-afghanistan/common-revision/cisi2-archive.pdf', [18, 21, 413, 445, 446]),
    ('CISI1', BASE + 'c-north-india/cisi1.pdf', [362, 385, 397]),
    ('BHAGWANPURA', BASE + 'c-north-india/bhagwanpura1993.pdf', [177, 178, 179, 180]),
    ('DESALPAR', BASE + 'b-gujarat-kutch-maharashtra/IAR1963-1964-ALT.pdf', [19]),
    ('NAGWADA', BASE + 'b-gujarat-kutch-maharashtra/IAR1987-1988-ALT.pdf', [28]),
    ('KARANPURA', BASE + 'c-north-india/iar2013_alt.pdf', [121, 122, 125]),
    ('RANGPUR', BASE + 'b-gujarat-kutch-maharashtra/RANGPUR1963.pdf', [169]),
    ('LOTHAL', BASE + 'b-gujarat-kutch-maharashtra/LOTHAL2005.pdf', [5, 6]),
    ('NIPPUR', BASE + 'd-finds-abroad/nippur1993-s3.pdf', [151]),
    ('CISI33', BASE + 'd-finds-abroad/cisi33-excerpt2022.pdf', [8, 9, 13, 17]),
    ('SALUT', BASE + 'd-finds-abroad/salut2016.pdf', [16, 17, 18]),
    ('GONUR', BASE + 'd-finds-abroad/gonur2005.pdf', [130]),
    ('ICIT2023', 'data/raw/2026-10-02-dataset-landscape/witnesses-v1/caa2023.pdf', [281])]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', required=True, help='New directory below paired local raw')
    ap.add_argument('--render', action='store_true', help='Render the selected pages for manual review')
    args = ap.parse_args()
    out = (ROOT / args.output_dir).resolve()
    if not out.is_relative_to(RAW) or out.exists():
        raise ValueError('Use a new directory under this package local raw')
    out.mkdir(parents=True)
    tmp = out / 'tmp'
    tmp.mkdir()
    for key in ['TMP', 'TEMP', 'MPLCONFIGDIR']:
        os.environ[key] = str(tmp)
    manifest = []
    for source, rel, pages in PLANS:
        p = ROOT / rel
        digest = sha256(p.read_bytes()).hexdigest()
        with fitz.open(p) as doc:
            for n in pages:
                stem = source + '-pdf' + str(n)
                text = doc[n - 1].get_text()
                (out / (stem + '.txt')).write_text(text, encoding='utf-8')
                if args.render:
                    doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(out / (stem + '.png'))
                manifest.append({'source_id': source, 'source': rel, 'source_sha256': digest,
                                 'pdf_page_1_based': n, 'text_characters': len(text),
                                 'text_file': stem + '.txt', 'render_file': stem + '.png' if args.render else None})
    p = ROOT / (BASE + 'b-gujarat-kutch-maharashtra/DHOLAVIRA2015.txt')
    s = p.read_text(encoding='utf-8-sig')
    targets = ['225 seals and 60 sealings', 'A total of 194 seals', 'A total of 61 sealings']
    for i, target in enumerate(targets):
        j = s.find(target)
        if j < 0:
            raise ValueError('Dholavira mirror passage not found: ' + target)
        (out / f'DHOLAVIRA-section-{i}.txt').write_text(s[max(0, j - 500):j + 1600], encoding='utf-8')
    manifest.append({'source_id': 'DHOLAVIRA', 'source': p.relative_to(ROOT).as_posix(),
                     'source_sha256': sha256(p.read_bytes()).hexdigest(), 'passage_files': [f'DHOLAVIRA-section-{i}.txt' for i in range(3)],
                     'source_basis': 'Saved mirror transcription; original report page images unavailable in this package'})
    (out / 'source-page-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pages': len(manifest) - 1, 'dholavira_passages': 3, 'output': out.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
