from pathlib import Path
import json,csv,hashlib
import fitz
raw=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-pass2')
assert not (raw/'target-inventory-v1.json').exists(), 'Frozen preparation output exists'
prior=json.load(open('data/raw/2026-10-24-object-identity-extension/identity-assertions-v1.json'))[:10]
inv=list(csv.DictReader(open('experiments/2026-10-21-post-catalogue-finds/objects.csv',encoding='utf-8-sig')))
target=[x for x in inv if x['row_id'] in {x['row_id'] for x in prior}]
ids={y for x in target for y in x['local_family_ids'].split('|')}
corpus=[json.loads(l) for l in open('data/normalized/lipi_observed_faces.jsonl',encoding='utf-8')]
corpus=[x for x in corpus if x['object_family_id'] in ids]
# Separate source text and metadata snapshots, kept local.
(raw/'candidate-corpus-faces-v1.json').write_text(json.dumps(corpus,indent=2)+'\n')
(raw/'target-inventory-v1.json').write_text(json.dumps(target,indent=2)+'\n')
links=list(csv.DictReader(open('experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv',encoding='utf-8-sig')))
linked=[x for x in links if x['object_family_id'] in ids]
(raw/'candidate-image-links-v1.json').write_text(json.dumps(linked,indent=2)+'\n')
d=fitz.open('data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf');obs=[]
for x in prior:
 page=x['catalogue_observation'][1];p=d[page-1];words=p.get_text('words');ss=[w for w in words if w[0]<100 and w[1]>95 and w[4].rstrip('.').isdigit() and w[4].endswith('.')];sw=next(w for w in ss if int(w[4][:-1])==x['catalogue_serial']);start=sw[1]-3;end=min([w[1]-3 for w in ss if w[1]>sw[1]]+[750]);rect=fitz.Rect(45,start,560,end)
 dest=raw/(x['row_id']+'-catalogue.png');p.get_pixmap(matrix=fitz.Matrix(2,2),clip=rect).save(dest)
 text=p.get_text(clip=rect);(raw/(x['row_id']+'-catalogue.txt')).write_text(text,encoding='utf-8')
 obs.append({'row_id':x['row_id'],'registration':x['source_registration'],'catalogue_serial':x['catalogue_serial'],'pdf_page':page,'printed_page':page-17,'clip':list(rect),'image_path':str(dest),'image_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(raw/'target-primary-panels-v1.json').write_text(json.dumps(obs,indent=2)+'\n')
print('Ten primary object panels rendered; candidate families',len(ids),'corpus faces',len(corpus),'linked photos',len(linked))
print(*[(x['row_id'],x['registration'],x['findspot'],x['depth_or_layer'],x['context_join_family']) for x in target],sep='\n')
