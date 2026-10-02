"""Verify saved source hashes, joins, cohort membership and exact calculations."""
from collections import defaultdict
import csv
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from analyze import summarize
from census import census

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]


def read(name):
    return json.loads((RUN / name).read_text(encoding='utf-8'))


def main():
    out = RUN / 'validation.json'
    if out.exists():
        raise FileExistsError('Existing validation endpoint.')
    checks = []
    source_count = 0
    for name in ['source-acquisition-v1.json', 'source-acquisition-v2.json', 'source-acquisition-v3.json']:
        for row in read(name)['sources']:
            if 'local_path' not in row:
                continue
            path = ROOT / row['local_path']
            assert len(path.read_bytes()) == row['bytes']
            assert sha256(path.read_bytes()).hexdigest() == row['sha256']
            source_count += 1
            if 'text_derivative' in row:
                derivative = row['text_derivative']
                assert sha256((ROOT / derivative['path']).read_bytes()).hexdigest() == derivative['sha256']
    checks.append(dict(name='source and PDF text hashes', result='pass', acquired_sources=source_count))
    derivatives = read('raw-derivatives.json')['derivatives']
    for row in derivatives:
        assert sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    checks.append(dict(name='local derivative hashes', result='pass', count=len(derivatives)))
    evidence = read('evidence-table.json')
    objects = evidence['objects']
    assert len({row['id'] for row in objects}) == len(objects) == 15
    with (RUN / 'evidence-table.csv').open(encoding='utf-8', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    for original, exported in zip(objects, csv_rows):
        for key, value in exported.items():
            expected = original.get(key)
            assert value == (str(expected) if expected is not None else '')
    assert len(csv_rows) == len(objects)
    checks.append(dict(name='unique object keys and CSV/JSON agreement', result='pass', count=len(objects)))
    museum = json.loads((ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west/louvre-sb13677.json').read_text(encoding='utf-8'))
    ids = {row['value'] for row in museum['objectNumber']}
    assert {'SB 13677', 'AS 2615'} <= ids
    assert 'quatre points' in museum['description']
    assert '224' in museum['bibliography'][0]['bibliographyDetail']
    checks.append(dict(name='museum/catalogue join and four-point source field', result='pass'))
    numerical = read('numerical-compatibility.json')
    assert numerical['input_sha256'] == sha256((RUN / 'evidence-table.json').read_bytes()).hexdigest()
    for key in ['susa_quarter_mina_hypothesis', 'girsu_readable_shekel_control']:
        rows = [{field: row[field] for field in ['id', 'mass_g', 'proposed_coefficient']}
                for row in numerical[key]['objects']]
        assert summarize(rows) == numerical[key]
    checks.append(dict(name='exact numerical endpoint reconstruction', result='pass'))
    source, extracted = census()
    census_result = read('marked-weight-census-v2.json')
    derivative = json.loads((ROOT / census_result['raw_derivative']).read_text(encoding='utf-8'))
    assert extracted == derivative['objects']
    assert len(extracted) == 69
    excluded = {int(key) for key in census_result['excluded_accession_collisions']}
    assert excluded == {119, 120, 129}
    groups = defaultdict(list)
    for row in extracted:
        if not row['missing_mass'] and row['family'] != 'mixed' and row['cat'] not in excluded:
            groups[(row['shape'], row['material'], row['date_bucket'], row['family'])].append(row)
    assert sum(map(len, groups.values())) == 57
    for group in census_result['groups']:
        key = tuple(group[field] for field in ['shape', 'material', 'date_bucket', 'family'])
        rows = groups[key]
        assert [row['cat'] for row in rows] == group['catalogue_members']
        units = [Fraction(row['mass_g']) / row['count'] for row in rows]
        tolerance = (max(units) - min(units)) / (max(units) + min(units))
        assert str(tolerance) == group['exact_tolerance_fraction']
    assert all(not group['explicit_shared_date_bucket'] for group in census_result['groups'] if group['count'] > 1)
    checks.append(dict(name='full marked census and all cohort interval bounds', result='pass', entries=69, analyzed=57))
    audit = read('indus-weight-audit.json')
    assert audit['source_sha256'] == sha256(source.read_bytes()).hexdigest()
    assert audit['total_records'] == sum(audit['site_counts'].values()) == 938
    assert audit['site_counts']['Dholavira'] == 870
    assert not audit['flagged_records']
    checks.append(dict(name='direct Indus catalogue coverage endpoint', result='pass', records=938))
    result = dict(status='pass', validated_utc=datetime.now(timezone.utc).isoformat(), checks=checks,
                  limitations='Verification reproduces recorded source joins and computations; ancient unit interpretations remain hypotheses.')
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status=result['status'], checks=len(checks)), indent=2))


if __name__ == '__main__':
    main()
