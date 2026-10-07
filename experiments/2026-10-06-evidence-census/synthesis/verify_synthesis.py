"""Read-only verification of synthesis outputs, pins and source-sample witnesses."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--endpoint', default='experiments/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6')
    ap.add_argument('--compare', help='Optional independently rebuilt endpoint')
    ap.add_argument('--output', help='New verification JSON inside owned directory')
    args = ap.parse_args()
    endpoint = (ROOT / args.endpoint).resolve()
    if not endpoint.is_relative_to(OWN):
        raise ValueError('Endpoint outside owned directory')
    checks = []
    def check(label, passed):
        checks.append({'check': label, 'passed': bool(passed)})
    pins = load(endpoint / 'input-manifest.json')
    for rel, metadata in pins.items():
        p = ROOT / rel
        check('input_pin:' + rel, p.exists() and sha256(p.read_bytes()).hexdigest() == metadata['sha256'])
    c = load(endpoint / 'coverage.json')
    csv_rows = list(csv.DictReader((endpoint / 'coverage.csv').open(encoding='utf-8')))
    check('coverage_csv_rows', len(csv_rows) == len(c['sites']))
    for a, b in zip(c['sites'], csv_rows):
        for key in ['site', 'assigned_region']:
            check('CSV:' + a['site'] + ':' + key, a[key] == b[key])
        for key in ['local_faces', 'local_families', 'local_cisi_identifiers']:
            check('CSV:' + a['site'] + ':' + key, a[key] == int(b[key]))
        for key in ['catalogue_runs', 'published_count_assertions', 'evidence']:
            check('CSV:' + a['site'] + ':' + key, a[key] == json.loads(b[key]))
    check('all_computation_checks_passed', load(endpoint / 'checks.json')['status'] == 'Verified computation')
    check('corrected_north_IM77', next(r['IM77_main_selected_objects_available'] for r in c['regions'] if r['region'].startswith('c')) == 117)
    check('BC_absent_section_partition', c['summary']['CISI1_BC_absent_graffiti_or_pottery_sections'] == 75 and c['summary']['CISI1_BC_absent_seal_impression_tablet_other_sections'] == 91)
    fields = list(csv.DictReader((endpoint / 'field-completeness.csv').open(encoding='utf-8')))
    check('twelve_structural_absences', sum(r['measurement'] == 'structural_schema_absence' for r in fields) == 12)
    check('structural_absences_no_percentage', all(r['percent'] == '' for r in fields if r['measurement'] == 'structural_schema_absence'))
    joins = load(endpoint / 'join-summary.json')
    check('expanded_museum_lower_bound', joins['confirmed_identifier_joins'] == 68 and joins['join_count_is_lower_bound'])
    check('expanded_museum_partition', joins['confirmed_identifier_joins'] + joins['unconfirmed_records'] == 114)
    check('unresolved_query_dispositions', sum(joins['unresolved_query_dispositions'].values()) == 46)
    selection = load(OWN / 'sample-selection.json')
    sample = load(OWN / 'source-sample-audit.json')
    check('sample_has_twenty_rows', sample['rows_checked'] == 20 == len(sample['rows']))
    for b in ['a-pakistan-afghanistan', 'b-gujarat-kutch-maharashtra', 'c-north-india', 'd-finds-abroad']:
        check('sample_selection:' + b, sorted(r['site'] for r in sample['rows'] if r['batch'] == b) == sorted(selection[b]))
    sources = load(OWN / 'sources.json')['sources']
    known_sources = {s['id'] for s in sources}
    for row in sample['rows']:
        check('sample_source:' + row['site'], row['source_id'] in known_sources)
    witness_pairs = {(w['source'], w['source_sha256']) for s in sources for w in s['inspected_witnesses']}
    for rel, digest in sorted(witness_pairs):
        check('source_hash:' + rel, (ROOT / rel).exists() and sha256((ROOT / rel).read_bytes()).hexdigest() == digest)
    for source in sources:
        if source['opened_in_B3']:
            check('opened_source_has_witness:' + source['id'], bool(source['inspected_witnesses']))
        check('source_bibliography:' + source['id'], all(source.get(k) for k in ['title', 'authors', 'year', 'venue', 'url']))
        check('no_snippet_title:' + source['id'], len(source['title']) <= 350 and len(source['title'].split()) <= 55)
    if args.compare:
        compare = (ROOT / args.compare).resolve()
        for p in endpoint.iterdir():
            if p.suffix in ['.json', '.csv']:
                if p.suffix == '.json':
                    equal = load(p) == load(compare / p.name)
                else:
                    equal = list(csv.DictReader(p.open(encoding='utf-8'))) == list(csv.DictReader((compare / p.name).open(encoding='utf-8')))
                check('independent_rebuild:' + p.name, equal)
    result = {'status': 'Verified computation' if all(c['passed'] for c in checks) else 'Failed', 'checks_count': len(checks),
              'failed': [c for c in checks if not c['passed']], 'checks': checks}
    if args.output:
        p = (ROOT / args.output).resolve()
        if not p.is_relative_to(OWN) or p.exists():
            raise ValueError('Use a new verification file inside owned directory')
        p.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, indent=2))
    if result['status'] != 'Verified computation':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
