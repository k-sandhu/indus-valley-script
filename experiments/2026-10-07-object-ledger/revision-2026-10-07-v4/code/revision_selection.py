"""Hash-ordered exploratory revision of the preserved first selection."""
import collections
import hashlib
import json
from common import candidate_frame, rank, digest, OWN, ROOT, PATHS, site
from select_pilot import select

SEED = 'object-ledger-review-20261007|'

def seeded_round_robin(rows, group, key):
    buckets = collections.defaultdict(list)
    for r in rows:
        buckets[group(r)].append(r)
    order = sorted(buckets, key=lambda k: (hashlib.sha256((SEED + json.dumps(k, separators=(',', ':'), ensure_ascii=True)).encode()).hexdigest(), str(k)))
    for k in buckets:
        buckets[k].sort(key=lambda r: rank(key(r)))
    for i in range(max(map(len, buckets.values()), default=0)):
        for k in order:
            if i < len(buckets[k]):
                yield buckets[k][i]

def external_identity(label, inputs, key=None):
    if key == 'BM-123208':
        label = 'Ur'
    row = next((r for r in inputs['external'] if site(label) in {site(r['site']), *map(site, r.get('local_labels', []))}), None)
    if row:
        return row['identity']['canonical_name'], row['identity']['country']['value'], row['site']
    return label, None, None

def revised_selection(inputs):
    original, exclusions = select(inputs)
    frame, _ = candidate_frame(inputs)
    chosen = {}
    # Reuse precisely the five original mandatory stages preceding external picks.
    for row in original['objects']:
        if not row['primary_selection'].startswith('external_') and row['primary_selection'] != 'stratified_fill':
            chosen[row['key']] = {k: v for k, v in row.items() if k != 'object_id'}
    def add(row, reason):
        if row['key'] in chosen:
            return False
        chosen[row['key']] = {k: v for k, v in row.items() if k != 'faces'}
        chosen[row['key']].update(primary_selection=reason, memberships=[reason])
        return True
    pools = collections.defaultdict(list)
    for r in frame.values():
        if r['region'] not in {'Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia'}:
            continue
        canonical, country, _ = external_identity(r['site'], inputs, r['key'])
        group = 'Iran' if country == 'Iran' else 'Mesopotamia' if country == 'Iraq' else 'Central Asia' if r['region'] == 'Central Asia' else 'Gulf' if r['region'] == 'Persian Gulf' else None
        if group:
            pools[group].append(r)
    for group, quota in [('Gulf', 6), ('Mesopotamia', 5), ('Iran', 4), ('Central Asia', 3)]:
        count = 0
        if group == 'Mesopotamia':
            count += add(frame['BM-123208'], 'external_Mesopotamia')
        for r in seeded_round_robin(pools[group], lambda r: external_identity(r['site'], inputs, r['key'])[0], lambda r: r['key']):
            if count == quota:
                break
            count += add(r, 'external_' + group)
        assert count == quota, (group, count, quota)
    strata = lambda r: (r['region'], r['site'], r['type'], r['length_bin'], r['damaged'], r['multi_face'])
    for r in seeded_round_robin(frame.values(), strata, lambda r: r['key']):
        if len(chosen) == 200:
            break
        add(r, 'hash_ordered_stratified_fill')
    assert len(chosen) == 200
    rows = list(chosen.values())
    for i, r in enumerate(rows, 1):
        r['object_id'] = f'OL-{i:04d}'
    original.update(status='Exploratory', protocol_sha256=digest(OWN/'PROTOCOL.md'), rule='AMENDMENT-2026-10-07-review-response.md', seed=SEED, objects=rows,
                    primary_counts=dict(collections.Counter(r['primary_selection'] for r in rows)))
    return original, exclusions
