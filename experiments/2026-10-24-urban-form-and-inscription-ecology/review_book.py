"""Index all locally rendered pages for visual inspection; preserve each QA run."""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


def main(pdf, renders, out):
    if out.exists():
        raise FileExistsError(out)
    manifest = json.loads((Path(__file__).parent / 'book-manifest-v4.json').read_text(encoding='utf-8'))
    pages = sorted(renders.glob('page-*.png'))
    document = fitz.open(pdf)
    assert len(pages) == len(document) == manifest['pages']
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == manifest['sha256']
    review = renders.parent / 'review'
    review.mkdir(exist_ok=False)
    off_page = []
    text_chars = []
    landscape_pages = []
    for i, page in enumerate(document, 1):
        if page.rect.width > page.rect.height:
            landscape_pages.append(i)
        text_chars.append({'page': i, 'text_chars': len(page.get_text().strip())})
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    if x0 < -0.5 or y0 < -0.5 or x1 > page.rect.width + .5 or y1 > page.rect.height + .5:
                        off_page.append({'page': i, 'bbox': span['bbox'], 'text': span['text']})
    sheets = []
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 19)
    for start in range(0, len(pages), 20):
        sheet = Image.new('RGB', (1360, 2020), '#e6e8eb')
        draw = ImageDraw.Draw(sheet)
        for j, path in enumerate(pages[start:start + 20]):
            x = (j % 4) * 340
            y = (j // 4) * 404
            with Image.open(path) as original:
                thumb = original.convert('RGB')
                thumb.thumbnail((324, 370))
                sheet.paste(thumb, (x + (340 - thumb.width) // 2, y + 27))
            draw.text((x + 12, y + 3), f'Page {start + j + 1}', fill='#182536', font=font)
        path = review / f'layout-{start // 20 + 1}.jpg'
        sheet.save(path, quality=91)
        sheets.append(str(path))
    result = {
        'version': 'v4', 'pdf_sha256': manifest['sha256'],
        'pages': len(document), 'rendered_pages': len(pages),
        'off_page_text': off_page, 'landscape_figure_pages': landscape_pages,
        'contact_sheets': sheets, 'text_characters_by_page': text_chars,
        'human_visual_review': 'Record the inspection separately after viewing these sheets and selected full pages.',
        'scientific_validation': False,
    }
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pages': len(document), 'off_page_text': len(off_page), 'contact_sheets': sheets}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--renders', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.pdf, args.renders, args.out)
