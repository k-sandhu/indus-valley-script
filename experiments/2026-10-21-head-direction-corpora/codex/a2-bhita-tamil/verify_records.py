"""Validate local A2 transcriptions and write counts without source text.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/verify_records.py --root .
The optional --freeze-reread flag saves first-pass files and compares the separate
image observations. This flag must run once before any reread corrections.
"""
import argparse
import collections
import hashlib
import json
import random
import re
import shutil
import struct
import subprocess
from pathlib import Path

PACKAGE = Path('experiments/2026-10-21-head-direction-corpora')
RAW = Path('data/raw/2026-10-21-head-direction-corpora')
SOURCES = ['asi-ar-1909-10', 'asi-ar-1911-12', 'mahadevan-2003']
FIELDS = 'source entry sub_entry page_printed page_pdf plates object_text material dimensions object_kind device legend_as_printed legend_lines_as_printed line_division_evidence translation_as_printed doubtful restored illegible_part date_as_printed language_note findspot_as_printed depth_as_printed impressions duplicates cross_references museum uncertain_fields transcriber'.split()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def pages(value):
    return value if isinstance(value, list) else [value]


def present(row):
    return bool(row.get('legend_as_printed') or row.get('legend_present') or row.get('illegible_part') or row.get('stated_line_count'))


def summarize(rows):
    uncertain = collections.Counter()
    languages = collections.Counter()
    for row in rows:
        for item in row['uncertain_fields']:
            uncertain[item['field']] += 1
        if present(row):
            languages[row.get('language') or 'not individually stated'] += 1
    return {
        'entries': len(rows),
        'entries_with_a_legend': sum(present(r) for r in rows),
        'entries_with_transcribed_legend': sum(bool(r.get('legend_as_printed')) for r in rows),
        'with_stated_line_division': sum(bool(r.get('legend_lines_as_printed') or r.get('stated_line_count')) for r in rows),
        'with_translation': sum(bool(r['translation_as_printed']) for r in rows),
        'with_site': sum(bool(r.get('site')) for r in rows),
        'with_findspot': sum(bool(r['findspot_as_printed']) and 'unknown' not in r['findspot_as_printed'].lower() for r in rows),
        'with_depth_or_level': sum(bool(r['depth_as_printed'] or r.get('stratum')) for r in rows),
        'with_plate_or_figure_reference': sum(bool(r['plates'] or r.get('figure')) for r in rows),
        'doubtful': sum(bool(r['doubtful']) for r in rows),
        'restored': sum(bool(r['restored']) for r in rows),
        'partly_illegible': sum(bool(r['illegible_part']) for r in rows),
        'doubtful_restored_or_partly_illegible': sum(bool(r['doubtful'] or r['restored'] or r['illegible_part']) for r in rows),
        'legends_by_language': dict(sorted(languages.items())),
        'uncertain_fields_by_field_name': dict(sorted(uncertain.items())),
        'catalogue_pdf_pages': sorted({p for r in rows for p in pages(r['page_pdf'])}),
        'entries_legend_corrected_from_ocr_draft': sum(bool(r.get('ocr_legend_corrected')) and bool(r.get('legend_as_printed')) for r in rows),
        'object_kinds': dict(sorted(collections.Counter(r.get('object_kind') or 'unresolved' for r in rows).items())),
    }


def compare_reread(root, rows):
    scratch = root / RAW / 'codex-a2'
    for source in SOURCES[1:]:
        dest = scratch / (source + '.first-pass.jsonl')
        if dest.exists():
            raise RuntimeError('First pass already frozen; omit --freeze-reread.')
        shutil.copyfile(root / RAW / 'transcriptions' / (source + '.jsonl'), dest)
    selection = random.Random('a2-check').sample(rows, 10)
    observed = json.loads((scratch / 'reread-observations.json').read_text(encoding='utf-8'))
    key = lambda r: (r['source'], r.get('table'), r['entry'])
    assert [key(r) for r in selection] == [key(r) for r in observed]
    reports = []
    for first, second in zip(selection, observed):
        different = [f for f in second if f not in ('source', 'table', 'entry') and first.get(f) != second[f]]
        reports.append({'source': first['source'], 'table': first.get('table'), 'entry': first['entry'],
                        'fields_checked': [f for f in second if f not in ('source', 'table', 'entry')],
                        'differing_fields': different,
                        'first_values': {f: first.get(f) for f in different},
                        'second_values': {f: second[f] for f in different}})
    dump(scratch / 'reread-comparison.json', {'seed': 'a2-check', 'records': reports})
    print(json.dumps([{'source': r['source'], 'table': r['table'], 'entry': r['entry'], 'differing_fields': r['differing_fields']} for r in reports]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--freeze-reread', action='store_true')
    args = ap.parse_args()
    root = args.root.resolve()
    out = root / PACKAGE / 'codex/a2-bhita-tamil'
    all_rows = []
    counts = {'sources': {}, 'definitions': {
        'entries': 'Numbered catalogue rows; grouped specimens and impressions remain grouped.',
        'entries_with_a_legend': 'Includes illegible or cross-referred legends without a printed reading.',
        'with_stated_line_division': 'Includes a stated line count without a transliterated text; counts bilingual textual rows when explicitly stated.',
        'with_findspot': 'Specific location or deposit statement; an unknown location is excluded. Site-only metadata is separate.',
        'legends_by_language': 'Catalogue-row counts; multilingual rows have their own category. General edition statements remain separate from individual identifications.',
        'entries_legend_corrected_from_ocr_draft': 'Complete image-checked NFC legend is absent from the complete OCR after whitespace removal. Punctuation and diacritic differences count; semantic error is not implied. Fields other than the legend are excluded.',
        'pages_read': 'Unique PDF pages inspected, including navigation, plates and blank leaves; a cropped figure page counts once.',
    }}
    problems = []
    images_checked = 0
    manifests = {}
    for source in SOURCES:
        folder = root / RAW / ('pages-' + source.replace('ar-', ''))
        manifests[source] = {}
        for path in folder.glob('*-manifest.json'):
            data = json.loads(path.read_text(encoding='utf-8'))
            manifests[source][path.stem.removesuffix('-manifest')] = data
            assert data['dpi'] >= 300
            assert (root / data['pdf']).is_file()
            for p, page in data['pages'].items():
                assert (root / page['image']).is_file(), page['image']
                with (root / page['image']).open('rb') as image_file:
                    header = image_file.read(24)
                assert header[:8] == b'\x89PNG\r\n\x1a\n'
                width, height = struct.unpack('>II', header[16:24])
                expected_width = page['width_points'] * data['dpi'] / 72
                expected_height = page['height_points'] * data['dpi'] / 72
                assert abs(width - expected_width) <= 1 and abs(height - expected_height) <= 1, page['image']
                images_checked += 1
        rows = [] if source == SOURCES[0] else read_rows(root / RAW / 'transcriptions' / (source + '.jsonl'))
        all_rows.extend(rows)
        primary = manifests[source]['primary']
        count = summarize(rows)
        count['pages_read'] = len(primary['pages'])
        count['pdf_pages_read'] = sorted(map(int, primary['pages']))
        count['scan_page_count'] = primary['pdf_page_count']
        if 'alternate' in manifests[source]:
            count['alternate_pdf_pages_read'] = sorted(map(int, manifests[source]['alternate']['pages']))
            count['pages_read'] += len(manifests[source]['alternate']['pages'])
        counts['sources'][source] = count
        for row in rows:
            identity = (source, row.get('table'), row['entry'])
            missing = set(FIELDS) - row.keys()
            if missing:
                problems.append({'identity': identity, 'missing_fields': sorted(missing)})
            if not (root / row['source_pdf']).is_file():
                problems.append({'identity': identity, 'source_pdf_missing': True})
            for p in pages(row['page_pdf']):
                if not isinstance(p, int) or not 1 <= p <= primary['pdf_page_count'] or str(p) not in primary['pages']:
                    problems.append({'identity': identity, 'invalid_page_pdf': p})
            if row.get('device') and len(row['device'].split()) > 15:
                problems.append({'identity': identity, 'device_word_count': len(row['device'].split())})
        groups = {t: [r for r in rows if r.get('table') == t] for t in sorted({r.get('table') for r in rows}, key=lambda v: v or '')}
        for t, rs in groups.items():
            sequence = [r['entry'] for r in rs]
            if sequence != list(range(1, len(rs) + 1)):
                problems.append({'source': source, 'table': t, 'sequence_gap': True})
        if source == 'mahadevan-2003':
            count['tables'] = {t: summarize(rs) for t, rs in groups.items()}
            associated_pages = {
                '1.6': [94, 95, 101, 106, 107, 244, 280, 281],
                '1.7': [94, 95, 102, 103, 108, 252, 280],
                '1.8': [94, 95, 102, 103, 109, 110, 111, 198, 280, 281],
            }
            for table, table_count in count['tables'].items():
                table_count['pdf_pages_read'] = associated_pages[table]
                table_count['pages_read'] = len(associated_pages[table])
    if args.freeze_reread:
        compare_reread(root, all_rows)
    checks = []
    acq = root / PACKAGE / 'acquisition'
    for source in SOURCES:
        for path in sorted(acq.glob(source + '-*.json')):
            record = json.loads(path.read_text(encoding='utf-8'))
            target = root / record['local_path']
            sha256 = hashlib.file_digest(target.open('rb'), 'sha256').hexdigest()
            sha1 = hashlib.file_digest(target.open('rb'), 'sha1').hexdigest()
            size = target.stat().st_size
            okay = sha256 == record['sha256'] and size == record['bytes'] and sha1 == record['sha1']
            if record.get('expected_sha1'):
                okay &= sha1 == record['expected_sha1'] and size == record['expected_bytes']
            checks.append({'record': path.relative_to(root).as_posix(), 'bytes': size,
                           'supplied_pin': bool(record.get('expected_sha1')), 'passed': okay})
            if not okay:
                problems.append({'acquisition': path.name, 'hash_or_size_mismatch': True})
    findspots = read_rows(root / RAW / 'transcriptions/asi-ar-1911-12.findspots.jsonl')
    for row in findspots:
        assert row['page_pdf'] == 121
        assert all(isinstance(n, int) and 1 <= n <= 120 for n in row['entries'])
    assert [r['row'] for r in findspots] == list(range(1, len(findspots) + 1))
    counts['sources']['asi-ar-1911-12']['findspot_index_rows'] = len(findspots)
    dump(out / 'transcription-counts.json', counts)
    dump(out / 'verification.json', {'acquisitions': checks, 'jsonl_rows': len(all_rows), 'findspot_index_rows': len(findspots), 'page_images_checked_for_300_dpi_pixel_dimensions': images_checked, 'problems': problems})
    print(json.dumps({'entries': {s: c['entries'] for s, c in counts['sources'].items()}, 'problems': problems}, ensure_ascii=False))


if __name__ == '__main__':
    main()
