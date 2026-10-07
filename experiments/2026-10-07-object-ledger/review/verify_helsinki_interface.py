"""Reviewer check of Package L's Helsinki 1979 import interface against Package M's staged rows.

Reads Package M's staged payload read-only, calls Package L's pure `import_rows` function, and writes
only a small aggregate result to review/helsinki-interface-check.json. Crosswalk rows used here are
invented test inputs: they pair a staged row with an arbitrary ledger alias to exercise the code path
and carry no identity claim. Nothing is written outside review/.

Run from the repository root:  python experiments/2026-10-07-object-ledger/review/verify_helsinki_interface.py
"""
import collections
import importlib.util
import itertools
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-07-object-ledger'
M = ROOT / 'experiments/2026-10-07-helsinki1979-digitization'
OUT = PKG / 'review' / 'helsinki-interface-check.json'

sys.path.insert(0, str(PKG))
spec = importlib.util.spec_from_file_location('l_importer', PKG / 'import_helsinki1979.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ledger = json.loads((PKG / 'run-2026-10-07-v4/ledger-public.json').read_text(encoding='utf-8'))
iface = json.loads((PKG / 'interface-schema.json').read_text(encoding='utf-8'))
rows_path = M / 'integration/2026-10-07-v1/ledger-import.jsonl'

res = {'staged_payload': str(rows_path.relative_to(ROOT))}

# ---- census of the staged rows (stream; the file is about 90 MB)
n = 0
numtype = collections.Counter()
suffix_examples = collections.Counter()
keys = collections.Counter()
seg_dupes = collections.Counter()
tok_types = collections.Counter()
rights_ok = 0
page_types = collections.Counter()
per_number = collections.Counter()
sample_by_kind = {}
with rows_path.open(encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        n += 1
        t = r.get('text_number')
        if t is None:
            k = 'null'
        elif re.fullmatch(r'\d+', str(t)):
            k = 'digits_only'
        else:
            k = 'has_non_digit'
            suffix_examples[str(t)] += 1
        numtype[k] += 1
        sample_by_kind.setdefault(k, r)
        for kk in r:
            keys[kk] += 1
        seg_dupes[r.get('segment_id')] += 1
        gt = r.get('glyph_tokens')
        tok_types[type(gt).__name__ + ':' + (type(gt[0]).__name__ if gt else 'empty')] += 1
        page_types[type(r.get('source_page')).__name__] += 1
        if t is not None:
            per_number[str(t)] += 1
res['rows'] = n
res['text_number_kinds'] = dict(numtype)
res['non_digit_text_number_examples'] = dict(suffix_examples.most_common(12))
res['non_digit_distinct_values'] = len(suffix_examples)
res['segment_id_duplicates'] = sum(1 for c in seg_dupes.values() if c > 1)
res['glyph_token_container_types'] = dict(tok_types)
res['source_page_types'] = dict(page_types)
res['text_numbers_with_more_than_one_occurrence'] = sum(1 for c in per_number.values() if c > 1)
res['distinct_text_numbers'] = len(per_number)
# stored as [name, count] pairs so that no key in this JSON file equals a payload key name
res['staged_row_field_names_and_counts'] = [[k, c] for k, c in keys.items()]
required = iface['$defs']['digitized_row']['required']
res['required_digitized_fields_missing_in_any_row'] = [k for k in required if keys.get(k, 0) != n]

# ---- exercise the importer
def first_rows(kind, count):
    out = []
    with rows_path.open(encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            t = r.get('text_number')
            ok = (kind == 'digits_only' and t is not None and re.fullmatch(r'\d+', str(t))) or \
                 (kind == 'has_non_digit' and t is not None and not re.fullmatch(r'\d+', str(t))) or \
                 (kind == 'null' and t is None)
            if ok:
                out.append(r)
                if len(out) == count:
                    break
    return out

summary = {}
for kind in ['digits_only', 'has_non_digit', 'null']:
    rs = first_rows(kind, 20)
    acc, quar = mod.import_rows(rs, [], ledger)
    reasons = collections.Counter(x for q in quar for x in q['reasons'] if not x.startswith('invalid concordance schema'))
    summary[kind] = {'rows': len(rs), 'accepted_without_crosswalk': len(acc), 'quarantined': len(quar), 'row_level_reasons': dict(reasons)}
res['import_without_crosswalk'] = summary

# ---- synthetic crosswalk tests (test inputs only; no identity claim)
target = next(i for i in ledger['identifiers'] if i['status'] == 'confirmed' and i['scheme'] == 'reported_catalogue_reference' and i['value'] == 'H-2218')
oid = target['object_id']
surf = next(t['surface_id'] for t in ledger['transcriptions'] if t['object_id'] == oid)
row = first_rows('digits_only', 1)[0]
cw = {'edition_id': 'Koskenniemi-Parpola-1979', 'text_number': row['text_number'], 'concordance_source': 'TEST-ONLY', 'concordance_page': 'TEST-PAGE',
      'source_access': 'opened_primary_concordance', 'target_identifier': {'scheme': target['scheme'], 'value': target['value']},
      'surface_id': surf, 'surface_review_status': 'reviewed_source_surface_alignment', 'relation': 'same_physical_object', 'status': 'confirmed', 'review_status': 'reviewed_object_identity'}
tests = {}
acc, quar = mod.import_rows([row], [cw], ledger)
tests['text_level_crosswalk_without_segment_id'] = {'accepted': len(acc), 'reasons': sorted({x for q in quar for x in q['reasons']})}
cw2 = dict(cw, segment_id=row['segment_id'])
acc, quar = mod.import_rows([row], [cw2], ledger)
tests['crosswalk_with_occurrence_segment_id'] = {'accepted': len(acc), 'reasons': sorted({x for q in quar for x in q['reasons']})}
if acc:
    a = acc[0]
    tests['accepted_row_status'] = a['status']
    tests['accepted_transcription_id'] = a['transcription_id']
    tests['glyph_token_unit_kinds_in_row'] = dict(collections.Counter(t.get('unit_kind') for t in row['glyph_tokens']))
    tests['length_that_builder_would_assert'] = len(row['glyph_tokens'])
# surface limitation
tests['ledger_surfaces'] = len(ledger['surfaces'])
tests['ledger_transcriptions'] = len(ledger['transcriptions'])
tests['surfaces_per_transcription_one_to_one'] = len(ledger['surfaces']) == len(ledger['transcriptions']) and len({t['surface_id'] for t in ledger['transcriptions']}) == len(ledger['transcriptions'])
# suffix row with otherwise valid crosswalk
suf = first_rows('has_non_digit', 1)
if suf:
    srow = suf[0]
    scw = dict(cw, text_number=srow['text_number'], segment_id=srow['segment_id'])
    acc, quar = mod.import_rows([srow], [scw], ledger)
    tests['suffix_text_number_with_complete_crosswalk'] = {'text_number': srow['text_number'], 'accepted': len(acc), 'reasons': sorted({x for q in quar for x in q['reasons']})}
# identifier-scheme friction: the corpus-linked carriers carry the export's CISI string under scheme reported_catalogue_reference
schemes = collections.Counter(i['scheme'].split('@')[0].split(':')[0] for i in ledger['identifiers'] if i['status'] == 'confirmed')
tests['confirmed_identifier_schemes'] = dict(schemes)

# catalogue-only carrier: the ledger has no surface row for it, so the importer cannot accept any text for it
cat = next(i for i in ledger['identifiers'] if i['scheme'] == 'CISI' and i['value'] == 'L-174')
cat_oid = cat['object_id']
tests['catalogue_only_object_has_surface_rows'] = sum(1 for sf in ledger['surfaces'] if sf['object_id'] == cat_oid)
tests['catalogue_only_objects_without_any_surface'] = len({o['id'] for o in ledger['objects']} - {sf['object_id'] for sf in ledger['surfaces']})
cw3 = dict(cw, segment_id=row['segment_id'], target_identifier={'scheme': 'CISI', 'value': 'L-174'}, surface_id='S-NEW-FOR-TEST')
acc, quar = mod.import_rows([row], [cw3], ledger)
tests['text_for_catalogue_only_carrier_with_new_surface_id'] = {'accepted': len(acc), 'reasons': sorted({x for q in quar for x in q['reasons']})}
# identifier-scheme friction on a corpus-linked carrier
cw4 = dict(cw, segment_id=row['segment_id'], target_identifier={'scheme': 'CISI', 'value': 'H-2218'})
acc, quar = mod.import_rows([row], [cw4], ledger)
tests['corpus_linked_carrier_addressed_by_scheme_CISI'] = {'accepted': len(acc), 'reasons': sorted({x for q in quar for x in q['reasons']})}
cw5 = dict(cw, segment_id=row['segment_id'], target_identifier={'scheme': 'reported_catalogue_reference', 'value': 'H 2218'})
acc, quar = mod.import_rows([row], [cw5], ledger)
tests['corpus_linked_carrier_with_unnormalized_value_H_space_2218'] = {'accepted': len(acc), 'reasons': sorted({x for q in quar for x in q['reasons']})}
res['synthetic_crosswalk_tests'] = tests

# ---- attach the accepted test row with build.py --helsinki-layer (outputs deleted afterwards)
import os
import shutil
import subprocess
from validate import validate, sequence_errors  # noqa: E402
RAWDIR = ROOT / 'data/raw/2026-10-07-object-ledger'
tmp_layer = RAWDIR / 'review-tmp-helsinki-layer'
tmp_raw_out = RAWDIR / 'review-tmp-helsinki-build'
tmp_out = PKG / 'review' / 'tmp-helsinki-build'
for p in (tmp_layer, tmp_raw_out, tmp_out):
    if p.exists():
        shutil.rmtree(p)
tmp_layer.mkdir()
acc, quar = mod.import_rows([row], [cw2], ledger)
(tmp_layer / 'accepted-transcriptions.json').write_text(json.dumps(acc), encoding='utf-8')
proc = subprocess.run([sys.executable, str(PKG / 'build.py'), '--selection', str(PKG / 'selection-2026-10-07-v1/selection.json'),
                       '--lothal-assertions', str(ROOT / 'experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json'),
                       '--helsinki-layer', str(tmp_layer / 'accepted-transcriptions.json'), '--output-dir', str(tmp_out), '--raw-dir', str(tmp_raw_out)],
                      capture_output=True, text=True, cwd=str(ROOT), env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
attach = {'description': 'One staged Package M row (digits-only text number) plus an invented crosswalk row to an arbitrary ledger alias was imported, written as an accepted layer under the raw directory, and attached with build.py --helsinki-layer. Test input only; no identity claim.',
          'importer_accepted': len(acc), 'builder_exit_code': proc.returncode}
if proc.returncode == 0:
    L2 = json.loads((tmp_out / 'ledger-public.json').read_text(encoding='utf-8'))
    attach.update({'validator_errors': len(validate(L2)), 'transcriptions_after_attach': len(L2['transcriptions']),
                   'helsinki_transcription_rows': sum(1 for t in L2['transcriptions'] if t['source_id'] == 'helsinki1979'),
                   'public_layer_sequence_errors': len(sequence_errors(L2)),
                   'public_layer_contains_candidate_alternatives_text': 'alternatives' in json.dumps(L2),
                   'length_asserted_from_plotted_units': L2['transcriptions'][-1]['fields']['length']['value'],
                   'note_on_length': 'length equals the number of staged units, which Package M labels as glyph or auxiliary and unverified; it can include auxiliary units.'})
else:
    attach['builder_stderr_tail'] = proc.stderr[-400:]
for p in (tmp_layer, tmp_raw_out, tmp_out):
    if p.exists():
        shutil.rmtree(p)
res['builder_attach_test'] = attach
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(res, indent=1, ensure_ascii=False))
