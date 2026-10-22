import json, sys

OUTDIR = sys.argv[1]
R = "data/raw/2026-10-21-town-axes/dating/"
CN = "data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/"


def rc(lab, material, context, phase, age, sig, src, page, cal=None, curve=None, hl=None, note=None):
    d = {"lab_no": lab, "material": material, "context": context, "phase": phase,
         "age_bp_printed": age, "sigma_printed": sig, "half_life_printed": hl,
         "age_bp_5568": (age if (hl == 5568 and age is not None) else (round(age / 1.03) if (hl == 5730 and age is not None) else None)),
         "sigma_5568": (sig if (hl == 5568 and sig is not None) else (round(sig / 1.03) if (hl == 5730 and sig is not None) else None)),
         "calibrated_published": cal, "curve": curve, "source": src, "page": page}
    if note:
        d["note"] = note
    return d


def dump(name, data):
    with open(OUTDIR + "/" + name + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("wrote", name)

# ---------------------------------------------------------------- FARMANA
PLD_SAMPLE = {
    "PLD-9491": ("07-009", "Tr. 03", "carbonized wood"), "PLD-9492": ("07-010", "Tr. 03", "carbonized wood"),
    "PLD-9493": ("07-011", "Tr. 03", "carbonized wood"), "PLD-12424": ("08-003", "Tr. 1A3 / Pit no. 1", "carbonized wood"),
    "PLD-12425": ("08-004", "Tr. 1C1 & 1C2", "carbonized wood"), "PLD-15048": ("09-018", "Trench 1D5-SW", "carbonized wood"),
    "PLD-15049": ("09-019", "Trench 1D5-SW", "carbonized wood"), "PLD-15050": ("09-020", "Trench 1D5", "carbonized wood"),
    "PLD-15051": ("09-021", "Trench 1D5", "carbonized wood"), "PLD-15052": ("09-022", "Trench 1D5", "carbonized wood"),
    "PLD-15054": ("09-024", "Trench 1D5", "carbonized wood"), "PLD-15056": ("09-026", "Trench 2D9-SE", "carbonized wood"),
    "PLD-15057": ("09-027", "Trench 2XD3-SW", "charred material"), "PLD-16340": ("10-001", "Trench 1C11", "carbonized wood"),
    "PLD-16341": ("10-002", "Trench 1C11", "carbonized wood"), "PLD-16342": ("10-003", "Trench 1C11", "carbonized wood"),
    "PLD-16343": ("10-004", "Trench 1C11", "carbonized wood"), "PLD-16344": ("10-005", "Trench 1C11", "carbonized wood"),
    "PLD-16348": ("10-009", "Trench 1C11", "carbonized wood"), "PLD-16349": ("10-010", "Trench 1C11", "carbonized wood"),
    "PLD-16350": ("10-011", "Trench 2D9", "carbonized wood"),
}
# (lab, season/area/trench as printed in Table 13.2, phase no, d13C, unrounded age, unrounded sigma, rounded age, rounded sigma, 1 sigma, 2 sigma, page)
PLD = [
    ("PLD-15051", "2008-09 Central Area Tr. 1D5", 2, "-25.35±0.22", 3923, 23, 3925, 25, "2471BC(29.9%)2436BC, 2421BC(14.3%)2404BC, 2379BC(24.0%)2349BC", "2476BC(93.4%)2338BC, 2322BC(2.0%)2309BC", "p. 833"),
    ("PLD-15052", "2008-09 Central Area Tr. 1D5", 2, "-27.66±0.11", 3975, 24, 3975, 25, "2561BC(32.5%)2536BC, 2492BC(35.7%)2469BC", "2571BC(50.3%)2513BC, 2503BC(45.1%)2462BC", "p. 833"),
    ("PLD-15054", "2008-09 Central Area Tr. 1D5", 2, "-25.56±0.11", 3903, 23, 3905, 25, "2464BC(43.1%)2401BC, 2382BC(25.1%)2348BC", "2469BC(89.1%)2335BC, 2324BC(6.3%)2301BC", "p. 833"),
    ("PLD-15048", "2008-09 Central Area Tr. 1D5", 3, "-27.24±0.11", 3901, 23, 3900, 25, "2463BC(43.0%)2401BC, 2382BC(25.2%)2348BC", "2469BC(88.3%)2335BC, 2324BC(7.1%)2301BC", "p. 833"),
    ("PLD-15049", "2008-09 Central Area Tr. 1D5", 3, "-26.57±0.11", 3903, 26, 3905, 25, "2464BC(43.3%)2401BC, 2382BC(24.9%)2348BC", "2470BC(86.9%)2332BC, 2326BC(8.5%)2299BC", "p. 833"),
    ("PLD-15050", "2008-09 Central Area Tr. 1D5", 3, "-26.20±0.12", 3903, 23, 3905, 25, "2464BC(43.1%)2401BC, 2382BC(25.1%)2348BC", "2469BC(89.1%)2335BC, 2324BC(6.3%)2301BC", "p. 833"),
    ("PLD-16340", "2008-09 Central Area Tr. 1C11", 1, "-24.19±0.12", 3851, 20, 3850, 20, "2401BC(8.9%)2382BC, 2348BC(50.2%)2283BC, 2249BC(8.0%)2233BC, 2217BC(1.0%)2215BC", "2459BC(10.4%)2417BC, 2410BC(68.8%)2273BC, 2256BC(16.2%)2207BC", "p. 833"),
    ("PLD-16341", "2008-09 Central Area Tr. 1C11", 1, "-24.15±0.10", 3880, 20, 3880, 20, "2456BC(24.3%)2419BC, 2408BC(21.8%)2375BC, 2368BC(2.8%)2363BC, 2354BC(10.6%)2337BC, 2323BC(8.7%)2308BC", "2461BC(95.4%)2296BC", "p. 833"),
    ("PLD-16342", "2008-09 Central Area Tr. 1C11", 1, "-25.06±0.12", 3884, 20, 3885, 20, "2457BC(25.7%)2417BC, 2410BC(42.5%)2341BC", "2462BC(95.4%)2299BC", "p. 833"),
    ("PLD-16343", "2008-09 Central Area Tr. 1C11", 1, "-14.75±0.14", 3939, 22, 3940, 20, "2480BC(37.4%)2452BC, 2443BC(1.3%)2440BC, 2420BC(11.3%)2405BC, 2378BC(18.2%)2350BC", "2560BC(4.2%)2536BC, 2491BC(91.2%)2344BC", "p. 833"),
    ("PLD-16344", "2008-09 Central Area Tr. 1C11", 1, "-24.79±0.15", 3893, 20, 3895, 20, "2459BC(41.8%)2398BC, 2384BC(26.4%)2346BC", "2466BC(85.9%)2332BC, 2326BC(9.5%)2299BC", "p. 833"),
    ("PLD-16349", "2008-09 Central Area Tr. 1C11", 1, "-27.89±0.12", 3903, 21, 3905, 20, "2463BC(42.3%)2402BC, 2382BC(25.9%)2348BC", "2470BC(90.5%)2335BC, 2324BC(4.9%)2307BC", "p. 833"),
    ("PLD-16348", "2008-09 Central Area Tr. 1C11", 2, "-27.36±0.12", 3926, 20, 3925, 20, "2472BC(25.1%)2452BC, 2444BC(2.9%)2440BC, 2420BC(15.0%)2405BC, 2378BC(25.2%)2350BC", "2477BC(95.4%)2342BC", "p. 833"),
    ("PLD-12424", "2007-08 Central Area Tr. 1A3/Pit 1", 5, "-27.34±0.22", 3860, 23, 3860, 25, "2453BC(3.3%)2444BC, 2438BC(7.9%)2420BC, 2405BC(14.4%)2378BC, 2350BC(42.6%)2287BC", "2461BC(87.8%)2280BC, 2251BC(5.7%)2230BC, 2220BC(1.9%)2211BC", "p. 833"),
    ("PLD-12425", "2007-08 Central Area Tr. 1C1-1C2", 5, "-25.65±0.22", 3845, 22, 3845, 20, "2396BC(4.0%)2385BC, 2346BC(46.1%)2278BC, 2251BC(12.9%)2229BC, 2221BC(5.2%)2210BC", "2458BC(8.0%)2418BC, 2407BC(9.9%)2376BC, 2351BC(77.5%)2205BC", "p. 833"),
    ("PLD-15057", "2008-09 East Area Tr. 2XD3", 4, "-14.73±0.12", 4034, 23, 4035, 25, "2579BC(18.6%)2561BC, 2536BC(49.6%)2492BC", "2621BC(95.4%)2476BC", "p. 833"),
    ("PLD-15056", "2008-09 North Ex. Tr. 2D9", 1, "-25.98±0.11", 3944, 23, 3945, 25, "2547BC(1.2%)2544BC, 2489BC(44.7%)2455BC, 2419BC(8.3%)2407BC, 2376BC(14.0%)2351BC", "2564BC(9.7%)2533BC, 2495BC(68.2%)2395BC, 2385BC(17.5%)2346BC", "p. 834"),
    ("PLD-16350", "2008-09 North Ex. Tr. 2D9", 2, "-24.46±0.13", 3868, 20, 3870, 20, "2449BC(1.2%)2446BC, 2436BC(9.3%)2420BC, 2405BC(17.1%)2378BC, 2350BC(40.6%)2293BC", "2463BC(94.9%)2286BC, 2247BC(0.5%)2244BC", "p. 834"),
    ("PLD-9491", "2006-07 North Area Tr. 3", 3, "-28.16±0.28", 3928, 34, 3930, 35, "2475BC(46.2%)2400BC, 2382BC(22.0%)2347BC", "2560BC(3.7%)2536BC, 2492BC(91.7%)2298BC", "p. 834"),
    ("PLD-9492", "2006-07 North Area Tr. 3", 3, "-26.48±0.27", 3871, 34, 3870, 35, "2456BC(19.2%)2419BC, 2407BC(17.1%)2376BC, 2351BC(31.9%)2294BC", "2467BC(88.3%)2278BC, 2251BC(5.0%)2229BC, 2221BC(2.1%)2210BC", "p. 834"),
    ("PLD-9493", "2006-07 North Area Tr. 3", 2, "-25.14±0.19", 3938, 34, 3940, 35, "2488BC(35.8%)2431BC, 2425BC(13.3%)2401BC, 2381BC(19.1%)2348BC", "2566BC(9.7%)2525BC, 2497BC(82.1%)2335BC, 2324BC(3.6%)2301BC", "p. 834"),
]
far_rc = []
for lab, ctx, ph, d13, ua, us, ra, rs, s1, s2, pg in PLD:
    smp, tr, mat = PLD_SAMPLE[lab]
    far_rc.append(rc(lab, mat, "%s (sample no. %s, %s in Table 13.1)" % (ctx, smp, tr), "Harappan, Phase %d" % ph, ra, rs,
                     "paleolabo2011farmana", "%s, Table 13.2 (samples: p. 832, Table 13.1)" % pg,
                     cal="1σ: %s; 2σ: %s" % (s1, s2), curve="IntCal09 (OxCal 4.1)", hl=5568,
                     note=("Printed conventional age (rounded) with the unrounded value %d ± %d BP and δ13C %s‰. 'Phase %d' is "
                           "a stratigraphic phase of the index trenches (Phases 1 to 5, bottom to top) used in the AMS and pottery chapters; "
                           "the report does not say which phases make up Period IIA and which Period IIB." % (ua, us, d13, ph))))

farmana = {
  "town": "farmana",
  "compiled_utc": "2026-10-21T05:40:00Z",
  "parts": [
    {
      "part": "settlement area (Locality 1 of the main mound; Central, East, North and Northwest Areas)",
      "layout_phase": "Period IIA (Mature Harappan), Structural Phase-1, in the final report of 2011; the 2008 interim report (Occasional Paper 6) assigned the exposed street plan to Structural Phase II, 'Late Period II'",
      "what_was_built": ("A planned Mature Harappan settlement of large mud-brick structure complexes arranged along a main street, smaller streets "
                         "and lanes, laid out as a parallelogram. The final report states that 'the plan of the Mature Harappan settlement at Farmana "
                         "appears to have been established during Period-IIA', with 'a main street, small streets and lanes, and massive structural "
                         "complexes neatly arranged along their margins', and that the pattern 'was established during Period-IIA and continued in IIB "
                         "without any change' (Shinde et al. 2011: 45); 'elaborate remains of well-planned mud and burnt-brick structural complexes, "
                         "streets, rectangular fire places and storage areas appear at the beginning of Period-IIA' (p. 40). The fully exposed street "
                         "and blocks, however, are described in the Period IIB section: Main Street, 3.60 to 4 m wide and traced for 28 m with "
                         "bullock-cart ruts, Lane no. 1 and Structure Complexes 2, 3 and 4 (pp. 97-153); Structure Complex 2 'lines up with Structure "
                         "No. 1, which is associated with an early construction phase' (p. 97). All structures are of mud brick in the ratio 1:2:4, "
                         "with burnt brick for bathing platforms and drains (p. 45). The site was levelled for agriculture, so only two or three basal "
                         "courses survive (Shinde et al. 2008: 24)."),
      "locator": "shinde2011farmana pp. 40, 45, 97, 103; shinde2008farmana pp. 15, 22-24",
      "excavator_range_bce": [2600, 2400],
      "excavator_basis": ("Cross-dating. The final report dates Period IIA to 2600-2400 BC, IIB to 2400-2200 BC and IIC to 2200-2000 BC and states that "
                          "'no radio carbon or AMS dates are yet available', so the ranges rest on 'the cultural materials identified at the site as "
                          "well as comparative analysis' with other sites (Shinde et al. 2011: 39); the planned town emerged 'in Period-II, around 2600 "
                          "BC' (p. 40). The 2008 interim report had dated the Mature Harappan phase 'tentatively ... to between 2500-2100 BCE on the "
                          "basis of seal and sealings and ceramic assemblages', the planned town to 'around 2500 BCE' (Shinde et al. 2008: 15), and the "
                          "early and late structural phases to c. 2500-2300 and c. 2300-2000 BCE (p. 22)."),
      "radiocarbon": far_rc,
      "bayesian_start": None,
      "syntheses": [
        {"source": "uesugi2011farmana", "page": "p. 254", "range_bce": None,
         "statement": ("The pottery specialist of the same project reads 'the 13 AMS 14C dates which point to the Harappan period' as ranging 'from "
                       "2536 BC (49.6%) 2492 BC (1 σ) to 2346 BC (46.1%) 2278 BC (1σ)', so that 'the occupation in the excavated area at "
                       "Farmana can be included in the early part of the entire Harappan period (2600 - 1900 BC)' and 'roughly corresponds to Periods "
                       "3A and 3B' of Harappa; he finds no clear change in the ceramic assemblage through Phases 1 to 5."),
         "disagreement": ("The excavator's chapters say no radiocarbon dates were available and divide the occupation into Period I (Early Harappan) "
                          "and Periods IIA-IIB with cross-dated ranges; the AMS dates span only about 2600-2200 BC at two sigma.")},
        {"source": "osada2011farmana", "page": "p. 839", "range_bce": None,
         "statement": ("The project leader's summary states that 'while Prof. Shinde places the earliest levels to the ‘Early Harappan period’ "
                       "based on his observations, the artefacts, especially pottery coupled with AMS dates from the lower levels point to the "
                       "‘Mature’ Harappan period occupation', while allowing that occupation may begin earlier."),
         "disagreement": "Disputes the excavator's Early Harappan Period I for the lowest excavated levels."},
        {"source": "weber2011farmana", "page": "p. 813", "range_bce": [2600, 2200],
         "statement": ("'Based on the stratrigraphy, ceramics and the carbon (AMS) dates, the site was occupied between 2600 and 2200 BCE', 'only "
                       "during the Mature Harappan Period', for a relatively short time."),
         "disagreement": "Leaves no room for the excavator's Period I (3500-2600 BC) or Period IIC (2200-2000 BC)."},
        {"source": "shinde2023perspectives", "page": "p. 12", "range_bce": [2600, 2400],
         "statement": ("The excavator's later regional summary dates periods IIA and IIB together to 2600-2400 BCE and IIC to 2200-1900 BCE 'on the basis "
                       "of a few accelerator mass spectrometry (AMS) dates' (p. 11), and says 'an extensive horizontal section of period IIB has been "
                       "unearthed at Farmana, exposing a piece of the perfectly planned Mature Harappan village' (p. 12)."),
         "disagreement": "Assigns the exposed planned area to IIB, as the 2011 descriptions do, and compresses IIA and IIB into 2600-2400 BCE."}
      ],
      "conflicts": ("The phase of the exposed street plan changed between reports: the 2008 interim report puts the 'parallelogram town plan in "
                    "Locality 1' with Main Street and Lane no. 1 in Structural Phase II, 'Late Period II', c. 2300-2000 BCE (Shinde et al. 2008: "
                    "22-23), while the 2011 report says the plan was established in Period IIA and kept unchanged in IIB, yet describes Main Street and "
                    "Complexes 2-4 under Period IIB. The 2011 report's chronology chapter says no radiocarbon dates were available (p. 39) and "
                    "announces a list of AMS dates for the Early Harappan levels of Farmana, Girawad and Mitathal that is not printed (p. 38), "
                    "while chapter 13 of the same volume publishes 21 AMS dates of the Harappan occupation, labelled by stratigraphic Phases 1 to 5 "
                    "rather than by period. The project's own specialists read the lowest dated levels as Mature Harappan, against the "
                    "excavator's Early Harappan attribution.")
    }
  ],
  "first_occupation": {
    "phase": "Period I, Early Harappan (Regional Hakra Culture Tradition), called Pre-Harappan in the 2008 interim report; pit-dwellings cut into natural soil, Layers 10-12",
    "range_bce": [3500, 2600],
    "basis": ("Cross-dating with Bhirrana. The final report dates Period I to 3500-2600 BC and says the Early Harappan AMS dates from Farmana, "
              "Girawad and Mitathal 'are not consistent and are of limited value', so that it relies on the early dates from Bhirrana to place "
              "the beginning 'in the middle of 4th millennium BC' (Shinde et al. 2011: 38). The project's own AMS series and its pottery and "
              "botanical specialists place the lowest dated levels in the Mature Harappan period (pp. 254, 813, 839)."),
    "locator": "shinde2011farmana pp. 38-39, 41-44; shinde2008farmana p. 15"
  },
  "sources": [
    {"id": "shinde2011farmana",
     "citation": ("Shinde, V., Osada, T. and Kumar, M. (eds) 2011. Excavations at Farmana, District Rohtak, Haryana, India, 2006-2008. Kyoto: Indus "
                  "Project, Research Institute for Humanity and Nature. Chapters 4 'Stratigraphy and cultural sequence' (pp. 27-40) and 5 "
                  "'Structural remains in the Settlement Area' (pp. 41-167), by V. Shinde."),
     "url_or_path": ("https://archive.org/details/excavationsatfarmana200608vshindeetal_212_v ; " + R + "farmana/shinde2011farmana.pdf "
                     "(text layer in .txt; printed page = pdf page - 14)"),
     "sha256": "ef5e71456067fbf099492cc116d51cea2f0d58ff572c93c562194a60a2a32215"},
    {"id": "paleolabo2011farmana",
     "citation": ("Paleo-Labo AMS Dating Group 2011. AMS radiocarbon dating. In V. Shinde, T. Osada and M. Kumar (eds), Excavations at Farmana, "
                  "District Rohtak, Haryana, India, 2006-2008, pp. 831-838. Kyoto: Indus Project, Research Institute for Humanity and Nature."),
     "url_or_path": R + "farmana/shinde2011farmana.pdf (pdf pp. 845-852)",
     "sha256": "ef5e71456067fbf099492cc116d51cea2f0d58ff572c93c562194a60a2a32215"},
    {"id": "uesugi2011farmana",
     "citation": ("Uesugi, A. 2011. Pottery from the Settlement Area. In V. Shinde, T. Osada and M. Kumar (eds), Excavations at Farmana, District "
                  "Rohtak, Haryana, India, 2006-2008, pp. 168-368. Kyoto: Indus Project, Research Institute for Humanity and Nature."),
     "url_or_path": R + "farmana/shinde2011farmana.pdf (pdf p. 268)",
     "sha256": "ef5e71456067fbf099492cc116d51cea2f0d58ff572c93c562194a60a2a32215"},
    {"id": "osada2011farmana",
     "citation": ("Osada, T. 2011. Summary. In V. Shinde, T. Osada and M. Kumar (eds), Excavations at Farmana, District Rohtak, Haryana, India, "
                  "2006-2008, pp. 839-. Kyoto: Indus Project, Research Institute for Humanity and Nature."),
     "url_or_path": R + "farmana/shinde2011farmana.pdf (pdf p. 853)",
     "sha256": "ef5e71456067fbf099492cc116d51cea2f0d58ff572c93c562194a60a2a32215"},
    {"id": "weber2011farmana",
     "citation": ("Weber, S. A., Kashyap, A. and Mounce, L. 2011. Archaeobotany at Farmana: new insights into Harappan plant use strategies. In V. "
                  "Shinde, T. Osada and M. Kumar (eds), Excavations at Farmana, District Rohtak, Haryana, India, 2006-2008, pp. 808-825. Kyoto: "
                  "Indus Project, Research Institute for Humanity and Nature."),
     "url_or_path": R + "farmana/shinde2011farmana.pdf (pdf p. 827)",
     "sha256": "ef5e71456067fbf099492cc116d51cea2f0d58ff572c93c562194a60a2a32215"},
    {"id": "shinde2008farmana",
     "citation": ("Shinde, V., Osada, T., Uesugi, A. and Kumar, M. 2008. A Report on Excavations at Farmana 2007-08. Occasional Paper 6: "
                  "Linguistics, Archaeology and the Human Past, ed. T. Osada and A. Uesugi. Kyoto: Indus Project, Research Institute for Humanity "
                  "and Nature."),
     "url_or_path": "https://nidanaheights.com/images/Library/ranbirbooks/op6.pdf ; " + R + "farmana/shinde2008op6.pdf (printed page = pdf page - 12)",
     "sha256": "b26569c4ce5489f8f3feb298dbacbe9d57c60fc72bdf1cd4d29e19ef0f9f6e4d"},
    {"id": "shinde2023perspectives",
     "citation": ("Shinde, V. 2023. Introduction to the Harappan Culture: Recent Perspectives. In V. Shinde, D. H. Shin and B. Bhattacharyya (eds), "
                  "New Perspectives on the Harappan Culture in Light of Recent Excavations at Rakhigarhi: 2011–2017, Volume 1: Bioarchaeological "
                  "Research on the Rakhigarhi Necropolis, pp. 1-18. Oxford: Archaeopress. Consulted in the publisher's sample PDF."),
     "url_or_path": ("https://www.archaeopress.com/Archaeopress/DMS/01839B015BD74EFBAA938B5AC62EBB33/9781803275918-sample.pdf ; "
                     + R + "rakhigarhi/archaeopress-9781803275918-sample.pdf"),
     "sha256": "1d241a3a4047f6294f8cb361c2260c68b13cdd84059c20f90df1d87701a475f7"}
  ],
  "notes": (
    "Farmana (Rohtak district) has a habitation mound of about 18 ha and a separate Harappan cemetery; only the habitation's layout concerns "
    "us. Deccan College and the Indus Project of the Research Institute for Humanity and Nature (Kyoto) excavated it in 2006-07, "
    "2007-08 and 2008-09. We read the 2007-08 interim report (Occasional Paper 6, 2008) and the final report of 2011, which the Internet Archive "
    "holds with a usable text layer. The excavator divides the sequence into Period I (Early Harappan, pit-dwellings) and Period II (Mature "
    "Harappan), subdivided into IIA, IIB and IIC, of which IIC has been removed by levelling; separately, the index-trench sections, the AMS "
    "chapter and the pottery chapter use stratigraphic Phases 1 to 5, and no table in the report converts one scheme into the other. We "
    "therefore list all 21 AMS determinations from the Harappan levels with the phase label they carry, and leave out the four Gupta-period and "
    "one late medieval determinations of the same table, which date later pits and fills.\n\n"
    "The AMS dates are conventional ages on the 5568-year half-life, calibrated with OxCal 4.1 and IntCal09 (p. 831); none comes from a hearth or "
    "oven (p. 254). No Bayesian model has been published. We did not obtain Occasional Paper 3 (Shinde et al. 2008, 'Exploration in "
    "the Ghaggar Basin and excavations at Girawad, Farmana (Rohtak District) and Mitathal (Bhiwani District), Haryana, India', pp. 77-158), "
    "which reports the 2006-07 season; we searched the Internet Archive and the web without finding a copy. The list of Early Harappan AMS dates "
    "announced on p. 38 of the final report is missing from the printed page, so any such dates remain unpublished as far as we know."
  )
}
dump("farmana", farmana)

# ---------------------------------------------------------------- MITATHAL
PRL_NOTE = ("PRL-III states that 'all dates are based on' the 5568-year half-life, uses 1950 as the base for AD/BC, and does not correct for "
            "13C fractionation (p. 234). Phase as printed by the laboratory. ")
mit_rc = [
    rc("PRL-290", "Charcoal", "Loc Tr MTL-1, Layer 17, depth 2.95m; sender's Sample 10", "Late Siswal culture (?)", 3820, 130, "rc-prl-iii",
       "p. 237", hl=5568,
       note=PRL_NOTE + "In the excavation report Layer 17 is the lowest Period I deposit in MTL-1, a floor in a pit cut into natural soil "
            "(Bhan 1975: 12), so this is the first-occupation date and the phase before the layout phase."),
    rc("PRL-291", "Charcoal", "Loc Tr MTL-1, pit sealed by Layer 10, depth 2.6m; sender's Sample 11", "Harappa culture", 3600, 110, "rc-prl-iii",
       "p. 237", hl=5568,
       note=PRL_NOTE + "In the report Layers 12-6 of MTL-1 form Period IIA (Bhan 1975: 12), so a pit sealed by Layer 10 falls in Period IIA by "
            "the report's layer list; the structural phase is not given."),
    rc("PRL-292", "Charcoal", "Loc Tr MTL-2, pit sealed by Layer 4; sender's Sample 15", "Harappa culture", 4210, 210, "rc-prl-iii",
       "p. 237", hl=5568,
       note=PRL_NOTE + "In the report Layers 10-1 of MTL-2 form Period IIB (Bhan 1975: 13), so by the layer list this pit belongs to Period "
            "IIB, later than the layout; we keep it because the laboratory labels it only 'Harappa culture' and it is older than the Period I "
            "date PRL-290."),
]

mitathal = {
  "town": "mitathal",
  "compiled_utc": "2026-10-21T05:40:00Z",
  "parts": [
    {
      "part": "whole town (twin mounds Mitathal 1 and Mitathal 2, trenches MTL-1 and MTL-2)",
      "layout_phase": "Period IIA (Harappan), from the end of its structural phase 2 (structural phases 3 to 5 of Period IIA)",
      "what_was_built": ("Period IIA has five structural phases on both mounds. The first two 'mark a formative stage of the Harappan settlement' "
                         "with few mud-brick walls and thatched roofs; 'there is, however, noticed an exuberance of culture at the end of structural "
                         "phase 2 when solid mud-brick structures were constructed all over the site rather abruptly', with walls up to a metre "
                         "thick, offsets at the foundations and bricks of 40 x 20 x 10 cm (Bhan 1975: 12). 'The settlement appears to be planned', "
                         "with streets that 'are staggered as at Kalibangan and measure 1 meter to 1.70 meter wide' (p. 13; also p. 7). The "
                         "excavator counts 'the twin mounds' among the Harappan features of Period IIA (p. 15). In Period IIB the structures and "
                         "streets kept the layout of IIA, with poorer walls and streets 1.50 to 3.10 m wide (pp. 8, 13). No fortification wall was "
                         "met in the two trenches."),
      "locator": "bhan1975mitathal pp. 7, 12-13, 15",
      "excavator_range_bce": [1900, 1700],
      "excavator_basis": ("Cross-dating. 'There are no Carbon 14 determinations' from the site, so 'the absolute chronology for the site has to be "
                          "worked out by cross dating' (Bhan 1975: 13). Period IIA is typologically a late-mature Harappan phase corresponding to the "
                          "late phase of Kalibangan II and Lothal A; its start follows Period I, placed after the end of Kalibangan I (c. 2000 B.C. on "
                          "Agrawal's radiocarbon bracket), and its end is tied to the end of Kalibangan II, 'about 1700 B.C.', giving 'a date between "
                          "C. 1900 B. C. and 1700 B. C.' (p. 15; summary on p. 17). These B.C. figures rest on uncalibrated radiocarbon dates from "
                          "other sites."),
      "radiocarbon": mit_rc,
      "bayesian_start": None,
      "syntheses": [
        {"source": "shinde2011farmana", "page": "p. 38", "range_bce": None,
         "statement": ("The Deccan College team, whose Occasional Paper 3 (2008) reports trial excavations at Mitathal, announces 'some of the AMS dates from the Early Harappan "
                       "levels from Farmana, Girawad and Mitathal' and calls them 'not consistent and ... of limited value', but the list is not "
                       "printed."),
         "disagreement": "Implies AMS dates exist for Mitathal's pre-Harappan levels that we could not find in print."},
        {"source": "sarkar2016bhirrana", "page": "p. 2", "range_bce": None,
         "statement": ("Lists 'Mithathal (Trench A-1, 8.2 ka BP)' among radiocarbon dates supporting an early Hakra phase in the Ghaggar-Hakra belt."),
         "disagreement": ("No trench A-1 is reported from Mitathal in Bhan 1975, and the 1968 levels date to the late third or early second millennium "
                          "B.C.; trench A-1 at Bhirrana gave a date of this order (BS-2333), so the attribution may be an error.")},
        {"source": "shinde2023perspectives", "page": "p. 11", "range_bce": [2600, 1900],
         "statement": ("Lists Mitathal among the Ghaggar basin sites that 'have revealed Early (6000–2600 BCE) and Mature Harappan (2600–1900 "
                       "BCE) remains'."),
         "disagreement": "A regional bracket roughly 700 years older at the start than Bhan's 1900-1700 B.C. for Period IIA."}
      ],
      "conflicts": ("The excavator's dates are cross-dated and uncalibrated; the three PRL determinations, published three years after the report, "
                    "were not used by it. By the report's layer lists, PRL-292 from a Period IIB context (4210 ± 210 BP) is older than the Period I "
                    "date PRL-290 (3820 ± 130 BP) and the Period IIA date PRL-291 (3600 ± 110 BP), so the three are not in stratigraphic order.")
    }
  ],
  "first_occupation": {
    "phase": "Period I, Late Siswal culture (non-Harappan, related to Kalibangan I), only in MTL-1 on Mitathal 1",
    "range_bce": [2000, 1900],
    "basis": ("Cross-dating: Mitathal I represents a late stage of the Kalibangan I culture and is placed after Agrawal's radiocarbon bracket of "
              "c. 2400-2000 B.C. for Kalibangan I, with about a century allowed for its deposit of under one metre (Bhan 1975: 15, 17). The later "
              "laboratory date PRL-290 from Layer 17, the lowest Period I deposit, is 3820 ± 130 BP on the 5568-year half-life."),
    "locator": "bhan1975mitathal pp. 4-5, 12, 15, 17; rc-prl-iii p. 237"
  },
  "sources": [
    {"id": "bhan1975mitathal",
     "citation": ("Suraj Bhan 1975. Excavation at Mitathal (1968) and Other Explorations in the Sutlej-Yamuna Divide. Kurukshetra: Kurukshetra "
                  "University."),
     "url_or_path": "https://ignca.gov.in/Asi_data/60032.pdf ; " + CN + "mitathal1975.pdf (image scan; printed p. 3 = pdf p. 20, p. 12 = pdf p. 31, p. 13 = pdf p. 36, p. 15 = pdf p. 38)",
     "sha256": "5ecc8be4646550b6ffb85044f5875f2e14d4f00fee3eccd82b4b5199e7c646ee"},
    {"id": "rc-prl-iii",
     "citation": ("Agrawal, D. P., Krishnamurthy, R. V., Kusumgar, S. and Pant, R. K. 1978. Physical Research Laboratory Radiocarbon Date List III. "
                  "Radiocarbon 20(2): 234-244. doi:10.1017/s0033822200004094"),
     "url_or_path": "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/PRL-III.pdf",
     "sha256": "31576ade8aff50d44c8edef4c154de891945cd7cf58bec9baa691870c1554b5b"},
    {"id": "shinde2011farmana",
     "citation": ("Shinde, V., Osada, T. and Kumar, M. (eds) 2011. Excavations at Farmana, District Rohtak, Haryana, India, 2006-2008. Kyoto: Indus "
                  "Project, Research Institute for Humanity and Nature. Chapter 4 'Stratigraphy and cultural sequence', by V. Shinde."),
     "url_or_path": "https://archive.org/details/excavationsatfarmana200608vshindeetal_212_v ; " + R + "farmana/shinde2011farmana.pdf",
     "sha256": "ef5e71456067fbf099492cc116d51cea2f0d58ff572c93c562194a60a2a32215"},
    {"id": "sarkar2016bhirrana",
     "citation": ("Sarkar, A., Mukherjee, A. D., Bera, M. K., Das, B., Juyal, N., Morthekai, P., Deshpande, R. D., Shinde, V. S. and Rao, L. S. "
                  "2016. Oxygen isotope in archaeological bioapatites from India: Implications to climate change and decline of Bronze Age "
                  "Harappan civilization. Scientific Reports 6: 26555. doi:10.1038/srep26555"),
     "url_or_path": "https://www.nature.com/articles/srep26555.pdf ; " + R + "shared-sarasvati/sarkar2016scirep.pdf",
     "sha256": "5341e9b1fac4b04b08572026b5afa16f88d87b1df70e5c6412261cfc3b94ffa1"},
    {"id": "shinde2023perspectives",
     "citation": ("Shinde, V. 2023. Introduction to the Harappan Culture: Recent Perspectives. In V. Shinde, D. H. Shin and B. Bhattacharyya (eds), "
                  "New Perspectives on the Harappan Culture in Light of Recent Excavations at Rakhigarhi: 2011–2017, Volume 1: Bioarchaeological "
                  "Research on the Rakhigarhi Necropolis, pp. 1-18. Oxford: Archaeopress. Consulted in the publisher's sample PDF."),
     "url_or_path": ("https://www.archaeopress.com/Archaeopress/DMS/01839B015BD74EFBAA938B5AC62EBB33/9781803275918-sample.pdf ; "
                     + R + "rakhigarhi/archaeopress-9781803275918-sample.pdf"),
     "sha256": "1d241a3a4047f6294f8cb361c2260c68b13cdd84059c20f90df1d87701a475f7"}
  ],
  "notes": (
    "Mitathal (Bhiwani district) is a pair of mounds 20 m apart: Mitathal 1 to the east, about 150 x 130 m and 5 m high, and Mitathal 2 to "
    "the west, about 300 x 175 m and 3 m high (Bhan 1975: 3-4). Suraj Bhan excavated one trench on each in January-April 1968. The sequence is "
    "Period I (Late Siswal, only in MTL-1), Period IIA (Harappan) and Period IIB (Late Harappan). The layout statement rests on two trenches "
    "of 25 x 6 m and 10 x 6 m, so 'planned' describes the streets met in those cuttings rather than an exposed town plan. The report is an "
    "image-only scan; we read it through our own OCR of the locally held copy and checked the passages used against the page images.\n\n"
    "The only published radiocarbon determinations we found are the three PRL dates of 1978, which the laboratory assigns to 'Late Siswal "
    "culture (?)' and 'Harappa culture' and which we tied to the report's periods through its layer lists; that mapping is ours. No Bayesian "
    "model exists. We did not obtain the Deccan College report on its trial excavation at Mitathal (Shinde et al. 2008, Occasional Paper 3, pp. "
    "77-158), and the compilations of Mandal (1972) and Ramachandran (1975) predate the PRL measurements and do not list Mitathal."
  )
}
dump("mitathal", mitathal)

# ---------------------------------------------------------------- BHIRRANA
RAO_NOTE = ("Rao et al. 2005 print the BSIP results for samples of the 2003-04 season without context, period, half-life or calibration "
            "curve, and judge BRN 5, 6 and 7 'very early', to be checked against a second set of nine samples sent to BSIP (p. 67).")
DIK_NOTE = ("Dikshit prints the BSIP dates without context and assigns them to periods only by grouping their calibrated ranges in his Table 4 "
            "(pp. 172-173), where group {g} is matched to the excavator's period {p}; no half-life or curve is stated.")
bh_rc = [
    rc("BS-2318", None, "BRN 5 (no context printed)", None, 6120, 250, "rao2005bhirrana", "p. 67, Table", cal="Cal. Age Range (1 Sigma) Yr. BP 7286 - 6671; Yr. BC 5336 - 4721",
       note=RAO_NOTE + " Dikshit 2022 classes this date with Period IB, the phase before the layout."),
    rc("BS-2314", None, "BRN 7 (no context printed)", None, 5700, 170, "rao2005bhirrana", "p. 67, Table", cal="Cal. Age Range (1 Sigma) Yr. BP 6720 - 6303; Yr. BC 4770 - 4353",
       note=RAO_NOTE + " Dikshit 2022 classes this date with Period IIA, the layout phase."),
    rc("BS-2318", None, "Trench ZE-10, depth 1.42 m (sample BRN-5)", None, None, None, "sarkar2016bhirrana",
       "Supplementary Information p. 2, table 'Radiocarbon and OSL chronology in Bhirrana trenches'",
       cal="Calibrated age ±1 year BC max. 5336, min. 4721; calibrated age year BP max. 7286, min. 6671", curve="IntCal09 (OxCal v 4.1)", hl=5730,
       note=("The supplement prints the radiocarbon age only as '4170 ± 250' in a column headed '14C age±1 year BC', states that 'all 14C ages "
             "are based on a half life of 5.730± 40 year', and cites Mani 2008 for the dates; it gives no period for the sample. 4170 BC is 1950 "
             "years less than the 6120 BP printed by Rao et al. 2005, so if Sarkar et al. are right the BSIP ages are on the 5730-year half-life "
             "and the 5568-year equivalent of 6120 ± 250 would be about 5942 ± 243 (our arithmetic; the published calibrations use the "
             "printed age unchanged).")),
    rc("BS-2318", "charcoal (Table 3 title: C14 dates of BSIP; material not stated)", "BRN 5", "IB c. 6000-4500 BCE (Dikshit's Period IIA, 'Transitional')", 6120, 250,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="(1 Sigma) Yr. BP 7286 - 6671; Yr. BCE 5316 – 4775",
       note=DIK_NOTE.format(g="II", p="IB") + " The BCE range differs from Rao et al. 2005 (5336 - 4721 BC) for the same sample."),
    rc("BS-2502", "not stated", "KRN(K) (no context printed)", "IB c. 6000-4500 BCE (Dikshit's Period IIA, 'Transitional')", 7150, 130,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="Yr. BCE 6200 – 5850",
       note=DIK_NOTE.format(g="II", p="IB") + " The sample label 'KRN(K)' differs from the BRN labels of the other Bhirrana samples, and the table does not explain it."),
    rc("BS-2314", "not stated", "BRN 7", "IIA c. 4500-3000 BCE (Dikshit's Period IIB, 'Early Harappan')", 5700, 170,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="(1 Sigma) Yr. BP 6720 - 6303; Yr. BCE 4714 – 4360",
       note=DIK_NOTE.format(g="III", p="IIA") + " The BCE range differs from Rao et al. 2005 (4770 - 4353 BC)."),
    rc("BS-2482", "not stated", "BRN 6 (a second sample labelled BRN 6; the first is BS-2333)", "IIA c. 4500-3000 BCE (Dikshit's Period IIB, 'Early Harappan')", 4990, 180,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="Yr. BCE 3970 – 3640", note=DIK_NOTE.format(g="III", p="IIA")),
    rc("BS-2485", "not stated", "No.8, BRN 1", "IIA c. 4500-3000 BCE (Dikshit's Period IIB, 'Early Harappan')", 4450, 170,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="Yr. BCE 3370 – 2890", note=DIK_NOTE.format(g="III", p="IIA")),
    rc("BS-2496", "not stated", "No.1, BRN 1", "IIA c. 4500-3000 BCE (Dikshit's Period IIB, 'Early Harappan')", 4340, 120,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="Yr. BCE 3100 – 2880", note=DIK_NOTE.format(g="III", p="IIA")),
    rc("BS-2497", "not stated", "No.5, BRN 1", "IIA c. 4500-3000 BCE (Dikshit's Period IIB, 'Early Harappan')", 4280, 110,
       "dikshit2022origin", "p. 172, Table 3; Table 4 pp. 172-173", cal="Yr. BCE 3020 – 2700", note=DIK_NOTE.format(g="III", p="IIA")),
]

bhirrana = {
  "town": "bhirrana",
  "compiled_utc": "2026-10-21T05:40:00Z",
  "parts": [
    {
      "part": "whole town (citadel and lower town within one fortification)",
      "layout_phase": "Period IIA, Early Mature Harappan (Rao et al. 2005, 2006), the 'Period II: Transitional' of the 2003-04 report",
      "what_was_built": ("The first fortified and planned town at Bhirrana belongs to Period IIA. The 2005-06 report states that 'the entire settlement "
                         "was reorganized' in this period, that 'the complete town was encompassed within a fortification wall as indicated by the "
                         "partially traced wall lying underneath the northern and western arms of the fortification wall of the Mature Harappan "
                         "period', and that 'the concept of twin units of town planning, viz. Citadel and Lower Town also came up during this "
                         "period', the citadel in the west-north-west part of the mound and the lower town in the east-south-east, separated by a "
                         "mud-brick wall 2.70 m wide, with the main entrances in the middle of the walls and a fortified lower town (Rao et al. 2006: "
                         "47-48). The preceding Period IB 'was probably an unfortified settlement as no defence/fortification wall has come to light "
                         "so far' (p. 47). In Period IIB the Mature Harappans 'strengthened and enhanced the height of the wall' with yellowish mud "
                         "bricks, moved the main entrances to the corners and partially modified the layout; streets of that period are 2.80 m wide "
                         "in the lower town and 4.0 m in the citadel, with a thoroughfare about 4.10 m wide along the wall (pp. 48-49). The wall "
                         "exposed in 2004-05 is of mud brick in the ratio 1:2:4, 95 m long, 5 m wide, seventeen courses and 1.80 m high on its "
                         "northern side, and 2.50-2.75 m wide on its southern side (Rao et al. 2005: 63-64)."),
      "locator": "rao2006bhirrana pp. 47-49; rao2005bhirrana pp. 60, 63-64; rao2004bhirrana p. 21",
      "excavator_range_bce": [4500, 3000],
      "excavator_basis": ("Radiocarbon. The excavators' own reports give no calendar range for Period IIA: Rao et al. 2005: 67 say only that four BSIP "
                          "dates agree with the known Harappan chronology from 'the fag end of the 4th millennium to the middle of the 2nd millennium "
                          "BC' while three are 'very early'. The range 4500-3000 BCE for IIA ('Beginning of fortification wall, house-complexes, "
                          "streets and lanes') is printed in the supplement of Sarkar et al. 2016 (p. 3), co-authored by the excavator L. S. Rao, "
                          "'based on radiocarbon ages in different trenches' and compiled from Rao et al. 2004-05 and Dikshit and Mani 2012; Dikshit "
                          "2022: 173 gives the same bracket, 'IIA C. 4500-3000 BCE'."),
      "radiocarbon": bh_rc,
      "bayesian_start": None,
      "syntheses": [
        {"source": "dikshit2022origin", "page": "pp. 171-173", "range_bce": [4500, 3000],
         "statement": ("Describes 'the fortification wall of Early Mature Harappan (IIA) and Mature Harappan (IIB)' and prints nineteen BSIP dates, which "
                       "he groups by calibrated range into IA c. 7500-6000, IB c. 6000-4500, IIA c. 4500-3000, IIB c. 3000-1800 and IIC to c. 1600 BCE; "
                       "in his own scheme the IIA group is 'Period IIB (Early Harappan)'."),
         "disagreement": ("Calls the dates of the excavator's Early Mature Harappan IIA 'Early Harappan', and his calendar conversions of the same BSIP "
                          "ages differ from those of Rao et al. 2005.")},
        {"source": "sarkar2016bhirrana", "page": "pp. 3-4", "range_bce": None,
         "statement": ("Gives the Bhirrana sequence as 'Pre-Harappan Hakra phase (~9.5–8 ka BP), Early Harappan (~8–6.5 ka BP), Early mature "
                       "Harappan (~6.5–5 ka BP) and mature Harappan (~5–2.8 ka BP)', and reports an OSL age of 5.9 ± 0.25 ka BP (6185 to "
                       "5695 years BP) for pottery from the early mature Harappan level at 143 cm in trench YF-2 and 4.8 ± 0.3 ka BP for mature "
                       "Harappan pottery at 42 cm, which it takes as confirming the radiocarbon chronology."),
         "disagreement": ("Its early mature Harappan bracket (about 4550-3050 BCE in calendar terms) and the OSL age put the layout some two millennia "
                          "before the conventional start of the Mature Harappan about 2600 BCE.")}
      ],
      "conflicts": ("The excavators changed their attribution of the first wall. In 2003-04 'the town appears to have been fortified' in Period II, "
                    "then called Transitional, 'which needs to be confirmed' (Rao et al. 2004: 21); in 2004-05 the fortification was described under "
                    "Period IIb, Mature Harappan, and little was found of IIa (Rao et al. 2005: 63); in 2005-06 the first wall and the division into "
                    "citadel and lower town were assigned to IIA, with IIB strengthening them (Rao et al. 2006: 47-48). The radiocarbon evidence has "
                    "no published contexts except four dates in Sarkar et al. 2016, which give trench and depth but no period. Two different samples "
                    "carry the label BRN 6 (BS-2333 and BS-2482). Sarkar et al. state that the BSIP ages are on the 5730-year half-life, while Rao et "
                    "al. and Dikshit state no half-life, and the BCE conversions of the same ages differ between Rao et al. 2005 and Dikshit 2022. The "
                    "dates Dikshit assigns to IIA (about 4700-2700 BCE) are far older than conventional Mature Harappan dates, a point the excavators "
                    "themselves flagged as needing confirmation.")
    }
  ],
  "first_occupation": {
    "phase": "Period IA, Hakra Ware Culture: subterranean dwelling pits cut into natural soil",
    "range_bce": [7500, 6000],
    "basis": ("Radiocarbon. The earliest BSIP dates are BS-2333 (BRN 6, 7590 ± 240 BP, 8597-8171 BP, 6647-6221 BC; Rao et al. 2005: 67) and "
              "BS-2481 (BRN 9, 8350 ± 140 BP, 7570-7180 BCE; Dikshit 2022: 172); the range 7500-6000 BCE for IA is printed in the supplement of "
              "Sarkar et al. 2016 (p. 3), co-authored by the excavator, and in Dikshit 2022: 172 ('IA C. 7500-6000 BCE'). Rao et al. 2005: 67 "
              "treated the earliest dates as needing confirmation."),
    "locator": "rao2005bhirrana pp. 60-61, 67; rao2006bhirrana pp. 45-46; sarkar2016bhirrana Supplementary Information pp. 2-3; dikshit2022origin pp. 172-173"
  },
  "sources": [
    {"id": "rao2004bhirrana",
     "citation": ("Rao, L. S., Sahu, N. B., Sahu, P., Shastry, U. A. and Diwan, S. 2004. Unearthing Harappan Settlement at Bhirrana (2003-04). "
                  "Puratattva 34 (2003-2004): 20-24."),
     "url_or_path": "https://ignca.gov.in/Asi_data/87942.pdf ; " + CN + "puratattva36_retry.pdf (this file is Puratattva 34; pp. 20-21 = pdf pp. 32-33)",
     "sha256": "ed1f85542c4c20e6ea287366eb188c2c30ca3815203413fba1496ca9cd4f7276"},
    {"id": "rao2005bhirrana",
     "citation": ("Rao, L. S., Sahu, N. B., Sahu, P., Diwan, S. and Shastry, U. A. 2005. New Light on the Excavation of Harappan Settlement at "
                  "Bhirrana. Puratattva 35 (2004-2005): 60-68."),
     "url_or_path": "https://ignca.gov.in/Asi_data/88233.pdf ; " + CN + "puratattva35_retry.pdf (pp. 60-67 = pdf pp. 74-81)",
     "sha256": "09a0220a9a65e633bbafa6168e282dced328b5ccf50051ec061a23dbffde8525"},
    {"id": "rao2006bhirrana",
     "citation": ("Rao, L. S., Sahu, N. B., Shastry, U. A., Sahu, P. and Diwan, S. 2006. Bhirrana Excavation — 2005-06. Puratattva 36 (2005-2006): "
                  "45-49."),
     "url_or_path": "https://archive.org/details/dli.ministry.29992 ; " + R + "shared-puratattva/puratattva36.pdf (pp. 45-49 = pdf pp. 59-63)",
     "sha256": "0718f8b3061d12224e4d35877c4f0edf97d715455eb65ed869d11bba22046182"},
    {"id": "sarkar2016bhirrana",
     "citation": ("Sarkar, A., Mukherjee, A. D., Bera, M. K., Das, B., Juyal, N., Morthekai, P., Deshpande, R. D., Shinde, V. S. and Rao, L. S. "
                  "2016. Oxygen isotope in archaeological bioapatites from India: Implications to climate change and decline of Bronze Age "
                  "Harappan civilization. Scientific Reports 6: 26555, with Supplementary Information (Word file). doi:10.1038/srep26555"),
     "url_or_path": ("https://www.nature.com/articles/srep26555.pdf ; " + R + "shared-sarasvati/sarkar2016scirep.pdf ; supplement "
                     "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fsrep26555/MediaObjects/41598_2016_BFsrep26555_MOESM23_ESM.doc "
                     "saved as " + R + "shared-sarasvati/sarkar2016scirep-si.bin (sha256 4bdfeb20e750a39dafb3fd6de8107d5c53cbc3b51d95f7fc71c0765e7362a257)"),
     "sha256": "5341e9b1fac4b04b08572026b5afa16f88d87b1df70e5c6412261cfc3b94ffa1"},
    {"id": "dikshit2022origin",
     "citation": ("Dikshit, K. N. 2022. The Origin of Indian Civilization in Sarasvati Valley. Abhidha Journal of Art, Archaeology and Cultural "
                  "Heritage 2(2): 156-215."),
     "url_or_path": ("https://abhidhajournal.com/wp-content/uploads/2024/06/Paper-10_-The-Origin-of-Indian-Civilization-in-Sarasvati-Valley-_v4.pdf ; "
                     + R + "shared-sarasvati/dikshit2022abhidha.pdf"),
     "sha256": "41266be600cd0e5febac2ee41e4c494c86bd95c60817b6eefc1601ad3476b544"}
  ],
  "notes": (
    "Bhirrana (Fatehabad district) is a mound of about 190 x 150 m and 5.5 m high, excavated by the Archaeological Survey of India under L. S. "
    "Rao from 2003 to 2006 (Rao et al. 2004: 20). The excavators' sequence, as revised in 2004-05, is Period IA (Hakra Ware Culture, dwelling "
    "pits), IB (Early Harappan), IIA (Early Mature Harappan) and IIB (Mature Harappan) (Rao et al. 2005: 60); the first report's 'Period II: "
    "Transitional' became IIA. We read the three interim reports in Puratattva 34, 35 and 36; the Puratattva 34 and 35 copies are locally held "
    "image scans, which we read from their page images.\n\n"
    "We list radiocarbon dates only where a published source ties them to IIA or IB: two in Rao et al. 2005 that Dikshit later grouped with "
    "those periods, one in Sarkar et al. 2016 with trench and depth, and Dikshit's grouped dates. Dikshit's period assignments are made by "
    "calibrated date, not by context, so they cannot test the chronology on their own. The BSIP date lists for Bhirrana have never appeared in "
    "Radiocarbon. No Bayesian model has been published. We did not obtain Mani 2008 or Dikshit and Mani 2012, which the supplement of Sarkar "
    "et al. cites as the source of its dates and periods, nor any final report of the excavation; the 2016 article in Heritage: Journal of "
    "Multidisciplinary Studies in Archaeology 4 that we checked concerns a seal from Bhirrana and gives no dates."
  )
}
dump("bhirrana", bhirrana)
