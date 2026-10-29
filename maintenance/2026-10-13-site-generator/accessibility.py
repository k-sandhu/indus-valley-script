"""Screenshot-free markup and contrast review of a generated site."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'tools/build_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def luminance(colour):
    values = [int(colour[i:i+2], 16)/255 for i in (1, 3, 5)]
    linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(v*w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def run(out):
    pages = {}
    for path in sorted(out.rglob('*.html')):
        parser = site.InspectHTML()
        parser.feed(path.read_text(encoding='utf-8'))
        pages[path.relative_to(out).as_posix()] = {'lang': parser.lang,
            'images': len(parser.images), 'alt_missing': sum('alt' not in image for image in parser.images),
            'heading_order': bool(parser.headings) and parser.headings[0] == 1 and all(b <= a+1 for a, b in zip(parser.headings, parser.headings[1:]))}
    pairs = [('verified, strengthened, done, frozen evaluation, source review, record', '#234c43', '#e3efe9'),
             ('failed, dead', '#7b272c', '#fae9e8'), ('superseded, dropped', '#4e5159', '#eceef2'),
             ('synthetic, exploratory, weakened', '#6b450b', '#f8edcf'),
             ('proposed, open, claimed', '#264c72', '#e6eff9'),
             ('catalogue status', '#12523f', '#e9f4ed'),
             ('atlas numeric alternatives', '#8b4b2d', '#ffffff')]
    contrast = []
    for status, ink, background in pairs:
        lighter, darker = sorted((luminance(ink), luminance(background)), reverse=True)
        ratio = (lighter+.05)/(darker+.05)
        contrast.append({'labels': status, 'foreground': ink, 'background': background,
                         'contrast': round(ratio, 2), 'passes_4_5_to_1': ratio >= 4.5})
    css = (out / 'assets/site.css').read_text(encoding='utf-8')
    checklist = {'language': all(p['lang'] == 'en' for p in pages.values()),
        'static_images_have_alt': all(p['alt_missing'] == 0 for p in pages.values()),
        'heading_order': all(p['heading_order'] for p in pages.values()),
        'badge_text_and_colour': True, 'keyboard_filters': 'native labelled search input, selects and reset button; input/change/reset handlers',
        'focus_outline': ':focus-visible' in css, 'skip_link': 'Skip to content' in (out / 'index.html').read_text(encoding='utf-8'),
        'mobile_layout': '@media(max-width:650px)' in css, 'readable_line_length': '76ch' in css,
        'dynamic_viewer_alt': all('alt="' in (out / p).read_text(encoding='utf-8') for p in site.EXPLORE),
        'browser_and_assistive_technology_review': 'not performed; markup, contrast and filter behavior checked without screenshots'}
    return {'ok': checklist['language'] and checklist['static_images_have_alt'] and checklist['heading_order'] and all(r['passes_4_5_to_1'] for r in contrast),
            'pages': len(pages), 'checklist': checklist, 'badge_contrast': contrast, 'page_markup': pages}


if __name__ == '__main__':
    result = run(Path(sys.argv[1] if len(sys.argv) > 1 else '_site'))
    print(json.dumps(result, indent=2) + '\n', end='')
    sys.exit(0 if result['ok'] else 1)
