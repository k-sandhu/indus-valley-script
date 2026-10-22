import requests,json,sys,time
H={'User-Agent':'indus-kb-dating/1.0'}
out={}
for q in ['Tata Institute Radiocarbon Date List','Physical Research Laboratory Radiocarbon Date List','University of Pennsylvania Radiocarbon Dates','Birbal Sahni Institute Radiocarbon Measurements','Heidelberg Radiocarbon Dates','radiocarbon dates Pakistan','radiocarbon dates India archaeological']:
  for off in (0,100):
    r=requests.get('https://api.crossref.org/works',params={'query.bibliographic':q,'filter':'issn:0033-8222','rows':100,'offset':off},headers=H,timeout=60)
    try: items=r.json()['message']['items']
    except Exception as e: print('ERR',q,r.status_code,r.text[:200]); continue
    for it in items:
      t=(it.get('title') or [''])[0]
      if any(k in t.lower() for k in ['tata','physical research','pennsylvania','birbal','heidelberg','india','pakistan','gakushuin','lucknow']):
        out[it['DOI']]=(t,it.get('volume'),it.get('page'),it.get('issued',{}).get('date-parts'))
    time.sleep(1)
for k,v in sorted(out.items(), key=lambda x:(x[1][0])):
  print(k,'|',v[0],'|',v[1],v[2],v[3])
