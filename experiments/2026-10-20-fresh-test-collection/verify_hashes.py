import pathlib,json,hashlib
P=pathlib.Path('experiments/2026-10-20-fresh-test-collection');m=json.loads((P/'reservation-manifest.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fail=[]
for key in ['local_object_register','payload_hash_manifest','access_log']:
 q=m[key];p=pathlib.Path(q['path'])
 if h(p)!=q['sha256']:fail.append(q['path'])
j=json.loads(pathlib.Path(m['payload_hash_manifest']['path']).read_text())
for q in j['files']:
 p=pathlib.Path(q['path'])
 if not p.is_file() or p.stat().st_size!=q['bytes'] or h(p)!=q['sha256']:fail.append(q['path'])
local=pathlib.Path('data/raw/2026-10-20-fresh-test-collection');listed={q['path'] for q in j['files']};unlisted=[p.as_posix() for p in local.rglob('*') if p.is_file() and p.as_posix() not in listed and p.as_posix()!=m['payload_hash_manifest']['path']]
r={'frozen_hashes_match':not fail,'failed_paths':fail,'payload_files_verified':len(j['files']),'unlisted_payload_files':unlisted,'manifest_itself_anchored_by_reservation_manifest':True,'pass':not fail and not unlisted};(P/'reservation-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));raise SystemExit(0 if r['pass'] else 1)
