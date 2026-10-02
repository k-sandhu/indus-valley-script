"""Enumerate complete fish-adjacent two-stroke candidates for primary audit.

No numerical value or phonetic meaning is assigned. This selects from observed
catalogue descriptions; independent plate observations are recorded separately.
"""
from pathlib import Path
import json, collections
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'fish_strokes'
OUT.mkdir(exist_ok=True)
faces=[json.loads(s) for s in (ROOT/'data/normalized/mayig_faces.jsonl').read_text(encoding='utf-8').splitlines()]
schema=json.loads((ROOT/'data/normalized/mayig_sign_schema.json').read_text(encoding='utf-8'))['signs']
fish={p for p,s in schema.items() if s['description'].lower().startswith('fish')}
li=collections.defaultdict(list)
for s in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines():
    r=json.loads(s)
    li[r['source_cisi']].append(r)
selected=[]
for r in faces:
    if not r['clear_transcription'] or r['line_count']!=1:
        continue
    seq=r['signs_visual_ltr']
    matches=[]
    for i,p in enumerate(seq):
        if p not in {'P122','P145'}:
            continue
        for j in [i-1,i+1]:
            if 0<=j<len(seq) and seq[j] in fish:
                matches.append({'stroke_position_visual_ltr':i,'fish_position_visual_ltr':j,
                                'stroke_mayig_class':p,'stroke_wells_candidates':schema[p]['wells_graphemes'],
                                'fish_mayig_class':seq[j],'fish_description':schema[seq[j]]['description'],
                                'fish_wells_candidates':schema[seq[j]]['wells_graphemes']})
    candidates=[c for c in li[r['object_family_id']] if c['single_line'] and c['metadata']['complete']=='Y' and c['direction']=='R/L']
    if matches and candidates:
        selected.append({'mayig_id':r['record_id'],'matches':matches,'mayig_visual_ltr':seq,
                         'lipi_candidates':[{'record_id':c['record_id'],'code':c['text_code_visual_ltr'],
                                             'signs_visual_ltr':c['signs_visual_ltr']} for c in candidates]})
selected.sort(key=lambda r:int(r['mayig_id'].split('-')[1].removesuffix('A')))
out={'selection_rule':'All Mayig zero-damage/zero-uncertainty/no-P000 single-line faces with P122 or P145 immediately adjacent to a class whose description starts Fish, and a complete R/L single-line Lipi CISI match.',
     'fish_class_frame':sorted(fish),'rows':selected,'number_of_objects':len(selected),
     'warnings':['Descriptions select graphic family only. Crosswalk arrays are compatibility candidates, not adjudicated fine codes.',
                 'Mayig stroke-height choices are annotator conventions, explicitly acknowledged in its README. Preserve raw sequences.']}
(OUT/'selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(selected),'ids':[r['mayig_id'] for r in selected],
                  'stroke_class_counts':dict(collections.Counter(m['stroke_mayig_class'] for r in selected for m in r['matches']))},indent=2))
for r in selected: print(r['mayig_id'],r['lipi_candidates'][0]['code'],r['matches'])
