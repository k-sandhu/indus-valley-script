"""Save final analytical inputs for the coordinator without changing frozen data."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west')

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    target=HERE/'module-freeze.json'
    if target.exists():raise FileExistsError(target)
    sources=read(HERE/'sources.json')
    panels=read(HERE/'plan-panels.json')['panels']
    for s in sources['sources']:
        s['current_plan_audit_locators']=[{'panel_id':p['id'],'locator':p['locator'],'pdf_page_index':p['pdf_page_index']} for p in panels if p['source_id']==s['id']]
        if s['id']=='W-S01':s['current_prose_audit_locator']='pp.95-99,110,114-122,131-144; PDF index=printed page+16'
        if s['id']=='W-S02':s['current_prose_audit_locator']='pp.85-87,101,109,124-126; PDF index=printed page+10; table of contents and plate omissions inspected'
        if s['id']=='W-S04':s['current_prose_audit_locator']='pp.45,48-56; PDF index=printed page-27; legacy phase namespace retained'
        if s['id']=='PW-HAR1997':s['current_prose_audit_locator']='pp.142-147,151-153; PDF index=printed page-139; Table1 radiocarbon rows verified in page images'
    write(HERE/'sources.json',sources)
    routes=read(RAW/'acquisition-routes-v1.json')+read(RAW/'acquisition-routes-v2.json')
    coverage={
      'created_utc':datetime.now(timezone.utc).isoformat(),'status_class':'exploratory',
      'towns':['harappa','dholavira','lothal'],
      'added':{'source_use_records':14,'inherited_pdf_records':6,'new_HARP_image_source_records':8,'selected_original_panels':23,'source_defined_cases':15,'source_eligibility_cases_included':1,'dimension_readings':7,'registered_descriptive_pairs':1,'annotated_boards':12,'new_object_identity_records':0,'new_inscription_readings':0},
      'acquisitions':routes,
      'raw_logical_prefix':'data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west/',
      'raw_physical_prefix':str(RAW),
      'new_fields':['Original image and caption URLs and hashes','PDF page boxes and zero-based page indices','Crop and rotation matrices','Source north references and bar endpoints','Local feature endpoints and endpoint-reading radii','Independent grid controls and held-out residuals','Composite, schematic, isometric and partial-exposure classifications','Observed geometry separated from access interpretation','Named counterexamples and reasons a phase pair is ineligible','Below-wall radiocarbon identities, source calibration convention and conflicting determination'],
      'eligible_persistence_episodes':0,'persistence_difference':None,
      'coverage_rule':'The 23 selected panels are a bounded audit, not the completeness of town architecture or the inscribed-object corpus. Fifteen cases include overlapping areas and a source-eligibility case.',
      'source_failures':[
       {'target':'Lothal original VolumeI street and phase plates','route':'Internet Archive creator query, then broad title query and held-item metadata','outcome':'Initial creator filter returned zero; corrected broad query returned32 items. No complete original plate volume acquired. Existing text scan contains Fig.16,17,19 but lacks whole street plateXXXVIII.','missing_reason':'Required original before/after street plates unavailable through the audited routes.'},
       {'target':'Lothal machine-readable source text','route':'Alternate held OCR PDF','outcome':'OCR is corrupt and misrecognizes the English pages. Original page images were inspected.','missing_reason':'No usable automatic source transcription for this scan.'},
       {'target':'Dholavira Lower Town trench15x24 before/after street plan','route':'Original report Lower Town chapter and figures','outcome':'Text gives earlier5.25 m width and Stage V encroachment; Fig.6.26 is an oblique photo without a surveyed trench join.','missing_reason':'No matching phase-keyed plan or later clear width located.'},
       {'target':'Harappa Trench39 complete phase pair','route':'Original HARP slides26 and63','outcome':'Different extents and composite later features; no comparable complete partition inventory.','missing_reason':'Pair does not supply the required common exposure or two separated phase networks.'},
       {'target':'Harappa Trench54 and Trench11 phase-separated plans','route':'Original HARP overview, detail and section slides','outcome':'Multiple periods, superimposed partial views and robbed masonry retained.','missing_reason':'Complete earlier/later exposures are not supplied.'}
      ],
      'rights_status':'All acquired source material and every crop or annotated derivative are rights-unverified and local-only.',
      'authors':[{'model':'GPT-6 family; exact serving variant unknown','harness':'Codex desktop','agent':'western_towns'}]
    }
    for row in coverage['source_failures']:
        row['outcome']=row['outcome'].replace('returned32','returned 32').replace('Fig.16,17,19','Figs.16,17,19').replace('plateXXXVIII','plate XXXVIII').replace('earlier5.25','earlier 5.25')
    write(HERE/'coverage.json',coverage)
    names=['sources.json','plan-panels.json','episodes.json','measurements.json','inventory-freeze.json','inventory-freeze.sha256.json','trace-manifest-v1.json','CROP-CLARIFICATION-01.json','visual-assets.json','coverage.json','RESEARCH.md','README.md','RETROSPECTIVE.md']
    names+=sorted(p.name for p in HERE.glob('*.py'))
    frozen={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Analytical source module frozen before receiving a newly assembled documentary overlay. Validation certificate may be added without changing these files.','status_class':'exploratory','files':[{'path':n,'sha256':sha(HERE/n),'bytes':(HERE/n).stat().st_size} for n in names],
      'raw_references':[{'path':str(RAW/n),'sha256':sha(RAW/n)} for n in ['traces-v1.json','panel-reference-points-v1.json','annotations-v1.json','measurement-v1/measurement-details.json','measurement-v1/registration-details.json']],
      'counts':coverage['added'],'eligible_P1_episodes':0,'P1_effect':None,
      'authors':coverage['authors']}
    write(target,frozen)
    write(HERE/'module-freeze.sha256.json',{'path':'module-freeze.json','sha256':sha(target)})
    print(json.dumps({'freeze':str(target),'sha256':sha(target),'analytical_files':len(names),'counts':frozen['counts']}))

if __name__=='__main__':main()
