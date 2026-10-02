"""Render every report page and retain geometry/text checks for visual review."""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--edition', default='draft_review')
    args = parser.parse_args()
    path = ROOT / 'output/pdf/indus_script_research_report.pdf'
    out = ROOT / 'tmp/pdfs' / args.edition
    out.mkdir(parents=True, exist_ok=True)
    document = fitz.open(path)
    pages = []
    thumbs = []
    for index, page in enumerate(document):
        image_path = out / f'page_{index+1:02d}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False).save(image_path)
        blocks = page.get_text('blocks')
        outside = [list(block[:4]) for block in blocks if block[0] < 0 or block[1] < 0
                   or block[2] > page.rect.width or block[3] > page.rect.height]
        pages.append({'page': index+1, 'text_characters': len(page.get_text()),
                      'blocks_outside_page': outside, 'rendered_png': image_path.relative_to(ROOT).as_posix()})
        thumb = Image.open(image_path).convert('RGB')
        thumb.thumbnail((440, 570))
        card = Image.new('RGB', (460, 610), '#e8edef')
        card.paste(thumb, ((460-thumb.width)//2, 25))
        ImageDraw.Draw(card).text((12, 588), f'Page {index+1}', fill='#263744')
        thumbs.append(card)
    for start in range(0, len(thumbs), 6):
        selected = thumbs[start:start+6]
        contact = Image.new('RGB', (920, 610*((len(selected)+1)//2)), 'white')
        for index, thumb in enumerate(selected):
            contact.paste(thumb, (460*(index%2), 610*(index//2)))
        contact.save(out / f'contact_{start+1:02d}.png')
    check = {'pdf_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
             'pages': pages, 'page_count': len(pages),
             'limitation': 'Geometry/text extraction is supplemental. Every rendered page must be visually inspected.'}
    (out / 'render_check.json').write_text(json.dumps(check, indent=2), encoding='utf-8')
    print(json.dumps({'page_count': len(pages), 'outside_page_blocks': sum(len(p['blocks_outside_page']) for p in pages),
                      'output': out.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
