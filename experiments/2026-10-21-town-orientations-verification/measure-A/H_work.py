"""Measurer A, Haryana/Rajasthan share: rendering and audit helpers only."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, shutil, subprocess, datetime, argparse
from PIL import Image, ImageDraw

ROOT = Path.cwd()
PKG = ROOT / 'experiments/2026-10-21-town-orientations-verification'
OWN = PKG / 'measure-A'
RAW = ROOT / 'data/raw/2026-10-21-town-orientations-verification/measure-A'
sys.path.insert(0, str(PKG / 'tools'))
from render_image import render

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')

def space():
    free = shutil.disk_usage(ROOT).free
    if free < 1_000_000_000:
        raise RuntimeError(f'Less than 1 GB free: {free}')
    return free

def images(slug):
    # Refresh both mutable infrastructure indexes immediately before each town.
    m = read(PKG/'infra-v1/imagery-manifest-v1.json')
    l = read(PKG/'infra-v1/plan-library-v1.json')
    s = next(x for x in read(PKG/'infra-v1/sites-located-v1.json')['sites'] if x['slug']==slug)
    im = next((x for x in m['towns'] if x['slug']==slug), None)
    pl = next(x for x in l['towns'] if x['slug']==slug)
    snap = dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_bytes=space(),site=s,imagery=im,plans=pl)
    write(OWN/'picks'/slug/'infra-snapshot-v1.json', snap)
    print(slug, 'composite:', (im or {}).get('composite',{}).get('path'), 'plans:', [(p['id'],p['pdf_page']) for p in pl['plans']])
    if not im or not im.get('composite'):
        return
    panels=[]
    for size,up in [(1600,5),(700,10)]:
        for layer,edge in [('RGB',False),('brightness',False),('NIR',False),('brightness',True)]:
            space()
            dest=RAW/slug/f'{size}-{layer}{"-edge" if edge else ""}-v1.png'
            render(im['composite']['path'],dest,s['coordinate_used'],size,layer,up,100,edge)
            panels.append(dest)
    for k in range(2):
        tiles=panels[k*4:k*4+4]
        ims=[Image.open(p).convert('RGB') for p in tiles]
        w=max(i.width for i in ims);h=max(i.height for i in ims)
        sheet=Image.new('RGB',(w*2,(h+24)*2),'white');d=ImageDraw.Draw(sheet)
        for j,(i,p) in enumerate(zip(ims,tiles)):
            x=j%2*w;y=j//2*(h+24)
            sheet.paste(i,(x,y+24));d.text((x+4,y+4),p.name,fill='black')
        target=RAW/slug/f'contact-{k+1}-v1.png'
        if target.exists(): raise FileExistsError(target)
        sheet.save(target)

def overlay(png, result, out):
    if Path(out).exists(): raise FileExistsError(out)
    im=Image.open(png).convert('RGB');d=ImageDraw.Draw(im)
    r=read(result)
    for line in r['lines']:
        pts=line.get('refined_endpoints_px',line.get('endpoints_refined_px',line.get('endpoints_px')))
        d.line([tuple(x) for x in pts],fill='red',width=2)
        for p in pts: d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),outline='red',width=2)
        d.text(tuple(pts[0]),line['id'],fill='red',stroke_width=1,stroke_fill='white')
    im.save(out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['images','overlay']);p.add_argument('paths',nargs='+');a=p.parse_args()
    if a.action=='images': images(*a.paths)
    else: overlay(*a.paths)
