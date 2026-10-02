"""Preselect an audit sample before observing primary plate images.

The inclusion frame is clean single-line Mayig faces with a matched CISI base.
This audits broad visual transcription consistency, not semantic reading.
"""
from pathlib import Path
import json, random, re, hashlib
import fitz

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
faces=[json.loads(s) for s in (ROOT/'data/normalized/mayig_faces.jsonl').read_text(encoding='utf-8').splitlines()]
eligible=[r for r in faces if r['max_damage']==0 and r['max_uncertainty']==0 and r['line_count']==1]
eligible.sort(key=lambda r:r['record_id'])
seed=20261001
chosen=random.Random(seed).sample(eligible,25)
chosen.sort(key=lambda r:int(re.search(r'\d+',r['record_id']).group()))
audit=json.loads((ROOT/'data/normalized/mayig_lipi_cisi_audit.json').read_text(encoding='utf-8'))
print(type(audit).__name__)
selection={'seed':seed, 'method':'Uniform seeded sample of 25 Mayig zero-damage, zero-uncertainty, single-line faces; selected before plate observation.',
           'eligible_count':len(eligible),'source_faces_sha256':hashlib.sha256((ROOT/'data/normalized/mayig_faces.jsonl').read_bytes()).hexdigest(),
           'selected_ids':[r['record_id'] for r in chosen], 'rows':chosen}
(OUT/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'eligible':len(eligible),'selected_ids':selection['selected_ids']}))
pdf=fitz.open(ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf')
for page_no in (37,50,65,70,80,90):
    page=pdf[page_no-1]
    page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT/f'locate_pdfpage_{page_no}.png')
