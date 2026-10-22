"""Build the reviewed identity table; source text is never copied wholesale."""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('out',type=Path);p.add_argument('raw',type=Path)
a=p.parse_args()
base=a.root/'experiments/2026-10-21-post-catalogue-finds'
rawbase=a.root/'data/raw/2026-10-21-post-catalogue-finds'
def readcsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(name,fields,rows):
    with (a.out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

FIELDS='row_id,site_code,site,site_as_published,country,baseline_volume,baseline_year,excavation,season,registration,other_numbers,findspot,depth_or_layer,period_or_phase,object_type,object_subtype,material,primary_publication,publication_year,page,pdf_page,plate_or_figure,photo_published,drawing_published,transcription_published,other_publications,row_basis,inscription_status,catalogue_status,excavated_before_baseline,possible_duplicate_of,extraction_note,extracted_by'.split(',')
NAMES=dict(zip('KHR KNM SKP GDH NGW PDR BTD KNT JKR KBD NVN SKT DSL RJD LTL DMB JNK PBM PTH NGS KNW RNG PRB'.split(),['Khirsara','Kanmer','Shikarpur','Gola Dhoro (Bagasra)','Nagwada','Padri','Bet Dwarka','Kuntasi','Juni Kuran','Kotada Bhadli','Navinal','Surkotada','Desalpar','Rojdi','Lothal','Daimabad','Juna Khatiya','Pabumath','Pithad','Nageshwar','Kanewal','Rangpur','Prabhas Patan']))
objects=[];merges=[];serial=Counter()
def obj(code,source,page,pdf,kind,**kw):
    serial[code]+=1
    r={f:'' for f in FIELDS}
    r.update(row_id=f'XG-{code}-{serial[code]:03d}',site_code=code,site=NAMES[code],site_as_published=NAMES[code],country='India',baseline_volume='CISI 1',baseline_year='1987',primary_publication=source,page=str(page),pdf_page=str(pdf),object_type=kind,publication_year={'surkotada-1990':'1990','gdh-jamison-2017':'2017','khirsara-2017-held':'2017','shikarpur-2009-held':'2009','puratattva-37':'2007','man-environment-22-23':'1998'}.get(source,source.removeprefix('iar-') if source.startswith('iar-') else '2012'),photo_published='unknown',drawing_published='unknown',transcription_published='unknown',row_basis='individual',inscription_status='stated',catalogue_status='post-catalogue',excavated_before_baseline='unknown',extracted_by='codex gpt-6.1-sol run 2G')
    r.update(kw)
    imprints={'iar-2004-05':'2014','iar-2007-08':'2016','iar-2009-10':'2016','iar-2010-11':'2016','iar-2012-13':'2015'}
    if source.startswith('iar-'):
        r['publication_year']=imprints.get(source,'')
        if not r['publication_year']:r['extraction_note']='; '.join(filter(None,[r['extraction_note'],'Imprint year not established; source ID identifies the issue']))
    objects.append(r);return r['row_id']
def merge(row,source,page,basis):
    r=next(r for r in objects if r['row_id']==row)
    r['other_publications']=';'.join(filter(None,[r['other_publications'],f'{source}:{page}']))
    merges.append(dict(kept_row_id=row,merged_source=source,merged_page=str(page),basis=basis))

# Khirsara: the seasonal total has no registrations or object-specific seasons in the overview.
khr1=obj('KHR','iar-2009-10','25',31,'seal',season='2009-10',object_subtype='bar type',excavation='Excavation Branch V, Archaeological Survey of India',plate_or_figure='pls. 5A-5D',excavated_before_baseline='no')
for i in range(6):
    obj('KHR','iar-2010-11','24',34,'seal',season='2010-11',row_basis='enumerated-count',plate_or_figure='Pl. 12',excavated_before_baseline='no',extraction_note='Seasonal total; materials and forms are not assigned to individual objects')
obj('KHR','khirsara-2017-held','unpaginated',1,'seal',season='2010 & 2013',plate_or_figure='Fig 2H',possible_duplicate_of=khr1,excavated_before_baseline='no',extraction_note='Caption identifies one object; overview does not give its individual season')

# Kanmer: only catalogue entries tied to the script inventories or explicitly scoped groups.
knm=[]
def kn(reg,pg,ctx,phase='KMR IIA',kind='inscribed-pottery',mat='Red Ware',status='uncertain',note='',sub='',trans='yes'):
    source='kanmer-frame-7' if pg in (2,3) else 'kanmer-frame-22' if pg in (4,5,6) else 'kanmer-frame-55'
    knm.append(dict(registration=reg,page=pg,source=source,ctx=ctx,phase=phase,kind=kind,material=mat,status=status,note=note,sub=sub,trans=trans))
kn('09-2060',2,'Tr. AA28; Layer 12','KMR I A',note='Context continues from draft page 1')
kn('06-1253',2,'Tr. Y30; Layer 13','KMR I A',mat='red ware')
kn('08-1928',2,'Tr. Z30; Layer 16','KMR I A',note='Registration repeated on draft page 3 with another context')
kn('06-1217',2,'Tr. Y30; Layer 20','KMR I A')
for reg,ctx in [('09-2047','Tr. Z28; Layer 9'),('08-1948','Tr. Z30; Qua. SW; Layer 10'),('09-2048','Tr. Z28; Layer 10'),('09-2049','Tr. Z28; Layer 10'),('09-2050','Tr. Z28; Qua. SE; Layer 10'),('09-2053','Tr. Z28; Layer 11')]:kn(reg,2,ctx)
for reg,ctx in [('09-2055','Tr. AA28; Layer 9'),('09-2051','Tr. Z28; Layer 10'),('09-2043','Tr. Z28; Layer 8'),('09-2052','Tr. Z28; Layer11'),('08-1283',''),('06-905','Tr. Y30; Layer 16'),('09-2057','Tr. AA28; Layer 12'),('09-2056','Tr. AA28; Qua. SW; Layer 11'),('09-2186','Tr. AA28; Qua. SW; Layer 8')]:kn(reg,3,ctx)
for reg,ctx in [('08-1286','Tr. Z30; Layer 8'),('09-900','Tr. AA28; Qua. SW; Layer 8'),('09-899','Tr. AA28; Qua. SW; Layer 8')]:kn(reg,4,ctx,'KMR II B','sealing','terracotta','stated',sub='seal impression')
kn('06-1054',5,'Tr. GG30; Qua. NE; Layer 8','KMR II B','sealing','clay','stated',sub='broken clay sealing')
kn('09-1996',6,'st. 29I; Tr. X30; Qua. SE; Layer 9','KMR II B','seal','steatite','uncertain',note='Fragment; inscription status requires review',sub='broken seal',trans='no')
for reg,ctx in [('08-1285','Tr. Z30; Qua. NE; Layer 8'),('09-1203','Tr. Z28; Qua. NW; Layer 8'),('08-1950','Tr. AA17; Qua. SW; Layer 4'),('08-1947','')]:kn(reg,6,ctx,'KMR II B',mat='Red ware')
kn('06-168',7,'Tr. Z15; Qua. SW; Layer 2','KMR II B',mat='')
kn('1226',7,'Tr. GG29; Qua. SW; Layer 5','KMR II B',mat='')
kn('09-1878',7,'Tr. AA28; Qua. SW; Layer 9','KMR II B',mat='')
kn('09-2061',7,'Tr. AA28; Qua. NW; Layer 6','KMR II B',mat='')
kn('08-202',8,'Tr. Z16; Layer 1','KMR II B',mat='')
kn('',8,'Tr. Z17; Qua. NE; Layer 3','KMR II B',mat='',note='Draft item 14; registration not recovered from the text witness')
kn('09-1995',8,'Tr. Q27; Layer 4','KMR III','seal','faience','uncertain',note='Publication compares the object with script-bearing examples',sub='rectangular seal')
kn('808',9,'Tr. Y12; Layer 4','KMR III','other','Red ware','uncertain',note='Draft item 8; object class requires review')
for d in knm:
    # Keep the printed depth/context components distinct.
    parts=d['ctx'].split('; ')
    layer='; '.join(x for x in parts if x.startswith('Layer'))
    find='; '.join(x for x in parts if not x.startswith('Layer'))
    rid=obj('KNM',d['source'],d['page'],d['page'],d['kind'],registration=d['registration'],findspot=find,depth_or_layer=layer,period_or_phase=d['phase'],material=d['material'],inscription_status=d['status'],object_subtype=d['sub'],transcription_published=d['trans'],season='2005-06–2008-09',excavated_before_baseline='no',extraction_note=d['note'])
    if d['registration']=='08-1928':
        merge(rid,'kanmer-frame-7','3','Same registration; draft gives a second context, retained in the note')
        objects[-1]['extraction_note']='Registration repeats on draft page 3: Tr. Z30, Qua. NW, Layer 13; context conflict retained'

# Shikarpur: two early pottery objects, then separate excavation seasons.
for i in range(2):obj('SKP','iar-1987-88','15',23,'inscribed-pottery',season='1987-88',row_basis='enumerated-count',excavated_before_baseline='no',extraction_note='Two objects reported together; registrations not printed')
obj('SKP','iar-2007-08','61',67,'sealing',season='2007-08',material='terracotta',findspot='trench Fp1',period_or_phase='Phase I',depth_or_layer='uppermost deposit',excavated_before_baseline='no')
for fig in ('fig 4d','fig.4c'):
    rid=obj('SKP','shikarpur-2009-held','4',4,'sealing',season='2008-09',material='terracotta',period_or_phase='Phase-I',plate_or_figure=fig,excavated_before_baseline='no',transcription_published='no')
    merge(rid,'skp-report-2009','4','Same publication and figure; second held PDF witness')
rid=obj('SKP','shikarpur-2009-held','4-5',4,'tablet',season='2008-09',material='terracotta',findspot='trench Fk13',period_or_phase='beginning of Phase II',object_subtype='square tablet',plate_or_figure='fig.4a',excavated_before_baseline='no',transcription_published='no')
merge(rid,'skp-report-2009','4-5','Same publication, trench and figure; second held PDF witness')
obj('SKP','iar-2012-13','31',37,'seal',season='2012-13',material='steatite',object_subtype='square',plate_or_figure='pl.32',excavated_before_baseline='no')

# Gola Dhoro: early sealings are outside the seasons/classes itemised in the seal study.
obj('GDH','iar-1995-96','18',26,'sealing',site_as_published='Bagasra',season='1995-96',material='terracotta',plate_or_figure='pl.VIA',excavated_before_baseline='no')
for i in range(2):obj('GDH','iar-1995-96','18',26,'sealing',site_as_published='Bagasra',season='1995-96',row_basis='enumerated-count',inscription_status='uncertain',excavated_before_baseline='no',extraction_note='Two additional stamped clay objects; script status is open')
gdh=[('BSR 2037',8,'1998','Trench El 15','3','100','Figure 5'),('BSR 5555',9,'2003','Trench Eg 2','10','300','Figure 6'),('BSR 6719',10,'2004','Trench Eo 11; Appendix 1: El 15','n/a','66','Figure 7'),('BSR 6952',11,'2004','western baulk of Trench Ea 12','5','70‐75','Figures 8–9'),('BSR 7197',11,'2004','Trench Eh 1','1','26','Figure 10'),('BSR 7368',12,'2004','Trench Eh 1','Pit 1','223','Figures 11–13'),('BSR 8288',14,'2004','Trench Ei 14; Appendix 1: El 14','4','105','Figure 14')]
for reg,pg,season,find,layer,depth,fig in gdh:
    note='Context also listed in Appendix 1, p.15'
    if reg in ('BSR 6719','BSR 8288'):note='Trench differs between object entry and Appendix 1'
    obj('GDH','gdh-jamison-2017',pg,pg,'seal',site_as_published='Bagasra',season=season,registration=reg,findspot=find,depth_or_layer=f'Layer {layer}; {depth} (Depth (Cm Below Datum))',material='steatite',plate_or_figure=fig,excavated_before_baseline='no',extraction_note=note)

obj('NGW','iar-1987-88','20',28,'sealing',season='1987-88',material='clay',excavation='Department of Archaeology and Ancient History, M.S. University of Baroda',excavated_before_baseline='no')
for fig,find,status in [('Fig. 3','intertidal zone','uncertain'),('Fig. 4','onshore explorations','stated')]:
    obj('BTD','man-environment-22-23','79',315,'inscribed-pottery',site_as_published='Bet Dwarka',season='1981 to 1995',findspot=find,plate_or_figure=fig,inscription_status=status,transcription_published='yes',excavated_before_baseline='unknown',extraction_note='Article discusses the attribution; individual recovery year not printed')
obj('JKR','iar-2004-05','35',40,'seal',site_as_published='Juni-Kuran',season='2004-05',material='steatite',object_subtype='broken',findspot='Trench Y-17',plate_or_figure='pl.13',excavated_before_baseline='no')

# Surkotada, chapter 9, in catalogue order.
for mat,phase,level in [('Steatite','Period I A','late level'),('Terracotta','Period I C','early level')]:
    obj('SKT','surkotada-1990','361',382,'seal',season='1971-72',registration='SKTD-1730',material=mat,object_subtype='square seal',period_or_phase=phase,depth_or_layer=level,plate_or_figure='Pl. LXXIX',photo_published='yes',drawing_published='no',transcription_published='yes',excavated_before_baseline='yes',extraction_note='Same registration printed for objects of different material and phase; kept separately')
paint=[('late','I A','jar','yes'),('late','I A','jar','yes'),('late','I A','jar','no'),('mid','I A','jar','yes'),('mid','I A','jar','no'),('late','I A','jar','yes'),('mid','I C','jar','yes'),('late','I A','shallow dish','yes'),('late','I A','shallow dish','yes'),('mid','I C','jar','yes'),('mid','I A','jar','yes'),('mid','I A','jar','no'),('','I A','dish','no'),('mid','I C','dish','no')]
for n,(level,phase,sub,tr) in enumerate(paint,1):
    obj('SKT','surkotada-1990','361' if n<=4 else '362',382 if n<=4 else 383,'inscribed-pottery',season='1971-72',other_numbers=f'Catalogue ii.{n}',object_subtype=sub,material='Harappan red ware' if n!=13 else '',depth_or_layer=f'{level}-level' if level=='mid' else f'{level} level' if level else 'a level',period_or_phase=f'Period {phase}',plate_or_figure='Fig. 84; Pl. LXXX',photo_published='yes',drawing_published='yes',transcription_published=tr,excavated_before_baseline='yes')
for n,sub in enumerate(['perforated jar',"S shaped jar",'dish'],1):
    obj('SKT','surkotada-1990','362',383,'inscribed-pottery',season='1971-72',other_numbers=f'Catalogue iii.A.{n}',object_subtype=sub,material='Harappan red ware' if n>1 else '',period_or_phase='Period I A' if n==3 else '',depth_or_layer='late level' if n==3 else '',plate_or_figure='Fig. 85A; Pl. LXXXI',photo_published='yes',drawing_published='yes',transcription_published='yes' if n<3 else 'no',excavated_before_baseline='yes')
for n in range(1,7):
    obj('SKT','surkotada-1990','363',384,'inscribed-pottery',season='1971-72',other_numbers=f'Catalogue iii.B.{n}',object_subtype='round open basin' if n<=2 else 'jar',material='Harappan red ware',period_or_phase='Period I C',depth_or_layer='mid-level' if n!=2 else '',plate_or_figure='Fig. 85B; Pl. LXXXII',photo_published='yes',drawing_published='yes',transcription_published='yes' if n==1 else 'no',excavated_before_baseline='yes')

for kind,mat in [('seal','steatite'),('seal','copper'),('sealing','terracotta')]:obj('DSL','puratattva-37','61',65,kind,site_as_published='Desalpar',season='1963-64',material=mat,row_basis='enumerated-count',excavated_before_baseline='yes',extraction_note='Historical excavation summary; later run checks catalogue containment')

BEST={'KHR':'iar-2010-11; khirsara-2017-held','KNM':'Kanmer chapter 8 draft: kanmer-frame-7; kanmer-frame-22; kanmer-frame-55','SKP':'shikarpur-2009-held','GDH':'gdh-jamison-2017','NGW':'iar-1987-88','BTD':'man-environment-22-23','JKR':'iar-2004-05','SKT':'surkotada-1990','DSL':'puratattva-37'}
COUNTS={
'KHR':'seal=6 (iar-2010-11 p.24; season 2010-11); these produce seasonal rows; overview illustrations may overlap',
'KNM':'seal=5; seal-impression=3; sealing=1; stamped-pottery=1 (kanmer-frame-55 draft p.1); includes classes excluded by the scope rule; only the script-related catalogue entries are rows',
'SKP':'pottery=2 (iar-1987-88 p.15); sealing>=5 (skp-report-2008 p.5); sealing=2 and tablet=1 (shikarpur-2009-held pp.3-5); seal=1 (iar-2012-13 p.31)',
'GDH':'seal=6 (gdh-bhan-2005 leaf 1); itemised seal=7 (gdh-jamison-2017 pp.8-14); reported totals differ by one; sealing=1 and additional clay objects=2 (iar-1995-96 p.18)',
'NGW':'sealing=1 (iar-1987-88 p.20); sealing=1 (man-environment-17 p.8 and puratattva-37 p.67), treated as programme summaries',
'BTD':'inscribed pottery=2 (man-environment-22-23 p.79)',
'RJD':'inscribed pottery=1 historical summary (puratattva-37 p.70); earlier than CISI 3.2 and therefore notes only; uncounted Harappan graffiti (iar-1992-93 p.32)',
'SKT':'seal=2; painted pottery=14; incised pottery=9 (surkotada-1990 p.359); agrees with 25 itemised rows',
'DSL':'seal=2; sealing=1 (puratattva-37 p.61)'}
MARKS={
'KNM':'graffiti pottery=7 (kanmer-frame-55 draft p.1, KMR I A); entries without an individual script attribution remain outside rows; later unqualified pottery marks and shell pieces also excluded',
'SKP':'sealing>=5 (skp-report-2008 p.5): the report does not attribute script to each object; one corresponding scripted example is recorded from iar-2007-08 p.61; geometric steatite tablet excluded',
'PDR':'terracotta button seal=1 (iar-1991-92 p.21; man-environment-17 p.211), excluded by the button-seal rule',
'BTD':'conch-shell seal=1 (man-environment-22-23 p.79; btd-gaur-2002 p.1353): no inscription attributed to that object; excluded',
'KNT':'faience seal=1 (puratattva-37 p.63): no explicit script attribution in the summary',
'RNG':'round steatite seal=1 (man-environment-16 pp.51-54): publication explicitly says no script',
'KHR':'uncounted pottery marks (iar-2011-12 p.10); geometric button seal (iar-2012-13 p.30), excluded',
'KBD':'ceramic decoration in iar-2011-12; no explicit Indus script attribution found',
'LTL':'rectangular terracotta Harappan seal=1 (iar-1988-89 p.115), a museum acquisition with no explicit script attribution'}
GROUPS={
'KHR':'Square, rectangular and bar seals described collectively (khirsara-2017-held leaf 1); no total assigned to that passage',
'GDH':'Inscribed black-slipped jars without a count (ngw-sonawane-2018 p.260); sealings without a count (gdh-bhan-2005 leaf 1; iar-1997-98 p.32)',
'KNM':'Uncounted script-related pottery in the chapter introduction; rows are limited to identifiable catalogue entries',
'RJD':'Harappan graffiti without a count in pre-2019 sources; no object rows under Amendment 1'}
UNREAD={
'KHR':'Nath and Kumaran 2012, Inscribed Material from Khirsara, Itihas Darpan 17(2):235-242: cited in khr-nath-2014 but article not held; Excavations at Khirsara, Puratattva 42 pp.122-132: contents only held',
'KBD':'Excavations at Kotada Bhadli, Puratattva 42 pp.182-201: contents only held',
'KNT':'Kuntasi final excavation monograph not among the supplied readable sources',
'NGW':'Excavation at Nagwada-1986 and 1987, Man and Environment: cited by ngw-sonawane-2018; article body not located in the supplied volumes'}
NOTES={
'KHR':'The 2017 caption supplies no individual season or registration; its row may overlap a seasonal object. The 2014 papers are specialist context studies.',
'KNM':'Draft pagination is used; source IDs refer to the registered acquisition records and their retained text witnesses. The two shell button objects and the explicitly named steatite button seal 09-1997 are excluded by the button-seal rule. Comparative script attributions are uncertain rows. A repeated registration is merged with its context conflict recorded. No signs or inventory numbers are retained.',
'SKP':'Several impressions on each sealing remain one object. The 2008 report has no script attribution for its full sealing total; the IAR identifies one scripted example in that season.',
'GDH':'The seven-seal study covers 1998, 2003 and 2004; overlapping seasonal seal totals add no anonymous rows. The earlier sealing season is recorded separately. Appendix 1 conflicts with two entry findspots.',
'PDR':'Held reports discuss a later-period tablet and a Harappan button seal; neither yields a row under the stated scope.',
'JKR':'Broken seal mentioned twice on the same page is one object.',
'JNK':'The assigned 2021 witness is a general discussion, not a Juna Khatiya object catalogue; no qualifying object found.',
'LTL':'Museum acquisition and historical summaries do not explicitly attribute script to a distinct post-baseline object in the pages screened.',
'RJD':'All located object statements predate 2019; Amendment 1 suppresses rows.',
'DMB':'Located mentions are historical or bibliographic; no qualifying later object identified.',
'PBM':'Historical mentions and bibliography only in the held candidates.',
'PTH':'Pithad is also Jaidak; the 2010 paper is a specialist context study.',
'NGS':'Located passages concern shell production or bibliography; no qualifying script object identified.',
'KNW':'Located passages concern ceramics or bibliography; no qualifying script object identified.',
'PRB':'Located entries concern archaeology of later periods and survey context; no qualifying script object identified.',
'NVN':'No object-bearing entry located in the supplied candidates.',
'KBD':'The IAR entry is readable; the cited journal catalogue body is not held.'}
SEASONS={'KHR':'2009-10:iar-2009-10; 2010-11:iar-2010-11; 2011-12:iar-2011-12; 2010-2013:khirsara-2017-held overview','KNM':'2005-06–2008-09:Kanmer chapter 8 draft; kanmer-ch6 is the pottery chapter','SKP':'1987-88:iar-1987-88; 1988-89:iar-1988-89; 2007-08:skp-report-2008 and iar-2007-08; 2008-09:shikarpur-2009-held; 2012-13:iar-2012-13','GDH':'1995-96:iar-1995-96; 1998,2003,2004:gdh-jamison-2017; 1996-2005:ngw-sonawane-2018 overview','NGW':'1987-88:iar-1987-88; 1985-1989:ngw-sonawane-2018 overview','BTD':'1981-1995:man-environment-22-23','JKR':'2004-05:iar-2004-05','SKT':'1971-72:surkotada-1990','DSL':'1963-64:puratattva-37 historical summary','PTH':'1991-92:iar-1991-92; 2005-06 and 2006-07:man-environment-35 specialist study'}

def ranges(values):
    nums=sorted(set(map(int,values)));out=[]
    for x in nums:
        if out and x==out[-1][-1]+1:out[-1].append(x)
        else:out.append([x])
    return ','.join(str(v[0]) if len(v)==1 else f'{v[0]}-{v[-1]}' for v in out)
readpages=readcsv(a.out/'pages-read-G.csv')
readset={(r['source_id'],int(r['pdf_page'])) for r in readpages}
sitepages=defaultdict(lambda:defaultdict(set))
for r in readcsv(base/'acquisition/candidate-pages-1a.csv'):
    if r['site_code'] in NAMES and (r['source_id'],int(r['pdf_page'])) in readset:sitepages[r['site_code']][r['source_id']].add(r['pdf_page'])
for name in ('scan-G.csv','extra-candidates-G.csv'):
    if not (a.out/name).exists():continue
    for r in readcsv(a.out/name):
        for c in r.get('site_codes','').split(';'):
            if c in NAMES and (r['source_id'],int(r['pdf_page'])) in readset:sitepages[c][r['source_id']].add(r['pdf_page'])
for r in objects:sitepages[r['site_code']][r['primary_publication']].add(r['pdf_page'])
if (a.out/'dholavira-pages-noted-G.csv').exists():
    dhopages=defaultdict(set)
    for r in readcsv(a.out/'dholavira-pages-noted-G.csv'):dhopages[r['source_id']].add(r['pdf_page'])
    NOTES['SKT']='Dholavira pages encountered during the text screen, excluded from rows: '+ '; '.join(f'{s}:PDF {ranges(ns)}' for s,ns in sorted(dhopages.items()))
SITEFIELDS='site_code,site,sources_read,best_publication,rows_individual,rows_enumerated,rows_uncertain_status,rows_possibly_in_cisi3,season_blocks,count_statements,marks_outside_scope,groups_without_count,unread_sources,notes'.split(',')
sites=[]
for c,name in NAMES.items():
    rs=[r for r in objects if r['site_code']==c]
    sites.append(dict(site_code=c,site=name,sources_read='; '.join(f'{s}:PDF {ranges(ns)}' for s,ns in sorted(sitepages[c].items())),best_publication=BEST.get(c,'none identified in held candidates'),rows_individual=sum(r['row_basis']=='individual' for r in rs),rows_enumerated=sum(r['row_basis']=='enumerated-count' for r in rs),rows_uncertain_status=sum(r['inscription_status']=='uncertain' for r in rs),rows_possibly_in_cisi3=sum(r['catalogue_status']=='possibly-in-cisi3' for r in rs),season_blocks=SEASONS.get(c,''),count_statements=COUNTS.get(c,''),marks_outside_scope=MARKS.get(c,''),groups_without_count=GROUPS.get(c,''),unread_sources=UNREAD.get(c,''),notes=NOTES.get(c,'No qualifying object found in the supplied candidate pages.')))

writecsv('objects-G.csv',FIELDS,objects)
writecsv('site-notes-G.csv',SITEFIELDS,sites)
writecsv('merge-log-G.csv',['kept_row_id','merged_source','merged_page','basis'],merges)
expo=[]
for s in sorted({r['source_id'] for r in readpages}):
    ns=[r['pdf_page'] for r in readpages if r['source_id']==s]
    access='automated keyword screen; filtered identity and scope review on candidate pages'
    if (a.raw/'text'/s).exists():access+='; local text extraction'
    if s=='surkotada-1990' or s=='btd-gaur-2002':access+='; English OCR repair'
    expo.append(dict(source_id=s,agent='codex gpt-6.1-sol run 2G',access=access,pages=ranges(ns),purpose='Locate qualifying physical objects and record identity fields; no image viewed by agent'))
writecsv('exposure-log-G.csv',['source_id','agent','access','pages','purpose'],expo)

summary=['We extracted '+str(len(objects))+' object rows. The table gives the independent count in each required category; categories can overlap.','', '| Site | individual / enumerated-count | stated / uncertain | post-catalogue / possibly-in-cisi3 | Best publication |','|---|---:|---:|---:|---|']
for s in sites:
    rs=[r for r in objects if r['site_code']==s['site_code']]
    summary.append(f"| {s['site_code']} {s['site']} | {s['rows_individual']} / {s['rows_enumerated']} | {sum(r['inscription_status']=='stated' for r in rs)} / {s['rows_uncertain_status']} | {sum(r['catalogue_status']=='post-catalogue' for r in rs)} / {s['rows_possibly_in_cisi3']} | {s['best_publication']} |")
summary+=['','Count differences: Gola Dhoro has six seals in gdh-bhan-2005 and seven individually listed in gdh-jamison-2017. Shikarpur has at least five sealings in skp-report-2008, while only one is explicitly linked to script in the seasonal IAR entry. The Kanmer total of five seals includes excluded button objects; comparative pottery attributions remain uncertain. Khirsara has six anonymous seasonal rows and a later illustration that may duplicate an earlier row. These totals have different coverage; site notes retain their locators.','','Unread sources: '+ '; '.join(f'{c}: {v}' for c,v in UNREAD.items())+'.','','Screened new-site leads: Umta and Siyot concern later-period remains; no qualifying Indus object was identified. Shaktari Timbo at Moti Pipli remains a screened ceramic-context lead. No new site code was assigned because no additional qualifying object was established.','','Deviations and access limits: the initial text filters admitted descriptive source passages into tool output, including portions of the Bagasra study beyond identity fields. The exposure log records those pages. Only identity fields are retained in the deliverables. Full page text is retained locally as expressly requested for 1B extraction. Source pages were screened computationally and reviewed through filtered text; no page image was visually opened. Kanmer chapter 8 uses the registered earlier-package witnesses because the held preview contains no chapter body. The coordinator interrupted the run for disk capacity; saved tables were checked and OCR renders removed before continuation. No downloads were made after resumption.','','Validation: see selftest-G.json, generated by selftest-G.py.','','Outputs: objects-G.csv; site-notes-G.csv; merge-log-G.csv; pages-read-G.csv; exposure-log-G.csv; selftest-G.json; final.md. Scripts and access metadata are in experiments/2026-10-21-post-catalogue-finds/extraction/G/. Local page text is in data/raw/2026-10-21-post-catalogue-finds/run2G/text/.']
(a.out/'final.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
print(json.dumps({'rows':len(objects),'sites':len(sites),'merges':len(merges),'by_site':dict(Counter(r['site_code'] for r in objects))}))
