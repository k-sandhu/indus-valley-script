import pathlib,json,hashlib,datetime,re
P=pathlib.Path('experiments/2026-10-20-farmana-reserve-review'); L=pathlib.Path('data/raw/2026-10-20-farmana-reserve-review'); A=pathlib.Path('data/raw/2026-10-20-fresh-test-collection')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp='2026-10-20-v1'; raw=L/f'enriched-objects-{stamp}.jsonl'; safe=P/f'enrichment-manifest-{stamp}.json'; log=L/f'ACCESS-LOG-enrichment-{stamp}.json'
assert not any(p.exists() for p in [raw,safe,log])
base=A/'objects.jsonl'; txt=L/'page-0385.txt'; source=A/'farmana.pdf'
rows=[json.loads(x) for x in base.read_text().splitlines()]
text=txt.read_text(); additions={}
for n in range(1,7):
 match=re.search(r'S-'+str(n)+r' (North Area|East Area|Central Area)\n(.*?)\n(?=S-|No\.|Table 7\.2)',text,re.S)
 assert match,n
 area=match[1]; values=match[2].splitlines(); trench,phase=values[:2]; measurements=values[2:]
 fields=['length','width','thickness_with_boss','thickness_without_boss','weight'] if n<5 else ['length','width','thickness']
 assert len(measurements)==len(fields)
 dims={}
 for field,val in zip(fields,measurements):
  dims[field]={'source_value':val,'numeric_value':float(val.rstrip('+')),'plus_marker':val.endswith('+'),'unit':'mm' if field!='weight' else None,'unit_status':'column-header' if field!='weight' else 'not-stated-in-table-header','value_status':'catalogued'}
 additions[f'FRN2011-S{n}']={'area':{'value':area,'value_status':'catalogued'},'trench':{'value':trench,'value_status':'catalogued'},'phase':{'value':phase,'value_status':'catalogued'},'dimensions':{'value':dims,'value_status':'catalogued','source':{'pdf_page':385,'printed_page':371,'table':'7.2' if n<5 else '7.3','row':f'S-{n}'}},'metadata_enrichment_source':{'pdf_page':385,'printed_page':371,'table':'7.2' if n<5 else '7.3','source_sha256':sha(source)}}
for r in rows:
 if r['object_id'] in additions:r.update(additions[r['object_id']])
 r['frozen_test_eligible']=False
 r['identity_review_caveats']={'family_154':{'block_house_recorded':'2D3-','excavation_id_derived_locus':'2D9','status':'unresolved-field-conflict; preserve both'},'family_155':{'block_house_recorded':'ID5-','normalized_candidate':'1D5','status':'provisional-I-to-1-normalization'},'absence_scope':'conditional on recorded loci and absence of unrecorded relocation or duplicate registration'}
 r['derivative_provenance']={'version':stamp,'parent_path':base.as_posix(),'parent_sha256':sha(base),'frozen_parent_preserved':True}
raw.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n')
access={'participant':'GPT-6.1-Sol / Codex desktop / reserve_identity_review','role':'acquisition metadata enrichment','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'access':[{'path':base.as_posix(),'purpose':'copy existing frozen register to separate derivative'},{'path':txt.as_posix(),'purpose':'transcribe all six table rows, without selecting on inscription content'},{'path':(A/'pages/page-0385.png').as_posix(),'purpose':'complete source page pixel review of table headers, units and row alignment'},{'path':'knowledge/editorial/WRITING.md','purpose':'re-read writing rules'}],'model_or_prediction_files_opened':False,'bench_run':False,'test_eligible':0,'reserved_content_returned_to_parent':False}
log.write_text(json.dumps(access,indent=2))
manifest={'version':stamp,'authors':['GPT-6.1-Sol / Codex desktop / reserve_identity_review'],'created_utc':access['completed_utc'],'status':'local-only-metadata-derivative','rows':36,'rows_enriched':6,'enriched_identifiers':list(additions),'fields_populated':['area','trench','phase','dimensions.length','dimensions.width','dimensions.thickness_with_boss (Table 7.2)','dimensions.thickness_without_boss (Table 7.2)','dimensions.weight (Table 7.2; unit unspecified in header)','dimensions.thickness (Table 7.3)','metadata_enrichment_source','identity_review_caveats','derivative_provenance'],'source_coordinates':[{'pdf_page':385,'printed_page':371,'table':'7.2','identifiers':'S-1 through S-4'},{'pdf_page':385,'printed_page':371,'table':'7.3','identifiers':'S-5 through S-6'}],'source_title':'Excavations at Farmana, District Rohtak, Haryana, India, 2006-2008','identity_assumptions':['Family 154 records block 2D3 and excavation-identifier-derived locus 2D9; conflict retained.','Family 155 ID5 to 1D5 normalization remains provisional.','Conditional absence claims require correct recorded loci and no unrecorded relocation or duplicate registration.'],'source_plus_markers_preserved':True,'weight_unit_assumed':False,'physical_faces_complete':'unknown','source_total_conflict':'29 reported versus 30 candidate pottery identifiers; P859/P860 relation unresolved','approved_test_eligible':0,'original_register_and_review_outputs_preserved':True,'files':[{'path':p.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [raw,log]],'parent_register':{'path':base.as_posix(),'sha256':sha(base)},'source_pdf_sha256':sha(source)}
safe.write_text(json.dumps(manifest,indent=2))
reloaded=[json.loads(x) for x in raw.read_text().splitlines()]; assert len(reloaded)==36 and sum(x['object_id'] in additions for x in reloaded)==6 and not any(x['frozen_test_eligible'] for x in reloaded)
print(json.dumps({'rows':36,'enriched':6,'eligible':0,'manifest':safe.as_posix(),'derivative_sha256':sha(raw)}))
