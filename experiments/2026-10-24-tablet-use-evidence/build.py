"""Build a bounded physical-use register without opening inscription payloads."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-tablet-use-evidence')
OLD = ROOT / 'experiments/2026-10-02-six-hour/harappa-object-frame'
SOURCE = ROOT / 'research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def main():
    assert RAW.is_dir()
    assert (ROOT / 'data/raw').resolve() == RAW.parent
    assert sha(SOURCE) == '967ebcb058e5611de4089facba852adac418108adfc36bf793d0588ba0d8b751'
    shutil.copy2(SOURCE, RAW / 'meadow-kenoyer2000.pdf')
    old = json.loads((OLD / 'annotated/results.json').read_text(encoding='utf-8'))
    objects = [o for o in old['physical_objects'] if o.get('target_id') in {f'H-{n}' for n in range(2218, 2240)}]
    assert len(objects) == 22
    # Each summary is our paraphrase, not an extracted passage or sign sequence.
    specifications = [
        ('manufacture', 'separately incised steatite, then fired', 'catalogued', 'published-description', [14], 'operation'),
        ('deposit', 'debris outside curtain wall 296, after wall and revetment fill and before Period 3C material', 'catalogued', 'published-description', [14], 'secondary-deposit'),
        ('incision_direction', 'shared cutting direction for each character across the reported group', 'catalogued', 'published-microscopic-mould-observation', [16], 'manufacture-observation'),
        ('incision_sequence', 'shared stroke order within each character across the reported group', 'catalogued', 'published-microscopic-mould-observation', [16], 'manufacture-observation'),
        ('engraver_count', 'at least three engravers', 'inferred', 'published-interpretation-from-moulds', [16], 'manufacture-interpretation'),
        ('single_production_event', None, 'unknown', 'source-presents-simultaneous-and-separated-production-alternatives', [16, 17], 'unresolved-production-history'),
        ('physical_attachment', None, 'unknown', 'not-reported-for-this-block-in-bounded-chapter', list(range(1, 22)), 'use-null'),
        ('container_contents', None, 'unknown', 'not-reported-for-this-block-in-bounded-chapter', list(range(1, 22)), 'use-null'),
        ('independent_quantity', None, 'unknown', 'not-reported-for-this-block-in-bounded-chapter', list(range(1, 22)), 'use-null'),
        ('use_wear', None, 'unknown', 'not-reported-for-this-block; worn-terracotta-on-pdf12-is-a-different-series', list(range(1, 22)), 'use-null'),
        ('physical_cancellation', None, 'unknown', 'not-reported-for-this-block-in-bounded-chapter', list(range(1, 22)), 'use-null'),
        ('pouch_preservation', None, 'unknown', 'pouch-is-proposed-in-reconstruction-not-reported-as-recovered', [18], 'use-null'),
        ('loss_of_validity', 'value or utility had ended before disposal', 'inferred', 'published-functional-interpretation-from-discard', [17, 18], 'use-interpretation'),
        ('non_impression_intent', 'tablets were intended to be read directly', 'inferred', 'authors-assumption-about-use; endnote-discusses-display-transformations', [17, 19, 20], 'use-interpretation'),
    ]
    records = []
    object_rows = []
    for obj in objects:
        specimen = obj['source_coordinate']['specimen']
        association = 'nearby' if specimen in (9, 16) else 'scattered' if specimen in (6, 17, 18, 20) else 'clump'
        row = {'object_id': obj['target_id'], 'source_specimen': specimen,
               'registration': obj['registration'], 'join_status': obj['export_join']['status'],
               'join_basis': obj['export_join']['basis'], 'association': association,
               'association_status': 'catalogued', 'phase': 'late Period 3B',
               'phase_basis': 'relative wall, fill and diagnostic ceramic sequence; no direct object date',
               'deposit_class': 'secondary-dump', 'manufacturing_group': obj['published_engraver_group']['value'],
               'manufacturing_group_status': 'inferred-by-source-authors',
               'museum_accession': None, 'dimensions_mm': None,
               'physical_source_sides_aligned_to_corpus_faces': False}
        object_rows.append(row)
        for field, value, status, basis, pages, relation in specifications:
            records.append({'assertion_id': f'TUE-{specimen:02d}-{field}', 'object_id': obj['target_id'],
                'relation': relation, 'field': field, 'value': value, 'value_status': status,
                'basis': basis, 'source_id': 'meadow-kenoyer2000', 'pdf_pages_one_based': pages,
                'scope': 'published-group-assertion-applied-to-caption-identified-member',
                'observer': 'gpt-6.1-sol; Codex collaboration', 'annotation_version': 'v1'})
    write(RAW / 'objects-v1.json', object_rows)
    write(RAW / 'relations-v1.json', records)
    matrix = Counter((o['manufacturing_group'], o['association']) for o in object_rows)
    summary = {'schema_version': '1.0', 'task': 'source-field-audit', 'synthetic': False,
        'confirmation_access': False, 'source_already_exposed': True,
        'objects': len(object_rows), 'new_objects': 0, 'new_registration_joins': 0,
        'inherited_displayed_faces': 66, 'relation_records': len(records),
        'relations_per_object': len(specifications),
        'association_counts': dict(Counter(o['association'] for o in object_rows)),
        'manufacture_group_by_association': [dict(group=g, clump=matrix[g,'clump'], nearby=matrix[g,'nearby'], scattered=matrix[g,'scattered']) for g in (1,2,3)],
        'source_reported_shared_cutting_direction_objects': 22,
        'source_reported_shared_stroke_order_objects': 22,
        'manufacturing_groups_are_independent_workshops': False,
        'direct_attachment_records': 0, 'direct_content_records': 0,
        'independent_quantity_records': 0, 'reported_use_wear_records_in_this_block': 0,
        'recovered_pouch_records': 0, 'physical_cancellation_records': 0,
        'use_null_assertions': sum(r['relation'] == 'use-null' for r in records),
        'null_means': 'not reported for the named objects in this chapter, not physically absent',
        'prior_credences_changed': False,
        'provenance': {'protocol_sha256': sha(PKG/'PROTOCOL.md'), 'code_sha256': sha(Path(__file__)),
            'source_sha256': sha(SOURCE), 'prior_join_ledger_sha256': sha(OLD/'annotated/results.json'),
            'local_object_register_sha256': sha(RAW/'objects-v1.json'),
            'local_relation_register_sha256': sha(RAW/'relations-v1.json')}}
    write(PKG / 'summary-v1.json', summary)
    assets = []
    for p in sorted(RAW.iterdir()):
        if p.is_file():
            assets.append({'logical_path': 'data/raw/2026-10-24-tablet-use-evidence/'+p.name,
                'physical_path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p),
                'handling': 'local-only', 'rights': 'rights-unverified' if p.suffix in ('.pdf','.png','.txt') else 'project-annotations-with-source-derived-object-keys'})
    write(PKG / 'source-manifest-v1.json', {'schema_version': '1.0',
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'source': {'source_id':'meadow-kenoyer2000', 'authors':['Richard H. Meadow','Jonathan Mark Kenoyer'],
            'year':2000, 'title':"The 'Tiny Steatite Seals' (Incised Steatite Tablets) of Harappa: Some Observations on Their Context and Dating",
            'url':'https://www.harappa.com/sites/default/files/pdf/Kenoyer2000_The%20Tiny%20Steatite%20Seals%20of%20Harappa.pdf',
            'access':'reused held author PDF; canonical PDF independently opened with web tool 2026-10-24',
            'original_acquisition_time':'see prior source-access-log; no new PDF download in this run',
            'original_log':'experiments/2026-10-02-six-hour/harappa-object-frame/source-access-log.json',
            'pages':21, 'rights_status':'rights-unverified', 'rights_basis':'public author-hosted access; no explicit open licence verified'},
        'page_exposure': {'text_extracted_and_inspected_pdf_pages':list(range(1,22)),
            'complete_renders':list(range(14,21)), 'visually_inspected_pdf_pages':[14,16,17,18,19,20],
            'rendered_but_not_visually_inspected_pdf_pages':[15],
            'pagination':'PDF 14 = author p.13 = mapped book p.333; thereafter +319 from PDF page to book page'},
        'transformations':['Poppler pdftotext -layout, whole chapter','Poppler pdftoppm -f 14 -l 20 -r 110 -png',
            'manual source-field adjudication; inherited exact registration joins; no sign-sequence access'],
        'assets':assets})

if __name__ == '__main__':
    main()
