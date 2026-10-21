"""Expand local image-reading annotations into the transcription brief's fields.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/build_records.py --annotations DIR --output DIR --acquisitions DIR
Annotation JSON files contain defaults and records. All source-derived content stays local.
"""
import argparse
import copy
import json
import unicodedata
from pathlib import Path

FIELDS = 'source entry sub_entry page_printed page_pdf plates object_text material dimensions object_kind device legend_as_printed legend_lines_as_printed line_division_evidence translation_as_printed doubtful restored illegible_part date_as_printed language_note findspot_as_printed depth_as_printed impressions duplicates cross_references museum uncertain_fields transcriber'.split()
ALIASES = dict(e='entry', p='page_printed', q='page_pdf', obj='object_text', mat='material', dim='dimensions', kind='object_kind', dev='device', leg='legend_as_printed', lines='legend_lines_as_printed', evidence='line_division_evidence', tr='translation_as_printed', date='date_as_printed', lang='language_note', fs='findspot_as_printed', depth='depth_as_printed', refs='cross_references', u='uncertain_fields')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--annotations', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--acquisitions', type=Path, required=True)
    args = ap.parse_args()
    compress = lambda text: ''.join(unicodedata.normalize('NFC', text).split())
    ocr = {}
    for record_path in args.acquisitions.glob('*-primary-ocr.json'):
        metadata = json.loads(record_path.read_text(encoding='utf-8'))
        if metadata['source_id'] in ('asi-ar-1911-12', 'mahadevan-2003'):
            ocr[metadata['source_id']] = compress(Path(metadata['local_path']).read_text(encoding='utf-8'))
    sources = {}
    for path in sorted(args.annotations.glob('*.annotations.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        for item in data['records']:
            row = {field: None for field in FIELDS}
            row.update(plates=[], doubtful=False, restored=False, illegible_part=False, duplicates=[], cross_references=[], uncertain_fields=[], transcriber={'by': 'GPT-6.1-Sol, Codex tool harness', 'method': 'ocr-checked-against-image'})
            row.update(copy.deepcopy(data.get('defaults', {})))
            row.update({ALIASES.get(k, k): v for k, v in item.items()})
            if row['source'] == 'asi-ar-1911-12' and row['language_note'] is None:
                row['language_note'] = 'General statement p.46: pre-Gupta legends are Prakrit or mixed Sanskrit; the remaining legends Sanskrit. No individual assignment made here.'
            if row['legend_lines_as_printed'] is not None and row['line_division_evidence'] is None:
                row['line_division_evidence'] = 'Edition prints separately numbered lines.'
            if row['line_division_evidence'] is None:
                row['line_division_evidence'] = 'No line division given in the printed description.'
            legend = row.get('legend_as_printed')
            if row['source'] in ocr:
                row['ocr_legend_corrected'] = bool(legend) and compress(legend) not in ocr[row['source']]
                row['ocr_comparison_method'] = 'Complete NFC legend, whitespace removed, searched in complete OCR draft; punctuation and diacritics retained.'
            sources.setdefault(row['source'], []).append(row)
    args.output.mkdir(parents=True, exist_ok=True)
    for source, rows in sources.items():
        rows.sort(key=lambda r: (r.get('table') or '', r['entry']))
        target = args.output / (source + '.jsonl')
        target.write_text(''.join(unicodedata.normalize('NFC', json.dumps(row, ensure_ascii=False)) + '\n' for row in rows), encoding='utf-8')
        print(source, len(rows))


if __name__ == '__main__':
    main()
