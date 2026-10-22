"""Generate experiments/2026-10-21-town-axes/dating-v1/towns/kuntasi.json."""
import json
import sys

OUT = sys.argv[1]

DHAV = ("Value taken from Kanungo and colleagues' Table 1, which cites Dhavalikar, Raval and Chitalwala 1996, Kuntasi: A "
        "Harappan Emporium on West Coast, p. 41; we could not obtain that report. ")

radiocarbon = [
    {"lab_no": "PRL-1370", "material": None, "context": "layer 12, 'middle level of period I, which marks the structural phase B'",
     "phase": "Period I", "age_bp_printed": 3820, "sigma_printed": 170, "half_life_printed": None,
     "age_bp_5568": None, "sigma_5568": None, "calibrated_published": "2291 BC", "curve": None,
     "source": "kanungo2025bhagatrav", "page": "pp. 59-61 (text) and p. 60 (Table 1)",
     "note": DHAV + ("The table prints '3820±170 BC' in the column headed 'Radiocarbon age (yr BP)' and does not state the "
                     "half-life, so the 5568 fields are left empty. The calibrated figure is a single year as printed; the "
                     "table footnote says calibrated dates are 'as in the original references and not recalculated'.")},
    {"lab_no": "BS-567", "material": None, "context": "'middle level of the period I'",
     "phase": "Period I", "age_bp_printed": None, "sigma_printed": None, "half_life_printed": None,
     "age_bp_5568": None, "sigma_5568": None,
     "calibrated_published": "2451-2356 BC; the Period I row adds 'Average 2451, 2433, 2392, 2384 and 2356 BC'",
     "curve": None, "source": "kanungo2025bhagatrav", "page": "p. 60 (Table 1), p. 61 (text)",
     "note": DHAV + "No radiocarbon age is printed for this Birbal Sahni Institute sample."},
]

parts = [
    {"part": "citadel mound fortification (whole settlement)",
     "layout_phase": "Period I (Mature Harappan); the structural phase within Period I is not stated in the sources we read",
     "what_was_built": (
         "The interim report of the first season states for Period I that 'the citadel mound was protected by a double "
         "fortification wall of stone rubble set in mud masonry', roughly squarish (93 m N-S by 83 m E-W), with a squarish "
         "watch tower at the south-western corner, an outer wall of large boulders and an inner wall of smaller stones; "
         "where the inner wall broadens and slopes and where a ramp joins the two walls on the east the excavators saw "
         "landing platforms (IAR 1987-88, p. 17). The second season reports 'a twin wall encircling the site' (IAR 1988-89, "
         "p. 11), and the third a gate 'with bastions' and a sloping ramp on the eastern part of the mound, without a "
         "period attribution in the summary (IAR 1989-90, p. 22)."),
     "locator": "iar1987-88 p. 17; iar1988-89 p. 11; iar1989-90 p. 22",
     "excavator_range_bce": [2400, 1900],
     "excavator_basis": (
         "The final report, which we know only through Kanungo and colleagues, gives Period I as 'layers 20-7, 2400-1900 "
         "BCE' (Dhavalikar et al. 1996: 27, quoted in kanungo2025bhagatrav p. 59), with radiocarbon dates of 2291 BC "
         "(PRL-1370, layer 12, structural phase B) and 2451-2356 BC (BS-567) from the middle of Period I (p. 41, quoted on "
         "kanungo2025bhagatrav pp. 59-61). The excavators' interim report had given Period I as 'c. 2300-1900 BC' without a "
         "stated basis (IAR 1987-88, p. 17), and the next season dated the whole settlement 'between circa 2200-1700 BC' "
         "'on the basis of the artefacts' (IAR 1988-89, p. 11)."),
     "radiocarbon": radiocarbon,
     "bayesian_start": None,
     "syntheses": [
         {"source": "kanungo2025bhagatrav", "page": "p. 59",
          "range_bce": [2400, 1900],
          "statement": ("Kanungo and colleagues place Kuntasi Period I as beginning 'from the end of the early Mature phase' "
                        "and covering 'the entire late Mature Harappan phase', with Period II (layers 6-1, 1900-1700 BCE) Late "
                        "Harappan, and count Kuntasi among Sorath Harappan settlements with fortifications that are not 'close "
                        "to what we get in Classic Harappan sites'."),
          "disagreement": None}],
     "conflicts": (
         "The excavators' own range for Period I moved from c. 2300-1900 BC (IAR 1987-88) to 2200-1700 BC for the whole "
         "settlement (IAR 1988-89) to 2400-1900 BCE in the final report as quoted by Kanungo and colleagues. The sources we "
         "read do not say in which part of Period I the fortification was built, so the radiocarbon dates from the middle "
         "of Period I bracket the occupation, not the wall.")},
]

first_occupation = {
    "phase": "Period I (Mature Harappan), from layer 20",
    "range_bce": [2400, 1900],
    "basis": ("Period I spans layers 20-7, 2400-1900 BCE in the final report (Dhavalikar et al. 1996: 27, quoted in "
              "kanungo2025bhagatrav p. 59); an open pottery kiln was found 'in the earliest levels of Period I' (IAR 1987-88, "
              "p. 18). The interim report gave c. 2300-1900 BC (IAR 1987-88, p. 17)."),
    "locator": "kanungo2025bhagatrav p. 59; iar1987-88 pp. 17-18",
}

IAR_BASE = "https://www.asiaurangabadcircle.com/assets/files/publications/"
LOCAL = "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/"
sources = [
    {"id": "kanungo2025bhagatrav",
     "citation": ("Kanungo, A. K., Kaushal, R. K., Bhushan, R., Chauhan, N., Kharakwal, J. S. and Ansari, S. 2025. "
                  "Luminescence and radiocarbon chronology of Bhagatrav: a Sorath Harappan camp site in South Gujarat. "
                  "Radiocarbon 67: 53-73. doi:10.1017/RDC.2024.119"),
     "url_or_path": ("https://www.cambridge.org/core/journals/radiocarbon/article/luminescence-and-radiocarbon-chronology-of-bhagatrav-a-sorath-harappan-camp-site-in-south-gujarat/F20A67111DE6F904BAD72BE922A6E78D ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-gujarat/bhagatrav2024radiocarbon.pdf"),
     "sha256": "aa69f2377f61d379322c3203deea65a2525afdc89ca1a18fe3f635d7418e38d0"},
]
for k, yr, sha, pages in [
        ("iar1987-88", "1987-1988", "fdb3eac83e5afe34ed3b99169ef3aa0d85d1281858797ec78f32c41375954573", "pp. 17-19 (35. Excavations at Kuntasi, District Rajkot)"),
        ("iar1988-89", "1988-1989", "265fccdf60788ada8945b3feefb6e7f16458b033db9e077ac46915a8fec12972", "p. 11 (24. Excavation at Kuntasi, District Rajkot)"),
        ("iar1989-90", "1989-1990", "b408f4212e23d66ea499ac828ebf14c7dee344c3251f1be32fda4bfe636e77e9", "pp. 22-23 (20. Excavations at Kuntasi, District Rajkot)")]:
    sources.append({"id": k,
                    "citation": ("Indian Archaeology %s - A Review. New Delhi: Archaeological Survey of India, %s. "
                                 "PDF of the ASI edition hosted by the ASI Aurangabad Circle; text read from the evidence-census "
                                 "page extraction." % (yr[:5] + yr[-2:], pages)),
                    "url_or_path": "%s%s.pdf ; %sIAR%s-ALT.pdf" % (IAR_BASE, yr, LOCAL, yr),
                    "sha256": sha})

notes = (
    "Kuntasi (Bibino Timbo), in Malia taluk in Rajkot district, was excavated by M. K. Dhavalikar, V. Shinde and S. Atre "
    "of Deccan College with M. H. Raval and Y. M. Chitalwala of the Gujarat State Department of Archaeology in "
    "seasons reported from 1987-88 to 1989-90. The final report, Dhavalikar, Raval and Chitalwala 1996, Kuntasi: A Harappan Emporium on West Coast "
    "(Deccan College), was not available to us: it is not on archive.org and we found only bookseller listings. We "
    "therefore rely on the three interim notes in Indian Archaeology: A Review and on the values Kanungo and colleagues "
    "quote from the final report. The fortification is assigned to Period I in the interim report, but we could not "
    "find which structural phase it belongs to. A third date, PRL-1371 (printed '3750±140 BC', calibrated 2145 BC, "
    "layer 5, Period II), is from the later period and is left out. Neither PRL-1370 nor PRL-1371 appears in the "
    "Physical Research Laboratory date lists in Radiocarbon, which end in 1991; no Bayesian model exists. Statements of "
    "wall direction in these sources were not recorded.")

doc = {"town": "kuntasi", "compiled_utc": "2026-10-21T05:25:00Z", "parts": parts,
       "first_occupation": first_occupation, "sources": sources, "notes": notes}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("wrote", OUT)
