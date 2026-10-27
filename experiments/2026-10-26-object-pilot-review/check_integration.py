"""Check parent projection without calling its validator."""
import json, hashlib, re
from pathlib import Path
P=Path('experiments/2026-10-26-object-pilot-review')
R=Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot/integration-v1')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=load('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot-register/pilot-register-v4.json')
joined=load(R/'pilot-integrated-v1.json')
b={o['record_id']:o for o in base['objects']};j={o['record_id']:o for o in joined['objects']}
def retained(a, rows):
    return any(all(row.get(k)==v for k,v in a.items()) for row in rows)
checks={'same_twenty_targets':set(b)==set(j) and len(joined['objects'])==20,
        'all_539_base_assertion_fields_retained':all(all(retained(a,j[k]['assertions']) for a in o['assertions']) for k,o in b.items()),
        'candidate_edges_and_statuses_unchanged':all(j[k]['candidate_family_ids']==o['candidate_family_ids'] and j[k]['accepted_physical_merge']==o['accepted_physical_merge'] for k,o in b.items()),
        'all_base_missing_fields_retained':all(j[k]['missing_fields']==o['missing_fields'] for k,o in b.items()),
        'no_context_only_target_images':not j['H-1682']['images'] and not j['H-1692']['images'],
        'H1657_no_local_photo_bytes':all(not i.get('path') for i in j['H-1657']['images']),
        'zero_new_photo_availability':joined['integration']['newly_available_pilot_photographs']==0,
        'zero_physical_merges':joined['integration']['physical_merges']==0}
hashes=[]
for s in joined['source_catalogue']:
    if s.get('sha256') and s.get('physical_path'):
        path=Path(s['physical_path']);hashes.append({'path':str(path),'matches':path.is_file() and sha(path)==s['sha256']})
checks['all_integration_source_hashes_match']=all(s['matches'] for s in hashes)
html=(R/'catalogue-integrated-v1.html').read_text(encoding='utf8')
checks['twenty_html_cards']=all(f'id="{k}"' in html for k in b)
checks['no_remote_image_embedding']=not re.search(r'<img[^>]+src=["\']https?://',html)
result={'checks':checks,'passed':sum(checks.values()),'failed':sum(not v for v in checks.values()),'source_hash_bindings':len(hashes),'projection_sha256':sha(R/'pilot-integrated-v1.json'),'html_sha256':sha(R/'catalogue-integrated-v1.html'),'scope':'Structural and hash review of integrated projection; source judgments in REPORT-v2.md'}
(P/'integration-review-v2.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
