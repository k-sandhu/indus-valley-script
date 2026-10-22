"""Run synthetic measurement checks, save working rasters, refuse existing outputs."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,collections,math
import numpy as np
from scipy.special import ndtr
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
from PIL import Image,ImageDraw
from common import write_json,sha256,code_hashes,GEOD,geodesic_bearing,delta,fold,check_space
from measure_lines import refine,measure
from render_image import render as render_image
from render_plan import render as render_plan
from systems import summarize,town_result,segment_distance
from register_plan import register
from igrf import field

def run(work,coefficients):
    work=Path(work);work.mkdir(parents=True,exist_ok=False);checks=[];groups=collections.defaultdict(list);detailed=[]
    rng=np.random.default_rng(10212026)
    for location,lon in [('central-meridian',69.),('far-central-meridian',71.8)]:
        lat=27.;epsg=32642;t=Transformer.from_crs(4326,epsg,always_xy=True);x,y=t.transform(lon,lat);tr=from_origin(x-1005,y+1005,10,10)
        sm=np.array([[10,0,tr.c+5],[0,-10,tr.f-5],[0,0,1]]);inv=np.linalg.inv(sm)
        yy,xx=np.mgrid[:201,:201];xy=np.stack([xx,yy],axis=-1)
        for bearing in [-40,-20,0,20,40]:
            for length in [50,100,200,300,400,1000]:
                ends=[]
                for b in [bearing+180,bearing]:
                    lo,la,_=GEOD.fwd(lon,lat,b,length/2);e,n=t.transform(lo,la);ends.append((inv@np.array([e,n,1]))[:2])
                ends=np.array(ends);v=ends[1]-ends[0];v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]]);distance=(xy-ends.mean(axis=0))@normal
                reference=geodesic_bearing((np.c_[ends,np.ones(2)]@sm.T)[:,:2],epsg)[0]
                for noise in [0.,.02,.08]:
                    for feature in ['edge','ridge','trough']:
                        signal=ndtr(distance/1.5) if feature=='edge' else np.exp(-distance**2/(2*1.5**2))*(1 if feature=='ridge' else -1)
                        for rep in range(3):
                            a=.3+.4*signal+rng.normal(0,noise,size=distance.shape)
                            # Sentinel-like integer radiometry keeps all working
                            # rasters compact. This 1e-4 intensity quantum is
                            # included in the array that is actually fitted.
                            packed=np.rint(a*10000).astype('int16');a=packed.astype(float)/10000
                            picks=ends+rng.normal(0,.4,size=(2,2));stem=f'{location}-{bearing}-{length}-{noise}-{feature}-{rep}'
                            try:
                                fit=refine(a,picks,4,feature);p=np.c_[fit['endpoints'],np.ones(2)]@sm.T;az=geodesic_bearing(p[:,:2],epsg)[0];res=delta(az,reference)
                                row=dict(location=location,bearing=bearing,length_m=length,noise=noise,feature=feature,rep=rep,residual_deg=res,sigma_deg=fit['sigma_deg'])
                            except Exception as e:row=dict(location=location,bearing=bearing,length_m=length,noise=noise,feature=feature,rep=rep,failure=str(e))
                            detailed.append(row);groups[(length,noise)].append(row)
        # Exercise render crop, labelled grid, source hash, upsampling and the CLI's measurement path.
        # Profile trials stay in memory; only the final example per location is
        # written to exercise the file-based render and measurement path.
        path=work/(location+'-example.tif')
        check_space(path,packed.nbytes+10000)
        with rasterio.open(path,'w',driver='GTiff',width=201,height=201,count=1,dtype='int16',crs=f'EPSG:{epsg}',transform=tr,compress='deflate',predictor=2) as ds:ds.write(packed,1);ds.set_band_description(1,'brightness');ds.scales=(.0001,)
        render_source=path;out=work/(location+'-render.png');side=render_image(render_source,out,[lat,lon],size=1500,layer='brightness',upsample=3,grid=200,edge=True)
        png_ends=(np.c_[ends,np.ones(2)]@sm.T)@np.linalg.inv(np.asarray(side['pixel_to_utm'])).T
        pick=dict(source_id='synthetic',lines=[dict(id='line',endpoints_px=png_ends[:,:2].tolist(),mode='manual',pick_sigma_px=1,feature='edge')])
        got=measure(pick,side)['lines'][0];err=delta(got['bearing_deg'],reference)
        grid_bearing=math.degrees(math.atan2(*(np.diff((np.c_[ends,np.ones(2)]@sm.T)[:,:2],axis=0)[0])))%360
        checks.append(dict(name='imagery transform and geodesic '+location,error_deg=err,grid_true_difference_deg=delta(grid_bearing,reference),pass_=abs(err)<1e-8 and (location!='far-central-meridian' or abs(delta(grid_bearing,reference))>.5)))
    aggregates=[]
    for (length,noise),rows in sorted(groups.items()):
        ok=[r for r in rows if 'residual_deg' in r];v=np.array([r['residual_deg'] for r in ok]);ratio=np.array([r['residual_deg']/r['sigma_deg'] for r in ok]);rms=float(np.sqrt(np.mean(v*v)))
        aggregates.append(dict(length_m=length,noise_sd=noise,n=len(ok),failures=len(rows)-len(ok),bias_deg=float(v.mean()),rms_deg=rms,standardized_rms=float(np.sqrt(np.mean(ratio*ratio)))))
        limit=12 if length==50 else 6 if length==100 else 3
        checks.append(dict(name=f'profile recovery length {length} noise {noise}',rms_deg=rms,limit_deg=limit,pass_=rms<limit and len(ok)==len(rows)))
    # Synthetic plan with a rotated arrow; y increases downwards.
    image=Image.new('L',(1000,1000),255);draw=ImageDraw.Draw(image)
    def segment(angle,centre,length):
        v=np.array([math.sin(math.radians(angle)),-math.cos(math.radians(angle))])*length/2
        return [list(np.asarray(centre)-v),list(np.asarray(centre)+v)]
    north=segment(31,[200,200],200);line=segment(51,[600,500],400)
    draw.line([tuple(q) for q in north],fill=0,width=5);draw.line([tuple(q) for q in line],fill=0,width=5)
    source=work/'synthetic-plan.png';image.save(source);side=render_plan(source,work/'synthetic-plan-render.png',dpi=72,grid=100)
    for magnetic in [False,True]:
        north_data=dict(class_='magnetic' if magnetic else 'true',evidence='Constructed north arrow',survey_year=1925,line=dict(endpoints_px=north,mode='manual',pick_sigma_px=.5,feature='ridge'))
        north_data['class']=north_data.pop('class_')
        picks=dict(source_id='synthetic-plan',north=north_data,scale=dict(endpoints_px=[[100,900],[500,900]],length_m=200),location=[45.,-75.],igrf_coefficients=str(coefficients),lines=[dict(id='test',endpoints_px=line,feature='trough',mode='manual',pick_sigma_px=.5)])
        result=measure(picks,side);r=result['lines'][0];expected=20+(field(45,-75,1925,coefficients=coefficients)['declination_deg'] if magnetic else 0)
        checks.append(dict(name='plan relative bearing '+('magnetic' if magnetic else 'true'),raw_deg=r['bearing_raw_deg'],corrected_deg=r['bearing_deg'],expected_deg=expected,pass_=abs(delta(r['bearing_deg'],expected,360))<1e-9 and abs(r['length_m']-200)<1e-9))
        if not magnetic:
            picks['north']['line'].update(mode='fit',feature='trough',corridor_half_width_px=6)
            picks['lines'][0].update(mode='fit',feature='trough',corridor_half_width_px=6)
            fitted=measure(picks,side)['lines'][0]
            checks.append(dict(name='plan fitted shafts and downward row sign',error_deg=delta(fitted['bearing_deg'],20,360),pass_=abs(delta(fitted['bearing_deg'],20,360))<.2))
    synthetic_lines=[dict(id='a',length_m=100,theta_deg=1,sigma_deg=.4,endpoints_utm=[[0,0],[100,0]],part='one'),dict(id='b',length_m=300,theta_deg=3,sigma_deg=.5,endpoints_utm=[[100,20],[400,20]],part='one')]
    s=summarize(synthetic_lines);expected=max(math.sqrt((100*1.5**2+300*.5**2)/400)/math.sqrt(2),math.sqrt(100**2*.4**2+300**2*.5**2)/400,.3)
    checks.append(dict(name='system exact mean and standard error',pass_=abs(s['theta_deg']-2.5)<1e-12 and abs(s['se_deg']-expected)<1e-12 and s['conditions_pass']))
    bad=[dict(r) for r in synthetic_lines];bad[1]['theta_deg']=8;bad[1]['endpoints_utm']=[[800,800],[900,800]]
    checks.append(dict(name='system rejects 200 m and 6 degree failures',pass_=len(summarize(bad)['warnings'])>=2))
    checks.append(dict(name='fold endpoints and downward image sign',pass_=fold(-45)==45 and fold(45)==45 and fold(20)==20 and fold(-20)==-20))
    plan=np.array([[0,0],[100,0],[0,100],[150,150]],float);a,b=2*math.cos(.3),2*math.sin(.3);matrix=np.array([[a,b],[b,-a]]);q=plan@matrix.T+[600000,3000000]
    reg=register(dict(epsg=32642,controls=[dict(plan_px=p.tolist(),utm=t.tolist()) for p,t in zip(plan,q)],control_sigma_m=1))
    checks.append(dict(name='similarity covariance and leave-one-out',pass_=abs(reg['scale_m_per_pixel']-2)<1e-9 and abs(reg['rotation_deg']-math.degrees(.3))<1e-9 and reg['rms_m']<1e-6 and len(reg['leave_one_out'])==4 and reg['rotation_error_deg']>0))
    detail=work/'synthetic-detail.json';write_json(detail,detailed)
    checks.append(dict(name='synthetic scratch below 50 MB',bytes=sum(p.stat().st_size for p in work.rglob('*') if p.is_file()),pass_=sum(p.stat().st_size for p in work.rglob('*') if p.is_file())<50_000_000))
    return dict(aggregates=aggregates,cases=len(detailed),checks=[{('pass' if k=='pass_' else k):v for k,v in c.items()} for c in checks])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--work',required=True);p.add_argument('--coefficients',required=True);a=p.parse_args()
    if Path(a.output).exists():raise FileExistsError(a.output)
    r=run(a.work,a.coefficients);write_json(a.output,dict(schema_version=1,task='town-orientation-measurement-tools',synthetic=True,provenance=dict(code_hashes=code_hashes(),coefficients_sha256=sha256(a.coefficients),seed=10212026),**r,overall_pass=all(c['pass'] for c in r['checks'])));print('overall_pass',all(c['pass'] for c in r['checks']))
if __name__=='__main__':main()
