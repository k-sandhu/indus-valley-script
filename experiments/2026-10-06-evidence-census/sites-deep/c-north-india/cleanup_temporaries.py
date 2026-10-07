"""Remove only rerenderable page PNGs created by this package; retain PDFs/OCR."""
from pathlib import Path
import json, re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
RAW=(ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/c-north-india').resolve()

def main():
    removed=[]
    for p in sorted(RAW.glob('*-pdf*.png')):
        match=re.fullmatch(r'(.+)-pdf\d{4}\.png',p.name)
        if not match or not (RAW/(match[1]+'.pdf')).exists():continue
        if p.resolve().parent!=RAW:raise ValueError('Target outside owned raw directory')
        removed.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,basis='Temporary page render; original PDF and OCR retained.'))
        p.unlink()
    record=dict(removed_files=removed,bytes_freed=sum(r['bytes'] for r in removed),scope=str(RAW))
    (RAW/'cleanup-manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(removed),bytes_freed=record['bytes_freed'])))

if __name__=='__main__':main()
