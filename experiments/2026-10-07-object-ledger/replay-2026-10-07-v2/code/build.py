"""Build source-attributed public tables and a separate restricted local register."""
import argparse
import collections
import gzip
import json
import re
from pathlib import Path
from common import OWN, RAW, ROOT, PATHS, HARP, CENSUS, cisi, coarse, digest, fresh, load_inputs, missing, site, write
from schema import OBJECT_FIELDS, CONTEXT_FIELDS, SURFACE_FIELDS, TRANSCRIPTION_FIELDS

LIPI_PIN = 'fc8813a52e183d19c441631dc26c33a4dccbea39'
MAYIG_PIN = 'ad2f1e218a34b8c33c57de0d6cb8d99272765bbb'
HARP_URL = 'https://www.harappa.com/sites/default/files/pdf/Kenoyer2000_The%20Tiny%20Steatite%20Seals%20of%20Harappa.pdf'
PERIOD_URL = 'https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf'
LOTHAL_URL = 'https://zenodo.org/records/5514283'
CISI_URL = 'https://ignca.gov.in/Asi_data/76884.pdf'

def empty(reason='not_recorded_in_inspected_sources'):
    return {'value': None, 'assertion_ids': [], 'missing_reason': reason}

def cell(value, ids):
    return {'value': value, 'assertion_ids': list(ids), 'missing_reason': None}

class Builder:
    def __init__(self, selection, inputs, selection_path):
        self.s = selection
        self.i = inputs
        self.selection_path = selection_path
        self.d = {'schema_version': '1.0', 'status': 'Exploratory', 'selection_sha256': digest(selection_path), 'sequence_policy': 'No sign sequences; transcription payloads are local-only'}
        for table in ['objects', 'contexts', 'surfaces', 'transcriptions', 'images', 'sources', 'identifiers', 'measurements', 'assertions', 'rights', 'relationships', 'correction_overlays']:
            self.d[table] = []
        self.lookups = collections.defaultdict(set)
        self.raw_transcriptions = []
        self.comparisons = []
        self.source_ids = set()
        self.register_sources()
        self.assertion_by_id = {}

    def source(self, ident, title, authors, year, venue, url, version, access='opened_local_register; primary_not_reopened'):
        if ident in self.source_ids:
            return
        self.source_ids.add(ident)
        self.d['sources'].append({'id': ident, 'title': title, 'authors': authors, 'year': year, 'year_missing_reason': None if year else 'not_recorded_in_reused_register', 'venue': venue, 'url': url, 'version': version, 'access_status': access, 'quoted_words': 0})

    def register_sources(self):
        self.source('lipi', 'Lipi observational export', ['yajnadevam'], None, 'GitHub repository; normalized locally', 'https://github.com/yajnadevam/lipi/tree/' + LIPI_PIN, LIPI_PIN, 'opened_local_normalized_records')
        self.source('mayig', 'Indus Valley Script Corpus', ['Michael Carlson'], 2024, 'GitHub repository; normalized locally', 'https://github.com/mayig/indus-valley-script-corpus/tree/' + MAYIG_PIN, MAYIG_PIN, 'opened_local_normalized_records')
        self.source('cisi1', 'Corpus of Indus Seals and Inscriptions. 1. Collections in India', ['Jagat Pati Joshi', 'Asko Parpola'], 1987, 'Annales Academiae Scientiarum Fennicae B 239; Helsinki', CISI_URL, '1987; first 431-page copy; scan repetition excluded')
        self.source('harappa2000', "The ‘Tiny Steatite Seals’ (Incised Steatite Tablets) of Harappa: Some Observations on Their Context and Dating", ['Richard H. Meadow', 'Jonathan Mark Kenoyer'], 2000, 'M. Taddei and G. De Marco (eds.), South Asian Archaeology 1997, pp.321–340', HARP_URL, 'author manuscript; corrected PDF/author/book pagination')
        self.source('harappa2010', 'Inscribed Objects from Harappa Excavations 1986–2007', ['Jonathan Mark Kenoyer', 'Richard H. Meadow'], 2010, 'Corpus of Indus Seals and Inscriptions 3.1; printed xlv, Table 1', PERIOD_URL, 'HARP approximate calibrated period table')
        self.source('lothal2005', 'The Lothal Sealings: Records from an Indus Civilization Town at the Eastern End of the Maritime Trade Circuits across the Arabian Sea', ['Dennys Frenez', 'Maurizio Tosi'], 2005, 'M. Perna (ed.), Studi in onore di Enrica Fiandra: Contributi di archeologia egea e vicinorientale, pp.65–103', LOTHAL_URL, 'Table 1; two local pixel transcriptions')
        self.source('census_v6', 'Evidence census synthesis and batch corrections', ['Repository research agents'], 2026, 'Private repository research notes', CENSUS + 'REPORT.md', '2026-10-07-v6', 'opened_local_reports_and_registers')
        self.source('ledger', 'Object-ledger pilot protocol', ['Package L research agent'], 2026, 'Private repository research notes', 'experiments/2026-10-07-object-ledger/PROTOCOL.md', '2026-10-07', 'own_work')
        self.source('helsinki1979', 'Corpus of Texts in the Indus Script', ['Kimmo Koskenniemi', 'Asko Parpola'], 1979, 'Department of Asian and African Studies, University of Helsinki; Research Reports 1', 'http://hdl.handle.net/10138/342677', '1979 interim edition', 'opened_local_provenance_manifest; primary_not_reopened')
        self.source('helsinki1980', 'Documentation and Duplicates of the Texts in the Indus Script', ['Kimmo Koskenniemi', 'Asko Parpola'], 1980, 'Department of Asian and African Studies, University of Helsinki', 'https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf', '1980', 'opened_local_provenance_manifest; concordance_not_transcribed')

    def assertion(self, oid, field, value, source, path, record, original_field, page=None, method='source_field_extraction', confidence='source-reported'):
        ident = f'A-{len(self.d["assertions"]) + 1:06d}'
        row = {'id': ident, 'object_id': oid, 'field': field, 'value': value, 'source_id': source,
               'locator': {'path': path, 'record': str(record), 'field': original_field, 'page_or_url': page, 'page_missing_reason': None if page else 'source_page_not_present_in_reused_record'},
               'method': method, 'confidence': confidence, 'review_status': 'not-expert-reviewed'}
        self.d['assertions'].append(row)
        self.assertion_by_id[ident] = row
        self.lookups[oid].add((path, str(record)))
        return ident

    def add(self, fields, oid, field, value, source, path, record, original_field, page=None, method='source_field_extraction', priority=False, confidence='source-reported'):
        if missing(value):
            if fields[field]['value'] is None:
                fields[field]['missing_reason'] = 'placeholder_or_uninformative_value_in_source'
            return None
        aid = self.assertion(oid, field, value, source, path, record, original_field, page, method, confidence)
        if priority or fields[field]['value'] is None:
            previous = fields[field]['assertion_ids']
            fields[field] = cell(value, previous + [aid])
        else:
            fields[field]['assertion_ids'].append(aid)
        return aid

    def identifier(self, oid, scheme, value, aid, edition=None, status='confirmed'):
        if not aid or missing(value):
            return
        ident = f'I-{len(self.d["identifiers"]) + 1:05d}'
        ec = empty('edition_not_verified_for_export_alias')
        if edition:
            parent = self.assertion_by_id[aid]
            loc = parent['locator']
            ea = self.assertion(oid, 'identifier_edition', edition, parent['source_id'], loc['path'], loc['record'], loc['field'] + '; source edition', loc['page_or_url'], 'source_edition_attribution_for_identifier')
            ec = cell(edition, [ea])
        self.d['identifiers'].append({'id': ident, 'object_id': oid, 'scheme': scheme, 'value': str(value), 'status': status, 'assertion_id': aid, 'edition': ec})

    def rights(self, oid, source, asset, disposition='reference-only'):
        ident = f'R-{len(self.d["rights"]) + 1:05d}'
        license_cell = empty('no_explicit_asset_license_verified')
        status = 'rights-unverified'
        if source == 'mayig' and disposition == 'local-only':
            aid = self.assertion(oid, 'license', 'MIT', 'mayig', 'knowledge/provenance/REDISTRIBUTION.md', 'Mayig source repository', 'license', 'https://github.com/mayig/indus-valley-script-corpus/blob/' + MAYIG_PIN + '/LICENSE', 'inherited_repository_license_review')
            license_cell, status = cell('MIT', [aid]), 'explicit-license'
        self.d['rights'].append({'id': ident, 'source_id': source, 'asset_ref': asset, 'status': status, 'license': license_cell, 'scope': 'image witness' if disposition == 'reference-only' else 'transcription payload', 'disposition': disposition, 'notice_locator': 'knowledge/provenance/REDISTRIBUTION.md'})
        return ident

    def image(self, oid, source, url, locator, kind, inspection, fields):
        ident = f'V-{len(self.d["images"]) + 1:05d}'
        rid = self.rights(oid, source, ident)
        self.d['images'].append({'id': ident, 'object_id': oid, 'source_id': source, 'rights_id': rid, 'url': url, 'locator': locator, 'kind': kind, 'inspection_status': inspection, 'surface_alignment': empty('object_level_pointer; source_faces_not_aligned_to_export')})
        aid = self.assertion(oid, 'image_pointer', ident, source, locator.split('#')[0], locator.split('#', 1)[-1], 'image witness locator', url, 'reference_pointer_from_reused_audit')
        if fields['image_pointer']['value'] is None:
            fields['image_pointer'] = cell(ident, [aid])
        else:
            fields['image_pointer']['assertion_ids'].append(aid)
        ra = self.assertion(oid, 'rights_pointer', rid, 'ledger', 'knowledge/provenance/REDISTRIBUTION.md', source, 'asset handling rule', method='asset_level_rights_record')
        if fields['rights_pointer']['value'] is None:
            fields['rights_pointer'] = cell(rid, [ra])
        else:
            fields['rights_pointer']['assertion_ids'].append(ra)

    def measurement(self, oid, dimension, value, source, path, record, original_field, fields, page=None, method='reported_dimension; measurement_method_unavailable'):
        aid = self.add(fields, oid, 'measurement', {'dimension': dimension, 'value': value, 'unit': 'mm'}, source, path, record, original_field, page, method)
        self.d['measurements'].append({'id': f'M-{len(self.d["measurements"]) + 1:05d}', 'object_id': oid, 'dimension': dimension, 'value': value, 'unit': 'mm', 'method': empty('measurement_method_not_reported_in_inspected_record'), 'assertion_id': aid})

    def corpus(self, chosen, of, cf):
        oid = chosen['object_id']
        faces = [f for f in self.i['lipi'] if f['object_family_id'] == chosen['family']]
        if not faces:
            for k in ['length_bin', 'damage', 'face_count']:
                of[k] = empty('absent_from_pinned_local_corpus; source_does_not_supply_field')
            return
        for field, value in [('length_bin', chosen['length_bin']), ('damage', chosen['damaged']), ('face_count', len(faces))]:
            self.add(of, oid, field, value, 'lipi', PATHS['lipi'], 'family=' + chosen['family'], field, method='aggregation_over_all_family_faces')
        for face in faces:
            rec = face['record_id']
            m = face['metadata']
            for field, original in [('object_type', 'type'), ('material', 'material'), ('catalogue_identifier', 'cisi'), ('excavation_identifier', 'excavation-idno')]:
                aid = self.add(of, oid, field, m.get(original), 'lipi', PATHS['lipi'], rec, 'metadata.' + original)
                if field in {'catalogue_identifier', 'excavation_identifier'}:
                    self.identifier(oid, 'reported_catalogue_reference' if field == 'catalogue_identifier' else 'excavation_registration', m.get(original), aid)
            for field, original in [('site', 'site'), ('region', 'region'), ('area', 'area-section'), ('room_grid', 'room-grid'), ('stratum_phase', 'phase'), ('period_label', 'time')]:
                self.add(cf, oid, field, m.get(original), 'lipi', PATHS['lipi'], rec, 'metadata.' + original)
            if not missing(m.get('period')):
                self.add(cf, oid, 'stratum_phase', m['period'], 'lipi', PATHS['lipi'], rec, 'metadata.period')
            for dim, original in [('horizontal', 'horizontal(mm)'), ('vertical', 'vertical(mm)'), ('thickness', 'thickness(mm)')]:
                try:
                    val = float(m.get(original, 0))
                except (ValueError, TypeError):
                    val = 0
                if val > 0:
                    self.measurement(oid, dim, val, 'lipi', PATHS['lipi'], rec, 'metadata.' + original, of)
            self.transcription(oid, face, 'lipi', of)
            alias = self.assertion(oid, 'export_family_identifier', chosen['family'], 'lipi', PATHS['lipi'], rec, 'object_family_id', method='source_qualified_export_identity')
            self.identifier(oid, 'Lipi_family@' + LIPI_PIN, chosen['family'], alias)
            # HARP dates apply only to Harappa; all literal labels remain separately attributed.
            if face['site'] == 'Harappa':
                pm = next((p for p in self.i['periods'] if p['label'] == m.get('time')), None)
                if pm and pm['bce_oldest'] is not None:
                    interval = {'bce_oldest': pm['bce_oldest'], 'bce_youngest': pm['bce_youngest']}
                    self.add(cf, oid, 'calendar_interval', interval, 'harappa2010', PATHS['periods'], 'label=' + pm['label'], 'bce_oldest,bce_youngest', PERIOD_URL + '#Table1,printed-xlv,PDF4', 'attributed_period_conversion; not_object_sample_date')
                    self.add(cf, oid, 'dating_basis', 'approximate HARP period interval applied to export label', 'harappa2010', PATHS['periods'], 'label=' + pm['label'], 'admissible_periods', PERIOD_URL + '#Table1,printed-xlv,PDF4', 'attributed_period_conversion')

    def transcription(self, oid, face, source, of):
        rec = face['record_id']
        sid = f'S-{len(self.d["surfaces"]) + 1:05d}'
        sf = {k: empty() for k in SURFACE_FIELDS}
        self.add(sf, oid, 'label', rec, source, PATHS[source], rec, 'record_id')
        self.add(sf, oid, 'orientation', face.get('direction') if source == 'lipi' else None, source, PATHS[source], rec, 'direction')
        self.add(sf, oid, 'arrangement', 'single_line' if face.get('single_line', not face.get('multiline', False)) else 'multiple_or_unresolved_lines', source, PATHS[source], rec, 'single_line' if source == 'lipi' else 'multiline', method='retained_source_boundary_metadata')
        sf['alignment'] = empty('source_record_surface; cross_source_face_alignment_unverified')
        self.d['surfaces'].append({'id': sid, 'object_id': oid, 'fields': sf})
        tf = {k: empty() for k in TRANSCRIPTION_FIELDS}
        self.add(tf, oid, 'length', face['length'], source, PATHS[source], rec, 'length')
        self.add(tf, oid, 'damage', bool(face['has_unknown_sign']), source, PATHS[source], rec, 'has_unknown_sign', method='unknown_marker_flag; separate_from_object_damage')
        self.add(tf, oid, 'order', 'visual_ltr; reading_rtl as normalized source hypothesis', source, PATHS[source], rec, 'orientation_basis', method='retained_order_conventions')
        self.add(tf, oid, 'boundaries', 'normalized_record; physical_face_and_line_extent_needs_review', source, PATHS[source], rec, 'record_id', method='retained_source_record_boundary')
        tf['inventory_version'] = empty('native_sign_inventory_version_not_verified_in_export')
        tid = f'T-{len(self.d["transcriptions"]) + 1:05d}'
        rid = self.rights(oid, source, tid, 'local-only')
        self.d['transcriptions'].append({'id': tid, 'object_id': oid, 'surface_id': sid, 'source_id': source, 'inventory': 'Wells' if source == 'lipi' else 'Mayig P classes', 'source_version': LIPI_PIN if source == 'lipi' else MAYIG_PIN, 'rights_id': rid, 'payload_disposition': 'local-only', 'fields': tf})
        self.raw_transcriptions.append({'transcription_id': tid, 'source_id': source, 'source_record': face})
        self.add(of, oid, 'rights_pointer', rid, 'ledger', 'knowledge/provenance/REDISTRIBUTION.md', source, 'asset handling rule', method='asset_level_transcription_rights_record')

    def harappa(self, chosen, of, cf):
        oid = chosen['object_id']
        po = next((p for p in self.i['harappa']['physical_objects'] if p.get('target_id') == chosen['catalogue_key']), None)
        if not po or chosen['key'] not in {f'H-{n}' for n in range(2218, 2240)}:
            return
        record = 'physical_objects[observation_id=' + po['observation_id'] + ']'
        reg = po['registration']
        caption = 'PDF16;author15;mapped-book335;Figure4'
        drawing = 'PDF15;author14;mapped-book334;Figure4;specimen=' + po['observation_id'].split('-')[-1]
        aid = self.add(of, oid, 'excavation_identifier', reg['literal'], 'harappa2000', PATHS['harappa'], record, 'registration.literal', caption, 'inherited_primary_caption_registration_join', priority=True, confidence='identifier-supported')
        self.identifier(oid, 'HARP_excavation_registration', reg['literal'], aid, 'Meadow and Kenoyer 2000 Figure 4 caption')
        for field, key in [('excavation_unit', 'excavation_unit'), ('excavation_item', 'item')]:
            self.add(cf, oid, field, reg[key], 'harappa2000', PATHS['harappa'], record, 'registration.' + key, caption, 'caption_item_and_unit_kept_separate', priority=True)
        self.add(of, oid, 'object_type', 'TAB:I', 'harappa2000', PATHS['harappa'], record, 'type', caption, 'normalized_incised_tablet', priority=True)
        self.add(of, oid, 'material', 'fired steatite', 'harappa2000', PATHS['harappa'], record, 'material.value', caption, priority=True)
        self.add(cf, oid, 'area', 'Mound E; HARP Trench 11; outside wall 250', 'harappa2000', PATHS['harappa_caption'], 'description_assertions[0]', 'value', 'PDF14,16,17;author13,15,16;mapped-book333,335,336', 'paraphrased_group_context_applied_only_to_specimens2-23', priority=True)
        self.add(cf, oid, 'period_label', 'late Period 3B', 'harappa2000', PATHS['harappa_caption'], 'description_assertions[1]', 'value', 'PDF14;author13;mapped-book333', priority=True)
        self.add(cf, oid, 'dating_basis', 'wall 296 and wall-250 fill precede tablet debris; Period 3C material follows', 'harappa2000', PATHS['harappa_caption'], 'description_assertions[1]', 'dating_basis', 'PDF14;author13;mapped-book333', 'own_summary_of_published_depositional_argument', priority=True)
        self.image(oid, 'harappa2000', HARP_URL, PATHS['harappa'] + '#' + record + ';' + drawing, 'published_drawing', 'prior_AI_source_inspection; primary_not_reopened_in_Package_L', of)
        aid = self.assertion(oid, 'identity_join', reg['literal'], 'harappa2000', PATHS['harappa'], record, 'export_join', caption, 'exact_caption_registration_to_export; inherited_review', 'identifier-supported')
        self.d['relationships'].append({'id': f'J-{len(self.d["relationships"]) + 1:05d}', 'object_id': oid, 'source_id': 'harappa2000', 'external_record': po['observation_id'], 'relation': 'same_reported_object', 'status': 'confirmed', 'method': 'caption_registration', 'assertion_id': aid})

    def lothal(self, chosen, of, cf):
        oid = chosen['object_id']
        l = next((p for p in self.i['lothal'] if p['object_id'] == chosen['catalogue_key']), None)
        if not l:
            return
        rec = 'object_id=' + l['object_id']
        page = f'Table1;PDF{l["pdf_page"]};printed{l["printed_page"]}'
        for field, value, original in [('object_type', 'sealing', 'object_id'), ('material', 'clay', 'object_id')]:
            self.add(of, oid, field, value, 'lothal2005', PATHS['lothal'], rec, original, page, 'source_frame_carrier_class', priority=True)
        if chosen['family'] is None:
            aid = self.add(of, oid, 'catalogue_identifier', l['object_id'], 'lothal2005', PATHS['lothal'], rec, 'object_id', page, 'published_catalogue_number', priority=True)
            self.identifier(oid, 'CISI', l['object_id'], aid, 'CISI 1 (1987), L124–L216 sealing section')
            self.add(cf, oid, 'site', 'Lothal', 'lothal2005', PATHS['lothal'], rec, 'object_id', page, 'source_frame_site')
            self.add(cf, oid, 'region', 'Gujarat/Kutch', 'ledger', str(self.selection_path.relative_to(ROOT)), chosen['object_id'], 'region', method='pilot_geographic_stratum')
        for field, original in [('physical_contact_category', 'physical_type'), ('context_code', 'context_code')]:
            self.add(cf, oid, field, l[original], 'lothal2005', PATHS['lothal'], rec, original, page, 'source_category; W1_inferred_from_stamp_recurrence' if l['context_code'] == 'W1' and field == 'context_code' else 'retained_source_table_category', priority=True)
        self.add(cf, oid, 'impression_count', int(l['impressions']), 'lothal2005', PATHS['lothal'], rec, 'impressions', page, priority=True)
        # Source appendix views are catalogue pointers; pixels were not inspected in this package.
        loc = f'{PATHS["lothal"]}#{rec};CISI1-L124-216-section;individual-photo-page-unverified'
        self.image(oid, 'cisi1', CISI_URL, loc, 'catalogue_section_pointer', 'individual_photograph_not_reopened', of)

    def museum(self, chosen, of, cf):
        oid = chosen['object_id']
        for j in self.i['joins']:
            if j['family'] != chosen['family'] or chosen['family'] is None:
                continue
            m = next(m for m in self.i['museum'] if m['institution'] + '|' + m['accession'] == j['key'])
            source = 'museum-' + m['record_id']
            self.source(source, 'Collection record ' + m['accession'], [m['institution']], None, 'Online collection catalogue; saved local record', m['url'], 'saved census record, 2026-10-07', 'opened_local_extracted_record; primary_page_not_reopened')
            rec = 'record_id=' + m['record_id']
            aid = self.add(of, oid, 'museum_accession', m['accession'], source, PATHS['museum'], rec, 'accession', m['url'], confidence='identifier-supported')
            self.identifier(oid, 'museum_accession:' + m['institution'], m['accession'], aid, 'saved museum catalogue record')
            self.add(of, oid, 'holding', m['institution'], source, PATHS['museum'], rec, 'institution', m['url'])
            self.add(of, oid, 'material', m['material'], source, PATHS['museum'], rec, 'material', m['url'])
            self.add(of, oid, 'object_type', m['object_type'], source, PATHS['museum'], rec, 'object_type', m['url'])
            self.add(cf, oid, 'site', m['site'], source, PATHS['museum'], rec, 'site', m['url'])
            if m.get('excavation_raw'):
                fa = self.add(of, oid, 'field_identifier', m['excavation_raw'], source, PATHS['museum'], rec, 'excavation_raw', m['url'])
                self.identifier(oid, 'museum_reported_field_identifier', m['excavation_raw'], fa, 'saved museum catalogue record')
            # Unlabelled axes are separate measurements, not matched by axis position.
            dm = str(m.get('dimensions', ''))
            mt = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)(?:\s*[xX×]\s*(\d+(?:\.\d+)?))?\s*(cm|centimeter|centimeters|mm)\s*', dm, re.I)
            if mt:
                factor = 1 if mt[4].casefold() == 'mm' else 10
                for axis in range(1, 4):
                    if mt[axis] is not None and float(mt[axis]) > 0:
                        self.measurement(oid, 'dimension_' + str(axis), float(mt[axis]) * factor, source, PATHS['museum'], rec, 'dimensions', of, m['url'], 'unlabelled_axis; explicit_cm_or_mm_converted_to_mm')
            date = str(m.get('date', ''))
            mt = re.search(r'(\d{3,4})\s*[-–]\s*(\d{3,4})\s*B\.?\s*C', date, re.I)
            if mt:
                old, young = int(mt[1]), int(mt[2])
                if old >= young:
                    self.add(cf, oid, 'calendar_interval', {'bce_oldest': old, 'bce_youngest': young}, source, PATHS['museum'], rec, 'date', m['url'], 'museum_attributed_range; basis_not_independently_verified')
                    self.add(cf, oid, 'dating_basis', 'museum catalogue attribution; dating method unspecified', source, PATHS['museum'], rec, 'date', m['url'], 'own_summary_of_dating_scope')
            self.image(oid, source, m['url'], PATHS['museum'] + '#' + rec + ';image_slots=' + str(m['image_slots']), 'museum_record_image_pointer', 'image_slot_reported; photograph_not_reopened', of)
            ja = self.assertion(oid, 'identity_join', j['key'], 'census_v6', PATHS['joins'], 'key=' + j['key'], 'family,source_evidence', j['source_evidence'], j['method'], 'identifier-supported')
            self.d['relationships'].append({'id': f'J-{len(self.d["relationships"]) + 1:05d}', 'object_id': oid, 'source_id': source, 'external_record': m['record_id'], 'relation': 'same_reported_object', 'status': 'confirmed', 'method': j['method'], 'assertion_id': ja})
            pair = next((p for p in self.i['pairs'] if p['key'] == j['key']), None)
            self.comparisons.append({'object_id': oid, 'museum_key': j['key'], 'adjudication': pair['comparison'] if pair else None, 'missing_reason': None if pair else 'v6_additional_pair_not_adjudicated', 'evidence': PATHS['pairs'] + '#key=' + j['key'] if pair else PATHS['joins'] + '#key=' + j['key']})

    def populate(self):
        for chosen in self.s['objects']:
            oid = chosen['object_id']
            of = {f: empty() for f in OBJECT_FIELDS}
            cf = {f: empty() for f in CONTEXT_FIELDS}
            of['authenticity'] = empty('no_independent_authenticity_assessment_in_inspected_records')
            cf['dating_sample'] = empty('no_object_associated_dating_sample_link_in_inputs')
            self.corpus(chosen, of, cf)
            self.harappa(chosen, of, cf)
            self.lothal(chosen, of, cf)
            self.museum(chosen, of, cf)
            # Mayig is a distinct annotation layer; its face mapping remains unverified.
            for f in self.i['mayig']:
                if cisi(f['object_family_id']) == chosen['catalogue_key'] and chosen['catalogue_key']:
                    self.transcription(oid, f, 'mayig', of)
                    aid = self.assertion(oid, 'identity_join', f['object_family_id'], 'mayig', PATHS['mayig'], f['record_id'], 'object_family_id', method='same_unique_catalogue_base; face_alignment_unverified', confidence='identifier-supported')
                    self.d['relationships'].append({'id': f'J-{len(self.d["relationships"]) + 1:05d}', 'object_id': oid, 'source_id': 'mayig', 'external_record': f['record_id'], 'relation': 'alternative_annotation_of_reported_object', 'status': 'confirmed', 'method': 'catalogue_base', 'assertion_id': aid})
            self.d['objects'].append({'id': oid, 'selection_key': chosen['key'], 'identity_status': 'identifier-supported' if chosen['catalogue_key'] else 'source-reported', 'fields': of})
            self.d['contexts'].append({'id': 'C-' + oid, 'object_id': oid, 'fields': cf})
        self.candidate_links()
        self.corrections()
        return self.d

    def candidate_links(self):
        museum = {m['record_id']: m for m in self.i['museum']}
        objects = {o['id']: o for o in self.d['objects']}
        for c in self.i['candidates']:
            m = museum[c['record_id']]
            pool = [r for r in self.s['objects'] if site(r['site']) == site(m['site']) and coarse(r['type']) == coarse(m['object_type'])]
            if not 1 <= len(pool) <= 5:
                continue
            source = 'museum-' + m['record_id']
            self.source(source, 'Collection record ' + m['accession'], [m['institution']], None, 'Online collection catalogue; saved local record', m['url'], 'saved census record, 2026-10-07', 'opened_local_extracted_record; candidate_identity')
            for r in pool:
                oid = r['object_id']
                aid = self.assertion(oid, 'candidate_identity_join', m['accession'], source, PATHS['museum'], 'record_id=' + m['record_id'], 'site,object_type,accession', m['url'], 'site_and_coarse_type_search_bucket; no_identity_acceptance', 'candidate')
                self.identifier(oid, 'museum_accession:' + m['institution'], m['accession'], aid, 'saved museum catalogue record', status='candidate')
                self.d['relationships'].append({'id': f'J-{len(self.d["relationships"]) + 1:05d}', 'object_id': oid, 'source_id': source, 'external_record': m['record_id'], 'relation': 'possible_same_object', 'status': 'candidate', 'method': 'site_and_coarse_type_bucket_at_most_five_selected_objects', 'assertion_id': aid})

    def corrections(self):
        # Site-level qualifications are overlays, never copied into individual contexts.
        aliases = {'Pabumath': 'Pabumath', 'Chanhu-daro': 'Chanhu-daro', 'Rohira': 'Rohira'}
        for c in self.i['corrections']['corrections']:
            named = c['site_or_source']
            ids = [r['object_id'] for r in self.s['objects'] if any(site(r['site']) == site(s.strip()) for s in named.split(' and '))]
            if not ids:
                continue
            action = 'site_scope_qualification_preserved; no_object_field_inferred'
            if c['id'] == 'B3-V6-050':
                action = 'production_and_findspot_roles_kept_separate; Dilmun_export_site_not_treated_as_confirmed_Ur_findspot'
            if c['id'] == 'B3-V6-035':
                action = 'CISI_holdings_are_dated_snapshots; no_current_holding_inferred_from_site_row'
            self.d['correction_overlays'].append({'id': 'O-' + c['id'], 'object_ids': ids, 'source_id': 'census_v6', 'correction_id': c['id'], 'affected_fields': c['fields'], 'locator': PATHS['corrections'] + '#id=' + c['id'] + ';' + c['primary_locator'], 'applied_action': action, 'status': 'Exploratory; attributed_review_qualification'})
        # The selected Dilmun carrier has a raw BM key, but the source audit leaves
        # its physical join unresolved. Preserve the candidate findspot without merging.
        for r in self.s['objects']:
            if r['key'] == 'BM-123208':
                ctx = next(c for c in self.d['contexts'] if c['object_id'] == r['object_id'])
                ctx['fields']['findspot_site'] = empty('candidate_Ur_findspot; BM123208_to_export_family_not_independently_reviewed')
                self.assertion(r['object_id'], 'findspot_site', 'Ur', 'census_v6', PATHS['corrections'], 'id=B3-V6-050', 'primary_locator', 'Gadd reprint pp.13–14; source audit requires family review', 'inherited_candidate_findspot_role', 'candidate')
                self.assertion(r['object_id'], 'reported_production_place', 'Dilmun', 'census_v6', PATHS['external'], 'site=Dilmun', 'identity', 'Gadd reprint pp.13–14', 'inherited_candidate_production_role', 'candidate')

    def attach_helsinki_layer(self, path):
        """Attach interface-accepted rows without redistributing glyph payloads."""
        from import_helsinki1979 import import_rows
        p = Path(path).resolve()
        if not p.is_relative_to(RAW):
            raise ValueError('Accepted layer must be stored in the package local raw directory')
        rows = json.loads(p.read_text(encoding='utf-8'))
        if any(r.get('status') == 'Synthetic' for r in rows):
            raise ValueError('Synthetic fixtures cannot enter the archaeological ledger')
        # Revalidate each accepted row against its complete original concordance.
        text_rows = [{'edition_id': r['source_edition'], 'text_number': r['source_text_number'], 'segment_id': r['concordance'].get('segment_id', 'whole-source-row'), 'inventory': r['inventory'], 'inventory_version': r['inventory_version'], 'source_page': r['source_page'], 'glyph_tokens': r['glyph_tokens'], 'auxiliary_markers': r['auxiliary_markers'], 'order': r['order'], 'boundary_status': r['boundary_status'], 'rights': r['rights'], 'digitization_version': r['digitization_version'], 'review_status': r['review_status']} for r in rows]
        accepted, rejected = import_rows(text_rows, [r['concordance'] for r in rows], self.d)
        if rejected:
            raise ValueError('Accepted layer no longer validates against this ledger')
        relpath = str(p.relative_to(ROOT)).replace('\\', '/')
        ids = {t['id'] for t in self.d['transcriptions']}
        for row in accepted:
            tid, oid = row['transcription_id'], row['object_id']
            if tid in ids:
                raise ValueError('Duplicate transcription identity in 1979 layer')
            ids.add(tid)
            tf = {f: empty() for f in TRANSCRIPTION_FIELDS}
            rec = 'transcription_id=' + tid
            for field, val, original in [('length', len(row['glyph_tokens']), 'glyph_tokens; plotted units, not lost ancient extent'), ('order', row['order'], 'order'), ('boundaries', row['boundary_status'], 'boundary_status'), ('inventory_version', row['inventory_version'], 'inventory_version')]:
                self.add(tf, oid, field, val, 'helsinki1979', relpath, rec, original, 'source PDF page=' + str(row['source_page']), 'reviewed_import_interface_metadata')
            tf['damage'] = empty('auxiliary_markers_retained_locally; damage_boolean_requires_edition_specific_mapping')
            rid = f'R-{len(self.d["rights"]) + 1:05d}'
            aid = self.assertion(oid, 'license', 'CC-BY-4.0', 'helsinki1979', relpath, rec, 'rights.license', 'http://hdl.handle.net/10138/342677', 'accepted_attribution_and_transformation_record')
            self.d['rights'].append({'id': rid, 'source_id': 'helsinki1979', 'asset_ref': tid, 'status': 'explicit-license', 'license': cell('CC-BY-4.0', [aid]), 'scope': '1979 digitized transcription; attribution retained in local layer', 'disposition': 'local-only', 'notice_locator': 'research/corpus/primary/koskenniemi_parpola1979_provenance.json'})
            self.d['transcriptions'].append({'id': tid, 'object_id': oid, 'surface_id': row['surface_id'], 'source_id': 'helsinki1979', 'inventory': row['inventory'], 'source_version': row['digitization_version'], 'rights_id': rid, 'payload_disposition': 'local-only', 'fields': tf})
            self.raw_transcriptions.append({'transcription_id': tid, 'source_id': 'helsinki1979', 'source_record': row})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selection', required=True)
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--raw-dir', required=True)
    ap.add_argument('--helsinki-layer', help='interface-accepted local raw JSON; never synthetic fixtures')
    a = ap.parse_args()
    sp = (ROOT / a.selection).resolve()
    selection = json.loads(sp.read_text(encoding='utf-8'))
    if digest(OWN / 'PROTOCOL.md') != selection['protocol_sha256']:
        raise ValueError('Frozen protocol changed; write a new explicit amendment/selection')
    for path, meta in selection['input_manifest'].items():
        if digest(ROOT / path) != meta['sha256']:
            raise ValueError('Frozen input changed: ' + path)
    b = Builder(selection, load_inputs(), sp)
    ledger = b.populate()
    if a.helsinki_layer:
        b.attach_helsinki_layer(a.helsinki_layer)
    out = fresh(a.output_dir, OWN)
    raw = fresh(a.raw_dir, RAW)
    write(out / 'ledger-public.json', ledger)
    write(out / 'museum-comparisons.json', b.comparisons)
    lookups = [{'object_id': oid, 'lookup_count': len(records), 'locators': [{'path': p, 'record': r} for p, r in sorted(records)]} for oid, records in sorted(b.lookups.items())]
    write(out / 'source-lookups.json', lookups)
    with gzip.open(raw / 'ledger-full.json.gz', 'wt', encoding='utf-8') as f:
        json.dump({'public_layer': ledger, 'local_transcription_payloads': b.raw_transcriptions}, f, ensure_ascii=False)
    write(out / 'build-manifest.json', {'status': 'Exploratory', 'selection_sha256': digest(sp), 'input_manifest': selection['input_manifest'], 'code_manifest': {p.name: digest(p) for p in OWN.glob('*.py')}, 'protocol_sha256': selection['protocol_sha256'], 'local_full_register': str((raw / 'ledger-full.json.gz').relative_to(ROOT)), 'tables': {k: len(v) for k, v in ledger.items() if isinstance(v, list)}})
    if a.helsinki_layer:
        write(out / 'helsinki-layer-manifest.json', {'path': str(Path(a.helsinki_layer).resolve().relative_to(ROOT)), 'sha256': digest(a.helsinki_layer), 'transcriptions': sum(t['source_id'] == 'helsinki1979' for t in ledger['transcriptions']), 'status': 'Exploratory'})
    # Preserve the exact executable source without putting copied source payloads here.
    import shutil
    (out / 'code').mkdir()
    for p in OWN.glob('*.py'):
        shutil.copy2(p, out / 'code' / p.name)
    print({'objects': len(ledger['objects']), 'transcriptions': len(ledger['transcriptions']), 'assertions': len(ledger['assertions'])})

if __name__ == '__main__':
    main()
