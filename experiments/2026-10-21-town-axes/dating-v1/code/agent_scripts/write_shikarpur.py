import json, pathlib, sys

OUT = pathlib.Path(sys.argv[1])
UTC = sys.argv[2]
CEN = "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/"

NO_DATE_BASIS = (
    "No calendar range. The excavators' interim reports that we read (bhan2008shikarpur, bhan2009shikarpur and the season entries in iar2007-08, iar2009-10 and iar2012-13) "
    "date Phase I only relatively, as 'entirely belonging to the Classical Harappan' of the urban phase, with a few Anarta sherds from the earliest level, isolated Sorath "
    "Harappan sherds from its middle levels, and Sorath Harappan pottery dominant in Phase II, whose forms they compare with Rojdi A and B, Kuntasi I, Bagasra III and "
    "Rangpur IIA-IIB (iar2007-08 pp. 60-61, 64). We found no radiocarbon determination from Shikarpur in any source.")

inner = {
    "part": "inner fortified settlement: the whole town inside the mud-brick fortification wall",
    "layout_phase": "Phase I of the M. S. University of Baroda excavations (2007-08 onward), Classical Harappan, urban phase",
    "what_was_built": (
        "The 2008-09 report states that 'Deep sounding just outside the wall in the trench Ep3 revealed that the construction of the wall had started from the very beginning of "
        "Harappan occupation at the site as the basal part of the wall was found resting on the natural sediments' (bhan2009shikarpur p. 1). The wall is of multi-coloured mud "
        "brick, built 'at least in three stages in order to increase the overall height', with a core 4.50-5.00 m thick of dark grey and light cream bricks, a thick whitish clay "
        "plaster on the lower part in the first stage, and a small rampart-like support of dark bricks at the base added later 'but in the first stage itself'; the extant top is "
        "about 9 m thick and the base probably more than 12 m (pp. 1-2). The 2009-10 season found that the early wall was much thinner, 6 m to at most 7.6 m, plastered inside and "
        "out and probably about 2.90 m high, and that it remained the core as the wall was widened and heightened; an internal bastion at the north-eastern corner was added in the "
        "second stage of construction (iar2009-10 p. 27). The four walls stand about 103.50 m apart, enclosing an almost square area of about 1.07 ha, or 1.52 ha including the "
        "wall (iar2009-10 p. 25). Inside, 'Harappan occupation in this phase starts with structures built of mud-bricks showing the Harappan ratio in their size' (iar2007-08 p. 60), "
        "and the low central part of the site was an open space surrounded by structures 'probably right from the beginning of Harappan occupation at the site and it remained so "
        "through out' (bhan2009shikarpur p. 2). The first season had not reached the base of the wall and reported that 'The history of construction of this wall is still not "
        "very clear', with two stages of construction and 'a massive repair work that was carried out in the early stages of the Phase II occupation' (iar2007-08 p. 64; "
        "bhan2008shikarpur p. 6)."),
    "locator": "bhan2009shikarpur pp. 1-2; iar2009-10 pp. 25, 27; iar2007-08 pp. 60, 64; bhan2008shikarpur pp. 4, 6",
    "excavator_range_bce": None,
    "excavator_basis": NO_DATE_BASIS,
    "radiocarbon": [],
    "bayesian_start": None,
    "syntheses": [
        {"source": "abhayan2025fish", "page": "Table 1 and section 4.3 (online article, no page numbers)", "range_bce": [2600, 2200],
         "statement": ("A regional synthesis co-authored by the excavation director P. Ajithprasad places 'SKP I' in a Mature Harappan 'Phase I (c. 2600-2200 BCE)', SKP II in "
                       "'Phase II (c. 2200-1900 BCE)' and SKP III in a Late Harappan 'Phase III (c.1900-1700 BCE)'. It describes the wall as 'Built during three stages' and "
                       "resting 'on natural sediments', and notes that the Early Harappan deposits reported by the earlier State excavation 'were not found in the later excavation'."),
         "disagreement": ("Supplies the only calendar range we found for Phase I; it is a regional phase bracket assigned by comparison of material culture across five sites, "
                          "not a date measured at Shikarpur.")},
        {"source": "iar1990-91", "page": "103", "range_bce": [2500, 2200],
         "statement": ("The Birbal Sahni Institute's palaeobotanical report on carbonized seeds, fruits and wood from the 1988-89 and 1989-90 State excavations describes them as "
                       "'collected from the Harappan levels (circa 2,500-2,200 BC)'."),
         "disagreement": ("Refers to the Harappan levels of the earlier State excavation as a whole and gives no basis for the range; it starts a century later than "
                          "abhayan2025fish and has no phase subdivision.")},
        {"source": "rajesh2007gujarat", "page": "61", "range_bce": None,
         "statement": ("Summarising the 1987-1990 State excavation under M. H. Raval, the authors report 'Harappan cultural materials in a deposit of over 3 m thickness', in which "
                       "'layers 1 to 9 are Mature Harappan and layers 10 to 19 are Early Harappan', according to the excavators. They give no date."),
         "disagreement": ("Implies an Early Harappan occupation below the Mature Harappan levels, which the University of Baroda excavations did not find (joglekar2011shikarpur "
                          "p. 15; abhayan2025fish section 4.3).")},
        {"source": "chakraborty2019kachchh", "page": "22", "range_bce": None,
         "statement": ("A doctoral synthesis of Kachchh places Shikarpur Period II in the 'Urban-Late Transition or the Late Mature Phase in Gujarat (circa. 2200-1900 BCE)' and "
                       "writes that 'major restoration of the Shikarpur settlement wall was carried out during this transition period', citing the excavators."),
         "disagreement": ("Concerns the repair rather than the building of the wall; read with abhayan2025fish it implies that the wall stood before about 2200 BCE, which no "
                          "excavator's report states in calendar years.")}
    ],
    "conflicts": (
        "The two excavating teams disagree on the earliest deposit. The Gujarat State Department of Archaeology (1987-1990, M. H. Raval) reported Early Harappan material in "
        "layer 10 of trench C1 (iar1987-88 p. 15) and, by the account in rajesh2007gujarat (p. 61), 'layers 10 to 19' as Early Harappan; the University of Baroda excavations "
        "'did not reveal any Early Harappan deposit' (joglekar2011shikarpur p. 15) and found Classical Harappan pottery predominant from the first floor on the natural sand "
        "(bhan2009shikarpur p. 3). The State team's 'portion of a 9.30 m thick portection (?) wall like structure made of mud bricks ... probably going around the entire mound' "
        "(iar1988-89 p. 10) and its 'broad wall or raised platform-like structure' enclosing the habitation (iar1989-90 p. 21) correspond to the Baroda fortification but were "
        "not dated. Within the Baroda reports, the first season left the wall's history unresolved (iar2007-08 p. 64), the second placed its foundation at the beginning of the "
        "Harappan occupation (bhan2009shikarpur p. 1), and the dimensions changed between seasons: the southern and northern walls are 99.55 m apart and the fortified area "
        "'close to one hectare' in bhan2009shikarpur (p. 2), but 103.50 m and 1.07 ha in iar2009-10 (p. 25). The thickness of Phase III is given as the top 10-20 cm "
        "(iar2007-08 p. 64) and as 30-50 cm (gadekar2014shikarpur p. 140). No source gives a calendar date measured at the site.")
}

outer = {
    "part": "outer fortification wall on the southern side and the habitation between the inner and outer walls",
    "layout_phase": "Phase I (Classical Harappan), built after the first spread of habitation in the southern part of the site",
    "what_was_built": (
        "In the sixth season (2012-13) a row of trenches about 40 m south of the southern inner wall, chosen after a ground-penetrating radar survey and from crop marks on "
        "aerial photographs, exposed stone and mud-brick dwellings: 'While both the structures were built in the phase I, the stone structures were continued to be in use in "
        "the phase II too' (iar2012-13 p. 30). Trench Id1 exposed an outer fortification wall 1.95 m thick at its extant top, against 10 m for the inner wall, tapering to a "
        "2.5 m thick base, its top about 4 m below that of the inner wall. 'The foundation trench of the wall had cut through about 30 to 40cm thick cultural deposit suggesting that "
        "the outer wall was constructed a bit later than the initial spread of habitation in the southern part of the site'; the pottery below and against the wall is Classical "
        "Harappan with a few Anarta sherds. The mud-brick structure of trench Ic3 runs south to join the outer wall; the wall was repaired on its eastern part from the tenth "
        "course upward and later fell out of use, its inner face cut by a large silo (iar2012-13 pp. 30-31). The plan in gadekar2014shikarpur (Fig. 2, p. 139) shows structures "
        "both inside and outside the fortified area."),
    "locator": "iar2012-13 pp. 30-31; gadekar2014shikarpur p. 139",
    "excavator_range_bce": None,
    "excavator_basis": NO_DATE_BASIS,
    "radiocarbon": [],
    "bayesian_start": None,
    "syntheses": [],
    "conflicts": ("Only one interim report (iar2012-13) describes the outer wall, so there is nothing to compare; it places the wall within Phase I but after the first habitation "
                  "in the south, which makes it later than the inner wall if the inner wall dates from the very beginning of the occupation as bhan2009shikarpur states.")
}

doc = {
    "town": "shikarpur",
    "compiled_utc": UTC,
    "parts": [inner, outer],
    "first_occupation": {
        "phase": "Phase I (University of Baroda excavations); the earlier State excavation called its lowest levels Early Harappan",
        "range_bce": None,
        "basis": (
            "No calendar date. In trench Em13 'the first habitation came up here after leveling the top of the sand-dune by reworking the sand and yellowish gravel and preparing a "
            "living floor' with an open hearth and a buried pot; this floor and the mud-brick structure and brick-paved floor above it, about 40 cm of deposit, contain more Anarta "
            "pottery than later layers, but 'the predominant ceramic type in this early level is the Classical Harappan pottery' (bhan2009shikarpur p. 3). Because the wall rests on "
            "the natural sediments and was begun 'from the very beginning of Harappan occupation' (p. 1), the excavators make first occupation and layout one phase. The State "
            "excavation of 1987-88 reported that 'layer 10 is marked by Early Harappan material' above natural soil in trench C1 (iar1987-88 pp. 14-15), a level the Baroda team did "
            "not find."),
        "locator": "bhan2009shikarpur pp. 1, 3; iar1987-88 pp. 14-15; joglekar2011shikarpur p. 15"
    },
    "sources": [
        {"id": "bhan2009shikarpur",
         "citation": ("Bhan, K. K. and P. Ajithprasad 2009. Excavations at Shikarpur, Gujarat 2008-2009. Harappa.com, PDF, 9 pp. (authors as given on the harappa.com page; the PDF "
                      "itself prints no author)."),
         "url_or_path": "https://www.harappa.com/sites/default/files/pdf/Shikarpur-2008-2009.pdf; " + CEN + "SHIKARPUR2009.pdf",
         "sha256": "b19286e37be4e17e172d44aaeb4c56bda13f8a77c4c9eec25f227f120f4ddc0f"},
        {"id": "bhan2008shikarpur",
         "citation": ("Bhan, K. K. and P. Ajithprasad 2008. Excavations at Shikarpur 2007-2008: A Costal Port and Craft Production Center of the Indus Civilization in Kutch, "
                      "India. Harappa.com, PDF, 9 pp."),
         "url_or_path": "https://www.harappa.com/sites/default/files/pdf/Excavations-at-Shikarpur-2007.pdf; data/raw/2026-10-21-town-axes/dating/shikarpur/bhan2008shikarpur.pdf",
         "sha256": "1181fbf3ae430bf9a5e93ca4e3c53a9c3e8cd151ae48ad872dee42107a87e447"},
        {"id": "iar1987-88",
         "citation": ("Archaeological Survey of India 1992. Indian Archaeology 1987-88 - A Review. New Delhi: Archaeological Survey of India. Entry 31, 'Excavation at Shikarpur "
                      "(Valmiyo Timbo), District Kutch' (Department of Archaeology, Government of Gujarat, M. H. Raval), pp. 14-15."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1987-1988.pdf; " + CEN + "IAR1987-1988-ALT.pdf",
         "sha256": "fdb3eac83e5afe34ed3b99169ef3aa0d85d1281858797ec78f32c41375954573"},
        {"id": "iar1988-89",
         "citation": ("Archaeological Survey of India 1993. Indian Archaeology 1988-89 - A Review. New Delhi: Archaeological Survey of India. Entry 21, 'Excavation at Shikarpur, "
                      "District Kutch' (Department of Archaeology, Government of Gujarat), p. 10."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1988-1989.pdf; " + CEN + "IAR1988-1989-ALT.pdf",
         "sha256": "265fccdf60788ada8945b3feefb6e7f16458b033db9e077ac46915a8fec12972"},
        {"id": "iar1989-90",
         "citation": ("Archaeological Survey of India 1994. Indian Archaeology 1989-90 - A Review. New Delhi: Archaeological Survey of India. Entry 18, 'Excavation at Shikarpur "
                      "(Valamiyo Timbo), District Kutch' (Department of Archaeology, Government of Gujarat), pp. 20-21."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1989-1990.pdf; " + CEN + "IAR1989-1990-ALT.pdf",
         "sha256": "b408f4212e23d66ea499ac828ebf14c7dee344c3251f1be32fda4bfe636e77e9"},
        {"id": "iar1990-91",
         "citation": ("Archaeological Survey of India 1995. Indian Archaeology 1990-91 - A Review. New Delhi: Archaeological Survey of India. Section VI, 'Palaeobotanical and "
                      "Pollen Analytical Investigations' (K. S. Saraswat and Chanchala, Birbal Sahni Institute of Palaeobotany), entry 2, Shikarpur, p. 103."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1990-1991.pdf; " + CEN + "IAR1990-1991-ALT.pdf",
         "sha256": "c393bd51465861988f68caf407282fedc066e14162e8aab0184f987ad5d319c9"},
        {"id": "iar2007-08",
         "citation": ("Archaeological Survey of India 2016. Indian Archaeology 2007-08 - A Review. New Delhi: Archaeological Survey of India. Entry 13, 'Excavation at Shikarpur, "
                      "District Kutchh' (Department of Archaeology and Ancient History, M. S. University of Baroda), pp. 60-61, 64."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2007-2008.pdf; data/raw/2026-10-21-town-axes/dating/shared-iar/iar2007-08.pdf",
         "sha256": "56f9a05bfa255e1f611b2a61cabbf6fb9179b5642d62deee7b3b54c862cc9a3d"},
        {"id": "iar2009-10",
         "citation": ("Archaeological Survey of India 2016. Indian Archaeology 2009-10 - A Review. New Delhi: Archaeological Survey of India. Entry 8, 'Excavations at Shikarpur, "
                      "Bhachhau Taluka, District Kachchh' (K. K. Bhan, P. Ajithprasad and Bhanu Sharma), pp. 25-29."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2009-2010.pdf; " + CEN + "IAR2009-10.pdf",
         "sha256": "16574ffcfc86cb9e635370ef4d7333d2266af61f2a80a4e486c4df26ecd36c73"},
        {"id": "iar2012-13",
         "citation": ("Archaeological Survey of India 2015. Indian Archaeology 2012-13 - A Review. New Delhi: Archaeological Survey of India. Entry 11, 'Excavations at Shikarpur, "
                      "District Kachchh' (P. Ajithprasad, K. Krishnan, K. K. Bhan and S. Pratapachandran), pp. 30-31, 33."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2012-2013.pdf; data/raw/2026-10-21-town-axes/dating/shared-iar/iar2012-13.pdf",
         "sha256": "43a3aa12807f45870a8e73f6bf9b3688938f23bccd6a344b1671e0742bf746be"},
        {"id": "joglekar2011shikarpur",
         "citation": ("Joglekar, P. P. and P. Goyal 2011. Faunal Remains from Shikarpur, a Harappan Site in Gujarat, India. Iranian Journal of Archaeological Studies 1(1): 15-25. "
                      "doi:10.22111/ijas.2011.454."),
         "url_or_path": "https://ijas.usb.ac.ir/article_454_bdcd879b499b5e2f241d124d88377b12.pdf; data/raw/2026-10-21-town-axes/dating/shikarpur/ijas2011shikarpur-fauna.pdf",
         "sha256": "1cc1d49641fbb672b3339506fb3e6c08895d0880dfc18522669b22b5f98b24c8"},
        {"id": "gadekar2014shikarpur",
         "citation": ("Gadekar, C., S. V. Rajesh and P. Ajithprasad 2014. Shikarpur lithic assemblage: New questions regarding Rohri chert blade production. Journal of Lithic "
                      "Studies 1(1): 137-149. doi:10.2218/jls.v1i1.764."),
         "url_or_path": "http://journals.ed.ac.uk/lithicstudies/article/download/764/1079; data/raw/2026-10-21-town-axes/dating/shikarpur/gadekar2014shikarpur.pdf",
         "sha256": "18dc13111f1b132a4b7df7e80a590526623c9c98ec9f4563079a904af5d9cc99"},
        {"id": "abhayan2025fish",
         "citation": ("Abhayan, G. S., P. P. Joglekar, P. Ajithprasad, S. V. Rajesh, P. Goyal, B. Chase, J. Kharakwal and P. Shirvalkar 2025. Ichthyoarchaeological perspectives "
                      "on roles of fish and red meat during Indus Civilization in Gujarat, India. Frontiers in Environmental Archaeology 4: 1517351. doi:10.3389/fearc.2025.1517351."),
         "url_or_path": "https://www.frontiersin.org/journals/environmental-archaeology/articles/10.3389/fearc.2025.1517351/full; " + CEN + "FRONTIERS2025.html",
         "sha256": "46b51550d90c6d0f46ef874ec63ef731ea726afde0a5fae003a4fd2e2fec7369"},
        {"id": "rajesh2007gujarat",
         "citation": "Rajesh S. V. and Ambika Patel 2007. Excavated Chalcolithic Sites in Gujarat: An Appraisal. Puratattva 37: 46-67.",
         "url_or_path": "https://archive.org/details/dli.ministry.29993; data/raw/2026-10-21-town-axes/dating/shared-puratattva/puratattva37-2007_text.pdf",
         "sha256": "0ed17c747fc9abf8f845ec0e68c8e352312e96937e3e30bcc757ef680b7c7164"},
        {"id": "chakraborty2019kachchh",
         "citation": ("Chakraborty, K. S. 2019. Subsistence-Based Economy and the Regional Interaction Processes of the Indus Civilization Borderland in Kachchh, Gujarat: A "
                      "Bio-Molecular Perspective. PhD thesis, Graduate Department of Anthropology, University of Toronto."),
         "url_or_path": "https://utoronto.scholaris.ca/bitstreams/e49f7f8f-d029-4cf2-8053-12a2c1389cda/download; data/raw/2026-10-21-town-axes/dating/shared-gujarat-syntheses/toronto2019kachchh.pdf",
         "sha256": "9767c8958fb94543c0b0577a34d5ea17ef7f32f9e6c55b46c649de90b485ef78"}
    ],
    "notes": (
        "Shikarpur (Valamiyo or Valmio Timbo, Bhachau taluka, Kachchh) was dug twice: by the Gujarat State Department of Archaeology under M. H. Raval in 1987-1990, published "
        "only as short notes in Indian Archaeology - A Review, and by the Department of Archaeology and Ancient History of the M. S. University of Baroda under K. K. Bhan and "
        "P. Ajithprasad from 2007-08 to at least 2012-13, published as interim reports on harappa.com and in Indian Archaeology - A Review. The Baroda team divides the 6.40 m "
        "deposit into Phase I (Classical Harappan, urban, about 3 m), Phase II (Sorath Harappan predominant, urban, 1.40-1.60 m) and Phase III (Late or Post-Urban Sorath "
        "Harappan, thin and patchy). We record two parts: the mud-brick inner fortification with the settlement inside it, which the excavators found to start with the first "
        "Harappan occupation, and an outer wall on the southern side, built later within Phase I. "
        "We found no radiocarbon, luminescence or Bayesian date for Shikarpur. The Tata Institute, Physical Research Laboratory, Birbal Sahni Institute and Pennsylvania date lists "
        "in Radiocarbon contain no Shikarpur entry, and the published Baroda reports, the faunal and lithic papers and the 2025 regional synthesis give none. The excavators cite "
        "an unpublished report, Ajithprasad, Krishnan, Bhan and Prathapchandran 2012, 'Excavations at Shikarpur 2011-2012' (report to the Archaeological Survey of India, 43 pp., "
        "cited in gadekar2014shikarpur), which we could not obtain; Indian Archaeology - A Review for 2010-11 has no Shikarpur entry and the 2011-12 volume is not on the copy site "
        "we used. We also could not open C. Gadekar's 2014 Baroda thesis, 'Lithic Blade Implements and their Role in the Harappan Chalcolithic "
        "Cultural Development in Gujarat' (Shodhganga 10603/56193), which compares Shikarpur, Bagasra, Datrana and Pithad and may give phase dates. The only calendar ranges we hold are therefore the regional "
        "bracket in abhayan2025fish and the unexplained 'circa 2,500-2,200 BC' of the 1990-91 palaeobotanical note. "
        "Some reports give the direction of walls and structures; following our method we did not record it.")
}

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)
