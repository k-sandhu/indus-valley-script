"""Acquire logged local inputs: python -I code/acquire.py {kolipakam,dravlex,dedr,s4}."""
from pathlib import Path, PurePosixPath
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import argparse
import datetime as dt
import hashlib
import json
import re
import time
import urllib.request
import urllib.error
import zipfile
from common import RAW, LOCAL, DOWNLOADS, RUN, PACKAGE, sha, write, read

UA = 'Mozilla/5.0 (compatible; indus-valley-script research knowledge base; dravidian root meanings study)'
LOG = LOCAL / 'requests.jsonl'
LAST = 0.0
BASE = 'https://dsal.uchicago.edu'
PAGES = [87,112,217,372,435,436,447,456,471,472,499,500,504]
FILES = [
 ('005.trees',10735720,'05a73b962cb62e1dea5b505b88a26d8a',5982046),
 ('003.zip',10735723,'bd7f83e55b463998d3559c431cc27db2',5965690),
 ('002.xml',10735729,'2871f3d891eec93be76dc9e22f009003',5982055),
 ('001.pdf',10735726,'92421f25b02621f20e1fe6b60dde5c3f',5982052),
 ('004.zip',10735717,'c6514dc09babc540a0445759f6d8f5cb',5965687)]

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def records():
    return [json.loads(x) for x in LOG.read_text(encoding='utf-8').splitlines()] if LOG.exists() else []

def fetch(url, path):
    global LAST
    path = Path(path)
    if path.exists():
        h = sha(path)
        if any(r.get('sha256') == h and r.get('local_path') == str(path.relative_to(RAW))
               and r['url'] == url for r in records()):
            return path
        raise ValueError('Existing file has no matching logged hash: '+str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    for rec in reversed(records()):
        if rec['url']==url and rec.get('sha256'):
            previous=RAW/rec['local_path']
            if previous.is_file() and sha(previous)==rec['sha256']:
                path.write_bytes(previous.read_bytes())
                reuse=dict(rec,local_path=str(path.relative_to(RAW)),reused_from=rec['local_path'],cached=True)
                with LOG.open('a',encoding='utf-8') as stream: stream.write(json.dumps(reuse)+'\n')
                return path
    for attempt in range(4):
        time.sleep(max(0, .65-(time.monotonic()-LAST)))
        rec = dict(url=url, utc_start=stamp(), local_path=str(path.relative_to(RAW)),
                   http_status=None, final_url=None, content_type=None, bytes=0, sha256=None)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':UA}), timeout=90) as response:
                data = response.read()
                rec.update(http_status=response.status, final_url=response.url,
                           content_type=response.headers.get('Content-Type'), bytes=len(data),
                           sha256=hashlib.sha256(data).hexdigest())
            path.write_bytes(data)
        except Exception as exc:
            rec.update(error=type(exc).__name__+': '+str(exc), http_status=getattr(exc,'code',None))
        LAST = time.monotonic()
        rec['utc_end'] = stamp()
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(rec)+'\n')
        if 'error' not in rec:
            return path
        if attempt == 3:
            raise RuntimeError(rec['error'])
        time.sleep(2**attempt)

def extract(archive, target):
    target = Path(target)
    if target.exists():
        raise ValueError('Extraction destination exists: '+str(target))
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            name = member.filename.replace('\\','/')
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or re.match(r'^[A-Za-z]:',name) or ((member.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError('Unsafe archive member')
        target.mkdir(parents=True)
        z.extractall(target)

def kolipakam():
    target = DOWNLOADS/'kolipakam2018'
    catalogue=read(fetch('https://api.figshare.com/v2/articles?resource_doi=10.1098%2Frsos.171504&page_size=100',target/'article-catalogue.json'))
    write(LOCAL/'figshare-catalogue-review.json',catalogue)
    rows = []
    for suffix, fid, md5, article in FILES:
        name = 'rsos171504_si_'+suffix
        path = fetch('https://ndownloader.figshare.com/files/'+str(fid), target/name)
        actual = hashlib.md5(path.read_bytes()).hexdigest()
        if actual != md5:
            raise ValueError('MD5 mismatch: '+name)
        metadata=read(fetch('https://api.figshare.com/v2/articles/'+str(article),target/(str(article)+'-metadata.json')))
        if fid not in [f['id'] for f in metadata['files']]: raise ValueError('Figshare article/file mismatch')
        licence=metadata['license']
        if 'CC BY 4.0' not in licence['name']: raise ValueError('Unexpected figshare licence')
        rows.append(dict(file=name, url='https://ndownloader.figshare.com/files/'+str(fid),
                         md5=actual, sha256=sha(path), bytes=path.stat().st_size,
                         figshare_article_id=article, doi=metadata['doi'],
                         article_doi='10.1098/rsos.171504', licence='CC BY 4.0',
                         licence_url=licence['url'],metadata_sha256=sha(target/(str(article)+'-metadata.json'))))
    write(RUN/'sources-kolipakam.json',rows)
    posterior = DOWNLOADS/'kolipakam2018-posterior'
    if not posterior.exists():
        extract(target/'rsos171504_si_003.zip',posterior)

def dravlex():
    target = DOWNLOADS/'dravlex'
    # A pinned CLDF archive avoids executing any downloaded curation code.
    meta = read(fetch('https://api.github.com/repos/lexibank/dravlex/commits/master',target/'commit.json'))
    commit = meta['sha']
    lic = read(fetch('https://api.github.com/repos/lexibank/dravlex/license?ref='+commit,target/'license.json'))
    spdx = lic.get('license',{}).get('spdx_id')
    usable = spdx in {'CC-BY-4.0','CC0-1.0','CC-BY-SA-4.0','MIT','Apache-2.0'}
    result = dict(commit=commit, original_doi='10.5281/zenodo.1181715', licence=spdx,
                  usable=usable, files=[])
    if usable:
        archive = fetch('https://api.github.com/repos/lexibank/dravlex/zipball/'+commit,target/'dravlex.zip')
        if not (target/'extracted').exists():
            extract(archive,target/'extracted')
    else:
        result['skip_reason']='No recognised open licence in the pinned repository metadata'
    result['files']=[dict(path=str(p.relative_to(target)),sha256=sha(p),bytes=p.stat().st_size)
                     for p in sorted(target.rglob('*')) if p.is_file()]
    write(RUN/'sources-dravlex.json',result)

def dedr_manifest():
    rows = [r for r in records() if 'dsal.uchicago.edu' in r['url']]
    protocol = (PACKAGE/'PROTOCOL.md').read_text(encoding='utf-8')
    notice = re.search(r'"(Copyright 1984 by Oxford University Press\..*?Press\.)"',protocol).group(1)
    files = [dict(path=str(p.relative_to(LOCAL)),sha256=sha(p),bytes=p.stat().st_size)
             for p in sorted((LOCAL/'dedr').rglob('*')) if p.is_file()]
    page_numbers=sorted({int(x) for r in rows for x in re.findall(r'[?&]page=(\d+)',r['url'])})
    write(RUN/'sources-dedr.json',dict(requests=sum(not r.get('cached',False) for r in rows), successful_requests=sum(r.get('http_status')==200 and not r.get('cached',False) for r in rows),
                                     pages=page_numbers, files=files, rights_notice=notice))

def page(n, folder):
    return fetch(BASE+'/cgi-bin/app/burrow_query.py?page='+str(n),folder/f'page-{n:05d}.html')

def dedr():
    # Following pages are fetched for boundary inspection; the parser joins only continuations.
    for n in sorted(set(PAGES+[p+1 for p in PAGES])):
        page(n, LOCAL/'dedr/pages')
    for name in ['burrow.pdf','new_frontmatter.html']:
        url = BASE+'/dictionaries/burrow/'+('frontmatter/' if name.endswith('.pdf') else '')+name
        fetch(url, LOCAL/'dedr/frontmatter'/name)
    dedr_manifest()

def s4():
    folder = LOCAL/'dedr/s4'
    numbers = set()
    for word in ['star','planet','constellation','asterism','comet','meteor']:
        p = fetch(BASE+'/cgi-bin/app/burrow_query.py?qs='+word+'&matchtype=default',folder/('search-'+word+'.html'))
        numbers.update(int(n) for n in re.findall(r'burrow_query\.py\?page=(\d+)',p.read_text(encoding='utf-8')))
    for n in sorted(numbers | {n+1 for n in numbers}):
        page(n, folder/'pages')
    dedr_manifest()

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['kolipakam','dravlex','dedr','s4'])
    try:
        globals()[ap.parse_args().command]()
    except Exception:
        if (LOCAL/'dedr').exists():
            dedr_manifest()
        raise
