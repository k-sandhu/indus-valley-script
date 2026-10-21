"""Export identifiers and existing ranks, with no sign strings."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
west=list(csv.DictReader((ROOT/'experiments/2026-10-12-published-claim-tests/foreign-finds/run-2026-10-12/objects.csv').open()))
west=[r for r in west if r['group']=='west_asia' and r['medium']=='round' and r['scorable']=='True' and r['record_id']!='6000.1']
south=[json.loads(s) for s in (ROOT/'data/raw/2026-10-12-decipherment-claim-tests/foreign-finds/run-2026-10-12/peripheral_rows.jsonl').read_text().splitlines()]
south=[r for r in south if r.get('peripheral_group')=='south_asian_round' and r['scorable']]
with (HERE/'legacy-ranks-and-eligibility.csv').open('x',newline='',encoding='utf-8') as f:
 fields=['record_id','family','group','site','object_type','length','u_surprisal','circular_eligible','tablet_excluded_eligible','text_conservative_eligible']
 out=csv.DictWriter(f,fieldnames=fields);out.writeheader()
 for r in west+south:
  row={k:r[k] for k in fields[:7]}; c=r['object_type']=='SEAL:C'; t=c and r['record_id']!='2977.1'; conservative=t and r['record_id']!='2913.1'
  row.update(circular_eligible=int(c),tablet_excluded_eligible=int(t),text_conservative_eligible=int(conservative));out.writerow(row)
