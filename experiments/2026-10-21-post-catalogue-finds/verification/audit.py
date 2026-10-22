"""Independent structural audit. Use Python -I and pass the repository path."""
import argparse
import collections
import csv
import hashlib
import functools
import json
import math
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')
sys.dont_write_bytecode=True
ROOT=Path(sys.argv[1]).resolve()
BASE=ROOT/'experiments/2026-10-21-post-catalogue-finds'
OUT=BASE/'verification'
RAW=ROOT/'data/raw/2026-10-21-post-catalogue-finds'
sys.path.insert(0,str(OUT))
from safe_read import RESTRICTED

def csvrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def inputpath(name):
    p=OUT/'revised-input-2026-10-21'/name
    return p if p.exists() else BASE/name

def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def savecsv(name,data,fields):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)

def interval(k,n):
    if not n:return [0.0,1.0]
    def prob(p,lo,hi):
        if p<=0:return float(lo==0)
        if p>=1:return float(hi==n)
        return sum(math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)+i*math.log(p)+(n-i)*math.log1p(-p)) for i in range(lo,hi+1))
    lo=0.0
    if k:
        a,b=0.0,1.0
        for _ in range(70):
            p=(a+b)/2
            if prob(p,k,n)<.025:a=p
            else:b=p
        lo=(a+b)/2
    hi=1.0
    if k<n:
        a,b=0.0,1.0
        for _ in range(70):
            p=(a+b)/2
            if prob(p,0,k)>.025:a=p
            else:b=p
        hi=(a+b)/2
    return [lo,hi]

def ids(s):return set(filter(None,re.split(r'[|;]',s or '')))
def page_numbers(s):
    out=[]
    for m in re.finditer(r'\d+\s*[-–]\s*\d+|\d+',s or ''):
        nums=list(map(int,re.findall(r'\d+',m[0])))
        if len(nums)==2 and nums[0]<=nums[1] and nums[1]-nums[0]<10000:out.extend(range(nums[0],nums[1]+1))
        else:out.extend(nums)
    return list(dict.fromkeys(out))
def norm(s):return re.sub(r'\s+',' ',str(s or '')).strip().casefold()
def safe(s):
    if RESTRICTED.search(str(s)) or re.search(r'\b\d+(?:\.\d+)?\s*(?:m{2}|c[m])\b',str(s),re.I):return '[restricted input withheld]'
    return s

def blind():
    path=OUT/'blind-observations-frozen.csv'
    freeze=json.loads((OUT/'blind-freeze.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(path.read_bytes()).hexdigest()==freeze['sha256']
    obs=csvrows(path); table={r['row_id']:r for r in csvrows(BASE/'objects.csv')}
    fields=[k for k in obs[0] if k not in ('row_id','assessment_note')]
    out=[];summary={}
    for f in fields:
        k=n=unassessed=notapp=0
        for r in obs:
            v=r[f]
            if f=='registration_present':t='yes' if table[r['row_id']]['registration'] else 'not-applicable'
            else:t=table[r['row_id']][f]
            if v=='UNASSESSABLE':agreement='unassessable';unassessed+=1
            elif v=='not-applicable':agreement='not-applicable';notapp+=1
            else:
                n+=1; equal=norm(v)==norm(t);k+=equal;agreement='yes' if equal else 'no'
            out.append(dict(row_id=r['row_id'],field=f,table_value=safe(t),verification_value=safe(v),agreement=agreement))
        summary[f]={'agreements':k,'assessed':n,'unassessed':unassessed,'not_applicable':notapp,'rate':k/n if n else None,'exact_binomial_95':interval(k,n),'all_applicable_denominator':len(obs)-notapp,'conservative_rate':k/(len(obs)-notapp) if len(obs)>notapp else None,'conservative_exact_binomial_95':interval(k,len(obs)-notapp)}
    savecsv('blind-sample.csv',out,list(out[0]))
    save('blind-summary.json',{'sample':len(obs),'comparison_rule':'Case and whitespace normalisation only. Unknown is a recorded value. Unassessed fields are reported separately; their exclusion changes the population of each agreement interval.','interval':'Two-sided Clopper-Pearson 95%; conditional descriptive intervals, without weighting or finite-population correction. Rows on shared pages are dependent.','freeze':freeze,'fields':summary,'disagreements':sum(r['agreement']=='no' for r in out),'unassessed_fields':sum(r['agreement']=='unassessable' for r in out)})
    print('BLIND',json.dumps(summary))

def skip_value(s,i):
    # Skip excluded JSON values without decoding or retaining their values.
    i0=i
    if s[i]=='"':
        i+=1
        while i<len(s):
            if s[i]=='\\':i+=2
            elif s[i]=='"':return i+1
            else:i+=1
    elif s[i] in '[{':
        stack=[s[i]];i+=1
        while stack:
            if s[i]=='"':i=skip_value(s,i)
            elif s[i] in '[{':stack.append(s[i]);i+=1
            elif s[i] in ']}':stack.pop();i+=1
            else:i+=1
        return i
    else:
        while i<len(s) and s[i] not in ',}]\r\n':i+=1
        return i
    raise ValueError('Invalid JSON value')

TOP={'record_id','object_family_id','source_cisi','site','region','object_type'}
META={'excavation-idno','area-section','block-house','room-grid','depth','time','period','phase','material','type','sides'}
DEC=json.JSONDecoder()
def project(s,start=0,metadata=False):
    i=start+1;result={}
    while True:
        while s[i].isspace() or s[i]==',':i+=1
        if s[i]=='}':return result,i+1
        key,end=DEC.raw_decode(s,i);i=end
        while s[i].isspace() or s[i]==':':i+=1
        if not metadata and key=='metadata':result[key],i=project(s,i,True)
        elif key in (META if metadata else TOP):result[key],i=DEC.raw_decode(s,i)
        else:i=skip_value(s,i)

def families():
    fam={}
    p=ROOT/'data/normalized/lipi_observed_faces.jsonl'
    with p.open(encoding='utf-8') as f:
        for line in f:
            d,_=project(line)
            fid=str(d['object_family_id']);d['object_family_id']=fid
            fam.setdefault(fid,[]).append(d)
    return fam

@functools.lru_cache(maxsize=None)
def sitekey(s):
    t=re.sub('[^a-z0-9]','',norm(s))
    aliases={'goladhorobagasra':'bagasra','goladhoro':'bagasra','lakhanjodaro':'lakhanjodaro','rupnagar':'rupar','surkotda':'surkotada','desalpur':'desalpar'}
    # Site spellings in the declared seed aliases are equivalent.
    for r in csvrows(BASE/'selection/sites-seed.csv'):
        canonical=re.sub('[^a-z0-9]','',norm(r['site']))
        for alias in re.split(r'[|;]',r.get('aliases','')):
            if alias:aliases[re.sub('[^a-z0-9]','',norm(alias))]=canonical
    return aliases.get(t,t)

def counts():
    obj=csvrows(inputpath('objects.csv')); decisions=csvrows(inputpath('join-decisions.csv')); diffs=[];decision_diffs=[];historical_diffs=[]
    last={r['row_id']:r for r in decisions}
    for r in obj:
        d=last.get(r['row_id'])
        if d:
            for k in ('local_match','local_family_ids','match_basis','catalogue_status','possible_duplicate_of'):
                if r[k]!=d[k]:historical_diffs.append({'row_id':r['row_id'],'field':k,'object_table':safe(r[k]),'decision_table':safe(d[k])})
            target=d.get('protocol_local_match') or d['local_match']
            if r['local_match']!=target:decision_diffs.append({'row_id':r['row_id'],'field':'local_match','object_table':r['local_match'],'protocol_decision':target})
            converted=target!=d['local_match']
            if converted:
                if ids(r.get('context_join_family',''))!=ids(d.get('context_join_family') or d['local_family_ids']):decision_diffs.append({'row_id':r['row_id'],'field':'context_join_family','failure':'historical context identity not preserved'})
            elif ids(r['local_family_ids'])!=ids(d['local_family_ids']):decision_diffs.append({'row_id':r['row_id'],'field':'local_family_ids','failure':'decision family set differs'})
            for k in ('match_basis','catalogue_status','possible_duplicate_of'):
                if r[k]!=d[k]:decision_diffs.append({'row_id':r['row_id'],'field':k,'failure':'decision differs'})
    claimed=set().union(*(ids(r['local_family_ids']) for r in obj if r['local_match']=='matched'))
    context_claimed=claimed|set().union(*(ids(r.get('context_join_family','')) for r in obj))
    expected=[]
    for site in sorted(set(r['site'] for r in obj)):
        rs=[r for r in obj if r['site']==site]; mains=[r for r in rs if r['catalogue_status']=='post-catalogue' and r['inscription_status']=='stated']
        unique=[r for r in mains if not r['possible_duplicate_of']]
        cands=[r for r in unique if r['local_match']=='candidate']
        free=set().union(*(ids(r['local_family_ids']) for r in cands))-claimed if cands else set()
        freq=collections.Counter(r['primary_publication'] for r in mains)
        d={'site_code':rs[0]['site_code'],'site':site,'country':rs[0]['country'],'baseline':rs[0]['baseline_volume']+' ('+rs[0]['baseline_year']+')','rows_total':len(rs),'rows_main':len(mains),'possible_duplicates_main':sum(bool(r['possible_duplicate_of']) for r in mains),'rows_uncertain_status':sum(r['catalogue_status']=='post-catalogue' and r['inscription_status']=='uncertain' for r in rs),'rows_in_baseline_catalogue':sum(r['catalogue_status']=='in-baseline-catalogue' for r in rs),'rows_possibly_in_cisi3':sum(r['catalogue_status']=='possibly-in-cisi3' for r in rs),'main_matched':sum(r['local_match']=='matched' for r in mains),'main_candidate':len([r for r in mains if r['local_match']=='candidate']),'main_absent':sum(r['local_match']=='absent' for r in mains),'free_candidate_families':len(free),'absent_lower':sum(r['local_match']=='absent' for r in unique)+max(0,len(cands)-len(free)),'absent_upper':sum(r['local_match']!='matched' for r in mains),'primary_publications':'; '.join(p+' ('+str(n)+')' for p,n in freq.most_common())}
        ctx_cand=[r for r in unique if r['local_match']=='candidate' and not r.get('context_join_family')]
        ctx_free=(set().union(*(ids(r['local_family_ids']) for r in ctx_cand))-context_claimed) if ctx_cand else set()
        d.update(matched_with_context_joins=sum(r['local_match']=='matched' or bool(r.get('context_join_family')) for r in mains),
                 absent_lower_with_context_joins=sum(r['local_match']=='absent' for r in unique)+max(0,len(ctx_cand)-len(ctx_free)),
                 absent_upper_with_context_joins=sum(r['local_match']!='matched' and not r.get('context_join_family') for r in mains))
        expected.append(d)
    total={k:'' for k in expected[0]};total.update(site_code='ALL',site='All sites')
    for k in total:
        if isinstance(expected[0][k],int):total[k]=sum(d[k] for d in expected)
    expected.append(total)
    actual=csvrows(inputpath('sites.csv')); actual_by={r['site_code']:r for r in actual}
    for e in expected:
        a=actual_by.get(e['site_code'],{})
        for k,v in e.items():
            if str(v)!=a.get(k):diffs.append({'site':e['site'],'column':k,'table_value':a.get(k),'recomputed_value':v})
        for k in set(a)-set(e):diffs.append({'site':e['site'],'column':k,'table_value':a[k],'recomputed_value':None,'failure':'column has no implemented protocol definition'})
    for code in set(actual_by)-{r['site_code'] for r in expected}:diffs.append({'site_code':code,'failure':'unexpected site row'})
    save('count-check.json',{'rows':len(obj),'site_rows':len(expected),'cells_checked':sum(len(d) for d in expected),'differences':diffs,'decision_application_differences':decision_diffs,'historical_decision_differences':historical_diffs,'decision_column_rule':'Where protocol_local_match is present, it defines the applied status. A demoted context identity is preserved in context_join_family; local_match and local_family_ids in the decision register retain the historical decision. Expanded candidate sets are reviewed separately.','recomputed_total':total,'recomputed_sites':expected,'bound_rule':'Stated post-catalogue rows only. For the lower bound, omit flagged possible duplicates, then add absent rows and candidate excess over the unassigned family union. Upper bound includes every main row not matched.','independence':'New implementation; review scripts read as specifications but never executed or imported.'})
    print('COUNTS differences',len(diffs),'decision differences',len(decision_diffs),'total',json.dumps(total))

def page_index():
    idx=collections.defaultdict(list)
    for run in ['run2N','run2G','run2D','run2P','run2E','run2F','run1a','run4']:
        for source in sorted((RAW/run/'text').glob('*')):
            if not source.is_dir():continue
            for p in sorted(source.glob('*.txt')):
                ns=re.findall(r'\d+',p.stem)
                if ns:idx[(source.name,int(ns[-1]))].append(p)
    return idx

def references(r,register):
    result=[]
    for part in re.split(r';\s*',r.get('other_publications','')):
        if not part.strip():continue
        matches=[s for s in register if re.match(r'^'+re.escape(s)+r'(?:\b|:|\s|$)',part)]
        if matches:
            source=max(matches,key=len);rest=part[len(source):]
            m=re.search(r'pdf(?:_page)?\s*[=:]?\s*([\d, -]+)',rest,re.I)
            result.append((source,m[1] if m else '',part))
        else:result.append(('', '',part))
    return result

def locators(fam,idx):
    obj=csvrows(inputpath('objects.csv')); reg={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')}
    for p in [BASE/'acquisition/source-register-1a.csv',BASE/'acquisition-web/source-candidates-1b.csv']:
        for r in csvrows(p):reg.setdefault(r['source_id'],r)
    failures=[];claimed=collections.defaultdict(list);checked_other=0;checked_pages=0;empty_pages=[]
    prefixes={m[1] for vs in fam.values() for d in vs for m in re.finditer(r'\b([A-Za-z]+)-\d+',str(d.get('source_cisi') or ''))}
    prefixes.update({'M','H','C','Dlv','Dlp','Sktd','Rgr','Krs','Tkwd','Rpr','B','K','L','Hls','Grb'})
    prefixes={x for x in prefixes if x.upper() not in {'CISI','VOL','VOLUME','PLATE','FIG','FIGURE','NO','PCF'}}
    cisi_pattern=re.compile(r'\b(?:'+'|'.join(re.escape(x) for x in sorted(prefixes,key=len,reverse=True))+r')[ -]\d+\b')
    for r in obj:
        rid=r['row_id'];source=r['primary_publication']
        if source not in reg:failures.append({'row_id':rid,'failure':'unknown primary source','source_id':source})
        pnums=page_numbers(r['pdf_page'])
        if not pnums:failures.append({'row_id':rid,'failure':'empty PDF-page locator','source_id':source})
        for x in pnums:
            checked_pages+=1
            if (source,int(x)) not in idx:failures.append({'row_id':rid,'failure':'page text unavailable','source_id':source,'pdf_page':x})
            elif not any(p.read_text(encoding='utf-8-sig',errors='replace').strip() for p in idx[source,int(x)]):empty_pages.append({'row_id':rid,'source_id':source,'pdf_page':x})
        for s,pg,raw in references(r,reg):
            checked_other+=1
            if not s:failures.append({'row_id':rid,'failure':'unknown secondary source','reference':safe(raw)})
        for fid in ids(r['local_family_ids']):
            if fid not in fam:failures.append({'row_id':rid,'failure':'unknown family','family':fid})
            elif not any(sitekey(x['site'])==sitekey(r['site']) for x in fam[fid]):failures.append({'row_id':rid,'failure':'family belongs to another site','family':fid})
        if r['local_match']=='matched':
            fs=ids(r['local_family_ids'])
            if len(fs)!=1:failures.append({'row_id':rid,'failure':'matched row does not name exactly one family'})
            for fid in fs:claimed[fid].append(r)
        if r['catalogue_status']=='in-baseline-catalogue' or r['local_match']=='in-baseline-catalogue':
            joined=' '.join(str(x) for k,x in r.items() if k not in ('row_id','reviewed_by','extracted_by'))
            if not cisi_pattern.search(joined):failures.append({'row_id':rid,'failure':'baseline row does not name a CISI identifier'})
    dup_edges={frozenset((r['row_id'],target)) for r in obj for target in ids(r['possible_duplicate_of'])}
    for fid,rs in claimed.items():
        for i,a in enumerate(rs):
            for b in rs[i+1:]:
                if frozenset((a['row_id'],b['row_id'])) not in dup_edges:failures.append({'failure':'family matched twice without a duplicate link','family':fid,'row_ids':[a['row_id'],b['row_id']]})
    save('locator-check.json',{'object_rows':len(obj),'primary_page_locators_checked':checked_pages,'secondary_references_checked':checked_other,'source_ids_in_registers':len(reg),'failures':failures,'failure_count':len(failures),'empty_primary_page_text':empty_pages,'cisi_prefix_source':'Prefixes observed in the approved corpus identity field, supplemented with baseline site prefixes. Site aliases come from the declared site seed.','policy':'Each primary PDF-page number is checked separately, expanding page ranges. Blank locators fail. Secondary source identifiers are checked independently; publication ranges do not identify individual object pages. Baseline rows must themselves name a CISI identifier.'})
    print('LOCATORS',len(failures),collections.Counter(x['failure'] for x in failures))

def info():
    for name in ['join-decisions.csv','local-unnamed.csv']:
        r=csvrows(BASE/name)
        print(name,'rows',len(r),'headers',list(r[0]) if r else [])
    r=csvrows(BASE/'join-decisions.csv');print('Decision categories',collections.Counter((x['local_match'],x['match_basis']) for x in r))
    for x in csvrows(BASE/'matching/source-register.csv'):
        if x['source_id'].startswith('kanmer-frame'):print(x['source_id'],x['local_path'])
    for x in r:
        if x['match_basis'] in {'context','plate-citation','registration-normalised','catalogue-containment'} and not x['row_id'].startswith('PCF-DHV'):
            print('REVIEW',x['row_id'],x['local_match'],x['local_family_ids'],x['match_basis'],safe(x['reason']))

def main():
    mode=sys.argv[2]
    if mode=='blind':blind()
    elif mode=='counts':counts()
    elif mode=='locators':locators(families(),page_index())
    elif mode=='info':info()
    elif mode=='corpus':
        f=families();p=ROOT/'data/normalized/lipi_observed_faces.jsonl';save('corpus-access.json',{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'families':len(f),'top_fields':sorted(TOP),'metadata_fields':sorted(META),'projection':'Excluded values are lexically skipped before decoding. Only approved fields are decoded; no corpus payload is emitted.'});print('CORPUS',len(f))

if __name__=='__main__':
    try:main()
    except OSError as e:
        try:save('WRITE-FAILURE.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
