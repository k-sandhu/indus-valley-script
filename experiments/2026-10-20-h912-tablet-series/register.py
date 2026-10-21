"""Preserve all faces and source-qualified joins for the related-object frame."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from bench.common import read_rows, write_json, sha256
RAW=ROOT/'data/raw/2026-10-20-h912-tablet-series'
BASIC=ROOT/'data/raw/2026-10-13-cisi-basic-data-full/assembled'
IMAGES=ROOT/'experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv'


def main():
 out=HERE/'register-v1';out.mkdir(exist_ok=False)
 local=RAW/'register-v1';local.mkdir(exist_ok=False)
 objects=[];events=[]
 for run in ('discovery-v1','confirmation-v1'):
  objects.extend(read_rows(RAW/run/'related-objects.jsonl'))
  events.extend(read_rows(RAW/run/'events.jsonl'))
 basic=defaultdict(list)
 for volume in (1,2):
  for row in read_rows(BASIC/f'cisi{volume}-basic-data.jsonl'):basic[row['cisi']].append(row)
 images=defaultdict(list)
 with IMAGES.open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):images[row['record_id']].append(row)
 evby=defaultdict(list)
 for e in events:evby[e['object_family_id']].append(e)
 flags=[];core=[]
 for obj in objects:
  fs=obj['faces'];family=obj['object_family_id']
  ids=sorted({c for r in fs for c in re.findall(r'[A-Za-z]+-\d+',r['source_cisi'])})
  obj['cisi']=ids
  obj['basic_data_assertions']=[r for c in ids for r in basic.get(c,[])]
  ims=list({r['file']:r for f in fs for r in images.get(f['record_id'],[])}.values())
  obj['images']=ims
  obj['number_v_events']=evby.get(family,[])
  obj['context_status']={'physical_container_attachment':'not supplied by this join',
       'fish_remains':'no object-to-fish-assemblage join in the held tables',
       'calendar_date':'no source-qualified calendar conversion',
       'source_review':'Separate primary excavation assertions in the excavation-links package; normalized fields are preserved as received.'}
  if any(e['fish'] for e in evby.get(family,[])):
   core.append({'object_family_id':family,'cisi':ids,
       'events':[{k:e[k] for k in ('record_id','component','value','stroke','v_code','item','v_position','object_type','site')} for e in evby[family] if e['fish']],
       'images':len(ims),'basic_data_records':len(obj['basic_data_assertions'])})
  flags.append({'object_family_id':family,'cisi':';'.join(ids),'faces':len(fs),
       'has_basic_data':int(bool(obj['basic_data_assertions'])),'has_image':int(bool(ims)),
       'number_v_events':len(evby.get(family,[])),'fish_on_any_face':int(obj['has_fish']),
       'v_and_fish_same_face':int(obj['same_face_vfish'])})
 with (local/'objects.jsonl').open('x',encoding='utf8') as f:
  for obj in objects:f.write(json.dumps(obj,ensure_ascii=False)+'\n')
 with (local/'events.jsonl').open('x',encoding='utf8') as f:
  for e in events:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 with (out/'object-coverage-flags.csv').open('x',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(flags[0]));w.writeheader();w.writerows(flags)
 write_json(out/'core-identifiers.json',{'scope':'Identifiers and coding assertions, not authenticated meanings or physical merges.','candidates':core})
 summary={'related_objects':len(objects),'all_retained_faces':sum(len(o['faces']) for o in objects),
   'objects_with_basic_data':sum(f['has_basic_data'] for f in flags),
   'objects_with_indexed_image':sum(f['has_image'] for f in flags),
   'number_v_events_all_carriers':len(events),
   'fish_number_v_candidate_objects':len(core),
   'local_register':(local/'objects.jsonl').relative_to(ROOT).as_posix(),
   'handling':'Source strings, complete sequences and copied image indexes remain local. Flags and source identifiers are tracked.',
   'input_hashes':{p.relative_to(ROOT).as_posix():sha256(p) for p in [IMAGES,BASIC/'cisi1-basic-data.jsonl',BASIC/'cisi2-basic-data.jsonl']},
   'register_sha256':sha256(local/'objects.jsonl')}
 write_json(out/'coverage.json',summary)
 print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
