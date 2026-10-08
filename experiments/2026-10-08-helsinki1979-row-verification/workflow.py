"""Model-independent packet/return contract. All writes stay in package N."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-08-helsinki1979-row-verification'
M = ROOT / 'experiments/2026-10-07-helsinki1979-digitization'
V2 = M / 'repair/2026-10-07-v2'
EDITION = 'Koskenniemi-Parpola-1979'
ATTRIBUTION = ('Kimmo Koskenniemi and Asko Parpola, Corpus of Texts in the Indus Script '
               '(1979), Research Reports 1, University of Helsinki')
sys.dont_write_bytecode = True


def setup():
    tmp = RAW / 'tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
        os.environ[key] = str(tmp)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode()).hexdigest()


def owned(path):
    p = Path(path).resolve()
    if not any(p.is_relative_to(base.resolve()) for base in (HERE, RAW)):
        raise ValueError(f'Write outside owned directories: {p}')
    return p


def write(path, value):
    p = owned(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def write_text(path, value):
    p = owned(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value)


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def now():
    return datetime.now(timezone.utc).isoformat()


def load_module(name, path, redirect_pipeline=False):
    """No bytecode or scratch-directory writes to M. Algorithm bytes unchanged."""
    setup()
    module = types.ModuleType(name)
    module.__file__ = str(path)
    source = Path(path).read_text(encoding='utf-8')
    if redirect_pipeline:
        needle = "RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'"
        if source.count(needle) != 1:
            raise ValueError('Pipeline scratch-path adaptation no longer matches')
        source = source.replace(needle, "RAW = ROOT / 'data/raw/2026-10-08-helsinki1979-row-verification'")
    sys.modules[name] = module
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


def evaluator():
    return load_module('helsinki_n_evaluator', M / 'evaluate.py')


def packet_hash(packet):
    return digest({k: v for k, v in packet.items() if k != 'packet_sha256'})


def check_packet(path):
    p = read(path)
    if packet_hash(p) != p['packet_sha256']:
        raise ValueError('Packet metadata hash mismatch')
    base = Path(path).parent.resolve()
    role_root = base.parent
    for asset in p['assets']:
        file = (base / asset['path']).resolve()
        if not file.is_relative_to(role_root):
            raise ValueError('Asset escapes role delivery root')
        if sha(file) != asset['sha256']:
            raise ValueError(f'Asset hash mismatch: {asset["path"]}')
    return p


def template(packet):
    return dict(schema_version=1, evidence_status='Proposed', batch_id=packet['batch_id'], role=packet['role'],
                packet_sha256=packet['packet_sha256'],
                reader=dict(provider=None, model=None, model_version=None, run_id=None,
                            independence_attestation=None),
                started_utc=None, finished_utc=None, elapsed_seconds=None,
                usage=dict(input_tokens=None, cached_input_tokens=None, output_tokens=None,
                           billed_usd=None, unavailable_reason='Coordinator must supply actual usage'),
                columns=[dict(**packet['assigned_column'], numbered_occurrences=None,
                              continuation_lines=None, coverage_complete=False,
                              observed_page_columns=None, unassigned_columns=[],
                              source_observations=None)],
                rows=[dict(item_id=r['item_id'], sample_index=r['sample_index'],
                           pdf_page=r['pdf_page'], pdf_column=r['pdf_column'],
                           source_row_ordinal=None, source_y_pdf=None,
                           printed_inscription_id=None, classification_literal=None,
                           drawn_unit_count=None, crop_correct=None, valid_printed_target=True,
                           units=[], blank_gaps=[], continuation_y_pdf=[], continuation_rows=[],
                           unresolved_fields=[], unresolved_boundary=None,
                           source_observations=None) for r in packet['items']])


def finite_nonnegative(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate_return(data, packet, codes):
    errors = []
    def need(condition, message):
        if not condition:
            errors.append(message)
    need(data.get('schema_version') == 1, 'schema_version must be 1')
    need(data.get('evidence_status') in ('Frozen evaluation', 'Synthetic'), 'evidence_status must identify actual or synthetic readings')
    for field in ('batch_id', 'role', 'packet_sha256'):
        need(data.get(field) == packet.get(field), f'{field} does not match packet')
    identity = data.get('reader', {})
    for field in ('provider', 'model', 'run_id', 'independence_attestation'):
        need(isinstance(identity.get(field), str) and bool(identity[field].strip()), f'missing reader.{field}')
    try:
        start = datetime.fromisoformat(data['started_utc'].replace('Z', '+00:00'))
        finish = datetime.fromisoformat(data['finished_utc'].replace('Z', '+00:00'))
        need(start.tzinfo is not None and finish.tzinfo is not None and finish >= start, 'invalid UTC task interval')
    except (ValueError, TypeError, KeyError, AttributeError):
        errors.append('missing/invalid UTC start or finish')
    need(finite_nonnegative(data.get('elapsed_seconds')), 'elapsed_seconds must be finite and nonnegative')
    usage = data.get('usage', {})
    for field in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'billed_usd'):
        value = usage.get(field)
        need(value is None or finite_nonnegative(value), f'invalid usage.{field}')
        if value is not None and field.endswith('tokens'):
            need(type(value) is int, f'{field} must be integer')
    if usage.get('cached_input_tokens') is not None and usage.get('input_tokens') is not None:
        need(usage['cached_input_tokens'] <= usage['input_tokens'], 'cached tokens exceed total input')
    if any(usage.get(k) is None for k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'billed_usd')):
        need(bool(usage.get('unavailable_reason')), 'missing usage requires unavailable_reason')
    expected = {r['item_id']: r for r in packet['items']}
    rows = data.get('rows', [])
    if not isinstance(rows, list):
        return errors + ['rows must be an array']
    ids = [r.get('item_id') for r in rows if isinstance(r, dict)]
    need(len(ids) == len(rows) and len(set(ids)) == len(ids), 'duplicate or malformed item IDs')
    need(set(expected).issubset(ids), 'missing assigned items')
    assigned = packet['assigned_column']
    sample_indices = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = row.get('item_id', '')
        loc = expected.get(item)
        extra = re.fullmatch(r'extra:' + re.escape(packet['batch_id']) + r':([1-9]\d*)', str(item))
        need(loc is not None or extra is not None, f'{item}: unknown item')
        if extra:
            ordinal = int(extra[1])
            need(row.get('source_row_ordinal') == ordinal and row.get('sample_index') == 1000000 + ordinal,
                 f'{item}: extra ID/index/ordinal inconsistent')
        need(type(row.get('sample_index')) is int, f'{item}: missing integer sample_index')
        sample_indices.append(row.get('sample_index'))
        if loc:
            for field in ('sample_index', 'pdf_page', 'pdf_column'):
                need(row.get(field) == loc[field], f'{item}: incorrect {field}')
        elif extra:
            for field in ('pdf_page', 'pdf_column'):
                need(row.get(field) == assigned[field], f'{item}: extra from different column')
        page = packet['page_dimensions'].get(str(row.get('pdf_page')))
        y = row.get('source_y_pdf')
        need(page is not None and finite_nonnegative(y) and y <= page[1], f'{item}: invalid source y')
        if loc and finite_nonnegative(y):
            need(abs(y - loc['target_y_pdf']) <= 9, f'{item}: source position misses locator by >9 points')
        need(type(row.get('valid_printed_target')) is bool, f'{item}: valid_printed_target missing')
        ordinal = row.get('source_row_ordinal')
        need(type(ordinal) is int and ordinal >= 1 or row.get('valid_printed_target') is False and ordinal is None,
             f'{item}: invalid source ordinal')
        number = row.get('printed_inscription_id')
        need(number is None or isinstance(number, str) and re.fullmatch(r'\d+[A-Za-z]*', number), f'{item}: malformed number')
        literal = row.get('classification_literal')
        need(literal is None or isinstance(literal, str) and re.fullmatch(r'[0-9 ]{5}', literal), f'{item}: classification must have five positions')
        units = row.get('units')
        need(isinstance(units, list), f'{item}: units must be array')
        if not isinstance(units, list):
            continue
        count = row.get('drawn_unit_count')
        need(type(count) is int and count >= 0 and count == len(units), f'{item}: unit count mismatch')
        need(type(row.get('crop_correct')) is bool, f'{item}: crop_correct missing')
        for pos, unit in enumerate(units):
            if not isinstance(unit, dict):
                errors.append(f'{item}: malformed unit {pos}')
                continue
            for field in ('strict_candidate_codes', 'shape_only_candidate_codes'):
                if field == 'shape_only_candidate_codes' and field not in unit:
                    continue
                values = unit.get(field)
                need(isinstance(values, list) and all(type(c) is int and c in codes for c in values)
                     and len(values) == len(set(values)), f'{item}: invalid {field} at unit {pos}')
            need(unit.get('unit_kind') in ('sign', 'hatched_span', 'loss_rectangle', 'unresolved'), f'{item}: invalid unit kind {pos}')
            need(type(unit.get('underline_dashes')) is bool, f'{item}: missing underline status {pos}')
            if not unit.get('strict_candidate_codes'):
                need(bool(unit.get('uncertainty_reason') or unit.get('note')), f'{item}: empty candidates need reason')
        need(isinstance(row.get('unresolved_fields'), list), f'{item}: unresolved_fields missing')
        if number is None or literal is None:
            need(bool(row.get('unresolved_fields')), f'{item}: null field needs unresolved_fields reason')
        need(isinstance(row.get('source_observations'), str) and bool(row['source_observations'].strip()), f'{item}: source observations missing')
        need(isinstance(row.get('blank_gaps'), list), f'{item}: blank_gaps missing')
        cont = row.get('continuation_y_pdf')
        need(isinstance(cont, list) and all(finite_nonnegative(v) and page and v <= page[1] for v in cont), f'{item}: invalid continuation coordinates')
        lines = row.get('continuation_rows', [])
        need(isinstance(lines, list) and isinstance(cont, list) and len(lines) == len(cont), f'{item}: continuation payload/count mismatch')
        if isinstance(lines, list) and isinstance(cont, list):
            for li, line in enumerate(lines):
                if not isinstance(line, dict):
                    errors.append(f'{item}: malformed continuation line')
                    continue
                need(line.get('source_y_pdf') == cont[li], f'{item}: continuation y mismatch')
                lu = line.get('units', [])
                need(isinstance(lu, list) and line.get('drawn_unit_count') == len(lu), f'{item}: continuation count mismatch')
                need(bool(line.get('source_observations')) and isinstance(line.get('unresolved_fields'), list), f'{item}: continuation observations missing')
                for unit in lu:
                    cs = unit.get('strict_candidate_codes') if isinstance(unit, dict) else None
                    need(isinstance(cs, list) and all(type(c) is int and c in codes for c in cs)
                         and len(cs) == len(set(cs)), f'{item}: invalid continuation codes')
                    if isinstance(unit, dict):
                        need(unit.get('unit_kind') in ('sign', 'hatched_span', 'loss_rectangle', 'unresolved')
                             and type(unit.get('underline_dashes')) is bool, f'{item}: invalid continuation unit fields')
                        if not cs:
                            need(bool(unit.get('uncertainty_reason') or unit.get('note')), f'{item}: unresolved continuation needs reason')
    need(len(sample_indices) == len(set(sample_indices)), 'duplicate sample_index')
    if packet['role'] != 'adjudicator' or packet.get('requires_complete_inventory'):
        columns = data.get('columns', [])
        need(isinstance(columns, list) and len(columns) == 1, 'one source column inventory required')
        if isinstance(columns, list) and len(columns) == 1:
            col = columns[0]
            for field in ('pdf_page', 'pdf_column'):
                need(col.get(field) == assigned[field], f'column {field} mismatch')
            for field in ('numbered_occurrences', 'continuation_lines'):
                need(type(col.get(field)) is int and col[field] >= 0, f'column {field} must be nonnegative integer')
            need(type(col.get('observed_page_columns')) is int and col['observed_page_columns'] >= 1,
                 'source page column count required')
            need(isinstance(col.get('unassigned_columns'), list), 'unassigned source columns must be an array')
            need(type(col.get('coverage_complete')) is bool and bool(col.get('source_observations')), 'column coverage observations required')
    if packet['role'] == 'adjudicator':
        for row in rows:
            need(bool(row.get('adjudication_basis')), f'{row.get("item_id")}: adjudication_basis required')
    return errors


def code_universe(packet=None):
    if packet and packet.get('chart_code_universe'):
        return set(packet['chart_code_universe'])
    return {c for row in read(M / 'chart-snapshot.json')['rows'] for c in [row['code']] + row['alternatives']}


def canonical(row):
    return dict(printed_inscription_id=row.get('printed_inscription_id'),
                classification_literal=row.get('classification_literal'),
                drawn_unit_count=row.get('drawn_unit_count'), crop_correct=row.get('crop_correct'),
                valid_printed_target=row.get('valid_printed_target'),
                source_row_ordinal=row.get('source_row_ordinal'),
                units=[dict(strict_candidate_codes=sorted(u.get('strict_candidate_codes', [])),
                            unit_kind=u.get('unit_kind'), underline_dashes=u.get('underline_dashes'))
                       for u in row.get('units', [])],
                blank_gaps=row.get('blank_gaps', []),
                continuation_rows=[dict(units=[dict(strict_candidate_codes=sorted(u.get('strict_candidate_codes', [])),
                                      unit_kind=u.get('unit_kind'), underline_dashes=u.get('underline_dashes'))
                                      for u in line.get('units', [])], unresolved_fields=line.get('unresolved_fields', []))
                                   for line in row.get('continuation_rows', [])],
                unresolved_fields=row.get('unresolved_fields', []),
                unresolved_boundary=row.get('unresolved_boundary'))


def differences(a, b):
    aa, bb = canonical(a), canonical(b)
    fields = [field for field in aa if aa[field] != bb[field]]
    for field in ('source_y_pdf',):
        av, bv = a.get(field), b.get(field)
        if av is None or bv is None or abs(av - bv) > 3:
            fields.append(field)
    ca, cb = a.get('continuation_y_pdf', []), b.get('continuation_y_pdf', [])
    if len(ca) != len(cb) or any(abs(x - y) > 3 for x, y in zip(ca, cb)):
        fields.append('continuation_y_pdf')
    return fields


def resolved(row):
    return bool(row and row.get('valid_printed_target') is True and
                row.get('printed_inscription_id') is not None and row.get('classification_literal') is not None and
                row.get('drawn_unit_count') is not None and row.get('source_row_ordinal') is not None and
                not row.get('unresolved_fields') and not row.get('unresolved_boundary') and
                all(len(u.get('strict_candidate_codes', [])) == 1 and u.get('unit_kind') != 'unresolved'
                    for u in row.get('units', []) + [u for line in row.get('continuation_rows', []) for u in line['units']])
                and all(not line.get('unresolved_fields') for line in row.get('continuation_rows', [])))


def inventory_complete(data, private_batch):
    if not data or not data.get('columns'):
        return False
    col = data['columns'][0]
    rows = [r for r in data['rows'] if r['item_id'] not in private_batch['controls'] and r.get('valid_printed_target')]
    ordinals = [r['source_row_ordinal'] for r in rows]
    return (col['coverage_complete'] and sorted(ordinals) == list(range(1, col['numbered_occurrences'] + 1))
            and not col.get('unassigned_columns')
            and col.get('observed_page_columns') == private_batch.get('detected_page_columns', 2)
            and len({round(y, 1) for r in rows for y in r['continuation_y_pdf']}) == col['continuation_lines'])


def as_prediction(row):
    return dict(sample_index=row['sample_index'], occurrence_key=row['item_id'], pdf_page=row['pdf_page'],
                inscription_number=row.get('printed_inscription_id'), classification_code=row.get('classification_literal'),
                units=[dict(alternatives=[dict(codes=u['strict_candidate_codes'])], confidence=None)
                       for u in row['units']])


def ledger_row(row, provenance):
    tokens, auxiliary = [], []
    for i, unit in enumerate(row['units']):
        record = dict(source_unit_index=i, strict_candidate_codes=unit['strict_candidate_codes'],
                      unit_kind=unit['unit_kind'], underline_dashes=unit['underline_dashes'])
        (tokens if unit['unit_kind'] == 'sign' else auxiliary).append(record)
    for line in row.get('continuation_rows', []):
        for i, unit in enumerate(line['units']):
            record = dict(source_unit_index=i, source_line_y_pdf=line['source_y_pdf'],
                          strict_candidate_codes=unit['strict_candidate_codes'], unit_kind=unit['unit_kind'],
                          underline_dashes=unit['underline_dashes'])
            (tokens if unit['unit_kind'] == 'sign' else auxiliary).append(record)
    segment = f'helsinki1979:pdf{row["pdf_page"]}:c{row["pdf_column"]}:source-r{row["source_row_ordinal"]}'
    return dict(edition_id=EDITION, text_number=row['printed_inscription_id'], segment_id=segment,
                inventory='Finnish numeric codes, Koskenniemi-Parpola', inventory_version='1979',
                source_page=row['pdf_page'], glyph_tokens=tokens, auxiliary_markers=auxiliary,
                classification_literal=row['classification_literal'], order='visual_left_to_right',
                continuation_rows=row.get('continuation_rows', []),
                boundary_status='physical_line_side_boundaries_unresolved',
                digitization_version='package-N-two-reader-v1', synthetic=provenance.get('evidence_status') == 'Synthetic',
                review_status='synthetic_fixture' if provenance.get('evidence_status') == 'Synthetic' else 'source_row_verified_requires_reviewed_concordance',
                rights=dict(license='CC-BY-4.0', source_url='http://hdl.handle.net/10138/342677',
                            attribution=ATTRIBUTION, modifications='Raster crops and independent numerical source verification'),
                provenance=provenance)
