"""Append attributed evidence without altering any earlier Package E record."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
BASE = OWN.parent
RAW = ROOT / 'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def source(sid, authors, year, title, venue, url, locations, witness=None,
           opened=True, access='opened full publication; relevant text and figures reviewed', note=''):
    s=dict(id=sid, authors=authors, year=year, title=title, venue=venue, url=url,
           opened=opened, access_status=access, locations_reviewed=locations, note=note,
           rights_status='rights-unverified; third-party payloads remain local-only', quote_words=0)
    if witness:
        path=ROOT/witness
        s.update(local_witness=witness, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return s

def local(name):
    return (RAW/name).relative_to(ROOT).as_posix()

def date(start, end, method, grade, location, note='', strength='low', selected=False, labs=(), measurement=None):
    return dict(start_year=start, end_year=end, method=method, grade=grade, source_location=location,
                note=note, lab_numbers=list(labs), calendar_strength=strength,
                published_measurement=measurement, selected_for_coverage=selected)

def row(rid, label, classes, dates, sids, locs, count=None, kind='unknown', unit='marked objects', basis='',
        repertoire=None, repertoire_basis='', images=False, additive=False, region='Indus northwest',
        sites=(), claims=(), limitations='', observations=None, adjacent=False):
    r=dict(id=rid, label=label, region=region, sites=list(sites), object_classes=classes,
           marked_object_count=count, count_kind=kind, count_unit=unit, count_basis=basis,
           repertoire_size=repertoire, repertoire_basis=repertoire_basis,
           dating_assessments=dates, source_ids=sids, source_locations=locs,
           image_corpus_verified=images, access='See sources.json access_status and source_locations; raw payloads local-only.',
           continuity_claim_ids=list(claims), limitations=limitations,
           include_in_additive_coverage=additive, adjacent_region=adjacent,
           status='Exploratory', documentary_revision='2026-10-07 Frenez follow-up; appended record')
    if observations: r['additional_observations']=observations
    return r

def make_sources():
    S=[]
    def add(*a, **kw): S.append(source(*a, **kw))
    add('quivron1980',['Gonzague Quivron'],1980,
        'Les marques incisées sur les poteries de Mehrgarh au Baluchistan, du milieu du IVe millénaire à la première moitié du IIIe millénaire',
        'Paléorient 6:269–280. DOI:10.3406/paleo.1980.4281',
        'https://www.persee.fr/doc/paleo_0153-9345_1980_num_6_1_4281',
        ['pp.269,274–279; tables 1–3; images of all 12 pages recovered; pp.269,275,278 visually sampled'],
        local('quivron1980-pages/pages.json'), access='opened complete paper as public page images and OCR; direct PDF returned 403',
        note='Manifest contains each page/image URL, status and SHA256. The 850 total counts marks, not authenticated distinct objects.')
    add('quivron1997',['Gonzague Quivron'],1997,
        'Incised and Painted Marks on the Pottery of Mehrgarh and Nausharo-Baluchistan',
        'In F. R. Allchin and B. Allchin (eds.), South Asian Archaeology 1995, pp.45–62. New Delhi: Oxford & IBH',
        'https://arscan.parisnanterre.fr/membre/gonzague-quivron/', ['bibliographic reference; Coningham 2002 pp.93–94,102'],
        local('quivron-bibliography.html'), opened=False,
        access='primary chapter not opened; institutional author bibliography opened; observations encountered through Coningham 2002',
        note='Do not treat the local bibliography witness as a copy of the chapter. Searches failed to recover the primary chapter.')
    add('coningham2002',['R. A. E. Coningham'],2002,'Deciphering the Indus Script',
        'In S. Settar and Ravi Korisettar (eds.), Indian Archaeology in Retrospect, Volume II: Protohistory—Archaeology of the Harappan Civilization, pp.81–103. New Delhi: Manohar',
        'https://www.harappa.com/sites/default/files/pdf/Deciphering_the_Indus_Script.pdf',
        ['pp.93–94 (PDF13–14); Quivron reference p.102 (PDF22); publication year/volume confirmed on Harappa record'],
        local('coningham-original.pdf'), note='The separate Mohen Jo Daro reprint uses pp.113–135. Use original folios here; no assumed Antiquity citation.')
    add('miller1997',['Heather M.-L. Miller'],1997,
        'Pottery Firing Structures (Kilns) of the Indus Civilization During the Third Millennium B.C.',
        'In Prudence M. Rice and W. David Kingery (eds.), Prehistory and History of Ceramic Kilns, pp.41–71. Columbus: American Ceramic Society',
        'https://www.harappa.com/sites/default/files/pdf/Miller_PotteryFiringStructuresKilns.pdf',
        ['pp.42–43,47–49,57,66–68; 16 PDF pages OCRed'], local('miller-kilns.pdf'),
        note='Independent kiln synthesis. It describes contemporary firing methods, not a measured disappearance of marks caused by one replacement.')
    add('durrani1988',['F. A. Durrani'],1988,'Excavations in the Gomal Valley (Rehman Dheri Excavation Report No. 1)',
        'Ancient Pakistan VI:1–232', 'https://sites.google.com/uop.edu.pk/ancientpakistan/volumes/volume-vi',
        ['pp.17–18 site; p.25 layer correlation; pp.27–29 phases and ivory object; Figure D p.139 (PDF144); key images sampled'],
        local('durrani1988.pdf'), note='Public PDF located through the official university volume index. Twelve laboratory determinations retained as printed; no recalibration.')
    add('durrani1995',['F. A. Durrani','Ihsan Ali','George Erdosy'],1995,'Seals and Inscribed Sherds of Rehman Dheri',
        'Ancient Pakistan X (1994–95):198–233', 'https://sites.google.com/uop.edu.pk/ancientpakistan/volumes/volume-x',
        ['pp.198–199 function; p.201 item54; p.206 illustration; pp.208–209 counts/interpretation; pp.210–221 catalogue/charts; pp.201,208,216–217 visually checked'],
        local('durrani1995.pdf'), note='314 registered sherds; 190 stratified. Printed phase sign totals add to 163. The 27 difference is unresolved, with units kept visible.')
    add('durrani1995-intro',['F. A. Durrani','Ihsan Ali','George Erdosy'],1995,'Introduction',
        'Ancient Pakistan X (1994–95):i–xiii', 'https://sites.google.com/uop.edu.pk/ancientpakistan/volumes/volume-x',
        ['p.vii: level-to-period mapping, phase chronology and reference to 12 radiocarbon dates; Table1'],
        local('durrani1995-introduction.pdf'))
    add('kenoyer2020',['Jonathan Mark Kenoyer'],2020,'Origin and Development of the Indus Script: Insights from Harappa and other sites',
        'In Kaleemullah Lashari (ed.), Studies on Indus Script, pp.217–236. Karachi: National Fund for Mohenjo-daro',
        'https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script.pdf',
        ['pp.220–221, Table2; pp.225–226, Figure2; p.235 references'],local('kenoyer2020.pdf'),
        note='Table2 groups the Rehman pendant at 2800–2600 BCE. This comparative placement is distinct from Durrani’s context assignments.')
    add('kenoyer-meadow2010-published',['J. Mark Kenoyer','Richard H. Meadow'],2010,'Inscribed Objects from Harappa Excavations 1986–2007',
        'In Asko Parpola, B. M. Pande and Petteri Koskikallio (eds.), Corpus of Indus Seals and Inscriptions, Vol.3, Part1, pp.xliv–lviii. Helsinki: Suomalainen Tiedeakatemia',
        'https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf',
        ['Table1 p.xlv (PDF4); p.li H1521/H1533 (PDF10); p.lii seal motifs (PDF11); p.liv boss comparisons (PDF13)'],
        local('kenoyer-meadow2010-published.pdf'),note='Published folios supplement the earlier preserved author typescript. Same excavation observations are not independent discoveries.')
    add('meadow-kenoyer2005',['Richard H. Meadow','Jonathan Mark Kenoyer'],2005,
        'Excavations at Harappa 2000–2001: New Insights on Chronology and City Organization',
        'In Catherine Jarrige and Vincent Lefèvre (eds.), South Asian Archaeology 2001, pp.207–225. Paris: Éditions Recherche sur les Civilisations / ADPF',
        'https://www.harappa.com/sites/default/files/pdf/Kenoyer2005_Excavations%20at%20Harappa%202000-2001%20New%20insights%20on.pdf',
        ['pp.207–211, Tables1–2 and Fig.4; p.225 references; complete PDF OCRed'],local('meadow-kenoyer2005.pdf'),
        note='Table2 uses Calib4.3 MethodB, 2-sigma. The authors say the beginning of Period2 remains largely undated, p.209.')
    add('kenoyer-meadow1999',['Jonathan Mark Kenoyer','Richard H. Meadow'],1999,'Harappa: New Discoveries on its Origins and Growth',
        'Lahore Museum Bulletin XII(1), January–June:1–12',
        'https://www.harappa.com/sites/default/files/pdf/Kenoyer1999_Harappa%20New%20Discoveries%20on%20its%20origins%20and%20growt.pdf',
        ['pp.3–4 chronology; Figure4 drawing (PDF12), caption p.6 (PDF7), item6 H98-3485/8437-01'],
        local('kenoyer-meadow1999.pdf'))
    add('harappa-hearth-gallery',['Harappa Archaeological Research Project'],None,'Sealing find; Seal impression',
        'Around the Indus in 90 Slides 2, slides136–137, Harappa.com excavation photographs and captions',
        'https://www.harappa.com/slide/sealing-find', ['slide136 find/hearth caption; https://www.harappa.com/indus2/137.html object caption'],
        local('harappa-sealing-find.html'), access='opened both excavation-gallery captions and image-bearing HTML',
        note='Circa2800 BCE is a phase label; these captions provide no radiocarbon lab number or specimen/sample join. Second caption witness harappa-sealing-object.html.')
    add('frenez2018',['Dennys Frenez'],2018,'Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities',
        'In D. Frenez, G. M. Jamison, R. W. Law, M. Vidale and R. H. Meadow (eds.), Walking with the Unicorn: Social Organization and Material Culture in Ancient South Asia, pp.166–193. Oxford: Archaeopress',
        'https://www.harappa.com/sites/default/files/pdf/private-person.pdf', ['p.177 Figure10, visually checked; pp.190,193 references'],
        'research/literature/sources/frenez_2018_private_person.pdf',
        note='Reused anchor-audit witness. Figure10 distinguishes cuneiform item a, Linear Elamite item f and separate Indus-text items.')
    add('frenez2023-caption',['Dennys Frenez'],2023,'Indus Valley: Early Commercial Connections with Central and Western Asia',
        'The Oxford Handbook of the Indus Civilization; public author chapter caption on Harappa.com',
        'https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia',
        ['Image1 (chapter Figure3), items F/G cuneiform; O Linear Elamite, Winkelmann2004 II.1-02'],
        local('frenez2023-caption.html'), access='opened public chapter caption; complete chapter not recovered in this amendment',
        note='Museum credits provide collection-level identity; BnF inventory number remains unrecovered.')
    add('gadd1932',['C. J. Gadd'],1932,'Seals of Ancient Indian Style Found at Ur',
        'Proceedings of the British Academy 18; separately paginated reprint pp.3–22',
        'https://ignca.gov.in/Asi_data/33779.pdf', ['no.1 pp.5–6 (PDF12–13); adjacent examples; source image sampled'],
        'research/root_primary/gadd1932.pdf', note='Reused anchor-audit witness. The Ur cuneiform seal is no.1, BM120573/U7683; no.6 is a different cylinder.')
    add('bm120573',['British Museum'],2026,'stamp-seal', 'Collection online, museum120573; registration1928,1009.56; excavationU7683',
        'https://www.britishmuseum.org/collection/object/W_1928-1009-56',
        ['indexed fields: circa2500 BCE; Diqdiqqah surface; Gadd1932 no.1 pp.5–6'],local('web-14.json'),
        opened=False,access='search-indexed catalogue fields only; direct browser and HTTP opens returned403',
        note='Gadd’s opened primary publication verifies the object independently. Search witness file contains the indexed result; inspect search-log for exact query.')
    add('possehl2006',['Gregory L. Possehl'],2006,'Shu-ilishu’s Cylinder Seal','Expedition 48(1):42–43',
        'https://www.harappa.com/sites/default/files/201402/Shu-ilishus-Cylinder-Seal.pdf',
        ['p.42 dating/provenance; p.43 rollout and inscription discussion'],
        'research/literature/sources/possehl_2006_shu_ilishu.pdf',
        note='Reused witness. Cuneiform interpreter inscription; no aligned Indus text. Author reports conflicting Late Akkadian and UrIII dates.')
    add('louvre-shu-ilishu',['Musée du Louvre'],2026,"Sceau-cylindre : naissance de l'enfant divin",'Collection online, AO22310, record updated23February2026',
        'https://collections.louvre.fr/ark:/53355/cl010147038', ['date Akkad2340–2200 BCE; origin attributed by style; inscriptions; identifiers'],
        local('louvre-shu-ilishu.html'),access='opened complete museum catalogue record',
        note='The museum’s Akkad bracket is a stylistic attribution, not excavated provenance.')
    add('laursen2010',['Steffen Terp Laursen'],2010,
        'The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC',
        'Arabian Archaeology and Epigraphy 21:96–134. DOI:10.1111/j.1600-0471.2010.00329.x',
        'https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf',
        ['Table1 p.100 no.28; p.104 n.4; Fig.9; p.119; p.121 proposed date; pp.133–134 references'],local('laursen2010.pdf'),
        note='No.28 Linear Elamite seal was mistakenly attributed to Bahrain in a later account. Proposed2112–2095 date relies on an assumed restricted Linear Elamite horizon.')
    add('winkelmann1999',['Sylvia Winkelmann'],2000,'Ein Stempelsiegel mit alt-elamischer Strichschrift',
        'Archäologische Mitteilungen aus Iran und Turan 31 (1999):23–32; publication year2000 in author bibliography',
        'https://www.orientarch.uni-halle.de/dept/staff/winkel.htm', ['author bibliography; Laursen2010 Table1 no.28, pp.104,119'],
        opened=False,access='article not opened; author bibliography opened; object encountered through Laursen2010',
        note='Laursen bibliography prints22–32; the institutional bibliography gives23–32. Nominal volume year and release year retained separately.')
    add('winkelmann2004',['Sylvia Winkelmann'],2004,'Seals of the Oasis from the Ligabue Collection', 'Venice: Il Punto',
        'https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia',
        ['catalogueII.1-02 as cited by Frenez2023 Figure3O; Frenez2018 p.193 bibliography'],
        opened=False,access='book not opened; exact item cited in opened Frenez caption',
        note='Book URL not authenticated; supplied URL is the opened citing caption. Do not count 2018/2023 reproductions as separate seals.')
    add('frenez2024-cv',['Dennys Frenez'],2024,'Curriculum Vitae','University of Bologna official CV witness, bibliography and papers in preparation',
        'https://www.unibo.it/it/ateneo/amministrazione-trasparente/consulenti-e-collaboratori/tabella-incarichi-attivi-di-collaborazione-e-di-consulenza-affidati-a-soggetti-esterni/last_years?format=cv&id=42247', ['PDF7 Papers in preparation; PDF5–6 2014 presentations; CV dated10July2024'],
        'research/literature/sources/frenez_cv_official.pdf',access='opened official preserved CV; live title/author searches also performed',
        note='Hybrid identities: Indus-related seals with Sumero-Akkadian cuneiform inscriptions is listed as in preparation in this2024 witness. Live title searches found no final published article; current status is not inferred from the CV alone.')
    add('laursen2026-abstract',['Steffen Terp Laursen','Nabiel Al Shaikh','Claire N. Reeler','Pierre Lombard','Gianni Marchesi'],2026,
        'Stamped Tokens with Cuneiform Inscriptions from Bahrain: New Light on Kingship and the Gods in Early 2nd Millennium BC Dilmun',
        'Journal of Near Eastern Studies85(1):115–145. DOI:10.1086/739820',
        'https://cris.unibo.it/handle/11585/1059790', ['institutional abstract, bibliography, file embargo until1April2027'],
        local('laursen2026-abstract.html'),access='opened institutional abstract via HTTP; full article/plates not opened',
        note='Three tokens impressed by two cuneiform seals. Abstract does not establish Indus-style imagery, exact token dates or paired Indus legends. Kept as a separate Gulf comparator.')
    add('frenez2026-lecture',['Dennys Frenez'],2026,'Ongoing decipherments : Writing in the Indus Civilization - by Dennys Frenez',
        'ILARA online lecture, uploaded3October2026; description title Memorizing Meanings: Archaeological Perspectives on Writing in the Indus Civilisation',
        'https://youtu.be/1i9q17ld_jU', ['17:05–24:00 early sequence; 48:25–48:55 oral/merchant account; 16:20–17:05 forthcoming contact paper'],
        'experiments/2026-10-06-research-program/frenez-talk-check.md', opened=False,
        access='coordinator’s caption-check note opened; video not independently watched; transcript retrieval failure recorded by coordinator',
        note='The retained witness is an authored audit, not a third-party transcript. Place-name correction is a publication-based inference.')
    add('jarrige1995-report',['Catherine Jarrige','Jean-François Jarrige','Richard H. Meadow','Gonzague Quivron'],1995,
        'Mehrgarh: Field Reports 1974–1985 from Neolithic Times to the Indus Civilization',
        'Karachi: Department of Culture and Tourism, Government of Sindh, with French Ministry of Foreign Affairs',
        'https://ehrafarchaeology.yale.edu/traditions/aq43/documents/001', ['catalogue metadata; references/locators through Miller1997 pp.47–49,57,67'],
        opened=False,access='catalogue metadata opened; full excavation report not recovered',
        note='Primary excavation report identified; no claim to have opened its kiln/mark specimen registers.')
    add('audouze-jarrige1979',['Francine Audouze','Catherine Jarrige'],1979,
        'A Third Millennium Pottery-Firing Structure at Mehrgarh and Its Economic Implications',
        'In Maurizio Taddei (ed.), South Asian Archaeology 1977, pp.213–221. Naples: Istituto Universitario Orientale',
        'https://www.harappa.com/sites/default/files/pdf/Miller_PotteryFiringStructuresKilns.pdf', ['citation through Miller1997 p.66; Quivron1980 p.275 footnote3'],
        opened=False,access='original paper not opened; referenced by opened primary mark study and kiln synthesis',
        note='Supplied URL is the citing synthesis. Quivron’s printed p.275 footnote gives213–231, differing from Miller213–221; original pagination remains to audit.')
    return S

def make_rows(labs):
    R=[]
    R.append(row('mehrgarh-pottery1980','Mehrgarh Chalcolithic pre-firing mark sequence', ['pre-firing pottery incisions'],
        [date(-3500,-2500,'excavated PeriodsIV–VII; legacy phase calendar in publication','B','Quivron1980 pp.275–276',
              'Studied sequence reaches approximately3500 to the first half of third millennium; no laboratory specimen join or calibration table recovered.', selected=True)],
        ['quivron1980'],['pp.269,274–279; tables1–3'], repertoire=147,
        repertoire_basis='147 variants grouped into50 categories, p.269; orientations on base fragments are partly arbitrary.',
        basis='Nearly850 marks; distinct marked-vessel/shard total is not given.',images=True,additive=True,sites=['Mehrgarh'],
        claims=['mehrgarh-function-followup','preseal-repertoire-followup'],
        limitations='Count unit is mark observations. Old phase chronology has low calendar strength. Workshop/owner function is an interpretation.',
        observations={'approximate_mark_observations':850,'categories':50,'excavation_seasons':'four,1974–1978'}))
    R.append(row('mehrgarh-nausharo1997','Mehrgarh and Nausharo pooled pre-firing marks, 1997 account', ['pre-firing pottery marks'],
        [date(-3600,-2500,'reported multi-site sequence through Coningham’s citation of Quivron','C','Coningham2002 p.93, citing Quivron1997 p.45',selected=True)],
        ['quivron1997','coningham2002'],['Coningham2002 pp.93–94; primary Quivron locators45,53,55,61'],
        count=1265,kind='reported mark observations',unit='marks, not unique marked objects',
        basis='Pooled count quoted by Coningham; primary chapter unopened. Overlaps Mehrgarh1980 and is excluded from additive coverage.',
        sites=['Mehrgarh','Nausharo'],claims=['mehrgarh-function-followup'],
        limitations='Nausharo-specific count and dates cannot be isolated. RoomCXVIII100 vessels/33 marked/16 signs is retained as a cited observation, without merging it with the1980 room183 vessels/23 marks.',
        observations={'room_CXVIII_vessels':100,'room_CXVIII_marked_vessels':33,'room_CXVIII_sign_types':16}))
    R.append(row('mehrgarh-failed-firing','Mehrgarh failed firing and kiln context', ['jar firing batch with some marked vessels'],
        [date(-2700,-2600,'circa2700 phase attribution; century bracket represents approximate point for audit only','C','Coningham2002 p.93 citing Quivron1997 p.53',
              'Excluded from additive coverage. Original chapter and mark denominator not recovered.'),
         date(None,None,'Quivron1980 printed PeriodIV; later literature calls the failed kiln PeriodVI','D','Quivron1980 p.275; Miller1997 pp.47–49',
              'Phase discrepancy is retained. No date is inferred by reconciling these reports.')],
        ['quivron1980','quivron1997','coningham2002','miller1997','audouze-jarrige1979','jarrige1995-report'],
        ['Quivron1980 p.275; Coningham2002 p.93; Miller1997 pp.47–49'],
        count=142,kind='batch denominator, not marked objects',unit='surviving jars',basis='142 jars in24m²; Miller estimates an original firing load near200. No exact marked subset.',
        sites=['Mehrgarh'],claims=['mehrgarh-function-followup'],
        limitations='The batch can test a production function once vessel/mark registrations are recovered. It supplies no observed mark-frequency comparison across kiln technologies.',
        observations={'batch_area_square_metres':24,'estimated_original_vessels':200}))
    R.append(row('nausharo-kiln-II','Nausharo PeriodII firing contexts, mark-join acquisition target', ['open-air firing areas','updraft kilns'],
        [date(-2500,-2400,'published archaeological phase for firing structures; no marked-object join','D','Miller1997 pp.48–49',
              'Context date is not an authenticated mark date and is unselected.')],
        ['miller1997','quivron1997'],['Miller1997 pp.48–49; Quivron1997 chapter not recovered'],
        sites=['Nausharo'],claims=['mehrgarh-function-followup'],
        limitations='Open-air and updraft technologies occur contemporaneously here. Marked-object counts and repertoire-by-kiln frequencies are missing.'))
    R.append(row('rehman-dheri-stratified','Rehman Dheri stratified inscribed sherds, 1976–82 and1991', ['incised sherds; catalogue also mentions marked terracotta items'],
        [date(-3300,-1900,'registered marked material in stratified PeriodsI–III; site phase calendar based on12 legacy radiocarbon determinations','B','Durrani et al.1995 p.208; Introduction p.vii; Durrani1988 FigureD p.139',
              'Calendar bracket from1995 Introduction. Legacy calibrated ranges retained separately; calibration curve/probability not stated in FigureD.',selected=True,labs=labs),
         date(-3340,-1900,'earlier phase chronology with IA starting3340','B','Durrani1988 pp.27–29',
              'Earlier alternative retained; no averaging of dates.')],
        ['durrani1988','durrani1995','durrani1995-intro'],['p.208 corpus; pp.210–221 catalogue/charts; pp.216–217 phase totals; Introduction p.vii; FigureD p.139'],
        count=190,kind='exact',unit='stratified inscribed sherds as reported p.208',basis='314 registered inscribed sherds,190 stratified;124 lack stratified placement. Do not allocate190 across centuries using the inconsistent sign totals.',
        repertoire=94,repertoire_basis='Derived numbered main catalogue entries1–94, pp.210–216 and charts; letter variants and normalization are separate, so94 is not an authenticated normalized repertoire.',
        images=True,additive=True,sites=['Rehman Dheri'],claims=['rehman-continuity-followup'],
        limitations='Wide phase bracket gives possible coverage only. Printed phase totals refer to signs, total163, and do not reconcile with190 stratified sherds;27 difference unresolved.',
        observations={'registered_sherds':314,'stratified_sherds':190,'unstratified_or_surface_difference':124,'printed_phase_signs':{'IA':7,'IB':12,'II':14,'IIIA':19,'IIIB':111}}))
    R.append(row('rehman-dheri-pendant54','Rehman Dheri rectangular bone/ivory seal or pendant, catalogue54', ['rectangular carved bone/ivory object; seal/amulet function disputed'],
        [date(-3100,-2850,'explicit PeriodIB attribution in excavation report','B','Durrani1988 p.28', 'Conflicts with later catalogue level19.'),
         date(-3300,-3100,'catalogue Level19 maps to IA; subphase endpoint uses earlier published IA/IB boundary','C','Durrani et al.1995 p.201 item54; Introduction p.vii; Durrani1988 p.27',
              'Later catalogue BIV25 Layer6 Level19; conflicting earlier layer correlation prevents selection.'),
         date(-2850,-2500,'local Layer6 correlated with main Layer12, PeriodII','C','Durrani1988 p.25', 'This correlation conflicts with the object’s PeriodIB prose and1995 Level19.'),
         date(-2800,-2600,'comparative table placement','C','Kenoyer2020 Table2 p.221', 'Not a new radiocarbon measurement or reconciliation.')],
        ['durrani1988','durrani1995','durrani1995-intro','kenoyer2020','kenoyer-meadow2010-published'],
        ['Durrani1988 pp.25,28; Durrani et al.1995 pp.198–201,206; Kenoyer2020 pp.221,225–226'],
        count=1,kind='exact',unit='physical object',basis='Catalogue54,BIV25,Layer6,Level19;31×28×4.5mm; paired goats and scorpions/frog motifs.',
        images=True,additive=True,sites=['Rehman Dheri'],claims=['preseal-repertoire-followup','rehman-continuity-followup'],
        limitations='No dating alternative selected. The report calls it ivory; the1995 catalogue calls it bone. The object is rectangular, not a verified button seal. Caption-to-object match is inferred, not independently checked against lecture imagery.'))
    R.append(row('harappa-ravi-prefire-subset','Harappa Ravi four pre-firing sherds, subset audit', ['pre-firing pottery marks'],
        [date(-3700,-2800,'excavated Ravi phase; approximate chronology based on calibrated radiocarbon','B','Kenoyer/Meadow2010 Table1',strength='moderate',selected=True),
         date(-3300,-2800,'earlier Ravi bracket','B','Kenoyer2006 Ravi section',strength='moderate')],
        ['kenoyer2006','kenoyer-meadow2010-published'],['Kenoyer2006 Ravi section and Figure3;2010 Table1'],
        count=4,kind='exact',basis='Four pre-firing sherds already included in parent harappa-ravi17; excluded to prevent duplication.',
        images=True,sites=['Harappa'],claims=['harappa-early-followup'],limitations='Parent count13 post-firing+4 pre-firing already contributes coverage.'))
    R.append(row('harappa-ravi-bone1521','Harappa Ravi bone button-seal fragment H1521', ['perforated carved bone fragment'],
        [date(-3700,-2800,'Ravi phase attribution of carved fragment','B','Kenoyer/Meadow2010 p.li and Table1',strength='moderate',selected=True)],
        ['kenoyer2006','kenoyer-meadow1999','kenoyer-meadow2010-published'],['2010 p.li,H1521;1999 Figure3 item8,H98-3503/8514-07'],
        count=1,kind='exact',basis='One illustrated bone fragment; separate object from parent Ravi pottery.',images=True,additive=True,sites=['Harappa'],
        claims=['harappa-early-followup'],limitations='Weathering/burning obscures design; stamping use versus ornament remains unresolved. No confirmed Indus-sign text on the fragment.'))
    R.append(row('harappa-kot-diji-hearth-sealing','Harappa Kot Diji hearth sealing H98-3485/8437-01', ['low-fired clay sealing with script-like signs'],
        [date(-2800,-2600,'excavated Kot Diji context, phase calendar based on calibrated radiocarbon','B','Kenoyer2006 Kot Diji section Figure5:9; Kenoyer/Meadow2010 Table1',
              'Gallery labels circa2800 BCE. No lab number/sample determination directly joined to this sealing was recovered.',strength='moderate',selected=True),
         date(None,None,'lecture claim that fireplace was radiocarbon-dated to about2800 BCE','D','Frenez lecture17:05–24:00 through coordinator note',
              'Direct specimen→hearth→sample/lab/calibration join not authenticated.')],
        ['kenoyer2006','kenoyer-meadow1999','kenoyer-meadow2010-published','meadow-kenoyer2005','harappa-hearth-gallery','frenez2026-lecture'],
        ['Kenoyer2006 Figure5:9 and Kot Diji section;1999 Figure4 item6 caption p.6; gallery136–137;2005 p.209/Table2'],
        count=1,kind='exact',basis='Registered terracotta sealing H98-3485/8437-01,1999 Figure4 item6. One observed specimen, not entire sealing corpus.',
        images=True,additive=True,sites=['Harappa'],claims=['harappa-early-followup'],
        limitations='No before2800 absolute endpoint authenticated. 2005 report says beginning of Period2 largely undated. Do not map a site carbon sample to registration8437 without the field register.'))
    R.append(row('harappa-kot-diji-elephant1533','Harappa Kot Diji unfinished elephant seal H1533', ['unfinished steatite intaglio seal with animal motif'],
        [date(-2800,-2600,'sealed stratigraphic context dated by ceramic associations','B','Kenoyer/Meadow2010 p.li,H1533;2005 p.211 Figure4.1',
              'Phase assignment is explicit; no direct specimen radiocarbon join.',strength='moderate',selected=True)],
        ['kenoyer-meadow2010-published','meadow-kenoyer2005'],['2010 p.li,H1533;2005 p.211/Figure4.1'],
        count=1,kind='exact',basis='One unfinished elephant-design seal; separate from pottery and sealing.',images=True,additive=True,sites=['Harappa'],
        claims=['harappa-early-followup'],limitations='Upper portion missing; no script preserved on this object. Its animal motif counts as a mark, while written repertoire inference requires the other evidence.'))
    R.append(row('contact-period-foreign-legends','Contact-period seal examples with cuneiform or Linear Elamite legends',
        ['Indus-style Ur stamp with cuneiform','BnF Indus-style stamp with cuneiform','round Indus-style stamp with Linear Elamite','Shu-ilishu cuneiform cylinder as contact comparator'],
        [date(None,None,'item-specific stylistic, palaeographic and provenance assessments in contact-items.json','D','contact-items.json',
              'No combined contact-corpus date; individual alternatives are kept separate.')],
        ['gadd1932','bm120573','frenez2018','frenez2023-caption','laursen2010','winkelmann1999','winkelmann2004','possehl2006','louvre-shu-ilishu','frenez2024-cv','frenez2026-lecture'],
        ['Gadd no.1 pp.5–6;Frenez2018 Figure10a/f;2023 Figure3F/G/O;Laursen Table1 no.28;Possehl42–43;LouvreAO22310'],
        count=4,kind='selected published examples',unit='four identified physical examples, not a complete corpus',
        basis='Four case records; repeated reproductions of one seal are deduplicated. Shu-ilishu is a comparator, not an Indus-style bilingual.',
        images=True,region='Adjacent western contact regions',sites=['Ur/Diqdiqqah','unknown collection provenance','unknown southwestern Iran; attributed','unknown Mesopotamian provenance'],
        claims=['contact-legends-followup'],adjacent=True,
        limitations='Excluded from South Asian coverage; no paired aligned Indus and foreign-script text authenticated. Link to existing external_phonetic_anchor_audit.md; forthcoming paper unverified.'))
    R.append(row('bahrain-cuneiform-tokens2026','Bahrain published cuneiform token cohort, abstract-level comparator',
        ['three clay tokens bearing impressions from two cuneiform seals'],
        [date(None,None,'Early2nd millennium/Middle Bronze Age label in primary title and abstract; precise token-context dates not recovered','D','Laursen et al.2026 abstract',
              'No numeric calendar interval inferred from the broad period label.')],
        ['laursen2026-abstract'],['institutional abstract and embargo notice; DOI10.1086/739820'],
        count=3,kind='exact',unit='tokens as reported in abstract',basis='Three tokens, two seal matrices. The two matrices are not added as recovered physical objects.',
        region='Adjacent western contact regions',sites=['Bahrain; exact token find contexts not recovered in abstract'],
        claims=['contact-legends-followup'],adjacent=True,
        limitations='Full article/plates unavailable in this record. Indus-style imagery and any Indus text are unverified. No claim that these are Frenez’s forthcoming-paper objects.'))
    return R

def make_claims():
    def c(cid,author,sids,loc,claim,intermediate,missing,assessment):
        return dict(id=cid,authors=author,source_ids=sids,locations=loc,claim=claim,
                    intermediate_evidence=intermediate,missing=missing,assessment=assessment)
    return [
      c('mehrgarh-function-followup','Gonzague Quivron; R.A.E.Coningham; Dennys Frenez',
        ['quivron1980','quivron1997','coningham2002','miller1997','frenez2026-lecture'],
        'Quivron1980 pp.275,278;Coningham2002 pp.93–94 citing Quivron1997 pp.53,55,61;lecture17:05–24:00',
        'Marks distinguish workshops or ownership in a communal firing; Frenez associates decline with a new kiln type.',
        'Marked failed-firing jars, varied vessel shapes with shared marks, storage batches, frequency decline; independent kiln typology.',
        'Primary1997 chapter, vessel/mark registers, marked/unmarked denominators by kiln and date, direct replacement-versus-decline comparison.',
        'Production/owner hypotheses have an identified precedent. The claimed causal kiln change is not authenticated by recovered mark-frequency evidence.'),
      c('preseal-repertoire-followup','Dennys Frenez; comparisons by Quivron, Durrani and Kenoyer',
        ['frenez2026-lecture','quivron1980','durrani1988','durrani1995','kenoyer2020'],
        'lecture17:05–24:00;Quivron1980 pp.275,279;Durrani1988 p.28;Kenoyer2020 pp.220–226',
        'Early pottery mark repertoires move onto seals by late fourth to early third millennium.',
        'Mehrgarh mark charts; early seals and Rehman rectangular object; Harappa later seals/sealings.',
        'A frozen sign-level mapping and rare compound sequences across independent dated objects; reconciliation of Rehman object context.',
        'Quivron explicitly distinguishes contemporary seal motifs from the pottery-mark repertoire. Simple geometric overlap can be tested, but the complete same-repertoire assertion remains unverified.'),
      c('rehman-continuity-followup','F.A.Durrani; F.A.Durrani,I.Ali,G.Erdosy',
        ['durrani1988','durrani1995','durrani1995-intro'],
        '1988 p.28;1995 pp.208–209,216–217',
        'Some Rehman marks antecede Indus signs; animal-plus-symbol designs and apparent right-to-left layout suggest continuity.',
        '314 registered sherds,190 stratified, drawings and level entries; rectangular bone/ivory object.',
        'Normalized phase frequencies, repaired count reconciliation, independent direction annotations, shape-complexity controls and dated later intermediates.',
        'The1995 authors report no clear simple-to-composite progression. Their direction inference is an attributed hypothesis to test.'),
      c('harappa-early-followup','Jonathan Mark Kenoyer and Richard H.Meadow; Dennys Frenez',
        ['kenoyer2006','kenoyer-meadow1999','kenoyer-meadow2010-published','meadow-kenoyer2005','harappa-hearth-gallery','frenez2026-lecture'],
        '2006 Ravi/Kot Diji sections;2010 p.li/Table1;2005 p.209;gallery136–137;lecture17:05–24:00',
        'Shared signs on pottery and seals/sealings mark an early writing stage; lecture places it before2800 BCE and a dated fireplace near2800.',
        'Ravi marked pottery/bone fragment; Kot Diji sherd sequences, unfinished elephant seal and clay sealing.',
        'Lab/sample/feature join for the hearth sealing, calibrated uncertainty and dated subphase placement demonstrating a before2800 endpoint.',
        'Recovered publications place intaglio seals and seal-impressed clay in2800–2600 BCE. The gallery supports a hearth find and circa2800 phase label, without authenticating the direct radiocarbon assertion.'),
      c('oral-merchants-followup','Dennys Frenez; compared with early Brahmi assessments already in Package E',
        ['frenez2026-lecture','coningham1996','deraniyagala','salomon1998','rajan-sivanantham2026-I'],
        'lecture48:25–48:55;parent rows anuradhapura,porunthal-I,kodumanal,keeladi,ashoka-brahmi;Salomon origins pp.19–30',
        'Later Indian priests preferred oral transmission and Buddhist merchants reintroduced writing in the fifth century BCE.',
        'Lecture historical account; distinct pre-Ashokan pottery assessments and later historical edict endpoint.',
        'Direct evidence identifying the agents/date of reintroduction, chronology and mechanism of the intervening change, plus specimen/sample joins for earlier pottery.',
        'Chronology constrains when writing is attested. It does not identify priests or merchants as the cause, or demonstrate an Indus transmission chain. Treat the fifth-century statement as Frenez’s account.'),
      c('contact-legends-followup','Dennys Frenez; C.J.Gadd; Steffen Terp Laursen; Gregory L.Possehl',
        ['frenez2026-lecture','frenez2024-cv','frenez2018','frenez2023-caption','gadd1932','laursen2010','possehl2006','louvre-shu-ilishu','laursen2026-abstract'],
        'lecture16:20–17:05;Frenez2018 Figure10;2023 Figure3;contact-items.json',
        'Indus-style seals carry cuneiform or Linear Elamite; Frenez reports a forthcoming study.',
        'Ur cuneiform stamp, BnF stamp, separate Linear Elamite stamp and interpreter cylinder; independently published images and descriptions.',
        'Published final forthcoming paper, complete specimen IDs/provenance for collection items, paired repeated Indus and known-script legends with externally checked alignments.',
        'Four individually illustrated cases supply no authenticated bilingual or phonetic correspondence. A separate2026 Bahrain abstract reports three cuneiform tokens without establishing Indus imagery/text. Existing anchor audit is reused, not superseded.')
    ]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True,help='Fresh directory inside amendment; may be inputs-rebuilt-01')
    a=p.parse_args(); out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists(): p.error('Choose a fresh output directory.')
    temp=RAW/'tmp';temp.mkdir(exist_ok=True)
    for key in ('TMP','TEMP','MPLCONFIGDIR'):os.environ[key]=str(temp)
    labs=['PRL-675','PRL-676','WIS-1697','WIS-1698','WIS-1699','WIS-1700','PRL-674','PRL-673','WIS-1701','WIS-1702','BM-2062','BM-2063']
    base_rows=read(BASE/'evidence-table.json')['rows'];new_rows=make_rows(labs)
    base_sources=read(BASE/'sources.json')['sources'];new_sources=make_sources()
    base_claims=read(BASE/'continuity-claims.json')['claims'];new_claims=make_claims()
    rows=base_rows+new_rows;sources=base_sources+new_sources;claims=base_claims+new_claims
    assert rows[:42]==base_rows and len(base_rows)==42
    assert len({r['id'] for r in rows})==len(rows)
    assert len({s['id'] for s in sources})==len(sources)
    assert len({c['id'] for c in claims})==len(claims)
    out.mkdir()
    write(out/'evidence-table.json',dict(status='Exploratory',schema_version=1,amendment_date='2026-10-07',rows=rows))
    write(out/'sources.json',dict(status='Exploratory',sources=sources))
    write(out/'continuity-claims.json',dict(status='Exploratory',claims=claims))
    write(out/'added-rows.json',dict(status='Exploratory',parent_rows_unchanged=42,rows=new_rows))
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'evidence-table.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
    write(out/'build-verification.json',dict(status='Verified computation',parent_rows_unchanged=len(base_rows),
        parent_sources_unchanged=len(base_sources),parent_claims_unchanged=len(base_claims),
        added_rows=len(new_rows),added_sources=len(new_sources),added_claims=len(new_claims),
        baseline_inputs_sha256={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ['evidence-table.json','sources.json','continuity-claims.json']}))
    print(json.dumps({'rows':len(rows),'sources':len(sources),'claims':len(claims)}))

if __name__=='__main__':main()
