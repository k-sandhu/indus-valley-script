from pathlib import Path
import json,csv,re,hashlib,datetime,collections
P=Path('experiments/2026-10-24-object-identity-pass3');R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-pass3')
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
prior=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-pass2')
targets=json.loads((prior/'target-inventory-v1.json').read_text())
faces=json.loads((prior/'candidate-corpus-faces-v1.json').read_text())
print('target keys',list(targets[0]));print('face keys',list(faces[0]))
files=sorted(Path('data/lipi/public/seal_images').iterdir());mapping=json.loads(Path('data/lipi/src/assets/data/seal_id_and_image_mapping.json').read_text())
indexed={n for names in mapping.values() for n in names}; unlinked=[f.name for f in files if f.name not in indexed]
prefix=collections.Counter(re.match(r'([A-Za-z]+)',f.name)[1] if re.match(r'([A-Za-z]+)',f.name) else '(none)' for f in files)
dump(R/'asset-inventory-v1.json',{'all_count':len(files),'mapped_files':len(indexed),'unmapped_files':unlinked,'prefix_counts':dict(prefix),'all_names':[f.name for f in files]})
print('prefix counts',dict(prefix));print('unmapped',len(unlinked));print('Dholavira sample',[f.name for f in files if re.match(r'(?i)(dh|dhol)',f.name)][:30])
for f in faces:
 if any(f['object_family_id'].endswith(str(n)) for n in [4162,4163,4164,138]):
  print(json.dumps({k:v for k,v in f.items() if k not in ['sequence','signs','raw_sequence','tokens']})[:1800])
