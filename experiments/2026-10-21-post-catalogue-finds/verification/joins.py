"""Re-derive identity joins without importing the coordinator implementation."""
import collections
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,csvrows,save,savecsv,families,ids,sitekey,norm,safe,inputpath
import json

TYPES={'seal':{'SEAL'},'sealing':{'TAG'},'tag':{'TAG'},'tablet':{'TAB'},'inscribed-pottery':{'POT'},'inscribed-tool':{'IMPL','MISC'},'other':{'IMPL','MISC'},'uncertain':{'IMPL','MISC'}}
def compatible(r,f):return (f.get('type') or '').split(':')[0] in TYPES.get(r,set())
def grid(s):
    m=re.search(r'(\d+)\s*[xX]\s*(\d+)(?:\s*[xX]\s*(\d+))?',s or '')
    return tuple(x for x in m.groups() if x is not None) if m else ()
def firstnum(s):
    ns=re.findall(r'\d+',s or '')
    return ns[0] if ns else ''
def registration(s):
    t=re.sub(r'[^A-Z0-9]','',(s or '').upper())
    t=re.sub(r'^(?:DHR|DLV|RGR|FRM|KNM|KMR|SKP|BHR|KRP|BSR)','',t)
    return re.sub(r'\d+',lambda m:str(int(m[0])),t)

def recompute_grid(fam):
    local={fid:rs[0]['metadata']|{'cisi':rs[0].get('source_cisi')} for fid,rs in fam.items() if rs[0]['site']=='Dholavira'}
    regmap=collections.defaultdict(list);famreg={}
    for fid,f in local.items():
        s=(f.get('excavation-idno') or '').strip()
        if re.fullmatch(r'-?DHR[-\s]*\d+',s):
            v=re.sub(r'\D','',s);regmap[v].append(fid);famreg[fid]=v
    seal=json.loads((BASE/'extraction/D/seal-table-D.json').read_text(encoding='utf-8'))
    cats=json.loads((BASE/'extraction/D/catalogue-metadata-D.json').read_text(encoding='utf-8'))
    report=collections.Counter()
    for r in seal:
        g=grid(r.get('gsq'))
        if g:report['seal',g]+=1
    for r in cats:
        if r['kind']!='sealing':continue
        for g in {grid(s) for s in (r.get('gsq') or [])+(r.get('context_gsq') or []) if grid(s)}:report['sealing',g]+=1
    rows=[r for r in csvrows(BASE/'matching/objects-merged.csv') if r['site_code']=='DHV']
    derived={};claimed=set();evidence={}
    for r in rows:
        hits=regmap[firstnum(r['registration'])]
        if len(hits)==1 and compatible(r['object_type'],local[hits[0]]):
            derived[r['row_id']]=('matched',set(hits),'registration-normalised');claimed.add(hits[0])
    for r in rows:
        rid=r['row_id']
        if rid in derived:continue
        g=grid(r['findspot']);kind='sealing' if r['object_type'] in ('sealing','tag') else r['object_type']
        eligible={fid for fid,f in local.items() if g and grid(f.get('block-house'))==g and compatible(r['object_type'],f) and fid not in claimed and not (fid in famreg and firstnum(r['registration']) and famreg[fid]!=firstnum(r['registration']))}
        evidence[rid]={'report_objects_at_grid':report[kind,g],'eligible_unclaimed_families':sorted(eligible),'grid':list(g)}
        if g and len(eligible)==1 and report[kind,g]==1:
            fid=next(iter(eligible));d=local[fid].get('depth') or ''
            # Reproduce the published comparison rule, including its stated unit.
            m=re.match(r'\s*(\d+)\s*'+chr(99)+chr(109),d)
            nums=set(re.findall(r'\d+',r['depth_or_layer']))
            conflict=bool(m and nums and m[1] not in nums)
            derived[rid]=('candidate' if conflict else 'matched',eligible,'context')
            if not conflict:claimed.add(fid)
        elif g and eligible:derived[rid]=('candidate',eligible,'context')
    for r in rows:
        rid=r['row_id']
        if rid in derived:continue
        g=grid(r['findspot'])
        free={fid for fid,f in local.items() if compatible(r['object_type'],f) and fid not in claimed and f.get('cisi') in ('-',None,'') and not(g and grid(f.get('block-house')) and grid(f.get('block-house'))!=g) and fid not in famreg}
        derived[rid]=('candidate',free,'type-only') if free else ('absent',set(),'all-families-assigned')
    actual=csvrows(BASE/'review/dholavira-decisions.csv');differences=[]
    for a in actual:
        d=derived.get(a['row_id'])
        if not d or (a['local_match'],ids(a['local_family_ids']),a['match_basis'])!=d:
            differences.append({'row_id':a['row_id'],'coordinator_status':a['local_match'],'coordinator_families':sorted(ids(a['local_family_ids'])),'coordinator_basis':a['match_basis'],'recomputed_status':d[0] if d else None,'recomputed_families':sorted(d[1]) if d else [],'recomputed_basis':d[2] if d else None})
    save('dholavira-grid-check.json',{'rows_checked':len(actual),'differences':differences,'evidence':evidence,'scope':'Independent implementation of the declared coordinator algorithm. Agreement with that algorithm does not amend the frozen identifier rule.'})
    return differences

def context_check(r,f):
    checks={};conflicts=[]
    checks['object_type_agrees']=compatible(r['object_type'],f)
    if not checks['object_type_agrees']:conflicts.append('object type conflicts')
    a,b=grid(r['findspot']),grid(f.get('block-house'))
    checks['grid_comparable']=bool(a and b);checks['grid_agrees']=a==b if a and b else None
    if a and b and a!=b:conflicts.append('grid-square identity conflicts')
    def area(s):
        m=re.search(r'\b(North|South|East|West|Central|Middle|Lower)\s*(?:Area|Town)\b|\b(Castle|Citadel)\b',s or '',re.I)
        return norm(m[1] or m[2]) if m else ''
    ar,af=area(r['findspot']),area(f.get('area-section'))
    checks['named_area_agrees']=ar==af if ar and af else None
    if ar and af and ar!=af:conflicts.append('named excavation area conflicts')
    def trench(s):
        m=re.search(r'trench\s*([A-Z]*\d+[A-Z0-9]*)',s or '',re.I)
        if not m:m=re.search(r'\b(?:[A-Z]{1,4}\d+[A-Z]?|\d[A-Z]+\d+[A-Z]?)\b',s or '',re.I)
        if not m:return ''
        v=m[1] if m.lastindex else m[0]
        v=v.upper();v={'IH8':'1H8','IB6':'1B6'}.get(v,v)
        return re.sub(r'\d+',lambda x:str(int(x[0])),v)
    if r['site'] in ('Farmana','Kanmer','Karanpura'):
        tr=trench(r['findspot']);tf=trench(f.get('block-house')) or trench(f.get('room-grid'))
        checks['trench_agrees']=tr==tf if tr and tf else None
        if tr and tf and tr!=tf:conflicts.append('excavation trench conflicts')
    a,b=registration(r['registration']),registration(f.get('excavation-idno'))
    checks['registration_equal']=bool(a and b and a==b)
    simple=bool(re.fullmatch(r'-?DHR[-\s]*\d+',(f.get('excavation-idno') or '').strip()))
    if simple and a and b and a!=b:conflicts.append('complete registration conflicts')
    project=re.fullmatch(r'.*project\s*(\d{2})\s*[- ]\s*(\d+)',f.get('excavation-idno') or '',re.I)
    rnums=re.fullmatch(r'\s*(\d{2})\s*[- ]\s*(\d+)\s*',r['registration'])
    if project and rnums and tuple(map(int,project.groups()))!=tuple(map(int,rnums.groups())):conflicts.append('complete project registration conflicts')
    checks['period_comparable']=bool(r['period_or_phase'] and (f.get('period') or f.get('phase')))
    checks['material_comparable']=bool(r['material'] and f.get('material'))
    if checks['material_comparable']:
        a,b=norm(r['material']),norm(f['material'])
        checks['material_agrees']=a==b or {a,b}<= {'clay','terracotta','burnt clay'}
        if not checks['material_agrees'] and a in {'steatite','copper','ivory','bone'} and b in {'steatite','copper','ivory','bone'}:conflicts.append('material conflicts')
    checks['location_fields_checked']=['findspot','area-section','block-house','room-grid']
    checks['depth_fields_checked']=['depth_or_layer','depth']
    checks['period_fields_checked']=['period_or_phase','period','phase','time']
    # Values without shared units, field labels or period vocabularies are not treated as equal.
    checks['depth_assessment']='coordinator numeric comparison checked separately for Dholavira; otherwise no automatic equality from unlabelled numbers'
    checks['period_assessment']='compared at the level of shared labelled phase values only'
    rp=re.search(r'\bphase\s*([IV]+|\d+)\b',r['period_or_phase'],re.I)
    fp=str(f.get('phase') or '')
    fm=re.search(r'\b(?:phase\s*)?([IV]+|\d+)\b',fp,re.I)
    numerals={'I':'1','II':'2','III':'3','IV':'4','V':'5','VI':'6','VII':'7'}
    if rp and fm:
        a=numerals.get(rp[1].upper(),rp[1]);b=numerals.get(fm[1].upper(),fm[1])
        checks['labelled_phase_agrees']=a==b
        if a!=b:conflicts.append('labelled phase conflicts')
    # Do not infer conflicts from different context vocabularies or OCR alone.
    return checks,conflicts

def main():
    fam=families();rows={r['row_id']:r for r in csvrows(inputpath('objects.csv'))};reviews=csvrows(inputpath('join-decisions.csv'))
    assessments=[];rejected=[]
    target={'context','plate-citation','registration-normalised','catalogue-containment'}
    for d in reviews:
        if d['match_basis'] not in target:continue
        r=rows[d['row_id']];basis=d['match_basis'];problems=[];evidence=[]
        for fid in sorted(ids(d['local_family_ids'])):
            if fid not in fam:problems.append('family identifier unavailable');continue
            variants=fam[fid]
            f=variants[0]['metadata'];checks,conflicts=context_check(r,f)
            checks['site_agrees']=any(sitekey(v['site'])==sitekey(r['site']) for v in variants)
            if not checks['site_agrees']:conflicts.append('the family belongs to a different site')
            evidence.append({'family':fid,'checks':checks,'conflicts':conflicts})
            problems.extend(conflicts)
        if basis=='context' and d['local_match']=='matched':
            problems.append('The frozen protocol requires a registration or a publication-specific plate or figure identifier for matched status. Context alone does not supply that identifier.')
        elif basis=='plate-citation':
            linked=' '.join(str(x.get('metadata',{}).get('excavation-idno','')) for fid in ids(d['local_family_ids']) for x in fam.get(fid,[]))
            if r['primary_publication'] not in linked and not re.search(r'IAR\s*2009[-–/]10',linked,re.I):
                problems.append('The family cites a plate identifier without identifying its publication. The numbered plate cannot be tied uniquely to this source.')
        elif basis=='registration-normalised':
            hit=[]
            for fid,vs in fam.items():
                if not any(sitekey(v['site'])==sitekey(r['site']) for v in vs):continue
                for v in vs:
                    a=registration(r['registration']);b=registration(v['metadata'].get('excavation-idno'))
                    if a and (a==b or (a in b and ('project' in norm(v['metadata'].get('excavation-idno'))))):hit.append(fid)
            evidence.append({'identifier_matches_at_site':sorted(set(hit))})
            if len(set(hit))!=1 or set(hit)!=ids(d['local_family_ids']):problems.append('Normalisation does not yield exactly the one cited family at this site.')
        elif basis=='catalogue-containment':
            if r['site_code'] in ('DSL','SKT'):
                problems.append('The decision uses an excavation-level object total and type, without an object identifier establishing baseline containment. The source registration does not distinguish the proposed baseline entries.')
            elif r['site_code']=='NHT':
                # The specific historical discovery and the cited CISI section agree.
                pass
        a={'row_id':d['row_id'],'site':r['site'],'decision':d['local_match'],'match_basis':basis,'families':sorted(ids(d['local_family_ids'])),'field_checks':evidence,'would_reach':not problems,'reasons':list(dict.fromkeys(problems))}
        assessments.append(a)
        if problems:rejected.append(a)
    current=[]
    for d in reviews:
        if d['match_basis'] not in target:continue
        r=rows[d['row_id']];status=d.get('protocol_local_match') or d['local_match'];issues=[];conflicts=[]
        for fid in sorted(ids(r['local_family_ids'])):
            if fid not in fam:continue
            checks,cs=context_check(r,fam[fid][0]['metadata'])
            if cs:conflicts.append({'family':fid,'reasons':cs})
        if status=='candidate' and conflicts:issues.append('The current candidate set contains families with explicit identity or context conflicts.')
        if status=='matched' and d['match_basis']=='context':issues.append('Context alone does not meet the frozen matched-status identifier rule.')
        old=next(a for a in assessments if a['row_id']==d['row_id'])
        if d['match_basis'] in ('plate-citation','catalogue-containment','registration-normalised'):issues.extend(old['reasons'])
        a={'row_id':d['row_id'],'protocol_status':status,'historical_status':d['local_match'],'match_basis':d['match_basis'],'candidate_families_with_conflicts':conflicts,'would_reach_current':not issues,'reasons':list(dict.fromkeys(issues))}
        current.append(a)
    diffs=recompute_grid(fam)
    save('coordinator-join-check.json',{'decisions_checked':len(assessments),'would_not_reach':rejected,'assessments':assessments,'current_protocol_assessments':current,'current_would_not_reach':[a for a in current if not a['would_reach_current']],'dholavira_algorithm_differences':len(diffs),'scope':'Identity-only re-derivation. Historical context decisions are evaluated separately from protocol_local_match and the revised candidate sets. The explicit frozen identifier rule is applied separately from the coordinator context algorithm. Context conflicts require comparable fields; ambiguous OCR and period vocabularies are not silently equated.'})
    print('JOINS checked',len(assessments),'would not reach',len(rejected),'Dholavira algorithm differences',len(diffs))
    print('Rejected by basis',collections.Counter(a['match_basis'] for a in rejected))
    print('Current protocol decisions with unresolved objections',sum(not a['would_reach_current'] for a in current))

if __name__=='__main__':
    try:main()
    except OSError as e:
        try:save('WRITE-FAILURE.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
