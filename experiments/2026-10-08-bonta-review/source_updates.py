"""Add late source checks, including HTTP-200 interstitial detection."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'

def main():
    p=OWN/'sources.json'; x=json.loads(p.read_text(encoding='utf-8'))
    for s in x['sources']:
        if s['id']=='Muk19':
            s['access']='Opened publisher article through the earlier web reader; later web opens failed through Nature identity redirect. Direct HTML and PDF requests returned HTTP 200 interstitial HTML, not an article/PDF witness.'
            s['download_verified_as_article']=False
        if s['id']=='Rao18':s['location']='Excerpt PDF pp. 7, 12–14; printed pp. 518, 523–525'
        if s['id']=='IMSC15':s['location']='PDF pp. 88, 91–92; printed pp. 80, 83–84. Page 88 gives May 4–5, 2015; pages 91–92 identify the meeting and Bonta.'
    ids={s['id'] for s in x['sources']}
    additions=[
      {'id':'Fair92','title':'The Harappan Civilization and Its Writing: A Model for the Decipherment of the Indus Script',
       'authors':'Walter A. Fairservis','year':1992,'venue':'Oxford & IBH Publishing Co., New Delhi/Bombay/Calcutta, scanned edition; Brill edition also catalogued',
       'url':'https://mc.dlib.nyu.edu/files/books/brill_awdl000035/brill_awdl000035_lo.pdf',
       'access':'Opened downloaded 256-page PDF and selected text on typology, numerals and storage tokens',
       'opened':True,'location':'PDF pp. 30, 57–58, 70, 75–77, 84; printed pp. 18, 45–46, 58, 63–65, 72',
       'licence':'No reuse licence established; local only','short_quotation':None},
      {'id':'Maha-review','title':'The Indus Script','authors':'Iravatham Mahadevan',
       'year':None,'venue':'Harappa.com author essay reviewing Asko Parpola’s Deciphering the Indus Script (1994); original publication date unverified',
       'url':'https://www.harappa.com/script/maha15.html',
       'access':'Opened full author essay through web reader and downloaded HTML','opened':True,
       'location':'Structural Analysis by Parpola; Parpola’s Methodology of Decipherment; Assessment of Parpola’s Model of Decipherment',
       'licence':'No reuse licence established; local only','short_quotation':None}
    ]
    for s in additions:
        if s['id'] not in ids:
            s['access_date_local']='2026-10-08';x['sources'].append(s)
    more=json.loads((RAW/'acquisition-2026-10-08-v3/manifest.json').read_text(encoding='utf-8'))
    urls={d['url'] for d in x['downloads']}
    for d in more:
        if d['url'] not in urls:x['downloads'].append(d)
    for d in x['downloads']:
        if d['url'].startswith('https://www.nature.com/'):
            d['payload_validation']='HTML identity/interstitial document; HTTP 200 does not establish article access'
            d['usable_article_witness']=False
    note={'query':'Direct Nature PDF; Fairservis NYU scan; Mahadevan author essay',
          'outcome':'Nature HTTP 200 was interstitial HTML; Fairservis and Mahadevan payloads opened. Generic PDF library accepted HTML as a one-page document, so magic bytes were checked.'}
    if note not in x['failed_searches']:x['failed_searches'].append(note)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('sources',len(x['sources']))

if __name__=='__main__':main()
