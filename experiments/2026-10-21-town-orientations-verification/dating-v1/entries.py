"""Curated source observations. Executed by the owned assembly script."""

for key,authors,year,title,volume,pages,doi in [
 ('tata1963','S. Kusumgar, D. Lal and R. P. Sarna',1963,'Tata Institute Radiocarbon Date List I',5,'273-282','10.1017/S0033822200036894'),
 ('tata1964','D. P. Agrawal, S. Kusumgar, D. Lal and R. P. Sarna',1964,'Tata Institute Radiocarbon Date List II',6,'226-232','10.1017/S0033822200010705'),
 ('tata1965','D. P. Agrawal, S. Kusumgar and D. Lal',1965,'Tata Institute Radiocarbon Date List III',7,'291-295','10.1017/S0033822200037279'),
 ('tata1966','D. P. Agrawal and Sheela Kusumgar',1966,'Tata Institute Radiocarbon Date List IV',8,'442-452','10.1017/S003382220000028X'),
 ('tata1968','D. P. Agrawal and Sheela Kusumgar',1968,'Tata Institute Radiocarbon Date List V',10,'131-143','10.1017/S0033822200019974')]:
    source(key,authors,year,title,f'Radiocarbon {volume}:{pages}','https://doi.org/'+doi,download=key+'.pdf',
           notes='Primary laboratory date list. Conventional ages use the Libby half-life; printed B.C. values are uncalibrated.')

# Primary contexts supplement the later Kalibangan compilations without hiding
# discrepancies between separately reported laboratory fractions.
for code,bp,error,material,context,pl,relation,key,page in [
 ('TF-25',3930,110,'charcoal','KLB; field F1-2.15 m / F2-8.20 m; depth 0.37 m; Harappa Culture','Period II, subphase unspecified','layout phase','tata1963','p. 280'),
 ('TF-150',3740,100,'charcoal mixed with earth','KLB-2, ZE1 Q4, layer 6; field 1962-63-16; latest Harappan','Period II','layout phase','tata1964','p. 229'),
 ('TF-139',3775,100,'charcoal mixed with earth','KLB-2, XA8 Q2, layer 6; field 1962-63-2; middle Harappan','Period II','layout phase','tata1964','p. 229'),
 ('TF-151',3800,100,'charcoal mixed with earth','KLB-2, E1 Q1, layer 17; field 1962-63-17; middle Harappan','Period II','layout phase','tata1964','p. 229'),
 ('TF-147',3865,100,'charcoal mixed with earth','KLB-2, E1 Q1, layer 23; field 1962-63-13; lower-middle Harappan','Period II','layout phase','tata1964','p. 229'),
 ('TF-145',3895,100,'charcoal mixed with earth','KLB-2, XA8 Q3, layer 14; field 1962-63-10; lower-middle Harappan','Period II','layout phase','tata1964','pp. 229-230'),
 ('TF-160',4060,100,'charcoal','KLB-1, XC1 Q2, layer 12; field 1962-63-10; Harappa Culture','Period II','layout phase','tata1965','p. 293'),
 ('TF-163',3910,100,'charcoal','KLB-1, YE1 Q4, layer 2R; field 1962-63-13; Harappa Culture','Period II','layout phase','tata1965','p. 293'),
 ('TF-165',3800,100,'charcoal','KLB-1, XD1 Q1 and Q2, layer 2R; field 1962-63-15; Sothi Culture','Period I','predecessor to layout','tata1965','p. 293'),
 ('TF-154',3665,110,'charcoal','KLB-1, ZC2, layer 8; field 1962-63-2; Sothi Culture','Period I','predecessor to layout','tata1965','p. 293'),
 ('TF-161',3930,100,'charcoal','KLB-1, YF2 Q2, layer 3; field 1962-63-11; Sothi Culture','Period I','predecessor to layout','tata1965','p. 293'),
 ('TF-157',4120,110,'charcoal','KLB-1, YF2 Q3, layer 5; field 1962-63-7; Sothi Culture','Period I','predecessor to layout','tata1965','p. 293'),
 ('TF-162',3940,100,'charcoal','KLB-1, XE1 Q2, pit 1 sealed by layer 3 and cut into natural; field 1962-63-12; Sothi Culture','Period I','predecessor to layout','tata1965','p. 293'),
 ('TF-138',3075,100,'charcoal','KLB-2, A7, layer 3; field 1962-63-1; uppermost levels, possible contamination','Period II','layout phase, anomalous result','tata1966','p. 447'),
 ('TF-244',3250,90,'charcoal','KLB-2, E2, layer 2; field 1963-64-4; uppermost levels, possible contamination','Period II','layout phase, anomalous result','tata1966','p. 447'),
 ('TF-143',3510,110,'wood','KLB-2, YA1, layer 2; field 1962-63-8','Period II','layout phase','tata1966','p. 447'),
 ('TF-152',3615,85,'charcoal','KLB-2, XB9, layer 5; field 1962-63-18','Period II','layout phase','tata1966','p. 447'),
 ('TF-142',3635,100,'charcoal','KLB-2, XB8, layer 4; field 1962-63-7','Period II','layout phase','tata1966','p. 447'),
 ('TF-149',3675,140,'charcoal','KLB-2, ZE1, layer 3; field 1962-63-15','Period II','layout phase','tata1966','p. 448'),
 ('TF-141',3705,110,'charcoal','KLB-2, A7, layer 7; field 1962-63-6','Period II','layout phase','tata1966','p. 448'),
 ('TF-153',3910,110,'charcoal','KLB-2, XB7, hearth sealed by layer 1; field 1962-63-20','Period II','layout phase','tata1966','p. 448'),
 ('TF-155',4195,115,'charcoal','KLB-1, ZB2, layer 9B; field 1962-63-3; stratigraphic position uncertain in laboratory comment','Period I','predecessor to layout, context uncertain','tata1966','p. 448'),
 ('TF-240',3610,110,'charcoal','KLB-1, XD1, pit 3 sealed by layer 3; field 1963-64-1; laboratory calls result too young','Period I','predecessor to layout, anomalous result','tata1966','p. 448'),
 ('TF-156',3740,105,'charcoal','KLB-1, XE1, layer 2; field 1962-63-5; laboratory calls result too young','Period I','predecessor to layout, anomalous result','tata1966','p. 448'),
 ('TF-241',4090,90,'charcoal','KLB-1, XD1, pit 4 sealed by layer 2; field 1963-64-2','Period I','predecessor to layout','tata1966','p. 448'),
 ('TF-605',3810,105,'charcoal','KLB-1, ZB9 Q3, layer 10; field 1965-66-7; late phase of citadel fortification','Period II','layout phase','tata1968','p. 134'),
 ('TF-607',3930,120,'charred wheat and charcoal bits','KLB-2, A8 Q2, layer 18; field 1965-66-9; early Harappan levels','Period II','layout phase','tata1968','p. 134'),
 ('TF-608',3910,110,'charred wheat','KLB-2, A6 Q2, layer 18; field 1965-66-10; early Harappan levels','Period II','layout phase','tata1968','p. 134')]:
    existing=next((r for r in RADIOCARBON if r['slug']=='kalibangan' and r['lab_code']==code and r['conventional_age_bp']==bp and r['error_bp']==error),None)
    if existing:
        existing['material']=material; existing['context']=context
        existing['notes']+=' Primary material and context: '+json.dumps(loc(key,page,code),ensure_ascii=False)
    else:
        rc('kalibangan',code,bp,error,material,context,pl,relation,loc(key,page,code),
           reported_calendar=dict(scale='uncalibrated B.C.; conventional BP minus 1950'),
           notes='Primary laboratory report. A separately reported BS fraction, if present, is retained separately.')
for r in RADIOCARBON:
    if r['slug']=='kalibangan' and r['lab_code']=='TF-957':
        r['reported_calendar']=dict(scale='Calib-3 corrected calendar dates',range_2sigma=['900 BCE','70 CE'],range_2sigma_astronomical=[-899,70],
                                    note='The compilation mixes BCE and CE endpoints. This anomalously young result is retained for audit.')

source('rao1979','S. R. Rao',1979,'Lothal: A Harappan Port Town (1955-62), Volume I',
       'Memoirs of the Archaeological Survey of India 78. New Delhi: Archaeological Survey of India.',
       'https://archive.org/details/lothalvol1',download='lothal1979.pdf',
       notes='Scanned text volume; printed pages used. Plates are absent from this copy. Internet Archive uploader licensing is not accepted as proof of ASI rights.')
ll=loc('rao1979','p. 29; p. 44; p. 85, section 2.A')
lp=[phase('Period A, Phase I','Village with a protective mud bund; earlier Harappan and local ceramic occupation. Street plan was not established by the excavation.',loc('rao1979','pp. 28, 44, 85')),
    phase('Period A, Phase II (IIA, IIB, IIC)','Systematic plan of raised house platforms, strengthened perimeter protection, acropolis and lower-town blocks.',loc('rao1979','pp. 29-30, 85-87')),
    phase('Period A, Phase III (IIIA, IIIB)','Reconstruction following flooding, raised platforms and expanded settlement.',loc('rao1979','p. 31')),
    phase('Period A, Phase IV','Reduced rebuilding and encroachment following destruction.',loc('rao1979','p. 32')),
    phase('Period B, Phase V (VA, VB)','Later occupation and diminished urban institutions.',loc('rao1979','pp. 33-35'))]
lparts=[]
for name in ['acropolis','lower town']:
    lparts.append(part(name,'Period A, Phase II',assertion('The report calls Phase II the point when the town was “elaborately planned”; systematic planning is first discernible in this phase.',ll),lp,
       alternatives=[assertion('Phase I had a protective mud bund, but the excavator states that its street plan is not known.',loc('rao1979','p. 85'))],
       notes='The published start estimate is retained in the rejected/unclassified date evidence. It is not silently converted into a calibrated date.',
       no_candidate_reason='The inspected excavation estimate combines uncalibrated site radiocarbon with cross-dating. No calibrated phase-start synthesis or independent non-radiocarbon start was located.'))
town('lothal','Lothal',lparts,
     first=dict(year_bce=None,locators=[loc('rao1979','p. 44')],
                evidence='The first habitation predates the planned acropolis. The excavation estimates Phase I from an assumed village duration and its combined chronological argument.',
                reported_estimates=[dict(year_bce=2450,astronomical_year=-2449,scale='excavation estimate using an uncalibrated radiocarbon framework',locator=loc('rao1979','p. 44'))]),
     searched=['Rao excavation Volume I and chronology chapter; Tata laboratory lists I and III; calibrated chronology and Bayesian phase-start search; recent Lothal palaeoenvironmental dating study and supplement.'],
     notes=[assertion('The excavator estimates the start of Phase II at 2350 B.C. by combining Sargonid cross-dating, assumed building durations and central uncalibrated radiocarbon dates. It therefore needs reviewer classification under the fixed levels.',loc('rao1979','pp. 41-44'))],
     disagreements=[assertion('The second set of charcoal dates is rejected by the excavator as out of stratigraphic order. The laboratory itself warns that younger-carbon contamination is possible.',loc('rao1979','pp. 39-40'),loc('tata1965','p. 294'))])
for code,bp,err,context,pl,page in [
 ('TF-23',3705,105,'SRG54, locus XLIII-XLVIII/4, field 28; post-hole in mud wall built over flood deposit','Phase VA','p. 277'),
 ('TF-19',3650,135,'SRG11, locus 5B, field 6; debris sealing dock embankment wall','Phase VA','p. 277'),
 ('TF-29',3740,110,'SRG55, locus XII-XVIII/7, field 53; waterlogged cesspool','Phase IVA','p. 277'),
 ('TF-22',3845,110,'SRG2, E13/9, field 29; ash-rich flood debris sealing a wall','end of Phase IIIB','p. 277'),
 ('TF-27',3840,110,'SRG2, D13/7A, field 32A; flood debris','Phase IIIB','p. 277'),
 ('TF-26',3830,120,'SRG2, D13/7A, field 32; flood debris','Phase IIIB','p. 277')]:
    rc('lothal',code,bp,err,'charcoal',context,pl,'later comparison within Period A or B',loc('tata1963',page,code),
       reported_calendar=dict(scale='uncalibrated B.C.; 5568-year half-life'),notes='Later than the initial layout phase; retained because the excavator uses this series to anchor the early-phase estimate.')
for code,bp,err,context,pl in [
 ('TF-133',3740,110,'SRG2, AX33, layer 6, field 75; disturbed level','Period A, Phase II'),
 ('TF-135',3405,125,'SRG2, AX33, layer 9, field 77; waterlogged deposit','Period A, Phase II'),
 ('TF-136',3915,130,'SRG2, AX33, layer 10, field 78','Period A, Phase I')]:
    rc('lothal',code,bp,err,'charcoal mixed with soil',context,pl,
       'layout phase' if code!='TF-136' else 'predecessor to layout',loc('tata1965','p. 294',code),
       reported_calendar=dict(scale='uncalibrated B.C.; 5568-year half-life'),
       notes='Laboratory warns of possible younger-carbon contamination; excavator rejects the second series. Phase sublabels differ between the laboratory and excavation table.')

source('bisht2015','R. S. Bisht',2015,'Excavations at Dholavira (1989-90 to 2004-2005)',
       'Archaeological Survey of India, preliminary report, January 2015.',
       'https://archive.org/details/dholavirareportpreliminaryjan2015_860_K',download='dholavira2015.pdf',
       notes='Native-text preliminary report with printed pagination; culture sequence and chronology inspected directly.')
source('sengupta2020','Torsa Sengupta, Arati Deshpande Mukherjee, Ravi Bhushan, F. Ram, M. K. Bera, Harsh Raj, Ankur J. Dabhi, R. S. Bisht, Y. S. Rawat, S. K. Bhattacharya, Navin Juyal and Anindya Sarkar',2020,
       'Did the Harappan settlement of Dholavira (India) collapse during the onset of Meghalayan stage drought?',
       'Journal of Quaternary Science 35(3):382-395. First online 26 December 2019.',
       'https://doi.org/10.1002/jqs.3178',access_route='Publisher abstract and supporting-information listing; author-uploaded full article text on ResearchGate.',
       notes='The newer calendar ranges are shell/otolith age envelopes, not Bayesian start boundaries. Supporting Table S4 was identified but its file route returned HTTP 403.')
dp=[phase('Stage I','First enclosed settlement beneath the castle; massive enclosure forms the nucleus retained by later building.',loc('bisht2015','p. 95')),
    phase('Stage II','Added inner brick masonry to enclosure; residential occupation outside the enclosed nucleus.',loc('bisht2015','pp. 97-99')),
    phase('Stage IIIA','Antecedent enclosure converted into castle; bailey and the town later called middle town founded, with outer enclosure and reservoirs.',loc('bisht2015','p. 99')),
    phase('Stage IIIB','Repairs after a catastrophe; lower town added and outer wall extended.',loc('bisht2015','pp. 99-100')),
    phase('Stages IV and V','Classical layout maintained, then repairs and decline.',loc('bisht2015','pp. 100-103')),
    phase('Stages VI and VII','Reduced settlement with changed domestic plan, followed after desertion by circular houses.',loc('bisht2015','pp. 103-104'))]
db=loc('bisht2015','pp. 104-105, Chronology table and discussion')
dparts=[part('castle','Stage I (nucleus); Stage IIIA (castle conversion)',
             assertion('The first exposed enclosure is assigned to Stage I. The report says its planning formed the nucleus of later expansion; the named castle was created by enlargement in Stage III.',loc('bisht2015','pp. 95, 99')),dp,
             [candidate(3,3000,db,'Excavator’s stratigraphic and typological chronology; first stage begins at the stated archaeological start. TL results are discussed separately; no site radiocarbon supported this table.')],
             alternatives=[assertion('For the developed castle rather than its earliest enclosure, Stage IIIA is the appropriate construction label.',loc('bisht2015','p. 99'))]),
        part('bailey','Stage IIIA',assertion('The report says a separately walled bailey “was added” when the antecedent enclosure was converted to a castle.',loc('bisht2015','p. 99')),dp,
             [candidate(3,2800,db,'Excavator’s stratigraphic and typological calendar start for Stage III; the bailey belongs to its opening construction.')]),
        part('middle town','Stage IIIA',assertion('The extensive walled town was founded in Stage III; a deep trench places habitation at the early stage of Stage III.',loc('bisht2015','pp. 99, 129')),dp,
             [candidate(3,2800,db,'Excavator’s stratigraphic and typological start for Stage III, supported by the deep-trench assignment to its early part.')]),
        part('lower town','Stage IIIB',assertion('The lower town was added after catastrophe within Stage III, and the enclosure extended to include it.',loc('bisht2015','pp. 99-100')),dp,
             no_candidate_reason='A separate calendar start for Stage IIIB is not given in the inspected chronology. The start of undivided Stage III would predate the lower-town addition.',
             notes='Most exposed domestic remains belong to later maintained phases; the report distinguishes those exposures from the initial lower-town addition.',
             alternatives=[assertion('The published shallow exposures are predominantly Stages IV and V, while deep trenches reach the original occupation.',loc('bisht2015','pp. 131-132'))])]
town('dholavira','Dholavira',dparts,
     first=dict(year_bce=3551,astronomical_year=-3550,evidence='Approximate beginning of occupation stated as about 5500 calibrated years BP in the newer shell chronology. Conversion uses astronomical year = 1950 - cal BP; the rounded age is not a modelled start median.',
                locators=[loc('sengupta2020','p. 382, Abstract; Table 1')],
                reported_estimates=[dict(year_bce=3000,astronomical_year=-2999,scale='excavator typological chronology',locator=db)]),
     searched=['Bisht preliminary report culture sequence, chronology and town divisions; Sengupta et al. published shell chronology; Wiley supplement S4 and author-uploaded article; Bayesian phase-start search.'],
     notes=[assertion('The newer study provides calibrated sample envelopes for cultural stages. Stages III and V lack dated material and their values are inferred from neighbouring stages; these are not independent start-boundary estimates.',loc('sengupta2020','Table 1 and Fig. 5'))],
     disagreements=[assertion('The newer shell chronology places first occupation earlier than the excavation’s typological table. Stage III lacks direct dated material in that study, so the newer dates do not supply the required part-specific opening boundary.',db,loc('sengupta2020','Table 1; Results, chronology discussion'))])

source('lal1979','B. B. Lal',1979,'Kalibangan and the Indus Civilization',
       'In D. P. Agrawal and Dilip K. Chakrabarti (eds.), Essays in Indian Protohistory, pp. 65-97. Delhi: B. R. Publishing Corporation.',
       'https://ignca.gov.in/Asi_data/64222.pdf',download='kalibangan-chronology1971.pdf',
       notes='The transport filename predates title-page identification. This is the complete edited book, not a publication from the year in that filename. Printed p. 94 is PDF p. 113.')
for p in TOWNS['kalibangan']['parts']:
    p['candidates_by_level']['2'].append(candidate(2,2500,loc('lal1979','p. 94, chronology discussion and corrected-date table'),
       'Excavator explicitly states a calibrated commencement using MASCA and Clark corrections to site determinations.'))
    p['proposed_candidate']['notes']+=' The primary excavation synthesis independently states the same commencement; see Lal 1979, p. 94.'
TOWNS['kalibangan']['first_occupation']=dict(year_bce=2900,astronomical_year=-2899,
    evidence='Excavator states the corrected radiocarbon start of Period I after discussing anomalously young samples.',
    locators=[loc('lal1979','pp. 93-94, corrected-date table')],
    reported_estimates=[dict(year_bce=2450,astronomical_year=-2449,scale='older uncalibrated estimate',locator=loc('thapar1975','p. 23'))])
TOWNS['kalibangan']['notes'].append(assertion('The primary synthesis explicitly calls the corrected commencement circa 2500 B.C. This direct statement resolves the calibration-basis gap in the later comparative table.',loc('lal1979','p. 94')))

source('joshi1990','Jagat Pati Joshi',1990,'Excavation at Surkotada 1971-72 and Exploration in Kutch',
       'Memoirs of the Archaeological Survey of India 87. New Delhi: Archaeological Survey of India.',
       local_path='data/raw/2026-10-21-post-catalogue-finds/run1a/sources/surkotada-1990/MASI 87 Excavations at Surkotada and Kutch Jagat Pati Joshi.pdf',
       notes='Scanned ASI report; printed pages used. Typographical and half-life discrepancies in its chronology are retained for review.')
source('tata1973','D. P. Agrawal and Sheela Kusumgar',1973,'Tata Institute Radiocarbon Date List X',
       'Radiocarbon 15(3):574-585','https://doi.org/10.1017/S0033822200009024',download='tata1973.pdf')
source('prl1976','D. P. Agrawal, R. V. Krishnamurthy, Sheela Kusumgar and R. K. Pant',1976,
       'Physical Research Laboratory Radiocarbon Date List I','Radiocarbon 18(1):89-95',
       'https://doi.org/10.1017/S0033822200002381',download='prl1976.pdf')
sp=[phase('Period IA','First fortified citadel and separately enclosed residential annexe; rubble houses, bath and drain. Enclosures repaired during the phase.',loc('joshi1990','p. 21; pp. 41-46')),
    phase('Period IB','Same enclosed areas maintained; rampart and gateway alterations, followed by a widespread fire.',loc('joshi1990','pp. 25-26, 46-48')),
    phase('Period IC','Rebuilt citadel and annexe using rubble and dressed stone; elaborated gateways and intercommunicating passage, later repairs and blocking.',loc('joshi1990','p. 26; pp. 49-58'))]
surparts=[]
for name in ['citadel','residential annexe']:
    surparts.append(part(name,'Period IA',assertion('The earliest occupants built both enclosed units; the report says the same settlement pattern was maintained in the successive subperiods.',loc('joshi1990','pp. 17, 21')),sp,
        alternatives=[assertion('The extensive standing stone architecture and elaborated gateway belong largely to the rebuilding of Period IC, within the older enclosed plan.',loc('joshi1990','pp. 26, 49-58'))],
        no_candidate_reason='The excavation chronology combines relative comparisons with uncalibrated radiocarbon ages. No inspected source supplies a calibrated start of Period IA or an independent non-radiocarbon start.',
        notes='The whole-site calibrated sample span sometimes quoted for Surkotada is not adopted as a part-specific start.'))
town('surkotada','Surkotada',surparts,
     first=dict(year_bce=None,evidence='First occupation is Period IA. The excavation’s estimate uses an uncalibrated radiocarbon framework together with ceramic comparisons.',
                reported_estimates=[dict(year_bce=2300,astronomical_year=-2299,scale='mixed relative and uncalibrated radiocarbon estimate',locator=loc('joshi1990','pp. 59, 62-63, 66'))],
                locators=[loc('joshi1990','pp. 21, 62-63')]),
     searched=['Joshi full excavation report: first enclosures, successive reconstructions and chronology; Tata date list X; PRL date list I; later calibrated synthesis and Bayesian phase-start searches.'],
     disagreements=[assertion('The excavation assigns the combined sample to Period IA and rejects it as mixed, whereas some later compilations place it in IB. It also misprints the age of TF-1310 and gives an inconsistent age for TF-1295. The primary laboratory list supplies the conventional values used here.',loc('joshi1990','pp. 62, 64'),loc('tata1973','pp. 579-580')),
                    assertion('PRL-85 has a different age in the primary laboratory list from the age reproduced in the excavation. Both reports are identified; the primary conventional value is used in the determination register.',loc('prl1976','p. 94'),loc('joshi1990','p. 62'))])
for code,bp,error,pl,context,page in [
 ('TF-1305',3890,95,'Period IA','ZA1 Q2, layer 19, earliest level just above raised ground','p. 579'),
 ('TF-1310',3810,95,'Period IA','ZA1 Q2, layer 11, latest level','p. 579'),
 ('TF-1304 / TF-1309 (combined)',3645,90,'Period IA, attribution disputed','ZA1 Q2, layers 18A and 20, mixed charcoal sample; rejected by excavator','p. 579'),
 ('TF-1295',3780,95,'Period IB','G1 Q3, layer 8, early level of residential annexe','p. 579'),
 ('TF-1297',3635,95,'Period IC','C1 Q4, pit sealed by layer 3','p. 579'),
 ('TF-1311',3625,90,'Period IC','ZA1 Q2, layer 4','p. 580'),
 ('TF-1294',3620,95,'Period IC','XC1 Q3, layer 3','p. 579'),
 ('TF-1307',3510,105,'Period IC','XA4 Q1, layer 5 in laboratory list; report instead says XA1','p. 579')]:
    rc('surkotada',code,bp,error,'charcoal',context,pl,'layout phase' if pl.startswith('Period IA') else 'later comparison',loc('tata1973',page,code),
       reported_calendar=dict(scale='uncalibrated B.C.; 5568-year half-life in laboratory list; excavation also prints longer-half-life equivalents'),
       notes='Phase attribution: '+json.dumps(loc('joshi1990','pp. 62-66',code),ensure_ascii=False))
rc('surkotada','PRL-85',4140,130,'charcoal','ZF1 Q2, layers 13 and 14; field 21; middle occupation of citadel',
   'Period IA','layout phase',loc('prl1976','p. 94','PRL-85'),reported_calendar=dict(scale='uncalibrated BC; laboratory introduction states Libby half-life'),
   notes='Excavation p. 62 instead reports 4365 ± 135 BP; this is a conflicting report of the same code, not an extra determination.')

source('joshi1999inventory','Jagat Pati Joshi, Krishna Deva, R. C. Agrawal, P. K. Trivedi and P. K. Mishra',1999,
       'Inventory of Monuments and Sites of National Importance, Vol. 1, Part 2: Chandigarh Circle',
       'New Delhi: Archaeological Survey of India.','https://ignca.gov.in/Asi_data/84884.pdf',download='banawali-asi.pdf',
       notes='Title and copyright pages inspected: ASI copyright 1999. Banawali is entry 22, printed pp. 22-23; PDF pp. 41-42.')
bp=[phase('Period IA (pre-defence)','Open settlement with houses; no circumvallation.',loc('joshi1999inventory','p. 22, entry 22')),
    phase('Period IB (defence)','Enclosed antecedent settlement; defensive wall and houses repeatedly enlarged.',loc('joshi1999inventory','p. 22, entry 22')),
    phase('Period IC (transitional / proto-Harappan)','Settlement rebuilt with a citadel and lower town within a general fortification; the street system of the subsequent town established.',loc('joshi1999inventory','p. 22, entry 22'),loc('bisht2015','p. 20, section 1.1.8')),
    phase('Period II (Mature Harappan)','Bilocular plan maintained with additions and rebuilt houses.',loc('joshi1999inventory','p. 22, entry 22'),loc('bisht2015','p. 20')),
    phase('Period III (post-Harappan / Banawali-Bara)','New occupation following desertion; mud-wall houses outside the earlier ruins.',loc('joshi1999inventory','pp. 22-23, entry 22'),loc('bisht2015','p. 21'))]
bparts=[]
for name in ['citadel','lower town']:
    bparts.append(part(name,'Period IC',assertion('The ASI inventory says the settlement was constructed “de novo” and its dichotomous layout introduced in IC. The excavator’s later account confirms this sequence.',loc('joshi1999inventory','p. 22, entry 22'),loc('bisht2015','p. 20')),bp,
       alternatives=[assertion('Period II rebuilt domestic structures while adopting the existing overall plan, so a date for the Mature Harappan occupation would postdate the inception of this layout.',loc('bisht2015','p. 20'))],
       no_candidate_reason='No calendar start of transitional Period IC was established in the inspected sources. Published site determinations are attributed to Period II, after inception of the plan.'))
town('banawali','Banawali',bparts,first=dict(year_bce=None,evidence='Open Period IA is first. A supported calendar boundary for it was not located.',locators=[loc('joshi1999inventory','p. 22, entry 22')]),
     searched=['Bisht excavation and town-planning bibliographies; ASI inventory entry; Bisht later account in Dholavira report; radiocarbon synthesis and laboratory-list routes; IC calibrated start and Bayesian chronology searches.'],
     notes=[assertion('The later sequence assigns inception of the overall layout to IC. An undifferentiated Mature Harappan label would conceal this distinction.',loc('bisht2015','pp. 19-21'),loc('joshi1999inventory','p. 22'))])
for code,bpv,err in [('PRL-207',3100,100),('PRL-204',3260,120),('PRL-203',3800,150),('PRL-205',3810,180)]:
    rc('banawali',code,bpv,err,'charcoal (later compilation attribution)','Period II; detailed trench not established in this synthesis','Period II',
       'later than layout inception; included for comparison',loc('kenoyer1991','p. 337, Table III',code),
       reported_calendar=dict(scale='Calibrated CALIB intercepts and uncalibrated longer-half-life BC both printed'),
       notes='No determination for transitional IC or its predecessor was identified. The conventional ages are those printed in this synthesis; primary laboratory context remains a gap.')

source('nath2014','Amarendra Nath',2014,'Excavations at Rakhigarhi (1997-98 to 1999-2000)',
       'Archaeological Survey of India, report manuscript with prefatory letter dated 31 December 2014; often cited as 2015.',
       'https://www.rarebooksocietyofindia.org/book_archive/196174216674_10153813006761675.pdf',
       local_path='data/raw/2026-10-20-fresh-test-collection/rakhigarhi-nath.pdf',
       notes='The held report is a draft with inconsistent phase terminology and unfinished passages. Numeric tables are cited by printed page; this status matters for review.')
source('suryanarayan2019','Akshyeta Suryanarayan',2019,
       'What’s cooking in the Indus Civilisation? Investigating Indus food through ceramic lipid residue analysis',
       'PhD dissertation, University of Cambridge, August 2019.',
       'https://api.repository.cam.ac.uk/server/api/core/bitstreams/515b5736-fa26-4c70-9ffb-7d5e9292221b/content',download='rakhigarhi-chronology-review.pdf',
       notes='The transport filename reflects the targeted section. This is a dissertation containing a site chronology review; its Rakhigarhi discussion is printed pp. 118-119.')
rp=[phase('Period IA (pre-formative), phases (i), (ii), (iii)','At RGR-6, mud platform followed by circular and rectangular mud-brick structures, then rectangular houses.',loc('nath2014','p. 129')),
    phase('Period IB (formative Early Harappan)','Organized streets, houses and public drainage; earlier settlement under the mature occupation.',loc('nath2014','p. 129')),
    phase('Period I, structural phases I-III (alternative chapter terminology)','Early structures and streets, flood damage at end of phase III. This chapter does not map its structural labels unambiguously onto IA/IB.',loc('nath2014','pp. 98-99, 104-105')),
    phase('Period II, structural phases IV-VI','Mature Harappan public platforms, houses, streets and enclosure. Rebuilt occupation follows the earlier plan.',loc('nath2014','pp. 98-99, 104-107'))]
rparts=[]
for name,label,support,page in [
 ('citadel / acropolis','Period II (specific first enclosure subphase unresolved)','The report identifies the mature public platforms and enclosure but does not demonstrate a dated first construction boundary for the enclosed unit.','pp. 94-95, 104-107, 111'),
 ('middle town','not established','The report names a middle-town division without resolving the first construction phase of a separately planned unit.','p. 93'),
 ('lower town','Period II, inherited earlier plan possible','Mature urban houses and public amenities are described, but the report also says rebuilding followed the earlier plan.','pp. 103-105'),
 ('RGR-6 antecedent settlement','Period IB (organized settlement)','The report attributes an organized street and drainage plan to formative Period IB at the antecedent settlement.','pp. 95, 129')]:
    rparts.append(part(name,label,assertion(support,loc('nath2014',page)),rp,
        no_candidate_reason='The dates inspected are sample ages or broad occupation spans, without a demonstrated calendar opening boundary for this part and layout.',
        notes='Mound identifiers and urban divisions are not treated as interchangeable. The report’s inconsistent mappings require review.'))
town('rakhigarhi','Rakhigarhi',rparts,
     first=dict(year_bce=None,evidence='Pre-formative occupation is documented beneath the early organized settlement. A single accepted start is unresolved; the report publishes calibrated sample ages rather than a start-boundary model.',locators=[loc('nath2014','pp. 57, 129, 335, Table 1'),loc('suryanarayan2019','pp. 118-119')]),
     searched=['Nath full report: cultural sequence, construction chapters and repeated radiometric table; Dikshit later table; Cambridge dissertation chronology review; recent Rakhigarhi excavation and cemetery dating papers; Bayesian and layout-start searches.'],
     disagreements=[assertion('The report uses both IA/IB and an alternative numbered structural sequence. The later review states that new early dates lack the stratigraphic profiles and cultural-material publication needed to assess establishment and abandonment.',loc('nath2014','pp. 98-99, 129'),loc('suryanarayan2019','p. 119'))])
for code,bpv,err,context,pl,cal,calerr in [
 ('BS-3318 / S-4173',5640,110,'RGR-6, sample 58, depth 4.96 m','pre-formative',6420,110),
 ('BS-3341 / S-4187',5440,290,'RGR-6, sample 51, depth 4.23 m','pre-formative',6230,320),
 ('BS-3344 / S-4190',4570,100,'RGR-1, sample 46','Early Harappan',5230,60),
 ('BS-3324 / S-4180',5200,100,'RGR-2, sample 213, depth 8.45 m','Early Harappan',5910,130),
 ('BS-3368 / S-4215',4040,90,'RGR-2, sample 78, depth 6.40 m','Mature Harappan',4560,90),
 ('BS-3389 / S-4237',3900,110,'RGR-2, sample 187, depth 5.60-5.90 m','Mature Harappan',4320,90)]:
    rc('rakhigarhi',code,bpv,err,'not specified in report table',context,pl,
       'layout or predecessor occupation; precise structural subphase unreported',loc('nath2014','p. 57 and p. 335, Table 1',code),
       reported_calendar=dict(scale='published calibrated years BP',age_cal_bp=cal,error_cal_bp=calerr),half_life=None,
       notes='Calibrated uncertainty is transcribed as printed, without interpreting it as a founding-boundary error. The repeated table is counted once.')
