"""Write reviewed run 2N object metadata and site notes. Run with python -I."""
import collections
import csv
import json
import runpy
from pathlib import Path

M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
OUT=M['OUT']; SITES=M['SITES'].copy()
SITES.update(ATR='Atranjikhera',LLQ='Lal Qila',GNS='Ganeshwar',IDN='Indiranagar (Kanpur)')
COLS='row_id site_code site site_as_published country baseline_volume baseline_year excavation season registration other_numbers findspot depth_or_layer period_or_phase object_type object_subtype material primary_publication publication_year page pdf_page plate_or_figure photo_published drawing_published transcription_published other_publications row_basis inscription_status catalogue_status excavated_before_baseline possible_duplicate_of extraction_note extracted_by'.split()
objects=[]; merges=[]

def add(code,source,year,pdf,page='',**kw):
    n=1+sum(r['site_code']==code for r in objects)
    r=dict.fromkeys(COLS,'')
    r.update(row_id=f'XN-{code}-{n:03}',site_code=code,site=SITES[code],site_as_published=SITES[code],country='India',baseline_volume='CISI 1',baseline_year='1987',primary_publication=source,publication_year=str(year),pdf_page=str(pdf),page=str(page),photo_published='unknown',drawing_published='unknown',transcription_published='unknown',row_basis='individual',inscription_status='stated',catalogue_status='post-catalogue',excavated_before_baseline='no',extracted_by=M['AGENT'])
    r.update(kw);objects.append(r);return r

def merge(row,source,page,basis):
    entry=f'{source}:{page}'
    row['other_publications']='; '.join(filter(None,[row['other_publications'],entry]))
    merges.append(dict(kept_row_id=row['row_id'],merged_source=source,merged_page=str(page),basis=basis))

# The report's unnumbered comparisons refer to separate physical specimens.
for item,trench in [('4','U 18/1'),('6','H-7/2')]:
    add('RGR','rakhigarhi-nath',2014,218,218,excavation='Archaeological Survey of India',season='1997-98 to 1999-2000',other_numbers=f'Terracotta Cake, item {item}',findspot=f'RGR-1 (trench {trench})',period_or_phase='Mature Harappan level',object_type='other',object_subtype='cake',material='terracotta',inscription_status='uncertain',transcription_published='no',extraction_note='script comparison is qualified')
lead=add('RGR','rakhigarhi-nath',2014,219,219,excavation='Archaeological Survey of India',season='1997-98 to 1999-2000',findspot='RGR-2 (trench Q-19/4)',period_or_phase='Mature Harappan level',object_type='other',material='lead',inscription_status='stated',plate_or_figure='Plate 5; Figure 14',transcription_published='no',extraction_note='appendices identify an inscribed ingot from the same mound')
merge(lead,'rakhigarhi-nath','352,378-379','same excavation, mound RGR-2, material and inscribed lead object; no conflicting identifier')
merge(lead,'puratattva-29','49','same inscribed lead ingot, mound and excavation; preliminary season report')
lead['season']='1998-99'
for num,status,trans in [('1','uncertain','no'),('2','stated','yes')]:
    add('RGR','rakhigarhi-nath',2014,219,219,excavation='Archaeological Survey of India',season='1997-98 to 1999-2000',other_numbers=f'Bone, specimen {num}',findspot='RGR -2 (trench Y 24/4)',period_or_phase='Mature Harappan level',object_type='other',material='bone',inscription_status=status,transcription_published=trans,extraction_note='listed in graffiti chapter')
add('RGR','puratattva-28',1998,57,45,excavation='Archaeological Survey of India',season='1997-98',findspot='RGR 2',object_type='seal',object_subtype='cylindrical',material='faience',transcription_published='no',extraction_note='plate citation partly illegible')
add('RGR','rakhigarhi-inventory-held',1998,53,site_as_published='Rakhigarhi (Rakhikhas & Rakhishahpur)',object_type='seal',object_subtype='cylindrical',transcription_published='no',excavated_before_baseline='unknown',possible_duplicate_of='XN-RGR-006',extraction_note='recent-excavation reference; season and field number unspecified')

farm=[]
for n,area,trench,phase in [(1,'North Area','2','4'),(2,'East Area','2XD5','4'),(3,'Central Area','1H8','4'),(4,'Central Area','1B6','5')]:
    r=add('FRM','farmana-2006-08',2011,385,371,season='2006-07 to 2008-09',other_numbers=f'S-{n}',findspot=f'{area}; Trench {trench}',period_or_phase=phase,object_type='seal',object_subtype='square',material='steatite',plate_or_figure='Table 7.2; Figures 7.2, 7.4-7.8',photo_published='yes',drawing_published='yes',transcription_published='no',extraction_note='phase from Table 7.2; prose assigns S-3 to Phase 5' if n==3 else 'listed in Table 7.2')
    farm.append(r)
r=add('FRM','farmana-2006-08',2011,399,385,season='2006-07 to 2008-09',other_numbers='S-5',findspot='North Area; Trench 3',period_or_phase='4',object_type='sealing',material='terracotta',plate_or_figure='Table 7.3; Figures 7.3, 7.4, 7.16',photo_published='yes',drawing_published='yes',transcription_published='no',extraction_note='listed in Table 7.3')
farm.append(r)
# Earlier report locates the partially preserved seal by a distinct house context;
# the final report and IAR also identify the first-season seal and sealing.
merge(farm[0],'farmana-2007-08-report','100-103','first-season seal; Trench 2 structure context; subsequent excavation report')
merge(farm[4],'farmana-2007-08-report','103,105','first-season sealing; same season, object class and excavation context')
merge(farm[0],'iar-2006-07','35','same first-season structure and object class')
merge(farm[4],'iar-2006-07','35','same first-season sealing cohort')
add('FRM','farmana-2007-08-report',2008,115,103,season='2007-08',findspot='St. no. 3H',object_type='seal',object_subtype='square',material='steatite',plate_or_figure='Fig. 106',photo_published='yes',drawing_published='yes',transcription_published='no',possible_duplicate_of=farm[3]['row_id'],extraction_note='possible reuse in final report; structure-to-trench crosswalk absent')

for n in range(3):
    r=add('BHR','puratattva-35-held',2005,79,65,season='2004-05',period_or_phase='Mature Harappan',object_type='seal',material='steatite',row_basis='enumerated-count',transcription_published='no',extraction_note='reported total less explicitly uninscribed specimen; no individual identifiers')
    merge(r,'iar-2004-05','49-51','same season and excavation cohort; no separate individual identifiers')
add('BHR','puratattva-36',2006,63,season='2005-06',period_or_phase='Period IIB',object_type='seal',object_subtype='broken rectangular',material='steatite',transcription_published='no',extraction_note='individual excavation find')
merge(objects[-1],'iar-2005-06','24','same season, period, material and partially preserved seal')
r=add('BHR','bhr-uesugi-2016',2016,4,4,excavation='surface collection',findspot='surface collection',object_type='seal',object_subtype='square',material='steatite',plate_or_figure='Figure 2',photo_published='yes',transcription_published='no',excavated_before_baseline='unknown',extraction_note='held by a local collector; collection year not established')
merge(r,'man-environment-36','219-220','same collector-held surface object; cited earlier publication')

for n in range(1,4):
    add('RPR','iar-2011-12',2016,80,74,site_as_published='Rupnagar or Rupar',excavation='Archaeological Survey of India, Excavation Branch II',season='2011-12',other_numbers=f'sherd {n}',object_type='inscribed-pottery',plate_or_figure='Pl. 30A-B',photo_published='yes',transcription_published='no',extraction_note='individually described in excavation entry')
add('RPR','iar-2011-12',2016,80,74,site_as_published='Rupnagar or Rupar',excavation='Archaeological Survey of India, Excavation Branch II',season='2011-12',object_type='inscribed-pottery',object_subtype='chakla',plate_or_figure='Pl. 30A-B',photo_published='unknown',transcription_published='no',inscription_status='uncertain',extraction_note='publication leaves inscription status open')

for n,trench,context,plate in [(1,'S170E40','house complex','Pl. 44'),(2,'S10E120 III','street deposit','Pl. 45')]:
    add('KRP','iar-2013-14',2016,122,117,excavation='Archaeological Survey of India',season='2013-14',other_numbers=f'seal {n}',findspot=f'trench {trench}; {context}',object_type='seal',material='steatite',plate_or_figure=plate,photo_published='yes',transcription_published='no',extraction_note='joined fragments form one object' if n==2 else 'individual excavation find')

r=add('BRR','puratattva-35-held',2005,68,54,season='2003-2004 and 2004-2005',period_or_phase='Mature Harappan',object_type='seal',object_subtype='square',material='steatite',plate_or_figure='Pl. 22',photo_published='yes',transcription_published='no',extraction_note='report covers two field seasons; individual season unspecified')

for reg,layer,otype,plate in [('119','4','seal','Pl. XLIX, A-B'),('247','1','sealing','Pl. L')]:
    r=add('TKD','tarkhanewala-2009',2009,140,118,site_as_published='Tarkhanewala-Dera',season='2003-2004',registration=reg,depth_or_layer=layer,object_type=otype,material='terracotta',plate_or_figure=plate,photo_published='yes',drawing_published='no',transcription_published='no')
    if otype=='sealing':
        merge(r,'puratattva-36-held','29','same 2003-2004 excavation, context and inscribed sealing; held issue is number 34')

add('MTL','man-environment-35',2010,61,57,excavation='surface reconnaissance',season='March of 2007',findspot='southern slope of Mound 2 not far from the canal',object_type='seal',object_subtype='rectangular',material='steatite',plate_or_figure='Fig. 6',photo_published='unknown',drawing_published='unknown',transcription_published='no')
add('HUL','new-hulas-report',2020,219,207,excavation='Archaeological Survey of India',season='1978-1983',registration='990',findspot='unstratified deposit',object_type='sealing',material='terracotta',plate_or_figure='Pl. 1',photo_published='yes',transcription_published='yes',excavated_before_baseline='yes',extraction_note='Appendix I; source prints a reading')
add('DHL','new-dhalewan-report',2018,285,season='1999-2000 & 2001-2002',registration='726',period_or_phase='Period lB. (Transition Period)',object_type='inscribed-pottery',object_subtype='fragment of a rim of a basin',plate_or_figure='Fig. 5.58; Pl. 5.19',photo_published='yes',drawing_published='yes',transcription_published='yes',inscription_status='uncertain',extraction_note='publication compares more than one script tradition')
add('DHL','new-dhalewan-report',2018,293,season='1999-2000 & 2001-2002',registration='1371',period_or_phase='Phase II of PeriodIC',object_type='seal',object_subtype='rectangular',material='grey-terracotta',plate_or_figure='Pl. 6.1',photo_published='yes',transcription_published='yes')
add('DHL','new-dhalewan-report',2018,297,season='1999-2000 & 2001-2002',registration='890',period_or_phase='Phase II of Period IC',object_type='sealing',material='clay',plate_or_figure='Pl. 6.3',photo_published='yes',transcription_published='no',extraction_note='registration 84 is excluded as uninscribed')
add('IDN','man-environment-32',2007,124,120,site_as_published='Kanpur (Indiranagar mound)',object_type='seal',object_subtype='square',inscription_status='uncertain',transcription_published='no',excavated_before_baseline='unknown',extraction_note='site attribution and script affiliation unresolved in review')

INFO={
'RGR':dict(best='rakhigarhi-nath; puratattva-28',seasons='1997-98: puratattva-28; 1998-99: puratattva-29; 1999-2000: puratattva-31; 1997-98 to 1999-2000: rakhigarhi-nath',counts='cylindrical seal=1; amulet=2 (puratattva-28 p.45); inscribed lead ingot=1 (puratattva-29 p.49)',marks='graffiti=163 pottery entries (rakhigarhi-nath pp.208-217); script-qualified subset has no total',groups='inscribed seals, no total (rakhigarhi-nath p.107; puratattva-28 p.45); inscribed pottery, no total (puratattva-31 p.44; rakhigarhi-nath pp.206-207,221)',notes='Nath draft dated 31 December 2014 lacks a seal catalogue and an itemised amulet inventory. rakhigarhi-inventory-held is Inventory of Monuments and Sites, Chandigarh Circle, 1998, a different work. Its cylindrical-seal entry is a possible duplicate: 6-7 physical objects in the rows. The lead comparison is stated as an inscription in the scientific appendices and the earlier season report. The amulet pair remains a count statement because Nath covers those seasons under Amendment 1.'),
'FRM':dict(best='farmana-2006-08',seasons='2006-07 to 2008-09: farmana-2006-08; 2007-08: farmana-2007-08-report',counts='seal=4; objects with seal impressions=2 (farmana-2006-08 p.371); seal=2; objects with seal impressions=2 (farmana-2007-08-report p.100)',marks='post-firing graffiti=29, including Harappan pottery=10 (farmana-2006-08 p.219); script status not established for these sherds',groups='possible script-bearing potsherds in St. no.3H, no count (farmana-2007-08-report p.40)',unread='farmana-necropolis: held unpaged OCR has no usable Latin text; intended report cannot be reviewed from it',notes='Five eligible objects from the final report plus one unresolved preliminary-report duplicate: 5-6 physical objects. S-6 has no stated surviving inscription and is excluded. The preliminary report covers fewer seasons, so its seal total is not a conflict. S-3 has conflicting phase assignments in Table 7.2 and prose p.384. The later seal studies cover the same four seals and yield no additional objects; their serial-number crosswalk is left unresolved.'),
'BHR':dict(best='puratattva-35-held; puratattva-36; bhr-uesugi-2016',seasons='2003-04: puratattva-36-held (actually issue 34); 2004-05: puratattva-35-held; 2005-06: puratattva-36; surface collection: bhr-uesugi-2016',counts='seal=4 (puratattva-35-held pp.64-65; iar-2004-05 pp.49-51); only 3 are described as inscribed; seal=1 (puratattva-36 PDF p.63); surface seal=1 (bhr-uesugi-2016 pp.3-4)',marks='unquantified pottery graffiti (puratattva-36-held PDF p.33)',unread='bhr-rao-2008: held four-page PDF is journal contents; article text absent',notes='The four-seal total includes one explicitly uninscribed object. The 2016 study illustrates the same excavation cohort and a separate collector-held surface object. No extra rows are made from those cohort references. The contents-only 2008 source identifies a further lead without readable object evidence.'),
'SNL':dict(best='puratattva-36; puratattva-36-held',seasons='2004-05: puratattva-36-held (actually issue 34); 2005-06: puratattva-36',unread='snl-prabhakar-2013: held 17-page PDF is an ornaments article; intended source absent from both source registers',notes='No eligible object established in the excavation entries reviewed. The held file identifier is retained in the text manifest and exposure records.'),
'RPR':dict(best='iar-2011-12',seasons='2011-12: iar-2011-12',counts='inscribed pottery sherd=3; possible inscribed chakla=1 (iar-2011-12 p.74)',notes='The three sherds are individually discussed; the chakla remains uncertain.'),
'KRP':dict(best='iar-2013-14',seasons='2012-13: iar-2012-13; 2013-14: iar-2013-14',counts='seal=2 (iar-2013-14 pp.114,117)',marks='graffiti=157 (iar-2013-14 p.120); total mixes script-qualified and other marks',groups='script-qualified pottery graffiti subset, no count (iar-2013-14 p.120)',unread='krp-preliminary-report: three-page PDF contains journal contents only',notes='The second seal was recovered in joining fragments. A spindle-whorl group is not explicitly script-qualified.'),
'BJR':dict(best='binjor2017-held; bjr-manjul-2017',notes='Both held nine-page sources are the metal-craft study. Their text establishes no eligible inscribed object. Later excavation seal inventories are not held in the assigned source set.'),
'BRR':dict(best='puratattva-35-held',seasons='2003-04 and 2004-05: puratattva-35-held; 2005-06: iar-2005-06',counts='inscribed seal=1 (puratattva-35-held p.54)',notes='Other seals in the report do not meet the inscription rule. IAR and journal wording differ on shape; no identity merge is asserted.'),
'TKD':dict(best='tarkhanewala-2009',seasons='2003-2004: tarkhanewala-2009',counts='seal=1; sealing=1 (tarkhanewala-2009 p.118)',notes='The pottery reference on p.118 points to CISI 1 and supplies no newly itemised pottery object. Chak 86 is a separate settlement and supplies no eligible object here.'),
'BNW':dict(best='iar-1987-88',seasons='1987-88: iar-1987-88',notes='No post-baseline inscription-qualified object established from the reviewed candidates. Many journal hits are comparisons with other sites or older catalogue references.'),
'KNL':dict(best='knl-konasukawa-2020',seasons='Period IC(i): knl-konasukawa-2020; 1991-92,1993-94,1994-95: IAR entries',notes='The study lists 11 seals and one sealing; their descriptions do not establish eligible inscriptions. Earlier IAR totals refer to the same non-script classes.'),
'KLB':dict(best='iar-1998-99',unread='puratattva-21 p.11: numerical site-table cells illegible in held text',notes='Baseline CISI 3.2, 2019. Reviewed pre-2019 references produce no rows under Amendment 1. No eligible publication from 2019 onward was established in the assigned sources.'),
'BLT':dict(best='puratattva-36',counts='sealing=2, Early Historic (puratattva-36 PDF p.304; outside Indus scope)',notes='Baseline CISI 3.2, 2019. The sealings noted in the review are assigned to a later archaeological period. No eligible post-2019 publication established.'),
'MSD':dict(best='iar-2008-09',seasons='2009: iar-2008-09',marks='unquantified post-firing graffiti (iar-2008-09 p.62)',unread='msd-petrie-2009: four-page PDF is journal contents only',notes='The readable excavation entry does not explicitly attribute the pottery marks to Indus script.'),
'MTL':dict(best='man-environment-35',seasons='March 2007 surface reconnaissance: man-environment-35',counts='seal=1 (man-environment-35 pp.57-58)',notes='The article distinguishes this surface find from the earlier Rakhigarhi seal cited in the 1975 report.'),
'HUL':dict(best='new-hulas-report',seasons='1978-1983: new-hulas-report',counts='sealing=1 (new-hulas-report p.207)',notes='The excavation predates the baseline. The 2020 report includes an appendix devoted to this object.'),
'DHL':dict(best='new-dhalewan-report',seasons='1999-2000 and 2001-2002: new-dhalewan-report',counts='seal=1; sealing=2 (new-dhalewan-report PDF p.297); only one sealing is inscribed',marks='unquantified pottery graffiti (puratattva-30 p.44; new-dhalewan-report pottery catalogue)',groups='pottery marks compared with Harappan script, no total (puratattva-30 p.44)',notes='Registration 84 is explicitly uninscribed and excluded. Pottery registration 726 has unresolved script affiliation and remains uncertain.'),
'ALG':dict(best='new-hulas-report; puratattva-37',groups='pottery marks compared with Harappan script in a comparative figure (puratattva-37 p.161); no physical-object count',notes='The comparative chart does not identify separate physical sherds. Earlier trough references do not explicitly establish an Indus inscription.'),
'CHG':dict(best='puratattva-24',notes='The explicit pottery article reference is to 1972-73, before the baseline. Chandigarh also identifies an office or publication circle in many hits. No post-baseline object was established.'),
'LHR':dict(best='man-environment-31',marks='unquantified pottery graffiti (man-environment-31 PDF p.208)',notes='The field-survey description does not identify its pottery mark as an Indus sign.'),
'ATR':dict(best='puratattva-37',groups='pottery marks compared with Harappan script, no object count (puratattva-37 p.161)',notes='New unused code included because the journal explicitly makes a script comparison. A comparative chart is insufficient to identify individual physical objects.'),
'LLQ':dict(best='puratattva-37',groups='pottery marks compared with Harappan script, no object count (puratattva-37 p.161)',notes='New unused code included because the journal explicitly makes a script comparison. A comparative chart is insufficient to identify individual physical objects.'),
'GNS':dict(best='puratattva-37',marks='unquantified pottery graffiti (man-environment-26 PDF p.215)',groups='pottery marks compared with Harappan script, no object count (puratattva-37 p.161)',notes='New unused code included because the journal explicitly makes a script comparison. The group remains unnumbered.'),
'IDN':dict(best='man-environment-32',counts='seal=1 (man-environment-32 p.120)',unread='book reviewed in man-environment-32 p.120: full work not held',notes='New unused code included for the seal reported at Kanpur, Indiranagar mound. The review questions the site attribution, including a possible Bangarmau provenance, and the proposed script affiliation remains uncertain. No authenticity or chronology is assigned.')}

NOTE_COLS='site_code site sources_read best_publication rows_individual rows_enumerated rows_uncertain_status rows_possibly_in_cisi3 season_blocks count_statements marks_outside_scope groups_without_count unread_sources notes'.split()
for c in ['BHR','BRR','TKD']:
    INFO[c]['unread']='; '.join(filter(None,[INFO[c].get('unread',''),'iar-2003-04: held archive OCR is unusable for English extraction; no PDF held for OCR recovery']))
# Captions that give no medium leave the medium unclassified under the image rule.
# The preliminary Farmana report explicitly identifies both media in its captions.
for r in objects:
    if r['primary_publication']!='farmana-2007-08-report':
        r['photo_published']='unknown'
        r['drawing_published']='unknown'
pages=M['rows'](OUT/'pages-read-N.csv')
readset={(r['source_id'],r['pdf_page']) for r in pages}
candidates=M['rows'](M['BASE']/'acquisition/candidate-pages-1a.csv')
extra=M['rows'](OUT/'additional-candidates-N.csv')
site_sources=collections.defaultdict(lambda:collections.defaultdict(set))
for r in candidates+extra:
    if (r['source_id'],r['pdf_page']) in readset:
        site_sources[r['site_code']][r['source_id']].add(int(r['pdf_page']))
for r in M['rows'](OUT/'candidate-pages-N.csv'):
    if (r['source_id'],r['pdf_page']) not in readset:continue
    for c,s in SITES.items():
        if s.lower() in r['sites'] or (c=='RPR' and ('ropar' in r['sites'] or 'rupar' in r['sites'])):
            site_sources[c][r['source_id']].add(int(r['pdf_page']))
for r in objects:
    site_sources[r['site_code']][r['primary_publication']].add(int(r['pdf_page']))
for c in ['ATR','LLQ','GNS','ALG']:
    site_sources[c]['puratattva-37'].add(175)

def ranges(ns):
    runs=[]
    for n in sorted(set(ns)):
        if runs and n==runs[-1][-1]+1:runs[-1].append(n)
        else:runs.append([n])
    return ','.join(str(a[0]) if len(a)==1 else f'{a[0]}-{a[-1]}' for a in runs)

notes=[]
for c,s in SITES.items():
    rr=[r for r in objects if r['site_code']==c]; d=INFO[c]
    notes.append(dict(site_code=c,site=s,sources_read='; '.join(f'{sid}:PDF {ranges(ns)}' for sid,ns in sorted(site_sources[c].items())),best_publication=d['best'],rows_individual=sum(r['row_basis']=='individual' for r in rr),rows_enumerated=sum(r['row_basis']=='enumerated-count' for r in rr),rows_uncertain_status=sum(r['inscription_status']=='uncertain' for r in rr),rows_possibly_in_cisi3=sum(r['catalogue_status']=='possibly-in-cisi3' for r in rr),season_blocks=d.get('seasons',''),count_statements=d.get('counts',''),marks_outside_scope=d.get('marks',''),groups_without_count=d.get('groups',''),unread_sources=d.get('unread',''),notes=d.get('notes','')))
M['savecsv'](OUT/'objects-N.csv',COLS,objects)
M['savecsv'](OUT/'site-notes-N.csv',NOTE_COLS,notes)
M['savecsv'](OUT/'merge-log-N.csv',['kept_row_id','merged_source','merged_page','basis'],merges)
print(json.dumps(dict(rows=len(objects),sites=len(notes),counts={c:sum(r['site_code']==c for r in objects) for c in SITES})))
