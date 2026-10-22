"""Check the extra IAR volumes for northern entries beyond the seed aliases."""
import json
import re
import runpy
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
pages=M['rows'](M['OUT']/'pages-read-N.csv')
seen={(r['source_id'],int(r['pdf_page'])) for r in pages}
result={}
for sid in [s for s in M['IDS'] if s.startswith('iar-')]:
    found=[]
    for p in sorted(M['path_for'](sid).glob('p*.txt')):
        n=int(p.stem[1:]);t=p.read_text(encoding='utf-8')
        if (sid,n) in seen:continue
        if not re.search(r'Harappan|Indus',t,re.I) or not M['KEY'].search(t):continue
        if re.search(M['ALIASES'],t,re.I):continue
        labels=sorted(set(s.lower() for s in re.findall(r'Haryana|Harayana|Punjab|Rajasthan|Uttar\s+Pradesh|Jammu|Delhi|Balu|Girawad|Kanpur|Indiranagar|Atranjikhera|Ganeshwar|Lal\s+Qila',t,re.I)))
        found.append(dict(pdf_page=n,north_labels=labels))
    result[sid]=found
    print(sid,found,flush=True)
(M['OUT']/'generic-review-N.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
