"""Freeze source-only assessments before opening the withheld table columns."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from safe_read import OUT, page_path

FIELDS=['season','object_type','findspot','page','plate_or_figure','photo_published','drawing_published','transcription_published','inscription_status','registration_present']
U='UNASSESSABLE'

def main():
    with (OUT/'blind-assignments.csv').open(encoding='utf-8',newline='') as f: assignments=list(csv.DictReader(f))
    evidence=[]
    for a in assignments:
        r={k:U for k in FIELDS}
        r.update(row_id=a['row_id'],season='',findspot='',photo_published='unknown',drawing_published='unknown',transcription_published='unknown',registration_present='not-applicable')
        source=a['primary_publication']; pages=[int(x) for x in re.findall(r'\d+',a['pdf_page'])]
        note='Page text only. Publication indicators left unknown without an object-specific textual statement.'
        reg=a['registration_or_position']
        if not reg.startswith('position:'):
            r['registration_present']='yes' if any(re.search(r'(?<!\d)'+r'[\s-]*'.join(map(re.escape,re.findall(r'[A-Za-z]+|\d+',reg)))+r'(?!\d)',page_path(source,p).read_text(encoding='utf-8-sig'),re.I) for p in pages if page_path(source,p)) else 'no'
        if source=='bisht-2015-held':
            p=pages[0];r['page']=str(p-17)
            if 264<=p<=275:
                r.update(object_type='seal',plate_or_figure='')
                s=page_path(source,p).read_text(encoding='utf-8-sig')
                for line in s.splitlines():
                    m=re.match(r'^\s*\d{1,3}\.\s+'+re.escape(reg)+r'\s+(\d{1,2}(?:[xX×+]\d{1,3})+)',line)
                    if m:r['findspot']=m[1]
                if not r['findspot']:r['findspot']=U
                note+=' Grid is the identity column only; continuation fragments not reconstructed.'
            elif p in (292,295):
                r.update(object_type='seal',plate_or_figure='')
            elif p in (328,329,330,333):
                r.update(object_type='sealing',plate_or_figure='',photo_published='yes')
            elif p==245:
                r.update(object_type=U,plate_or_figure=U,drawing_published='yes')
                note+=' Multiple numbered captions; the positional cue does not identify a unique caption.'
            elif p==248:
                r.update(object_type=U,plate_or_figure='Fig. 8.9',drawing_published='yes')
        elif source=='hrp-parpola-2019':
            r.update(season=U,object_type=U,findspot=U,page=str(pages[0]-1),plate_or_figure=U,photo_published=U,drawing_published=U,transcription_published=U)
            note='The page discusses multiple catalogue objects. A position among table rows cannot be mapped independently to a source mention; object-specific fields remain unassessed.'
        elif source=='rakhigarhi-nath':
            r.update(season=U,object_type=U,findspot=U,page='218',plate_or_figure=U,photo_published=U,drawing_published=U,transcription_published=U)
            note='The supplied page lists cakes. No eligible object can be identified at either assigned position.'
        elif source=='gdh-jamison-2017':
            r.update(object_type='seal',page=str(pages[0]),plate_or_figure='Figure 6' if reg=='BSR 5555' else 'Figure 7')
            r['inscription_status']='stated' if reg=='BSR 6719' else U
        elif source=='iar-1996-97-archive':
            r.update(object_type='sealing',page='23',plate_or_figure='pl. IX')
            note+=' The page reports a group, but the supplied position does not select its eligible member.'
        elif source=='iar-1995-96':
            r.update(object_type='sealing',page='18',plate_or_figure='pl. VI',inscription_status='stated')
        elif source=='iar-2003-04-asi':
            if a['row_id']=='PCF-GDH-012':r.update(object_type='seal',page='32;34',plate_or_figure=U,inscription_status='stated')
            elif a['row_id']=='PCF-GDH-013':r.update(object_type='seal',page='38',plate_or_figure='pl. 21',findspot=U,inscription_status='stated')
            elif a['row_id']=='PCF-TKD-001':r.update(object_type='sealing',page='206',plate_or_figure=U)
            elif a['row_id']=='PCF-BHR-003':r.update(object_type=U,page='54;56',plate_or_figure=U,findspot=U)
            else:r.update(object_type=U,page='56',plate_or_figure=U,findspot=U)
        elif source=='iar-2010-11':
            r.update(object_type='seal',page='23;24',plate_or_figure='Pl. 12')
            note+=' The text file spans two printed pages; the ordinal does not identify an individually registered object.'
        elif source=='iar-2004-05':
            r.update(object_type='seal',page='35',plate_or_figure='pl. 13')
        elif source=='surkotada-1990':
            r.update(object_type='inscribed-pottery',page=U,plate_or_figure=U,findspot=U)
            note+=' The ordinal cannot be tied safely to a catalogue entry from these identity fragments.'
        elif source=='man-environment-32':
            r.update(object_type='seal',findspot='Kanpur (Indiranagar mound)',page='120',plate_or_figure=U)
        elif source=='farmana-2006-08':
            r.update(object_type='seal',findspot='East Area 2XD5',page=U,plate_or_figure='')
            note+=' Second seal in the source identity table; printed page not recovered.'
        elif source=='bhr-uesugi-2016':
            r.update(season='2003-04 to 2005-06',object_type='seal',page='4',plate_or_figure='Figure 3')
        r['assessment_note']=note
        evidence.append(r)
    path=OUT/'blind-observations-frozen.csv'
    if path.exists():raise SystemExit('Frozen observations already exist; refusing to replace them.')
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['row_id',*FIELDS,'assessment_note']);w.writeheader();w.writerows(evidence)
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT/'blind-freeze.json').write_text(json.dumps({'file':path.name,'sha256':sha,'rows':len(evidence),'status':'frozen before comparison','unassessed_marker':U,'scope':'Independent page-text assessment; missing page-level evidence is retained, not filled from the object table.','author':'GPT-6 / Codex API harness'},indent=2)+'\n',encoding='utf-8')
    print('Frozen',len(evidence),'records.',sha)

if __name__=='__main__':main()
