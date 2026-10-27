"""Check frozen inputs, source references, scientific denominators and local products."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

P=Path(__file__).resolve().parent
REPO=P.parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')

def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main(figures,tag):
    output=P/f'study-validation-{tag}.json'
    if output.exists():raise FileExistsError('Preserve validation output')
    checks=[]
    def check(name,passed,detail=None):
        checks.append({'name':name,'passed':bool(passed),'detail':detail})
    run=read(P/'run-v1.json')
    check('frozen_run_hash',sha(P/'run-v1.json')=='1217731e249aa6cb51eaeebc9a7346a2ec291dccbbdd6fff7616847d199ddd3d')
    for r in run['inputs']:
        f=REPO/r['path'];check('input:'+r['path'],f.is_file() and sha(f)==r['sha256'])
    for r in read(P/'EXPOSURE.json')['prior_pins']:
        f=REPO/r['path'];check('prior_unchanged:'+r['path'],f.is_file() and sha(f)==r['sha256'])
    cf=read(P/'modules/contexts/context-freeze.json')
    for r in cf['frozen_files']:
        check('context_freeze:'+r['path'],sha(P/'modules/contexts'/r['path'])==r['sha256'])
    wf=read(P/'modules/plans-west/module-freeze.json')
    for r in wf['files']:
        check('west_freeze:'+r['path'],sha(P/'modules/plans-west'/r['path'])==r['sha256'])
    for r in wf['raw_references']:
        check('west_raw_freeze:'+Path(r['path']).name,sha(Path(r['path']))==r['sha256'])
    check('context_coded_before_new_architecture',cf['architecture_outcomes_received_or_read'] is False)
    check('new_measurement_class',run['status_class']=='exploratory')
    check('fixed_primary_six_towns',len(run['primary_towns'])==6 and run['supplementary_control_town']=='mohenjo-daro')
    for c in run['decisions']:
        check('ineligible_effect_remains_unknown:'+c['claim'],c['eligible']==0 and c['effect'] is None)
    check('18_quantities',len(run['measurements'])==18)
    check('17_lengths_one_angle',run['counts']['measurement_units']=={'m':17,'degree':1})
    check('32_context_assessments',len(run['context_assessments'])==32)
    check('78_source_date_entries',len(run['date_evidence'])==78)
    check('76_determinations_or_TL',sum(bool(r.get('determination_as_reported')) for r in run['date_evidence'])==76)
    check('no_repair_dates_substituted',all(not r['usable_as_specific_repair_date'] for r in run['date_evidence']))
    for r in run['source_hash_checks']:
        f=Path(r['physical_path'])
        check('source_payload:'+r['source_ref'],f.is_file() and sha(f)==r['expected_sha256'])
    check('source_hash_scope',len(run['source_use_records'])==42 and run['counts']['distinct_source_payload_hashes']==35)
    check('independent_math_review',read(P/'measurement-review-v1.json')['passed'])
    check('math_check_count',len(read(P/'measurement-review-v1.json')['quantity_checks'])==19)
    check('independent_lothal_recount',read(P/'lothal-recount-v1.json')['passed'])
    check('lothal_distinct_denominators',run['Lothal_denominators']['table_rows']==93 and run['Lothal_denominators']['prose_category_sum']==92)
    check('Dholavira_usable_labels',run['Dholavira_coverage']['gate_counts']['stratum_label']==211 and run['Dholavira_coverage']['gate_counts']['depth_label']==201)
    check('postjoin_lead_not_inserted',len(run['context_assessments'])==32 and read(P/'POSTJOIN-LEAD-01.json')['changes_frozen_counts'] is False)
    lead=read(P/'POSTJOIN-LEAD-01.json')
    check('postjoin_lead_source',sha(Path(lead['physical_path']))==lead['sha256'])
    check('no_real_confirmation',read(P/'EXPOSURE.json')['real_confirmation_opened'] is False)
    bench=read(P/'bench-shots-synthetic-v1.json')
    check('benchmark_synthetic',bench.get('synthetic') is True)
    heavy=[str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.suffix.lower() in {'.pdf','.pptx','.png','.jpg','.jpeg','.zip','.geojson'}]
    check('bulk_products_not_in_checkout',not heavy,heavy)
    logical=REPO/'data/raw/2026-10-24-shared-infrastructure-plan-test'
    check('C_logical_path_reaches_D',logical.resolve()==RAW.resolve())
    atlas=read(figures)
    check('30_atlas_figures',len(atlas['figures'])==30)
    for f in atlas['figures']:
        path=Path(f['physical_path'])
        check('figure_hash:'+f['id'],path.is_file() and sha(path)==f['sha256'])
        check('figure_on_D:'+f['id'],path.resolve().is_relative_to(RAW.resolve()))
        check('figure_locators:'+f['id'],bool(f.get('source_note')) and bool(f.get('caption')))
    for filename in ('book-manifest-v2.json','explorer-manifest-v2.json'):
        manifest=read(P/filename)
        path=Path(manifest.get('output_physical_path',manifest.get('physical_path')))
        check(filename+':hash',sha(path)==manifest['sha256'])
        check(filename+':on_D',path.resolve().is_relative_to(RAW.resolve()))
        check(filename+':local_only',manifest['local_only'])
    explorer=read(P/'explorer-manifest-v2.json')
    html=Path(explorer['physical_path']).read_text(encoding='utf8')
    check('no_external_HTML_assets',not re.search(r'<(?:script|img|link)[^>]+(?:src|href)=[\"\']https?://',html,re.I))
    check('embedded_figures',html.count('data:image/jpeg;base64,')==30 and explorer['external_assets']==0)
    check('PDF_render_review',read(P/'book-visual-review-v2.json')['passed'])
    check('explorer_UI_review',read(P/'explorer-ui-review-v2.json')['passed'])
    deck=read(P/'modules/presentation/artifact-manifest.json')
    presentation=Path(deck['artifact']['physical_path'])
    check('presentation_hash',sha(presentation)==deck['artifact']['sha256'])
    check('presentation_on_D',presentation.resolve().is_relative_to(RAW.resolve()))
    check('presentation_local_only',deck['local_only'])
    check('presentation_same_run',deck['analytical_run']['sha256']==sha(P/'run-v1.json'))
    check('presentation_same_atlas',deck['atlas_manifest']['sha256']==sha(figures))
    for key in ('input_manifest',):
        r=deck[key];check('presentation:'+key,sha(Path(r['path']))==r['sha256'])
    for key in ('portable_finalization','source_numeric_and_package_checks','render_and_visual_review'):
        r=deck['validation'][key]
        check('presentation_review_hash:'+key,sha(Path(r['path']))==r['sha256'])
    for r in deck['authored_files']:
        check('presentation_authored_hash:'+Path(r['path']).name,sha(Path(r['path']))==r['sha256'])
    dv=deck['validation']
    check('presentation_review_pass',dv['status']=='pass')
    check('presentation_rendered_and_unchanged',dv['all_final_slides_rendered'] and dv['final_file_unchanged_by_native_checks'])
    check('presentation_three_editable_chart_checks',dv['native_chart_edit_resize_save_reopen_samples']==3)
    check('presentation_no_layout_findings',dv['layout_findings']==0 and dv['layout_warnings']==0)
    numeric=read(Path(dv['source_numeric_and_package_checks']['path']))
    check('presentation_42_chart_values_checked',numeric['status']=='pass' and numeric['chart_source_numeric_points_checked']==42)
    visual=read(Path(dv['render_and_visual_review']['path']))
    check('presentation_26_reviewed_renders',visual['status']=='pass' and len(visual['rendered_slides'])==26)
    for r in visual['rendered_slides']:
        check('presentation_render_hash:'+str(r['slide']),sha(Path(r['path']))==r['sha256'])
    with zipfile.ZipFile(presentation) as archive:
        names=archive.namelist()
        slides=[n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        # Locate chart parts by their XML type; this package nests them under slides/charts.
        charts=[n for n in names if n.endswith('.xml') and ET.fromstring(archive.read(n)).tag=='{http://schemas.openxmlformats.org/drawingml/2006/chart}chartSpace']
        notes=[n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
        tables=sum(len(ET.fromstring(archive.read(n)).findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}tbl')) for n in slides)
        check('presentation_package_integrity',archive.testzip() is None)
        check('presentation_26_slides_and_notes',len(slides)==26 and len(notes)==26)
        check('presentation_native_charts_and_tables',len(charts)==3 and tables==8,{'chart_parts':charts,'table_count':tables})
    result={'scope':'Same-team source and reproducibility review; not independent archaeological confirmation',
            'run_sha256':sha(P/'run-v1.json'),'atlas_manifest_sha256':sha(figures),
            'presentation_manifest_sha256':sha(P/'modules/presentation/artifact-manifest.json'),
            'checks':checks,'check_count':len(checks),'passed':all(c['passed'] for c in checks),
            'failures':[c for c in checks if not c['passed']],
            'authors':[{'model':'GPT-6 family; exact variant unavailable','harness':'Codex desktop collaboration','role':'root validation'}]}
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'checks':len(checks),'passed':result['passed'],'failures':result['failures']}))
    assert result['passed']

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--figures',type=Path,required=True);a.add_argument('--tag',required=True)
    args=a.parse_args();main(args.figures,args.tag)
