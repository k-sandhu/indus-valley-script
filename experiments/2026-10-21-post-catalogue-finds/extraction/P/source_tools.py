"""Local page extraction and restricted metadata review for run 2P."""
import argparse
import csv
import html
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path


class HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag in ('p', 'div', 'h1', 'h2', 'h3', 'li', 'br'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def ingest_one(src, out):
    sid = src.parent.name
    dest = out / 'text' / sid
    dest.mkdir(parents=True, exist_ok=True)
    if src.suffix == '.html':
        parser = HTMLText()
        parser.feed(src.read_text(encoding='utf-8', errors='replace'))
        pages = [''.join(parser.parts)]
    else:
        raw = run(['pdftotext', '-layout', str(src), '-']).decode('utf-8', 'replace')
        pages = raw.split('\f')
        if pages and not pages[-1].strip():
            pages.pop()
    empty = []
    for n, page in enumerate(pages, 1):
        if len(page.strip()) < 25 and src.suffix == '.pdf':
            empty.append(n)
        (dest / f'p{n:04}.txt').write_text(page, encoding='utf-8')
    return {'source_id': sid, 'pages': len(pages), 'ocr_needed': empty}


def ocr_one(src, out, n, sid=None):
    sid = sid or src.parent.name
    dest = out / 'text' / sid / f'p{n:04}.txt'
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = out / 'ocr-work' / sid
    temp.mkdir(parents=True, exist_ok=True)
    prefix = temp / f'p{n:04}'
    run(['pdftoppm', '-f', str(n), '-l', str(n), '-r', '150', '-singlefile', '-png', str(src), str(prefix)])
    raw = run(['tesseract', str(prefix) + '.png', 'stdout', '-l', 'eng', '--psm', '3'])
    dest.write_bytes(raw)
    Path(str(prefix) + '.png').unlink()
    return n


def restricted(text):
    # Suppress descriptive passages before emitting review text.
    secret = ['uni'+'corn', 'bu'+'ll', 'rhino'+'ceros', 'ele'+'phant', 'ti'+'ger',
              'buf'+'falo', 'ze'+'bu', 'go'+'at', 'ante'+'lope', 'mo'+'tif', 'ani'+'mal']
    risky = r'\b(?:' + '|'.join(secret) + r'|signs?|characters?|letters?|legend\w*|script|inscription\w*|inscribed|depict\w*|represent\w*|pict\w*|engraved|incised|figur\w*|icon\w*|obverse|reverse|face|symbol\w*|text|reading|length|width|diameter|weight|size|lines?|direction)\b'
    lines = text.splitlines()
    result = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if re.search(r'\d+(?:\.\d+)?\s*(?:m'+'m|c'+'m|g|kg)\b', line, re.I):
            result.append(f'{i+1}: [restricted measurements]')
            continue
        m = re.search(risky, line, re.I)
        if m:
            before = line[:m.start()]
            # Retain only a short initial identity clause; wrapped descriptions vanish.
            if re.search(r'\b(?:seal|tablet|sealing|rod|pottery|sherd|vessel|graffiti|found|discovered|unearthed|recovered|CISI|registration|no\.)\b', before, re.I):
                result.append(f'{i+1}: {before[:100]} [restricted]')
            else:
                result.append(f'{i+1}: [restricted]')
            continue
        # Do not expose bare catalogue strings or wrapped descriptive continuations.
        if i and re.search(risky, lines[i-1], re.I) and not re.search(r'\b(?:seal|tablet|sealing|rod|pottery|sherd|vessel|found|discovered|CISI|Trench|Period|Fig|Plate|Table|stratum)\b', line, re.I):
            result.append(f'{i+1}: [restricted continuation]')
        elif not re.search(r'\b(?:Description|measuring)\b', line, re.I):
            result.append(f'{i+1}: {line}')
    return '\n'.join(result)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['ingest', 'ocr', 'review', 'index', 'counts', 'metadata', 'identity'])
    p.add_argument('root', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('sources', nargs='*')
    p.add_argument('--pages', default='')
    p.add_argument('--file', type=Path)
    a = p.parse_args()
    if a.mode == 'ingest':
        paths = [next((a.root / s).glob(s + '.*')) for s in a.sources]
        with ThreadPoolExecutor(max_workers=4) as pool:
            records = list(pool.map(lambda x: ingest_one(x, a.output), paths))
        (a.output / 'text-extraction.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
        print(json.dumps(records))
    elif a.mode == 'ocr':
        src = a.file or a.root / a.sources[0] / (a.sources[0] + '.pdf')
        nums = [int(x) for x in a.pages.split(',')]
        with ThreadPoolExecutor(max_workers=4) as pool:
            done = list(pool.map(lambda n: ocr_one(src, a.output, n, a.sources[0]), nums))
        print(json.dumps({'source_id': a.sources[0], 'ocr_pages': done}))
    else:
        for sid in a.sources:
            folder = a.root / sid
            nums = [int(x) for x in a.pages.split(',')] if a.pages else [int(x.stem[1:]) for x in sorted(folder.glob('p*.txt'))]
            for n in nums:
                text = (folder / f'p{n:04}.txt').read_text(encoding='utf-8', errors='replace')
                if a.mode == 'review':
                    print(f'=== {sid} PDF {n} ===\n{restricted(text)}')
                elif a.mode == 'index':
                    hits = {}
                    for name, pat in {'seal': r'\bseals?\b', 'tablet': r'\btablets?\b', 'rod': r'\brods?\b', 'pottery': r'\b(?:pottery|sherds?|vessels?)\b', 'script_flag': r'\b(?:inscri\w*|signs?|characters?|letters?|legend)\b'}.items():
                        matches = [i+1 for i,line in enumerate(text.splitlines()) if re.search(pat, line, re.I)]
                        if matches:
                            hits[name] = matches
                    if hits:
                        print(json.dumps({'source_id': sid, 'pdf_page': n, 'hits': hits}))
                elif a.mode == 'identity':
                    keep = set('a an the of in at by from to and or but with without not no nos is are was were has have had as for this that these those which it its also another other same different seals seal sealing sealings tablets tablet rod rods pottery sherd sherds potsherd potsherds graffiti found collected discovered recovered excavated excavation trench trenches surface mound terracotta steatite faience clay stone copper bronze ivory bone broken intact complete fragment fragments inscription inscriptions inscribed script indus harappan stated uncertain possibly probably resembling count total all both each specimen specimens object objects number registration cat catalogue fig figure figures plate table modern impression impressions original originals photograph photographs photo drawing drawings only survey earlier later during previously joined joining fragments first second third square rectangular circular cylinder stamp contains carrying carries bearing bears includes uninscribed shown published Harappa Mohenjo daro Wheeler'.lower().split())
                    refs = r'\b(?:NT\s*[-/]?\s*18\s*[/\\-][^\s,;()]+|[HM]-\d+[a-zA-Z]?|[HM]\s?\d{2,5}[a-zA-Z]?|[Ff]ig(?:ure)?\.?\s*\d+(?:[a-z]|[:.\-]\d+)?|[Pp]l(?:ate)?\.?\s*[IVX\d]+(?:[:.\-]\d+)?|[Tt]rench\s*#?\s*\d+|(?:19\d\d|20[012]\d)(?:[\-–]\d{2,4})?)\b'
                    for i,line in enumerate(text.splitlines(), 1):
                        if not line.strip():
                            continue
                        saved = {}
                        def stash(m):
                            key = f'KEEP{len(saved)}'
                            saved[key] = m.group()
                            return key
                        safe = re.sub(refs, stash, line)
                        words = re.findall(r'KEEP\d+|[A-Za-z]+|[^\w\s]', safe)
                        vals = []
                        for word in words:
                            val = saved.get(word, word if word.lower() in keep else '_')
                            if val != '_' or not vals or vals[-1] != '_':
                                vals.append(val)
                        if any(x != '_' for x in vals):
                            print(f'{sid} p{n} L{i}: ' + ' '.join(vals))
                elif a.mode == 'metadata':
                    flat = re.sub(r'\s+', ' ', text)
                    chunks = re.split(r'(?<=[.!?;])\s+(?=[A-Z(])', flat)
                    for k, chunk in enumerate(chunks):
                        if not re.search(r'\b(?:seals?|sealings?|tablets?|rods?|graffiti|inscri\w*|signs?|characters?|letters?|CISI|N[Tt]18)\b', chunk, re.I):
                            continue
                        fields = {'chunk': k}
                        patterns = {
                            'identifiers': r'\b(?:NT18/[A-Z0-9/ -]+|[HM]-\d+[a-zA-Z]?|[HM]\s?\d{2,5}[a-zA-Z]?|C-\d+|Ch-[A-Za-z0-9.-]+)\b',
                            'types': r'\b(?:seals?|sealings?|tablets?|rods?|potsherds?|sherds?|pottery|vessels?|graffiti|stamp-seal|cylinder-seal)\b',
                            'materials': r'\b(?:terracotta|terra cotta|steatite|faience|clay|copper|ivory|bone|stone|bronze|ceramic)\b',
                            'context': r'\b(?:Trench\s*#?\s*\d+|[Mm]ound\s+[ABC]|[Pp]eriod\s+[IVX0-9A-C]+|[Ll]ayer\s+[IVX0-9A-C]+|[Ss]tratum\s+[IVX0-9A-C]+|[Aa]rea\s+[A-Z0-9]+)\b',
                            'references': r'\b(?:[Ff]ig(?:ure)?\.?\s*\d+(?:[a-z]|[:.\-]\d+)?|[Pp]l(?:ate)?\.?\s*[IVX\d]+(?:[:.\-]\d+)?|[Tt]able\s*\d+)\b',
                            'years': r'\b(?:19\d\d|20[012]\d)(?:[\-–]\d{2,4})?\b',
                            'object_counts': r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred)\s+(?:(?:inscribed|Harappan|Indus|steatite|terracotta|faience|clay|square|rectangular|copper|ivory|bone|miniature|intact|broken|complete|stone|seal)\s+){0,4}(?:seals?|sealings?|tablets?|rods?|graffiti|sherds?)\b'
                        }
                        for label, pat in patterns.items():
                            vals = list(dict.fromkeys(re.findall(pat, chunk)))
                            if vals:
                                fields[label] = vals
                        fields['eligibility_terms'] = bool(re.search(r'\b(?:inscri\w*|signs?|characters?|letters?|legend)\b', chunk, re.I))
                        fields['uncertainty_terms'] = bool(re.search(r'\b(?:perhaps|possibly|probably|resembling|uncertain)\b', chunk, re.I))
                        fields['negation_terms'] = bool(re.search(r'\b(?:no|not|without|uninscribed)\b', chunk, re.I))
                        if len(fields) > 4:
                            print(json.dumps({'source_id': sid, 'pdf_page': n, **fields}))
                else:
                    for m in re.finditer(r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred)\s+(?:(?:inscribed|Harappan|Indus|steatite|terracotta|faience|clay|square|rectangular|copper|ivory|bone|miniature|intact|broken|complete|stone|seal)\s+){0,4}(?:seals?|sealings?|tablets?|rods?|graffiti|sherds?)\b', text, re.I):
                        val = m.group()
                        if not re.search(r'\bsigns?\b', val, re.I):
                            print(json.dumps({'source_id': sid, 'pdf_page': n, 'count_phrase': val, 'offset': m.start()}))


if __name__ == '__main__':
    main()
