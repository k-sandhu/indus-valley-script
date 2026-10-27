"""Independent structural, link, hash and renderer checks; no source pixels read."""
import argparse, json, hashlib, re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
from render_catalogue import render

class Page(HTMLParser):
 def __init__(self):super().__init__();self.cards=0;self.files=[];self.remote=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='article':self.cards+=1;self.ids.add(a.get('id'))
  for key in ['href','src']:
   if key in a:
    u=urlparse(a[key])
    if u.scheme=='file':self.files.append(Path(unquote(u.path.lstrip('/'))))
    elif tag in ['script','img','link'] and u.scheme in ['http','https']:self.remote.append(a[key])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('projection',type=Path);a.add_argument('html',type=Path);a.add_argument('output',type=Path);x=a.parse_args()
 d=json.loads(x.projection.read_text(encoding='utf8'));objects=d['objects'];sources={s['source_ref']:s for s in d['source_catalogue']};page=Page();page.feed(x.html.read_text(encoding='utf8'))
 required={'record_id','site','aliases','assertions','images','missing_fields','candidate_family_ids','identity_status','accepted_physical_merge'}
 expected={f'PCF-DHV-{n:03}' for n in range(5,15)}|{'H-1657','H-2587','H-1688','H-1682','H-1692','L-164','L-163','L-167','L-146','L-174'}
 checks={
 'exact_twenty_target_frame':len(objects)==20 and {o['record_id'] for o in objects}==expected,
 'required_object_fields':all(required<=o.keys() for o in objects),
 'canonical_assertion_statuses':all(a['status'] in ['catalogued','inferred','unknown','conflicting'] for o in objects for a in o['assertions']),
 'unique_assertion_ids':len({a['assertion_id'] for o in objects for a in o['assertions']})==sum(len(o['assertions']) for o in objects),
 'all_assertion_sources_resolve':all(a['source_refs'] and all(s in sources for s in a['source_refs']) for o in objects for a in o['assertions']),
 'all_image_sources_resolve':all(all(s in sources for s in im['source_refs']) for o in objects for im in o['images']),
 'all_assertions_have_coordinates_or_explicit_gap':all(isinstance(a['locator'],dict) and bool(a['locator']) for o in objects for a in o['assertions']),
 'all_source_hashes_recomputed':all(not s.get('physical_path') or (Path(s['physical_path']).is_file() and digest(Path(s['physical_path']))==s['sha256']) for s in sources.values()),
 'image_hashes_recomputed':all(not im.get('path') or digest(Path(im['path']))==im['sha256'] for o in objects for im in o['images']),
 'no_payload_fields':not any(re.match(r'^(transcription|text_code|signs_visual|sequence)',a['field'],re.I) for o in objects for a in o['assertions']),
 'candidate_edges_274':sum(len(o['candidate_family_ids']) for o in objects)==274,
 'candidate_families_62':len({f for o in objects for f in o['candidate_family_ids']})==62,
 'html_cards_and_ids':page.cards==20 and page.ids==expected,
 'html_local_links_exist':all(p.exists() for p in page.files),
 'html_has_no_remote_assets':not page.remote,
 'detailed_outputs_on_D':all(str(p.resolve()).lower().startswith('d:') for p in [x.projection,x.html]),
 }
 # A synthetic identifier tests escaping independently of the observed metadata.
 synthetic={'objects':[{'record_id':'<img src=x onerror=alert(1)>','site':'Harappa','aliases':[],'assertions':[],'images':[],'missing_fields':[],'candidate_family_ids':[]}]}
 checks['html_escapes_untrusted_text']='<img src=x onerror=alert(1)>' not in render(synthetic)
 result={'checks':checks,'passed':sum(checks.values()),'failed':sum(not c for c in checks.values()),'projection_sha256':digest(x.projection),'html_sha256':digest(x.html),'local_html_link_count':len(page.files),'validation_scope':'independent structure/hash/HTML inspection; no browser or image-pixel review'}
 with x.output.open('x',encoding='utf8') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result));raise SystemExit(bool(result['failed']))
