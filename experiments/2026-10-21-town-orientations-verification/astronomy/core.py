"""Independent numerical implementation of the frozen astronomical definitions.

Vondrak, Capitaine & Wallace (2011, 2012) coefficients as published in
ERFA ltpequ/ltpecl; see LICENSE-ERFA.txt. ERFA is only imported by validate.py.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import math
import numpy as np
from functools import lru_cache
from records import OUT
import json
RAD=math.pi/180
AS=RAD/3600
AU=149597870700.0
C=299792458*86400/AU
TARGETS=('alcyone','aldebaran','procyon','equinox_set','equinox_rise',
         'june_set','june_rise','december_set','december_rise')
MAGS=dict(alcyone=2.87,aldebaran=.86,procyon=.34)
EQPOL=np.array([[5453.282155,.4252841,-.00037173,-.000000152],
                [-73750.930350,-.7675452,-.00018725,.000000231]])
EQPER=np.array([
[256.75,-819.940624,75004.344875,81491.287984,1558.515853],
[708.15,-8444.676815,624.033993,787.163481,7774.939698],
[274.20,2600.009459,1251.136893,1251.296102,-2219.534038],
[241.45,2755.175630,-1102.212834,-1257.950837,-2523.969396],
[2309.,-167.659835,-2660.664980,-2966.799730,247.850422],
[492.20,871.855056,699.291817,639.744522,-846.485643],
[396.10,44.769698,153.167220,131.600209,-1393.124055],
[288.90,-512.313065,-950.865637,-445.040117,368.526116],
[231.10,-819.415595,499.754645,584.522874,749.045012],
[1610.,-538.071099,-145.188210,-89.756563,444.704518],
[620.,-189.793622,558.116553,524.429630,235.934465],
[157.87,-402.922932,-23.923029,-13.549067,374.049623],
[220.30,179.516345,-165.405086,-210.157124,-171.330180],
[1200.,-9.814756,9.344131,-44.919798,-22.899655]])
ECLPOL=np.array([[5851.607687,-.1189000,-.00028913,.000000101],
                [-1600.886300,1.1689818,-.00000020,-.000000437]])
ECLPER=np.array([
[708.15,-5486.751211,-684.661560,667.666730,-5523.863691],
[2309.,-17.127623,2446.283880,-2354.886252,-549.747450],
[1620.,-617.517403,399.671049,-428.152441,-310.998056],
[492.20,413.442940,-356.652376,376.202861,421.535876],
[1183.,78.614193,-186.387003,184.778874,-36.776172],
[622.,-180.732815,-316.800070,335.321713,-145.278396],
[882.,-87.676083,198.296701,-185.138669,-34.744450],
[547.,46.140315,101.135679,-120.972830,22.885731]])

def _series(year,pol,per):
    t=(year-2000)/100
    phase=2*math.pi*t/per[:,0]
    return (pol @ np.array([1,t,t*t,t*t*t])+
            np.cos(phase) @ per[:,1:3]+np.sin(phase) @ per[:,3:5])*AS

def ltpequ(year):
    x,y=_series(year,EQPOL,EQPER)
    return np.array([x,y,math.sqrt(max(0,1-x*x-y*y))])

def ltpecl(year):
    p,q=_series(year,ECLPOL,ECLPER)
    w=math.sqrt(max(0,1-p*p-q*q)); eps=84381.406*AS
    return np.array([p,-q*math.cos(eps)-w*math.sin(eps),
                    -q*math.sin(eps)+w*math.cos(eps)])

@lru_cache(maxsize=100000)
def ltpb(year):
    pole=ltpequ(year)
    equinox=np.cross(pole,ltpecl(year)); equinox/=np.linalg.norm(equinox)
    precession=np.array([equinox,np.cross(pole,equinox),pole])
    dx,de,dr=np.array([-.016617,-.0068192,-.0146])*AS
    bias=np.array([[1,dr,-dx],[-dr,1,-de],[dx,de,1]])
    return precession @ bias

def obliquity(year):
    return math.acos(np.clip(np.dot(ltpequ(year),ltpecl(year)),-1,1))/RAD

@lru_cache()
def stars():
    return json.loads((OUT/'stars-retrieved-v1.json').read_text())['stars']

def space_direction(s,year):
    """Observed ICRS direction with inertial linear motion and light travel time.

    Convert catalogue rates into inertial velocity with the special relativistic
    correction used by starpv; solve the reception/emission time relation at the
    second epoch. Positive parallax and subrelativistic speed are required here.
    """
    ra,dec=np.array([s['ra'],s['dec']])*RAD
    if s['plx_value']<=0: raise ValueError('positive parallax required')
    u=np.array([math.cos(dec)*math.cos(ra),math.cos(dec)*math.sin(ra),math.sin(dec)])
    east=np.array([-math.sin(ra),math.cos(ra),0])
    north=np.array([-math.sin(dec)*math.cos(ra),-math.sin(dec)*math.sin(ra),math.cos(dec)])
    dist=1/(s['plx_value']*.001*AS)
    transverse=dist*(s['pmra']*east+s['pmdec']*north)*.001*AS/365.25
    radial=s['rvz_radvel']*1000*86400/AU
    bs=radial/C; bt=np.linalg.norm(transverse)/C
    br,btr=bs,bt
    for _ in range(100):
        d=1+br; w=br*br+btr*btr
        delta=-w/(math.sqrt(1-w)+1)
        nr=d*bs+delta; nt=d*bt
        if abs(nr-br)+abs(nt-btr)<1e-17: break
        br,btr=nr,nt
    velocity=d*transverse+C*(d*bs+delta)*u
    p=dist*u; dt=(year-2000)*365.25; tl1=dist/C
    geometric=p+velocity*(dt+tl1)
    rdv=np.dot(geometric,velocity); c2=C*C-np.dot(velocity,velocity)
    tl2=(-rdv+math.sqrt(rdv*rdv+c2*np.dot(geometric,geometric)))/c2
    observed=p+velocity*(dt+tl1-tl2)
    return observed/np.linalg.norm(observed)

@lru_cache(maxsize=100000)
def direction(target,year):
    return ltpb(year) @ space_direction(stars()[target],year)

@lru_cache(maxsize=100000)
def declination(target,year):
    if target in MAGS or target=='thuban':
        v=direction(target,year)
        return math.atan2(v[2],math.hypot(v[0],v[1]))/RAD
    if target not in TARGETS: raise ValueError(target)
    return obliquity(year)*(1 if target.startswith('june') else -1 if target.startswith('december') else 0)

def refraction(ha,temperature=20,pressure=1010):
    return (pressure/1010)*(283/(273+temperature))/math.tan((ha+7.31/(ha+4.4))*RAD)/60

def airmass(z):
    return 1/(math.cos(z*RAD)+.50572*(96.07995-z)**-1.6364)

@lru_cache()
def extinction(target,k=.30):
    from scipy.optimize import brentq
    return brentq(lambda h:MAGS[target]+k*(airmass(90-h)-1)-6,0,89.9,xtol=1e-12)

def azimuth(dec,lat,h=0,setting=True):
    d,p,a=np.array([dec,lat,h])*RAD
    c=(math.sin(d)-math.sin(p)*math.sin(a))/(math.cos(p)*math.cos(a))
    if abs(c)>1: return float('nan')
    east=math.acos(c)/RAD
    return 360-east if setting else east
