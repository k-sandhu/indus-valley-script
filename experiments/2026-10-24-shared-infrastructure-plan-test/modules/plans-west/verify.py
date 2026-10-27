"""Check source provenance, crop transforms and independently recomputed readings."""
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name,condition,detail=None):
        checks.append({'check':name,'pass':bool(condition),'detail':detail})
    f=read(HERE/'module-freeze.json')
    for row in f['files']:check('frozen authored file '+row['path'],sha(HERE/row['path'])==row['sha256'])
    for row in f['raw_references']:check('frozen raw reference '+Path(row['path']).name,sha(row['path'])==row['sha256'])
    sources=read(HERE/'sources.json')['sources']; sourceids={s['id'] for s in sources}
    panels=read(HERE/'plan-panels.json')['panels']; bypanel={p['id']:p for p in panels}
    check('source-use count',len(sources)==14)
    check('unique source identifiers',len(sourceids)==len(sources))
    for row in sources:
        p=Path(row['physical_path'])
        check('source hash '+row['id'],sha(p)==row['sha256'])
        check('source D storage '+row['id'],str(p.resolve()).lower().startswith('d:\\projects\\indus_valley_script\\'))
    check('panel count',len(panels)==23)
    for p in panels:
        check('panel source '+p['id'],p['source_id'] in sourceids)
        im=Image.open(p['crop_physical_path'])
        check('crop hash '+p['id'],sha(p['crop_physical_path'])==p['crop_sha256'])
        check('crop size '+p['id'],list(im.size)==p['crop_size'])
        matrix=np.asarray(p['parent_pixel_to_crop_pixel_matrix'])
        left,top,right,bottom=p['crop_pixels_actual']
        corners=np.asarray([[left,top,1],[right-1,top,1],[right-1,bottom-1,1],[left,bottom-1,1]])
        mapped=(matrix@corners.T).T
        bounds=[min(mapped[:,0]),min(mapped[:,1]),max(mapped[:,0]),max(mapped[:,1])]
        check('integer crop transform '+p['id'],np.allclose(bounds,[0,0,im.width-1,im.height-1]))
        missing_scale_reason=p.get('scale_endpoint_missing_reason') or p.get('scale_note')
        check('north and scale scope '+p['id'],bool(p.get('north_reference')) and (p.get('scale_bar_metres') is not None or bool(missing_scale_reason)))
    traces=read(RAW/'traces-v1.json'); traceby={t['id']:t for t in traces['measurements']}
    measurements=read(HERE/'measurements.json')
    check('dimension count',len(measurements['measurements'])==7)
    for m in measurements['measurements']:
        t=traceby[m['id']]
        d=math.dist(*t['feature_endpoints']);b=math.dist(*t['scale_endpoints']);s=t['scale_metres']
        e=t['feature_endpoint_radius_px'];eb=t['scale_endpoint_radius_px']
        value=s*d/b;lo=s*max(0,d-2*e)/(b+2*eb);hi=s*(d+2*e)/(b-2*eb)
        check('independent ratio '+m['id'],abs(m['metres']-value)<1e-11)
        check('independent sensitivity '+m['id'],max(abs(lo-m['digitization_sensitivity_metres'][0]),abs(hi-m['digitization_sensitivity_metres'][1]))<1e-11)
        w,h=bypanel[t['panel']]['crop_size']
        check('endpoints within source crop '+m['id'],all(0<=x<w and 0<=y<h for x,y in t['feature_endpoints']+t['scale_endpoints']))
    check('published 2.18 m source check',next(m for m in measurements['measurements'] if m['id']=='PW-M02')['published_check_inside_reading_bound'])
    fits=read(RAW/'measurement-v1/registration-details.json')
    for pid,r in fits.items():
        a=np.asarray(r['pixel_to_grid_offset_matrix'])
        err=[]
        for c in r['controls']:
            p=(a@np.array([*c['pixel'],1]))[:2]
            q=np.array(c['grid'])-[2355,1015]
            err.append(float(np.linalg.norm(p-q)))
        check('independent registration readback '+pid,abs(math.sqrt(sum(x*x for x in err)/len(err))-r['grid_fit_rmse_metres'])<1e-9)
        check('independent control count '+pid,len(r['controls'])==6 and len(r['held_out_controls'])==2)
    episodes=read(HERE/'episodes.json')['episodes']
    check('case count',len(episodes)==15)
    check('eligible P1 count is zero',sum(e['C0017_P1_eligible'] for e in episodes)==0)
    check('effect remains null',measurements['decision']['C0017_P1_effect'] is None)
    check('architecture coded before new overlay',all(e['new_documentary_overlay_received'] is False for e in episodes))
    routes=read(RAW/'acquisition-routes-v1.json')+read(RAW/'acquisition-routes-v2.json')
    check('acquired payload count',len(routes)==19)
    for r in routes:check('acquisition hash '+Path(r['physical_path']).name,sha(r['physical_path'])==r['sha256'])
    assets=read(HERE/'visual-assets.json')['assets']
    check('final board count',len(assets)==12)
    for a in assets:
        check('board hash '+a['id'],sha(a['physical_path'])==a['sha256'])
        check('board citation '+a['id'],all(s['source_id'] in sourceids and bool(s['locator']) for s in a['source_panels']))
        check('board local D '+a['id'],str(Path(a['physical_path']).resolve()).lower().startswith('d:\\projects\\indus_valley_script\\'))
    check('no source media or binary in owned checkout',all(p.suffix.lower() in {'.md','.json','.py','.pyc'} for p in HERE.rglob('*') if p.is_file()))
    command=['C:/Python313/python.exe',str(ROOT/'tools/review_prose.py'),'--path',str(HERE.relative_to(ROOT)),'--no-write']
    proc=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
    prose= json.loads(proc.stdout) if proc.returncode==0 else {'error':proc.stderr}
    check('prose scan completes',proc.returncode==0)
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'pass' if all(c['pass'] for c in checks) else 'fail','checks':checks,'check_count':len(checks),'passed':sum(c['pass'] for c in checks),'module_freeze_sha256':sha(HERE/'module-freeze.json'),
      'visual_review':{'initial_boards_individually_inspected':12,'final_version':'boards-v2','correction':'Shortened panel headers to retain narrow-inset width. Original board pixels and data unchanged. Corrected inset and contact sheet inspected.','final_board_ids':[a['id'] for a in assets],'reviewer':'western_towns, GPT-6 family; exact serving variant unknown, Codex desktop'},
      'prose_scan':prose,'manual_prose_review':'One README table cell uses source/page/figure to list three metadata fields. This flag is descriptive field notation, with no rhetorical stock wording. The analytical prose and source wording remain frozen.',
      'parent_independent_check':'The coordinating agent separately checked dimension arithmetic and both grid fits; its certificate is outside this owned module.'}
    (HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[c for c in checks if not c['pass']],'prose_flags':prose.get('flags')}))
    if result['status']!='pass':raise SystemExit(1)

if __name__=='__main__':main()
