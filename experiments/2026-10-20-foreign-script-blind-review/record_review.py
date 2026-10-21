import json,csv,hashlib
from pathlib import Path
out=Path('experiments/2026-10-20-foreign-script-blind-review')
p=Path('data/raw/2026-10-20-foreign-script-audit/review-packet.json')
a=json.loads(p.read_text(encoding='utf-8-sig'))
notes={
'A02':('M-417','CISI1 printed 101 / PDF137','No separable inscription identified; joined animal composition fills preserved field.','Broken circular segment; edge loss prevents reconstructing original field.','Photographs of object and mirrored impression agree in animal arrangement; zero securely identified text signs.','No text direction available.'),
'A04':('M-1369','full page locator pending','Several distinct signs and grouped strokes follow curved edge; segmentation and code assignments unresolved.','Large lower sector missing; crack crosses field; some outer signs clipped.','Object and impression are mirrored; reverse photograph adds no text.','Mirror polarity is supported; starting edge and reading direction remain unresolved.'),
'A08':('C-32','CISI1 printed 335 / PDF371','Approximately five visible upper-field units, including narrow strokes whose grouping is uncertain.','Lower-left loss intersects animal; upper text largely preserved but surface uneven.','Object/impression mirrored; reverse and profile show same seal, not extra text-bearing objects.','Linear upper row visible; reading direction unestablished from picture alone.'),
'A15':('M-416','CISI1 printed 101 / PDF137','Roughly four large clusters around animal; count depends on whether stroke groups are single signs.','Rim and upper-right surface loss; alternate photographs improve some strokes.','Two object and two impression photographs are repeated views of one face.','Curved placement has no marked start; mirrored pairing established.'),
'A18':('M-415','CISI1 printed 100 / PDF136','Three main upper-field sign shapes appear, but left edge and internal marks remain uncertain.','Horizontal damaged band crosses animal; upper field worn; rim losses.','Two impression photographs show the same layout with different lighting; reverse adds no independent text.','Upper row identifiable; physical evidence does not settle reading direction.'),
'A22':('M-500','CISI1 printed 125 / PDF161','Incised face contains multiple radial/angled shapes; no defensible sign count from this image.','Light and relief change stroke visibility; preserve alternatives.','Full page labels this object TABLETS incised. Reverse is tree imagery; six images include repeated impressions of two faces. It should not silently enter a seal-only population.','Radial arrangement supplies no definite start or traversal.'),
'A29':('Dmd-1','CISI1 printed 352 / PDF388','One large U-shaped mark is visible; minor adjacent marks cannot be assigned confidently.','Coarse worn surface; internal detail poor in object and impression.','Object/impression mirroring supports polarity; reverse/profile are ancillary views.','A single mark supplies no sequence direction.')}
with (out/'observations.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['opaque_id','catalogue_caption','disposition','source_location','visible_forms','damage','polarity_and_duplicate_views','direction','mapping_confidence'])
 for o in a['objects']:
  if o['opaque_id'] in notes:
   n=notes[o['opaque_id']];w.writerow([o['opaque_id'],n[0],'pictured-reviewed',*n[1:],'No candidate transcription or mapping aid supplied; code agreement unassessed'])
  else:w.writerow([o['opaque_id'],'','unpictured-unverified','','','','','unresolved','unassessed'])
inputs=[]
for o in a['objects']:
 for im in o['images']:
  b=Path(im['path']).read_bytes();h=hashlib.sha256(b).hexdigest();inputs.append(dict(opaque_id=o['opaque_id'],path=im['path'],sha256=h,packet_hash_matches=h==im['sha256']))
for q in [p,Path(a['additional_primary_plate']),Path('research/literature/sources/joshi_parpola_1987_cisi1.pdf'),*Path('data/raw/2026-10-20-foreign-script-blind-review').glob('*.png')]:
 inputs.append(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
(out/'input-hashes.json').write_text(json.dumps(inputs,indent=2)+'\n')
print(len(a['objects']),sum(bool(o['images']) for o in a['objects']),len([x for x in inputs if 'opaque_id' in x]),all(x.get('packet_hash_matches',True) for x in inputs))
