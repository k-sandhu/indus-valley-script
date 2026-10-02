"""Additional source-labelled numeral/filter counts and representative image checks."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    output = BASE / 'filter-supplement-2026-10-02'
    if output.exists():
        raise RuntimeError('Preserve previous source/filter endpoints.')
    output.mkdir()
    corpus_path = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
    observed = [json.loads(line) for line in corpus_path.read_text(encoding='utf-8').splitlines()]
    # VN is the literal derivative text-class label. It nominates a candidate
    # population and supplies no authenticated numerical values to this audit.
    candidate = [row for row in observed if row['metadata']['class'] == 'VN']
    candidate_counts = dict(label='VN', basis='Modern sign-structure category; preserved Wells 2008 definition describes sign 700 plus a numeral.', rows=len(candidate), families=len({row['object_family_id'] for row in candidate}), lengths=dict(Counter(row['length'] for row in candidate)), complete_observed=sum(row['complete_observed'] for row in candidate), clean_rtl_singleline=sum(row['clean_rtl_singleline'] for row in candidate), principal_length_at_least3=sum(row['clean_rtl_singleline'] and row['length'] >= 3 for row in candidate), excluded_from_principal=sum(not (row['clean_rtl_singleline'] and row['length'] >= 3) for row in candidate), definition_source='data/normalized/source_definitions.json: wells2008_text_classes', selected_definition_account='research/corpus/CORPUS_REPORT.md')
    cases = []
    for identifier in ('H-904', 'M-1383'):
        found = [row for row in observed if row['source_cisi'] == identifier]
        cases.append(dict(source_id=identifier, rows=len(found), lengths=dict(Counter(row['length'] for row in found)), eligible_rows=sum(row['clean_rtl_singleline'] and row['length'] >= 3 for row in found), source_premise_record='research/literature/metrology/numerical_source_premises.json', independent_inscription_linked_content_count='unresolved in the reviewed source-premise record'))
    visual_samples = [
        dict(file='M-1_imp_a.jpg', visible='Printed crop shows an animal figure beneath a glyph row; its label is M-1 a. The filename marks an impression witness.', role='Example of pictorial context and inscription present in a local indexed crop.'),
        dict(file='H-904_A.jpg', visible='Small printed crop shows a marked oblong surface with a crescent/U-like central graphic and stroke groups; its label is H-904 A.', role='The crop supplies paired-target graphics; higher-quality Vats source inspection is retained in the numerical-premise audit.'),
        dict(file='L-124_B.jpg', visible='Printed crop shows a broken clay object with irregular rear contact texture; its label is L-124 B.', role='Physical contact witness, with richer views and author interpretation in the original Frenez/Tosi figures.'),
    ]
    for row in visual_samples:
        path = ROOT / 'data/lipi/public/seal_images' / row['file']
        row.update(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=digest(path), inspection_basis='Local pixels displayed and visually inspected in the readiness audit; no copied pixels in this endpoint.')
    context = json.loads((ROOT / 'experiments/2026-10-02-six-hour/context-audit/source-cohorts/results.json').read_text(encoding='utf-8'))
    cohort_counts = {name: dict(published_objects=row['published_bases'], joined_objects=row['matched_bases'], joined_faces=row['matched_faces'], stages=row['stages'], length_distribution=row['face_length_counts'], supplied_direction_distribution=row['directions']) for name, row in context['cohorts'].items() if name != 'targeted_source_cautions'}
    graph_schema = dict(preserved=['object/registration', 'physical face boundary', 'source drawing/photo', 'displayed orientation', 'direct stroke-group count', 'damage region', 'relative source phase', 'dating basis'], unresolved=['physical longitudinal orientation of all three faces', 'source-to-export side alignment', 'individual dimensions for the 22 tablets', 'quantity meaning of stroke groups', 'independently known content count or named referent'])
    result = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), code_sha256=digest(Path(__file__)), corpus_sha256=digest(corpus_path), candidate_filter=candidate_counts, paired_numerical_targets=cases, harappa_source_cohort_filter=cohort_counts, paired_surface_schema=graph_schema, visual_samples=visual_samples, scope='Additional actual-source readiness counts and three purposive image-presence checks; no semantic model fitted, no interpretation labels treated as evaluation answers.')
    checks = [
        dict(check='VN accounting', passed=len(candidate) == 355 and candidate_counts['families'] == 354 and sum(candidate_counts['lengths'].values()) == len(candidate)),
        dict(check='VN principal/excluded partition', passed=candidate_counts['principal_length_at_least3'] == 2 and candidate_counts['excluded_from_principal'] == 353),
        dict(check='copied tablet filter', passed=cohort_counts['incised_tablet_copies']['joined_faces'] == 66 and cohort_counts['incised_tablet_copies']['length_distribution'] == {'2': 66} and cohort_counts['incised_tablet_copies']['stages']['primary_length_at_least3']['faces'] == 0),
        dict(check='source cohort totals', passed=sum(row['published_objects'] for row in cohort_counts.values()) == 69 and sum(row['joined_objects'] for row in cohort_counts.values()) == 60 and sum(row['stages']['primary_length_at_least3']['families'] for row in cohort_counts.values()) == 2),
        dict(check='two eligible paired H904 rows', passed=cases[0]['rows'] == cases[0]['eligible_rows'] == 2),
        dict(check='three visually inspected crops retain hashes', passed=all((ROOT / row['path']).is_file() and digest(ROOT / row['path']) == row['sha256'] for row in visual_samples)),
    ]
    write(output / 'results.json', result)
    write(output / 'verification.json', dict(checks_total=len(checks), checks_passed=sum(row['passed'] for row in checks), checks=checks))
    (output / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(candidate_filter=candidate_counts, checks=len(checks), passed=sum(row['passed'] for row in checks))))


if __name__ == '__main__':
    main()
