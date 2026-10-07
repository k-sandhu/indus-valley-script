"""Validate schema, keys, missingness, references, units, intervals and sequence exclusion."""
import argparse
import json
import re
from pathlib import Path
import jsonschema
from common import OWN, ROOT, write

SEQUENCE_KEYS = {'signs_visual_ltr', 'signs_reading_rtl', 'text_code_visual_ltr', 'sign_sequence', 'sequence', 'graphemes', 'tokens', 'token_codes', 'sign_occurrences', 'source_record'}

def sequence_errors(value, location='$'):
    errors = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k.casefold() in SEQUENCE_KEYS:
                errors.append(location + '.' + k + ': prohibited source-payload key')
            errors.extend(sequence_errors(v, location + '.' + k))
    elif isinstance(value, list):
        # Tokens may not be concealed as numeric-code arrays in generic assertion values.
        if value and all(isinstance(v, str) and re.fullmatch(r'(?:P|W)?\d{3}', v) for v in value):
            errors.append(location + ': code-like array')
        for i, v in enumerate(value):
            errors.extend(sequence_errors(v, f'{location}[{i}]'))
    elif isinstance(value, str) and re.fullmatch(r'\+?(?:\d{3}|P\d{3})(?:[- ](?:\d{3}|P\d{3})){2,}\+?', value):
        errors.append(location + ': code-like sequence string')
    return errors

def validate(ledger):
    schema = json.loads((OWN / 'schema.json').read_text(encoding='utf-8'))
    errors = [str(e.json_path) + ': ' + e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(ledger)]
    errors += sequence_errors(ledger)
    maps = {}
    all_ids = set()
    for table, rows in ledger.items():
        if not isinstance(rows, list):
            continue
        ids = [r.get('id') for r in rows]
        if len(ids) != len(set(ids)):
            errors.append(table + ': duplicate identifier')
        if all_ids.intersection(ids):
            errors.append(table + ': identifier reused across tables')
        all_ids.update(ids)
        maps[table] = {r.get('id'): r for r in rows}
    def ref(table, ident, context):
        if ident not in maps[table]:
            errors.append(context + ': broken reference to ' + table + '/' + str(ident))

    def cells(v, context):
        if isinstance(v, dict):
            if set(v) == {'value', 'assertion_ids', 'missing_reason'}:
                if v['value'] is None and not v['missing_reason']:
                    errors.append(context + ': empty value without reason')
                for aid in v['assertion_ids']:
                    ref('assertions', aid, context)
                if v['value'] is not None and not any(maps['assertions'].get(aid, {}).get('value') == v['value'] for aid in v['assertion_ids']):
                    errors.append(context + ': chosen value absent from referenced assertions')
            for k, val in v.items():
                cells(val, context + '.' + k)
        elif isinstance(v, list):
            for i, val in enumerate(v):
                cells(val, f'{context}[{i}]')
    cells(ledger, '$')
    for table, rows in maps.items():
        for ident, row in rows.items():
            if 'object_id' in row:
                ref('objects', row['object_id'], ident)
            if 'source_id' in row:
                ref('sources', row['source_id'], ident)
            if 'assertion_id' in row:
                ref('assertions', row['assertion_id'], ident)
                a = maps['assertions'].get(row['assertion_id'], {})
                if a.get('object_id') != row.get('object_id'):
                    errors.append(ident + ': assertion points to another object')
            if 'rights_id' in row:
                ref('rights', row['rights_id'], ident)
                rights = maps['rights'].get(row['rights_id'], {})
                if rights.get('asset_ref') != ident:
                    errors.append(ident + ': rights record belongs to another asset')
                if rights.get('source_id') != row.get('source_id'):
                    errors.append(ident + ': rights/source mismatch')
            if table == 'transcriptions':
                ref('surfaces', row['surface_id'], ident)
                if maps['surfaces'].get(row['surface_id'], {}).get('object_id') != row['object_id']:
                    errors.append(ident + ': surface belongs to another object')
            if table == 'rights':
                if row['asset_ref'] not in maps['images'] and row['asset_ref'] not in maps['transcriptions']:
                    errors.append(ident + ': rights asset missing')
                if row['status'] == 'explicit-license' and row['license']['value'] is None:
                    errors.append(ident + ': explicit license missing')
            if table == 'sources':
                if row['year'] is None and not row['year_missing_reason']:
                    errors.append(ident + ': missing source year without reason')
            if table == 'correction_overlays':
                for oid in row['object_ids']:
                    ref('objects', oid, ident)
            if table == 'assertions':
                loc = row['locator']
                if loc['page_or_url'] is None and not loc['page_missing_reason']:
                    errors.append(ident + ': missing page without reason')
                if not (ROOT / loc['path']).is_file():
                    errors.append(ident + ': source file does not exist ' + loc['path'])
                if row['field'] == 'calendar_interval':
                    interval = row['value']
                    if not isinstance(interval, dict) or set(interval) != {'bce_oldest', 'bce_youngest'}:
                        errors.append(ident + ': malformed BCE interval')
                    elif not all(isinstance(v, (int, float)) and v > 0 for v in interval.values()) or interval['bce_oldest'] < interval['bce_youngest']:
                        errors.append(ident + ': reversed/nonpositive BCE interval')
            if table == 'measurements':
                if row['value'] <= 0 or row['unit'] not in {'mm', 'cm', 'g', 'kg'}:
                    errors.append(ident + ': invalid measurement')
                if row['dimension'] in {'horizontal', 'vertical', 'thickness', 'dimension_1', 'dimension_2', 'dimension_3'} and row['unit'] not in {'mm', 'cm'}:
                    errors.append(ident + ': dimension requires length unit')
    if len(maps.get('objects', {})) != 200:
        errors.append('Pilot must contain exactly 200 object records')
    if len(maps.get('contexts', {})) != 200:
        errors.append('Pilot requires one context record per object')
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--output')
    ap.add_argument('--scan-dir')
    a = ap.parse_args()
    ledger = json.loads(Path(a.ledger).read_text(encoding='utf-8'))
    errors = validate(ledger)
    scanned = []
    if a.scan_dir:
        for p in sorted(Path(a.scan_dir).rglob('*.json')):
            if p.name == 'schema.json':
                continue
            errors.extend(str(p) + ': ' + e for e in sequence_errors(json.loads(p.read_text(encoding='utf-8'))))
            scanned.append(str(p))
    result = {'status': 'Verified computation' if not errors else 'Failed', 'errors': errors, 'objects': len(ledger['objects']), 'assertions': len(ledger['assertions']), 'scanned_json_files': scanned}
    if a.output:
        p = Path(a.output).resolve()
        if not p.is_relative_to(OWN) or p.exists():
            raise ValueError('Validation output must be a new file in the owned directory')
        write(p, result)
    print(json.dumps(result, ensure_ascii=True))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
