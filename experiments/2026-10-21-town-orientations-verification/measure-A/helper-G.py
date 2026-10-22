"""Measurer A Gujarat: owned-path orchestration; no architecture is auto-selected."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, json, shutil, datetime, subprocess, hashlib
ROOT = Path.cwd()
PKG = ROOT/'experiments/2026-10-21-town-orientations-verification'
OWN = PKG/'measure-A'
RAW = ROOT/'data/raw/2026-10-21-town-orientations-verification/measure-A'
TOOLS = PKG/'tools'
sys.path.insert(0, str(TOOLS))
from common import read_json, write_json
from render_image import render as image_render
from render_plan import render as plan_render, page_image
from measure_lines import measure
from PIL import Image, ImageDraw

def fresh_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(str(path), obj)

def free():
    n=shutil.disk_usage(ROOT).free
    if n<1_000_000_000: raise RuntimeError(f'Free space below 1 GB: {n}')
    return n

def start(slug):
    sites=read_json(PKG/'infra-v1/sites-located-v1.json')
    im=read_json(PKG/'infra-v1/imagery-manifest-v1.json')
    pl=read_json(PKG/'infra-v1/plan-library-v1.json')
    s=next(x for x in sites['sites'] if x['slug']==slug)
    i=next((x for x in im['towns'] if x['slug']==slug),None)
    p=next((x for x in pl['towns'] if x['slug']==slug),None)
    snapshot=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_bytes=free(),site=s,imagery=i,plans=p)
    fresh_json(OWN/'picks'/slug/'source-index-G-v1.json',snapshot)
    print(json.dumps(dict(slug=slug,coordinate=s['coordinate_used'],imagery_status=i.get('status') if i else None,plans=p),ensure_ascii=False))
    if i and i.get('composite'):
        source=i['composite']['path']; point=s['coordinate_used']; directory=RAW/slug
        files=[]
        for size,up in [(2000,4),(800,10)]:
            for layer,edge in [('RGB',False),('NIR',False),('brightness',False),('brightness',True)]:
                free(); name=f'{size}-{layer}{"-edge" if edge else ""}-G-v1.png'; dest=directory/name
                image_render(source,str(dest),point,size,layer,up,100 if size==800 else 250,edge)
                files.append(dest)
        sheet=Image.new('RGB',(1600,850),'white');d=ImageDraw.Draw(sheet)
        for j,f in enumerate(files):
            image=Image.open(f);image.thumbnail((400,400)); x=(j%4)*400;y=(j//4)*425
            sheet.paste(image,(x,y+25));d.text((x+5,y+5),f.name,fill='black')
        out=directory/'overview-G-v1.jpg'
        if out.exists():raise FileExistsError(out)
        sheet.save(out,quality=90)
        print(out)

def renderplan(slug,planid,tag,dpi,region):
    snap=read_json(OWN/'picks'/slug/'source-index-G-v1.json')
    plan=next(p for p in snap['plans']['plans'] if p['id']==planid)
    free();dest=RAW/slug/f'{tag}.png'
    plan_render(plan['local_source_path'],str(dest),plan['pdf_page'],dpi,region,100)
    print(dest)

def picked(slug,tag,render,config):
    obj=json.loads(config)
    pp=OWN/'picks'/slug/f'{tag}.json';fresh_json(pp,obj)
    out=OWN/'picks'/slug/f'{tag}-refined.json';result=measure(obj,str(RAW/slug/f'{render}.png.json'));fresh_json(out,result)
    # A fresh unmarked source render, followed by fitted lines, keeps the source
    # grid and all original pixels. This is a verification display, not a pick image.
    side=read_json(RAW/slug/f'{render}.png.json');overlay=RAW/slug/f'{tag}-check.png'
    if side['kind']=='plan':
        plan_render(side['source'],str(overlay),side['page'],side['dpi'],side.get('region'),100)
    else:
        # Retain original display and its exact dimensions for pixel overlay.
        image=Image.open(RAW/slug/f'{render}.png').convert('RGB')
        if overlay.exists():raise FileExistsError(overlay)
        image.save(overlay)
    image=Image.open(overlay).convert('RGB');d=ImageDraw.Draw(image)
    for line in result['lines']:
        ends=line['refined_endpoints_px'];d.line([tuple(e) for e in ends],fill='red',width=2);d.text(tuple(ends[0]),line['id'],fill='red',stroke_width=1,stroke_fill='white')
    if result['arrow']:
        d.line([tuple(e) for e in result['arrow']['refined_endpoints_px']],fill='green',width=2)
    # Never overwrite the new render: save marked verification separately.
    marked=RAW/slug/f'{tag}-check-marked.png'
    if marked.exists():raise FileExistsError(marked)
    image.save(marked)
    print(json.dumps(dict(file=str(out),arrow=result['arrow'],lines=[{k:v for k,v in x.items() if k in ['id','theta_deg','sigma_deg','length_m','inlier_count','profile_count','residual_rms_px','refined_endpoints_px','warnings']} for x in result['lines']]),ensure_ascii=False))

def finish(slug,config):
    spec=json.loads(config);snap=read_json(OWN/'picks'/slug/'source-index-G-v1.json');s=snap['site'];i=snap['imagery'];pl=snap['plans']
    sources=[];lines=[]
    if i and i.get('composite'):
        sources.append(dict(id='imagery',kind='imagery',scene_ids=i.get('composite_scene_ids',[]),scene_datetimes=[x['datetime'] for x in i['scenes'] if x.get('used_in_composite')],manifest_path=str(PKG/'infra-v1/imagery-manifest-v1.json'),composite=i['composite'],assessment=spec['imagery_assessment']))
    for tag in spec.get('measurements',[]):
        res=read_json(OWN/'picks'/slug/f'{tag}-refined.json')
        for line in res['lines']:
            line['source_id']=res['source_id'];line['measurement_record']=str(OWN/'picks'/slug/f'{tag}-refined.json');lines.append(line)
        if res['kind']=='plan':
            p=next(p for p in pl['plans'] if p['id']==res['source_id'])
            sources.append(dict(id=p['id'],kind='plan',citation=p['citation'],pdf_page=p['pdf_page'],printed_page=p['printed_page'],figure=p['figure_or_plate'],source_record=p['source'],north_class=res['north']['class'],north_evidence=res['north']['evidence'],survey_year=res['north'].get('survey_year'),north=res['north'],arrow=res['arrow'],measurement_record=str(OWN/'picks'/slug/f'{tag}-refined.json')))
    for p in (pl or {}).get('plans',[]):
        if not any(x['id']==p['id'] for x in sources):
            sources.append(dict(id=p['id'],kind='plan',citation=p['citation'],pdf_page=p['pdf_page'],printed_page=p['printed_page'],figure=p['figure_or_plate'],source_record=p['source'],assessment=spec.get('plan_assessment','Inspected; no qualifying measurable lines selected.')))
    town=dict(schema_version=1,slug=slug,measurer='A',authors=[dict(model='GPT-6',harness='Codex API')],located_point=dict(latitude=spec.get('point',s['coordinate_used'])[0],longitude=spec.get('point',s['coordinate_used'])[1],method=spec['location_method']),sources=sources,lines=lines,registrations=spec.get('registrations',[]),notes=spec['notes'],unmeasurable_reason=spec.get('unmeasurable_reason'),imagery_assessment=spec['imagery_assessment'],plan_assessment=spec.get('plan_assessment'),empirical_error_calibration=dict(source='infra-v1/validation-v1/summary.json',segment_rms_deg={'100m':4.272758,'200m':1.764927,'300m':.988215,'400m':.746483},sigma_policy='Tool sigma retained unchanged; calibration is separate.'))
    inp=OWN/'picks'/slug/'town-input-G-v1.json';fresh_json(inp,town)
    dest=OWN/'towns'/f'{slug}.json'
    subprocess.run([sys.executable,'-I',str(TOOLS/'systems.py'),str(inp),str(dest),'--summary',str(OWN/'summary-G.csv')],check=True)
    print(dest)

parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
p=sub.add_parser('start');p.add_argument('slug')
p=sub.add_parser('plan');p.add_argument('slug');p.add_argument('planid');p.add_argument('tag');p.add_argument('--dpi',type=int,default=144);p.add_argument('--region',type=float,nargs=4)
p=sub.add_parser('pick');p.add_argument('slug');p.add_argument('tag');p.add_argument('render');p.add_argument('config')
p=sub.add_parser('finish');p.add_argument('slug');p.add_argument('config')
a=parser.parse_args()
if a.action=='start':start(a.slug)
elif a.action=='plan':renderplan(a.slug,a.planid,a.tag,a.dpi,a.region)
elif a.action=='pick':picked(a.slug,a.tag,a.render,a.config)
elif a.action=='finish':finish(a.slug,a.config)
