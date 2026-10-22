"""Fit a similarity from plan pixels (y down) to UTM, with uncertainty and LOO."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,math
import numpy as np
from pyproj import Transformer
from common import read_json,write_json,GEOD,delta

def solve(p,q,sigma=None):
    # Remove large coordinate offsets before least squares so UTM northings
    # cannot consume the precision of the rotation and scale coefficients.
    pc=p.mean(axis=0);qc=q.mean(axis=0)
    x,y=(p-pc).T;A=np.zeros((2*len(p),4));A[::2]=np.c_[x,y,np.ones(len(p)),np.zeros(len(p))];A[1::2]=np.c_[-y,x,np.zeros(len(p)),np.ones(len(p))]
    # E=a*x+b*y+tx, N=b*x-a*y+ty.
    z=(q-qc).ravel();coef,_,rank,_=np.linalg.lstsq(A,z,rcond=None)
    if rank<4:raise ValueError('control geometry cannot determine a similarity')
    a,b,tcx,tcy=coef;tx=qc[0]+tcx-a*pc[0]-b*pc[1];ty=qc[1]+tcy-b*pc[0]+a*pc[1]
    fitted=(A@coef).reshape(-1,2)+qc;res=q-fitted;dof=2*len(p)-4
    if a*a+b*b<1e-20:raise ValueError('controls imply zero transform scale')
    variance=float(np.sum(res**2)/dof) if dof>0 else None
    if sigma is not None:variance=max(variance or 0,sigma**2)
    error=None;cov=None
    if variance is not None:
        cov=variance*np.linalg.inv(A.T@A);gradient=np.array([-b,a,0,0])/(a*a+b*b)
        error=math.degrees(math.sqrt(max(0,float(gradient@cov@gradient))))
        change=np.array([[1,0,0,0],[0,1,0,0],[-pc[0],-pc[1],1,0],[pc[1],-pc[0],0,1]])
        cov=change@cov@change.T
    return dict(matrix=[[float(a),float(b),float(tx)],[float(b),float(-a),float(ty)],[0,0,1]],rotation_deg=math.degrees(math.atan2(b,a)),scale_m_per_pixel=float(math.hypot(a,b)),residuals_m=res.tolist(),rms_m=float(np.sqrt(np.mean(np.sum(res**2,axis=1)))),rotation_covariance_error_deg=error,covariance=cov.tolist() if cov is not None else None)

def register(data):
    pairs=data['controls'];p=np.asarray([r['plan_px'] for r in pairs],float);q=np.asarray([r['utm'] for r in pairs],float)
    if len(p)<2:raise ValueError('two or more controls required')
    result=solve(p,q,data.get('control_sigma_m'));loos=[]
    if len(p)>=3:
        for i in range(len(p)):
            mask=np.arange(len(p))!=i
            try:
                fit=solve(p[mask],q[mask]);m=np.asarray(fit['matrix']);prediction=(m@np.r_[p[i],1])[:2]
                loos.append(dict(omitted=i,rotation_deg=fit['rotation_deg'],rotation_delta_deg=delta(fit['rotation_deg'],result['rotation_deg'],360),omitted_residual_m=(q[i]-prediction).tolist()))
            except ValueError as e:loos.append(dict(omitted=i,failure=str(e)))
    rot=[r['rotation_delta_deg'] for r in loos if 'rotation_delta_deg' in r]
    # Jackknife rotation SE is sqrt((n-1)/n sum (leave-one-out - mean)^2).
    looerror=float(np.sqrt((len(rot)-1)/len(rot)*np.sum((np.asarray(rot)-np.mean(rot))**2))) if len(rot)>1 else None
    e,n=q.mean(axis=0);to_geo=Transformer.from_crs(data['epsg'],4326,always_xy=True);lon,lat=to_geo.transform(e,n);lon2,lat2,_=GEOD.fwd(lon,lat,0,100)
    e2,n2=Transformer.from_crs(4326,data['epsg'],always_xy=True).transform(lon2,lat2)
    v=np.linalg.inv(np.asarray(result['matrix'])[:2,:2])@np.array([e2-e,n2-n]);v=v/np.linalg.norm(v)
    return dict(schema_version=1,epsg=data['epsg'],controls=pairs,**result,leave_one_out=loos,rotation_loo_error_deg=looerror,rotation_error_deg=max([e for e in [result['rotation_covariance_error_deg'],looerror] if e is not None],default=None),true_north_plan_unit_vector=v.tolist(),true_north_plan_direction_deg=math.degrees(math.atan2(v[0],-v[1]))%360,warning='Two controls give an exact fit with no residual degrees of freedom; state control_sigma_m to estimate error.' if len(p)==2 and data.get('control_sigma_m') is None else None)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('controls');p.add_argument('output');a=p.parse_args();write_json(a.output,register(read_json(a.controls)))
if __name__=='__main__':main()
