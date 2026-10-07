"""Enumerate portal queries and capture candidate object pages, without images."""
import concurrent.futures, json, math, re
from urllib.parse import urlencode
from focused_fetch import ROOT, RAW, fetch

def capture(name, url):
    if not (RAW/(name+'.request.json')).exists():
        fetch((name,url))
    log=json.loads((RAW/(name+'.request.json')).read_text(encoding='utf8'))
    body=(RAW/(name+'.body')).read_bytes()
    return log,body

def json_body(body):
    try: return json.loads(body.decode('utf8'))
    except UnicodeDecodeError: return json.loads(body.decode('latin1'))

def india_term(term):
    pages=[]; records=[]; total=None
    for page in range(1,100):
        url='https://museumsofindia.gov.in/repository/search/basic/fetch?'+urlencode(dict(searchterm=term,museumId='all',pageNo=page,facetFilters='{}',anaglyph=''))
        name='portal-'+re.sub(r'\W+','-',term.lower())+'-'+str(page)
        log,body=capture(name,url)
        if log.get('http_status')!=200:
            pages.append(dict(name=name,error=log.get('error'))); break
        data=json_body(body); total=data['resultSize']
        pages.append(dict(name=name,result_count=total,returned=len(data['listOfResult']),facets=data.get('facetMap')))
        records.extend(data['listOfResult'])
        if page>=math.ceil(total/28): break
    return dict(term=term,total=total,pages=pages,returned=len(records),records=records,complete=(total is not None and len(records)==total))

if __name__=='__main__':
    terms=['Indus','Harappa','Harappan','Mohenjo-daro','Mohenjodaro','Chanhu-daro','Lothal']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(india_term,terms))
    (RAW/'portal-enumeration.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    unique={r['recordIdentifier']:r for q in results for r in q['records']}
    candidates=[r for r in unique.values() if re.search(r'seal|tablet|inscri|pictogra',r.get('title','')+' '+r.get('description',''),re.I)]
    (RAW/'portal-candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(lambda r:capture('object-'+r['recordIdentifier'],'https://museumsofindia.gov.in/repository/record/'+r['recordIdentifier'])[0],candidates))
    print(json.dumps(dict(queries=[dict(term=q['term'],total=q['total'],returned=q['returned'],complete=q['complete']) for q in results],unique_records=len(unique),candidate_pages=len(candidates),http_statuses={str(k):sum(r.get('http_status')==k for r in rows) for k in set(r.get('http_status') for r in rows)}),indent=2))
