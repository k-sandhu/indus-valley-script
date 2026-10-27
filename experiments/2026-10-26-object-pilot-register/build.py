"""Project held metadata into a fixed pilot; source-derived records stay on D:."""
from pathlib import Path
import json, hashlib, re, collections, sys

ROOT=Path(__file__).resolve().parents[2]
P=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw')
OUT=RAW/'2026-10-26-object-pilot-register'
VERSION=sys.argv[1] if len(sys.argv)>1 else 'v2'
assert re.fullmatch(r'v\d+',VERSION)
def endpoint(name):return name.replace('-v1.',f'-{VERSION}.')
BASE=RAW/'2026-10-22-object-register/run-v2'
TARGETS=[f'PCF-DHV-{n:03}' for n in range(5,15)]+['H-1657','H-2587','H-1688','H-1682','H-1692','L-164','L-163','L-167','L-146','L-174']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):
 with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def logical(p):
 p=p.resolve()
 for root in [Path('D:/projects/indus_valley_script'),ROOT]:
  try:return p.relative_to(root).as_posix()
  except ValueError:pass
 return str(p)
catalog={}; inputs={}; original_sources={}
def source(p,title=None,expected=None):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 key=logical(p)
 if key not in catalog:
  exists=p.exists();actual=sha(p) if exists and p.is_file() else None
  catalog[key]={'source_ref':key,'logical_path':key,'physical_path':str(p.resolve()),'exists':exists,'bytes':p.stat().st_size if exists else None,'sha256':actual,'title':title or p.name,'rights':'source-specific; detailed reuse local-only','expected_sha256':expected,'hash_matches_prior':actual==expected if expected else None}
 return key
def load(p):
 key=source(p);inputs[key]=catalog[key];return read(Path(p))

# Import original source catalogues without reading inscription content.
packages=['2026-10-22-object-register','2026-10-24-object-identity-extension','2026-10-24-object-identity-pass2','2026-10-24-object-identity-pass3','2026-10-24-harappa-context-extension','2026-10-24-harappa-context-pass2','2026-10-24-harappa-context-pass3','2026-10-24-office-seal-evidence','2026-10-24-office-seal-pass2','2026-10-24-office-seal-pass3','2026-10-24-office-source-verification']
for package in packages:
 d=ROOT/'experiments'/package
 manifests=sorted(d.glob('*source-manifest*.json'))
 if package=='2026-10-22-object-register':manifests=[d/'run-v2/source-manifest.json']
 for manifest in manifests:
  m=load(manifest)
  for row in m.get('sources',m.get('inputs',[])):
   loc=row.get('logical_path',row.get('path'))
   sid=row.get('source_id',row.get('id'))
   if not sid:continue
   if loc:
    ref=source(loc,row.get('title'),row.get('sha256'))
    catalog[ref].update({k:row[k] for k in ['url','title','author','authors','year','lineage','coordinates'] if k in row})
   elif row.get('url'):
    ref=row['url'];catalog[ref]={'source_ref':ref,**row,'logical_path':None,'physical_path':None,'exists':None,'sha256':None,'hash_unavailable_reason':'web reader source; retained caption notes are linked by assertion input','rights':'unverified; local-only'}
   else:continue
   original_sources[(package,sid)]=ref

objects={t:{'record_id':t,'site':'Dholavira' if t.startswith('PCF') else 'Harappa' if t.startswith('H-') else 'Lothal','identity_status':'unresolved-source-target' if t.startswith('PCF') else 'provisional-catalogue-target','accepted_physical_merge':False,'aliases':[],'candidate_family_ids':[],'assertions':[],'faces':[],'images':[],'missing_fields':[],'conflicts':[],'exposure_status':'previously-examined; no freshness claim'} for t in TARGETS}
counter=0
def add(t,field,value,status,refs,locator=None,**extra):
 global counter
 if value is None or value=='':return
 counter+=1
 objects[t]['assertions'].append({'assertion_id':f'P{counter:05}','field':field,'value':value,'status':status,'source_refs':list(dict.fromkeys(refs)),'locator':locator or {'missing_reason':'original coordinate not held; see exact input record'},**extra})
def upstream(package,sid):return original_sources.get((package,sid))

# The base register already excludes inscription payload from its object and face interfaces.
baseobjects=[]
for line in (BASE/'objects.jsonl').open(encoding='utf8'):
 x=json.loads(line)
 if any(a['value'] in objects for a in x.get('aliases',[])):baseobjects.append(x)
baseids={x['object_id'] for x in baseobjects}
base_ref=source(BASE/'objects.jsonl');assertion_ref=source(BASE/'assertion-values.jsonl');face_ref=source(BASE/'faces.jsonl')
id_to_t={}
for x in baseobjects:
 ts={a['value'] for a in x['aliases'] if a['value'] in objects}
 for t in ts:
  id_to_t[x['object_id']]=t
  objects[t]['source_family_id']=x['source_family_id']
  objects[t]['aliases']=x['aliases']
  objects[t]['base_fields']=x['fields']
  objects[t]['conflicts']+=x.get('conflicts',[])
for line in (BASE/'assertion-values.jsonl').open(encoding='utf8'):
 x=json.loads(line);t=id_to_t.get(x.get('object_id'))
 if not t:continue
 loc=x.get('locator') or {};refs=[assertion_ref]
 if loc.get('path'):refs.append(source(loc['path']))
 add(t,x['field'],x.get('normalized_value'),x['value_status'],refs,loc,original_assertion_id=x['assertion_id'],raw_value=x.get('raw_value'),uncertainty=x.get('uncertainty'),join_status=x.get('join_status'),dependency_group=x.get('source_id'))
for line in (BASE/'faces.jsonl').open(encoding='utf8'):
 x=json.loads(line);t=id_to_t.get(x.get('object_id'))
 if not t:continue
 objects[t]['faces'].append(x)
 for image in x['image_links']:
  img=dict(image);img['source_refs']=[face_ref];img['coverage_class']='inherited-index-link';objects[t]['images'].append(img)

# Dholavira accession targets retain candidate edges separately from aliases.
q=RAW/'2026-10-24-object-identity-pass2'
inventory=load(q/'target-inventory-v1.json');panels={x['row_id']:x for x in load(q/'target-primary-panels-v1.json')};obs=load(q/'source-observations-v1.json')
earlier=load(RAW/'2026-10-24-object-identity-extension/identity-assertions-v1.json')
bridge=load(q/'bridge-decisions-v1.json');dispositions=load(RAW/'2026-10-24-object-identity-pass3/identity-dispositions-v1.json')
bisht=upstream('2026-10-24-object-identity-pass2','bisht-2015-held')
for x in inventory:
 t=x['row_id'];o=objects[t];panel=panels[t];iref=logical(q/'target-inventory-v1.json')
 o['candidate_family_ids']=x['local_family_ids'].split('|')
 o['aliases']=[{'scheme':'Bisht excavation registration','value':x['registration'],'status':'source-asserted'}]
 o['identity_evidence']=[a for a in earlier if a['row_id']==t]
 o['bridge_decision']=next(a for a in bridge if a['row_id']==t)
 o['latest_identity_disposition']=next(a for a in dispositions if a['row_id']==t)
 for field in ['registration','other_numbers','findspot','depth_or_layer','period_or_phase','object_type','object_subtype','material']:
  add(t,field,x[field],'catalogued',[iref,bisht],{'pdf_page':int(x['pdf_page']),'printed_page':int(x['page']),'row_id':t},dependency_group='Bisht2015')
 for field in ['primary_publication','publication_year']:
  add(t,field,x[field],'catalogued',[iref,bisht],{'pdf_page':panel['pdf_page'],'printed_page':panel['printed_page'],'catalogue_serial':panel['catalogue_serial']},dependency_group='Bisht2015')
 if t in obs['measurements']:
  m=obs['measurements'][t]
  add(t,'dimensions',{'values':{k:v for k,v in m.items() if k!='pdf_page'},'unit':obs['unit']},'catalogued',[logical(q/'source-observations-v1.json'),bisht],{'pdf_page':m['pdf_page'],'printed_page':m['pdf_page']-17,'row_id':t},dependency_group='Bisht2015',uncertainty='raw strings retained; ext and Frag are not scalar dimensions')
 image_ref=source(panel['image_path'],expected=panel['image_sha256'])
 o['images'].append({'path':panel['image_path'],'sha256':panel['image_sha256'],'kind':'catalogue panel with accession-labelled face photograph','side_match':False,'coverage_class':'source-target-photo','source_refs':[bisht,image_ref,logical(q/'target-primary-panels-v1.json')],'locator':{k:panel[k] for k in ['pdf_page','printed_page','clip','catalogue_serial']},'reverse_coverage':'not established'})
 add(t,'physical_observation',obs['photo_notes'][t],'catalogued',[logical(q/'source-observations-v1.json'),bisht],{k:panel[k] for k in ['pdf_page','printed_page','clip']},dependency_group='Bisht2015')

# Harappa primary source assertions, including later context additions and contrary lots.
hp='2026-10-24-harappa-context-extension';f=RAW/hp/'context-records-v1.json';hr=load(f)
for x in hr['records']:
 t=x['cisi']
 if t not in objects:continue
 for field in ['registration','excavation_unit','item','mound','deposit','period','dating_basis','conflict']:
  add(t,field,x.get(field),'conflicting' if field=='conflict' else 'catalogued',[logical(f),upstream(hp,x['source_id'])],{'pdf_pages':x['pdf_pages'],'cisi':t},dependency_group='HARP excavation lineage')
hp2='2026-10-24-harappa-context-pass2';f=RAW/hp2/'context-records-v1.json'
for x in load(f):
 t=x['object']
 if t=='H-1657':
  for field in ['key','area','trench','room','recovery_relation','published_period']:
   add(t,field,x.get(field),'catalogued',[logical(f),upstream(hp2,'HARP56')],{'slide':56,'web_reader_lines':'10-12'},dependency_group='HARP excavation lineage')
hp3='2026-10-24-harappa-context-pass3';f=RAW/hp3/'observations-v1.json'
for x in load(f)['cases']:
 t=x['case']
 if x.get('source'):
  for field in ['registration','lot','item','assertion','join']:
   add(t,field,x.get(field),'catalogued',[logical(f),upstream(hp3,x['source'])],{'pdf_page':7 if t=='H-2587' else 65,'printed_page':6 if t=='H-2587' else 249,'figure':'4 item 2' if t=='H-2587' else '13.44e'},dependency_group='HARP excavation lineage')
  if x.get('conflicting_source'):add(t,'conflict',x['conflicting_source'],'conflicting',[logical(f),upstream(hp,'KM2010')],{'pdf_pages':[9,10]},dependency_group='HARP excavation lineage')

# Available Harappa figure pages and the retained HARP slide pointer are separate
# from accepted isolated face photographs. No additional source pixels are read.
for t,filename,sid,locator,kind in [
 ('H-2587','page-12.png','K1999',{'pdf_page':12,'figure':'4','item':2,'caption_pdf_page':7,'caption_printed_page':6},'line drawing on complete source figure page'),
 ('H-1688','1991-page-65.png','DK1991',{'pdf_page':65,'printed_page':249,'figure':'13.44e'},'drawing on complete source figure page')]:
 asset=RAW/hp3/filename;ref=source(asset)
 objects[t]['images'].append({'path':str(asset.resolve()),'sha256':sha(asset),'kind':kind,'source_refs':[ref,upstream(hp3,sid),logical(f)],'locator':locator,'coverage_class':'source-qualified-drawing-page','side_match':False,'binding_status':'published figure cross-reference retained; isolated face geometry not assigned','image_scope':'whole page including neighboring objects'})
objects['H-1657']['images'].append({'kind':'HARP slide 56 photograph page pointer; image file not acquired in prior pass','source_refs':[upstream(hp2,'HARP56'),source(RAW/hp2/'web-reader-notes.txt')],'locator':{'slide':56,'web_reader_lines':'10-12'},'coverage_class':'web-source-page-pointer','side_match':False,'binding_status':'published full registration joins caption to target; no local photo bytes or all-side inspection'})
for t,page in [('H-1682',10),('H-1692',11)]:
 add(t,'source_narrative_page',{'source':'Inscribed Objects from Harappa Excavations 1986–2007','pdf_page':page,'image_availability':'No target image linked in inspected held layer; this pointer is narrative context.'},'catalogued',[upstream(hp,'KM2010'),source(RAW/hp/'2010-selected-text.txt')],{'pdf_page':page,'cisi':t},dependency_group='HARP excavation lineage')

# Office evidence uses the corrected relation ledger, preserving qualified group statements.
f=RAW/'2026-10-24-office-seal-evidence/relations-v2.json'
for x in load(f)['relations']:
 t=x['subject']
 if t not in objects:continue
 sid=upstream('2026-10-24-office-seal-evidence',x['source_id'])
 add(t,x['predicate'],x['value'],x['value_status'],[logical(f),sid],{k:x[k] for k in ['pdf_page','printed_page'] if k in x},dependency_group=x['source_id'],qualification={k:v for k,v in x.items() if k not in ['subject','predicate','value','value_status','source_id']})
# Carry later view ledger wholesale as metadata, without interpreting images again.
f=RAW/'2026-10-24-office-seal-pass2/view-ledger-v1.json';views=load(f)
dump(OUT/endpoint('held-view-ledger-v1.json'),views)
for target in views['targets']:
 t=target['object']
 for view in target['views']:
  view=dict(view);sid=upstream('2026-10-24-office-seal-pass2',view['source'])
  view['source_refs']=[logical(f),sid]
  view['coverage_class']='source-qualified-view-pointer'
  view['side_match']=False
  if t=='L-164' and view['source']=='rao1985':
   view['binding_status']='conflicting plate association; source photo is not assigned to L-164'
   view['coverage_class']='unresolved-candidate-source-page'
  filename=(f"cisi1-pdf{view['pdf_page']}.png" if view['source']=='cisi1' else f"frenez-pdf{view['pdf_page']}.png" if view['source']=='frenez2005' else f"rao-pdf{view['pdf_page']}-upright.png")
  asset=RAW/'2026-10-24-office-seal-pass2'/filename
  if asset.exists():
   view['path']=str(asset.resolve());view['sha256']=sha(asset);view['source_refs'].append(source(asset))
   view['image_scope']='whole published page; target panel stated separately'
  objects[t]['images'].append(view)
  add(t,'published_image_view',{k:v for k,v in view.items() if k not in ['path','sha256','source_refs']},'conflicting' if view['coverage_class']=='unresolved-candidate-source-page' else 'catalogued',view['source_refs'],{k:view[k] for k in ['pdf_page','printed_page','panel'] if k in view},dependency_group=view['source'])
f=RAW/'2026-10-24-office-seal-pass3/observations.md';source(f)
add('L-164','plate_reference_conflict',{'Rao1985_p319':'1864 associated with CLXI F','Rao1985_p325':'1830 associated with CLXI F','adjudication':'unresolved; actual photographed specimen not established'},'conflicting',[logical(f),upstream('2026-10-24-office-seal-pass3','rao1985')],{'pdf_pages':[70,76],'printed_pages':[319,325]},dependency_group='Rao1985')

# Preserve reviews as qualification dependencies, never as independent excavation sources.
reviews=[]
for package in ['2026-10-24-harappa-context-pass2-review','2026-10-24-office-source-verification']:
 d=ROOT/'experiments'/package
 for p in d.glob('*.md'):
  if p.name in ['REPORT.md','RETROSPECTIVE.md']:reviews.append(source(p))
for o in objects.values():o['review_refs']=reviews

if int(VERSION[1:])>=4:
 # Amendment 1 closes catalogue-only omissions using held, qualified layers.
 text=source(RAW/hp/'2010-selected-text.txt')
 for field,value in [('material','steatite'),('dimensions',{'dimension':'maximum diameter','value':15.29,'unit':'mm'}),('key','H96/7158-01')]:
  add('H-2587',field,value,'conflicting' if field=='key' else 'catalogued',[text,upstream(hp,'KM2010')],{'pdf_page':9,'retained_text_lines':'363-366'},dependency_group='HARP excavation lineage',qualification='Held primary narrative; key conflicts with figure caption; separate reviewer checks material.')
 add('H-2587','key','H96/7458-0001','conflicting',[text,upstream(hp,'KM2010')],{'pdf_page':10,'figure':'2.1','retained_text_lines':'389-390'},dependency_group='HARP excavation lineage')
 objects['H-2587']['aliases'] += [{'scheme':'HARP prose key','value':'H96/7158-01','status':'conflicting'},{'scheme':'HARP figure key','value':'H96/7458-0001','status':'conflicting'}]
 cisi_path=ROOT/'data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl'
 cisi_ref=source(cisi_path)
 with cisi_path.open(encoding='utf8') as f:
  row=next(json.loads(line) for i,line in enumerate(f) if i==782)
 assert row['cisi']=='L-174'
 objects['L-174']['catalogue_only_basic_data']=row
 original_cisi=upstream('2026-10-24-office-seal-pass2','cisi1')
 locator={'row_index_zero_based':782,'printed_page':373,'pdf_page':409,'catalogue_key':'L-174'}
 for field,column,status in [('catalogue_identifier','cisi','catalogued'),('fc_number','col2_fc','catalogued'),('excavation_alias','col3_excavation','catalogued'),('museum_cell_raw','col4_museum','unknown'),('photo_credit_cell_raw','col5_photographs','catalogued')]:
  add('L-174',field,row[column],status,[cisi_ref,original_cisi],{**locator,'column':column},dependency_group='CISI1 basic data',qualification='Catalogue-only source row; museum ??? remains unknown; See Corr. retained; no Lipi family join.',uncertainty={'uncertain_columns':row['uncertain_columns'],'blind_adjudicated_columns':row['blind_adjudicated_columns'],'rechecked_columns':row['rechecked_columns']})
 objects['L-174']['aliases'] += [{'scheme':'CISI','value':'L-174','status':'source-asserted'},{'scheme':'FC','value':row['col2_fc'],'status':'source-asserted'},{'scheme':'excavation number','value':row['col3_excavation'],'status':'source-asserted'}]
 pilot=ROOT/'experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json'
 old=load(pilot);pilot_ref=logical(pilot)
 for a in old['assertions']:
  if a.get('object_id')!='OL-0094':continue
  loc=a.get('locator',{});refs=[pilot_ref]
  if loc.get('path'):refs.append(source(loc['path']))
  if a['source_id']=='lothal2005':refs.append(upstream('2026-10-24-office-seal-pass2','frenez2005'))
  elif a['source_id']=='cisi1':refs.append(original_cisi)
  status='conflicting' if a['field']=='impression_count' else 'inferred' if a.get('confidence')=='derived' else 'catalogued'
  add('L-174',a['field'],a['value'],status,refs,loc,dependency_group=a['source_id'],original_assertion_id=a['id'],qualification={k:a.get(k) for k in ['method','confidence','review_status']})
 objects['L-174']['conflicts'].append('impression_count: earlier table 1; later prose/corrigendum and plate 2; all witnesses retained')

groups={'identity':['registration','excavation_identifier','excavation_alias','key'],'material':['material'],'dimensions':['measurement','dimensions'],'findspot':['findspot','area','room','mound','room_grid'],'stratum_phase':['depth_or_layer','period_or_phase','period','published_period','stratum_phase','period_label'],'date':['calendar_interval','date_interval','manufacture_date'],'accession':['museum_accession','museum_registration'],'publications':['primary_publication','bibliographic_locator'],'lot':['lot','excavation_unit','lot_identifier'],'mass':['mass'],'dating_sample':['dating_sample','radiocarbon_sample']}
queue=[];coverage={}
for name,fields in groups.items():
 present=[]
 for t,o in objects.items():
  assertions=[a for a in o['assertions'] if a['field'] in fields and a['value'] not in [None,'','unknown']]
  if assertions:present.append(t)
  else:
   o['missing_fields'].append(name)
   queue.append({'record_id':t,'field':name,'priority':1 if name in ['identity','lot'] else 2 if name in ['findspot','stratum_phase','dimensions'] else 3,'reason':'no qualified nonempty assertion in consolidated inputs','required_evidence':'registered item record or source-qualified catalogue page' if name in ['identity','lot'] else 'source observation with object identity and measurement/date basis'})
 coverage[name]={'denominator':20,'source_assertion_records':len(present),'accepted_physical_identity_records':0,'accepted_identity_policy':'No physical identities adjudicated in this consolidation; source-key presence is counted separately.'}
for t,o in objects.items():
 o['missing_fields']+=['mass' ] if 'mass' not in o['missing_fields'] else []
 o['missing_fields'].append('complete_face_inventory')
 if t.startswith('PCF'):
  o['missing_fields']+=['corpus_identity_bridge','reverse_image']
  queue.append({'record_id':t,'field':'corpus_identity_bridge','priority':0,'reason':'candidate families remain unmerged','required_evidence':'accession-to-CISI concordance or source-qualified photograph of the same carrier','candidate_count':len(o['candidate_family_ids'])})
 else:
  queue.append({'record_id':t,'field':'complete_face_inventory','priority':2,'reason':'indexed panels do not establish exhaustive all-side coverage','required_evidence':'registered obverse/reverse/edge image inventory with scale and side assignments'})
 if o['conflicts'] or any(a['status']=='conflicting' for a in o['assertions']):o['conflicts'].append('source assertions retain unresolved contrary values; inspect assertion statuses and field values')
coverage['images']={'denominator':20,'source_assertion_records':sum(bool(o['images']) for o in objects.values()),'local_file_records':sum(any(im.get('path') for im in o['images']) for o in objects.values()),'web_pointer_only_records':sum(bool(o['images']) and not any(im.get('path') for im in o['images']) for o in objects.values()),'accepted_physical_identity_records':0,'source_target_photos':10,'all_faces_complete':0}
data={'schema_version':'1.0','protocol_sha256':sha(P/'PROTOCOL.md'),'scope':'20 fixed target records; no new physical merge; no inscription payload','objects':[objects[t] for t in TARGETS],'source_catalogue':list(catalog.values()),'view_ledger_ref':logical(OUT/endpoint('held-view-ledger-v1.json')),'source_dependencies':['HARP publications and captions belong to one excavation lineage','Bisht context and individual catalogue are arrangements of one report','CISI and derived exports may inherit the same printed assertion; agreement is not independent corroboration'],'review_status':'author validation; separate integration review required'}
dump(OUT/endpoint('pilot-register-v1.json'),data)
dump(OUT/endpoint('missing-evidence-v1.json'),{'denominator':20,'rows':sorted(queue,key=lambda x:(x['priority'],x['record_id'],x['field']))})
dump(P/endpoint('coverage-v1.json'),coverage)
aggregate={'target_records':20,'site_counts':dict(collections.Counter(o['site'] for o in objects.values())),'assertions':counter,'dholavira_candidate_families':len({f for o in objects.values() for f in o['candidate_family_ids']}),'dholavira_candidate_edges':sum(len(o['candidate_family_ids']) for o in objects.values()),'new_source_acquisitions':0,'new_empirical_field_gains':0,'new_physical_merges':0,'consolidated_prior_layers':len(packages),'missing_evidence_rows':len(queue),'new_confirmation_reads':0}
dump(P/endpoint('aggregate-v1.json'),aggregate)
dump(P/endpoint('source-manifest-v1.json'),{'protocol_sha256':sha(P/'PROTOCOL.md'),'sources':list(catalog.values()),'outputs':[{'logical_path':logical(p),'physical_path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'handling':'local-only'} for p in OUT.glob('*.json')]})
checks={'exact_frame':list(objects)==TARGETS,'unique_record_ids':len(set(objects))==20,'ten_dholavira':sum(t.startswith('PCF') for t in objects)==10,'candidate_families':aggregate['dholavira_candidate_families']==62,'candidate_edges':aggregate['dholavira_candidate_edges']==274,'no_physical_merges':all(not o['accepted_physical_merge'] for o in objects.values()),'source_refs_resolve':all(ref in catalog for o in objects.values() for a in o['assertions'] for ref in a['source_refs']),'local_source_files_exist':all(s['exists'] is not False for s in catalog.values()),'prior_hashes_match':all(s.get('hash_matches_prior') is not False for s in catalog.values()),'detailed_output_D':str(OUT.resolve()).lower().startswith('d:'),'raw_junction_D':str((ROOT/'data/raw').resolve()).lower().startswith('d:'),'all_explicit_missing':all(o['missing_fields'] for o in objects.values()),'H2587_conflict_retained':any('7158' in str(a['value']) and '7458' in str(a['value']) for a in objects['H-2587']['assertions']),'L164_conflict_retained':any(a['field']=='plate_reference_conflict' for a in objects['L-164']['assertions']),'no_sequence_fields':not any(re.search(r'^(transcription|text_code|signs_visual|sequence)',a['field'],re.I) for o in objects.values() for a in o['assertions'])}
dump(P/endpoint('validation-v1.json'),{'checks':checks,'passed':sum(checks.values()),'failed':sum(not v for v in checks.values()),'tier':'submitted','failures':[s for s in catalog.values() if s.get('exists') is False or s.get('hash_matches_prior') is False]})
print(json.dumps(aggregate));print(json.dumps(checks))
