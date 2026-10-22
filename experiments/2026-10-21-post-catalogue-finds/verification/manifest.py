"""Hash the audit code and the exact identity witnesses used by its samples."""
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,csvrows,page_index,save

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
idx=page_index();pages={}
for name in ['blind-assignments.csv','omission-assignments.csv']:
    for r in csvrows(OUT/name):
        source=r.get('primary_publication',r.get('source_id'))
        for n in re.findall(r'\d+',r['pdf_page']):
            for p in idx.get((source,int(n)),[]):pages[str(p.relative_to(ROOT))]=sha(p)
inputs=['matching/source-register.csv','acquisition/source-register-1a.csv','acquisition-web/source-candidates-1b.csv','acquisition/candidate-pages-1a.csv','acquisition-web/candidate-publication-locators-1b.json','extraction/D/seal-table-D.json','extraction/D/catalogue-metadata-D.json','review/dholavira-decisions.csv','review/match_dholavira.py','review/build_list.py','selection/sites-seed.csv','PROTOCOL.md','AMENDMENT-1.md']
inputs.extend(str(p.relative_to(BASE)) for p in sorted((BASE/'extraction').glob('*/pages-read-*.csv')))
save('run-manifest.json',{'author':'Codex / GPT-6; exact build identifier not exposed','harness':'API tool harness','python':sys.version.split()[0],'execution':'Python isolated mode; bytecode writes disabled for final checks. Standard library only.','code_hashes':{p.name:sha(p) for p in sorted(OUT.glob('*.py'))},'input_hashes':{str((BASE/n).relative_to(ROOT)):sha(BASE/n) for n in inputs},'sample_page_text_hashes':pages,'input_revision_record':'input-revision.json','corpus_identity_record':'corpus-access.json','baseline_identity_record':'catalogue-containment-check.json','source_acquisition':'Existing held sources only; no new acquisition or conversion.'})
print('MANIFEST',len(pages),'sample text witnesses hashed.')
