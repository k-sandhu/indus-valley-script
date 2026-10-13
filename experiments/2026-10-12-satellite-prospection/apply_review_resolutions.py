"""Create a revised geographic endpoint while preserving all prior decisions."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,csv,hashlib,json,copy
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def main():
    a=argparse.ArgumentParser();a.add_argument('--input',type=Path,required=True);a.add_argument('--resolutions',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--version',type=int,required=True);args=a.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    data=read(args.input);changes=read(args.resolutions);features=data['feature_collection']['features'];ids={f['properties']['id']:f for f in features}
    for identifier,update in changes['updates'].items():
        if identifier not in ids:raise KeyError(identifier)
        props=ids[identifier]['properties'];props['previous_classifications']=props.get('previous_classifications',[])+[{'stage':data.get('review_stage','coordinator pre-review'),'status':props['status'],'explanation':props['explanation']}]
        props.update(update)
    data.update(created_utc=datetime.now(timezone.utc).isoformat(),review_stage=changes['stage'],limits=changes['limits'])
    save(args.output/f'atlas-data-v{args.version}.json',data)
    reviewed=[f for f in features if '-A' in f['properties']['id'] or '-T' in f['properties']['id'] and 'source_component_label' in f['properties']]
    prospects=[f for f in reviewed if f['properties']['status']=='screening_lead'];reserve=[f for f in reviewed if f['properties'].get('desk_check_reserve')]
    save(args.output/'reviewed-features.geojson',{'type':'FeatureCollection','features':reviewed})
    save(args.output/'reconnaissance-prospects.geojson',{'type':'FeatureCollection','features':prospects})
    save(args.output/'reconnaissance-register.geojson',{'type':'FeatureCollection','features':prospects+reserve})
    columns=['id','block_id','latitude','longitude','status','priority','threshold_support_ha','peak_minus_annulus_m','strength','alternative','next_test','nearest_reference_id','reference_distance_m','inside_assumed_reference_buffer','novelty_status']
    with (args.output/'reconnaissance-register.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=columns);writer.writeheader()
        for f in prospects+reserve:
            p=f['properties'];m=p['nearest_reference_matches'][0]
            writer.writerow(dict(id=p['id'],block_id=p['block_id'],latitude=round(p['lat'],6),longitude=round(p['lon'],6),status=p['status'],priority=p['priority'],threshold_support_ha=p['support_area_ha'],peak_minus_annulus_m=round(p['local_measurement']['point_minus_annulus_m'],3),strength=p['strength'],alternative=p['alternative'],next_test=p['next_test'],nearest_reference_id=m['id'],reference_distance_m=round(m['distance_m'],1),inside_assumed_reference_buffer=m['within_assumed_buffer'],novelty_status=p['novelty_status']))
    summary=dict(area_km2=sum(b['area_km2'] for b in data['study_blocks']),blocks=len(data['study_blocks']),scenes=sum(len(b['scene_ids']) for b in data['study_blocks']),reviewed_targets=len(reviewed),reviewed_status_counts=dict(Counter(f['properties']['status'] for f in reviewed)),atlas_feature_counts=dict(Counter(f['properties']['status'] for f in features)),desk_check_reserves=len(reserve),review_stage=changes['stage'])
    save(args.output/'summary.json',summary)
    save(args.output/'manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'code_path':rel(Path(__file__)),'code_sha256':sha(Path(__file__)),'inputs':[{'path':rel(p),'sha256':sha(p)} for p in [args.input,args.resolutions]],'files':[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(args.output.rglob('*')) if p.is_file()],'summary':summary})
    print(json.dumps(summary))
if __name__=='__main__':main()
