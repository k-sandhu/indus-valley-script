"""Inspect locator and catalogue metadata without emitting source passages."""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['entries', 'catalogue', 'journals', 'locators'])
    p.add_argument('root', type=Path)
    p.add_argument('package', type=Path)
    p.add_argument('--source', default='')
    p.add_argument('--pages', default='')
    a = p.parse_args()
    if a.mode == 'journals':
        candidates = list(csv.DictReader((a.package / 'acquisition/candidate-pages-1a.csv').open(encoding='utf-8-sig', newline='')))
        selected = [r for r in candidates if r['site_code'] in ('HRP','MHJ') and r['source_id'].startswith(('puratattva-', 'man-environment-'))]
        grouped = {}
        for r in selected:
            grouped.setdefault((r['source_id'], int(r['pdf_page'])), set()).add(r['site_code'])
        found = []
        for (sid, page), sites in sorted(grouped.items()):
            path = a.root / sid / f'p{page:04}.txt'
            text = path.read_text(encoding='utf-8', errors='replace')
            pat = r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred)\s+(?:(?:inscribed|Harappan|Indus|steatite|terracotta|faience|clay|square|rectangular|copper|ivory|bone|miniature|intact|broken|complete|stone|seal)\s+){0,4}(?:seals?|sealings?|tablets?|rods?|graffiti|sherds?)\b'
            vals = [re.sub(r'\s+', ' ', m.group()) for m in re.finditer(pat, text, re.I)]
            if vals:
                found.append({'source_id':sid, 'pdf_page':page,'candidate_sites':sorted(sites),'count_phrases': vals})
        print(json.dumps({'scanned_pages':len(grouped),'count_candidates':found}, indent=2))
        return
    folder = a.root / a.source
    nums = [int(x) for x in a.pages.split(',')] if a.pages else [int(x.stem[1:]) for x in sorted(folder.glob('p*.txt'))]
    for page in nums:
        text = (folder / f'p{page:04}.txt').read_text(encoding='utf-8', errors='replace')
        if a.mode == 'locators':
            nums2 = [(i+1,line.strip()) for i,line in enumerate(text.splitlines()) if re.fullmatch(r'\s*\d{1,4}\s*',line)]
            print(json.dumps({'source_id':a.source,'pdf_page':page,'standalone_numeric_locators': nums2[:1]+nums2[-1:]}))
        elif a.mode == 'entries':
            entries = []
            for i,line in enumerate(text.splitlines(),1):
                m = re.match(r'^\s*(\d{1,2})[.)]\s+[A-Z]',line)
                if m:
                    entries.append({'line':i,'entry_id':m.group(1)})
                # LKD table: retain only first three identity columns.
                m = re.match(r'^\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+[A-Z]',line)
                if m:
                    entries.append({'line':i,'table_identity_columns':m.groups()})
            print(json.dumps({'source_id':a.source,'pdf_page':page,'entries':entries}))
        else:
            out = []
            for i,line in enumerate(text.splitlines(),1):
                ids = re.findall(r'\b[HM]-\d+(?:[A-Z])?\b', line)
                if ids:
                    types = re.findall(r'\b(?:seal|seals|tablet|tablets|rod|rods|pottery)\b',line,re.I)
                    out.append({'line':i,'catalogue_ids':ids,'type_words':types})
            print(json.dumps({'source_id':a.source,'pdf_page':page,'mentions':out}))

if __name__ == '__main__':
    main()
