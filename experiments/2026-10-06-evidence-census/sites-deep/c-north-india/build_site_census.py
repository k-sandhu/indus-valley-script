"""Offline census builder. Run from repository root; source payloads remain local."""
import csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote
sys.dont_write_bytecode = True
from evidence_notes import SITES, SOURCES, CISI, M77, count

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/c-north-india'
COVERAGE = ROOT / 'experiments/2026-10-06-research-program/local-site-coverage.json'
DATE = '2026-10-07'
CLASSES = ['seals','sealings','tablets','pottery_graffiti','metal','other']
METADATA = ['findspot','stratum_or_phase','absolute_dates','dimensions','material','photographs','drawings','registration_numbers']

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(u): return unquote(u).replace('http://','https://').rstrip('/')
def sid(u):
    return next((k for k,v in SOURCES.items() if norm(u)==norm(v['url'])), 'web-'+hashlib.sha256(norm(u).encode()).hexdigest()[:12])
def matches(q):
    found=[]
    for s in SITES:
        ns=[s['name'],*s['aliases']]
        if s['name']=='Ropar (Rupar)':ns+=['Ropar/Rupar']
        if s['name']=='Binjor (4MSR)':ns+=['Binjor']
        if any(n.casefold() in q.casefold() for n in ns):found.append(s['name'])
    return found

def logs():
    sources={};searches=[];opens=[];acqs=[]
    def add(u,title=None,witness=None):
        k=sid(u)
        r=sources.setdefault(k,dict(id=k,title=title,authors=None,year=None,venue=None,url=u,opened=False,seen_in_search=False,open_attempt_failed=False,witnesses=[]))
        if witness:r['witnesses'].append(witness)
        return r
    for f in sorted(RAW.glob('*.json')):
        if not f.name.startswith(('live-search-','adaptive-search-','live-open-','live-find-')):continue
        d=read(f);t=d if isinstance(d,str) else d.get('result','')
        if not isinstance(t,str):t=json.dumps(t,ensure_ascii=False)
        w=str(f.relative_to(ROOT)).replace('\\','/')
        refs=re.findall(r'(?:^|\n)([^\n]*?)\((https?://[^\n]+?)\)\n[^\n]*\[wordlim',t)
        for title,u in refs:
            r=add(u,title.strip() or None,w)
            if 'search-' in f.name:r['seen_in_search']=True
            for part in t.split('--------------------------------------------------------------------------------'):
                if u in part and 'Content type:' in part and 'Source:' in part:r['opened']=True
        if isinstance(d,dict):
            for i,q in enumerate(d.get('queries',[]),1):
                searches.append(dict(id=f'{f.stem}-q{i}',query=q,date=d.get('date',DATE),place_searched='live web search (web.run)',sites=matches(q),
                    result_source_ids=[sid(u) for _,u in refs],raw_response=w,query_group=f.stem,
                    result='Source leads returned in this query group; exact response retained locally. Grouped results cannot be assigned to each individual query.'))
        if f.name.startswith(('live-open-','live-find-')):opens.append(dict(id=f.stem,date=DATE,raw_response=w,source_ids=[sid(u) for _,u in refs]))
        for u in re.findall(r'Failed to fetch (https?://[^\s]+)',t):add(u.rstrip(':'),witness=w)['open_attempt_failed']=True
    old=read(OUT/'first-pass/searches.json')
    for i,q in enumerate(old.get('searches',[]),1):
        searches.append(dict(id=f'first-pass-q{i}',query=q['query'],date=old.get('date',DATE),place_searched=old.get('service'),sites=matches(q['query']),
            result=q.get('results'),raw_response='first-pass/searches.json',first_pass=True,result_source_ids=[],
            limitation='Original raw web response absent; excluded from follow-up search count.'))
    for f in sorted(set(RAW.glob('*.acquisition.json')) | set(RAW.glob('*.html-acquisition.json'))):
        a=read(f);a['manifest']=str(f.relative_to(ROOT)).replace('\\','/');acqs.append(a)
        if a.get('url'):
            r=add(a['url'],witness=a['manifest'])
            if a.get('status')=='failed':r['open_attempt_failed']=True
    for k,v in SOURCES.items():
        r=add(v['url']);r.update({x:y for x,y in v.items() if x not in ['raw_id','access_override']})
        if v.get('raw_id') and (RAW/(v['raw_id']+'.acquisition.json')).exists():
            a=read(RAW/(v['raw_id']+'.acquisition.json'));r['acquisition']=a;r['opened']=a.get('status')=='acquired'
            if r['opened']:r['local_pdf']=str((RAW/(v['raw_id']+'.pdf')).relative_to(ROOT)).replace('\\','/')
        if v.get('access_override'):r['opened']=False;r['access']=v['access_override']
        else:r['access']='opened; selected locations inspected' if r['opened'] else 'snippet/lead; full access unresolved'
        r['reuse']=v.get('reuse','Applicable open reuse terms not verified; payload and images remain local-only.')
    for old in read(OUT/'first-pass/sources.json').get('opened_or_seen_in_search',[]):
        if old.get('url') and sid(old['url']) not in sources:
            r=add(old['url'],old.get('title'),'first-pass/sources.json')
            r.update(authors=old.get('authors'),year=old.get('year'),venue=old.get('venue'),seen_in_search=True,
                     access='First-pass history only; original claimed opening not independently established.')
    for r in sources.values():
        r.setdefault('reuse','Rights unverified; payload and images local-only.')
        r.setdefault('access','opened via web' if r['opened'] else 'search snippet or failed access')
        r['bibliography_complete']=all(r.get(k) is not None for k in ['title','authors','year','venue'])
        r['witnesses']=sorted(set(r['witnesses']));r['date_accessed']=DATE;r['quotation']='No direct quotation in census prose.'
    return searches,sources,opens,acqs

def main():
    searches,sources,opens,acqs=logs()
    local={r['site'].casefold():r for r in read(COVERAGE)['sites']};rows=[]
    for s in SITES:
        name=s['name'];src=s['primary'];loc=s['inspection']
        qs=[q for q in searches if name in q['sites'] and not q.get('first_pass')];qids=[q['id'] for q in qs]
        def missing(explanation):
            return dict(value=None,status='not located in inspected sources and searches',explanation=explanation,
                        inspected=[dict(source_id=src,location=loc)],search_ids=qids)
        row=dict(canonical_name=name,alternative_spellings=s['aliases'],country='India',province_or_union_territory=s['state'],
            name_and_location_evidence=[dict(source_id=src,location=loc)],coordinates=s['coordinates'] or missing('Excavation-point coordinates unlocated; searches returned locality leads only.'),
            excavation_campaigns=s['campaigns'],primary_and_final_publications=s['publications'],final_excavation_monograph_identified=s['final_report'],
            primary_source_opened=dict(source_id=src,location=loc,opened=sources[src]['opened']),distinct_followup_searches=len(set(q['query'] for q in qs)),search_ids=qids,evidence_status='Exploratory')
        c=s['counts'].copy()
        row['cisi_coverage']=missing('No site section located in inspected CISI 1 contents or accessible later-volume records. CISI 2 covers Pakistan; CISI 3.1 is the Mohenjo-daro/Harappa supplement. Full later-volume inventories were not accessed.')
        if name in CISI:
            p,n,pg,cl,where=CISI[name]
            row['cisi_coverage']=dict(volume='CISI 1',year=1987,page_range=pg,prefix=p,entry_range=f'{p}1–{n}',catalogue_objects=n,contiguous_run_checked=True,
                evidence=[dict(source_id='cisi1',location=where)],limitation='Catalogue includes blank/indeterminate legends and geometric objects; later material may expand numbering.')
            c+=[count(k,v,'cisi1',where,1987,'CISI 1 catalogue entries','catalogue objects','Catalogue inclusion; not necessarily legible Indus text') for k,v in cl.items()]
            if name=='Kalibangan':row['cisi_coverage']['later_volume']=dict(volume='CISI 3.2',year=2019,page_range=None,evidence=[dict(source_id='cisi32',location='institutional publication record')],search_ids=qids,limitation='Pages and K123–476 continuity not audited.')
        row['mahadevan_1977_or_icit_count']=missing('ICIT site body/count inaccessible; M77 excerpt gives no site count here.')
        if name in M77:row['mahadevan_1977_or_icit_count']=dict(main_corpus_objects=M77[name],unit='inscribed objects selected for main corpus',count_date=1977,
            evidence=[dict(source_id='m77',location='printed p. 6 §4, PDF p. 9')],addendum_objects=3 if name=='Kalibangan' else 1 if name=='Banawali' else 0,
            addendum_evidence=[dict(source_id='m77',location='printed p. 24 §16, PDF p. 27')],search_ids=qids,
            limitation='Main corpus excludes blank/illegible material. Class appendix V pp. 816–829 absent; ICIT body inaccessible.')
        row['reported_object_counts']=c
        row['counts_by_class']={k:([x for x in c if x['object_class']==k] or missing(f'No numerical {k} count found for the requested inscribed-object scope. Unquantified/geometric/historic finds do not establish this count.')) for k in CLASSES}
        row['main_publication_metadata']={k:s['metadata'].get(k,dict(availability='no',evidence=[dict(source_id=src,location=loc)],
            explanation='Inscribed-object field unlocated in inspected source. General site or other-object metadata cannot be transferred to an unverified inscription.',unresolved=True,search_ids=qids)) for k in METADATA}
        lc=next((local[x.casefold()] for x in [name,*s['aliases']] if x.casefold() in local),None)
        if name=='Tarkhanewala Dera':lc=local.get('tarkhanewala-dera',lc)
        row['local_corpus']=dict(lc) if lc else dict(site_label_absent=True,faces=0,object_families=0,distinct_cisi_ids=0,cisi_prefixes={},max_cisi_number_by_prefix={},object_classes={},limitation='No site label in local starting register; zeros describe this export only.')
        if not lc:
            row['local_corpus'].update({k:0 for k in ['faces_with_period_or_time','faces_with_room_or_grid','faces_with_dimensions','faces_with_excavation_number']})
        row['local_corpus']['source_location']='experiments/2026-10-06-research-program/local-site-coverage.json#/sites/site='+(lc['site'] if lc else name)
        judgment=s['coverage'] or (f"Local {row['local_corpus']['distinct_cisi_ids']} distinct CISI IDs against {CISI[name][1]} CISI 1 objects; faces, families and later finds have different denominators." if name in CISI else 'Complete compatible published denominator unverified; local faces/families do not establish archaeological coverage.')
        row['local_coverage_judgment']=dict(value=judgment,evidence=[dict(source_id='cisi1' if name in CISI else src,location=CISI[name][4] if name in CISI else loc)],local_source=row['local_corpus']['source_location'])
        row['post_cisi_finds']=s['later'] or missing('No securely documented later inscribed discovery located. Publication after 1987 does not by itself date discovery after 1987.')
        row['post_1987_inscribed_find_documented']=s['later'] is not None
        row['post_cisi_finds']['comparison_baseline']='CISI 1 India, 1987. For sites absent from that catalogue this is a calendar baseline, not a demonstrated site-specific catalogue omission.'
        row['current_holding']=s['holding'] or missing('Present original-inscription custody unlocated; generic museum finds, administration and souvenirs do not identify original inscriptions.')
        used={src}
        def refs(o):
            if isinstance(o,dict):
                for k,v in o.items():
                    if k=='source_id':
                        if v.startswith('http'):o[k]=sid(v)
                        used.add(o[k])
                    else:refs(v)
            elif isinstance(o,list):
                for v in o:refs(v)
        refs(row)
        assert used<=set(sources),(name,used-set(sources))
        row['digital_availability_and_reuse']=dict(publications=[dict(source_id=k,url=sources[k]['url'],access=sources[k]['access'],reuse=sources[k]['reuse']) for k in sorted(used)],image_access='Illustrations identified in metadata fields; raw payloads, images and OCR remain local.',search_ids=qids)
        row['open_problems']=s['problems']+['Unknown counts, metadata and present custody link to executed searches and inspected source locations in this row.']
        rows.append(row)
    assert len(rows)==25 and all(r['distinct_followup_searches']>=3 for r in rows)
    assert all(r['primary_source_opened']['opened'] for r in rows),[(r['canonical_name'],r['primary_source_opened']) for r in rows if not r['primary_source_opened']['opened']]
    write('searches.json',dict(date=DATE,service='live web search via web.run',searches=searches,source_open_operations=opens,failed_downloads=[a for a in acqs if a.get('status')=='failed']))
    write('sources.json',dict(date=DATE,sources=sorted(sources.values(),key=lambda x:x['id']),note='All observed result headings retained; unused search leads have unresolved bibliography. Exact responses stay local.'))
    write('site-rows.json',dict(status='Exploratory',generated=DATE,rows=rows,metadata_semantics='yes: field located for cited sample; partial: incomplete, scaled-only or site-level; no: unavailable in inspected source, including explicit unstratified/missing cases. Unknown counts are null.'))
    with (OUT/'site-rows.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
    cat=[r for r in rows if r['canonical_name'] in CISI];cmp=[]
    for r in cat:
        n=r['canonical_name'];lc=r['local_corpus'];p,total,_,_,_=CISI[n];mx=lc['max_cisi_number_by_prefix'].get(p,0)
        cmp.append(dict(site=n,cisi1_catalogue_objects=total,local_faces=lc['faces'],local_families=lc['object_families'],local_distinct_cisi_ids=lc['distinct_cisi_ids'],local_max_cisi_number=mx,
                        within_cisi1_run_count_comparable=mx<=total,identifier_fraction=lc['distinct_cisi_ids']/total if mx<=total else None,
                        note='Distinct-ID inventory comparison; no authenticated-text recall estimate.'))
    stats=dict(status='Exploratory',sites=len(rows),supplied_sites=23,added_sites=['Tigrana','Rohira'],minimum_distinct_followup_searches=min(r['distinct_followup_searches'] for r in rows),
        followup_queries=sum(not q.get('first_pass',False) for q in searches),primary_or_substantial_source_opened_sites=len(rows),
        final_excavation_monograph_sites=[r['canonical_name'] for r in rows if r['final_excavation_monograph_identified']],final_excavation_monograph_count=sum(r['final_excavation_monograph_identified'] for r in rows),
        final_monograph_access=dict(full_relevant_volumes=['Mitathal','Hulas','Bhagwanpura'],partial_volume=['Kalibangan Part II'],bibliography_only=['Farmana','Tarkhanewala Dera']),
        published_short_excavation_chapters_additional=['Manda','Siswal'],post_1987_inscribed_find_sites=[r['canonical_name'] for r in rows if r['post_1987_inscribed_find_documented']],
        post_1987_inscribed_find_count=sum(r['post_1987_inscribed_find_documented'] for r in rows),post_cisi1_previously_catalogued_sites=[r['canonical_name'] for r in rows if r['post_1987_inscribed_find_documented'] and r['canonical_name'] in CISI],
        cisi1_sites=len(CISI),cisi1_catalogue_objects=sum(v[1] for v in CISI.values()),cisi1_class_counts={k:sum(v[3].get(k,0) for v in CISI.values()) for k in CLASSES},
        local_totals={k:sum(r['local_corpus'][k] for r in rows) for k in ['faces','object_families','distinct_cisi_ids']},local_totals_on_cisi1_sites={k:sum(r['local_corpus'][k] for r in cat) for k in ['faces','object_families','distinct_cisi_ids']},
        mahadevan1977_main_objects_on_seven_sites=sum(M77.values()),mahadevan1977_addendum_objects_on_those_sites=4,
        missing_metadata_fields=dict(Counter(k for r in rows for k,v in r['main_publication_metadata'].items() if v['availability']=='no').most_common()),
        unresolved_counts_by_class={k:sum(isinstance(r['counts_by_class'][k],dict) for r in rows) for k in CLASSES},source_records=len(sources),failed_download_attempts=sum(a.get('status')=='failed' for a in acqs),comparisons=cmp)
    write('aggregates.json',stats)
    write('checks.json',dict(status='Verified computation',sites=len(rows),all_sites_three_searches=True,all_sites_opened_source=True,count_class_fields_per_site=6,metadata_fields_per_site=8,
        cisi1_classes_sum=sum(stats['cisi1_class_counts'].values()),cisi1_objects=stats['cisi1_catalogue_objects'],first_pass_manifest_unchanged=all(hashlib.sha256((OUT/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in read(OUT/'first-pass-manifest.json'))))
    print(json.dumps(stats,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
