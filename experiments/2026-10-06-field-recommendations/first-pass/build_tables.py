import csv, json
from pathlib import Path
root=Path(__file__).resolve().parent
rows=json.loads((root/'recommendations.json').read_text(encoding='utf-8'))
fields=list(rows[0])
with (root/'recommendations.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader()
 for row in rows: writer.writerow({k:('; '.join(v) if isinstance(v,list) else v) for k,v in row.items()})
print(f'Wrote {len(rows)} recommendation rows.')
