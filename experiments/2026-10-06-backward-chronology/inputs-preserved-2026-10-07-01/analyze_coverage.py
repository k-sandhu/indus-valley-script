"""Recompute documentary coverage; keep every new run in a fresh owned directory."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent

def write_json(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def overlaps(start,end,lo,hi):
    return start < hi and end > lo

def selected(row):
    return [d for d in row['dating_assessments'] if d['selected_for_coverage']
            and d['start_year'] is not None and d['end_year'] is not None]

def object_eligible(row):
    return row['marked_object_count'] is not None and row['count_kind']=='exact'

def eligible(row):
    return row['include_in_additive_coverage'] and not row['adjacent_region'] and bool(selected(row))

def cover(rows,lo,hi):
    found=[]
    for r in rows:
        if not eligible(r): continue
        ds=[d for d in selected(r) if overlaps(d['start_year'],d['end_year'],lo,hi)]
        if ds: found.append((r,ds))
    grades=Counter(ds[0]['grade'] for r,ds in found)
    exact=[(r,ds) for r,ds in found if object_eligible(r)]
    ab=[(r,ds) for r,ds in found if ds[0]['grade'] in 'AB']
    reliable=[(r,ds) for r,ds in ab if ds[0]['calendar_strength'] in ['high','moderate']]
    def lower(items):
        return sum(r['marked_object_count'] for r,ds in items if object_eligible(r)
                   and all(d['start_year']>=lo and d['end_year']<=hi for d in selected(r)))
    def upper(items):
        return sum(r['marked_object_count'] for r,ds in items if object_eligible(r))
    return dict(start_year=lo,end_year=hi,label=f'{-lo}–{-hi} BCE',
        assemblages=len(found), **{f'grade_{g}':grades[g] for g in 'ABCD'},
        phase_or_historical_AB=len(ab), high_moderate_calendar_AB=len(reliable),
        assemblages_with_verified_images=sum(r['image_corpus_verified'] for r,ds in found),
        exact_objects_assignable_lower=lower(exact),exact_objects_possible_upper=upper(exact),
        exact_AB_objects_assignable_lower=lower(ab),exact_AB_objects_possible_upper=upper(ab),
        unknown_object_count_assemblages=sum(r['marked_object_count'] is None for r,ds in found),
        non_object_or_unaligned_count_assemblages=sum(r['marked_object_count'] is not None and not object_eligible(r) for r,ds in found),
        assemblage_ids=[r['id'] for r,ds in found],
        high_moderate_calendar_AB_ids=[r['id'] for r,ds in reliable])

def empty_runs(bins,key):
    nonempty=[i for i,b in enumerate(bins) if b[key]>0]
    first=nonempty[0] if nonempty else None
    last=nonempty[-1] if nonempty else None
    runs=[]; i=0
    while i<len(bins):
        if bins[i][key]: i+=1; continue
        begin=i
        while i<len(bins) and bins[i][key]==0: i+=1
        internal=first is not None and begin>first and i-1<last
        runs.append(dict(start_year=bins[begin]['start_year'],end_year=bins[i-1]['end_year'],
                         centuries=i-begin,years=100*(i-begin),internal=internal))
    return dict(series=key,empty_runs=runs,
                longest=max(runs,key=lambda r:r['years']) if runs else None,
                longest_internal=max([r for r in runs if r['internal']],key=lambda r:r['years'],default=None))

def self_checks():
    assert not overlaps(-300,-200,-200,-100)
    assert overlaps(-300,-200,-300,-200)
    assert not overlaps(-400,-300,-300,-200)
    a={'id':'fixture','include_in_additive_coverage':True,'adjacent_region':False,
       'dating_assessments':[{'selected_for_coverage':True,'start_year':-500,'end_year':-400,'grade':'B','calendar_strength':'moderate'}],
       'marked_object_count':7,'count_kind':'exact','image_corpus_verified':True}
    b=cover([a],-500,-400)
    assert b['exact_objects_assignable_lower']==b['exact_objects_possible_upper']==7
    a['dating_assessments'][0]['end_year']=-300
    assert cover([a],-500,-400)['exact_objects_assignable_lower']==0
    a['include_in_additive_coverage']=False
    assert cover([a],-500,-400)['assemblages']==0
    a['include_in_additive_coverage']=True; a['count_kind']='site count, not objects'
    assert cover([a],-500,-400)['exact_objects_possible_upper']==0
    return 7

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True,help='Fresh directory inside this package')
    args=p.parse_args()
    out=Path(args.output).resolve(); out.relative_to(OWN)
    if out.exists(): p.error('Run directory exists. Choose a new output; frozen endpoints are never overwritten.')
    rows=json.loads((OWN/'evidence-table.json').read_text(encoding='utf-8'))['rows']
    sources=json.loads((OWN/'sources.json').read_text(encoding='utf-8'))['sources']
    claims=json.loads((OWN/'continuity-claims.json').read_text(encoding='utf-8'))['claims']
    ids={r['id'] for r in rows}; sids={s['id'] for s in sources}; cids={c['id'] for c in claims}
    assert len(ids)==len(rows)
    for r in rows:
        assert set(r['source_ids'])<=sids and set(r['continuity_claim_ids'])<=cids
        assert len(selected(r))<=1, 'Alternative dates must not count as independent assemblages'
        for d in selected(r):
            assert d['start_year']<d['end_year']
            assert d['grade'] in 'ABCD'
        assert r['marked_object_count'] is None or r['marked_object_count']>=0
    hashes=[]
    for s in sources:
        if 'local_witness' in s:
            actual=hashlib.sha256((ROOT/s['local_witness']).read_bytes()).hexdigest()
            assert actual==s['sha256'],s['id']
            hashes.append({'source_id':s['id'],'sha256':actual,'verified':True})
    with (OWN/'evidence-table.csv').open(encoding='utf-8-sig',newline='') as f:
        csvrows=list(csv.DictReader(f))
    assert [r['id'] for r in csvrows]==[r['id'] for r in rows]
    for c,r in zip(csvrows,rows):
        assert json.loads(c['dating_assessments'])==r['dating_assessments']
        assert c['marked_object_count']==('' if r['marked_object_count'] is None else str(r['marked_object_count']))
    fixture_checks=self_checks()
    bins=[cover(rows,lo,lo+100) for lo in range(-3500,-200,100)]
    assert len(bins)==33
    assert all(b['assemblages']==sum(b[f'grade_{g}'] for g in 'ABCD') for b in bins)
    regions=[]
    for region in sorted({r['region'] for r in rows}):
        rs=[r for r in rows if r['region']==region]
        within=[r for r in rs if eligible(r) and overlaps(selected(r)[0]['start_year'],selected(r)[0]['end_year'],-3500,-200)]
        regions.append(dict(region=region,inventory_rows=len(rs),dated_additive_rows_in_window=len(within),
                            rows_with_verified_images=sum(r['image_corpus_verified'] for r in rs),
                            known_exact_object_count_rows=sum(object_eligible(r) for r in within),
                            dating_link_grades=dict(Counter(selected(r)[0]['grade'] for r in within)),
                            missing_calendar_or_mark_join_rows=sum(not selected(r) for r in rs)))
    gaps={key:empty_runs(bins,key) for key in ['grade_A','phase_or_historical_AB','high_moderate_calendar_AB']}
    regional_gaps={region:{key:empty_runs([cover([r for r in rows if r['region']==region],lo,lo+100) for lo in range(-3500,-200,100)],key)
                          for key in ['grade_A','phase_or_historical_AB','high_moderate_calendar_AB']}
                   for region in sorted({r['region'] for r in rows})}
    inwindow=[r for r in rows if eligible(r) and overlaps(selected(r)[0]['start_year'],selected(r)[0]['end_year'],-3500,-200)]
    summary=dict(status='Verified computation',documentary_status='Exploratory',
        inventory_rows=len(rows),sources=len(sources),continuity_claims=len(claims),century_bins=len(bins),
        dated_additive_rows_in_window=len(inwindow),
        window_dating_grades=dict(Counter(selected(r)[0]['grade'] for r in inwindow)),
        rows_with_verified_images=sum(r['image_corpus_verified'] for r in rows),
        rows_without_selected_calendar_interval=sum(not selected(r) for r in rows),
        zero_A_centuries=sum(b['grade_A']==0 for b in bins),
        zero_AB_centuries=sum(b['phase_or_historical_AB']==0 for b in bins),
        zero_high_moderate_AB_centuries=sum(b['high_moderate_calendar_AB']==0 for b in bins),
        lal_arithmetic={'shared_types':47,'megalithic_total':53,'earlier_pooled_total':55,'union_types':61,
                        'shared_pct_megalithic':100*47/53,'shared_pct_earlier_pool':100*47/55},
        catalogue_arithmetic={'recognized_plus_unrecognized':9619+4546,'graffiti_documented':14165,'printed_final_total':14168,'unresolved_difference':3,
                              'tamil_brahmi_reported':1570,'tamil_brahmi_documented':1182,'unavailable':388,'documented_plus_unavailable':1182+388,
                              'rangpur_objects':26+188+8},
        gaps=gaps,regions=regions,
        object_count_interpretation='Within each bin: known inventoried exact-object rows only. Upper values are possible contributors; never sum across centuries. Unknown counts and unaligned/site units are separate.')
    audit=[dict(id=r['id'],selected_dates=selected(r),coverage_eligible=eligible(r),
                in_window=r in inwindow,count_in_numeric_bounds=object_eligible(r),
                excluded_reason= None if r in inwindow else
                    ('pooled parent, duplicate category, comparator or excluded boundary' if not r['include_in_additive_coverage']
                     else 'no selected usable calendar interval' if not selected(r) else 'outside requested window'),
                limitations=r['limitations']) for r in rows]
    out.mkdir(parents=True)
    write_json(out/'coverage.json',{'status':'Verified computation','bins':bins})
    with (out/'coverage.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(bins[0])); w.writeheader()
        for b in bins: w.writerow({k:json.dumps(v) if isinstance(v,list) else v for k,v in b.items()})
    write_json(out/'summary.json',summary)
    write_json(out/'dating-audit.json',audit)
    write_json(out/'regional-gaps.json',regional_gaps)
    write_json(out/'verification.json',dict(status='Verified computation',source_hashes=hashes,source_hash_checks=len(hashes),
          evidence_csv_json_rows_checked=len(rows),fixture_checks=fixture_checks,
          input_sha256={name:hashlib.sha256((OWN/name).read_bytes()).hexdigest() for name in ['evidence-table.json','evidence-table.csv','sources.json','continuity-claims.json','PROTOCOL.md','analyze_coverage.py']}))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
