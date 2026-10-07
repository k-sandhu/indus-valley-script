"""Freeze the deterministic 200-carrier selection before enrichment."""
import argparse
import collections
from common import OWN, RAW, ROOT, PATHS, cisi, candidate_frame, digest, fresh, load_inputs, rank, round_robin, write

def select(inputs):
    frame, exclusions = candidate_frame(inputs)
    selected = {}
    def add(row, reason):
        if row['key'] in selected:
            selected[row['key']]['memberships'].append(reason)
            return False
        r = {k: v for k, v in row.items() if k != 'faces'}
        r['primary_selection'] = reason
        r['memberships'] = [reason]
        selected[row['key']] = r
        return True

    def take(rows, quota, reason):
        added = 0
        for r in rows:
            if added == quota:
                break
            added += add(r, reason)
        return added

    for n in range(2218, 2240):
        add(frame[f'H-{n}'], 'Harappa_22_tablets')
    for period, quota in [('3A', 1), ('3B', 8), ('3C', 8)]:
        pool = [r for r in frame.values() if r['site'] == 'Harappa' and any(f['metadata'].get('time', '') == f'Period {period}' or f['metadata'].get('time', '').startswith(f'Period {period}-') for f in r['faces'])]
        assert take(sorted(pool, key=lambda r: rank(r['key'])), quota, f'Harappa_{period}') == quota

    fam = {r['family']: r for r in frame.values()}
    museum = {m['institution'] + '|' + m['accession']: m for m in inputs['museum']}
    joins = [j for j in inputs['joins'] if j['family'] in fam]
    jm = list(round_robin(joins, lambda j: museum[j['key']]['institution'], lambda j: j['key']))
    assert take([fam[j['family']] for j in jm], 24, 'museum_confirmed') == 24

    lpool = [(l, frame[l['object_id']]) for l in inputs['lothal'] if l['object_id'] in frame]
    ls = round_robin(lpool, lambda pair: (pair[0]['context_code'], pair[0]['physical_type']), lambda pair: pair[0]['object_id'])
    assert take([r for _, r in ls], 25, 'Lothal_joined_sealings') == 25

    absences = {cisi(b) for a in inputs['absent'] if a['edition'].startswith('CISI1') for b in a['absent_base_identifiers']}
    absent_pool = []
    for l in inputs['lothal']:
        b = l['object_id']
        if b in absences:
            absent_pool.append({'key': b, 'catalogue_key': b, 'family': None, 'site': 'Lothal', 'region': 'Gujarat/Kutch', 'type': 'sealing', 'length_bin': 'unavailable', 'damaged': None, 'multi_face': None})
    assert take(sorted(absent_pool, key=lambda r: rank(r['key'])), 20, 'CISI1_absent_sealings') == 20

    for region in ['Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia']:
        pool = [r for r in frame.values() if r['region'] == region]
        take(round_robin(pool, lambda r: r['site'], lambda r: r['key']), min(5, len(pool)), f'external_{region}')

    strata = lambda r: (r['region'], r['site'], r['type'], r['length_bin'], r['damaged'], r['multi_face'])
    take(round_robin(frame.values(), strata, lambda r: r['key']), 200 - len(selected), 'stratified_fill')
    assert len(selected) == 200
    rows = list(selected.values())
    for i, r in enumerate(rows, 1):
        r['object_id'] = f'OL-{i:04d}'
    return {
        'status': 'Frozen evaluation', 'date': '2026-10-07',
        'protocol_sha256': digest(OWN / 'PROTOCOL.md'),
        'rule': 'PROTOCOL.md#deterministic-selection', 'objects': rows,
        'primary_counts': dict(collections.Counter(r['primary_selection'] for r in rows)),
        'frame_exclusion_counts': dict(collections.Counter(r['reason'] for r in exclusions)),
        'input_manifest': {PATHS[k]: {'sha256': digest(ROOT / PATHS[k]), 'bytes': (ROOT / PATHS[k]).stat().st_size} for k in inputs},
    }, exclusions

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--raw-dir', required=True)
    a = ap.parse_args()
    selection, exclusions = select(load_inputs())
    out = fresh(a.output_dir, OWN)
    raw = fresh(a.raw_dir, RAW)
    write(out / 'selection.json', selection)
    write(raw / 'candidate-frame-exclusions.json', exclusions)
    print({'selected': len(selection['objects']), 'primary_counts': selection['primary_counts']})

if __name__ == '__main__':
    main()
