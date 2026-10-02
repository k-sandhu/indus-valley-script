"""Audit source eligibility and direct compatibility for the root sensitivity.

This script does not evaluate the statistical model or inspect restoration
predictions. It writes only inside the corpus workstream.
"""
from pathlib import Path
from collections import defaultdict
import datetime, hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/corpus/independent_annotator_provenance_review.json'

def read_rows(name):
    return [json.loads(x) for x in (ROOT/'data/normalized'/name).read_text(encoding='utf-8').splitlines()]

mayig = read_rows('mayig_faces.jsonl')
lipi = read_rows('lipi_observed_faces.jsonl')
clean = read_rows('lipi_clean_rtl_singleline.jsonl')
schema = json.loads((ROOT/'data/normalized/mayig_sign_schema.json').read_text(encoding='utf-8'))['signs']
cross = json.loads((ROOT/'data/normalized/mayig_wells_class_crosswalk.json').read_text(encoding='utf-8'))['by_mayig_class']
mapping_errors = []
for p, row in cross.items():
    expected = {w.removeprefix('W').zfill(3) for w in schema[p].get('wells_graphemes', [])}
    observed = {w.removeprefix('W').zfill(3) for w in row['wells_candidates']}
    if expected != observed:
        mapping_errors.append(p)
orientation_errors = [r['record_id'] for r in mayig if r['signs_reading_rtl'] != r['signs_visual_ltr'][::-1]]
feature_errors = [r['record_id'] for r in mayig if r['clear_transcription'] != (
    'P000' not in r['signs_visual_ltr'] and r['max_damage'] == 0 and r['max_uncertainty'] == 0)]
eligible = [r for r in mayig if r['clear_transcription'] and r['line_count'] == 1 and r['length'] >= 3]
mapped = [r for r in eligible if all(cross[p]['wells_candidates'] for p in r['signs_reading_rtl'])]

def families(rows):
    return {r['object_family_id'] for r in rows if any(1 <= int(n) <= 199 for n in
            re.findall(r'\bM\s*-?\s*(\d+)', r['source_cisi'], re.I))}

full_families = families(lipi)
eligible_source_families = families([r for r in clean if r['length'] >= 3])
omitted = full_families - eligible_source_families
retained_risk = [r['record_id'] for r in clean if r['length'] >= 3 and r['object_family_id'] in omitted]
cisi_families = defaultdict(set)
for r in lipi:
    m = re.fullmatch(r'([A-Za-z]+)-(\d+)([A-Za-z]*)', r['source_cisi'].strip())
    if m:
        cisi_families[(m[1].upper(), int(m[2]))].add(r['object_family_id'])
conflicting_cisi = [f'{p}-{n}' for (p,n), fs in cisi_families.items() if len(fs) > 1]

row = {
    'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reviewed_source_initial_sha256': '62ae7f9658371f73d3f950212310728c00aeb098e56b6571345d42a0f799e07d',
    'review_scope': 'P-to-W source mapping, order, source eligibility and physical identity logic only. Statistical math is reviewed by the methods workstream.',
    'manual_source_conclusions': [
        'Mayig README says glyphs are recorded left-to-right on seal impressions and normally read right-to-left; reversing the list matches the source convention.',
        'Default damage and uncertainty flags are annotator judgments; P000 must be independently excluded.',
        'P classes and Wells candidate lists are supplied by the same annotator. Whole-class sets deliberately ignore feature vectors and are not exact token-level conversions.',
        'Overlapping P candidate sets are valid fine-code events for sensitivity scoring, but not a transitive sign-equivalence system or necessarily a normalized P-label predictor.',
        'The test uses a second manual annotator of the same CISI photographs. Shared primary artifacts and shared inventory interpretation limit the word independent.',
        'All clear length-eligible rows are considered, rather than only rows compatible with Lipi. This avoids selecting agreement as a prerequisite.'
    ],
    'verification': {
        'crosswalk_P_classes': len(cross),
        'direct_candidate_mapping_errors': mapping_errors,
        'orientation_reversal_errors': orientation_errors,
        'clear_flag_errors': feature_errors,
        'eligible_clear_single_line_length3plus': len(eligible),
        'fully_candidate_mapped_eligible': len(mapped),
        'M1_M199_numeric_families_full_export': len(full_families),
        'M1_M199_numeric_families_clean_length3plus': len(eligible_source_families),
        'source_families_omitted_by_clean_length_filter': len(omitted),
        'clean_length3plus_rows_in_omitted_families': retained_risk,
        'simple_CISI_bases_assigned_multiple_numeric_families': conflicting_cisi
    },
    'recommendation': 'Discover source identities from the full observational export before filtering training rows. The current pinned clean-length scan causes no actual retained eligible rows in the40 omitted source families, but a full-export scan makes the stated rule literal and robust.',
    'source_quality_flags': ['M-140', 'M-81', 'M-181', 'M-62'],
    'flag_limit': 'These are source-photo/catalogue discrepancies, not silently applied corrections. Other unresolved fine-variant or layout issues remain.',
    'input_hashes': {name: hashlib.sha256((ROOT/'data/normalized'/name).read_bytes()).hexdigest() for name in [
        'mayig_faces.jsonl', 'mayig_sign_schema.json', 'mayig_wells_class_crosswalk.json',
        'lipi_observed_faces.jsonl', 'lipi_clean_rtl_singleline.jsonl']}
}
assert not mapping_errors and not orientation_errors and not feature_errors and not retained_risk and not conflicting_cisi
OUT.write_text(json.dumps(row, indent=2)+'\n', encoding='utf-8')
print(json.dumps(row['verification'], indent=2))
