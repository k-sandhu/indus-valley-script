"""Further curated observations, read by assemble.py."""
source('mackay1943','Ernest J. H. Mackay',1943,'Chanhu-daro Excavations 1935-36',
       'American Oriental Series 20. New Haven: American Oriental Society, for the American School of Indic and Iranian Studies and Museum of Fine Arts, Boston.',
       local_path='research/literature/sources/mackay_1943_chandaro.pdf',
       notes='Scanned original, title and copyright pages inspected. Old Harappa occupation labels run from upper to lower deposits, and must not be equated numerically to the modern Indus periods.')
source('didier2017','Aurore Didier',2017,
       'Mission Archéologique Française du Bassin de l’Indus: Dossier de candidature au Prix Clio 2017',
       'MAFBI / CNRS ArScAn UMR7041 research dossier, 12 pp.',
       'https://www.clio.fr/securefilesystem/MAFBI_Dossier_Clio%20Copy.pdf',download='chanhu-clio.pdf')
cp=[phase('Harappa III and deeper occupations (Mackay nomenclature)','Deep cutting revealed architecture below the extensively exposed occupations; full correlation with the larger exposed plans remained unresolved.',loc('mackay1943','pp. 9, 12-13')),
    phase('Harappa II, then Harappa I (Mackay nomenclature)','Extensive brick houses and drainage, separated by destruction and rebuilding. Later Jhukar reused earlier masonry.',loc('mackay1943','pp. 12-13, 34')),
    phase('1ère période Indus (modern sequence)','New excavation revealed planned mud-brick residential and workshop quarters beneath the later occupations.',loc('didier2017','pp. 4-7, Figs. 3-5')),
    phase('2ème et 3ème périodes Indus (modern sequence)','Comparative ceramic reassessment assigns the major old excavation levels to these later Indus periods.',loc('didier2017','p. 4')),
    phase('Jhukar, then Jhangar','Later occupations at the site, with disturbed and reused earlier building materials.',loc('mackay1943','pp. viii-ix, 34'))]
town('chanhu-daro','Chanhu-daro',[
    part('planned settlement','1ère période Indus (modern sequence)',
         assertion('The new excavation exposed planned residential and workshop quarters in the first Indus period. The former mounds are not demonstrated to be separately planned town units.',loc('didier2017','pp. 4-7, Fig. 3'),loc('mackay1943','p. v')),cp,
         [candidate(3,2500,loc('didier2017','p. 2; pp. 5-7, Figs. 3-5'),
             'Excavator’s comparative ceramic assignment of the earliest planned architecture to the stated first Indus period; no radiocarbon determination is reported in this dossier.',
             notes='The dossier also uses a slash-form alternative opening in a later heading. This is not treated as a statistical uncertainty range.')],
         alternatives=[assertion('The main old exposed brick levels have been reassigned to later Indus periods. Their date cannot be transferred to the newly excavated earlier quarters.',loc('didier2017','p. 4'))],
         notes='A later radiocarbon-supported revision may supersede this candidate. Public metadata for recent field reports was found, but their full files and sample tables were unavailable.')],
    first=dict(year_bce=None,evidence='The first Indus period is the earliest planned architecture documented here. Water prevented the old excavation from reaching the bottom of occupation, so this is not proof of the first settlement date.',locators=[loc('mackay1943','pp. 9, 12'),loc('didier2017','pp. 4-5')]),
    searched=['Mackay original report, deep cutting and extensive plans; Didier field dossier; HAL metadata for recent field reports and chronological revision; recent AMS and Bayesian dating searches.'],
    disagreements=[assertion('The major old occupation labels and modern Indus-period labels are different sequences. The recent reassessment moves most extensively exposed old architecture to later periods.',loc('mackay1943','pp. 12-13'),loc('didier2017','p. 4'))])

source('kharakwal2011','J. S. Kharakwal, Y. S. Rawat, T. Osada, L. C. Patel, Hansmukh Seth, Rajesh Meena, S. Meena, K. P. Singh and A. Hussain',2011,
       'Kanmer: A Multicultural Site in Kachchh, Gujarat, India',
       'In T. Uno (ed.), Changing Perceptions of Japan in South Asia in the New Asian Era: The State of Japanese Studies in India and Other SAARC Countries, pp. 355-376. Kyoto: International Research Center for Japanese Studies.',
       'https://doi.org/10.15055/00001253',download='kanmer2011.pdf')
source('pokharia2011','Anil K. Pokharia, Jeewan Singh Kharakwal, R. S. Rawat, Toshiki Osada, C. M. Nautiyal and Alka Srivastava',2011,
       'Archaeobotany and archaeology at Kanmer, a Harappan site in Kachchh, Gujarat: evidence for adaptation in response to climatic variability',
       'Current Science 100(12):1833-1846, 25 June 2011.',
       'https://www.currentscience.ac.in/Volumes/100/12/1833.pdf',download='kanmer-botany2011.pdf')
source('goyal2013','Pankaj Goyal, Anil K. Pokharia, Jeewan Singh Kharakwal, Pramod Joglekar, Y. S. Rawat and Toshiki Osada',2013,
       'Subsistence System, Paleoecology, and 14C Chronology at Kanmer, a Harappan Site in Gujarat, India',
       'Radiocarbon 55(1):141-150.','https://doi.org/10.1017/S003382220004786X',
       access_route='Author-uploaded full article text on ResearchGate; publisher PDF route returned an abstract page.',
       notes='Article tables add a grain date and reproduce the earlier suite. OxCal is used for calibration; no modelled phase-start median is reported.')
source('pokharia2013review','Anil K. Pokharia and Chanchala Srivastava',2013,
       'Current Status of Archaeobotanical Studies in Harappan Civilization: An Archaeological Perspective',
       'Heritage: Journal of Multidisciplinary Studies in Archaeology 1:118-137.',
       'https://www.heritageuniversityofkerala.com/JournalPDF/Volume1/118-137.pdf',download='pokharia2013review.pdf')
kmph=[phase('KMR I','Antecedent settlement on bedrock or natural soil, described as pre-fortification deposits.',loc('kharakwal2011','p. 356; p. 373')),
      phase('KMR IIa','Planned settlement enclosed by a massive fortification.',loc('kharakwal2011','pp. 358, 373'),loc('pokharia2011','p. 1834')),
      phase('KMR IIb','Changed domestic planning and ashy deposits; enclosure raised and narrowed towards end of urban phase.',loc('kharakwal2011','pp. 358, 373-374')),
      phase('KMR III','Later occupation initially uses enclosure, then builds houses over it.',loc('kharakwal2011','pp. 373-374')),
      phase('KMR IV and KMR V','Historic and medieval occupations after desertions, with pits disturbing earlier strata.',loc('kharakwal2011','p. 358'))]
kmc1=candidate(2,2500,loc('pokharia2011','p. 1835, paragraph immediately before Radiocarbon dating; Tables 1-2 on pp. 1836-1837'),
    'Site study assigns the Mature phase its calendar opening, supported by its calibrated site radiocarbon suite.')
kmc2=candidate(2,2600,loc('pokharia2013review','p. 130, Kanmer paragraph'),
    'Later synthesis of the same site study gives the opening of the winter/summer crop phase identified with the Mature occupation.',
    notes='Eligibility requires the phase correlation supplied by the excavation and dating articles. The review does not repeat calibration methods, but cites the site study. Reviewer should examine the revised opening.')
town('kanmer','Kanmer',[
    part('fortified settlement','KMR IIa',assertion('The excavators identify KMR I as pre-fortification and say the planned fortified settlement was built during KMR II.',loc('kharakwal2011','pp. 356, 373')),kmph,[kmc1,kmc2],
         notes='The newer synthesis is proposed under the same-level recency rule. Its change from the earlier site article is explicit in the disagreement record.')],
    first=dict(year_bce=2800,astronomical_year=-2799,evidence='Opening of the earliest site phase in the later synthesis; the original dating article gives a slightly earlier opening.',
               locators=[loc('pokharia2013review','p. 130')],reported_estimates=[dict(year_bce=2850,astronomical_year=-2849,scale='calibrated phase chronology in site article',locator=loc('pokharia2011','p. 1835'))]),
    searched=['Excavators’ institutional report, pottery chapter and culture sequence; Current Science original site dating article; Radiocarbon follow-up tables; later archaeobotanical synthesis; Bayesian chronology search.'],
    notes=[assertion('No separate lower town was located in the excavation reported here.',loc('kharakwal2011','p. 374'))],
    disagreements=[assertion('The original site article and later synthesis assign different openings to both Early and Mature occupations. The radiocarbon tables also contain old charcoal results alongside younger AMS determinations from related levels. None is replaced by an analyst-selected oldest endpoint.',loc('pokharia2011','pp. 1835-1837'),loc('pokharia2013review','p. 130'))])
for code,bpv,err,context,cal in [
 ('BS-2619',4190,80,'Y-30 / layer 20 / depth 930 cm',[2850,2623]),
 ('BS-3028',4630,90,'Z-30 / layer 12 / depth 942-967 cm',[3099,3600]),
 ('BS-3042',4750,100,'Z-30 / layer 11 / depth 900-923 cm',[3100,3600]),
 ('BS-2685',4200,120,'Y-30 / layer 8 / depth 307 cm',[2875,2581]),
 ('BS-2627',3870,100,'R-21 / layer 7 / depth 466 cm',[2470,2149]),
 ('BS-2699',4720,180,'HH-20 / layer 4 / depth 529 cm',[3660,3345]),
 ('BS-3027',4660,110,'Z-18 / layer 4 / depth 395 cm',[3037,3600]),
 ('BS-2628',3610,90,'HH-30 / layer 3 / depth 280 cm',[2130,1785]),
 ('BS-2698',4290,80,'R-20 / layer 2 / depth 320 cm',[3006,2877])]:
    rc('kanmer',code,bpv,err,'wood charcoal',context,'Harappan sequence; individual period not assigned in date table',
       'layout or predecessor sequence, sample-to-phase join unresolved',loc('pokharia2011','p. 1836, Table 1',code),
       reported_calendar=dict(scale='published calibrated BC',range_as_printed_bce=cal),half_life=None,
       notes='Endpoint order and apparent inconsistencies in the printed calendar table are preserved. This result is not a phase start.')
for code,bpv,err,unrounded,unerr,context,cal in [
 ('14748',3780,25,3782,26,'AA-17 / layer 6 / depth 3.63 m',[[2292,2137]]),
 ('14749',3750,25,3751,27,'FF-29 / layer 3 / depth 3.85 m',[[2279,2250],[2230,2220],[2211,2121],[2095,2041]]),
 ('14750',3770,25,3769,24,'FF-29 / layer 3 / depth 3.85 m',[[2287,2133],[2079,2061]]),
 ('14751',3985,25,3984,24,'Z-30 / layer 12 / depth 9.72 m',[[2571,2513],[2504,2466]]),
 ('14752',3935,25,3935,24,'Z-30 / layer 10 / depth 9.04 m',[[2560,2536],[2491,2341]]),
 ('14753',3680,25,3682,24,'EE-30 / layer 4 / depth 4.58 m',[[2141,2011],[2001,1977]]),
 ('14754',3895,25,3896,25,'Q-28 / layer 11 / depth 8.00 m',[[2467,2299]]),
 ('14755',3865,25,3866,25,'Q-28 / layer 12 / depth 8.20 m',[[2464,2281],[2250,2231],[2219,2212]]),
 ('14756',3875,25,3873,24,'Z-28 / layer 12 / depth 8.91 m',[[2465,2286],[2247,2243]]),
 ('14757',3810,25,3809,23,'AA-28 / layer 9 / depth printed 788',[[2337,2323],[2308,2196],[2172,2146]]),
 ('14758',3890,25,3892,24,'Q-28 / layer 13 / depth 8.45 m',[[2466,2298]]),
 ('14759',3900,20,3898,22,'Q-28 / layer 11 / depth 8.09 m',[[2468,2335],[2324,2301]]),
 ('14760',3875,25,3875,23,'AA-28 / layer 8 / depth 7.11 m',[[2464,2288]]),
 ('14761',3885,25,3886,27,'Q-28 / layer 10 / depth 8.03 m',[[2466,2292]]),
 ('14762',3815,25,3814,24,'A-28 / layer 12 / depth 9.24 m',[[2344,2196],[2172,2146]]),
 ('16352',3880,20,3882,20,'Y-30 / layer 20 / depth 9.30 m',[[2461,2298]])]:
    rc('kanmer','PLD-'+code,bpv,err,'carbonized grain' if code=='16352' else 'charcoal',context,
       'Harappan sequence; individual period not assigned in date table','layout or predecessor sequence, sample-to-phase join unresolved',
       loc('pokharia2011','p. 1837, Table 2','PLD-'+code),reported_calendar=dict(scale='calibrated BC',range_2sigma_segments_bce=cal),
       notes=f'Rounded published result used; unrounded result also printed as {unrounded} ± {unerr} BP in the same table. Calibration details in Goyal et al. 2013, p. 143; no Bayesian start model reported.')
rc('kanmer','PLD-17147',3835,20,'carbonized grain','Z-30 / layer 10 / depth 10.30 m',
   'Harappan sequence, phase join unresolved','layout or predecessor sequence, phase join unresolved',loc('goyal2013','p. 144, Table 2','PLD-17147'),
   reported_calendar=dict(scale='calibrated BC',range_2sigma_segments_bce=[[2435,2420],[2405,2378],[2350,2201]]),
   notes='Additional determination in the later article; source labels it a rounded conventional age.')

source('bhanajith2009','Department of Archaeology and Ancient History, Maharaja Sayajirao University of Baroda',2009,
       'Excavations at Shikarpur, Gujarat 2008 - 2009','Excavation-season report, 9 pp.',
       'https://www.harappa.com/content/excavations-shikarpur-gujarat-2008-2009',
       local_path='data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/SHIKARPUR2009.pdf')
source('chase2014','Brad Chase',2014,'On the Pastoral Economies of Harappan Gujarat: Faunal Analyses at Shikarpur in Context',
       'Heritage: Journal of Multidisciplinary Studies in Archaeology 2:1-22.',
       'https://www.heritageuniversityofkerala.com/JournalPDF/Volume2/1-22.pdf',download='chase2014shikarpur.pdf')
source('chase2020','Brad Chase, David Meiggs and P. Ajithprasad',2020,
       'Pastoralism, climate change, and the transformation of the Indus Civilization in Gujarat: Faunal analyses and biogenic isotopes',
       'Journal of Anthropological Archaeology 59:101173, pp. 1-21.',
       'https://doi.org/10.1016/j.jaa.2020.101173',access_route='Full author-uploaded article text displayed by web retrieval from Academia, linked from Harappa.com.',
       notes='Direct download route returned HTTP 403. The full article table and site/sequence discussion were inspected through web retrieval, not downloaded to disk.')
shph=[phase('Phase I / Phase 1','Enclosure built from the first occupation, mud-brick houses and streets; stone structures appear near the terminal portion.',loc('bhanajith2009','pp. 1-3'),loc('chase2014','p. 6')),
      phase('Phase II / Phase 2','Same enclosure and some houses remain in use with reduced upkeep and increasing Sorath pottery.',loc('bhanajith2009','pp. 3-4'),loc('chase2020','pp. 6-7')),
      phase('Phase III / Phase 3','Ephemeral settlement over defunct enclosure walls, rough stone foundations and pits.',loc('chase2014','p. 6'),loc('chase2020','p. 7'))]
shdate=loc('chase2020','p. 7, Shikarpur site discussion; p. 6, Table 1 and Fig. 2')
town('shikarpur','Shikarpur (Kachchh)',[
    part('walled enclosure','Phase I',assertion('The excavators traced the basal enclosure to natural sediment and state construction began with Harappan occupation. The later synthesis explicitly assigns that construction to Phase I.',loc('bhanajith2009','p. 1'),loc('chase2020','p. 6')),shph,
         [candidate(2,2500,shdate,'Published synthesis states that site radiocarbon dates suggest establishment as early as this calendar date; the opening occupation includes enclosure construction.')]),
    part('extramural residential area (planning status unresolved)','not established',assertion('Residential areas occur both inside and outside the enclosure. The first construction phase of a separately planned extramural unit is not demonstrated.',loc('chase2014','pp. 5-6')),shph,
         no_candidate_reason='No independently phased beginning of the extramural residential layout was established.')],
    first=dict(year_bce=2500,astronomical_year=-2499,evidence='Published radiocarbon-supported establishment estimate; the excavator found no preceding occupation under the enclosure.',locators=[shdate,loc('bhanajith2009','pp. 1-3')]),
    searched=['Season report and full site sequence; Chase faunal study; later site radiocarbon synthesis with Table 1; new Shikarpur dating and Bayesian chronology searches.'],
    disagreements=[assertion('Earlier reports of Early Harappan deposits were not confirmed in the later work: the first deposits associated with the enclosure contain Classical Harappan material.',loc('bhanajith2009','pp. 1, 3'),loc('chase2014','pp. 3-4, 6'))])
for code,bpv,err,pl,cal in [('Beta-360113',3890,30,'Phase 1',[2470,2290]),('Beta-360115',3870,30,'Phase 1',[2470,2210]),('Beta-360112',3890,30,'Phase 1',[2470,2290]),('Beta-360114',3720,30,'Phase 2',[2210,2030])]:
    rc('shikarpur',code,bpv,err,'not specified in published summary table','Phase assigned by authors; trench and lot absent from Table 1',pl,
       'layout phase' if pl=='Phase 1' else 'later comparison',loc('chase2020','p. 6, Table 1',code),
       reported_calendar=dict(scale='calibrated BC; IntCal13, OxCal 4.3.2',range_2sigma_bce=cal),half_life=None,
       notes='Individual calibrations, not a Bayesian boundary model. Full laboratory material/context records remain to be recovered.')

# The first occupation is explicitly stated in the newer site chronology.
dcastle=TOWNS['dholavira']['parts'][0]
dc=candidate(2,3551,loc('sengupta2020','p. 382, Abstract; Table 1'),
             'Site dating study explicitly places the beginning of occupation at approximately 5500 calendar years BP. The first enclosed nucleus is the first occupation in the excavation sequence.',
             notes='Rounded published beginning; conversion uses cal BP relative to 1950 CE and the absence of year zero in BCE. The approximate statement supplies no start uncertainty.')
dcastle['candidates_by_level']['2'].append(dc);dcastle['proposed_candidate']=dc
