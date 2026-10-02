"""Normalize the pinned mayig CISI transcription without altering raw data.

Run from the project root. No inferred phonetic or semantic readings are added.
"""
from pathlib import Path
import json, hashlib, collections, re, subprocess

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'data' / 'mayig'
OUT = ROOT / 'data' / 'normalized'
OUT.mkdir(exist_ok=True)

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

schemas = {}
for p in sorted((SRC / 'features').glob('*.json')):
    schemas[p.stem.upper()] = json.loads(p.read_text(encoding='utf-8'))
default = schemas.pop('DEFAULT_FEATURES')
dump(OUT / 'mayig_sign_schema.json', {'default_features': default, 'signs': schemas})

rows, lines, errors, hashes = [], [], [], []
for p in sorted((SRC / 'corpus').rglob('*.json')):
    raw = p.read_bytes()
    hashes.append({'path': p.relative_to(SRC).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes':len(raw)})
    try:
        faces = json.loads(raw)
    except Exception as exc:
        errors.append({'path':p.relative_to(SRC).as_posix(), 'error':str(exc)})
        continue
    for face in faces:
        desc = face['description']
        family = re.sub(r'[A-Za-z]+$', '', face['id'])
        # Site follows CISI prefix, not a classification learned from sign text.
        site = {'M':'Mohenjo-daro'}.get(family.split('-')[0], 'unmapped')
        kind = 'seal' if 'seal' in desc.lower() and 'sealing' not in desc.lower() else 'sealing' if 'sealing' in desc.lower() else 'tablet' if 'tablet' in desc.lower() else 'unknown'
        groups = collections.defaultdict(list)
        for j,g in enumerate(face['graphemes']):
            f = g['features']
            sign = g['id']
            if sign not in schemas:
                errors.append({'id':face['id'], 'sign':sign, 'issue':'missing sign schema'})
            expected = 3 + len(schemas.get(sign, {}).get('features', []))
            if len(f) != expected:
                errors.append({'id':face['id'], 'index':j, 'sign':sign, 'issue':'feature count differs from schema', 'observed':len(f), 'expected':expected})
            groups[f[1] if len(f)>1 else None].append(g)
        left = [g['id'] for g in face['graphemes']]
        row = {'record_id':face['id'], 'object_family_id':family, 'source_file':p.relative_to(SRC).as_posix(), 'site':site,
               'description':desc, 'object_type':kind, 'graphemes':face['graphemes'],
               'signs_visual_ltr':left, 'signs_reading_rtl':list(reversed(left)), 'length':len(left),
               'line_count':len(groups), 'multiline':len(groups)>1,
               'has_unknown_sign':'P000' in left,
               'orientation_basis':'README: signs visual left-to-right; seals transcribed as sealing; reading normally right-to-left',
               'max_damage':max((g['features'][0] for g in face['graphemes']), default=0),
               'max_uncertainty':max((g['features'][2] for g in face['graphemes']), default=0)}
        row['clear_transcription']=not row['has_unknown_sign'] and row['max_damage']==0 and row['max_uncertainty']==0
        rows.append(row)
        # Each line kept separately: no spurious boundary-crossing n-grams.
        for line_no,gr in sorted(groups.items()):
            ls = [g['id'] for g in gr]
            lines.append({'record_id':face['id'] + ':line' + str(line_no), 'face_id':face['id'], 'object_family_id':family,
                          'source_file':row['source_file'], 'site':site, 'description':desc, 'object_type':kind,
                          'line_number':line_no, 'signs_visual_ltr':ls, 'signs_reading_rtl':list(reversed(ls)),
                          'length':len(ls), 'graphemes':gr, 'has_unknown_sign':'P000' in ls,
                          'max_damage':max((g['features'][0] for g in gr), default=0),
                          'max_uncertainty':max((g['features'][2] for g in gr), default=0)})

for name,data in [('mayig_faces.jsonl',rows),('mayig_lines.jsonl',lines)]:
    (OUT / name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data), encoding='utf-8')
dump(OUT / 'mayig_file_hashes.json', hashes)
seq = collections.Counter(tuple(r['signs_visual_ltr']) for r in rows)
summary = {'commit':subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip(),
           'source_url':'https://github.com/mayig/indus-valley-script-corpus', 'license':'MIT; copyright Michael Carlson 2024',
           'files':len(hashes), 'faces':len(rows), 'objects':len(set(r['object_family_id'] for r in rows)), 'lines':len(lines),
           'tokens':sum(r['length'] for r in rows), 'distinct_signs':len(set(s for r in rows for s in r['signs_visual_ltr'])),
           'unique_face_sequences':len(seq), 'repeated_face_sequence_records':sum(n-1 for n in seq.values()),
           'types':dict(collections.Counter(r['object_type'] for r in rows)), 'descriptions':dict(collections.Counter(r['description'] for r in rows)),
           'multiline_faces':sum(r['multiline'] for r in rows), 'faces_with_damage':sum(r['max_damage']>0 for r in rows),
           'faces_with_uncertainty':sum(r['max_uncertainty']>0 for r in rows),
           'faces_with_unknown_sign':sum(r['has_unknown_sign'] for r in rows),
           'clear_transcriptions':sum(r['clear_transcription'] for r in rows), 'issues':errors,
           'limitations':['Only Mohenjo-daro subset, not full CISI or ICIT.', 'Descriptions are annotator categories, not full archaeological metadata.',
                          'Cross-catalogue correspondence arrays are many-to-many and cannot justify token-level exact conversion.',
                          'Normal right-to-left order is retained explicitly; a particular artifact may have exceptional direction.',
                          'Whole-face RTL reversal is not an asserted reading order for multiline faces; use line rows.',
                          'P000 represents damage/loss even if its default damage and uncertainty feature values equal zero. Exclude it explicitly for clear transcription analyses.',
                          'Line_count is annotator feature metadata, not independently verified layout; primary plate M-141A has two visual rows despite all observed tokens assigned line 1.']}
dump(OUT / 'mayig_summary.json', summary)
print(json.dumps({k:v for k,v in summary.items() if k not in ['descriptions','issues']},indent=2))
print('Feature/schema issues:',len(errors))
