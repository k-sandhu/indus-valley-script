import pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parent
errors=[]
for x in json.loads((P/'local-artifacts-v1.json').read_text(encoding='utf8')):
 f=pathlib.Path(x['physical_path'])
 if not f.exists() or f.stat().st_size!=x['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=x['sha256']:errors.append(str(f))
a=json.loads((P/'aggregate-v1.json').read_text());assert a['baseline']=={'akkadian':11,'tamil_including_coins':23,'tamil_seals_rings':16};assert a['admitted']==0;assert a['queries']<=8;assert a['direct_requests']<=a['direct_request_limit_amended']
s=json.loads((P/'source-manifest.json').read_text());assert len(s['sources'])==a['direct_requests'];assert pathlib.Path(s['sources'][-1]['path']).read_bytes().startswith(b'%PDF')
assert hashlib.sha256((P/'PROTOCOL.md').read_bytes()).hexdigest().upper()==(P/'PROTOCOL.sha256').read_text().strip()
result={'passed':not errors,'errors':errors,'source_responses':len(s['sources']),'local_artifacts':len(json.loads((P/'local-artifacts-v1.json').read_text())),'admissions':0,'tier':'author validation; no separate specialist review'}
(P/'validation-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(bool(errors))
