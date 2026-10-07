"""Rebuild the census from curated observations and preserved live-search witnesses.

Run from the repository root. Does not search, mutate archives, or download.
All source payloads stay in the paired ignored raw directory.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
from collections import Counter
from urllib.parse import urlsplit
from evidence_catalog import ROWS, SOURCES, COORDS, COORD_OVERRIDES, CATALOGUE1, MAHA_COUNTS, ICIT_SIGNS, ref

OWN=Path(__file__).resolve().parent
ROOT=OWN.parents[3]
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra'
LOCAL_PATH=ROOT/'experiments/2026-10-06-research-program/local-site-coverage.json'
LOCAL=json.loads(LOCAL_PATH.read_text(encoding='utf-8'))['sites']
DATE='2026-10-07'
CLASSES=['seals','sealings','tablets','pottery_graffiti','metal_objects','other_objects']
ALIASES={'Desalpar':'Desalpur','Rojdi':'Rodji'}

def write(name,value):
    (OWN/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def clean_metadata(text):
    # Raw source witnesses retain their original bytes. Only discovery metadata
    # is normalised; never reconstruct an unreadable source title by guessing.
    for old,new in [('â€“','–'),('â€”','—'),('â€œ','“'),('â€\x9d','”'),('Ã¡','á'),('Ã¤','ä'),('Ã¶','ö'),('Ã¼','ü')]:
        text=text.replace(old,new)
    if '\ufffd' in text:
        return 'Title contains unreadable characters in retrieved metadata; see raw witness.'
    return text

def headers(result):
    found=[]
    for line in str(result).splitlines():
        if line.startswith(('L0:','L1:','\ue200')) or re.match(r'^L\d+[@:]',line):continue
        m=re.match(r'^(.*?) \((https?://.+)\)$',line.strip())
        if m: found.append((clean_metadata(m[1]) or 'Source title not supplied',m[2]))
    return list(dict.fromkeys(found))

logs=[]; searches=[]; discovery={}
for path in sorted(list(RAW.glob('B[0-9][0-9].json'))+list(RAW.glob('O[0-9][0-9].json'))):
    log=json.loads(path.read_text(encoding='utf-8')); logs.append(log)
    result=log.get('result',''); seen=headers(result)
    queries=log.get('queries',log.get('request',{}).get('search_query',[]))
    for n,q in enumerate(queries,1):
        searches.append(dict(id=log['id']+f'-Q{n}',sites=log['sites'],scope='regional_shared' if log['id']=='B40' else 'site_specific',date=log.get('retrieved_at',DATE),place='Live web search via web.run',query=q['q'],domains=q.get('domains'),result_urls=[u for t,u in seen],result_summary=f'{len(seen)} source headers returned in the saved multi-query response. Individual result-to-query attribution is not supplied by the tool; inspect the raw bundle for the actual snippets and failures.',raw_witness=str(path.relative_to(ROOT)).replace('\\','/')))
    for title,url in seen:
        d=discovery.setdefault(url,dict(id='DISC-'+hashlib.sha256(url.encode()).hexdigest()[:12],title=title,authors=None,year=None,venue=urlsplit(url).netloc,url=url,access_state='snippet_only',seen_in=[],opened_in=[],failed_in=[],metadata_note='Uncatalogued discovery result; author/year not extracted. Not used to support site claims.',rights='Unresolved; raw response remains local.'))
        d['seen_in'].append(log['id'])
        if log['id'].startswith('O'):
            # Identify error blocks independently, including bundles containing
            # both successful and failed opens.
            block=str(result).split(url,1)[1].split('--------------------------------------------------------------------------------',1)[0]
            if 'Failed to fetch' in block or 'not accessible via this tool' in block or 'Total lines: 1\nL0:' in block:
                d['failed_in'].append(log['id'])
            else:
                d['opened_in'].append(log['id']);d['access_state']='opened'

# Preserve failed request URLs which may not have a normal source header.
failures=[]
for log in logs:
    result=str(log.get('result',''))
    if any(x in result for x in ['Failed to fetch','not accessible via this tool','Internal Error','Too Many Requests','Forbidden']):
        failures.append(dict(log_id=log['id'],sites=log['sites'],raw_witness=str((RAW/(log['id']+'.json')).relative_to(ROOT)).replace('\\','/'),request=log.get('request',{}),note='One or more accesses failed; exact error and successful accesses are retained side by side in the raw bundle.'))

acquisitions=[]
for p in sorted(RAW.glob('*.acquisition.json')):
    a=json.loads(p.read_text(encoding='utf-8'))
    # Acquisition success is a transport result, not proof of a useful document.
    if a.get('id') in ['LOTHAL1985','KANMER2012CH8','BETDWARKA1998']:
        a['content_audit']='HTTP200 returned a challenge/HTML page, not full primary-source content; successful web-indexed reads have separate O logs.'
    elif a.get('status')=='acquired':
        a['content_audit']='PDF/content extraction retained; inspection locations specified by curated sources where used.'
    acquisitions.append(a)

sources=[dict(s) for s in SOURCES]
curated_urls={s['url'] for s in sources}
for s in sources:
    d=discovery.get(s['url'],{})
    s['seen_in']=d.get('seen_in',[]);s['opened_in']=d.get('opened_in',[])
    s['retrieval_date']=DATE
    s['quotation']=None
    s['raw_acquisitions']=[a['id'] for a in acquisitions if a.get('url')==s['url'] or a.get('id')==s['id']]
sources.extend(d for u,d in sorted(discovery.items()) if u not in curated_urls)
source_map={s['id']:s for s in sources}

def missing(row,field,why):
    return dict(status='unresolved',value=None,field=field,reason=why,search_ids=row['search_ids'],inspected_sources=[row['primary_read']],search_outcome='Recorded queries returned the sources in searches.json/result_urls and the saved raw response. The inspected source did not expose a usable value for this field; absence from those passages does not establish archaeological absence.')

rows=[]
for original in ROWS:
    r=json.loads(json.dumps(original)); name=r['canonical_name']
    r['status']='Exploratory';r['audit_date']=DATE
    r['alternative_spellings']=[x.strip() for item in r['alternative_spellings'] for x in item.split(';') if x.strip()!=name]
    r['search_ids']=[q['id'] for q in searches if name in q['sites']]
    r['source_access_logs']=[l['id'] for l in logs if l['id'].startswith('O') and name in l['sites']]
    r['source_read_basis']='A specific primary or substantial secondary passage was read. Direct PDF reads are represented by acquisition/.pages.json witnesses; web reads by O logs. Landing pages alone are excluded.'
    r['country']='Pakistan' if name=='Nuhato' else 'India'
    r['province']='Sindh' if name=='Nuhato' else 'Maharashtra' if name=='Daimabad' else 'Gujarat'
    r['administrative_evidence']=ref('NUHATO2018','p.2') if name=='Nuhato' else ref('GAZETTEER2018','Table1,pp.8–9') if name in COORDS else r['primary_read']
    r['batch_scope']='Explicitly requested Sindh cross-reference; excluded from Gujarat/Maharashtra-only totals.' if name=='Nuhato' else 'Regional site'
    if name in COORDS:
        lat,lon,n=COORDS[name]
        r['coordinates']=dict(latitude=lat,longitude=lon,datum='WGS84 as labelled by gazetteer',precision_note='Printed coordinate precision does not establish survey accuracy.',evidence=[ref('GAZETTEER2018',f'Table1,row{n},p.'+('9' if n==184 else '8'))])
    if name in COORD_OVERRIDES:r['coordinates']=COORD_OVERRIDES[name]
    if name=='Khirsara':r['coordinates']['conflicts']='IAR2009–10 p.16 gives23°50′N,69°05′E; this is incompatible with the gazetteer point. Original report transcription retained without correction.'
    if name=='Nagwada':r['coordinates']['conflicts']='IAR1987–88 p.19 gives23°20′N,71°41′E; gazetteer gives23.3042N,71.7125E; original points unaligned.'
    if name=='Rangpur':
        r['coordinates']['conflicts']='RANGPUR1963 p.7 prints latitude22°26′E and longitude71°55′N, with reversed hemisphere labels; even after exchanging the labels the latitude differs from the gazetteer point. Gazetteer point retained; no silent correction of the report.'
        r['coordinates']['evidence'].append(ref('RANGPUR1963','p.7; RANGPUR1963-p18-coordinate-check.png'))
    r['local_corpus']=next((s for s in LOCAL if s['site']==ALIASES.get(name,name)),None)
    if r['local_corpus'] is None:
        r['local_corpus']=dict(site=None,faces=0,object_families=0,distinct_cisi_ids=0,cisi_prefixes={},max_cisi_number_by_prefix={},object_classes={},faces_with_period_or_time=0,faces_with_room_or_grid=0,faces_with_dimensions=0,faces_with_excavation_number=0,label_present=False)
    else:r['local_corpus']['label_present']=True
    r['local_corpus']['evidence']=dict(file=str(LOCAL_PATH.relative_to(ROOT)).replace('\\','/'),field='sites[site='+str(r['local_corpus']['site'])+']',sha256=hashlib.sha256(LOCAL_PATH.read_bytes()).hexdigest())
    if not r['local_coverage_judgment']:
        r['local_coverage_judgment']='No local export row for this site; a published inscribed-object denominator was not verified, so corpus completeness cannot be estimated.' if r['local_corpus']['faces']==0 else 'Local faces are present but object identities and source inventory are unaligned; no completeness fraction computed.'
    r['cisi_coverage']=[]
    if name in CATALOGUE1:
        prefix,number,pages,basic=CATALOGUE1[name]
        r['cisi_coverage'].append(dict(volume='CISI1',year=1987,page_range=pages,basic_data_pages=basic,identifier_prefix=prefix,identifier_range=f'{prefix}1–{number}',catalogue_object_slots=number,unit='catalogue object identifiers',contiguity_check='The printed site catalogue and contents delimit a contiguous1–N range. Lower-case impression images and bis/ter photographic views are not additional objects. This is not a claim that all excavated finds were catalogued.',evidence=[ref('CISI1','contents pp.III–IV; site pp.'+pages+'; basic data pp.'+basic)]))
    else:r['cisi_coverage'].append(dict(volume='CISI1',year=1987,status='no_site_section_in_inspected_contents',page_range=None,evidence=[ref('CISI1','contents pp.III–IV')],search_ids=r['search_ids']))
    r['cisi_coverage'].append(dict(volume='CISI2',year=1991,status='reported_by_excavation_report_not_directly_verified' if name=='Nuhato' else 'no_applicable_site_section_verified',page_range='390 (citation only; range unresolved)' if name=='Nuhato' else None,evidence=[ref('NUHATO2018','p.41 cites CISI2 p.390')] if name=='Nuhato' else [ref('CISI2','bibliographic title: Collections in Pakistan')],search_ids=r['search_ids']))
    r['cisi_coverage'].append(dict(volume='CISI3.1',year=2010,status='volume addresses Mohenjo-daro and Harappa; no batch site section verified',page_range=None,evidence=[ref('FULS2022','preview bibliography, CISI3.1 title')],search_ids=r['search_ids']))
    r['cisi_coverage'].append(dict(volume='CISI3.2',year=2019,status='site inclusion bibliographically verified; pages/counts unavailable' if name=='Rojdi' else 'no_site_section_for_this_site_in_published_volume_title',page_range=None,evidence=[ref('CISI32','official volume title and site list')],search_ids=r['search_ids']))
    r['mahadevan1977']=dict(value=MAHA_COUNTS[name],unit='selected legible inscribed objects; each object treated as one text',count_date=1977,evidence=[ref('MAHADEVAN1977','p.6,Table1; method pp.5–6')]) if name in MAHA_COUNTS else missing(r,'mahadevan1977','No separate site total in the inspected Table1,p.6; a later site absent from the table is not assigned zero historical finds.')
    r['icit_site_count']=dict(status='published_aggregate',value=ICIT_SIGNS[name],unit='legible sign occurrences, not objects/faces/texts',count_date=2023,count_basis='Author’s ICIT-based corpus regional list; no direct database query.',evidence=[ref('FULS2023SIGNS','§5.3,p.501,regional site list before p.502')],object_count=missing(r,'icit_inscribed_object_count','Published regional list counts signs; no ICIT site-level object inventory acquired.')) if name in ICIT_SIGNS else missing(r,'icit_site_count','No site aggregate for this label in the inspected Fuls2023 regional list; no queryable ICIT inventory accessed. B40 records the actual ICIT search.')
    r['counts_by_class']={c:[v for v in r['reported_counts'] if v['object_class']==c] or [missing(r,c,'No usable numerical inventory for '+c+' in the inspected site passages. See primary_publications for unavailable final-report pages and open_problems for site-specific gaps.')] for c in CLASSES}
    for c in r['reported_counts']:
        if c['count_date'] is None:c['count_date']=source_map[c['evidence'][0]['source_id']]['year']
    r['count_comparisons']=[dict(object_class=c,observations=[dict(value=v['value'],unit=v['unit'],basis=v['count_basis'],date=v['count_date'],evidence=v['evidence']) for v in records],note='Keep count bases and source dates distinct. Different totals may reflect selection, overlapping mentions or genuine disagreement; site open_problems gives the specific issue.') for c,records in r['counts_by_class'].items() if len(records)>1]
    r['metadata_available']=r.pop('metadata_observation')
    for k,v in r['metadata_available'].items():
        if v['availability']=='no':v['unresolved_searches']=missing(r,k,'Not demonstrated for an identified inscription in the cited passage; other publication pages may contain it.')
    if r['holdings']['status']=='unresolved':r['holdings']['unresolved_searches']=missing(r,'current_holdings',r['holdings']['observation'])
    if r['post_cisi_finds']['status']=='unresolved':r['post_cisi_finds']['search_record']=missing(r,'post_cisi_finds',r['post_cisi_finds']['note'])
    if r['final_report']['status']=='unresolved':r['final_report']['search_record']=missing(r,'final_report',r['final_report']['note'])
    r['digital_availability']=[dict(source_id=s['id'],url=s['url'],access_state=s['access_state'],publication_availability='Relevant text inspected in indicated witness.' if s['access_state']=='opened' else 'Bibliography/preview/snippet only; do not treat as full report access.',image_availability='See metadata_available.photographs and drawings; accessible image is not permission to redistribute.',reuse_terms=s['rights'],witness=s['witness']) for p in r['primary_publications']+[dict(source_id=r['primary_read']['source_id'])] for s in [source_map[p['source_id']]]]
    # De-duplicate repeated main-publication references.
    r['digital_availability']=list({v['source_id']:v for v in r['digital_availability']}.values())
    r['missing_fields']=[f'counts_by_class.{c}' for c,v in r['counts_by_class'].items() if v[0].get('status')=='unresolved']
    r['missing_fields'] += ['metadata_available.'+k for k,v in r['metadata_available'].items() if v['availability']=='no']
    r['missing_fields'] += ['icit_inscribed_object_count']
    if name not in ICIT_SIGNS:r['missing_fields'].append('icit_site_count')
    for key in ['holdings','post_cisi_finds','final_report']:
        if r[key]['status']=='unresolved':r['missing_fields'].append(key)
    if name=='Rojdi':r['missing_fields'].append('CISI3.2.page_range_and_counts')
    if name=='Nuhato':r['missing_fields'].append('CISI2.direct_page_verification')
    if any('unresolved' in v.get('director','').lower() or 'not stated' in v.get('director','').lower() for v in r['excavation_campaigns']):r['missing_fields'].append('excavation_campaigns.director')
    if any('not specified' in v.get('years','').lower() or 'unresolved' in v.get('years','').lower() for v in r['excavation_campaigns']):r['missing_fields'].append('excavation_campaigns.complete_years')
    r['unresolved_fields']=[missing(r,k,'Consult the cited inspected passages and site open_problems; recorded searches did not resolve this field.') for k in r['missing_fields']]
    r['addition_basis']='Found while reading IAR1977–78 p.21 for Pabumath; explicit inscribed pottery at Kanewal, then B37 three live searches and official final-report catalogue opened.' if name=='Kanewal' else 'Regional local export label; CISI1 Pbm1 independently verifies the added inscribed site.' if name=='Pabumath' else 'Regional local export lead; unnumbered pottery face remains unverified as inscription.' if name=='Juna Khatiya' else 'Explicit user list.'
    rows.append(r)

metrics=dict(status='Exploratory',audit_date=DATE,sites=len(rows),regional_sites=sum(r['canonical_name']!='Nuhato' for r in rows),requested_cross_references=['Nuhato'],explicit_list_sites=22,added_sites=['Pabumath','Juna Khatiya','Kanewal'],local_labels_present=sum(r['local_corpus']['label_present'] for r in rows),local_faces=sum(r['local_corpus']['faces'] for r in rows),local_object_families=sum(r['local_corpus']['object_families'] for r in rows),distinct_local_cisi_ids_sum=sum(r['local_corpus']['distinct_cisi_ids'] for r in rows),live_search_queries=len(searches),live_search_bundles=sum(l['id'].startswith('B') for l in logs),minimum_distinct_searches_per_site=min(len(set(q['query'] for q in searches if r['canonical_name'] in q['sites'])) for r in rows),sites_with_substantial_source_passage_read=len(rows),sites_with_coordinates_or_published_extent=sum('coordinates' in r for r in rows),sites_with_coordinate_point=sum(r['coordinates'].get('latitude') is not None for r in rows),sites_with_completed_report=sum(r['final_report']['status']=='bibliographically_verified' for r in rows),completed_report_relevant_pages_read=sum(r['final_report'].get('relevant_object_pages_read',False) for r in rows),completed_report_sites=[r['canonical_name'] for r in rows if r['final_report']['status']=='bibliographically_verified'],post_site_catalogue_find_sites=[r['canonical_name'] for r in rows if r['post_cisi_finds'].get('comparison_kind')=='after_site_catalogue'],post_reported_site_catalogue_find_sites=[r['canonical_name'] for r in rows if r['post_cisi_finds'].get('comparison_kind')=='after_reported_site_catalogue'],new_sites_with_script_material_after_1987=[r['canonical_name'] for r in rows if r['post_cisi_finds'].get('comparison_kind')=='new_site_after_1987' and r['post_cisi_finds']['status']=='documented'],uncertain_later_find_sites=[r['canonical_name'] for r in rows if r['post_cisi_finds']['status']=='uncertain'],cisi1=dict(sites=len(CATALOGUE1),catalogue_object_slots=sum(v[1] for v in CATALOGUE1.values()),basis='Sum of the ten directly inspected contiguous CISI1 site ranges; includes selected geometric/pictorial objects and broad graffiti. Not all317 are authenticated texts.',local_faces_at_these_sites=sum(r['local_corpus']['faces'] for r in rows if r['canonical_name'] in CATALOGUE1),local_families_at_these_sites=sum(r['local_corpus']['object_families'] for r in rows if r['canonical_name'] in CATALOGUE1),local_distinct_cisi_ids_at_these_sites=sum(r['local_corpus']['distinct_cisi_ids'] for r in rows if r['canonical_name'] in CATALOGUE1)),mahadevan1977=dict(sites=len(MAHA_COUNTS),selected_inscribed_objects=sum(MAHA_COUNTS.values()),basis='Table1,p.6: Lothal165,Desalpar2,Dholavira1,Rojdi2,Surkotada5. Do not add to CISI1 totals because records overlap.'),most_often_missing=Counter(k for r in rows for k in r['missing_fields']).most_common(),acquisition_attempts=len(acquisitions),failed_acquisitions=sum(a.get('status')=='failed' for a in acquisitions),transport_success_challenge_payloads=[a['id'] for a in acquisitions if 'challenge' in a.get('content_audit','')],source_records=len(sources),opened_curated_sources=sum(s['access_state']=='opened' for s in SOURCES))

write('site-rows.json',rows);write('sources.json',sources);write('searches.json',searches);write('aggregate-results.json',metrics)
write('source-access.json',dict(web_access_failures=failures,acquisitions=acquisitions,note='Transport and content audit distinguished. Some web access failures have successful requests-based local PDF acquisitions.'))
with (OWN/'site-rows.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
    for r in rows:writer.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(list,dict)) else v for k,v in r.items()})

# Reviewer constraints are computed as an audit, not a test of archaeology.
audit=dict(status='Verified computation',sites=len(rows),unique_site_names=len(set(r['canonical_name'] for r in rows)),minimum_queries_per_site=metrics['minimum_distinct_searches_per_site'],class_fields_per_site=len(CLASSES),metadata_fields_per_site=8,all_claim_source_ids_resolve=True,archive_hashes_unchanged=True)
def refs_in(v):
    if isinstance(v,dict):
        if 'source_id' in v:yield v['source_id']
        for x in v.values():yield from refs_in(x)
    elif isinstance(v,list):
        for x in v:yield from refs_in(x)
audit['unknown_source_ids']=sorted(set(refs_in(rows))-set(source_map));audit['all_claim_source_ids_resolve']=not audit['unknown_source_ids']
metrics['minimum_distinct_searches_per_site']=min(len(set(q['query'] for q in searches if r['canonical_name'] in q['sites'] and q['scope']=='site_specific')) for r in rows)
metrics['site_specific_query_records']=sum(q['scope']=='site_specific' for q in searches)
metrics['regional_shared_query_records']=sum(q['scope']=='regional_shared' for q in searches)
audit['minimum_queries_per_site']=metrics['minimum_distinct_searches_per_site']
metrics['published_icit_sign_aggregate_sites']=len(ICIT_SIGNS)
metrics['published_icit_sign_occurrences']=sum(ICIT_SIGNS.values())
metrics['icit_object_count_totals_available']=0
write('aggregate-results.json',metrics)
manifest=json.loads((OWN/'first-pass/preservation-manifest.json').read_text(encoding='utf-8'))
audit['archive_mismatches']=[item['path'] for item in manifest['files'] if hashlib.sha256((OWN/'first-pass'/item['path']).read_bytes()).hexdigest()!=item['sha256']]
audit['archive_hashes_unchanged']=not audit['archive_mismatches']
with (OWN/'site-rows.csv').open(encoding='utf-8',newline='') as f:
    csv_rows=list(csv.DictReader(f))
expected_csv=[{k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(list,dict)) else '' if v is None else str(v) for k,v in r.items()} for r in rows]
audit['csv_matches_json']=csv_rows==expected_csv
audit['utf8_decode_failures']=[]
audit['current_text_files_with_replacement_characters']=[]
for p in sorted(OWN.rglob('*')):
    if not p.is_file() or 'first-pass' in p.relative_to(OWN).parts or p.suffix not in {'.md','.py','.json','.csv','.txt'}:continue
    try: content=p.read_text(encoding='utf-8')
    except UnicodeError:
        audit['utf8_decode_failures'].append(str(p.relative_to(OWN)));continue
    if '\ufffd' in content:audit['current_text_files_with_replacement_characters'].append(str(p.relative_to(OWN)))
write('build-audit.json',audit)
print(json.dumps(metrics,ensure_ascii=False,indent=2))
