"""Independently recompute point differences from the public eligibility table."""
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE/'legacy-ranks-and-eligibility.csv').open()))
for name,flag in [('legacy_pooled',None),('circular_only','circular_eligible'),('circular_exclude_tablet','tablet_excluded_eligible'),('circular_exclude_tablet_and_uncertain_composition','text_conservative_eligible')]:
 a=[r for r in rows if flag is None or r[flag]=='1']
 w=[r for r in a if r['group']=='west_asia'];s=[r for r in a if r['group']=='south_asia']
 delta=sum(float(r['u_surprisal']) for r in w)/len(w)-sum(float(r['u_surprisal']) for r in s)/len(s)
 expected=json.loads((HERE/'sensitivity.json').read_text())['variants'][name]['difference']
 assert abs(delta-expected)<1e-12
 print(f'{name}: West {len(w)} faces/{len({r["family"] for r in w})} families; South Asia {len(s)} faces/{len({r["family"] for r in s})} families; difference {delta:.9f}')
