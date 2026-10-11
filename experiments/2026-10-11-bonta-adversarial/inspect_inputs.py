"""Print bounded input summaries before selecting adversarial diagnostics."""
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[2]

def load(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))

rows=load('experiments/2026-10-08-bonta-extension/run-2026-10-09-v5/candidates.json')
print('Catalogue container',type(rows).__name__)
if isinstance(rows,dict):
    print('keys',list(rows))
    rows=rows.get('rows',rows.get('candidates'))
print('First candidate',json.dumps(rows[0],ensure_ascii=False)[:6500])
print('New priority A', [(r['code'],r.get('meaning'),r.get('preferred',{}).get('meaning')) for r in rows if r.get('priority')=='A'])
for p in ['data/normalized/lipi_clean_rtl_singleline.jsonl','data/normalized/lipi_observed_faces.jsonl']:
    rs=[json.loads(x) for x in (ROOT/p).read_text(encoding='utf-8').splitlines()]
    print(p,len(rs),'keys',list(rs[0]),'sites',Counter(r.get('site') for r in rs),'types',Counter(r.get('object_type') for r in rs))
for p in ['data/raw/2026-10-08-bonta-extension/run-2026-10-09-v2/preferred-lexical-witnesses.json',
          'experiments/2026-10-08-bonta-review/two-coder-2026-10-09-v1/disagreements.json',
          'experiments/2026-10-08-bonta-review/pdf-2026-10-09-v1/mapping-v1-frozen.json']:
    if (ROOT/p).exists():
        x=load(p)
        print(p,'keys',list(x)[:12] if isinstance(x,dict) else 'list',json.dumps(x if isinstance(x,list) else (x.get('233') or x),ensure_ascii=False)[:3000])
