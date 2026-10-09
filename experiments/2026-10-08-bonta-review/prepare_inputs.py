"""Check supplied witnesses and reproduce the local page-segment derivative."""
from pathlib import Path
import argparse, hashlib, json, re

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raw-directory',default='derived-review-2026-10-08-01')
    ap.add_argument('--output',default='input-checks.json');a=ap.parse_args()
    directory=RAW/a.raw_directory;directory.mkdir(exist_ok=False)
    dest=OWN/a.output
    if dest.exists():raise FileExistsError(dest)
    source=RAW/'papers/bonta-2024-partial-decipherment-2nd-ed.page-text.txt'
    segments=source.read_text(encoding='utf-8').split('\f')
    payload=json.dumps(segments,ensure_ascii=False).encode('utf-8')
    (directory/'page-segments.json').write_bytes(payload)
    original=RAW/'papers/page-segments.json'
    durations=[]
    for p in sorted((RAW/'captions').glob('*.txt')):
        t=p.read_text(encoding='utf-8');m=re.search(r'^length_seconds: (\d+)$',t,re.M)
        durations.append({'lecture':int(p.name[:2]),'seconds':int(m[1]),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    pdfs=[]
    for p in sorted(RAW.glob('acquisition-*/*.pdf')):
        pdfs.append({'path':p.relative_to(ROOT).as_posix(),'has_PDF_magic':p.read_bytes().startswith(b'%PDF-')})
    result={'status':'Verified computation','page_segments':len(segments),
      'page_derivative_identical':payload==original.read_bytes(),'captions':len(durations),
      'caption_duration_seconds':sum(x['seconds'] for x in durations),'duration_records':durations,
      'pdf_payload_checks':pdfs,
      'full_2024_manuscript_PDF_present':any(p.read_bytes().startswith(b'%PDF-') for p in (RAW/'papers').glob('*.pdf')),
      'scope':'Byte and inventory checks only; no certification of machine captions or missing figures'}
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ['duration_records','pdf_payload_checks']},indent=2))
    assert result['page_derivative_identical']

if __name__=='__main__':main()
