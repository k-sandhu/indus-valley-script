"""Build the H-912 comparison series through the shared half loader.

Complete transcriptions and event rows are written only under data/raw.
"""
from collections import Counter, defaultdict
import argparse
import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from bench import shots
from bench.common import read_rows, write_json, sha256

RAW = ROOT / 'data/raw/2026-10-20-h912-tablet-series'
CODING = ROOT / 'experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv'


def coding():
    with CODING.open(encoding='utf8', newline='') as f:
        return {r['code']: r for r in csv.DictReader(f, delimiter='\t')}


def dump_rows(path, rows):
    with path.open('x', encoding='utf8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def extract(rows, table):
    """A complete 2/3-sign face beginning with one coded stroke group.

    Three-sign forms permit an item either before or after V. Other forms stay
    in the source register but supply no inferred quantity event.
    """
    by = defaultdict(list)
    for r in rows:
        by[r['object_family_id']].append(r)
    events, related = [], []
    for family, faces in by.items():
        has_v = any(table.get(str(s).zfill(3), {}).get('base') == 'B700'
                    for r in faces for s in r['signs_reading_rtl'])
        has_fish = any(table.get(str(s).zfill(3), {}).get('base') == 'B220'
                       for r in faces for s in r['signs_reading_rtl'])
        target = any(r['site'] == 'Harappa' and r['object_type'].split(':')[0] == 'TAB'
                     for r in faces)
        same_face_vfish = any(
            any(table.get(str(s).zfill(3), {}).get('base') == 'B700' for s in r['signs_reading_rtl'])
            and any(table.get(str(s).zfill(3), {}).get('base') == 'B220' for s in r['signs_reading_rtl'])
            for r in faces)
        if (target and has_v) or same_face_vfish:
            related.append({'object_family_id': family, 'faces': faces,
                            'has_v': has_v, 'has_fish': has_fish,
                            'same_face_vfish': same_face_vfish})
        for r in faces:
            if not r['clean_rtl_singleline']:
                continue
            seq = [str(s).zfill(3) for s in r['signs_reading_rtl']]
            if len(seq) not in (2, 3):
                continue
            num = table.get(seq[0], {})
            if num.get('base') not in ('B001', 'B031') or not num.get('count'):
                continue
            vpos = [i for i in range(1, len(seq)) if table.get(seq[i], {}).get('base') == 'B700']
            if len(vpos) != 1:
                continue
            vp = vpos[0]
            item = seq[3-vp] if len(seq) == 3 else None
            if item and table.get(item, {}).get('base') in ('B001', 'B031'):
                continue
            fish = bool(item and table.get(item, {}).get('base') == 'B220')
            descriptor = sorted(tuple(str(s).zfill(3) for s in x['signs_reading_rtl'])
                                for x in faces if x['record_id'] != r['record_id']
                                and x['clean_rtl_singleline'])
            prototype = sorted(tuple(str(s).zfill(3) for s in x['signs_reading_rtl'])
                               for x in faces if x['clean_rtl_singleline'])
            events.append({'object_family_id': family, 'record_id': r['record_id'],
                'component': r['component'], 'site': r['site'], 'object_type': r['object_type'],
                'source_cisi': r['source_cisi'], 'seq': seq,
                'value': int(num['count']), 'stroke': num['base'],
                'strict_stroke': num['confidence'] == 'high' and not num['mods'],
                'v_code': seq[vp], 'v_position': vp, 'item': item, 'fish': fish,
                'descriptor': descriptor, 'prototype': prototype,
                'harappa_tablet': r['site'] == 'Harappa' and r['object_type'].split(':')[0] == 'TAB'})
    return events, related


def counts(events):
    return {'events': len(events),
            'objects': len({e['object_family_id'] for e in events}),
            'components': len({e['component'] for e in events}),
            'values': dict(sorted(Counter(e['value'] for e in events).items())),
            'stroke_families': dict(Counter(e['stroke'] for e in events)),
            'v_codes': dict(Counter(e['v_code'] for e in events)),
            'items': dict(Counter(e['item'] or 'none' for e in events)),
            'orders': dict(Counter('n-V-item' if e['v_position'] == 1 else 'n-item-V'
                                   for e in events if e['item']))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('half', choices=['discovery', 'confirmation'])
    ap.add_argument('--run', required=True)
    args = ap.parse_args()
    out, local = HERE / args.run, RAW / args.run
    out.mkdir(exist_ok=False)
    local.mkdir(parents=True, exist_ok=False)
    rows, access = shots.load_half(HERE/'round.json', args.half, 'h912',
                                  ledger_path=RAW/'spent-private.json', allow_spent=True)
    events, related = extract(rows, coding())
    dump_rows(local/'faces.jsonl', rows)
    dump_rows(local/'events.jsonl', events)
    dump_rows(local/'related-objects.jsonl', related)
    primary = [e for e in events if e['harappa_tablet'] and e['v_code'] == '700'
               and e['strict_stroke']]
    summary = {'status_class': 'exploratory' if args.half == 'discovery' else 'frozen-evaluation',
        'historical_exposure': True, 'fresh_claim_allowed': False,
        'access': access, 'all_events': counts(events), 'primary': counts(primary),
        'fish_primary': counts([e for e in primary if e['fish']]),
        'fish_all_carriers': counts([e for e in events if e['fish']]),
        'related_objects': len(related),
        'related_source_ids': sorted({r['source_cisi'] for x in related for r in x['faces']}),
        'source_hashes': {str(CODING.relative_to(ROOT)): sha256(CODING),
                          str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))}}
    write_json(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('related_source_ids', 'source_hashes')}, indent=2))


if __name__ == '__main__':
    main()
