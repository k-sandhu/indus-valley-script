"""Review only each registration match's immediate source line."""
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,csvrows,page_index,save,savecsv
from search_and_content import pattern

idx=page_index();out=[]
for r in csvrows(OUT/'unnamed-search.csv'):
    if r['result']!='registration-shaped occurrence':continue
    pg=int(r['pdf_page']);lines_seen=[];classification='unresolved number occurrence'
    for p in idx[r['source_id'],pg]:
        lines=p.read_text(encoding='utf-8-sig',errors='replace').splitlines()
        n=int(r['line'])
        if n>len(lines):continue
        line=lines[n-1];rx=pattern(r['registration']);m=rx.search(line)
        if not m:continue
        digits=re.sub(r'^DHR[- ]*','',r['registration'],flags=re.I).strip('- ')
        if re.fullmatch(r'\s*'+re.escape(digits)+r'\s*',line,re.I):classification='isolated number; identity unconfirmed'
        if re.search(r'\bDHR[- ]*\d+',line,re.I) or re.search(r'\b(?:reg(?:istration)?|acc(?:ession)?|antiquity|field\s+no)\b',line,re.I):classification='identifier-context occurrence'
        if re.match(r'^\s*\d{1,3}[.)]\s+'+re.escape(digits)+r'\b',line):classification='catalogue registration occurrence'
        lines_seen.append({'line':n,'line_has_type_word':bool(re.search(r'\b(?:seal|sealing|tablet|sherd|pottery)\b',line,re.I)),'line_has_registration_label':bool(re.search(r'\b(?:reg(?:istration)?|acc(?:ession)?|antiquity)\b',line,re.I)),'line_is_isolated_number':bool(re.fullmatch(r'\s*\d+\s*',line))})
    out.append(r|{'line_assessment':classification})
savecsv('unnamed-line-review.csv',out,list(out[0]) if out else ['family','source_id','pdf_page','line','line_assessment'])
save('unnamed-line-review.json',{'occurrences':out,'scope':'Only the immediate matching line is classified. No source line or adjacent description is reproduced. Registration-shaped hits are not promoted to object identities.'})
for r in out:print(r['family'],r['source_id'],r['pdf_page'],r['line'],r['line_assessment'])
