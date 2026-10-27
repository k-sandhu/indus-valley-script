"""Compile the hand-reviewed bibliographic and evidence registers.

This is bookkeeping, not an automated archaeological classifier.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/continuity')

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def witness(logical):
    p = ROOT / logical
    return {'logical_path': logical, 'physical_path': str(p.resolve()), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'handling': 'local-only'}

def source(sid, title, authors, year, url, citation, lineage, scope, paths=(), **extra):
    return {'id': sid, 'title': title, 'authors': authors, 'year': year, 'url': url, 'citation': citation,
            'lineage': lineage, 'inspected_scope': scope, 'accessed': '2026-10-26',
            'rights': {'status': 'rights-unverified', 'handling': 'raw and detailed derivatives local-only'},
            'witnesses': [witness(p) for p in paths], **extra}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for name in ['sources.json', 'evidence.json', 'derivatives-v1.json']:
        if (HERE / name).exists():
            raise FileExistsError(HERE / name)
    crop = read('experiments/2026-10-25-crop-continuity/source-manifest.json')['sources']
    sw = next(s for s in crop if s['id']=='SW2026')
    sources = [
        source('MK1997', 'Excavations at Harappa 1994-1995: New Perspectives on the Indus Script, Craft Activities, and City Organization',
               ['Richard H. Meadow', 'Jonathan Mark Kenoyer'], 1997,
               'https://www.harappa.com/sites/default/files/pdf/Kenoyer1997_Excavations%20at%20Harappa%201994-1995%20New%20Perspective.pdf',
               'In Bridget Allchin and Raymond Allchin, eds., South Asian Archaeology 1995, pp. 139–172.',
               'HARP Harappa excavation and regional interpretation', 'Introduction, printed p. 139, PDF p. 1; title and argument checked in the primary PDF.',
               ['data/raw/2026-10-11-societal-persistence/evidence/acquisition-v1/meadow-kenoyer1997.pdf'], access_depth='primary text'),
        source('KM2004', 'Fifty-Five Years of Archaeological Research in Pakistan: The Prehistoric Periods',
               ['Jonathan Mark Kenoyer', 'Richard H. Meadow'], 2004,
               'https://www.harappa.com/sites/default/files/pdf/Kenoyer2004_Fifty-five%20years%20of%20Archaeological%20Research%20in%20P.pdf',
               'In Craig Baxter, ed., Pakistan on the Brink: Politics, Economics, and Society. Lexington Books, pp. 191–219.',
               'HARP Harappa excavation and research synthesis', 'Printed pp. 202–203, PDF p. 7; local OCR and original page image inspected. Source title and 2004 publication checked against the publisher.',
               ['data/raw/2026-10-26-indus-living-atlas/continuity/kenoyer-meadow2004.pdf'], access_depth='primary excavator synthesis',
               metadata_url='https://www.bloomsbury.com/au/pakistan-on-the-brink-9780739104989/'),
        source('K2010', 'Measuring the Harappan world: Insights into the Indus order and cosmology',
               ['J. Mark Kenoyer'], 2010,
               'https://www.harappa.com/sites/default/files/pdf/Kenoyer%202010%20Measuring%20the%20Harappan%20World.pdf',
               'In Iain Morley and Colin Renfrew, eds., The Archaeology of Measurement: Comprehending Heaven, Earth and Time in Ancient Societies, pp. 106–121. Cambridge University Press.',
               'HARP Harappa weight measurements and broader comparative synthesis', 'Printed pp. 117 and 120, PDF pp. 13 and 16; late weight history and the stated need for a better intermediate sequence.',
               ['data/raw/2026-10-26-indus-living-atlas/continuity/kenoyer2010.pdf'], access_depth='primary specialist synthesis'),
        source('M1943', 'Chanhu-Daro Excavations 1935-36', ['Ernest J. H. Mackay'], 1943,
               'https://www.panjabdigilib.org/webuser/searches/displayPageContent.jsp?CategoryID=1&ID=2920&Searched=W3GX&page=1',
               'American Oriental Series 20. New Haven: American Oriental Society, for the American School of Indic and Iranian Studies and Museum of Fine Arts, Boston.',
               'Chanhu-daro 1935–1936 excavations', 'Preface p. ix (PDF 14), contents, pottery p. 107 (PDF 128), seals p. 143 (PDF 164). Original scan images inspected; OCR is a finding aid. Legacy phase and ethnic terminology are retained only as source labels.',
               ['research/literature/sources/mackay_1943_chandaro.pdf'], access_depth='primary excavation report',
               metadata_url='https://www.harappa.com/content/chanhu-daro-excavations-1935-1936',
               current_access='Digitization link returned 403; previously held complete scan used.'),
        source('B2015', 'Excavations at Dholavira (1989–90 to 2004–2005)', ['R. S. Bisht'], 2015,
               'https://archive.org/details/dholavirareportpreliminaryjan2015_860_K',
               'Archaeological Survey of India, preliminary report posted for comments; not a final published excavation monograph.',
               'ASI Dholavira excavation programme', 'Sections 5.6–5.7 and chronology, printed pp. 103–104, PDF pp. 120–121. Text and original pages inspected.',
               ['data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf',
                'data/raw/2026-10-11-societal-persistence/evidence/acquisition-v1/bisht2015-cover.pdf'],
               access_depth='primary preliminary excavation report',
               metadata_url='https://asi.nic.in/pdf/dholavira_excavation_report_cover.pdf',
               chronology_note='Stage ranges are the excavator’s provisional assignments, not independently remodeled direct dates for each object.'),
        source('G2012', 'Fluvial landscapes of the Harappan civilization',
               ['Liviu Giosan', 'Peter D. Clift', 'Mark G. Macklin', 'Dorian Q. Fuller', 'Stefan Constantinescu',
                'Julie A. Durcan', 'Thomas Stevens', 'Geoff A. T. Duller', 'Ali R. Tabrez', 'Kavita Gangal',
                'Ronojoy Adhikari', 'Anwar Alizai', 'Florin Filip', 'Sam VanLaningham', 'James P. M. Syvitski'], 2012,
               'https://pmc.ncbi.nlm.nih.gov/articles/PMC3387054/',
               'Proceedings of the National Academy of Sciences 109(26): E1688–E1694. DOI 10.1073/pnas.1112743109.',
               'Primary geomorphology plus previously compiled settlement distributions',
               'Brief Harappan History; Settlement Dynamics in the Harappan Domain; regional alluvial preservation. Web text and previously acquired full HTML inspected. Dating tables not reanalyzed.',
               ['data/raw/2026-10-11-early-indian-continuity/review/giosan2012.html'], access_depth='primary full text',
               doi='10.1073/pnas.1112743109', current_access='Initial web text available; later PMC page gave a challenge, Europe PMC XML 500 and alternate PDF 403. Existing full witness reused.'),
        source('GP2018', 'Landscapes of Urbanization and De-Urbanization: A Large-Scale Approach to Investigating the Indus Civilization’s Settlement Distributions in Northwest India',
               ['Adam S. Green', 'Cameron A. Petrie'], 2018, 'https://doi.org/10.1080/00934690.2018.1464332',
               'Journal of Field Archaeology 43(4): 284–299.', 'Integrated northwest India surveys, including Land, Water and Settlement fieldwork',
               'Publisher XML sections S005 Discussion and S006 Conclusions; chronology, survey coverage and proposed northeastern relocation qualifications.',
               ['data/raw/2026-10-11-societal-persistence/evidence/acquisition-v4/green-petrie2018-full.xml'],
               access_depth='primary survey-data integration', doi='10.1080/00934690.2018.1464332',
               metadata_url='https://www.repository.cam.ac.uk/items/445ace45-8184-464b-8000-0cb9379f0948'),
        source('N2020', 'Geoarchaeological insights into the location of Indus settlements on the plains of northwest India',
               ['Sayantani Neogi', 'Charles A. I. French', 'Julie A. Durcan', 'Ravindra N. Singh', 'Cameron A. Petrie'], 2020,
               'https://doi.org/10.1017/qua.2019.70', 'Quaternary Research 94: 137–155; first online 20 December 2019.',
               'Land, Water and Settlement, four excavated sites and their surrounding soil profiles',
               'Accepted manuscript PDF pp. 10–23 and supplementary pp. 57, 61–62; Alamgirpur, Masudpur and discussion. Publisher full text checked for version identity.',
               ['data/raw/2026-10-26-indus-living-atlas/continuity/neogi2020-accepted.pdf'], access_depth='primary geoarchaeological analysis',
               doi='10.1017/qua.2019.70', download_url='https://api.repository.cam.ac.uk/server/api/core/bitstreams/8239b10a-1dd9-4e78-91b5-d27e5da823b6/content',
               rights={'status':'explicit-license', 'licence':'CC BY-NC-ND 4.0 for the published article', 'handling':'Original and extracted witnesses local-only; this package provides our factual summaries.'}),
        source('S2021', 'Lipid residues in pottery from the Indus Civilisation in northwest India',
               ['Akshyeta Suryanarayan', 'Miriam Cubas', 'Oliver E. Craig', 'Carl P. Heron', 'Vasant S. Shinde', 'Ravindra N. Singh', 'Tamsin C. O’Connell', 'Cameron A. Petrie'], 2021,
               'https://pmc.ncbi.nlm.nih.gov/articles/PMC7829615/', 'Journal of Archaeological Science 125: 105291; first online 9 December 2020. DOI 10.1016/j.jas.2020.105291.',
               'Seven sites; urban/posturban comparison principally Alamgirpur and Masudpur VII; partly shares Land, Water and Settlement excavations',
               'Methods section 2.1, Tables 1 and 4, discussion section 4.4 and conclusions; complete primary XML acquired.',
               ['data/raw/2026-10-26-indus-living-atlas/continuity/suryanarayan2021.xml'], access_depth='primary analytical study', doi='10.1016/j.jas.2020.105291',
               rights={'status':'explicit-license', 'licence':'CC BY-NC-ND 4.0 for publisher article', 'handling':'Raw witness local-only; our factual summaries tracked.'}),
        source('PB2017', '‘Multi-cropping’, Intercropping and Adaptation to Variable Environments in Indus South Asia',
               ['Cameron A. Petrie', 'Jennifer Bates'], 2017, 'https://doi.org/10.1007/s10963-017-9101-z',
               'Journal of World Prehistory 30: 81–130.', 'Land, Water and Settlement excavation samples and Bates thesis; same crop observations audited on 25 October',
               'Accepted manuscript supplement Table S23, PDF pp. 91–92, plus Burj sequence discussion; prior 25 October arithmetic reused without a new statistical test.',
               ['data/raw/2026-10-25-crop-continuity/petrie-bates-2017.pdf'], access_depth='primary archaeobotanical study and supplement', doi='10.1007/s10963-017-9101-z',
               rights={'status':'explicit-license', 'licence':'CC BY 4.0', 'handling':'Full source remains local under project handling.'}),
        source('SP2013', 'Recent Excavations at Alamgirpur, Meerut District: A Preliminary Report',
               ['Ravindra N. Singh', 'Cameron A. Petrie', 'P. P. Joglekar', 'Sayantani Neogi', 'Carla Lancelotti', 'Arun K. Pandey', 'Anubha Pathak'], 2013,
               'https://www.researchgate.net/publication/283348204_Recent_Excavations_at_Alamgirpur_Meerut_District_A_Preliminary_Report',
               'Man and Environment 38(1): 32–54.', 'BHU Alamgirpur 2008 excavations; overlaps later soil, lipid and plant publications',
               'Author-deposited full-text web extraction, title page and Observations on printed pp. 53–54. Publisher abstract verifies title, authors, year and pagination. Original PDF not obtained.',
               access_depth='primary report text through web extraction; figures not visually checked',
               metadata_url='https://manandenvironment.org/images/ispqs/pdf/abs38-40.pdf',
               current_access='Direct ResearchGate HTML 403 and PDF tool click failed; visible full text used. No local original byte hash.'),
        source('SW2026', sw['title'], sw['authors'], 2026, 'https://doi.org/10.1007/s00334-026-01140-4',
               'Vegetation History and Archaeobotany; published online 23 July 2026. DOI 10.1007/s00334-026-01140-4.',
               'Jognakhera 1996 excavation, eight flotation samples; exactly the source audited by the project on 25 October',
               'Prior audited primary web-text representation, source PDF p. 7 chronology; full supplement remains unavailable. Dates rechecked against that representation, no new sample analysis.',
               ['data/raw/2026-10-25-crop-continuity/web-paper-sections-v1.txt'], access_depth='primary text representation from the preceding audit',
               doi='10.1007/s00334-026-01140-4', current_access='DOI was unavailable in the current web call; previous source witness and audit retained.'),
    ]
    by_id={s['id']:s for s in sources}
    evidence=[]
    def add(eid,sid,locator,observation,interpretation,chronology,dates,geography,domain,confidence,group,scenario,kind='observation'):
        s=by_id[sid]
        evidence.append({'id':eid,'source_id':sid,'title':s['title'],'authors':s['authors'],'year':s['year'],'url':s['url'],
            'locator':locator,'observation':observation,'interpretation':interpretation,'chronology':chronology,
            'date_range_bce':dates,'geography':geography,'marker_domain':domain,'confidence':confidence,
            'statement_kind':kind,'independence':{'group':group,'note':s['lineage']},'scenario_implications':scenario})
    add('E01','MK1997','Printed p.139; PDF p.1, Introduction',
        'The excavators distinguish widely shared urban traits from older, locally diverse farming and pastoral traditions.',
        'A definition based on urban traits will stop recognizing some continuing local activity when those traits disappear.',
        'Early through Late Harappan regional framework', [3500,1300], ['Indus domain','Harappa'],
        ['classification','domestic practices'], 'high for the stated scholarly argument; not a measured rate', 'HARP',
        ['regionalization plausible; classification is selective'], 'author interpretation')
    add('E02','KM2004','Printed pp.202–203; PDF p.7, Table10.2 and Late Harappan paragraph',
        'The excavators describe regional exchange and craft activity at Harappa in Cemetery H levels, approximately 1800 to perhaps 1500 BCE, alongside loss of script and standardized weights.',
        'Local posturban activity is visible even where particular administrative markers cease. The prose and provisional phase table have different end-date uncertainty.',
        'Late Harappan/Cemetery H, source prose c.1800–1500 BCE', [1800,1500], ['Harappa','Punjab, Pakistan'],
        ['occupation','craft','writing','weights'], 'moderate to high for site activity; final calendar limit provisional', 'HARP',
        ['supports local continuation with institutional change'])
    add('E03','K2010','Printed pp.117,120; PDF pp.13,16',
        'The chapter reports loss of cubical stone weights after the urban period and a related system in Early Historic South Asia, while calling the intervening relationship unresolved.',
        'Later recurrence requires a dated transmission sequence. It cannot fill the intervening centuries; Dholavira supplies a regional exception to the broad disappearance statement.',
        'Urban end c.1900 BCE; Early Historic comparison c.600 BCE', [1900,600], ['Harappa','northern South Asia'],
        ['weights','institution'], 'high for the source statement; direct transmission unestablished', 'HARP',
        ['broad marker discontinuity; institution continuity requires intermediates'], 'author interpretation')
    add('E04','M1943','Printed p.143; PDF p.164, seals and amulets discussion',
        'Most Jhukar seals or amulets described here are round. The excavator records no clear script on them, while allowing ambiguous marks.',
        'The familiar inscribed square seal ceases to be the only relevant search target. This absence cannot establish whether writing continued on an unpreserved medium.',
        'Jhukar is stratigraphically post-Harappan here; no modern absolute date inferred from this legacy report', None,
        ['Chanhu-daro','Sindh, Pakistan'], ['seals','writing'], 'high for the inspected assemblage; relative chronology only', 'CHANHUDARO1935',
        ['administrative material changed; medium-switch remains untested'])
    add('E05','M1943','Preface printed p.ix; PDF p.14',
        'The report describes extensive brick removal in upper Mound II and disturbed contexts containing older objects.',
        'An urban-period object in a later layer can be residual or reused. Such a find needs a depositional assessment before counting as continued manufacture.',
        'Successive Harappan and Jhukar occupations; relative chronology', None, ['Chanhu-daro','Sindh, Pakistan'],
        ['taphonomy','reuse'], 'high for reported disturbance; specific reuse is an excavator inference', 'CHANHUDARO1935',
        ['redeposition can create apparent continuity'])
    add('E06','B2015','Section5.6; printed p.103, PDF p.120; chronology p.104',
        'Stage VI follows a short desertion and occupies a reduced area. Rectangular inscribed seals and cubical chert weights persist, alongside changed pottery and housing.',
        'The report describes marker persistence into a reduced settlement, challenging a single conventional cutoff. Its phase envelope spans 1900 BCE; primary contexts and absolute dates are needed to establish post-1900 last use and exclude residual objects.',
        'Preliminary Stage VI assignment c.1950–1800 BCE', [1950,1800], ['Dholavira','Kutch, Gujarat'],
        ['occupation','architecture','writing','weights'], 'high for report description; moderate for provisional absolute placement', 'ASI_DHOLAVIRA',
        ['supports phased regionalization and local interruption'])
    add('E07','B2015','Section5.7 and chronology; printed p.104, PDF p.121',
        'Stage VII follows a longer, unquantified desertion and contains circular houses with urban attributes absent. Its provisional range is c.1500–1450 BCE.',
        'Return to the same site can follow a real break. Similarity to current regional houses cannot establish occupation through the intervening centuries.',
        'Preliminary Stage VII assignment c.1500–1450 BCE', [1500,1450], ['Dholavira','Kutch, Gujarat'],
        ['occupation','architecture'], 'high for the reported gap and forms; moderate for calendar range', 'ASI_DHOLAVIRA',
        ['rebuts universal uninterrupted same-site occupation'])
    add('E08','G2012','Settlement Dynamics in the Harappan Domain, Sindh preservation paragraph',
        'The primary landform study distinguishes well-preserved upper Sindh sites from southwestern alluvial areas where later sediment could cover former settlements.',
        'Burial is a geographically specific mechanism. The statement predicts where surface surveys can miss deposits; it does not count hidden settlements.',
        'Holocene landform sequence, including Harappan occupation', None, ['upper Sindh','southwestern Sindh'],
        ['preservation','survey'], 'high for mapped landform contrast; individual buried-site presence untested', 'GIOSAN_GEOMORPH',
        ['supports differentiated detectability, not universal burial'], 'author inference from primary geomorphology')
    add('E09','G2012','Brief Harappan History; Settlement Dynamics in the Harappan Domain',
        'The article combines regional abandonment and smaller posturban settlements with later activity in Kutch; these settlement observations draw on earlier archaeological sources.',
        'Regional loss and redistribution can coexist. This synthesis is not an independent excavation count or a demonstrated migration route.',
        'Posturban transition after c.1900 BCE; source uses years ago', [1900,1000], ['Indus domain','Kutch','Punjab','Haryana','upper Ganges'],
        ['settlement'], 'moderate; broad compiled chronology', 'COMPILED_SETTLEMENTS',
        ['regionalization and local abandonment both supported'], 'author synthesis')
    add('E10','GP2018','XML S005 Discussion and S006 Conclusions',
        'Integrated surveys show different local settlement trajectories. The authors identify possible northeastern reoccupation but require renewed coverage to separate it from earlier survey practices.',
        'Mapped site density is not a direct census of people. Apparent relocation must survive a common survey frame and reliable phase assignments.',
        'Early, Mature, Late Harappan and Painted Grey Ware survey categories', [2600,700], ['northwest India','Haryana','Rakhigarhi hinterland'],
        ['survey','relocation'], 'high for documented survey qualifications; movement of particular people untested', 'LWS_SURVEY_COMPILE',
        ['distribution change supported; simple eastward arrows premature'])
    add('E11','N2020','Accepted manuscript pp.10–23; supplement pp.57,61–62',
        'Soil profiles recover former surfaces and low levee or dune settings now obscured by later modification. Masudpur profiles include buried horizons below the current surface.',
        'A flat modern field can conceal earlier landscape structure. Buried soil alone does not establish a settlement or its date.',
        'Holocene geomorphology associated with named Indus sites; individual profile dates retained in the source', None,
        ['Alamgirpur','Masudpur I','Masudpur VII','Burj','northwest India'], ['preservation','landscape'],
        'high for sampled profiles; coverage outside profiles unmeasured', 'LWS_SOILS',
        ['supports sub-surface sampling before negative conclusions'])
    add('E12','S2021','Sections2.1 and4.4; Tables1,4; Fig.7',
        'The study analyzed 172 sherds from seven sites. Its small urban/posturban comparisons at Alamgirpur and Masudpur VII found no statistically detected shift in the reported lipid isotope variables.',
        'Domestic practices can remain archaeologically measurable across changing material categories. Limited samples and mixed product signatures prevent an equivalence claim.',
        'Mature Harappan c.2600/2500–1900 BCE and Late Harappan c.1900–1300 BCE; samples assigned by context', [2600,1300],
        ['Alamgirpur','Masudpur VII','northwest India'], ['foodways','domestic practices'],
        'high for the published analytical result; moderate for culinary continuity', 'LWS_LIPIDS',
        ['supports selective daily-practice continuity'])
    add('E13','PB2017','Supplement TableS23; accepted PDF pp.91–92; prior crop audit run-v2',
        'Bahola retains winter and summer crop categories in Late Harappan and Painted Grey Ware assemblages. The published winter share rises from 6.87% to 17.29%.',
        'Repertoire retention can accompany changing proportions. Pooled plant-remain percentages do not establish unchanged fields, diets or social institutions.',
        'Source-assigned Late Harappan and Painted Grey Ware phases', [1900,700], ['Bahola','Haryana'],
        ['agriculture'], 'high for published phase summaries; local management continuity unmeasured', 'LWS_PLANTS',
        ['selective retention with adaptation; prior audited evidence'])
    add('E14','PB2017','Burj site sequence discussion and supplementary TablesS8–S9',
        'Burj has Early Harappan and Painted Grey Ware plant assemblages separated by an occupation break.',
        'Repeated use of a location is compatible with a hiatus. This site is a required counterexample when designing a continuity sample.',
        'Early Harappan to later Painted Grey Ware; no continuous intervening sequence', [3200,700], ['Burj','Haryana'],
        ['occupation','agriculture'], 'high for reported sequence; exact break duration not estimated here', 'LWS_PLANTS',
        ['rebuts inferring uninterrupted occupation from multiple phases'])
    add('E15','SP2013','Observations; printed pp.53–54',
        'Alamgirpur’s excavators report no clear stratigraphic break and possible pottery overlap, while noting a protracted gap in available AMS dates and seven failed dating submissions.',
        'Stratigraphic proximity and calendar continuity remain distinct. The dating conflict is unresolved and the transition needs new directly associated samples.',
        'Harappan-to-Painted Grey Ware transition; precise bridge unresolved', None, ['Alamgirpur','upper Ganges basin'],
        ['occupation','chronology'], 'high for report’s stated conflict; uninterrupted occupation unresolved', 'ALAMGIRPUR2008',
        ['a strong test case requiring chronology repair'])
    add('E16','SW2026','Primary chronology, source PDF p.7; prior audit REPORT and run-v2',
        'The Jognakhera paper reports green gram at 1880–1691 cal BCE and rice at 1517–1428 cal BCE.',
        'Dated posturban crops supply intermediate activity. The sampled deposits still need a complete phase join before assigning them to a named later pottery culture.',
        'Two source-reported calibrated intervals; not a continuous occupation span', [1880,1428], ['Jognakhera','Haryana','Ghaggar basin'],
        ['agriculture','chronology'], 'moderate; source supplement and full sample-date ledger remain unavailable', 'JOGNAKHERA1996',
        ['posturban farming documented; prior exposed evidence'])

    (HERE/'sources.json').write_text(json.dumps({'schema_version':'1.0','study':'INDUS-MARKER-CONTINUITY-2026-10-26',
        'selection':'Bounded purposive source review; publication count does not measure independent replication.',
        'sources':sources},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'evidence.json').write_text(json.dumps({'schema_version':'1.0','study':'INDUS-MARKER-CONTINUITY-2026-10-26',
        'date_convention':'BCE pairs are older to younger; null means no absolute range justified here. Broad phase brackets are display context, not direct dates of every object.',
        'independence_note':'Groups identify a principal lineage; HARP sources share field observations. Soil, lipid and plant measurements differ but share LWS sites, context chronology and excavation selection. No vote count or pooled significance is calculated.',
        'evidence':evidence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    derivatives=[]
    for p in sorted(RAW.iterdir()):
        if p.is_file():
            prefix=p.name.split('-')[0]
            parent={'KM2004':'KM2004','M1943':'M1943','N2020':'N2020','K2010':'K2010','B2015':'B2015'}.get(prefix)
            if p.name in ['suryanarayan2021.xml','neogi2020-accepted.pdf','kenoyer2010.pdf','kenoyer-meadow2004.pdf']:
                continue
            derivatives.append({'source_id':parent,'logical_path':'data/raw/2026-10-26-indus-living-atlas/continuity/'+p.name,
                'physical_path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                'method':'PyMuPDF page rendering or text extraction; Tesseract English OCR where named; metadata JSON for OCR manifest',
                'handling':'local-only'})
    (HERE/'derivatives-v1.json').write_text(json.dumps({'derivatives':derivatives},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sources':len(sources),'evidence_rows':len(evidence),'local_witnesses':sum(len(s['witnesses']) for s in sources),'derivatives':len(derivatives)},indent=2))

if __name__=='__main__':
    main()
