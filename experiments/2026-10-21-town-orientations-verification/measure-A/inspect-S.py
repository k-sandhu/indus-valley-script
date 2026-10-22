"""Read only permitted source indexes; compact town inventory for measurer A south."""
import json, sys, shutil
from pathlib import Path

base = Path(sys.argv[1])
slugs = sys.argv[2:]
print('FREE_BYTES', shutil.disk_usage('C:/').free)
for slug in slugs:
    print('\nTOWN', slug)
    for name, key in [('sites-located-v1.json', 'sites'), ('imagery-manifest-v1.json', 'towns'), ('plan-library-v1.json', 'towns')]:
        obj = json.loads((base / name).read_text(encoding='utf-8'))
        row = next((r for r in obj[key] if r['slug'] == slug), None)
        if row is None:
            print(name, 'NO ENTRY')
        elif key == 'sites':
            print(json.dumps({k: row.get(k) for k in ['coordinate_used','coordinate_source','flags']}, ensure_ascii=True))
        elif name.startswith('imagery'):
            print(json.dumps({k: row.get(k) for k in ['status','point','composite','missing_reason']}, ensure_ascii=True))
        else:
            print(json.dumps(row, ensure_ascii=True))
