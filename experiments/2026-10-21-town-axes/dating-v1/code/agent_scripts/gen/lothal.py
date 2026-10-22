"""Generate experiments/2026-10-21-town-axes/dating-v1/towns/lothal.json."""
import json
import sys

OUT = sys.argv[1]


def rc(lab, material, context, phase, age, sig, hl, calib, curve, src, page, note=None, cited_via=None):
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
    if cited_via:
        d["cited_via"] = cited_via
    return d


def mandal(lab, phase, bc, sig, page, extra=""):
    bp5730 = bc + 1950
    d = rc(lab, None, None, phase, None, None, 5730, None, None,
           "mandal1972radiocarbon", page,
           note=("Mandal prints only %d ± %d B.C., on the 5730-year half-life with A.D. 1950 as reference year "
                 "(stated p. 7). This implies %d ± %d BP on 5730, which we convert to the 5568 fields. %s"
                 % (bc, sig, bp5730, sig, extra)).strip())
    d["age_bp_5568"] = round(bp5730 / 1.03)
    d["sigma_5568"] = round(sig / 1.03)
    return d


def rao(lab, phase, bc, sig, context, note_extra="", material=None):
    return rc(lab, material, context, phase, None, None, 5730, None, None, "rao1979lothal", "p. 39",
              note=("Rao's table prints only '%d±%d' under 'B.C. dates based on half life 5730' and does not state "
                    "the reference year, so the BP fields are left empty. %s" % (bc, sig, note_extra)).strip())


POSSEHL_NOTE = ("Possehl and Raval print this age in a column headed '5568 Half-life', but it equals the Tata Institute "
                "5568-year age multiplied by 1.03, so it is a 5730-based age; we therefore set half_life_printed to 5730 "
                "and divide by 1.03. The printed sigma is the unscaled 5568 sigma, so the converted sigma is slightly too "
                "small. The calibrated range was evidently computed from the 5730-based age.")
POSSEHL_CURVE = ("not named; the Table 1 footnote says the averages are from the M. Stuiver computer program "
                 "distributed in 1986 (Stuiver and Pearson 1986)")

phase_I = [
    rc("TF-136", "charcoal (the list comment describes TF-133, TF-135 and TF-136 as charcoal mixed with soil)",
       "Trench SRG2, Locus AX33, Layer 10, depth 3.0 m, Field No. 78", "Phase I, Period A",
       3915, 130, 5568, None, None, "rc-tf-iii", "p. 294",
       note=("Printed as 1965 B.C. (5568, A.D. 1950). The list comment says TF-133, TF-135 and TF-136 were "
             "wet-combusted and 'contamination by younger carbon is not unlikely in these samples'.")),
    rao("TF-136", "Period A, Phase I (second series)", 2080, 135, None,
        "Rao rejects all three 'second series' dates (TF-136, TF-135, TF-133) 'perhaps because the samples are contaminated' (p. 39)."),
    rc("TF-136", "charcoal mixed with earth", "Trench SRG 2, AX 33, layer 10, depth 3.0 m. Field no. 78",
       "Mature Harappan, Phase A", 3915, 130, 5568, None, None, "ramachandran1975radiocarbon", "p. 83",
       note="Also printed: (4030 ± 135) B.P. on 5730 and 2080 ± 135 B.C."),
    mandal("TF-136", "late level of Phase I, Period A or I", 2080, 135, "pp. 64-65",
           "Mandal treats this date as the lower limit of the Harappa culture at Lothal (p. 66)."),
    rc("TF-136", None, None, "Lothal A", 4032, 130, 5730, "2655-2185 B.C.", POSSEHL_CURVE,
       "possehl1989rojdi", "p. 10 (Table 1)", note=POSSEHL_NOTE + " The 5730 column gives 2080 B.C."),
]

phase_II = [
    rc("TF-135", "charcoal (mixed with soil, per the list comment)",
       "Trench SRG2, Locus AX33, Layer 9, depth 2.5 m, Field No. 77", "waterlogged deposits of Phase II, Period A",
       3405, 125, 5568, None, None, "rc-tf-iii", "p. 294",
       note="Printed as 1455 B.C. Wet-combusted; possible contamination by younger carbon (list comment)."),
    rao("TF-135", "Period A, Phase IIA (second series)", 1555, 135, None,
        "Rao calls the IIA date 'more strange' than the others and rejects the second series (p. 39)."),
    mandal("TF-135", "early level of Phase II, Period A or I", 1555, 130, "pp. 64-65",
           "Mandal excludes TF-133 and TF-135 as 'a case either of contamination or of scatter' (p. 66). "
           "Ramachandran 1975 does not list TF-135."),
    rc("TF-135", None, None, "Lothal A", 3507, 125, 5730, "1950-1570 B.C.", POSSEHL_CURVE,
       "possehl1989rojdi", "p. 10 (Table 1)", note=POSSEHL_NOTE + " The 5730 column gives 1555 B.C."),
    rc("TF-133", "charcoal (mixed with soil, per the list comment)",
       "Trench SRG2, Locus AX33, Layer 6, depth 1.35 m, Field No. 75", "disturbed level of Phase II, Period A",
       3740, 110, 5568, None, None, "rc-tf-iii", "p. 294",
       note="Printed as 1790 B.C. Wet-combusted; possible contamination by younger carbon (list comment)."),
    rao("TF-133", "Period A, Phase IIB (second series)", 1895, 115, None, "Rejected by Rao with the second series (p. 39)."),
    rc("TF-133", "charcoal with earth", "Trench SRG-2, AX 33, layer 6, depth 1.37 m. Field no. 75",
       "Mature Harappan, Phase A", 3740, 110, 5568, None, None, "ramachandran1975radiocarbon", "p. 84",
       note="Also printed: (3845 ± 115) B.P. on 5730 and 1895 ± 115 B.C. The depth differs from the 1.35 m of TF-III."),
    mandal("TF-133", "late level of Phase II, Period A or I", 1895, 115, "pp. 64-65"),
    rc("TF-133", None, None, "Lothal A", 3850, 110, 5730, "2340-1980 B.C.", POSSEHL_CURVE,
       "possehl1989rojdi", "p. 10 (Table 1)", note=POSSEHL_NOTE + " The 5730 column gives 1900 B.C."),
]

IIIB_NOTE = ("Phase IIIB is two sub-phases after the layout phase. We include it because Rao takes these three dates "
             "as the radiocarbon anchor ('2000 B.C. (TF 26, TF 27) as the central date for Period A') from which he "
             "counts back to the start of Phase II (p. 44).")
phase_IIIB = [
    rc("TF-22", "charcoal (mixed with soil)",
       "Trench No. SRG2, Locus E 13/9 (sealing wall of Phase III), depth 1.88 m, Field No. 29; loose ashy layer sealing flood debris and wall of Phase IIIB",
       "End of Phase IIIB (Period I)", 3845, 110, 5568, None, None, "rc-tf-i", "p. 277",
       note=IIIB_NOTE + " Printed as 1895 B.C. Kusumgar, Lal and Sarna (1963: 149) print the same age with 3960 ± 115 on 5730."),
    rao("TF-22", "Period A, Phase IIIB (first series)", 2010, 115,
        "loose ashy layer 9 of SRG 2, E13, sealing the remnants of the mud-brick wall of phase IIIB (fig. 7)",
        "Rao reads this layer of silt and flood debris as marking 'the end of the heyday of Lothal A'.", material="charcoal"),
    rc("TF-22", "charcoal with soil", "Trench SRG 2, E 13/9, sealing wall of phase III, depth 1.88 m. Field no. 29",
       "Mature Harappan, Phase A", 3845, 110, 5568, None, None, "ramachandran1975radiocarbon", "p. 83",
       note=("Also printed: (3960 ± 115) B.P. on 5730 and '1895±115 B.C.'; the B.C. figure does not follow "
             "from the 5730 age (which gives 2010 B.C.) and appears to be a misprint.")),
    mandal("TF-22", "late level of Phase III, Period A or I", 2010, 115, "pp. 64-65"),
    rc("TF-22", None, None, "Lothal A", 3960, 110, 5730, "2430-2165 B.C.", POSSEHL_CURVE,
       "possehl1989rojdi", "p. 10 (Table 1)", note=POSSEHL_NOTE + " The 5730 column gives 2010 B.C."),
    rc("TF-27", "charcoal (mixed with mud and dirt)",
       "Trench No. SRG2, Locus D13/7A, depth 1.98 m, Field No. 32A; flood debris, loam etc. accumulated against wall of IIIB",
       "Phase IIIB (Period I)", 3840, 110, 5568, None, None, "rc-tf-i", "p. 277",
       note="Printed as 1890 B.C. Kusumgar, Lal and Sarna (1963: 149) print 3950 ± 115 on 5730."),
    rao("TF-27", "Period A, Phase IIIB (first series)", 2005, 115,
        "layer 7A of D 13 of SRG 2, a flood deposit sealing a mud-brick house of phase IIIB"),
    rc("TF-27", "charcoal with mud and dirt", "Trench SRG-2, D 13/7A, depth 1.98 m. Field no. 32 A",
       "Mature Harappan, Phase A", 3840, 110, 5568, None, None, "ramachandran1975radiocarbon", "pp. 83-84",
       note="Also printed: (3950 ± 115) B.P. on 5730 and 2000 ± 115 B.C."),
    mandal("TF-27", "late level of Phase III, Period A or I", 2000, 115, "pp. 64-65"),
    rc("TF-27", None, None, "Lothal A", 3955, 110, 5730, "2425-2160 B.C.", POSSEHL_CURVE,
       "possehl1989rojdi", "p. 10 (Table 1)", note=POSSEHL_NOTE + " The 5730 column gives 2005 B.C."),
    rc("TF-26", "charcoal (coarse and fine grain)",
       "Trench SRG2, Locus D.13/7A, depth 1.98 m to 2.26 m, Field No. 32; flood debris and loam accumulated against wall of IIIB",
       "Phase IIIB (Period I)", 3830, 120, 5568, None, None, "rc-tf-i", "p. 277",
       note="Printed as 1880 B.C. Kusumgar, Lal and Sarna (1963: 149) print 3950 ± 125 on 5730."),
    rao("TF-26", "Period A, Phase IIIB (first series)", 1995, 115,
        "a second sample from layer 7A of D 13 of SRG 2",
        "Rao's sigma (115) differs from the 125 that the 5730 conversion of the TF-I sigma (120) gives."),
    rc("TF-26", "charcoal coarse and fine grain",
       "Trench SRG 2, D 13/AA, depth 1.98-2.26 m., sample from flood debris and loam deposited against wall of phase III B. Field no. 32",
       "Mature Harappan, Phase A", 3830, 120, 5568, None, None, "ramachandran1975radiocarbon", "p. 84",
       note="Also printed: (3950 ± 125) B.P. on 5730 and 2000 ± 125 B.C. The locus is printed 'D 13/AA' rather than D 13/7A."),
    mandal("TF-26", "late level of Phase III, Period A or I", 2000, 125, "pp. 64-65"),
    rc("TF-26", None, None, "Lothal A", 3945, 120, 5730, "2425-2195 B.C.", POSSEHL_CURVE,
       "possehl1989rojdi", "p. 10 (Table 1)", note=POSSEHL_NOTE + " The 5730 column gives 1995 B.C."),
]

ALL_RC = phase_I + phase_II + phase_IIIB

SYN_COMMON = [
    {"source": "rc-tf-i", "page": "pp. 276-277", "range_bce": [2500, 1500],
     "statement": ("The first Tata Institute list, describing the samples Rao collected, reports that 'on archaeological "
                   "evidence' Period I (later Rao's Period A, Phases I-IV) was dated ca. 2500-1500 B.C. and Period II "
                   "ca. 1500-1000 B.C., and comments that the C14 dates show the upper levels of Period I and all of "
                   "Period II to have been placed too late."),
     "disagreement": ("This pre-radiocarbon range for Period I as a whole begins 50 years before Rao's 1979 date for "
                      "Phase I and ends 400 years after his 1979 end of Period A (1900 B.C.).")},
    {"source": "rao1979lothal", "page": "p. 37",
     "range_bce": [2200, 1700],
     "statement": ("Rao reports that D. P. Agrawal (1964, 'Harappa Culture: New Evidence for a Shorter Chronology', Science; not consulted by us), 'relying entirely on C-14 dates', proposed a maximum spread of 2200-1700 B.C. "
                   "for the peripheral Harappa Culture, Lothal and Kalibangan included."),
     "disagreement": ("Rao rejects this as ignoring the archaeological evidence that takes the beginning of the Harappa "
                      "Culture back to 2500 B.C.; it puts the whole Harappan occupation of Lothal after Rao's date for "
                      "the layout.")},
    {"source": "mandal1972radiocarbon", "page": "pp. 64-66, 74-75", "range_bce": [2200, 1800],
     "statement": ("Using the nine Tata Institute dates on the 5730-year half-life, uncalibrated, Mandal dates the Harappa "
                   "culture at Lothal to c. 2200-1800 B.C. The lower limit comes from TF-136 (late level of Phase I, "
                   "2080 ± 135 B.C., 'within one standard deviation c. 2200 B.C.'), which he notes is 'not the lowest' "
                   "level; he excludes TF-133 and TF-135 from Phase II as contamination or scatter."),
     "disagreement": ("Mandal's start is about 250 years younger than Rao's 2450 B.C. for Phase I and 150 years younger "
                      "than Rao's 2350 B.C. for the layout in Phase IIa.")},
    {"source": "possehl1989rojdi", "page": "p. 10 (text and Table 1)", "range_bce": [2500, 2300],
     "statement": ("Possehl and Raval write that the radiocarbon determinations from Lothal and Surkotada 'can be used to "
                   "suggest that the Urban Phase Sindhi Harappans settled in Gujarat, including Kutch, ca. 2500-2300 B.C.'; "
                   "their averaged calibrated intercepts for Lothal A are 2452, 2427, 2395, 2374 and 2366 B.C. and for "
                   "Lothal B 2275, 2210 and 2207 B.C."),
     "disagreement": ("The calibrated settlement date agrees with Rao's 2450 B.C. for Phase I, but it rests on ages printed "
                      "under a '5568 Half-life' heading that are in fact 5730-based, which makes each calibration older "
                      "than the 5568 ages warrant. The table does not separate Rao's phases within Lothal A.")},
    {"source": "frenez2005lothal", "page": "pp. 68-69", "range_bce": [2350, 2200],
     "statement": ("Frenez and Tosi restate Rao's sequence as Period A-I (ca. 2450-2350 BC), A-II (ca. 2350-2200 BC), when "
                   "the town was enclosed by a mud-brick enclosure and buildings were raised on box-like platforms, A-III "
                   "(2200-2000 BC), A-IV (2000-1900 BC) and Period B (ca. 1800-1600 BC); the platform under the "
                   "'warehouse' was 'probably built in the first stage of Period A-II', and the brick-lined basin was "
                   "excavated in Period A-II."),
     "disagreement": ("No chronological disagreement; they follow Rao 1979 (citing p. 28) and read his 2200 B.C. as the end "
                      "of Phase II. They question the dock interpretation of the basin, not its date.")},
    {"source": "kanungo2025bhagatrav", "page": "pp. 60, 62", "range_bce": None,
     "statement": ("Kanungo and colleagues reprint Possehl and Raval's Lothal values in a table headed 'Radiocarbon age "
                   "(yr BP)' with the calibrated ranges 'as in the original references and not recalculated', and quote "
                   "Rao (1962: 15) that it is a 'certainty that the Harappans came to Lothal for trade or colonizing in "
                   "2450 B.C.'"),
     "disagreement": ("No new dates; the reprint carries forward the 5730-based ages as if they were conventional ages.")},
]

SYN_DOCK = SYN_COMMON + [
    {"source": "das2022seawater", "page": "abstract", "range_bce": None,
     "statement": ("From a 'well-dated vertical sediment trench' in the dockyard area, Das and colleagues infer a relative sea-level fall that 'initiated at 4150 ± 230 "
                   "and continued up to 3625 ± 200 yr BP' and 'likely dried this ancient Harappan dockyard'."),
     "disagreement": ("The study dates the end of the basin's marine connection rather than its construction; we could "
                      "read only the abstract, so the individual dates and their relation to Rao's phases are not recorded.")},
]

BASIS_IIA = ("Cross-dating and a stratigraphic count anchored on radiocarbon. Rao fixes Phase IIIB at about 2000 B.C. from "
             "TF-22, TF-26 and TF-27 on the 5730-year half-life and dates the end of Period A to 1900 B.C. (p. 39); "
             "for the earlier phases 'one has to rely on archaeological evidence' (p. 41): Sargonid-period contacts "
             "with Ur and Brak shown by Mesopotamian objects and Reserved Slip Ware in Phases II and III, the "
             "'Persian Gulf' seal, and the Tepe Yahya sherd dated 2320 B.C. (pp. 41-44). Allowing for three building "
             "sub-phases in Phase II and two in Phase III, he writes that 'the beginning of phase IIA may be dated to "
             "2200 B.C. and the beginning of phase II to 2350 B.C.' (p. 44). Phase IIa is the first sub-phase of Phase "
             "II and the dock is said to be 'constructed in circa 2350 B.C. in phase IIa' (p. 125), so we read 'IIA' "
             "in that sentence as a misprint for 'IIIA' and record 2350-2200 B.C. as Rao's range for Phase II, the "
             "reading Frenez and Tosi also adopt. Rao rejects the three radiocarbon dates from Phases I and II "
             "(p. 39). All B.C. figures are uncalibrated.")

CONFLICTS_IIA = (
    "Four disagreements bear on when the layout was built. (1) The excavator's date of about 2350 B.C. rests on "
    "cross-dating and a count of building sub-phases back from radiocarbon dates of about 2000 B.C. (5730, uncalibrated) "
    "for Phase IIIB; the only determinations from Phases I and II (TF-136, TF-135, TF-133) are out of order with each "
    "other and no older than the Phase IIIB dates, and Rao and Mandal set the Phase II dates aside while the Tata "
    "Institute list warns that all three wet-combusted samples may contain younger carbon. (2) Mandal's radiocarbon "
    "reading puts the start of the Harappan occupation, Phase I included, at c. 2200 B.C. (5730, uncalibrated), after "
    "Rao's date for the layout; Possehl and Raval's calibrated reading (Harappans in Gujarat ca. 2500-2300 B.C.) agrees "
    "with Rao but is computed from 5730-based ages printed as if they were on 5568. (3) Rao's own text is inconsistent: "
    "p. 44 assigns 2200 B.C. to 'the beginning of phase IIA' and 2350 B.C. to the beginning of Phase II, while pp. 85 "
    "and 125 put the flood that ended Phase I and the building of the dock in Phase IIa at circa 2350 B.C.; the Rao 1985 "
    "appendix heads the dock '2350-2000 B.C.' (p. 690). (4) The interim reports divided the sequence differently "
    "(three phases in IAR 1954-55, Pre-Defence, Defence and Post-Defence Periods in IAR 1955-56, six Periods in IAR "
    "1956-57, five Sub-periods with the outer platform and a street in the second in IAR 1957-58, five Phases from IAR "
    "1958-59); Rao 1979 (p. 60) explains that three construction stages of the Acropolis platform, first taken as separate "
    "occupation phases, were all completed in Phase IIa.")

parts = [
    {"part": "acropolis",
     "layout_phase": "Period A, Phase IIa (first sub-phase of structural Phase II)",
     "what_was_built": (
         "Rao describes the Acropolis as built after a flood destroyed the Phase I village: box-like enclosures of "
         "mud-brick walls packed with earth and kankar, much of it 'excavated from the basin of the dock', raised the "
         "working level, and the ruler's residence 'stood on the highest platform built in phase IIa' (p. 59). The "
         "platform under Block B was built in three stages that were first taken as separate occupation phases, but "
         "'all the three stages were completed in phase IIa' (p. 60). 'Block B was carefully planned and constructed in "
         "phase IIa' and 'the basic plan of Block B as laid out in phase IIa was not altered' (p. 100). The 'warehouse' "
         "on the solid mud-brick podium of Block C 'came into existence in phase II' over Phase I habitation debris "
         "(pp. 61, 111). Phase I left only traces of mud-brick walls in Blocks B and C (pp. 100, 111). In the chapter "
         "summary Rao writes that the Acropolis 'stood on a 14 ft. high platform' enclosing three blocks (p. 29)."),
     "locator": "rao1979lothal pp. 29, 59-61, 100, 111",
     "excavator_range_bce": [2350, 2200],
     "excavator_basis": BASIS_IIA,
     "radiocarbon": ALL_RC,
     "bayesian_start": None,
     "syntheses": SYN_COMMON,
     "conflicts": CONFLICTS_IIA},
    {"part": "lower town",
     "layout_phase": "Period A, Phase IIa (first sub-phase of structural Phase II)",
     "what_was_built": (
         "Rao writes that 'it is in phase II that the town was elaborately planned, the dock was built, trade expanded "
         "and new industries were established' (p. 44), and that 'the systematic planning of the town' is 'noticeable at "
         "Lothal also in phase II', after the "
         "Phase I village whose street alignment is unknown: blocks of houses on mud-brick platforms 4 to 12 ft. high "
         "in straight rows along arterial streets and lanes, with underground public drains (p. 85; also p. 29, where "
         "the earth excavated from the dock basin fills the platforms of the Acropolis and Lower Town). In Block A, the "
         "bazaar, Phase I left only the mud-bund, and the block 'became the shopping centre of the town in phase IIa and "
         "was served by a 22 ft.-wide street flanked by shops' (p. 88). 'The initial lay-out and plans of blocks and houses "
         "were meticulously maintained in successive phases' (p. 86), and no encroachment on the streets appears until "
         "Phase IV (p. 87). The interim report for 1957-58 likewise places a 12-ft. wide street in the second "
         "Sub-period, its alignment 'maintained in the third and fourth Sub-periods' (IAR 1957-58, p. 12)."),
     "locator": "rao1979lothal pp. 29, 44, 85-88; iar1957-58 p. 12",
     "excavator_range_bce": [2350, 2200],
     "excavator_basis": BASIS_IIA,
     "radiocarbon": ALL_RC,
     "bayesian_start": None,
     "syntheses": SYN_COMMON,
     "conflicts": CONFLICTS_IIA},
    {"part": "dock",
     "layout_phase": "Period A, Phase IIa (first sub-phase of structural Phase II)",
     "what_was_built": (
         "The brick-walled trapezoid basin on the town's eastern margin, which Rao calls the dock: 'After excavating the "
         "basin of the dock in phase IIa the builders increased its depth by erecting brick walls on all sides' (p. 63), "
         "and 'the dock was constructed in circa 2350 B.C. in phase IIa and continued to be in good use upto the end of "
         "phase IIIb when a great flood in 2000 B.C. caused heavy breaches in the walls' (p. 125). A new inlet was added "
         "in Phase IV, and the flood at the end of Phase IVb 'in circa 1900 B.C.' destroyed the dock with the township "
         "(p. 125). The same excavated earth filled the Acropolis platforms (p. 59). Rao's 1985 appendix heads the "
         "structure 'Lothal Dock (2350-2000 B.C.)' (rao1985lothal p. 690). Rao's chronology chapter puts it the same way: 'it is in phase II that the town was "
         "elaborately planned, the dock was built' (p. 44). The basin was first exposed in 1958-59 "
         "(IAR 1958-59, p. 14)."),
     "locator": "rao1979lothal pp. 29-30, 44, 59, 63, 123-125; rao1985lothal p. 690; iar1958-59 p. 14",
     "excavator_range_bce": [2350, 2200],
     "excavator_basis": BASIS_IIA + (" For the dock itself Rao gives construction circa 2350 B.C. and use until the "
                                     "Phase IIIb flood of 2000 B.C. 'dating by C 14 method' (rao1985lothal p. 690)."),
     "radiocarbon": ALL_RC,
     "bayesian_start": None,
     "syntheses": SYN_DOCK,
     "conflicts": CONFLICTS_IIA + (
         " For the dock in particular, TF-19 (3650 ± 135 BP on 5568, Phase VA) comes from debris sealing the "
         "western embankment wall and gives a terminus ante quem for its decay, not its construction (rc-tf-i p. 277; "
         "rao1979lothal p. 39).")},
    {"part": "peripheral wall",
     "layout_phase": "Period A, Phase I (mud-bund), raised and reinforced in Phase IIa",
     "what_was_built": (
         "A peripheral flood bund around the Phase I village, which Rao describes as 'a mud-bund, 52 ft. wide at the base "
         "and 42 ft. at the top' (p. 85; on the southern margin 42 ft. at the base and 40 ft. at the top, p. 62), built of "
         "the fine black clay found over the natural silt (p. 61). 'The flood at the end of phase I caused wide breaches "
         "in the bund which were mended with mud-bricks, and the height was also raised in phase IIa by adding 3 to 4 "
         "courses of bricks on top' (p. 62). In Phase II 'the damaged peripheral mud wall was strengthened and enlarged "
         "with mud-bricks' on three sides and reinforced with burnt bricks along the nullah (p. 29); in Block A 'the "
         "damaged mud-bund was reinforced with kiln-burnt bricks in phase II for the first time' (p. 88). The interim "
         "report of the last season states that the brick wall on the northern fringe 'had been built in Phase II over "
         "the remnants of an earlier mud-bund' (IAR 1962-63, p. 7). Rao reads the walls as flood defences, not "
         "fortifications (p. 87)."),
     "locator": "rao1979lothal pp. 29, 61-62, 71, 85, 87-88; iar1962-63 p. 7",
     "excavator_range_bce": [2450, 2350],
     "excavator_basis": (
         "Stratigraphic estimate. Rao dates Phase I to 2450-2350 B.C. (p. 46) by allowing the village about 100 years "
         "before the start of Phase II, which he fixes at 2350 B.C. by cross-dating and by counting back from the "
         "radiocarbon dates of about 2000 B.C. for Phase IIIB (p. 44); he places the flood that ended Phase I 'in circa "
         "2350 B C.' (p. 85). The one radiocarbon date from Phase I, TF-136, is rejected by Rao with the other 'second "
         "series' dates (p. 39). All B.C. figures are uncalibrated."),
     "radiocarbon": phase_I,
     "bayesian_start": None,
     "syntheses": SYN_COMMON,
     "conflicts": (
         "The final report and the early interim reports disagree on when the enclosing bund was first built. Rao 1979 "
         "places a mud-bund around the Phase I village, before the first flood (pp. 62, 85, 88). IAR 1954-55 (p. 12) "
         "describes an earliest phase 'washed away by a flood' followed by a second phase 'marked by a clay rampart, 8 ft. "
         "high and more than 16 ft. thick', and IAR 1955-56 (p. 6) has a Pre-Defence occupation damaged by floods, then a "
         "mud-brick platform, and only then a raised platform with a clay rampart 35 ft. wide and 8 ft. high that "
         "ushered in the Defence Period. IAR 1957-58 (p. 12) assigns the outer mud-brick platform enclosing the habitation "
         "area to the second of five Sub-periods. Mandal's radiocarbon reading puts Phase I at c. 2200 B.C. or later "
         "(5730, uncalibrated), about 250 years after Rao's 2450-2350 B.C.")},
]

first_occupation = {
    "phase": "Period A, Phase I (Harappan settlement beside an indigenous Micaceous Red Ware village)",
    "range_bce": [2450, 2350],
    "basis": (
        "Stratigraphic estimate counted back from the cross-dated start of Phase II: 'Granting that the life of the "
        "village was only 100 years, the beginning of Lothal phase I goes back to 2450 B.C.' (p. 44); 'phase I "
        "(2450-2350 B.C.)' (p. 46). Rao supports the early date with a habitation deposit about 10 ft. thick with a "
        "structure in situ below the present water table in SRG 30 (p. 44). He describes Lothal before the Harappans as "
        "'a small village standing on a river bank and occupied by an indigenous Chalcolithic folk' using Micaceous Red "
        "Ware, with Harappan wares present but fewer in the lowest Phase I levels (p. 24); the 1961-62 season found the "
        "Micaceous Red Ware 'always associated with the Harappan wares' down to natural soil at 6 m (IAR 1961-62, "
        "pp. 9-10). The only radiocarbon date from Phase I, TF-136 (3915 ± 130 BP on 5568, from the late level of "
        "Phase I according to Mandal), is younger than Rao's range and was rejected by him."),
    "locator": "rao1979lothal pp. 24, 44, 46; iar1961-62 pp. 9-10; rc-tf-iii p. 294",
}

RC_LISTS = {
    "rc-tf-i": ("Kusumgar, S., Lal, D. and Sarna, R. P. 1963. Tata Institute Radiocarbon Date List I. Radiocarbon 5: 273-282. doi:10.1017/s0033822200036894",
                "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/TF-I.pdf",
                "f20e5656fc81c20001b77765b72feccc0f30581222886ddefc2400b843934b11"),
    "rc-tf-iii": ("Agrawal, D. P., Kusumgar, S. and Lal, D. 1965. Tata Institute Radiocarbon Date List III. Radiocarbon 7: 291-295. doi:10.1017/s0033822200037279",
                  "data/raw/2026-10-21-town-axes/dating/radiocarbon-journal/TF-III.pdf",
                  "83ba490e67cf215319092b8bf2c6e782118f3a521dce73c3bcb3aed00dfc8855"),
}
IAR_BASE = "https://asiaurangabadcircle.com/assets/files/publications/"
IAR = {
    "iar1954-55": ("1954-1955", "402a60f85eb87daa35cf45847a2c0bfc66d1e6c1be3a00af89255ec1c7afced9", "p. 12 (Lothal, District Ahmedabad)"),
    "iar1955-56": ("1955-1956", "3838536aa7ea3ebd6918f10d9a72085c84c0fe4c4a9edf3a1244ab21e6c32765", "pp. 6-7 (Excavation at Lothal)"),
    "iar1956-57": ("1956-1957", "8bad5e4000168388b350f906e010f28568d167d49849c78b9cf7ce42c32c42ae", "pp. 15-16 (Excavation at Lothal (Saragwala))"),
    "iar1957-58": ("1957-1958", "f67de821414337af7688ad33d41ea1221b57fa2fbba903310987bfff53f45ad3", "pp. 12-13 (Excavation at Lothal (Saragwala))"),
    "iar1958-59": ("1958-1959", "b1443108517d42280412f804c4a9fa29f7cb8f8ab45fdb3fc58f0a2535c46b9b", "pp. 13-15 (Excavation at Lothal (Saragwala))"),
    "iar1961-62": ("1961-1962", "997895863fe3ca06a69535ea49fa8a896181abd3cb614789202a6458eff20555", "pp. 9-10 (Excavation at Lothal)"),
    "iar1962-63": ("1962-1963", "328a3cbf50af8b894c15aea8320a669c0619d647c5bbd0763d6ff72e99ce5a72", "p. 7 (Excavation at Lothal)"),
}

sources = []
for k, (c, p, s) in RC_LISTS.items():
    sources.append({"id": k, "citation": c, "url_or_path": p, "sha256": s})
sources += [
    {"id": "rao1979lothal",
     "citation": ("Rao, S. R. 1979. Lothal: A Harappan Port Town (1955-62), Vol. I. Memoirs of the Archaeological Survey "
                  "of India 78. New Delhi: Archaeological Survey of India. Scan of the Digital Library of India copy "
                  "('Part 1 (Plates Missing)'); its text layer is unusable OCR, so pages were read as images."),
     "url_or_path": ("https://archive.org/details/masi78lothalaharappanporttownraos.r.part1platesmissing_443_k ; "
                     "data/raw/2026-10-21-town-axes/dating/lothal/rao1979lothal-part1.pdf (printed page = PDF page - 11 "
                     "in the text chapters)"),
     "sha256": "34f6c5ece83dfb2b0308541c9f27e59962f011ccdabf4e35f388253f5fa181bf"},
    {"id": "rao1985lothal",
     "citation": ("Rao, S. R. 1985. Lothal: A Harappan Port Town (1955-62), Vol. II. Memoirs of the Archaeological Survey "
                  "of India 78. New Delhi: Archaeological Survey of India. Appendix II, 'Indus Engineering, Metrology "
                  "and Astronomy', pp. 689-690."),
     "url_or_path": ("https://archive.org/details/masi78lothalaharappanporttownraos.r.part2_531_D ; "
                     "data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf (p. 690 = PDF p. 437; no text layer)"),
     "sha256": "bc5f16e3d8836ac0f03b5b28e74fc9775ab042cf972fb64d59f082d7a8074865"},
    {"id": "kusumgar1963results",
     "citation": ("Kusumgar, S., Lal, D. and Sarna, R. P. 1963. Radiocarbon dating: results. Proceedings of the Indian "
                  "Academy of Sciences, Section A, 58(3): 141-152 (Lothal, pp. 148-149)."),
     "url_or_path": ("https://www.ias.ac.in/public/Volumes/seca/058/03/0141-0152.pdf ; "
                     "data/raw/2026-10-21-town-axes/dating/lothal/kusumgar1963pias.pdf"),
     "sha256": "07e663006773274ac621f5fee88b57c527fd2da7935aa5241ef05726b58ef3be"},
    {"id": "ramachandran1975radiocarbon",
     "citation": ("Ramachandran, K. S. 1975. Radiocarbon Dates of Archaeological Sites in India. Archaeological Series 42. "
                  "New Delhi: Archaeological Survey of India (Lothal, pp. 82-84; half-life convention in the introduction, "
                  "PDF p. 5)."),
     "url_or_path": ("https://archive.org/download/RadiocarbonDatesOfArchaeologicalSitesInIndia/RadiocarbonDatesOfArchaeologicalSitesInIndia.pdf ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-compilations/ramachandran1975.pdf"),
     "sha256": "4f9b4090cfbf627acc32a76d1b42b7ff742975b1abd2ee8e8b704aa5376a71d6"},
    {"id": "mandal1972radiocarbon",
     "citation": ("Mandal, D. 1972. Radiocarbon Dates and Indian Archaeology. Allahabad: Vaishali Publishing House "
                  "(half-life and reference year, p. 7; Lothal, pp. 64-66, 74-75). Read from the archive.org text layer; "
                  "page numbers are the running heads in that text."),
     "url_or_path": ("https://archive.org/details/bpvu_radiocarbon-dates-and-indian-archaeology-by-d-mandal-archaeology-allahabad- ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-compilations/mandal1972_djvu.txt"),
     "sha256": "bdd9c423048bb5bd2772d35be80847008d6a62b0862526b4241b466ab5240ac4"},
    {"id": "possehl1989rojdi",
     "citation": ("Possehl, G. L. and Raval, M. H. 1989. Harappan Civilization and Rojdi. Leiden: E. J. Brill; New Delhi: "
                  "Oxford & IBH (Table 1, 'Radiocarbon Determinations for Lothal and Surkotada', p. 10)."),
     "url_or_path": ("https://archive.org/details/harappan-civilization-and-rojdi ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-gujarat/possehl1989rojdi.pdf"),
     "sha256": "532d56f5c4ef8334f92572363901a620ff8173621c5cc7261d8d953f2fd6aac6"},
    {"id": "frenez2005lothal",
     "citation": ("Frenez, D. and Tosi, M. 2005. The Lothal Sealings: Records from an Indus Civilization Town at the "
                  "Eastern End of the Maritime Trade Circuits across the Arabian Sea. In M. Perna (ed.), Studi in onore di "
                  "Enrica Fiandra: Contributi di archeologia egea e vicinorientale (Studi Egei e Vicinorientali 1), "
                  "pp. 65-103. Napoli; Paris: De Boccard."),
     "url_or_path": ("https://zenodo.org/records/5514283 ; "
                     "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/LOTHAL2005.pdf"),
     "sha256": "b0694314c9b91321dc85e90a9c66c1cf410fe46387efd0e2dffeb747fa7ddcd3"},
    {"id": "kanungo2025bhagatrav",
     "citation": ("Kanungo, A. K., Kaushal, R. K., Bhushan, R., Chauhan, N., Kharakwal, J. S. and Ansari, S. 2025. "
                  "Luminescence and radiocarbon chronology of Bhagatrav: a Sorath Harappan camp site in South Gujarat. "
                  "Radiocarbon 67: 53-73. doi:10.1017/RDC.2024.119"),
     "url_or_path": ("https://www.cambridge.org/core/journals/radiocarbon/article/luminescence-and-radiocarbon-chronology-of-bhagatrav-a-sorath-harappan-camp-site-in-south-gujarat/F20A67111DE6F904BAD72BE922A6E78D ; "
                     "data/raw/2026-10-21-town-axes/dating/shared-gujarat/bhagatrav2024radiocarbon.pdf"),
     "sha256": "aa69f2377f61d379322c3203deea65a2525afdc89ca1a18fe3f635d7418e38d0"},
    {"id": "das2022seawater",
     "citation": ("Das, A., Sodhi, A., Vedpathak, C. D., Prizomwala, S. P., Agnihotri, R., Makwana, N., Joseph, J., "
                  "Patel, N., Chopra, S. and Ravi Kumar, M. 2022. Evidence for Seawater Retreat With Advent of Meghalayan "
                  "Era (~4200 a BP) in a Coastal Harappan Settlement. Geochemistry, Geophysics, Geosystems 23(6): "
                  "e2021GC010264. doi:10.1029/2021GC010264. Only the abstract (Crossref record) was read; the publisher "
                  "refused the PDF (HTTP 403)."),
     "url_or_path": ("https://doi.org/10.1029/2021GC010264 ; "
                     "data/raw/2026-10-21-town-axes/dating/lothal/das2022g3-crossref.json"),
     "sha256": "80b4e92300299a25ccff821717083a1b8718f930cded10caecd84976ffca57a3"},
]
for k, (yr, sha, pages) in IAR.items():
    sources.append({"id": k,
                    "citation": ("Ghosh, A. (ed.). Indian Archaeology %s - A Review. New Delhi: Archaeological Survey of "
                                 "India. Excavation report by S. R. Rao, %s. PDF of the ASI edition hosted by the ASI "
                                 "Aurangabad Circle." % (yr[:5] + yr[-2:], pages)),
                    "url_or_path": "%s%s.pdf ; data/raw/2026-10-21-town-axes/dating/shared-iar/iar%s.pdf" % (IAR_BASE, yr, yr),
                    "sha256": sha})

notes = (
    "Lothal was excavated by S. R. Rao for the Archaeological Survey of India from 1955 to 1962. Rao divides the "
    "occupation into Period A, the mature Harappan, with structural Phases I to IV (Phase II has sub-phases IIa-IIc, "
    "Phases III and IV two each), and Period B, the Late Harappan, Phase V (rao1979lothal p. 24); the Tata Institute "
    "lists of 1963 and 1965 call the same units Period I and Period II. The layout we record is the one Rao assigns to "
    "Phase IIa: after a flood destroyed the Phase I village he has the town rebuilt on mud-brick platforms, with the "
    "Acropolis, the Lower Town blocks and streets, the warehouse platform and the brick-lined basin he calls a dock all "
    "built at once, the basin's spoil filling the platforms. The peripheral bund is the one structure he places earlier, "
    "in Phase I, and we give it its own part. "
    "Rao's dates are uncalibrated and rest on cross-dating and on counting building sub-phases back from the Phase IIIB "
    "radiocarbon dates; they are 2450-2350 B.C. for Phase I, circa 2350 B.C. for the layout, 2000 B.C. for the Phase IIIB "
    "flood and 1900 B.C. for the end of Period A (rao1979lothal pp. 39-46, 125). "
    "Nine Tata Institute determinations exist, all on charcoal and all first published in Radiocarbon on the 5568-year "
    "half-life (rc-tf-i pp. 276-277; rc-tf-iii p. 294). We list the three from Phases I and II and the three Phase IIIB "
    "dates that Rao uses as his anchor, each with every reprint that changes the value, half-life, context or phase "
    "wording. We leave out the three later dates and list them here from rc-tf-i p. 277: TF-29, 3740 ± 110 BP, "
    "Phase IVA, waterlogged cesspool debris in SRG55 at 2.11 m; TF-23, 3705 ± 105 BP, Phase VA, posthole of a mud wall "
    "in SRG54 at 1.22 m; TF-19, 3650 ± 135 BP, Phase VA, debris sealing the western embankment wall of the dock in "
    "SRG11 at 2.19-2.25 m. Kusumgar, Lal and Sarna (kusumgar1963results pp. 148-149) published the six first-series "
    "dates in the same year with 5730 values in parentheses; their TF-19 value '(3750 ± 40)' is a misprint for a sigma "
    "of about 140. Rao (p. 39) quotes all nine dates as B.C. on the 5730-year half-life. "
    "Two features of these reprints matter for any re-analysis. Possehl and Raval's Table 1 prints 5730-based ages under "
    "a '5568 Half-life' heading and calibrates them, and Kanungo and colleagues reprint those figures as conventional "
    "ages; and Ramachandran's B.C. figure for TF-22 (1895 B.C.) does not follow from his own 5730 age. "
    "We found no published Bayesian model of Lothal's phases and no radiocarbon date from an archaeological context at "
    "Lothal later than the 1965 list; the 2022 sediment study in the dock (das2022seawater) dates a sea-level fall, and we "
    "could read only its abstract. "
    "Sources we sought and could not obtain: Rao 1973, Lothal and the Indus Civilization; Rao 1962, 'Further excavations "
    "at Lothal', Lalit Kala 11 (quoted only through kanungo2025bhagatrav); Possehl's 1989 radiocarbon compilation and "
    "his Indus Age: The Beginnings (1999) and The Indus Civilization (2002), which are access-restricted on archive.org; "
    "Agrawal and colleagues in Current Science 33 (1964): 266-269; the full text of Das et al. 2022. "
    "We did not record statements of wall or street direction found in these sources.")

doc = {"town": "lothal", "compiled_utc": "2026-10-21T04:15:29Z", "parts": parts,
       "first_occupation": first_occupation, "sources": sources, "notes": notes}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("wrote", OUT, len(ALL_RC), "rc entries")
