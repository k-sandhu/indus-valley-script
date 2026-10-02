from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'experiments/2026-10-02-six-hour/harappa-object-frame'
r = json.loads((OLD / 'annotated/results.json').read_text(encoding='utf-8'))
print('endpoint keys:', list(r))
for key, value in r.items():
    if isinstance(value, list) and value:
        print(key, len(value), json.dumps(value[0], ensure_ascii=False))
    elif isinstance(value, dict):
        print(key, 'dict keys', list(value)[:20])
rows = [json.loads(x) for x in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
chosen = [x for x in rows if x.get('source_cisi','').replace('-','') in {f'H{n}' for n in range(2218,2240)}]
print('selected', len(chosen))
for x in chosen:
    print(x['source_cisi'], x['record_id'], x['signs_visual_ltr'])
idx = json.loads((ROOT / 'data/lipi/src/assets/data/seal_id_and_image_mapping.json').read_text(encoding='utf-8'))
for key in idx:
    if key.replace('-','') in {f'H{n}' for n in range(2218,2240)}:
        print('image', key, idx[key])
print('all H22 index keys:', [k for k in idx if k.startswith('H-22')])
