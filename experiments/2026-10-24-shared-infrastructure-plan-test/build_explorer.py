"""Make a self-contained local gallery; no tiles, remote assets or cloud upload."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
from PIL import Image

P=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')

HTML='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shared infrastructure | plan and context explorer</title>
<style>
:root{--ink:#193337;--teal:#207d82;--paper:#f6f4ef;--line:#d7dedb;--rust:#ad5139}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Arial,sans-serif}
header{padding:44px max(5vw,24px) 28px;background:#173c41;color:white}header p{max-width:900px;color:#d3e4e2;margin:8px 0}h1{font-size:clamp(28px,4vw,44px);line-height:1.15;margin:12px 0}h2{line-height:1.25}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:2px}
nav{padding:18px max(5vw,24px);border-bottom:1px solid var(--line);display:flex;gap:16px;flex-wrap:wrap;align-items:center;background:white;position:sticky;top:0;z-index:5}
label{font-size:13px;font-weight:bold}select,input[type=search]{margin-left:7px;padding:9px 12px;color:var(--ink);border:1px solid #a8bab7;border-radius:5px;background:white;font:inherit;max-width:220px}#count{margin-left:auto;font-size:13px;color:#506765}
main{padding:30px max(5vw,24px)}.intro{max-width:1000px;margin:0 0 28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:25px}.card{background:white;border:1px solid var(--line);border-radius:7px;overflow:hidden;box-shadow:0 4px 14px #19333709}.card button{display:block;width:100%;border:0;padding:0;background:#eef2ef;cursor:zoom-in}.card img{width:100%;aspect-ratio:1.56;object-fit:contain;display:block}.card .body{padding:18px 20px 24px}.card h2{font-size:20px;margin:6px 0 12px}.tag{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--teal);font-weight:bold}.card p{font-size:14px;margin:8px 0}.source{font-size:12px!important;color:#536a6b}footer{padding:30px max(5vw,24px);font-size:13px;border-top:1px solid var(--line)}button,select,input{outline-offset:4px}
dialog{padding:0;border:0;border-radius:8px;width:96vw;max-width:1700px;height:94vh;background:var(--paper);color:var(--ink)}dialog::backdrop{background:#102729d9}.viewer-head{display:flex;gap:18px;align-items:center;padding:12px 20px;background:white;border-bottom:1px solid var(--line)}.viewer-head h2{font-size:18px;margin:0;flex:1}.viewer-head button{padding:8px 14px;border:1px solid #9eb4b1;border-radius:4px;background:white;cursor:pointer}.viewer-head label{white-space:nowrap}.viewer-image{height:calc(100% - 200px);overflow:auto;text-align:center;padding:12px;background:#dfe6e2}.viewer-image img{display:block;margin:auto;height:auto;max-width:none;min-width:300px}.viewer-note{padding:12px 20px;height:125px;overflow:auto;font-size:14px}.viewer-note p{margin:2px 0}.viewer-note .source{margin-top:7px}
@media(max-width:600px){nav{position:static;gap:10px}select{max-width:155px}.grid{grid-template-columns:1fr}.viewer-head{flex-wrap:wrap}.viewer-image{height:calc(100% - 245px)}}
@media print{nav,dialog{display:none}header{background:white;color:#193337}header p{color:#193337}.grid{display:block}.card{break-inside:avoid;margin:20px 0;box-shadow:none}.card img{aspect-ratio:auto;max-height:70vh}.card button{background:white}}
</style></head><body>
<header><div class="eyebrow">Indus research project · 24 October 2026 · local edition</div>
<h1>Shared infrastructure against excavation evidence</h1>
<p>Explore the actual plan evidence, new measurements, dated contexts and counterexamples. Open a figure to inspect its source detail and annotations.</p></header>
<nav aria-label="Figure filters"><label>Town<select id="town"><option value="all">All towns</option></select></label><label>Evidence<select id="kind"><option value="all">All evidence</option></select></label><label>Find<input id="search" type="search" placeholder="Feature or source"></label><span id="count" aria-live="polite"></span></nav>
<main><p class="intro">The figures distinguish observed architecture, scoped readings, proposed explanations and missing joins. A narrowed route can remain connected; a closed building entrance does not close an entire lane. Plan blanks and unreported finds remain unknown. Dates retain their relationship to the sampled deposit.</p><div class="grid" id="grid"></div></main>
<footer>All display imagery is embedded in this local file. Full-resolution figures remain in the companion atlas archive and illustrated PDF. There are no external map tiles, scripts, fonts, analytics or network requests. Attributed excavation plans retain their source terms. This exploratory study supplies no fresh confirmation score.</footer>
<dialog id="viewer"><div class="viewer-head"><h2 id="view-title"></h2><label>Zoom <input id="zoom" type="range" min="70" max="300" value="100"> <span id="zoom-label">100%</span></label><button id="close">Close</button></div><div class="viewer-image" id="viewport"><img id="view-img" alt=""></div><div class="viewer-note"><p id="view-caption"></p><p class="source" id="view-source"></p></div></dialog>
<script id="figures-data" type="application/json">__DATA__</script>
<script>
'use strict';
const figures=JSON.parse(document.getElementById('figures-data').textContent),byId=new Map(figures.map(f=>[f.id,f]));
const el=id=>document.getElementById(id), town=el('town'),kind=el('kind'),search=el('search'),grid=el('grid'),viewer=el('viewer');
const townNames={harappa:'Harappa',dholavira:'Dholavira',lothal:'Lothal',farmana:'Farmana',kanmer:'Kanmer',banawali:'Banawali','mohenjo-daro':'Mohenjo-daro'};
for(const value of [...new Set(figures.flatMap(f=>f.towns||[]))].sort()){const o=document.createElement('option');o.value=value;o.textContent=townNames[value]||value;town.add(o)}
for(const value of [...new Set(figures.map(f=>f.kind||'evidence'))].sort()){const o=document.createElement('option');o.value=value;o.textContent=value;kind.add(o)}
function render(){const q=search.value.toLowerCase();const selected=figures.filter(f=>(town.value==='all'||(f.towns||[]).includes(town.value))&&(kind.value==='all'||f.kind===kind.value)&&(!q||[f.title,f.caption,f.source_note].join(' ').toLowerCase().includes(q)));grid.replaceChildren();for(const f of selected){const card=document.createElement('article');card.className='card';const b=document.createElement('button');b.type='button';b.setAttribute('aria-label','Inspect '+f.title);b.addEventListener('click',()=>show(f.id));const im=document.createElement('img');im.src=f.image;im.alt=f.title;im.loading='lazy';b.append(im);const body=document.createElement('div');body.className='body';const tag=document.createElement('div');tag.className='tag';tag.textContent='Figure '+f.figure+' · '+f.kind;const h=document.createElement('h2');h.textContent=f.title;const p=document.createElement('p');p.textContent=f.caption;const s=document.createElement('p');s.className='source';s.textContent=f.source_note;body.append(tag,h,p,s);card.append(b,body);grid.append(card)}el('count').textContent=selected.length+' of '+figures.length+' figures'}
function zoom(){el('view-img').style.width=el('zoom').value+'%';el('zoom-label').textContent=el('zoom').value+'%'}
function show(id){const f=byId.get(id);el('view-title').textContent='Figure '+f.figure+'. '+f.title;el('view-img').src=f.image;el('view-img').alt=f.title;el('view-caption').textContent=f.caption;el('view-source').textContent=f.source_note;el('zoom').value=100;zoom();viewer.showModal();el('viewport').scrollTo(0,0)}
town.addEventListener('change',render);kind.addEventListener('change',render);search.addEventListener('input',render);el('zoom').addEventListener('input',zoom);el('close').addEventListener('click',()=>viewer.close());viewer.addEventListener('click',e=>{if(e.target===viewer)viewer.close()});render();
</script></body></html>'''


def main(manifest,out,tag,web_optimized=False):
    if out.exists() or (P/f'explorer-manifest-{tag}.json').exists():
        raise FileExistsError('Preserve the explorer endpoint.')
    assert out.resolve().is_relative_to(RAW.resolve())
    records=json.loads(manifest.read_text(encoding='utf-8'))['figures']
    out.parent.mkdir(parents=True,exist_ok=False)
    if web_optimized:(out.parent/'display-images').mkdir()
    data=[]
    derivatives=[]
    for row in records:
        path=Path(row['physical_path']);raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        mime='image/png'
        if web_optimized:
            image=Image.open(path).convert('RGB');original_size=list(image.size)
            image.thumbnail((1800,1800))
            display=out.parent/'display-images'/(row['id']+'.jpg')
            image.save(display,format='JPEG',quality=85,subsampling=0,optimize=True)
            raw=display.read_bytes();mime='image/jpeg'
            derivatives.append({'id':row['id'],'source_sha256':row['sha256'],
                                'physical_path':str(display),'sha256':hashlib.sha256(raw).hexdigest(),
                                'original_pixels':original_size,'display_pixels':list(image.size),
                                'operation':'Uniform thumbnail, maximum1800px; JPEGquality85, no chroma subsampling. No scientific line or value edited.'})
        r={k:row.get(k) for k in ['id','figure','title','caption','source_note','towns','kind']}
        r['image']='data:'+mime+';base64,'+base64.b64encode(raw).decode('ascii')
        data.append(r)
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    out.write_text(HTML.replace('__DATA__',payload),encoding='utf-8')
    record={'physical_path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,
            'figures':len(records),'embedded_images':len(data),'external_assets':0,'local_only':True,
            'source_manifest':str(manifest),'source_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'web_optimized':web_optimized,'display_derivatives':derivatives}
    (P/f'explorer-manifest-{tag}.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--tag',required=True)
    parser.add_argument('--web-optimized',action='store_true')
    args=parser.parse_args();main(args.manifest,args.out,args.tag,args.web_optimized)
