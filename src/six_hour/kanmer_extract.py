"""Preserve local text and render selected pages from acquired Kanmer witnesses."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import fitz
from bs4 import BeautifulSoup


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pages', default='')
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError('Keep earlier extraction endpoints.')
    args.output.mkdir(parents=True)
    manifest = {'input': str(args.input), 'input_sha256': digest(args.input),
                'code_sha256': digest(Path(__file__)), 'outputs': []}
    raw = args.input.read_bytes()
    if raw.startswith(b'%PDF'):
        doc = fitz.open(args.input)
        manifest['page_count'] = len(doc)
        texts = []
        for i, page in enumerate(doc):
            texts.append(f'\n--- PDF page {i + 1} ---\n' + page.get_text())
        path = args.output / 'text.txt'
        path.write_text(''.join(texts), encoding='utf-8')
        manifest['outputs'].append({'path': path.name, 'sha256': digest(path)})
        for n in [int(s) for s in args.pages.split(',') if s]:
            page = doc[n - 1]
            path = args.output / f'pdf{n}.png'
            page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(path)
            manifest['outputs'].append({'path': path.name, 'page_1based': n,
                                        'sha256': digest(path)})
    else:
        text = raw.decode('utf-8')
        array = json.loads(text[text.index('(') + 1:text.rindex(')')])
        soup = BeautifulSoup(array[0], 'html.parser')
        path = args.output / 'text-original.txt'
        path.write_text(soup.get_text('\n', strip=True), encoding='utf-8')
        manifest['outputs'].append({'path': path.name, 'sha256': digest(path)})
        decoded = path.read_text(encoding='utf-8').translate({0xF0030 + i: str(i) for i in range(10)})
        target = args.output / 'text-digit-decoded.txt'
        target.write_text(decoded, encoding='utf-8')
        manifest['outputs'].append({'path': target.name, 'sha256': digest(target)})
        manifest['decoding'] = {'map': 'U+F0030..U+F0039 to ASCII 0..9',
                                'changes': sum(a != b for a, b in zip(path.read_text(encoding='utf-8'), decoded))}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
