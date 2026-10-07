"""Scan the active package files for byte-order marks, invalid or damaged characters,
line endings and words fused to numbers (for example "about65%"). Read-only on the
package; writes only review-2/scan-results.json.

Active files exclude first-pass/, review/, review-2/ and the first review (REVIEW.md).
The damage markers are built with chr() so that this file itself passes the package's
encoding check.
"""
import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
SKIP_DIRS = {'first-pass', 'review', 'review-2', '__pycache__'}
SKIP_NAMES = {'REVIEW.md', 'REVIEW-2.md'}
REPLACEMENT = chr(0xfffd)
MOJIBAKE = [chr(0xe2) + chr(0x20ac), chr(0xc3) + chr(0xa9), chr(0xc3) + chr(0xa8),
            chr(0xc2) + chr(0xa0), chr(0xef) + chr(0xbf) + chr(0xbd)]
LOST_CHAR = re.compile(r'\w' + re.escape(chr(63)) + r'\w')
WORD_THEN_NUMBER = re.compile(r'\b[A-Za-z]*[a-z]{2,}\d[\d.,\-]*[A-Za-z%]*')
NUMBER_THEN_WORD = re.compile(r'\d(?!(?:st|nd|rd|th)\b)[A-Za-z]{2,}\b')
LOCATOR_WORDS = {'printed', 'paragraph', 'section', 'proposal', 'principle', 'lines', 'slides', 'slide',
                 'page', 'footnote', 'image', 'pdf', 'chapter', 'scan', 'appendix'}
SKIP_KEYS = {'id', 'sha256', 'witness_sha256', 'url', 'witness_path', 'acquisition_log', 'path', 'final_url',
             'source_id', 'old_source_id', 'replacement_source_id', 'source_ids', 'repository_links', 'extraction_path'}


def strings_in(value, key=''):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from strings_in(v, k)
    elif isinstance(value, list):
        for v in value:
            yield from strings_in(v, key)
    elif isinstance(value, str) and key not in SKIP_KEYS:
        yield value


def run_ons(text):
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\]\([^)]*\)', ']', text)
    text = re.sub(r'`[^`]*`', '', text)
    found = []
    for match in WORD_THEN_NUMBER.finditer(text):
        token = match.group(0)
        lead = re.match(r'[A-Za-z]+', token).group(0).lower()
        found.append(('locator' if lead in LOCATOR_WORDS else 'prose', token))
    for match in NUMBER_THEN_WORD.finditer(text):
        found.append(('prose', match.group(0)))
    return found


def main():
    files = []
    for path in sorted(PACKAGE.rglob('*')):
        rel = path.relative_to(PACKAGE)
        if not path.is_file() or rel.parts[0] in SKIP_DIRS or path.name in SKIP_NAMES:
            continue
        files.append(path)
    report, totals = [], collections.Counter()
    for path in files:
        data = path.read_bytes()
        bom = data.startswith(b'\xef\xbb\xbf')
        try:
            text, valid = data.decode('utf-8'), True
        except UnicodeDecodeError:
            text, valid = data.decode('utf-8', errors='replace'), False
        crlf = data.count(b'\r\n')
        lf = data.count(b'\n') - crlf
        entry = dict(file=path.relative_to(PACKAGE).as_posix(), bom=bom, valid_utf8=valid,
                     replacement_chars=text.count(REPLACEMENT),
                     mojibake_sequences=sum(text.count(m) for m in MOJIBAKE),
                     letter_question_letter=len(LOST_CHAR.findall(text)),
                     line_endings='CRLF' if crlf and not lf else 'LF' if lf and not crlf else 'mixed' if crlf else 'none',
                     non_ascii=dict(collections.Counter(c for c in text if ord(c) > 127)))
        if path.suffix == '.md':
            fused = run_ons(text)
        elif path.suffix == '.json':
            fused = [item for s in strings_in(json.loads(text)) for item in run_ons(s)]
        else:
            fused = []
        entry['fused_prose'] = sum(1 for kind, _ in fused if kind == 'prose')
        entry['fused_locator'] = sum(1 for kind, _ in fused if kind == 'locator')
        entry['fused_prose_examples'] = [t for kind, t in fused if kind == 'prose'][:6]
        report.append(entry)
        totals['files'] += 1
        totals['bom'] += bom
        totals['invalid_utf8'] += (not valid)
        totals['replacement_chars'] += entry['replacement_chars']
        totals['mojibake_sequences'] += entry['mojibake_sequences']
        totals['letter_question_letter'] += entry['letter_question_letter']
        totals['fused_prose'] += entry['fused_prose']
        totals['fused_locator'] += entry['fused_locator']
        totals['line_endings_' + entry['line_endings']] += 1
    result = dict(scope='active package files; first-pass/, review/, review-2/ and the first review are excluded',
                  totals=dict(totals), files=report)
    with open(HERE / 'scan-results.json', 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(totals)))
    for e in report:
        if e['fused_prose']:
            print(e['file'], e['fused_prose'], e['fused_prose_examples'])


if __name__ == '__main__':
    main()
