"""Acquire open runway windows and validate automatically generated edge picks.

Only modern runway features are measured. Published threshold coordinates seed
the picks. Distinct segments do not overlap within an edge and length family.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,csv,concurrent.futures,math,re,collections
import numpy as np
import rasterio
from pyproj import Transformer
from common import read_json,write_json,sha256,GEOD,geodesic_bearing,delta,utc,code_hashes
from acquire import imagery
from measure_lines import measure

def references(raw,sites):
    root=Path(raw);d=root/'validation'/'ourairports'
    airports={r['ident']:r for r in csv.DictReader((d/'airports.csv').open(encoding='utf-8'))}
    records=[]
    for row in csv.DictReader((d/'runways.csv').open(encoding='utf-8')):
        ident=row['airport_ident']
        if ident not in ['OPMJ','OPSK','VABJ','VAKE','VAAH','VIHR','OPFA','VIBT'] or row['closed']=='1':continue
        if ident=='OPFA' and row['le_ident']!='03R':continue
        if not all(row.get(k) for k in ['le_latitude_deg','le_longitude_deg','he_latitude_deg','he_longitude_deg']):continue
        p=np.array([[float(row['le_longitude_deg']),float(row['le_latitude_deg'])],[float(row['he_longitude_deg']),float(row['he_latitude_deg'])]])
        f,b,length=GEOD.inv(*p[0],*p[1]);az=(f+delta(b-180,f,360)/2)%360
        nearest=min((GEOD.inv(p[:,0].mean(),p[:,1].mean(),s['coordinate_used'][1],s['coordinate_used'][0])[2],s['slug']) for s in sites if s['coordinate_used'])
        warning=[]
        if abs(length-float(row['length_ft'])*.3048)>100:warning.append('Threshold separation and stated length differ by over 100 m')
        # Binary float tails in coordinates do not imply high survey precision.
        if any(len(str(row[k]).split('.')[-1])>9 for k in ['le_latitude_deg','le_longitude_deg','he_latitude_deg','he_longitude_deg']):warning.append('Coordinates contain float32-style tails; source precision doubtful, approximately 4 decimal degrees')
        reference=dict(airport=ident,runway=row['le_ident']+'/'+row['he_ident'],thresholds_lonlat=p.tolist(),reference_bearing_deg=az,reference_kind='WGS84 mean forward/reversed backward azimuth between OurAirports thresholds',threshold_distance_m=length,stated_length_m=float(row['length_ft'])*.3048,width_m=float(row['width_ft'] or 98)*.3048,point=[float(p[:,1].mean()),float(p[:,0].mean())],nearest_town=nearest[1],nearest_town_distance_km=nearest[0]/1000,warnings=warning,eligible=length>=1500 and nearest[0]<=300000,surface=row['surface'])
        # Read only the official runway table, never a basemap or third-party geometry.
        path=root/'validation'/'official-aip'/f'{ident}.html'
        if path.exists():
            text=path.read_text(encoding='utf-8',errors='replace')
            marker=text.find('RUNWAY PHYSICAL CHARACTERISTICS')
            if marker>=0:
                section=text[marker:marker+25000];plain=re.sub('<[^>]+>',' ',section);plain=__import__('html').unescape(plain);plain=' '.join(plain.split())
                reference['official_table_source_path']=path.as_posix()
                # Values must be transcribed in an explicit reference JSON after checking.
        records.append(reference)
    return records

def validate_one(ref,acq,raw,work=None):
    ident=ref['airport'];result=dict(reference=ref,edges=[],segments=[],failures=[])
    if not ref['eligible']:result['failure']='Runway fails reference length or distance condition';return result
    if not acq.get('composite'):result['failure']=acq.get('failure','No composite');return result
    source=acq['composite']['path']
    with rasterio.open(source) as ds:
        tr=ds.transform;epsg=ds.crs.to_epsg();sm=np.array([[tr.a,tr.b,tr.c+(tr.a+tr.b)/2],[tr.d,tr.e,tr.f+(tr.d+tr.e)/2],[0,0,1]])
    inverse=np.linalg.inv(sm);to_grid=Transformer.from_crs(4326,epsg,always_xy=True)
    p=np.asarray(ref['thresholds_lonlat']);x,y=to_grid.transform(p[:,0],p[:,1]);p=np.c_[x,y];v=p[1]-p[0];length=np.linalg.norm(v);v/=length;normal=np.array([-v[1],v[0]])
    lines=[]
    for edge in [-1,1]:
        start=p[0]+v*100+normal*ref['width_m']/2*edge;finish=p[1]-v*100+normal*ref['width_m']/2*edge
        def add(id_,ends,family):
            png=(np.c_[ends,np.ones(2)]@inverse.T)[:,:2]
            lines.append(dict(id=id_,family=family,edge=edge,endpoints_px=png.tolist(),corridor_half_width_px=2.,feature='edge',mode='fit'))
        add(f'{edge}-full',[start,finish],'full')
        for seg in [100,200,300,400]:
            for k in range(int((length-200)//seg)):
                ends=np.stack([start+v*k*seg,start+v*(k+1)*seg]);add(f'{edge}-{seg}-{k}',ends,str(seg))
    side=dict(kind='imagery',source=source,source_sha256=sha256(source),epsg=epsg,pixel_to_utm=sm.tolist())
    for line in lines:
        try:
            m=measure(dict(source_id=ident,lines=[line]),side)['lines'][0]
            record=dict(id=m['id'],edge=m['edge'],family=m['family'],bearing_deg=m['bearing_deg'],reference_bearing_deg=ref['reference_bearing_deg'],residual_deg=delta(m['bearing_deg'],ref['reference_bearing_deg']),sigma_deg=m['sigma_deg'],length_m=m['length_m'],inlier_count=m['inlier_count'],profile_count=m['profile_count'],residual_rms_px=m['residual_rms_px'])
            (result['edges'] if line['family']=='full' else result['segments']).append(record)
        except Exception as e:result['failures'].append(dict(id=line['id'],family=line['family'],failure=str(e)))
    if result['edges']:result['runway_residual_deg']=float(np.mean([r['residual_deg'] for r in result['edges']]))
    dest=(Path(work) if work else Path(raw)/'validation'/'runways')/ident;dest.mkdir(parents=True,exist_ok=True)
    write_json(dest/'automatic-picks.json',dict(reference=ref,sidecar=side,lines=lines))
    return result

def aggregate(results):
    residuals=[r['runway_residual_deg'] for r in results if 'runway_residual_deg' in r]
    segments=[s for r in results for s in r['segments']];bylen={}
    for family in ['100','200','300','400']:
        rows=[s for s in segments if s['family']==family];v=np.array([s['residual_deg'] for s in rows]);z=np.array([s['residual_deg']/s['sigma_deg'] for s in rows])
        bylen[family]=dict(n=len(rows),mean_deg=float(v.mean()) if len(v) else None,rms_deg=float(np.sqrt(np.mean(v*v))) if len(v) else None,empirical_to_stated_sigma_rms=float(np.sqrt(np.mean(z*z))) if len(z) else None)
    z=np.array([s['residual_deg']/s['sigma_deg'] for s in segments])
    return dict(n_runways=len(residuals),mean_deg=float(np.mean(residuals)) if residuals else None,rms_deg=float(np.sqrt(np.mean(np.asarray(residuals)**2))) if residuals else None,by_segment_length_m=bylen,empirical_to_stated_sigma_rms=float(np.sqrt(np.mean(z*z))) if len(z) else None,ratio_definition='sqrt(mean((signed residual / stated line sigma)^2)), all successful segments',segment_independence='Non-overlapping within each runway edge and length family. Opposite edges share the scene; different length families overlap. These are calibration observations, not independent archaeological samples.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('sites');p.add_argument('raw');p.add_argument('output');p.add_argument('--acquire-only',action='store_true');p.add_argument('--official-references');p.add_argument('--imagery-manifest',help='Use only reconciled held runway imagery; makes no network calls');p.add_argument('--work',help='Fresh directory for automatic picks, independent of the held source root');a=p.parse_args();sites=read_json(a.sites)['sites'];refs=references(a.raw,sites)
    if Path(a.output).exists():raise FileExistsError(a.output)
    if a.official_references:
        overrides=read_json(a.official_references)
        for r in refs:
            if r['airport'] in overrides:r.update(overrides[r['airport']])
    # Threshold-derived fields must describe the selected reference, including
    # when an official table replaces obsolete OurAirports coordinates.
    for ref in refs:
        q=np.asarray(ref['thresholds_lonlat']);length=GEOD.inv(*q[0],*q[1])[2]
        ref['threshold_distance_m']=length;ref['point']=[float(q[:,1].mean()),float(q[:,0].mean())]
        nearest=min((GEOD.inv(ref['point'][1],ref['point'][0],s['coordinate_used'][1],s['coordinate_used'][0])[2],s['slug']) for s in sites if s['coordinate_used'])
        ref['nearest_town']=nearest[1];ref['nearest_town_distance_km']=nearest[0]/1000;ref['eligible']=length>=1500 and nearest[0]<=300000
    raw=Path(a.raw);runroot=raw/'validation'/'runway-imagery';runroot.mkdir(parents=True,exist_ok=True)
    def get(ref):
        if a.imagery_manifest:
            held=read_json(a.imagery_manifest)['runways']
            return next((r for r in held if r['slug']==ref['airport']),dict(slug=ref['airport'],composite=None,failure='No held runway imagery'))
        if not ref['eligible']:return dict(slug=ref['airport'],failure='Reference length less than 1500 m')
        old=sorted((runroot/'imagery'/ref['airport']).glob('acquisition-v*/acquisition-result.json'))
        good=[read_json(p) for p in old if read_json(p).get('composite')]
        return good[-1] if good else imagery(dict(slug=ref['airport'],coordinate_used=ref['point']),runroot,9)
    with concurrent.futures.ThreadPoolExecutor(3) as pool:acquisitions=list(pool.map(get,refs))
    if a.acquire_only:write_json(a.output,dict(references=refs,acquisitions=acquisitions));return
    results=[validate_one(r,acq,a.raw,a.work) for r,acq in zip(refs,acquisitions)]
    precise=[r for r in results if r['reference'].get('precision_class')=='official' or not r['reference']['warnings']]
    checks=[dict(name='at least six eligible runways measured',pass_=sum('runway_residual_deg' in r for r in results)>=6),dict(name='two full edges per measured runway',pass_=all(len(r['edges'])==2 for r in results if 'runway_residual_deg' in r))]
    write_json(a.output,dict(schema_version=1,created_utc=utc(),task='modern-runway-validation',synthetic=False,provenance=code_hashes(),results=results,imagery=acquisitions,aggregate=aggregate(results),precise_reference_aggregate=aggregate(precise),checks=[{('pass' if k=='pass_' else k):v for k,v in c.items()} for c in checks],overall_pass=all(c['pass_'] for c in checks),pass_scope='Execution and coverage checks. Empirical errors calibrate conditional fit sigma; no archaeological bearing is measured.'))
if __name__=='__main__':main()
