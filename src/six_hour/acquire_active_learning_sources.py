"""Acquire primary active-learning witnesses locally and record their hashes."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import requests
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
SOURCES=[{'id':'Tang2026','title':'Representative, Informative, and De-Amplifying: Requirements for Robust Bayesian Active Learning under Model Misspecification',
    'authors':['Roubing Tang','Sabina J. Sloman','Samuel Kaski'],'year':2026,
    'record_url':'https://proceedings.mlr.press/v300/tang26d.html',
    'url':'https://raw.githubusercontent.com/mlresearch/v300/main/assets/tang26d/tang26d.pdf',
    'rights':'Open author proceedings; asset license requires witness review; local-only'}]

def main():
    destination=ROOT/'data/six-hour/active-learning'
    destination.mkdir(parents=True,exist_ok=True)
    entries=[]
    for source in SOURCES:
        path=destination/(source['id']+'.pdf')
        if path.exists():
            raise RuntimeError('Refusing to replace a source witness.')
        response=requests.get(source['url'],timeout=60)
        response.raise_for_status()
        payload=response.content
        if not payload.startswith(b'%PDF'):
            raise ValueError('Source is not a PDF.')
        path.write_bytes(payload)
        reader=PdfReader(path)
        text='\n\n'.join(f'PDF PAGE {i+1}\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
        extracted=path.with_suffix('.txt')
        extracted.write_text(text,encoding='utf-8')
        entries.append({**source,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
            'final_url':response.url,'local_path':path.relative_to(ROOT).as_posix(),'bytes':len(payload),
            'sha256':hashlib.sha256(payload).hexdigest(),'pages':len(reader.pages),
            'extraction':{'tool':'pypdf','path':extracted.relative_to(ROOT).as_posix(),
                'sha256':hashlib.sha256(extracted.read_bytes()).hexdigest()}})
    target=ROOT/'experiments/2026-10-02-six-hour/active-identities/active-learning-sources.json'
    if target.exists():
        raise RuntimeError('Refusing source manifest replacement.')
    target.write_text(json.dumps(entries,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{'id':x['id'],'bytes':x['bytes'],'pages':x['pages']} for x in entries]))

if __name__=='__main__':
    main()
