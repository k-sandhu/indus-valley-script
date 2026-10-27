"""Integrate held-source reviews without changing the parent register or its IDs."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'data/raw/2026-10-22-object-register/run-v2'
SCHEMA = ROOT / 'experiments/2026-10-22-object-register/schema-v2.json'
RAW = ROOT / 'data/raw/2026-10-22-evidence-integration'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def lines(path, values):
    with Path(path).open('w', encoding='utf-8', newline='\n') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')


def unique(values, field, count=None):
    indexed = {row[field]: row for row in values}
    if len(indexed) != len(values) or (count is not None and len(values) != count):
        raise ValueError(f'{field}: wrong population or duplicate identifiers')
    return indexed


def layout_accepted(face, adjudication):
    return bool(face['accepted_for_physical_layout'] and adjudication['accepted_for_physical_layout'])


def order_accepted(face, adjudication):
    return bool(layout_accepted(face, adjudication) and face['accepted_for_segment_order']
                and adjudication['accepted_for_segment_order'])


class Integration:
    def __init__(self):
        self.data = read(BASE / 'register-v2.json')
        self.objects = unique(rows(BASE / 'objects.jsonl'), 'object_id', 4695)
        self.faces = unique(rows(BASE / 'faces.jsonl'), 'face_id', 5680)
        self.surfaces = {x['id']: x for x in self.data['surfaces']}
        self.values = []
        self.changes = []
        self.inputs = {}
        self.events = []

    def source(self, name, path, title):
        path = Path(path)
        source_id = 'review:' + name
        self.inputs[rel(path)] = sha(path)
        self.data['sources'].append({
            'id': source_id, 'title': title,
            'authors': ['The project; Codex GPT-6 family, desktop collaboration harness'],
            'year': 2026, 'year_missing_reason': None,
            'venue': 'Held-source review package', 'url': rel(path), 'version': sha(path),
            'access_status': 'local-only detailed review; provisional AI source observation',
            'quoted_words': 0, 'creator_role': 'repository contributor',
        })
        return source_id

    def assertion(self, oid, field, value, sid, path, record, status='observed', confidence='derived'):
        if oid not in self.objects:
            raise ValueError('Unknown object: ' + oid)
        aid = f'EI-A-{len(self.values)+1:06d}'
        locator = {'path': rel(path), 'record': str(record), 'field': field,
                   'page_or_url': None, 'page_missing_reason': 'primary locators retained in linked review record'}
        self.data['assertions'].append({
            'id': aid, 'object_id': oid, 'field': field, 'value': value,
            'source_id': sid, 'locator': locator,
            'method': 'held-source review; see linked record and frozen observations',
            'confidence': confidence, 'review_status': 'not-expert-reviewed',
        })
        self.values.append({'assertion_id': aid, 'object_id': oid, 'field': field,
                            'raw_value': value, 'normalized_value': value,
                            'value_status': status, 'uncertainty': 'provisional AI review; expert acceptance pending',
                            'source_id': sid, 'source_sha256': sha(path), 'locator': locator,
                            'join_status': 'source-qualified review'})
        return aid

    def face_reviews(self, review_path, adjudication_path):
        reviews = unique(rows(review_path), 'face_id', 29)
        decisions = unique(rows(adjudication_path), 'face_id', 29)
        if set(reviews) != set(decisions):
            raise ValueError('Face review and independent adjudication populations differ')
        sid = self.source('face-adjudication', adjudication_path, 'Independent face-layout adjudication')
        self.inputs[rel(review_path)] = sha(review_path)
        for fid, review in reviews.items():
            decision = decisions[fid]
            for witness in review['image_witnesses']:
                image_path = ROOT / witness['path']
                if sha(image_path) != witness['sha256']:
                    raise ValueError('Changed reviewed image: ' + witness['path'])
                self.inputs[witness['path']] = witness['sha256']
            for sealed in decision['first_pass_records']:
                if sha(ROOT / sealed['path']) != sealed['sha256']:
                    raise ValueError('Sealed independent observation changed')
            code_sheet = decision['inspected_code_sheet']
            self.inputs[code_sheet] = sha(ROOT / code_sheet)
            face = self.faces[fid]
            oid = face['object_id']
            accepted = layout_accepted(review, decision)
            order = order_accepted(review, decision)
            if order and list(decision['independent_segment_to_group'].values()) != review['source_alignment']['segment_to_group']:
                raise ValueError('Independent segment maps disagree: ' + fid)
            for path_key, hash_key in [('source_path','source_sha256'), ('source_font_path','source_font_sha256')]:
                alignment = review['source_alignment']
                alignment_path, digest = alignment[path_key], alignment[hash_key]
                if alignment_path not in self.inputs and sha(ROOT / alignment_path) != digest:
                    raise ValueError('Source alignment input changed: ' + alignment_path)
                self.inputs[alignment_path] = digest
            value = {'face_id': fid, 'layout_reviewed': True,
                     'accepted_for_physical_layout': accepted, 'accepted_for_segment_order': order,
                     'arrangement': review['observations']['arrangement'],
                     'segment_to_group': review['source_alignment']['segment_to_group'] if order else None,
                     'linguistic_reading_order': None,
                     'review_status': 'provisional AI source observation',
                     'unresolved_reasons': decision['unresolved_reasons']}
            aid = self.assertion(oid, 'surface.layout_review', value, sid, adjudication_path, fid,
                                 status='observed' if accepted else 'unknown')
            face['layout_review'] = {**value, 'assertion_ids': [aid], 'review_path': rel(review_path),
                                     'adjudication_path': rel(adjudication_path)}
            if accepted:
                arrangement = review['observations']['arrangement']
                aa = self.assertion(oid, 'surface.arrangement', arrangement, sid, adjudication_path, fid)
                old = deepcopy(self.surfaces[fid]['fields']['arrangement'])
                self.surfaces[fid]['fields']['arrangement'] = {
                    'value': arrangement, 'assertion_ids': [aa], 'missing_reason': None}
                self.changes.append({'entity_id': fid, 'field': 'surface.arrangement',
                                     'before': old, 'after': self.surfaces[fid]['fields']['arrangement'],
                                     'evidence_assertion_id': aa})
                self.data['correction_overlays'].append({
                    'id': f'EI-C-{fid}', 'object_ids': [oid], 'source_id': sid,
                    'correction_id': decision['adjudication_id'], 'affected_fields': ['surface.arrangement'],
                    'locator': rel(adjudication_path) + '#' + fid,
                    'applied_action': 'Add independent spatial-layout review; preserve earlier source assertion',
                    'status': 'provisional AI review; expert acceptance pending'})
            face['exposure_status'] = 'image-displayed-to-current-reviewers'
            face['exposure_review'] = {'scope': 'exact held face image or identified panel',
                                       'participants': ['integrating contributor', 'face reviewer'],
                                       'new_confirmation_eligible': False,
                                       'record': rel(adjudication_path) + '#' + fid}
            self.objects[oid]['exposure_status'] = 'at-least-one-face-displayed-to-current-reviewers'
            self.objects[oid].setdefault('reviewed_face_ids', []).append(fid)
            self.events.append({'event_id': f'EI-EXPOSURE-{fid}', 'date': '2026-10-22',
                                'object_id': oid, 'face_id': fid,
                                'participants': ['integrating contributor', 'face reviewer'],
                                'method': 'actual image display through view_image',
                                'scope': 'visual review of identified face or panel',
                                'evidence_path': rel(adjudication_path),
                                'confirmation_eligible': False})
        return list(reviews.values())

    def candidate_reviews(self, path, event_path):
        reviews = rows(path)
        unique(reviews, 'source_row_id', 358)
        events = rows(event_path)
        event_ids = set(unique(events, 'event_id'))
        sid = self.source('candidate-identity-exposure', path, 'Candidate identity and exposure metadata review')
        self.inputs[rel(event_path)] = sha(event_path)
        for review in reviews:
            rid = review['source_row_id']
            if review['confirmation_eligible'] is not False:
                raise ValueError('Source audit cannot establish confirmation eligibility')
            matched_ids = {event['event_id'] for event in review['exposure_events']}
            source_only = set(review['source_level_event_ids_without_page_overlap'])
            if not (matched_ids | source_only) <= event_ids:
                raise ValueError('Candidate links missing exposure event')
            supported = set(review['supported_candidate_family_ids'])
            candidates = set(review['unresolved_candidate_family_ids']) - supported
            for oid in sorted(supported | candidates):
                if oid not in self.objects:
                    raise ValueError('Candidate links missing object: ' + oid)
                value = {'source_row_id': rid, 'identity_status': review['identity_status'],
                         'relation_status': 'source-identifier-supported' if oid in supported else 'candidate',
                         'physical_identity_status': 'provisional; no families merged',
                         'reviewed_exposure_status': review['reviewed_exposure_status'],
                         'page_mapping_status': review['page_mapping_status'],
                         'participant_scope': review['participant_scope'],
                         'exposure_event_ids': sorted(matched_ids),
                         'object_specific_content_verified': False,
                         'confirmation_eligible': False}
                aid = self.assertion(oid, 'candidate.identity_exposure_review', value, sid, path, rid,
                                     status='inferred', confidence='identifier-supported' if oid in supported else 'candidate')
                self.data['relationships'].append({
                    'id': f'EI-REL-{rid}-{oid}', 'object_id': oid, 'source_id': sid,
                    'external_record': rid, 'relation': 'candidate_inventory_row_to_provisional_family',
                    'status': 'confirmed' if oid in supported else 'candidate',
                    'method': 'source-qualified identifier review; physical identity remains provisional',
                    'assertion_id': aid})
                self.objects[oid].setdefault('candidate_reviews', []).append({
                    'source_row_id': rid, 'assertion_id': aid,
                    'supported_relation': oid in supported, 'review_path': rel(path)})
        self.events.extend(events)
        self.historical_event_count = len(events)
        return reviews

    def supplemental_reviews(self, path):
        decisions = rows(path)
        sid = self.source('supplemental-image-review', path, 'Caption, duplicate-image and face-side review')
        for decision in decisions:
            fid, oid = decision['face_id'], decision['object_id']
            face = self.faces[fid]
            if face['object_id'] != oid:
                raise ValueError('Supplemental face belongs to another object')
            source_path = ROOT / decision['source_review']
            self.inputs[rel(source_path)] = sha(source_path)
            aid = self.assertion(oid, 'surface.image_identity_review', decision, sid, path, fid, status='inferred')
            face['image_identity_review'] = {**decision, 'assertion_id': aid}
            selected = set(decision['accepted_paths'])
            if selected - {link['path'] for link in face['image_links']}:
                raise ValueError('Reviewed side link absent from inherited object images')
            for link in face['image_links']:
                if link['path'] not in selected:
                    continue
                old = deepcopy(link)
                digest = sha(ROOT / link['path'])
                if digest != link['sha256']:
                    raise ValueError('Reviewed image differs from inherited image')
                self.inputs[link['path']] = digest
                link.update({'side_match': True, 'join_status': 'source-reviewed-provisional-face-link',
                             'review_assertion_id': aid, 'review_status': decision['review_status'],
                             'source_image_payload_id': 'SHA256:' + digest})
                self.changes.append({'entity_id': fid, 'field': 'image_links', 'before': old,
                                     'after': deepcopy(link), 'evidence_assertion_id': aid})
                for image in self.data['images']:
                    if image['object_id'] == oid and image['url'] == link['path']:
                        image['inspection_status'] = decision['review_status']
                        image['surface_alignment'] = {'value': decision, 'assertion_ids': [aid], 'missing_reason': None}
            face['exposure_status'] = decision['exposure_status']
            if selected:
                self.objects[oid]['exposure_status'] = 'at-least-one-face-displayed-to-current-reviewers'
                self.objects[oid].setdefault('reviewed_face_ids', []).append(fid)
            self.events.append({'event_id': 'EI-SUPPLEMENTAL-EXPOSURE-' + fid, 'date': '2026-10-22',
                                'object_id': oid, 'face_id': fid,
                                'participants': ['integrating contributor', 'face reviewer'],
                                'method': 'actual image display through view_image',
                                'scope': 'identified face' if selected else 'candidate face; assignment unresolved',
                                'evidence_path': rel(path), 'confirmation_eligible': False})
        return decisions


def validate_core(data):
    import jsonschema
    errors = [e.json_path + ': ' + e.message for e in jsonschema.Draft202012Validator(read(SCHEMA)).iter_errors(data)]
    maps = {key: {row['id']: row for row in values} for key, values in data.items() if isinstance(values, list)}
    all_ids = [row['id'] for values in data.values() if isinstance(values, list) for row in values]
    if len(all_ids) != len(set(all_ids)):
        errors.append('duplicate IDs')
    def inspect(value, owner):
        if isinstance(value, dict):
            if set(value) == {'value', 'assertion_ids', 'missing_reason'}:
                assertions = [maps['assertions'].get(a) for a in value['assertion_ids']]
                if any(a is None or (owner and a['object_id'] != owner) for a in assertions):
                    errors.append('broken or foreign assertion')
                elif value['value'] is not None:
                    if value['value'] not in [a['value'] for a in assertions]:
                        errors.append('accepted value without assertion')
                    if any(a['confidence'] == 'candidate' for a in assertions):
                        errors.append('candidate assertion in accepted field')
            for item in value.values():
                inspect(item, owner)
        elif isinstance(value, list):
            for item in value:
                inspect(item, owner)
    for table, values in data.items():
        if not isinstance(values, list):
            continue
        for row in values:
            owner = row.get('object_id') or (row['id'] if table == 'objects' else None)
            inspect(row, owner)
            for field, target in [('object_id','objects'), ('source_id','sources'), ('assertion_id','assertions'), ('rights_id','rights')]:
                if field in row and row[field] not in maps[target]:
                    errors.append(f'{row["id"]}: missing {field}')
            if table == 'assertions' and not (ROOT / row['locator']['path']).is_file():
                errors.append('missing assertion source: ' + row['id'])
    base = read(BASE / 'register-v2.json')
    for table in ['objects', 'contexts', 'surfaces', 'images', 'identifiers', 'measurements', 'rights']:
        if {r['id'] for r in data[table]} != {r['id'] for r in base[table]}:
            errors.append('changed population: ' + table)
    if data['assertions'][:len(base['assertions'])] != base['assertions']:
        errors.append('parent assertions changed')
    return sorted(set(errors))


def build(args):
    out, summary = Path(args.out), Path(args.summary)
    if not out.is_absolute(): out = ROOT / out
    if not summary.is_absolute(): summary = ROOT / summary
    if out.exists() or summary.exists():
        raise ValueError('Choose new output and summary directories; frozen outputs are never replaced')
    paths = {name: ROOT / getattr(args, name) for name in ['faces', 'adjudications', 'candidates', 'events', 'senses', 'compounds']}
    for path in paths.values():
        if not path.is_file(): raise ValueError('Missing completed review: ' + rel(path))
    integration = Integration()
    parent_hashes = {p.name: sha(p) for p in sorted(BASE.iterdir()) if p.is_file()}
    face_reviews = integration.face_reviews(paths['faces'], paths['adjudications'])
    supplemental_path = RAW / 'supplemental-adjudications.jsonl'
    supplemental = integration.supplemental_reviews(supplemental_path)
    candidates = integration.candidate_reviews(paths['candidates'], paths['events'])
    senses, compounds = rows(paths['senses']), rows(paths['compounds'])
    unique(senses, 'form', 24)
    unique(compounds, 'entry_id', 43)
    freeze_path = ROOT / 'experiments/2026-10-22-lexical-source-review/FREEZE.json'
    freeze = read(freeze_path)
    selected = {row['sample_id']: row['entry_id'] for row in freeze['selected_row_ids']}
    reviewed_sample = {row['sample_id']: row['entry_id'] for row in compounds if row['sample_id'] in selected}
    if reviewed_sample != selected:
        raise ValueError('Compound source review differs from frozen sample')
    for path in [*paths.values(), RAW / 'root-visual-pass.jsonl', RAW / 'root-supplemental-review.jsonl',
                 ROOT / 'data/raw/2026-10-22-face-adjudication/visual-pass-1.json',
                 HERE / 'PROTOCOL.md', HERE / 'VISUAL-PASS-FREEZE.json', freeze_path, Path(__file__), SCHEMA]:
        integration.inputs[rel(path)] = sha(path)
    errors = validate_core(integration.data)
    if errors: raise ValueError('\n'.join(errors))
    for name, expected in parent_hashes.items():
        if sha(BASE / name) != expected: raise ValueError('Parent changed during integration: ' + name)
    out.mkdir(parents=True)
    summary.mkdir(parents=True)
    dump(out / 'register-v2.json', integration.data)
    lines(out / 'objects.jsonl', integration.objects.values())
    lines(out / 'faces.jsonl', integration.faces.values())
    for name in ['missing-values.jsonl', 'join-queue.jsonl', 'cisi-reader-decisions.jsonl']:
        shutil.copyfile(BASE / name, out / name)
    # Preserve inherited detailed assertions byte for byte and append the new rows.
    shutil.copyfile(BASE / 'assertion-values.jsonl', out / 'assertion-values.jsonl')
    with (out / 'assertion-values.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
        for row in integration.values:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    for name, key in [('candidate-reviews.jsonl', 'candidates'), ('face-reviews.jsonl', 'faces'),
                      ('face-adjudications.jsonl', 'adjudications'), ('lexical-sense-review.jsonl', 'senses'),
                      ('lexical-compound-review.jsonl', 'compounds')]:
        shutil.copyfile(paths[key], out / name)
    lines(out / 'exposure-events.jsonl', integration.events)
    lines(out / 'changes.jsonl', integration.changes)
    shutil.copyfile(supplemental_path, out / 'supplemental-adjudications.jsonl')
    accepted = [face for face in integration.faces.values() if face.get('layout_review', {}).get('accepted_for_physical_layout')]
    accepted_order = [face for face in accepted if face['layout_review']['accepted_for_segment_order']]
    coverage = {
        'register_release': 'held-source-review-2026-10-22-v1', 'core_schema_version': '2.0',
        'parent_register': rel(BASE), 'objects': len(integration.objects), 'faces': len(integration.faces),
        'base_assertions': 225223, 'added_assertions': len(integration.values),
        'total_assertions': len(integration.data['assertions']),
        'reviewed_faces': len(face_reviews), 'accepted_spatial_layouts_provisional': len(accepted),
        'unresolved_spatial_layouts': len(face_reviews)-len(accepted),
        'accepted_export_segment_orders_provisional': len(accepted_order),
        'linguistic_reading_orders_authenticated': 0,
        'reviewed_candidate_rows': len(candidates),
        'candidate_rows_with_supported_family_relation': sum(bool(r['supported_candidate_family_ids']) for r in candidates),
        'candidate_rows_with_new_supported_family_relation': sum(bool(r['new_supported_family_ids']) for r in candidates),
        'candidate_identity_status': dict(Counter(r['identity_status'] for r in candidates)),
        'candidate_exposure_status': dict(Counter(r['reviewed_exposure_status'] for r in candidates)),
        'candidate_page_mapping_status': dict(Counter(r['page_mapping_status'] for r in candidates)),
        'candidate_exposure_documentation_records': integration.historical_event_count,
        'current_face_review_exposure_records': len(integration.events)-integration.historical_event_count,
        'supplemental_face_review_records': len(supplemental),
        'restored_provisional_face_image_links': sum(len(r['accepted_paths']) for r in supplemental),
        'restored_distinct_image_payloads': len({sha(ROOT / p) for r in supplemental for p in r['accepted_paths']}),
        'physical_family_merges': 0, 'confirmation_eligible_candidates': 0,
        'lexical_form_reviews': len(senses), 'compound_review_rows_including_diagnostics': len(compounds),
        'lexical_scope': 'Separately versioned source review; no archaeological meaning assertions added',
    }
    manifest = {'parent': rel(BASE), 'parent_output_hashes': parent_hashes,
                'inputs': [{'path': path, 'sha256': digest} for path, digest in sorted(integration.inputs.items())],
                'outputs': {p.name: sha(p) for p in sorted(out.iterdir())},
                'detailed_output_directory': rel(out), 'source_rights': 'Detailed derivatives remain local-only',
                'review_status': 'provisional AI source review; expert and maintainer acceptance pending'}
    dump(summary / 'coverage.json', coverage)
    dump(summary / 'source-manifest.json', manifest)
    dump(summary / 'validation.json', {'status': 'pass', 'errors': errors,
                                      'schema': 'unchanged version2 core schema',
                                      'population_and_parent_assertions': 'preserved',
                                      'review_joins_and_event_references': 'checked',
                                      'primary_source_interpretations': 'provisional AI review',
                                      'output_local_dir': rel(out),
                                      'output_hashes': manifest['outputs']})
    print(json.dumps(coverage, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['out', 'summary', 'faces', 'adjudications', 'candidates', 'events', 'senses', 'compounds']:
        parser.add_argument('--' + name, required=True)
    build(parser.parse_args())


if __name__ == '__main__':
    main()
