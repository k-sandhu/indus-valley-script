"""Join preserved observations, classifications and geographic layers into a new export."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,csv,hashlib,json,math
from collections import Counter
from shapely.geometry import Point,shape,box,mapping
from pyproj import Geod,Transformer

ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
GEOD=Geod(ellps='WGS84')
DEM_NOTICE='produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return path.resolve().relative_to(ROOT).as_posix()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def distance(a,b):return abs(GEOD.inv(a[0],a[1],b[0],b[1])[2])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    paths=[BASE/'outputs-v1/block-analysis.json',BASE/'outputs-v2/block-analysis.json',BASE/'outputs-v1/review-targets.geojson',BASE/'outputs-v2/review-targets.geojson',BASE/'outputs-terrain-v1/review-targets.geojson',BASE/'outputs-terrain-v1/block-analysis.json',BASE/'review/optical-visual-decisions-v1.json',BASE/'review/terrain-visual-decisions-v1.json',BASE/'research/known-locations.geojson',BASE/'research/concordance-sources.json',BASE/'research/data-source-register.json',BASE/'THIRD-PARTY-NOTICES.md']
    outputs=[read(p) for p in paths[:2]];blocks=sum([v['blocks'] for v in outputs],[]);overlays=sum([v['overlays'] for v in outputs],[])
    optical=sum([read(p)['features'] for p in paths[2:4]],[]);terrain=read(paths[4])['features'];terrain_report=read(paths[5]);known=read(paths[8])['features']
    sources=read(paths[9])['sources']+read(paths[10])['sources'];source_map={s['id']:s for s in sources}
    decisions={v['id']:v for path in paths[6:8] for v in read(path)['decisions']}
    if len(decisions)!=len(optical)+len(terrain):raise ValueError('Classification join count mismatch')
    features=[]
    for feature in optical+terrain:
        f=copy.deepcopy(feature);p=f['properties'];d=decisions[p['id']]
        p.update(status=d['status'],name=p['id']+': '+('reconnaissance prospect' if d['status']=='screening_lead' else d['alternative']),explanation=d['observation'],alternative=d['alternative'],next_test=d.get('next_test','No archaeological priority from this screen; reassess only with new source or ground evidence.'),observation_ids=[p['id']+'-VIS1'],source_ids=['D02','D10']+(['D13'] if '-T' in p['id'] else []),coordinate_uncertainty_m=30,uncertainty_is_assumed=True,uncertainty_basis='Analyst plotting buffer comparable to the DSM grid. It is not a measured geolocation error or archaeological boundary.',archaeological_probability=None,occupation_date=None)
        if '-T' in p['id']:
            p['native_center_xy']=p['peak_native_xy'];p['dates']=[v['date'] for v in next(b for b in blocks if b['id']==p['block_id'])['scene_qa']]
            p['metrics']={'area_ha':p['support_area_ha'],'relative_height_m':p['local_measurement']['point_minus_annulus_m'],'relative_height_definition':'DSM peak minus surrounding annulus median; differs from optical area-equivalent-circle median descriptor','tree_fraction_2021':p['WorldCover2021_fractions']['tree'],'built_fraction_2021':p['WorldCover2021_fractions']['built']}
            p['panel_path']=p['panel']['path'];p['panel_sha256']=p['panel']['sha256'];p['source_item_ids']=p['scene_ids'];p['analysis_method']='Post-optical-outcome exploratory terrain screen'
        else:p['analysis_method']='Original fixed-parameter optical screen'
        if d['status']=='known':p['source_ids']+=['SC15','SPC09']
        p['source_urls']=[source_map[s]['url'] for s in p['source_ids']]
        p['strength']=d.get('strength');p['priority']=d.get('priority')
        points=[v for v in known if v['geometry']['type']=='Point' and v['properties']['kind']=='known_archaeological_reference']
        coord=[p['lon'],p['lat']]
        matches=sorted([{'id':v['properties']['id'],'entity_id':v['properties']['entity_id'],'distance_m':distance(coord,v['geometry']['coordinates']),'reference_buffer_m':v['properties']['coordinate_uncertainty_m'],'within_assumed_buffer':distance(coord,v['geometry']['coordinates'])<=v['properties']['coordinate_uncertainty_m']} for v in points],key=lambda v:v['distance_m'])
        p['nearest_reference_matches']=matches[:3]
        p['novelty_status']='not established; incomplete gazetteers and unverified site extents'
        cores=[v for v in known if v['geometry']['type']=='Point' and v['properties']['kind']=='published_sediment_core']
        p['nearest_published_core']=min([{'id':v['properties']['id'],'distance_m':distance(coord,v['geometry']['coordinates']),'meaning':'Distance to a borehole, not to a channel edge or Bronze Age water source'} for v in cores],key=lambda v:v['distance_m'])
        features.append(f)
    for original in known:
        f=copy.deepcopy(original);p=f['properties'];kind=p['kind'];p['source_ids']=[p['source_id']];p['source_urls']=[source_map[p['source_id']]['url']]
        p['observation_ids']=[p['source_id']+'-O1'];p['status']='known' if kind=='known_archaeological_reference' else 'context'
        p['explanation']='Source observation at '+p['source_locator']+'. '+p.get('coordinate_concordance',p.get('sampled_landform',p.get('interpretation','Published metadata coverage only.')))
        p['next_test']='Resolve field position and site plan before using this point to label an image feature.' if kind=='known_archaeological_reference' else 'Consult the source stratigraphy or historical map metadata; do not transfer an age to nearby imagery.'
        p['dates']=[str(p.get('field_survey_reference_year',p.get('map_date','published source')))]
        if f['geometry']['type']=='Point':
            p['block_id']=next((b['id'] for b in blocks if box(*b['bbox_lonlat']).covers(shape(f['geometry']))),None)
            p['imagery_coverage']='inside acquired block' if p['block_id'] else 'outside acquired imagery; geographic reference only'
        features.append(f)
    for block in blocks:
        for control in block['comparison_points']:
            p=copy.deepcopy(control);p.update(name=p['id']+': seeded optical context',status='control',kind='seeded_optical_context',block_id=block['id'],observation_ids=[p['id']+'-O1'],explanation='Seeded coordinate with actual four-date colour/NDVI descriptors. Archaeological absence is not verified.',dates=[q['date'] for q in block['scene_qa']],source_ids=['D02'],source_urls=[source_map['D02']['url']],coordinate_uncertainty_m=30,next_test='Use as diagnostic context only; no field absence label.')
            features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[p['lon'],p['lat']]},'properties':p})
    for block in terrain_report['blocks']:
        for control in block['diagnostic_controls']:
            p=copy.deepcopy(control);p.update(name=p['id']+': '+p['kind'],status='control',block_id=block['block_id'],observation_ids=[p['id']+'-O1'],explanation=p.get('meaning','Diagnostic landscape comparator with no verified archaeological absence.'),dates=['WorldCover 2021; DSM principal epoch 2011-2015'],source_ids=['D10','D13'],source_urls=[source_map['D10']['url'],source_map['D13']['url']],coordinate_uncertainty_m=30,next_test='Diagnostic method check only; do not interpret as a negative archaeological sample.')
            features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[p['lon'],p['lat']]},'properties':p})
    for overlay in overlays:
        overlay['path']='../'+str(Path(overlay['path']).relative_to(BASE.relative_to(ROOT))).replace('\\','/')
        if overlay['kind']=='terrain':
            overlay.update(date='Principal DSM acquisition epoch 2011-2015, with other fill sources; AWS 2021 release',attribution=DEM_NOTICE)
        else:
            year=overlay['date'][:4];overlay['attribution']=f'Contains modified Copernicus Sentinel data ({year}). ESA/Copernicus; Element84 Earth Search C1.'
            if overlay['kind']=='false_colour':overlay['native_pixel_m']='20 m SWIR; 10 m NIR and red'
        overlay['limits']+=' Full component notices: THIRD-PARTY-NOTICES.md.'
    export=dict(title='Indus settlement reconnaissance: acquired imagery and source observations',created_utc=datetime.now(timezone.utc).isoformat(),study_blocks=[{k:b[k] for k in ['id','name','region_ids','bbox_lonlat','native_epsg','scene_ids','area_km2']} for b in blocks],overlays=overlays,feature_collection={'type':'FeatureCollection','features':features},sources=[{'id':s['id'],'title':s['title'],'url':s['url']} for s in sources],limits='Three low-confidence reconnaissance prospects. No new archaeological site, occupation date, field verification or archaeological detection accuracy has been established. Assumed point buffers do not bound actual site positions.',notices=DEM_NOTICE+' The organisations in charge of the Copernicus programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.')
    save(args.output/'atlas-data-v1.json',export)
    reviewed=[f for f in features if f['properties']['id'] in decisions]
    save(args.output/'reviewed-features.geojson',{'type':'FeatureCollection','features':reviewed})
    save(args.output/'reconnaissance-prospects.geojson',{'type':'FeatureCollection','features':[f for f in reviewed if f['properties']['status']=='screening_lead']})
    columns=['id','block_id','latitude','longitude','status','priority','threshold_support_ha','peak_minus_annulus_m','strength','alternative','next_test','nearest_reference_id','reference_distance_m','inside_assumed_reference_buffer','novelty_status']
    with (args.output/'reconnaissance-prospects.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=columns);writer.writeheader()
        for f in reviewed:
            p=f['properties']
            if p['status']!='screening_lead':continue
            m=p['nearest_reference_matches'][0]
            writer.writerow(dict(id=p['id'],block_id=p['block_id'],latitude=round(p['lat'],6),longitude=round(p['lon'],6),status=p['status'],priority=p['priority'],threshold_support_ha=p['support_area_ha'],peak_minus_annulus_m=round(p['local_measurement']['point_minus_annulus_m'],3),strength=p['strength'],alternative=p['alternative'],next_test=p['next_test'],nearest_reference_id=m['id'],reference_distance_m=round(m['distance_m'],1),inside_assumed_reference_buffer=m['within_assumed_buffer'],novelty_status=p['novelty_status']))
    summary={'area_km2':sum(b['area_km2'] for b in blocks),'blocks':len(blocks),'scenes':sum(len(b['scene_ids']) for b in blocks),'optical_components':sum(b['retained_components'] for b in blocks),'optical_reviewed':len(optical),'terrain_reviewed':len(terrain),'reviewed_status_counts':dict(Counter(f['properties']['status'] for f in reviewed)),'atlas_feature_counts':dict(Counter(f['properties']['status'] for f in features)),'minimum_three_date_land_fraction':min(b['land_usable_atleast3dates_fraction'] for b in blocks),'all_acquisition_dates':[{'block_id':b['id'],'dates':[q['date'] for q in b['scene_qa']]} for b in blocks]}
    save(args.output/'summary.json',summary)
    files=[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(args.output.rglob('*')) if p.is_file()]
    save(args.output/'manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'code_path':rel(Path(__file__)),'code_sha256':sha(Path(__file__)),'inputs':[{'path':rel(p),'sha256':sha(p)} for p in paths],'files':files,'summary':summary,'classification_stage':'Root visual classifications before independent/Claude review; preserve and create a later export if decisions change.'})
    print(json.dumps(summary))

if __name__=='__main__':main()
