"""Write allahdino.json and sutkagen-dor.json in experiments/2026-10-21-town-axes/dating-v1/towns/."""
import json
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Users\sandh\OneDrive\Projects\indus_valley_script")
TOWNS = ROOT / "experiments" / "2026-10-21-town-axes" / "dating-v1" / "towns"
UTC = sys.argv[1]

PENN19_NOTE = ("Penn XIX gives BP ages on the 5568-year half-life (p. 188); the BC date marked with an asterisk 'has been "
               "calculated with the half-life value of 5730 yr and then corrected by means of MASCA correction factors' "
               "(p. 188). Fairservis's general comment: 'samples from high on site. Only P-2296 could qualify as assoc with "
               "main bldg period; P-2237 and -2295 from last phase of occupation' (p. 214).")
CURVE19 = "MASCA correction factors applied to the 5730-year age (Penn XIX introduction, p. 188, citing Ralph et al. 1973)"

ALLCHIN = {"id": "allchin1982rise",
           "citation": ("Allchin, B. and Allchin, R. 1982. The Rise of Civilization in India and Pakistan. Cambridge: "
                        "Cambridge University Press. Consulted in the 1983 Indian reprint (New Delhi: Selectbook Service "
                        "Syndicate) through its archive.org OCR text; page numbers are the printed running heads."),
           "url_or_path": ("https://archive.org/details/gdmp_the-rise-of-civilization-in-india-and-pakistan-by-bridget-and-raymond-allch; "
                           "local OCR text data/raw/2026-10-21-town-axes/dating/shared-allchin/allchin1982rise-djvu.txt (the 203 MB "
                           "PDF scan was not saved because the disk was full)"),
           "sha256": "08158dc3404c2ff5ef42ed266f6bbacdb3d009e299acf81d9f5958834807d1e0"}

# ---------------------------------------------------------------- Allahdino
allahdino = {
    "town": "allahdino",
    "compiled_utc": UTC,
    "parts": [{
        "part": "whole site (building complex around the central court)",
        "layout_phase": "the 'major construction period' of Buildings I, II, III and probably IV; the radiocarbon list calls the dated level 'Building Level I'",
        "what_was_built": (
            "Allahdino is a low silt mound no more than 100 m across. At its highest, central part the excavators cleared "
            "an open court about 20 by 8 m with a stone-built well (Well A) and a pavement, surrounded by Buildings I to VII; "
            "access to the court was by open passageways between the buildings. Building I, the largest, had two wings "
            "joined by 'a platform and drain complex', Building II a stone-lined bathroom with covered drains, Building VII "
            "'a broad brick platform', and two stone-lined drain channels with a movable sluice stone met at the head of "
            "the alley between Buildings I and II. Fairservis lists the traits of the complex: every building is partly of "
            "stone, 'There is a formality of plan which integrates the structures. There is a general absence of "
            "haphazardness both in the way the buildings were constructed and the way they relate one to another', and "
            "'There was no perimeter, or enclosing wall around the site' (pp. 109-110). Stratigraphically, 'there was an "
            "early phase when Harappan cattle pastoralists settled the site. This was followed by a major construction "
            "period during which Buildings I, II, III and probably IV, were created', with flimsier structures added to the "
            "south later (p. 111)."),
        "locator": "fairservis1982allahdino pp. 108-111",
        "excavator_range_bce": [2100, 1700],
        "excavator_basis": (
            "Not stated in the excavation report, which gives no absolute date and judges from 'The conformity and "
            "continuity of artifacts and structures' that the Harappan occupation lasted 'no more than a hundred years at "
            "the most' (fairservis1982allahdino p. 111). The range recorded here is the date Fairservis expected when he "
            "submitted the two Building Level I samples, 'Date expected to be 1900 +/- 200 BC' (rc-penn-xix p. 215); its "
            "basis is not given, and presumably rests on the conventional Harappan chronology of the time."),
        "radiocarbon": [
            {"lab_no": "P-2296", "material": "Charcoal",
             "context": "Charcoal from Bldg Level I, 60cm depth. Date expected to be 1900 +/- 200 BC.",
             "phase": "Building Level I; the only sample Fairservis would associate with the main building period",
             "age_bp_printed": 3930, "sigma_printed": 50, "half_life_printed": 5568,
             "age_bp_5568": 3930, "sigma_5568": 50,
             "calibrated_published": "*2550 +/- 50 BC", "curve": CURVE19,
             "source": "rc-penn-xix", "page": "215", "note": PENN19_NOTE},
            {"lab_no": "P-2295-A", "material": "Charcoal",
             "context": "Charcoal from Bldg Level I, 40cm depth. Date expected to be 1900 +/- 200 BC. Comment: NaOH pretreatment.",
             "phase": "Building Level I, 40 cm depth; by Fairservis's comment from the last phase of occupation",
             "age_bp_printed": 3760, "sigma_printed": 70, "half_life_printed": 5568,
             "age_bp_5568": 3760, "sigma_5568": 70,
             "calibrated_published": "*2180 +/- 70 BC", "curve": CURVE19,
             "source": "rc-penn-xix", "page": "215",
             "note": PENN19_NOTE + " The general comment calls it '-2295'; the entry is P-2295-A. It postdates the layout and is kept because the site has only three dates."},
            {"lab_no": "P-2237", "material": "Charcoal",
             "context": "Sq E 5: charcoal from small burned area in Sq 5 E, 60cm from N balk, 60cm depth. Date expected to be 2000 +/- 200 BC.",
             "phase": "last phase of occupation (Fairservis's comment)",
             "age_bp_printed": 3840, "sigma_printed": 60, "half_life_printed": 5568,
             "age_bp_5568": 3840, "sigma_5568": 60,
             "calibrated_published": "*2410-2340 +/- 70 BC", "curve": CURVE19,
             "source": "rc-penn-xix", "page": "215",
             "note": PENN19_NOTE + " It postdates the layout and is kept because the site has only three dates."},
        ],
        "bayesian_start": None,
        "syntheses": [
            {"source": "allchin1982rise", "page": "144",
             "range_bce": None,
             "statement": "The Allchins note that at Allahdino 'The main settlement is of the Harappan period and relatively little can be said of the earlier occupation.'",
             "disagreement": None},
        ],
        "conflicts": (
            "The one date Fairservis tied to the main building period, P-2296 (3930 +/- 50 BP), was published with a "
            "MASCA-corrected date of 2550 +/- 50 BC, about six centuries older than the 1900 +/- 200 BC he expected; the two "
            "samples from the last phase give 2410-2340 and 2180 BC on the same correction, so the dated sequence runs "
            "older than his expectation throughout and the spread of the three dates (about 370 years in MASCA terms) is "
            "longer than his estimate of a Harappan occupation of at most a hundred years. P-2295-A, from 40 cm in the "
            "same 'Building Level I', is 170 radiocarbon years younger than P-2296 at 60 cm."),
    }],
    "first_occupation": {
        "phase": "an early phase in which 'Harappan cattle pastoralists settled the site', identified in Shaffer's sondage in quadrant 5-6, below the major construction period",
        "range_bce": None,
        "basis": ("Stratigraphic only; no date is given for it. Fairservis notes that, contrary to expectation, no Amrian "
                  "(Early Harappan) material was found in the lower levels (fairservis1982allahdino pp. 109, 111)."),
        "locator": "fairservis1982allahdino pp. 109, 111",
    },
    "sources": [
        {"id": "fairservis1982allahdino",
         "citation": ("Fairservis, W. A., Jr. 1982. Allahdino: an excavation of a small Harappan site. In G. L. Possehl "
                      "(ed.), Harappan Civilization: A Contemporary Perspective, pp. 107-112. Warminster: Aris & Phillips "
                      "(and New Delhi: Oxford & IBH), in cooperation with the American Institute of Indian Studies."),
         "url_or_path": ("https://rhinoresourcecenter.com/wp-content/uploads/2025/06/1218186492.pdf (Rhino Resource Center "
                         "copy of the chapter with the volume's title page); local "
                         "data/raw/2026-10-21-town-axes/dating/allahdino/fairservis1982allahdino.pdf (PDF p. 2 = p. 107)"),
         "sha256": "f3e5e52e51b137eeff10fe71367d49ecaca198ae2b2cd92eb4af29382c5c6d1a"},
        {"id": "rc-penn-xix",
         "citation": "Fishman, B., Forbes, H. and Lawn, B. 1977. University of Pennsylvania Radiocarbon Dates XIX. Radiocarbon 19(2): 188-228. doi:10.1017/s0033822200003532",
         "url_or_path": "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/PENN-XIX.pdf",
         "sha256": "a0d0169c63e8b991e800cf41ec0392a8d212eb66bfdc7607c932a70c5aa23631"},
        ALLCHIN,
    ],
    "notes": (
        "Allahdino is a small, unwalled Harappan site near Karachi, and its layout is that of a single planned building "
        "complex rather than a town grid: a central court with wells, a paved surface and drains, ringed by buildings "
        "with stone footings and platforms that Fairservis describes as integrated by a 'formality of plan'. We include it "
        "because the planned complex and its platforms are the layout the brief asks about. The excavator's 1982 summary "
        "chapter is our only description of the architecture; the expedition papers (Fairservis 1976 and 1977 on the seals "
        "and graffiti, Hoffman and Cleland 1977 on the lithics) and Shaffer's 1974 study 'Allahdino and the Mature "
        "Harappan', which holds the stratigraphy, were not available online, nor were Possehl's radiocarbon compilations. "
        "The three Pennsylvania dates in Penn XIX are the only determinations we found, and none comes from the early "
        "pastoralist phase below the buildings. We found no Bayesian model or later re-dating. The two ways the Penn list "
        "states each date (a conventional BP age and a MASCA-corrected BC date) should not be mixed: the BP ages are on "
        "the Libby half-life, the BC dates on 5730 years with the MASCA correction."),
}

# ---------------------------------------------------------------- Sutkagen-dor
sutkagen = {
    "town": "sutkagen-dor",
    "compiled_utc": UTC,
    "parts": [{
        "part": "citadel (walled enclosure between two natural ridges)",
        "layout_phase": "Phase 2 of Dales's sequence in Operation A-A/1 (Levels 10A, 10, 9 and 8)",
        "what_was_built": (
            "Two massive stone walls join the ends of two sandstone ridges and so enclose a raised plateau; Stein "
            "describes the larger wall as built of large, roughly squared slabs with little clay between the courses, about "
            "30 feet thick at the base and 20 to 25 feet high as preserved, and a gate with the massive foundations of what "
            "may have been two towers at one corner of the enclosure (stein1931gedrosia pp. 61-62). Dales's L-shaped trench "
            "against the inner face of one wall reached natural soil and showed a solid mudbrick structure 2.3 m wide, built "
            "on a deliberate foundation of crushed stones and sand laid on the natural surface, against the inner face of "
            "the stone wall: 'a rampart, or better still, a \"banquette\"' (dales1992makran p. 137). He reconstructs seven "
            "phases, of which Phase 2 comprises 'Level 10A: foundation laid for the citadel enclosure. Level 10: construction of "
            "stone citadel wall and mudbrick rampart. Levels 9 and 8: earliest occupations associated with the citadel "
            "enclosure' (p. 138). Inside, stone house walls associated exclusively with Harappan sherds belong to later "
            "phases (pp. 135-136, 139)."),
        "locator": "dales1992makran pp. 135-139; stein1931gedrosia pp. 61-62",
        "excavator_range_bce": None,
        "excavator_basis": (
            "Neither excavator gives an absolute date for the enclosure, and no radiocarbon sample has been published. "
            "Stein assigned the site to 'chalcolithic times' by comparing its surface finds, house contents and cinerary "
            "pots with sites in northern Baluchistan, and saw in the finds 'a single if prolonged period of occupation' "
            "(stein1931gedrosia pp. 63, 68). Dales identified the walled citadel as Harappan from the associated pottery "
            "and placed the Indus civilization in general at 'cir. 2500-1800 B.C.' (dales1992makran, Preface, pdf p. 11)."),
        "radiocarbon": [],
        "bayesian_start": None,
        "syntheses": [
            {"source": "dales1977shell", "page": "13",
             "range_bce": None,
             "statement": ("Dales, introducing Balakot as 'one of four known ancient coastal sites in Pakistan dating to the "
                           "period of South Asia's earliest civilization-the Harappan (or Indus)-that flourished in the "
                           "centuries just before and after 2000 B.C.', names Sutkagen Dor and Sotkha Koh as the two major "
                           "sites found by the 1959-60 Makran survey."),
             "disagreement": "Later and narrower than the 'cir. 2500-1800 B.C.' Dales gives in the 1992 report; neither is specific to Sutkagen-dor."},
            {"source": "allchin1982rise", "page": "170",
             "range_bce": None,
             "statement": "The Allchins mention Stein's trial trenches and add that 'More recently Dales has shown the existence of a great fortification around this Harappan outpost.'",
             "disagreement": None},
            {"source": "doam2026sotkagendor", "page": "site record 9024",
             "range_bce": [3500, 1800],
             "statement": ("The Pakistan Department of Archaeology and Museums heritage database gives 'Relative Chronology: 3500 "
                           "BCE - 1800 BCE' and says 'The pottery represented Kulli-Harappan cultures', citing Possehl, The "
                           "Indus Age: The Beginnings (1999)."),
             "disagreement": ("Begins a millennium earlier than any Harappan date; it is a relative span for the whole site "
                              "from a heritage inventory, not a dated layout.")},
        ],
        "conflicts": (
            "No source dates the citadel wall. The published statements are general spans for the Harappan or Indus period: "
            "'the centuries just before and after 2000 B.C.' (Dales 1977), 'cir. 2500-1800 B.C.' (Dales 1992) and 3500-1800 "
            "BCE (Pakistan heritage database). Dales notes that his seven-phase reading of Trench A-A/1 differs in 'a "
            "couple minor discrepancies' from the version Mughal submitted to the Department of Archaeology (p. 138)."),
    }],
    "first_occupation": {
        "phase": "Phase 1 of Dales's sequence (Level 11): 'the earliest presence of the Harappans who presumably brought with them micaceous pottery from Sind'",
        "range_bce": None,
        "basis": "Stratigraphic: Level 11 lies on wash over the natural surface (Level 12) and below the foundation of the enclosure (Level 10A); no date is given.",
        "locator": "dales1992makran p. 138",
    },
    "sources": [
        {"id": "dales1992makran",
         "citation": ("Dales, G. F. and Lipo, C. P. 1992. Explorations on the Makran Coast, Pakistan: A Search for "
                      "Paradise. Contributions of the Archaeological Research Facility 50. Berkeley: University of "
                      "California. ISBN 1-882744-00-4 (CC BY 4.0 on eScholarship)."),
         "url_or_path": ("https://escholarship.org/uc/item/2qg1r0gp; local "
                         "data/raw/2026-10-21-town-axes/dating/sutkagen-dor/dales1992makran.pdf (printed p. 136 = PDF p. 148)"),
         "sha256": "10b88b64f83581a117ebaa96bb953a9f521eaf388793fa6353e966103c283d60"},
        {"id": "stein1931gedrosia",
         "citation": ("Stein, M. A. 1931. An Archaeological Tour in Gedrosia. Memoirs of the Archaeological Survey of India "
                      "43. Calcutta: Government of India Central Publication Branch."),
         "url_or_path": ("https://archive.org/details/dli.pahar.2466; local "
                         "data/raw/2026-10-21-town-axes/dating/sutkagen-dor/stein1931gedrosia.pdf (printed p. 62 = PDF p. 79)"),
         "sha256": "7391525c6eee261e2f8a09f05e0ce00726d76d8c3ea4dc21c3be844f3aaf23ac"},
        {"id": "dales1977shell",
         "citation": "Dales, G. F. and Kenoyer, J. M. 1977. Shell working at ancient Balakot, Pakistan. Expedition 19(2): 13-19.",
         "url_or_path": ("https://www.harappa.com/sites/default/files/pdf/Kenoyer1977_Shell%20Working%20at%20Ancient%20Balakot%2C%20Pakistan.pdf; "
                         "local data/raw/2026-10-21-town-axes/dating/balakot/dales1977expedition.pdf"),
         "sha256": "d60fac156b72494a2c9f11676c3c91ab995f71951217053b01eb6c9b470cece3"},
        ALLCHIN,
        {"id": "doam2026sotkagendor",
         "citation": ("Department of Archaeology and Museums, Government of Pakistan. Sotkagen-dor, site record 9024, Heritage "
                      "of Pakistan database (accessed 21 October 2026)."),
         "url_or_path": "https://doam.gov.pk/public/sites/9024; local data/raw/2026-10-21-town-axes/dating/sutkagen-dor/doam-sotkagen-dor.html",
         "sha256": "25492ef3e5d09e1354dff7b627a5b6fd6b8ba7f2d5230caa7ff11440a856be49"},
    ],
    "notes": (
        "Sutkagen-dor is the westernmost Harappan site, on the Dasht river in Makran, and its layout is a fortified "
        "enclosure rather than a street grid: stone walls with a gateway close the gaps between two rocky ridges, and a "
        "mudbrick rampart stands against the inner face of the wall. Dales's 1960 test trench showed that the enclosure "
        "was founded in his Phase 2, directly after a thin first Harappan occupation (Phase 1) on the natural surface, so "
        "layout and first occupation are close in time. The site has no published radiocarbon date and no excavator's "
        "absolute date, so every date field is empty and the syntheses give only general spans. Dales's soundings in the "
        "'lower town' east of the citadel went 4.5 to 5 m down through sterile silt and found no occupation strata, so we "
        "record no lower-town part (dales1992makran pp. 44, 46, 139). We read Stein's 1931 report and the full 1992 report "
        "of Dales's survey; Dales's preliminary article 'Harappan outposts on the Makran coast' (Antiquity 36, 1962: "
        "86-92) is paywalled on Cambridge Core and was not read, and Possehl's compilations were not available. The "
        "Antiquity abstract page we fetched carried no dating information and was not kept. Directions and bearings of "
        "the walls given by Stein and Dales are deliberately not recorded."),
}

for slug, doc in (("allahdino", allahdino), ("sutkagen-dor", sutkagen)):
    path = TOWNS / (slug + ".json")
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", path)
