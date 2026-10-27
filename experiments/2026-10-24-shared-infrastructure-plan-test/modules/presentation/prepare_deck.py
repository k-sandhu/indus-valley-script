"""Freeze source data and prepare local display crops for a 26-slide PowerPoint."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STUDY=ROOT/'experiments/2026-10-24-shared-infrastructure-plan-test'
LOCAL=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/presentation')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(d,key='assets'):return d if isinstance(d,list) else d[key]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='v1');ap.add_argument('--atlas',default='manifest-run-v2.json');a=ap.parse_args()
    LOCAL.mkdir(parents=True,exist_ok=True)
    target=LOCAL/'build'/f'evidence-{a.version}.json'
    if target.exists():raise FileExistsError(target)
    (LOCAL/'build').mkdir(exist_ok=True);(LOCAL/'output').mkdir(exist_ok=True)
    display=LOCAL/'display-crops'/a.version;display.mkdir(parents=True,exist_ok=False)
    paths=[STUDY/n for n in ['run-v1.json','REPORT.md','DECISION.md','TEST-DESIGN.md','MEASUREMENT-RULES.md','PROTOCOL.md','PROTOCOL.sha256.json','lothal-recount-v1.json','measurement-review-v1.json']]
    paths +=[STUDY/'modules'/m/f for m,f in [('plans-west','plan-panels.json'),('plans-west','visual-assets.json'),('plans-west','module-freeze.json'),('plans-east','visual-assets.json'),('plans-east','RESEARCH.md'),('contexts','visual-assets.json'),('contexts','RESEARCH.md'),('mohenjo-control','plan-panels.json')]]
    atlaspath=STUDY/'modules/visuals'/a.atlas
    if not atlaspath.exists():raise FileNotFoundError(f'Final atlas required: {atlaspath}')
    paths.append(atlaspath)
    lead=STUDY/'POSTJOIN-LEAD-01.json'
    if lead.exists():paths.append(lead)
    root=read(STUDY/'run-v1.json')
    assert sha(STUDY/'run-v1.json')=='1217731e249aa6cb51eaeebc9a7346a2ec291dccbbdd6fff7616847d199ddd3d'
    for row in root['inputs']:
        assert sha(ROOT/row['path'])==row['sha256'],row['path']
    assets={}
    def add(key,path,citation,caption='',expected=None,box=None):
        p=Path(path)
        h=sha(p)
        if expected:assert h==expected,key
        im=Image.open(p)
        source_path=p;source_hash=h
        if box:
            im=im.crop(tuple(box));p=display/f'{key}.png';im.save(p);h=sha(p)
        assets[key]={'id':key,'physical_path':str(p),'sha256':h,'pixels':list(im.size),'source_image_path':str(source_path),'source_image_sha256':source_hash,'display_crop':box,'citation':citation,'caption':caption,'local_only':True}
    westpanels=rows(read(STUDY/'modules/plans-west/plan-panels.json'),'panels')
    for p in westpanels:
        add(p['id'],p['crop_physical_path'],f"{p['source_id']}: {p['source_title']}. {p['locator']}. PDF zero-based index {p['pdf_page_index']}. {p['source_url']}. Source SHA-256 {p['parent_source_sha256']}. Phase: {p['phase']}. North: {p['north_reference']}. {p['panel_class']}. Crop and rotation: {p['crop_pixels_actual']}, {p['rotation_counterclockwise_degrees']} degrees CCW. Original survey error unknown.",p.get('phase',''),p['crop_sha256'])
    for w in rows(read(STUDY/'modules/plans-west/visual-assets.json')):
        cite='\n'.join(f"{s['source_id']}: {s['title']}. {s['locator']}. PDF zero-based index {s['pdf_page_index']}. {s['url']}. Source SHA-256 {s['source_sha256']}." for s in w['source_panels'])
        add(w['id'],w['physical_path'],cite,w['caption'],w['sha256'],[52,190,1640,1480])
    for e in rows(read(STUDY/'modules/plans-east/visual-assets.json')):
        im=Image.open(e['physical_path'])
        cite=f"{e['source_id']}: {e['source_title']}. Printed p.{e['printed_page']}, Fig.{e['figure']}, PDF zero-based index {e['pdf_zero_based_index']}. {e['source_url']}. Source SHA-256 {e['source_parent_sha256']}."
        add(e['id'],e['physical_path'],cite,e['caption'],e['sha256'],[0,125,im.width-510,im.height-100])
    for c in rows(read(STUDY/'modules/contexts/visual-assets.json')):
        cite=f"{c['source_id']}: {c['source_title']}. Locator {json.dumps(c['locator'],ensure_ascii=False)}. {c['source_url']}. Source SHA-256 {c['source_sha256']}."
        with Image.open(c['physical_path']) as im:
            mask=np.asarray(im.convert('L'))<235
            xs=np.where(mask.mean(axis=0)>.002)[0];ys=np.where(mask.mean(axis=1)>.002)[0]
            crop=[max(0,int(xs.min())-25),max(0,int(ys.min())-25),min(im.width,int(xs.max())+26),min(im.height,int(ys.max())+26)]
        add(c['id'],c['physical_path'],cite,c['caption'],c['sha256'],crop)
    for c in rows(read(STUDY/'modules/mohenjo-control/plan-panels.json'),'panels'):
        add(c['id'],c['physical_path'],f"{c['source_id']}: {c['locator']}. {c['title']}. Original plan with source-reading annotation; supplementary availability control, not a persistence episode.",c['title'],c['sha256'])
    atlas=read(atlaspath)
    assert sha(atlaspath)=='1db55b6a2e3ef1de7835ff31b14e7c95dcd8122eb66d94f0203c2ffef61a579b'
    for f in atlas['figures']:
        cite=json.dumps(f['sources'],ensure_ascii=False,indent=2)
        add(f"ATLAS-{f['figure']:02d}",f['physical_path'],cite,f['caption'],f['sha256'])
        if f['figure'] in [1,10,18]:
            crop={1:[590,350,2190,1915],10:[35,190,1740,1690],18:[35,200,1740,1980]}[f['figure']]
            add(f"ATLAS-{f['figure']:02d}-DETAIL",f['physical_path'],cite,f['caption'],f['sha256'],crop)
    for index in [45,51]:
        src=next(s for s in root['source_use_records'] if s['source_ref']=='mohenjo-control::MACKAY-VOL2')
        path=LOCAL.parent/'mohenjo-control'/f'scale-detail-{index}.png'
        cite=f"{src['title']}. PDF zero-based index{index}; source 0-50 feet bar. {src['url']}. Source SHA-256 {src['sha256']}. Local detail of the untouched source render, not a new scale drawing."
        add(f'MD-SCALE-{index}',path,cite,'Original printed scale-bar detail. Negative subdivided extension excluded from calibration.')
    context={r['id']:r for r in root['context_assessments']}
    measurements={r['id']:r for r in root['measurements']}
    evidence={'version':a.version,'root_run_sha256':sha(STUDY/'run-v1.json'),'root':root,'assets':assets,'atlas':atlas,'context_by_id':context,'measurement_by_id':measurements,
      'report':(STUDY/'REPORT.md').read_text(encoding='utf-8'),'decision':(STUDY/'DECISION.md').read_text(encoding='utf-8'),'test_design':(STUDY/'TEST-DESIGN.md').read_text(encoding='utf-8'),
      'postjoin_lead':read(lead) if lead.exists() else None}
    write(target,evidence)
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'evidence_path':str(target),'evidence_sha256':sha(target),'version':a.version,
      'root_run_sha256':evidence['root_run_sha256'],'atlas_manifest_path':str(atlaspath),'atlas_manifest_sha256':sha(atlaspath),
      'inputs':[{'logical_path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in paths],
      'image_assets':[{'id':k,'physical_path':v['physical_path'],'sha256':v['sha256'],'source_image_path':v['source_image_path'],'source_image_sha256':v['source_image_sha256'],'display_crop':v['display_crop']} for k,v in assets.items()],
      'storage':'All source pixels, derivatives, drafts, final PPTX and renders remain local-only on D.',
      'authors':[{'model':'GPT-6 family; exact serving variant unknown','harness':'Codex desktop collaboration','role':'presentation author with coordinator and source-module contributions'}]}
    write(HERE/f'input-manifest-{a.version}.json',manifest)
    print(json.dumps({'assets':len(assets),'atlas_figures':len(atlas['figures']),'evidence_sha256':sha(target),'path':str(target)}))

if __name__=='__main__':main()
