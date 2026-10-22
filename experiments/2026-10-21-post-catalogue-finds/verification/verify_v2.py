"""Audit the frozen follow-up snapshot using approved identity fields."""
import collections
import json
import re
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
import audit
import joins
from audit import ROOT,BASE,OUT,csvrows,ids,norm,safe,families,page_index,page_numbers,references
SNAP=OUT/'input-v2-2026-10-21'
def inputpath(name):return SNAP/name
def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def site(s):return re.sub('[^a-z0-9]','',norm(s))
def metadata(v):return v.get('metadata',{})
def present(v):return bool(v and str(v).strip() not in {'-','--','None'})

def contexts(r,f):
    checks,conflicts=joins.context_check(r,f)
    # Preserve the explicit type mapping in the matching prompt.
    # An external location relative to an area does not identify that area.
    def areas(s):
        out=set()
        for m in re.finditer(r'\b(?:North|South|East|West|Central|Middle|Lower)\s*(?:Area|Town)\b|\b(?:Castle|Citadel)\b',s or '',re.I):
            before=(s or '')[max(0,m.start()-28):m.start()]
            if re.search(r'\b(?:outside|of|near|beyond)\s*$',before,re.I):continue
            out.add(norm(m[0]).replace('citadel','castle'))
        return out
    ar,af=areas(r['findspot']),areas(str(f.get('area-section') or ''))
    conflicts=[x for x in conflicts if x!='named excavation area conflicts']
    checks['named_area_agrees']=bool(ar&af) if ar and af else None
    if ar and af and not ar&af:conflicts.append('named excavation area conflicts')
    # Trench labels may occur in any of the three approved location fields.
    def trenches(s):
        s=(s or '').upper()
        out=set()
        for m in re.finditer(r'\b(?:TRENCH|TR\.)\s*([A-Z]{0,3}\s*\d+[A-Z0-9]*)',s):
            t=re.sub(r'\s+','',m[1]);t={'IH8':'1H8','IB6':'1B6'}.get(t,t)
            t=re.sub(r'\d+',lambda m:str(int(m[0])),t);out.add(t)
        out.update(re.findall(r'\bS\d+E\d+\b',s))
        return out
    a=trenches(r['findspot']);b=trenches(' '.join(str(f.get(k) or '') for k in ['area-section','block-house','room-grid']))
    if a and b:
        checks['explicit_trench_agrees']=bool(a&b)
        if not a&b:conflicts.append('explicit excavation trench conflicts')
    return checks,sorted(set(conflicts))

def registration_matches(r,variants):
    a=joins.registration(r['registration'])
    if not a:return False
    for v in variants:
        raw=str(metadata(v).get('excavation-idno') or '')
        b=joins.registration(raw)
        # The export prepends a project label in Kanmer identities.
        if 'project' in raw.casefold():b=joins.registration(re.split('project',raw,flags=re.I)[-1])
        if a==b:return True
        # Appended identifiers are accepted only at an explicit separator.
        if any(a==joins.registration(piece) for piece in re.split(r'[;,|]',raw) if piece.strip()):return True
    return False

def run_counts():
    audit.inputpath=inputpath
    audit.save=lambda name,data:save('count-check-v2.json' if name=='count-check.json' else name,data)
    audit.counts()

def run_joins():
    obj=csvrows(inputpath('objects.csv'));fam=families();dec=csvrows(inputpath('join-decisions.csv'))
    assessments=[];failures=[];cand_checks=[];refinement=[]
    for r in obj:
        rid=r['row_id'];fs=ids(r['local_family_ids']);issues=[];evidence=[]
        if r['local_match']=='matched':
            hits={fid for fid,vs in fam.items() if any(site(v['site'])==site(r['local_site_label']) for v in vs) and registration_matches(r,vs)}
            if len(fs)!=1:issues.append('Matched status requires exactly one family.')
            if len(hits)!=1 or hits!=fs:issues.append('Registration normalisation does not identify exactly the cited family at this site.')
            for fid in sorted(fs):
                vs=fam.get(fid,[])
                field_checks=[contexts(r,metadata(v)) for v in vs]
                cs=sorted(set(x for _,xs in field_checks for x in xs))
                if cs:issues.extend(cs)
                evidence.append({'family':fid,'registration_tie':registration_matches(r,vs),'field_checks':[c for c,_ in field_checks],'conflicts':cs})
            if r.get('context_join_family'):issues.append('A protocol matched row also carries a context-only join.')
            assessments.append({'row_id':rid,'match_basis':r['match_basis'],'status':'matched','identifier_families_at_site':sorted(hits),'evidence':evidence,'would_reach':not issues,'reasons':issues})
        if r['local_match']=='candidate':
            conflicts=[]
            if not fs:issues.append('Candidate set is empty.')
            for fid in sorted(fs):
                if fid not in fam:continue
                variants=fam[fid]
                all_checks=[contexts(r,metadata(v)) for v in variants]
                # A family is rejected only when no approved face record is compatible.
                if all(cs for _,cs in all_checks):conflicts.append({'family':fid,'reasons':sorted(set(c for _,cs in all_checks for c in cs))})
            if conflicts:issues.append('Candidate set includes a family with a comparable identity or context conflict.')
            cand_checks.append({'row_id':rid,'families_checked':len(fs),'empty':not fs,'conflicts':conflicts,'would_reach':not issues,'reasons':issues})
        if r['match_basis'] in {'context','plate-number'} or r.get('context_join_family'):
            problems=[]
            # Context is retained in the historical decision register; applied object status is checked here.
            if r['local_match']=='matched':problems.append('Context-only evidence is applied as a protocol match.')
            if r.get('context_join_family'):
                if r['local_match']!='candidate':problems.append('Context-joined object does not remain a protocol candidate.')
                if len(ids(r['context_join_family']))!=1:problems.append('Context join does not identify one family.')
                if not r.get('context_join_basis'):problems.append('Context join lacks its separate evidence field.')
                if not ids(r['context_join_family'])<=fs:problems.append('Context join is missing from the protocol candidate set.')
            elif r.get('context_join_basis'):problems.append('Context evidence is present without a context family.')
            refinement.append({'row_id':rid,'protocol_status':r['local_match'],'match_basis':r['match_basis'],'context_join_family':r.get('context_join_family',''),'failures':problems})
            issues.extend(problems)
        if issues:failures.append({'row_id':rid,'status':r['local_match'],'match_basis':r['match_basis'],'reasons':sorted(set(issues))})
    selected=[d for d in dec if d['match_basis'] in {'context','plate-citation','plate-number','registration-normalised','catalogue-containment'}]
    # The original independent grid implementation is repeated into a new endpoint.
    joins.save=lambda name,data:save(name.replace('.json','-v2.json'),data)
    grid_diffs=joins.recompute_grid(fam)
    containment=json.loads((OUT/'containment-review-v2.json').read_text(encoding='utf-8')) if (OUT/'containment-review-v2.json').exists() else {'assessments':[],'status':'awaiting site-section review'}
    failures.extend({'row_id':a['row_id'],'status':'in-baseline-catalogue','match_basis':'catalogue-containment','reasons':a['reasons']} for a in containment['assessments'] if not a['would_reach'])
    chosen={d['row_id'] for d in selected}
    selected_assessments=[]
    for d in selected:
        r=next(r for r in obj if r['row_id']==d['row_id'])
        ca=next((x for x in cand_checks if x['row_id']==d['row_id']),None)
        ma=next((x for x in assessments if x['row_id']==d['row_id']),None)
        co=next((x for x in containment['assessments'] if x['row_id']==d['row_id']),None)
        problems=next((x['reasons'] for x in failures if x['row_id']==d['row_id']),[])
        selected_assessments.append({'row_id':d['row_id'],'match_basis':d['match_basis'],'historical_status':d['local_match'],'protocol_status':r['local_match'],'context_join_family':r.get('context_join_family',''),'candidate_conflicts':ca['conflicts'] if ca else [],'registration_tie':ma['would_reach'] if ma else None,'containment_confirmed':co['would_reach'] if co else None,'would_reach':not problems,'reasons':problems})
    result={'snapshot':'input-v2-2026-10-21','object_rows':len(obj),'coordinator_decisions':len(dec),'selected_coordinator_decisions':len(selected),'selected_coordinator_assessments':selected_assessments,'coordinator_would_not_reach':[x for x in failures if x['row_id'] in chosen],'supplemental_candidate_objections':[x for x in failures if x['row_id'] not in chosen],'matched_rows_checked':len(assessments),'matched_assessments':assessments,'candidate_rows_checked':len(cand_checks),'empty_candidate_sets':[x['row_id'] for x in cand_checks if x['empty']],'candidate_assessments':cand_checks,'context_rows_checked':len(refinement),'context_join_rows':sum(bool(r.get('context_join_family')) for r in obj),'context_storage_checks':refinement,'containment':containment,'would_not_reach':failures,'dholavira_algorithm_rows':len(csvrows(BASE/'review/dholavira-decisions.csv')),'dholavira_algorithm_differences':grid_diffs,'rule':'Protocol matches require one unique registration tie or a publication-specific plate or figure citation, with compatible context. Every current matched row is tested through its registration; none claims a plate-only match. Context identities are retained only as a separate applied sensitivity identity. Historical local_match columns in the decision register are not the applied status. Unknown context values supply no affirmative agreement. Named-area conflicts compare explicit internal areas; a location described only relative to an area does not identify that area.','projection':'Only the approved identity and context fields are decoded from the local corpus.'}
    save('coordinator-join-check-v2.json',result)
    print('JOINS',len(assessments),'matched;',len(cand_checks),'candidate;',len(failures),'objections; empty',len(result['empty_candidate_sets']),'grid differences',len(grid_diffs))
    print('SELECTED coordinator objections',len(result['coordinator_would_not_reach']),'supplemental candidate objections',len(result['supplemental_candidate_objections']))
    print('CONFLICT reasons',collections.Counter(x for r in cand_checks for f in r['conflicts'] for x in f['reasons']))

def run_locators():
    fam=families();idx=page_index();obj=csvrows(inputpath('objects.csv'))
    reg={}
    for name in ['matching/source-register.csv','acquisition/source-register-1a.csv','acquisition-web/source-candidates-1b.csv']:
        for r in csvrows(BASE/name):reg.setdefault(r['source_id'],r)
    prefixes={m[1] for vs in fam.values() for d in vs for m in re.finditer(r'\b([A-Za-z]+)-\d+',str(d.get('source_cisi') or ''))}
    cp=re.compile(r'\b(?:'+'|'.join(re.escape(x) for x in sorted(prefixes,key=len,reverse=True))+r')[ -]\d+\b',re.I)
    failures=[];empty=[];claimed=collections.defaultdict(list);pcount=scount=fcount=ccount=baseline=0
    for r in obj:
        rid=r['row_id'];sid=r['primary_publication']
        if sid not in reg:failures.append({'row_id':rid,'failure':'Unknown primary source','source_id':sid})
        pgs=page_numbers(r['pdf_page'])
        if not pgs:failures.append({'row_id':rid,'failure':'Missing PDF-page locator'})
        for pg in pgs:
            pcount+=1
            if (sid,pg) not in idx:failures.append({'row_id':rid,'failure':'Page text missing','source_id':sid,'pdf_page':pg})
            elif not any(p.read_text(encoding='utf-8-sig',errors='replace').strip() for p in idx[sid,pg]):empty.append({'row_id':rid,'source_id':sid,'pdf_page':pg})
        for s,pg,raw in references(r,reg):
            scount+=1
            if not s:failures.append({'row_id':rid,'failure':'Unknown secondary source','reference':safe(raw)})
        for field in ['local_family_ids','context_join_family']:
            for fid in ids(r.get(field,'')):
                if field=='local_family_ids':fcount+=1
                else:ccount+=1
                if fid not in fam:failures.append({'row_id':rid,'failure':'Unknown family','field':field,'family':fid})
                elif not any(site(v['site'])==site(r['local_site_label']) for v in fam[fid]):failures.append({'row_id':rid,'failure':'Family site differs from local_site_label','field':field,'family':fid,'local_site_label':r['local_site_label']})
        if r['local_match']=='matched':
            fs=ids(r['local_family_ids'])
            if len(fs)!=1:failures.append({'row_id':rid,'failure':'Matched row does not identify exactly one family'})
            for fid in fs:claimed[fid].append(r)
        if r['catalogue_status']=='in-baseline-catalogue':
            baseline+=1
            if not cp.search(r.get('cisi_in_baseline','')) and not cp.search(r.get('other_numbers','')):failures.append({'row_id':rid,'failure':'Baseline row has no CISI identifier in its designated identity columns'})
    edges={frozenset([r['row_id'],target]) for r in obj for target in ids(r['possible_duplicate_of'])}
    for fid,rs in claimed.items():
        for i,a in enumerate(rs):
            for b in rs[i+1:]:
                if frozenset([a['row_id'],b['row_id']]) not in edges:failures.append({'failure':'Family matched twice without duplicate flag','family':fid,'row_ids':[a['row_id'],b['row_id']]})
    save('locator-check-v2.json',{'snapshot':'input-v2-2026-10-21','object_rows':len(obj),'primary_page_locators_checked':pcount,'secondary_references_checked':scount,'family_memberships_checked':fcount,'context_family_memberships_checked':ccount,'matched_rows':sum(r['local_match']=='matched' for r in obj),'baseline_rows_checked':baseline,'source_ids_in_registers':len(reg),'failure_count':len(failures),'failures':failures,'empty_primary_page_text':empty,'policy':'Site membership uses the explicit local_site_label, with only punctuation and case normalised. Baseline identifiers must be in cisi_in_baseline or other_numbers. Every PDF page in a range is checked. Secondary publication identifiers, unique match cardinality and duplicate links are checked independently.'})
    print('LOCATORS',len(failures),'failures;',len(empty),'empty primary pages')

if __name__=='__main__':
    try:
        {'counts':run_counts,'joins':run_joins,'locators':run_locators}[sys.argv[2]]()
    except OSError as e:
        try:save('WRITE-FAILURE-v2.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
