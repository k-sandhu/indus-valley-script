"""Extract closed-vocabulary clause metadata from source columns."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pdf',required=True,type=Path)
    p.add_argument('--pages',required=True)
    a=p.parse_args()
    ns=[]
    for term in a.pages.split(','):
        if '-' in term:
            lo,hi=map(int,term.split('-')); ns.extend(range(lo,hi+1))
        else: ns.append(int(term))
    for n in ns:
        data=subprocess.run([r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin\pdftotext.exe','-f',str(n),'-l',str(n),'-bbox',str(a.pdf),'-'],capture_output=True,check=True).stdout
        doc=ET.fromstring(data)
        pg=next(x for x in doc.iter() if x.tag.endswith('page'))
        words=[(float(x.attrib['xMin']),float(x.attrib['yMin']),x.text or '') for x in doc.iter() if x.tag.endswith('word')]
        for c in ('L','R'):
            ws=sorted((x,y,t) for x,y,t in words if (x<300)==(c=='L') and 72<y<725)
            lines={}
            for x,y,t in ws:
                line=next((k for k in lines if abs(k-y)<3),y)
                lines.setdefault(line,[]).append((x,t))
            flat=' '.join(' '.join(t for _,t in sorted(lines[k])) for k in sorted(lines))
            flat=re.sub(r'(?<=[A-Za-z])-\s+(?=[a-z])','',flat)
            clauses=re.split(r'(?<!\d)[.;](?!\d)|(?<=[.!?])\s+(?=[A-Z])',flat)
            for i,s in enumerate(clauses):
                if not re.search(r'\b(?:seals?|sealings?|tablets?|inscri\w*|celts?|graffit\w*|tags?|DISTRICT)\b',s,re.I): continue
                counts=re.findall(r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|several|few|solitary|single)\s+(?:(?:Harappan|terracotta|steatite|copper|inscribed|square|broken|clay|large|small)\s+){0,4}(?:seals?|sealings?|tablets?|celts?|potsherds?|sherds?|tags?)\b',s,re.I)
                locs=re.findall(r'\b(?:[Pp]l(?:ate)?\.?\s*\d+[a-z]?|[Ff]ig(?:s|ure)?\.?\s*\d+(?:\s*[-–]\s*\d+)?|[Pp]hase\s*[-–]?[IVX0-9Il]+|[Pp]eriod\s*[-–]?[IVX0-9Il]+|[Tt]rench(?:es)?\s+[A-Z][a-z]?\s*\d+|[A-Z][a-z]?\d{1,2})\b',s)
                label=re.findall(r'(?:AT|at|IN|in)\s+([A-Z][A-Za-z\- ]{2,55}),\s*(?:DISTRICT|district)',s)
                print(json.dumps(dict(pdf_page=n,column=c,clause=i,site_heading=label,types=re.findall(r'\b(?:seals?|sealings?|tablets?|celts?|sherds?|potsherds?|vessels?|tags?|pottery)\b',s,re.I),counts=counts,locators=locs,material=re.findall(r'\b(?:copper|steatite|terracotta|clay|shell|ivory|bone|faience|stone)\b',s,re.I),has_script_reference=bool(re.search(r'inscri|script|sign|character|letter|legend|alphabet|symbol',s,re.I)),has_Harappan=bool(re.search(r'Harappan|Indus',s,re.I)),is_unscripted=bool(re.search(r'uninscribed|without.*(?:inscri|script)',s,re.I)),is_broken=bool(re.search(r'broken|fragment',s,re.I)),is_total=bool(re.search(r'total|number|brought|brings',s,re.I)),qualified=bool(re.search(r'possibl|resembl|probably',s,re.I)))))


if __name__=='__main__': main()
