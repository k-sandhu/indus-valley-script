"""Validation-only use of ERFA and astropy; production code imports neither."""
from pathlib import Path
import sys,os,json,re,math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *
(RAW/'astropy-cache').mkdir(parents=True,exist_ok=True)
(RAW/'astropy-config').mkdir(parents=True,exist_ok=True)
os.environ['ASTROPY_CACHE_DIR']=str(RAW/'astropy-cache')
os.environ['ASTROPY_CONFIG_DIR']=str(RAW/'astropy-config')
from core import *
import erfa
from scipy.optimize import minimize_scalar,brentq
import astropy.units as u
from astropy.coordinates import SkyCoord,EarthLocation,AltAz
from astropy.time import Time
from astropy.utils import iers
iers.conf.auto_download=False

def separation(a,b):
    return math.atan2(np.linalg.norm(np.cross(a,b)),np.dot(a,b))/RAD

def validate():
    ob=obliquity(-2499)
    opt=minimize_scalar(lambda y:90-declination('thuban',float(y)),bounds=(-3100,-2500),method='bounded',options={'xatol':1e-8})
    th={'astronomical_year':float(opt.x),'BCE_year':1-float(opt.x),'polar_distance_deg':float(opt.fun),'pass':2700<=1-opt.x<=2900}
    wanzke=[]
    for year,w in [(-2499,-2.70),(-1499,3.42)]:
        a=azimuth(declination('aldebaran',year),27.329)
        wanzke.append(dict(year=year,azimuth_deg=a,theta_deg=a-270,wanzke_theta_deg=w,wanzke_gon=w/.9,difference_deg=a-270-w))
    # Extract only numeric test literals as data. No downloaded code is evaluated.
    text=(RAW/'erfa/t_erfa_c.c').read_text()
    vectors={}
    for name,func in [('ltpequ',ltpequ),('ltpecl',ltpecl),('ltpb',ltpb)]:
        section=text.split('static void t_'+name+'(')[1].split('\nstatic void ')[0]
        epoch=float(re.search(r'epj\s*=\s*([-\d.]+);',section)[1])
        pairs=re.findall(r'vvd\([^,]+,\s*([-+\deE.]+),\s*([-+\deE.]+)',section)
        expected=np.array([float(x[0]) for x in pairs]); tolerance=np.array([float(x[1]) for x in pairs])
        actual=func(epoch).ravel(); dif=np.abs(actual-expected)
        vectors[name]=dict(epoch=epoch,actual=actual,expected=expected,tolerances=tolerance,
                           absolute_differences=dif,max_absolute_difference=float(max(dif)),pass_=bool(np.all(dif<=tolerance)))
    erfa_checks={}
    for name in MAGS:
        s=stars()[name]; ra=s['ra']*RAD; dec=s['dec']*RAD
        r,d,*_=erfa.pmsafe(ra,dec,s['pmra']*.001*AS/math.cos(dec),s['pmdec']*.001*AS,s['plx_value']*.001,s['rvz_radvel'],2451545.,0.,2451545.,365.25*(-2499-2000))
        ref=erfa.ltpb(-2499) @ np.array([math.cos(d)*math.cos(r),math.cos(d)*math.sin(r),math.sin(d)])
        dif=separation(direction(name,-2499),ref)
        erfa_checks[name]={'difference_deg':dif,'pass':dif<.001,'own_direction':direction(name,-2499),'reference_direction':ref}
    astropy_checks={}
    loc=EarthLocation(lat=27.329*u.deg,lon=68.138*u.deg,height=0*u.m)
    start=Time('2026-10-21T00:00:00',scale='utc')
    for name in MAGS:
        s=stars()[name]
        c=SkyCoord(ra=s['ra']*u.deg,dec=s['dec']*u.deg,
          pm_ra_cosdec=s['pmra']*u.mas/u.yr,pm_dec=s['pmdec']*u.mas/u.yr,
          distance=(1000/s['plx_value'])*u.pc,radial_velocity=s['rvz_radvel']*u.km/u.s,
          obstime=Time(2000.,format='jyear',scale='tt'),frame='icrs')
        def observed(seconds):
            t=start+seconds*u.s
            moving=c.apply_space_motion(new_obstime=t)
            return moving.transform_to(AltAz(obstime=t,location=loc,pressure=0*u.hPa))
        grid=np.arange(0,86400+600,600); alt=[observed(float(t)).alt.deg for t in grid]
        brackets=[(grid[i],grid[i+1]) for i in range(len(grid)-1) if alt[i]>0>=alt[i+1]]
        if len(brackets)!=1: raise ValueError('setting bracket count')
        root=brentq(lambda t:observed(t).alt.deg,*brackets[0],xtol=1e-5)
        at=observed(root); epoch=float((start+root*u.s).tt.jyear)
        own=azimuth(declination(name,epoch),27.329)
        dif=own-float(at.az.deg)
        astropy_checks[name]=dict(own_azimuth_deg=own,astropy_azimuth_deg=float(at.az.deg),difference_deg=dif,
            setting_utc=(start+root*u.s).utc.isot,epoch_tt=epoch,pass_=abs(dif)<.02)
    refr=[]
    for h in [0,1,2,5]:
        expected=(283/293)/np.tan(np.deg2rad(h+7.31/(h+4.4)))/60
        got=refraction(h)
        refr.append(dict(apparent_altitude_deg=h,refraction_arcmin=got*60,formula_arcmin=expected*60,
                         difference_arcmin=(got-expected)*60,pass_=abs(got-expected)<1e-12))
    html=(RAW/'kasten-young-1989.html').read_text(encoding='utf-8')
    rows={}
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',html,re.S):
        cells=[re.sub('<[^>]+>','',c).strip() for c in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.S)]
        if len(cells)>=3:
            try: rows[float(cells[0])]=float(cells[2])
            except ValueError: pass
    air=[]
    for z in [0,60,85,90]:
        table=rows[90-z]; got=airmass(z); relative=(got/table-1)*100
        # Formula is an approximation to the ray-integrated Table II.
        air.append(dict(zenith_distance_deg=z,formula_airmass=got,table_II_airmass=table,
                    difference=got-table,relative_error_percent=relative,tolerance_relative_percent=.5,pass_=abs(relative)<.5))
    passed=abs(ob-23.97)<=.02 and th['pass'] and all(x['pass_'] for x in vectors.values()) and all(x['pass'] for x in erfa_checks.values()) and all(x['pass_'] for x in astropy_checks.values()) and all(x['pass_'] for x in refr+air)
    return dict(all_pass=passed,obliquity=dict(year=-2499,degrees=ob,reference_deg=23.97,tolerance_deg=.02,pass_=abs(ob-23.97)<=.02),
       thuban=th,aldebaran_wanzke=wanzke,erfa_vectors=vectors,pyerfa_positions=erfa_checks,
       astropy_setting=astropy_checks,bennett=refr,kasten_young=air,
       extinction_angles_deg={n:extinction(n) for n in MAGS},
       igrf='Outside this assignment; no magnetic correction is implemented or validated here.',
       source_exception= json.loads((OUT/'stars-retrieved-v1.json').read_text())['thuban_coordinate_exception'])

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path); a=ap.parse_args()
    if a.output and a.output.exists(): raise FileExistsError(a.output)
    result=validate()
    if a.output:
        inputs=[OUT/'stars-retrieved-v1.json',RAW/'erfa/t_erfa_c.c',RAW/'kasten-young-1989.html']
        write_json(a.output,'astronomy-validation',result,inputs=inputs,codes=[__file__,Path(__file__).with_name('core.py')])
    print(json.dumps(clean(result),indent=2))
    if not result['all_pass']: raise SystemExit(1)
