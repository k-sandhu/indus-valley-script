"""Check labelled systems and compute the measurement rules' exact statistics."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,csv,math,collections
import numpy as np
from common import read_json,write_json,utc

def point_segment(p,a,b):
    v=b-a;t=np.clip(np.dot(p-a,v)/max(np.dot(v,v),1e-30),0,1)
    return float(np.linalg.norm(p-a-t*v))

def segment_distance(a,b):
    """Euclidean shortest distance, including intersecting segments."""
    a,b=np.asarray(a,float),np.asarray(b,float)
    cross=lambda u,v:u[0]*v[1]-u[1]*v[0]
    r=a[1]-a[0];s=b[1]-b[0];den=cross(r,s)
    if abs(den)>1e-12:
        t=cross(b[0]-a[0],s)/den;u=cross(b[0]-a[0],r)/den
        if 0<=t<=1 and 0<=u<=1:return 0.
    return min(point_segment(a[0],*b),point_segment(a[1],*b),point_segment(b[0],*a),point_segment(b[1],*a))

def summarize(lines):
    if not lines:raise ValueError('empty system')
    L=np.array([r['length_m'] for r in lines],float);theta=np.array([r['theta_deg'] for r in lines],float);sigma=np.array([r['sigma_deg'] for r in lines],float)
    if np.any(L<=0) or np.any(sigma<0):raise ValueError('lengths must be positive and errors nonnegative')
    mean=float(np.dot(L,theta)/L.sum());sd=float(np.sqrt(np.dot(L,(theta-mean)**2)/L.sum()));scatter=sd/np.sqrt(len(lines));prop=float(np.sqrt(np.sum(L**2*sigma**2))/L.sum())
    warnings=[]
    if float(theta.max()-theta.min())>6+1e-10:warnings.append('deviations exceed a 6 degree window')
    points=[r.get('endpoints_utm',r.get('endpoints_plan_m')) for r in lines]
    graph=[set() for _ in lines]
    if any(p is None for p in points):warnings.append('200 m condition could not be checked: metric endpoints missing')
    else:
        for i in range(len(lines)):
            for j in range(i):
                if segment_distance(points[i],points[j])<=200:graph[i].add(j);graph[j].add(i)
        if any(not g for g in graph):warnings.append('at least one line has no other system line within 200 m')
        reached={0};front=[0]
        while front:
            for j in graph[front.pop()]-reached:reached.add(j);front.append(j)
        if len(reached)<len(lines):warnings.append('200 m neighbour graph is disconnected; review whether this is one part of the town')
    if len(set(r.get('part') for r in lines))>1:warnings.append('system includes more than one named town part')
    if len(set(r.get('epsg') for r in lines if r.get('epsg')))>1:warnings.append('mixed metric projections; distances require a common frame')
    return dict(line_ids=[r['id'] for r in lines],n=len(lines),total_length_m=float(L.sum()),theta_deg=mean,weighted_sd_deg=sd,scatter_se_deg=float(scatter),propagated_se_deg=prop,se_deg=max(float(scatter),prop,.3),deviation_window_deg=float(theta.max()-theta.min()),warnings=warnings,conditions_pass=not warnings)

def town_result(town):
    result=dict(town);lines=town.get('lines',[]);groups=collections.defaultdict(list)
    seen=set()
    for line in lines:
        key=(line['source_id'],line['id'])
        if key in seen:raise ValueError('duplicate line ID within source')
        seen.add(key)
        for field in ['system','part','kind','identification','endpoints_px','length_m','bearing_deg','theta_deg','sigma_deg']:
            if field not in line:raise ValueError('missing line field: '+field)
        groups[(line['source_id'],line['system'])].append(line)
    systems=[];main={}
    for (source,label),rows in groups.items():systems.append(dict(source_id=source,id=label,**summarize(rows)))
    for source in sorted(set(s['source_id'] for s in systems)):
        choices=[s for s in systems if s['source_id']==source];choices.sort(key=lambda s:(-s['total_length_m'],-s['n'],s['id']))
        main[source]=choices[0]['id']
        if len(choices)>1 and (choices[0]['total_length_m'],choices[0]['n'])==(choices[1]['total_length_m'],choices[1]['n']):
            choices[0]['warnings'].append('length and line-count tie remains; lexical system ID is the documented final tie break')
    result.update(schema_version=1,created_utc=utc(),systems=systems,main_system_by_source=main)
    if not lines and not town.get('unmeasurable_reason'):raise ValueError('unmeasured town requires unmeasurable_reason')
    return result

FIELDS=['schema_version','town','source_id','main_system','n','total_length_m','theta_deg','se_deg','conditions_pass','unmeasurable_reason']
def append_summary(path,town):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    existing=[]
    if p.exists():
        with p.open(encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=FIELDS:raise ValueError('summary schema differs')
            existing=list(reader)
        if any(r['town']==town['slug'] for r in existing):raise ValueError('summary already contains this town; use a new output')
    with p.open('a',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if not existing:w.writeheader()
        if not town['systems']:w.writerow(dict(schema_version=1,town=town['slug'],unmeasurable_reason=town['unmeasurable_reason']))
        for source,label in town['main_system_by_source'].items():
            s=next(s for s in town['systems'] if s['source_id']==source and s['id']==label)
            w.writerow(dict(schema_version=1,town=town['slug'],source_id=source,main_system=label,**{k:s[k] for k in ['n','total_length_m','theta_deg','se_deg','conditions_pass']}))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');p.add_argument('--summary',required=True);a=p.parse_args();r=town_result(read_json(a.input))
    if Path(a.output).exists():raise FileExistsError(a.output)
    if Path(a.summary).exists():
        with open(a.summary,encoding='utf-8') as f:
            if any(x['town']==r['slug'] for x in csv.DictReader(f)):raise ValueError('summary already contains town')
    write_json(a.output,r);append_summary(a.summary,r)
    for s in r['systems']:
        for warning in s['warnings']:print(s['source_id'],s['id'],warning)
if __name__=='__main__':main()
