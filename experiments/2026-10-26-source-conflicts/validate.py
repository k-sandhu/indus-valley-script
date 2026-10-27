import json,pathlib,hashlib
P=pathlib.Path('experiments/2026-10-26-source-conflicts'); R=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-26-source-conflicts'); checks=[]
def check(n,v):checks.append({'check':n,'pass':bool(v)})
c=json.loads((R/'conflicts-v2.json').read_text(encoding='utf8'));a=json.loads((P/'asset-manifest-v2.json').read_text(encoding='utf8'));s=json.loads((P/'source-manifest-v2.json').read_text(encoding='utf8'))
check('two conflicts affecting two targets',len(c['conflicts'])==2 and c['affected_target_count']==2)
check('twenty target frame and comparison entity separated',c['pilot_target_count']==20 and c['comparison_entity_count']==1 and c['conflicts'][0]['comparison_entities']==['L-161'])
for row in c['conflicts']:
 for field in ['conflict_id','target_ids','field','competing_assertions','disposition','safe_to_display','blocked_assertions','what_newly_checked','source_independence','exact_resolving_record']:check(row['conflict_id']+' '+field, bool(row[field]))
 check(row['conflict_id']+' unresolved',row['disposition']=='unresolved')
for item in a['assets']:
 p=pathlib.Path(item['physical_path']);check('asset hash '+p.name,p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
for item in s['sources']:
 p=pathlib.Path(item['logical_path']);check('source hash '+item['id'],hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
check('storage D exists',R.exists());check('below byte cap',a['source_payload_bytes']<150000000)
check('zero requests',s['web_queries']==0 and s['new_acquisitions']==0)
check('protocol hash',hashlib.sha256((P/'PROTOCOL.md').read_bytes()).hexdigest()==s['protocol_sha256'])
for n,h in s['amendment_sha256'].items():check('amendment '+n,hashlib.sha256((P/n).read_bytes()).hexdigest()==h)
v={'status':'pass' if all(x['pass'] for x in checks) else 'fail','checks':checks,'passed':sum(x['pass'] for x in checks),'total':len(checks),'closed_conflicts':0,'new_confirmed_image_joins':0,'bench':'inapplicable metadata source review'}
(P/'validation-v2.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf8');print(v['status'],v['passed'],v['total'])
paths=[p.as_posix() for p in P.iterdir() if p.is_file()]+['knowledge/registry/attempts/SOURCE-CONFLICTS-2026-10-26.json']
(P/'changed-paths.json').write_text(json.dumps({'owned_tracked_paths':sorted(set(paths+[(P/'changed-paths.json').as_posix()])),'local_only_root':str(R),'shared_files_changed':[]},indent=2)+'\n',encoding='utf8')
