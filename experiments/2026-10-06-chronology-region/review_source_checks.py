"""Preserve source corrections and two small reacquisition attempts in fresh paths."""
from __future__ import annotations
import argparse, copy, datetime, hashlib, json, os
from pathlib import Path
OWN=Path(__file__).resolve().parent; ROOT=OWN.parents[1]
RAW=ROOT/'data/raw/2026-10-06-chronology-region'
for key in ['TMP','TEMP','MPLCONFIGDIR']: os.environ[key]=str(RAW/'tmp')
import fitz
import pandas as pd
import requests

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True); parser.add_argument('--raw-dir',required=True)
    args=parser.parse_args(); output=Path(args.output_dir).resolve(); local=Path(args.raw_dir).resolve()
    if output.exists() or local.exists(): raise FileExistsError('Choose fresh source-check directories.')
    output.mkdir(parents=True); local.mkdir(parents=True)
    old=read(OWN/'sources.json'); follow=read(OWN/'sources-post-launch.json')
    by_id={s['id']:copy.deepcopy(s) for s in old['sources']+follow['sources']}
    checks=[]
    for name,folder,pages in [('kenoyer_meadow2010','sources-2026-10-06-v1',[1,3]),
                            ('suga2024','sources-2026-10-06-v1',[0]),
                            ('yadav2013','sources-2026-10-06-v1',[18]),
                            ('vidale2004','sources-post-launch-2026-10-07-v1',[1,10]),
                            ('parpola2018','sources-2026-10-06-v1',[3,4,5])]:
        path=RAW/folder/(name+'.pdf')
        with fitz.open(path) as pdf:
            texts={str(p+1):pdf[p].get_text() for p in pages}
        write(local/(name+'_source_check.json'),{'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'physical_pdf_pages':texts})
        checks.append({'id':name,'local_witness':path.relative_to(ROOT).as_posix(),'sha256':digest(path),'physical_pdf_pages_opened':[p+1 for p in pages]})
    by_id['suga2024']['title']='Diachronic Changes in the Indus Script Based on the Proposed Arrangement of the Indus Seal'
    by_id['suga2024']['locations'].insert(0,'Printed 25, physical PDF page 1: title has no colon')
    by_id['vidale2004']['title']='Growing in a Foreign World: For a History of the “Meluhha Villages” in Mesopotamia in the 3rd Millennium BC'
    by_id['vidale2004']['locations'][0]='Printed 270, physical PDF page 11: man sign and variants; patronymic hypothesis citing Parpola 1986:411. Twins are not discussed in this passage.'
    by_id['vidale2004']['use']='Man/variant and patronymic precedent. Twins precedent is separately supported by Vidale 2005 Figure 5, Laursen 2010 and Yadav 2013 printed 85.'
    by_id['yadav2013']['locations'].append('Printed 85, physical PDF page 19: Mahadevan sign 1 is frequent at West Asian sites; numbering is distinct from Wells')
    by_id['parpola2018']['use']='Section I.C supports Kish/Umma, Failaka/Bahrain and Central Asian site/type leads. It does not name Ur. The chapter describes Gonur/Shortughai finds as classical Indus seals; row identities remain unchecked.'
    acquisitions=[]
    urls={'fuls2022':by_id['fuls2022']['url'],
          'laursen2010':'https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf'}
    for key,url in urls.items():
        result={'id':key,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            response=requests.get(url,timeout=45)
            data=response.content
            if len(data)>16_000_000: raise ValueError('Source exceeds this package’s 16 MB download bound.')
            suffix='.pdf' if data.startswith(b'%PDF') else '.html'
            path=local/(key+suffix); path.write_bytes(data)
            result.update(http_status=response.status_code,bytes=len(data),sha256=digest(path),path=path.relative_to(ROOT).as_posix())
            if response.ok and suffix=='.pdf':
                with fitz.open(path) as pdf:
                    text='\n'.join(f'[PDF PAGE {i+1}]\n{page.get_text()}' for i,page in enumerate(pdf)); result['pages']=len(pdf)
                (local/(key+'.txt')).write_text(text,encoding='utf-8'); result['status']='downloaded-primary-pdf'
            else: result['status']='Failed'
        except Exception as error: result.update(status='Failed',error=str(error))
        acquisitions.append(result); write(local/'acquisition.json',acquisitions)
        print(json.dumps({k:result.get(k) for k in ['id','status','http_status','bytes','pages']}),flush=True)
    fuls=by_id['fuls2022']; acquired=next(r for r in acquisitions if r['id']=='fuls2022')
    fuls.update(opened=True,search_snippet_only=False,
        access='Original excerpt was not reproducible for the reviewer. A current live web tool opens a cached 35-page primary excerpt; the direct retry is recorded separately. Full book not opened.',
        locations=['Current ResearchGate author record: title, author, Mathematica Epigraphica 3 and 2022; cached excerpt bibliographic front matter only used'],
        use='Bibliographic ICIT-catalogue precedent only. Earlier section 1.3/1.4 content attribution is withdrawn because no reproducible local excerpt witness supported it.',
        direct_retry=acquired)
    laursen=by_id['laursen2010']; acquired=next(r for r in acquisitions if r['id']=='laursen2010')
    if acquired['status']=='downloaded-primary-pdf':
        laursen.update(opened=True,search_snippet_only=False,local_witness=acquired['path'],sha256=acquired['sha256'],
            access='New primary PDF acquired from Harappa.com; opened first-page abstract and source title. Substantive plate/code audit not performed.',
            locations=['Printed 96, physical PDF page 1: exact title, author, journal citation and abstract’s prefixed twins observation'],
            title='The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC')
    else: laursen.update(opened=True,search_snippet_only=False,access='Publisher/Crossref abstract opened in earlier work; new full-PDF retrieval failed as recorded')
    # Do not repeat the earlier abstract-only access record as the current one.
    by_id.pop('laursen2010_reused_abstract',None)
    corrections=[
        {'id':'Ur_attribution','historical_location':'exploratory-2026-10-07-v1/external_literature_check.csv: site=Ur','correction':'Parpola 2018 I.C does not name Ur; Harappa.com’s Frenez review image 1 caption supplies a secondary Ur lead only.'},
        {'id':'Vidale2004_twins','historical_location':'sources-post-launch.json: vidale2004.locations[0] and historical REPORT','correction':'Printed 270 treats man and variants; it supplies no twins attribution.'},
        {'id':'Suga2024_title','historical_location':'sources.json: suga2024.title','correction':by_id['suga2024']['title']},
        {'id':'Fuls2022_excerpt','historical_location':'sources.json: fuls2022.access/locations/use','correction':fuls['use']},
        {'id':'candidate_timing','historical_location':'registry-entry.json: remedy','correction':'Graphic candidates were specified before the matched-frequency computation; earlier broad per-region counts existed. Ordering is evidenced by file times only.'}]
    for source in by_id.values():
        source.setdefault('opened',source.get('access','').startswith(('opened','Opened','downloaded','Reused')))
        source.setdefault('search_snippet_only',False)
    write(output/'sources.json',{'origin':'second post-launch amendment','status':'Exploratory','date':'2026-10-07',
        'prior_source_manifests_preserved':['sources.json','sources-post-launch.json'],'quotation_policy':'No direct source passages quoted in new prose.',
        'sources':list(by_id.values()),'corrections':corrections,'stored_source_checks':checks,
        'search_log':[{'query':'"Corpus of Indus Inscriptions" "Fuls" "2022"','outcome':'Author ResearchGate record and cached excerpt opened; direct download retry recorded.'},
                      {'query':'"The westward transmission of Indus Valley sealing technology" twins','outcome':'Primary Harappa.com PDF found; Aarhus author record and publisher issue found as search results.'}],
        'acquisition_manifest':(local/'acquisition.json').relative_to(ROOT).as_posix()})
    data=pd.read_csv(OWN/'exploratory-2026-10-07-v1/external_literature_check.csv',keep_default_na=False)
    data.loc[data['site']=='Ur',['source_id','location','scope']]=['frenez2023','Harappa.com review image 1 caption, Ur examples','Secondary caption-level lead; not in Parpola 2018 I.C; individual identities/codes unchecked']
    data.loc[data['site']=="Ra's al-Junayz",['source_id','location','scope']]=['frenez2023','Harappa.com review general Oman discussion','General regional lead only; this site is not named in the inspected captions; individual identities/codes unchecked']
    data.insert(0,'status','Exploratory'); data.insert(0,'origin','second post-launch amendment')
    data.to_csv(output/'external_literature_check.csv',index=False)
    write(output/'completion.json',{'status':'Verified computation','corrections':len(corrections),'stored_sources_reopened':len(checks),'prior_manifests_unchanged':True,'code_sha256':digest(Path(__file__))})

if __name__=='__main__': main()
