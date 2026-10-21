"""A source-qualified fish-family study. All real half reads use bench.shots."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys

import numpy as np
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from bench import shots
from bench.common import envelope, sha256, write_json, read_rows, read_json
from bench.meaning_map import units

RAW = ROOT / 'data/raw/2026-10-20-fish-context'
INPUT = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
CODING = ROOT / 'experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv'
CODING2 = CODING.parent / 'second-coder/components_coder2.tsv'
TABLES = ROOT / 'experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv'
IMAGES = ROOT / 'experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv'
BASIC = ROOT / 'data/raw/2026-10-13-cisi-basic-data-full/assembled'
VALUES = list(range(1, 11)) + [12, 24]
ALPHA = 0.05 / 3
SEED = 20261020


def csv_rows(path, delimiter=','):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def coding(path=CODING):
    return {r['code']: r for r in csv_rows(path, '\t')}


def fish_codes(table):
    return {s for s, r in table.items() if r['base'] == 'B220'}


def is_seal(row):
    return row['object_type'].strip().upper().split(':')[0] == 'SEAL'


def sequences(rows, seals=False):
    """Keep one representative per full text after source-wide dependency closure."""
    seen = set()
    out = []
    for r in sorted(rows, key=lambda r: r['record_id']):
        if not r['clean_rtl_singleline'] or (seals and not is_seal(r)):
            continue
        seq = tuple(str(s).zfill(3) for s in r['signs_reading_rtl'])
        # A full text on another object is one observation of this sequence.
        if seq in seen:
            continue
        seen.add(seq)
        out.append(dict(r, seq=seq))
    return out


def pair_rows(rows, fish):
    return [(r['component'], a, b) for r in rows for a, b in zip(r['seq'], r['seq'][1:])
            if a in fish and b in fish and a != b]


def learn_order(rows, fish):
    counts = Counter(s for r in rows for s in r['seq'] if s in fish)
    common = sorted([s for s in fish if counts[s] >= 5], key=lambda s: (-counts[s], s))[:7]
    ps = pair_rows(rows, set(common))
    best, score = [], -1
    for order in itertools.permutations(sorted(common)):
        rank = {s: i for i, s in enumerate(order)}
        val = sum(rank[a] < rank[b] for _, a, b in ps)
        if val > score:
            best, score = list(order), val
    return {'codes': best, 'discovery_pairs': len(ps), 'discovery_forward_pairs': score,
            'discovery_occurrences': dict(counts), 'selection': 'at most seven codes with >=5 discovery occurrences'}


def sign_result(by_component):
    vals = [float(v) for v in by_component.values()]
    pos, neg = sum(v > 1e-12 for v in vals), sum(v < -1e-12 for v in vals)
    p = float(binomtest(pos, pos + neg, .5, alternative='greater').pvalue) if pos + neg else None
    total = sum(vals)
    loo = min(((total - v) / (len(vals) - 1) for v in vals), default=None) if len(vals) > 1 else None
    return {'components': len(vals), 'positive': pos, 'negative': neg, 'ties': len(vals) - pos - neg,
            'p_one_sided': p, 'mean_component_value': float(np.mean(vals)) if vals else None,
            'minimum_leave_one_component_out_mean': loo}


def score_order(rows, fish, model):
    order = model['order']['codes']
    rank = {s: i for i, s in enumerate(order)}
    ps = pair_rows(rows, fish & set(rank))
    by = defaultdict(list)
    pc = Counter()
    for component, a, b in ps:
        by[component].append(1 if rank[a] < rank[b] else -1)
        pc[a + '>' + b] += 1
    votes = {k: float(np.mean(v)) for k, v in by.items()}
    result = sign_result(votes)
    n = result['positive'] + result['negative']
    result.update(order=order, directed_pairs=dict(pc), pairs=len(ps),
                  forward_pairs=sum(rank[a] < rank[b] for _, a, b in ps),
                  pass_rule={'min_components': 15, 'min_positive_share': .75, 'alpha': ALPHA})
    result['pass'] = bool(n >= 15 and result['positive'] / n >= .75 and result['p_one_sided'] <= ALPHA)
    return result, votes


def stroke(table, sign, strict=False):
    r = table.get(sign, {})
    if r.get('base') not in ('B001', 'B031') or not r.get('count'):
        return None
    if strict and (r['confidence'] != 'high' or r['mods']):
        return None
    return (r['base'], int(r['count']))


def number_events(rows, table, fish, strict=False):
    out = []
    for r in rows:
        seq = r['seq']
        for i, s in enumerate(seq[:-1]):
            num = stroke(table, s, strict)
            if num is None or num[1] not in VALUES or stroke(table, seq[i + 1]) is not None:
                continue
            out.append({'component': r['component'], 'record_id': r['record_id'],
                        'genre': 'seal' if is_seal(r) else r['object_type'],
                        'stroke_family': num[0], 'stroke_code': s, 'value': num[1], 'item': seq[i + 1],
                        'fish': seq[i + 1] in fish,
                        'left': seq[i - 1] if i else '<start>'})
    return out


def key(*parts):
    return '|'.join(parts)


def learn_numbers(rows, table, fish):
    events = number_events(rows, table, fish)
    q, local = defaultdict(Counter), defaultdict(Counter)
    canonical = Counter()
    for e in events:
        if not e['fish']:
            q[key(e['genre'], e['stroke_family'])][str(e['value'])] += 1
            q['all'][str(e['value'])] += 1
        else:
            local[key(e['genre'], e['stroke_family'], e['item'])][str(e['value'])] += 1
            if e['genre'] == 'seal' and e['item'] == '220' and e['stroke_family'] == 'B001' and e['value'] in (3, 6, 7):
                canonical[str(e['value'])] += 1
    return {'quantity_counts': dict(q), 'local_counts': dict(local), 'canonical_counts': dict(canonical),
            'prior_strength': 8, 'celestial_mass': .9, 'values': VALUES}


def probability(e, model):
    qcounts = model['quantity_counts'].get(key(e['genre'], e['stroke_family']), model['quantity_counts'].get('all', {}))
    q = (qcounts.get(str(e['value']), 0) + .5) / (sum(qcounts.values()) + .5 * len(VALUES))
    lc = model['local_counts'].get(key(e['genre'], e['stroke_family'], e['item']), {})
    lexical = (lc.get(str(e['value']), 0) + model['prior_strength'] * q) / (sum(lc.values()) + model['prior_strength'])
    cc = model['canonical_counts']
    celestial = (.9 * (cc.get(str(e['value']), 0) + .5) / (sum(cc.values()) + 1.5)
                 if e['value'] in (3, 6, 7) else .1 / (len(VALUES) - 3))
    return q, lexical, celestial


def wilson(k, n):
    if not n:
        return [None, None]
    z = 1.959963984540054
    p, d = k / n, 1 + z*z/n
    mid = (p + z*z/(2*n)) / d
    delta = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return [mid-delta, mid+delta]


def score_numbers(rows, table, fish, model, strict=False):
    events = [e for e in number_events(rows, table, fish, strict) if e['fish']]
    by, cby = defaultdict(list), defaultdict(list)
    values, families = Counter(), defaultdict(Counter)
    plain, logs = [], []
    for e in events:
        probs = probability(e, model['numbers'])
        ll = [math.log2(v) for v in probs]
        by[e['component']].append(ll[1] - ll[0])
        logs.append(ll)
        values[e['value']] += 1
        families[e['item']][e['value']] += 1
        if e['item'] == '220' and e['stroke_family'] == 'B001':
            plain.append(e)
            cby[e['component']].append((ll[2]-ll[0], ll[2]-ll[1], e['value'] in (3,6,7)))
    diffs = {k: float(np.mean(v)) for k, v in by.items()}
    result = sign_result(diffs)
    result.update(events=len(events), values=dict(values), by_fish={s: dict(c) for s,c in families.items()},
                  mean_log2_probability_Q_L=list(np.mean(np.array(logs)[:, :2], axis=0)) if logs else [None]*2,
                  pass_rule={'min_components': 15, 'alpha': ALPHA, 'positive_gain_and_all_loo_positive': True},
                  strict_strokes=strict)
    result['pass'] = bool(result['positive']+result['negative'] >= 15 and result['p_one_sided'] <= ALPHA
                          and result['mean_component_value'] > 0
                          and result['minimum_leave_one_component_out_mean'] > 0)
    # One component gets one canonical vote; require every event in it to be canonical.
    ck = sum(all(x[2] for x in xs) for xs in cby.values())
    ci = wilson(ck, len(cby))
    c_q = float(np.mean([np.mean([x[0] for x in xs]) for xs in cby.values()])) if cby else None
    c_l = float(np.mean([np.mean([x[1] for x in xs]) for xs in cby.values()])) if cby else None
    celestial = {'plain_fish_events': len(plain), 'components': len(cby), 'canonical_components': ck,
                 'canonical_component_share': ck / len(cby) if cby else None, 'wilson95': ci,
                 'values': dict(Counter(e['value'] for e in plain)), 'mean_gain_over_Q_bits': c_q,
                 'mean_gain_over_L_bits': c_l,
                 'pass': bool(len(cby) >= 20 and ci[0] >= .8 and c_q > 0 and c_l > 0)}
    result['narrow_celestial'] = celestial
    return result, diffs, events


def make_map(rows, table):
    freq, positions = Counter(), defaultdict(list)
    for r in rows:
        for s in set(r['seq']):
            freq[s] += 1
        for i, s in enumerate(r['seq']):
            positions[s].append(i / max(1, len(r['seq'])-1))
    fish = fish_codes(table)
    mapping = {}
    for s in sorted(freq):
        if freq[s] < 20 or stroke(table, s):
            continue
        p = float(np.mean(positions[s]))
        pb = 'initial' if p < 1/3 else 'final' if p > 2/3 else 'middle'
        mapping[s] = {'label': 'fish' if s in fish else 'other',
                      'band': [int(math.log2(freq[s])), pb], 'discovery_faces': freq[s],
                      'position_band': pb}
    return mapping


def bench_objects(rows):
    # Build one unit per dependency component; mixed sites are explicitly mixed.
    by = defaultdict(list)
    for r in rows:
        by[r['component']].append(r)
    objects = []
    for component, members in sorted(by.items()):
        sites = {r['site'] for r in members}
        sitestr = next(iter(sites)) if len(sites) == 1 else '<mixed-sites>'
        length = np.mean([len(r['seq']) for r in members])
        objects.append({'component': component, 'signs': sorted({s for r in members for s in r['seq']}),
                        'properties': {'seal': float(np.mean([is_seal(r) for r in members])),
                                       'site': sitestr, 'length_bin': '<=3' if length <=3 else '4-5' if length<=5 else '6+'}})
    return objects


def coverage(rows, fish):
    f = [r for r in rows if any(s in fish for s in r['signs_reading_rtl'])]
    families = {r['object_family_id'] for r in f}
    return {'faces': len(f), 'objects': len(families),
            'clean_faces': sum(r['clean_rtl_singleline'] for r in f),
            'sites': dict(Counter(r['site'] for r in f)),
            'object_types': dict(Counter(r['object_type'] for r in f)),
            'sign_tokens': dict(Counter(s for r in f for s in r['signs_reading_rtl'] if s in fish))}


def dump_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def run_discovery(args):
    dest, local = HERE / args.out, RAW / args.out
    dest.mkdir(exist_ok=False)
    local.mkdir(parents=True, exist_ok=False)
    rows, event = shots.load_half(HERE/'round.json', 'discovery', 'fish')
    table = coding()
    fish = fish_codes(table)
    clean, seals = sequences(rows), sequences(rows, seals=True)
    model = {'order': learn_order(seals, fish), 'numbers': learn_numbers(clean, table, fish),
             'fish_codes': sorted(fish), 'created_utc': datetime.now(timezone.utc).isoformat()}
    mapping = make_map(clean, table)
    write_json(dest/'model.json', model)
    write_json(dest/'map.json', mapping)
    write_json(dest/'bench-predictions.json', {'predictions': [
        {'id': 'fish_on_seals', 'variable': 'seal', 'positive': 'fish', 'negative': 'other',
         'direction': 1, 'measure': 'mean', 'criterion': 'loo', 'min_units': 8,
         'controls': ['site', 'length_bin']}]})
    dump_jsonl(local/'discovery-objects.jsonl', bench_objects(clean))
    dump_jsonl(local/'discovery-faces.jsonl', rows)
    write_json(dest/'summary.json', {'coverage': coverage(rows, fish), 'clean_unique_texts':len(clean),
                                     'seal_unique_texts':len(seals), 'order': model['order'],
                                     'map_signs':len(mapping), 'mapped_fish':[s for s,v in mapping.items() if v['label']=='fish'],
                                     'access':event, 'source_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in [INPUT,CODING,CODING2,TABLES,IMAGES]}})
    print(json.dumps(read_json(dest/'summary.json'), indent=2))


def run_confirmation(args):
    dest, local = HERE/args.out, RAW/args.out
    dest.mkdir(exist_ok=False)
    local.mkdir(parents=True, exist_ok=False)
    rows, event = shots.load_half(HERE/'round.json', 'confirmation', 'fish', allow_spent=True)
    table, second = coding(), coding(CODING2)
    fish = fish_codes(table)
    consensus = fish & fish_codes(second)
    model = read_json(HERE/'discovery-v2/model.json')
    results, details = {}, {}
    for label, seals_only, strict, codes in [
        ('primary_seals',True,False,fish), ('strict_strokes_seals',True,True,fish),
        ('all_carriers',False,False,fish), ('consensus_fish_seals',True,False,consensus)]:
        clean = sequences(rows, seals=seals_only)
        order, ov = score_order(clean,codes,model)
        numbers, nv, events = score_numbers(clean,table,codes,model,strict)
        results[label] = {'order':order,'numbers':numbers,'clean_unique_texts':len(clean)}
        details[label] = {'order_component_scores':ov,'number_component_scores':nv,'number_events':events}
    # The primary astronomical rule also requires the strict-stroke result.
    results['primary_seals']['numbers']['narrow_celestial']['joint_strict_pass'] = bool(
        results['primary_seals']['numbers']['narrow_celestial']['pass'] and
        results['strict_strokes_seals']['numbers']['narrow_celestial']['pass'])
    a = results['primary_seals']['order']['pass']
    b = results['primary_seals']['numbers']['pass']
    prior = .55 if a and b else .45 if a or b else .20
    write_json(dest/'results.json', envelope('fish-context', {
        'status_class':'frozen-evaluation', 'historical_exposure':True, 'fresh_claim_allowed':False,
        'access':event, 'comparisons':results, 'functional_credence_before_carrier_test':prior,
        'narrow_celestial_credence':.30 if results['primary_seals']['numbers']['narrow_celestial']['joint_strict_pass'] else .05,
        'consensus_fish_codes':sorted(consensus), 'confirmation_coverage':coverage(rows,fish)},
        paths=[HERE/'PROTOCOL.md',HERE/'PREDICTIONS.json',HERE/'discovery-v2/model.json',CODING,CODING2,Path(__file__)]))
    write_json(local/'component-scores.json',details)
    dump_jsonl(local/'confirmation-faces.jsonl',rows)
    dump_jsonl(local/'confirmation-objects.jsonl',bench_objects(sequences(rows)))
    print(json.dumps(results,indent=2))


def base_cisi(text):
    return list(dict.fromkeys(re.findall(r'[A-Za-z?]+-\d+',text or '')))


def usable(value):
    return str(value or '').strip() not in ('','-','--','?','??','Unknown','0','0.0')


def run_register(args):
    dest, local = HERE/args.out, RAW/args.out
    dest.mkdir(exist_ok=False)
    local.mkdir(parents=True,exist_ok=False)
    # Assembly follows the already frozen, logged scoring read. No unlogged raw read.
    rows=[]
    for half in ('discovery','confirmation'):
        f = RAW/('discovery-v2' if half=='discovery' else 'confirmation-v1')/(half+'-faces.jsonl')
        rows.extend(read_rows(f))
    table = coding(); fish=fish_codes(table)
    faces=[r for r in rows if any(s in fish for s in r['signs_reading_rtl'])]
    families={r['object_family_id'] for r in faces}
    # Include every face of an object bearing fish on any face.
    all_faces=[r for r in rows if r['object_family_id'] in families]
    basic=defaultdict(list)
    for volume in (1,2):
        for r in read_rows(BASIC/f'cisi{volume}-basic-data.jsonl'):
            basic[r['cisi']].append(r)
    tables=defaultdict(list)
    for r in csv_rows(TABLES):tables[r['lipi_family_id']].append(r)
    images=defaultdict(list)
    for r in csv_rows(IMAGES):images[r['record_id']].append(r)
    by=defaultdict(list)
    for r in all_faces:by[r['object_family_id']].append(r)
    objects=[]; assertions=[]; flags=[]
    for family, fs in sorted(by.items(),key=lambda x:int(x[0])):
        ids=sorted({c for r in fs for c in base_cisi(r['source_cisi'])})
        bs=[r for c in ids for r in basic.get(c,[])]
        ts=tables.get(family,[])
        ims=[im for r in fs for im in images.get(r['record_id'],[])]
        meta=fs[0]['metadata']
        for r in bs:
            for field,col in [('fc_number','col2_fc'),('excavation_registration','col3_excavation'),('museum','col4_museum'),('photograph_source','col5_photographs')]:
                assertions.append({'object_family_id':family,'field':field,'value':r[col],
                                   'value_status':'conflicting' if '[' in r[col] else 'catalogued',
                                   'uncertain': '[' in r[col], 'source':r['volume'],
                                   'printed_page':r['printed_page'],'pdf_page':r['pdf_page'],'cisi':r['cisi']})
        for r in ts:
            for field in ('field_no','material','area','locus','level_ft','level_reference','size_in_as_printed'):
                assertions.append({'object_family_id':family,'field':field,'value':r[field],
                                   'value_status':'catalogued' if usable(r[field]) else 'unknown',
                                   'source':r['source'],'printed_page':r['printed_page'],
                                   'catalogue_no':r['catalogue_no'],'source_row_id':r['source_row_id']})
        obj={'object_family_id':family,'cisi':ids,'sites':sorted({r['site'] for r in fs}),
             'object_types':sorted({r['object_type'] for r in fs}),'faces':[r['record_id'] for r in fs],
             'fish_faces':[r['record_id'] for r in fs if any(s in fish for s in r['signs_reading_rtl'])],
             'fish_codes':sorted({s for r in fs for s in r['signs_reading_rtl'] if s in fish}),
             'basic_data_records':bs,'excavation_table_rows':ts,'images':ims,
             'metadata_by_face':{r['record_id']:r['metadata'] for r in fs},
             'context_status':{'calendar_date':'unknown: no sourced conversion',
                               'commodity_or_quantity_anchor':'unknown: no independently joined observation',
                               'deposit_associations':'unknown: no joined excavation assemblage'}}
        objects.append(obj)
        flags.append({'object_family_id':family,'cisi':';'.join(ids),'faces':len(fs),'fish_faces':len(obj['fish_faces']),
                      'has_basic_data':int(bool(bs)),'has_excavation_table':int(bool(ts)),
                      'has_image':int(bool(ims)),
                      'face_side_images':int(any(i['relation']=='face-side' for i in ims)),
                      'museum_before':int(usable(meta.get('museum'))),
                      'museum_with_basic':int(any(r['parsed']['museum_number_usable'] for r in bs)),
                      'museum_unbracketed':int(any(r['parsed']['museum_number_usable'] and '[' not in r['col4_museum'] for r in bs)),
                      'has_published_context_locator':int(any(usable(r['area']) or usable(r['locus']) for r in ts))})
    dump_jsonl(local/'objects.jsonl',objects)
    dump_jsonl(local/'faces.jsonl',all_faces)
    dump_jsonl(local/'assertions.jsonl',assertions)
    with (dest/'object-coverage-flags.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(flags[0]));w.writeheader();w.writerows(flags)
    summary={'population':coverage(rows,fish),'retained_all_faces':len(all_faces),'assertions':len(assertions),
             'coverage':{k:sum(r[k] for r in flags) for k in flags[0] if k not in ('object_family_id','cisi','faces','fish_faces')},
             'input_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in [INPUT,TABLES,IMAGES,BASIC/'cisi1-basic-data.jsonl',BASIC/'cisi2-basic-data.jsonl']},
             'unknown_anchors':{'independent_calendar_date':0,'measured_referent_quantity':0,'object_linked_fish_bone_deposit':0},
             'local_paths':{k:str((local/k).relative_to(ROOT)) for k in ['objects.jsonl','faces.jsonl','assertions.jsonl']},
             'interpretation':'Coverage added here is linkage to existing source records. No new physical object is asserted.'}
    write_json(dest/'coverage.json',summary)
    print(json.dumps(summary,indent=2))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['discovery','confirmation','register'])
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    {'discovery':run_discovery,'confirmation':run_confirmation,'register':run_register}[args.action](args)


if __name__=='__main__':main()
