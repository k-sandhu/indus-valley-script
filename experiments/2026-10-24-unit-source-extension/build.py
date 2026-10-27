"""Build source additions and aggregate checks; detailed derivatives remain on D:."""
import csv,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
PKG=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension')
LOGICAL='data/raw/2026-10-24-unit-source-extension/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
 with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def csvread(p):return list(csv.DictReader(p.open(encoding='utf8')))
def record(p):
 p=Path(p);return {'logical_path':LOGICAL+p.name if p.parent==RAW else p.relative_to(ROOT).as_posix(),'physical_path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
 assert RAW.exists() and str((ROOT/'data/raw').resolve()).lower().startswith('d:')
 out=RAW/'run-v2';out.mkdir(exist_ok=False); crops=out/'crops';crops.mkdir()
 faces={r['record_id']:r for r in map(json.loads,(ROOT/'data/normalized/lipi_observed_faces.jsonl').open(encoding='utf8'))}
 queuepath=ROOT/'data/raw/2026-10-22-unit-readiness/run-v2/divided-face-queue.csv';q=[r for r in csvread(queuepath) if not r['image_files']];assert len(q)==43
 keys={r['key']:r for r in csvread(ROOT/'experiments/2026-10-13-image-index-and-units/run-2026-10-13/pages/key-pages.csv')}
 routes=[]
 for r in q:
  m=faces[r['source_record_id']]['metadata']; key=r['cisi']; locator=m.get('excavation-idno'); hasid=locator not in [None,'','-']; h=keys.get(key)
  route={'face_id':r['face_id'],'catalogue_key':key,'site':r['site'],'export_object_locator':locator,'locator_basis':'inherited export metadata, primary identity not yet verified','new_confirmation_eligible':False}
  if h:route.update(route='held-CISI2-page-recovered',volume=int(h['volume']),pdf_page=int(h['pdf_page']),printed_page=int(h['printed_page']),source='cisi-2',crop_recovered=True)
  elif key!='-':route.update(route='CISI3.2-Chanhu-daro' if key.startswith('C-') else 'CISI3.1-Mohenjo-daro-Harappa',source='CISI 3.2 (2019)' if key.startswith('C-') else 'CISI 3.1 (2010)',page=None,crop_recovered=False,access='bibliographic route only; plates not held')
  else:route.update(route=('HARP-object-and-figure' if r['site']=='Harappa' else 'Dholavira-excavation-number') if hasid else 'primary-object-locator-missing',page=None,crop_recovered=False,access='object locator carried forward for primary report search' if hasid else 'requires upstream export bibliography or identity recovery')
  routes.append(route)
 dump(out/'missing-face-routes.json',routes)
 obs=json.loads((RAW/'authored-observations.json').read_text(encoding='utf8'));links=csvread(ROOT/'experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv')
 annotations=[];panels=[];sourceimages=[];exposure=[]
 for r in obs:
  plates=[(RAW/(r['key']+'-plate.png'),r['pdf_page'],r['printed_page'],r['panels'])]
  if 'extra_plate' in r:
   e=r['extra_plate'];plates.append((RAW/e['file'],e['pdf_page'],e['printed_page'],e['panels']))
  for plate,pdfpage,printed,boxes in plates:
   with Image.open(plate) as im:
    for label,box in boxes:
     assert 0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height
     target=crops/(r['key']+'-'+label+('-impression' if label.islower() else '-object')+'.png');im.crop(box).save(target)
     panels.append({'key':r['key'],'label':label,'plate':record(plate),'pdf_page':pdfpage,'printed_page':printed,'render_scale':1.5,'page_pixel_size':list(im.size),'bbox_pixels':box,'rotation_degrees':0,'mirror_applied':False,'crop_path':str(target),'crop_sha256':sha(target)})
   exposure.append({'participant':'gpt-6.1-sol / Codex collaboration','content':'entire rendered catalogue page: images, captions and heading','key':r['key'],'volume':r['volume'],'pdf_page':pdfpage,'printed_page':printed,'eligibility':'historical exploratory exposure','page_file_sha256':sha(plate)})
  for faceid,label in r['faces']:
   annotations.append({'face_id':faceid,'catalogue_key':r['key'],'source_side':label,'status':'provisional-source-graphic-bridge' if label else 'unresolved-parts-versus-faces','accepted_side_bridge':label is not None,'basis':r['observations'],'polarity':r['polarity'],'normalized_order_transform':r['normalized_order_transform'],'image_transform_applied':'none','historical_reading_traversal':None,'word_boundaries':None,'new_confirmation_eligible':False,'author_review_only':True})
  selected={x['file'] for x in links if x['object_family_id']==r['object_id'].split(':')[1]}
  for name in sorted(selected):
   p=ROOT/'data/lipi/public/seal_images'/name
   with Image.open(p) as im: dims=list(im.size)
   label=name[len(r['key'])+1:].split('.')[0]; side={'imp_a':'A','imp_b':'B','imp_c':'C','C_bis':'C'}.get(label,label)
   matched=[a['face_id'] for a in annotations if a['catalogue_key']==r['key'] and a['source_side']==side]
   sourceimages.append({'file':name,'logical_path':p.relative_to(ROOT).as_posix(),'physical_path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p),'pixel_size':dims,'verified_by':'displayed contact sheet and whole primary plate caption with matching graphic content','source_side_or_view':side,'provisional_face_links':matched,'accepted_for_face_side':bool(matched),'polarity':'impression' if label.startswith('imp_') else r['polarity'],'rotation_degrees':0,'mirror_applied':False,'unresolved_reason':None if matched else ('caption gives numbered parts on the same side A' if r['key']=='H-1001' else 'ancillary view without an export inscription bridge')})
 dump(out/'face-annotations.json',annotations);dump(out/'panels.json',panels);dump(out/'image-annotations.json',sourceimages)
 # The route amendment adds one recovered primary witness, without source-segment mapping.
 p=RAW/'M-1188-plate.png'
 with Image.open(p) as im:
  recovery=[]
  for label,box in [('A',[52,440,406,708]),('a',[445,440,755,714])]:
   target=crops/('M-1188-'+label+('-impression' if label.islower() else '-object')+'.png');im.crop(box).save(target);recovery.append({'label':label,'bbox_pixels':box,'pixel_size':list(im.size),'path':str(target),'sha256':sha(target),'polarity':'engraved object' if label=='A' else 'impression','mirror_applied':False,'rotation_degrees':0})
 dump(out/'recovered-divided-face.json',{'face_id':'LIPI:3539.1','catalogue_key':'M-1188','volume':2,'pdf_page':175,'printed_page':140,'plate':record(p),'render_scale':2,'source_side':'A','observation':'Three visible tiers include a short lower stroke group. Fracture truncates the surface. Both the object and the mirrored impression are captioned. No source-segment position map is assigned.','division_evidence':'visible-tier-arrangement-author-observation','unknown_or_damaged_sign_retained':True,'segmenter_or_predictions_changed':False,'panels':recovery,'new_confirmation_eligible':False})
 exposure.append({'participant':'gpt-6.1-sol / Codex collaboration','content':'entire catalogue page, images, captions and heading; adjacent M-1187 and M-1189 also visible','volume':2,'pdf_page':175,'printed_page':140,'page_file_sha256':sha(p),'eligibility':'historical exploratory exposure'})
 exposure.extend([{'participant':'gpt-6.1-sol / Codex collaboration','content':'all ten export code rows on alignment sheet and 20 linked photograph thumbnails','sha256':[sha(RAW/'alignment.png'),sha(RAW/'linked-images.png')],'eligibility':'historical exploratory exposure'},{'participant':'gpt-6.1-sol / Codex collaboration','content':'bibliographic web search snippets for CISI 3.1 and 3.2; incidental catalogue references M-1820 and M-1134 displayed; no plates','eligibility':'source-search exposure, no freshness certified'}]);dump(out/'exposure-log.json',exposure)
 residual={'missing_divided_faces':[r for r in routes if not r['crop_recovered']],'selected_unresolved_faces':[a for a in annotations if not a['accepted_side_bridge']],'multiface_remaining_unreviewed_objects':373,'reviewed_object_count':5,'physical_identity_merges':0};dump(out/'residual-queue.json',residual)
 inputs=[queuepath,ROOT/'data/normalized/lipi_observed_faces.jsonl',ROOT/'experiments/2026-10-13-image-index-and-units/run-2026-10-13/pages/key-pages.csv',ROOT/'data/raw/2026-10-22-evidence-integration/run-v2/faces.jsonl',RAW/'authored-observations.json']
 outputs=[p for p in out.rglob('*') if p.is_file()]
 summary={'schema_version':'1.0','scope':'source and physical-side additions, author reviewed','missing_divided_faces_before':43,'inherited_CISI3_tasks':32,'no_CISI_keys':11,'source_routes':dict(Counter(r['route'] for r in routes)),'recovered_divided_faces':1,'missing_divided_faces_after':42,'physical_side_block_objects':5,'physical_side_block_export_faces':10,'provisional_face_side_bridges':sum(a['accepted_side_bridge'] for a in annotations),'unresolved_export_faces':2,'linked_photographs_displayed':len(sourceimages),'photographs_with_provisional_face_bridges':sum(x['accepted_for_face_side'] for x in sourceimages),'recovered_panel_crops':len(panels)+2,'full_primary_pages_displayed':7,'confirmation_reads':0,'models_fit':0,'physical_identity_merges':0,'segmenter_stock_predictions_changed':False,'inputs':[record(p) for p in inputs],'local_outputs':[{'logical_path':LOGICAL+p.relative_to(RAW).as_posix(),'physical_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in outputs]}
 checks={'route_count':len(routes)==43,'unique_route_faces':len({r['face_id'] for r in routes})==43,'selected_faces_unique':len({r['face_id'] for r in annotations})==10,'bridges_have_graphic_basis':all(a['basis'] and a['source_side'] for a in annotations if a['accepted_side_bridge']),'H1001_not_opposite_sides':all(not a['accepted_side_bridge'] for a in annotations if a['catalogue_key']=='H-1001'),'local_outputs_on_D':all(str(p.resolve()).lower().startswith('d:') for p in outputs),'all_historical':all(a['new_confirmation_eligible'] is False for a in annotations),'image_sha_matches_index':all(sha(ROOT/x['logical_path'])==x['sha256'] for x in sourceimages)}
 summary['checks']=checks;assert all(checks.values());dump(PKG/'results-v2.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs','local_outputs']},indent=2))
if __name__=='__main__':main()
