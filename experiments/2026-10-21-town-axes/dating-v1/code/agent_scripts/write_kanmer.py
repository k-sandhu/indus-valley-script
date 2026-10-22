import json, pathlib, sys

OUT = pathlib.Path(sys.argv[1])
UTC = sys.argv[2]

AMS_NOTE = ("Paleo Labo AMS date from the table 'AMS radiocarbon dating of charcoal/grains of Kanmer archaeological site'. "
            "The table heads the age column 'Conventional radiocarbon age', which by definition uses the 5568-year half-life; "
            "the paper does not state the half-life or the calibration curve. age_bp_printed is the unrounded value; ")


def ams(lab, prov, d13c, raw, rawsig, rnd, rndsig, one, two, phase="not stated in the source", extra=""):
    return {
        "lab_no": lab,
        "material": "charcoal",
        "context": prov + " (trench/layer/depth as printed)",
        "phase": phase,
        "age_bp_printed": raw, "sigma_printed": rawsig, "half_life_printed": 5568,
        "age_bp_5568": raw, "sigma_5568": rawsig,
        "calibrated_published": "1 sigma: " + one + "; 2 sigma: " + two + " (cal BC)",
        "curve": None,
        "source": "pokharia2011kanmer", "page": "1837, Table 2",
        "note": AMS_NOTE + f"the rounded value is {rnd}±{rndsig}; delta 13C {d13c} per mil. "
                "kharakwal2011multicultural reprints the same values in its Table 1.2 (pp. 368-369) without phase. " + extra,
    }


rc = []
# ---- KMR I (phase before the layout) ----
rc.append({
    "lab_no": "BS-2619", "material": "wood charcoal (table title)",
    "context": "Trench Y-30, depth 930 cm, layer 19",
    "phase": "KMR Pd I",
    "age_bp_printed": 4190, "sigma_printed": 80, "half_life_printed": None,
    "age_bp_5568": 4190, "sigma_5568": 80,
    "calibrated_published": "4838-4573 cal BP; 2888-2623 BC", "curve": None,
    "source": "kharakwal2011multicultural", "page": "368, Table 1.1",
    "note": "Birbal Sahni Institute (BSIP) date. The half-life is not stated; the authors calibrate the printed age directly, "
            "which treats it as a conventional 5568-year age, so we copy it into age_bp_5568. iar2007-08 (pp. 48-49) prints the same "
            "trench, depth, layer, age, calibration and phase ('KMR I')."
})
rc.append({
    "lab_no": "BS-2619", "material": "charcoal",
    "context": "Trench Y-30, depth 930 cm, layer 20",
    "phase": "not stated in Table 1; the text (p. 1841) ties BS-2619 to the earliest, Early Harappan occupation in Y-30",
    "age_bp_printed": 4190, "sigma_printed": 80, "half_life_printed": None,
    "age_bp_5568": 4190, "sigma_5568": 80,
    "calibrated_published": "4838-4573 cal BP; 2850-2623 BC", "curve": None,
    "source": "pokharia2011kanmer", "page": "1836, Table 1; 1841",
    "note": "Second entry for BS-2619 because this source prints a different layer (20, not 19) and a different calibrated BC range "
            "(2850-2623, not 2888-2623) from kharakwal2011multicultural and iar2007-08. Half-life not stated; treated as conventional as above."
})
rc.append({
    "lab_no": "BS-3028", "material": "charcoal",
    "context": "Trench Z-30, depth 942-967 cm, layer 12",
    "phase": "KMR Pd I",
    "age_bp_printed": 4630, "sigma_printed": 90, "half_life_printed": None,
    "age_bp_5568": 4630, "sigma_5568": 90,
    "calibrated_published": "5152-5472 cal BP; 3099-3600 BC", "curve": None,
    "source": "kharakwal2011multicultural", "page": "368, Table 1.1",
    "note": "BSIP date; half-life not stated, treated as conventional because the authors calibrate it directly. "
            "pokharia2011kanmer Table 1 (p. 1836) prints the same values without a phase. With BS-3042 it is one of the dates that, in the "
            "excavators' words, 'bracket the pre urban or pre fortification deposit between 3600 and 2800 BC', which they say they 'can not interpret' (p. 368)."
})
rc.append({
    "lab_no": "BS-3042", "material": "charcoal",
    "context": "Trench Z-30, depth 900-923 cm, layer 11",
    "phase": "KMR Pd I",
    "age_bp_printed": 4750, "sigma_printed": 100, "half_life_printed": None,
    "age_bp_5568": 4750, "sigma_5568": 100,
    "calibrated_published": "5356-5578 cal BP; 3100-3600 BC", "curve": None,
    "source": "kharakwal2011multicultural", "page": "368, Table 1.1",
    "note": "BSIP date; half-life not stated, treated as conventional because the authors calibrate it directly. "
            "pokharia2011kanmer Table 1 (p. 1836) prints the same values without a phase."
})
rc.append({
    "lab_no": "PLD-16352", "material": "grain (barley, per the text p. 1842)",
    "context": "Y-30/20/9.30m (trench/layer/depth as printed)",
    "phase": "Early Harappan (KMR I), per the text p. 1842",
    "age_bp_printed": 3882, "sigma_printed": 20, "half_life_printed": 5568,
    "age_bp_5568": 3882, "sigma_5568": 20,
    "calibrated_published": "1 sigma: 2456 (25.6%) 2418, 2408 (22.9%) 2374, 2368 (17.7%) 2340, 2314 (2.1%) 2310; 2 sigma: 2461 (95.4%) 2298 (cal BC)",
    "curve": None,
    "source": "pokharia2011kanmer", "page": "1837, Table 2; 1842",
    "note": AMS_NOTE + "the rounded value is 3880±20; delta 13C -24.14±0.12 per mil. The authors date a barley grain 'from the mixture of total grains' of the "
            "Early Harappan phase and conclude that 'some of the grains from the upper layer may have percolated down' (p. 1842), so they do not take it as a date for KMR I. "
            "It comes from the same trench and layer number (Y-30, layer 20) as BS-2619 in pokharia2011kanmer Table 1."
})
# ---- KMR IIa (layout phase) ----
rc.append({
    "lab_no": "BS-2628", "material": "charcoal (per pokharia2011kanmer Table 1)",
    "context": "Trench HH-30, depth 280 cm, layer 3",
    "phase": "KMR II A",
    "age_bp_printed": 3610, "sigma_printed": 90, "half_life_printed": None,
    "age_bp_5568": 3610, "sigma_5568": 90,
    "calibrated_published": "4080-3735 cal BP; 2130-1785 BCE", "curve": None,
    "source": "iar2007-08", "page": "48, table '14C dates of Kanmer'",
    "note": "The only determination we found that the excavators assign to the layout phase. It is younger than BS-2627 (3870±100 BP, 2470-2149 BCE, "
            "trench R-21, 466 cm, layer 7), which the same table assigns to the later sub-phase KMR II B, and younger than every AMS date from the site's lower "
            "Harappan levels. pokharia2011kanmer Table 1 (p. 1836) prints the same values without a phase. Half-life not stated; treated as conventional because the authors calibrate it directly."
})
# ---- KMR II, sub-phase not stated ----
rc.append({
    "lab_no": "PLD-16354", "material": "grain (barley)",
    "context": "not stated",
    "phase": "Mature Harappan (KMR II), sub-phase not stated: the text gives it as the barley date of the phase following the Early Harappan",
    "age_bp_printed": None, "sigma_printed": None, "half_life_printed": None,
    "age_bp_5568": None, "sigma_5568": None,
    "calibrated_published": "2469 BC (90.0%) 2335 BC", "curve": None,
    "source": "pokharia2011kanmer", "page": "1842",
    "note": "Printed only in the running text, 'barley (AMS date: PLD-16354-2469 BC (90.0%) 2335 BC)'; it is not in Table 2, and no conventional age, error or context is given."
})
# ---- AMS dates with no stated phase, from trenches outside the north-eastern and south-eastern areas ----
rc.append(ams("PLD-14751", "Z-30/12/9.72m", "-22.76±0.13", 3984, 24, 3985, 25,
              "2564 (37.9%) 2534, 2494 (30.3%) 2472", "2571 (56.2%) 2513, 2504 (39.2%) 2466",
              extra="Layer 12 of trench Z-30 is also the layer of BS-3028, which kharakwal2011multicultural assigns to KMR I; the AMS table itself gives no phase."))
rc.append(ams("PLD-14752", "Z-30/10/9.04m", "-24.76±0.13", 3935, 24, 3935, 25,
              "2476 (35.6%) 2437, 2421 (30.3%) 2404, 2379 (20.2%) 2349", "2560 (3.2%) 2536, 2491 (92.2%) 2341",
              extra="The printed 1-sigma probabilities add to 86.1%, not 68.2%; we checked the page image and record them as printed."))
rc.append(ams("PLD-14754", "Q-28/11/8.00m", "-25.92±0.29", 3896, 25, 3895, 25,
              "2462 (42.4%) 2398, 2384 (25.8%) 2346", "2467 (95.4%) 2299"))
rc.append(ams("PLD-14755", "Q-28/12/8.20m", "-26.07±0.14", 3866, 25, 3865, 25,
              "2455 (16.2%) 2420, 2406 (15.5%) 2377, 2350 (36.5%) 2291", "2464 (90.4%) 2281, 2250 (3.9%) 2231, 2219 (1.1%) 2212"))
rc.append(ams("PLD-14756", "Z-28/12/8.91m", "-25.45±0.20", 3873, 24, 3875, 25,
              "2455 (19.0%) 2419, 2406 (17.3%) 2377, 2350 (31.9%) 2296", "2465 (94.9%) 2286, 2247 (0.5%) 2243"))
rc.append(ams("PLD-14757", "AA-28/9/788", "-11.41±0.22", 3809, 23, 3810, 25,
              "2286 (68.2%) 2205", "2337 (2.2%) 2323, 2308 (86.7%) 2196, 2172 (6.5%) 2146",
              extra="Depth printed as '788' without a unit. The delta 13C of -11.41 per mil is unusual for wood charcoal; the source does not comment."))
rc.append(ams("PLD-14758", "Q-28/13/8.45m", "-21.25±0.18", 3892, 24, 3890, 25,
              "2459 (42.1%) 2391, 2385 (26.1%) 2346", "2466 (95.4%) 2298"))
rc.append(ams("PLD-14759", "Q-28/11/8.09m", "-25.29±0.14", 3898, 22, 3900, 20,
              "2462 (42.8%) 2402, 2382 (25.4%) 2348", "2468 (87.9%) 2335, 2324 (7.5%) 2301"))
rc.append(ams("PLD-14760", "AA-28/8/7.11m", "-22.33±0.15", 3875, 23, 3875, 25,
              "2455 (20.0%) 2419, 2406 (17.7%) 2377, 2351 (30.5%) 2298", "2464 (95.4%) 2288"))
rc.append(ams("PLD-14761", "Q-28/10/8.03m", "-25.68±0.17", 3886, 27, 3885, 25,
              "2457 (68.2%) 2342", "2466 (95.4%) 2292"))
rc.append(ams("PLD-14762", "A-28/12/9.24", "-24.22±0.20", 3814, 24, 3815, 25,
              "2288 (18.5%) 2267, 2260 (49.7%) 2206", "2344 (90.6%) 2196, 2172 (4.8%) 2146",
              extra="Trench printed as 'A-28' and depth without a unit."))

part = {
    "part": "whole town: the fortified main mound (the excavators found no lower town)",
    "layout_phase": "KMR IIa, the first sub-phase of KMR II (Mature Harappan, 'urban phase'); IAR 2006-07 calls the same unit Period II",
    "what_was_built": (
        "The excavators assign the fortification and the first planned houses to KMR IIa: 'The remains of KMR II, overlying KMR I, was marked by appearance of a massive "
        "fortification, planned residential complexes, characteristic Harappan pottery, seals...' (p. 360) and 'This fortification stratigraphically belongs to KMR IIa' (p. 361). "
        "The wall has a core of brown or yellowish sandy clay, sometimes laid as bricks of the same material, faced on both sides with large semi-dressed blocks of local sandstone "
        "and other hard rock, some of the lower ones 2 m long, 50 cm broad and 40 cm thick (p. 361). The northern and eastern arms are about 18 m wide at 2.20 m below the highest "
        "point and an estimated 20 m at the base, the western arm about 15 m; the space inside measures 76 m by 75 m, about 5,852 square metres (p. 362). In a cutting against the "
        "inner face of the western arm the wall overlies the KMR I 'pre-fortification' deposit and stands 5.70 m high in 29 courses, of which all but the lowest four were rebuilt; "
        "the excavators read this as serious damage 'soon after its construction' and take the addition or veneer built against the outer face on three sides as the repair "
        "(pp. 361-362). IAR 2006-07 (p. 29) reports that at the north-eastern corner both the original wall and the addition were 'raised right on the natural soil', and that "
        "the outer arm at the north-western corner rests on bedrock. Inside the wall, the first major structural phase in the south-central area consists of two complexes of rooms "
        "of semi-dressed stone bound with yellowish sandy clay (pila lilva) round an open space, with one room of 4.80 by 3.00 m and a platform at a house entrance; the excavators "
        "take their regular layout as evidence of 'a planned settlement inside' (pp. 363-364). The wall was later remodelled: at the end of KMR IIb the northern arm was narrowed "
        "by moving its inner face about 10 m outward, which IAR 2007-08 (p. 44) calls the third major structural phase of the fort wall, and the KMR III people finally built "
        "houses on top of the rampart (p. 365)."),
    "locator": "kharakwal2011multicultural pp. 360-365; iar2006-07 pp. 29-30; iar2007-08 pp. 44-45",
    "excavator_range_bce": [2500, 2000],
    "excavator_basis": (
        "Radiocarbon. The excavators write that most of 'more than a dozen AMS dates ... demonstrate consistency for the urban phase remains of Harappans at Kanmer and provide "
        "a bracket of around 500 years i.e., between 2500 and 2000 BC' (kharakwal2011multicultural p. 368). The range covers the whole urban phase KMR II (IIa and IIb); no "
        "separate range is published for KMR IIa. The same team, in pokharia2011kanmer (p. 1835), gives 'the Early (2850-2500 BC) and its subsequent development in the Mature "
        "(2500-2100 BC) and Late (2100-1700 BC) phases', also on the radiocarbon series."),
    "radiocarbon": rc,
    "bayesian_start": None,
    "syntheses": [
        {"source": "uesugi2012kanmer", "page": "299, 322", "range_bce": None,
         "statement": ("The pottery chapter of the final report finds that 'Periods I - III belong to the Mature Harappan period' (p. 299) and concludes that, 'taking the typological "
                       "features of ceramics and AMS dates from the excavations into consideration', 'Periods I and Period IIA may date to the early part of the Mature Harappan period "
                       "and Periods IIB and III can be assigned to the later part' (p. 322). It compares Period I and part of Period II with Surkotada IA-IB and Dholavira Stages III-V."),
         "disagreement": ("Places Period I, which the excavators' other reports call Early Harappan and pre-fortification, inside the Mature Harappan together with the layout phase "
                          "IIA, so the interval between first occupation and the building of the wall shrinks; it gives no calendar years.")},
        {"source": "abhayan2025fish", "page": "Table 1 and section 4.2 (online article, no page numbers)", "range_bce": [2600, 2200],
         "statement": ("A regional synthesis co-authored by Kharakwal places 'KMR I and KMR IIA' together in a Mature Harappan 'Phase I (c. 2600-2200 BCE)', and KMR IIB and KMR III in "
                       "'Phase II (c. 2200-1900 BCE)'. It describes KMR I as 'Early Harappan/Early Mature Harappan ... a pre-fortification phase' and KMR II as the phase marked by "
                       "'a fortification wall'."),
         "disagreement": ("Starts the block that contains the layout phase about a century before the excavators' 2500 BC and closes it at 2200 BCE; the range is a regional phase "
                          "bracket assigned by comparison, not a site-specific date.")},
        {"source": "rajesh2007gujarat", "page": "53", "range_bce": None,
         "statement": ("A survey of excavated Chalcolithic sites in Gujarat describes Kanmer, from IAR 1985-86 and Kharakwal et al. 2005, as a fortified site with 'two divisions', a "
                       "higher and larger eastern upper town and a low-lying lower town in which 'No defense wall is visible', with Mature and Late Harappan pottery. It gives no date."),
         "disagreement": ("Reports a lower town, whereas the excavators found that 'Outside the rampart area no other settlement like a lower town could be located', only a very thin "
                          "deposit like KMR III east of the main mound (kharakwal2011multicultural p. 374).")}
    ],
    "conflicts": (
        "The sources agree that the wall and the planned houses belong to KMR IIa and that KMR I lies below the wall, but they disagree on dates and labels. "
        "(1) The excavators' range for the urban phase is 2500-2000 BC in kharakwal2011multicultural (p. 368) and 2500-2100 BC for the 'Mature' phase in pokharia2011kanmer (p. 1835). "
        "(2) The only date assigned to KMR IIa, BS-2628 (3610±90 BP, 2130-1785 BCE, from 280 cm depth), is younger than the KMR IIb date BS-2627 and than all AMS dates from the "
        "lower Harappan levels, which fall between 3984 and 3809 BP (about 2570-2150 cal BC as published); it cannot mark the start of the layout. "
        "(3) For KMR I, three BSIP dates (BS-2619, BS-3028, BS-3042) range from 4190 to 4750 BP, which the excavators publish as a 3600-2800 BC bracket but say they 'can not "
        "interpret', while on the same page they write that 'there are no dates available' for the pre-fortification phase; AMS dates from the same trenches (PLD-14751 in Z-30 "
        "layer 12, PLD-16352 in Y-30 layer 20) are 3984 and 3882 BP, close to the urban-phase series. "
        "(4) BS-2619 is printed from layer 19 with 2888-2623 BC in kharakwal2011multicultural and iar2007-08, and from layer 20 with 2850-2623 BC in pokharia2011kanmer. "
        "(5) KMR I is 'Early Harappan' in the excavation reports but 'Mature Harappan' in the final report's pottery chapter (uesugi2012kanmer). "
        "(6) A lower town is reported in rajesh2007gujarat but not found by the excavators.")
}

doc = {
    "town": "kanmer",
    "compiled_utc": UTC,
    "parts": [part],
    "first_occupation": {
        "phase": "KMR I (Period I), called Early Harappan and 'pre fortification' by the excavators",
        "range_bce": [2850, 2500],
        "basis": (
            "The range is the excavators' 'Early (2850-2500 BC)' phase in pokharia2011kanmer (p. 1835), which they base on ceramics ('Amri wares') and the radiocarbon date BS-2619 "
            "(p. 1841). KMR I is a deposit about 40-45 cm thick resting on bedrock in the central part of the mound and on a thin layer of fine sand (15 cm of virgin soil in "
            "pokharia2011kanmer p. 1834) in the west, with bichrome and cream-slipped red ware like the Anarta pottery of North Gujarat and without characteristic Harappan types "
            "(kharakwal2011multicultural p. 359). The excavators add that their KMR I charcoal comes only from the upper horizons, so the dates 'do not reveal the beginning of the "
            "settlement', and on comparison with North Gujarat, Padri and Amri material they suggest that 'the beginning of rural folks at Kanmer may be another 100 to 200 years "
            "older than the beginning of urban phase'; three BSIP dates 'bracket the pre urban or pre fortification deposit between 3600 and 2800 BC', which they do not interpret "
            "(kharakwal2011multicultural p. 368)."),
        "locator": "kharakwal2011multicultural pp. 359, 368; pokharia2011kanmer pp. 1834-1835, 1841; iar2006-07 p. 30"
    },
    "sources": [
        {"id": "kharakwal2011multicultural",
         "citation": ("Kharakwal, J. S., Y. S. Rawat, T. Osada, L. C. Patel, H. Seth, R. Meena, S. Meena, K. P. Singh and A. Hussain 2011. Kanmer: A Multicultural Site in Kachchh, "
                      "Gujarat, India. In T. Uno (ed.), Changing Perceptions of Japan in South Asia in the New Asian Era: The State of Japanese Studies in India and Other SAARC "
                      "Countries (International Symposium in India 2009), pp. 355-376. Kyoto: International Research Center for Japanese Studies. DOI 10.15055/00001253."),
         "url_or_path": "https://nichibun.repo.nii.ac.jp/record/1259/files/symp_016__357__355_376__357_378.pdf; data/raw/2026-10-21-town-axes/dating/kanmer/kharakwal2011multicultural.pdf",
         "sha256": "bac2021f4abebafe89757bfe4fa4d571401ea544e1ba5dbdba7289f5bfded435"},
        {"id": "pokharia2011kanmer",
         "citation": ("Pokharia, A. K., J. S. Kharakwal, R. S. Rawat [sic, for Y. S. Rawat], T. Osada, C. M. Nautiyal and A. Srivastava 2011. Archaeobotany and archaeology at Kanmer, "
                      "a Harappan site in Kachchh, Gujarat: evidence for adaptation in response to climatic variability. Current Science 100(12): 1833-1846."),
         "url_or_path": "https://www.currentscience.ac.in/Volumes/100/12/1833.pdf; data/raw/2026-10-21-town-axes/dating/kanmer/pokharia2011kanmer.pdf",
         "sha256": "3d11c35676e8f3849ccea51485693b66afb77d22618f2cd1fda97930818f1931"},
        {"id": "uesugi2012kanmer",
         "citation": ("Uesugi, A. and S. Meena 2012. Chapter 6: Pottery. In J. S. Kharakwal, Y. S. Rawat and T. Osada (eds), Excavation at Kanmer 2005-06 - 2008-09: Kanmer "
                      "Archaeological Research Project, an Indo-Japanese Collaboration, pp. 219-480. Kyoto: Indus Project, Research Institute for Humanity and Nature; Gandhinagar: "
                      "Gujarat State Department of Archaeology; Udaipur: Institute of Rajasthan Studies. ISBN 978-4-902325-72-0. (Internet Archive item holding this chapter only.)"),
         "url_or_path": "https://archive.org/details/excavationsatkanmer200509ch6auesugismeena_648_B; data/raw/2026-10-21-town-axes/dating/kanmer/kanmer2012ch6-uesugi-meena.pdf",
         "sha256": "91d415433991909152f7497c8834af021608d925e48199f416fe77ad321ef741"},
        {"id": "iar2006-07",
         "citation": ("Archaeological Survey of India 2016. Indian Archaeology 2006-07 - A Review. New Delhi: Archaeological Survey of India. Entry 14, 'Excavation at Kanmer, "
                      "District Kachchh' (J. S. Kharakwal, Y. S. Rawat and T. Osada), pp. 29-31."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2006-2007.pdf; data/raw/2026-10-21-town-axes/dating/shared-iar/iar2006-07.pdf",
         "sha256": "778661f0729b894235568ec4630c51303cb4b587d156c6ea67dd926d2404100c"},
        {"id": "iar2007-08",
         "citation": ("Archaeological Survey of India 2016. Indian Archaeology 2007-08 - A Review. New Delhi: Archaeological Survey of India. Entry 11, 'Excavation at Kanmer, "
                      "District Kachchh' (J. S. Kharakwal, Y. S. Rawat and T. Osada), pp. 44-49, with the table '14C dates of Kanmer', pp. 48-49."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2007-2008.pdf; data/raw/2026-10-21-town-axes/dating/shared-iar/iar2007-08.pdf",
         "sha256": "56f9a05bfa255e1f611b2a61cabbf6fb9179b5642d62deee7b3b54c862cc9a3d"},
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
        "Kanmer (Bakar Kot, Rapar taluka, Kachchh) was excavated in seasons from 2005-06 to 2009-10 (the final report covers 2005-06 to 2008-09) by the Institute of Rajasthan Studies, the Gujarat State Department of Archaeology and the "
        "Indus Project of the Research Institute for Humanity and Nature. The excavators divide the deposit into KMR I (Early Harappan, pre-fortification), KMR II (urban, "
        "subdivided into IIa and IIb), KMR III (Late Harappan), KMR IV (Historic) and KMR V (Medieval). We treat the fortified mound as a single part because the excavators "
        "found no lower town. Our main witnesses are the excavators' 2011 synthesis (kharakwal2011multicultural), their Current Science paper with the full radiocarbon tables "
        "(pokharia2011kanmer) and the season reports in Indian Archaeology - A Review for 2006-07 and 2007-08; the 2007-08 report supplies the only per-sample phase attributions "
        "for the Birbal Sahni Institute dates. "
        "The radiocarbon list holds the dates the sources assign to KMR I and KMR IIa, the KMR II grain date PLD-16354, and the AMS charcoal dates whose phase is not stated, from "
        "trenches outside the north-eastern and south-eastern areas. We left out four AMS dates from the north-eastern area (PLD-14748, AA-17/6/3.63m, 3782±26 BP) and the "
        "south-eastern area (PLD-14749 and PLD-14750, FF-29/3/3.85m, 3751±27 and 3769±24 BP; PLD-14753, EE-30/4/4.58, 3682±24 BP), because the final report says only Periods "
        "IIB-V were excavated in those areas (uesugi2012kanmer p. 291). We also left out the KMR II B date BS-2627 (R-21, 466 cm, layer 7, 3870±100 BP, 2470-2149 BCE), the "
        "KMR IV and V dates BS-2618 and BS-2692 (iar2007-08 p. 49), two Historic-period rice dates (PLD-16351, PLD-16353), and four further BSIP dates that pokharia2011kanmer "
        "(p. 1836) prints without a phase from upper layers: BS-2685 (Y-30, 307 cm, layer 8, 4200±120 BP), BS-3027 (Z-18, 395 cm, layer 4, 4660±110 BP), BS-2699 (HH-20, "
        "529 cm, layer 4, 4720±180 BP) and BS-2698 (R-20, 320 cm, layer 2, 4290±80 BP). These upper-layer ages are as old as or older than the KMR I dates, which suggests that "
        "old or reworked charcoal is common in the BSIP series. None of the sources states the half-life of the BSIP ages or the calibration curve used for any date. "
        "We sought and could not obtain: Goyal, Pokharia, Kharakwal, Joglekar, Rawat and Osada 2013, 'Subsistence System, Paleoecology, and 14C Chronology at Kanmer, a Harappan "
        "Site in Gujarat, India', Radiocarbon 55(1): 141-150 (closed on Cambridge Core; the open Arizona archive copy sits behind an automated bot check that we did not pass; we "
        "saved only the abstract page at data/raw/2026-10-21-town-axes/dating/kanmer/goyal2013kanmer.html); the final report's excavation and chronology chapters (only "
        "chapter 6 is on the Internet Archive); Kharakwal, Rawat and Osada 2009, 'Excavation at Kanmer: A Harappan Site in Kachchh, Gujarat', Puratattva 39: 147-164; their RIHN "
        "Occasional Papers 2 (2007), 5 (2008) and 10 (2011); and Indian Archaeology - A Review for 2005-06 and 2008-09, which the copy site we used does not hold. Possehl's "
        "radiocarbon compilations of 1989, 1999 and 2002 predate the excavation. No published Bayesian model of the Kanmer sequence was found. "
        "Some sources state the direction of the fort wall and houses; following our method we did not record it.")
}

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)
