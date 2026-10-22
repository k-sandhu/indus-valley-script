import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess,copy
own=Path(sys.argv[1]);raw=Path(sys.argv[2]);tools=Path(sys.argv[3])
def read(p):return json.loads(p.read_text())
p=read(own/'picks/banawali/plan-01-picks-v2.json')
p['revision_note']='v3 uses enlarged fresh 600 dpi checks. Earlier middle and south lines ran beyond individual solid-black exposures and are superseded. Only the black defence face is retained. Two faces of the same acropolis wall are correlated and do not represent independent buildings.'
for row in p['lines']:
 if row['id']=='outer-east-middle':
  row.update(endpoints_px=[[1828.5,1680.5],[1841.5,1730.5]],mode='manual',pick_sigma_px=3,system='lower-east')
  row['identification']='Bisht 1998-99, PDF p.47, printed p.33, Fig.1: eastern face of short solid black eastern Harappan Defences exposure above the original v1 middle pick. Fresh face-detail-v3 locates its limits; trench and moat lines excluded.'
 if row['id']=='outer-east-south':
  row.update(endpoints_px=[[1899,1885],[1908,1911.5]],mode='manual',pick_sigma_px=3,system='lower-south-exposure')
  row['identification']='Same Fig.1: short eastern face of southern solid-black Harappan Defences exposure, before the gap. Earlier extension along the moat-side line is excluded.'
outer=copy.deepcopy(p['lines'][-1])
outer.update(id='acropolis-opposite-face',endpoints_px=[[1618,1821.5],[1630.5,1914]],mode='manual',pick_sigma_px=4)
outer['identification']='Same Fig.1: opposite, eastern face of the lower straight acropolis defence, from the enlarged acropolis-detail-v3. The irregular face is measured manually with four-pixel endpoint sigma. Shares one wall with acropolis-east-south.'
p['lines'].append(outer)
f=own/'picks/banawali/plan-01-picks-v3.json'
with f.open('x') as stream:json.dump(p,stream,indent=2)
q=read(own/'picks/farmana/plan-04-picks-v2.json')
for row in q['lines']:
 if row['id']=='c2-south':row['corridor_half_width_px']=4
q['revision_note']='v3 restores the four-pixel corridor for c2-south. The v2 wider corridor selected a different complex-2 wall below the intended 2B face. All other v2 candidates are retained.'
g=own/'picks/farmana/plan-04-picks-v3.json'
with g.open('x') as stream:json.dump(q,stream,indent=2)
for slug,n,png in [('banawali',1,'plan-01-300-v1.png'),('farmana',4,'plan-04-v1.png')]:
 pp=own/f'picks/{slug}/plan-0{n}-picks-v3.json';rr=own/f'picks/{slug}/plan-0{n}-lines-v3.json'
 subprocess.run([sys.executable,'-I',str(tools/'measure_lines.py'),str(pp),str(raw/slug/png)+'.json',str(rr)],check=True)
 subprocess.run([sys.executable,'-I',str(own/'H_work.py'),'overlay',str(raw/slug/png),str(rr),str(raw/slug/f'plan-0{n}-check-v3.png')],check=True)
