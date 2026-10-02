"""Extract original raster figures from the acquired 2012 Kanmer author copy."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use'
SOURCE = BASE / 'local-witness/acquisition-gis-file/teramura-kondo-uno2012-gis-chapter.pdf'
OUT = BASE / 'local-witness/gis-native-figures-reviewed'


def main():
    if OUT.exists():
        raise RuntimeError('Keep earlier image endpoints.')
    OUT.mkdir(parents=True)
    doc = fitz.open(SOURCE)
    page = doc[24]
    records = []
    # The captions were inspected on the complete rendered page. Resource xref
    # order is unrelated to visual order, so order images by their page bounds.
    xrefs = sorted((i[0] for i in page.get_images(full=True)),
                   key=lambda x: (round(page.get_image_rects(x)[0].y0),
                                  page.get_image_rects(x)[0].x0))
    labels = [('5.1.27', '899c'), ('5.1.28', '900c'),
              ('5.1.29', '1286b'), ('5.1.30', '1054'),
              ('5.1.31', '1996c'), ('5.1.32', '1997c'),
              ('5.1.33', '1995c'), ('5.1.34', '1007')]
    mappings = [(x, figure, label) for x, (figure, label) in zip(xrefs, labels)]
    for xref, figure, label in mappings:
        content = doc.extract_image(xref)
        path = OUT / f'figure-{figure}-{label}.{content["ext"]}'
        path.write_bytes(content['image'])
        records.append({'xref': xref, 'figure': figure, 'caption_object_label': label,
                        'path': path.relative_to(BASE).as_posix(),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'pixels': [content['width'], content['height']],
                        'pdf_bounds_points': [list(rect) for rect in page.get_image_rects(xref)],
                        'operation': 'Unchanged original embedded image bytes extracted with PyMuPDF.'})
    manifest = {'pdf_page_1based': 25, 'printed_page': 187,
                'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                'embedded_mesh_files': doc.embfile_count(), 'figures': records}
    (BASE / 'gis-figure-manifest-reviewed.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
