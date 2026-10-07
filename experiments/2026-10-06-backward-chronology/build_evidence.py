"""Curated source assessments, not a transcription of third-party catalogues.

Run from the repository root. Refuses to replace an existing evidence endpoint.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-backward-chronology'
SOURCES = []
ROWS = []

def source(id, authors, year, title, venue, url, access, witness=None, locations=None, note=''):
    item = dict(id=id, authors=authors, year=year, title=title, venue=venue, url=url,
                access_status=access, opened=access.startswith('opened'),
                locations_reviewed=locations or [], note=note,
                rights_status='rights-unverified; payload local-only')
    if witness:
        path = ROOT / witness
        item.update(local_witness=witness, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    SOURCES.append(item)

source('kenoyer2006',['Jonathan Mark Kenoyer'],2006,
       'The Origin, Context and Function of the Indus Script: Recent Insights from Harappa',
       'In Toshiki Osada (ed.), Proceedings of the Pre-symposium of RIHN and 7th ESCA Harvard-Kyoto Roundtable, pp. 9–27',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer2006_The%20Origin%2C%20Context%20and%20Function%20of%20the%20Indus%20Sc.pdf',
       'opened full PDF; OCR and selected page images', 'data/raw/2026-10-06-backward-chronology/kenoyer2006.pdf',
       ['Ravi and Kot Diji sections; Late Harappa section; figures'],
       'The preserved excerpt has two printed pages on some PDF pages. Use section names with PDF/OCR locators.')
source('kenoyer-meadow2010',['J. Mark Kenoyer','Richard H. Meadow'],2010,
       'Inscribed Objects from Harappa Excavations 1986–2007',
       'In Asko Parpola, B. M. Pande and Petteri Koskikallio (eds.), Corpus of Indus Seals and Inscriptions 3, New Material, Untraced Objects, and Collections Outside India and Pakistan, Part 1: Mohenjo-daro and Harappa; opened author excerpt, pp. 1–15',
       'https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf',
       'opened full author excerpt', 'data/raw/2026-10-06-backward-chronology/kenoyer-meadow2010.pdf',
       ['PDF pp. 2–4, Table 1 and dating footnote; Harappan periods; late deposits'])
source('kenoyer2009',['Jonathan Mark Kenoyer'],2009,
       'Indus Seals: An overview of Iconography and Style',
       'Ancient Sindh 9 (nominal 2006–2007), pp. 7–30',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer2009%20Indus%20Seals_0.pdf',
       'opened full PDF; OCR', 'data/raw/2026-10-06-backward-chronology/kenoyer2009.pdf',
       ['PDF pp. 8–9, 19; printed pp. 10–11 and figure captions'],
       'Harappa hosts the file as Kenoyer2009; the journal cover carries 2006–2007. Both are retained.')
source('lal1960',['B. B. Lal'],1960,
       'From the Megalithic to the Harappa: Tracing Back the Graffiti on the Pottery',
       'Ancient India 16, pp. 4–24, plates I–XXXIV', 'https://ignca.gov.in/Asi_data/18414.pdf',
       'opened original issue; OCR and page images', 'data/raw/2026-10-06-backward-chronology/lal1960.pdf',
       ['PDF pp. 11–65; printed pp. 4–24; p. 21 visually checked'],
       'Original title says Harappa. Article received 20 October 1960, p. 24. The 2026 Tamil bibliography gives 1962; use the original issue date.')
source('rao1963',['S. R. Rao'],1963,
       'Excavation at Rangpur and Other Explorations in Gujarat',
       'Ancient India 18–19 (1962–1963), pp. 5–207; contributions by B. B. Lal, Bhola Nath, S. S. Ghosh and Krishna Lal',
       'https://ignca.gov.in/Asi_data/40421.pdf', 'opened original issue; selected OCR pages',
       'data/raw/2026-10-06-backward-chronology/rangpur-original.pdf',
       ['Contents; chronology pp. 25–28; social conditions p. 48; graffiti pp. 128–137'],
       'Historical chronology is retained as an author estimate, not substituted for a modern calibrated sequence.')
source('thapar1967',['B. K. Thapar'],1967,
       'Prakash 1955: A Chalcolithic Site in the Tapti Valley',
       'Ancient India 20–21 (nominal 1964–1965; printed 1967), pp. 5–167; contributions by V. T. Athavale, K. Ramesh Rao and R. Shahi',
       'https://ignca.gov.in/Asi_data/45764.pdf', 'opened original issue; selected OCR pages',
       'data/raw/2026-10-06-backward-chronology/prakash1967.pdf',
       ['Chronology pp. 21–24; graffiti pp. 66–68, fig. 19; contents and imprint'])
source('sali1986',['S. A. Sali'],1986,'Daimabad 1976–79',
       'Memoirs of the Archaeological Survey of India 83, New Delhi: ASI',
       'https://asi.nic.in/admin/publications/ePublicationReportsDetails/download/49',
       'opened full excavation report', 'data/raw/2026-10-06-backward-chronology/asi-daimabad49.pdf',
       ['Chronology pp. 206–211, Table 2; graffiti p. 248; seals and inscriptions pp. 504–506'],
       'MASCA-corrected brackets and conventional brackets are separate source assessments; neither is a new calibration.')
source('sundaresh-gaur1998',['Sundaresh','A. S. Gaur'],1998,'Archaeology of Bet Dwarka Island',
       'Man and Environment 23(2), pp. 77–86',
       'https://www.ancientportsantiques.com/wp-content/uploads/Documents/PLACES/IndOc-Gulf/GujaratBetDwarka-Sundaresh1998.pdf',
       'opened full author-paper copy; OCR', 'data/raw/2026-10-06-backward-chronology/bet-dwarka1998-recovered.pdf',
       ['pp. 77, 79, 81, 85; figs. 2–4'], 'NIO direct download served a bot challenge; recovered paper from a mirror.')
source('jarrige-enault1976',['Jean-François Jarrige','Jean-François Enault'],1976,
       'Fouilles de Pirak - Baluchistan','Arts Asiatiques 32, pp. 29–70; doi:10.3406/arasi.1976.1095',
       'https://www.persee.fr/doc/arasi_0004-3958_1976_num_32_1_1095',
       'opened publisher record and first-page text', 'data/raw/2026-10-06-backward-chronology/pirak1976.html',
       ['Publisher metadata and opening page'], 'Pirak seal dates/images below are recovered through Kenoyer2009, not the full excavation article.')
source('kenoyer2004',['Jonathan Mark Kenoyer'],2004,
       'Wheeled Vehicles of the Indus Valley Civilization of Pakistan and India',
       'Die Karren der Induskultur Pakistans und Indiens, in M. Fansa and S. Burmeister (eds.), Rad und Wagen: Der Ursprung einer Innovation, pp. 87–106, Mainz: Philipp von Zabern; opened English author manuscript',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer2004_Wheeled%20Vehicles%20of%20the%20Indus%20Valley%20Civilizatio.pdf',
       'opened full author manuscript', 'data/raw/2026-10-06-backward-chronology/kenoyer2004-vehicles.pdf',
       ['PDF p. 17, Inamgaon cart graffito caption'])
source('mahadevan2001',['Iravatham Mahadevan'],2001,
       'The Indus-Like Symbols on Megalithic Pottery: New Evidence',
       'Studia Orientalia 94, pp. 379–386', 'https://journal.fi/store/article/download/43982/11036',
       'opened full journal PDF', 'data/raw/2026-10-06-backward-chronology/mahadevan2001.pdf',
       ['pp. 379, 382–384; Sulur dish and pair comparisons'])
source('rajan-sivanantham2025',['K. Rajan','R. Sivanantham'],2025,
       'Indus Signs and Graffiti Marks of Tamil Nadu: A Morphological Study',
       'Tamil Nadu State Department of Archaeology; opened eight-page brochure',
       'https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2025/08/TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study.pdf',
       'opened full eight-page brochure; reused local witness',
       'data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf',
       ['Whole brochure, counts and comparison statements'],
       'The available file is a brochure, not a recovered full monograph. Its population differs from the digital portal and 2026 catalogue.')
source('rajan-sivanantham2026-I',['K. Rajan','R. Sivanantham'],2026,
       'Inscribed Potsherds of Tamil Nadu - Graffiti and Tamiḻi, Volume I',
       'Chennai: Department of Archaeology, Government of Tamil Nadu, publication 366; ISBN 978-81-977842-3-1',
       'https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2026/03/TVA_TVA_BOK_062969/upload_primary_20260302113351638_20260302111421.pdf',
       'opened full PDF; reused local witness',
       'data/raw/2026-10-02-connections-and-priority/south-india/inscribed-potsherds-vol1-2026.pdf',
       ['pp. 56–57, 69–74, 102, 167, 181–194, 227–229, 263–265, 295–301'],
       'Printed main-text page = PDF page minus 39. Images and specimen tables extend beyond the reviewed narrative.')
source('rajan-sivanantham2026-II',['K. Rajan','R. Sivanantham'],2026,
       'Inscribed Potsherds of Tamil Nadu - Graffiti and Tamiḻi, Volume II',
       'Chennai: Department of Archaeology, Government of Tamil Nadu, publication 366; ISBN 978-81-977842-3-1',
       'https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2026/03/TVA_TVA_BOK_062968/upload_primary_20260302120759232_20260302110011.pdf',
       'opened full PDF; reused local witness',
       'data/raw/2026-10-02-connections-and-priority/south-india/inscribed-potsherds-vol2-2026.pdf',
       ['Catalogue examples; bibliography pp. 1203–1205'], 'Catalogue exists with photographs/drawings; specimen-to-date reconstruction is unfinished.')
source('coningham1996',['R. A. E. Coningham','F. R. Allchin','C. M. Batt','D. Lucy'],1996,
       'Passage to India? Anuradhapura and the Early Use of the Brahmi Script',
       'Cambridge Archaeological Journal 6(1), pp. 73–97; doi:10.1017/S0959774300001608',
       'https://www.cambridge.org/core/journals/cambridge-archaeological-journal/article/abs/passage-to-india-anuradhapura-and-the-early-use-of-the-brahmi-script/DAAA2514FB08E1DDE3FAFF2171AB097B',
       'opened publisher abstract via web', locations=['Abstract: beginning of fourth century BCE'],
       note='Full article was not recovered; Cambridge direct request and Durham repository returned access failures. Online 2008 date is not publication year.')
source('deraniyagala',['S. U. Deraniyagala'],None,
       'Early Man and the Rise of Civilisation in Sri Lanka: The Archaeological Evidence',
       'Authored overview hosted at vedda.org; undated page citing The Prehistory of Sri Lanka (1992)',
       'https://www.vedda.org/deraniyagala.htm', 'opened full authored web overview',
       'data/raw/2026-10-06-backward-chronology/deraniyagala-overview.html',
       ['Early Historic period: writing; Protohistoric Iron Age: Ibbankatuwa'],
       'Anuradhapura 600–500 BCE is an alternative assessment; sample table and marked contexts not recovered here.')
source('salomon1998',['Richard Salomon'],1998,
       'Indian Epigraphy: A Guide to the Study of Inscriptions in Sanskrit, Prakrit, and the Other Indo-Aryan Languages',
       'New York and Oxford: Oxford University Press', 'https://academic.oup.com/book/49774',
       'opened full book PDF from mirror', 'data/raw/2026-10-06-backward-chronology/salomon1998-book.pdf',
       ['pp. 10–13, 19–30, 34–36, 46–47, 131, 133; appendix images'],
       'Local mirror https://rapeutation.com/salomonindianepigraphy.pdf. Original origin-theory works are reviewed through this book, not asserted to have been opened.')
source('changizi2006',['Mark A. Changizi','Qiong Zhang','Hao Ye','Shinsuke Shimojo'],2006,
       'The Structures of Letters and Symbols throughout Human History Are Selected to Match Those Found in Objects in Natural Scenes',
       'The American Naturalist 167(5), pp. E117–E139; doi:10.1086/502806',
       'https://www.journals.uchicago.edu/doi/full/10.1086/502806',
       'opened full publisher HTML via web', locations=['A Topological Notion of Shape: Configuration Types; Human Visual Signs Possess a Characteristic Signature Configuration Distribution'],
       note='Full text reached through web tool; direct PDF guesses failed and direct publisher HTTP was 403. Paper uses 36 types in the catalogue and 32 three-segment types for primary comparisons.')

def date(start, end, method, grade, location, note='', labs=None, measurement=None, selected=True, strength=None):
    return dict(start_year=start, end_year=end, method=method, grade=grade,
                source_location=location, note=note, lab_numbers=labs or [],
                calendar_strength=strength or {'A':'high','B':'moderate','C':'low','D':'unresolved'}[grade],
                published_measurement=measurement, selected_for_coverage=selected)

def row(id, label, region, sites, objects, sources, locations, dates=None,
        count=None, count_basis='No marked-object total recovered.', repertoire=None,
        repertoire_basis='No repertoire total recovered.', images=False,
        claims=None, limitations='', include=True, count_kind='exact', adjacent=False):
    ROWS.append(dict(id=id, label=label, region=region, sites=sites, object_classes=objects,
        marked_object_count=count, count_kind=count_kind if count is not None else 'unknown',
        count_unit='marked objects', count_basis=count_basis, repertoire_size=repertoire,
        repertoire_basis=repertoire_basis, dating_assessments=dates or [],
        source_ids=sources, source_locations=locations, image_corpus_verified=images,
        access='See linked source access_status; third-party payloads remain local-only.',
        continuity_claim_ids=claims or [], limitations=limitations,
        include_in_additive_coverage=include, adjacent_region=adjacent,
        status='Exploratory'))

K6='kenoyer2006'; K10='kenoyer-meadow2010'; K9='kenoyer2009'; L='lal1960'; T='thapar1967'; R='rao1963'; S='sali1986'; TN='rajan-sivanantham2026-I'; SAL='salomon1998'
row('harappa-ravi','Harappa Ravi phase','Indus northwest',['Harappa'],['pre-firing pottery marks','post-firing pottery graffiti'],[K6,K10],
    ['2006 Ravi section, OCR PDF pp. 3–4; 2010 PDF p. 2 Table 1'],
    [date(-3700,-2800,'stratigraphic phase; approximate calendar chronology based on calibrated radiocarbon','B','2010 Table 1', 'Count is a 2006 excavation snapshot, not a total for every Ravi context.'),
     date(-3300,-2800,'earlier published phase bracket','B','2006 Ravi section',selected=False)],17,
    '2006 reports 13 post-firing and 4 pre-firing sherds; categories are disjoint.',images=True,claims=['harappa-development'])
row('harappa-kot-diji','Harappa Kot Diji phase','Indus northwest',['Harappa'],['marked pottery','seals','sealings'],[K6,K10],
    ['2006 Kot Diji section; 2010 Table 1'],[date(-2800,-2600,'stratigraphy; calibrated-radiocarbon phase chronology','B','2010 Table 1')],95,
    '95 marked sherds from unmixed contexts in 2006; count excludes other object classes and mixed sherds.',images=True,claims=['harappa-development'])
row('harappa-mature','Harappa Mature phase','Indus northwest',['Harappa'],['seals','tablets','pottery','tools','ornaments'],[K10,K6],
    ['2010 Table 1 and Harappan periods; 2006 figures'],[date(-2600,-1900,'excavated phase chronology based on calibrated radiocarbon','B','2010 Table 1', 'Subphases 3A 2600–2450, 3B 2450–2200, 3C 2200–1900 BCE.')],images=True,claims=['harappa-development'])
row('mehrgarh-button-seals','Mehrgarh early button seals','Indus northwest',['Mehrgarh'],['terracotta seals','bone seals','stone seals','pendant'],[K9],
    ['printed p. 11, fig. 2 captions (PDF p. 19)'],[date(-3300,-2600,'excavated phase attribution V–VII, figure-caption calendar brackets','B','fig. 2', 'Narrative says most 3300–2800; pictured Period VII examples extend to 2600. No object total inferred from illustrations.')],images=True,claims=['stepped-cross'])
row('harappa-late','Harappa late deposits / Cemetery H phase','Indus northwest',['Harappa'],['possible pottery graffiti','geometric button seals'],[K6,K10],
    ['2006 Late Harappa section; 2010 late deposits and Table 1'],[date(-1900,-1700,'author phase estimate; tentative identification of graffiti','C','2006 Late Harappa section', 'Later occupation to <1300 in 2010 does not establish that the possible graffiti span that period.')],images=False,claims=['harappa-development'],limitations='Few possible examples; disturbance and residual material. Cemetery H pottery dates cannot authenticate every incision.')
row('jhukar','Jhukar geometric seals','Indus northwest',['Chanhudaro','Mohenjo-daro'],['button seals with geometric motifs'],[K9],
    ['printed pp. 10–11'],[date(-1900,-1300,'broad Late Harappa cultural attribution','C','printed pp. 10–11', 'Not an independently dated Jhukar mark sequence.')],images=False,claims=['stepped-cross'],limitations='Opened account describes geometric seals, not a recovered corpus of Jhukar script inscriptions.')
row('pirak','Pirak button and compartmented seals','Indus northwest',['Pirak'],['terracotta button seal','bronze compartmented seal'],[K9,'jarrige-enault1976'],
    ['Kenoyer printed p. 11; fig. 3, PDF p. 19'],[date(-1800,-1300,'excavated phase attribution summarized in scholarly review','B','Kenoyer p. 11 and fig. 3', 'Fig. 3a Period IIIA, 3b Period II. Full original article not recovered.')],2,
    'Two pictured specimens; an illustrated subset, not the site total.',images=True,claims=['stepped-cross'])
row('rangpur','Rangpur pottery graffiti','Gujarat',['Rangpur'],['incised pottery'],[R,TN],
    ['Rao pp. 25–28, 48, 128–137, figs. 47–49; Rajan/Sivanantham p. 264'],
    [date(-2000,-800,'historical author chronology for stratified Periods IIA–III','B','Rao chronology pp. 25–28', 'IIA 2000–1500, IIB 1500–1100, IIC 1100–1000, III 1000–800 BCE. Author infers elapsed centuries from deposit thickness; not modern calibration.',strength='low')],222,
    'Original report p. 130: 26 figurative + 188 linear + 8 compound-bearing potsherds = 222. This replaces the later review\'s approximate over-100 statement before computation.',images=True,claims=['lal-bridge'],limitations='Most marks IIC–III, fewer IIA–IIB. Broad envelope has no century-level frequencies; chronology is a weak absolute estimate despite excavated phase linkage.')
row('rojdi','Rojdi marked bowl','Gujarat',['Rojdi'],['incised convex bowl'],[R],['Rao p. 48 and comparative graffiti discussion'],
    [date(-1500,-1100,'ceramic contemporaneity with Rangpur IIB in original report','C','Rao p. 48 and chronology', 'Historical report attribution; later Rojdi monograph chronology not recovered.')],1,
    'One explicitly mentioned bowl; published exemplar, not a site inventory.',images=False,claims=['lal-bridge'])
row('lothal-late','Lothal B and later Gujarat marks','Gujarat',['Lothal','other Gujarat sites'],['pottery graffiti'],[L,R],
    ['Lal pp. 21–22 and plates; Rao comparative sequence'],images=True,claims=['lal-bridge'],limitations='Marked examples are published. A separately verified calendar bracket for the late marked objects was not recovered; broad Lothal occupation is not used.')
row('bet-dwarka','Bet Dwarka inscribed sherds and motif seal','Gujarat',['Bet Dwarka'],['two inscribed sherds','one shell motif seal'],['sundaresh-gaur1998'],
    ['pp. 77, 79, 81, 85; figs. 2–4'],[date(None,None,'unjoined pottery TL and typology; shell and sherd dates unresolved','D','p. 79', 'Paper gives c.1400 settlement, early second millennium conclusion, and explicitly no dated stratigraphic context for shell objects.')],3,
    'Two inscribed sherds plus one motif seal, not three text-bearing objects.',images=True,claims=['bet-dwarka-relation'],limitations='Seven-character sherd from intertidal exploration; two-character sherd onshore; motif seal UW6 layer 2. No direct dated mark-to-sample association.')
row('daimabad-II','Daimabad Phase II inscriptions','Deccan',['Daimabad'],['terracotta seals','inscribed potsherds'],[S],
    ['pp. 504–506; chronology p. 211'],
    [date(-2440,-2120,'published MASCA-corrected stratigraphic phase bracket','B','p. 211','Envelope of printed alternatives 2330/2440 to 2120/2140 BCE; old correction, not a modern calibration.',strength='low'),
     date(-2000,-1800,'conventional author phase bracket','B','p. 211','Excluded from calendar coverage to avoid treating conventional radiocarbon years as calendar years.',selected=False)],6,
    'Two seals and four inscribed potsherds explicitly catalogued in Phase II.',images=True,claims=['daimabad-survival'])
row('daimabad-II-graffiti','Daimabad Phase II other graffiti','Deccan',['Daimabad'],['red-ware graffiti'],[S],['p. 248; chronology p. 211'],
    [date(-2440,-2120,'published MASCA-corrected phase bracket','B','p. 211','Separate category, possible overlap with four inscribed potsherds.',strength='low')],12,
    'About a dozen in narrative, not an exact inventory; cannot add to six inscriptions.',images=True,count_kind='approximate',include=False,claims=['daimabad-survival'])
row('daimabad-III','Daimabad Phase III inscribed sherd','Deccan',['Daimabad'],['pink-ware inscribed sherd'],[S],
    ['pp. 504–505; chronology p. 211'],
    [date(-2140,-1800,'published MASCA-corrected phase bracket','B','p. 211','Printed 2120–2140 to 1800 BCE; no new calibration.',strength='low'),
     date(-1800,-1600,'conventional author phase bracket','B','p. 211',selected=False)],1,
    'One described sherd with five or six signs; no repertoire size inferred.',images=True,claims=['daimabad-survival'])
row('inamgaon','Inamgaon cart graffito','Deccan',['Inamgaon'],['figurative pottery graffito'],['kenoyer2004'],
    ['PDF p. 17 figure caption, after Sankalia 1974'],[date(-1500,-1400,'circa 1500 BCE Early Jorwe attribution; century bin for approximate label','C','PDF p. 17','Century envelope is an editorial coarse-bin representation, not a dated confidence interval.')],1,
    'One illustrated cart-bearing pot; no site graffiti census.',images=True,claims=['lal-bridge'],limitations='Original excavation specimen/sample link not recovered.')
row('navdatoli','Navdatoli Chalcolithic graffiti','Central India',['Navdatoli'],['incised pottery'],[L,T],
    ['Lal symbol descriptions and plates; Thapar pp. 21–22 comparative chronology'],images=True,claims=['lal-bridge'],limitations='Thapar cites P-201, P-200, P-475 and TF-59 conventional dates for phases, not individually identified Lal sherds. No calibrated marked-object interval selected.')
row('prakash-I','Prakash Period I graffiti','Deccan',['Prakash'],['grey-ware, Malwa-ware and Jorwe-ware graffiti'],[T],
    ['pp. 21–24, 66–68; fig. 19'],repertoire=10,
    repertoire_basis='Ten different marks, four incomplete, reported p. 66; six grey-ware, one Malwa-ware, three Jorwe-ware types. Type count is not an object census.',images=True,claims=['lal-bridge'],limitations='Indirect conventional radiocarbon chronology transferred from Navdatoli, Ahar and other sites. Calendar calibration and specimen join were not recovered.')
row('ahar-banas','Ahar–Banas / Gilund marks','Central India',['Ahar','Gilund'],['pottery graffiti'],[L,T,TN],
    ['Lal p. 22; Thapar comparative chronology; Rajan/Sivanantham p. 263'],images=True,claims=['lal-bridge'],limitations='Bridge argument invokes ceramic similarities and examples. No recovered dated graffiti inventory or calibrated mark-to-sample join.')
row('ocp','Ochre Coloured Pottery contexts','Ganga plain',['OCP assemblages, site-level recovery pending'],['reported pottery marks requiring specimen verification'],[],[],limitations='Search did not recover an opened primary dated mark corpus; cultural date ranges and total pottery counts are not substituted.')
row('copper-hoards','Copper Hoard contexts','Ganga plain',['Copper Hoard assemblages, site-level recovery pending'],['reported marks requiring verification'],[],[],limitations='No primary marked-object inventory, repertoire, or dating join recovered in this package.')
row('pgw','Painted Grey Ware contexts','Ganga plain',['PGW assemblages, site-level recovery pending'],['pottery; marked examples unresolved'],[L],['p. 22'],limitations='Lal states graffiti had not yet been noted on PGW in 1960. This is a dated research observation, not a present-day zero count. Failed IAR recovery cannot establish a context.')
row('nbpw','NBPW and successor grey-ware graffiti','Ganga plain',['Sonpur','Rajghat'],['incised pottery'],[L],['p. 23'],images=False,claims=['lal-bridge'],limitations='Marks are reported, but the opened account provides no specimen-to-calendar interval. No generic NBPW date range substituted.')
row('south-megalithic-lal','Lal megalithic comparative repertoire','South India',['Brahmagiri','Maski','Sanur','other illustrated sites'],['pottery graffiti'],[L],['pp. 4–24 and plates; discussion p. 21'],
    repertoire=53,repertoire_basis='47 shared plus 6 exclusive megalithic types in Lal comparison. Combined union 61; Harappan/Chalcolithic comparator 55.',images=True,claims=['lal-bridge'],include=False,limitations='Pooled comparative type inventory, not a marked-object total or a dated regional corpus.')
row('sanur','Sanur three-sign pottery examples','South India',['Sanur'],['burial pottery graffiti'],[L,TN],
    ['Lal p. 23; Rajan/Sivanantham p. 299'],images=True,claims=['lal-bridge'],limitations='Three signs reported in varying order; burial-level calendar dates and an exact object count not recovered.')
row('sulur','Sulur dish','South India',['Sulur'],['four-mark terracotta dish'],['mahadevan2001'],['p. 379, museum 1935.4-19.15; pp. 382–384'],
    [date(-100,0,'British Museum label cited by author, first century BCE','C','p. 379','Outside 3500–200 BCE window.')],1,
    'One dish, four marks; four is not the object count.',repertoire=4,repertoire_basis='Four marks on one specimen, not the Sulur repertoire.',images=True,claims=['mahadevan-pairs'],include=False)
row('anuradhapura','Anuradhapura early Brahmi pottery','Sri Lanka',['Anuradhapura'],['inscribed pottery'],['coningham1996','deraniyagala',SAL],
    ['1996 abstract; Deraniyagala Early Historic writing section; Salomon p. 12'],
    [date(-400,-300,'published beginning-fourth-century placement from radiometric/stratigraphic investigation','C','1996 abstract','Full sample table, lab numbers and specimen associations not recovered.'),
     date(-600,-500,'alternative authored overview: charcoal radiocarbon and TL with cross-checks','C','Deraniyagala writing section','Different assessment retained separately; no merging with 1996 interval.',selected=False)],images=False,claims=['brahmi-distribution'],limitations='Abstract opened, full 1996 article not recovered; corpus images not verified in the recovered source.')
row('ibbankatuwa','Ibbankatuwa megalithic context','Sri Lanka',['Ibbankatuwa'],['burial pottery; marked specimen verification pending'],['deraniyagala'],['Protohistoric Iron Age section, citing 1992 p. 734'],
    [date(-750,-400,'reported radiocarbon burial-context chronology; mark link absent','D','Deraniyagala overview','Lab numbers and marked objects not supplied; not selected as marked coverage.',selected=False)],limitations='Dated cemetery alone does not establish dated graffiti.')
row('keeladi','Keeladi pottery graffiti and Tamil-Brahmi','South India',['Keeladi'],['graffiti sherds','Tamil-Brahmi sherds'],[TN],
    ['pp. 56–57; catalogue Table 3.1 p. 227'],
    [date(-679,312,'published calibrated occupation envelope; mark-to-sample join unresolved','C','pp. 56–57','Source separates conventional 580 BCE–200 CE and calibrated 679 BCE–312 CE; no lab IDs in this reviewed section.'),
     date(-580,200,'conventional source occupation bracket','C','p. 56',selected=False)],3782,
    'Collected graffiti total 2447 ASI + 1335 TNSDA. Documented subset 2132 = 797+1335. Tamil-Brahmi 172 counted separately and not added; dual-mark overlap unknown.',images=True,claims=['tn-morphology','early-tamil-brahmi'])
row('kodumanal','Kodumanal graffiti and Tamil-Brahmi','South India',['Kodumanal'],['graffiti sherds','Tamil-Brahmi sherds'],[TN],
    ['p. 102; Table 3.1 p. 227; Tamil-Brahmi documentation p. 229'],
    [date(-480,-210,'published calibrated settlement interval; aggregate mark/sample association unresolved','C','p. 102','37 AMS determinations, 10 contaminated, 27 considered. ZE8 75 cm: 2210±30 and 2247±27 BP; laboratory identifiers not recovered. Grave MEG19 2718±30 BP is not a Tamil-Brahmi specimen date.'),
     date(-408,-200,'conventional source settlement interval','C','p. 102',selected=False)],2632,
    'Documented graffiti in Table 3.1. Other Tamil-Brahmi counts and excluded ASI specimens not pooled.',images=True,claims=['tn-morphology','early-tamil-brahmi'])
row('porunthal-I','Porunthal MEG I inscribed ringstands','South India',['Porunthal'],['two Tamil-Brahmi ringstands'],[TN],
    ['p. 167; figs. 3.2–3.3, printed pp. 247–248'],
    [date(None,None,'rice AMS determination associated with grave goods; calibrated interval not recovered','C','p. 167','2440±30 BP is reported as uncalibrated 490 BCE. No calendar interval inferred by subtracting BP from 1950.',labs=['Beta-302854'],measurement={'bp':2440,'sigma':30,'material':'rice from four-legged jar, MEG I'})],2,
    'Two inscribed ringstands described in MEG I; dated sample is rice from another grave vessel.',images=True,claims=['early-tamil-brahmi'],limitations='Association described, original lab calibration and grave register not recovered. Therefore excluded from century coverage until a calendar range is available.')
row('porunthal-IV','Porunthal MEG IV graffiti context','South India',['Porunthal'],['burial graffiti context'],[TN],['p. 167 and grave discussion'],
    [date(None,None,'rice AMS determination; mark-specific link and calibrated interval unresolved','C','p. 167','2400±30 BP reported as uncalibrated 450 BCE.',labs=['Beta-305904'],measurement={'bp':2400,'sigma':30,'material':'rice, MEG IV'})],images=True,limitations='Graffiti total and dated marked-object association not recovered. No calendar interval selected.')
row('kilnamandi-burials','Kilnamandi burial graffiti','South India',['Kilnamandi'],['burial pottery graffiti'],[TN],['pp. 69–74'],
    [date(-1769,-1615,'calibrated radiocarbon interval for MEG III; aggregate graffiti grave join unresolved','C','p. 74','Published 93.3% interval. 43 marks from burial group do not establish that all occur in dated MEG III.',labs=['Beta-666752'],measurement={'bp':3400,'sigma':30,'material':'burial sample, MEG III','calibration_probability':0.933})],43,
    '43 burial graffiti sherds across the reported excavation, not 43 specimens individually joined to MEG III.',images=True,claims=['tn-morphology'])
row('kilnamandi-habitation','Kilnamandi habitation graffiti','South India',['Kilnamandi locality 2'],['pottery graffiti'],[TN],['pp. 69–74'],images=True,
    count=45,count_basis='45 habitation graffiti sherds, depths 50–70 cm.',limitations='Chronology inferred by ceramic comparison with graves; no independent selected calendar range. Not assigned the MEG III radiocarbon date.')
row('perumbalai','Perumbalai graffiti','South India',['Perumbalai'],['pottery graffiti'],[TN],['pp. 181–182; Table 3.1 p. 227'],
    [date(-649,-499,'stratigraphic phase bracket from published calibrated sample midpoints','B','pp. 181–182','Not a calibration confidence envelope. Charcoal below Floor I at 190–292 cm. Individual graffiti counts by layer missing.',labs=['Beta-640429','Beta-640430','Beta-640431','Beta-640432'],measurement={'calibrated_midpoints_bce':[499,620,649,649]})],1028,
    'Site-wide documented graffiti; aggregate is not restricted to these sample contexts.',images=True,claims=['tn-morphology'],limitations='B applies to the reported graffiti-bearing phase; site-wide count is not temporally aligned.',count_kind='exact, temporally unaligned')
row('sivagalai-early-burials','Sivagalai early dated urns','South India',['Sivagalai'],['dated urn burials without reported graffiti'],[TN],['Table 2.1 p. 181; p. 295'],
    [date(None,None,'AMS calibrated point estimates for unmarked urn burials','D','Table 2.1','Separate dates: Beta-583593 4670±30 BP, calibrated point 3345 BCE; 583592 4540±30 BP, point 3259 BCE; 583594 4300±30 BP, point 2953 BCE. OSL dates are separate methods.',labs=['Beta-583593','Beta-583592','Beta-583594'],selected=False)],0,
    '2026 p. 295 states the early urn burials at Sivagalai have no graffiti. This scope-specific observation does not count all site pottery.',include=False,limitations='Early iron or urn dates cannot be transferred to graffiti or Tamil-Brahmi.')
row('sivagalai-habitation','Sivagalai habitation marks and claimed early Tamil-Brahmi','South India',['Sivagalai'],['habitation graffiti','Tamil-Brahmi sherds'],[TN],['pp. 183, 194; Table 3.1 p. 227'],
    [date(None,None,'charcoal AMS calibrated point estimate; full interval and specimen join missing','C','pp. 183, 194','Beta-600727, habitation A1, depth 4m, 2560±30 BP, reported calibrated midpoint 685 BCE. No uncertainty interval invented.',labs=['Beta-600727'],measurement={'bp':2560,'sigma':30,'calibrated_midpoint_bce':685})],images=True,claims=['early-tamil-brahmi'],limitations='Narrative associates charcoal with Tamil-Brahmi; specimen registration and same-deposit sample join require verification.')
row('tn-pooled','Tamil Nadu 2026 pooled catalogue','South India',['Tamil Nadu catalogue sites'],['graffiti sherds','Tamil-Brahmi sherds'],[TN,'rajan-sivanantham2026-II','rajan-sivanantham2025'],['pp. 227–229; 2025 brochure'],
    count=15184,count_basis='Reported graffiti. Documented 14165, recognized 9619, unrecognized 4546; final table line 14168 differs by three. Tamil-Brahmi reported 1570, documented 1182, unavailable 388.',
    repertoire=42,repertoire_basis='42 base families in 2026; composites and variants are different units. Brochure: 42+544+1521=2107 classified forms. Earlier portal: 42+546+1522, reused without rerunning.',images=True,include=False,claims=['tn-morphology'],limitations='Parent catalogue overlaps site rows and extends beyond 200 BCE; excluded from additive coverage.')
row('ashoka-brahmi','Ashokan Brahmi rock and pillar corpus','Early historic South Asia',['Girnar','Dhauli','Jaugada','other Ashokan locations'],['rock inscriptions','pillar inscriptions'],[SAL],['pp. 10–13, 30, 133; appendix images'],
    [date(-272,-232,'historical attribution to Ashoka; broad reign envelope reported by Salomon','A','p. 133 (PDF p. 156)','Salomon reports ca.272–232 BCE. Envelope, not assertion that every edict dates to accession. Documentary revision 03 corrects earlier assumed 268 to the opened source\'s 272; century membership is unchanged.')],repertoire=38,
    repertoire_basis='Salomon p. 30: 6 initial vowels + 32 consonants. Eight medial vowel diacritics and anusvara are separately described, not pooled into this base count.',images=True,claims=['brahmi-origins'])
row('ashoka-kharosthi','Shahbazgarhi and Mansehra Kharosthi edicts','Early historic South Asia',['Shahbazgarhi','Mansehra'],['rock inscriptions'],[SAL],['p. 46'],
    [date(-260,-240,'historical middle-third-century Ashokan edicts; coarse envelope','A','p. 46','Chronology is historical; proposed earlier origins are not attested dated specimens.')],2,
    'Two named edict assemblages/sites, NOT two marked objects.',images=False,count_kind='site count, not objects',claims=['kharosthi-aramaic'])
row('tamil-cave','Early Tamil-Brahmi cave inscriptions','South India',['Mangulam and other early cave-inscription sites'],['rock cave inscriptions'],[SAL],['pp. 35–36, note 103'],
    [date(-200,0,'Mahadevan palaeographic second/first-century BCE dating reviewed by Salomon','C','p. 35 note 103','Boundary/outside selected coverage; later claims require separate source verification.')],images=False,include=False,claims=['early-tamil-brahmi'],limitations='Mankulam government report download timed out. No invented pre-200 BCE palaeographic envelope.')
row('bhattiprolu','Bhattiprolu relic-casket inscriptions','South India',['Bhattiprolu'],['stone relic caskets'],[SAL],['pp. 34–35'],
    [date(None,None,'competing palaeographic estimates','C','p. 35','Bühler: not later than 200 BCE; Sircar: end of second century BCE. No merged interval.')],images=False,include=False,claims=['brahmi-origins'])
row('adjacent-aramaic','Achaemenid Aramaic route comparator','Adjacent West Asia / Afghanistan',['Achaemenid territories; Bactria acquisition target'],['administrative writing'],[SAL],['pp. 23–30, 54–55'],include=False,adjacent=True,
    limitations='Origin argument reviewed. Khalili collection site timed out/429; internally dated Bactrian documents were seen only in search results. No dates or counts promoted to opened-source coverage.')

# Dated documentary revision after run 01. Preserve that input/output endpoint.
# These corrections do not alter any selected date interval or numeric count.
by_id={r['id']:r for r in ROWS}
by_id['ahar-banas']['image_corpus_verified']=False
by_id['ahar-banas']['limitations']+=' The recovered Gilund bridge observation concerns ceramics; a graffiti image corpus was not verified.'
by_id['prakash-I']['dating_assessments'].append(date(-1700,-1300,
    'published conventional comparative phase bracket; not calendar calibrated','C',
    'Thapar pp. 21–24, summary p. 24',
    '1700–1500 IA and 1500–1300 IB BCE in the report. Transferred from other sites; no calibrated specimen interval selected.',
    labs=['P-201','P-200','P-475','TF-59','P-204','P-205'],selected=False))
for id in ['daimabad-II','daimabad-II-graffiti']:
    for d in by_id[id]['dating_assessments']:
        d['lab_numbers']=['PRL-420','PRL-657','BS-180','PRL-426']
        d['note']+=' See dating-details.json for rejected/inconsistent determinations and unjoined TL samples; these identifiers do not imply direct sample-to-inscription joins.'
for d in by_id['daimabad-III']['dating_assessments']:
    d['lab_numbers']=['PRL-428','PRL-419','BS-182','PRL-655','BS-177']
    d['note']+=' Phase determinations were considered inconsistent by Sali; see dating-details.json.'
for r in ROWS:
    r['documentary_revision']='2026-10-07-03; source-audit corrections; Exploratory'

def dump(path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',default=str(OWN))
    args=p.parse_args()
    output=Path(args.output).resolve()
    output.relative_to(OWN)
    output.mkdir(parents=True,exist_ok=True)
    targets=[output/x for x in ['sources.json','evidence-table.json','evidence-table.csv']]
    if any(x.exists() for x in targets):
        p.error('Evidence endpoint exists; choose a fresh --output beneath the owned directory.')
    assert len({r['id'] for r in ROWS})==len(ROWS)
    assert all(set(r['source_ids'])<=set(s['id'] for s in SOURCES) for r in ROWS)
    dump(targets[0],{'status':'Exploratory','sources':SOURCES})
    dump(targets[1],{'status':'Exploratory','schema_version':1,'rows':ROWS})
    with targets[2].open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(ROWS[0]))
        writer.writeheader()
        for r in ROWS:
            writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
    print(json.dumps({'sources':len(SOURCES),'rows':len(ROWS),'output':str(output)}))

if __name__=='__main__': main()
