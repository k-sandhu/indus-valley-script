"""Exclusive output records and auditable, data-only downloads."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math
import urllib.request

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
RAW = ROOT / 'data/raw/2026-10-21-town-orientations-verification/astro'
OUT = PACKAGE / 'astro-v1'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def clean(x):
    if isinstance(x, dict): return {str(k): clean(v) for k,v in x.items()}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if hasattr(x, 'tolist'): return clean(x.tolist())
    if isinstance(x, float) and not math.isfinite(x): return None
    return x

def provenance(inputs=(), codes=()):
    return {'inputs': {str(p): sha(p) for p in inputs},
            'code': {str(p): sha(p) for p in codes}}

def write_json(path, task, results, inputs=(), codes=(), synthetic=False):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    record = dict(schema_version='1.0', task=task, synthetic=synthetic,
                  provenance=provenance(inputs, codes), **results)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(clean(record), f, indent=2, allow_nan=False); f.write('\n')
    return record

def write_text(path, text):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f: f.write(text)

def download(url, path, rights, body=None):
    p=Path(path); meta=p.with_name(p.name+'.source.json')
    if p.exists():
        m=json.loads(meta.read_text(encoding='utf-8'))
        if m['url'] != url or m['sha256'] != sha(p): raise ValueError('cache mismatch: '+str(p))
        return p
    p.parent.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(url,data=body,headers={'User-Agent':'Indus-independent-verification/1.0'})
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    with urllib.request.urlopen(req,timeout=180) as r:
        data=r.read(); status=r.status
    with p.open('xb') as f: f.write(data)
    write_json(meta,'source-acquisition',dict(url=url,retrieved_utc=started,
               bytes=len(data),sha256=sha(p),rights=rights,http_status=status,
               request_body=body.decode() if body else None),codes=[__file__])
    return p
