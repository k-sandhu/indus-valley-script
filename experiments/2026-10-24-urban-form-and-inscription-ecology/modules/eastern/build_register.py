"""Build the eastern town source assertions. Source copies remain local on D:."""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw')
LOCAL = RAW / '2026-10-24-urban-form-and-inscription-ecology/eastern'
SOURCES = []
OBS = []


def source(id, title, authors, year, publication, path, url, pages, method, **extra):
    p = RAW / path
    data = p.read_bytes()
    row = dict(id=id, title=title, authors=authors, year=year, publication=publication,
               url=url, logical_path='data/raw/' + path, physical_path=str(p),
               sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
               access_status='held source reused; no new download', new_acquisition=False,
               source_class='excavator or excavation-project primary report',
               rights='rights unresolved; source and source-derived page images local-only',
               pages_read=pages, reading_method=method, reviewed_on='2026-10-24', **extra)
    SOURCES.append(row)


def obs(town, phase, feature, assertion, sid, locator, *, status='reported observation',
        basis='site stratigraphy and source phase assignment', uncertainty=None,
        missing_reason=None, quantity=None, unit=None, scope=None, **extra):
    id = f'EAST-{town.upper()}-{sum(r["town"] == town for r in OBS) + 1:03}'
    assertion = re.sub(r'(?<=[a-z])(?=\d)', ' ', assertion)
    assertion = re.sub(r'\b(A|An|The)(?=\d)', r'\1 ', assertion)
    assertion = re.sub(r'(?<=\d)(?=(?:mm|cm|km|ha|m²|m|BC|BP|AD)(?![A-Za-z]))', ' ', assertion)
    assertion = re.sub(r'\b(Period|Phase)(?=[IVX])', r'\1 ', assertion)
    assertion = re.sub(r',(?=\d)', ', ', assertion)
    row = dict(id=id, town=town, phase=phase, feature=feature, assertion=assertion,
               source_id=sid, locator=locator, evidence_status=status,
               dating_basis=basis, uncertainty=uncertainty,
               missing_reason=missing_reason, **extra)
    if quantity is not None:
        row.update(quantity=quantity, unit=unit, count_or_measurement_scope=scope,
                   measurement_error='source gives no quantified measurement error')
    OBS.append(row)


source('EAST-THAPAR1975', 'Kalibangan: A Harappan Metropolis Beyond the Indus Valley',
       ['B. K. Thapar'], 1975, 'Expedition 17(2):19–32',
       '2026-10-21-town-orientations-verification/dating/kalibangan1975.pdf',
       'https://www.penn.museum/documents/publications/expedition/17-2/Thapar.pdf',
       'Printed pp.19–32; eight PDF leaves, including two-page spreads; all visually read',
       'All eight leaves rendered and visually read; Penn HTML used as search aid',
       copy_note='The scan has 180 m for Period I E–W width; Penn HTML transcribes 160 m. The scan controls this register.')
source('EAST-IAR1967', 'Indian Archaeology 1967-68—A Review',
       ['Archaeological Survey of India; excavation directed by B. B. Lal and B. K. Thapar'],
       1968, 'Excavation at Kalibangan, District Ganganagar, pp.42–45',
       '2026-10-21-town-axes/dating/kalibangan/iar1967-68.pdf',
       'https://www.asiaurangabadcircle.com/assets/files/publications/1967-1968.pdf',
       'Printed pp.42–45; PDF indices49–52 (p.43 is plan)', 'PDF text extraction; locators checked against page headings')
source('EAST-BISHT1999', 'Dholavira and Banawali: Two different paradigms of the Harappan Urbis forma',
       ['R. S. Bisht'], 1999, 'Puratattva 29 (1998–99):14–37',
       '2026-10-21-town-orientations-verification/infra/plans/banawali/bisht-volume/source.pdf',
       'https://ignca.gov.in/Asi_data/85200.pdf',
       'Banawali pp.14–20, PDF indices27–33; title and copyright pages; Fig.1 locator inherited from checked prior source index',
       'Printed pp.15–20 rendered and visually read; inherited OCR aids navigation',
       copy_note='The file is the entire 180-leaf Puratattva 29 volume, despite its generic folder name. Publication copyright page reads 1999.')
source('EAST-IAR1986', 'Indian Archaeology 1986-87—A Review',
       ['Archaeological Survey of India; excavation directed by R. S. Bisht'], 1992,
       'Excavation at Banawali, District Hissar, pp.32–34',
       '2026-10-21-town-axes/dating/banawali/iar1986-87.pdf',
       'https://www.asiaurangabadcircle.com/assets/files/publications/1986-1987.pdf',
       'Printed pp.32–34, PDF indices40–42', 'PDF text and held OCR compared')
source('EAST-KHARAKWAL2011', 'Kanmer: A Multicultural Site in Kachchh, Gujarat, India',
       ['J. S. Kharakwal', 'Y. S. Rawat', 'T. Osada', 'L. C. Patel', 'Hanmukh Seth',
        'Rajesh Meena', 'S. Meena', 'K. P. Singh', 'A. Hussain'], 2011,
       'Nichibunken International Symposium 16:355–376',
       '2026-10-21-town-axes/dating/kanmer/kharakwal2011multicultural.pdf',
       'https://nichibun.repo.nii.ac.jp/record/1259/files/symp_016__357__355_376__357_378.pdf',
       'Printed pp.355–372, especially pp.356,358–370; PDF index=printed page−355',
       'Native PDF text; numerical contexts and tables read in full',
       copy_note='Only the stable institutional URL is exported; an inherited short-lived signed redirect is excluded.')
source('EAST-BHAN2008', 'Excavations at Shikarpur 2007-2008: A Costal Port and Craft Production Center of the Indus Civilization in Kutch, India',
       ['Kuldeep K. Bhan', 'P. Ajithprasad'], 2008, 'Excavation-project web report, pp.1–9',
       '2026-10-21-town-axes/dating/shikarpur/bhan2008shikarpur.pdf',
       'https://www.harappa.com/sites/default/files/pdf/Excavations-at-Shikarpur-2007.pdf',
       'Printed pp.1–9; observations mainly pp.3–6', 'Native PDF text read; original author report re-opened on web')
source('EAST-SHINDE2011', 'Excavations at Farmana, District Rohtak, Haryana, India, 2006-2008',
       ['Vasant Shinde', 'Toshiki Osada', 'Manmohan Kumar (editors)'], 2011,
       'Indus Project, Research Institute for Humanity and Nature, Kyoto; ISBN 978-4-902325-62-1',
       '2026-10-21-town-axes/dating/farmana/shinde2011farmana.pdf',
       'https://archive.org/details/excavationsatfarmana200608vshindeetal_212_v',
       'pp.5–6,20–25,31,38–45,70,78,97,103,117,141–143,164–166,831–834,839; PDF index=printed page+13',
       'Native PDF text; source chapter and table identities checked',
       copy_note='Chapter 4 chronology and concluding chapter disagree about the date of the earliest occupation. Chapter 13 supplies calibrated laboratory results.')
source('EAST-NATH2014-DRAFT', 'Excavations at Rakhigarhi [1997-98 to 1999-2000]',
       ['Amarendra Nath'], 2014, 'Archaeological Survey of India draft report, covering letter dated 31 December 2014',
       '2026-10-21-town-axes/dating/rakhigarhi/nath-excavations-1997-2000.pdf',
       'https://archive.org/details/excavationsatrakhigarhi19972000amarendranath_457_Z',
       'pp.7–8,93–98,108–122,128–129; PDF index=printed page−1',
       'Native PDF text; cover and dated covering letter inspected',
       copy_note='Draft status retained. Prose has inconsistent phase nomenclature and several incomplete figure references. Functional labels are separate from architectural observations.')
source('EAST-JOSHI1990', 'Excavation at Surkotada 1971-72 and Exploration in Kutch',
       ['Jagat Pati Joshi (editor and architectural author)'], 1990,
       'Memoirs of the Archaeological Survey of India87',
       '2026-10-21-town-axes/plan-B/downloads/joshi1990_surkotada_masi87.pdf',
       'https://archive.org/details/masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t',
       'pp.14,25–28,40–41,44–50,54,58,60–66; PDF indices32,43–46,62–70,74,78,80–86 individually inspected',
       'Scan pages visually read; OCR too poor for numerical transcription',
       copy_note='Printed pp.42–43 are absent between PDF leaves63 and64 in this held scan. Initial enclosure description is therefore supplemented from IAR1971–72. Published BC dates are retained as author arithmetic, not recalibrated.')
source('EAST-IAR1971', 'Indian Archaeology 1971-72—A Review',
       ['Archaeological Survey of India; excavation directed by J. P. Joshi'], 1975,
       'Excavation at Surkotada, District Kutch, pp.13–19',
       '2026-10-21-town-axes/dating/surkotada/iar1971-72.pdf',
       'https://archive.org/details/indianarchaeology197172areview_206_P',
       'pp.13,16–17 and associated Fig.2; PDF indices21,24,26', 'Native PDF text and inherited OCR read')

# Kalibangan: count excavated components within their phase and area.
t='kalibangan';s='EAST-THAPAR1975'
obs(t,'all','location','The site is on the left bank of the Ghaggar in northern Rajasthan.',s,'p.19, introductory paragraph',basis='modern source description',uncertainty='River identification and ancient discharge are not measured by this architectural source.')
obs(t,'I','enclosed dimensions','The reported early settlement measures approximately250m N–S by180m E–W.',s,'p.20, Period I; PDF index1 left page',quantity=[250,180],unit='m',scope='outline of Period I enclosure; not excavated floor area',uncertainty='Penn HTML says160m E–W; visual scan reads180m. Approximate dimensions, no surveyed error.')
obs(t,'I','fortification change','The mud-brick enclosure has two structural phases: basal width1.9m, then3–4m after inward additions.',s,'p.20, Period I',quantity=[1.9,3,4],unit='m',scope='reported fortification section widths; not town means')
obs(t,'I','building material','House and enclosure bricks measure30×20×10cm, ratio3:2:1; a baked-brick drain is reported.',s,'p.20',quantity=[30,20,10],unit='cm',scope='reported brick size; sampling distribution not given')
obs(t,'I','house count missing','Complete house plans could not be exposed in the limited slope excavation; deeper work would have removed later deposits.',s,'p.20, paragraph beginning Within the walled area',status='documented coverage limitation',missing_reason='Limited early exposure and preserved superimposed Harappan deposits prevent an early house census.')
obs(t,'I','rebuilding sequence','Five structural phases were recognized; the upper three largely rebuilt the existing plan.',s,'p.23, first and chronology paragraphs',quantity=5,unit='structural phases',scope='excavated Period I sequence, not five simultaneously occupied neighborhoods')
obs(t,'I to II','interruption and replanning','The earlier settlement ended with displaced strata and subsided walls, followed by a thin sand layer; Period II introduced a separate eastern lower city and western citadel.',s,'pp.23–24',status='observed stratigraphic sequence plus source planning inference',uncertainty='Seismic causation is proposed by Thapar; the architectural break does not identify its cause.')
obs(t,'II','citadel dimensions','The citadel is reported as240m N–S by120m E–W and split into two separately patterned parts.',s,'p.23',quantity=[240,120],unit='m',scope='citadel outline; not house floor area')
obs(t,'II','lower city dimensions','The eastern lower city is reported as240m E–W by360m N–S, separated from the citadel by about40m.',s,'p.26',quantity=[240,360,40],unit='m',scope='enclosure dimensions and interdivision gap')
obs(t,'II','platform count','Substantial portions of five citadel platforms were exposed; one outline was complete, approximately50×25m.',s,'p.24',quantity=5,unit='partly exposed platforms',scope='southern citadel; one fully outlined platform; author estimates five to six existed',uncertainty='Superstructures were damaged by brick removal; this is not a count of temples.')
obs(t,'II','burning features','A row of seven rectangular burning installations is reported on one platform near a well.',s,'p.24',quantity=7,unit='features',scope='one exposed platform, not town-wide count',status='reported observation; fire-altar function is excavator interpretation',uncertainty='Ritual use is source attribution; retain feature geometry independently.')
obs(t,'II','arterial street count','Excavations established four N–S arterial streets and three E–W streets, with an indication of a fourth E–W street.',s,'p.26',quantity={'north_south':4,'east_west_established':3,'east_west_indicated':1},unit='street axes',scope='lower-city excavation; staggered E–W delivery lanes do not cross all N–S arterials')
obs(t,'II','street widths','Reported street widths range1.8–7.2m in multiples of1.8m.',s,'p.26',quantity=[1.8,7.2],unit='m',scope='lower-city thoroughfares and streets; no individual error estimates')
obs(t,'II','street continuity','Thoroughfare widths were maintained; rectangular platforms outside houses were the reported structural encroachments.',s,'pp.26–27',status='source synthesis of excavated phases',uncertainty='No town-wide phase-by-phase GIS or exposure denominator is published in this resume.')
obs(t,'II','drainage','Regular street drains were not found; house drains discharged into soakage jars below street floors.',s,'p.27',status='observed absence within excavation',missing_reason='Does not establish absence in every unexcavated street segment.')
obs(t,'II','building materials','Domestic walls use mud brick; baked brick is concentrated in drains, wells, sills and bathing platforms.',s,'p.27',uncertainty='A functional allocation reported by the excavator, not a measured town-wide material fraction.')
obs(t,'I and II','dating convention','Thapar proposes2450–2300BC for I and2300–1750BC for II, explicitly without radiocarbon correction factors.',s,'p.23 and p.32',status='historical chronological interpretation',basis='1975 radiocarbon and cross-dating discussion; not modern calibrated boundaries',uncertainty='Do not plot these dates on the same calendar scale as calibratedBC intervals or subtract them to estimate securely dated occupation duration.')
obs(t,'II','local alignment adjustment','Nine successive building and road levels occur in both east and west cuttings; houses near the perimeter follow its alignment and those near streets follow street alignment.', 'EAST-IAR1967','p.44, PDF index51',quantity=9,unit='successive building levels',scope='two cross-cutting areas and central house block; not nine whole-town rebuilds',uncertainty='The report leaves street realignment versus local adjustment unresolved.')
obs(t,'II','inscribed object context','A steatite seal and copper implements were recovered from different floor levels in one excavated room of the central house block.', 'EAST-IAR1967','p.44, final paragraph',uncertainty='Object registration and exact floor-to-phase joins are missing in this short account; the room label alone does not establish association in one event.')

# Banawali: inherited curving forms can be deliberately rebuilt.
t='banawali';s='EAST-BISHT1999'
obs(t,'all','location','Bisht reports29°37′5″N,75°23′6″E on the right bank of the channel called Sarasvati in the report.',s,'p.14; PDF index27',basis='modern geographic description',quantity={'latitude_dms':'29 37 05 N','longitude_dms':'75 23 06 E'},unit='source DMS',scope='reported site point',uncertainty='Coordinate datum and surveyed precision unstated; named palaeoriver is source terminology.')
obs(t,'IA','settlement form','The first settlement was an open village on a dune with no enclosing wall reported.',s,'p.15, The Pre-Harappan Period',uncertainty='Early houses and streets were sparsely exposed; an unplanned layout does not follow from the absence of an enclosure.')
obs(t,'IA','building material','Sun-dried brick in mud mortar was the principal material; moulded sizes follow3:2:1 length:width:thickness.',s,'p.15',quantity=[3,2,1],unit='brick dimension ratio',scope='reported early brick forms; no sample count')
obs(t,'IB','enclosure growth','An initial1.40m boundary wall was reinforced inside and later widened outside after tilting and water damage.',s,'pp.15–16',quantity=1.4,unit='m',scope='initial boundary-wall width at investigated section',uncertainty='Damage mechanisms are the excavator interpretation; later width varies by surviving section.')
obs(t,'IC','replanning','Existing residential buildings were razed and replaced with thicker-walled brick houses; a new street system and bipartite settlement were introduced while the earlier enclosure was retained and widened.',s,'pp.16–17',status='reported sequence plus source planning inference',uncertainty='This is a settlement-scale inference from sampled exposures; per-house demolition dates are absent.')
obs(t,'IC','radial form','Bisht dates the radial lower-town street arrangement to IC and relates it to the adopted, widened curving fortification.',s,'p.17, opening left-column paragraph',status='excavator planning interpretation',uncertainty='The source attributes the mechanism; no independent network statistic has been computed.')
obs(t,'II','plan retention','Period II demolished earlier houses and rebuilt them while preserving the inherited town outline with marginal modifications.',s,'p.17, The Harappan Period',status='excavator synthesis',uncertainty='Retention concerns broad layout; individual structures changed.')
obs(t,'II','structural sequence','Bisht describes six or more building phases across about five centuries in Period II.',s,'p.17, The Harappan Period',quantity={'lower_bound':6},unit='building phases',scope='source town-sequence synthesis',basis='relative stratigraphy and source approximate duration',uncertainty='Five centuries is an author estimate without dated start/end boundary model in this passage.')
obs(t,'II','town extent','The town including fortifications and acropolis is estimated at8.8–9ha.',s,'p.18, first paragraph',quantity=[8.8,9],unit='ha',scope='reconstructed overall settlement outline',uncertainty='Southern wall and parts of outline lost; estimate inferred from surviving contours and structures, not excavated area.')
obs(t,'II','citadel extent','The citadel is estimated at2.7–2.8ha.',s,'p.19, left column',quantity=[2.7,2.8],unit='ha',scope='citadel reconstructed area',uncertainty='Printed axial spans and area are not transparently reconciled in the source; do not recompute a rectangular area for an apsidal outline.')
obs(t,'II','street form contrast','The citadel has rectilinear streets and six identifiable housing sectors; the lower town has radial streets forming triangular or trapezoidal sectors.',s,'p.19, item6',quantity=6,unit='identified housing sectors',scope='visible citadel sectors on source plan; additional sectors conjectured',status='observed layout plus excavator sector identification')
obs(t,'II','gate street convergence','Five main streets meet the east-gate piazza: three from the interior and two along the fortification.',s,'p.20, opening paragraph',quantity=5,unit='major streets',scope='one gate-piazza convergence, not total town streets')
obs(t,'II','well count','One well had been found at the east-gate piazza at the date of the report.',s,'p.20, opening paragraph',quantity=1,unit='excavated well',scope='report-date exposed well count; not all ancient wells')
obs(t,'II','traffic','Repeated cart ruts are reported in the outer street near the citadel northern apex; the excavator infers restricted vehicle access elsewhere.',s,'p.20, left column',status='reported rut observation with separate traffic inference',uncertainty='Absence of ruts elsewhere is affected by exposed surfaces and preservation; legal prohibition is not observed.')
obs(t,'II','sanitation','Baked-brick house drains discharge to pottery jars in streets; storm-water channels pass through gate defences.',s,'p.20, right column',uncertainty='The report distinguishes household sullage disposal and surface runoff; drainage coverage is not quantified.')
obs(t,'II','gate drain rebuilding','The east-gate drain has five rebuilding phases in Bisht1999.',s,'p.20, item7',quantity=5,unit='drain rebuilding phases',scope='one gate drain',uncertainty='Earlier IAR1986–87 p.33 reported at least three phases; these are report-date coverage differences, not automatically contradictions.')
obs(t,'II','building material','Defence walls are moulded bricks in mud mortar with mud, husk and dung plaster; fired-brick bathing platforms occur in citadel houses.',s,'pp.19–20',uncertainty='No town-wide volume or brick-count denominator.')
obs(t,'III','later settlement','Post-Indus Period III is described as a small village with house remains and no classical urban layout in the investigated evidence.',s,'p.20, end of Banawali section',status='excavator interpretation',uncertainty='No excavated village-wide census or absolute phase boundary in this passage.')
obs(t,'II','bathing platform count','Three fired-brick bathing platforms were exposed along citadel Street11, itself exposed for20m.', 'EAST-IAR1986','p.33; PDF index41',quantity={'platforms':3,'street_exposure_m':20},unit='features and m',scope='one20m exposed street segment; not town-wide platform count')
obs(t,'II','writing carriers','Seals, sealings and stamped cakes are listed among Period II finds.', 'EAST-IAR1986','pp.33–34; platesXIIB, XIIC',uncertainty='No per-house counts or object-to-construction-event joins in this summary.')

# Kanmer: changing use of reserved space without an orientation reset.
t='kanmer';s='EAST-KHARAKWAL2011'
obs(t,'all','location','Kanmer/Bakar Kot is in Rapar taluka, Kachchh; a seasonal nala drains its surroundings.',s,'pp.355–356',basis='modern survey description',uncertainty='Source coordinate23°23′N,70°52′E is coarser and differs from later precise publications; do not silently merge points.')
obs(t,'all','site extent','The source distinguishes total site115×155m from main mound115×105m.',s,'p.356',quantity={'site_m':[115,155],'main_mound_m':[115,105]},unit='m',scope='different surface definitions; neither is an excavated-area denominator')
obs(t,'I','pre-enclosure occupation','A roughly40cm cultural deposit underlies the western fortification on virgin soil, with no cultural break into II reported.',s,'pp.356,359',quantity=0.4,unit='m',scope='western stratigraphic section',uncertainty='Only a small low-level area was exposed; settlement-wide original extent is unknown.')
obs(t,'IIa','fortification addition','The massive fortification belongs stratigraphically to IIa and is oriented NNW–SSE.',s,'pp.360–361; Fig.5',uncertainty='Compass reference is qualitative; no true-north error budget supplied.')
obs(t,'IIa','fortification material','The rampart has brown/yellow sandy-clay core, occasional mud bricks and veneers of large semi-dressed local sandstone and other hard rocks.',s,'p.361; Fig.6',uncertainty='Petrographic identifications and material volume fractions are not supplied.')
obs(t,'IIa and later repair','fortification scale','At specified depths northern and eastern arms measure about18m wide; the source estimates about20m at the base.',s,'p.362',quantity={'measured_width_m':18,'measurement_depth_m':2.2,'estimated_base_m':20},unit='m',scope='northern/eastern arms; base width is extrapolation',uncertainty='Do not equate depth-specific width with another town’s basal wall thickness.')
obs(t,'II','interior area conflict','The source gives interior76×75m but prints approximately5852m²; multiplying those two spans gives5700m².',s,'p.362',status='source numerical inconsistency',quantity={'spans_m':[76,75],'printed_area_m2':5852,'arithmetic_rectangle_m2':5700},unit='m and m²',scope='interior envelope; not residential floors',uncertainty='Possible irregular outline or arithmetic error unadjudicated; do not select an exact density denominator.')
obs(t,'II','structural sequence','Five major structural phases were exposed in different areas, each with additions or alterations; all were only partly exposed and disturbed by later occupants.',s,'p.363',quantity=5,unit='major structural phases',scope='three central plus two southeastern exposures, not five complete town plans')
obs(t,'IIa','open-space dimensions','A central open space was partly exposed over7×5m; earlier successive floors shift northwards into the open area.',s,'p.363',quantity=[7,5],unit='m',scope='partly exposed central space',uncertainty='Original total width unknown; shift interpreted from floors.')
obs(t,'IIa first major structural phase','room exposure','One northern structure and eight southern rooms were partly exposed around the open space; one room4.80×3.00m was completely exposed.',s,'pp.363–364; Fig.8',quantity={'northern_structures':1,'southern_rooms':8,'fully_exposed_rooms':1},unit='excavated components',scope='two partial central complexes; not town totals or household count')
obs(t,'IIa','house material','Reported house walls use semi-dressed stone in yellow fine sand and clay binder, usually45–50cm thick.',s,'p.364',quantity=[45,50],unit='cm',scope='exposed first-phase central structures; not all houses')
obs(t,'IIb','open-space occupation','The earlier open space was completely occupied by buildings; orientation stayed the same while structures became wider.',s,'p.364, KMR IIb',status='reported architectural sequence',uncertainty='Occupation of an open area is clear; its authorization, pace and social cause are not observed.')
obs(t,'IIb','room and hearth counts','Eight rooms were partly exposed in each of two superimposed phases; two fireplaces were identified across exposed floors.',s,'p.364',quantity={'rooms_per_phase':8,'superimposed_phases':2,'fireplaces':2},unit='exposed components',scope='south-central partial exposure; phases cannot be added as16 coeval rooms',uncertainty='Cooking interpretation of fireplaces is tentative.')
obs(t,'III','fortification reuse','Later occupants reused IIb structures, built houses on or against the rampart, and removed rampart stone for house construction.',s,'p.365',uncertainty='The sequence supports a change of rampart use; causes and settlement-wide timing remain unknown.')
obs(t,'I–III','chronological extent','The authors place most urban-phase AMS evidence around2500–2000BC; beginning of I and termination of III remain undated in their discussion.',s,'p.368; Tables1.1–1.2 pp.368–369',status='source chronological synthesis',basis='AMS charcoal/grain dates and ceramic sequence',uncertainty='Some older charcoal results3600–2800BC are explicitly unexplained by the authors.500years is a broad source bracket, not a boundary-model duration.')
obs(t,'II','inscribed carriers','Three matching terracotta impressions share a square-seal image and different reverse marks; their small perforations are reported.',s,'pp.369–370; Figs12–13',quantity=3,unit='impressions',scope='published matching group, not all sealings',uncertainty='The author’s identity-card interpretation is a functional proposal; no architectural issuing office is identified.')

# Shikarpur: small exposure, change of materials, reuse rather than town census.
t='shikarpur';s='EAST-BHAN2008'
obs(t,'all','location','Valmio Timbo is4.5km south of Shikarpur village at a creek from the Gulf of Kutch; reported point23°14′15″N,70°40′39″E.',s,'p.3',basis='modern geographic description',quantity={'latitude_dms':'23 14 15 N','longitude_dms':'70 40 39 E'},unit='source DMS',scope='site point',uncertainty='Datum and coordinate survey precision unstated; modern creek is not itself a reconstruction of ancient shoreline.')
obs(t,'all','mound area','The rectangular mound covers approximately3.4ha over an elevated stabilized sand dune.',s,'p.3',quantity=3.4,unit='ha',scope='surface mound envelope; not exposed habitation area')
obs(t,'all excavated phases','excavation exposure','Nine5×5m trenches were laid: six along the southern fortification-to-interior line and three across a western rain gully.',s,'p.4',quantity={'trenches':9,'nominal_trench_dimensions_m':[5,5]},unit='trenches',scope='2007–08 laid-out trenches;225m² is nominal layout area, actual area at each phase not given',uncertainty='Do not divide counts by225m² as if every trench reached every phase.')
obs(t,'I','architecture material','The first excavated phase has about3m of deposits and structures of Harappan-style mud brick.',s,'p.4',quantity=3,unit='m',scope='Phase I deposit in sampled sections',uncertainty='Deposit thickness is not elapsed occupation time.')
obs(t,'II','architecture material change','The following phase has1.4–1.6m of deposits and extensive use of locally quarried stone in buildings.',s,'p.6',quantity=[1.4,1.6],unit='m',scope='reported Phase II deposits; building material fraction not quantified')
obs(t,'III','reuse structures','The top10–20cm are patchy late occupation with slight circular or apsidal stone structures interpreted as reusing preceding stone.',s,'p.6',quantity=[10,20],unit='cm',scope='surviving late deposit',uncertainty='The source infers stone reuse; no complete late plan or dated building census.')
obs(t,'early II repair','fortification sequence','The southern mud-brick fortification showed two construction stages and major early-II repairs, but its base was not reached.',s,'p.6',quantity=2,unit='construction stages',scope='one exposed southern wall segment; not original founding date',missing_reason='Unreached base prevents original construction-phase assignment.')
obs(t,'I','writing carriers','At least five terracotta sealings and one steatite button seal are reported in Phase I.',s,'p.5; Figs6–7 on p.6',quantity={'sealings_lower_bound':5,'button_seals':1},unit='published finds',scope='2007–08 Phase I finds; not full-site assemblage')
obs(t,'I–III','street network missing','The selected first-season report provides no house-block or street-network plan; Fig.1 is a mound contour map.',s,'pp.3–6; Fig.1',status='documented source gap',missing_reason='Nine small trenches and contour figure cannot provide town-wide connectivity, house totals or encroachment rates.')
obs(t,'I–III','occupation interval missing','The report uses relative Harappan phases but does not give a measured start/end calendar interval for this architectural sequence.',s,'pp.4–6',status='documented source gap',basis='relative stratigraphy and ceramics',missing_reason='Calendar boundary evidence and construction-sample joins not supplied in selected report.')

# Farmana: dimensions, local growth, and disagreement inside the same final report.
t='farmana';s='EAST-SHINDE2011'
obs(t,'all','location','The report gives29°02′22″N,76°18′21″E at Daksh Kheda,4km west of Farmana village.',s,'p.5; Fig.2.1 p.6',basis='modern site description',quantity={'latitude_dms':'29 02 22 N','longitude_dms':'76 18 21 E'},unit='source DMS',scope='reported site point',uncertainty='Main plan’s datum has a different precise point; these are not interchangeable wall locations.')
obs(t,'all','surface extent and destruction','Initial survey assigned over18ha of occupation; the surviving central portion is about80×60m after agricultural levelling of much of the periphery.',s,'pp.5–6; Fig.2.9 p.13',quantity={'surface_lower_bound_ha':18,'relatively_intact_core_m':[80,60]},unit='ha and m',scope='different coverage definitions, not contemporaneous inhabited area or excavated floor area')
obs(t,'all','fortification missing','Peripheral destruction prevented tracing an enclosure wall.',s,'p.6',status='preservation-limited absence',missing_reason='Destroyed perimeter; the author’s expectation that a large town had a wall is not an observed wall.')
obs(t,'all','well missing','No Harappan well had been excavated; two farmer-reported wells and surface wedge bricks are leads.',s,'p.5',status='excavated absence plus unverified reports',missing_reason='Farmer accounts and brick types do not yield excavated well identities or a town count.')
obs(t,'I as Shinde labels it','early dwelling','A shallow oval pit dwelling with postholes is reported below rectangular mud-brick architecture.',s,'pp.39,41–44; Figs5.2–5.5',status='architectural observation; chronological attribution contested within report',uncertainty='Final summary p.839 places the sampled earliest material in Mature Harappan on pottery/AMS evidence.')
obs(t,'IIA–IIB','house material','Walls and foundations are principally mud brick; fired brick occurs in baths/drainage and some foundations or strengthening additions. Source brick ratios are1:2:4.',s,'p.45',quantity=[1,2,4],unit='thickness:width:length ratio',scope='reported building practice; material quantities not measured')
obs(t,'IIA to IIB','plan retention','The excavator says the main street, lanes and complexes were established in IIA and the broad NW–SE parallelogram pattern continued in IIB.',s,'p.45; Fig.5.1 p.41',status='excavator planning synthesis',uncertainty='This concerns broad framework; later local lane encroachments are separately reported.')
obs(t,'Mature Harappan, index trench1C11','rebuilding count','At least six mud-brick structural phases were inferred in the index trench, with two measured upper walls sharing orientation.',s,'p.31; Fig.4.3',quantity={'lower_bound':6},unit='structural phases',scope='one deep index trench; not six town-wide rebuilding episodes')
obs(t,'IIA then later addition','lane occupation','A1.50×1.43m bathing platform encroached on the western exposed end of East Area Lane1.',s,'p.70; Fig.5.38',quantity=[1.5,1.43],unit='m',scope='one later platform at East Area Lane1; distinct from Central Area Lane1',uncertainty='Later relative to lane; source does not give a separately dated construction boundary.')
obs(t,'IIA then later addition','lane occupation','Structure11A was added into the western end of East Area Lane2, whose earlier exposed width was1.90m.',s,'p.78; Figs5.47–5.48',quantity=1.9,unit='m',scope='East Area Lane2 before encroachment; no town-wide street loss estimate')
obs(t,'IIB and later repair','street encroachment','Structure3I received a55cm external strengthening wall exposed for2.10m that encroaches into the street.',s,'p.117; Fig.5.88',quantity={'addition_width_m':0.55,'exposed_length_m':2.1},unit='m',scope='one eastern buttress of Structure3I',uncertainty='Repair and diminished street importance are source interpretations; exact date unresolved.')
obs(t,'IIB','complex enlargement','Complex2 has an earlier6.20×4.20m enclosure; outer brick courses thickened its walls and an extension formed another complex.',s,'p.97; Figs5.69–5.71',quantity=[6.2,4.2],unit='m',scope='earlier Complex2 footprint, not final complex or household size')
obs(t,'IIB','household inference','The report interprets Complex3 as eight households using room size, floors, kitchens and storage facilities.',s,'pp.141–142',quantity=8,unit='inferred households',scope='one partly exposed multiroom complex',status='excavator social/function interpretation',uncertainty='Eight observed families is not a count; proposed shared extended-family residence needs independent activity/deposition evidence.')
obs(t,'IIB','room exposure','Nine rooms4A–4I of Complex4 were labelled; the building extends into unexcavated areas.',s,'p.143',quantity=9,unit='labelled excavated rooms',scope='one partial complex; not nine buildings')
obs(t,'IIB','lane drainage','Central Area Lane3 is1.60m wide and exposed20m; a40cm-wide drain is exposed19.40m.',s,'pp.142–143; Fig.5.114',quantity={'lane_width_m':1.6,'lane_exposure_m':20,'drain_width_m':0.4,'drain_exposure_m':19.4},unit='m',scope='one lane/drain pair; no full-site drainage fraction')
obs(t,'Mature Harappan broad attribution','kiln','A clay-lined pear-shaped kiln2.10m long was found70m southwest of Locality1, attributed by associated sherds.',s,'pp.164–166; Figs5.139–5.141',quantity={'kiln_length_m':2.1,'offset_m':70},unit='m',scope='one exposed kiln; firing function inferred from form and burning',basis='associated Mature Harappan pottery, not directly dated construction',uncertainty='No pots in situ; original function attribution is comparative.')
obs(t,'I and IIA–IIC as Shinde labels them','chronology proposal','Chapter4 assigns3500–2600BC to I,2600–2400BC to IIA,2400–2200BC to IIB and2200–2000BC to IIC.',s,'pp.38–39',status='tentative excavator chronology',basis='ceramic comparison and general chronology; author says phase dates require more support',uncertainty='The final summary and AMS chapter conflict with the early start; IIC deposits were removed. Do not convert these labels into exact wall dates.')
obs(t,'sampled earliest and Mature Harappan levels','chronology disagreement','Osada concludes that pottery and AMS results favor a Mature Harappan date for sampled lower levels, while leaving earlier occupation possible.',s,'p.839, third paragraph',status='explicit within-report disagreement',basis='pottery and AMS evidence discussed by report editor',uncertainty='Shinde’s Early Harappan attribution is preserved separately; no single founding date adopted.')
obs(t,'dated sample','AMS method','The laboratory calibrated with OxCal4.1 and IntCal09 and gives68.2% and95.4% ranges.',s,'p.831, chapter13',status='laboratory method',basis='Paleo-Labo AMS dating group',uncertainty='A 2011 calibration is source evidence; no new calibration or Bayesian occupation-boundary model performed.')
obs(t,'Harappan Phase2, Central Area Tr1D5','dated charcoal','PLD-15052 is3975±25BP rounded; published95.4% calibrated ranges are2571–2513BC(50.3%) and2503–2462BC(45.1%).',s,'Table13.1 p.832 and Table13.2 p.833 row2',status='laboratory determination',basis='carbonized wood; OxCal4.1/IntCal09',uncertainty='Charcoal dates growth/death, with residuality/old wood and construction association unadjudicated; no exact occupation duration.')
obs(t,'Gupta label in dated-sample table','residual context problem','PLD-12422 is labelled Tr1E1/St3N in sample table but Gupta in result table,1390±20BP and616–666AD at95.4%.',s,'Table13.1 p.832; Table13.2 p.834 row25',status='documented cross-table chronological caution',basis='carbonized wood; OxCal4.1/IntCal09',uncertainty='Do not date Harappan Structure3N or its finds by sharing this label; detailed sampling/deposition relation needs adjudication.')

# Rakhigarhi: source draft kept explicit; room counts and assigned functions separate.
t='rakhigarhi';s='EAST-NATH2014-DRAFT'
obs(t,'all','location conflict','The draft gives29°17′30″N,76°06′50″E at p.128 and cites an older toposheet point29°16′N,76°10′E at p.7.',s,'pp.7,128',basis='source geographic descriptions',uncertainty='Points differ; datum and archaeological reference point not specified. Do not treat older toposheet coordinate as a surveyed city centre.')
obs(t,'all','area conflict','The draft describes seven mounds and300ha but also says3km radius in the same sentence.',s,'p.128, Archaeological context',status='source numerical inconsistency',quantity={'reported_ha':300,'reported_radius_km':3,'mounds':7},unit='source area, radius and mound count',scope='archaeological residue envelope; definitions inconsistent',uncertainty='A3km-radius disk is2827ha, so300ha cannot be derived from that radius. No repaired area silently selected.')
obs(t,'all','preservation and exposure','A large portion is under modern village/cultivation; RGR6 had only three trenches in the reported three seasons.',s,'pp.96,121',quantity=3,unit='trenches',scope='RGR6 report-date exposure; not all excavation at Rakhigarhi')
obs(t,'I and II','relative occupation','RGR1 had6m of deposits, with4m assigned to I and2m to II.',s,'p.94',quantity={'total_m':6,'period_I_m':4,'period_II_m':2},unit='m',scope='RGR1 selected cutting; thickness is not duration')
obs(t,'I, RGR6 sequence','form change','The draft describes a partly exposed2m circular house, later rectangular walls and a subsequent street/room layout.',s,'pp.121–122',quantity=2,unit='m',scope='diameter of one circular structure',uncertainty='RGR6 phase numbering differs from broad I/II schemes elsewhere in the draft; preserve local sequence without forcing a cross-mound match.')
obs(t,'I, RGR6 PhaseV','room exposure','Seven rooms in one complex open toward lanes/street in the exposed RGR6 PhaseV layout.',s,'p.122',quantity=7,unit='rooms',scope='one partial complex',uncertainty='The draft calls it a market from entrances; market function is an interpretation, not a counted shop category.')
obs(t,'II','building materials','Houses are sun-dried brick in clay mortar; baked bricks concentrate in wet installations, and a wooden doorway beam is reported.',s,'pp.108–109',uncertainty='Wood species unassigned; mortar identifications are report descriptions without laboratory methods here.')
obs(t,'II','plan retention','The report says PeriodII followed the predecessor street arrangement in RGR2.',s,'p.113',status='excavator planning synthesis',uncertainty='No cross-mound, coeval full-city plan; incomplete figure references limit geometric verification.')
obs(t,'II, RGR2 PhaseIV to V','fortification rebuild','The partially N–S fortification of PhaseIV was reconstructed in PhaseV.',s,'p.118',uncertainty='No dated sampled bond to a true-north surveyed face.')
obs(t,'II, RGR2 PhaseV','rectangular block count','An L-shaped mud-brick structure contains ten small blocks; the report calls it a granary.',s,'pp.119–121',quantity=10,unit='architectural blocks',scope='one exposed L-shaped structure',status='observed blocks; granary function is excavator interpretation',uncertainty='Barley in accumulated cell earth is reported p.121; primary grain storage versus later fill requires contextual/taphonomic analysis.')
obs(t,'II, RGR2 PhaseV','room exposure','A neighboring complex has five similar rooms plus two larger rooms, with differing entrance directions.',s,'p.119',quantity=7,unit='rooms',scope='one exposed complex',uncertainty='Source shopping-arcade/market attribution retained as interpretation; seven observed commercial premises not established.')
obs(t,'II, RGR2 PhaseV','platform dimensions','A large podium measures22×12m and shows13 mud-brick courses in its western face.',s,'p.120',quantity={'dimensions_m':[22,12],'visible_courses':13},unit='m and courses',scope='one exposed podium')
obs(t,'II, RGR2 PhaseV','burning features','Four square burning features are described in a N–S series on the podium, about48×50cm each.',s,'p.120',quantity={'features':4,'dimensions_cm':[48,50]},unit='features and cm',scope='one podium series',status='reported structures; fire-altar/religious function is excavator interpretation')
obs(t,'II','well exposure','Two deep baked-brick wells are reported near the southeast gate and western corner of a podium.',s,'pp.113–114',quantity=2,unit='exposed wells',scope='reported excavation, not total ancient city wells',uncertainty='Religious use of second well is a source proposal.')
obs(t,'I–II','occupation duration missing','The draft gives phase-associated radiometric ranges in yearsBP with ambiguous calibrated wording, not a defensible start/end boundary for each architectural system.',s,'p.129',status='source limitation',basis='draft ranges without sample-to-construction model',missing_reason='No occupation duration computed; lab tables, calibration convention and wall joins need separate review.')

# Surkotada: source-specific phase labels and rebuilding are retained.
t='surkotada';s='EAST-JOSHI1990'
obs(t,'IA','partial house exposure','No complete IA house plan is available because early-level excavation was restricted.',s,'p.44; PDF index64',status='documented exposure limitation',missing_reason='Earlier house census cannot be reconstructed from partial walls.')
obs(t,'IA','lanes and drainage','A4.20m lane flanked by houses and a soakage jar/covered drain in two construction phases is described in the residential annexe.',s,'pp.45–46; PDF indices65–66',quantity=4.2,unit='m',scope='one exposed residential-annexe lane; not typical town street width')
obs(t,'IA to IB','retained plan','IB used the same citadel and residential-annexe areas; the IA rampart was reused with a mud-brick inner revetment.',s,'pp.46–48; PDF indices66–68',uncertainty='No settlement-wide house count or calendar duration follows from reuse.')
obs(t,'IB','entrance relocation','The IA southeastern annexe entrance was not used in IB; a southern9.05×4m rectangular structure with openings was built instead.',s,'p.48; PDF index68',quantity=[9.05,4],unit='m',scope='one entrance complex; functional role inferred from gaps and paving')
obs(t,'IB to IC','destruction and rebuild','A fire is reported at the end of IB; IC rebuilt substantial stone fortifications and entrance works without a culture break in the report.',s,'pp.49,64–66; PDF indices69,84–86',status='reported sequence with source continuity interpretation',uncertainty='Fire extent, synchronous date and cause require independent contextual review.')
obs(t,'IC','citadel dimensions','The source gives60×60m for the inner citadel.',s,'p.49; PDF index69',quantity=[60,60],unit='m',scope='citadel interior; not entire enclosed settlement')
obs(t,'IC','house exposure','One citadel house group has nine listed rooms with individual dimensions.',s,'pp.53–54; PDF index74 for room list',quantity=9,unit='rooms',scope='one Group2 complex; not all citadel houses',uncertainty='Recorded room units are not inferred family or household totals.')
obs(t,'IC','lane width','An east–west residential-annexe lane bypasses platforms on both sides and is1.50m wide at the described segment.',s,'p.58; PDF index78',quantity=1.5,unit='m',scope='one exposed lane segment',uncertainty='Do not compare to IA4.20m lane as the same named lane without a plan/section identity join.')
obs(t,'IA–IC','source chronology','Joshi proposes occupation beginning about2300BC and ending about1750BC or later; IC discussion gives1790–1660BC from arithmetic radiocarbon dates.',s,'pp.65–66; PDF indices85–86',status='historical chronological interpretation',basis='relative ceramic chronology and author arithmetic using published BP dates',uncertainty='Different ending statements coexist in source. Not a recalibrated occupation interval; no precise duration computed.')
obs(t,'IA','founding enclosure material','The earliest enclosure contained hard yellow rammed earth with mud/mud-brick wall,40×20×10cm bricks and rubble inner veneer.', 'EAST-IAR1971','p.13; PDF index21',quantity=[40,20,10],unit='cm',scope='initial citadel wall description; size order length,width,thickness')
obs(t,'IA','annexe enclosure','A mud-brick enclosure3.25m wide surrounded the residential annexe adjoining the citadel.', 'EAST-IAR1971','p.16; PDF index24',quantity=3.25,unit='m',scope='reported annexe enclosure; not IC stone wall width')
obs(t,'IA–IC sampled sequence','excavation exposure','A140×45m southern area was excavated horizontally with additional western/central trenches.', 'EAST-IAR1971','p.13; PDF index21',quantity=[140,45],unit='m',scope='reported1971–72 operation extent; area reached at each phase not given')
obs(t,'IC','stone construction','IC fortifications were rebuilt in stone with3.5–4m average basal width and corner bastions.', 'EAST-IAR1971','p.17; PDF index26',quantity=[3.5,4],unit='m',scope='reported fortification average basal width in IC, not initial IA enclosure')
obs(t,'IC','passage closure','The intercommunicating passage between citadel and annexe was partly blocked later in IC.', 'EAST-IAR1971','p.17; plateXXVIIA',uncertainty='Closure date, authority and reason remain unspecified.')
obs(t,'all','location and printed coordinate','Joshi places Surkotada12km northeast of Adesar amid sandstone hillocks and gives23°37′N,70°50′E.',s,'p.14; PDF index32',basis='modern source description',quantity={'latitude_dms':'23 37 N','longitude_dms':'70 50 E'},unit='source DMS',scope='printed site coordinate; not accepted survey point',uncertainty='The longitude conflicts with the corrected archaeological location in the prior town-axis register. Retain as source assertion and do not use it for plan registration or horizon calculation.')
obs(t,'IC','annexe dimensions','Joshi reports60×55m for the residential complex beside the60×60m citadel.',s,'p.26; PDF index44',quantity=[60,55],unit='m',scope='reported IC residential complex interior; separate from citadel dimensions')
obs(t,'IA–IC','structural phases in sections','The citadel stratigraphic account identifies three IA, two IB and three IC structural phases; the annexe section also distinguishes3,2,3 phases.',s,'p.28; PDF index46',quantity={'citadel':{'IA':3,'IB':2,'IC':3},'annexe':{'IA':3,'IB':2,'IC':3}},unit='successive structural phases',scope='reported section sequences; do not double-count phases across areas as16 independent town episodes')

# Calendar fields retain their source conventions, independently of feature measurements.
date_fields = {
    'EAST-KALIBANGAN-017': dict(convention='historical BC before radiocarbon corrections; not calibrated BC',
        intervals=[dict(phase='I',earlier=2450,later=2300,unit='source BC'),
                   dict(phase='II',earlier=2300,later=1750,unit='source BC')],
        occupation_duration_years=None, missing_reason='No modern calibrated start/end boundary model.'),
    'EAST-BANAWALI-008': dict(convention='excavator approximate duration',
        source_approximate_duration_years=500, occupation_duration_years=None,
        missing_reason='No start/end boundary model; approximate duration is the source estimate.'),
    'EAST-KANMER-015': dict(convention='authors broad AMS-based urban bracket',
        intervals=[dict(phase='urban',earlier=2500,later=2000,unit='source BC')],
        source_approximate_duration_years=500, occupation_duration_years=None,
        missing_reason='Source bracket does not date earliest occupation or final abandonment.'),
    'EAST-FARMANA-017': dict(convention='Shinde tentative cross-dating chronology; contested within report',
        intervals=[dict(phase=p,earlier=a,later=b,unit='source BC') for p,a,b in
            [('I',3500,2600),('IIA',2600,2400),('IIB',2400,2200),('IIC',2200,2000)]],
        occupation_duration_years=None, missing_reason='Chronological disagreement and loss of upper deposits.'),
    'EAST-SURKOTADA-009': dict(convention='Joshi chronological interpretation and arithmetic radiocarbon BC',
        intervals=[dict(phase='whole occupation, one source estimate',earlier=2300,later=1750,unit='source BC'),
                   dict(phase='IC arithmetic sample bracket',earlier=1790,later=1660,unit='source BC')],
        occupation_duration_years=None, missing_reason='Alternative endings and uncalibrated arithmetic; no boundary model.')
}
for row in OBS:
    if row['id'] in date_fields:
        row['chronology_numeric'] = date_fields[row['id']]

def dump(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


ids = [x['id'] for x in OBS]
assert len(ids) == len(set(ids))
source_ids = {x['id'] for x in SOURCES}
assert all(x['source_id'] in source_ids and x['locator'] for x in OBS)
assert all(x['physical_path'].startswith('D:') for x in SOURCES)
dump('sources.json', SOURCES)
dump('observations.json', OBS)
dump('quantitative-table.json', [dict(observation_id=x['id'], town=x['town'],
    phase=x['phase'], feature=x['feature'], quantity=x['quantity'], unit=x['unit'],
    scope=x['count_or_measurement_scope'], uncertainty=x['uncertainty'],
    source_id=x['source_id'], locator=x['locator']) for x in OBS if 'quantity' in x])
dump('CHECKS.json', {
    'date':'2026-10-24', 'status':'author-checked; not independent source verification',
    'sources':len(SOURCES), 'observations':len(OBS),
    'town_counts':dict(collections.Counter(x['town'] for x in OBS)),
    'source_ids_unique':len(source_ids)==len(SOURCES), 'observation_ids_unique':True,
    'all_observations_resolve_source_and_locator':True,
    'source_assets_hashed_locally':True, 'new_downloads':0,
    'raw_assets_exported_to_repository':False,
    'scientific_test':'none; exploratory source register only',
    'known_source_conflicts':['Kalibangan180m scan versus160m HTML',
       'Kanmer76×75m versus5852m² printed area',
       'Rakhigarhi300ha versus3km radius and inconsistent local phase schemes',
       'Farmana early-date attribution versus final AMS/editor discussion']})
manifest = []
for p in sorted(LOCAL.iterdir()):
    if p.is_file() and p.name != 'derivative-manifest.json':
        b=p.read_bytes()
        manifest.append(dict(logical_path='data/raw/'+p.relative_to(RAW).as_posix(),
                             physical_path=str(p),bytes=len(b),
                             sha256=hashlib.sha256(b).hexdigest(),
                             rights='local-only source derivative',
                             kind='PDF text extraction or rendered source page'))
(LOCAL/'derivative-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources':len(SOURCES),'observations':len(OBS),
                  'towns':dict(collections.Counter(x['town'] for x in OBS))},indent=2))
