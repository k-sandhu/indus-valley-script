"""Compact identity-only views of held page text. Run with python -I."""
import argparse
import csv
import json
import re
import runpy
from pathlib import Path

M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))

def facts(sid, spec):
    nums=[]
    for part in spec.split(','):
        a=part.split('-');nums.extend(range(int(a[0]),int(a[-1])+1))
    M['log'](sid,nums,'candidate')
    for n in nums:
        p=M['path_for'](sid)/f'p{n:04}.txt'
        if not p.exists():print(sid,n,'MISSING');continue
        t=p.read_text(encoding='utf-8')
        # Only short metadata fragments are emitted; no source narrative is copied.
        refs=re.findall(r'\b(?:Reg(?:istration)?\.?\s*(?:[Nn]o\.?\s*)?|DLW,?\s*Reg\.\s*No\.?\s*)[\w./-]+',t)
        figs=re.findall(r'\b(?:Fig(?:s|ures?)?\.?|Pl(?:ate|s)?\.?|PI\.)\s*[IVXLC\d]+(?:[.:-][\dIVXLC]+)*(?:\s*[-–,]\s*\d+)?',t)
        contexts=re.findall(r'\b(?:[Ff]rom|[Ii]n)\s+(?:(?:[Tt]he|[Aa])\s+)?(?:[Ll]ayer|[Tt]rench|[Pp]eriod|[Pp]hase|[Mm]ound|[Uu]nstratified|[Ss]urface)[^\n.;]{0,80}',t)
        totals=re.findall(r'\b(?:[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix|[Ss]even|[Ee]ight|[Nn]ine|[Tt]en|[Ee]leven|[Tt]welve|[Tt]hirteen|\d+)\s+(?:(?:\w+[- ]?){0,4}\s+)?(?:seals?|sealings?|tablets?|potsherds?|graffiti)\b',t)
        labels=sorted(set(re.findall(r'\b(?:Indus|Harappan|Brahmi|Kharo\w+|Gupta|Kushan|Mature|Early|Late)\b',t,re.I)))
        print(json.dumps(dict(source=sid,pdf=n,refs=refs,figures=figs,contexts=[M['safe'](x) for x in contexts],totals=[M['safe'](x) for x in totals],labels=labels),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('pages');a=p.parse_args();facts(a.source,a.pages)
