"""Reviewer check of the frozen selection (Package L).

Re-implements the PROTOCOL.md selection text from the pinned Lipi export and the census inputs
without importing the package code, then compares the result with selection.json and measures
how the stratified fill and the round-robin groups behave.

Run from the repository root:  python experiments/2026-10-07-object-ledger/review/verify_selection.py
Writes review/selection-check.json (small aggregate output only).
"""
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-07-object-ledger'
OUT = PKG / 'review' / 'selection-check.json'


def jl(p):
    return [json.loads(l) for l in (ROOT / p).read_text(encoding='utf-8-sig').splitlines() if l.strip()]


def js(p):
    return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))


def rank(key):
    return hashlib.sha256(('object-ledger-20261007|' + str(key)).encode()).hexdigest(), str(key)


def base(v):
    m = re.fullmatch(r'([A-Za-z]+)[ -]*(\d+)(?:[A-C])?(?:\s*(?:bis|ter|quater))?', str(v).strip(), re.I)
    return f'{m[1].upper()}-{int(m[2])}' if m else None


def coarse(v):
    s = str(v).strip().casefold()
    if s.startswith(('seal:i', 'seal impression')) or s in {'sealing', 'sealings'}:
        return 'sealing'
    if s.startswith('seal'):
        return 'seal'
    if s.startswith(('tab', 'tablet')):
        return 'tablet'
    if s.startswith(('pot', 'post', 'pottery')):
        return 'pottery'
    return s


lipi = jl('data/normalized/lipi_observed_faces.jsonl')
sel = js('experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json')
chosen = sel['objects']
by_key = {o['key']: o for o in chosen}

# ---- candidate frame (independent implementation of the protocol sentence) ----
fam = collections.defaultdict(list)
for f in lipi:
    fam[f['object_family_id']].append(f)
base_to_fams = collections.defaultdict(set)
for f in lipi:
    b = base(f['source_cisi'])
    if b:
        base_to_fams[b].add(f['object_family_id'])
EXTERNAL = {'Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia'}
frame = {}
for fid, faces in fam.items():
    bases = {base(f['source_cisi']) for f in faces} - {None}
    if len(bases) > 1:
        continue
    b = next(iter(bases)) if bases else None
    if b and len(base_to_fams[b]) != 1:
        continue
    ext = any(f['region'] in EXTERNAL for f in faces)
    if not b and not ext:
        continue
    n = max(x['length'] for x in faces)
    lb = '0' if n == 0 else '1-2' if n <= 2 else '3-5' if n <= 5 else '6-9' if n <= 9 else '10+'
    dmg = any(x['has_unknown_sign'] or not x['complete_observed'] or str(x['metadata'].get('preservation', '')).casefold() not in {'complete', '', '-', '--'} for x in faces)
    key = b or f'LIPI-{fid}'
    frame[key] = dict(key=key, fam=fid, site=faces[0]['site'], region=faces[0]['region'], type=coarse(faces[0]['object_type']), lb=lb, dmg=dmg, mf=len(faces) > 1, faces=faces)

res = {'frame_size': len(frame), 'lipi_families': len(fam)}

# ---- mandatory group 1: tablets
res['tablets_H2218_H2239_present'] = all(f'H-{n}' in by_key for n in range(2218, 2240))

# ---- mandatory group 2: periods (independent re-ranking)
picked = {f'H-{n}' for n in range(2218, 2240)}
period_check = {}
for period, quota in [('3A', 1), ('3B', 8), ('3C', 8)]:
    pool = [r for r in frame.values() if r['site'] == 'Harappa' and any(
        f['metadata'].get('time', '') == f'Period {period}' or f['metadata'].get('time', '').startswith(f'Period {period}-') for f in r['faces'])]
    pool.sort(key=lambda r: rank(r['key']))
    expected = []
    for r in pool:
        if r['key'] in picked:
            continue
        expected.append(r['key'])
        picked.add(r['key'])
        if len(expected) == quota:
            break
    actual = [o['key'] for o in chosen if o['primary_selection'] == f'Harappa_{period}']
    period_check[period] = {'pool': len(pool), 'expected_set_equals_actual': set(expected) == set(actual), 'actual': actual}
res['period_picks'] = period_check
labels = collections.Counter()
for r in frame.values():
    if r['site'] == 'Harappa':
        for t in {f['metadata'].get('time', '') for f in r['faces']}:
            labels[t] += 1
res['harappa_time_labels_in_frame_by_carrier'] = dict(labels)
res['harappa_3B_slash_C_carriers_excluded_by_rule'] = labels.get('Period 3B/C', 0)

# ---- mandatory group 3: museum-confirmed
joins = js('data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/confirmed-object-joins.json')
museum = {m['institution'] + '|' + m['accession']: m for m in js('data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/focused-records.json')}
fam_to_key = {r['fam']: k for k, r in frame.items()}
eligible_joins = [j for j in joins if j['family'] in fam_to_key]
res['confirmed_joins_total'] = len(joins)
res['confirmed_joins_with_family_in_frame'] = len(eligible_joins)
inst_counts = collections.Counter(museum[j['key']]['institution'] for j in eligible_joins)
res['museum_eligible_by_institution'] = dict(inst_counts)
sel_mus = [o for o in chosen if 'museum_confirmed' in o['memberships']]
res['museum_primary'] = sum(1 for o in chosen if o['primary_selection'] == 'museum_confirmed')
res['museum_member_objects'] = len(sel_mus)
res['museum_selected_by_institution'] = dict(collections.Counter(
    next(museum[j['key']]['institution'] for j in joins if j['family'] == o['family']) for o in sel_mus))
res['museum_joined_objects_in_final_200'] = len({o['family'] for o in chosen if o['family'] in {j['family'] for j in joins}})

# ---- mandatory group 4/5: Lothal frame and catalogue-only
lothal = list(csv.DictReader((ROOT / 'data/six-hour/lothal/table-coding/reviewed-pass.csv').open(encoding='utf-8-sig')))
absent = js('data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/absent-catalogue-identifiers.json')
absent_keys = {base(b) for a in absent if a['edition'].startswith('CISI1') for b in a['absent_base_identifiers']}
lothal_absent = sorted(l['object_id'] for l in lothal if l['object_id'] in absent_keys)
cat_only = [o['key'] for o in chosen if o['family'] is None]
ranked_absent = sorted(lothal_absent, key=rank)
res['lothal_table_rows'] = len(lothal)
res['lothal_table_rows_absent_from_export'] = len(lothal_absent)
res['catalogue_only_selected'] = len(cat_only)
res['catalogue_only_equals_20_lowest_rank_of_absent'] = set(cat_only) == set(ranked_absent[:20])
res['catalogue_only_all_in_L124_L216'] = all(124 <= int(k.split('-')[1]) <= 216 for k in cat_only)
res['absent_lothal_not_selected'] = sorted(set(lothal_absent) - set(cat_only))
res['CISI1_absent_keys_in_register_all_sites'] = len(absent_keys)
res['catalogue_only_sites'] = dict(collections.Counter(o['site'] for o in chosen if o['family'] is None))

lo_pool = [(l, frame[l['object_id']]) for l in lothal if l['object_id'] in frame]
combos = collections.Counter((l['context_code'], l['physical_type']) for l, _ in lo_pool)
lo_sel = [o for o in chosen if 'Lothal_joined_sealings' in o['memberships']]
res['lothal_joined_pool_rows'] = len(lo_pool)
res['lothal_context_type_combinations_in_pool'] = len(combos)
sel_combos = {(l['context_code'], l['physical_type']) for l, r in lo_pool if r['key'] in {o['key'] for o in lo_sel}}
res['lothal_context_type_combinations_selected'] = len(sel_combos)
res['lothal_combos_not_reached'] = sorted(map(str, set(combos) - sel_combos))

# ---- mandatory group 6: external
ext_res = {}
for region in ['Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia']:
    pool = [r for r in frame.values() if r['region'] == region]
    sites = sorted({r['site'] for r in pool})
    taken = sorted({o['site'] for o in chosen if o['region'] == region and any(m.startswith('external_') for m in o['memberships'])})
    ext_res[region] = {'pool_carriers': len(pool), 'pool_sites': sites, 'selected_sites': taken,
                       'sites_in_pool_not_selected': sorted(set(sites) - set(taken)),
                       'alphabetical_prefix_of_sites': sites[:len(taken)] == taken}
res['external'] = ext_res
ext_all = [(f['site'], f['region']) for fid, faces in fam.items() for f in faces[:1] if f['region'] in EXTERNAL]
res['external_families_in_export_by_region'] = dict(collections.Counter(r for _, r in ext_all))

# ---- fill
strata = collections.defaultdict(list)
for r in frame.values():
    strata[(r['region'], r['site'], r['type'], r['lb'], r['dmg'], r['mf'])].append(r)
order = sorted(strata, key=str)
sel_keys_before_fill = {o['key'] for o in chosen if o['primary_selection'] != 'stratified_fill'}
fill = [o for o in chosen if o['primary_selection'] == 'stratified_fill']
res['fill_slots'] = len(fill)
res['strata_in_frame'] = len(order)
fill_strata = {(o['region'], o['site'], o['type'], o['length_bin'], o['damaged'], o['multi_face']) for o in fill}
res['fill_strata_used'] = len(fill_strata)
# how many strata in sorted order precede/included in the fill set
last_idx = max(order.index(s) for s in fill_strata if s in order)
res['fill_last_stratum_position_in_sorted_order'] = last_idx + 1
res['fill_regions'] = dict(collections.Counter(o['region'] for o in fill))
res['fill_sites'] = dict(collections.Counter(o['site'] for o in fill))
reg_all = collections.Counter(r['region'] for r in frame.values())
site_all = collections.Counter((r['region'], r['site']) for r in frame.values())
res['frame_carriers_by_region'] = dict(reg_all)
res['frame_regions_with_no_fill'] = sorted(set(reg_all) - {o['region'] for o in fill})
res['frame_sites_total'] = len(site_all)
final_sites = {o['site'] for o in chosen}
res['frame_sites_not_in_final_200'] = len(set(s for _, s in site_all) - final_sites)
big = sorted(((n, rs) for rs, n in site_all.items()), reverse=True)[:12]
res['largest_frame_sites_and_final_counts'] = [{'region': rs[0], 'site': rs[1], 'frame_carriers': n, 'selected': sum(1 for o in chosen if o['site'] == rs[1])} for n, rs in big]
sorted_regions_of_strata = []
for s in order:
    if not sorted_regions_of_strata or sorted_regions_of_strata[-1][0] != s[0]:
        sorted_regions_of_strata.append([s[0], 0])
    sorted_regions_of_strata[-1][1] += 1
res['stratum_count_by_region_in_sort_order'] = sorted_regions_of_strata

# simulate round-robin fill exactly as the protocol sentence describes, with the sort order as the only unspecified choice
def simulate(order_fn):
    taken = list(sel_keys_before_fill)
    taken_set = set(taken)
    buckets = {k: sorted([r for r in v if r['key'] not in taken_set], key=lambda r: rank(r['key'])) for k, v in strata.items()}
    out = []
    keys = order_fn(list(strata))
    i = 0
    while len(out) < len(fill):
        progressed = False
        for k in keys:
            if i < len(buckets[k]):
                out.append(buckets[k][i]['key'])
                progressed = True
                if len(out) == len(fill):
                    break
        i += 1
        if not progressed:
            break
    return out

def simulate_skip(order_fn):
    """Round-robin over strata where an already-selected carrier still occupies its slot in the stratum
    (it is skipped, not replaced). This is the reading under which the frozen fill is reproduced."""
    buckets = {k: sorted(v, key=lambda r: rank(r['key'])) for k, v in strata.items()}
    keys = order_fn(list(strata))
    out, i = [], 0
    while len(out) < len(fill):
        progressed = False
        for k in keys:
            if i < len(buckets[k]):
                progressed = True
                key = buckets[k][i]['key']
                if key not in sel_keys_before_fill and key not in out:
                    out.append(key)
                    if len(out) == len(fill):
                        break
        i += 1
        if not progressed:
            break
    return out

alpha = simulate(lambda ks: sorted(ks, key=str))
alpha_skip = simulate_skip(lambda ks: sorted(ks, key=str))
res['fill_reproduced_by_alphabetical_stratum_order_removing_selected_first'] = set(alpha) == {o['key'] for o in fill}
res['fill_reproduced_by_alphabetical_stratum_order_skipping_selected'] = set(alpha_skip) == {o['key'] for o in fill}
hash_skip = simulate_skip(lambda ks: sorted(ks, key=lambda k: rank(str(k))))
hs = [frame[k] for k in hash_skip]
res['hash_ordered_stratum_fill_regions'] = dict(collections.Counter(r['region'] for r in hs))
res['hash_ordered_stratum_fill_distinct_sites'] = len({r['site'] for r in hs})
res['hash_ordered_stratum_fill_overlap_with_frozen_fill'] = len(set(hash_skip) & {o['key'] for o in fill})
# alternative order the protocol also permits: strata ordered by hash of the stratum key
alt = simulate(lambda ks: sorted(ks, key=lambda k: rank(str(k))))
alt_chosen = [frame[k] for k in alt]
res['alt_hash_ordered_fill_regions'] = dict(collections.Counter(r['region'] for r in alt_chosen))
res['alt_hash_ordered_fill_sites_n'] = len({r['site'] for r in alt_chosen})
res['alt_hash_ordered_fill_overlap_with_actual'] = len(set(alt) & {o['key'] for o in fill})

# ---- protocol arithmetic
res['primary_counts'] = sel['primary_counts']
res['selection_sum'] = sum(sel['primary_counts'].values())
res['unique_keys'] = len(by_key)

# ---- protocol/selection timing is checked separately with file timestamps
OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(res, indent=1, ensure_ascii=False))
