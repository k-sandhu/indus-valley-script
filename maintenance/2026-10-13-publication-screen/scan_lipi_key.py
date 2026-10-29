"""Count reproductions of the Lipi sign-to-letter key (xlits.csv) and Lipi readings (glossing.csv).

Added after the first sequence run: the Sanskrit-key tests use the key published in the Lipi repository,
so the key table and Lipi readings are further Lipi content that could be copied into tracked files.
Key pairs count when a code and its exact Lipi letter appear adjacent (code, separator, letter).
Readings count when a Lipi reading form of at least eight characters, or a Lipi translation of at
least three words, appears verbatim. Matched strings are written only to the ignored raw directory.
"""
from pathlib import Path
from collections import Counter
import csv, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-13-publication-screen'
LIPI = ROOT / 'data/lipi'
TEXT = {'.json', '.jsonl', '.csv', '.tsv', '.md', '.html', '.js', '.txt', '.py', '.yml', '.tpl', ''}
PAIR = re.compile(r'(?<![0-9A-Za-z])W?(\d{3})["\']?\s*(?:[:=,|\t]|->|→)\s*["\']?([A-Za-zĀ-ɏḀ-ỿ]{1,4})(?![A-Za-z])')


def main():
    inv = json.loads((RAW / (sys.argv[1] if len(sys.argv) > 1 else 'inventory.json')).read_text(encoding='utf-8'))
    out_name = sys.argv[2] if len(sys.argv) > 2 else 'lipi-key-scan.json'
    key = {}
    with open(LIPI / 'src/assets/data/xlits.csv', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['xlit'].strip() and r['xlit'] not in '.':
                key[r['sign']] = r['xlit']
    forms, translations = set(), set()
    with open(LIPI / 'glossing.csv', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if len(r['form']) >= 8:
                forms.add(r['form'])
            if len((r['translation_lexeme'] or '').split()) >= 3:
                translations.add(r['translation_lexeme'].strip())
    form_re = re.compile(r'(?<![\w-])(' + '|'.join(sorted(map(re.escape, forms), key=len, reverse=True)) + r')(?![\w-])') if forms else None
    results, detail = [], {}
    for f in inv['files']:
        if f['bytes'] is None or Path(f['path']).suffix.lower() not in TEXT:
            continue
        t = (ROOT / f['path']).read_bytes().decode('utf-8', 'replace')
        pairs = Counter((c, x) for c, x in PAIR.findall(t) if key.get(c) == x)
        fm = Counter(form_re.findall(t)) if form_re else Counter()
        tr = Counter(s for s in translations if s in t)
        if len(pairs) >= 5 or fm or tr:
            results.append({'path': f['path'], 'bytes': f['bytes'], 'distinct_key_pairs': len(pairs),
                            'distinct_reading_forms': len(fm), 'distinct_translations': len(tr)})
            detail[f['path']] = {'pairs': [f'{c}={x}' for (c, x), _ in pairs.most_common(20)],
                                 'forms': [s for s, _ in fm.most_common(20)], 'translations': [s for s, _ in tr.most_common(10)]}
    out = {'scope': __doc__.strip(), 'key_entries': len(key), 'reading_forms_ge8': len(forms),
           'translations_ge3_words': len(translations),
           'files_scanned': sum(1 for f in inv['files'] if f['bytes'] is not None and Path(f['path']).suffix.lower() in TEXT),
           'files': sorted(results, key=lambda r: -(r['distinct_key_pairs'] + r['distinct_reading_forms'] + r['distinct_translations']))}
    (HERE / out_name).write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    (RAW / out_name.replace('.json', '-matches.json')).write_text(json.dumps(detail, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k not in ('files', 'scope')}, indent=1))
    for r in out['files'][:40]:
        print(r)


if __name__ == '__main__':
    main()
