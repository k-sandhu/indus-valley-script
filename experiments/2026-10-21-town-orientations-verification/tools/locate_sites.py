"""Locate town starting points from Wikidata search and P625, preserving responses."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,time
import requests
from common import record,write_json,utc,GEOD
TOWNS=[('mohenjo-daro','Mohenjo-daro',27.324,68.136,'Q5725'),('harappa','Harappa',30.631,72.864,'Q185562'),('kalibangan','Kalibangan',29.473,74.130,'Q1722226'),('lothal','Lothal',22.522,72.249,'Q9443'),('dholavira','Dholavira',23.887,70.213,'Q9468'),('surkotada','Surkotada',23.617,70.841,'Q7646429'),('banawali','Banawali',29.598,75.393,'Q59635614'),('rakhigarhi','Rakhigarhi',29.290,76.110,'Q59633503'),('chanhu-daro','Chanhudaro',26.174,68.323,'Q1062208'),('kanmer','Kanmer',23.400,70.865,'Q15119098'),('shikarpur','Shikarpur Gujarat',23.230,70.670,'Q7496551'),('juni-kuran','Juni Kuran',None,None,None),('gola-dhoro','Gola Dhoro',None,None,'Q1534503'),('desalpur','Desalpar Gunthli',None,None,'Q15242944'),('khirsara','Khirasara',None,None,None),('kuntasi','Kuntasi',None,None,'Q6445076'),('rojdi','Rojdi',None,None,'Q7359915'),('kot-diji','Kot Diji',None,None,'Q1017084'),('nausharo','Nausharo',None,None,'Q2039702'),('sutkagen-dor','Sutkagan Dor',None,None,'Q2369920'),('balakot','Balakot archaeological site',None,None,None),('allahdino','Allahdino',None,None,'Q4730348'),('lakhanjo-daro','Lakhan Jo Daro',None,None,None),('ganweriwala','Ganweriwala',None,None,None),('farmana','Farmana',None,None,'Q5435662'),('bhirrana','Bhirrana',None,None,'Q4901824'),('kunal','Kunal Haryana',None,None,'Q6444146'),('mitathal','Mitathal',None,None,'Q6880777'),('karanpura','Karanpura archaeological site',None,None,'Q16354872'),('rangpur','Rangpur India archaeological',None,None,'Q7292902'),('kotada-bhadli','Kotada Bhadli',None,None,'Q105438960'),('pabumath','Pabumath',None,None,'Q7121835'),('navinal','Navinal',None,None,None)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw');p.add_argument('output');a=p.parse_args()
    session=requests.Session();session.headers['User-Agent']='IndusResearchInfrastructure/1.0 (local noncommercial research)'
    sites=[];files=[]
    for idx,(slug,name,lat,lon,preferred) in enumerate(TOWNS):
        dest=Path(a.raw)/'coordinates'/slug;dest.mkdir(parents=True,exist_ok=True)
        def get(params,stem,url='https://www.wikidata.org/w/api.php'):
            path=dest/(stem+'.json')
            if path.exists():
                from common import read_json
                files.append(record(path,requests.Request('GET',url,params=params).prepare().url,'explicit-license','Wikidata structured data CC0 1.0' if 'wikidata' in url else 'OpenStreetMap data ODbL 1.0; coordinates only',retrieval_note='Cached first successful response; file mtime records retrieval',retrieved_utc=__import__('datetime').datetime.fromtimestamp(path.stat().st_mtime,__import__('datetime').timezone.utc).isoformat()))
                return read_json(path)
            time.sleep(2.1)
            for attempt in range(6):
                r=session.get(url,params=params,timeout=40)
                if r.status_code!=429:break
                time.sleep(min(60,15*(attempt+1)))
            r.raise_for_status();path.write_bytes(r.content)
            files.append(record(path,r.url,'explicit-license','Wikidata structured data CC0 1.0' if 'wikidata' in url else 'OpenStreetMap data ODbL 1.0; coordinates only'))
            return r.json()
        row=dict(slug=slug,required=idx<11,search_name=name,guess=[lat,lon] if lat is not None else None,wikidata=None,coordinate_used=None,coordinate_source=None,distance_from_guess_m=None,flags=[],second_source=None)
        try:
            data=get(dict(action='wbsearchentities',search=name,language='en',format='json',limit=10),'search')
            results=data.get('search',[])
            if not results and slug=='juni-kuran':
                data=get(dict(action='wbsearchentities',search='Junikuran',language='en',format='json',limit=10),'search-alternate');results=data.get('search',[])
            row['search_results']=[dict(qid=r['id'],label=r.get('label'),description=r.get('description')) for r in results]
            ids=[r['id'] for r in results]
            if preferred and preferred not in ids:ids.insert(0,preferred)
            if ids:
                entities=get(dict(action='wbgetentities',ids='|'.join(ids),props='labels|descriptions|claims',languages='en',format='json'),'entities')['entities']
                q=preferred if preferred else next((q for q,e in entities.items() if any(t in e.get('descriptions',{}).get('en',{}).get('value','').lower() for t in ['archaeolog','indus','harappan'])),ids[0])
                e=entities[q];claims=e.get('claims',{}).get('P625',[])
                claims=[c for c in claims if c.get('rank')!='deprecated' and 'datavalue' in c['mainsnak']]
                claims.sort(key=lambda c:c.get('rank')!='preferred')
                coords=[c['mainsnak']['datavalue']['value'] for c in claims]
                row['wikidata']=dict(qid=q,label=e.get('labels',{}).get('en',{}).get('value',name),description=e.get('descriptions',{}).get('en',{}).get('value'),P625=coords,url='https://www.wikidata.org/wiki/'+q,found_by_search=q in [r['id'] for r in results])
                if coords:row.update(coordinate_used=[coords[0]['latitude'],coords[0]['longitude']],coordinate_source='https://www.wikidata.org/wiki/'+q+'#P625')
            if row['coordinate_used'] and lat is not None:
                c=row['coordinate_used'];row['distance_from_guess_m']=GEOD.inv(lon,lat,c[1],c[0])[2]
                if row['distance_from_guess_m']>2000:row['flags'].append('Wikidata more than 2 km from guess')
            if not row['coordinate_used']:row['flags'].append('Wikidata has no usable coordinate')
            if row['flags']:
                time.sleep(1.1)
                second=get(dict(q=name+', '+('Pakistan' if slug in ['balakot','allahdino','lakhanjo-daro','ganweriwala'] else 'India'),format='jsonv2',limit=5,addressdetails=0),'osm-search','https://nominatim.openstreetmap.org/search')
                row['second_source']=dict(url=files[-1]['url'],results=[{k:r.get(k) for k in ['osm_type','osm_id','lat','lon','display_name']} for r in second])
                if not row['coordinate_used'] and second:
                    row.update(coordinate_used=[float(second[0]['lat']),float(second[0]['lon'])],coordinate_source=files[-1]['url'])
            print(slug,row['wikidata']['qid'] if row['wikidata'] else None,row['coordinate_used'],row['flags'],flush=True)
        except Exception as e:row['flags'].append('Acquisition error: '+str(e));print(slug,str(e),flush=True)
        sites.append(row)
    write_json(a.output,dict(schema_version=1,created_utc=utc(),task='starting points only; mounds to be located independently',sites=sites,files=files))
if __name__=='__main__':main()
