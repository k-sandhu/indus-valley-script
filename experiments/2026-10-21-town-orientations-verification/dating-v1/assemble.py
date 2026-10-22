"""Assemble the dated evidence register from explicitly transcribed observations.

This script writes only within dating-v1. Source values retain their locators.
Run with python -I; it does not download or execute source documents.
"""
import csv
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RAW = ROOT / 'data/raw/2026-10-21-town-orientations-verification/dating'
SOURCES = {}
TOWNS = {}
RADIOCARBON = []


def source(key, authors, year, title, publication, url=None, local_path=None,
           access_route='local PDF, title and relevant pages inspected', download=None, notes=''):
    obj = dict(source_key=key, authors=authors, year=year, exact_title=title,
               publication=publication, url=url, local_path=local_path,
               access_route=access_route, notes=notes, locators=[])
    if download:
        acq = json.loads((RAW / (download + '.acquisition.json')).read_text(encoding='utf-8'))
        obj['acquisition'] = acq
        obj['local_path'] = acq['path']
    elif local_path and (ROOT / local_path).is_file():
        b = (ROOT / local_path).read_bytes()
        obj['held_copy'] = dict(byte_count=len(b), sha256=hashlib.sha256(b).hexdigest(),
                                handling='existing local-only source; no new acquisition')
    SOURCES[key] = obj


def loc(key, page, detail=''):
    s = SOURCES[key]
    result = dict(source_key=key, authors=s['authors'], year=s['year'],
                  exact_title=s['exact_title'], page_table_figure=page, detail=detail)
    if result not in s['locators']:
        s['locators'].append(result)
    return result


def assertion(text, *locators):
    return dict(text=text, locators=list(locators))


def phase(label, architecture, *locators):
    return dict(label=label, architecture=architecture, locators=list(locators))


def candidate(level, bce, locator, basis, start_range=None, range95=None, notes=''):
    sigma = ((abs(range95[0]-range95[1])/3.92) if level == 1 else
             (abs(start_range[0]-start_range[1])/4 if start_range else 150) if level == 2 else 200)
    return dict(level=level, year_bce=bce, astronomical_year=1-bce, sigma_D_years=sigma,
                start_range_bce=start_range, start_boundary_95_range_bce=range95,
                basis=basis, locator=locator, notes=notes,
                rule='assignment: levels of evidence and candidate values')


def part(name, label, support, phases, candidates=(), alternatives=(), notes='', no_candidate_reason=''):
    cs = list(candidates)
    proposed = min(cs, key=lambda c: (c['level'], -SOURCES[c['locator']['source_key']]['year'])) if cs else None
    return dict(part=name, phases=phases, layout_phase=dict(label=label, support=support,
                alternatives=list(alternatives)), candidates_by_level={str(i):[c for c in cs if c['level']==i] for i in (1,2,3)},
                proposed_candidate=proposed, reviewer_status='pending project judgement',
                no_candidate_reason=no_candidate_reason if proposed is None else '', notes=notes)


def town(slug, name, parts, first=None, searched=(), notes=(), disagreements=(), required=True):
    TOWNS[slug] = dict(slug=slug, town=name, required=required, parts=parts,
                      first_occupation=first, searches=list(searched), notes=list(notes),
                      disagreements=list(disagreements), radiocarbon_determinations=[],
                      authors=[dict(model='GPT-6 (Codex)', harness='Codex API with functions tools')],
                      evidence_status='source assembly; candidate dates await project review')


def rc(slug, code, bp, error, material, context, phase_label, relation, locator,
       part_names=(), reported_calendar=None, half_life=5568, notes=''):
    row = dict(slug=slug, lab_code=code, conventional_age_bp=bp, error_bp=error,
               material=material, context=context, phase_label=phase_label,
               relation_to_layout_phase=relation, part_names=list(part_names),
               reported_calendar=reported_calendar, half_life_years=half_life,
               locator=locator, notes=notes)
    RADIOCARBON.append(row)
    return row


source('stuckenrath1967','Robert Stuckenrath, Jr.',1967,
       'University of Pennsylvania Radiocarbon Dates X','Radiocarbon 9:333-345',
       'https://doi.org/10.1017/S0033822200000618',download='penn1967.pdf')
source('kenoyer1991','Jonathan Mark Kenoyer',1991,
       'The Indus Valley Tradition of Pakistan and Western India','Journal of World Prehistory 5(4):331-385',
       'https://doi.org/10.1007/BF00978474',download='kenoyer1991.pdf')
source('uesugi2018','Akinori Uesugi',2018,
       'Current state of research and issues of Indus Archaeology: Focusing on field researches and material cultural studies',
       'In Akinori Uesugi (ed.), Current Research on Indus Archaeology, South Asian Archaeology Series 4, pp. 1-55. Kansai University.',
       'https://researchmap.jp/a_uesugi/published_papers/16441010/attachment_file.pdf',download='gujarat2018.pdf',
       notes='Despite the transport filename, this download contains the opening chapter and front matter, not the Rajesh chapter listed in its contents.')
source('kenoyermeadow2010','J. Mark Kenoyer and Richard H. Meadow',2010,
       'Inscribed Objects from Harappa Excavations 1986-2007',
       'In Asko Parpola, B. M. Pande and Petteri Koskikallio (eds.), Corpus of Indus Seals and Inscriptions, vol. 3, part 1, pp. xliv-lviii. Helsinki: Suomalainen Tiedeakatemia.',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf',
       'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez/kenoyer-meadow2010-published.pdf')

source('sindhi2026','Sheikh Javed Ali Sindhi',2026,
       "Discovering Mohenjo-Daro's Ancient Defences",'The Friday Times, 13 May 2026',
       'https://www.thefridaytimes.com/13-May-2026/discovering-mohenjo-daro-s-ancient-defences',
       download='mohenjo2026-defences.html',access_route='Field participant article quoting the preliminary report with page numbers; report itself not acquired.')
source('kenoyer2008cities','Jonathan Mark Kenoyer',2008,
       'Indus Urbanism: New Perspectives on its Origin and Character',
       'Author manuscript for The Ancient City: New Perspectives on Urbanism in the Old and New World (Joyce Marcus and Jeremy A. Sabloff, eds.); manuscript revision dated 1 October 2005. Manuscript pagination is used here.',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer2008%20Indus%20Cities%20Sackler%20Colloquiumfinalrevised.pdf',
       download='kenoyer2008-cities.pdf')
source('meadowkenoyer2005','Richard H. Meadow and Jonathan Mark Kenoyer',2005,
       'Excavations at Harappa 2000-2001: New Insights on Chronology and City Organization',
       'In Catherine Jarrige and Vincent Lefèvre (eds.), South Asian Archaeology 2001, pp. 207-225. Paris: Éditions Recherche sur les Civilisations.',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer2005_Excavations%20at%20Harappa%202000-2001%20New%20insights%20on.pdf',
       'data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v2/kenoyer2005-harappa.pdf',
       notes='Scanned source: chronology and determination table read with OCR; Table 2 checked against rendered page image.')
source('meadowkenoyer1997','Richard H. Meadow and Jonathan Mark Kenoyer',1997,
       'Excavations at Harappa 1994-1995: New Perspectives on the Indus Script, Craft Activities, and City Organization',
       'In Raymond Allchin and Bridget Allchin (eds.), South Asian Archaeology 1995, pp. 139-172. New Delhi: Oxford & IBH.',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer1997_Excavations%20at%20Harappa%201994-1995%20New%20Perspective.pdf',download='harappa1997.pdf')

md26=loc('sindhi2026','Preliminary Report of the Mohenjo-Daro Excavations 2025-26, pp. 6-8, quoted under “What Were the Major Discoveries, Antiquities, and Findings?”',
         'Indirect access: Kenoyer, Ibrahim and Lashari preliminary report, submitted in March; page numbers supplied by the participant article.')
mdlow=loc('kenoyer2008cities','manuscript p. 17; Table 3 on manuscript p. 16')
mdphases=[phase('Early Harappan / Kot Dijian Period','Pottery-bearing deposits precede the earliest mud-brick perimeter wall. The wall has earlier occupation beneath it.',md26),
          phase('Harappan Phase','Citadel platforms and public buildings; residential streets and houses in the lower-town excavation areas. The published era table does not synchronize the first construction of these units.',mdlow)]
town('mohenjo-daro','Mohenjo-daro',[
    part('citadel / perimeter wall','Early Harappan / Kot Dijian Period',
         assertion('The participant article quotes a core from the lower perimeter wall and earlier occupation below it. The report calls the first masonry a “mud brick perimeter wall”.',md26),mdphases,
         no_candidate_reason='The accessible account gives calibrated sample ranges and an informal wall date, but no published calibrated start of the layout phase or Bayesian start boundary. Its pottery-based period bracket conflicts with its own later radiocarbon discussion. The primary preliminary report and laboratory results remain unacquired.'),
    part('lower town','not established across excavated areas',
         assertion('The synthesis describes early pottery in the lowest excavations and later residential occupation but gives no dated first-construction boundary for the lower-town grid.',mdlow),mdphases,
         no_candidate_reason='Neither the first construction phase of the exposed grid nor its calendar start is tied to an inspected primary dating sequence.')],
    first=dict(year_bce=None,range_bce=[3300,2800],range_astronomical_years=[-3299,-2799],
               evidence='Reported pottery cross-date for earlier occupation below the perimeter wall; this is a period attribution, not a measured founding date.',locators=[md26]),
    searched=['Mohenjo-daro radiocarbon Dales P-1179 P-1180; University of Pennsylvania Radiocarbon Dates X; Mohenjo-Daro Excavations 2025-26 preliminary report; Kenoyer author-hosted city synthesis; held Marshall scan (no usable text layer).'],
    notes=[assertion('The recent wall sample is reported as 2708-2576 cal BC at the stated probability of 50%. A single dated core is insufficient to replace a published phase-start estimate under the assignment rules.',md26),
           assertion('The six determinations below are retained as late-occupation comparisons. They do not date the first layout.',loc('stuckenrath1967','pp. 333-334, Mohenjo-daro series'))],
    disagreements=[assertion('The preliminary report quoted at p. 6 gives a pottery bracket of 3300-2800 BC; its p. 8 gives a wall-core result of 2708-2576 cal BC. The article separately reports 2700-2600 BC for the first wall. These statements require the full report and sample-context review.',md26),
                   assertion('Kenoyer’s synthesis reverses the ages associated with P-1176 and P-1178A relative to the laboratory publication. We transcribe the laboratory source.',loc('kenoyer1991','p. 337, Table III'),loc('stuckenrath1967','pp. 333-334'))])
for code,bp,err,material,context,pg in [
    ('P-1176',3801,59,'ash','Area VII, 4, Level 4; storage jar used as fireplace in house floor',333),
    ('P-1177',3985,64,'charcoal','Area VII, 3, Level 4a; centre of floor',333),
    ('P-1178A',3802,59,'charred straw','Area VI, 9, Level 4; floor of collapsed burned room',334),
    ('P-1179',3913,64,'charred wood, outer rings','Area VI, 9, Level 4; door jamb burned in place',334),
    ('P-1180',3828,61,'charred wood, core','Area VI, 9, Level 4; same door jamb as P-1179',334),
    ('P-1182A',3702,63,'charred straw','Area VI, 9, Level 4; doorway associated with the burned jamb',334)]:
    rc('mohenjo-daro',code,bp,err,material,context,'latest Mature Harappan, HR mound',
       'later occupation; not assignable to first layout or predecessor',loc('stuckenrath1967',f'p. {pg}, sample {code}; half-life on p. 333'),
       reported_calendar=dict(scale='uncalibrated B.C. (BP minus reference epoch)',year_bce=bp-1950),
       notes='Laboratory author qualifies the relative dating as tentative and does not claim these are the latest levels of the whole city.')

hpdate=loc('kenoyermeadow2010','p. xlv, Table 1 and footnote 3')
hpfirst=loc('kenoyermeadow2010','p. xlvii, General Site Chronology and Highlights of the Excavations')
hplay=loc('kenoyer2008cities','manuscript pp. 9, 13-14')
hpphases=[phase('Period 1 (Ravi Phase)','Village occupation with hearths, pits and craft activity; precedes the walled town.',loc('meadowkenoyer2005','pp. 209-210')),
          phase('Period 2 (Kot Diji Phase)','First documented walled planning of Mounds AB and E, with mud-brick houses, platforms and streets.',hplay),
          phase('Period 3A','Harappan walls built above or slightly offset from earlier walls; new wall-and-street plan in part of Mound E.',hplay),
          phase('Period 3B','Expansion into walled suburbs, including Mounds F and ET; public building on Mound F.',hplay),
          phase('Period 3C','Rebuilding of gateways and walls; circular platforms in Mound F.',hplay),
          phase('Period 4 / Period 5','Transitional and Late Harappan occupation; streets encroached upon and upper architecture badly robbed.',loc('kenoyer2008cities','manuscript p. 16'),hpdate)]
hpparts=[]
for name in ['Mound AB','Mound E']:
    hpparts.append(part(name,'Period 2',assertion('The excavator places the first perimeter walls and planned streets in the Kot Diji phase. The Harappan city preserves this planning through rebuilding.',hplay),hpphases,
        [candidate(2,2800,hpdate,'Excavators’ calibrated site chronology; all essay ages explicitly based on calibrated site determinations.')],
        alternatives=[assertion('If the target is the first replacement Harappan masonry, the relevant label is Period 3A, with a stated calibrated start of 2600 BCE. The earlier grid and enclosure began in Period 2.',hplay,hpdate)],
        notes='Candidate refers to earliest planning. The beginning of Period 2 remains weakly sampled; the earlier excavation report explicitly calls it largely undated.'))
for name in ['Mound F','Mound ET']:
    hpparts.append(part(name,'Period 3B',assertion('The excavator assigns the construction of the new walled suburbs to this phase.',hplay),hpphases,
        [candidate(2,2450,hpdate,'Excavators’ calibrated site chronology for the phase of suburban construction.')],
        alternatives=[assertion('For Mound ET, an earlier report dates the enclosing wall only as later than its underlying hearth. This terminus does not itself fix the phase-start year.',loc('meadowkenoyer1997','pp. 143-144, 147; Table 1, p. 143'))] if name=='Mound ET' else [],
        notes='The phase boundary is a site chronology, not an independently modelled boundary for this individual wall.'))
hpparts.append(part('mound beneath modern Harappa town','not established',
    assertion('The excavator lists this as a separate mound whose major early occupation is buried beneath the modern settlement.',loc('kenoyermeadow2010','p. xlv'),loc('kenoyer2008cities','manuscript p. 13')),hpphases,
    no_candidate_reason='No exposed layout with an established first-construction phase in the inspected sources.'))
town('harappa','Harappa',hpparts,
     first=dict(year_bce=3700,astronomical_year=-3699,evidence='Excavators’ stated initial village date, based on their calibrated site chronology.',locators=[hpdate,hpfirst]),
     searched=['Harappa Period 2 city wall; Harappa Period 3A radiocarbon; excavations 1994-1995, 2000-2001, 1986-2007; later 1986-2010 chapter located but full text not acquired.'],
     notes=[assertion('The determination register includes the inspected dated contexts and retains rejected and anomalous determinations. It is not a complete transcription of every HARP laboratory result.',loc('meadowkenoyer2005','pp. 208-209'))],
     disagreements=[assertion('The earlier report says most dated basal Ravi samples do not predate about 3300 cal BC, while allowing earlier deposits beneath the centre of Mound AB. The later essay states initial occupation about 3700 BC. We retain the later stated first-occupation date and the earlier sampling qualification.',loc('meadowkenoyer2005','p. 209'),hpdate,hpfirst),
                    assertion('The earlier chronology places the Harappan transition between 2600 and 2500 cal BC; the later table states the start of Period 3A at 2600 BC. The earlier table also assigns Period 3B an end at 2250 BC, while the later table uses 2200 BC.',loc('meadowkenoyer1997','p. 140'),loc('meadowkenoyer2005','pp. 207, 209'),hpdate)])
for code,bp,err,context,ph,cal in [
    ('Beta-163719',4480,50,'H2000/11036 [686]','1A',[3355,3015]),
    ('Beta-163715',4430,40,'H2000/9525 [454]','1A',[3330,2920]),
    ('Beta-163717',4390,40,'H2000/9942 [582]','1A',[3100,2900]),
    ('Beta-163718',4000,40,'H2000/11009 [658]','2',[2600,2455]),
    ('Beta-163712',3780,40,'H1999/8949 [166]','2',[2310,2040]),
    ('Beta-163710',4040,40,'H1998/8414 [16]','2',[2670,2465]),
    ('Beta-163711',3930,40,'H1998/8570 [72]','2',[2500,2290]),
    ('Beta-163714',3910,40,'H2000/2127 [46]','3A',[2475,2285]),
    ('Beta-163720',3760,40,'H2001/9036 [532]','3B/3C',[2290,2035]),
    ('Beta-163721',3800,40,'H2001/11756 [956]','3C',[2350,2130]),
    ('Beta-163713',3440,40,'H1999/9803 [410]','5',[1880,1680])]:
    rc('harappa',code,bp,err,'not reported in Table 2 (carbon samples in text)',context,'Period '+ph,
       'predecessor to AB/E layout' if ph=='1A' else 'AB/E layout phase' if ph=='2' else 'predecessor to F/ET layout' if ph=='3A' else 'layout/later phase unresolved' if ph=='3B/3C' else 'later comparison',
       loc('meadowkenoyer2005','p. 209, Table 2',code),reported_calendar=dict(scale='cal BC',range_bce=cal,probability='at least 90%; CALIB revision 4.3, Method B'),
       notes='Source flags date as too late for stratigraphic context.' if code=='Beta-163712' else '')

for code,bp,err,context,ph,cal,flag,pg in [
 ('A-7527',3960,95,'H93/4311 [230], Trench 10W, Hearth 235A','2',[2575,2320],'',142),
 ('A-7530',3545,'+155/-150','H93/4337 [263], Trench 10W, Hearth 265; basal deposits','2',[2120,1680],'rejected by authors',142),
 ('A-8045',4130,'+225/-215','H94/3974 [28], Trench 21, Hearth 27','2',[2920,2403],'',142),
 ('A-8044',3765,'+260/-255','H94/3973 [26], Trench 21, Hearth 27; basal hearth','2',[2560,1778],'rejected by authors; printed cross-reference repeats its own code',142),
 ('A-7522',3875,55,'H93/4054 [13], Trench 10W, Room 92, Hearth 25, lower','3B',[2457,2207],'',142),
 ('QL-4732',3890,20,'H93/4055 [26], Trench 10W, Room 92, Hearth 25, lower','3B',[2453,2323],'',142),
 ('A-7523',3835,50,'H93/4061 [32], Trench 10W, Room 92, Hearth 25, middle','3B',[2395,2149],'',142),
 ('QL-4733',3840,20,'H93/4061 [32], Trench 10W, Room 92, Hearth 25, middle','3B',[2320,2206],'',142),
 ('A-7524',4385,'+155/-150','H93/4124 [128], Trench 10W, Room 92, Hearth 16','3B',[3336,2879],'rejected by authors; probably old charcoal',142),
 ('A-7525',3790,85,'H93/4208 [7], Trench 9, Hearth 7','3B',[2391,2043],'',142),
 ('QL-4731',3880,40,'H93/4209 [20], Trench 9, Hearth 7','3B',[2455,2284],'',142),
 ('A-8050',3895,'+140/-135','H94/5442 [259], Trench 9, Hearth 259','3B',[2565,2141],'',142),
 ('QL-4778',3820,60,'H94/4553 [169], Trench 9, Hearth 144','3B',[2393,2142],'',142),
 ('A-8046',4130,'+170/-165','H94/4553 [169], Trench 9, Hearth 144; same sample as QL-4778','3B',[2906,2464],'somewhat aberrant',142),
 ('A-7526',3750,'+150/-145','H93/4284 [90], Trench 9, Hearth 91','3B',[2450,1935],'',142),
 ('A-8051',4065,55,'H94/5467 [274], Trench 9, Hearth 274','3B',[2850,2493],'rejected by authors',142),
 ('QL-4777',3860,40,'H94/5467 [274], Trench 9, Hearth 274','3B',[2451,2206],'',142),
 ('QL-4776',3780,60,'H94/5472 [273], Trench 9, Hearth 273','3B',[2285,2048],'',142),
 ('A-8052',4075,70,'H94/5472 [273], Trench 9, Hearth 273; same sample as QL-4776','3B',[2858,2491],'somewhat aberrant; may include earlier charcoal',142),
 ('A-7528',3165,'+190/-185','H93/4315 [236], Trench 10W, Room 93, Hearth 233','3B',[1629,1168],'rejected by authors; possible contamination near surface',143),
 ('QL-4734',3820,60,'H93/4194 [215], Trench 10W, Hearth 210, upper','3B',[2393,2142],'',143),
 ('A-7529',3905,75,'H93/4331 [256], Trench 10W, Room 93, Hearth 210, lower','3B',[2468,2280],'',143),
 ('QL-4730',3900,30,'H93/4331 [256], Trench 10W, Room 93, Hearth 210, lower','3B',[2457,2325],'',143),
 ('A-8047',3965,55,'H94/5383 [64], Trench 22, Hearth 64, below Wall 15; AMS alias AA-16461','3B',[2558,2404],'one measurement with two identifiers, not two determinations',143),
 ('A-8048',3975,'+110/-105','H94/5384 [66], Trench 22, Hearth 64, below Wall 15','3B',[2589,2320],'',143),
 ('A-8049',3785,'+145/-140','H94/5385 [67], Trench 22, Hearth 68, below Wall 15','3B',[2457,1976],'somewhat aberrant; same stratigraphic context as A-8047 and A-8048',143),
 ('QL-4729',3720,40,'H93/3541 [11], Trench 2, Pit 11 outside Wall 17A','3B/C',[2180,2034],'',143),
 ('A-7521',3895,70,'H93/3541 [11], Trench 2, Pit 11 outside Wall 17A; same sample as QL-4729','3B/C',[2465,2208],'rejected by authors; possible earlier charcoal',143),
 ('A-8053',3705,55,'H94/697 [3], Trench 31, hearth behind mosque','3C/4',[2180,1980],'later comparison',143),
 ('QL-4775',3740,90,'H94/647 [5], Trench 31, hearth behind mosque','3C/4',[2281,1980],'later comparison',143)]:
    rc('harappa',code,bp,err,'not individually specified in table; hearth carbon unless pit context',context,'Period '+ph,
       'AB/E layout phase' if ph=='2' else 'Mound ET layout-phase attribution; some contexts predate its wall' if ph=='3B' else 'later comparison',
       loc('meadowkenoyer1997',f'p. {pg}, Table 1',code),
       reported_calendar=dict(scale='calibrated BC',range_1sigma_bce=cal),notes=flag)

source('thapar1975','B. K. Thapar',1975,
       'Kalibangan: A Harappan Metropolis Beyond the Indus Valley','Expedition 17(2):19-32',
       'https://www.penn.museum/sites/expedition/kalibangan/',download='kalibangan1975.pdf',
       notes='Scanned page spreads. Printed page numbers are used; the dated numerical passage explicitly excludes radiocarbon correction factors.')
source('prasadsingh2021','Esha Prasad and Ravindra Nath Singh',2021,
       'The Chronology of the Ganeshwar Jodhpura Culture: A Reassessment Based on Graffiti and Cross-Cultural Comparisons',
       'Ancient Asia 12:10, pp. 1-21','https://doi.org/10.5334/aa.238',download='ganeshwar2021.pdf',
       notes='PDF p. 21 explicitly states CC BY 4.0. The comparative site-date table on p. 9 cites Brunswig’s radiocarbon calibration study for Kalibangan.')
source('dikshit2013','K. N. Dikshit',2013,
       'Origin of Early Harappan Cultures in the Sarasvati Valley: Recent Archaeological Evidence and Radiometric Dates',
       'Journal of Indian Ocean Archaeology 9:87-141',
       'https://pdfcoffee.com/origin-of-early-harappan-cultures-in-the-sarasvati-valley-recent-archaeological-evidence-and-radiometric-dates-pdf-free.html',
       download='dikshit2013-page.html',access_route='Third-party HTML transcription of the published article; printed page headers retained. Numerical transcription requires primary page-image review.',
       notes='The journal’s official PDF route retrieved only a contents list. This HTML copy is treated as a transcription, not an independently verified excavation record.')
source('lal2020part2','B. B. Lal, Jagat Pati Joshi, A. K. Sharma, Madhu Bala and K. S. Ramachandran',2020,
       'Excavations at Kalibangan: The Harappans (1960-69), Part II',
       'Memoirs of the Archaeological Survey of India 110. New Delhi: Archaeological Survey of India.',
       local_path='data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/kalibangan_report2020.pdf',
       notes='Title, copyright and preface inspected. Part I, which is needed for the main settlement chronology, was not recovered. No candidate is inferred from this part’s publication date.')
klay=loc('thapar1975','pp. 23-27; plan on p. 19')
kdate=loc('prasadsingh2021','p. 9, comparative site/phase/date/reference table')
kph=[phase('Period I (Kalibangan I)','Fortified antecedent settlement; mud-brick houses and lane; rebuilding within the same plan, followed by an abandonment deposit.',loc('thapar1975','pp. 20-23')),
     phase('Period II (Kalibangan II): Early, Middle, Late','New Harappan plan with a citadel divided by an internal fortification and a separate lower town. Platforms, houses, streets and enclosure were rebuilt within the occupation.',klay,loc('thapar1975','p. 32'))]
kp=[]
for name,description in [
 ('citadel: ritual sector','Mud-brick platforms occupy a separately enclosed part of the citadel. The enclosing Harappan walls are built over antecedent ruins.'),
 ('citadel: residential annexe','The other separately enclosed citadel sector contains houses and a street, within the new Harappan plan.'),
 ('lower town','The lower city was laid out on the natural plain, separately from the citadel, within the changed Harappan plan.')]:
    kp.append(part(name,'Period II',assertion(description+' The excavator describes the new arrangement as “two distinct parts”.',klay),kph,
        [candidate(2,2500,kdate,'Published calendar span for Kalibangan Period II, explicitly referred to Brunswig’s radiocarbon calibration study.',
                   notes='Calibration study is accessed indirectly through this later comparative synthesis; its complete tables were not acquired.')],
        alternatives=[assertion('The excavation account’s older start at 2300 B.C. explicitly excludes radiocarbon correction factors and therefore is not a calibrated candidate.',loc('thapar1975','p. 23; p. 32'))],
        notes='The selected year is the stated phase start; the source supplies no uncertainty interval for that start. The total occupation span is not used as a start-error range.'))
town('kalibangan','Kalibangan',kp,
     first=dict(year_bce=None,evidence='Period I is the first occupation. The older excavation estimate is uncalibrated; calibrated determinations in the later table do not establish a single accepted founding boundary.',
                reported_estimates=[dict(year_bce=2450,scale='uncalibrated B.C.',locator=loc('thapar1975','p. 23'))],
                locators=[loc('thapar1975','pp. 20, 23'),loc('dikshit2013','pp. 120-121, Table 2')]),
     searched=['Kalibangan calibrated radiocarbon chronology Period II; Brunswig 1975 calibration study; Tata date lists; Radiocarbon dates of Kalibangan samples; Kalibangan 2020 Part I routes; official JIOA contents and Dikshit article transcription; Bayesian chronology search.'],
     notes=[assertion('KLB-1 and KLB-2 name mounds; Period I and Period II name successive occupations. The excavator explicitly distinguishes these labels.',loc('thapar1975','p. 20')),
            assertion('The excavation report describes a ritual compound outside the lower town. It is retained as a feature of Period II rather than assumed to be a separate planned residential town unit.',loc('thapar1975','pp. 28-31'))],
     disagreements=[assertion('The older uncalibrated start and the later calibrated comparative span use different timescales. The anomalously early predecessor determination in the later compilation also needs context review.',loc('thapar1975','p. 23'),kdate,loc('dikshit2013','pp. 120-121, Table 2'))])
for code,bp,err in [('TF-143',3510,110),('TF-152 (BS)',3570,125),('TF-946',3605,100),('TF-142',3635,100),
                    ('TF-149',3675,140),('TF-139',3775,100),('TF-151',3800,100),('TF-147',3865,100),
                    ('TF-608',3910,110),('TF-163 (BS)',3925,125),('TF-607',3930,120),('TF-160',4060,100)]:
    rc('kalibangan',code,bp,err,'not specified in synthesis table','Period II; context not supplied in this selected-date table','Period II',
       'layout phase, subphase unspecified',loc('kenoyer1991','p. 338, Table III',code),
       reported_calendar=dict(scale='Both uncalibrated BC using the longer half-life and calibrated CALIB intercepts are printed; see source table.'),
       notes='This is a selected-date synthesis, not the complete excavation suite. Individual sample material and trench context remain to be recovered.')
for code,bp,err,context,cal in [
 ('TF-957',2355,200,'Late',[900,-70]),('TF-154',3665,110,'Late',[2395,1741]),
 ('TF-156 (BS)',4010,165,'Late',[2917,2034]),('TF-156',3740,105,'Late',[2462,1789]),
 ('TF-165',3800,100,'Late',[2489,1934]),('TF-161',3930,100,'Middle',[2853,2059]),
 ('TF-240',3610,110,'Early',[2281,1680]),('TF-162',3940,100,'Early',[2857,2137]),
 ('TF-241',4090,90,'Early',[2888,2404]),('TF-157',4120,110,'Early (table ordering)',[2918,2362]),
 ('TF-155',4195,115,'Early',[3072,2465]),('TF-439 (BS)',6507,125,'Early',[5600,5224])]:
    rc('kalibangan',code,bp,err,'not specified in Table 2','Predecessor occupation, '+context+' levels; trench not supplied','Period I',
       'predecessor to layout',loc('dikshit2013','p. 121, Table 2',code),
       reported_calendar=dict(scale='Calib-3 corrected BC',range_2sigma_bce=cal,
                              note='For TF-957 the later endpoint is AD 70, retained as signed BCE -70.' if code=='TF-957' else ''),
       notes='Read from HTML transcription. Source also prints longer-half-life ages. TF-439 without BS is described only as the same result, and is not counted as another determination.' if code=='TF-439 (BS)' else 'Read from HTML transcription; primary page-image verification remains outstanding.')

# Further observations are added below before the export call.
exec(compile((OUT/'entries.py').read_text(encoding='utf-8'), str(OUT/'entries.py'), 'exec'))
exec(compile((OUT/'entries2.py').read_text(encoding='utf-8'), str(OUT/'entries2.py'), 'exec'))
exec(compile((OUT/'entries3.py').read_text(encoding='utf-8'), str(OUT/'entries3.py'), 'exec'))
exec(compile((OUT/'entries4.py').read_text(encoding='utf-8'), str(OUT/'entries4.py'), 'exec'))
exec(compile((OUT/'finalize.py').read_text(encoding='utf-8'), str(OUT/'finalize.py'), 'exec'))


ORDER='mohenjo-daro harappa kalibangan lothal dholavira surkotada banawali rakhigarhi chanhu-daro kanmer shikarpur juni-kuran gola-dhoro desalpur khirsara kuntasi rojdi kot-diji nausharo sutkagen-dor balakot allahdino lakhanjo-daro ganweriwala farmana bhirrana kunal mitathal karanpura rangpur kotada-bhadli pabumath navinal'.split()

def calendars(value):
    """Add astronomical counterparts to explicitly calendar-BCE fields."""
    if isinstance(value,list):
        for item in value: calendars(item)
    elif isinstance(value,dict):
        for key,v in list(value.items()):
            calendars(v)
            if key.endswith('_bce') and v is not None:
                newkey=key[:-4]+'_astronomical'
                if isinstance(v,(int,float)): value.setdefault(newkey,1-v)
                elif isinstance(v,list) and all(isinstance(x,(int,float)) for x in v):
                    value.setdefault(newkey,[1-x for x in v])

def export():
    for row in RADIOCARBON:
        TOWNS[row['slug']]['radiocarbon_determinations'].append(row)
    (OUT/'evidence').mkdir(exist_ok=True)
    for slug in ORDER:
        data=TOWNS[slug]
        calendars(data)
        (OUT/'evidence'/f'{slug}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    acquisitions=[]
    for f in sorted(RAW.glob('*.acquisition.json')):
        a=json.loads(f.read_text(encoding='utf-8'))
        a['record_path']=f.relative_to(ROOT).as_posix()
        acquisitions.append(a)
    review=json.loads((OUT/'acquisition-review.json').read_text(encoding='utf-8'))
    (OUT/'sources.json').write_text(json.dumps(dict(sources=list(SOURCES.values()), acquisitions=acquisitions,
        acquisition_review=review), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    fields=['slug','part','layout_phase_label','level','candidate_year_bce','candidate_astronomical_year',
            'sigma_D_years','source_key','first_occupation_year_bce','first_occupation_astronomical_year','locator','layout_locator','first_occupation_locator','notes']
    with (OUT/'candidates.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for slug in ORDER:
            t=TOWNS[slug]
            for p in t['parts']:
                c=p['proposed_candidate'];first=t['first_occupation'] or {}
                writer.writerow(dict(slug=slug,part=p['part'],layout_phase_label=p['layout_phase']['label'],
                   level=c['level'] if c else '',candidate_year_bce=c['year_bce'] if c else '',
                   candidate_astronomical_year=c['astronomical_year'] if c else '',sigma_D_years=c['sigma_D_years'] if c else '',
                   source_key=c['locator']['source_key'] if c else '',first_occupation_year_bce=first.get('year_bce',''),
                   first_occupation_astronomical_year=1-first['year_bce'] if first.get('year_bce') is not None else '',
                   locator=json.dumps(c['locator'] if c else p['layout_phase']['support']['locators'],ensure_ascii=False),
                   layout_locator=json.dumps(p['layout_phase']['support']['locators'],ensure_ascii=False),
                   first_occupation_locator=json.dumps(first.get('locators',[]),ensure_ascii=False),
                   notes=p['notes']+' '+p['no_candidate_reason']))
    fields=['slug','lab_code','conventional_age_bp','error_bp','material','context','phase_label','relation_to_layout_phase',
            'part_names','reported_calendar','half_life_years','source_key','locator','notes']
    with (OUT/'radiocarbon.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in sorted(RADIOCARBON,key=lambda x:ORDER.index(x['slug'])):
            row=r.copy();row['source_key']=r['locator']['source_key']
            for k,v in list(row.items()):
                if isinstance(v,(dict,list)): row[k]=json.dumps(v,ensure_ascii=False)
            writer.writerow(row)


if __name__=='__main__':
    export()
