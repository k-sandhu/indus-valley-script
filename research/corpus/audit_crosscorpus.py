"""Conservative CISI/side-aware comparisons; no bulk sign merging or reading."""
from pathlib import Path
import json,collections,re
ROOT=Path(__file__).resolve().parents[2]
N=ROOT/'data'/'normalized'
def rows(name): return [json.loads(x) for x in (N/name).read_text(encoding='utf-8').splitlines()]
lipi=rows('lipi_observed_faces.jsonl'); old=rows('indus_website_observed.jsonl'); mayig=rows('mayig_faces.jsonl')
li=collections.defaultdict(list)
for r in lipi:
    if r['source_cisi'] not in {'-','',None}:
        li[r['source_cisi'].upper()].append(r)

old_results=[]
for r in old:
    cisi=(r['source_cisi'] or '').upper()
    candidates=li.get(cisi,[])
    seq=r['signs_visual_ltr']
    exact=[c['record_id'] for c in candidates if c['signs_visual_ltr']==seq]
    undamaged=[c['record_id'] for c in candidates if [s for s in c['signs_visual_ltr'] if s!='000']==seq]
    old_results.append({'old_id':r['record_id'],'cisi':cisi,'old_sequence':seq,'candidate_lipi_ids':[c['record_id'] for c in candidates],
                        'exact_matches':exact,'matches_ignoring_lipi_eroded_000':undamaged,
                        'old_zeros_or_line_breaks':len(r['parts_visual_ltr'])-1})

schema=json.loads((N/'mayig_sign_schema.json').read_text(encoding='utf-8'))['signs']
mayig_results=[]
for r in mayig:
    # Mayig IDs carry side letter, lipi CISI column generally carries base object ID.
    base=re.sub(r'[A-Z]+$','',r['record_id']).upper()
    candidates=li.get(base,[])
    mseq=r['signs_visual_ltr']
    # Token-level candidate W sets, never choosing one allograph arbitrarily.
    ws=[{s[1:].zfill(3) for s in schema[p].get('wells_graphemes',[])} for p in mseq]
    compat=[]
    for c in candidates:
        wseq=c['signs_visual_ltr']
        if len(wseq)==len(ws) and all(w in choices for w,choices in zip(wseq,ws)):
            compat.append(c['record_id'])
    mayig_results.append({'mayig_id':r['record_id'],'cisi_base':base,'p_sequence':mseq,
                          'w_candidate_sets':[sorted(s) for s in ws], 'lipi_candidate_ids':[c['record_id'] for c in candidates],
                          'compatible_lipi_ids':compat,'damaged':r['max_damage']>0,'uncertain':r['max_uncertainty']>0,
                          'unknown_sign':r['has_unknown_sign'],'clear_transcription':r['clear_transcription']})

summary={'old_to_lipi_cisi_join':{'rows':len(old),'has_nonempty_cisi':sum(bool(x['cisi']) for x in old_results),
                              'cisi_found':sum(bool(x['candidate_lipi_ids']) for x in old_results),
                              'exact_sequence_match_any_face':sum(bool(x['exact_matches']) for x in old_results),
                              'match_after_ignoring_eroded_000':sum(bool(x['matches_ignoring_lipi_eroded_000']) for x in old_results)},
         'mayig_to_lipi_cisi_join':{'rows':len(mayig),'cisi_found':sum(bool(x['lipi_candidate_ids']) for x in mayig_results),
                                'compatible_wells_candidate_sets_any_face':sum(bool(x['compatible_lipi_ids']) for x in mayig_results),
                                'zero_feature_flag_faces':sum(not x['damaged'] and not x['uncertain'] for x in mayig_results),
                                'clear_faces':sum(x['clear_transcription'] for x in mayig_results),
                                'clear_compatible_faces':sum(x['clear_transcription'] and bool(x['compatible_lipi_ids']) for x in mayig_results)},
         'warnings':['CISI base identifies a physical object, not a side. Any-face matches confirm code correspondence but do not resolve side identity.',
                     'Many-to-many W candidate sets confirm compatibility only; they do not independently verify exactly which allograph should be assigned.',
                     'Unmatched texts may reflect side differences, graphic variants, damage, transcription changes or errors; this audit does not choose among them.',
                     'Lipi and old website share an upstream maintainer; their agreement is version stability, not independent scholarly authentication.']}
for name,data in [('old_lipi_cisi_audit.json',old_results),('mayig_lipi_cisi_audit.json',mayig_results),('crosscorpus_summary.json',summary)]:
    (N/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
