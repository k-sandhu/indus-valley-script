"""Internal reference consistency checks only; no machine predictions read."""
from pathlib import Path
from datetime import datetime,timezone
import json
import hashlib

OUT=Path(__file__).resolve().parent
CHART=OUT.parent/'chart_complete'
fresh=json.loads((OUT/'manual_reference.json').read_text(encoding='utf-8'))
ten=json.loads((OUT.parent/'font_row_audit/manual_reference.json').read_text(encoding='utf-8'))
cols=json.loads((CHART/'manual_columns1_4.json').read_text(encoding='utf-8'))
col0=json.loads((CHART/'column0_reinspection.json').read_text(encoding='utf-8'))
chart={(20,0,r['row_0based']):set(r.get('candidate_codes',[r['code']])) for r in col0['rows']}
for col in cols['columns']:
    for r in col['rows']:
        chart[(20,col['col_0based'],r['row_0based'])]=set(r.get('candidate_codes',[r['code']]))
seen=set()
checked=[]
for data in (ten,fresh):
    for row in data['rows']:
        for u in row['units']:
            for ref in u['chart_references']:
                key=(ref['pdf_page_1based'],ref['col_0based'],ref['row_0based'])
                if key in chart and (key,ref['code']) not in seen:
                    checked.append({'reference':key,'code':ref['code'],'numeric_reference_candidates':sorted(chart[key]),'compatible':ref['code'] in chart[key]})
                    seen.add((key,ref['code']))
bad=[r for r in checked if not r['compatible']]
manifest=json.loads((OUT/'source_selection_manifest.json').read_text(encoding='utf-8'))
expected={(r['col_0based'],r['row_0based']) for r in manifest['rows']}
actual={(r['col_0based'],r['row_0based']) for r in fresh['rows']}
missing_crops=[]
hash_errors=[]
for row in fresh['rows']:
    crop=OUT/row['source_crop']
    if not crop.is_file():
        missing_crops.append(str(crop))
    elif hashlib.sha256(crop.read_bytes()).hexdigest()!=row['source_crop_sha256']:
        hash_errors.append(str(crop))
result={
    'method':'Internal source-reference consistency, not external expert validation or machine-transcription scoring',
    'checked_utc':datetime.now(timezone.utc).isoformat(),
    'fresh_reference_sha256':hashlib.sha256((OUT/'manual_reference.json').read_bytes()).hexdigest(),
    'selected_rows_preserved':expected==actual,
    'checked_chart_reference_count':len(checked),
    'chart_reference_conflicts':bad,
    'crop_missing':missing_crops,
    'crop_hash_errors':hash_errors,
    'checks':checked,
}
(OUT/'reference_consistency_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert expected==actual and not bad and not missing_crops and not hash_errors
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
