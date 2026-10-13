"""Capture local-only primary witnesses without overwriting previous attempts."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import sys
import requests
import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'data/raw/2026-10-11-societal-persistence/literature'
HERE = Path(__file__).resolve().parent

PLAN = [
 ('L01-childe1950', 'https://faculty.washington.edu/plape/citiesaut11/readings/Childe-urban%20revolution%201950.pdf'),
 ('L02-tainter2006', 'https://research.fs.usda.gov/download/treesearch/61158.pdf'),
 ('L03-holling1973', 'https://pure.iiasa.ac.at/id/eprint/26/7/RP-73-003.pdf'),
 ('L04-holling2001', 'https://alnap.cdn.ngo/media/documents/holling-complexity-econecol-socialsys-2001.pdf'),
 ('L05-walker2004', 'https://ecologyandsociety.org/vol9/iss2/art5/inline.html'),
 ('L06-folke2010', 'https://research.fs.usda.gov/download/treesearch/42598.pdf'),
 ('L07-anderies2004', 'https://ecologyandsociety.org/vol9/iss1/art18/inline.html'),
 ('L08-ostrom2009', 'https://www.dpi.inpe.br/gilberto/cursos/cst-317/papers/ostrom_sustainability.pdf'),
 ('L09-smith2021', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8157985/'),
 ('L10-lawrence2025', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12036995/'),
 ('L11-pichancourt2025', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11867035/'),
 ('L12-henrich2004', 'https://coevolution.fas.harvard.edu/sites/g/files/omnuum5841/files/culture_cognition_coevol_lab/files/henrich_2004-2.pdf'),
 ('L13-derex2016', 'https://maximederex.github.io/assets/pdf/derex2016.pdf'),
 ('L14-hirth1998', 'https://www.journals.uchicago.edu/doi/10.1086/204759'),
 ('L15-halstead1989', 'https://assets.cambridge.org/97805216/11923/excerpt/9780521611923_excerpt.pdf'),
 ('L16-vonneumann1945', 'https://www.erlinger.name/Tekster/VonNeumann1945.pdf'),
 ('L17-sraffa1960', 'https://www.nuevatribuna.es/media/nuevatribuna/files/2013/04/15/production_of_commodities_by_means_of_commodities.pdf'),
 ('L18-hawkinssimon1949', 'https://iiif.library.cmu.edu/file/Simon_box00029_fld02213_bdl0001_doc0001/Simon_box00029_fld02213_bdl0001_doc0001.pdf'),
 ('L19-lade2020', 'https://ecologyandsociety.org/vol25/iss3/art19/'),
 ('L20-sellberg2024', 'https://ecologyandsociety.org/vol29/iss3/art26/'),
 ('L21-feinman2023', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10400939/'),
 ('L25-tainter1988', 'https://assets.cambridge.org/97805213/86739/excerpt/9780521386739_excerpt.pdf'),
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def capture(item, tag):
    ident, url = item
    row = dict(id=ident, requested_url=url, retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), rights='rights-unverified', redistribution='local-only', tls_verification=True)
    try:
        res = requests.get(url, timeout=30, headers={'User-Agent':'Research source witness inspection/1.0'})
        data = res.content
        fmt = 'pdf' if data.startswith(b'%PDF') else 'html' if b'<html' in data[:4000].lower() or b'<!doctype' in data[:4000].lower() else 'bin'
        dest = OUT / f'{ident}-{tag}.{fmt}'
        if dest.exists():
            raise FileExistsError(str(dest))
        dest.write_bytes(data)
        row.update(status_code=res.status_code, final_url=res.url, path=dest.relative_to(ROOT).as_posix(), bytes=len(data), sha256=sha(data), format=fmt, content_type=res.headers.get('Content-Type'))
        if fmt=='pdf':
            doc=fitz.open(stream=data, filetype='pdf')
            pages=[dict(pdf_page_1based=i+1, text=p.get_text()) for i,p in enumerate(doc)]
            row['page_count']=len(doc)
            extracted=OUT/f'{ident}-{tag}-pages.json'
            encoded=json.dumps(dict(parent_path=row['path'], parent_sha256=row['sha256'], extraction='PyMuPDF', extraction_version=fitz.VersionBind, pages=pages),ensure_ascii=False,indent=2).encode('utf-8')
        elif fmt=='html':
            soup=BeautifulSoup(data,'html.parser')
            for x in soup(['script','style','nav']): x.decompose()
            lines=[t.strip() for t in soup.get_text('\n').splitlines() if t.strip()]
            extracted=OUT/f'{ident}-{tag}-text.txt'
            encoded=('\n'.join(lines)+'\n').encode('utf-8')
        else:
            return row
        extracted.write_bytes(encoded)
        row['extraction']=dict(path=extracted.relative_to(ROOT).as_posix(),sha256=sha(encoded),bytes=len(encoded), parent_sha256=row['sha256'])
    except Exception as exc:
        row['error']=type(exc).__name__+': '+str(exc)
    return row

def main():
    tag = sys.argv[1] if len(sys.argv)>1 else 'capture-v1'
    chosen = set(sys.argv[2:])
    plan=[x for x in PLAN if not chosen or x[0] in chosen]
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/f'{tag}.json'
    if target.exists(): raise FileExistsError(str(target))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda x:capture(x,tag),plan))
    target.write_text(json.dumps(dict(script_sha256=sha(Path(__file__).read_bytes()), attempts=rows),ensure_ascii=False,indent=2),encoding='utf-8')
    for r in rows:
        print(r['id'], r.get('status_code'),r.get('format'),r.get('bytes'),r.get('error',''))

if __name__=='__main__': main()
