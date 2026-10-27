from pathlib import Path
import json,hashlib
P=Path('experiments/2026-10-24-town-phase-pass2');R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-phase-pass2')
def main():
 errors=[];manifest=json.loads((P/'local-file-manifest.json').read_text());sources=json.loads((P/'source-manifest.json').read_text())['sources']; rows=json.loads((R/'relations.json').read_text());a=json.loads((P/'aggregate.json').read_text())
 for f in manifest['files']:
  p=Path(f['physical_path']); assert p.is_relative_to(R)
  if p.stat().st_size!=f['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']: errors.append(str(p))
 sm={s['id']:s for s in sources}
 for row in rows:
  if not 0<=row['pdf_index']<sm[row['source']]['pdf_pages']:errors.append(row['id'])
 assert len(rows)==a['relation_records']==6
 assert sum(len(s['pages_read_zero_based']) for s in sources)==a['new_pages_read']==11
 assert a['queries']==9 and a['construction_sample_joins']==0
 assert hashlib.sha256((P/'PROTOCOL.md').read_bytes()).hexdigest()==a['protocol_sha256']
 result={'passed':not errors,'errors':errors,'source_hashes_checked':2,'local_files_checked':len(manifest['files']),'relation_bindings_checked':6,'pages_read':11,'tier':'author validation; submitted'}
 (P/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__': main()
