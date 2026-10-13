"""Use pinned repositories and declared access repairs without replacing v1."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import requests
import fitz
from bs4 import BeautifulSoup
from acquire_sources import ROOT,HERE,RAW,capture,sha


def public_tls_exception(item):
    ident,url=item
    row=dict(witness_id=ident,requested_url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tls_verification=False,
             transport_caveat='One public, unauthenticated request only after v1 expired-certificate failure. No credentials or global TLS change; hashes establish retained bytes, not authenticated transport.',
             rights='rights-unverified',redistribution='local-only')
    try:
        res=requests.get(url,timeout=30,verify=False,headers={'User-Agent':'Source inspection research/1.0'})
        data=res.content;dest=RAW/f'{ident}-v2.html'
        if dest.exists():raise FileExistsError(dest)
        dest.write_bytes(data)
        row.update(status_code=res.status_code,resolved_url=res.url,path=dest.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha(data),content_type=res.headers.get('Content-Type'),format='html')
        soup=BeautifulSoup(data,'html.parser')
        for node in soup(['script','style','nav']):node.decompose()
        content=('\n'.join(x.strip() for x in soup.get_text('\n').splitlines() if x.strip())+'\n').encode('utf8')
        out=RAW/f'{ident}-v2-text.txt'
        if out.exists():raise FileExistsError(out)
        out.write_bytes(content)
        row['derivative']=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(content),bytes=len(content),parent_sha256=row['sha256'])
    except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
    return row


def main():
    target=RAW/'capture-v2.json'
    if target.exists():raise FileExistsError(target)
    greek=json.loads((RAW/'greek-repo-commit-v1.json').read_text('utf8'))['sha']
    pali=json.loads((RAW/'bilara-repo-commit-v1.json').read_text('utf8'))['sha']
    normal=[
        ('witzel-substrates1999-author-barehost','https://michaelwitzel.org/wp-content/uploads/2014/06/ejvs0501article.pdf'),
        ('greek-folder',f'https://api.github.com/repos/PerseusDL/canonical-greekLit/contents/data/tlg0012/tlg002?ref={greek}'),
        ('odyssey-greek',f'https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/{greek}/data/tlg0012/tlg002/tlg0012.tlg002.perseus-grc2.xml'),
        ('odyssey-english',f'https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/{greek}/data/tlg0012/tlg002/tlg0012.tlg002.perseus-eng2.xml'),
        ('dn1-pali',f'https://raw.githubusercontent.com/suttacentral/bilara-data/{pali}/root/pli/ms/sutta/dn/dn1_root-pli-ms.json'),
        ('dn1-sujato',f'https://raw.githubusercontent.com/suttacentral/bilara-data/{pali}/translation/en/sujato/sutta/dn/dn1_translation-en-sujato.json'),
        ('bilara-license',f'https://raw.githubusercontent.com/suttacentral/bilara-data/{pali}/LICENSE')]
    insecure=[('yasna9-avestan','https://www.avesta.org/yasna/y9.htm'),('yasna-mills','https://www.avesta.org/yasna/yasna.htm'),('vendidad3-avestan','https://www.avesta.org/vendidad/vd3.htm'),('vendidad3-darmesteter','https://www.avesta.org/vendidad/vd3sbe.htm')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda item:capture(item,'v2'),normal))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows.extend(pool.map(public_tls_exception,insecure))
    target.write_text(json.dumps(dict(script_sha256=sha(Path(__file__).read_bytes()),capture_helper_sha256=sha((HERE/'acquire_sources.py').read_bytes()),repository_pins=dict(greek=greek,pali=pali),reason='Pin successful repository commits; bare author hostname after mismatch; explicit per-fetch expired-certificate exception for public Avesta witnesses',attempts=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for r in rows:print(r['witness_id'],r.get('status_code'),r.get('format'),r.get('bytes'),r.get('error',''))


if __name__=='__main__':main()
