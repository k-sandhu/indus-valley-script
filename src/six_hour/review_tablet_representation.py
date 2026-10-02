"""Check display partitions directly from preserved drawing annotations."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAME = ROOT / 'experiments/2026-10-02-six-hour/harappa-object-frame'
BASE = ROOT / 'experiments/2026-10-02-six-hour/tablet-representation'


def main():
    out = BASE / 'review'
    if out.exists():
        raise RuntimeError('Use a fresh review endpoint.')
    paths = [FRAME / 'figure4-first-observations.json',
             FRAME / 'figure4-native-reinspection.json',
             FRAME / 'annotated/results.json', BASE / 'main/results.json']
    first, native, ledger, result = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
    specimens = {r['specimen']: dict(r) for r in first['tablets']}
    for change in native['changes']:
        row = specimens[change['specimen']]
        assert row[change['field']] == change['first_value']
        row[change['field']] = change['revised_value']
    joined = {r['observation_id']: r for r in ledger['target_ledger'] if r['group'] == 'copied_tablets'}
    observed = []
    unresolved = []
    for specimen, row in sorted(specimens.items()):
        target = joined[f'MK2000-F4-{specimen}']
        fields = ['middle_form', 'middle_position', 'bottom_form', 'bottom_position']
        if any(row[k] is None for k in fields):
            unresolved.append(target['target_id'])
            continue
        assert {row['middle_form'], row['bottom_form']} == {'A', 'D'}
        a_side = row['middle_position'] if row['middle_form'] == 'A' else row['bottom_position']
        d_side = row['middle_position'] if row['middle_form'] == 'D' else row['bottom_position']
        observed.append({'target_id': target['target_id'], 'specimen': specimen,
                         'middle_form': row['middle_form'], 'middle_position': row['middle_position'],
                         'bottom_position': row['bottom_position'], 'A_position': a_side,
                         'D_position': d_side, 'same_displayed_side': a_side == d_side})
    # Direct labels implement the quotient without using the main run's orbit code.
    partitions = {
        'fixed_display': lambda r: (r['middle_form'], r['middle_position'], r['bottom_position']),
        'unordered_lower_faces': lambda r: (r['A_position'], r['D_position']),
        'unordered_with_common_reversal': lambda r: r['same_displayed_side'],
        'unordered_with_independent_reversals': lambda r: 'one-inventory',
    }
    checks = {}
    checks['22_original_objects_19_resolved_3_unresolved'] = (len(specimens), len(observed), len(unresolved)) == (22, 19, 3)
    saved = {r['target_id']: r for r in result['resolved_objects']}
    checks['all_resolved_source_fields_match'] = all(all(saved[r['target_id']][k] == r[k] for k in ['A_position', 'D_position', 'same_displayed_side']) for r in observed)
    for package in result['packages']:
        classify = partitions[package['representation']]
        direct = {}
        for row in observed:
            direct.setdefault(classify(row), set()).add(row['target_id'])
        expected = {frozenset(g['target_ids']) for g in package['groups']}
        checks[package['representation'] + '_direct_partition_matches'] = {frozenset(v) for v in direct.values()} == expected
    count_same = sum(r['same_displayed_side'] for r in observed)
    checks['bounds_include_all_unresolved_objects'] = result['missing_observation_bounds'] == {
        'total': 22, 'unresolved': 3,
        'same_displayed_side': {'observed': count_same, 'possible_total': [count_same, count_same + 3]},
        'opposite_displayed_side': {'observed': 19-count_same, 'possible_total': [19-count_same, 22-count_same]}}
    checks['protocol_hash_matches'] = hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest() == result['protocol_sha256']
    checks['main_code_hash_matches'] = hashlib.sha256((BASE/'main/code_snapshot.py').read_bytes()).hexdigest() == result['code_sha256']
    assert all(checks.values()), checks
    out.mkdir()
    (out/'checks.json').write_text(json.dumps({'created_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
        'inputs': [{'path': str(p.relative_to(ROOT)).replace('\\', '/'), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        'unresolved_targets': unresolved, 'source_reconstructed_objects': observed}, indent=2)+'\n', encoding='utf-8')
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks_passed': len(checks), 'source_reconstructed': len(observed), 'same': count_same, 'opposite': 19-count_same}))


if __name__ == '__main__':
    main()
