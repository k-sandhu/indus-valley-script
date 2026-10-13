"""Freeze separate source-frame and declaration counts without pooling lineages."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=HERE/'source-summary-v1.json'
    if out.exists():raise SystemExit('Summary endpoint exists; no overwrite.')
    names=['material/sources.json','material/observations.json','texts/SOURCES-v2.json',
           'texts/OBSERVATIONS.json','texts/LEXICAL-SOURCE-OBSERVATIONS.json',
           'review/sources-v2.json','review/observations-v2.json',
           'coordinator/sources-v2.json','coordinator/observations-v2.json',
           'coordinator/comparisons-v1.json','coordinator/run-v1/audit.json']
    data={name:json.loads((PACKAGE/name).read_text('utf-8')) for name in names}
    mat=data[names[1]]['observations'];text=data[names[3]]['observations'];lex=data[names[4]]['observations']
    review=data[names[6]]['observations'];own=data[names[8]]['observations']
    comparisons=data[names[9]]['comparisons'];audits=data[names[10]]['comparisons']
    main=[row for row in text if row['observation_id'].startswith('TX-RV')]
    status={'scope':'Separate purposive frames. Records/editions, source readers and shared excavation lineages are not independent observations and are not pooled.',
            'input_sha256':{name:sha(PACKAGE/name) for name in names},
            'material':{'source_records':len(data[names[0]]['sources']),'observations':len(mat),
                        'observed_teaching_relationships':sum(row['teaching_relationship_observed'] is not None for row in mat),
                        'diagnostic_cross_domain_joins':sum(row['diagnostic_cross_domain_join'] for row in mat)},
            'texts':{'source_records':len(data[names[2]]['sources']),'main_stanzas':len(main),
                     'control_observation_summaries':len(text)-len(main),'lexical_source_observations':len(lex),
                     'authored_observation_records':len(text)+len(lex)},
            'independent_review':{'target_records':len(data[names[5]]['sources']),
                                  'scoped_primary_works':6,'unavailable_target_records':1,
                                  'observations':len(review),'scope':'Six inspected works at recorded scopes; Pollock target unavailable. Some overlap with the text and coordinator frames.'},
            'coordinator_controls':{'source_records':len(data[names[7]]['sources']),'observations':len(own)},
            'comparisons':{'cases':len(comparisons),'rival_records':sum(len(row['rivals']) for row in comparisons),
                           'asserted_traced_local_literary_descent':sum(row['claims_traced_local_literary_descent'] for row in audits),
                           'declared_record_completeness':sum(row['declared_local_descent_record_completeness'] for row in audits),
                           'scope':'The completeness field checks declarations; manual semantic review assesses relevance and rival conclusions.'}}
    assert status['texts']['main_stanzas']==27 and status['texts']['authored_observation_records']==43
    with out.open('x',encoding='utf-8') as stream:json.dump(status,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({k:status[k] for k in ['material','texts','independent_review','coordinator_controls','comparisons']},ensure_ascii=True))


if __name__=='__main__':main()
