"""Extract focused record witnesses. Third-party values remain in ignored raw storage."""
import json,re
from bs4 import BeautifulSoup
from focused_fetch import RAW

def dump(name, rows):
    (RAW/name).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def run():
    portal=json.loads((RAW/'portal-unique-review.json').read_text(encoding='utf8'))
    records=[]
    for r in portal:
        if r['status']!='confirmed_description':continue
        f=r['fields']
        records.append(dict(institution=f['Museum Name'],record_id=r['record_identifier'],accession=f['Accession Number'],url=r['url'],raw=r['body'],site=f.get('Origin Place') or f.get('Provenance',''),object_type=r['object_type_review'],material=f.get('Main Material',''),dimensions=f.get('Dimensions',''),date=f.get('Period / Year of Work') or f.get('Culture',''),description=f.get('Brief Description',''),image_slots=len(r['image_slots']),bibliography='',excavation_raw='',metadata=f,duplicate_pages=r['duplicate_record_identifiers']))
    for p in sorted(RAW.glob('penn-*.body')):
        if p.stem not in ['penn-83829','penn-83830','penn-149372','penn-238862','penn-329820']:continue
        s=BeautifulSoup(p.read_bytes(),'html.parser'); f={}
        for tr in s.select('tr'):
            cells=tr.find_all('td')
            if len(cells)>1 and 'left' in cells[0].get('class',[]):f[cells[0].get_text(' ',strip=True)]=cells[1].get_text(' ',strip=True)
        bib=' '.join(td.get_text(' ',strip=True) for td in s.select('td.center.ps-0'))
        fields=re.findall(r'(\d+) - Field No',f.get('Other Number',''))
        plates=re.findall(r'Pl\.,? (LII|LI), No\. (\d+)',bib)
        refs=[dict(field=a,plate=b,figure=c) for a,(b,c) in zip(fields,plates)]
        image_total=re.search(r'View All \((\d+)\) Object Images',s.get_text(' ',strip=True))
        image_count=int(image_total.group(1)) if image_total else len(s.select('img.obj-image'))
        objno=f['Object Number'];log=json.loads((RAW/(p.stem+'.request.json')).read_text())
        records.append(dict(institution='Penn Museum',record_id=p.stem.split('-')[1],accession=objno,url=log['url'],raw=log['body'],site=f.get('Site Name',''),object_type='seal',material=f.get('Materials',''),dimensions='',date=f.get('Date Made',''),description=f.get('Description',''),image_slots=image_count,bibliography=bib,excavation_raw='; '.join(fields),published_references=refs,metadata=f,duplicate_pages=[]))
    for id in ['324062','324063','324064','324065','38287']:
        p=RAW/('met-'+id+'.body');s=BeautifulSoup(p.read_bytes(),'html.parser');t=s.get_text(' ',strip=True);f={}
        labels=['Title','Period','Date','Geography','Culture','Medium','Dimensions','Classification','Credit Line','Object Number','Curatorial Department']
        for i,label in enumerate(labels):
            end='(?:'+'|'.join(re.escape(x)+':' for x in labels)+r'|More Artwork|$)'
            m=re.search(re.escape(label)+r': (.*?)(?='+end+')',t)
            if m:f[label]=m.group(1).strip()
        log=json.loads((RAW/('met-'+id+'.request.json')).read_text())
        records.append(dict(institution='Metropolitan Museum of Art',record_id=id,accession=f.get('Object Number',''),url=log['url'],raw=log['body'],site=f.get('Geography',''),object_type='seal',material=f.get('Medium',''),dimensions=f.get('Dimensions',''),date=f.get('Date',''),description=f.get('Title',''),image_slots=1,bibliography='',excavation_raw='',metadata=f,duplicate_pages=[],inscription_confirmation='Title or inspected image; image witnesses recorded in focused decisions'))
    for name in ['louvre-md-json','louvre-sb5614','louvre-ao6064','louvre-sb2425']:
        p=RAW/(name+'.body');j=json.loads(p.read_bytes());log=json.loads((RAW/(name+'.request.json')).read_text())
        records.append(dict(institution='Louvre',record_id=j['arkId'],accession='; '.join(x['value'] for x in j['objectNumber']),url=j['url'],raw=log['body'],site=j.get('placeOfDiscovery',''),object_type='seal',material=j.get('materialsAndTechniques',''),dimensions='; '.join(x['type']+': '+x['displayDimension'] for x in j['dimension']),date=j['displayDateCreated'],description=j['description'],image_slots=len(j['image']),bibliography=j['bibliography'],excavation_raw='',metadata=j,duplicate_pages=[]))
    records.extend(json.loads((RAW/'bm-record-observations.json').read_text(encoding='utf8')))
    dump('focused-records.json',records)
    print('Original inscription-confirmed records',len(records))

if __name__=='__main__':run()
