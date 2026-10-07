"""Recompute authored counts and paired comparisons from preserved local witnesses.

Run from repository root. No network calls, images, or third-party record exports
are written to the owned directory. Source-specific values are in ignored raw files.
"""
import collections,csv,hashlib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from focused_fetch import ROOT,RAW
from focused_classify import norm
from focused_enumerate import json_body

OWN=Path(__file__).resolve().parent
def load(path):return json.loads(path.read_text(encoding='utf8'))
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def csvout(path,rows,fields=None):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def site(value):
    for pattern,name in [('mohenjo|mohenjod','Mohenjo-daro'),('harapp','Harappa'),('chanhu','Chanhu-daro'),('lothal','Lothal'),('dholavir','Dholavira'),('banawali','Banawali'),('susa|suse','Susa'),('girsu|tello','Girsu/Tello')]:
        if re.search(pattern,value,re.I):return name
    return ''
def museum_keys(r):
    if r['excavation_raw']:
        if r['institution']=='Penn Museum':return ['CH '+n for n in r['excavation_raw'].split('; ')]
        return [r['excavation_raw']]
    # Delimited museum compound numbers retain their excavation prefix. The
    # prefix's interpretation is independently checked against CISI when present.
    if r['institution']=='National Museum, New Delhi':
        m=re.match(r'^((?:DKI|DK|HR|VS|SD|DM|PI|BNL|DHR|SRG|HP|H)[ .-]*\d+[A-Za-z]?)',r['accession'],re.I)
        return [m.group(1)] if m else []
    return []
def corpus_dimensions(c):
    vals=[c['metadata'].get(k,'') for k in ['horizontal(mm)','vertical(mm)','thickness(mm)']]
    if any(v and not re.fullmatch(r'\d+(?:\.\d+)?',v.strip()) for v in vals):return None
    return sorted(float(v) for v in vals if v and float(v)>0)
def museum_dimensions(r):
    text=r['dimensions']
    if not text:return None
    # Met gives imperial followed by metric parentheses. Use the metric group.
    if r['institution']=='Metropolitan Museum of Art':
        m=re.search(r'\(([^()]*?cm)\)',text)
        if m:text=m.group(1)
    factor=25.4 if re.search(r'inch|\bin\.',text,re.I) else 10 if re.search(r'cm|centimet',text,re.I) else 1 if 'mm' in text else None
    if not factor or re.search(r'Of the impression|max depth',text,re.I):return None
    return sorted(float(x)*factor for x in re.findall(r'\d+(?:\.\d+)?',text))
def compare(r,faces):
    c=faces[0];a=site(r['site']);b=site(c['site'])
    sc='agreement' if a and a==b else 'disagreement' if a and b else 'less_specific_or_missing'
    m=r['material'].lower();cm=c['metadata'].get('material','').lower()
    if not cm or cm in ['-','?'] or m in ['others','']:mc='uninformative_or_missing'
    elif cm in m or (cm=='baked clay' and 'terracotta' in m):mc='agreement'
    elif cm=='steatite' and m=='stone':mc='broader_museum_term'
    elif cm=='clay' and m=='terracotta':mc='terminology_difference'
    else:mc='disagreement'
    ct=c['object_type'];typ='seal' if ct.startswith('SEAL') else 'tablet' if ct.startswith('TAB') else ct
    tc='agreement' if r['object_type']==typ else 'terminology_difference'
    md=museum_dimensions(r);cd=corpus_dimensions(c)
    if not r['dimensions']:dc='museum_missing'
    elif md is None or cd is None or not md or not cd or len(md)!=len(cd):dc='incomplete_measurement_comparison'
    else:dc='within_tolerance' if all(abs(a-b)<=max(.5,.05*b) for a,b in zip(md,cd)) else 'outside_tolerance'
    words={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11}
    numeric=re.search(r'\b(\d+|'+ '|'.join(words)+r')\s+(?:characters|signs|pictograms|pictographs|graff?it?ti)(?:\s+marks)?',r['description'],re.I)
    # Multiple faces and multiple count assertions retain the raw wording and
    # are not assigned automatically to a particular face.
    num=words.get(numeric.group(1).lower(),int(numeric.group(1)) if numeric and numeric.group(1).isdigit() else None) if numeric else None
    if numeric and len(faces)==1:ic='count_agreement' if num==c['length'] else 'count_disagreement'
    else:ic='numeric_count_not_comparable'
    return dict(site_comparison=sc,type_comparison=tc,material_comparison=mc,dimensions_comparison=dc,inscription_comparison=ic,museum_dimensions_mm=md,corpus_dimensions_mm=cd)

def run():
    records=load(RAW/'focused-records.json');cross=load(RAW/'cisi1-concordance-transcription.json')
    corpus_path=ROOT/'data/normalized/lipi_observed_faces.jsonl'
    corpus=[json.loads(x) for x in corpus_path.read_text(encoding='utf8').splitlines()]
    cisi=collections.defaultdict(list);exact=collections.defaultdict(list);normalized=collections.defaultdict(list)
    for c in corpus:
        cisi[c['source_cisi']].append(c)
        v=c['metadata'].get('excavation-idno','')
        if v and v not in ['-','--','?']:
            exact[(site(c['site']),v)].append(c);normalized[(site(c['site']),norm(v))].append(c)
    joins=[];full=[];candidates=[];usable=0
    for r in records:
        keys=museum_keys(r); cr=next((x for x in cross if norm(x['museum_accession'])==norm(r['accession']) and (x['registration'].startswith('IM') if r['institution']=='Indian Museum, Kolkata' else x['registration'].startswith(('NMI','LTH')) if r['institution']=='National Museum, New Delhi' else False)),None)
        refs=r.get('published_references',[]); usable_flag=bool(keys or cr or refs)
        # Louvre accession explicitly preserves published CCO catalogue numbers,
        # but this local export has no matching identifiers for its Susa/Girsu rows.
        if r['institution']=='Louvre' and 'CCO ' in r['accession']:usable_flag=True
        usable+=usable_flag
        faces=[];method='';evidence='';shared='';attempts=[]
        for k in keys:
            found=exact.get((site(r['site']),k),[]);kind='exact_excavation'
            if not found:found=normalized.get((site(r['site']),norm(k)),[]);kind='normalized_excavation'
            attempts.append(dict(key=k,exact_face_count=len(exact.get((site(r['site']),k),[])),normalized_face_count=len(normalized.get((site(r['site']),norm(k)),[]))))
            if found and len({x['object_family_id'] for x in found})==1:faces=found;method=kind;shared=k;break
        if cr:
            found=cisi.get(cr['cisi'],[])
            if found and len({x['object_family_id'] for x in found})==1:
                if faces and {x['object_family_id'] for x in faces}!={x['object_family_id'] for x in found}:
                    attempts.append(dict(rejected_direct_collision=[x['record_id'] for x in faces],published_cisi=cr['cisi'],reason='Primary published museum registration crosswalk overrides a different corpus identifier match'))
                    faces=[]
                if not faces:faces=found;method='published_CISI_concordance';shared=cr['registration']+' / '+cr['excavation']
                evidence=f"CISI 1 (1987), printed p. {cr['printed_page']}, row {cr['cisi']}; raw/{cr['witness']}"
            else:attempts.append(dict(published_cisi=cr['cisi'],face_count=len(found)))
        if not faces and refs:
            found=[]
            for ref in refs:
                target=norm('CH '+ref['field']+'Pl. '+ref['plate']+':'+ref['figure'])
                found.extend(x for x in corpus if site(x['site'])==site(r['site']) and norm(x['metadata'].get('excavation-idno',''))==target)
            if found and len({x['object_family_id'] for x in found})==1:
                faces=found;method='shared_field_and_published_plate';shared='; '.join(ref['field']+' / Pl. '+ref['plate']+':'+ref['figure'] for ref in refs);evidence='Penn Bibliography and Other Number; Lipi metadata.excavation-idno'
        if r['institution']=='British Museum' and r['accession']=='1947,0416.4':
            found=[x for x in corpus if x['metadata'].get('excavation-idno')=='HR 5635345' and x['source_cisi']=='M-1906']
            if len(found)==1:
                faces=found;method='published_Marshall_composite';shared='HR 5635 / plate no. 345';evidence='Marshall (ed.) 1931, vol. II, p. 404, table row 345; raw/marshall-table-055.png'
        if not faces:
            candidates.append(dict(institution=r['institution'],accession=r['accession'],record_id=r['record_id'],usable_identifier=usable_flag,attempts=attempts,status='unconfirmed',reason='No unique explicit join in the inspected export/concordance',raw_record=r['raw']))
            continue
        faces=list({x['record_id']:x for x in faces}.values());cmp=compare(r,faces)
        row=dict(institution=r['institution'],museum_record_id=r['record_id'],museum_accession=r['accession'],museum_url=r['url'],cisi='; '.join(sorted({x['source_cisi'] for x in faces})),corpus_record_ids='; '.join(x['record_id'] for x in faces),object_family_id=faces[0]['object_family_id'],join_method=method,shared_identifier=shared,join_evidence=evidence,rejected_direct_collision=any('rejected_direct_collision' in a for a in attempts),**{k:v for k,v in cmp.items() if k.endswith('_comparison')},status='Exploratory',raw_comparison_file='data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/paired-comparisons.json',raw_comparison_key=r['institution']+'|'+r['accession'])
        joins.append(row);full.append(dict(key=row['raw_comparison_key'],museum=r,corpus_faces=faces,comparison=cmp,matching_attempts=attempts,join=row))
    joins.sort(key=lambda r:(r['institution'],norm(r['museum_accession'])))
    for i,r in enumerate(joins):r['sample_30_selected']=i<30
    csvout(OWN/'paired-full-audit.csv',joins);csvout(OWN/'paired-sample-audit.csv',joins[:30])
    dump(RAW/'paired-comparisons.json',full);dump(RAW/'unconfirmed-join-candidates.json',candidates)
    method_counts=dict(collections.Counter(r['join_method'] for r in joins))
    by_inst={}
    for inst in sorted({r['institution'] for r in records}):
        subset=[r for r in records if r['institution']==inst];matched=[r for r in joins if r['institution']==inst]
        by_inst[inst]=dict(inspected_original_records=len(subset),confirmed_joins=len(matched),join_fraction=len(matched)/len(subset),object_types=dict(collections.Counter(r['object_type'] for r in subset)))
    summary=dict(status='Exploratory',observed_on='2026-10-07',inspected_original_records=len(records),usable_identifier_records=usable,confirmed_join_records=len(joins),confirmed_distinct_corpus_families=len({r['object_family_id'] for r in joins}),confirmed_corpus_faces=len({id for r in joins for id in r['corpus_record_ids'].split('; ')}),join_fraction_all_inspected=len(joins)/len(records),join_fraction_usable=len(joins)/usable,selected_sample_size=min(30,len(joins)),join_methods=method_counts,by_institution=by_inst,comparisons={key:dict(collections.Counter(r[key] for r in joins)) for key in ['site_comparison','type_comparison','material_comparison','dimensions_comparison','inscription_comparison']},corpus_faces=len(corpus),corpus_object_families=len({c['object_family_id'] for c in corpus}),corpus_sha256=hashlib.sha256(corpus_path.read_bytes()).hexdigest(),unconfirmed_join_records=len(candidates),selection_rule='First 30 confirmed joins sorted by institution, normalized accession; convenience sample')
    summary['direct_http_200_original_records']=sum(r['institution']!='British Museum' for r in records)
    summary['search_provider_only_original_records']=sum(r['institution']=='British Museum' for r in records)
    summary['rejected_identifier_collisions']=sum(r['rejected_direct_collision'] for r in joins)
    dump(OWN/'focused-summary.json',summary)
    # Field presence uses inspected originals. A populated broad term is present
    # but its specificity is assessed separately in paired comparisons.
    fields=['accession_number','findspot','excavation_number','date','dimensions','material','photographs','multiple_views','bibliography']
    field_rows=[]
    for inst in by_inst:
        subset=[r for r in records if r['institution']==inst];nums=collections.Counter()
        for r in subset:
            vals=dict(accession_number=bool(r['accession']),findspot=bool(r['site']),excavation_number=bool(museum_keys(r) or next((x for x in cross if norm(x['museum_accession'])==norm(r['accession'])),None)),date=bool(r['date']),dimensions=bool(r['dimensions']),material=bool(r['material']),photographs=r['image_slots'] is not None and r['image_slots']>0,multiple_views=r['image_slots'] is not None and r['image_slots']>1,bibliography=bool(r['bibliography']))
            nums.update(k for k,v in vals.items() if v)
        field_rows.append(dict(source=inst,records_inspected=len(subset),**{f:nums[f] for f in fields},named_site=sum(bool(site(r['site'])) for r in subset),image_count_unmeasured=sum(r['image_slots'] is None for r in subset),field_basis='Inspected originals; findspot includes broad geography; named_site counts site-specific values; multiple_views counts image slots, physical view identity not inspected; excavation_number includes published crosswalk-supported compound components'))
    csvout(OWN/'focused-field-counts.csv',field_rows)
    # Every direct request, including failures and ignored pagination, is indexed.
    query_rows=[]
    portal_pages={r['body']:r for r in load(RAW/'portal-record-review-v2.json')}
    inspected_by_body={r['raw']:r for r in records}
    for p in sorted(RAW.glob('*.request.json')):
        log=load(p);count=None;basis='not a search total / unmeasured'
        body=RAW/(p.name.removesuffix('.request.json')+'.body')
        if log.get('http_status')==200 and body.exists():
            try:
                j=json_body(body.read_bytes())
                if isinstance(j,dict) and 'resultSize' in j:count=j['resultSize'];basis='Returned portal matches; mixed object types'
            except (ValueError,UnicodeError):pass
            if p.stem.startswith('penn-'):
                text=BeautifulSoup(body.read_bytes(),'html.parser').get_text(' ',strip=True)
                m=re.search(r'\d+\s*-\s*\d+ of ([\d,]+) Records',text)
                if m:count=int(m.group(1).replace(',',''));basis='Catalogue records; objects and possibly finding aids, filter recorded in URL'
            if p.stem.startswith('met-') and 'collection/search' in log.get('url',''):
                text=BeautifulSoup(body.read_bytes(),'html.parser').get_text(' ',strip=True)
                m=re.search(r'([\d,]+) results for',text)
                if m:count=int(m.group(1).replace(',',''));basis='Website search matches; mixed types; Indus seal is broad matching'
                elif 'One result for' in text:count=1;basis='Website search matches; mixed types'
        body_ref=log.get('body','')
        if not body_ref and (RAW/(p.name.removesuffix('.request.json')+'.pdf')).exists():body_ref=str((RAW/(p.name.removesuffix('.request.json')+'.pdf')).relative_to(ROOT))
        seen=[]
        if body_ref in portal_pages:seen=list(portal_pages[body_ref]['fields'])
        elif body_ref in inspected_by_body:
            r=inspected_by_body[body_ref];seen=[k for k in ['accession','site','material','dimensions','date','description','bibliography','excavation_raw'] if r.get(k)];seen+=['image_slots'] if r.get('image_slots') else []
        elif log.get('name','').startswith('portal-') and count is not None:seen=['recordIdentifier','title','description','museumName','displayImage','facets','resultSize']
        query_rows.append(dict(name=log.get('name',p.name),url=log.get('url',''),requested_at=log.get('requested_at',''),http_status=log.get('http_status'),result_count=count,count_basis=basis,record_fields_seen='; '.join(seen),bytes=log.get('bytes'),sha256=log.get('sha256'),raw_body=body_ref,response_complete=log.get('complete',True) if log.get('bytes') else False,error=log.get('error','')))
    csvout(OWN/'focused-query-log.csv',query_rows)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    run()
