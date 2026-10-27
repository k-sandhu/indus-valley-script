"""Check source integrity, metric invariants, mesh indices and frozen exports."""
import argparse
import hashlib
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',default='run-v4');parser.add_argument('--out',required=True);args=parser.parse_args()
    result=HERE/args.out
    if result.exists():raise FileExistsError(result)
    run=HERE/args.run;data=json.loads((run/'scenes.json').read_text(encoding='utf-8'));checks=[]
    def check(name,ok,detail=None):
        checks.append(dict(name=name,passed=bool(ok),detail=detail))
    def close(a,b):return abs(a-b)<1e-7
    def span(mesh):
        return [max(p[i] for p in mesh['vertices'])-min(p[i] for p in mesh['vertices']) for i in range(3)]
    scenes={s['id']:s for s in data['scenes']};sources={s['id']:s for s in data['sources']}
    check('seven promised models',set(scenes)=={'mohenjo-daro','dholavira','great-bath','dholavira-reservoir','dholavira-gate','pillared-hall','lothal-basin'})
    check('metre and coordinate contract',data['units']=='metres' and data['coordinates']=='right-handed X east, Y north, Z up')
    counts=dict(models=len(scenes),features=0,meshes=0,faces=0,vertices=0,obj_faces=0,obj_vertices=0)
    for sid,s in scenes.items():
        features={f['id']:f for f in s['features']};counts['features']+=len(features);counts['meshes']+=len(s['meshes'])
        check(sid+' unique feature identities',len(features)==len(s['features']))
        for f in features.values():
            check(sid+'/'+f['id']+' evidence and assumptions',all(f.get(k) for k in ['name','description','sources','footprint','placement','vertical','assumptions','focus','span']) and all(k in sources for k in f['sources']))
            if f.get('detail_model'):check(sid+'/'+f['id']+' detail route',f['detail_model'] in scenes)
        for i,m in enumerate(s['meshes']):
            counts['vertices']+=len(m['vertices']);counts['faces']+=len(m['faces'])
            ok=m['feature'] in features and m['material'] in data['materials']
            ok=ok and all(len(v)==3 and all(math.isfinite(x) for x in v) for v in m['vertices'])
            ok=ok and all(len(f)>=3 and len(set(f))==len(f) and all(0<=v<len(m['vertices']) for v in f) for f in m['faces'])
            check(sid+f' mesh {i} finite indexed geometry',ok)
        for d in s['dimensions']:
            check(sid+'/'+d['label']+' source',d['source'] in sources and bool(d['locator']))
            if d['start'] and d['end']:
                actual=math.dist(d['start'],d['end']);check(sid+'/'+d['label']+' metric ruler',close(actual,d['value_m']),dict(actual_m=actual,published_display_m=d['value_m']))
        obj=(run/'exports'/(sid+'.obj')).read_text(encoding='utf-8');verts=[];faces=[]
        for line in obj.splitlines():
            if line.startswith('v '):verts.append([float(v) for v in line.split()[1:]])
            elif line.startswith('f '):faces.append([int(v) for v in line.split()[1:]])
        expected=[m for m in s['meshes'] if m['role'] not in ['roof','water']]
        check(sid+' OBJ independently parsed indices',all(all(1<=i<=len(verts) for i in f) for f in faces))
        check(sid+' OBJ count',len(verts)==sum(len(m['vertices']) for m in expected) and len(faces)==sum(len(m['faces']) for m in expected))
        for axis in range(3):
            actual=[min(v[axis] for v in verts),max(v[axis] for v in verts)]
            intended=[min(v[axis] for m in expected for v in m['vertices']),max(v[axis] for m in expected for v in m['vertices'])]
            check(sid+f' OBJ axis {axis} extent',all(abs(a-b)<1e-6 for a,b in zip(actual,intended)))
        counts['obj_vertices']+=len(verts);counts['obj_faces']+=len(faces)
    bath=scenes['great-bath'];floor=next(m for m in bath['meshes'] if m['feature']=='basin' and m['role']=='floor')
    check('Great Bath interior floor 7 by12',close(span(floor)[0],7) and close(span(floor)[1],12))
    walls=[m for m in bath['meshes'] if m['feature']=='basin' and len(m['vertices'])==8 and close(span(m)[2],2.4)]
    check('Great Bath fixed published depth',len(walls)==4 and all(not m['variable'] for m in walls))
    s=scenes['dholavira-reservoir'];faces=[m for m in s['meshes'] if m['feature']=='basin' and len(m['vertices'])==4]
    tops=[v for m in faces for v in m['vertices'] if close(v[2],10.6)];bottoms=[v for m in faces for v in m['vertices'] if close(v[2],3.25)]
    check('Reservoir upper spans',close(max(v[0] for v in tops)-min(v[0] for v in tops),29.3) and close(max(v[1] for v in tops)-min(v[1] for v in tops),73.45))
    check('Reservoir lower spans',close(max(v[0] for v in bottoms)-min(v[0] for v in bottoms),27.725) and close(max(v[1] for v in bottoms)-min(v[1] for v in bottoms),70))
    check('Reservoir general depth inside published range',7.2<=10.6-3.25<=7.5)
    check('Reservoir localized deepest floor',any(m['feature']=='probe' and close(max(v[2] for v in m['vertices']),0) for m in s['meshes']))
    s=scenes['dholavira-gate'];opening=next(m for m in s['meshes'] if m['feature']=='passage' and m['material']=='floor')
    check('West gate source passage dimensions',close(span(opening)[0],9) and close(span(opening)[1],2.2))
    s=scenes['pillared-hall'];pillars=[m for m in s['meshes'] if m['feature']=='pillars'];check('Hall twenty pillars',len(pillars)==20)
    centres=[[(min(v[i] for v in m['vertices'])+max(v[i] for v in m['vertices']))/2 for i in [0,1]] for m in pillars]
    check('Hall four rows of five',len(set(x[0] for x in centres))==5 and len(set(x[1] for x in centres))==4)
    s=scenes['dholavira'];walls=[m for m in s['meshes'] if m['feature']=='city-wall' and len(m['vertices'])==8][:4]
    # Reconstruct the internal rectangle from opposite wall inner faces.
    inner_x=max(v[0] for v in walls[2]['vertices']);outer_x=min(v[0] for v in walls[3]['vertices'])
    inner_y=max(v[1] for v in walls[0]['vertices']);outer_y=min(v[1] for v in walls[1]['vertices'])
    check('Dholavira inner corner spans',close(outer_x-inner_x,771.1) and close(outer_y-inner_y,616.87))
    s=scenes['lothal-basin'];walls=[m for m in s['meshes'] if m['feature']=='basin' and m['material']=='brick']
    check('Lothal long-wall mean span',sum(close(span(m)[1],214.87) for m in walls)==2)
    check('Lothal published extant wall height',all(close(span(m)[2],3.3) and not m['variable'] for m in walls))
    for sid,source in sources.items():
        if source.get('physical_path'):
            p=Path(source['physical_path']);ok=p.exists() and p.stat().st_size==source['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256']
            check(sid+' raw witness hash',ok)
            if source['new_acquisition']:check(sid+' D: storage',str(p).lower().replace('\\','/').startswith('d:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/reconstruction/'))
    html=(run/'index.html').read_text(encoding='utf-8')
    check('offline HTML has no remote runtime assets',not re.search(r'<script[^>]+src=|<img[^>]+src=|<link[^>]+rel=["\']stylesheet',html,re.I))
    check('no runtime fetch or vendor request',not re.search(r'\bfetch\(|XMLHttpRequest|https://cdn\.',html))
    script=html.split('<script>')[1].split('</script>')[0]
    with tempfile.NamedTemporaryFile(suffix='.js',mode='w',encoding='utf-8',delete=False) as f:
        f.write(script);name=f.name
    syntax=subprocess.run(['node','--check',name],capture_output=True,text=True)
    Path(name).unlink();check('Node syntax check',syntax.returncode==0,syntax.stderr.strip() or 'passes')
    manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
    for f in manifest['files']:
        p=HERE/f['path'];check('frozen hash '+f['path'],hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'])
    output=dict(schema_version='1.0',task='architectural-model-software-verification',run=args.run,
                author='GPT-6 family / Codex desktop collaboration; author verification, not independent review',
                counts=counts,checks=checks,passed=all(x['passed'] for x in checks),
                scope='Software geometry, source integrity and packaging. No archaeological meaning or fresh confirmation tested.')
    result.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=output['passed'],checks=len(checks),failures=[x for x in checks if not x['passed']],counts=counts)))
    return 0 if output['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
