"""Record a bounded source-pattern candidate; never join historical numeric IDs."""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'data/normalized/lipi_observed_faces.jsonl'
rows=[json.loads(x) for x in SOURCE.read_text(encoding='utf-8').splitlines()]
matches=[r for r in rows if {'700','900'}<=set(r['signs_visual_ltr']) and {'032','033'}&set(r['signs_visual_ltr'])]
candidate=[r for r in matches if r['source_cisi'].strip()=='H-904']
related=[r for r in rows if r['source_cisi'].strip()=='H-904']
payload={
 'status':'Current-source pattern candidate only; historical Fuls2020 ICIT3786 identity unconfirmed.',
 'method':'Bounded observational query for a face containingW700,W900 andW032orW033; identify current physicalCISI reference and preserve all that object faces. No numericID join across versions.',
 'query_source':'data/normalized/lipi_observed_faces.jsonl',
 'query_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'raw_export_sha256':'c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c',
 'query_matching_rows':len(matches),'query_match_ids':[r['record_id'] for r in matches],
 'candidate_current_source_cisi':'H-904','candidate_query_matches':len(candidate),
 'preserved_current_faces':related,
 'independent_primary_photo_lead':{
   'source':'Vats1940 PlateXCVI no477; metadata table printed349/PDF378, J213, areaD',
   'owner':'/root/literature; /root/methods independently viewed count contrast',
   'local_photo_crop':'research/literature/metrology/primary_numeric/vats_h904/477_crop12x.png',
   'reported_visible_pattern':'Three long strokes next toU/crescent; two next tocircles on opposite face; short marks less clear.',
   'limits':'Photo count contrast and excavation cross-link do not confirm historical3786 identity or numerical equivalence. No semantic coefficient assigned.'},
 'next_required_evidence':'Fuls2020 Figure16 and exact source-object cross-reference; do not replace historicalID with current1786 by arithmetic or context.',
}
out=Path(__file__).with_name('H904_current_pattern_candidate.json')
out.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'query_matches':len(matches),'candidate_cisi':'H-904','preserved_faces':len(related)}))
