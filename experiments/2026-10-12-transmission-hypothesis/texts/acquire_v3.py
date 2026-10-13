"""Follow observed source links and repair two retained locator failures."""
import json
import concurrent.futures
from pathlib import Path
import requests
import fitz
from acquire_sources import ROOT,HERE,RAW,capture,sha
from acquire_followup import public_tls_exception


def author_pdf():
    url='https://www.michaelwitzel.org/wp-content/uploads/2014/06/ejvs0501article.pdf'
    ident='witzel-substrates1999-author'
    row=dict(witness_id=ident,requested_url=url,tls_verification=False,transport_caveat='Per-fetch public unauthenticated exception after two recorded hostname failures; no global TLS change',rights='rights-unverified',redistribution='local-only')
    from datetime import datetime,timezone
    row['retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
    try:
        r=requests.get(url,timeout=30,verify=False,headers={'User-Agent':'Source inspection research/1.0'})
        data=r.content;kind='pdf' if data.startswith(b'%PDF') else 'bin'
        path=RAW/f'{ident}-v3.{kind}'
        if path.exists():raise FileExistsError(path)
        path.write_bytes(data)
        row.update(status_code=r.status_code,resolved_url=r.url,path=path.relative_to(ROOT).as_posix(),sha256=sha(data),bytes=len(data),format=kind,content_type=r.headers.get('Content-Type'))
        if kind=='pdf':
            doc=fitz.open(stream=data,filetype='pdf');out=RAW/f'{ident}-v3-pages.json'
            payload=json.dumps(dict(parent_path=row['path'],parent_sha256=row['sha256'],tool='PyMuPDF',version=fitz.VersionBind,pages=[dict(pdf_page_1based=i+1,text=p.get_text()) for i,p in enumerate(doc)]),ensure_ascii=False,indent=2).encode('utf8')
            out.write_bytes(payload);row['pdf_pages']=len(doc);row['derivative']=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(payload),bytes=len(payload),parent_sha256=row['sha256'])
    except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
    return row


def main():
    target=RAW/'capture-v3.json'
    if target.exists():raise FileExistsError(target)
    greek=json.loads((RAW/'greek-repo-commit-v1.json').read_text('utf8'))['sha']
    pali=json.loads((RAW/'bilara-repo-commit-v1.json').read_text('utf8'))['sha']
    normal=[('odyssey-english-corrected',f'https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/{greek}/data/tlg0012/tlg002/tlg0012.tlg002.perseus-eng3.xml'),('bilara-readme',f'https://raw.githubusercontent.com/suttacentral/bilara-data/{pali}/README.md'),('bilara-root-index',f'https://api.github.com/repos/suttacentral/bilara-data/contents/?ref={pali}')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda item:capture(item,'v3'),normal))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows.extend(pool.map(public_tls_exception,[('yasna9-avestan-corrected','https://www.avesta.org/yasna/y9to11.htm'),('vendidad-avestan-corrected','https://www.avesta.org/vendidad/vd.htm')]))
        rows.append(author_pdf())
    target.write_text(json.dumps(dict(script_sha256=sha(Path(__file__).read_bytes()),reason='Observed Greek folder and Avesta translation links supply corrected locators; source selection unchanged; public author TLS exception separately recorded',attempts=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for r in rows:print(r['witness_id'],r.get('status_code'),r.get('format'),r.get('bytes'),r.get('error',''))


if __name__=='__main__':main()
