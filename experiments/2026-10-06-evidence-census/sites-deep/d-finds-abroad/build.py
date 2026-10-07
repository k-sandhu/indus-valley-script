"""Build the census from curated observations, saved searches, and coordinator aggregates.

Run from the repository root. The default build never replaces differing output.
Use --verify for a read-only repeat, or --output-dir for a new dated endpoint.
"""
import argparse, collections, csv, hashlib, io, json, pathlib, re, sys
sys.dont_write_bytecode = True
from research_data import ROWS, SOURCES
ROOT=pathlib.Path(__file__).resolve().parents[4]
OWNED=pathlib.Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad'
DATE='2026-10-07'
META=['findspot','stratum_or_phase','absolute_dates','dimensions','material','photographs','drawings','registration_numbers']
CLASS_FIELDS=['seals','sealings','tablets','inscribed_pottery_and_graffiti','metal','other_inscribed_objects']
def canonical_url(u):
 return u.replace('%3A',':').rstrip('/')
def seen_records(calls):
 seen={}
 for ci,c in enumerate(calls):
  chunks=c['response'].split('--------------------------------------------------------------------------------')
  for ch in chunks:
   m=re.search(r'^([^\n]*?) \((https?://[^\n]+)\)\s*$',ch,re.M)
   if not m: continue
   title,url=m.groups();key=canonical_url(url)
   rec=seen.setdefault(key,dict(title=title.strip(),url=url,seen_in=[],opened_in=[],failed_in=[]))
   rec['seen_in'].append(ci)
   if c['kind']!='search' and 'Total lines:' in ch and 'Total lines: 1\n' not in ch and 'Internal Error' not in ch and '503 Service' not in ch:
    rec['opened_in'].append(ci)
  # Retain attempted URLs even when the reader returned no source title.
  for url in c.get('urls',[]):
   key=canonical_url(url);rec=seen.setdefault(key,dict(title=None,url=url,seen_in=[],opened_in=[],failed_in=[]))
   if ci not in rec['seen_in']:rec['seen_in'].append(ci)
   if url in c['response'] and re.search(r'Failed to fetch '+re.escape(url),c['response']):rec['failed_in'].append(ci)
 return seen
def source_manifest(calls):
 seen=seen_records(calls);sources={k:dict(v) for k,v in SOURCES.items()}
 byurl=collections.defaultdict(list)
 for k,v in sources.items():byurl[canonical_url(v['url'])].append(k)
 for key,rec in sorted(seen.items()):
  if key not in byurl:
   sid='WEB-'+hashlib.sha256(key.encode()).hexdigest()[:12]
   sources[sid]=dict(id=sid,title=rec['title'],authors=None,year=None,venue=None,url=rec['url'],access='opened_text' if rec['opened_in'] else 'search_snippet' if rec['title'] else 'failed_open',bibliography_status='Unresolved; not used as a literature authority unless explicitly linked in a row',reuse_terms='Unresolved; payload local-only',quoted_words=0)
   byurl[key].append(sid)
  for sid in byurl[key]:
   sources[sid].update(access_date=DATE,search_snippet_seen=any(calls[i]['kind']=='search' for i in rec['seen_in']),web_content_opened=bool(rec['opened_in']),raw_web_calls=sorted(set(rec['seen_in'])),raw_witness='data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/web-witness.json')
   if rec['failed_in']:sources[sid]['failed_open_calls']=rec['failed_in']
 for sid,rec in sources.items():
  rec.setdefault('access_date',DATE);rec.setdefault('web_content_opened',False);rec.setdefault('search_snippet_seen',False)
  if sid in ['gadd1932','parpola2018','salut2016','gonur2005','kircho2008','cisi33','nippur1993','frankfort1933']:
   fn={'cisi33':'cisi33-excerpt2022','nippur1993':'nippur1993-s3','frankfort1933':'frankfort1933-s3'}.get(sid,sid)
   p=RAW/(fn+'.pdf')
   rec.update(local_content_opened=True,raw_pdf=str(p.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 return sources,byurl
def searches(calls,byurl):
 result=[]
 for ci,c in enumerate(calls):
  if c['kind']!='search':continue
  pairs=c.get('pairs') or [(None,q) for q in c.get('queries',[])]
  group=seen_records([c]);ids=sorted(set(sid for url in group for sid in byurl.get(url,[])))
  for s,q in pairs:
   result.append(dict(id='Q%03d'%(len(result)+1),site=s,query=q,place_searched='Live web search via web.run',date=DATE,raw_call_index=ci,raw_witness='data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/web-witness.json',returned_source_ids=ids,result_scope='Pooled response for this tool call; individual-result/query attribution is unavailable',outcome='Returned '+str(len(ids))+' distinct source records in the pooled response' if ids else 'No source title/URL pair returned',accepted_as_count_inventory=False))
 return result
def unresolved(field,query_ids,detail):
 return dict(status='unresolved_after_search',value=None,reason=detail,search_ids=query_ids,field=field)
def class_bucket(c):
 t=c['object_class'].lower()
 if 'tablet' in t or 'document' in t:return 'tablets'
 if 'pottery' in t or 'graffiti' in t:return 'inscribed_pottery_and_graffiti'
 if 'clay sealing' in t or 'seal-impressed' in t:return 'sealings'
 if 'seal' in t:return 'seals'
 return 'other_inscribed_objects'
def build():
 calls=json.loads((RAW/'web-witness.json').read_text(encoding='utf-8'))
 source_map,byurl=source_manifest(calls)
 qs=searches(calls,byurl)
 coverage_path=ROOT/'experiments/2026-10-06-research-program/local-site-coverage.json'
 coverage=json.loads(coverage_path.read_text(encoding='utf-8'))
 local={r['site']:r for r in coverage['sites']}
 rows=[]
 for raw in ROWS:
  r=json.loads(json.dumps(raw,ensure_ascii=False))
  qids=[q['id'] for q in qs if q['site']==r['site']]
  assert len(qids)>=3,(r['site'],qids)
  r['search_ids']=qids;r['status']='Exploratory'
  opened=[k for k in r['sources'] if source_map[k]['access'] in ['opened_text','opened_local_text']]
  assert opened,r['site'];r['opened_substantial_source_ids']=opened
  r['identity']=dict(canonical_name=r['site'],alternative_spellings=r.pop('aliases'),country=dict(value=r.pop('country'),sources=r['sources'],location='Site attribution in associated source(s); country granularity'),province=dict(value=r.pop('province'),status='provisional_admin_assignment' if raw['province'] else 'unresolved_after_search',sources=r['sources'],search_ids=qids,reason='Modern subdivision needs a dedicated geographic authority' if raw['province'] else 'Searches did not recover a verified modern subdivision'),coordinates=r.pop('coordinates') or unresolved('coordinates',qids,'No verified site-specific coordinate witness recovered; region labels have no site coordinate. See returned source records, including failed gazetteer routes.'))
  records=[local[x] for x in r['local_labels']]
  r['local_corpus']=dict(source='experiments/2026-10-06-research-program/local-site-coverage.json',source_sha256=hashlib.sha256(coverage_path.read_bytes()).hexdigest(),records=records,faces=sum(x['faces'] for x in records),object_families=sum(x['object_families'] for x in records),distinct_cisi_ids_sum=sum(x['distinct_cisi_ids'] for x in records),summation_basis='Sum of literal alias-label rows, without archaeological object deduplication',local_label_absent=not records)
  r['cisi_coverage']=r.pop('cisi') or unresolved('cisi_volume_pages',qids,'No site page range found in the four assignment volumes. CISI 3.3 preface p. xi assigns West Asia/Gulf to planned 3.4. This search did not establish publication of 3.4; local absence is not a cutoff.')
  r['icit_mahadevan_counts']=unresolved('icit_mahadevan_counts',qids,'Targeted site/Mahadevan/ICIT query returned general corpus or interpretation pages, but no inspected primary site subtotal. Local Lipi totals are recorded separately.')
  r['published_counts']=r.pop('counts')
  buckets={k:[] for k in CLASS_FIELDS}
  for count in r['published_counts']:
   buckets[class_bucket(count)].append(count)
   if count['object_class'].startswith('copper stamp'):buckets['metal'].append(count)
  r['counts_by_requested_class']={k:v or unresolved(k,qids,'No class-specific published Indus count recovered; no archaeological zero inferred.') for k,v in buckets.items()}
  r['excavation_campaigns']=r.pop('campaigns') or [unresolved('campaigns',qids,'Inscription source located, but campaign years, directors and institutions were not jointly recovered.')]
  r['primary_reports_and_final_publications']=r.pop('publications') or [unresolved('primary_reports',qids,'No sufficiently verified final-report bibliography recovered; opened specimen or regional source is cited separately.')]
  r['coverage_judgment']=r.pop('coverage')
  met=r.pop('metadata')
  if met:
   r['publication_metadata']={k:dict(availability=met[k],source=met['source'],location=met['location']) for k in META}
  elif 'laursen2010' in r['sources']:
   r['publication_metadata']={k:dict(availability=v,source='laursen2010',location='Table 1 and site-linked figures; applies only to illustrated specimens') for k,v in zip(META,['partial','partial','partial','yes','partial','partial','yes','partial'])}
  else:
   r['publication_metadata']={k:dict(availability=None,**unresolved(k,qids,'Associated source was read for site/publication history; a specimen catalogue was not available for this metadata check.')) for k in META}
  r['later_find_reports']=r.pop('later')
  r['post_cisi_find_status']=dict(firmly_documented_post_site_coverage=False,reason='A dated discovery and applicable complete catalogue cutoff have not both been established.',later_publication_or_season_evidence=bool(r['later_find_reports']),sources=r['sources'],search_ids=qids)
  if not r['later_find_reports']:r['later_find_reports']=[unresolved('later_inscribed_finds',qids,'Later-find searches did not recover a dated, authenticated Indus object with an accession and applicable CISI cutoff.')]
  r['current_holdings']=r.pop('holdings') or unresolved('current_holdings',qids,'No specimen-specific present custody statement recovered; excavation nationality is not used to infer a museum.')
  r['digital_availability_and_reuse']=[dict(source=k,url=source_map[k]['url'],access=source_map[k]['access'],terms=source_map[k]['reuse_terms'],local_only=True) for k in r['sources']]
  r['open_problems']=r.pop('problems')
  # Compare only compatible specimen minima. Different classes and catalogue sequences are retained separately.
  r['published_indus_related_minimum_objects']=sum(c['count'] for c in r['published_counts'] if c['include_in_indus_minimum'] and c['basis']=='objects')
  r['count_comparison']=dict(local_families=r['local_corpus']['object_families'],published_selected_minimum_objects=r['published_indus_related_minimum_objects'],coverage_fraction=None,reason='Selected specimens, mixed uncertainty and incomplete joins prevent a coverage fraction.')
  rows.append(r)
 named=[r for r in rows if r['scope']=='named_batch_site']
 minima=[r for r in rows if r['published_indus_related_minimum_objects']>0]
 aggregate=dict(status='Verified computation',census_status='Exploratory',date=DATE,rows=len(rows),named_batch_sites=len(named),added_literature_rows=[r['site'] for r in rows if r['scope']=='added_from_literature'],scope_counts=dict(collections.Counter(r['scope'] for r in rows)),rows_with_local_faces=sum(bool(r['local_corpus']['faces']) for r in rows),local_faces=sum(r['local_corpus']['faces'] for r in rows),local_object_family_label_sum=sum(r['local_corpus']['object_families'] for r in rows),local_distinct_cisi_id_label_sum=sum(r['local_corpus']['distinct_cisi_ids_sum'] for r in rows),local_metadata_face_counts={k:sum(rec[k] for r in rows for rec in r['local_corpus']['records']) for k in ['faces_with_period_or_time','faces_with_room_or_grid','faces_with_dimensions','faces_with_excavation_number']},rows_with_final_report_identified=sum(r['final_report_identified'] for r in rows),named_sites_with_final_report_identified=sum(r['final_report_identified'] for r in named),final_report_definition='Bibliographically identified excavation synthesis or final specialist catalogue; does not imply all volumes read or all seasons closed.',rows_with_verified_coordinates=sum('source' in r['identity']['coordinates'] for r in rows),rows_with_later_report_evidence=sum(r['post_cisi_find_status']['later_publication_or_season_evidence'] for r in rows),firm_post_cisi_sites=0,rows_with_selected_indus_related_object_minimum=len(minima),selected_indus_related_object_minimum_sum=sum(r['published_indus_related_minimum_objects'] for r in rows),minimum_sum_scope='Selected published object minima including Gulf signs/pseudo-signs and provisional Ornach/Hajar attribution; no complete inventory or deduplication across region labels.',published_vs_local=[dict(site=r['site'],published_selected_minimum_objects=r['published_indus_related_minimum_objects'],local_faces=r['local_corpus']['faces'],local_families=r['local_corpus']['object_families'],source_ids=sorted(set(c['source'] for c in r['published_counts']))) for r in rows],searches=len(qs),source_records=len(source_map),input_hashes={'research_data.py':hashlib.sha256((OWNED/'research_data.py').read_bytes()).hexdigest(),'raw_web_witness':hashlib.sha256((RAW/'web-witness.json').read_bytes()).hexdigest(),'local_coverage':hashlib.sha256(coverage_path.read_bytes()).hexdigest()})
 # All region-labelled local rows must occur exactly once; aliases only combine labels.
 expected={r['site'] for r in coverage['sites'] if r['region'] in ['Mesopotamia','Persian Gulf','Iranian Plateau','Central Asia']}
 actual=[x for r in rows for x in r['local_labels']]
 assert set(actual)==expected,(set(actual)-expected,expected-set(actual))
 assert len(actual)==len(set(actual))
 assert len(rows)==36 and len(named)==23
 assert len({r['site'] for r in rows})==len(rows)
 for r in rows:
  assert set(r['publication_metadata'])==set(META)
  for c in r['published_counts']:
   assert c['source'] in source_map and c['location']
   assert c['count_date'] is not None or c['source']=='ornach_primary'
 # CSV serialises nested values as JSON; no information is dropped.
 fields=list(rows[0])
 buff=io.StringIO(newline='');writer=csv.DictWriter(buff,fieldnames=fields);writer.writeheader()
 for r in rows:writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in r.items()})
 for original, recovered in zip(rows,csv.DictReader(io.StringIO(buff.getvalue()))):
  for key,value in original.items():
   if isinstance(value,(dict,list)):assert json.loads(recovered[key])==value,(original['site'],key)
   else:assert recovered[key]==str(value),(original['site'],key)
 outputs={'site-rows.json':rows,'sources.json':list(source_map.values()),'searches.json':qs,'aggregate-results.json':aggregate,'validation.json':dict(status='Verified computation',checks={'36_unique_rows':True,'23_named_sites':True,'all_local_region_labels_once':True,'minimum_three_live_queries_each':True,'opened_substantial_source_each':True,'all_metadata_fields_present':True,'source_references_resolve':True,'csv_preserves_nested_json':True},limitations='Checks validate record structure and arithmetic, not archaeological classification or bibliographic truth.')}
 payloads={k:(json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode('utf-8') for k,v in outputs.items()}
 payloads['site-rows.csv']=buff.getvalue().encode('utf-8')
 return payloads,aggregate
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');parser.add_argument('--output-dir',type=pathlib.Path,default=OWNED);args=parser.parse_args()
 dest=args.output_dir.resolve();assert dest==OWNED or OWNED in dest.parents,'Output must remain within owned directory'
 payloads,agg=build()
 if not args.verify:dest.mkdir(parents=True,exist_ok=True)
 for name,data in payloads.items():
  p=dest/name
  if args.verify:
   assert p.read_bytes()==data,'Reproduction mismatch: '+name
  elif p.exists() and p.read_bytes()!=data:
   raise RuntimeError('Existing output differs: '+str(p)+'; use a new dated --output-dir')
  elif not p.exists():p.write_bytes(data)
 print(json.dumps({k:agg[k] for k in ['rows','named_batch_sites','local_faces','local_object_family_label_sum','rows_with_final_report_identified','rows_with_verified_coordinates','rows_with_later_report_evidence','firm_post_cisi_sites','selected_indus_related_object_minimum_sum','searches','source_records']},indent=2))
 print('Verified saved outputs' if args.verify else 'Built census outputs')
if __name__=='__main__':main()
