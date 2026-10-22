"""Recover catalogue site locators without viewing or retaining a page image."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,OUT,RAW,save
from safe_read import RESTRICTED,UNIT
source=ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
target=(RAW/'run4/cisi1-identity-review').resolve();target.mkdir(parents=True,exist_ok=True)
assert target.is_relative_to((RAW/'run4').resolve())
binary=Path('C:/Users/sandh/Downloads/poppler-24.07.0/Library/bin/pdftoppm.exe')
records=[]
try:
    for pg in map(int,sys.argv[2:]):
        output=target/f'page-{pg:04}.json';png=target/f'page-{pg:04}.png';prefix=png.with_suffix('')
        if output.exists():
            d=json.loads(output.read_text(encoding='utf-8'));assert d.get('complete_identity_projection');records.append(d);print('CACHED',pg,json.dumps(d['identity_lines']),flush=True);continue
        subprocess.run([str(binary),'-f',str(pg),'-l',str(pg),'-r','100','-singlefile','-png',str(source),str(prefix)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
        done=subprocess.run(['tesseract',str(png),'stdout','--psm','3'],capture_output=True,check=True)
        s=done.stdout.decode('utf-8',errors='replace');lines=[]
        # On the contents pages, site-heading lines contain publication locators.
        for i,line in enumerate(s.splitlines(),1):
            site=next((name for name in ['Desalpur','Desalpar','Surkotada','Surkotda'] if re.search(r'\b'+name+r'\b',line,re.I)),None)
            if site:
                lines.append({'site':site,'source_line':i,'locator_numbers':re.findall(r'\b\d{1,3}\b',line),'has_seal_term':bool(re.search(r'\bseals?\b',line,re.I)),'has_sealing_term':bool(re.search(r'\bsealings?\b',line,re.I))})
        d={'source_id':'cisi-1','pdf_page':pg,'complete_identity_projection':True,'raw_ocr_sha256':hashlib.sha256(done.stdout).hexdigest(),'identity_lines':lines,'text_recoverable':bool(s.strip()),'images_viewed':False,'projection':'Site heading and locator metadata only. Full OCR text is not saved or displayed.'}
        output.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
        # The explicit page-render cleanup is confined to this owned directory.
        assert png.resolve().is_relative_to(target)
        png.unlink()
        records.append(d);print('OCR',pg,json.dumps(lines),flush=True)
    save('catalogue-locator-access-v2.json',{'pages':records,'images_opened':0,'render_cleanup':'Each new render deleted immediately after its identity projection was saved. Existing source witnesses were not modified.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
except OSError as e:
    try:save('WRITE-FAILURE-v2.json',{'stopped':True,'error_class':type(e).__name__})
    finally:raise SystemExit('Stopped after an input/output error.')
