"""Refine picked edges, ridges or troughs and return bearings with conditional errors.

Pixel coordinates have x to the right and y downward. Imagery bearings use the
circular mean of the WGS84 forward and reversed backward geodesic azimuths.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,math
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter1d
import rasterio
from common import read_json,write_json,sha256,affine_points,geodesic_bearing,pixel_bearing,fold,code_hashes
from render_plan import page_image

def refine(array,endpoints,corridor,feature="edge",mode="fit",pick_sigma=None):
    """Fit a line in native pixel coordinates; errors include a 0.1 pixel floor.

    Profiles are spaced at least 3 native pixels where length permits. The
    number of independent samples is capped at length/3, reflecting blur.
    """
    p=np.asarray(endpoints,float);vec=p[1]-p[0];length=np.linalg.norm(vec)
    if length<=0:raise ValueError("coincident endpoints")
    if mode=="manual":
        if pick_sigma is None or pick_sigma<=0:raise ValueError("manual mode requires positive pick_sigma_px")
        error=math.degrees(math.atan(math.sqrt(2)*pick_sigma/length))
        return dict(endpoints=p.tolist(),inlier_count=2,profile_count=0,residual_rms_px=None,length_px=float(length),sigma_fit_deg=error,sigma_deg=error,mode="manual",pick_sigma_px=pick_sigma)
    if feature not in ["edge","ridge","trough"]:raise ValueError("unknown feature")
    if corridor<1:raise ValueError("corridor must span at least one source pixel")
    direction=vec/length;normal=np.array([-direction[1],direction[0]])
    # Short, blurred features need enough candidate profiles for a consensus.
    # Oversampling does not add independent observations: neff stays capped
    # by length/3 below, including when fewer than three source pixels separate
    # adjacent profiles.
    count=max(12,int(length/3)+1);t=np.linspace(0,length,count);centres=p[0]+t[:,None]*direction
    offsets=np.arange(-corridor,corridor+.05,.25)
    xy=centres[:,None,:]+offsets[None,:,None]*normal
    values=map_coordinates(np.asarray(array,float),[xy[:,:,1],xy[:,:,0]],order=1,mode="constant",cval=np.nan)
    good=np.isfinite(values).all(axis=1);centres=centres[good];values=values[good]
    if len(values)<4:raise ValueError("too few profiles inside source extent")
    # A quarter-pixel sampling grid needs a four-sample smoothing scale.
    # Without it, differentiating bilinear samples locks edges to pixel phases.
    values=gaussian_filter1d(values,4.,axis=1)
    scores=np.abs(np.gradient(values,offsets,axis=1)) if feature=="edge" else (values if feature=="ridge" else -values)
    pts=[];strength=[]
    for centre,score in zip(centres,scores):
        k=int(np.argmax(score))
        if k<2 or k>=len(offsets)-2:continue
        a,b,c=score[k-1:k+2];den=a-2*b+c
        sub=float(np.clip(.5*(a-c)/den,-1,1)) if abs(den)>1e-15 else 0.
        pts.append(centre+(offsets[k]+sub*.25)*normal);strength.append(float(b-np.median(score)))
    pts=np.asarray(pts)
    if len(pts)<4:raise ValueError("feature peaks hit corridor boundary; refine picks or corridor")
    # Deterministic RANSAC, scored by consensus then residual, followed by TLS.
    rng=np.random.default_rng(61413);best=None
    for _ in range(256):
        i,j=rng.choice(len(pts),2,replace=False);v=pts[j]-pts[i]
        if np.linalg.norm(v)<1:continue
        v=v/np.linalg.norm(v)
        if abs(np.dot(v,direction))<.85:continue
        n=np.array([-v[1],v[0]]);d=np.abs((pts-pts[i])@n);mask=d<=1.
        score=(int(mask.sum()),-float(np.sum(d[mask]**2)))
        if best is None or score>best[0]:best=(score,mask)
    if best is None or best[1].sum()<4:raise ValueError("line has fewer than four inlier profiles")
    mask=best[1]
    for _ in range(4):
        q=pts[mask];centre=q.mean(axis=0);_,_,vh=np.linalg.svd(q-centre,full_matrices=False);v=vh[0]
        if np.dot(v,direction)<0:v=-v
        n=np.array([-v[1],v[0]]);res=(pts-centre)@n
        rms=float(np.sqrt(np.mean(res[mask]**2)));new=np.abs(res)<=max(.5,min(1.5,3*rms))
        if new.sum()<4 or np.array_equal(mask,new):break
        mask=new
    q=pts[mask];centre=q.mean(axis=0);_,_,vh=np.linalg.svd(q-centre,full_matrices=False);v=vh[0]
    if np.dot(v,direction)<0:v=-v
    n=np.array([-v[1],v[0]]);res=(q-centre)@n;rms=float(np.sqrt(np.mean(res**2)))
    along=(q-centre)@v;sxx=float(np.sum((along-along.mean())**2));neff=max(2.,min(len(q),length/3))
    fitted=np.stack([centre+v*np.dot(p[k]-centre,v) for k in range(2)])
    fit_sigma=math.degrees(math.sqrt(float(np.sum(res**2))/max(len(q)-2,1)/max(sxx,1e-12))*math.sqrt(len(q)/neff))
    floor=math.degrees(math.atan(math.sqrt(2)*.1/length))
    return dict(endpoints=fitted.tolist(),inlier_count=int(mask.sum()),profile_count=len(pts),residual_rms_px=rms,length_px=float(np.linalg.norm(fitted[1]-fitted[0])),sigma_fit_deg=fit_sigma,sigma_deg=max(fit_sigma,floor),sigma_floor_deg=floor,effective_profile_count=neff,mode="fit",warnings=(["Fewer than half of profiles are inliers"] if mask.sum()<len(pts)/2 else []))

def measure(picks,sidecar):
    side=read_json(sidecar) if isinstance(sidecar,(str,Path)) else sidecar
    source=side['source']
    if sha256(source)!=side['source_sha256']:raise ValueError("source hash differs from render sidecar")
    kind=side['kind'];results=[]
    if kind=='imagery':
        with rasterio.open(source) as ds:
            idx=picks.get('band',7 if ds.count>=7 else 1)
            array=ds.read(idx).astype(float)
            tr=ds.transform
            sm=np.array([[tr.a,tr.b,tr.c+(tr.a+tr.b)/2],[tr.d,tr.e,tr.f+(tr.d+tr.e)/2],[0,0,1]])
        mapping=np.linalg.inv(sm)@np.asarray(side['pixel_to_utm'])
    else:
        im,m=page_image(source,side.get('page',1),side.get('dpi',300),side.get('region'))
        array=np.asarray(im.convert('L'),float);mapping=np.linalg.inv(m)@np.asarray(side['pixel_to_source'])
    ratio=float(np.sqrt(abs(np.linalg.det(mapping[:2,:2]))))
    inverse=np.linalg.inv(mapping)
    def one(line):
        native=affine_points(mapping,line['endpoints_px'])
        fit=refine(array,native,line.get('corridor_half_width_px',3)*ratio,line.get('feature','edge'),line.get('mode','fit'),line.get('pick_sigma_px',0)*ratio)
        png=affine_points(inverse,fit['endpoints']);fit['refined_endpoints_px']=png.tolist();fit['native_endpoints_px']=fit.pop('endpoints')
        fit['residual_rms_render_px']=fit['residual_rms_px']/ratio if fit['residual_rms_px'] is not None else None
        return fit
    north=picks.get('north');arrow=None;metres_per_px=None;declination=None
    if kind=='plan':
        if not north or north.get('class') not in ['true','magnetic','grid','unspecified']:raise ValueError("plan requires north class, evidence, and tail-to-tip picks")
        if not north.get('evidence'):raise ValueError("north evidence is required")
        arrow=one(north['line']);arrow['direction_px_deg']=pixel_bearing(arrow['refined_endpoints_px'])
        scale=picks.get('scale')
        if not scale or scale.get('length_m',0)<=0:raise ValueError("plan requires two scale-bar endpoints and positive length_m")
        metres_per_px=scale['length_m']/np.linalg.norm(np.diff(np.asarray(scale['endpoints_px']),axis=0))
        if north['class']=='magnetic' and north.get('survey_year') is not None and north['survey_year']>=1900 and picks.get('location'):
            from igrf import field
            declination=field(*picks['location'],north['survey_year'],coefficients=picks['igrf_coefficients'])['declination_deg']
    for line in picks['lines']:
        fit=one(line);row={**line,**fit}
        if kind=='imagery':
            xy=affine_points(sm,fit['native_endpoints_px']);bearing,length,geographic=geodesic_bearing(xy,side['epsg'])
            row.update(endpoints_utm=xy.tolist(),epsg=side['epsg'],endpoints_lonlat=geographic,length_m=length,bearing_deg=bearing)
        else:
            raw=(pixel_bearing(fit['refined_endpoints_px'])-arrow['direction_px_deg'])%360
            row.update(bearing_raw_deg=raw,bearing_deg=(raw+(declination or 0))%360,declination_deg=declination,length_m=fit['length_px']/ratio*metres_per_px,sigma_line_deg=fit['sigma_deg'],sigma_arrow_deg=arrow['sigma_deg'],sigma_deg=math.hypot(fit['sigma_deg'],arrow['sigma_deg']),north_class=north['class'],endpoints_plan_m=(np.asarray(fit['refined_endpoints_px'])*metres_per_px).tolist())
            row['north_correction_status']='IGRF-14 applied' if declination is not None else ('true arrow' if north['class']=='true' else 'true reference unresolved; retain raw bearing')
        row['theta_deg']=fold(row['bearing_deg']);results.append(row)
    return dict(schema_version=1,source_id=picks['source_id'],kind=kind,source=source,source_sha256=side['source_sha256'],render_sidecar=sidecar if isinstance(sidecar,str) else None,north=north,arrow=arrow,metres_per_render_pixel=metres_per_px,lines=results,provenance=code_hashes(),error_scope='Conditional line fit and arrow measurement. Survey, map distortion, pixel registration, feature identification and IGRF model error are not included. See empirical validation.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('picks');p.add_argument('sidecar');p.add_argument('output');a=p.parse_args();write_json(a.output,measure(read_json(a.picks),a.sidecar))
if __name__=='__main__':main()
