import json, pathlib, requests
from pypdf import PdfReader
ROOT=next(v for v in pathlib.Path(__file__).resolve().parents if (v/'knowledge/INDEX.md').exists())
p=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/afghan-minor-revision'
import os
(p/'tmp').mkdir(exist_ok=True)
for key in ('TMP','TEMP','MPLCONFIGDIR'): os.environ[key]=str(p/'tmp')
urls={
'mughal1989':'https://pahar.in/pahar/Books%20and%20Articles/Indian%20Subcontinent/1989%20Archaeological%20Tour%20along%20the%20Ghaggar-Hakra%20River%20by%20Stein%20s.pdf',
'sandal-bar':'https://ignca.gov.in/Asi_data/85282.pdf',
'nuhato2019':'https://drive.google.com/uc?export=download&id=1jUadiydHWZRnDqUQVmpGOrLWsIbWcFzM',
'gazetteer4':'https://chikyu.repo.nii.ac.jp/record/378/files/IndusKoukogakunotenbouNo4804.pdf',
'naru-heritage2024':'https://iris.unive.it/retrieve/999adae2-39cb-44d2-8319-54561bc05328/heritage%20PB%202024.pdf',
'baloch2004':'https://library-sindhi-sp-2020.s3.us-east-2.amazonaws.com/files/Sindh_Studies_Cultural-N_A_Baloch-2004-cs.pdf'}
log=[]
for k,u in urls.items():
    try:
        r=requests.get(u,timeout=40);r.raise_for_status()
        (p/(k+'.pdf')).write_bytes(r.content)
        reader=PdfReader(p/(k+'.pdf'))
        pages=[{'pdf_page':i+1,'text':v.extract_text() or ''} for i,v in enumerate(reader.pages)]
        (p/(k+'.pages.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
        (p/(k+'.txt')).write_text('\n'.join('PDF PAGE '+str(a['pdf_page'])+'\n'+a['text'] for a in pages),encoding='utf-8')
        log.append({'id':k,'url':u,'status':r.status_code,'pages':len(pages)})
    except Exception as e:log.append({'id':k,'url':u,'error':str(e)})
(p/'acquisition.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
print(json.dumps(log))
