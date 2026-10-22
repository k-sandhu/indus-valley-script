"""Optional-site observations; executed only by the owned assembly script."""
source('pramanik2004','Shubhra Pramanik',2004,'Excavation at Juni Kuran: 2003-2004: A Preliminary Report',
       'Puratattva 34:45-67','https://ignca.gov.in/Asi_data/87942.pdf',download='puratattva34-full.pdf')
jloc=loc('pramanik2004','pp. 47, 52-55; Fig. 8')
jph=[phase('Period I: Mature Harappan, with sub-phases','Stone and mud-brick structures occur through the excavated sequence; citadel enclosure and gateways, residential remains and gathering spaces are exposed. The report gives a tentative layer attribution, with a shared layer at the transition.',jloc),
     phase('Period II: Late Harappan','Upper occupation; gateway architecture has successive rebuilding and closure, without a secure correlation of its construction phases to the index trench.',jloc)]
town('juni-kuran','Juni Kuran',[
    part('citadel','Period I; earliest enclosure subphase unresolved',assertion('The report identifies the fortified citadel and successive gateway construction, but does not synchronize the original enclosure with a named index-trench subphase.',jloc),jph,no_candidate_reason='No calendar start or radiocarbon determination for the enclosure phase was found in the preliminary report.'),
    part('residential / middle-town area','not established',assertion('A residential excavation and a middle town are mentioned, but their founding layout is not assigned to a dated construction phase.',jloc),jph,no_candidate_reason='Construction phase and its calendar start are unresolved.')],
    first=dict(year_bce=None,evidence='The basal occupation is assigned to Mature Harappan Period I, with no calendar founding date.',locators=[jloc]),
    searched=['Pramanik preliminary report, including index trench, enclosure and gateway descriptions; current radiocarbon and Bayesian chronology searches.'],
    notes=[assertion('The proposed correlation with Dholavira is typological. It does not supply a separately stated calendar start for a Juni Kuran construction phase.',loc('pramanik2004','pp. 53-54'))],required=False)

source('pokharia2017khirsara','Anil K. Pokharia, Rajesh Agnihotri, Shalini Sharma, Sunil Bajpai, Jitendra Nath, R. N. Kumaran and Bipin Chandra Negi',2017,
       'Altered cropping pattern and cultural continuation with declined prosperity following abrupt and extreme arid event at ~4,200 yrs BP: Evidence from an Indus archaeological site Khirsara, Gujarat, western India',
       'PLOS ONE 12(10):e0185684','https://doi.org/10.1371/journal.pone.0185684',download='khirsara2017.pdf')
kharch=loc('pokharia2017khirsara','pp. 4-5; Fig. 1')
khdate=loc('pokharia2017khirsara','pp. 6, 9; Tables 2-4')
khph=[phase('Phase IA / 1A','Earlier Mature Harappan occupation; the publication does not attribute the first walls of individual named town parts to this phase.',kharch,khdate),
      phase('Transitional Phase (TP)','Occupation distinguished by ceramics and subsistence changes; no new town plan is dated.',khdate),
      phase('Phase IB / 1B','Later Mature Harappan occupation; no separately dated layout boundary is supplied.',khdate)]
town('khirsara','Khirsara',[
    part(n,'Mature Harappan; construction subphase unresolved',assertion(a,kharch),khph,
         no_candidate_reason='The radiocarbon article dates occupation subphases but does not identify the first construction subphase of this part.')
    for n,a in [('citadel','The settlement description names a citadel among its architectural components.'),
                ('warehouse enclosure','The settlement description names a warehouse; its status as a separately planned unit requires excavation-report review.'),
                ('factory area','A factory area is identified, without a phase-specific founding plan in this article.'),
                ('habitational annexes','Habitational annexes are identified, without a phase-specific founding plan in this article.')]],
    first=dict(year_bce=2651,astronomical_year=-2650,evidence='The article states an earlier occupation start at approximately 4600 calendar years BP. Conversion uses the calendar-BP epoch, not the radiocarbon half-life.',reported_calendar_bp=4600,locators=[khdate]),
    searched=['Excavator-coauthored calibrated dating article and all its determination tables; Khirsara excavation architecture and phase searches.'],
    notes=[assertion('The stated occupation phases have calendar starts at approximately 4600, 4300 and 4100 BP. These are chronological observations, awaiting a construction-phase link for each part.',khdate),
           assertion('The tables include young charcoal and bulk-sediment determinations, and grain dates which differ from charcoal at the same reported depth. These are preserved separately.',khdate)],required=False)
khrows=[('BS-3362',3900,70,'wood charcoal','Z-38/1; depth 530-560 cm',2198,2505,2),
('BS-3358',3860,70,'wood charcoal','Z-38/1; depth 500-550 cm',2136,2492,2),
('BS-3310',3920,90,'wood charcoal','Z-38/1; depth 450-460 cm',2137,2666,2),
('BS-3471',3290,70,'wood charcoal','AE-35/4; depth 221-251 cm',1428,1700,2),
('BS-3469',3390,70,'wood charcoal','AE-35/4; depth 210-240 cm',1527,1882,2),
('BS-3354',3390,70,'wood charcoal','Z-37/2; depth 205-215 cm',1527,1882,2),
('BS-3468',3800,80,'wood charcoal','S-37/1; depth 200-210 cm',2026,2471,2),
('BS-3466',3230,70,'soil sediment organic matter','AF-35/1; depth 190 cm',1386,1685,3),
('GdA-2850',3810,25,'soil sediment organic matter','AF-35/1; depth 220 cm',2195,2340,3),
('GdA-2849',3805,25,'soil sediment organic matter','AF-35/1; depth 275 cm',2143,2309,3),
('GdA-2847',4155,25,'soil sediment organic matter','AF-35/1; depth 400 cm',2659,2876,3),
('Beta-427231',3750,30,'barley grain','Z-38/1; depth 530-560 cm',2038,2231,4),
('Beta-422014',3760,30,'wheat grain','Z-38/1; depth 530-560 cm',2091,2287,4)]
for code,bp,err,mat,ctx,young,old,tab in khrows:
    rc('khirsara',code,bp,err,mat,ctx,'Mature Harappan; individual sample-to-subphase join not tabulated',
       'occupation sequence; relation to first construction unresolved',loc('pokharia2017khirsara',f'p. {10 if tab==4 else 9}, Table {tab}',code),
       reported_calendar=dict(scale='calibrated BC, OxCal/IntCal13',range_2sigma_bce=[old,young]),
       half_life=None,notes='Tables report calibrated results, not a Bayesian phase-boundary model. The article does not state the conventional-age half-life. Reported calendar endpoints are retained even where another printed column is inconsistent.')

# The same dated comparative source covers the occupation before Bagasra's enclosure.
bagloc=loc('chase2014','pp. 3-7')
bagdate=loc('chase2020','pp. 6-7; Table 1')
bagph=[phase('Phase 1','Unwalled settlement; precedes the enclosure.',bagloc),
       phase('Phase 2','Construction and use of the enclosure.',bagloc),
       phase('Phase 3','Continued occupation, with changed material culture and declining enclosure maintenance.',bagloc),
       phase('Phase 4','Occupation over the disused enclosure.',bagloc)]
town('gola-dhoro','Gola Dhoro (Bagasra)',[
    part('walled enclosure','Phase 2',assertion('The enclosure was constructed after the unwalled initial settlement.',bagloc),bagph,
         no_candidate_reason='The calibrated establishment date refers to the first settlement. No stated calendar start of Phase 2 was recovered.'),
    part('extramural settlement','not established as separately planned',assertion('Occupation outside the enclosure is reported, but a separate founding plan is not dated.',bagloc),bagph,
         no_candidate_reason='A construction phase and its calendar start were not established.')],
    first=dict(year_bce=2500,astronomical_year=-2499,evidence='The comparative radiocarbon study places establishment as early as this calendar date.',locators=[bagdate]),
    searched=['Chase excavation and dated comparative studies; Sonawane excavation-report references; calibrated enclosure phase and Bayesian chronology searches.'],
    notes=[assertion('The earliest settlement date is retained as first occupation, independently of enclosure construction.',bagdate,bagloc)],required=False)
for code,bp,err,ph,old,young in [('Beta-217982',3930,40,'1',2570,2290),('Beta-217983',3900,40,'2',2490,2210),
 ('Beta-217984',3920,40,'3',2570,2290),('Beta-244091',3880,40,'3',2470,2200),('Beta-217985',3820,40,'3',2460,2140),('Beta-244090',3610,40,'4',2140,1880)]:
    rc('gola-dhoro',code,bp,err,'not specified in comparative table','Bagasra; detailed sample context not supplied',f'Phase {ph}',
       'layout phase' if ph=='2' else 'predecessor to layout' if ph=='1' else 'later occupation comparison',bagdate,
       reported_calendar=dict(scale='calibrated BC',range_2sigma_bce=[old,young]),half_life=None)

source('kanungo2025','Alok Kumar Kanungo, Rahul Kumar Kaushal, Ravi Bhushan, Naveen Chauhan, Jeewan Singh Kharakwal and Shahida Ansari',2025,
       'Luminescence and radiocarbon chronology of Bhagatrav: A Sorath Harappan camp site in South Gujarat',
       'Radiocarbon 67:53-73; first published online December 2024','https://doi.org/10.1017/RDC.2024.119',download='bhagatrav2025.pdf')
kunt=loc('kanungo2025','pp. 59-61; Table 1; citing Dhavalikar, Raval and Chitalwala 1996, pp. 27, 32, 41')
town('kuntasi','Kuntasi',[part('fortified settlement','Period I; first enclosure structural phase unresolved',
     assertion('The synthesis identifies the fortified settlement, and distinguishes a structural phase within Period I, but does not locate the first enclosure construction within that sequence.',kunt),
     [phase('Period I','Occupation includes successive structural phases; the published calendar span begins at 2400 BCE.',kunt),
      phase('Period II','Later occupation, dated to start at 1900 BCE in the cited excavation chronology.',kunt)],
     no_candidate_reason='The calibrated Period I start is a possible chronological anchor, but the first enclosure phase was not recovered from the excavation report.')],
     first=dict(year_bce=2400,astronomical_year=-2399,evidence='Published synthesis gives the start of Period I from the excavation chronology and discusses site radiocarbon determinations.',locators=[kunt]),
     searched=['Recent regional calibrated-date synthesis; Kuntasi excavation report and first-enclosure phase searches; Kenoyer selected-date compilation.'],required=False)
rc('kuntasi','BS-567',3870,90,'not specified in selected-date table','Kuntasi Period I; detailed context not supplied','Period I',
   'possible layout occupation; construction join unresolved',loc('kenoyer1991','p. 338, Table III','BS-567'),notes='Conventional Libby age from the earlier synthesis; the recent table omits its BP value.')
for code,bp,err,ph,cal in [('PRL-1370',3820,170,'I',2291),('PRL-1371',3750,140,'II',2145)]:
    rc('kuntasi',code,bp,err,'charcoal','Layer 12, structural phase B' if ph=='I' else 'Layer 5',f'Period {ph}',
       'possible layout occupation; construction join unresolved' if ph=='I' else 'later occupation comparison',kunt,
       reported_calendar=dict(scale='calibrated BCE',reported_intercept_bce=cal),half_life=None,
       notes='Table 1 labels the radiocarbon-age column yr BP but these individual cells print BC; preserved as a column/cell unit disagreement. Conventional-age interpretation requires checking the original report.')
rjloc=loc('kanungo2025','pp. 59-61; Table 1, citing Possehl and Raval 1989, pp. 12-13')
town('rojdi','Rojdi',[part('main settlement and enclosure','construction phase unresolved',
     assertion('The synthesis identifies an enclosure and occupation phases but does not date the first enclosure construction.',rjloc),
     [phase('Rojdi A','Earlier occupation sampled in lower main-mound levels; architectural founding sequence not recovered.',rjloc),
      phase('Rojdi B','Middle-level occupation.',rjloc),phase('Rojdi C','Later occupation, after the main urban interval.',rjloc)],
     no_candidate_reason='The excavation architecture must be joined to the dated occupation sequence before a layout start can be selected.')],
     first=dict(year_bce=None,evidence='Lower-level dates exist, but the inspected synthesis does not state a founding boundary for Rojdi A.',locators=[rjloc]),
     searched=['Recent regional calibrated-date synthesis; Possehl and Raval excavation-report references; Rojdi enclosure founding phase and radiocarbon searches.'],required=False)
for code,bp,err,ph,ctx,old,young in [('PRL-1088',3770,125,'B?','Main mound, 45K, middle',2420,1980),
('PRL-1089',3865,115,'A','Main mound, 45K, lower',2640,2150),('PRL-1093',3920,105,'A','Main mound, 45K, lower',2645,2310),
('PRL-1087',4010,105,'A','Main mound, 45K, lower',2680,2515),('PRL-1085',4020,105,'A','Main mound, 45K, lower',2680,2515),
('PRL-1282',3470,140,'B','Main mound, 46L, middle',2000,1665),('PRL-1281',3520,110,'B','Main mound, 46L, middle',2015,1710),
('PRL-1285',3740,140,'A','Main mound, 46L, lower',2410,1945),('PRL-1284',3810,100,'A','Main mound, 46L, lower',2415,2135),
('PRL-1283',3980,100,'A','Main mound, 46L, lower',2660,2385),('PRL-1084',3700,145,'A','Main mound, 46L, lower',2350,1890),
('PRL-1083',3875,125,'A','Main mound, 46L, lower',2640,2160),('TF-200',3810,110,'B','Trench B, Period I, 1962/63 season',2415,2135),
('TF-199',3590,110,'B','Trench C, Period I, 1962/63 season',2160,1850)]:
    rc('rojdi',code,bp,err,'not specified in comparative table',ctx,'Rojdi '+ph,'construction-phase relationship unresolved',rjloc,
       reported_calendar=dict(scale='calibrated BC as original references; not recalculated by synthesis',range_bce=[old,young]),half_life=None,
       notes='The more recent synthesis differs from Kenoyer’s selected table in some BP rounding and errors. These are one determination per laboratory code, not additional samples.')

source('biagividale2022','Paolo Biagi and Massimo Vidale',2022,
       'Lakheen-Jo-Daro, an Indus Civilization Settlement at Sukkur in Upper Sindh (Pakistan): A Scrap Copper Hoard and Human Figurine from a Dated Context',
       'Asian Perspectives 61(1):2-27','https://iris.unive.it/retrieve/9c27148d-aea7-42a6-b806-9e32280a4baa/Lak%20jo%20daro%202022.pdf',download='lakhanjo2022.pdf')
lak=loc('biagividale2022','pp. 5-8; Figs. 3-5')
town('lakhanjo-daro','Lakhanjo-daro',[part('excavated settlement areas','Mature Indus; first planned phase unresolved',
     assertion('The source describes residential structures and streets, but its dated workshop context is not a founding wall or layout boundary. Surviving mound names are not demonstrated to be separately planned ancient units.',lak),
     [phase('Mature Indus','Residential and craft areas, with repeated structures; earliest common town plan not established.',lak)],
     no_candidate_reason='The dated charcoal lens establishes occupation in an excavated area, without a published calendar start of a layout phase.')],
     first=dict(year_bce=None,evidence='First occupation remains undated in the inspected dated-context study.',locators=[lak]),
     searched=['Recent primary dated-context article; Sindh Antiquities excavation overview; first occupation and construction chronology searches.'],required=False)
rc('lakhanjo-daro','GrN-23123',3960,140,'Acacia sp. charcoal','Mound D, Trench C; charcoal lens at depth 30 cm; associated craft floor',
   'Mature Indus','dated occupation, construction-phase link unresolved',loc('biagividale2022','p. 7; Figs. 4-5','GrN-23123'),
   reported_calendar=dict(scale='cal BC',range_bce=[2881,2133],reported_probability_percent=94.2,source_label='2 sigma'),half_life=None)

source('shinde2008farmana','Vasant Shinde, Toshiki Osada, Akinori Uesugi and Manmohan Kumar',2008,
       'A Report on Excavations at Farmana 2007-08','Occasional Paper 6, Linguistics, Archaeology and the Human Past. Kyoto: Research Institute for Humanity and Nature.',
       local_path='data/raw/2026-10-21-post-catalogue-finds/run1a/sources/farmana-2007-08-report/Farmana Excavation Report 2007-08 - Vasant Shinde et al.pdf')
source('shinde2011farmana','Vasant Shinde',2011,'Stratigraphy and cultural sequence',
       'In Vasant Shinde, Toshiki Osada and Manmohan Kumar (eds.), Excavations at Farmana, District Rohtak, Haryana, India 2006-2008, pp. 25-40. Kyoto: Research Institute for Humanity and Nature.',
       local_path='data/raw/2026-10-21-post-catalogue-finds/run1a/sources/farmana-2006-08/Excavations at Farmana, 2006-08 - V Shinde et al.pdf')
source('paleolabo2011farmana','Paleo-Labo AMS dating group',2011,'AMS radiocarbon dating',
       'In Vasant Shinde, Toshiki Osada and Manmohan Kumar (eds.), Excavations at Farmana, District Rohtak, Haryana, India 2006-2008, pp. 831-838. Kyoto: Research Institute for Humanity and Nature.',
       local_path=SOURCES['shinde2011farmana']['local_path'])
source('osada2011farmana','Toshiki Osada',2011,'Summary',
       'In Vasant Shinde, Toshiki Osada and Manmohan Kumar (eds.), Excavations at Farmana, District Rohtak, Haryana, India 2006-2008, pp. 839-840. Kyoto: Research Institute for Humanity and Nature.',
       local_path=SOURCES['shinde2011farmana']['local_path'])
flay=loc('shinde2011farmana','pp. 38-40')
town('farmana','Farmana',[part('planned settlement','Period IIA',
     assertion('The excavator places well-planned structural complexes and streets at the beginning of Period IIA.',loc('shinde2011farmana','p. 40')),
     [phase('Period I: Early Harappan (Regional Hakra Culture Tradition)','Pit dwellings, followed by floor levels and rectangular structures; attribution of the earliest excavated material is disputed within the report.',flay),
      phase('Transition Period','Small rectangular structures and hearths precede the mature plan.',flay),
      phase('Period IIA','Planned brick structural complexes, streets and storage areas.',flay),
      phase('Period IIB','Continued settlement with changed material and burial evidence.',flay),
      phase('Period IIC','Hypothesized final phase; its deposits are described as removed.',flay)],
     [candidate(3,2600,loc('shinde2011farmana','pp. 39-40'),'Excavator explicitly bases the phase division on cultural comparison and says phase dates lack radiocarbon support.'),
      candidate(3,2500,loc('shinde2008farmana','p. 15'),'Earlier tentative start based explicitly on seals, sealings and ceramic assemblages.')],
     notes='The later book also publishes calibrated determinations, but the cross-dated construction estimate is not presented as a radiocarbon-based start. Structural Phase numbers in the dating table have not been equated to cultural subperiod labels.')],
     first=dict(year_bce=None,evidence='The cultural-sequence chapter proposes an early founding estimate from regional comparison; the final synthesis questions the early attribution of the excavated basal levels. Neither supplies an agreed site-specific calibrated founding boundary.',
                reported_estimates=[dict(year_bce=3500,astronomical_year=-3499,scale='excavator comparative estimate',locator=loc('shinde2011farmana','p. 38'))],
                locators=[flay,loc('osada2011farmana','p. 839')]),
     searched=['Existing preliminary and final excavation reports, chronology chapter and AMS appendix; Bayesian boundary and newer dating searches.'],
     disagreements=[assertion('The preliminary and final excavation chronologies differ in the start of the planned town. The final summary also questions the basal Early Harappan attribution.',loc('shinde2008farmana','p. 15'),flay,loc('osada2011farmana','p. 839'))],required=False)
for code,bp,err,ph,tr,old,young in [('PLD-15051',3925,25,2,'1D5',2476,2309),('PLD-15052',3975,25,2,'1D5',2571,2462),
('PLD-15054',3905,25,2,'1D5',2469,2301),('PLD-15048',3900,25,3,'1D5',2469,2301),('PLD-15049',3905,25,3,'1D5',2470,2299),
('PLD-15050',3905,25,3,'1D5',2469,2301),('PLD-16340',3850,20,1,'1C11',2459,2207),('PLD-16341',3880,20,1,'1C11',2461,2296),
('PLD-16342',3885,20,1,'1C11',2462,2299),('PLD-16343',3940,20,1,'1C11',2560,2344),('PLD-16344',3895,20,1,'1C11',2466,2299),
('PLD-16349',3905,20,1,'1C11',2470,2307),('PLD-16348',3925,20,2,'1C11',2477,2342),('PLD-12424',3860,25,5,'1A3, Pit 1',2461,2211),
('PLD-12425',3845,20,5,'1C1-1C2',2458,2205)]:
    rc('farmana',code,bp,err,'carbonized wood','Central Area; trench '+tr,'Harappan structural Phase '+str(ph),
       'within planned-settlement sequence; cultural IIA join unresolved',loc('paleolabo2011farmana','pp. 831-833, Tables 13.1-13.2',code),
       reported_calendar=dict(scale='calibrated BC, IntCal09/OxCal',outer_envelope_2sigma_bce=[old,young],note='Disjoint intervals and probabilities are printed in the source; envelope here does not fill the gaps.'),
       notes='Rounded conventional column transcribed. Historical intrusive determinations are excluded. Some further Harappan rows lost their laboratory-code cells in text extraction and remain pending page-image verification.')
