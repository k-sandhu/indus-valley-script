"""Repair source metadata and acquire follow-up witnesses into a fresh raw directory."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re

OWN=Path(__file__).resolve().parent
ROOT=OWN.parents[1]
RAW=ROOT/'data/raw/2026-10-06-resemblance-baseline'
for key in ('TMP','TEMP','MPLCONFIGDIR'):os.environ[key]=str(RAW/'tmp')
import fitz
import requests

URLS={
    'library-marc-2025':'https://tamildigitallibrary.in/Marc-Articles/Indus%20signs%20and%20graffiti%20marks%20of%20Tamil%20Nadu',
    'pti-theweek-2025':'https://www.theweek.in/wire-updates/national/2025/01/06/mes7-tn-excavations-indus-valley.html',
    'exotic-book-record':'https://www.exoticindiaart.com/book/details/indus-signs-and-graffiti-marks-of-tamil-nadu-morphological-study-hby328/'
}

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',default='amendment-sources-20261007');args=p.parse_args()
    dest=(RAW/args.directory).resolve();assert dest.parent==RAW.resolve()
    dest.mkdir(exist_ok=False)
    def download(item):
        key,url=item
        try:
            response=requests.get(url,timeout=45)
            payload=response.content;(dest/(key+'.html')).write_bytes(payload)
            return {'id':key,'url':url,'http_status':response.status_code,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'local_path':str((dest/(key+'.html')).relative_to(ROOT)).replace('\\','/'),'success':response.status_code==200}
        except requests.RequestException as e:
            return {'id':key,'url':url,'success':False,'error':str(e)}
    with ThreadPoolExecutor(max_workers=3) as pool:acquisition=list(pool.map(download,URLS.items()))
    (dest/'acquisition.json').write_text(json.dumps(acquisition,indent=2)+'\n',encoding='utf-8')
    volume=ROOT/'data/raw/2026-10-02-connections-and-priority/south-india/inscribed-potsherds-vol1-2026.pdf'
    with fitz.open(volume) as pdf:
        for page in [12,273,282,302]:(dest/('volume-I-pdf-'+str(page)+'.txt')).write_text(pdf[page-1].get_text(),encoding='utf-8')
    data=json.loads((OWN/'history/2026-10-07-before-amendment/sources.json').read_text(encoding='utf-8'))
    replacement={'Tami?i':'Tami\u1e3bi','1680?169F':'1680\u2013169F','2D30?2D7F':'2D30\u20132D7F','E117?E139':'E117\u2013E139','Parpola?s':'Parpola\u2019s','c.2600?1900BCE':'c. 2600\u20131900 BCE',' ? Attempted':' \u2014 Attempted','pages4,6,7':'pages 4, 6, 7','October2':'October 2','seed20261006':'seed 20261006','row2':'row 2','returned403':'returned 403','and90%':'and 90%','nearly90%':'nearly 90%','Oneindia,6January2025 15:14IST':'Oneindia, 6 January 2025, 15:14 IST','Sections03 and04':'Sections 03 and 04','Section03':'Section 03','Section04':'Section 04'}
    def repair(value):
        if isinstance(value,dict):return {k:repair(v) for k,v in value.items()}
        if isinstance(value,list):return [repair(v) for v in value]
        if isinstance(value,str) and not value.startswith(('http','data/','output/','research/')):
            for old,new in replacement.items():value=value.replace(old,new)
            value=re.sub(r'PDF(?=\d)','PDF ',value)
            value=re.sub(r'\b(pages?|printed)(?=\d)',r'\1 ',value)
            value=value.replace('/printed149','/printed 149').replace('/printed321','/printed 321')
        return value
    data=repair(data);sources={r['id']:r for r in data['sources']}
    sources['rajan-2025-brochure']['access_scope']='All eight PDF pages extracted; pages 4, 6, 7 visually inspected. Library record TVA_BOK_0065888 identifies this witness as an 8-page booklet (MARC 300), separate from the 145-page edition.'
    sources['rajan-2026-volumes']['access_scope']='October 2 audit reused; follow-up opened Volume I PDF pages 12, 273, 282 and 302. Targeted reading, not exhaustive method review.'
    sources['rajan-2026-volumes']['locations']=['Volume I PDF 12 / printed xi: nearly 60% resemblance in preface','Volume I PDF 273 / printed 234, Table 3.3 total row: 551 variants, 1531 composites, 2124 total forms','Volume I PDF 282 / printed 243: comparison plates for visual similarity; prose category labels differ from Table 3.3','Volume I PDF 302 / printed 263: attributes 89% and reverse-direction 85% to B. B. Lal 1962:21']
    sources['rajan-2026-volumes']['volume_I_sha256']=hashlib.sha256(volume.read_bytes()).hexdigest()
    sources['pti-oneindia-2025']['access_scope']='PTI-labelled syndicated page opened in v1. Follow-up also recovered and opened the exact The Week item; original failed search remains in the frozen source metadata and local search log.'
    sources['exotic-book-record'].update(opened=True,access_scope='Product page opened via live web browser in follow-up; Specifications: 145 pages, 2025 edition, paperback, ISBN 9788197784255. The book itself was not read.',pages=145,isbn='9788197784255')
    data['sources'].append({'id':'library-marc-2025','title':'Indus signs and graffiti marks of Tamil Nadu : a morphological study','authors':['K. Rajan','R. Sivanantham'],'year':2025,'venue':'Tamil Digital Library MARC catalogue, Tamil Virtual Academy','url':URLS['library-marc-2025'],'opened':True,'access_scope':'Live MARC record opened; saved reviewer HTML independently read. Record TVA_BOK_0065888, fields 245, 260, 300, 995, Primary File. A search snippet also displayed a different record TVA_BOK_0065889 with 145 p.; the live opened response was the 8-page record.','locations':['MARC 300: 8 pages','MARC 995: TVA_BOK_0065888','Primary File: TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study'],'rights_status':'rights-unverified','licence':'No open licence verified; payload local-only.','reviewed_date':'2026-10-07','quotations':[]})
    data['sources'].append({'id':'pti-theweek-2025','title':'Study finds graffiti marks from TN archaeological sites similar to Indus Valley Civilisation signs','authors':['PTI'],'year':2025,'venue':'The Week, 6 January 2025, updated 13:50 IST','url':URLS['pti-theweek-2025'],'opened':True,'access_scope':'Live web browser opened full syndicated item. Direct-download status recorded separately in acquisition manifest.','locations':['Opening report: nearly 90%','Later paragraph: more than 90%','Footer: auto-generated from PTI news service; The Week not responsible for content'],'rights_status':'rights-unverified','licence':'No open licence verified; payload local-only.','reviewed_date':'2026-10-07','quotations':[]})
    for row in data['sources']:
        if row['id'] in URLS:row['acquisition_record']=str((dest/'acquisition.json').relative_to(ROOT)).replace('\\','/')
    data['amendment']={'date':'2026-10-07','status':'Exploratory','preserved_original':'history/2026-10-07-before-amendment/sources.json','searches':[{'query':'site:tamildigitallibrary.in "Indus Signs" "Marc"','result':'MARC booklet and separate 145-page record found; live response identifies booklet.'},{'query':'site:exoticindiaart.com "9788197784255"','result':'145-page edition confirmed.'}],'failed_original_search':'Exact The Week URL was not recovered during v1; follow-up recovered it. Original search failures retained.'}
    (OWN/'sources.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    observations={'status':'Exploratory','date':'2026-10-07','observations':[{'id':'library-booklet','source_id':'library-marc-2025','location':'MARC 300 and 995','pages':8,'record':'TVA_BOK_0065888'},{'id':'145-page-edition','source_id':'exotic-book-record','location':'Specifications','pages':145,'isbn':'9788197784255'},{'id':'volume-I-classification-revision','source_id':'rajan-2026-volumes','location':'Volume I PDF 273 / printed 234, Table 3.3','base_signs':42,'variants':551,'composites':1531,'total_forms':2124,'note':'Use table labels: page 282 prose labels these three totals differently.'},{'id':'volume-I-lal-1962','source_id':'rajan-2026-volumes','location':'Volume I PDF 302 / printed 263, first paragraph','forward_percent':89,'forward_population':'Iron Age megalithic signs, parallels in Harappan and central Chalcolithic cultures','reverse_percent':85,'reverse_population':'Harappan-Chalcolithic signs, parallels in Iron Age culture','cited_location':'Lal 1962:21','primary_1962_source_opened':False},{'id':'volume-I-method-scope','source_id':'rajan-2026-volumes','location':'Volume I PDF 12 and 282','note':'Nearly 60% in preface; visual comparison plates described, no numerical matching threshold on these inspected pages. No whole-volume absence claim.'}]}
    (OWN/'source-observations-v2.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(acquisition,indent=2))

if __name__=='__main__':main()
