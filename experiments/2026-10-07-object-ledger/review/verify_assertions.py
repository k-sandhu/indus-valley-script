"""Reviewer check: does each ledger assertion value equal the value at its cited source locator?

Resolves the locators of the file types that dominate the ledger (Lipi export, Mayig export, saved museum
records, Lothal table CSV, HARP period mapping) and compares the stored value. Other locator types are
counted but not resolved here (they are checked by hand in REVIEW.md).

Run from the repository root:  python experiments/2026-10-07-object-ledger/review/verify_assertions.py
Writes review/assertion-check.json (aggregate counts and a short list of mismatches).
"""
import collections
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-07-object-ledger'
OUT = PKG / 'review' / 'assertion-check.json'

led = json.loads((PKG / 'run-2026-10-07-v4/ledger-public.json').read_text(encoding='utf-8'))
sel = json.loads((PKG / 'selection-2026-10-07-v1/selection.json').read_text(encoding='utf-8'))


def jl(p):
    return [json.loads(l) for l in (ROOT / p).read_text(encoding='utf-8-sig').splitlines() if l.strip()]


lipi = {f['record_id']: f for f in jl('data/normalized/lipi_observed_faces.jsonl')}
mayig = {f['record_id']: f for f in jl('data/normalized/mayig_faces.jsonl')}
museum = {m['record_id']: m for m in json.loads((ROOT / 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/focused-records.json').read_text(encoding='utf-8'))}
lothal = {r['object_id']: r for r in csv.DictReader((ROOT / 'data/six-hour/lothal/table-coding/reviewed-pass.csv').open(encoding='utf-8-sig'))}
periods = {p['label']: p for p in json.loads((ROOT / 'experiments/2026-10-06-chronology-region/main-2026-10-07-v1/period_mapping.json').read_text(encoding='utf-8'))}
fam_faces = collections.defaultdict(list)
for f in lipi.values():
    fam_faces[f['object_family_id']].append(f)
sel_by_oid = {o['object_id']: o for o in sel['objects']}

LIPI = 'data/normalized/lipi_observed_faces.jsonl'
MAYIG = 'data/normalized/mayig_faces.jsonl'
MUS = 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/focused-records.json'
LOT = 'data/six-hour/lothal/table-coding/reviewed-pass.csv'
PER = 'experiments/2026-10-06-chronology-region/main-2026-10-07-v1/period_mapping.json'


def nested(d, dotted):
    for part in dotted.split('.'):
        d = d[part]
    return d


stats = collections.Counter()
mismatch = []
unresolved = collections.Counter()
for a in led['assertions']:
    p, rec, fld, val = a['locator']['path'], a['locator']['record'], a['locator']['field'], a['value']
    kind = None
    expect = None
    try:
        if p == LIPI and rec in lipi:
            kind = 'lipi_record'
            f = lipi[rec]
            if fld.startswith('metadata.'):
                raw = f['metadata'][fld.split('.', 1)[1]]
                expect = float(raw) if a['field'] == 'measurement' else raw
                if a['field'] == 'measurement':
                    expect = {'dimension': val['dimension'], 'value': float(raw), 'unit': 'mm'}
            elif fld == 'record_id':
                expect = f['record_id'] if a['field'] == 'label' else ('normalized_record; physical_face_and_line_extent_needs_review' if a['field'] == 'boundaries' else None)
            elif fld == 'direction':
                expect = f['direction']
            elif fld == 'single_line':
                expect = 'single_line' if f['single_line'] else 'multiple_or_unresolved_lines'
            elif fld == 'length':
                expect = f['length']
            elif fld == 'has_unknown_sign':
                expect = bool(f['has_unknown_sign'])
            elif fld == 'object_family_id':
                expect = f['object_family_id']
            elif fld == 'orientation_basis':
                expect = 'visual_ltr; reading_rtl as normalized source hypothesis'
            if a['field'] == 'damage' and fld == 'has_unknown_sign':
                expect = bool(f['has_unknown_sign'])
        elif p == LIPI and rec.startswith('family='):
            kind = 'lipi_family'
            fid = rec.split('=', 1)[1]
            faces = fam_faces[fid]
            if fld == 'length_bin':
                n = max(x['length'] for x in faces)
                expect = '0' if n == 0 else '1-2' if n <= 2 else '3-5' if n <= 5 else '6-9' if n <= 9 else '10+'
            elif fld == 'damage':
                expect = any(x['has_unknown_sign'] or not x['complete_observed'] or str(x['metadata'].get('preservation', '')).casefold() not in {'complete', '', '-', '--'} for x in faces)
            elif fld == 'face_count':
                expect = len(faces)
        elif p == MAYIG and rec in mayig:
            kind = 'mayig_record'
            f = mayig[rec]
            expect = {'record_id': (f['record_id'] if a['field'] == 'label' else ('normalized_record; physical_face_and_line_extent_needs_review' if a['field'] == 'boundaries' else None)), 'direction': f.get('direction'), 'length': f['length'], 'has_unknown_sign': bool(f['has_unknown_sign']), 'object_family_id': f['object_family_id']}.get(fld)
            if fld == 'multiline':
                expect = 'single_line' if not f['multiline'] else 'multiple_or_unresolved_lines'
        elif p == MUS and rec.startswith('record_id='):
            kind = 'museum_record'
            m = museum[rec.split('=', 1)[1].split(';')[0]]
            if a['field'] in ('calendar_interval', 'dating_basis'):
                mt = re.search(r'(\d{3,4})\s*[-–]\s*(\d{3,4})\s*B\.?\s*C', str(m['date']), re.I)
                expect = {'bce_oldest': int(mt[1]), 'bce_youngest': int(mt[2])} if (mt and a['field'] == 'calendar_interval') else ('museum catalogue attribution; dating method unspecified' if mt else None)
            elif fld in m and a['field'] not in ('measurement',):
                expect = m[fld]
            elif fld == 'dimensions' and a['field'] == 'measurement':
                expect = 'parsed'
            elif fld == 'date':
                expect = 'parsed_range_or_text'
        elif p == LOT and rec.startswith('object_id='):
            kind = 'lothal_row'
            r = lothal[rec.split('=', 1)[1].split(';')[0]]
            if fld == 'impressions':
                expect = int(r['impressions'])
            elif fld == 'physical_type':
                expect = r['physical_type']
            elif fld == 'context_code':
                expect = r['context_code']
            elif fld == 'object_id':
                expect = {'object_type': 'sealing', 'material': 'clay', 'catalogue_identifier': r['object_id'], 'site': 'Lothal'}.get(a['field'])
        elif p == PER and rec.startswith('label='):
            kind = 'period_label'
            pm = periods[rec.split('=', 1)[1]]
            if fld == 'bce_oldest,bce_youngest':
                expect = {'bce_oldest': pm['bce_oldest'], 'bce_youngest': pm['bce_youngest']}
            elif fld == 'admissible_periods':
                expect = 'approximate HARP period interval applied to export label'
    except KeyError as e:
        mismatch.append({'id': a['id'], 'problem': 'locator not found: ' + str(e), 'kind': kind})
        continue
    if kind is None:
        unresolved[p] += 1
        continue
    if expect is None or expect == 'parsed' or expect == 'parsed_range_or_text':
        stats[kind + ':present_not_compared'] += 1
        continue
    if val == expect:
        stats[kind + ':match'] += 1
    else:
        stats[kind + ':MISMATCH'] += 1
        if len(mismatch) < 40:
            mismatch.append({'id': a['id'], 'object': a['object_id'], 'field': a['field'], 'ledger_value': val, 'source_value': expect, 'locator': [p, rec, fld]})

# Mismatches caused by an intended normalization are listed so the reader can judge them.
res = {'assertions': len(led['assertions']), 'resolved_stats': dict(stats), 'unresolved_by_path': dict(unresolved), 'mismatch_sample': mismatch}

# ---- Source-value quality: export strings with figure suffixes carried into excavation identifiers
fig = [a for a in led['assertions'] if a['field'] == 'excavation_identifier' and re.search(r'Figure|Fig\.', str(a['value']))]
res['excavation_identifier_assertions_with_figure_suffix'] = len(fig)
res['objects_with_figure_suffixed_excavation_identifier'] = len({a['object_id'] for a in fig})
ids = [i for i in led['identifiers'] if i['scheme'] == 'excavation_registration' and re.search(r'Figure|Fig\.', i['value'])]
res['confirmed_excavation_registration_identifiers_with_figure_suffix'] = len(ids)
res['example_figure_suffixed_values'] = sorted({i['value'] for i in ids})[:8]

# ---- stratum_phase values that are calendar dates, not phases
sp = collections.Counter()
for c in led['contexts']:
    v = c['fields']['stratum_phase']['value']
    if v is not None:
        sp[str(v)] += 1
res['stratum_phase_value_counts'] = dict(sp.most_common(30))
res['stratum_phase_values_that_look_like_calendar_dates'] = {k: n for k, n in sp.items() if re.search(r'BC|BCE|\d{3,4}', k)}

# ---- assertion basis for catalogue-only derived fields
cat = [o for o in sel['objects'] if o['family'] is None]
cat_oids = {o['object_id'] for o in cat}
by_field = collections.defaultdict(collections.Counter)
for a in led['assertions']:
    if a['object_id'] in cat_oids:
        by_field[a['field']][(a['source_id'], a['method'], a['confidence'])] += 1
res['catalogue_only_assertion_basis'] = {f: [{'source': k[0], 'method': k[1], 'confidence': k[2], 'n': n} for k, n in c.items()] for f, c in by_field.items()}

OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(res, indent=1, ensure_ascii=False)[:9000])
