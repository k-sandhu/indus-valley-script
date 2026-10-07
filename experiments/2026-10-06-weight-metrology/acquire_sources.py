"""Bounded public-source downloads with format checks and local-only witnesses."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import urllib.request
from parse_catalogue import ROOT, RAW, write_json
import fitz

URLS = {
 'ialongo-vacca-peyronel-2018.pdf':'https://apeiron.iulm.it/bitstream/10808/24864/1/ialongo_vacca_peyronel_2018_jas_91.pdf',
 'ialongo-lago-2021.pdf':'https://iris.uniroma1.it/retrieve/2adf4953-5745-4187-9af8-006cbd2bde6c/Ialongo_Small-change_2021.pdf',
 'hemmy-1931.pdf':'https://rws.xoba.com/indus_weights/Marshall-1931-Weights-Mohenjodaro.pdf',
 'bibby-1970.pdf':'https://tidsskrift.dk/kuml/article/download/105436/154240',
 'laursen-2016.pdf':'https://www.harappa.com/sites/default/files/pdf/Laursen-2016-Arabian_Archaeology_and_Epigraphy.pdf',
 'cqarchaeo-2024-issue.pdf':'https://www.archcalc.cnr.it/indice/issues/AC_35.1.pdf',
}

def acquire(item):
    name,url=item
    record={'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'path':str((RAW/'literature'/name).relative_to(ROOT)),
            'rights_status':'rights-unverified','attempt':'ordinary public HTTPS; no login or account'}
    target=RAW/'literature'/name
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(request,timeout=35) as response:
            payload=response.read(); record.update({'http_status':response.status,'final_url':response.geturl(),'content_type':response.headers.get('Content-Type')})
        target.write_bytes(payload)
        record.update({'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'pdf_magic':payload.startswith(b'%PDF-')})
        if not record['pdf_magic']:
            record['status']='Failed: response is not PDF'; return record
        doc=fitz.open(target); record.update({'status':'downloaded PDF','pages':len(doc)})
        (target.with_suffix('.txt')).write_text('\n\f\n'.join(p.get_text() for p in doc),encoding='utf-8')
        record['text_sha256']=hashlib.sha256(target.with_suffix('.txt').read_bytes()).hexdigest()
    except Exception as exc:
        record.update({'status':'Failed','error':str(exc)})
    return record

def main():
    manifest=RAW/'literature/acquisition.json'
    if manifest.exists(): raise FileExistsError(manifest)
    manifest.parent.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(acquire,URLS.items()))
    write_json(manifest,records)
    print(json.dumps([{k:r[k] for k in ['url','status']} for r in records],ensure_ascii=False))

if __name__=='__main__': main()
