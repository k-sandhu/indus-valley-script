"""Verify the saved census, reference integrity, CSV and acquired witness hashes."""
import argparse, collections, csv, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
OWNED = pathlib.Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true', help='Compare with saved checks; do not write')
    args = parser.parse_args()
    read = lambda name: json.loads((OWNED / name).read_text(encoding='utf-8'))
    rows, source_list, search_list = read('site-rows.json'), read('sources.json'), read('searches.json')
    sources = {x['id']: x for x in source_list}
    searches = {x['id']: x for x in search_list}
    aggregate = read('aggregate-results.json')
    assert len(sources) == len(source_list) and len(searches) == len(search_list)
    with (OWNED / 'site-rows.csv').open(encoding='utf-8', newline='') as handle:
        csv_rows = list(csv.DictReader(handle))
    assert len(csv_rows) == len(rows)
    for row, csv_row in zip(rows, csv_rows):
        assert set(row) == set(csv_row)
        for key, value in row.items():
            if isinstance(value, (list, dict)):
                assert json.loads(csv_row[key]) == value, (row['site'], key)
            else:
                assert csv_row[key] == str(value), (row['site'], key)

    reference_count = 0
    def check_refs(value):
        nonlocal reference_count
        if isinstance(value, dict):
            for key, child in value.items():
                if key == 'source' and isinstance(child, str) and child in sources:
                    reference_count += 1
                elif key == 'source' and isinstance(child, str) and not (ROOT / child).is_file():
                    raise AssertionError('Missing source reference: ' + child)
                elif key in ('sources', 'opened_substantial_source_ids', 'source_ids') and isinstance(child, list):
                    for sid in child:
                        assert sid in sources, sid
                        reference_count += 1
                elif key == 'search_ids':
                    assert all(qid in searches for qid in child)
                check_refs(child)
        elif isinstance(value, list):
            for child in value:
                check_refs(child)
    check_refs(rows)
    for row in rows:
        assert len(set(row['search_ids'])) >= 3
        assert all(searches[qid]['site'] == row['site'] for qid in row['search_ids'])
        assert row['opened_substantial_source_ids']
        assert row['count_comparison']['coverage_fraction'] is None
    assert sum(row['local_corpus']['faces'] for row in rows) == aggregate['local_faces'] == 42
    assert sum(row['published_indus_related_minimum_objects'] for row in rows) == 36
    assert sum(row['final_report_identified'] for row in rows) == 14
    hash_checks = []
    for source in source_list:
        if source.get('raw_pdf'):
            pdf = ROOT / source['raw_pdf']
            assert hashlib.sha256(pdf.read_bytes()).hexdigest() == source['sha256'], source['id']
            hash_checks.append(source['id'])
    used = {sid for row in rows for sid in row['sources']}
    result = dict(status='Verified computation', rows=len(rows), csv_round_trip=True,
                  source_and_search_references_resolve=True, checked_source_references=reference_count,
                  acquired_pdf_hashes_checked=sorted(hash_checks),
                  sources_associated_with_rows=len(used),
                  used_source_access_counts=dict(sorted(collections.Counter(sources[x]['access'] for x in used).items())),
                  query_minimum=min(len(row['search_ids']) for row in rows),
                  limitations='Source access and archaeological classifications remain curated assertions; reference and hash checks do not validate their interpretation.')
    payload = (json.dumps(result, indent=2) + '\n').encode('utf-8')
    target = OWNED / 'review-checks.json'
    if args.verify:
        assert target.read_bytes() == payload
    elif target.exists():
        assert target.read_bytes() == payload, 'Saved checks differ; use a new dated endpoint'
    else:
        target.write_bytes(payload)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
