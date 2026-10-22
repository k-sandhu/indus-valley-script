"""Preview grammatical relations using an explicit metadata vocabulary."""
import argparse
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser();p.add_argument('--pdf',required=True,type=Path);p.add_argument('--pages',required=True);a=p.parse_args()
    allowed=set(('a an the was were is are of from in and or to at by for on with without these this that those also include includes including yielded found brought discovered excavation season current previous total number site another other remaining both each among one its their it they above belonged belong belonging period phase Harappan Indus inscribed inscription inscriptions seals seal sealing sealings tablet tablets copper steatite terracotta clay square broken fragment fragments intact Trench Trenches latter former not no has have had all same such only two presently made decorative antiquities during early mature late find besides earlier mentioned recovered levels deposit layer assigned stated modern impression impressions mould cast knobs reverse obverse holes handle celts celt engravings partly effaced top portion pottery sherd potsherd sherds potsherds graffiti marks uninscribed alphabets alphabetical bearing bears carrying carries script legend legends characters letters'.lower()).split())
    allowed.difference_update(['one','two']);allowed.update(['sign','signs'])
    # Numerical content is removed before the vocabulary pass.
    for n in map(int,a.pages.split(',')):
        data=subprocess.run([r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin\pdftotext.exe','-f',str(n),'-l',str(n),'-bbox',str(a.pdf),'-'],capture_output=True,check=True).stdout
        doc=ET.fromstring(data);words=[(float(x.attrib['xMin']),float(x.attrib['yMin']),x.text or '') for x in doc.iter() if x.tag.endswith('word')]
        for c in ['L','R']:
            lines={}
            for x,y,t in words:
                if (x<300)!=(c=='L') or not 35<y<725:continue
                line=next((k for k in lines if abs(k-y)<3),y);lines.setdefault(line,[]).append((x,t))
            flat=' '.join(' '.join(t for _,t in sorted(lines[k])) for k in sorted(lines))
            for i,s in enumerate(re.split(r'(?<!\d)[.;](?!\d)|(?<=[.!?])\s+(?=[A-Z])',flat)):
                if not re.search(r'\b(?:seal\w*|celts?|tablets?|inscrib\w*|letters?|characters?|legends?|alphabets?|symbols?|signs?)\b',s,re.I):continue
                tokens=re.findall(r'[A-Za-z]+|[^A-Za-z\s]+',s)
                masked=' '.join(t if t.lower() in allowed else '[omitted]' for t in tokens)
                masked=re.sub(r'(?:\[omitted\]\s*){2,}','[omitted] ',masked)
                print(f'{n}{c} clause {i}: {masked}')


if __name__=='__main__':main()
