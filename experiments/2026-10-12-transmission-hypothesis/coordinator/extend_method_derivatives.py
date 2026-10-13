"""Add two accepted-manuscript PDF pages; retain the earlier extraction endpoint."""
import hashlib
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/method-v1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=RAW/'shennan2020-additional-pages-v2.json';out=RAW/'derivatives-v2.json'
    if path.exists() or out.exists():raise SystemExit('Additional derivative endpoint exists; no overwrite.')
    pdf=RAW/'shennan2020.pdf';doc=fitz.open(pdf);pages=[14,16]
    with path.open('x',encoding='utf-8') as stream:
        json.dump({'parent_sha256':sha(pdf),'pdf_pages_one_based':pages,
                   'pages':[{'pdf_page':n,'text':doc[n-1].get_text()} for n in pages]},
                  stream,ensure_ascii=False,indent=2);stream.write('\n')
    records=json.loads((RAW/'derivatives-v1.json').read_text('utf-8'))['derivatives']
    records.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size,
                    'parent_path':pdf.relative_to(ROOT).as_posix(),'parent_sha256':sha(pdf),'redistribution':'local-only'})
    with out.open('x',encoding='utf-8') as stream:json.dump({'derivatives':records,'pdf_page_count':len(doc)},stream,indent=2);stream.write('\n')
    for number in pages:
        print('PDF PAGE',number);print(doc[number-1].get_text().encode('ascii','backslashreplace').decode())


if __name__=='__main__':main()
