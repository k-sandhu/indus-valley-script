from pathlib import Path
import json, collections
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sel=json.loads((OUT/'selection.json').read_text(encoding='utf-8'))
notes={r['id']:r for r in json.loads((OUT/'blind_visual_notes.json').read_text(encoding='utf-8'))['observations']}
schemas=json.loads((ROOT/'data/normalized/mayig_sign_schema.json').read_text(encoding='utf-8'))['signs']
audits={r['mayig_id']:r for r in json.loads((ROOT/'data/normalized/mayig_lipi_cisi_audit.json').read_text(encoding='utf-8'))}
lipi={r['record_id']:r for r in [json.loads(s) for s in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]}
rows=[]
for r in sel['rows']:
    a=audits[r['record_id']]
    candidates=[lipi[i] for i in a['lipi_candidate_ids']]
    row={
        'id':r['record_id'], 'blind_observation':notes[r['record_id']],
        'mayig_signs_visual_ltr':r['signs_visual_ltr'],
        'mayig_descriptions_visual_ltr':[schemas[p]['description'] for p in r['signs_visual_ltr']],
        'mayig_wells_candidate_sets':a['w_candidate_sets'],
        'lipi_candidates':[{'id':c['record_id'],'code':c['text_code_visual_ltr'],'signs_visual_ltr':c['signs_visual_ltr'],
                            'source_complete':c['metadata']['complete'],'source_single_line':c['single_line'],'source_direction':c['direction']} for c in candidates],
        'any_candidate_compatible':bool(a['compatible_lipi_ids']),
        'compatible_lipi_ids':a['compatible_lipi_ids'],
    }
    rows.append(row)
    print(r['record_id'], 'COMPAT' if row['any_candidate_compatible'] else 'DIFF', str([c['text_code_visual_ltr'] for c in candidates]))
    print(' | '.join(f"{p}: {schemas[p]['description']}" for p in r['signs_visual_ltr']))
(OUT/'comparisons.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
