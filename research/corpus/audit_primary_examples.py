"""Compare a small author-selected primary convenience sample to the derivative.

This cannot validate the whole corpus, selection is explicitly nonrandom.
"""
from pathlib import Path
import json,re,collections,hashlib
ROOT=Path(__file__).resolve().parents[2]; N=ROOT/'data'/'normalized'
rows=[json.loads(x) for x in (N/'lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
doc=json.loads((N/'fuls2010_example_codes.json').read_text(encoding='utf-8'))
findings=[]
for r in doc['rows']:
    seq=re.findall(r'\d+',r['code'])
    family=[c for c in rows if c['object_family_id']==r['icit_id']]
    # Exact primary sequence plus archaeological excavation ID is safer than ID alone.
    code_matches=[c for c in rows if c['site']==r['site'] and c['object_type']==r['type'] and c['signs_visual_ltr']==seq]
    excavation_matches=[c for c in rows if c['site']==r['site'] and r['excavation'].replace(' ','').upper() in c['metadata']['excavation-idno'].replace(' ','').upper()]
    findings.append({'primary_icit_id':r['icit_id'],'primary_code':r['code'],'primary_type':r['type'],
                      'numeric_family_lipi_candidates':[{'id':c['record_id'],'cisi':c['source_cisi'],'code':c['text_code_visual_ltr'],'excavation':c['metadata']['excavation-idno'],'type':c['object_type']} for c in family],
                      'exact_code_matches_same_site_type':[{'id':c['record_id'],'cisi':c['source_cisi'],'excavation':c['metadata']['excavation-idno']} for c in code_matches],
                      'excavation_lipi_candidates':[c['record_id'] for c in excavation_matches],
                      'family_has_matching_excavation':any(c['metadata']['excavation-idno'].replace(' ','').upper()==r['excavation'].replace(' ','').upper() for c in family)})
summary={'source_url':doc['source_url'],'sampling':doc['sampling'],'primary_rows':len(findings),
          'examples_with_exact_code_match_same_site_type':sum(bool(x['exact_code_matches_same_site_type']) for x in findings),
          'families_with_matching_excavation':sum(x['family_has_matching_excavation'] for x in findings),
          'findings':findings,'limitations':'ICIT numeric IDs in 2010 examples are different from current IDs. Agreement of sign code and archaeological context on a small nonrandom sample confirms some stability, not full corpus accuracy. Code matching alone is not physical-object identification.'}
(N/'primary_example_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
