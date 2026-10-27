"""Record the verified local presentation without copying source-image bytes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
LOCAL=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/presentation')

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
    p=Path(p)
    return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    v=read(HERE/'verification-v3.json')
    i=read(HERE/'input-manifest-v3.json')
    final=Path(v['final_path'])
    assert sha(final)==v['final_sha256']
    receipt=LOCAL/'build/v3/validation.json'
    r=read(receipt)
    assert r['finalSha256']==v['final_sha256']
    assert r['presentationLayout']['finding_count']==0
    assert r['presentationLayout']['warning_count']==0
    comp=LOCAL/'build/v3/render-comparison.json'
    c=read(comp)
    assert c['changed_slide_numbers']==[6,16]
    native=LOCAL/'build/v3/powerpoint/native-review.json'
    n=read(native)
    assert n['finalFileChanged'] is False
    # This is validation metadata, without source-image bytes or payloads.
    write(HERE/'finalization-v3.json',r)
    write(HERE/'render-review-v3.json',{
        'status':'pass','method':'Every v2 slide was inspected individually. All v3 slides were rendered; 24 PNGs match v2 byte for byte, and modified slides 6 and 16 were individually reinspected. The final contact sheet was reviewed.',
        'final_render_comparison':ref(comp),
        'powerpoint_native_review':ref(native),
        'final_contact_sheet':ref(LOCAL/'build/v3/powerpoint/contact.png'),
        'rendered_slides':c['final_rendered_slides'],
        'outstanding_visual_issues':[]
    })
    authored=['prepare_deck.py','build_deck.mjs','render_powerpoint.ps1','verify_deck.py','finish_manifest.py','input-manifest-v3.json','verification-v3.json','finalization-v3.json','render-review-v3.json','README.md','VISUAL-REVIEW.md','RETROSPECTIVE.md']
    manifest={
        'schema_version':'local-presentation.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'final','title':'Shared infrastructure through rebuilding',
        'authors':[{'model_family':'GPT-6','exact_serving_variant':'unknown','harness':'Codex desktop collaboration'}],
        'local_only':True,'rights':'Original publication rights remain in force. Acquired source imagery and all presentation binaries are local-only.',
        'artifact':{'physical_path':str(final),'logical_path':'data/raw/2026-10-24-shared-infrastructure-plan-test/presentation/output/'+final.name,'sha256':sha(final),'bytes':final.stat().st_size,'format':'pptx'},
        'analytical_run':{'logical_path':'experiments/2026-10-24-shared-infrastructure-plan-test/run-v1.json','sha256':i['root_run_sha256']},
        'atlas_manifest':{'physical_path':i['atlas_manifest_path'],'sha256':i['atlas_manifest_sha256'],'version':'run-v2'},
        'input_manifest':ref(HERE/'input-manifest-v3.json'),
        'content':{k:v[k] for k in ['slides','native_chart_slides','native_table_slides','source_image_slides','embedded_media_files','note_pages','chart_source_numeric_points_checked','frozen_input_files','frozen_image_assets']},
        'source_notes':'Every slide contains full source references and locators in its notes, with the root run hash. Source panels and display crops have hash and transformation records in the input manifest and D evidence payload.',
        'validation':{'status':'pass','portable_finalization':ref(HERE/'finalization-v3.json'),'source_numeric_and_package_checks':ref(HERE/'verification-v3.json'),'render_and_visual_review':ref(HERE/'render-review-v3.json'),'powerpoint_version':n.get('powerPointVersion',n.get('powerpointVersion','16.0')),'all_final_slides_rendered':True,'native_chart_edit_resize_save_reopen_samples':3,'final_file_unchanged_by_native_checks':True,'layout_findings':0,'layout_warnings':0},
        'authoring':{'library':'@oai/artifact-tool','font':'Arial','palette':['#F7F4ED','#182C30','#207D80','#BA573B'],'artifact_operation_marker':'Ran once immediately before first PPTX authoring; all revisions belong to that creation operation.','native_chart_data':'Frozen literal chart snapshots in embedded editable workbooks. No source formulas existed to preserve.'},
        'revision_history':[{'version':'v1','status':'preserved layout draft'},{'version':'v2','status':'preserved inspected layout draft','changes':'Enlarged source contexts and shortened eligibility-table text.'},{'version':'v3','status':'final','changes':'Replaced wrapped Metres headers on slides 6 and 16 with m; no archaeological value changed.'}],
        'scope':'Exploratory source and measurement audit. Zero qualified institutional comparisons; no new conjecture credence update. Previously exposed material is discovery material.',
        'slide_index':v['slide_index'],
        'authored_files':[ref(HERE/p) for p in authored]
    }
    write(HERE/'artifact-manifest.json',manifest)
    print(json.dumps({'artifact':str(final),'sha256':sha(final),'manifest':str(HERE/'artifact-manifest.json'),'manifest_sha256':sha(HERE/'artifact-manifest.json'),'status':'pass'}))

if __name__=='__main__':main()
