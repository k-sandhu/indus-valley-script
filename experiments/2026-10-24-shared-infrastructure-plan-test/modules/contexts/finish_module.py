"""Validate and freeze context records before receiving architectural outcomes."""
from pathlib import Path
import collections,datetime,hashlib,json,re
from PIL import Image
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[1]
ROOT=PACKAGE.parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/contexts')
P='11c69454d6e50304b5704db0865f76abca8d84363a67a21d42e8573e256cdb6e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    assert sha(PACKAGE/'PROTOCOL.md')==P
    sources=read(HERE/'sources.json')['sources']; sm={r['source_id']:r for r in sources}
    joins=read(HERE/'context-joins.json')['joins']; dates=read(HERE/'date-evidence.json')['records']
    access={'source_access':[{'source_id':'KANMER2013','status':'excluded HTML landing page',
      'physical_path':sm['KANMER2013']['physical_path'],'sha256':sm['KANMER2013']['sha256'],
      'url':sm['KANMER2013']['url'],'reason':'No full article obtained. Native .pdf extension and permissive rendering do not establish PDF content.'},
      {'source_id':'KANMER-CH8-LEAD','status':'indexed primary-author/source-repost lead; full chapter not held',
      'title':'Seals, Sealing and other Script Material','author_page_url':'https://www.academia.edu/4891402/Harappan_Script_Material_from_Kanmer',
      'repost_url':'https://www.scribd.com/document/212393968/Kanmer-seals-sealing-and-other-script-material-Chapter-8',
      'held_shell_text_path':str(RAW/'kanmer-ch8-held.txt'),'held_shell_text_sha256':sha(RAW/'kanmer-ch8-held.txt'),
      'reason':'Viewer shell is not the chapter; indexed layer8/9 and room claims remain leads, not adjudicated object contexts.'}],
      'acquisition_outcome':'No new network download in this module. Reused held witnesses and local derivatives are pinned by path/hash.'}
    write(HERE/'source-access.json',access)
    visual=read(HERE/'visual-assets.json')
    for a in visual['assets']:
        a['visual_review']='Inspected in contact sheet and against the original bounded pages; no added archaeological marks.'
        assert sha(Path(a['physical_path']))==a['sha256']
        w,h=Image.open(a['physical_path']).size
        assert w>300 and h>300
        a['pixels']=[w,h]
    write(HERE/'visual-assets.json',visual)
    plan=[
      {'town':'Farmana','assessment_ids':['FAR-S1','FAR-S2','FAR-S3','FAR-S4','FAR-S5','FAR-S6'],
       'source_id':'EAST-SHINDE2011','locator':'p.384/Fig.7.18,PDFindex397','asset_id':'FAR-PHASEMAP',
       'anchor':'bounded source trenches; leaders to object illustrations','north_reference':'survey graphic; no independently established true/magnetic conversion',
       'uncertainty':'No exact registered-object operating-surface point; no map overlay may imply one.'},
      {'town':'Kanmer','assessment_ids':['KAN-3IMP'],'source_id':'EAST-KHARAKWAL2011',
       'locator':'pp.369–370,indices14–15; indexed Chapter8 lead unheld','asset_id':None,
       'anchor':None,'north_reference':None,'uncertainty':'No defensible object-to-named-room plan panel in the held article. Layer numbers are not survey coordinates.'},
      {'town':'Banawali','assessment_ids':['BAN-SITTINGROOM'],'source_id':'BISHT1982-P117',
       'locator':'p.117; archivepageimagen139','asset_id':None,
       'anchor':'house in Plates10.11a–b, sitting room; plate reference only','north_reference':None,
       'uncertainty':'No room number/survey grid on the held page; source photograph does not supply map coordinates.'},
      {'town':'Harappa','assessment_ids':['HAR-TR54-MANUFACTURE'],'source_id':'KENOYER2005',
       'locator':'Fig.2,index7','asset_id':'HAR-WORKSHOP-PLAN',
       'anchor':'workshop[601] area; gridE2105–2110 vicinity,N1235 to north ofN1240',
       'north_reference':'Narrow on source; reference convention unspecified','scale':'5m bar',
       'uncertainty':'Bounded area only; registered tablets lack individual plotted points.'},
      {'town':'Harappa','assessment_ids':['HAR-W296-22'],'source_id':'MK2000',
       'locator':'author-PDFp.7/Fig.2,index7','asset_id':'HAR-SECONDARY-CLUMP',
       'anchor':'approximate source-plan finds, E2515–2530,N1172–1202',
       'north_reference':'source north arrow; reference convention unspecified','scale':'5m bar',
       'uncertainty':'Secondary dump; approximate find dots do not locate original tablet use.'},
      {'town':'Harappa','assessment_ids':['HAR-TR10E-COURTYARD','HAR-TR10E-ROOM','HAR-TR9-SUMP'],'source_id':'MK1997',
       'locator':'pp.150–151,Figures7/12 indices11–12,15,22','asset_ids':['HAR-FLOOR-SEALS','HAR-SUMP-JAR'],
       'anchor':'named trench/room or courtyard; figure captions supply object identity and locus',
       'north_reference':None,'uncertainty':'No exact object point/crosswalk to one hearth or rebuilding episode was supplied by the bounded figures.'},
      {'town':'Dholavira','assessment_ids':['DHO-ROOM-83','DHO-ROOM-140','DHO-ROOM-211','DHO-GATE10'],
       'source_id':'BISHT2015-PRELIM','locator':'tablepp.251/254/258; gatepp.228–230,indices244–246',
       'asset_id':None,'anchor':'source grid/room labels or gate western chamber; original labels retained',
       'north_reference':None,'uncertainty':'Room labels are not unique site-wide; use floor and original gate-panel mount remain unresolved. No invented point or construction phase.'},
      {'town':'Lothal','assessment_ids':['LOT-WAREHOUSE-COHORT'],'source_id':'FT2005','locator':'Figure2,p.97,index34',
       'asset_id':'LOT-DEPOSIT-PLAN','anchor':'warehouse passage41I–41J, bounded sealing-discovery area',
       'north_reference':'source north arrows; diagram orientation must be retained','scale':'100m site and5m detail bars',
       'uncertainty':'Discovery area for a cohort, not individual original application points; competing formation histories.'}]
    write(HERE/'plan-anchors.json',{'anchors':plan,'rule':'No exact modern coordinates are inferred. Every overlay must retain source label, scale/north convention and bounded uncertainty.'})
    coverage={'source_records':len(sources),'distinct_source_file_hashes':len({r['sha256'] for r in sources}),
      'new_downloads':0,'newly_adjudicated_physical_objects':0,'new_semantic_readings':0,
      'change':'New authored documentary-context/date joins and rejection assessments over held sources; detailed source tables remain local-only.',
      'context_assessment_records':len(joins),'date_evidence_entries':len(dates),
      'date_entries_with_a_published_determination':sum(r['determination_as_reported'] is not None for r in dates),
      'dholavira_source_rows_gated':225,'lothal_provenance_rows_transcribed':93,'visual_source_witnesses':len(visual['assets']),
      'not_a_coverage_claim':'No full-corpus recovery percentage or settlement-frequency estimate is inferred. Missing joins denote unassembled or unreported links.',
      'related_data_gaps':['object identity and aliases','findspot/stratum/date','source locator and contextual provenance','original-use versus manufacture/discard','independently dated construction or repair'],
      'logical_raw_root':'data/raw/2026-10-24-shared-infrastructure-plan-test/contexts',
      'physical_raw_root':str(RAW),'local_only':True,'rights':'Unverified third-party rights retained; no acquired corpus or pixels tracked.'}
    write(HERE/'coverage-changes.json',coverage)
    dids={r['id'] for r in dates}; townset={'Farmana','Kanmer','Banawali','Harappa','Dholavira','Lothal'}
    checks=[]
    def check(name,value,detail=None):
        assert value,(name,detail)
        checks.append({'check':name,'pass':True,'detail':detail})
    check('protocol hash unchanged',sha(PACKAGE/'PROTOCOL.md')==P)
    check('fixed six-town frame',set(r['town'] for r in joins)==townset)
    check('unique assessment IDs',len({r['id'] for r in joins})==len(joins))
    check('unique date IDs',len(dids)==len(dates))
    check('all rejected date references exist',all(d in dids for r in joins for d in r['rejected_date_candidates']))
    check('every assessment has a source and explicit limit',all(r['source_locators'] and r['reason_codes'] and r['missing_reason'] for r in joins))
    check('all assessed pairs unqualified',all(not r['eligible_C0018_matched_pair'] and not r['eligible_C0019_work_allocation_pair'] for r in joins))
    check('source witness paths and hashes',all(Path(r['physical_path']).is_file() and sha(Path(r['physical_path']))==r['sha256'] for r in sources))
    check('HTML article excluded',sm['KANMER2013']['usable_for_sample_or_object_facts'] is False and all(r['source_id']!='KANMER2013' for r in dates))
    check('source locator PDF indices in range',all(l['source_id'] in sm and (l['pdf_index'] is None or 0<=l['pdf_index']<sm[l['source_id']]['pages']) for r in joins for l in r['source_locators']))
    check('no invented object point coordinates',all(r['spatial_anchor'] is None or r['spatial_anchor']['point_coordinates'] is None for r in joins))
    dhol=read(RAW/'dholavira225-join-gates-v1.json')['rows'];ds=read(HERE/'dholavira225-summary.json')
    check('all225 Dholavira serials preserved',[r['source_row']['table_serial'] for r in dhol]==list(range(1,226)))
    check('all225 Dholavira accession strings unique',len({r['source_row']['accession'] for r in dhol})==225)
    check('Dholavira stage and room gate counts',ds['gate_counts']['unqualified_stage']==162 and ds['gate_counts']['explicit_room_label']==3)
    check('Lothal93 rows retained',len(read(RAW/'lothal-ft2005-table1-provenance-transcription-v1.json')['rows'])==93)
    check('Lothal disagreement preserved',read(HERE/'lothal-denominators.json')['table_literal_counts']=={'W':35,'W1':18,'W2':11,'O':10,'?':19})
    check('sample dependency controls retained',len({r['physical_sample_dependency_group'] for r in dates if r['id'] in ('HAR-A7523','HAR-QL4733')})==1 and len({r['physical_sample_dependency_group'] for r in dates if r['id'] in ('HAR-A7529','HAR-QL4730')})==1)
    check('later samples retained',all(i in dids for i in ('FAR-PLD12422','FAR-PLD12423','KAN-PLD16351','KAN-PLD16353')))
    check('raw data and source assets are onD',all(Path(a['physical_path']).resolve().is_relative_to(Path('D:/projects/indus_valley_script')) for a in visual['assets']))
    checks.append({'check':'independent archaeological adjudication','pass':None,'detail':'This module is the source audit itself. The manual Lothal transcription and source interpretations require independent review; executable validation does not certify them.'})
    write(HERE/'validation.json',{'status':'computable checks passed; source adjudication remains reviewable','checks':checks,
      'counts':coverage,'architecture_outcomes_received_or_read':False,'bench_confirmation_read':False})
    files=[]
    for p in sorted(RAW.iterdir()):
        if p.is_file():files.append({'physical_path':str(p),'logical_path':'data/raw/2026-10-24-shared-infrastructure-plan-test/contexts/'+p.name,
          'bytes':p.stat().st_size,'sha256':sha(p),'local_only':True,'rights_status':'inherited third-party rights; analysis derivatives and source text remain local-only'})
    write(HERE/'local-assets.json',{'physical_root':str(RAW),'files':files,'reused_original_sources':'See sources.json for original witness paths/hashes/URLs; files are not copied toC.'})
    frozen=['context-joins.json','date-evidence.json','eligibility-summary.json','dholavira225-summary.json','lothal-denominators.json','sources.json','source-access.json','plan-anchors.json','coverage-changes.json','visual-assets.json']
    witnesses=[{'path':name,'sha256':sha(HERE/name)} for name in frozen]
    combined=hashlib.sha256(json.dumps(witnesses,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    freeze={'version':'context-prejoin-v1','protocol_sha256':P,'architecture_outcomes_received_or_read':False,
      'prior_familiarity':'Declared inSCOPE.md. This is not a truly blind or fresh confirmation population.',
      'frozen_files':witnesses,'combined_sha256':combined,
      'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    target=HERE/'context-freeze.json'
    if target.exists():assert read(target)['combined_sha256']==combined,'Frozen records changed; preserve endpoint and issue a new version.'
    else:write(target,freeze)
    print(json.dumps({'freeze_sha256':combined,'assessments':len(joins),'date_entries':len(dates),'sources':len(sources),'source_panels':len(visual['assets'])},indent=2))
if __name__=='__main__':main()
