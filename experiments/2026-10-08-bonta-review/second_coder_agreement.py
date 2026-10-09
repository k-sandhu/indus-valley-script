"""Candidate-set agreement and a reference check, with no adjudication."""
from pathlib import Path
import argparse, collections, copy, datetime, json, re
from pdf_followup import ROOT, OWN, RAW, read, write, sha

DEFAULT=OWN/'two-coder-2026-10-09-v1'
RETURN=RAW/'second-coder-v1/returns/coder2-merged.json'
FIRST=OWN/'pdf-2026-10-09-v1/mapping-v2-frozen.json'
SCHEMA=read(ROOT/'data/normalized/mayig_sign_schema.json')['signs']
CHART=read(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json')['rows']
CELLS={f'p{r["pdf_page"]}_c{r["column"]}_r{r["row"]}':r for r in CHART}

def well(x):return str(int(str(x).removeprefix('W'))).zfill(3)
def normalize(mapping):
    result=copy.deepcopy(mapping)
    for r in result['rows']:
        r['mayig_candidates']=sorted(set(r['mayig_candidates']))
        r['wells_candidates']=sorted({well(v) for v in r['wells_candidates']})
        r['helsinki_candidates']=sorted(r['helsinki_candidates'],key=lambda c:c['cell_id'])
    return result
def candidates(row,domain):
    return set(c['cell_id'] for c in row['helsinki_candidates']) if domain=='helsinki' else set(row[domain+'_candidates'])
def target_type(sign):
    return 'caption form' if sign.startswith('U') else 'Table 18 drawing' if int(sign[1:])<=65 else 'field or anchor target'
def measures(pairs,domain):
    pairs=[(candidates(a,domain),candidates(b,domain)) for a,b in pairs]
    singleton=[(next(iter(a)),next(iter(b))) for a,b in pairs if len(a)==len(b)==1]
    n=len(singleton);ca=collections.Counter(a for a,b in singleton);cb=collections.Counter(b for a,b in singleton)
    chance=sum(v*cb[k] for k,v in ca.items())/n**2 if n else None
    observed=sum(a==b for a,b in singleton)/n if n else None
    meaningful=n>=2 and len(set(ca)|set(cb))>=2 and chance!=1
    return {'targets':len(pairs),'exact_singleton_matches':sum(len(a)==len(b)==1 and a==b for a,b in pairs),
        'paired_singleton_rows':n,'equal_nonempty_sets':sum(bool(a) and a==b for a,b in pairs),
        'candidate_set_overlap':sum(bool(a&b) for a,b in pairs),
        'disjoint_nonempty_sets':sum(bool(a) and bool(b) and not a&b for a,b in pairs),
        'missing_one_or_both_sets':sum(not a or not b for a,b in pairs),
        'both_empty':sum(not a and not b for a,b in pairs),
        'kappa_paired_singletons':(observed-chance)/(1-chance) if meaningful else None,
        'singleton_observed_agreement':observed,'singleton_chance_agreement':chance,
        'kappa_scope':'Both coders supply a singleton; ambiguous/missing rows excluded.' if meaningful else 'Kappa undefined for the available paired singleton marginals.'}

def main(output=DEFAULT):
    output=Path(output).resolve()
    if not output.is_relative_to(OWN) or (output/'agreement.json').exists():raise SystemExit('Use fresh owned endpoints')
    output.mkdir(parents=True,exist_ok=True)
    first=normalize(read(FIRST));second=normalize(read(RETURN));bysecond={r['sign_id']:r for r in second['rows']}
    assert len(first['rows'])==len(second['rows'])==96
    pairs=[(a,bysecond[a['sign_id']]) for a in first['rows']]
    assert set(bysecond)=={a['sign_id'] for a in first['rows']}
    parts=[]
    for r in read(RETURN)['parts']:
        p=RETURN.parent/r['file'];parts.append({'path':p.relative_to(ROOT).as_posix(),
            'sha256':sha(p),'matches_declared_hash':sha(p)==r['sha256'],'notes':r['notes']})
    assert all(r['matches_declared_hash'] for r in parts)
    domainresults={d:measures(pairs,d) for d in ['mayig','wells','helsinki']}
    strata={}
    for grouping,key in [('first_confidence',lambda a,b:a['confidence']),('second_confidence',lambda a,b:b['confidence']),
                         ('joint_confidence',lambda a,b:a['confidence']+'/'+b['confidence']),
                         ('target_type',lambda a,b:target_type(a['sign_id']))]:
        groups=collections.defaultdict(list)
        for a,b in pairs:groups[key(a,b)].append((a,b))
        strata[grouping]={k:{d:measures(v,d) for d in domainresults} for k,v in sorted(groups.items())}
    disagreements=[]
    for a,b in pairs:
        domains=[d for d in domainresults if candidates(a,d)!=candidates(b,d)]
        component_diff=a['component_sequence_candidates']!=b['component_sequence_candidates']
        if domains or component_diff:
            note=b['basis'].split('. ')[0].rstrip('.')+'.'
            disagreements.append({'sign_id':a['sign_id'],'target_type':target_type(a['sign_id']),
                'different_domains':domains,'component_difference':component_diff,
                'first_coding':a,'second_coding':b,'visual_note':note,
                'note_basis':'Second reader visual description; candidate sets preserved for an adjudicator.'})
    write(output/'agreement.json',{'status':'Exploratory','coding_rounds':'First Codex reader and second Claude Sonnet 5.5 round split across two fresh sessions; no specialist review.',
        'domains':domainresults,'strata':strata,'first_confidence_counts':dict(collections.Counter(r['confidence'] for r in first['rows'])),
        'second_confidence_counts':dict(collections.Counter(r['confidence'] for r in second['rows'])),
        'disagreement_targets':len(disagreements),'disagreements':disagreements,
        'first_input_sha256':sha(FIRST),'second_input_sha256':sha(RETURN)})
    # Cell rank and explicit code join check, independent of candidate agreement.
    schemajoins=[];missing=[]
    bycode={str(c['code']).zfill(3):(cid,c) for cid,c in CELLS.items()}
    for mid,m in SCHEMA.items():
        for pc in m['parpola_graphemes']:
            code=pc.removeprefix('V').zfill(3)
            if code not in bycode:missing.append({'mayig':mid,'Parpola_code':code});continue
            cid,c=bycode[code];schemajoins.append({'mayig':mid,'code':code,'cell_id':cid,
                'printed_rank':c['rank'],'Mayig_minus_rank':int(mid[1:])-c['rank']})
    payload=[]
    for coder,mp in [('first',first),('second',second)]:
        for r in mp['rows']:
            for h in r['helsinki_candidates']:
                c=CELLS[h['cell_id']]
                if h['class']!=c['rank'] or str(h['code']).zfill(3)!=str(c['code']).zfill(3):
                    payload.append({'coder':coder,'sign_id':r['sign_id'],'return':h,'reference_rank':c['rank'],'reference_code':c['code']})
    expected=lambda r:0 if int(r['mayig'][1:])<=372 else 2 if int(r['mayig'][1:])>=375 else None
    exceptions=[r for r in schemajoins if r['Mayig_minus_rank']!=expected(r)]
    refs={'status':'Verified computation','direct_code_joins':len(schemajoins),
        'offset_histogram':dict(collections.Counter(r['Mayig_minus_rank'] for r in schemajoins)),
        'offset_rule_exceptions':exceptions,'Mayig_classes_373_374':{k:v for k,v in SCHEMA.items() if k in ['P373','P374']},
        'code369_chart':{cid:c for cid,c in CELLS.items() if c['code']==369},
        'code369_Mayig_classes':[k for k,v in SCHEMA.items() if 'V369' in v['parpola_graphemes']],
        'Mayig_Parpola_codes_absent_from_chart':missing,'returned_cell_payload_errors':payload,
        'part_witnesses':parts,'instruction_resolution':'class means chart rank; use v2 template. Explicit code/cell joins remain primary.',
        'reference_sha256':sha(ROOT/'experiments/2026-10-08-chart-reference-audit/chart-reference-v2.1.json')}
    write(output/'reference-check.json',refs)
    agreed=[]
    for a,b in pairs:
        intersection=sorted(candidates(a,'mayig')&candidates(b,'mayig'))
        if not intersection:continue
        w=sorted(candidates(a,'wells')&candidates(b,'wells'))
        hids=candidates(a,'helsinki')&candidates(b,'helsinki')
        agreed.append({'sign_id':a['sign_id'],'mayig_candidates':intersection,'wells_candidates':w,
            'helsinki_candidates':[h for h in a['helsinki_candidates'] if h['cell_id'] in hids],
            'component_sequence_candidates':[s for s in a['component_sequence_candidates'] if s in b['component_sequence_candidates']],
            'confidence':'agreed candidates','basis':'Nonempty Mayig intersection; Wells and chart-cell intersections retained without adjudication.'})
    for label,mapping in [('first',first),('second',second),('agreed_only',{'status':'Exploratory','coder':'Intersection of two AI coding rounds','rows':agreed})]:
        write(output/f'mapping-{label}.json',mapping)
    write(output/'mapping-freeze.json',{'protocol_sha256':sha(DEFAULT/'PROTOCOL-registered.md'),
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'mappings':{label:{'sha256':sha(output/f'mapping-{label}.json'),'targets':len(read(output/f'mapping-{label}.json')['rows'])} for label in ['first','second','agreed_only']},
        'dropped_targets':[a['sign_id'] for a,b in pairs if not candidates(a,'mayig')&candidates(b,'mayig')]})
    print(json.dumps({'domains':domainresults,'disagreement_targets':len(disagreements),
        'agreed_targets':len(agreed),'reference_offset_histogram':refs['offset_histogram'],
        'reference_offset_exceptions':len(exceptions),'cell_payload_errors':len(payload)},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-root',default=str(DEFAULT));main(p.parse_args().output_root)
