"""Preservation, independent agreement counts, source census and numerical replay."""
from pathlib import Path
import argparse, collections, json
from pdf_followup import ROOT, OWN, RAW, OUT, WORK, read, write, sha
from second_coder_agreement import normalize, candidates
from second_coder_sensitivity import BASE, LOCAL

def main(replay,output):
    output=(OWN/output).resolve();replay=(OWN/replay).resolve();raw_replay=RAW/replay.name
    if not output.is_relative_to(OWN) or output.exists() or not replay.is_relative_to(OWN):raise SystemExit('Fresh owned output and owned replay required')
    checks=[]
    def check(name,actual,expected):
        same=actual==expected
        if isinstance(actual,set):actual=sorted(actual)
        if isinstance(expected,set):expected=sorted(expected)
        checks.append({'check':name,'passed':same,'actual':actual if len(str(actual))<300 else 'equal' if same else str(actual)[:700],
            'expected':expected if len(str(expected))<300 else 'equal' if same else str(expected)[:700]})
    history=OWN/'history/2026-10-09-before-second-coder'
    editable={'README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','sources.json','registry-entry.json',
        'claims.jsonl','claims.md','ledger-coverage.json','COMPLETION.md','FILES.json'}
    protected=0
    for r in read(history/'baseline-files.json'):
        p=ROOT/r['path']
        if p.parent==OWN and p.name in editable:continue
        protected+=1;check('preserved '+r['path'],sha(p) if p.exists() else None,r['sha256'])
    reg=read(BASE/'registration.json')
    check('registered protocol hash',sha(BASE/'PROTOCOL-registered.md'),reg['protocol_sha256'])
    check('first frozen input hash',sha(OUT/'mapping-v2-frozen.json'),reg['first_mapping_sha256'])
    return_path=RAW/'second-coder-v1/returns/coder2-merged.json'
    check('merged input hash',sha(return_path),reg['second_return_sha256'])
    returned=read(return_path);first=normalize(read(OUT/'mapping-v2-frozen.json'));second=normalize(returned)
    bysecond={r['sign_id']:r for r in second['rows']};check('all96 target identities',set(bysecond),{r['sign_id'] for r in first['rows']})
    parts=[r for part in returned['parts'] for r in read(return_path.parent/part['file'])['rows']]
    check('merged rows unchanged from parts',returned['rows'],parts)
    check('second confidence census',dict(collections.Counter(r['confidence'] for r in second['rows'])),{'high':66,'medium':23,'low':7})
    agreement=read(BASE/'agreement.json')
    for domain in ['mayig','wells','helsinki']:
        pairs=[(candidates(r,domain),candidates(bysecond[r['sign_id']],domain)) for r in first['rows']]
        counts={'exact_singleton_matches':sum(len(a)==len(b)==1 and a==b for a,b in pairs),
            'equal_nonempty_sets':sum(bool(a) and a==b for a,b in pairs),
            'candidate_set_overlap':sum(bool(a&b) for a,b in pairs),
            'disjoint_nonempty_sets':sum(bool(a) and bool(b) and not a&b for a,b in pairs),
            'missing_one_or_both_sets':sum(not a or not b for a,b in pairs)}
        for k,v in counts.items():check(domain+' '+k,v,agreement['domains'][domain][k])
        labels=[(next(iter(a)),next(iter(b))) for a,b in pairs if len(a)==len(b)==1]
        n=len(labels);ca=collections.Counter(a for a,b in labels);cb=collections.Counter(b for a,b in labels)
        expected=sum(ca[c]/n*cb[c]/n for c in set(ca)|set(cb));observed=sum(a==b for a,b in labels)/n
        k=(observed-expected)/(1-expected)
        check(domain+' independent kappa',round(k,12),round(agreement['domains'][domain]['kappa_paired_singletons'],12))
    for key,groups in agreement['strata'].items():
        for domain in ['mayig','wells','helsinki']:
            check('strata coverage '+key+'/'+domain,sum(v[domain]['targets'] for v in groups.values()),96)
    agreed=read(BASE/'mapping-agreed_only.json');keep={r['sign_id'] for r in agreed['rows']}
    expected_keep={r['sign_id'] for r in first['rows'] if set(r['mayig_candidates'])&set(bysecond[r['sign_id']]['mayig_candidates'])}
    check('agreed intersection identities',keep,expected_keep);check('agreed target count',len(keep),78)
    for row in agreed['rows']:
        a=next(r for r in first['rows'] if r['sign_id']==row['sign_id']);b=bysecond[row['sign_id']]
        for domain in ['mayig','wells','helsinki']:check('intersection '+row['sign_id']+'/'+domain,candidates(row,domain),candidates(a,domain)&candidates(b,domain))
    refs=read(BASE/'reference-check.json')
    check('rank/code payload errors',refs['returned_cell_payload_errors'],[])
    check('code369 no direct Mayig code',refs['code369_Mayig_classes'],[])
    check('sole offset exception is damage',[(r['mayig'],r['code']) for r in refs['offset_rule_exceptions']],[('P000','599')])
    freeze=read(BASE/'mapping-freeze.json')
    for label,r in freeze['mappings'].items():check('operational mapping hash '+label,sha(BASE/f'mapping-{label}.json'),r['sha256'])
    pins=read(BASE/'operational-registration.json')
    check('operational code unchanged',sha(OWN/'second_coder_sensitivity.py'),pins['script_sha256'])
    check('reused lexical code unchanged',sha(OWN/'pdf_lexical.py'),pins['lexical_code_sha256'])
    check('pinned dictionary unchanged',sha(RAW/'acquisition-2026-10-08-v1/mw.txt'),pins['dictionary_sha256'])
    check('inventory unchanged',sha(WORK/'reading-inventory-v4.json'),pins['reading_inventory_sha256'])
    aggregates=['field-test.json','fish-units.json','mayig-fields.json','lexical-test.json','lexical-caption-sensitivity.json',
        'reading-joins.json','reading-consistency.json','selection-coverage.json','field-code-recipe.json']
    derivatives=['corpus-field-annotations.json','field-and-fish-shuffles.json','mayig-field-annotations.json',
        'lexical-predictions.json','lexical-caption-predictions.json','reading-join-coverage.json','lexical-selection-v2.json']
    for label in ['first','second','agreed_only']:
        for filename in aggregates:
            a=read(BASE/label/filename);b=read(replay/label/filename)
            # MS patterns are tested as set membership; Python set iteration
            # changes their serialized order without changing the grammar.
            if filename=='field-code-recipe.json':
                a['MS_patterns']=sorted(a['MS_patterns']);b['MS_patterns']=sorted(b['MS_patterns'])
            check('replay '+label+'/'+filename,a,b)
        for filename in derivatives:check('raw replay '+label+'/'+filename,sha(LOCAL/label/filename),sha(raw_replay/label/filename))
        c=read(BASE/label/'field-test.json')['classification'];check('field population '+label,sum(c.values()),2469)
        j=read(BASE/label/'reading-joins.json');check('alias joins '+label,j['alias_joined_attempt_rows'],713)
        check('joined objects '+label,j['alias_joined_object_families'],338)
        support=j['fully_reference_supported_attempts']+j['partially_reference_supported_attempts']+j['no_reference_supported_attempts']
        check('reference coverage partitions '+label,support,859)
        coverage=read(BASE/label/'selection-coverage.json');check('selected coverage '+label,coverage['retained_occurrences']+coverage['removed_occurrences'],640)
    for filename,key in [('field-test.json','classification'),('field-test.json','canonical_clean_shuffle'),('fish-units.json','adjacency')]:
        check('first mapping reproduces PDF '+filename+'/'+key,read(BASE/'first'/filename)[key],read(OUT/filename)[key])
    for filename in ['lexical-test.json','lexical-caption-sensitivity.json']:
        check('first lexical reproduces PDF '+filename,read(BASE/'first'/filename)['panels'],read(OUT/filename)['panels'])
    claims=[json.loads(l) for l in (OWN/'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    old={r['id']:r for r in [json.loads(l) for l in (history/'claims.jsonl').read_text(encoding='utf-8').splitlines()]}
    check('ledger records',len(claims),1021)
    for key in ['paraphrase','quotation','source_id','source_location']:
        check('source ledger wording retained '+key,all(r[key]==old[r['id']][key] for r in claims),True)
    check('agreement dropped targets restricted to packet',all(set(r.get('second_coding_evaluation',{}).get('agreed_only_dropped_targets',[]))<={s['sign_id'] for s in first['rows']} for r in claims),True)
    check('all 58 Table values have two-coding test annotation',sum(bool(r.get('graphic_identity')) and 'S2-A' in r['test_ids'] for r in claims),58)
    result={'status':'Verified computation' if all(c['passed'] for c in checks) else 'Failed',
        'checks':len(checks),'passed':sum(c['passed'] for c in checks),'protected_existing_files':protected,
        'replay':replay.relative_to(ROOT).as_posix(),'results_status':'Exploratory; two AI coding rounds without specialist review',
        'records':checks}
    write(output,result);print({k:v for k,v in result.items() if k!='records'})
    for c in checks:
        if not c['passed']:print(c)
    if result['status']=='Failed':raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--replay',type=Path,default=Path('two-coder-replay-2026-10-09-01'))
    p.add_argument('--output',type=Path,default=Path('two-coder-checks-2026-10-09-v2.json'));a=p.parse_args();main(a.replay,a.output)
