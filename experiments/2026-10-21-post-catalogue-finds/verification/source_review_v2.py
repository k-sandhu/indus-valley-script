"""Read source identity clauses through a closed vocabulary, without images."""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,RAW,page_index,csvrows
TERMS=set(('a an the this that these those and or but of in on at to from for with without by is are was were has have had it its their they which as one two three four five six seven eight nine ten no not all both only some any other same also each more less found reported recovered collected excavated yielded discovered obtained preserved published illustrated identified mentioned described called known held excavation excavations exploration explorations survey collection collections museum surface settlement site sites season seasons year years period phase mature early late ancient Indus Harappan Harappa Mohenjo-daro Chanhu-daro Dholavira Surkotada Surkotda Desalpar Desalpur Farmana Kanmer Karanpura Rakhigarhi Rojdi Kalibangan Khirsara Bhirrana Birrana Binjor Banawali Lothal India Gujarat Kutch Haryana Rajasthan Sindh Pakistan pottery potsherd potsherds sherd sherds seal seals sealing sealings tablet tablets tag tags tool tools rod rods stone steatite terracotta clay copper ivory bone inscribed uninscribed inscription inscriptions script letters characters legend legends graffiti mark marks evidence tentative possible possibly probably suggests references bibliography contents table figure figures fig plate plates pl caption captions photograph photographs drawing drawings number numbers registration antiquity accession antiquities basic data section sections corpus catalogue catalogued article report reports account general discussion note notes historical history earlier later total totals now first during before after since between include included includes including complete district department archaeological archaeology conservation chemical treatment transported analysis samples sample study investigation laboratory book books review reviews Indian 1963-64 1971-72 CISI Dlp Sktd Grb Joshi Parpola').casefold().split())
TERMS.update('remaining rest bear bears bearing bore carry carries carrying except either whereas however respectively conservation preservation cleaning cleaned treatment treated consolidating consolidation chemically plaster temple temples tomb tombs mosque inscriptions'.split())
TERMS.update('bangle bangles ring rings bead beads pendant pendants ornament ornaments bracelet bracelets amulet amulets fragment fragments vessel vessels lid lids handle handles celt celts adze adzes arrowhead arrowheads axe axes spearhead spearheads chisel chisels ingot ingots plaque plaques disc discs cake cakes ball balls cone cones cuneiform Brahmi Tamil Uraiyur Kanchipuram'.casefold().split())
def closed(line):
    # Quantities are allowed only when the phrase explicitly counts objects.
    # Other numerals may belong to excluded fields and are never displayed.
    counts={m.start():m.group() for m in re.finditer(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:(?:inscribed|steatite|terracotta|clay|copper|square)\s+){0,3}(?:seals?|sealings?|tablets?|potsherds?|sherds?|rods?)\b',line,re.I)}
    line=re.sub(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b','[quantity withheld]',line,flags=re.I)
    tokens=re.findall(r"\b[\w]+(?:[-’'][\w]+)*\b|[.;:!?()]",line)
    out=[];mask=False
    for t in tokens:
        if t.casefold() in TERMS or t in '.;:!?()':
            out.append(t);mask=False
        elif not mask:out.append('[omitted]');mask=True
    return ' '.join(out)
def display(s,lines=None):
    ls=s.splitlines()
    for n,line in enumerate(ls,1):
        if lines is not None and n not in lines:continue
        if not line.strip():continue
        view=closed(line)
        if view not in ('[omitted]','[omitted] .'):print(n,view)
idx=page_index();mode=sys.argv[2];access=[]
if mode=='omission':
    for sid,pg in [('iar-2013-14',106),('iar-2003-04-asi',62),('iar-1997-98-archive',329),('puratattva-33',188),('puratattva-35-held',85)]:
        p=idx[sid,pg][0];s=p.read_text(encoding='utf-8-sig',errors='replace')
        print('PAGE',sid,pg);display(s)
        access.append({'source_id':sid,'pdf_page':pg,'access':'Closed identity and qualification vocabulary; source numbers masked; no image.'})
elif mode=='relations':
    for sid,pg in [('iar-2003-04-asi',62),('iar-1997-98-archive',329),('puratattva-33',188)]:
        p=idx[sid,pg][0];s=p.read_text(encoding='utf-8-sig',errors='replace');print('PAGE',sid,pg)
        ls=s.splitlines()
        keep=set(range(59,100)) if sid=='iar-2003-04-asi' else None
        display(s,keep)
        for m in re.finditer(r'\b(?:Excavations?|Excavated)\s+(?:at|site)\s+([A-Z][A-Za-z -]{2,45})',s):
            print('site heading',m[1].strip())
        # Object quantities are distinct from all excluded source quantities.
        flat=re.sub(r'\s+',' ',s)
        phrases=re.findall(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:(?:inscribed|Harappan|steatite|terracotta|square)\s+){0,3}(?:seals?|sealings?|tablets?|potsherds?|sherds?|rods?)\b',flat,re.I)
        print('object quantities',phrases)
        access.append({'source_id':sid,'pdf_page':pg,'access':'Identity relations and object quantities only; no other quantities or image.'})
elif mode=='layout':
    register={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')}
    for sid,pg in [('iar-2003-04-asi',62),('iar-1997-98-archive',329)]:
        p=ROOT/register[sid]['local_path']
        done=subprocess.run(['pdftotext','-f',str(pg),'-l',str(pg),'-layout',str(p),'-'],capture_output=True,check=True)
        s=done.stdout.decode('utf-8',errors='replace')
        print('LAYOUT',sid,pg)
        # Extract the two report columns independently before applying the mask.
        lines=s.splitlines();left=[];right=[]
        for l in lines:
            parts=re.split(r'\s{5,}',l.strip(),maxsplit=1)
            left.append(parts[0]);right.append(parts[1] if len(parts)>1 else '')
        for label,ls in [('left',left),('right',right)]:
            print('COLUMN',label);display('\n'.join(ls))
        access.append({'source_id':sid,'pdf_page':pg,'access':'PDF text layer with columns separated; closed identity vocabulary; no OCR or image.'})
elif mode=='columns':
    binary=Path('C:/Users/sandh/Downloads/poppler-24.07.0/Library/bin/pdftotext.exe')
    if not binary.exists():raise SystemExit('Coordinate text extraction is unavailable; no package is installed.')
    register={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')}
    for sid,pg in [('iar-2003-04-asi',62),('iar-1997-98-archive',329)]:
        p=ROOT/register[sid]['local_path']
        done=subprocess.run([str(binary),'-f',str(pg),'-l',str(pg),'-bbox-layout',str(p),'-'],capture_output=True,check=True)
        root=ET.fromstring(done.stdout);page=next(x for x in root.iter() if x.tag.endswith('page'));middle=float(page.attrib['width'])/2
        cols=[{},{}]
        for line in page.iter():
            if not line.tag.endswith('line'):continue
            col=int(float(line.attrib['xMin'])>middle);y=float(line.attrib['yMin'])
            for w in line:
                if w.tag.endswith('word'):cols[col].setdefault(y,[]).append((float(w.attrib['xMin']),w.text or ''))
        print('PAGE',sid,pg)
        for col,ys in enumerate(cols):
            print('COLUMN',col)
            text='\n'.join(' '.join(w for _,w in sorted(ws)) for y,ws in sorted(ys.items()))
            display(text)
            # Return object-count and predicate identity without any source description.
            flat=re.sub(r'\s+',' ',text)
            patterns=[r'\b(?:one|two|three|four|five|\d+)\s+seals?\b',r'\b(?:remaining|other|rest)\s+(?:one|two|three|four|five|\d+)\b',r'\b(?:remaining|other|rest)\s+seals?\b']
            print('object-group identity phrases',[m[0] for pat in patterns for m in re.finditer(pat,flat,re.I)])
        access.append({'source_id':sid,'pdf_page':pg,'access':'PDF word coordinates separate report columns before closed identity filtering; no image or OCR.'})
elif mode=='containment':
    p=ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
    existing=p.with_suffix('.txt')
    if existing.exists() and existing.stat().st_size:
        pages=existing.read_text(encoding='utf-8-sig',errors='replace').split('\f')
    else:
        done=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True)
        pages=done.stdout.decode('utf-8',errors='replace').split('\f')
    found=0
    for pg,s in enumerate(pages,1):
        if re.search(r'\b(?:Desalpur|Desalpar|Surkotada|Surkotda)\b',s,re.I):
            found+=1;print('CISI1 PDF',pg)
            # For each site name show only its paragraph and nearby identity clauses.
            ls=s.splitlines();keep=set()
            for i,l in enumerate(ls):
                if re.search(r'\b(?:Desalpur|Desalpar|Surkotada|Surkotda)\b',l,re.I):keep.update(range(max(1,i-2),min(len(ls),i+14)+1))
            display(s,keep);access.append({'source_id':'cisi-1','pdf_page':pg,'access':'Existing PDF text layer; closed identity vocabulary near site heading only; no image.'})
    print('CISI1 site-name pages',found)
    # Only the identity portions of the two report pages are needed here.
    for sid,pg,keep in [('puratattva-37',65,set(range(1,18))),('surkotada-1990',382,set(range(37,59)))]:
        p=idx[sid,pg][0];s=p.read_text(encoding='utf-8-sig',errors='replace');print('PAGE',sid,pg);display(s,keep)
        access.append({'source_id':sid,'pdf_page':pg,'access':'Closed identity vocabulary in the object identity portion; no image.'})
(OUT/('source-review-access-'+mode+'-v2.json')).write_text(json.dumps(access,indent=2)+'\n',encoding='utf-8')
