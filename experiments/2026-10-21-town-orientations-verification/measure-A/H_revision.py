import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess
base=Path(sys.argv[1]);raw=Path(sys.argv[2]);tools=Path(sys.argv[3])
def read(p):return json.loads(p.read_text())
for n in (3,4):
 p=read(base/f'plan-0{n}-picks-v1.json')
 if n==3:
  p['north']['line']['endpoints_px']=[[859,158],[859,103]];p['north']['line']['pick_sigma_px']=2
  p['scale']['endpoints_px']=[[513,1047],[905,1047]]
  pts=[[[104,319],[482,141]],[[500,166],[804,734]],[[111,387],[327,865]],[[547,869],[802,738]]]
  for row,pair in zip(p['lines'],pts):row['endpoints_px']=pair;row['corridor_half_width_px']=5
 else:
  # Remove v1 candidates which failed the architectural-face overlay review.
  p['lines']=[r for r in p['lines'] if r['id'] not in ['c3-t-south','c3-lane','c3-court-east','c2-east']]
  # Use the same underlying whole-page render and deliberately broader corridors
  # for the remaining coloured exterior faces. Preserve all earlier attempts.
  for row in p['lines']:row['corridor_half_width_px']=10
 p['revision_note']='v2 follows fresh-overlay review. Rejected candidates and previous results remain beside this file. Figure 17 is re-picked on a larger fresh crop to follow room-facing wall outlines.'
 out=base/f'plan-0{n}-picks-v2.json'
 with out.open('x') as f:json.dump(p,f,indent=2)
 render=raw/(f'plan-0{n}-detail-v2.png' if n==3 else f'plan-0{n}-v1.png')
 result=base/f'plan-0{n}-lines-v2.json'
 subprocess.run([sys.executable,'-I',str(tools/'measure_lines.py'),str(out),str(render)+'.json',str(result)],check=True)
 subprocess.run([sys.executable,'-I',str(base.parents[1]/'H_work.py'),'overlay',str(render),str(result),str(raw/f'plan-0{n}-check-v2.png')],check=True)
