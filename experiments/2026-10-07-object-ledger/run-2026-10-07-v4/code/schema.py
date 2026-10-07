"""Generate the public ledger's JSON Schema without source payloads."""
import argparse
from common import OWN, write

TEXT = {'type': 'string', 'minLength': 1}
REFS = {'type': 'array', 'items': TEXT, 'minItems': 1, 'uniqueItems': True}
CELL = {'oneOf': [
    {'type': 'object', 'additionalProperties': False, 'required': ['value', 'assertion_ids', 'missing_reason'], 'properties': {'value': {'not': {'type': 'null'}}, 'assertion_ids': REFS, 'missing_reason': {'const': None}}},
    {'type': 'object', 'additionalProperties': False, 'required': ['value', 'assertion_ids', 'missing_reason'], 'properties': {'value': {'const': None}, 'assertion_ids': {'const': []}, 'missing_reason': TEXT}},
]}
OBJECT_FIELDS = ['object_type', 'material', 'holding', 'authenticity', 'catalogue_identifier', 'excavation_identifier', 'field_identifier', 'museum_accession', 'measurement', 'image_pointer', 'rights_pointer', 'face_count', 'length_bin', 'damage']
CONTEXT_FIELDS = ['site', 'region', 'area', 'room_grid', 'stratum_phase', 'period_label', 'calendar_interval', 'dating_basis', 'dating_sample', 'excavation_unit', 'excavation_item', 'physical_contact_category', 'context_code', 'impression_count', 'findspot_site', 'reported_production_place']
SURFACE_FIELDS = ['label', 'orientation', 'arrangement', 'alignment']
TRANSCRIPTION_FIELDS = ['length', 'damage', 'order', 'boundaries', 'inventory_version']

def record(properties):
    return {'type': 'object', 'additionalProperties': False, 'required': list(properties), 'properties': properties}

def fields(names):
    return record({n: CELL for n in names})

def schema():
    definitions = {
        'objects': record({'id': TEXT, 'selection_key': TEXT, 'identity_status': {'enum': ['identifier-supported', 'source-reported']}, 'fields': fields(OBJECT_FIELDS)}),
        'contexts': record({'id': TEXT, 'object_id': TEXT, 'fields': fields(CONTEXT_FIELDS)}),
        'surfaces': record({'id': TEXT, 'object_id': TEXT, 'fields': fields(SURFACE_FIELDS)}),
        'transcriptions': record({'id': TEXT, 'object_id': TEXT, 'surface_id': TEXT, 'source_id': TEXT, 'inventory': TEXT, 'source_version': TEXT, 'rights_id': TEXT, 'payload_disposition': {'const': 'local-only'}, 'fields': fields(TRANSCRIPTION_FIELDS)}),
        'images': record({'id': TEXT, 'object_id': TEXT, 'source_id': TEXT, 'rights_id': TEXT, 'url': TEXT, 'locator': TEXT, 'kind': TEXT, 'inspection_status': TEXT, 'surface_alignment': CELL}),
        'sources': record({'id': TEXT, 'title': TEXT, 'authors': {'type': 'array', 'items': TEXT, 'minItems': 1}, 'year': {'type': ['integer', 'null']}, 'year_missing_reason': {'type': ['string', 'null']}, 'venue': TEXT, 'url': TEXT, 'version': TEXT, 'access_status': TEXT, 'quoted_words': {'const': 0}}),
        'identifiers': record({'id': TEXT, 'object_id': TEXT, 'scheme': TEXT, 'value': TEXT, 'status': {'enum': ['confirmed', 'candidate']}, 'assertion_id': TEXT, 'edition': CELL}),
        'measurements': record({'id': TEXT, 'object_id': TEXT, 'dimension': {'enum': ['horizontal', 'vertical', 'thickness', 'dimension_1', 'dimension_2', 'dimension_3']}, 'value': {'type': 'number', 'exclusiveMinimum': 0}, 'unit': {'enum': ['mm', 'cm', 'g', 'kg']}, 'method': CELL, 'assertion_id': TEXT}),
        'assertions': record({'id': TEXT, 'object_id': TEXT, 'field': TEXT, 'value': {'not': {'type': 'null'}}, 'source_id': TEXT, 'locator': record({'path': TEXT, 'record': TEXT, 'field': TEXT, 'page_or_url': {'type': ['string', 'null']}, 'page_missing_reason': {'type': ['string', 'null']}}), 'method': TEXT, 'confidence': {'enum': ['source-reported', 'identifier-supported', 'candidate']}, 'review_status': {'const': 'not-expert-reviewed'}}),
        'rights': record({'id': TEXT, 'source_id': TEXT, 'asset_ref': TEXT, 'status': {'enum': ['own-work', 'explicit-license', 'rights-unverified', 'mixed-assets']}, 'license': CELL, 'scope': TEXT, 'disposition': {'enum': ['reference-only', 'local-only']}, 'notice_locator': TEXT}),
        'relationships': record({'id': TEXT, 'object_id': TEXT, 'source_id': TEXT, 'external_record': TEXT, 'relation': TEXT, 'status': {'enum': ['confirmed', 'candidate']}, 'method': TEXT, 'assertion_id': TEXT}),
        'correction_overlays': record({'id': TEXT, 'object_ids': {'type': 'array', 'items': TEXT, 'minItems': 1}, 'source_id': TEXT, 'correction_id': TEXT, 'affected_fields': {'type': 'array', 'items': TEXT, 'minItems': 1}, 'locator': TEXT, 'applied_action': TEXT, 'status': TEXT}),
    }
    result = record({'schema_version': {'const': '1.0'}, 'status': {'const': 'Exploratory'}, 'selection_sha256': TEXT, 'sequence_policy': {'const': 'No sign sequences; transcription payloads are local-only'}, **{k: {'type': 'array', 'items': {'$ref': '#/$defs/' + k}} for k in definitions}})
    result['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    result['$defs'] = definitions
    return result

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default=str(OWN / 'schema.json'))
    a = ap.parse_args()
    from pathlib import Path
    p = Path(a.output).resolve()
    if not p.is_relative_to(OWN) or p.exists():
        raise ValueError('Schema output must be a new file inside the owned directory')
    write(p, schema())
