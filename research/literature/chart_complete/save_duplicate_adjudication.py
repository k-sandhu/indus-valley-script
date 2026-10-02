"""Post-comparison original-source adjudication; preserve all prior references."""
from pathlib import Path
import json,shutil
B=Path(__file__).parent
observed=[
 (20,2,1,43,369,'high',[],'Middle digit has curved six form; no uniqueness constraint used.'),
 (21,5,9,313,359,'high',[],'Middle digit has five form.'),
 (20,4,1,86,506,'high',[],'Retained duplicate506; no forced uniqueness.'),
 (21,7,5,350,506,'high',[],'Terminal digit degraded but six shape retained; duplicate506 remains.'),
 (20,4,13,93,360,'high',[],'Middle digit has six shape.'),
 (21,1,19,234,350,'high',[],'Middle digit has five shape.'),
 (20,4,21,98,465,'high',[],'Middle digit has an open top and lower loop, six.'),
 (20,7,24,153,485,'high',[],'Middle digit is two-loop eight.'),
 (20,7,25,153,383,'high',[],'Middle digit reads eight, with upper and lower curves.'),
 (21,8,33,387,363,'high',[],'Middle digit reads six; previously adjudicated from original source.'),
 (20,8,5,162,591,'high',[],'Initial digit reads five.'),
 (21,8,2,368,691,'high',[],'Initial digit reads six; compare the six in upper rank on this same original cell.'),
 (20,9,19,193,676,'high',[],'Initial digit reads six.'),
 (21,4,7,291,576,'high',[],'Initial digit reads five.'),
 (20,9,33,202,53,'high',[],'Initial digit reads five.'),
 (21,8,16,378,63,'medium',[53],'Initial digit best six but degraded five/six remains; preserve both candidates.'),
]
rows=[]
for p,c,r,rank,code,confidence,alts,note in observed:
 rows.append({'pdf_page':p,'printed_page':p-1,'column_0based':c,'row_0based':r,
  'upper_rank':rank,'lower_stable_finnish_code':code,'upper_confidence':'high',
  'lower_confidence':confidence,'lower_alternatives':alts,'candidate_union':sorted(set([code]+alts)),
  'numeric_underlining':False,'note':note,'source_image':f'pdf{p}_c{c}_r{r}.png'})
out={'method':'Manual original 1979 PDF numeric-label reinspection,12x. Coordinates were flagged by parent as duplicate best-code groups. No uniqueness assumption, root predicted code or matching score resolves a glyph. Post-comparison sensitivity, not a fresh blind score.',
 'source_sha256':'7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27',
 'rows':rows,'confirmed_duplicate':{'code':506,'cells':[[20,4,1],[21,7,5]],'status':'Both original numeric labels read506; preserve rather than deduplicate by assumption.'},
 'scope':'Printed numeric labels only. Does not validate sign drawings, allograph identity, phonetics or semantics.'}
(B/'duplicate_labels/adjudication.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for stem in ['full21_audit','manual_numeric_labels']:
 for ext in ['json','csv']:
  src=B/f'{stem}.{ext}';dst=B/f'{stem}_before_duplicate_adjudication.{ext}'
  if not dst.exists():shutil.copyfile(src,dst)
q=B/'save_full_pdf21.py';s=q.read_text(encoding='utf-8')
s=s.replace('(368,591)','(368,691)').replace('(378,53)','(378,63)')
s=s.replace('AMBIGUOUS={','AMBIGUOUS={\n (8,16):{\'lower_confidence\':\'medium\',\'lower_alternatives\':[53],\'note\':\'Post-duplicate source reinspection:63 best,53 possible. Preserve both; not selected by uniqueness.\'},')
s=s.replace('post-comparison source adjudication of22 disagreements','post-comparison source adjudication of22 disagreements and later duplicate-label source checks')
q.write_text(s,encoding='utf-8')
q=B.parent/'chart_label_audit/save_full_pdf20_owned.py';s=q.read_text(encoding='utf-8')
s=s.replace('(153,363)','(153,383)').replace('(193,576)','(193,676)')
s=s.replace("'method':'Blind original-image reading; root templates, OCR labels and match results not inspected.'","'method':'Initial independent original-image reading preserved in manual_numeric_labels_before_duplicate_adjudication.json; current source reinspection corrects c7r25 to383 and c9r19 to676. Later duplicate-label flags do not enforce uniqueness. Numeric labels only.'")
q.write_text(s,encoding='utf-8')
print('Saved16 source adjudications, preserved old references, updated reproducible manual writers.')
