import csv,json,statistics,random,hashlib
from pathlib import Path
root=Path.cwd(); main=root/'experiments/2026-10-20-foreign-script-audit'; out=Path(__file__).parent
rows=list(csv.DictReader((main/'legacy-ranks-and-eligibility.csv').open())); summary=json.loads((main/'sensitivity.json').read_text())
scenarios={'legacy_pooled':lambda r:True,'circular_only':lambda r:r['circular_eligible']=='1','circular_exclude_tablet':lambda r:r['tablet_excluded_eligible']=='1','circular_exclude_tablet_and_uncertain_composition':lambda r:r['text_conservative_eligible']=='1'}
def calc(rr):
 w=[r for r in rr if r['group']=='west_asia'];s=[r for r in rr if r['group']=='south_asia'];avg=lambda a:statistics.fmean(float(r['u_surprisal']) for r in a)
 val={'west_faces':len(w),'south_faces':len(s),'west_families':len({r['family'] for r in w}),'south_families':len({r['family'] for r in s}),'west_mean_u':avg(w),'south_mean_u':avg(s),'difference':avg(w)-avg(s)}
 loo=[]
 for side in [w,s]:
  for fam in dict.fromkeys(r['family'] for r in side):
   reduced=[r for r in side if r['family']!=fam];loo.append(avg(reduced)-avg(s) if side is w else avg(w)-avg(reduced))
 val['leave_one_family_out_range']=[min(loo),max(loo)]
 rng=random.Random(20261020)
 def draw(side):
  fam={}
  for r in side:fam.setdefault(r['family'],[]).append(float(r['u_surprisal']))
  values=[]
  for key in rng.choices(list(fam),k=len(fam)):values.extend(fam[key])
  return statistics.fmean(values)
 boot=sorted(draw(w)-draw(s) for _ in range(10000));val['bootstrap_95']=[boot[249],boot[9749]]
 # Equal weight per family is a separate descriptive sensitivity.
 def familymean(side):
  return statistics.fmean(avg([r for r in side if r['family']==f]) for f in dict.fromkeys(r['family'] for r in side))
 val['equal_family_weight_difference']=familymean(w)-familymean(s)
 return val
results={};checks={}
for name,pred in scenarios.items():
 v=calc([r for r in rows if pred(r)]);results[name]=v;checks[name]={}
 for k,target in summary['variants'][name].items():
  ours=v[k];checks[name][k]=all(abs(a-b)<1e-12 for a,b in zip(ours,target)) if isinstance(target,list) else abs(ours-target)<1e-12
cell=calc([r for r in rows if r['tablet_excluded_eligible']=='1' and r['length']=='4']);results['length4']=cell
checks['length4']={k:all(abs(a-b)<1e-12 for a,b in zip(cell[k],v)) if isinstance(v,list) else abs(cell[k]-v)<1e-12 for k,v in summary['length_cells_with_at_least_two_per_side']['4'].items()}
frame_path=main/'frame.json'
if not frame_path.exists():frame_path=root/'data/raw/2026-10-20-foreign-script-audit/frame.json'
frame=json.loads(frame_path.read_text()); ann=json.loads((main/'annotations.json').read_text());
source={'frame_faces':len(frame),'frame_families':len({r['family'] for r in frame}),'indexed_image_faces':sum(bool(r['images']) for r in frame),'indexed_images':sum(len(r['images']) for r in frame),'secure_table1_join_faces':sum(r['table1_number'] is not None for r in ann),'secure_table1_objects':len({r['table1_number'] for r in ann if r['table1_number'] is not None})}
checks['source_counts']={k:v==json.loads((main/'audit-summary.json').read_text())[k] for k,v in source.items()}
output={'results':results,'checks':checks,'all_checks_pass':all(all(c.values()) for c in checks.values()),'source_counts':source,'repeated_scored_families':{f:[r['record_id'] for r in rows if r['family']==f] for f in dict.fromkeys(r['family'] for r in rows) if sum(r['family']==f for r in rows)>1},'input_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [main/'legacy-ranks-and-eligibility.csv',main/'sensitivity.json',frame_path,main/'annotations.json',main/'audit-summary.json']}}
(out/'verification.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'all_checks_pass':output['all_checks_pass'],'checks':checks,'source':source}))
