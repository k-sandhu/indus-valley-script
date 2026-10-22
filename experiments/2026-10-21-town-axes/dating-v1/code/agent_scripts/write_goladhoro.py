import json, pathlib, sys

OUT = pathlib.Path(sys.argv[1])
UTC = sys.argv[2]
IAR = "data/raw/2026-10-21-town-axes/dating/shared-iar/"

rc_note = ("Calibrated results only: the table gives no laboratory number, radiocarbon age, material or context, and the original publication (P. Ajithprasad 2014, "
           "'Bagasra', in D. K. Chakrabarti and Makkhan Lal (eds), History of Ancient India vol. II, Protohistoric Foundations, p. 645) was not available to us. "
           "The table footnote says 'The calibrated dates are as in the original references and not recalculated'. We include the Phase III results because Phase III "
           "overlies the Phase II deposit in which the fortification was built, so they give a minimum age for the layout.")

part = {
    "part": "whole town: the fortified enclosure in the northern half of the mound (the southern part, outside the wall, was also inhabited)",
    "layout_phase": "Phase II (Urban/Mature Harappan) of the M. S. University of Baroda sequence, Stage I of the wall",
    "what_was_built": (
        "The first season found 'a large periphery/fortification wall' on the northern edge of the mound and reported that 'This wall belonged to phase II', together with a "
        "large mud-brick structure in the central trench EQ3 built in Phase II and used in Phase III; the bricks follow the 1:2:4 ratio in two sizes, 46 x 23 x 11.5 cm and "
        "36 x 18 x 9 cm (iar1995-96 p. 17). In 1999-2000 a section across the western wall in trench Eb11 showed that 'Subsequent deposits in this trench belonged to the "
        "phase-II, which is marked by the construction of a fortification wall'. The tapering wall is 7.75 m thick at the base and 5.20 m at the extant top, 5.50 m above it; "
        "its base is six or seven courses of stone slabs, of which 'the first three courses, which are found cutting through the phase-I deposit, formed the foundation of "
        "the wall in the first stage (Stage-I) of construction', with two further courses added in Stage II; about 2.20 m of Phase II habitation deposit is associated with "
        "the wall, and shell and copper working begin 'in the beginning itself' of Phase II (iar1999-2000 p. 29). The excavators' summary is that the settlement 'probably "
        "began as a small farming village and subsequently acquired a massive fortification wall measuring 5.20m in width built in three successive stages in the northern "
        "half of the site', enclosing about 50 by 50 m with houses and craft workshops, while 'some of the population lived outside the fortified area to the south' "
        "(bhan2005goladhoro p. 1). A gateway with flanking structures is illustrated as 'The Eastern Gateway' (p. 2)."),
    "locator": "iar1995-96 p. 17; iar1997-98 pdf pp. 30-31; iar1999-2000 p. 29; bhan2005goladhoro pp. 1-2",
    "excavator_range_bce": None,
    "excavator_basis": (
        "No calendar range for Phase II appears in the excavators' reports that we read. The only dating argument in them for Phase II is cross-dating: black-slipped jar "
        "sherds of Phase II are compared with vessels 'reported from the Chalcolithic sites in Oman datable to the second half of the third millennium BC' (iar1995-96 p. 18), "
        "and Phase III pottery is compared with Rangpur IIA-B and Rojdi A-B (iar1995-96 p. 18; iar1999-2000 p. 27). The excavators' preliminary report (Sonawane et al. 2003, "
        "Man and Environment 28(2): 21-50, not obtained) ascribed 2100-1900 BCE to Phase III by comparison with Rojdi B, as quoted in kanungo2024bhagatrav (p. 61), and "
        "bhan2005goladhoro (p. 5) states that 'The occupation of the site continued in the post-urban period up to 1700 BC'."),
    "radiocarbon": [
        {"lab_no": "not given (first of two Phase III results)", "material": None, "context": "not given",
         "phase": "Phase III (Late Urban)",
         "age_bp_printed": None, "sigma_printed": None, "half_life_printed": None, "age_bp_5568": None, "sigma_5568": None,
         "calibrated_published": "68% probability: 2310-2200 BC; 95% probability: 2430-2140 BC; intercept age: 2280 BC",
         "curve": None, "source": "kanungo2024bhagatrav", "page": "61, Table 1 (continued)", "cited_via": "kanungo2024bhagatrav",
         "note": rc_note},
        {"lab_no": "not given (second of two Phase III results)", "material": None, "context": "not given",
         "phase": "Phase III (Late Urban)",
         "age_bp_printed": None, "sigma_printed": None, "half_life_printed": None, "age_bp_5568": None, "sigma_5568": None,
         "calibrated_published": "68% probability: 2460-2290 BC; 95% probability: 2470-2210 BC; intercept age: 2390-2340 BC",
         "curve": None, "source": "kanungo2024bhagatrav", "page": "61, Table 1 (continued)", "cited_via": "kanungo2024bhagatrav",
         "note": rc_note}
    ],
    "bayesian_start": None,
    "syntheses": [
        {"source": "abhayan2025fish", "page": "Table 1 and section 4.1 (online article, no page numbers)", "range_bce": [2600, 2200],
         "statement": ("A regional synthesis co-authored by P. Ajithprasad places 'BSR I and BSR II' in a Mature Harappan 'Phase I (c. 2600-2200 BCE)', BSR III in 'Phase II "
                       "(c. 2200-1900 BCE)' and BSR IV in 'Phase III (c.1900-1700 BCE)'. It dates 'The earliest occupation at Bagasra (Phase I)' to 'the early Urban Harappan "
                       "period (c. 2600 BCE)' and states that 'Phase II saw the construction of a mud-brick fortification'."),
         "disagreement": ("Puts Phase I, which the excavators' 1999-2000 report describes as dominated by local and Anarta pottery of 'early/pre-Harappan lineage', in the "
                          "early Urban Harappan; calls the wall mud-brick, where the excavation reports describe a stone-slab base with mud-brick above; the range is a regional "
                          "phase bracket, not a site date.")},
        {"source": "chase2010goladhoro", "page": "528 (abstract)", "range_bce": None,
         "statement": ("The abstract of Chase's faunal study states that 'A square fort, imposed on a settlement of livestock herders in the later third millennium BC, was shown "
                       "to have contained people who introduced a broader diet of meat and seafood'."),
         "disagreement": ("Places the building of the fort in the later third millennium BC, which is later than the c. 2600 BCE start of the block that abhayan2025fish "
                          "assigns to Phases I-II; we read only the abstract.")},
        {"source": "rajesh2007gujarat", "page": "48-49", "range_bce": None,
         "statement": ("Summarising the Baroda excavations, the authors write that 'Phase I represents the early stage of the Mature/Urban Harappan along with Anarta pottery. "
                       "Phase II demarcates the construction of a fortification', and that Phase III is marked by Sorath Harappan pottery and Phase IV is Post-Urban."),
         "disagreement": None},
        {"source": "kanungo2024bhagatrav", "page": "61", "range_bce": None,
         "statement": ("A radiocarbon paper on Bhagatrav reviews the Bagasra chronology: Sonawane et al. (2003, 49) 'ascribed 2100-1900 BCE to Phase-III of Bagasra' and "
                       "1900-1700 BCE follows for Phase IV, and 'Later on, the AMS radiocarbon dates obtained for Bagasra matched with the dates proposed on the basis of "
                       "ceramic chronology'; its Table 1 lists the calibrated Phase III and IV results from Ajithprasad 2014."),
         "disagreement": ("Its own Table 1 gives Phase III results of 2470-2140 BC at 95%, older than the 2100-1900 BCE it says they match.")}
    ],
    "conflicts": (
        "The sources agree that the wall was built in Phase II, after a Phase I occupation, but describe Phase I and the wall differently. The first season found 'Mature/Urban "
        "Harappan pottery ... all through the deposit', with Anarta pottery 'right from the early level onwards' (iar1995-96 p. 18); the 1999-2000 season found Phase I "
        "'predominated by the vessels belonging to a local ceramic tradition and the Anarta pottery of the north Gujarat region', whose forms 'indicate their early/pre-Harappan "
        "lineage' (iar1999-2000 p. 29); rajesh2007gujarat and abhayan2025fish call Phase I early Mature or Urban Harappan. The wall is 'about 5.20 m thick' and 'built of stone "
        "and mud-bricks' in iar1997-98, 5.20 m wide in three stages in bhan2005goladhoro, 7.75 m at the base and 5.20 m at the extant top on the west in iar1999-2000, and "
        "'mud-brick' in abhayan2025fish. The first season recognised three phases; Phase IV, outside the wall in the south, was added in 1997-98. No determination from Phase I "
        "or Phase II has been published in any source we found; the two Phase III results (95% ranges 2430-2140 and 2470-2210 BC) are older than the 2100-1900 BCE that the "
        "excavators had proposed for Phase III, and the c. 2600 BCE start in abhayan2025fish rests on comparison, not on a date from the site.")
}

doc = {
    "town": "gola-dhoro",
    "compiled_utc": UTC,
    "parts": [part],
    "first_occupation": {
        "phase": "Phase I",
        "range_bce": [2600, None],
        "basis": (
            "The value is the 'c. 2600 BCE' that abhayan2025fish (section 4.1) gives for 'The earliest occupation at Bagasra (Phase I)', a date by comparison, not by "
            "radiocarbon. In the excavation, Phase I is about 1.20 m of habitation debris in trench Eb11 resting on a black clayey deposit over indurated reddish-yellow gravel, "
            "with a mud-brick structure of Harappan brick ratio, probably part of a kiln or hearth, and a plastered floor; its pottery is predominantly local and Anarta "
            "(iar1999-2000 p. 29). In the first season Phase I was layers 15 to 8, about 1.30 m of clay floors, and natural soil was not reached (iar1995-96 p. 17). The "
            "excavators describe the first settlement as 'probably ... a small farming village' (bhan2005goladhoro p. 1)."),
        "locator": "iar1999-2000 p. 29; iar1995-96 p. 17; bhan2005goladhoro p. 1; abhayan2025fish section 4.1"
    },
    "sources": [
        {"id": "iar1995-96",
         "citation": ("Archaeological Survey of India 2002. Indian Archaeology 1995-96 - A Review. New Delhi: Archaeological Survey of India. Entry 15, 'Excavation at Bagasra, "
                      "District Rajkot' (V. H. Sonawane, V. S. Parekh, P. Ajithprasad, K. K. Bhan, P. C. Choudhari and A. Majumdar), pp. 16-22."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1995-1996.pdf; " + IAR + "iar1995-96.pdf",
         "sha256": "6801e5453c2622018f281fa1c4bcabf4934e07d2978ab40bc7fb53c2817eff9a"},
        {"id": "iar1997-98",
         "citation": ("Archaeological Survey of India 2003. Indian Archaeology 1997-98 - A Review. New Delhi: Archaeological Survey of India. Entry 16, 'Excavation at Bagasra, "
                      "District Rajkot' (V. H. Sonawane and others), pdf pp. 30-31 of the copy (no printed page numbers on these pages). The copy site's file named "
                      "1996-1997.pdf is the same 1997-98 volume."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1997-1998.pdf; " + IAR + "iar1997-98.pdf",
         "sha256": "26a4316a2212fe271740cdef7699efb901e9afc4965e266f8ef511a0abd9add4"},
        {"id": "iar1999-2000",
         "citation": ("Archaeological Survey of India 2005. Indian Archaeology 1999-2000 - A Review. New Delhi: Archaeological Survey of India. Entry 22, 'Excavation at Bagasra, "
                      "District Rajkot' (V. H. Sonawane, K. K. Bhan, K. Krishnan, S. Pratapachandran, A. Majumdar and P. Ajithprasad), pp. 27-30."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1999-2000.pdf; " + IAR + "iar1999-2000.pdf",
         "sha256": "abe66bf6546405c8c663ee3a2a8a7a8b03118e3b0a6b51d1d99bb793f92e09eb"},
        {"id": "bhan2005goladhoro",
         "citation": ("Bhan, K. K., V. H. Sonawane, P. Ajithprasad and S. Pratapchandran 2005. A Harappan trading and craft production centre at Gola Dhoro (Bagasra). "
                      "Antiquity 79 (304), Project Gallery, 5 pp. doi:10.15184/S2978855200904840."),
         "url_or_path": "https://doi.org/10.15184/S2978855200904840; data/raw/2026-10-21-town-axes/dating/gola-dhoro/bhan2005goladhoro.pdf",
         "sha256": "e0197bb86eef12c38b540b2a1392ff465f66622a413725356a9fd4b161760f43"},
        {"id": "chase2010goladhoro",
         "citation": ("Chase, B. 2010. Social change at the Harappan settlement of Gola Dhoro: a reading from animal bones. Antiquity 84 (324): 528-543. "
                      "doi:10.1017/S0003598X00066758. (Abstract page only; the full text is not open.)"),
         "url_or_path": "https://doi.org/10.1017/S0003598X00066758; data/raw/2026-10-21-town-axes/dating/gola-dhoro/chase2010goladhoro.html",
         "sha256": "7cc8b02190868d6b353372f4fb3b946f539aae599a7e01cb4d68edf39d5be05c"},
        {"id": "kanungo2024bhagatrav",
         "citation": ("Kanungo, A. K., R. K. Kaushal, R. Bhushan, N. Chauhan, J. S. Kharakwal and S. Ansari 2025 (online 18 December 2024). Luminescence and radiocarbon "
                      "chronology of Bhagatrav: A Sorath Harappan camp site in South Gujarat. Radiocarbon 67: 53-73. doi:10.1017/RDC.2024.119."),
         "url_or_path": "https://doi.org/10.1017/RDC.2024.119; data/raw/2026-10-21-town-axes/dating/shared-gujarat-syntheses/bhagatrav2024.pdf",
         "sha256": "aa69f2377f61d379322c3203deea65a2525afdc89ca1a18fe3f635d7418e38d0"},
        {"id": "abhayan2025fish",
         "citation": ("Abhayan, G. S., P. P. Joglekar, P. Ajithprasad, S. V. Rajesh, P. Goyal, B. Chase, J. Kharakwal and P. Shirvalkar 2025. Ichthyoarchaeological perspectives "
                      "on roles of fish and red meat during Indus Civilization in Gujarat, India. Frontiers in Environmental Archaeology 4: 1517351. doi:10.3389/fearc.2025.1517351."),
         "url_or_path": "https://www.frontiersin.org/journals/environmental-archaeology/articles/10.3389/fearc.2025.1517351/full; data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/FRONTIERS2025.html",
         "sha256": "46b51550d90c6d0f46ef874ec63ef731ea726afde0a5fae003a4fd2e2fec7369"},
        {"id": "rajesh2007gujarat",
         "citation": "Rajesh S. V. and Ambika Patel 2007. Excavated Chalcolithic Sites in Gujarat: An Appraisal. Puratattva 37: 46-67.",
         "url_or_path": "https://archive.org/details/dli.ministry.29993; data/raw/2026-10-21-town-axes/dating/shared-puratattva/puratattva37-2007_text.pdf",
         "sha256": "0ed17c747fc9abf8f845ec0e68c8e352312e96937e3e30bcc757ef680b7c7164"}
    ],
    "notes": (
        "Gola Dhoro (Bagasra, Maliya taluka, now Morbi district) was excavated in field seasons from 1995-96 to 2004-05 by the Department of Archaeology and Ancient History of "
        "the M. S. University of Baroda. Its sequence is Phase I (earliest occupation), Phase II (the fortification, seals and the height of craft production), Phase III "
        "(Sorath Harappan pottery predominant, late Urban) and Phase IV (Post-Urban, outside the wall in the south). We treat the walled enclosure as the one part with a layout "
        "phase; the excavators also report occupation south of the wall in the urban phases, but no planned layout there. "
        "The radiocarbon evidence we found is limited to calibrated Phase III and IV results quoted from Ajithprasad 2014 in kanungo2024bhagatrav; we left out the single Phase "
        "IV result (68%: 2020-1920 BC; 95%: 2120-1880 BC; intercept 1960 BC) because it postdates the layout. The Radiocarbon-journal date lists we searched contain no Bagasra "
        "entry. We could not obtain the excavators' preliminary report, Sonawane, Ajithprasad, Bhan, Krishnan, Prathapachandran, Majumdar, Patel and Menon 2003, 'Excavations at "
        "Bagasra 1996-2003: A Preliminary Report', Man and Environment 28(2): 21-50 (the Internet Archive holds only issue 28(1), which we downloaded and checked); Ajithprasad "
        "2014 in History of Ancient India vol. II; the full text of chase2010goladhoro; Bhan et al. 2004 in Journal of Interdisciplinary Studies in History and Archaeology "
        "1(1); and the season notes in Indian Archaeology - A Review for 1996-97 (the copy site's file of that name is the 1997-98 volume) and 2001-02 to 2004-05 (not on the "
        "copy site); the 1998-99 and 2000-01 volumes we downloaded have no Bagasra entry. "
        "Some reports give the direction of the walls; following our "
        "method we did not record it.")
}

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)
