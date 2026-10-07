"""Import CC BY 1979 rows through explicit, reviewed object concordances.

All payloads and quarantined rows are written to a fresh local raw directory.
This interface accepts digitization output; it does not infer a concordance.
"""
import argparse
import collections
import json
import re
from pathlib import Path
from common import OWN, RAW, cisi, fresh, write

EDITION = 'Koskenniemi-Parpola-1979'
LICENSE = 'CC-BY-4.0'

def read_rows(path):
    p = Path(path)
    if p.suffix == '.jsonl':
        return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l]
    x = json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(x, list):
        raise ValueError('Input must be a JSON array or JSONL rows')
    return x

def import_rows(rows, crosswalk, ledger, allow_synthetic=False):
    import jsonschema
    interface = json.loads((OWN / 'interface-schema.json').read_text(encoding='utf-8'))
    def schema_errors(value, definition):
        s = {'$ref': '#/$defs/' + definition, '$defs': interface['$defs']}
        return [e.message for e in jsonschema.Draft202012Validator(s).iter_errors(value)]
    objects = {o['id']: o for o in ledger['objects']}
    identifiers = collections.defaultdict(set)
    for i in ledger['identifiers']:
        if i['status'] == 'confirmed':
            identifiers[(i['scheme'], i['value'])].add(i['object_id'])
    accepted, quarantined = [], []
    seen = set()
    for row in rows:
        reasons = []
        type_errors = schema_errors(row, 'digitized_row')
        if type_errors:
            quarantined.append({'source_row': row, 'crosswalk_candidates': [], 'reasons': ['invalid digitization schema: ' + e for e in type_errors]})
            continue
        if row.get('synthetic') and not allow_synthetic:
            reasons.append('synthetic fixture forbidden in archaeological import')
        number = str(row.get('text_number', ''))
        segment = str(row.get('segment_id', 'whole-source-row'))
        key = (EDITION, number, segment)
        if key in seen:
            reasons.append('duplicate source text/segment in import batch')
        seen.add(key)
        required = ['edition_id', 'text_number', 'inventory', 'inventory_version', 'source_page', 'glyph_tokens', 'auxiliary_markers', 'order', 'boundary_status', 'rights', 'digitization_version', 'review_status']
        if any(k not in row for k in required):
            reasons.append('missing digitization interface field')
        if row.get('edition_id') != EDITION or not re.fullmatch(r'\d+', number):
            reasons.append('wrong edition or nonnumeric source text number')
        rights = row.get('rights', {})
        if rights.get('license') != LICENSE or rights.get('source_url') != 'http://hdl.handle.net/10138/342677' or not rights.get('attribution') or not rights.get('modifications'):
            reasons.append('missing exact CC BY license, attribution, source or transformation record')
        if not row.get('source_page') or not row.get('inventory_version') or not isinstance(row.get('glyph_tokens'), list) or not isinstance(row.get('auxiliary_markers'), list):
            reasons.append('invalid page, inventory version or payload arrays')
        links = [c for c in crosswalk if c.get('edition_id') == EDITION and str(c.get('text_number')) == number and str(c.get('segment_id', 'whole-source-row')) == segment]
        if len(links) != 1:
            reasons.append('no unique source-qualified concordance row')
        link = links[0] if len(links) == 1 else {}
        reasons += ['invalid concordance schema: ' + e for e in schema_errors(link, 'crosswalk_row')]
        if link.get('status') != 'confirmed' or link.get('review_status') != 'reviewed_object_identity':
            reasons.append('object identity concordance unconfirmed or unreviewed')
        if not link.get('concordance_source') or not link.get('concordance_page') or link.get('source_access') != 'opened_primary_concordance':
            reasons.append('unopened or unlocated primary concordance')
        if link.get('relation') != 'same_physical_object':
            reasons.append('text duplicate relation cannot establish carrier identity')
        target = link.get('target_identifier', {})
        hits = identifiers.get((target.get('scheme'), target.get('value')), set())
        if len(hits) != 1:
            reasons.append('target identifier does not resolve one ledger object')
        oid = next(iter(hits)) if len(hits) == 1 else None
        surface = link.get('surface_id')
        if not surface:
            reasons.append('source text/surface boundary or alignment unresolved')
        elif not any(s['id'] == surface and s['object_id'] == oid for s in ledger['surfaces']):
            reasons.append('surface missing or belongs to another object')
        if link.get('surface_review_status') != 'reviewed_source_surface_alignment':
            reasons.append('source surface alignment not reviewed')
        if reasons:
            quarantined.append({'source_row': row, 'crosswalk_candidates': links, 'reasons': sorted(set(reasons))})
        else:
            status = 'Synthetic' if row.get('synthetic') else 'Exploratory' if row['review_status'] != 'independently_reviewed' else 'Frozen evaluation'
            accepted.append({'transcription_id': f'H79-{number}-{segment}', 'object_id': oid, 'surface_id': surface, 'source_edition': EDITION, 'inventory': row['inventory'], 'inventory_version': row['inventory_version'], 'digitization_version': row['digitization_version'], 'source_text_number': number, 'source_page': row['source_page'], 'glyph_tokens': row['glyph_tokens'], 'auxiliary_markers': row['auxiliary_markers'], 'order': row['order'], 'boundary_status': row['boundary_status'], 'review_status': row['review_status'], 'rights': rights, 'concordance': link, 'status': status})
    return accepted, quarantined

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rows', required=True)
    ap.add_argument('--crosswalk', required=True)
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--raw-dir', required=True)
    a = ap.parse_args()
    ledger = json.loads(Path(a.ledger).read_text(encoding='utf-8'))
    accepted, quarantine = import_rows(read_rows(a.rows), read_rows(a.crosswalk), ledger)
    out = fresh(a.raw_dir, RAW)
    write(out / 'accepted-transcriptions.json', accepted)
    write(out / 'quarantine.json', quarantine)
    write(out / 'summary.json', {'accepted': len(accepted), 'quarantined': len(quarantine), 'reasons': dict(collections.Counter(reason for q in quarantine for reason in q['reasons'])), 'sequence_disposition': 'local-only; public transcription metadata can be projected after payload review'})
    print({'accepted': len(accepted), 'quarantined': len(quarantine)})

if __name__ == '__main__':
    main()
