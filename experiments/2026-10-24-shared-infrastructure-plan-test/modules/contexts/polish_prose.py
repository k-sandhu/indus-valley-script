"""Apply readability spacing to authored prose, never to raw source cells."""
from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent
def polish(t):
    t=re.sub(r'\b(Trench|Trenches|Figure|Figures|Table|Tables|Wall|Walls|Structure|Structures|Period|Phase|Phases|Room|Hearth|sample|all|of|and|through|between|about|after|before|at|indices|Plates|Chapter|layers|contains|Serial|serial|accession|Of|rows|normalization|retained|dates|passage|later|is|a)(?=\d)',r'\1 ',t)
    t=re.sub(r'\b(Period|Phase|Stage)(?=(?:[IVX]+[AB]?|3[BC])\b)',r'\1 ',t)
    t=re.sub(r'\bMound(?=(?:AB|ET|F|E)\b)','Mound ',t)
    t=re.sub(r'(?<!\w)(pp?\.)(?=\d)',r'\1 ',t)
    t=re.sub(r'(?<=\d)(BCE|BC|BP)\b',r' \1',t)
    t=re.sub(r'\bAD(?=\d)','AD ',t)
    t=re.sub(r'(?<=\d)(m|cm|sqm)\b',r' \1',t)
    t=re.sub(r'\b(\d+)(of)(?=\d)',r'\1 \2 ',t)
    t=re.sub(r'(?<=\d)(sealing|sealings|rows|lab|AMS|illustration|unit|sign)\b',r' \1',t)
    t=re.sub(r"('s)(?=\d)",r'\1 ',t)
    t=re.sub(r'(?<=\d)of(?=\d)',' of ',t)
    t=t.replace('MoundsAB andF','Mounds AB and F').replace('W35','W=35').replace('O10','O=10').replace('O11','O=11').replace('and?19','and ?=19').replace('and?17','and ?=17')
    t=t.replace('onD','on D:').replace('toC.','to C:.').replace('under the new D: raw directory','under the new D: raw directory')
    return t
def main():
    for name in ('RESEARCH.md','RETROSPECTIVE.md'):
        p=HERE/name;t=p.read_text(encoding='utf8')
        t=t.replace('31 authored context assessments and 75 date-evidence entries','32 authored context assessments and 78 date-evidence entries').replace('Seventy-three date entries','Seventy-six date entries')
        t=t.replace('We retained75 date-evidence entries','We retained78 date-evidence entries')
        t=t.replace('Table 1 in the same report gives A-8047','Table 1 in the 1994–1995 excavation report gives A-8047')
        t=t.replace('MiddleTown as printed','“Midle Town” as printed')
        t=t.replace('S1 is reported with Structure 1; S2 seals Phase 4 structures','S1 is reported with Structure 1; S2 came from a layer sealing Phase 4 structures')
        if name=='RESEARCH.md' and 'H94-2274/5332-01' not in t:
            paragraph='\n\nA further Harappa candidate shows where a plausible chain breaks. Table1 in the same report gives A-8047/AA-16461, A-8048 and A-8049 from hearths below Wall15, and the text infers that the wall was built after about2470BC. The Trench22 narrative places two faience tablets inside the perimeter wall, but Figure11.4/.6 labels the registered objects H94-2274/5332-01 and H94-2283/5332-02 as Trench7/8,wash. We preserve the conflict and the underlying-wall dates rather than choosing the location that would complete an association. A-8049 is source-flagged somewhat aberrant and remains in the record. Locators: printed pp.143–144,147 and160; indices4–5,8 and21.'
            t=t.replace('Actual dates in that article come from MoundsAB andF, about half a kilometre from the MoundE excavations, and are retained as rejected date transfers.',
              'Actual dates in that article come from MoundsAB andF, about half a kilometre from the MoundE excavations, and are retained as rejected date transfers.'+paragraph)
        p.write_text(polish(t),encoding='utf8')
    p=HERE/'visual-assets.json';data=json.loads(p.read_text(encoding='utf8'))
    for a in data['assets']:
        a['title']=polish(a['title']);a['caption']=polish(a['caption'])
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
