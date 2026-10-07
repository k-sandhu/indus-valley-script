"""Assemble revised census offline; writes only inside this package."""
from __future__ import annotations
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'knowledge/INDEX.md').exists())
DATE='2026-10-07'
CLASSES=['seals','sealings','tablets','inscribed_pottery_and_graffiti','metal','other_inscribed_objects']
META=['findspot','stratum_or_phase','absolute_dates','dimensions','material','photographs','drawings','registration_numbers']
def read(name): return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
def write(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(d,key): return d[key] if isinstance(d,dict) else d
def repair(v):
 if isinstance(v,list): return [repair(x) for x in v]
 if isinstance(v,dict): return {k:repair(x) for k,x in v.items()}
 if not isinstance(v,str): return v
 if any(x in v for x in ['Ã','Â°','â€']):
  try: return v.encode('cp1252').decode('utf-8')
  except UnicodeError: pass
  for b,g in [('â€“','–'),('â€”','—'),('â€™','’'),('â€œ','“'),('Ã§','ç'),('Ã©','é'),('Â°','°')]: v=v.replace(b,g)
 return v
def refs(v):
 result=[]
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='source_id' and x: result.append(('source',x))
   elif k=='source_ids' and isinstance(x,list): result.extend(('source',i) for i in x if i)
   elif k in ('search_ids','query_ids','failed_query_ids') and isinstance(x,list): result.extend(('search',i) for i in x if i)
   else: result.extend(refs(x))
 elif isinstance(v,list):
  for x in v: result.extend(refs(x))
 return result
def numeric(v): return isinstance(v,dict) and isinstance(v.get('count',v.get('value')),(int,float))
def unresolved(v):
 if v is None: return True
 if isinstance(v,list): return not any(not unresolved(x) for x in v)
 if isinstance(v,dict):
  if v.get('status') in ('unresolved','not_located'): return True
  if 'value' in v: return v['value'] is None
  if 'volume_or_range' in v: return v['volume_or_range'] is None
  if 'verified_ranges' in v: return not v['verified_ranges']
  return not v
 return False

sites=[];sources=rows(read('first-pass/sources.json'),'sources');searches=rows(read('first-pass/searches.json'),'searches')
rowfiles={'major':'revision-major-sites.json','west-upper':'revision-west-upper.json','afghan-minor':'revision-afghan-minor.json','discovery':'revision-discovery-sites.json','additional-pakistan':'revision-additional-pakistan.json'}
for stem,rowfile in rowfiles.items():
 sites.extend(rows(read(rowfile),'sites'))
 sources.extend(rows(read(f'revision-{stem}-sources.json'),'sources'))
 searches.extend(rows(read(f'revision-{stem}-searches.json'),'searches'))
sources.extend(read('revision-common-sources.json'));searches.extend(read('revision-common-searches.json'))
sites=repair(sites);sources=repair(sources);searches=repair(searches)
for s in sources:
 s.setdefault('access_date',DATE)
 s['record_role']='historical lead' if not str(s['id']).startswith('R') else 'revision source or search lead'
src={s['id']:s for s in sources};qry={s['id']:s for s in searches}
if len(src)!=len(sources) or len(qry)!=len(searches): raise ValueError('Duplicate ledger IDs')
common=read('revision-common-counts.json');comparisons=[]
coverage_path=ROOT/'experiments/2026-10-06-research-program/local-site-coverage.json'
coverage= json.loads(coverage_path.read_text(encoding='utf-8-sig'))['sites']
def norm(v): return re.sub('[^a-z0-9]','',v.casefold())
coverage_by_name={norm(v['site']):v for v in coverage}
aliases={'Balakot':'Bala-kot','Rehman Dheri':'Rahman-deri','Nindowari':'Nindowari-damb'}
sources.append(dict(id='RCO-LOCAL',title='Local site coverage aggregate',authors='Repository research-program coordinator',year=2026,venue='Private repository aggregate generated2026-10-07',url='experiments/2026-10-06-research-program/local-site-coverage.json',opened=True,access_scope='Complete JSON reused; source row aggregates copied exactly.',locators=['sites array'],reuse='Local derivative; upstream rights unchanged.'))
src['RCO-LOCAL']=sources[-1]
write('local-coverage-witness.json',dict(source_path=str(coverage_path.relative_to(ROOT)),sha256=hashlib.sha256(coverage_path.read_bytes()).hexdigest(),note='Local aggregate reused; no independent object inventory acquired.'))
for s in sites:
 name=s['canonical_name'];qids=s.get('search_ids',[])
 if name in ('Sibri','Ornach area','Murda Sang'):
  s['discovery']=dict(method='Country check of Pakistan labels assigned to Iranian Plateau in the local aggregate, followed by live searches and opened source inspection.',source_ids=s.get('source_ids',[]),search_ids=qids,classification='Site-specific inscription or mark classification and archaeological locality identity remain as documented in this row.')
 prior_local=s.get('local_corpus') or {}
 local=coverage_by_name.get(norm(aliases.get(name,name)))
 s['local_corpus']=local
 if local:
  if any(prior_local.get(k)!=local[k] for k in ['faces','object_families','distinct_cisi_ids']):
   s['local_coverage_judgment']='The canonical name was joined to the coordinator’s original label. Catalogue counts and local source rows require matching object definitions before a completeness ratio can be computed.'
  s['local_coverage_judgment']+=f" Exact coordinator aggregate: {local['faces']} faces, {local['object_families']} object families and {local['distinct_cisi_ids']} distinct CISI identifiers; local label {local['site']}."
 else:
  s['local_coverage_judgment']='No matching label in the coordinator aggregate. Published catalogue observations and unresolved counts remain in this row.'
 s.setdefault('site_entity_id',re.sub('[^a-z0-9]+','-',name.lower()).strip('-'))
 if name in ('Gharo Bhiro','Nuhato'):
  s['site_entity_id']='gharo-bhiro-nuhato'
  s['identity_note']='CISI2 heading Gharo Bhiro (Nuhato), Grb1p392; two requested labels retained as one catalogue locality.'
 s['revision_query_ids']=[i for i in qids if str(i).startswith('R')]
 s.setdefault('source_ids',[])
 s['source_ids'].append('RCO-LOCAL')
 counts=s.get('reported_object_counts',[])
 if isinstance(counts,dict):
  s['count_scope']=counts.get('count_scope')
  s['reported_object_counts']=[dict(c,object_class=cls) for cls,items in counts.get('by_class',{}).items() for c in items]
 if name in common['site_totals']:
  c=dict(count=common['site_totals'][name],unit='included inscribed physical objects',date_of_count=1977,source_id='RCO-M77',location='p6; inclusion rule pp5–6',count_basis=common['basis'])
  s['mahadevan_1977_count']=c;s['source_ids'].append('RCO-M77')
  s.setdefault('reported_object_counts',[]).append(dict(c,object_class='all classes'))
  for cls,n in common['by_class'].get(name,{}).items():
   if cls=='components': continue
   s['reported_object_counts'].append(dict(count=n,object_class=cls,unit='included inscribed physical objects',date_of_count=1977,source_id='RCO-M77',location='p7,class-by-site table',count_basis=common['basis'],blank_cells=common['blank_cells']))
  local=s.get('local_corpus') or {}
  comparisons.append(dict(site=name,published_count=c['count'],published_unit=c['unit'],publication_year=1977,source_id='RCO-M77',source_location='p6',local_faces=local.get('faces',0),local_object_families=local.get('object_families',0),local_distinct_cisi_ids=local.get('distinct_cisi_ids',0),interpretation='Historical included-object total versus current local labels. Dates and selection differ; no completeness percentage inferred.'))
  s['local_coverage_judgment']+=f" Mahadevan 1977 p.6 includes {c['count']} inscribed objects. This historical inventory is a separate comparison from later catalogue entries and local face rows."
 s['reported_counts_by_class']={cls:[] for cls in CLASSES}
 for c in s.get('reported_object_counts',[]):
  c.setdefault('unit',c.get('unit_or_basis'))
  if not c['unit']: c['unit']=c.get('count_basis',c.get('basis','Unit unresolved; see source observation.'))
  c.setdefault('date_of_count',c.get('count_date',c.get('date')))
  c.setdefault('location',c.get('source_page',c.get('source_location',c.get('locator'))))
  if c['date_of_count'] is None:
   c['date_gap']=dict(reason='Original count/publication date not established on inspected source page.',inspection_date=DATE,failed_query_ids=qids)
  c.setdefault('count_basis',c.get('basis',c.get('claim',c.get('detail'))))
  cls=c.get('object_class',c.get('class',''))
  cls={'other':'other_inscribed_objects','pottery':'inscribed_pottery_and_graffiti','graffiti':'inscribed_pottery_and_graffiti'}.get(cls,cls)
  if cls in CLASSES: s['reported_counts_by_class'][cls].append(c)
 for cls in CLASSES:
  if not s['reported_counts_by_class'][cls]:
   gap=s.get('class_count_gaps',{}).get(cls,s.get('class_count_gaps',{}).get('other',{}))
   s['reported_counts_by_class'][cls]=[dict(count=None,status='unresolved',reason=gap.get('reason','No class-specific numerical inventory recovered; catalogue illustrations are not an excavation census.'),failed_query_ids=gap.get('failed_query_ids',gap.get('search_ids',qids)))]
 metadata=s.get('publication_metadata',{})
 if 'fields' in metadata: metadata=metadata['fields']
 s['publication_metadata']=metadata
 for k in META: metadata.setdefault(k,dict(status='unresolved',reason='No object-level datum recovered from inspected source.',failed_query_ids=qids))
 for v in metadata.values():
  if isinstance(v,dict) and v.get('status')=='no' and 'Full excavation report was not obtained' in v.get('scope',''):
   v['status']='unresolved';v['original_revision_label']='no, scoped to uninspected report';v['failed_query_ids']=v.get('search_ids',qids)
 audit={}
 for k in ['coordinates','excavation_campaigns','publications','cisi','icit_count','mahadevan_1977_count','present_holding','digital_availability']:
  v=s.get(k);audit[k]=dict(status='unresolved' if unresolved(v) or not v else 'recorded',observation_field=k,search_ids=qids)
 s['holding_assessment']=dict(status='unresolved',reason='The inspected sources provide historical holding codes or no holder. No current object-level repository verification was obtained; retain the dated published observations in present_holding.',failed_query_ids=qids)
 audit['present_holding']['status']='unresolved'
 audit['present_holding']['observation_field']='holding_assessment and present_holding'
 for k in META: audit['metadata.'+k]=dict(status=metadata[k].get('status','unresolved') if isinstance(metadata[k],dict) else 'unresolved',observation_field='publication_metadata.'+k,search_ids=qids)
 for k in CLASSES: audit['counts.'+k]=dict(status='recorded' if any(numeric(c) for c in s['reported_counts_by_class'][k]) else 'unresolved',observation_field='reported_counts_by_class.'+k,search_ids=qids)
 final=s.get('final_report',{})
 partial={'Gumla','Mehrgarh','Naru-Waro-dharo','Rehman Dheri','Sarai Khola'}
 surveys={'Jhukar','Lohumjo-daro','Sotka Koh','Sutkagen-dor','Ornach area'}
 if name in partial and final.get('status')=='identified':
  final['publication_assessment']='Excavation report identified; final/comprehensive status unresolved for this census.'
 elif final.get('status') in ('identified','verified'):
  final['publication_assessment']='Final exploration publication' if name in surveys else 'Final excavation monograph'
 else: final['publication_assessment']='No final publication established by the recorded searches.'
 audit['final_report']=dict(status='unresolved' if name in partial else final.get('status','unresolved'),observation_field='final_report',search_ids=qids)
 audit['post_cisi_finds']=dict(status=s.get('post_cisi_assessment',{}).get('status','unresolved'),observation_field='post_cisi_assessment',search_ids=qids)
 s['field_audit']=audit
sites.sort(key=lambda s:s['canonical_name'].casefold());checks=[];problems=[]
for s in sites:
 missing=[dict(kind=k,id=i) for k,i in refs(s) if i not in (src if k=='source' else qry)]
 queries={qry[i]['query'] for i in s['revision_query_ids'] if i in qry}
 opened=[i for k,i in refs(s) if k=='source' and i in src and src[i].get('opened') and i!='RCO-LOCAL']
 c=dict(site=s['canonical_name'],distinct_revision_queries=len(queries),opened_source_ids=sorted(set(opened)),dangling_references=missing);checks.append(c)
 if missing or len(queries)<3 or not opened: problems.append(c)
if problems: write('integration-failures.json',problems);raise ValueError('Incomplete query/source/reference coverage; see integration-failures.json')
missing_fields=Counter(k for s in sites for k,v in s['field_audit'].items() if v['status'] in ['unresolved','not_located'])
final=Counter(s.get('final_report',{}).get('status','unresolved') for s in sites)
post=Counter(s.get('post_cisi_assessment',{}).get('status','unresolved') for s in sites)
local=[s for s in sites if s.get('local_corpus')]
agg=dict(as_of=DATE,status='Exploratory',site_label_rows=len(sites),catalogue_localities=len({s['site_entity_id'] for s in sites}),identity_basis='Gharo Bhiro and Nuhato share one CISI2 locality; unresolved homonyms are not deduplicated.',local_matched_label_rows=len(local),local_label_sum_faces=sum(s['local_corpus'].get('faces',0) for s in local),local_label_sum_object_families=sum(s['local_corpus'].get('object_families',0) for s in local),local_label_sum_distinct_cisi_ids=sum(s['local_corpus'].get('distinct_cisi_ids',0) for s in local),local_sum_basis='Per-label sums, not independently deduplicated physical objects.',final_report_status_counts=dict(final),post_cisi_assessment_status_counts=dict(post),sites_with_documented_post_cisi_finds=[s['canonical_name'] for s in sites if s.get('post_cisi_assessment',{}).get('status')=='documented_find'],sites_with_numeric_class_observations=sum(any(any(numeric(c) for c in s['reported_counts_by_class'][k]) for k in CLASSES) for s in sites),sites_with_coordinates=sum(not unresolved(s.get('coordinates')) for s in sites),sources=len(sources),opened_source_records=sum(bool(s.get('opened')) for s in sources),search_records=len(searches),revision_search_records=sum(str(s['id']).startswith('R') for s in searches),minimum_distinct_revision_queries_per_site=min(c['distinct_revision_queries'] for c in checks),missing_fields=dict(missing_fields.most_common()),mahadevan1977_comparison=dict(sites=len(comparisons),published_included_objects=sum(c['published_count'] for c in comparisons),local_faces=sum(c['local_faces'] for c in comparisons),local_object_families=sum(c['local_object_families'] for c in comparisons),local_distinct_cisi_ids=sum(c['local_distinct_cisi_ids'] for c in comparisons),basis='Seven historical site totals; dates/selection differ; no pooled completeness ratio.'))
agg['site_entities_after_known_alias_join']=agg['catalogue_localities']
agg['sites_with_final_publication_identified']=[s['canonical_name'] for s in sites if s['final_report']['publication_assessment'] in ('Final excavation monograph','Final exploration publication')]
agg['sites_with_final_excavation_monograph_identified']=[s['canonical_name'] for s in sites if s['final_report']['publication_assessment']=='Final excavation monograph']
agg['sites_with_final_exploration_publication_identified']=[s['canonical_name'] for s in sites if s['final_report']['publication_assessment']=='Final exploration publication']
agg['sites_with_full_final_report_scan_inspected']=[s['canonical_name'] for s in sites if s['final_report'].get('full_text_inspected')]
agg['sites_with_report_identified_final_status_unresolved']=[s['canonical_name'] for s in sites if s['final_report']['publication_assessment'].startswith('Excavation report identified')]
agg['revision_live_web_queries']=sum(str(s['id']).startswith('R') and 'local' not in str(s.get('place','')).lower() for s in searches)
write('site-rows.json',dict(as_of=DATE,status='Exploratory',sites=sites));write('sources.json',dict(as_of=DATE,sources=sources));write('searches.json',dict(as_of=DATE,searches=searches));write('aggregate.json',agg);write('site-count-comparison.json',comparisons)
with (OUT/'site-rows.csv').open('w',encoding='utf-8',newline='') as f:
 fields=sorted({k for s in sites for k in s});writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
 for s in sites: writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in s.items()})
archive=[dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((OUT/'first-pass').iterdir()) if p.is_file()]
if (OUT/'preservation.json').exists():
 if read('preservation.json')['files']!=archive: raise ValueError('Preserved archive differs from recorded hashes')
else: write('preservation.json',dict(archive_files=len(archive),files=archive,note='First-pass files copied before edits; hashes identify preserved witnesses.'))
write('revision-audit.json',dict(as_of=DATE,status='Verified computation',checks=checks,dangling_references=0,minimum_queries=agg['minimum_distinct_revision_queries_per_site'],archive_files=len(archive),note='Mechanical query/reference checks do not verify source interpretation or authenticity.'))
print(json.dumps(agg,ensure_ascii=False,indent=2))
