"""Render a local-only projection to an exclusive standalone HTML endpoint."""
import argparse, json, html, hashlib, re
from pathlib import Path
from urllib.parse import urlparse

def esc(x):return html.escape(str(x),quote=True)
def display(x):return json.dumps(x,ensure_ascii=False,indent=2) if isinstance(x,(dict,list)) else str(x)
def uri(value):
 s=str(value)
 if s.startswith(('https://','http://')):return s
 p=Path(s)
 if not p.is_absolute():p=Path(__file__).resolve().parents[2]/p
 return p.resolve().as_uri()
def render(data):
 sources={x['source_ref']:x for x in data.get('source_catalogue',[])}
 def link(ref,locator=None):
  source=sources.get(ref,{})
  dest=source.get('physical_path') or source.get('url') or ref
  if not str(dest).startswith(('http://','https://')) and not Path(dest).is_absolute():
   return esc(ref)
  label=source.get('title') or Path(ref).name
  coord=' · '+display(locator) if locator else ''
  return f'<a href="{esc(uri(dest))}" title="{esc(dest)}">{esc(label)}</a>{esc(coord)}'
 cards=[]
 for o in data['objects']:
  t=o['record_id'];rows=[]
  for a in o['assertions']:
   refs='<br>'.join(link(r) for r in a['source_refs'])
   rows.append(f'<tr><th>{esc(a["field"])}</th><td><pre>{esc(display(a["value"]))}</pre><span class="status">{esc(a["status"])}</span></td><td>{refs}<pre class="coordinates">{esc(display(a.get("locator",{})))}</pre></td></tr>')
  pictures=[]
  for image in o.get('images',[]):
   path=image.get('path');label=image.get('kind','indexed image')
   image_sources='<br>'.join(link(ref) for ref in image.get('source_refs',[]))
   coordinates={k:image[k] for k in ['pdf_page','printed_page','panel','locator','coverage_class','binding_status','image_scope','side_match'] if k in image}
   if path and Path(path).suffix.lower() in ['.png','.jpg','.jpeg','.webp']:
    pictures.append(f'<figure><a href="{esc(uri(path))}"><img loading="lazy" src="{esc(uri(path))}" alt="{esc(t+": "+label)}"></a><figcaption>{esc(label)}<pre>{esc(display(coordinates))}</pre><a href="{esc(uri(path))}">{esc(path)}</a><p>{image_sources}</p></figcaption></figure>')
   else:pictures.append(f'<p>{esc(label)} {esc(display(coordinates))}<br>{image_sources}</p>')
  aliases=', '.join(f'{a.get("scheme", "alias")}: {a.get("value", "")}' for a in o.get('aliases',[]))
  candidates=o.get('candidate_family_ids',[])
  identity=f'{len(candidates)} candidate corpus families' if candidates else o.get('identity_status','unspecified')
  search=esc((t+' '+o['site']+' '+aliases+' '+display(o.get('assertions',[]))).lower())
  cards.append(f'''<article data-site="{esc(o['site'])}" data-search="{search}" id="{esc(t)}">
<h2>{esc(t)} <span>{esc(o['site'])}</span></h2><p class="identity">{esc(identity)} · Physical merge accepted: {esc(o.get('accepted_physical_merge',False))}</p>
<p>{esc(aliases)}</p><p><strong>Missing evidence:</strong> {esc(', '.join(o['missing_fields']))}</p>
<details><summary>Candidate family IDs and retained conflicts</summary><p>{esc(', '.join(candidates) or 'No candidate set assigned')}</p><pre>{esc(display(o.get('conflicts',[])))}</pre></details>
<div class="images">{''.join(pictures) or '<p>No linked local image in this projection.</p>'}</div>
<details><summary>{len(rows)} source assertions and coordinates</summary><table><thead><tr><th>Field</th><th>Value and status</th><th>Sources and coordinates</th></tr></thead><tbody>{''.join(rows)}</tbody></table></details></article>''')
 return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Twenty-target object register</title><style>
body{font:16px/1.55 system-ui,sans-serif;background:#f2f0e9;color:#172522;margin:0}header,main{max-width:1250px;margin:auto;padding:1.5rem}header{padding-bottom:0}h1{font-size:2rem}h2{margin:0}h2 span{font-size:1rem;color:#52675f;font-weight:400}nav{display:flex;gap:1rem;flex-wrap:wrap;position:sticky;top:0;background:#f2f0e9;padding:1rem 0;z-index:2}input,select{font:inherit;padding:.5rem;border:1px solid #87968e;border-radius:4px}input{width:min(600px,90%)}article{background:white;padding:1.25rem;margin-bottom:1.5rem;border:1px solid #c7d0c7;border-radius:8px}.identity{color:#5b4421}details{margin:.8rem 0}summary{cursor:pointer;font-weight:600}table{width:100%;border-collapse:collapse;table-layout:fixed}th,td{border-bottom:1px solid #d3dad4;text-align:left;vertical-align:top;padding:.6rem;overflow-wrap:anywhere}th:first-child{width:20%}pre{white-space:pre-wrap;font:13px/1.4 ui-monospace,monospace;margin:.3rem 0;overflow-wrap:anywhere}.status{background:#eee9dc;padding:.1rem .35rem;font-size:.8rem}.coordinates{color:#425d52}.images{display:flex;flex-wrap:wrap;gap:1rem;margin-top:1rem}figure{width:280px;margin:0}img{max-width:280px;max-height:300px;object-fit:contain;border:1px solid #d3dad4}figcaption{font-size:.8rem;overflow-wrap:anywhere}a{color:#135b70}article[hidden]{display:none}
</style><header><h1>Twenty-target object register</h1><p>We bring together the held metadata for ten Dholavira, five Harappa and five Lothal targets. The Dholavira accession records retain their candidate corpus families. Source assertions, their disagreements and the evidence still needed remain visible together. Whole-page images include the named panel and surrounding material.</p><p>Detailed data and images remain on this computer. Opening file links requires a local browser that permits local files.</p><nav><label>Site <select id="site"><option value="">All sites</option><option>Dholavira</option><option>Harappa</option><option>Lothal</option></select></label><input id="search" type="search" placeholder="Search identifiers, metadata or sources" aria-label="Search catalogue"><output id="count">20 targets</output></nav></header><main>'''+''.join(cards)+'''</main><script>
const cards=[...document.querySelectorAll('article')], site=document.querySelector('#site'), search=document.querySelector('#search');
function filter(){let n=0;for(const c of cards){c.hidden=!!((site.value&&c.dataset.site!==site.value)||(search.value&&!c.dataset.search.includes(search.value.toLowerCase())));if(!c.hidden)n++}document.querySelector('#count').textContent=n+' targets'}
site.addEventListener('change',filter);search.addEventListener('input',filter);
</script></html>'''

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
 assert str(args.output.resolve()).lower().startswith('d:'),'Detailed HTML must be on D:'
 assert not args.output.exists(),'Use a new endpoint'
 data=json.loads(args.input.read_text(encoding='utf-8-sig'))
 assert len(data['objects'])==20 and len({o['record_id'] for o in data['objects']})==20
 page=render(data)
 with args.output.open('x',encoding='utf8') as f:f.write(page)
 print(json.dumps({'output':str(args.output.resolve()),'bytes':args.output.stat().st_size,'cards':page.count('<article '),'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))
