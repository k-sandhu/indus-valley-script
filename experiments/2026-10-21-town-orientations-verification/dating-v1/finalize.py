"""Source-word excerpts and coverage qualifications for the assembled register."""
for code,bp,err,ph,tr,old,young,material in [('PLD-15057',4035,25,4,'2XD3',2621,2476,'charred material'),
('PLD-15056',3945,25,1,'2D9',2564,2346,'carbonized wood'),('PLD-16350',3870,20,2,'2D9',2463,2244,'carbonized wood'),
('PLD-9491',3930,35,3,'3',2560,2298,'not specified in sample-preparation table'),
('PLD-9492',3870,35,3,'3',2467,2210,'not specified in sample-preparation table'),
('PLD-9493',3940,35,2,'3',2566,2301,'not specified in sample-preparation table')]:
    rc('farmana',code,bp,err,material,'Trench '+tr,'Harappan structural Phase '+str(ph),
       'within planned-settlement sequence; cultural IIA join unresolved',loc('paleolabo2011farmana','pp. 833-834, Table 13.2',code),
       reported_calendar=dict(scale='calibrated BC, IntCal09/OxCal',outer_envelope_2sigma_bce=[old,young],note='Source gives disjoint intervals; this is their outer envelope.'),
       notes='Rounded conventional column checked against the rendered page image. Historical intrusive determinations excluded.')
for r in RADIOCARBON:
    if r['slug']=='farmana' and r['lab_code'] not in ('PLD-9491','PLD-9492','PLD-9493'):
        r['notes']='Rounded conventional column checked against the rendered table. Historical intrusive determinations are excluded.'

def words(slug,index,quote,key,page):
    p=TOWNS[slug]['parts'][index]
    p['layout_phase'].setdefault('source_words',[]).append(dict(quotation=quote,locator=loc(key,page)))

words('mohenjo-daro',0,'mud brick perimeter wall','sindhi2026','Quoted preliminary report, p. 7')
for i in (0,):
    words('harappa',i,'delimited by massive mud-brick perimeter walls','kenoyer2008cities','manuscript p. 9')
words('harappa',1,'constructed along a different plan','kenoyer2008cities','manuscript p. 13')
for i in (2,3):
    # Phrase in the architectural synthesis; the full interpretation is in support.text.
    words('harappa',i,'walled suburbs','kenoyer2008cities','manuscript pp. 13-14')
for i in range(3): words('kalibangan',i,'two distinct parts','thapar1975','pp. 23-24')
for i in range(2): words('lothal',i,'elaborately planned','rao1979','p. 29')
words('dholavira',0,'nucleus','bisht2015','p. 95')
words('dholavira',1,'was added','bisht2015','p. 99')
words('dholavira',2,'extensive walled town','bisht2015','p. 99')
words('dholavira',3,'the lower town was added','bisht2015','p. 99')
for i in range(2): words('surkotada',i,'earliest occupants of Surkotada','joshi1990','p. 21')
for i in range(2): words('banawali',i,'de novo','joshi1999inventory','p. 22, entry 22')
words('chanhu-daro',0,'première période Indus','didier2017','p. 5')
words('kanmer',0,'a planned settlement was built','kharakwal2011','p. 373')
words('shikarpur',0,'from the very beginning of Harappan occupation','bhanajith2009','p. 1')
words('farmana',0,'at the beginning of Period-IIA','shinde2011farmana','p. 40')
words('bhirrana',0,'people stuck to a definite planning','rao2004bhirrana','p. 21')
words('kotada-bhadli',0,'Beginning_of_walled_occupation','chakraborty2024','p. 8, Fig. 5')
words('rangpur',0,'earliest Harappa settlement','rao1963rangpur','p. 36')

# Record coverage directly, including the tables whose individual values remain unavailable.
gaps={
 'mohenjo-daro':'The recent preliminary report was accessed indirectly. New sample ranges lack laboratory identifiers and conventional BP/error values in the accessible participant article. The older suite does not date first layout construction.',
 'harappa':'The recorded excavation suites are substantial but do not establish that every determination ever published for the site has been recovered. Individual context-to-part assignments remain incomplete.',
 'kalibangan':'Selected later-occupation dates and predecessor dates were combined with primary laboratory lists. Some predecessor entries still depend on an HTML transcription. The complete excavation determination inventory was not acquired.',
 'lothal':'The accessible primary laboratory lists include disputed determinations. No published calibrated start of the initial planned phase was recovered.',
 'dholavira':'Individual BP/error/context rows are in Sengupta et al. supporting Table S4, whose file route was inaccessible. Stage envelopes and the stated beginning are recorded, but no individual determinations from that study are transcribed.',
 'surkotada':'Primary laboratory lists and the excavation discussion were compared. Report and synthesis transcription disagreements remain flagged. No calibrated construction-phase start was recovered.',
 'banawali':'The layout is reassigned to IC in the excavator and ASI accounts. The selected radiocarbon suite is attributed to II; individual contexts and an IC start remain missing.',
 'rakhigarhi':'The excavation table and a further synthesis suite are recorded, with shared laboratory identifiers deduplicated. Newer calibrated observations without full lab/BP/error/context values are not converted into determination rows.',
 'chanhu-daro':'A modern field dossier and original report were inspected. Newer final-report metadata were found, but no public full text or site radiocarbon table was recovered.',
 'kanmer':'Accessible botanical and dating tables were recorded; most do not assign each individual determination to a cultural phase. The full report laboratory appendix remains a coverage target.',
 'shikarpur':'The accessible comparative table supplies phase-associated determinations, but no detailed material and trench context for each sample.'}
for slug,t in TOWNS.items():
    t['coverage']={
        'status':'accessible-source assembly; completeness not certified',
        'phase_sequence':'Published labels retained; unobserved architectural joins are explicit.',
        'radiocarbon':gaps.get(slug,'Only the accessible tables and observations specified here were recovered. A blank list does not establish absence of radiocarbon work at the site.'),
        'part_definition':'Named units are retained separately; explicitly unresolved entries are coverage placeholders and do not establish ancient planning.'}
    for p in t['parts']:
        p['layout_phase'].setdefault('source_words',[])
        if not p['layout_phase']['source_words']:
            p['layout_phase']['quotation_status']='No short founding-construction quotation recovered; inspect the cited support before accepting a layout-phase assignment.'
    for key in ('1','2','3'):
        for p in t['parts']:
            for c in p['candidates_by_level'][key]:
                c['is_approximate']=True
                c['sigma_status']='fixed assignment rule; not a newly fitted archaeological error'

# Distinguish a first plan from the later exposed enclosure at Bhirrana.
bh=TOWNS['bhirrana']
bh['parts'][0]['phases'][2]=phase('Period IIA: Early Mature Harappan',
    'Earlier Transitional Period II: overground houses, platforms, pathways and definite planning; fortification was initially tentative.',bhplan,bhcross)
bh['parts'][0]['phases'][3]=phase('Period IIB: Mature Harappan',
    'Exposed enclosure, drainage through its thickness, house complexes, streets and lanes.',bhcross)
bh['published_sequence_crosswalk']=[assertion('The first report uses I (Early), II (Transitional) and III (Mature). The revised sequence separates IA and IB from the earliest occupation and relabels Transitional II as IIA and Mature III as IIB.',loc('rao2004bhirrana','pp. 21-22'),loc('rao2005bhirrana','pp. 60, 63'))]

# The mature plan in the changed Mound E exposure must be distinguished from its antecedent enclosure.
he=TOWNS['harappa']['parts'][1]
prior=he['proposed_candidate']
he['layout_phase']['label']='Period 3A (replanned Harappan exposure)'
he['layout_phase']['support']=assertion('The source describes a changed Harappan street and city-wall plan in an excavated sector of Mound E at the transition to Period 3A. Its older enclosed settlement had an earlier plan.',loc('kenoyer2008cities','manuscript pp. 9, 13'))
he['layout_phase']['alternatives'].append(assertion('If the object being dated is the first enclosure of Mound E, rather than the exposed changed Harappan plan, Period 2 is the alternative layout phase.',loc('kenoyer2008cities','manuscript pp. 9, 13')))
he['alternative_layout_candidates']=[dict(layout_phase_label='Period 2: first enclosure',candidate=prior)]
hc=candidate(2,2600,loc('kenoyermeadow2010','p. xlv, Table 1 and note 3'),'Calibrated site phase chronology for the beginning of Period 3A; joined to the documented change of plan in Mound E.',notes='Applies to the replanned Harappan exposure. The first enclosure of the mound is an explicitly retained alternative.')
he['candidates_by_level']={'1':[],'2':[hc],'3':[]};he['proposed_candidate']=hc
he['notes']='Mound E is not assumed to preserve one unchanged grid. The candidate dates the documented mature replanning; the first enclosure has a different phase and remains an alternative.'
TOWNS['harappa']['disagreements'].append(assertion('The source describes continuity in some Harappan sectors and changed planning in another Mound E exposure. A shared founding date for every surviving plan is not established.',loc('kenoyer2008cities','manuscript p. 13')))

source('jarrige2011','Jean-François Jarrige, Aurore Didier and Gonzague Quivron',2011,
       'Shahr-i Sokhta and the chronology of the Indo-Iranian regions','Paléorient 37(2):7-34',
       'https://doi.org/10.3406/paleo.2011.5420',access_route='Persée paginated article viewer and indexed table / text; construction-to-part linkage not recovered.')
source('prabhakar2014','V. N. Prabhakar and Jaseera C. Majid',2014,
       'Preliminary Results of Excavation at Karanpura, a Harappan Settlement in District Hanumangarh, Rajasthan',
       'Man and Environment 39(2):13-41',
       'https://www.academia.edu/40455750/Preliminary_Results_of_Excavation_at_Karanpura_a_Harappan_Settlement_in_District_Hanumangarh_Rajasthan',
       access_route='Official journal contents and Harappa article introduction checked. Academia preview unavailable; full report not inspected.')
source('mittra1983iar','Debala Mittra (ed.)',1983,'Indian Archaeology 1980-81—A Review',
       'New Delhi: Archaeological Survey of India',
       'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201980-81%20A%20Review.pdf',
       access_route='Official report search-indexed title page and Pabumath notice; direct full-PDF access timed out.')
source('uolganweriwala','University of Lahore','n.d.',
       'UOL’s SoCA and IMBB lead the audio-visual documentation and genetic analysis of Ganweriwala excavation',
       'Institutional project announcement; no dated phase table',
       'https://uol.edu.pk/uols-soca-and-imbb-lead-the-audio-visual-documentation-and-genetic-analysis-of-ganweriwala-excavation/',
       access_route='Institutional web announcement; publication date not established. Used as an acquisition lead only.')
source('dales1974','George F. Dales',1974,'Excavations at Balakot, Pakistan, 1973',
       'Journal of Field Archaeology 1(1-2):3-22','https://doi.org/10.1179/jfa.1974.1.1-2.3',
       access_route='Publisher abstract inspected; full report unavailable on that route.')
for slug,keys in {'nausharo':['jarrige2011'],'ganweriwala':['uolganweriwala'],'karanpura':['prabhakar2014'],
                  'pabumath':['mittra1983iar'],'balakot':['dales1974','kenoyer1991']}.items():
    TOWNS[slug]['searched_source_keys']=keys
TOWNS['balakot']['parts'][0]['phases']=[
    phase('Period A (first report) / I (later usage)','Earlier Indus occupation beneath the mature settlement; construction sequence not recovered from the abstract.',loc('dales1974','p. 3, abstract')),
    phase('Period B (first report) / II (later usage)','Mature Indus occupation; the abstract does not identify a founding layout event.',loc('dales1974','p. 3, abstract'),loc('kenoyer1991','p. 337, Table III'))]
SOURCES['sengupta2020']['access_urls']=['https://onlinelibrary.wiley.com/doi/10.1002/jqs.3178',
 'https://www.researchgate.net/publication/338189247_Did_the_Harappan_settlement_of_Dholavira_India_collapse_during_the_onset_of_Meghalayan_stage_drought']
SOURCES['goyal2013']['access_urls']=['https://www.researchgate.net/publication/293810116_Subsistence_System_Paleoecology_and_14C_Chronology_at_Kanmer_a_Harappan_Site_in_Gujarat_India']
SOURCES['chase2020']['access_urls']=['https://www.academia.edu/43051387/Pastoralism_climate_change_and_the_transformation_of_the_Indus_Civilization_in_Gujarat_Faunal_analyses_and_biogenic_isotopes']

import re
for row in RADIOCARBON:
    e=row['error_bp']
    if isinstance(e,str):
        m=re.fullmatch(r'\+(\d+)/-(\d+)',e)
        if m:row['error_bp']={'plus':int(m[1]),'minus':int(m[2])}
    c=row['reported_calendar']
    if isinstance(c,dict) and 'central_cal_bp' in c:
        c['epoch_converted_central_year_bce']=c['central_cal_bp']-1949
        c['epoch_conversion_note']='Conversion of the printed calibrated-BP summary only; no recalibration of the conventional determination. Source inconsistencies remain flagged.'

bag=TOWNS['gola-dhoro']
bag['first_occupation']['reported_estimates']=[dict(year_bce=2600,astronomical_year=-2599,
    scale='later regional synthesis, approximate earliest occupation',locator=loc('abhayan2025','p. 6, section 4.1'))]
bag['disagreements'].append(assertion('The later faunal synthesis gives a broader earlier establishment estimate than the radiocarbon-focused comparative study. Neither supplies a separate calendar start for the enclosure phase.',loc('abhayan2025','p. 6, section 4.1'),bagdate))
TOWNS['rojdi']['first_occupation']={'year_bce':2600,'astronomical_year':-2599,
    'evidence':'The archaeobotanical synthesis describes establishment at approximately this calendar date; this is an approximate published site estimate, not an excavation start-boundary model.',
    'locators':[loc('pokharia2013review','p. 128, Rojdi paragraph')]}
for slug in ('harappa','kalibangan','dholavira','shikarpur','kanmer','gola-dhoro','khirsara','kuntasi','bhirrana','rojdi'):
    TOWNS[slug]['first_occupation']['date_qualifier']='approximate published estimate; see evidence and alternative estimates'

he['layout_phase']['alternatives']=he['layout_phase']['alternatives'][-1:]
TOWNS['harappa']['parts'][0]['alternative_layout_candidates']=[dict(layout_phase_label='Period 3A: replacement Harappan masonry',
    candidate=candidate(2,2600,loc('kenoyermeadow2010','p. xlv, Table 1 and note 3'),'Alternative architectural target: the replacement Harappan masonry, rather than the older grid.'))]
TOWNS['dholavira']['parts'][0]['alternative_layout_candidates']=[dict(layout_phase_label='Stage IIIA: castle conversion',
    candidate=candidate(3,2800,loc('bisht2015','pp. 99, 104-105'),'Alternative target: conversion of the antecedent enclosure into the developed castle.'))]
TOWNS['bhirrana']['parts'][0]['alternative_layout_candidates']=[dict(layout_phase_label='Period IIB: exposed enclosure',
    candidate=candidate(2,3051,bhdate,'Alternative architectural target: the mature enclosure described under IIB, using the newer rounded Mature Harappan phase beginning at approximately 5 calendar ka BP.',
        notes='The primary report dates the exposed wall to IIB, but its first-construction contact still needs review. This alternative is not the selected earlier-plan candidate.'))]
for row in RADIOCARBON:
    if row['slug']=='harappa':
        if row['phase_label']=='Period 2':row['relation_to_layout_phase']='AB earlier-grid layout phase; predecessor to E replanning and F/ET expansion'
        elif row['phase_label']=='Period 3A':row['relation_to_layout_phase']='E replanning phase; predecessor to F/ET expansion; later than AB earlier grid'
        elif row['phase_label'].startswith('Period 1'):row['relation_to_layout_phase']='earlier occupation before the proposed layouts; not necessarily their immediate construction predecessor'
