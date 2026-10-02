"""A displacement-controlled visibility model for invented carved graphics.

This code predicts geometric contact and declared retained relief. It does not
infer clay forces, identify archaeological stamps or assign sign meanings.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.ndimage import gaussian_filter1d

try:
    import matplotlib
except ModuleNotFoundError:
    local_runtime = Path(__file__).resolve().parents[2] / 'experiments/2026-10-02-six-hour/stamp-geometry/local-witness/runtime-packages'
    sys.path.append(str(local_runtime))
    import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/stamp-geometry'
CLASSES = ['line', 'cross', 'loop', 'diagonal_cross']
THRESHOLD_MM = 0.08
VISIBLE_FRACTION = 0.8
STROKE_SAMPLES = 256


@dataclass(frozen=True)
class Geometry:
    slots: int = 8
    width: float = 24.0
    height: float = 8.0
    radius: float = 50.0
    displacement: float = 0.4
    tilt_u: float = 0.0
    tilt_v: float = 0.0
    rotation: float = 0.0


@dataclass(frozen=True)
class Imprint:
    depth: float = 0.4
    groove_width: float = 0.16
    retention: float = 1.0
    blur_sigma: float = 0.025
    damage: str = 'none'
    profile: str = 'rectangular'


def attenuation(width: float, sigma: float) -> float:
    return 1.0 if sigma == 0 else math.erf(width / (2 * math.sqrt(2) * sigma))


def penetration(u, v, geometry: Geometry):
    angle = math.radians(geometry.rotation)
    x = np.asarray(u) * math.cos(angle) - np.asarray(v) * math.sin(angle)
    if math.isinf(geometry.radius):
        sag = np.zeros_like(x)
    else:
        if np.any(np.abs(x) >= geometry.radius):
            raise ValueError('The sampled face extends beyond the cylinder projection.')
        # This rationalized form avoids cancellation for large radii.
        sag = x * x / (geometry.radius + np.sqrt(geometry.radius**2 - x * x))
    return (geometry.displacement - sag
            - math.tan(math.radians(geometry.tilt_u)) * np.asarray(u)
            - math.tan(math.radians(geometry.tilt_v)) * np.asarray(v))


def glyph_samples(geometry: Geometry, samples: int = STROKE_SAMPLES):
    """Return centreline coordinates, normals and length weights for each slot."""
    pitch = geometry.width / geometry.slots
    half_width = 0.34 * pitch
    half_height = 1.6
    segments = {
        'line': [(0, -half_height, 0, half_height)],
        'cross': [(0, -half_height, 0, half_height), (-half_width, 0, half_width, 0)],
        'loop': [(-half_width, -half_height, half_width, -half_height),
                 (half_width, -half_height, half_width, half_height),
                 (half_width, half_height, -half_width, half_height),
                 (-half_width, half_height, -half_width, -half_height)],
        'diagonal_cross': [(-half_width, -half_height, half_width, half_height),
                           (-half_width, half_height, half_width, -half_height)]}
    shapes = []
    fractions = (np.arange(samples) + 0.5) / samples
    for slot in range(geometry.slots):
        centre = (slot + 0.5) * pitch - geometry.width / 2
        row = []
        for label in CLASSES:
            u, v, nu, nv, weights = [], [], [], [], []
            for u0, v0, u1, v1 in segments[label]:
                length = math.hypot(u1 - u0, v1 - v0)
                u.extend(centre + u0 + fractions * (u1 - u0))
                v.extend(v0 + fractions * (v1 - v0))
                nu.extend(np.full(samples, -(v1 - v0) / length))
                nv.extend(np.full(samples, (u1 - u0) / length))
                weights.extend(np.full(samples, length / samples))
            row.append(tuple(np.asarray(values) for values in (u, v, nu, nv, weights)))
        shapes.append(row)
    return shapes


def retained_region(u, geometry: Geometry, damage: str):
    if damage == 'none':
        return np.ones_like(u, dtype=bool)
    if damage == 'left_quarter':
        return u >= -geometry.width / 4
    if damage == 'right_quarter':
        return u <= geometry.width / 4
    raise ValueError(damage)


def visibility(geometry: Geometry, imprint: Imprint, shapes=None):
    shapes = glyph_samples(geometry) if shapes is None else shapes
    score = np.zeros((geometry.slots, len(CLASSES)))
    blur = attenuation(imprint.groove_width, imprint.blur_sigma)
    for slot, row in enumerate(shapes):
        for graphic, (u, v, nu, nv, weights) in enumerate(row):
            if imprint.profile == 'rectangular':
                relief = imprint.retention * np.minimum(imprint.depth, np.maximum(penetration(u, v, geometry), 0))
                survived = (relief * blur >= THRESHOLD_MM) & retained_region(u, geometry, imprint.damage)
                score[slot, graphic] = np.dot(survived, weights) / weights.sum()
            elif imprint.profile == 'triangular':
                offsets = ((np.arange(7) + 0.5) / 7 - 0.5) * imprint.groove_width
                shifted_u = u[:, None] + nu[:, None] * offsets
                shifted_v = v[:, None] + nv[:, None] * offsets
                depth = imprint.depth * (1 - np.abs(2 * offsets / imprint.groove_width))
                relief = imprint.retention * np.minimum(depth, np.maximum(penetration(shifted_u, shifted_v, geometry), 0))
                # Width-averaged relief is a declared profile sensitivity.
                survived = (relief.mean(axis=1) * blur >= THRESHOLD_MM) & retained_region(u, geometry, imprint.damage)
                score[slot, graphic] = np.dot(survived, weights) / weights.sum()
            else:
                raise ValueError(imprint.profile)
    return score, score >= VISIBLE_FRACTION


def endpoint_expectations(visible):
    """Exact expectations for independent uniform synthetic graphic choices."""
    rates = visible.mean(axis=1)
    first = np.zeros(visible.shape[1])
    last = np.zeros(visible.shape[1])
    prefix = suffix = 1.0
    for i in range(len(rates)):
        first += prefix * visible[i] / visible.shape[1]
        prefix *= 1 - rates[i]
        j = len(rates) - 1 - i
        last += suffix * visible[j] / visible.shape[1]
        suffix *= 1 - rates[j]
    row_retention = 1 - prefix
    visible_class_mass = visible.sum(axis=0) / visible.shape[1]
    return {'row_retention': row_retention, 'expected_visible_length': rates.sum(),
            'first_mass': first, 'last_mass': last, 'visible_class_mass': visible_class_mass,
            'first': first / row_retention if row_retention else np.zeros(visible.shape[1]),
            'last': last / row_retention if row_retention else np.zeros(visible.shape[1]),
            'class_distribution': visible_class_mass / rates.sum() if rates.sum() else np.zeros(visible.shape[1])}


def record(geometry: Geometry, imprint: Imprint, shapes=None):
    score, visible = visibility(geometry, imprint, shapes)
    expectation = endpoint_expectations(visible)
    middle = [geometry.slots // 2] if geometry.slots % 2 else [geometry.slots // 2 - 1, geometry.slots // 2]
    return {'geometry': asdict(geometry), 'imprint': asdict(imprint),
            'stroke_survival_fraction': score.tolist(), 'visible': visible.astype(int).tolist(),
            **{key: value.tolist() if isinstance(value, np.ndarray) else float(value)
               for key, value in expectation.items()},
            'left_right_endpoint_tv': float(abs(expectation['first'] - expectation['last']).sum() / 2),
            'class_frequency_tv': float(abs(expectation['class_distribution'] - 0.25).sum() / 2) if expectation['row_retention'] else None,
            'outer_visibility': float(visible[[0, -1]].mean()),
            'middle_visibility': float(visible[middle].mean())}


def analytic_roots(radius, displacement, tilt_degrees):
    slope = math.tan(math.radians(tilt_degrees))
    discriminant = (1 + slope**2) * radius**2 - (radius - displacement)**2
    if discriminant < 0:
        return None
    shift = -slope * (radius - displacement)
    extent = math.sqrt(discriminant)
    denominator = 1 + slope**2
    return (shift - extent) / denominator, (shift + extent) / denominator


def scalar_roots(radius, displacement, tilt_degrees):
    """Independent direct circle/plane evaluation and bracketed bisection."""
    slope = math.tan(math.radians(tilt_degrees))

    def value(x):
        return displacement - (radius - math.sqrt(radius * radius - x * x)) - slope * x

    xs = np.linspace(-radius * 0.999999, radius * 0.999999, 4001)
    brackets = [(a, b) for a, b in zip(xs[:-1], xs[1:]) if value(a) * value(b) < 0]
    roots = []
    for lo, hi in brackets:
        for _ in range(80):
            mid = (lo + hi) / 2
            if value(lo) * value(mid) <= 0:
                hi = mid
            else:
                lo = mid
        roots.append((lo + hi) / 2)
    return roots


def clip_polygon(points, a, b, c):
    """Clip a polygon to a*u+b*v <= c."""
    output = []
    for start, end in zip(points, points[1:] + points[:1]):
        f_start = a * start[0] + b * start[1] - c
        f_end = a * end[0] + b * end[1] - c
        inside_start, inside_end = f_start <= 0, f_end <= 0
        if inside_start:
            output.append(start)
        if inside_start != inside_end:
            fraction = f_start / (f_start - f_end)
            output.append((start[0] + fraction * (end[0] - start[0]),
                           start[1] + fraction * (end[1] - start[1])))
    return output


def analytic_contact_area(geometry):
    if geometry.tilt_u or geometry.tilt_v:
        raise ValueError('Area formula is for untilted contact.')
    if geometry.displacement <= 0:
        return 0.0
    if math.isinf(geometry.radius):
        return geometry.width * geometry.height
    half = math.sqrt(2 * geometry.radius * geometry.displacement - geometry.displacement**2)
    a, b = math.cos(math.radians(geometry.rotation)), -math.sin(math.radians(geometry.rotation))
    points = [(-geometry.width/2, -geometry.height/2), (geometry.width/2, -geometry.height/2),
              (geometry.width/2, geometry.height/2), (-geometry.width/2, geometry.height/2)]
    points = clip_polygon(points, a, b, half)
    points = clip_polygon(points, -a, -b, half)
    return abs(sum(u0*v1-u1*v0 for (u0,v0),(u1,v1) in zip(points,points[1:]+points[:1]))) / 2


def verify_model():
    checks = []

    def check(name, passed, details=None):
        checks.append({'check': name, 'passed': bool(passed), 'details': details})

    differences = []
    for radius, displacement, tilt in product([15., 50., 200.], [0.05, 0.4, 1.2], [-4., 0., 4.]):
        exact = analytic_roots(radius, displacement, tilt)
        numerical = scalar_roots(radius, displacement, tilt)
        if len(numerical) != 2:
            differences.append(float('inf'))
        else:
            differences.extend(abs(a-b) for a,b in zip(exact,numerical))
    check('analytic_contact_roots_match_independent_bisection', max(differences) < 1e-9,
          {'cases': 27, 'maximum_absolute_error_mm': max(differences)})
    area_cases = []
    for rotation in [0., 30., 60., 90.]:
        geometry = Geometry(radius=25., displacement=0.4, rotation=rotation)
        exact = analytic_contact_area(geometry)
        errors = []
        for resolution in [100, 200, 400]:
            u = (np.arange(resolution)+0.5)/resolution*geometry.width-geometry.width/2
            v = (np.arange(resolution)+0.5)/resolution*geometry.height-geometry.height/2
            contact = penetration(u[:,None],v[None,:],geometry)>0
            numeric = contact.mean()*geometry.width*geometry.height
            errors.append(abs(numeric-exact)/(geometry.width*geometry.height))
        area_cases.append({'rotation':rotation,'area_mm2':exact,'relative_face_area_errors':errors})
    check('contact_area_agrees_with_fine_grid', max(row['relative_face_area_errors'][-1] for row in area_cases)<0.003,area_cases)
    all_visible = visibility(Geometry(radius=math.inf), Imprint())[1]
    check('flat_complete_contact_all_graphics_visible', all_visible.all())
    check('zero_displacement_zero_visibility', not visibility(Geometry(displacement=0),Imprint())[1].any())
    check('groove_depth_below_threshold_zero_visibility', not visibility(Geometry(radius=math.inf),Imprint(depth=0.05))[1].any())
    reflection_error = []
    expectation_error = []
    for slots,radius,tilt,rotation in product([3,8],[25.,100.],[0.,2.,4.],[0.,30.,90.]):
        geometry=Geometry(slots=slots,width=14. if slots==3 else 24.,radius=radius,tilt_u=tilt,rotation=rotation)
        for damage, mirrored_damage in [('none','none'),('left_quarter','right_quarter')]:
            own=record(geometry,Imprint(damage=damage))
            mirror=record(replace(geometry,tilt_u=-tilt),Imprint(damage=mirrored_damage))
            reflection_error.append(np.max(abs(np.asarray(own['stroke_survival_fraction'])-np.asarray(mirror['stroke_survival_fraction'])[::-1])))
            expectation_error.append(np.max(abs(np.asarray(own['first'])-np.asarray(mirror['last']))))
    check('reflection_reverses_visibility', max(reflection_error)<1e-12,{'maximum_fraction_error':float(max(reflection_error))})
    check('reflection_reverses_endpoint_distributions',max(expectation_error)<1e-12,{'maximum_probability_error':float(max(expectation_error))})
    geometry=Geometry(slots=3,width=14.,radius=25.,displacement=0.4,tilt_u=2.)
    visible=visibility(geometry,Imprint(damage='left_quarter'))[1]
    expected=endpoint_expectations(visible)
    first=np.zeros(4);last=np.zeros(4);retained=0;length=0
    for row in product(range(4),repeat=3):
        ids=[i for i,k in enumerate(row) if visible[i,k]]
        if ids:
            retained+=1;first[row[ids[0]]]+=1;last[row[ids[-1]]]+=1
        length+=len(ids)
    check('endpoint_formula_matches_64_exhaustive_rows',
          np.allclose(first/64,expected['first_mass']) and np.allclose(last/64,expected['last_mass'])
          and abs(retained/64-expected['row_retention'])<1e-12 and abs(length/64-expected['expected_visible_length'])<1e-12)
    blur_cases=[]
    for width,sigma in product([0.08,0.16,0.32],[0.025,0.05]):
        spacing=0.0001
        coordinates=np.arange(-1.,1.+spacing/2,spacing)
        profile=(abs(coordinates)<=width/2).astype(float)
        numerical=gaussian_filter1d(profile,sigma/spacing,mode='constant',truncate=8)[len(profile)//2]
        exact=attenuation(width,sigma)
        blur_cases.append({'width_mm':width,'sigma_mm':sigma,'analytic':exact,'numerical':float(numerical),'error':float(abs(exact-numerical))})
    check('line_blur_agrees_with_independent_raster_convolution',max(row['error'] for row in blur_cases)<0.001,blur_cases)
    return checks


def pool(records):
    if not records:
        return None
    retention=sum(row['row_retention'] for row in records)
    first=np.sum([row['first_mass'] for row in records],axis=0)
    last=np.sum([row['last_mass'] for row in records],axis=0)
    class_mass=np.sum([row['visible_class_mass'] for row in records],axis=0)
    first=first/retention if retention else first*0
    last=last/retention if retention else last*0
    return {'configurations':len(records),'mean_row_retention':retention/len(records),
            'empty_configurations':sum(row['row_retention']==0 for row in records),
            'mean_visible_length':sum(row['expected_visible_length'] for row in records)/len(records),
            'first_class_distribution':first.tolist(),'last_class_distribution':last.tolist(),
            'left_right_endpoint_tv':float(abs(first-last).sum()/2),
            'visible_class_distribution':(class_mass/class_mass.sum()).tolist() if class_mass.sum() else None,
            'mean_outer_visibility':float(np.mean([row['outer_visibility'] for row in records])),
            'mean_middle_visibility':float(np.mean([row['middle_visibility'] for row in records]))}


def serialize(row):
    value={**row['geometry'],**row['imprint'],**{key:row[key] for key in ['row_retention','expected_visible_length','left_right_endpoint_tv','class_frequency_tv','outer_visibility','middle_visibility']}}
    value['visibility_by_slot']= '|'.join(''.join(map(str,slot)) for slot in row['visible'])
    for prefix in ['first','last','class_distribution']:
        for label,number in zip(CLASSES,row[prefix]):value[prefix+'_'+label]=number
    return value


def save_csv(path,records):
    rows=[serialize(row) for row in records]
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def json_safe(value):
    if isinstance(value,float) and not math.isfinite(value):
        if math.isinf(value):
            return 'infinity' if value>0 else '-infinity'
        raise ValueError('An undefined numerical value reached an output.')
    if isinstance(value,dict):
        return {key:json_safe(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):
        return [json_safe(item) for item in value]
    return value


def make_figures(endpoint):
    geometry=Geometry(radius=25.,displacement=0.4)
    fig,axes=plt.subplots(2,2,figsize=(10,6),constrained_layout=True)
    u=np.linspace(-12,12,800)
    for tilt,ax in zip([0,2],axes[0]):
        depths=penetration(u,np.zeros_like(u),replace(geometry,tilt_u=tilt))
        ax.plot(u,depths,color='#244a72',label='Land penetration')
        ax.axhline(0,color='grey',linewidth=0.8)
        ax.axhline(THRESHOLD_MM/attenuation(0.16,0.025),color='#bd6b25',linestyle='--',label='Visibility height threshold')
        ax.set(xlabel='Position along stamp (mm)',ylabel='Depth (mm)',title=f'R=25 mm, displacement=0.4 mm, tilt={tilt}°',ylim=(-2.8,0.7))
        ax.legend(fontsize=8)
    for tilt,ax in zip([0,2],axes[1]):
        row=record(replace(geometry,tilt_u=tilt),Imprint())
        image=np.asarray(row['stroke_survival_fraction']).T
        ax.imshow(image,origin='upper',vmin=0,vmax=1,cmap='viridis',aspect='auto',extent=(-0.5,7.5,3.5,-0.5))
        ax.set(xlabel='Synthetic slot, left to right',yticks=range(4),yticklabels=CLASSES,title='Fraction of each graphic stroke that survives')
    fig.savefig(endpoint/'contact-and-visibility.svg')
    fig.savefig(endpoint/'contact-and-visibility.png',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3),constrained_layout=True)
    row=record(geometry,Imprint())
    for slot in range(geometry.slots):
        samples=glyph_samples(geometry)[slot][slot%4]
        axes[0].scatter(samples[0],samples[1],s=2,color='#244a72')
    axes[0].set(xlim=(-12,12),ylim=(-4,4),aspect='equal',title='Invented graphic geometry',xlabel='u (mm)',ylabel='v (mm)')
    axes[1].bar(np.arange(4)-0.15,row['first'],width=0.3,label='First visible')
    axes[1].bar(np.arange(4)+0.15,row['last'],width=0.3,label='Last visible')
    axes[1].axhline(0.25,color='grey',linestyle='--')
    axes[1].set(xticks=range(4),xticklabels=CLASSES,ylabel='Conditional probability',title='Uniform input classes, symmetric contact')
    axes[1].tick_params(axis='x',labelrotation=20)
    axes[1].legend(fontsize=8)
    fig.savefig(endpoint/'synthetic-graphics-and-endpoints.svg')
    fig.savefig(endpoint/'synthetic-graphics-and-endpoints.png',dpi=180)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--endpoint',required=True)
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    if not args.endpoint.replace('-','').isalnum() or '/' in args.endpoint:
        raise ValueError('Use a simple endpoint name.')
    endpoint=BASE/args.endpoint
    if endpoint.exists():raise RuntimeError('Preserve the completed endpoint.')
    checks=verify_model()
    endpoint.mkdir()
    (endpoint/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    write=lambda name,value:(endpoint/name).write_text(json.dumps(json_safe(value),indent=2,allow_nan=False)+'\n',encoding='utf-8')
    write('verification.json',checks)
    if any(not row['passed'] for row in checks) or args.check_only:
        write('status.json',{'status':'checked-pilot','passed':sum(row['passed'] for row in checks),'failed':sum(not row['passed'] for row in checks)})
        print((endpoint/'status.json').read_text())
        if any(not row['passed'] for row in checks):raise SystemExit(1)
        return
    primary=[]
    shapes={slots:glyph_samples(Geometry(slots=slots,width=14. if slots==3 else 24.)) for slots in [3,8]}
    for slots,radius,d,tilt,alpha in product([3,8],[15.,25.,50.,100.,200.,math.inf],[0.05,0.1,0.2,0.4,0.8,1.2],[-4.,-2.,0.,2.,4.],[0.,30.,60.,90.]):
        geometry=Geometry(slots=slots,width=14. if slots==3 else 24.,radius=radius,displacement=d,tilt_u=tilt,rotation=alpha)
        for damage in ['none','left_quarter','right_quarter']:
            primary.append(record(geometry,Imprint(damage=damage),shapes[slots]))
    nuisance=[]
    for radius,d,tilt,alpha,depth,width,eta,sigma,damage in product([25.,100.,math.inf],[0.1,0.4,0.8],[0.,2.],[0.,90.],[0.1,0.2,0.4],[0.08,0.16,0.32],[0.25,0.5,1.],[0.,0.025,0.05],['none','left_quarter','right_quarter']):
        nuisance.append(record(Geometry(radius=radius,displacement=d,tilt_u=tilt,rotation=alpha),Imprint(depth,width,eta,sigma,damage),shapes[8]))
    profiles=[]
    for radius,d,tilt,alpha,width in product([25.,100.,math.inf],[0.1,0.4,0.8],[0.,2.],[0.,90.],[0.08,0.32]):
        geometry=Geometry(radius=radius,displacement=d,tilt_u=tilt,rotation=alpha)
        box=record(geometry,Imprint(groove_width=width),shapes[8])
        triangle=record(geometry,Imprint(groove_width=width,profile='triangular'),shapes[8])
        profiles.append({'geometry':asdict(geometry),'groove_width':width,'rectangular_visible':box['visible'],'triangular_visible':triangle['visible'],
                         'rectangular_expected_length':box['expected_visible_length'],'triangular_expected_length':triangle['expected_visible_length']})
    pools={}
    for slots in [3,8]:
        selected=[row for row in primary if row['geometry']['slots']==slots]
        definitions={'centred_no_damage':lambda row:row['geometry']['tilt_u']==0 and row['imprint']['damage']=='none',
                     'balanced_tilt_no_damage':lambda row:row['imprint']['damage']=='none',
                     'positive_tilt_no_damage':lambda row:row['geometry']['tilt_u']>0 and row['imprint']['damage']=='none',
                     'balanced_tilt_left_break':lambda row:row['imprint']['damage']=='left_quarter',
                     'balanced_tilt_both_break_sides':lambda row:row['imprint']['damage']!='none'}
        pools[str(slots)]={name:pool([row for row in selected if condition(row)]) for name,condition in definitions.items()}
    usable=[row for row in primary if row['row_retention']>0]
    worst=max(usable,key=lambda row:row['left_right_endpoint_tv'])
    worst_frequency=max(usable,key=lambda row:row['class_frequency_tv'])
    save_csv(endpoint/'primary-configurations.csv',primary)
    save_csv(endpoint/'nuisance-configurations.csv',nuisance)
    write('profile-sensitivity.json',profiles)
    write('extreme-examples.json',{'maximum_endpoint_difference':worst,'maximum_class_frequency_distortion':worst_frequency})
    result={'status':'synthetic-forward-contact-and-visibility-model','created_utc':datetime.now(timezone.utc).isoformat(),
            'primary_geometries':1440,'primary_configurations':len(primary),'nuisance_configurations':len(nuisance),'profile_comparisons':len(profiles),
            'classes':CLASSES,'threshold_mm':THRESHOLD_MM,'visible_fraction':VISIBLE_FRACTION,'stroke_samples':STROKE_SAMPLES,
            'primary_pools':pools,'nuisance_pool':pool(nuisance),
            'maximum_primary_endpoint_tv':worst['left_right_endpoint_tv'],
            'maximum_primary_class_frequency_tv':worst_frequency['class_frequency_tv'],
            'profile_changed_visibility_comparisons':sum(row['rectangular_visible']!=row['triangular_visible'] for row in profiles),
            'verification':{'checks':len(checks),'passed':sum(row['passed'] for row in checks)},
            'protocol_sha256':hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_dependency':'Harappa/Beas observation frame and primary mechanics provenance; all simulation dimensions and material factors are declared inputs.'}
    write('results.json',result)
    make_figures(endpoint)
    print(json.dumps({key:value for key,value in result.items() if key not in ['primary_pools','nuisance_pool']},indent=2))


if __name__=='__main__':main()
