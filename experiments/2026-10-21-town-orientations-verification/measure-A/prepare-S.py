"""Make fresh permitted renders and preserve the current per-town source snapshot."""
import json, sys, subprocess, shutil
from pathlib import Path
base, owned, raw, slug = map(Path, sys.argv[1:5])
slug = str(slug)
def read(name, key):
    return next(r for r in json.loads((base / name).read_text(encoding='utf-8'))[key] if r['slug']==slug)
site=read('sites-located-v1.json','sites')
im=read('imagery-manifest-v1.json','towns')
pl=read('plan-library-v1.json','towns')
dest=raw/slug
dest.mkdir(parents=True,exist_ok=True)
picks=owned/'picks'/slug
picks.mkdir(parents=True,exist_ok=True)
snapshot=picks/'source-snapshot-v1.json'
with snapshot.open('x',encoding='utf-8') as f: json.dump(dict(site=site,imagery=im,plans=pl),f,indent=2)
tool=base.parent/'tools'
if im.get('composite'):
    for size in [2000,800]:
        for layer,edge in [('brightness',False),('RGB',False),('NIR',False),('brightness',True)]:
            if shutil.disk_usage('C:/').free<1073741824: raise RuntimeError('Below 1 GiB free')
            out=dest/f'{size}-{layer}{"-edge" if edge else ""}-v1.png'
            cmd=[sys.executable,'-I',str(tool/'render_image.py'),im['composite']['path'],str(out),'--point',*map(str,site['coordinate_used']),'--size',str(size),'--layer',layer,'--upsample','6' if size==800 else '3','--grid','100']
            if edge:cmd.append('--edge')
            subprocess.run(cmd,check=True)
for i,p in enumerate(pl.get('plans',[]),1):
    if shutil.disk_usage('C:/').free<1073741824: raise RuntimeError('Below 1 GiB free')
    subprocess.run([sys.executable,'-I',str(tool/'render_plan.py'),p['local_source_path'],str(dest/f'plan-{i}-v1.png'),'--page',str(p['pdf_page']),'--dpi','180','--grid','200'],check=True)
print(slug,'prepared',shutil.disk_usage('C:/').free)
