"""Render scan pages at 300 dpi and retain a local page manifest.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/render_pages.py --pdf PATH --out DIR --pages 1,40-42 [--label primary] [--rotate 90] [--crop-page N --crop x0,y0,x1,y1 --crop-name NAME]
Page numbers are one-based. Crop coordinates are fractions of page width and height.
"""
import argparse
import hashlib
import json
import site
import sys
from pathlib import Path

sys.path.append(site.getusersitepackages())
import fitz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--pages', default='')
    ap.add_argument('--label', default='primary')
    ap.add_argument('--rotate', type=int, default=0)
    ap.add_argument('--crop-page', type=int)
    ap.add_argument('--crop')
    ap.add_argument('--crop-name', default='detail')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    pages = set()
    for part in filter(None, args.pages.split(',')):
        bounds = part.split('-')
        pages.update(range(int(bounds[0]), int(bounds[-1]) + 1))
    manifest_path = args.out / (args.label + '-manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'pdf': args.pdf.as_posix(), 'sha256': hashlib.file_digest(args.pdf.open('rb'), 'sha256').hexdigest(), 'dpi': 300, 'pages': {}}
    with fitz.open(args.pdf) as doc:
        manifest['pdf_page_count'] = len(doc)
        for n in sorted(pages):
            page = doc[n - 1]
            if args.rotate:
                page.set_rotation((page.rotation + args.rotate) % 360)
            target = args.out / f'{args.label}-p{n:04}.png'
            if not target.exists():
                pix = page.get_pixmap(dpi=300)
                pix.save(target)
            manifest['pages'][str(n)] = {'image': target.as_posix(), 'width_points': page.rect.width, 'height_points': page.rect.height}
            print(f'{n}: {target}', flush=True)
        if args.crop_page:
            page = doc[args.crop_page - 1]
            coords = [float(v) for v in args.crop.split(',')]
            clip = fitz.Rect(coords[0] * page.rect.width, coords[1] * page.rect.height, coords[2] * page.rect.width, coords[3] * page.rect.height)
            target = args.out / f'{args.label}-p{args.crop_page:04}-{args.crop_name}.png'
            page.get_pixmap(dpi=300, clip=clip).save(target)
            print(target, flush=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
