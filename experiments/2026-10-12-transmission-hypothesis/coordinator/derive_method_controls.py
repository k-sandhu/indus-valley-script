"""Save inspected-page and HTML derivatives without distributing source text."""
import hashlib
import json
from pathlib import Path
import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-12-transmission-hypothesis/coordinator/method-v1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths=[RAW/'shennan2020-selected-pages-v1.json',RAW/'diachenko2023-body-v1.txt',RAW/'derivatives-v1.json']
    if any(path.exists() for path in paths):raise SystemExit('Derivatives exist; no overwrite.')
    pdf=RAW/'shennan2020.pdf';doc=fitz.open(pdf);pages=[1,6,9,11,13,15]
    with paths[0].open('x',encoding='utf-8') as stream:
        json.dump({'parent_sha256':sha(pdf),'pdf_pages_one_based':pages,
                   'pages':[{'pdf_page':n,'text':doc[n-1].get_text()} for n in pages]},
                  stream,ensure_ascii=False,indent=2);stream.write('\n')
    html=RAW/'diachenko2023.html'
    soup=BeautifulSoup(html.read_bytes(),'html.parser')
    article=soup.find('article') or soup
    with paths[1].open('x',encoding='utf-8') as stream:stream.write(article.get_text('\n',strip=True)+'\n')
    records=[]
    for path,parent in zip(paths[:2],[pdf,html]):
        records.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size,
                        'parent_path':parent.relative_to(ROOT).as_posix(),'parent_sha256':sha(parent),
                        'redistribution':'local-only'})
    with paths[2].open('x',encoding='utf-8') as stream:
        json.dump({'derivatives':records,'pdf_page_count':len(doc)},stream,indent=2);stream.write('\n')
    print(json.dumps({'pdf_pages':len(doc),'selected_pages':pages,'derivatives':len(records)}))


if __name__=='__main__':main()
