"""Generate experiments/2026-10-21-town-axes/dating-v1/towns/rojdi.json."""
import json
import sys

OUT = sys.argv[1]


def rc(lab, material, context, phase, age, sig, hl, calib, curve, src, page, note=None):
    if age is None:
        a5568 = s5568 = None
    elif hl == 5730:
        a5568, s5568 = round(age / 1.03), round(sig / 1.03)
    else:
        a5568, s5568 = age, sig
    d = {"lab_no": lab, "material": material, "context": context, "phase": phase,
         "age_bp_printed": age, "sigma_printed": sig, "half_life_printed": hl,
         "age_bp_5568": a5568, "sigma_5568": s5568,
         "calibrated_published": calib, "curve": curve, "source": src, "page": page}
    if note:
        d["note"] = note
    return d


PRL_NOTE = ("PRL-VI gives the PRL number, identification number, depth and age only; the list states ages on the 5568-year "
            "half-life with 1950 as base year, errors from counting statistics, not corrected for 13C. The series comment "
            "reads 'samples dated to study Rojdi southern extension and post-urban phase'. The phase comes from Possehl and "
            "Raval's Table 2.")
P_CURVE = ("not named; Possehl and Raval's Table 1 footnote says the averages in their tables are from the M. Stuiver "
           "computer program distributed in 1986 (Stuiver and Pearson 1986)")


def prl(lab, ident, depth, age, sig, extra=""):
    return rc(lab, "charcoal", "identification no. %s, depth %s cm (trench not stated)" % (ident, depth), None,
              age, sig, 5568, None, None, "rc-prl-vi", "pp. 333-334 (Table 1)", note=(PRL_NOTE + " " + extra).strip())


def pos(lab, context, phase, age, sig, bc5730, calib, page="p. 12 (Table 2)", extra=""):
    return rc(lab, None, context, phase, age, sig, 5568, calib, P_CURVE, "possehl1989rojdi", page,
              note=("Possehl and Raval print this age under '5568 Half-life' and give %s B.C. under '5730 Half-life'. %s"
                    % (bc5730, extra)).strip())


layout_rc = [
    prl("PRL-1084", "2218", "86", 3700, 150),
    pos("PRL-1084", "Rojdi South Extension (Trench 76L), Upper Levels", "Rojdi C?", 3700, 145, 1860, "2350-1890 B.C.",
        extra="Possehl and Raval's sigma (145) differs from PRL-VI (150)."),
    prl("PRL-1088", "10126", "190-220", 3770, 120),
    pos("PRL-1088", "Rojdi Main Mound (Trench 45K), Middle levels", "Rojdi B?", 3770, 125, 1930, "2420-1980 B.C.",
        extra="Sigma differs from PRL-VI (120)."),
    prl("PRL-1083", "2248", "150-160", 3870, 120),
    pos("PRL-1083", "Rojdi South Extension (Trench 76L), Lower levels", "Rojdi B?", 3875, 125, 2040, "2640-2160 B.C.",
        extra="Age and sigma differ from PRL-VI (3870 ± 120)."),
    prl("PRL-1282", "10481", "131", 3470, 140),
    pos("PRL-1282", "Rojdi Main Mound (Trench 46L), Middle Levels", "Rojdi B", 3470, 140, 1620, "2000-1665 B.C."),
    prl("PRL-1281", "10483", "140", 3520, 110),
    pos("PRL-1281", "Rojdi Main Mound (Trench 46L), Middle Levels", "Rojdi B", 3520, 110, 1680, "2015-1710 B.C."),
    rc("TF-200", "charcoal (NaOH pretreatment also given)",
       "Trench B, Locus VII-IX, Layer 3, depth .65 m, Field No. Mound I/Tr.B/5", "Phase B of Period I",
       3810, 110, 5568, None, None, "rc-tf-iii", "p. 294",
       note=("Printed as 1860 B.C. (5568, A.D. 1950). From the 1962-63 excavation by J. M. Nanavati (Gujarat State "
             "Department of Archaeology); no source we read equates this Phase B with Possehl and Raval's Rojdi B.")),
    rc("TF-200", None, "Rojdi Trench B, 1962/63 season", "Period I, Phase B", 3810, 110, 5568, "2415-2135 B.C.", P_CURVE,
       "possehl1989rojdi", "p. 13 (Table 3)", note="5730 column: 1975 B.C."),
    rc("TF-200", "charcoal", "Mound I, Trench B/5, VII-IX, layer 3, depth 0.65 m", "Harappan Period I, Sub-phase B",
       3810, 110, 5568, None, None, "ramachandran1975radiocarbon", "p. 120",
       note="Also printed: (3920 ± 125) B.P. on 5730 and 1970 ± 125 B.C.; the 5730 sigma differs from IAR 1962-63 (115)."),
    rc("TF-200", None, None, "Period I, Sub-phase B", None, None, 5730, None, None, "iar1962-63", "p. 8",
       note=("The excavation report gives only '1970± 115' B.C., 'calculated at 5730 as half-life value', without "
             "stating the reference year, so the BP fields are empty.")),
    rc("TF-199", "charcoal (rootlets handpicked; NaOH pretreatment also given)",
       "Trench C, Pit 2 sealed by Layer 4, depth 1.75 m, Field No. Mound III/Tr.C/4", "Phase B of Period I",
       3590, 100, 5568, None, None, "rc-tf-iii", "p. 294",
       note="Printed as 1640 B.C. (5568, A.D. 1950). 1962-63 excavation by J. M. Nanavati."),
    rc("TF-199", None, "Rojdi Trench C, 1962/63 season", "Period I, Phase B", 3590, 110, 5568, "2160-1850 B.C.", P_CURVE,
       "possehl1989rojdi", "p. 13 (Table 3)", note="5730 column: 1745 B.C. Sigma (110) differs from TF-III (100)."),
    rc("TF-199", "charcoal", "Mound III, Trench C, pit 2 sealed by layer 4, depth '1.75 cm' [sic]",
       "Harappan Period I, 'Sub-phase 3' [sic]", 3590, 100, 5568, None, None, "ramachandran1975radiocarbon", "p. 120",
       note="Also printed: (3695 ± 105) B.P. on 5730 and 1745 ± 105 B.C."),
    rc("TF-199", None, None, "Period I, Sub-phase B", None, None, 5730, None, None, "iar1962-63", "p. 8",
       note="The excavation report gives only '1745 ± 105 B.C.' on the 5730-year half-life, reference year not stated."),
]

phaseA_rc = [
    prl("PRL-1089", "10161", "236-243", 3870, 120),
    pos("PRL-1089", "Rojdi Main Mound (Trench 45K), Lower levels", "Rojdi A", 3865, 115, 2030, "2640-2150 B.C.",
        extra="Possehl and Raval mark this number with an asterisk that we could not resolve. Age and sigma differ from PRL-VI."),
    prl("PRL-1093", "10137", "237-243", 3920, 110),
    pos("PRL-1093", "Rojdi Main Mound (Trench 45K), Lower levels", "Rojdi A", 3920, 105, 2090, "2645-2310 B.C.",
        extra="Sigma differs from PRL-VI (110)."),
    prl("PRL-1091", "10148", "236-244", 4150, 110,
        extra=("This determination is not in Possehl and Raval's Table 2. Its depth matches PRL-1089 and PRL-1093, "
               "which they assign to the lower levels of Trench 45K (Rojdi A), but no source we read gives its phase.")),
    prl("PRL-1087", "10173", "244-276", 4010, 110),
    pos("PRL-1087", "Rojdi Main Mound (Trench 45K), Lower levels", "Rojdi A", 4010, 105, 2180, "2680-2515 B.C.",
        extra="Sigma differs from PRL-VI (110)."),
    prl("PRL-1085", "10184", "280-288", 4020, 110),
    pos("PRL-1085", "Rojdi Main Mound (Trench 45K), Lower levels", "Rojdi A", 4020, 105, 2190, "2680-2515 B.C.",
        extra="Sigma differs from PRL-VI (110). Possehl and Raval give 'Average for Lowest levels: 2469 B.C.' for Trench 45K."),
    prl("PRL-1285", "10769", "257", 3740, 140),
    pos("PRL-1285", "Rojdi Main Mound (Trench 46L), Lower Levels", "Rojdi A", 3740, 140, 1900, "2410-1945 B.C."),
    prl("PRL-1284", "10768", "263", 3810, 100),
    pos("PRL-1284", "Rojdi Main Mound (Trench 46L), Lower Levels", "Rojdi A", 3810, 100, 1980, "2415-2135 B.C."),
    prl("PRL-1283", "10763", "207", 3980, 100),
    pos("PRL-1283", "Rojdi Main Mound (Trench 46L), Lower Levels", "Rojdi A", 3980, 100, 2140, "2660-2385 B.C."),
]

SYN = [
    {"source": "possehl1989rojdi", "page": "pp. 11-13, 171",
     "range_bce": [2000, 1700],
     "statement": ("Possehl and Raval's own synthesis: Rojdi A (2500-2200 B.C.) and Rojdi B (2200-2000 B.C.) are the "
                   "'Sorath Harappan', a regional expression of the Urban Phase, and Rojdi C (2000-1700 B.C.) has pottery "
                   "'characteristic of the early Post-urban'. The ranges rest on the calibrated PRL and TF dates."),
     "disagreement": None},
    {"source": "mandal1972radiocarbon", "page": "pp. 66-67",
     "range_bce": None,
     "statement": ("Mandal notes that there is no C14 date for Phase A of the 1950s-60s excavations and doubts both Phase B "
                   "dates: TF-199 from Pit 2 sealed by layer 4 is younger than TF-200 from layer 3 by about 225 years, "
                   "which he calls 'real' at 95% confidence, and he concludes there is 'doubt about the validity of both dates'."),
     "disagreement": "Rejects the only radiocarbon dates the earlier excavators had for the phase before the enclosure."},
    {"source": "kanungo2025bhagatrav", "page": "pp. 59-61",
     "range_bce": [2200, 1900],
     "statement": ("Kanungo and colleagues list fortifications 'around some settlements, including Kuntasi, Rojdi, and "
                   "Pithad/Jaidak but none are close to what we get in Classic Harappan sites', reprint Possehl and Raval's "
                   "Rojdi dates, and write that 'Rojdi-B has been dated by 14C to 2200-1900 BCE (Possehl and Raval 1989, 12)', "
                   "following Dhavalikar and colleagues (1996: 32)."),
     "disagreement": ("Ends Rojdi B at 1900 BCE where Possehl and Raval end it at 2000 B.C. (p. 171), which would move the "
                      "start of Rojdi C, and so the enclosure, a century later.")},
]

parts = [
    {"part": "circumvallation and gateway (whole settlement)",
     "layout_phase": "Rojdi C, 'possibly the early part of this period' (Possehl and Raval's ceramic phase)",
     "what_was_built": (
         "A circumvallation of large basalt boulders, set in shallow foundation trenches as a double line 1.5 to 2 m apart "
         "packed with rammed earth and rubble, which 'encloses the entire settlement, save for the river side', with a "
         "double-bastioned gateway on the west (possehl1989rojdi pp. 27-29). The gateway excavation showed that the "
         "circumvallation and gateway 'post-date the earliest Harappan occupation at Rojdi' (p. 29). The Large Square "
         "Building on the North Slope was built in the same architectural period, on the same hard black-soil surface "
         "(p. 29), and the excavators conclude that the Large Square Building, gateway and circumvallation 'were all built "
         "very close to one another in time and date to Rojdi C, possibly the early part of this period' (p. 140). The "
         "large building of Architectural Subphase 2b on the Main Mound, cut into the last Rojdi B stratum of trench 46L, "
         "opens Rojdi C, and all building on the South Extension is Rojdi C (p. 130); together these are 'the main "
         "architectural period' and 'were built near the end of the protohistoric occupation of the site' (p. 50). The "
         "boulder wall was first noticed in 1957-58, when the mound 'was scraped at several places and revealed the remains "
         "of a protection-wall made of big boulders' (IAR 1957-58, p. 18)."),
     "locator": "possehl1989rojdi pp. 27-29, 50, 130, 140, 171 (Table 35); iar1957-58 p. 18",
     "excavator_range_bce": [2000, 1700],
     "excavator_basis": (
         "Ceramic correlation tied to radiocarbon. The pottery from the gateway and from the trenches joining the "
         "circumvallation and the Large Square Building is Rojdi C, with a few possibly late Rojdi B pieces from weathered "
         "near-surface strata (pp. 131, 140). Rojdi C is dated 2000-1700 B.C. as one of 'the basic dates for the ceramic "
         "phases', which combine the relative sequence with the calibrated radiocarbon dates of Tables 1-3 (p. 171). No "
         "radiocarbon sample comes from the wall itself."),
     "radiocarbon": layout_rc,
     "bayesian_start": None,
     "syntheses": SYN,
     "conflicts": (
         "Two excavation programmes use different phase schemes. P. P. Pandya (1957-59) and J. M. Nanavati (1962-63) "
         "divided Period I into Phases A, B and C (IAR 1958-59, pp. 19-20; IAR 1962-63, p. 8), while Possehl and Raval "
         "(1982-86) use the ceramic phases Rojdi A, B and C; we found no explicit concordance, so the TF-199 and TF-200 "
         "dates from the earlier Phase B are listed beside Possehl and Raval's Rojdi B dates without equating them. Within "
         "Rojdi B, PRL-1281 and PRL-1282 calibrate to 2015-1710 and 2000-1665 B.C. in Possehl and Raval's own table, "
         "inside their Rojdi C range rather than their Rojdi B range of 2200-2000 B.C. Mandal rejects TF-199 and TF-200 as "
         "stratigraphically inverted. Possehl and Raval reprint several PRL ages and sigmas slightly differently from the "
         "laboratory list (PRL-1083, PRL-1084, PRL-1088), and TF-199 with a sigma of 110 where TF-III prints 100. Kanungo "
         "and colleagues end Rojdi B at 1900 BCE instead of 2000 B.C. In Possehl and Raval's scheme the enclosure belongs "
         "to the early Post-urban, not to the Urban Phase.")},
    {"part": "main mound house platform (1957-63 excavations)",
     "layout_phase": "Period I, Phase A (Pandya and Nanavati)",
     "what_was_built": (
         "The first settlers 'built a 2-ft. high mud platform, capped by rammed earth and lime, to carry their mud and "
         "mud-brick houses' (IAR 1958-59, p. 19); in 1962-63 the Phase A 'mud-platform was found to support a succession "
         "of seven lime-floorings alternated with mud-ramming' (IAR 1962-63, p. 8). This is a house platform in the "
         "excavated part of the main mound, not a planned layout; Phase B followed 'after the destruction of the previous "
         "Phase by fire' with rubble and mud structures (IAR 1958-59, p. 19)."),
     "locator": "iar1958-59 pp. 19-20; iar1962-63 p. 8",
     "excavator_range_bce": None,
     "excavator_basis": (
         "The 1957-63 excavators published no date for Phase A; the two radiocarbon dates of 1962-63 are from Phase B "
         "(IAR 1962-63, p. 8; Mandal 1972, p. 66). The radiocarbon entries below are the lower-level Main Mound dates of "
         "the 1982-86 excavation, which Possehl and Raval assign to Rojdi A (2500-2200 B.C., p. 171); that this Rojdi A is "
         "the same horizon as the earlier Phase A platform is our assumption, not a published statement."),
     "radiocarbon": phaseA_rc,
     "bayesian_start": None,
     "syntheses": [SYN[0]],
     "conflicts": ("PRL-1091 (4150 ± 110 BP) appears in PRL-VI at the depth of the Trench 45K Rojdi A samples but is "
                   "omitted from Possehl and Raval's Table 2 without comment; PRL-1089, PRL-1093, PRL-1087 and PRL-1085 are "
                   "reprinted with sigmas 5 years smaller than in PRL-VI.")},
]

first_occupation = {
    "phase": "Rojdi A (Possehl and Raval); Period I, Phase A of the 1957-63 excavations",
    "range_bce": [2500, 2200],
    "basis": (
        "Calibrated radiocarbon with the ceramic sequence: 'Rojdi A: 2500-2200 B.C.' (p. 171), with 'Average for Lowest "
        "levels: 2469 B.C.' for Trench 45K (p. 12, Table 2). Table 35 places Architectural Subphase 1a (a floor in 45K and a "
        "hearth in 46L) directly on virgin soil. Rojdi A pottery is 'quite similar to the pottery of Rangpur IIA' (p. 12)."),
    "locator": "possehl1989rojdi pp. 12, 171 (Table 35); iar1958-59 p. 19",
}

RC = {
    "rc-tf-iii": ("Agrawal, D. P., Kusumgar, S. and Lal, D. 1965. Tata Institute Radiocarbon Date List III. Radiocarbon 7: 291-295. doi:10.1017/s0033822200037279",
                  "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/TF-III.pdf",
                  "83ba490e67cf215319092b8bf2c6e782118f3a521dce73c3bcb3aed00dfc8855"),
    "rc-prl-vi": ("Agrawal, D. P., Kusumgar, S. and Yadava, M. G. 1991. Physical Research Laboratory Radiocarbon Date List VI. Radiocarbon 33(3): 329-344. doi:10.1017/s0033822200040352",
                  "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/PRL-VI.pdf",
                  "2538a056b3d310776e6dde565b78760a98a08d859f3f6b28e2716beaf4c81d03"),
}
sources = [{"id": k, "citation": c, "url_or_path": p, "sha256": s} for k, (c, p, s) in RC.items()]
sources += [
    {"id": "possehl1989rojdi",
     "citation": ("Possehl, G. L. and Raval, M. H. 1989. Harappan Civilization and Rojdi. Leiden: E. J. Brill; New Delhi: "
                  "Oxford & IBH (Tables 2-3, pp. 12-13; Gateway and Large Square Building, pp. 27-33; architectural "
                  "summary p. 50; correlation pp. 130-140; Table 35, p. 171). Printed page = PDF page - 10."),
     "url_or_path": ("https://archive.org/details/harappan-civilization-and-rojdi ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-gujarat/possehl1989rojdi.pdf"),
     "sha256": "532d56f5c4ef8334f92572363901a620ff8173621c5cc7261d8d953f2fd6aac6"},
    {"id": "ramachandran1975radiocarbon",
     "citation": ("Ramachandran, K. S. 1975. Radiocarbon Dates of Archaeological Sites in India. Archaeological Series 42. "
                  "New Delhi: Archaeological Survey of India (Rojdi, pp. 119-120)."),
     "url_or_path": ("https://archive.org/download/RadiocarbonDatesOfArchaeologicalSitesInIndia/RadiocarbonDatesOfArchaeologicalSitesInIndia.pdf ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-compilations/ramachandran1975.pdf"),
     "sha256": "4f9b4090cfbf627acc32a76d1b42b7ff742975b1abd2ee8e8b704aa5376a71d6"},
    {"id": "mandal1972radiocarbon",
     "citation": ("Mandal, D. 1972. Radiocarbon Dates and Indian Archaeology. Allahabad: Vaishali Publishing House "
                  "(Rojdi, pp. 66-67). Read from the archive.org text layer."),
     "url_or_path": ("https://archive.org/details/bpvu_radiocarbon-dates-and-indian-archaeology-by-d-mandal-archaeology-allahabad- ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-compilations/mandal1972_djvu.txt"),
     "sha256": "bdd9c423048bb5bd2772d35be80847008d6a62b0862526b4241b466ab5240ac4"},
    {"id": "kanungo2025bhagatrav",
     "citation": ("Kanungo, A. K., Kaushal, R. K., Bhushan, R., Chauhan, N., Kharakwal, J. S. and Ansari, S. 2025. "
                  "Luminescence and radiocarbon chronology of Bhagatrav: a Sorath Harappan camp site in South Gujarat. "
                  "Radiocarbon 67: 53-73. doi:10.1017/RDC.2024.119"),
     "url_or_path": ("https://www.cambridge.org/core/journals/radiocarbon/article/luminescence-and-radiocarbon-chronology-of-bhagatrav-a-sorath-harappan-camp-site-in-south-gujarat/F20A67111DE6F904BAD72BE922A6E78D ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-gujarat/bhagatrav2024radiocarbon.pdf"),
     "sha256": "aa69f2377f61d379322c3203deea65a2525afdc89ca1a18fe3f635d7418e38d0"},
]
IAR_BASE = "https://asiaurangabadcircle.com/assets/files/publications/"
for k, yr, sha, pages in [
        ("iar1957-58", "1957-1958", "f67de821414337af7688ad33d41ea1221b57fa2fbba903310987bfff53f45ad3", "p. 18 (exploration and trial excavation at Rojdi)"),
        ("iar1958-59", "1958-1959", "b1443108517d42280412f804c4a9fa29f7cb8f8ab45fdb3fc58f0a2535c46b9b", "pp. 19-20 (16. Excavation at Rojdi, District Madhya Saurashtra)"),
        ("iar1962-63", "1962-1963", "328a3cbf50af8b894c15aea8320a669c0619d647c5bbd0763d6ff72e99ce5a72", "p. 8 (19. Excavation at Rojdi, District Rajkot)")]:
    sources.append({"id": k,
                    "citation": ("Ghosh, A. (ed.). Indian Archaeology %s - A Review. New Delhi: Archaeological Survey of "
                                 "India, %s. PDF of the ASI edition hosted by the ASI Aurangabad Circle." % (yr[:5] + yr[-2:], pages)),
                    "url_or_path": "%s%s.pdf ; data/raw/2026-10-21-town-axes/dating/shared-iar/iar%s.pdf" % (IAR_BASE, yr, yr),
                    "sha256": sha})

notes = (
    "Rojdi, on the Bhadar river in Rajkot district, was excavated by P. P. Pandya in 1957-59, by J. M. Nanavati of "
    "the Gujarat State Department of Archaeology in 1962-63, and by M. H. Raval and G. L. Possehl in 1982-86. "
    "We record two parts. The planned element that matters for the town table is the boulder circumvallation with its "
    "gateway, which Possehl and Raval date by its pottery to Rojdi C, the early Post-urban phase, together with the main "
    "architectural period on the Main Mound and the South Extension; it is not a Mature Harappan layout. The second part "
    "is the house platform that the earlier excavators found under the first settlement, recorded so that the earliest "
    "built level has its dates beside it. "
    "Radiocarbon: the Physical Research Laboratory published fourteen Rojdi determinations in PRL-VI without context or "
    "phase; Possehl and Raval give trench, level and phase for twelve of them, on the 5568-year half-life with a "
    "5730-based B.C. column and calibrated ranges. Their 5568 column for Rojdi matches the laboratory list, which "
    "confirms that the different-looking Lothal ages in their Table 1 are 5730-based. Two PRL-VI numbers are absent from "
    "Possehl and Raval: PRL-1091 (listed here with the Phase A part) and PRL-1081, 2360 ± 210 BP at 46-52 cm, which "
    "we leave out as probably later. Rojdi A dates are listed only with the platform part, and the circumvallation part "
    "carries the Rojdi C date and the Rojdi B and Phase B dates of the phase immediately before. We found no Bayesian "
    "model for Rojdi. Statements of wall direction in these sources were not recorded.")

doc = {"town": "rojdi", "compiled_utc": "2026-10-21T05:05:00Z", "parts": parts,
       "first_occupation": first_occupation, "sources": sources, "notes": notes}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("wrote", OUT, len(layout_rc), len(phaseA_rc))
