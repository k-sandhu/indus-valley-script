"""Third structural audit. Run with python -I -B and a repository argument."""
import collections
import csv
import hashlib
import json
import re
import sys
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
import audit
import verify_v2
from audit import ROOT,BASE,OUT,csvrows,ids,families,safe,norm
from safe_read import RESTRICTED,UNIT
SNAP=OUT/'input-v3-2026-10-21'
NAMES=['objects.csv','sites.csv','join-decisions.csv','local-unnamed.csv']
NEW_NAMES={'verify_v3.py','input-manifest-v3.json','count-check-v3.json','candidate-conflicts-v3.csv','candidate-check-v3.json','locator-check-v3.json','integrity-check-v3.json','WRITE-FAILURE-v3.json'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):
    assert name in NEW_NAMES
    text=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
    if RESTRICTED.search(text) or UNIT.search(text):raise ValueError('Content guard rejected a new audit record.')
    (OUT/name).write_text(text,encoding='utf-8')
def checked_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:rs=list(csv.reader(f,strict=True))
    if not rs or any(len(r)!=len(rs[0]) for r in rs):raise ValueError('Incomplete CSV record: '+p.name)
    return csvrows(p)

def prepare():
    if (OUT/'input-manifest-v3.json').exists():raise ValueError('The third snapshot already exists; refusing replacement.')
    earlier={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in NEW_NAMES and not p.is_relative_to(SNAP)}
    report=OUT/'VERIFICATION.md';prefix=report.read_bytes()
    SNAP.mkdir(exist_ok=False)
    (SNAP/'VERIFICATION-before.md').write_bytes(prefix)
    records=[]
    for name in NAMES:
        p=BASE/name;rows=checked_csv(p);b=p.read_bytes();s=b.decode('utf-8-sig')
        if RESTRICTED.search(s) or UNIT.search(s):raise ValueError('Content guard rejected a snapshot input.')
        target=SNAP/name;target.write_bytes(b)
        assert checked_csv(target)==rows
        records.append({'input':str(p.relative_to(ROOT)),'snapshot':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'rows':len(rows)})
    frozen={str(p.relative_to(ROOT)):sha(p) for p in [BASE/'PROTOCOL.md',BASE/'AMENDMENT-1.md']}
    save('input-manifest-v3.json',{'captured_utc':datetime.now(timezone.utc).isoformat(),'authors':'Codex / GPT-6 / API harness','inputs':records,'earlier_verification_files':earlier,'report_prefix_sha256':hashlib.sha256(prefix).hexdigest(),'report_prefix_bytes':len(prefix),'frozen_protocols':frozen,'scope':'Counts for both reported interpretations; candidate registration, grid, trench and named-area conflicts; match identifiers; locators. The five containment decisions are not reassessed.'})
    print('SNAPSHOT',[(Path(r['input']).name,r['rows']) for r in records],flush=True)

def counts():
    obj=checked_csv(SNAP/'objects.csv');dec=checked_csv(SNAP/'join-decisions.csv');actual=checked_csv(SNAP/'sites.csv')
    claimed=set().union(*(ids(r['local_family_ids']) for r in obj if r['local_match']=='matched'))
    context_claimed=claimed|set().union(*(ids(r.get('context_join_family','')) for r in obj))
    expected=[]
    for site in sorted({r['site'] for r in obj}):
        rs=[r for r in obj if r['site']==site]
        main=[r for r in rs if r['catalogue_status']=='post-catalogue' and r['inscription_status']=='stated']
        nondup=[r for r in main if not r['possible_duplicate_of']]
        def bounds(context):
            def matched(r):return r['local_match']=='matched' or context and bool(r.get('context_join_family'))
            cand=[r for r in nondup if r['local_match']=='candidate' and not matched(r)]
            union=set().union(*(ids(r['local_family_ids']) for r in cand)) if cand else set()
            free=union-(context_claimed if context else claimed)
            absent=sum(r['local_match']=='absent' for r in nondup)
            return sum(bool(matched(r)) for r in main),len(free),absent+max(0,len(cand)-len(free)),sum(not matched(r) for r in main)
        m0,f0,l0,u0=bounds(False);m1,f1,l1,u1=bounds(True)
        pubs=collections.Counter(r['primary_publication'] for r in main)
        expected.append({'site_code':rs[0]['site_code'],'site':site,'country':rs[0]['country'],'baseline':rs[0]['baseline_volume']+' ('+rs[0]['baseline_year']+')','rows_total':len(rs),'rows_main':len(main),'possible_duplicates_main':len(main)-len(nondup),'rows_uncertain_status':sum(r['catalogue_status']=='post-catalogue' and r['inscription_status']=='uncertain' for r in rs),'rows_in_baseline_catalogue':sum(r['catalogue_status']=='in-baseline-catalogue' for r in rs),'rows_possibly_in_cisi3':sum(r['catalogue_status']=='possibly-in-cisi3' for r in rs),'main_matched':m0,'main_candidate':sum(r['local_match']=='candidate' for r in main),'main_absent':sum(r['local_match']=='absent' for r in main),'free_candidate_families':f0,'absent_lower':l0,'absent_upper':u0,'matched_with_context_joins':m1,'absent_lower_with_context_joins':l1,'absent_upper_with_context_joins':u1,'primary_publications':'; '.join(p+' ('+str(n)+')' for p,n in pubs.most_common())})
    total={k:sum(r[k] for r in expected) if isinstance(expected[0][k],int) else '' for k in expected[0]}
    total.update(site_code='ALL',site='All sites');expected.append(total)
    observed={r['site_code']:r for r in actual};differences=[]
    for e in expected:
        a=observed.get(e['site_code'],{})
        for key in set(e)|set(a):
            if str(e.get(key,''))!=a.get(key):differences.append({'site_code':e['site_code'],'column':key,'table_value':safe(a.get(key)),'recomputed_value':safe(e.get(key))})
    for code in set(observed)-{r['site_code'] for r in expected}:differences.append({'site_code':code,'failure':'Unexpected site row'})
    applied=[];rows={r['row_id']:r for r in obj}
    for d in dec:
        r=rows.get(d['row_id'])
        if not r:applied.append({'row_id':d['row_id'],'failure':'Decision row absent from object list'});continue
        if r['local_match']!=(d.get('protocol_local_match') or d['local_match']):applied.append({'row_id':d['row_id'],'failure':'Applied status differs from protocol decision'})
        if ids(r.get('context_join_family',''))!=ids(d.get('context_join_family','')):applied.append({'row_id':d['row_id'],'failure':'Separate context identity differs from decision'})
    result={'snapshot':'input-v3-2026-10-21','object_rows':len(obj),'site_rows':len(expected),'cells_checked':sum(len(r) for r in expected),'differences':differences,'decision_status_differences':applied,'recomputed_total':total,'recomputed_sites':expected,'count_rule':'Main rows are stated post-catalogue rows. The lower bound removes flagged duplicate rows and adds absent rows to the excess of candidate rows over the union of unassigned candidate families. The upper bound includes every main row not matched. In the second interpretation a separate context identity also counts as matched, and its family is assigned.','decision_register_rule':'protocol_local_match and context_join_family are applied decisions. Historical family sets and bases in the decision register are retained by the coordinator and are not compared to the filtered sets as though they were applied sets.','implementation':'New third-check count routine; coordinator code was read but not imported or executed.'}
    save('count-check-v3.json',result)
    print('COUNTS',len(differences),'cell differences;',len(applied),'applied-status differences;',json.dumps(total),flush=True)
    return obj

def number_normal(s):return re.sub(r'\d+',lambda m:str(int(m[0])),s)
def reg_normal(s):
    s=re.split('project',str(s or ''),flags=re.I)[-1]
    s=re.sub(r'[^A-Z0-9]','',s.upper())
    s=re.sub(r'^(?:DHR|DLV|RGR|FRM|KNM|KMR|SKTD|SKP|BHR|KRP|BSR)','',s)
    return number_normal(s)

def complete_registration_conflict(row,local):
    a=str(row or '').strip();b=str(local or '').strip()
    if not a or not b or re.search(r'[?\[\]]',a+b):return False
    # A complete DHR number is directly comparable to the report's field number.
    if re.fullmatch(r'-?DHR[\s-]*\d+',b,re.I) and reg_normal(a).isdigit():return reg_normal(a)!=reg_normal(b)
    # Complete project season-number pairs identify the same numbering scheme.
    if re.search(r'project\s*\d{2}[\s-]+\d+\s*$',b,re.I) and re.fullmatch(r'\d{2}[\s-]+\d+',a):return reg_normal(a)!=reg_normal(b)
    # Other explicit site prefixes can be compared when both use that scheme.
    pa=re.match(r'^-?([A-Za-z]{2,5})[\s-]*\d',a);pb=re.match(r'^-?([A-Za-z]{2,5})[\s-]*\d',b)
    if pa and pb and pa[1].upper()==pb[1].upper() and re.fullmatch(r'-?[A-Za-z]{2,5}[\s-]*\d+',a) and re.fullmatch(r'-?[A-Za-z]{2,5}[\s-]*\d+',b):return reg_normal(a)!=reg_normal(b)
    return False

def grids(s):
    return {tuple(int(x) for x in m.groups() if x is not None) for m in re.finditer(r'\b(\d+)\s*[xX×]\s*(\d+)(?:\s*[xX×]\s*(\d+))?',s or '')}
def grid_conflict(a,b):
    if not a or not b:return False
    # A pair identifies a square; a third component refines it.
    return not any(x[:2]==y[:2] and (len(x)<3 or len(y)<3 or x[2]==y[2]) for x in a for y in b)

def trenches(s):
    s=re.sub('trench',' Trench ',s or '',flags=re.I)
    out=set()
    for m in re.finditer(r'\b(?:TRENCH|TR\.?)(?:\s*|(?=\d))([A-Z]{0,3}\s*\d+[A-Z0-9]*(?:/\d+)?)',s,re.I):
        code=re.sub(r'\s+','',m[1]).upper();code={'IH8':'1H8','IB6':'1B6'}.get(code,code)
        out.add(number_normal(code))
    out.update(number_normal(m[0].upper()) for m in re.finditer(r'\bS\d+E\d+\b',s,re.I))
    return out

def areas(s):
    s=re.sub(r'\bMIDLE\b','MIDDLE',str(s or '').upper())
    named=set();compass=set()
    for m in re.finditer(r'\b(?:CASTLE|CITADEL|BAILEY|ANNEXE?|MIDDLE\s+TOWN|LOWER\s+TOWN)\b',s):
        before=s[max(0,m.start()-30):m.start()]
        # Exclude an external relation to a place. A named feature such as
        # the gate of a town still supplies that town as a possible context.
        if re.search(r'\b(?:OUTSIDE|BEYOND|NEAR)(?:\s+(?:OF|THE))*\s*$',before):continue
        if re.search(r'\b(?:NORTH|SOUTH|EAST|WEST)\s+OF(?:\s+THE)?\s*$',before):continue
        v=re.sub(r'\s+',' ',m[0]);v={'CITADEL':'CASTLE','ANNEX':'ANNEXE'}.get(v,v);named.add(v)
    for m in re.finditer(r'\b(?:NORTH|SOUTH|EAST|WEST|CENTRAL)\b',s):
        if re.match(r'\s+OF\b',s[m.end():]):continue
        compass.add(m[0])
    return named,compass

def conflicts(r,m):
    result=[]
    if complete_registration_conflict(r['registration'],m.get('excavation-idno')):result.append('registration')
    if r['site_code']=='DHV' and grid_conflict(grids(r['findspot']),grids(m.get('block-house'))|grids(m.get('room-grid'))):result.append('grid square')
    tr=trenches(r['findspot']);tf=trenches(' '.join(str(m.get(k) or '') for k in ['area-section','block-house','room-grid']))
    if tr and tf and not tr&tf:result.append('trench')
    ar,cr=areas(r['findspot']);af,cf=areas(m.get('area-section'))
    if ar and af and not ar&af:result.append('named area')
    if cr and cf and not cr&cf:result.append('compass-named area')
    return result

def parser_checks():
    fixtures=[('Citadel aliases Castle',areas('Citadel')[0]==areas('Castle')[0]),('Source spelling normalised',areas('Midle Town')[0]==areas('Middle Town')[0]),('Bailey and Castle distinct',not areas('Bailey')[0]&areas('Castle')[0]),('Annexe recognised',areas('Annexe')[0]=={'ANNEXE'}),('Compass fields compared separately',areas('North; Castle')[0].isdisjoint(areas('North; Lower Town')[0])),('Relative location remains unresolved',not areas('East of Castle')[0]),('Town gate preserves the named town',areas('Lower Town; east gate of Middle Town')[0]=={'LOWER TOWN','MIDDLE TOWN'}),('External location does not identify the town',not areas('Outside Middle Town')[0]),('Grid square with finer context compatible',not grid_conflict(grids('12x34'),grids('12x34x2'))),('Different grid squares conflict',grid_conflict(grids('12x34'),grids('12x35'))),('Fused trench label recognised',trenches('Central AreaTrench Z30')==trenches('Tr. Z30')),('Trench OCR alias',trenches('Tr. IH8')==trenches('Tr. 1H8')),('Conflicting complete registration',complete_registration_conflict('100','DHR-101')),('Project label normalised',not complete_registration_conflict('06-1054','RIHN-Indus project06-1054'))]
    if not all(ok for _,ok in fixtures):raise ValueError('A third-check parser fixture failed.')
    return [{'check':name,'passed':ok} for name,ok in fixtures]

def candidates(obj):
    fam=families();pairs=[];empty=[];variant_differences=[];count=0;candidate_rows=0;matched=[]
    for r in obj:
        if r['local_match']=='candidate':
            candidate_rows+=1;fs=ids(r['local_family_ids'])
            if not fs:empty.append(r['row_id'])
            for fid in sorted(fs,key=int):
                count+=1;vs=fam.get(fid,[])
                if not vs:continue
                cs=[conflicts(r,v['metadata']) for v in vs]
                if any(cs) and not all(cs):variant_differences.append({'row_id':r['row_id'],'family':fid,'reason':'Approved records for this family differ in comparable context; no unambiguous family conflict is asserted.'})
                if all(cs):
                    reasons=sorted(set(x for c in cs for x in c))
                    pairs.append({'row_id':r['row_id'],'family':fid,'site':r['site'],'conflict_fields':'; '.join(reasons),'reason':'Comparable row and family identity fields disagree.'})
        elif r['local_match']=='matched':
            fs=ids(r['local_family_ids']);hits={fid for fid,vs in fam.items() if any(verify_v2.site(v['site'])==verify_v2.site(r['local_site_label']) for v in vs) and verify_v2.registration_matches(r,vs)}
            identifier_ok=len(fs)==1 and fs==hits
            # Every current matched row is registration-based. A plate fallback
            # is not inferred merely from a plate number without its publication.
            field_conflicts=[{'family':fid,'fields':conflicts(r,v['metadata'])} for fid in fs for v in fam.get(fid,[]) if conflicts(r,v['metadata'])]
            matched.append({'row_id':r['row_id'],'families':sorted(fs),'identifier_basis':r['match_basis'],'unique_registration_families_at_site':sorted(hits),'identifier_requirement_met':identifier_ok,'comparable_context_conflicts':field_conflicts})
    with (OUT/'candidate-conflicts-v3.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['row_id','family','site','conflict_fields','reason']);w.writeheader();w.writerows(pairs)
    result={'snapshot':'input-v3-2026-10-21','candidate_rows_checked':candidate_rows,'candidate_family_pairs_checked':count,'conflicting_pair_count':len(pairs),'conflicting_row_count':len({p['row_id'] for p in pairs}),'conflict_csv':'candidate-conflicts-v3.csv','empty_candidate_sets':empty,'family_variant_disagreements':variant_differences,'matched_rows_checked':len(matched),'match_identifier_failures':[r for r in matched if not r['identifier_requirement_met']],'matched_context_failures':[r for r in matched if r['comparable_context_conflicts']],'matched_assessments':matched,'parser_checks':parser_checks(),'scope':'Registration, Dholavira grid square, trench and named excavation area only. Every candidate set is checked, including baseline candidates and any retained context family. Object-class, material and containment decisions are outside this third check.','comparison_rule':'Only comparable complete registrations are treated as conflicts. Grid pairs and their refinements can overlap. Castle and Citadel are equivalent; Bailey, Middle Town (including Midle Town), Lower Town and Annexe remain distinct. Compass and named town areas are compared separately. A location merely relative to an area does not affirm that area. Each family is rejected only when every approved record for it has a comparable conflict.','implementation':'New independent conflict parser; approved corpus identity projection and prior independent registration matcher reused. No coordinator implementation imported or executed.'}
    save('candidate-check-v3.json',result)
    print('CANDIDATES',candidate_rows,'rows;',count,'pairs;',len(pairs),'conflicts; empty',len(empty),'; match identifier failures',len(result['match_identifier_failures']),flush=True)
    for r in pairs:print(json.dumps(r),flush=True)

def locators():
    verify_v2.SNAP=SNAP
    def routed(name,data):
        assert name=='locator-check-v2.json'
        data['snapshot']='input-v3-2026-10-21';data['implementation_reused']='Prior independent locator routine in verify_v2.py; only the frozen input and new output destination change.'
        save('locator-check-v3.json',data)
    verify_v2.save=routed
    verify_v2.run_locators()

def inspect_conflicts():
    rows={r['row_id']:r for r in checked_csv(SNAP/'objects.csv')};fam=families()
    for p in checked_csv(OUT/'candidate-conflicts-v3.csv'):
        r=rows[p['row_id']]
        print(json.dumps({'row_id':r['row_id'],'findspot':safe(r['findspot']),'match_basis':r['match_basis'],'context_join_family':r['context_join_family'],'parsed_named_area':sorted(areas(r['findspot'])[0]),'parsed_compass':sorted(areas(r['findspot'])[1])}))
        for v in fam[p['family']]:
            m=v['metadata']
            print(json.dumps({'family':p['family'],'area':safe(m.get('area-section')),'block':safe(m.get('block-house')),'parsed_named_area':sorted(areas(m.get('area-section'))[0]),'parsed_compass':sorted(areas(m.get('area-section'))[1])}))

def integrity(append=False):
    manifest=json.loads((OUT/'input-manifest-v3.json').read_text(encoding='utf-8'));changed=[];live=[];malformed=[]
    for name,h in manifest['earlier_verification_files'].items():
        p=OUT/name
        if name=='VERIFICATION.md':
            before=(SNAP/'VERIFICATION-before.md').read_bytes()
            if not p.read_bytes().startswith(before):changed.append(name)
        elif not p.exists() or sha(p)!=h:changed.append(name)
    for item in manifest['inputs']:
        if sha(ROOT/item['input'])!=item['sha256'] or sha(ROOT/item['snapshot'])!=item['sha256']:live.append(item['input'])
    frozen=[n for n,h in manifest['frozen_protocols'].items() if sha(ROOT/n)!=h]
    for p in [SNAP/n for n in NAMES]+[OUT/n for n in ['count-check-v3.json','candidate-check-v3.json','candidate-conflicts-v3.csv','locator-check-v3.json']]:
        try:
            if p.suffix=='.csv':checked_csv(p)
            else:json.loads(p.read_text(encoding='utf-8'))
        except (ValueError,csv.Error):malformed.append(p.name)
    if changed or live or frozen or malformed:raise ValueError('Third-check integrity failed: '+json.dumps({'earlier_changes':changed,'input_changes':live,'protocol_changes':frozen,'malformed_records':malformed}))
    c=json.loads((OUT/'count-check-v3.json').read_text(encoding='utf-8'));j=json.loads((OUT/'candidate-check-v3.json').read_text(encoding='utf-8'));l=json.loads((OUT/'locator-check-v3.json').read_text(encoding='utf-8'))
    if append:
        t=c['recomputed_total']
        text='\n## Third check of the rebuilt files\n\n'
        text+=f"We froze the rebuilt inputs in input-v3-2026-10-21/ and recomputed all {c['cells_checked']} site-table cells. There are {len(c['differences'])} count-cell differences and {len(c['decision_status_differences'])} applied-status differences. The {t['rows_main']} main rows comprise {t['main_matched']} matched, {t['main_candidate']} candidate and {t['main_absent']} absent rows, with protocol absent bounds {t['absent_lower']}–{t['absent_upper']}. Accepting the separate context joins gives {t['matched_with_context_joins']} matched rows and bounds {t['absent_lower_with_context_joins']}–{t['absent_upper_with_context_joins']}. count-check-v3.json records every recomputed cell.\n\n"
        text+=f"Our independent conflict test examined {j['candidate_family_pairs_checked']} row–family pairs across all {j['candidate_rows_checked']} candidate sets, including baseline candidates and retained context families. It found {j['conflicting_pair_count']} conflicting pairs in {j['conflicting_row_count']} rows on registration, grid square, trench or named area; candidate-conflicts-v3.csv records each pair. The field for PCF-DHV-206 names Lower Town and the east gate of Middle Town, so both towns remain possible contexts. There are {len(j['empty_candidate_sets'])} empty candidate sets. All {j['matched_rows_checked']} matched rows have unique registration ties; the identifier check has {len(j['match_identifier_failures'])} failures and the comparable-context check has {len(j['matched_context_failures'])} failures. candidate-check-v3.json gives the individual assessments and parser checks. Object class, material and the five unchanged containment decisions were outside this check.\n\n"
        text+=f"The locator audit checks {l['primary_page_locators_checked']} primary page locators and {l['secondary_references_checked']} secondary publication identifiers, family membership under local_site_label, match cardinality and duplicate links, and baseline identifiers in cisi_in_baseline or other_numbers. It reports {l['failure_count']} locator or identifier failures and {len(l['empty_primary_page_text'])} empty primary text records in locator-check-v3.json. The earlier report text and every earlier verification file are preserved. input-manifest-v3.json records the input and preservation hashes; integrity-check-v3.json records completeness and preservation checks. The new script is verify_v3.py. This third check used existing text and approved corpus identity fields; no OCR, image view, download or installation was needed.\n"
        if RESTRICTED.search(text) or UNIT.search(text):raise ValueError('Report append content guard failed.')
        report=OUT/'VERIFICATION.md'
        if b'## Third check of the rebuilt files' in report.read_bytes():raise ValueError('Third-check section already exists; refusing duplicate append.')
        with report.open('ab') as f:f.write(text.encode('utf-8'))
    report=OUT/'VERIFICATION.md';before=(SNAP/'VERIFICATION-before.md').read_bytes()
    result={'earlier_verification_files_checked':len(manifest['earlier_verification_files']),'earlier_file_changes':changed,'earlier_report_prefix_preserved':report.read_bytes().startswith(before),'live_inputs_equal_snapshot':not live,'frozen_protocols_unchanged':not frozen,'new_record_completeness_failures':malformed,'parser_checks_passed':all(x['passed'] for x in j['parser_checks']),'corpus_projection':'Only the approved identity and context fields are decoded by audit.families.','report_section_appended':b'## Third check of the rebuilt files' in report.read_bytes(),'source_access':'Existing page text is checked mechanically for non-empty primary locators; no page description or image is displayed.','output_paths':['count-check-v3.json','candidate-conflicts-v3.csv','candidate-check-v3.json','locator-check-v3.json','VERIFICATION.md'],'code_sha256':sha(OUT/'verify_v3.py')}
    save('integrity-check-v3.json',result)
    print('INTEGRITY earlier files unchanged',len(manifest['earlier_verification_files']),'; new records complete; section appended',result['report_section_appended'],flush=True)

if __name__=='__main__':
    try:
        mode=sys.argv[2]
        if mode=='prepare':prepare()
        elif mode=='check':
            obj=counts();candidates(obj);locators();integrity()
        elif mode=='report':integrity(append=True)
        elif mode=='integrity':integrity()
        elif mode=='inspect':inspect_conflicts()
    except OSError as e:
        try:save('WRITE-FAILURE-v3.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
