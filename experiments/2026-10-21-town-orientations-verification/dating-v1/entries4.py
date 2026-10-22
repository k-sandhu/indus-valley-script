"""Further source observations and explicit records of unresolved optional sites."""
source('sarkar2016','Anindya Sarkar, Arati Deshpande Mukherjee, M. K. Bera, B. Das, Navin Juyal, P. Morthekai, R. D. Deshpande, V. S. Shinde and L. S. Rao',2016,
       'Oxygen isotope in archaeological bioapatites from India: Implications to climate change and decline of Bronze Age Harappan civilization',
       'Scientific Reports 6:26555','https://doi.org/10.1038/srep26555',download='bhirrana2016.html',
       access_route='Full article HTML from PMC; linked PDF and supplement returned challenge HTML. Fig. 2 and its associated cultural chronology were inspected as text.')
bharch=loc('dikshit2013','pp. 128-130; Fig. 78')
bhdate=loc('sarkar2016','Fig. 2; text beginning “A compilation of calibrated radiocarbon dates”')
source('rao2004bhirrana','L. S. Rao, N. B. Sahu, Prabash Sahu, U. A. Shastry and Samir Diwan',2004,
       'Unearthing Harappan Settlement at Bhirrana (2003-04)','Puratattva 34:20-24',
       'https://ignca.gov.in/Asi_data/87942.pdf',download='puratattva34-full.pdf')
source('rao2005bhirrana','L. S. Rao, Nandini B. Sahu, Prabash Sahu, Samir Diwan and U. A. Shastry',2005,
       'New Light on the Excavation of Harappan Settlement at Bhirrana','Puratattva 35:60-68',
       'https://ignca.gov.in/Asi_data/88233.pdf',download='gujarat-ceramics.pdf')
bhplan=loc('rao2004bhirrana','p. 21, Period II (Transitional)')
bhcross=loc('rao2005bhirrana','pp. 60, 63-64, revised sequence and Period IIa / IIb')
bhph=[phase('Period IA: Hakra','Subterranean pit complex precedes ground-level masonry.',bharch),
      phase('Period IB: Early Harappan','Mud-brick structures follow the pit occupation.',bharch),
      phase('Period IIA: Early Mature Harappan','Enclosure wall is attributed jointly to this and the succeeding mature phase; earliest enclosure subphase remains a review issue.',bharch),
      phase('Period IIB: Mature Harappan','Enclosure, houses, streets and lanes.',bharch)]
town('bhirrana','Bhirrana',[part('planned settlement, later enclosed','Period IIA (earlier report: Transitional Period II)',
     assertion('The first report places definite planning, overground rectangular houses and pathways in its Transitional Period II. The next report relabels that occupation Early Mature Harappan IIA, and describes the exposed enclosure under IIB.',bhplan,bhcross),bhph,
     [candidate(2,4551,bhdate,'The newer site dating study places Early Mature Harappan at approximately 6.5-5 calendar ka BP; the earlier boundary is converted using the calendar-BP epoch.',
                notes='Rounded published phase estimate, joined to the revised excavation sequence. This is not an independently dated enclosure foundation.'),
      candidate(2,4500,loc('dikshit2013','p. 132, Table 5'),'The calibrated-site synthesis proposes a tentative start for IIA from the listed site determinations.')],
     alternatives=[assertion('Dating the exposed enclosure rather than the first reported planned settlement would require IIB: the primary report describes the wall under IIB, while the later synthesis attributes it jointly to IIA and IIB.',bhcross,bharch)],
     notes='The proposal dates the earlier planned settlement. A reviewer who defines the part by the exposed enclosure must reject this join and use its construction phase instead. Published cultural labels and very early chronology require review.')],
     first=dict(year_bce=7551,astronomical_year=-7550,evidence='The newer article places the first Hakra phase at approximately 9.5 calendar ka BP; this is its rounded proposed phase chronology.',
                reported_estimates=[dict(year_bce=7500,astronomical_year=-7499,scale='earlier tentative synthesis',locator=loc('dikshit2013','p. 132, Table 5'))],locators=[bhdate]),
     searched=['Original preliminary report route, later calibrated synthesis and site isotope/chronology article; supplement and Bayesian chronology search.'],
     disagreements=[assertion('The later article combines conventional-age language and calibrated phase brackets. The synthesis calls the early chronology tentative and uses an alternative set of period labels alongside the excavator labels. These assignments must be evaluated against the excavated profiles.',bhdate,loc('dikshit2013','pp. 131-132, Tables 4-5'))],required=False)
for code,bp,err,ph,old,young in [('BS-2308',3300,200,'later occupation, phase unresolved',1878,1839),
('BS-2327',40,80,'contaminated; phase unresolved',None,None),('BS-2310',3190,160,'later occupation, phase unresolved',1641,1287),
('BS-2311',3890,90,'IIB (synthesis grouping)',2471,2273),('BS-2318',6120,250,'IB (synthesis grouping)',5316,4775),
('BS-2333',7590,240,'IA (synthesis grouping)',6689,6201),('BS-2314',5700,170,'IIA (synthesis grouping)',4714,4360),
('BS-2301',4050,90,'IIB (synthesis grouping)',2856,2414),('BS-2485',4450,170,'IIA (synthesis grouping)',3370,2890),
('BS-2492',4230,100,'IIB (synthesis grouping)',2920,2640),('BS-2494',3750,110,'IIB (synthesis grouping)',2310,1980),
('BS-2495',4160,100,'IIB (synthesis grouping)',2880,2580),('BS-2496',4340,120,'IIA (synthesis grouping)',3100,2880),
('BS-2497',4280,110,'IIA (synthesis grouping)',3020,2700),('BS-2499',3490,120,'IIC (synthesis grouping)',1950,1640),
('BS-2481',8350,140,'IA (synthesis grouping)',7570,7180),('BS-2482',4990,180,'IIA (synthesis grouping)',3970,3640)]:
    rc('bhirrana',code,bp,err,'charcoal (site suite; individual identification not specified)','Field labels in Table 4; trench, layer and depth not supplied',ph,
       'layout occupation' if ph.startswith('IIA') else 'predecessor' if ph.startswith('IB ') else 'other occupation comparison',
       loc('dikshit2013','pp. 131-132, Tables 4-5',code),
       reported_calendar=dict(scale='calibrated BCE as printed',range_bce=[old,young] if old is not None else None,
                              interval_note='First lot is headed one sigma; second lot does not restate interval probability.'),half_life=None,
       notes='HTML transcription pending page-image check. Individual phase association is the synthesis grouping by printed age range, not an independently supplied excavation context. BS-2308 has inconsistent calendar columns and remains unresolved.')
TOWNS['bhirrana']['excluded_determination_observations']=[assertion('Table 4 also lists BS-2502, field label KRN(K), with conventional age 7150 ± 130 BP. The field label raises a site-attribution question; it is withheld from the Bhirrana determination rows pending checking.',loc('dikshit2013','p. 131, Table 4','KRN(K), BS-2502'))]

# Recover the additional Rakhigarhi suite without assigning unreported phases.
for code,bp,err,ctx,cal,ce in [('BS-3313 / S-4168',5410,100,'No.86, RGR-2, 1080 CM',6180,50),
('BS-3314 / S-4169',5230,90,'No.43, RGR-1, 3.2-3.3 CM (unit as printed)',6030,40),
('BS-3323 / S-4179',3910,100,'No.223, RGR-2, 8.45 m',5350,100),
('BS-3325 / S-4181',4690,120,'No.155, RGR-2, 0.74 CM (unit as printed)',5450,80),
('BS-3340 / S-4186',3740,70,'No.59, RGR-1, 2.70 m',4090,80),('BS-3342 / S-4188',4950,310,'No.51, RGR-6, 4.32 m',5680,340),
('BS-3345 / S-4191',4430,80,'No.37, RGR-1, 2.55-2.70 m',5060,40),('BS-3350 / S-4197',4650,90,'No.28A, RGR-1, 200-205 cm',5410,90),
('BS-3352 / S-4199',3840,70,'No.35, RGR-1, 240-250 cm',4270,60),('BS-3353 / S-4200',3810,70,'No.43, RGR-1, 320-330 cm',4200,100)]:
    rc('rakhigarhi',code,bp,err,'charcoal',ctx,'not supplied in Table 3','phase relationship unresolved',
       loc('dikshit2013','p. 127, Table 3',code),reported_calendar=dict(scale='calibrated BP as reported',central_cal_bp=cal,error_cal_bp=ce),half_life=None,
       notes='Two shared laboratory codes already recorded from Nath are not duplicated. The BS-3323 conventional/calibrated pairing and some printed depth units require primary-table review. Calibrated BP summaries are not founding boundaries.')

source('chakraborty2024','Kalyan Sekhar Chakraborty, Sheahan Bestel, Mary Lucus, Patrick Roberts, Prabodh Shirvalkar, Yadubirsingh Rawat, Thomas Larsen and Heather M.-L. Miller',2024,
       'To waste or not to waste: a multi-proxy analysis of human-waste interaction and rural waste management in Indus Era Gujarat',
       'Archaeological and Anthropological Sciences 16:141, pp. 1-22','https://doi.org/10.1007/s12520-024-02046-w',download='kotada2024-mpg-rest.pdf')
kblay=loc('chakraborty2024','pp. 5-7, Table 1; p. 10, AMS dates')
kbdate=loc('chakraborty2024','p. 10, AMS dates; Fig. 5 on p. 8')
town('kotada-bhadli','Kotada Bhadli',[part('walled settlement','Beginning_of_walled_occupation (model label); wall foundation S6',
     assertion('The study models the beginning of walled occupation separately from an earlier basal sample. Wall foundations overlie earlier deposits; the residential occupation rests on natural soil.',kblay),
     [phase('prewall (model phase)','Basal charcoal precedes or is contemporary with the wall; table and narrative differ in whether this represents prior occupation.',kblay),
      phase('walled (model phase)','Enclosure, central residential complex and occupational deposits.',kblay)],
     [candidate(2,2270,kbdate,'The dating study explicitly states an approximate calendar beginning for occupation at the walled settlement from its site radiocarbon model.',
                notes='The plotted start boundary has no printed numerical median or start-only 95% range. The prose value is retained at Level 2; the overall occupation interval is not used as start uncertainty.')],
     notes='Later paper metadata was found, but its complete paginated text was unavailable. Its broad site chronology is not used to replace this inspected construction-specific start.')],
     first=dict(year_bce=None,evidence='The basal dated deposit may indicate initial occupation, but is described as prior to or contemporary with wall construction. No separate accepted first-occupation point is given.',locators=[kblay,kbdate]),
     searched=['Primary calibrated dating and model article, excavation preliminary-report references, later caravanserai paper; institutional PDF route and model figure inspection.'],
     disagreements=[assertion('The stratigraphy table calls the basal deposit pre-occupation, while the narrative allows it to represent initial settlement. The reported occupation interval is not the start-boundary range.',kblay,kbdate)],required=False)
TOWNS['kotada-bhadli']['published_models']=[dict(level=1,eligible_candidate=False,
    reason='Fig. 5 publishes a Bayesian phase model and a plotted start distribution, but no numerical median and start-only 95% range were recovered. Neither was estimated from pixels.',
    locator=kbdate,overall_occupation_95_range_bce=[2350,1810],overall_occupation_68_range_bce=[2270,2000])]
for code,bp,tr,depth,layer,old,young in [('UOC-4155',3731,'-XM3',-3.61,'S3',2290,1980),
('UOC-4156',3677,'-XJ11',-4.05,'S5',2200,1930),('UOC-4157',3758,'-XB2',-4.2,'3 (residence)',2300,2030),
('UOC-4158',3858,'-XO3',-4.2,'S9',2470,2200)]:
    rc('kotada-bhadli',code,bp,43,'charcoal; taxon unidentifiable',f'Trench {tr}; level {depth} m below datum as printed; layer {layer}',
       'prewall' if code=='UOC-4158' else 'walled','predecessor or contemporary basal deposit' if code=='UOC-4158' else 'layout occupation',
       loc('chakraborty2024','pp. 6-8, Table 2',code),reported_calendar=dict(scale='calibrated BCE, IntCal20',range_2sigma_bce=[old,young]),
       notes='Conventional-age calculation specified in methods. A modelled start is distinct from this sample interval.')

source('abhayan2025','G. S. Abhayan, Pramod P. Joglekar, P. Ajithprasad, S. V. Rajesh, Pankaj Goyal, Brad Chase, Jeevan Kharakwal and Prabodh Shirvalkar',2025,
       'Ichthyoarchaeological perspectives on roles of fish and red meat during Indus Civilization in Gujarat, India',
       'Frontiers in Environmental Archaeology 4:1517351','https://doi.org/10.3389/fearc.2025.1517351',download='navinal2025-retry.pdf')
nv=loc('abhayan2025','pp. 6-7, Table 1; section 4.4; Fig. 2E')
town('navinal','Navinal',[part('settlement, planned-unit status unresolved','NVL I; earliest exposed construction phase unresolved',
     assertion('The study gives occupation affiliations and a site plan, but does not establish the first construction of a separately planned unit.',nv),
     [phase('NVL I','Mature Harappan material culture; first architecture not assigned in the inspected chronology.',nv),
      phase('NVL II','Late Harappan material culture.',nv)],no_candidate_reason='The reported radiocarbon span dates collected fish otoliths, without a first-construction context or stated layout-phase start.')],
     first=dict(year_bce=None,evidence='Surface and test-pit material establishes occupation, without a founding boundary.',locators=[nv]),
     searched=['Latest site-coauthored faunal synthesis; Navinal exploration and craft-production publications; radiocarbon and first-layout searches.'],
     notes=[assertion('The article reports an otolith date span of 2325-1460 BCE, but supplies no laboratory codes or BP/error table in the site account. This span is retained as an occupation observation, not a determination row.',nv)],required=False)
# More recent regional era labels do not establish calendar starts from the sites' own determinations.
for slug in ('kanmer','shikarpur','gola-dhoro'):
    TOWNS[slug]['notes'].append(assertion('A newer faunal synthesis uses broad regional calendar bins for the site phases. It supplies no revised site-specific start-boundary analysis; earlier dated phase estimates are retained.',loc('abhayan2025','pp. 6-7, Table 1 and site accounts')))

source('rao1963rangpur','S. R. Rao, with contributions by B. B. Lal, Bhola Nath, S. S. Ghosh and Krishna Lal',1963,
       'Excavation at Rangpur and Other Explorations in Gujarat','Ancient India 18-19 (1962-1963):5-207',
       'https://ignca.gov.in/Asi_data/37501.pdf',download='rangpur1963.pdf')
rg=loc('rao1963rangpur','pp. 20-22, 25-27, 35-38; Figs. 7-10')
town('rangpur','Rangpur',[part('Harappan built settlement','Sub-period II A, structural Phase I',
     assertion('The earliest Harappan construction phase includes houses, raised platforms and drains over the earlier microlithic occupation and a sterile interval.',rg),
     [phase('Period I','Microlithic occupation, followed by a sterile interval.',rg),
      phase('Sub-period II A, Phases I-IV','Harappan houses, platforms and drains; initial Phase I followed by rebuildings.',rg),
      phase('Sub-period II B','Later habitation with floors; drains and well-preserved brick houses absent.',rg),
      phase('Sub-period II C','Changed ceramic assemblage and limited surviving structures.',rg),
      phase('Period III','Later brick houses; no reconstruction of the early Harappan plan demonstrated.',rg)],
     [candidate(3,2000,loc('rao1963rangpur','pp. 25-27, Chronology'),'Excavator states the first Harappan settlement start from ceramic and stratigraphic cross-dating; no absolute dating evidence from Rangpur itself.',
                notes='Historical excavation estimate within an older chronology, indirectly compared with old Lothal radiocarbon results. It is not a calibrated radiocarbon start from Rangpur.')])],
     first=dict(year_bce=None,evidence='The microlithic occupation precedes the Harappan structures. Its proposed date is explicitly provisional, without definite dating evidence.',
                reported_estimates=[dict(year_bce=3000,astronomical_year=-2999,scale='excavator provisional estimate',locator=loc('rao1963rangpur','pp. 20, 26-27'))],locators=[rg]),
     searched=['Original excavation chronology and architecture; recent regional radiocarbon synthesis; first-layout and Bayesian chronology searches.'],
     disagreements=[assertion('The original excavation chronology assigns a much later Harappan sequence than modern regional era schemes. No site-specific replacement calibrated start for its first built layout was recovered.',rg,loc('kanungo2025','pp. 59-61'))],required=False)

source('ghosh1967iar','A. Ghosh (ed.)',1967,'Indian Archaeology 1963-64—A Review',
       'New Delhi: Archaeological Survey of India','https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201963-64%20A%20Review.pdf',
       access_route='Search-indexed text of official report; direct full-PDF access timed out. Publication year checked against Central University of Punjab catalogue.',
       notes='Bibliographic year corroborated at https://opac.cup.edu.in/bib/21022. Numerical architecture values are not transcribed from the index.')
de=loc('ghosh1967iar','pp. 10-12, Desalpur account; pl. VII')
town('desalpur','Desalpur (Gunthli)',[part('walled settlement','Period IA; founding structural subphase unresolved',
     assertion('The report identifies the stone-enclosed settlement and an earlier Mature Harappan occupation, but the inspected extract does not fix the enclosure foundation to a named structural subphase.',de),
     [phase('Period IA','Mature Harappan settlement and masonry enclosure; internal structural succession needs full report review.',de),
      phase('Period IB','Late Harappan continuation.',de),phase('Period II','Separate early-historic occupation.',de)],
     no_candidate_reason='No eligible calendar start tied to initial enclosure construction was recovered.')],
     first=dict(year_bce=None,evidence='Mature Harappan occupation is the earliest excavated cultural period in the inspected report extract; a calendar founding date is unresolved.',locators=[de]),
     searched=['Original IAR report and Soundara Rajan reference; later regional syntheses and radiocarbon searches.'],required=False)

kd=loc('bisht2015','pp. 14-15, Kot Diji account, citing F. A. Khan 1965, pp. 11-85')
kdph=[phase('Period I: Kot Dijian / Early Harappan','Fortified settlement with domestic structures against the enclosure; ends after fire episodes.',kd),
      phase('Period II: Mature Harappan','Settlement on the earlier mound and in an adjacent lower residential area.',kd)]
town('kot-diji','Kot Diji',[
    part('citadel / antecedent enclosed mound','Period I enclosure; Mature Harappan plan unresolved',assertion('The antecedent settlement has the first enclosure, while the mature occupation uses the accumulated mound. The inspected account does not establish continuity of the exposed mature plan.',kd),kdph,
         no_candidate_reason='No inspected calendar start is tied securely to the exposed Harappan construction phase.'),
    part('lower residential settlement','Period II',assertion('The account attributes the lower residential settlement to the Mature Harappan occupation.',kd),kdph,
         no_candidate_reason='A site-specific calendar start for this lower-town construction phase was not recovered.')],
     first=dict(year_bce=None,evidence='The antecedent Kot Dijian occupation precedes the mature settlement, but an eligible founding boundary was not established.',locators=[kd]),
     searched=['Khan excavation-report route; Mughal reanalysis and Bisht comparative account; site calibration and Bayesian chronology searches.'],required=False)

# Selected-date observations are retained for these screened sites, with unknown architecture joins.
for slug,name,seq,rows,page in [
('balakot','Balakot','Period II / earlier Period B: Mature Harappan',[('HAR-1993',3890,100),('HAR-1992',4050,130)],'p. 337, Table III'),
('allahdino','Allahdino','Mature Harappan; architectural subphase unresolved',[('P-2295',3760,70),('P-2237',3840,60),('P-2296',3930,50)],'p. 337, Table III'),
('mitathal','Mitathal','architectural phase unresolved',[('PRL-291',3600,110),('PRL-290',3820,130)],'p. 338, Table III')]:
    ll=loc('kenoyer1991',page)
    town(slug,name,[part('town parts and first planned unit unresolved',seq,
         assertion('The selected-date compilation identifies occupation at this site but supplies no first-construction context for a town part.',ll),[],
         no_candidate_reason='The dated samples have not been joined to an excavator-defined founding layout phase.')],
         first=dict(year_bce=None,evidence='The inspected determination compilation does not establish first occupation.',locators=[ll]),
         searched=({'balakot':['Dales original and later excavation summaries; Franke-Vogt reanalysis; calibrated-date synthesis and layout-start searches.'],
                    'allahdino':['Fairservis report and architecture searches; recent salvage-project overview; calibrated-date synthesis and phase-start searches.'],
                    'mitathal':['Suraj Bhan excavation report and newer excavation-report routes, including SSRN access failure; calibrated-date compilation and phase-start searches.']})[slug],required=False)
    for code,bp,err in rows:
        rc(slug,code,bp,err,'not specified in selected-date table','Detailed trench context not supplied',seq,'construction-phase relationship unresolved',loc('kenoyer1991',page,code),
           reported_calendar=dict(scale='CALIB intercepts and longer-half-life uncalibrated BC appear in source table'),
           notes='Selected compilation only; full excavation/laboratory suite remains to be recovered.')

ku=loc('dikshit2013','pp. 127-128, Kunal account')
town('kunal','Kunal',[part('planned settlement','Period IC, internal subphase unresolved',
     assertion('The synthesis attributes rectangular ground-level houses and drainage with street soakage jars to IC, after successive pit-dwelling occupations.',ku),
     [phase('Period IA','Subterranean pit dwellings.',ku),phase('Period IB','Expanded pit dwellings lined with mud bricks.',ku),
      phase('Period IC (i)-(iii)','Ground-level rectangular houses and drainage; successive enlargement.',ku)],
     no_candidate_reason='The inspected source supplies sample calibrations for the site but no calendar start explicitly assigned to IC.')],
     first=dict(year_bce=None,evidence='The synthesis states that the earliest level has not been dated.',locators=[ku]),
     searched=['Excavation report and Possehl laboratory correspondence routes; site calibrated-age synthesis and first street-plan searches.'],required=False)
source('possehl1994letter','Gregory L. Possehl',1994,'From Gregory L. Possehl',
       'Letter to T. D. Jogpal, 18 November 1994, reproduced in Puratattva 24 (1993-94), scanned journal copy.',
       'https://ignca.gov.in/Asi_data/87872.pdf',download='kunal2008.pdf',
       access_route='Search-indexed letter tables. Download title page identifies the journal; the letter page image remains to be located.',
       notes='Transport filename is misleading: the acquired volume is Puratattva 24, not the Kunal report.')
for code,bp,err,ctx,old,young,ph in [('Beta-77726',4040,70,'YC I, quadrant IV; layer 4; depth 149 cm',2837,2466,'IB (IAR attribution)'),
('Beta-77727',4250,130,'YA 2, quadrant II; layer 10; depth 300 cm',3016,2621,'IA (IAR attribution)'),
('Beta-77728',3990,70,'XA 3, quadrant I; layer 12; depth 243 cm',2577,2409,'not supplied in letter')]:
    rc('kunal',code,bp,err,'charcoal',ctx,ph,'predecessor occupation or unassigned; IC join unresolved',
       loc('possehl1994letter','Unnumbered letter, sample-context table and radiocarbon-results table',code),
       reported_calendar=dict(scale='Calib-3 cal BC',range_bce=[old,young]),
       notes='Letter separates conventional Libby BP from longer-half-life BC. Phase attribution for the first two is corroborated in the search-indexed IAR 1997-98 radiocarbon section; it is not stated in this letter.')

source('wheeler1968','R. E. M. Wheeler',1968,'The Indus Civilization',
       'Third edition. Cambridge: Cambridge University Press.',
       'https://storage.googleapis.com/teachmint/public/ca59eb01-d613-474d-be9e-0d34e8b86776.pdf',
       access_route='Search-indexed paginated text; underlying Dales and Stein excavation accounts identified, not fully acquired.')
sd=loc('wheeler1968','pp. 60-61, Sutkagen-dor and other sites')
town('sutkagen-dor','Sutkagen-dor',[
    part('citadel','earliest Harappan phase (Phase I)',assertion('The enclosure is described as founded on bedrock with an internal platform in the earliest Harappan phase.',sd),
         [phase('Harappan Phases I-III','Repeated occupation within the enclosure; complete construction succession not recovered.',sd)],
         no_candidate_reason='No site radiocarbon model or calendar start assigned by the excavator to the first enclosure phase was recovered.'),
    part('lower / outer town','not established',assertion('The source describes a lower residential area but supplies no founding phase.',sd),[],
         no_candidate_reason='First planned phase and calendar start are unresolved.')],
    first=dict(year_bce=None,evidence='Earliest Harappan occupation on bedrock is described without a calendar founding date.',locators=[sd]),
    searched=['Stein and Dales report routes; Wheeler paginated account; calibrated and Bayesian site chronology searches.'],required=False)

# No construction-phase observation with an adequate locator was recovered for these sites.
screened={
 'nausharo':('Nausharo',['Jarrige, Didier and Quivron 2011, Paléorient 37(2):7-34, DOI 10.3406/paleo.2011.5420; Persée article and chronology table routes.',
              'Jarrige institutional excavation-project overview; original excavation accounts and enclosure / house-block construction searches.'],
             'The occupation chronology was located, but a locatable correlation of the first construction of each planned mound with its phase was not recovered.'),
 'ganweriwala':('Ganweriwala',['Mughal survey and later topographic studies; University of Lahore project account and recent excavation / radiocarbon searches.',
                  'https://uol.edu.pk/uols-soca-and-imbb-lead-the-audio-visual-documentation-and-genetic-analysis-of-ganweriwala-excavation/'],
                 'Project announcements were found; no paginated construction-phase chronology or site radiocarbon table was recovered.'),
 'karanpura':('Karanpura',['Prabhakar and Majid, Preliminary Results of Excavation at Karanpura, Man and Environment 39(2):13-41; official contents and Harappa article route.',
                'Academia preview unavailable; ResearchGate upload did not expose the report text. IAR report route and radiocarbon / enclosure founding searches.'],
               'The report was identified but its phase-specific architecture and dating pages were not acquired; no candidate is inferred from a generic occupation span.'),
 'pabumath':('Pabumath',['IAR excavation notices, especially Indian Archaeology 1980-81—A Review, p. 14; direct official PDF route timed out.',
                'Original earlier excavation references and regional calibrated-date / enclosure phase searches.'],
               'A building notice and bibliography were located; a construction-phase chronology and calendar start were not recovered.')}
for slug,(name,searches,reason) in screened.items():
    town(slug,name,[],first=None,searched=searches,notes=[dict(text=reason,locators=[])],required=False)
    TOWNS[slug]['no_candidate_reason']=reason
    TOWNS[slug]['coverage_status']='screened; construction-phase evidence not recovered'

# Preserve the caption's alternative dating of Chanhu-daro artefacts without treating it as a new measured boundary.
TOWNS['chanhu-daro']['disagreements'].append(assertion('The narrative defines the first Indus period as beginning at 2500 BCE, while the artefact caption gives 2600/2500 BCE as an opening alternative. The more specific first-period narrative supplies the proposal.',loc('didier2017','p. 2; p. 6, Fig. 4')))
