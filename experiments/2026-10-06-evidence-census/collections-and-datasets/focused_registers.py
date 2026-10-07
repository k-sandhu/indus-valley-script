"""Integrate focused aggregates while retaining the previous pass in history."""
import collections,csv,json
from pathlib import Path
from focused_fetch import ROOT,RAW
from focused_analysis import OWN,load,dump,csvout

HISTORY=OWN/'history/2026-10-07-depth-pass'
MAP={'National Museum New Delhi':'National Museum, New Delhi','Indian Museum Kolkata':'Indian Museum, Kolkata','British Museum':'British Museum','Penn Museum':'Penn Museum','Louvre':'Louvre','Metropolitan Museum of Art':'Metropolitan Museum of Art'}
FIELD_KEYS=['accession_number','findspot','excavation_number','date','dimensions','material','photographs','multiple_views','bibliography']
def run():
    summary=load(OWN/'focused-summary.json');records=load(RAW/'focused-records.json');portal=load(RAW/'portal-unique-review.json');queries=load(RAW/'portal-enumeration.json')
    field_counts={r['source']:r for r in csv.DictReader((OWN/'focused-field-counts.csv').open(encoding='utf8'))}
    query_rows=list(csv.DictReader((OWN/'focused-query-log.csv').open(encoding='utf8')))
    register=load(HISTORY/'collection-register.json');all_records={};term_rows=[]
    for q in queries:
        unique={r['recordIdentifier']:r for r in q['records']};all_records.update(unique)
        counts=collections.Counter(r['museumName'] for r in unique.values())
        for museum in ['National Museum, New Delhi','Indian Museum, Kolkata','Allahabad Museum, Prayagraj','National Gallery of Modern Art, New Delhi','Victoria Memorial Hall, Kolkata']:
            term_rows.append(dict(term=q['term'],institution=museum,result_count=counts[museum],all_museum_query_total=q['total'],query_complete=q['complete'],page_count=len(q['pages']),date='2026-10-07',http_status=200,query_url=next(x['url'] for x in query_rows if x['name']==q['pages'][0]['name']),deduplication='recordIdentifier within term',raw_enumeration='data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/portal-enumeration.json'))
    csvout(OWN/'portal-term-counts.csv',term_rows)
    union_counts=collections.Counter(r['museumName'] for r in all_records.values())
    candidate_rows=[]
    for museum in union_counts:
        subset=[r for r in portal if r['fields'].get('Museum Name')==museum];nums=collections.Counter(r['status'] for r in subset)
        candidate_rows.append(dict(institution=museum,unique_query_records=union_counts[museum],candidate_object_records=len(subset),confirmed_original_inscribed=nums['confirmed_description'],modern_copies=nums['modern_copy'],unconfirmed_inscription=nums['unconfirmed_inscription'],other_period_or_script=nums['other_period_or_script'],count_basis='Complete union of seven keyword query result sets; candidates selected from title/description; not an institution inventory'))
    csvout(OWN/'portal-candidate-counts.csv',candidate_rows)
    licence={
        'National Museum New Delhi':('No open image reuse licence verified; portal footer reserves rights','No open data reuse licence verified'),
        'Indian Museum Kolkata':('No open image reuse licence verified; portal footer reserves rights','No open data reuse licence verified'),
        'British Museum':('Most Trustee-owned images: CC BY-NC-SA 4.0; third-party and marked-item exceptions; direct policy request 403, official provider text reviewed','No blanket bulk data licence verified; institutional text/data mining terms apply'),
        'Penn Museum':('Research, educational and personal use with credit; commercial use excluded by terms; no image CC0 grant','Downloaded datasets CC BY 4.0; data page updated 2026-09-30, 144.25 MB; images excluded'),
        'Louvre':('Medium-format photographs of public-domain works: limited private/scientific/educational reuse under CGU 4.1.1.2, credit and permalink; other uses require permission/fees; not CC0','Record information: Etalab Open Licence 2.0, CGU 4.1.2, attribution and update date'),
        'Metropolitan Museum of Art':('Five sampled records mark images Public Domain; official Open Access policy uses CC0 for eligible images','Basic public-domain collection data under CC0; website works, search API returned 410 in earlier depth pass')
    }
    prefixes={'National Museum New Delhi':['portal-','object-nat_del-','nm-own-'],'Indian Museum Kolkata':['portal-','object-im_kol-'],'Allahabad Museum':['portal-'],'British Museum':['bm-'],'Penn Museum':['penn-'],'Louvre':['louvre-'],'Metropolitan Museum of Art':['met-'],'MFA Boston':['mfa-'],'National Museum of Pakistan Karachi':['pakistan-'],'ASI site museums: Lothal, Kalibangan, Dholavira, Rakhigarhi':['nmma-','asi-'],'Archaeological Museum Kalibangan':['nmma-kalibangan','asi-'],'Dholavira site museum':['asi-'],'Rakhigarhi Site Museum and Interpretation Centre':['asi-']}
    for row in register['collections']:
        inst=row['institution']
        if inst not in prefixes:continue
        attempts=[dict(name=q['name'],url=q['url'],requested_at=q['requested_at'],http_status=int(q['http_status']) if q['http_status'] else None,result_count=int(q['result_count']) if q['result_count'] else None,count_basis=q['count_basis'],record_fields_seen=q['record_fields_seen'],raw_body=q['raw_body'],response_complete=q['response_complete']=='True',error=q['error']) for q in query_rows if any(q['name'].startswith(p) for p in prefixes[inst])]
        focused=dict(date='2026-10-07',status='Exploratory',query_attempts=attempts,query_log='focused-query-log.csv',web_search_witnesses=['data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/web-focused-verification.json','data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/web-regional-rights.json'],not_found_vs_not_queried='Queries executed; blocked, timeout and missing total are unmeasured, not zero')
        if inst in MAP:
            key=MAP[inst];info=summary['by_institution'][key];fc=field_counts[key]
            focused.update(inscribed_original_record_minimum=info['inspected_original_records'],object_type_counts=info['object_types'],count_basis='Inspected inscription-confirmed original records; minimum within bounded queries, not complete institution inventory',inscription_inventory_total=None,records_with_usable_identifier=None,confirmed_corpus_joins=info['confirmed_joins'],join_fraction=info['join_fraction'],metadata_field_counts={k:int(fc[k]) for k in FIELD_KEYS},records_inspected=int(fc['records_inspected']),named_site=int(fc['named_site']),image_count_unmeasured=int(fc['image_count_unmeasured']),image_licence=licence[inst][0],data_licence=licence[inst][1],image_count_basis='Exposed object-image slots; distinct physical views unverified; BM slots unmeasured, Met primary image minimum')
            row['record_fields']={k:bool(int(fc[k])) if k not in ['photographs','multiple_views'] or key!='British Museum' else None for k in FIELD_KEYS}
            row['result_count']=info['inspected_original_records'];row['count_basis']=focused['count_basis'];row['search_status']='Focused inscription-confirmed minimum; see focused_pass and raw query responses';row['query_date']='2026-10-07'
            row['image_data_licence']='Images: '+licence[inst][0]+'. Data: '+licence[inst][1]
            row['cisi_or_excavation_join']=str(info['confirmed_joins'])+'/'+str(info['inspected_original_records'])+' inspected originals joined; see paired-full-audit.csv'
            if inst in ['National Museum New Delhi','Indian Museum Kolkata']:
                focused.update(unique_keyword_query_records=union_counts[key],portal_candidates=next(r for r in candidate_rows if r['institution']==key),term_counts=[r for r in term_rows if r['institution']==key],api_or_bulk='Public internal JSON fetch route; no documented stable bulk API or redistribution grant verified')
                row['api_or_bulk_download']=focused['api_or_bulk']
            elif inst=='Penn Museum':
                focused.update(inscription_filter_record_count=34,original_seals=5,plaster_impression_records=29,count_basis='Complete 34-record Indus Script filter: 5 original seals and 29 plaster impressions by type/material facets; broader queries are not completely adjudicated')
                row['api_or_bulk_download']='Public CSV metadata download advertised, 144.25 MB, updated 2026-09-30; not downloaded'
                focused['loan_note']='The five originals carry MFA Boston numbers and Penn L-141 loan numbers; counted once at Penn, not again as MFA online records'
            elif inst=='British Museum':focused['count_limit']='Six cached official catalogue witnesses; direct HTTP 403 and browser search malfunction; 724 culture objects excluded as an inscription total'
            elif inst=='Louvre':focused['count_limit']='Four per-object JSON records HTTP 200; search query 429 and browser human-verification challenge; 21 cached mixed records is not an inscription count'
            elif inst=='Metropolitan Museum of Art':focused['count_limit']='Website Indus query 76 records, fully enumerated using offset=42; five seal records individually inspected; page=2 ignored by website; other types not all adjudicated for script'
        elif inst=='Allahabad Museum':
            focused.update(unique_keyword_query_records=union_counts['Allahabad Museum, Prayagraj'],candidate_object_records=0,inscribed_original_record_minimum=0,inscription_inventory_total=None,count_basis='Zero inscription/seal/tablet candidates in the 65-record seven-term union; returned descriptions are a bounded search frame, not complete holdings',term_counts=[r for r in term_rows if r['institution']=='Allahabad Museum, Prayagraj'],not_found_vs_not_queried='Queried: no candidate found in this seven-term frame; holdings total unmeasured')
            row['result_count']=0;row['count_basis']=focused['count_basis'];row['search_status']='Queried; no inscription candidate found in bounded portal frame'
        elif inst=='MFA Boston':
            focused.update(inscribed_original_record_minimum=None,inscription_inventory_total=None,count_basis='Own catalogue HTTP 403 / browser blank; five MFA-numbered seals documented at Penn, not an MFA catalogue count',cross_catalogue_witnesses=5,image_licence='Unverified for MFA own catalogue',data_licence='Unverified')
            row['result_count']=None;row['count_basis']=focused['count_basis']
        elif inst=='National Museum of Pakistan Karachi':
            focused.update(inscribed_original_record_minimum=None,inscription_inventory_total=None,count_basis='Official museum/gallery description found, no object-level public inventory located; direct request SSL transfer failure',online_catalogue='No object-level public catalogue located by these official-site searches; gallery page exists',image_licence='No open reuse licence verified',data_licence='No bulk record access verified')
            row['result_count']=None;row['count_basis']=focused['count_basis']
        else:
            focused.update(inscribed_original_record_minimum=1 if inst.startswith('ASI site') else None,inscription_inventory_total=None,count_basis='Lothal earlier object witness gives five signs; 133 seal/sealing category entries remain unadjudicated, direct NMMA route timed out; other site inventories not located or inaccessible',online_catalogue='Lothal NMMA sample/category; Kalibangan route timed out; Dholavira/Rakhigarhi object inventory not located in official-site searches',image_licence='No open image reuse licence verified',data_licence='No bulk record access verified')
        row['focused_pass']=focused
    register['note']='Focused results are dated 2026-10-07; result_count now holds confirmed record minima or a bounded queried zero for focal collections, with exact count_basis. Earlier observations remain in depth_pass and history. Null is unmeasured, not zero.'
    dump(OWN/'collection-register.json',register)
    csvrows=[]
    for row in register['collections']:
        out={k:row.get(k,'') for k in ['institution','region','online_catalogue','query','query_date','search_status','result_count','count_basis','image_data_licence','api_or_bulk_download','cisi_or_excavation_join','notes']}
        out.update({k:row.get('record_fields',{}).get(k) for k in FIELD_KEYS});f=row.get('focused_pass',{})
        out.update(focused_date=f.get('date',''),focused_count=f.get('inscribed_original_record_minimum'),focused_count_basis=f.get('count_basis',''),focused_joins=f.get('confirmed_corpus_joins'),focused_query_log=f.get('query_log',''));csvrows.append(out)
    csvout(OWN/'collection-register.csv',csvrows)
    datasets=load(HISTORY/'dataset-register.json')
    for d in datasets['datasets']:
        if d['name']=='Lipi':
            d['metadata_fields']=['source_cisi','metadata.excavation-idno','site','object_type','material','horizontal(mm)','vertical(mm)','thickness(mm)','sign sequence','face/object family identifiers']
            d['focused_pass_review']=dict(date='2026-10-07',status='Exploratory',local_export_faces=5680,local_export_object_families=4695,excavation_identifier_faces_Mohenjo_daro=1831,excavation_identifier_faces_Harappa=2652,corpus_sha256=summary['corpus_sha256'],confirmed_museum_joins=61,comparison_output='paired-full-audit.csv',provenance='Reused existing normalized export and source CSV; undelimited concatenations already occur in source CSV and were not introduced by normalize_lipi.py',rights='Local-only observational export; earlier pinned licence assessment retained')
        elif d['name'] in ['CISI photographic corpus and editions','Helsinki CISI photographs and editions']:
            d['focused_pass_review']=dict(date='2026-10-07',status='Exploratory',edition_used='CISI volume 1, Collections in India (Joshi and Parpola, eds., 1987)',location='Basic data pp. 366–372; 42 manually checked museum/excavation concordance rows, 41 found by source_cisi in this export',raw_concordance='data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/cisi1-concordance-transcription.json',reuse='Complete existing local CISI1 scan reused; official 76884.pdf is volume 1, not volume 3',rights='No general image reuse licence verified for this edition; scan and extracted rows remain local-only')
            if d['name']=='CISI photographic corpus and editions':d['licence']='No general image reuse licence verified for CISI 1987/1991/2010 editions; earlier Finnish concordance licence statements are separate publications'
        elif d['name']=='Museum APIs and collection portals':
            d['focused_pass_review']=dict(date='2026-10-07',status='Exploratory',museums_of_india='Seven complete paginated term queries, 4007 unique record IDs, 158 candidate pages, 94 unique description-confirmed originals',met='HTTP 410 API history retained; website HTTP 200 with five inspected seals',penn_bulk='CSV metadata advertised 2026-09-30, 144.25 MB, CC BY 4.0; images excluded; not downloaded',louvre='Per-object JSON works, record data Etalab Open Licence 2.0; images governed separately by CGU',output='focused-summary.json')
    dump(OWN/'dataset-register.json',datasets)
    matrix=list(csv.DictReader((HISTORY/'metadata-field-matrix.csv').open(encoding='utf-8-sig')))
    for r in matrix:
        key=MAP.get(r['source']);fc=field_counts.get(key)
        r['records_inspected']=fc['records_inspected'] if fc else ''
        for f in FIELD_KEYS:r[f+'_records']=fc[f] if fc else ''
        if fc:
            for f in FIELD_KEYS:r[f]=str(int(fc[f])>0) if not (key=='British Museum' and f in ['photographs','multiple_views']) else 'Unmeasured'
            r['field_basis']=fc['field_basis']+'; see focused-field-counts.csv and focused-records.json in raw storage'
        if r['source']=='Lipi':r['excavation_number']='True';r['dimensions']='True';r['material']='True';r['field_basis']='Observed local export schema; size and missingness vary by face; see dataset-register.json focused_pass_review'
    csvout(OWN/'metadata-field-matrix.csv',matrix)
    print('Updated',len(register['collections']),'collections,',len(datasets['datasets']),'datasets,',len(matrix),'matrix rows')

if __name__=='__main__':run()
