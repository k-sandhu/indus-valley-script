"""Reviewer negative tests for Package L's validator (validate.py).

Each mutation is applied twice: to the full public ledger in memory (baseline: no errors) and to a
two-object slice (baseline: only the two cardinality errors, because the validator insists on exactly 200
objects and 200 contexts). A mutation counts as caught when the validator reports an error that the
unmodified copy does not report.

The sign-sequence tests write throw-away fixture files to a directory under the package's local raw
directory and run the validator's directory scan on them. The fixture strings use sign codes that do not
occur in the Lipi or Mayig exports and carry no corpus content.

Run from the repository root:  python experiments/2026-10-07-object-ledger/review/negative_tests.py
Writes review/negative-tests/slice-control.json, slice-<id>.json for four illustrative defects, and
review/negative-tests-results.json.
"""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-07-object-ledger'
RAW = ROOT / 'data/raw/2026-10-07-object-ledger'
sys.path.insert(0, str(PKG))
from validate import validate, sequence_errors  # noqa: E402

ledger = json.loads((PKG / 'run-2026-10-07-v4/ledger-public.json').read_text(encoding='utf-8'))


def make_slice(full, keep):
    keep = set(keep)
    d = {k: v for k, v in full.items() if not isinstance(v, list)}
    amap = {a['id']: a for a in full['assertions']}
    d['objects'] = [o for o in full['objects'] if o['id'] in keep]
    d['contexts'] = [c for c in full['contexts'] if c['object_id'] in keep]
    for t in ['surfaces', 'transcriptions', 'images', 'identifiers', 'measurements', 'assertions', 'relationships']:
        d[t] = [r for r in full[t] if r['object_id'] in keep]
    d['rights'] = [r for r in full['rights'] if r['asset_ref'] in {x['id'] for x in d['images']} | {x['id'] for x in d['transcriptions']}]
    d['correction_overlays'] = []
    used = {a['source_id'] for a in d['assertions']} | {x['source_id'] for x in d['images']} | {x['source_id'] for x in d['transcriptions']} | {x['source_id'] for x in d['rights']} | {x['source_id'] for x in d['relationships']}
    d['sources'] = [s for s in full['sources'] if s['id'] in used]
    return d


SLICE_IDS = ['OL-0001', 'OL-0045']
slice_ = make_slice(ledger, SLICE_IDS)


def by_id(d, table, ident):
    return next(r for r in d[table] if r['id'] == ident)


def cell(d, table, ident, field):
    return by_id(d, table, ident)['fields'][field]


# ---- mutations: (name, category, description, function)
M = []


def mut(name, category, description):
    def deco(fn):
        M.append((name, category, description, fn))
        return fn
    return deco


@mut('R1_context_points_to_missing_object', 'referential', 'context.object_id set to an identifier that is not in objects')
def _(d):
    by_id(d, 'contexts', 'C-OL-0045')['object_id'] = 'OL-9999'


@mut('R2_identifier_points_to_missing_assertion', 'referential', 'identifier.assertion_id set to a nonexistent assertion')
def _(d):
    d['identifiers'][0]['assertion_id'] = 'A-999999'


@mut('R3_cell_cites_missing_assertion', 'referential', 'object cell lists a nonexistent assertion id')
def _(d):
    cell(d, 'objects', 'OL-0001', 'catalogue_identifier')['assertion_ids'] = ['A-999999']


@mut('R4_transcription_points_to_surface_of_other_object', 'referential', 'transcription.surface_id belongs to a different object')
def _(d):
    t = next(t for t in d['transcriptions'] if t['object_id'] == 'OL-0001')
    t['surface_id'] = next(s['id'] for s in d['surfaces'] if s['object_id'] == 'OL-0045')


@mut('R5_relationship_points_to_missing_source', 'referential', 'relationship.source_id is not in sources')
def _(d):
    d['relationships'][0]['source_id'] = 'no-such-source'


@mut('R6_measurement_row_disagrees_with_its_assertion', 'referential', 'measurements.value changed to 99.0 while its assertion still says 12.5')
def _(d):
    m = next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')
    m['value'] = 99.0


@mut('R7_identifier_value_disagrees_with_its_assertion', 'referential', 'identifiers.value changed while its assertion keeps the original value')
def _(d):
    i = next(i for i in d['identifiers'] if i['object_id'] == 'OL-0001' and i['scheme'] == 'reported_catalogue_reference')
    i['value'] = 'H-9999'


@mut('R8_two_contexts_for_one_object_none_for_another', 'referential', 'second context re-pointed to the first object; counts stay at the expected totals')
def _(d):
    by_id(d, 'contexts', 'C-OL-0045')['object_id'] = 'OL-0001'


@mut('R9_locator_record_does_not_exist_in_source_file', 'referential', 'assertion.locator.record names a record that is not in the cited file; the file path exists')
def _(d):
    a = next(a for a in d['assertions'] if a['object_id'] == 'OL-0045' and a['field'] == 'material')
    a['locator']['record'] = 'record_id=THIS-RECORD-DOES-NOT-EXIST'


@mut('R10_locator_file_missing', 'referential', 'assertion.locator.path names a file that does not exist')
def _(d):
    a = next(a for a in d['assertions'] if a['object_id'] == 'OL-0045' and a['field'] == 'material')
    a['locator']['path'] = 'data/normalized/not-a-file.jsonl'


@mut('R11_relationship_confirmed_without_assertion_support', 'referential', 'candidate relationship relabelled confirmed while its assertion keeps candidate confidence')
def _(d):
    r = d['relationships'][0]
    r['status'] = 'confirmed'
    # status confirmed on a relationship whose backing assertion is candidate-confidence
    a = by_id(d, 'assertions', r['assertion_id'])
    a['confidence'] = 'candidate'


@mut('U1_unit_not_in_enum', 'unit', 'measurements.unit set to m')
def _(d):
    next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')['unit'] = 'm'


@mut('U2_negative_value', 'unit', 'measurements.value set to -1')
def _(d):
    next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')['value'] = -1


@mut('U3_mass_unit_on_length_dimension', 'unit', 'horizontal dimension recorded in g')
def _(d):
    next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')['unit'] = 'g'


@mut('U4_unit_changed_mm_to_cm_row_only', 'unit', 'measurement row says cm for a value that its assertion gives in mm')
def _(d):
    next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')['unit'] = 'cm'


@mut('U5_inches_inside_accepted_cell_and_assertion', 'unit', 'object measurement cell and its assertion both carry unit inch (the measurements table is untouched)')
def _(d):
    c = cell(d, 'objects', 'OL-0001', 'measurement')
    v = {'dimension': 'horizontal', 'value': 12.5, 'unit': 'inch'}
    for aid in c['assertion_ids'][:1]:
        by_id(d, 'assertions', aid)['value'] = v
    c['value'] = v


@mut('U6_implausible_magnitude_12_5_metres', 'unit', 'a seal width of 12500 mm (12.5 m) in the measurement row and assertion')
def _(d):
    m = next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')
    m['value'] = 12500.0
    a = by_id(d, 'assertions', m['assertion_id'])
    a['value'] = {'dimension': 'horizontal', 'value': 12500.0, 'unit': 'mm'}
    c = cell(d, 'objects', 'OL-0001', 'measurement')
    if c['assertion_ids'][0] == m['assertion_id']:
        c['value'] = a['value']


@mut('U7_nan_value', 'unit', 'measurement value NaN')
def _(d):
    next(m for m in d['measurements'] if m['object_id'] == 'OL-0001')['value'] = float('nan')


def cal_assertion(d, oid):
    return next(a for a in d['assertions'] if a['object_id'] == oid and a['field'] == 'calendar_interval')


def set_interval(d, oid, value):
    a = cal_assertion(d, oid)
    a['value'] = value
    ctx = by_id(d, 'contexts', 'C-' + oid)
    c = ctx['fields']['calendar_interval']
    if a['id'] in c['assertion_ids']:
        c['value'] = value


@mut('I1_reversed_interval', 'interval', 'bce_oldest younger than bce_youngest')
def _(d):
    set_interval(d, 'OL-0001', {'bce_oldest': 1900, 'bce_youngest': 2600})


@mut('I2_string_endpoints', 'interval', 'endpoints given as strings')
def _(d):
    set_interval(d, 'OL-0001', {'bce_oldest': '2600', 'bce_youngest': '1900'})


@mut('I3_zero_endpoint', 'interval', 'bce_youngest set to 0')
def _(d):
    set_interval(d, 'OL-0001', {'bce_oldest': 2600, 'bce_youngest': 0})


@mut('I4_extra_key', 'interval', 'interval carries an additional ce key')
def _(d):
    set_interval(d, 'OL-0001', {'bce_oldest': 2600, 'bce_youngest': 1900, 'ce': 0})


@mut('I5_interval_inconsistent_with_period_label', 'interval', 'object labelled late Period 3B receives the Period 3A interval 2600-2450')
def _(d):
    set_interval(d, 'OL-0001', {'bce_oldest': 2600, 'bce_youngest': 2450})


@mut('I6_implausible_interval', 'interval', 'interval 50000-40000 BCE for a Harappa tablet')
def _(d):
    set_interval(d, 'OL-0001', {'bce_oldest': 50000, 'bce_youngest': 40000})


@mut('I7_interval_attributed_to_wrong_source', 'interval', 'museum range assertion re-sourced to the HARP table without a matching table row')
def _(d):
    a = cal_assertion(d, 'OL-0045')
    a['source_id'] = 'harappa2010'


@mut('I8_calendar_interval_on_nonharappa_object_from_harp_mapping', 'interval', 'HARP-method assertion attached to a Mohenjo-daro object')
def _(d):
    a = cal_assertion(d, 'OL-0045')
    a['method'] = 'attributed_period_conversion; not_object_sample_date'
    a['source_id'] = 'harappa2010'


def run_mutations(base, label):
    before = set(validate(base))
    out = {}
    for name, cat, desc, fn in M:
        d = copy.deepcopy(base)
        try:
            fn(d)
        except StopIteration:
            out[name] = {'category': cat, 'description': desc, 'result': 'mutation not applicable to this object set'}
            continue
        after = validate(d)
        new = sorted(set(after) - before)
        out[name] = {'category': cat, 'description': desc, 'caught': bool(new), 'new_errors': new[:3], 'new_error_count': len(new)}
    return before, out


full_before, full_out = run_mutations(ledger, 'full')
slice_before, slice_out = run_mutations(slice_, 'slice')

# ---- write small bad examples for four illustrative defects (full-slice JSON, no sequences)
OUTDIR = PKG / 'review' / 'negative-tests'
OUTDIR.mkdir(exist_ok=True)
(OUTDIR / 'slice-control.json').write_text(json.dumps(slice_, ensure_ascii=False) + '\n', encoding='utf-8')
for name in ['R1_context_points_to_missing_object', 'U1_unit_not_in_enum', 'I1_reversed_interval', 'R6_measurement_row_disagrees_with_its_assertion']:
    d = copy.deepcopy(slice_)
    next(fn for n, c, ds, fn in M if n == name)(d)
    (OUTDIR / f'slice-{name}.json').write_text(json.dumps(d, ensure_ascii=False) + '\n', encoding='utf-8')

# ---- sign-sequence tests on fixture files (throw-away; raw directory)
FIX = RAW / 'review-tmp' / 'sequence-fixtures'
if FIX.exists():
    shutil.rmtree(FIX)
FIX.mkdir(parents=True)
# invented codes that do not occur in either export
used = set()
for line in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8-sig').splitlines():
    if line.strip():
        r = json.loads(line)
        used.update(r['signs_visual_ltr'])
for line in (ROOT / 'data/normalized/mayig_faces.jsonl').read_text(encoding='utf-8-sig').splitlines():
    if line.strip():
        r = json.loads(line)
        used.update(str(x) for x in r['signs_visual_ltr'])
codes = [c for c in ('987', '988', '989', '986', '985') if c not in used]
assert len(codes) >= 3, 'choose other invented codes'
a, b, c = codes[:3]
fixtures = {
    'F1_key_sign_sequence.json': {'x': {'sign_sequence': [a, b, c]}},
    'F2_new_key_three_token_string.json': {'x': {'readout': f'{a}-{b}-{c}'}},
    'F3_new_key_two_token_string.json': {'x': {'readout': f'{a}-{b}'}},
    'F4_text_code_two_signs.json': {'x': {'inscription': f'+{a}-{b}+'}},
    'F5_embedded_in_sentence.json': {'x': {'note': f'Compare {a}-{b}-{c} with the neighbouring seal.'}},
    'F6_integer_array.json': {'x': {'signs': [int(a), int(b), int(c)]}},
    'F7_comma_separated_string.json': {'x': {'readout': f'{a},{b},{c}'}},
    'F8_string_array_two_codes.json': {'x': {'readout': [a, b]}},
    'F9_p_codes_space_separated.json': {'x': {'readout': f'P{a} P{b} P{c}'}},
    'F10_mayig_style_grapheme_dicts_new_key.json': {'x': {'marks': [{'id': f'P{a}'}, {'id': f'P{b}'}, {'id': f'P{c}'}]}},
}
for name, payload in fixtures.items():
    (FIX / name).write_text(json.dumps(payload) + '\n', encoding='utf-8')
(FIX / 'F11_sequence_in_csv.csv').write_text(f'object,reading\nOL-X,{a}-{b}-{c}\n', encoding='utf-8')
(FIX / 'F12_sequence_in_markdown.md').write_text(f'The reading {a}-{b}-{c} appears here.\n', encoding='utf-8')
(FIX / 'F13_sequence_in_jsonl.jsonl').write_text(json.dumps({'x': {'sign_sequence': [a, b, c]}}) + '\n', encoding='utf-8')
(FIX / 'schema.json').write_text(json.dumps({'x': {'sign_sequence': [a, b, c]}}) + '\n', encoding='utf-8')

per_file = {}
for p in sorted(FIX.iterdir()):
    if p.suffix == '.json' and p.name != 'schema.json' and not p.name.endswith('-schema.json'):
        per_file[p.name] = 'caught' if sequence_errors(json.loads(p.read_text(encoding='utf-8'))) else 'NOT caught'
    elif p.suffix == '.json':
        per_file[p.name] = 'skipped by the scanner (schema file name)'
    else:
        per_file[p.name] = 'not scanned (file type other than .json)'

# run the real command-line scan on the fixture directory
proc = subprocess.run([sys.executable, str(PKG / 'validate.py'), '--ledger', str(PKG / 'run-2026-10-07-v4/ledger-public.json'), '--scan-dir', str(FIX)],
                      capture_output=True, text=True, cwd=str(ROOT), env={**__import__('os').environ, 'PYTHONDONTWRITEBYTECODE': '1'})
try:
    scan = json.loads(proc.stdout.strip().splitlines()[-1])
except Exception:
    scan = {'raw_stdout': proc.stdout[-500:]}
import re as _re
flagged_files = sorted({m.group(1) for e in scan.get('errors', []) for m in [_re.search(r'([^\\/]+\.json): ', e)] if m})
shutil.rmtree(FIX)

res = {
    'full_ledger_baseline_errors': sorted(full_before),
    'two_object_slice_baseline_errors': sorted(slice_before),
    'mutations_on_full_ledger': full_out,
    'mutations_on_slice': {k: {kk: vv for kk, vv in v.items() if kk in ('caught', 'new_error_count')} for k, v in slice_out.items()},
    'sequence_fixtures_function_level': per_file,
    'sequence_fixtures_command_line_scan_exit_code': proc.returncode,
    'sequence_fixtures_command_line_scan_flagged_files': flagged_files,
    'invented_codes_used': 'three codes absent from both exports (not listed here)',
}
(PKG / 'review' / 'negative-tests-results.json').write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
caught = [k for k, v in full_out.items() if v.get('caught')]
missed = [k for k, v in full_out.items() if v.get('caught') is False]
print('caught on full ledger:', len(caught), caught)
print('NOT caught on full ledger:', len(missed), missed)
print(json.dumps({'slice_baseline': sorted(slice_before)}, indent=1))
print(json.dumps(per_file, indent=1))
print('scan exit code', proc.returncode, 'flagged:', flagged_files)
