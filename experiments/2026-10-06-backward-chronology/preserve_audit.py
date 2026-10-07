"""Package-local retrieval ledger and complete file inventory."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-06-backward-chronology'

def dump(path,data):
    if path.exists(): raise FileExistsError(f'Preserved record exists: {path}')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def retrieval():
    attempts=[]
    for path in sorted(RAW.glob('*.acquisition.json')):
        item=json.loads(path.read_text(encoding='utf-8'))
        if not item.get('url'): continue
        state='payload recovered'
        if item.get('error'): state='request failed'
        elif item.get('http_status',200)>=400: state='HTTP failure'
        elif item['id']=='bet-dwarka1998': state='HTTP 200 bot challenge; source not recovered'
        attempts.append(dict(id=item['id'],url=item['url'],outcome=state,
                             witness=path.relative_to(ROOT).as_posix(),
                             http_status=item.get('http_status'),error=item.get('error')))
    # Earlier OCR processing replaced two acquisition metadata records. These
    # reconstructions use URL/status values printed at acquisition, not new downloads.
    corrections=[dict(id='kenoyer2006',url='https://www.harappa.com/sites/default/files/pdf/Kenoyer2006_The%20Origin%2C%20Context%20and%20Function%20of%20the%20Indus%20Sc.pdf',
                      observed_acquisition_utc='2026-10-07T03:58:43.053455+00:00',http_status=200),
                 dict(id='lal1960',url='https://ignca.gov.in/Asi_data/18414.pdf',
                      observed_acquisition_utc='2026-10-07T03:58:44.084710+00:00',http_status=200)]
    for c in corrections:
        c['sha256']=hashlib.sha256((RAW/(c['id']+'.pdf')).read_bytes()).hexdigest()
        attempts.append(dict(id=c['id'],url=c['url'],outcome='payload recovered; original metadata reconstructed from tool output',
                             witness='data/raw/2026-10-06-backward-chronology/metadata-corrections.json',http_status=200,error=None))
    dump(RAW/'metadata-corrections.json',{'reason':'OCR processing replaced initial acquisition metadata; PDF witnesses preserved. Acquisition script now writes a separate processing record.', 'records':corrections})
    web_failures=[dict(target='Aramaic documents from Bactria',url='https://aramaicdocuments.com/',outcome='web fetch timeout',response='web-17.json'),
                  dict(target='Khalili collection primary record',url='https://khalilicollections.org/all-collections/',outcome='web fetch HTTP 429',response='web-17.json'),
                  dict(target='Pirak original article',url='https://www.persee.fr/doc/arasi_0004-3958_1976_num_32_1_1098',outcome='candidate was a different article; corrected to 1095',response='web-10.json')]
    failures=[a for a in attempts if a['outcome'] not in ['payload recovered','payload recovered; original metadata reconstructed from tool output']]
    dump(RAW/'acquisition-failures.json',{'failed_downloads':failures,'web_failures_or_wrong_targets':web_failures})
    search_groups=[
        {'topic':'Harappa Ravi/Kot Diji marks, dates and counts','outcome':'2006 and 2010 author papers recovered'},
        {'topic':'Late Harappa, Cemetery H, Jhukar and Pirak seals','outcome':'Kenoyer review recovered; Pirak publisher record opened, full excavation article not recovered'},
        {'topic':'Rangpur, Rojdi, Lothal, late Gujarat and Bet Dwarka','outcome':'Original Rangpur recovered after wrong PDF guess; Bet Dwarka recovered after NIO bot challenge; later Rojdi monograph not recovered'},
        {'topic':'Daimabad, Inamgaon, Navdatoli, Prakash, Ahar–Banas','outcome':'Daimabad/Prakash excavation reports and Inamgaon illustration recovered; several calibrated mark/context joins remain absent'},
        {'topic':'OCP, Copper Hoards, PGW and NBPW graffiti','outcome':'No opened primary dated OCP/Copper Hoard mark inventory; PGW search did not yield an authenticated joined assemblage; IAR download timed out; Lal provides NBPW examples'},
        {'topic':'Anuradhapura and Sri Lankan megalithic contexts','outcome':'1996 abstract and Deraniyagala overview opened; full 1996 paper unavailable; Ibbankatuwa mark-to-date join not recovered'},
        {'topic':'Porunthal, Kodumanal, Keeladi, Kilnamandi, Perumbalai and Sivagalai dates','outcome':'2026 local primary volumes examined; original Porunthal calibrated output and sample-specific Tamil-Brahmi joins not recovered; two government downloads timed out'},
        {'topic':'Lal 1960, Mahadevan graffiti, Rajan/Sivanantham 2025/2026','outcome':'Lal and Mahadevan2001 original papers recovered; 2025 local witness is an eight-page brochure; 2026 two volumes reused'},
        {'topic':'Brahmi/Kharosthi origins and adjacent Aramaic evidence','outcome':'Salomon full review recovered; original theory works not opened; Bactrian primary collection fetches failed'},
        {'topic':'Changizi, Zhang, Ye and Shimojo 2006 shape configurations','outcome':'Full publisher HTML opened through web after PDF guesses failed; direct HTTP403 retained'}]
    log={'scope':'Live searches conducted 6–7 October 2026; source assembly for Package E',
         'record_completeness':'Earlier searches are grouped by topic, with response witnesses web-02 through web-16. Exact earlier query strings were not saved; the first response witness was not retained. The exact final requests below were retained. Failed target retrievals are enumerated separately.',
         'search_groups':search_groups,'exact_requests':[
           {'response':'web-17.json','operation':'open','urls':['https://aramaicdocuments.com/','https://khalilicollections.org/all-collections/','https://www.journals.uchicago.edu/doi/full/10.1086/502806']},
           {'response':'web-18.json','operation':'search','queries':['site.harappa.com Kenoyer "Indus Seals" 2009 2006 2007','site.harappa.com "Origin, Context" 2006 9 27','K Rajan V P Yatheeskumar Porunthal 2013 2440 Beta 302854 radiometric Antiquity']}],
         'response_witnesses':[p.relative_to(ROOT).as_posix() for p in sorted(RAW.glob('web-*.json'))],
         'failed_search_targets':['Opened primary dated OCP/Copper Hoard mark inventory','Calibrated Porunthal laboratory output','Specimen-joined early Tamil-Brahmi calibration table','Full 2025 morphological monograph','Dated diagnostic intermediate chain connecting late Indus to early historic writing']}
    dump(RAW/'search-log.json',log)
    dump(OWN/'retrieval-audit.json',{'status':'Verified computation','URL_attempts_with_local_records':len(attempts),
            'failed_or_blocked_direct_downloads':len(failures),'web_failures_or_wrong_targets':len(web_failures),
            'response_witnesses':len(log['response_witnesses']),
            'search_log':'data/raw/2026-10-06-backward-chronology/search-log.json',
            'failure_log':'data/raw/2026-10-06-backward-chronology/acquisition-failures.json',
            'metadata_corrections':'data/raw/2026-10-06-backward-chronology/metadata-corrections.json',
            'attempts':attempts,'log_limitation':log['record_completeness']})

def inventory(name='file-manifest.json'):
    if not re.fullmatch(r'file-manifest(?:-[a-z0-9]+)*\.json',name):
        raise ValueError('Use a safe file-manifest name beneath the owned directory.')
    destination=OWN/name
    items=[]
    for directory in [OWN,RAW]:
        for path in sorted(directory.rglob('*')):
            if not path.is_file() or path==destination: continue
            path.relative_to(directory)
            items.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,
                              sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              handling='local-only' if directory==RAW else 'package artifact'))
    dump(destination,{'scope':'All files created in the two owned roots; this manifest itself is excluded from self-hashing. Earlier inventories are preserved snapshots.',
                                 'files':items,'file_count':len(items),
                                 'owned_file_count':sum(i['handling']=='package artifact' for i in items),
                                 'local_raw_file_count':sum(i['handling']=='local-only' for i in items)})

def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['retrieval','inventory']); p.add_argument('--name',default='file-manifest.json'); args=p.parse_args()
    if args.action=='retrieval': retrieval()
    else: inventory(args.name)

if __name__=='__main__':main()
