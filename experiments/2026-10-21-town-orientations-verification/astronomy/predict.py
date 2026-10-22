"""Predict deviations and rates, or regenerate a town's complete time table."""
from pathlib import Path
import sys,json,csv
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
from records import *
from horizon import profile,horizon_at

def validation_gate():
    p=OUT/'validation-v1.json'
    data=json.loads(p.read_text())
    if not data['all_pass']: raise RuntimeError('astronomy validation did not pass')
    for code,digest in data['provenance']['code'].items():
        if sha(code)!=digest: raise RuntimeError('code changed since validation: '+code)

def theta(target,lat,lon,year,extinction_variant='base',horizon_variant='dem',profile_data=None):
    if target not in TARGETS: raise ValueError(target)
    if extinction_variant not in ('base','k020','k045','none'): raise ValueError(extinction_variant)
    if horizon_variant not in ('dem','flat'): raise ValueError(horizon_variant)
    setting=not target.endswith('rise')
    data=profile_data
    if horizon_variant=='dem' and data is None: data=profile(lat,lon)
    dec=declination(target,float(year))
    az=azimuth(dec,lat,setting=setting)
    for _ in range(200):
        horizon=0 if horizon_variant=='flat' else horizon_at(data,az)
        if target in MAGS:
            ha=horizon if extinction_variant=='none' else max(horizon,extinction(target,{'base':.30,'k020':.20,'k045':.45}[extinction_variant]))
        else: ha=horizon-.267
        new=azimuth(dec,lat,ha-refraction(ha),setting)
        if not math.isfinite(new): return float('nan')
        if abs(new-az)<.001: return new-(270 if setting else 90)
        az=new
    raise RuntimeError('azimuth/horizon iteration failed')

def predict(target,lat,lon,year,extinction_variant='base',horizon_variant='dem',profile_data=None):
    """Return (theta degrees, central-difference rate degrees/year at D +/-50).

    The caller can reuse a profile dictionary for a town. CLI calls check the
    frozen validation record; library callers should call validation_gate once.
    """
    data=profile_data
    if horizon_variant=='dem' and data is None: data=profile(lat,lon)
    args=dict(extinction_variant=extinction_variant,horizon_variant=horizon_variant,profile_data=data)
    t=theta(target,lat,lon,year,**args)
    rate=(theta(target,lat,lon,year+50,**args)-theta(target,lat,lon,year-50,**args))/100
    return t,rate

def table_rows(slug,lat,lon):
    data=profile(lat,lon)
    variants=[('base','base','dem'),('k020','k020','dem'),('k045','k045','dem'),('no_extinction','none','dem'),('flat','base','flat')]
    for year in range(-3499,-1498,10):
        for target in TARGETS:
            row=dict(slug=slug,lat=lat,lon=lon,year=year,target=target)
            for label,ext,hor in variants:
                t,r=predict(target,lat,lon,year,ext,hor,data)
                row['theta_'+label]=format(t,'.12f') if math.isfinite(t) else ''
                row['rate_'+label]=format(r,'.12f') if math.isfinite(r) else ''
            yield row

def write_table(slug,lat,lon,output):
    p=Path(output); meta=p.with_name(p.name+'.provenance.json')
    if p.exists() or meta.exists(): raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    rows=table_rows(slug,lat,lon); first=next(rows)
    with p.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(first),lineterminator='\n'); w.writeheader(); w.writerow(first); w.writerows(rows)
    # Locate the exact profile already cached by table_rows.
    data=profile(lat,lon)
    hp=next(x for x in (OUT/'horizon').glob('*.json') if json.loads(x.read_text())['lat']==lat and json.loads(x.read_text())['lon']==lon)
    codes=[Path(__file__),Path(__file__).with_name('core.py'),Path(__file__).with_name('horizon.py')]
    write_json(meta,'predicted-deviation-table',dict(provisional=True,slug=slug,lat=lat,lon=lon,
        csv_sha256=sha(p),rows=1809,year_range=[-3499,-1499],step_years=10,
        rate_definition='central difference at D +/-50 Julian years, degrees per year',
        deviation_definition='A-270 setting; A-90 rising, every solar target included'),
        inputs=[OUT/'stars-retrieved-v1.json',OUT/'validation-v1.json',hp],codes=codes)

def theta_many(target,lat,lon,years,extinction_variant='base',horizon_variant='dem',profile_data=None):
    """Vector form of theta for independent normal date draws in power runs.

    All years are evaluated directly by the long-term model; no interpolation
    or local rate approximation is made. Scalar agreement is self-tested.
    """
    years=np.asarray(years,dtype=float)
    if target not in MAGS: return np.array([theta(target,lat,lon,float(y),extinction_variant,horizon_variant,profile_data) for y in years])
    t=(years-2000)/100
    phase=2*np.pi*t[:,None]/EQPER[:,0]
    xy=(np.column_stack([np.ones_like(t),t,t*t,t*t*t]) @ EQPOL.T+
        np.cos(phase) @ EQPER[:,1:3]+np.sin(phase) @ EQPER[:,3:5])*AS
    pole=np.column_stack([xy,np.sqrt(np.maximum(0,1-np.sum(xy*xy,axis=1)))])
    s=stars()[target]; ra,dec=np.array([s['ra'],s['dec']])*RAD
    unit=np.array([math.cos(dec)*math.cos(ra),math.cos(dec)*math.sin(ra),math.sin(dec)])
    east=np.array([-math.sin(ra),math.cos(ra),0])
    north=np.array([-math.sin(dec)*math.cos(ra),-math.sin(dec)*math.sin(ra),math.cos(dec)])
    dist=1/(s['plx_value']*.001*AS)
    vt=dist*(s['pmra']*east+s['pmdec']*north)*.001*AS/365.25
    bs=s['rvz_radvel']*1000*86400/AU/C; bt=np.linalg.norm(vt)/C
    br,btr=bs,bt
    for _ in range(100):
        d=1+br; w=br*br+btr*btr; delta=-w/(math.sqrt(1-w)+1)
        nr=d*bs+delta; nt=d*bt
        if abs(nr-br)+abs(nt-btr)<1e-17: break
        br,btr=nr,nt
    vel=d*vt+C*(d*bs+delta)*unit
    dt=(years-2000)*365.25; tl1=dist/C
    geom=dist*unit+(dt+tl1)[:,None]*vel
    rdv=geom @ vel; c2=C*C-vel @ vel
    tl2=(-rdv+np.sqrt(rdv*rdv+c2*np.sum(geom*geom,axis=1)))/c2
    obs=dist*unit+(dt+tl1-tl2)[:,None]*vel
    obs/=np.linalg.norm(obs,axis=1)[:,None]
    dx,de,dr=np.array([-.016617,-.0068192,-.0146])*AS
    bias=np.array([[1,dr,-dx],[-dr,1,-de],[dx,de,1]])
    sine=np.sum((obs @ bias.T)*pole,axis=1)
    dec=np.arcsin(np.clip(sine,-1,1))
    phi=lat*RAD
    def angles(h):
        h=np.asarray(h)*RAD
        c=(np.sin(dec)-math.sin(phi)*np.sin(h))/(math.cos(phi)*np.cos(h))
        return 360-np.rad2deg(np.arccos(np.where(np.abs(c)<=1,c,np.nan)))
    az=angles(0)
    data=profile_data
    if horizon_variant=='dem' and data is None: data=profile(lat,lon)
    if extinction_variant not in ('base','k020','k045','none'): raise ValueError(extinction_variant)
    if horizon_variant not in ('dem','flat'): raise ValueError(horizon_variant)
    for _ in range(200):
        if horizon_variant=='dem':
            if np.any(~(((45<=az)&(az<=135))|((225<=az)&(az<=315)))): raise ValueError('azimuth coverage')
            h=np.interp(az,data['azimuth_deg'],data['apparent_altitude_deg'])
        else: h=np.zeros_like(az)
        if extinction_variant!='none': h=np.maximum(h,extinction(target,{'base':.30,'k020':.20,'k045':.45}[extinction_variant]))
        true=h-(283/293)/np.tan(np.deg2rad(h+7.31/(h+4.4)))/60
        new=angles(true)
        if np.all(np.abs(new-az)<.001): return new-270
        az=new
    raise RuntimeError('vector horizon convergence')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--target',choices=TARGETS); ap.add_argument('--lat',type=float,required=True)
    ap.add_argument('--lon',type=float,required=True); ap.add_argument('--year',type=float)
    ap.add_argument('--extinction',choices=['base','k020','k045','none'],default='base')
    ap.add_argument('--horizon',choices=['dem','flat'],default='dem')
    ap.add_argument('--table',action='store_true'); ap.add_argument('--slug')
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args(); validation_gate()
    if a.table: write_table(a.slug,a.lat,a.lon,a.output)
    else:
        if not a.target or a.year is None: ap.error('--target and --year required')
        if a.output.exists(): raise FileExistsError(a.output)
        t,r=predict(a.target,a.lat,a.lon,a.year,a.extinction,a.horizon)
        inputs=[OUT/'stars-retrieved-v1.json',OUT/'validation-v1.json']
        write_json(a.output,'predicted-deviation',dict(target=a.target,lat=a.lat,lon=a.lon,
            year=a.year,theta_deg=t,rate_deg_per_year=r,extinction=a.extinction,horizon=a.horizon),
            inputs=inputs,codes=[__file__,Path(__file__).with_name('core.py'),Path(__file__).with_name('horizon.py')])
