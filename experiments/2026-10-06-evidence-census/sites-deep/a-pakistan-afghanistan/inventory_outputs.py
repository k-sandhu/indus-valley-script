"""List every package and local raw file; perform requested output consistency checks."""
import csv,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'knowledge/INDEX.md').exists())
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan'
def write(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sites=json.loads((OUT/'site-rows.json').read_text(encoding='utf-8'))['sites']
with (OUT/'site-rows.csv').open(encoding='utf-8',newline='') as f: csvrows=list(csv.DictReader(f))
if len(csvrows)!=len(sites) or [s['canonical_name'] for s in sites]!=[s['canonical_name'] for s in csvrows]: raise ValueError('CSV/JSON row mismatch')
for a,b in zip(sites,csvrows):
 for k,v in a.items():
  if isinstance(v,(list,dict)) and json.loads(b[k])!=v: raise ValueError(f'CSV nested field mismatch: {a["canonical_name"]}.{k}')
audit=json.loads((OUT/'revision-audit.json').read_text(encoding='utf-8'))
archive=json.loads((OUT/'preservation.json').read_text(encoding='utf-8'))
for r in archive['files']:
 if hashlib.sha256((OUT/r['path']).read_bytes()).hexdigest()!=r['sha256']: raise ValueError('Archive changed')
for p in OUT.rglob('*'):
 if p.is_file() and 'first-pass' not in p.parts and p.suffix in {'.json','.csv','.md','.py'}:
  t=p.read_text(encoding='utf-8-sig')
  if '\ufffd' in t: raise ValueError('Encoding replacement character: '+str(p))
audit.update(csv_json_row_count=len(sites),csv_nested_fields_match=True,first_pass_hashes_match=True,active_utf8_replacement_characters=0)
write('revision-audit.json',audit)
def entries(root):
 return [dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size) for p in sorted(root.rglob('*')) if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
owned=entries(OUT)
original={Path(r['path']).name:r['sha256'] for r in archive['files']}
changed=[];created=[];unchanged=[]
for r in owned:
 p=ROOT/r['path'];rel=p.relative_to(OUT)
 if len(rel.parts)==1 and p.name in original:
  (unchanged if hashlib.sha256(p.read_bytes()).hexdigest()==original[p.name] else changed).append(r['path'])
 else: created.append(r['path'])
manifest_path=(OUT/'created-paths.json').relative_to(ROOT).as_posix()
if manifest_path not in created: created.append(manifest_path)
write('created-paths.json',dict(created_owned_paths=created,changed_owned_paths=changed,unchanged_first_pass_working_paths=unchanged,owned_files=owned,raw_files=entries(RAW),basis='Owned changes compared with preserved first-pass hashes. Raw inventory covers this package’s four revision subdirectories; source download hashes are in acquisition manifests.',removed_regenerable_raw_files=['common-revision/cisi2-archive.txt']+[f'common-revision/sibri-report-pdf{i:02}.png' for i in range(1,14)],removal_reason='Drive full; source PDFs, page-text JSON and OCR retained; renders and text can be regenerated.'))
print(f'Checked{len(sites)}CSV/JSON rows and{len(archive["files"])}archive hashes; wrotepathinventory.')
