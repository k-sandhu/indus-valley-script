import json, sys

OUT = sys.argv[1]
R = "data/raw/2026-10-21-town-axes/dating/"

def rc(lab, material, context, phase, age, sig, src, page, cal=None, curve=None, hl=None, note=None):
    d = {"lab_no": lab, "material": material, "context": context, "phase": phase,
         "age_bp_printed": age, "sigma_printed": sig, "half_life_printed": hl,
         "age_bp_5568": (age if hl == 5568 else (round(age / 1.03) if hl == 5730 else None)),
         "sigma_5568": (sig if hl == 5568 else (round(sig / 1.03) if hl == 5730 else None)),
         "calibrated_published": cal, "curve": curve, "source": src, "page": page}
    if note:
        d["note"] = note
    return d

NATH_NOTE = ("BSIP sample number {s}; the report's table does not state the material, the half-life or the calibration "
             "curve, and labels the calibrated column 'Calibrated Age (Yrs BP)'. Sample CO2 column: {co2}.")
DIK_NOTE = ("BSIP sample number {s}. Dikshit prints the twelve BSIP Rakhigarhi dates 'courtesy: Amrendra Nath' without "
            "period or phase; he calls the samples charcoal and gives no half-life or curve, only the laboratory's advice "
            "to calibrate with Calib 4.4.")

nath = "nath2014rakhigarhi"
dik = "dikshit2022origin"
vah = "vahia2016rakhigarhi"

citadel_rc = [
    rc("BS-3324", None, "No. 213, RGR-2, 8.45 m", "Early Harappan", 5200, 100, nath,
       "p. 57, Table 1 (repeated in Appendix 2, p. 335)", cal="5910 ± 130 (Yrs BP)",
       note=NATH_NOTE.format(s="S-4180", co2="98.5") + " Dikshit 2022: 169 reprints the same values for BS-3324 without a phase."),
    rc("BS-3368", None, "No. 78, RGR-2, 6.40 m", "Mature Harappan", 4040, 90, nath,
       "p. 57, Table 1 (repeated in Appendix 2, p. 335)", cal="4560 ± 90 (Yrs BP)",
       note=NATH_NOTE.format(s="S-4215", co2="44.8")),
    rc("BS-3389", None, "No. 187, RGR-2, 5.60 – 5.90 m", "Mature Harappan", 3900, 110, nath,
       "p. 57, Table 1 (repeated in Appendix 2, p. 335)", cal="4320 ± 90 (Yrs BP)",
       note=NATH_NOTE.format(s="S-4237", co2="33.0")),
    rc("BS-3313", "charcoal", "No.86, RGR-2, 1080 CM", None, 5410, 100, dik, "p. 169, Table 2",
       cal="6180±50 (Yrs BP)", note=DIK_NOTE.format(s="S-4168") + " At 10.80 m this is the deepest RGR-2 sample in either table."),
    rc("BS-3323", "charcoal", "No.223, RGR-2, 8.45 m", None, 3910, 100, dik, "p. 169, Table 2",
       cal="5350±100 (Yrs BP)",
       note=DIK_NOTE.format(s="S-4179") + " Printed as found: a radiocarbon age of 3910 BP cannot calibrate to 5350 BP, and the sample comes from the same depth as BS-3324 (5200 ± 100), so one of the printed columns is probably in error."),
    rc("BS-3325", "charcoal", "No.155, RGR-2, 0.74CM", None, 4690, 120, dik, "p. 169, Table 2",
       cal="5450±80 (Yrs BP)", note=DIK_NOTE.format(s="S-4181") + " The depth is printed as '0.74CM'."),
]

rgr1_rc = [
    rc("BS-3344", None, "No. 46, RGR-1 (no depth printed)", "Early Harappan", 4570, 100, nath,
       "p. 57, Table 1 (repeated in Appendix 2, p. 335)", cal="5230 ± 60 (Yrs BP)",
       note=NATH_NOTE.format(s="S-4190", co2="39.4") + " Dikshit 2022: 169 reprints the same values without a phase."),
    rc("BS-3314", "charcoal", "No.43, RGR-1, 3.2-3.3 CM", None, 5230, 90, dik, "p. 169, Table 2",
       cal="6030±40 (Yrs BP)", note=DIK_NOTE.format(s="S-4169") + " The same field number No. 43 and the same depth (as 320-330 CM) are printed for BS-3353, which gives 3810 ± 70."),
    rc("BS-3340", "charcoal", "No.59, RGR-1, 2.70 M", None, 3740, 70, dik, "p. 169, Table 2",
       cal="4090±80 (Yrs BP)", note=DIK_NOTE.format(s="S-4186")),
    rc("BS-3345", "charcoal", "No.37, RGR-1, 2.55-2.70 M", None, 4430, 80, dik, "p. 169, Table 2",
       cal="5060±40 (Yrs BP)", note=DIK_NOTE.format(s="S-4191")),
    rc("BS-3350", "charcoal", "No.28A, RGR-1, 200-205 CM", None, 4650, 90, dik, "p. 169, Table 2",
       cal="5410±90 (Yrs BP)", note=DIK_NOTE.format(s="S-4197")),
    rc("BS-3352", "charcoal", "No.35, RGR-1, 240-250 CM", None, 3840, 70, dik, "p. 169, Table 2",
       cal="4270±60 (Yrs BP)", note=DIK_NOTE.format(s="S-4199")),
    rc("BS-3353", "charcoal", "No.43, RGR-1, 320-330 CM", None, 3810, 70, dik, "p. 169, Table 2",
       cal="4200±100 (Yrs BP)", note=DIK_NOTE.format(s="S-4200") + " Same field number and depth as BS-3314 (5230 ± 90)."),
]

rgr6_rc = [
    rc("BS-3318", None, "No. 58, RGR-6, 4.96 m", "Pre-formative", 5640, 110, nath,
       "p. 57, Table 1 (repeated in Appendix 2, p. 335)", cal="6420 ± 110 (Yrs BP)",
       note=NATH_NOTE.format(s="S-4173", co2="96.3") + " Period I(a), the phase before the layout phase on this mound."),
    rc("BS-3341", None, "No. 51, RGR-6, 4. 23 m", "Pre-formative", 5440, 290, nath,
       "p. 57, Table 1 (repeated in Appendix 2, p. 335)", cal="6230 ± 320 (Yrs BP)",
       note=NATH_NOTE.format(s="S-4187", co2="18.3") + " Period I(a). Dikshit 2022 gives field sample No. 51 a different laboratory number, depth and age (BS-3342, below)."),
    rc("BS-3342", "charcoal", "No.51, RGR-6, 4.32 M", None, 4950, 310, dik, "p. 169, Table 2",
       cal="5680±340 (Yrs BP)", note=DIK_NOTE.format(s="S-4188") + " Nath 2014 assigns field sample No. 51 to BS-3341 at 4.23 m with 5440 ± 290; the two tables disagree on laboratory number, depth and age for the same field number."),
]

VAH_NOTE = ("No laboratory number, mound or excavator's phase is published; the samples came from 'a vertical trench' dug by "
            "Deccan College in 2015 and were measured on the IUAC accelerator. The ages are given as 'Libby years (BP)' and the data "
            "'according to Stuiver and Polach', the convention that uses the 5568-year half-life, so we entered 5568. "
            "Calibrated with 'OxCal 4.2' online; the curve is not named.")

def vrow(depth, age, sig, mx, mn, calbp, extra=""):
    return rc(None, "charcoal", "Deccan College 2015 vertical trench, depth %s m" % depth, None, age, sig, vah,
              "p. 27, Table 1", cal="Age (years BC) maximum %d, minimum %d; calibrated age (BP) %s" % (mx, mn, calbp),
              curve="OxCal 4.2 (curve not named)", hl=5568, note=VAH_NOTE + extra)

town_rc = [
    vrow("9.1", 3824, 80, 2351, 2196, "4273 ± 39", " The text concludes that this sample 'has a maximum age of about 2273 ± 38 yrs BC' (p. 28)."),
    vrow("15.7", 4141, 75, 2780, 2628, "4704 ± 38", " The authors treat this sample as off their age-depth line (p. 28)."),
    vrow("16.1", 3900, 82, 2481, 2280, "4380 ± 50"),
    vrow("17.3", 3903, 224, 2671, 2119, "4395 ± 138", " The authors treat this sample as off their age-depth line (p. 28)."),
    vrow("18.4", 4067, 90, 2697, 2488, "4592 ± 52"),
    vrow("19.3", 4060, 75, 2679, 2480, "4579 ± 50"),
    vrow("20.6", 4060, 129, 2762, 2470, "4616 ± 73", " The text concludes that this sample 'has a maximum age of 2762 ± 73 yrs BC' (p. 28)."),
]

PERIOD_II_BASIS = ("Radiocarbon. The 2014 report gives no calendar range for Period II. It states that 'the calibrated radiometric dates "
                   "range from 4560 + 90 to 4320 + 90 (Yrs BP)' (Nath 2014: 129), the calibrated values of the two Mature Harappan BSIP "
                   "determinations from RGR-2 (BS-3368 and BS-3389, p. 57), and its opening line places the civilisation at Rakhigarhi "
                   "'during the fourth- third millennium B.C.' (p. 4). The preliminary reports of 1998-2001 in Puratattva and Indian "
                   "Archaeology: A Review give no dates.")

EH_BASIS = ("Radiocarbon. Nath 2014: 76 attributes the Early Harappan formative stage to 'circa 4th millennium BCE' (citing its Table 1), "
            "which we entered as [4000, 3000], and p. 129 states that the calibrated dates of Period I(b) 'range from 5910 + 130 to "
            "5230 + 60 (Yrs BP)', the calibrated values of BS-3324 (RGR-2) and BS-3344 (RGR-1).")

NOTES_TEXT = "Rakhigarhi is a cluster of mounds. RGR-1 to RGR-5 form the integrated city, RGR-6 (Arda) is a separate Early Harappan mound and RGR-7 is the Mature Harappan cemetery; the Deccan College volume of 2023 lists newly discovered localities RGR-8 and RGR-9, which no excavation report we found describes. Our account of the layout rests on the ASI excavations of 1997-2000 directed by Amarendra Nath, which we read in three forms: the season reports in Indian Archaeology: A Review for 1997-98 to 1999-2000, the interim articles in Puratattva 28, 29 and 31, and the draft final report of 2014 held by the Internet Archive. Nath divides the occupation into Period I (Early Harappan), split into I(a) 'pre-formative urbanism' and I(b) 'formative urbanism', and Period II (Mature Harappan). The 2014 report numbers the structural phases continuously, I to III in Period I and IV to VI in Period II, while the interim reports number phases afresh within each period and mound, so the same phase can carry different numbers. Planned layouts appear twice: Early Harappan streets and drains on RGR-1 and RGR-6 in Period I(b), and the fortified citadel on RGR-2, with its street grid, podiums and granary, at the start of Period II, when the excavator says the settlers kept the earlier plan.\n\nThe dating evidence is thin. Nath's 2014 table lists six determinations from the Birbal Sahni Institute (BSIP) with periods, and Dikshit (2022) prints twelve BSIP determinations from the same excavation without periods; only two laboratory numbers overlap, and the tables disagree about field sample No. 51. Neither source states the half-life or the calibration curve, and both head a column 'Calibrated Age (Yrs BP)' without saying how it was computed, so we left half_life_printed and the 5568-year fields null for these dates. The Birbal Sahni Institute lists published in Radiocarbon in 1978-1982 used the conventional 5570-year half-life, but that does not establish the convention for these later measurements. The seven AMS dates of Vahia et al. (2016) come from a 2015 Deccan College trench whose mound and phases are unpublished, so we filed them under the whole town. No determination is tied to the construction of a wall, street or platform, and no Bayesian model of phase boundaries has been published for Rakhigarhi. Determinations from later phases are included only where the source gives no phase, because we cannot then exclude them.\n\nSources sought and not obtained: the Deccan College report on the 2013-2016 habitation excavations (Shinde, Shin and Bhattacharyya (eds) 2023, New Perspectives on the Harappan Culture in Light of Recent Excavations at Rakhigarhi: 2011-2017, vol. 1, chapter 3, 'Excavations 2013-2016', pp. 43-63), of which only the publisher's sample with the front matter and chapter 1 is open; its list of figures shows trenches on RGR-2, RGR-4 and RGR-6. The IUAC date list I (Sharma et al. 2020, Radiocarbon 62(5), doi:10.1017/RDC.2020.44) is paywalled, and its open abstract page names Rakhigarhi only in a reference. We found no report of the ASI excavations of 2021-2024, only press articles, which we did not use. Indian Archaeology 2011-12 is not online at the address that holds the other volumes, and Indian Archaeology 2012-13 (saved at data/raw/2026-10-21-town-axes/dating/rakhigarhi/iar2012-13.pdf) has no Rakhigarhi excavation entry. We did not consult Possehl's compilations of 1999 and 2002; the first Rakhigarhi determinations we found in print date from 2014. Page 44 of Nath 2001 is largely illegible in the scan, and IAR 1999-2000: 31-32 carries the same season's account. The ASI Chandigarh Circle inventory of protected monuments held locally (data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/rakhigarhi_inventory.pdf, entry 33) gives no dates. Nath 1998: 41 also reports, from a cutting made by villagers on RGR-3, courses of burnt brick and mud brick side by side that he takes to be 'two phases of construction in the fortification wall'; RGR-3 was not excavated, and no phase is given."

data = {
  "town": "rakhigarhi",
  "compiled_utc": "2026-10-21T04:05:00Z",
  "parts": [
    {
      "part": "citadel (RGR-2)",
      "layout_phase": "Period II (Mature Harappan), its first structural phase: 'Phase 1' of five tentative Mature Harappan levels in Nath 1998; 'phase-IV', the first phase of Period II, in Nath 2014",
      "what_was_built": ("A mud-brick fortification wall around the mound, first built at the start of the Mature Harappan occupation, and inside it "
                         "a grid of streets and lanes with podiums, a granary and drains. In the gateway cuttings Nath (1998: 43) gives the wall a "
                         "thickness of 5 m in Phase 1; a burnt-brick buttress was added in Phase 2, the thickness was doubled and an entrance stair "
                         "built in Phase 3, the top was paved with burnt brick between guard cells in Phase 4, and mud-brick courses raised it in "
                         "Phase 5, while 'a lane parallel to fortification walls remained undisturbed till the last occupation at the site'. The "
                         "2014 report states that the 'fortification wall of phase-IV' was 'reconstructed in phase-V', with two circular hearths of "
                         "Period I, Phase II beneath it, and that the inhabitants 'built the enormous mud brick platform and granary in the phase-V' "
                         "(Nath 2014: 118). It describes 'streets and lanes joined in a chess board pattern' (p. 95) and says 'the period II people "
                         "follow his predecessor plan and did not change more on city plan' (p. 113). Nath 1999: 48 describes the wall as a mud-brick "
                         "core with burnt-brick facing inside and out, and the 1999-2000 season exposed a western stretch 12 m wide with a stepped "
                         "entrance of burnt brick (IAR 1999-2000: 32). Public drains appear 'from the lower-middle phase' (Nath 1998: 43)."),
      "locator": "nath1998rakhigarhi p. 43; nath2014rakhigarhi pp. 95, 113, 118; nath1999rakhigarhi p. 48; iar1999-2000 p. 32 (pdf p. 40)",
      "excavator_range_bce": None,
      "excavator_basis": PERIOD_II_BASIS,
      "radiocarbon": citadel_rc,
      "bayesian_start": None,
      "syntheses": [
        {"source": "dikshit2022origin", "page": "p. 169", "range_bce": None,
         "statement": ("Reprints twelve BSIP determinations from RGR-1, RGR-2 and RGR-6 supplied by Nath, without period or phase, and states that "
                       "the excavations 'revealed all the phases of the Harappan civilization, i.e., period I (Early Harappan), period II (Mature "
                       "Harappan) and period III (Late Harappan)'."),
         "disagreement": ("Nath's own reports found no Late Harappan deposit in the stratified cuttings of RGR-1 and RGR-2 (Nath 1999: 46; Nath 2014: "
                          "104), and ten of Dikshit's twelve laboratory numbers do not appear in Nath's 2014 table.")}
      ],
      "conflicts": ("The phase in which the wall was first built is numbered differently in the two main accounts: Phase 1 of five Mature Harappan "
                    "levels in the 1998 interim report, which warns that 'the present observations would be subject to correction' until trenches "
                    "across the wall were verified, and phase IV of a Period II divided into phases IV to VI in the 2014 report. Both put the first "
                    "wall at the beginning of the Mature Harappan occupation. Reported widths differ by location and season: 5 m in Phase 1 at the "
                    "gateway (Nath 1998: 43), 12 m for the western stretch (IAR 1999-2000: 32) and a maximum breadth of 6 m at the north-western "
                    "corner (Nath 2014: 111). Among the radiocarbon determinations, BS-3323 in Dikshit's table comes from the same depth (8.45 m) as "
                    "Nath's Early Harappan BS-3324 but gives 3910 ± 100 against 5200 ± 100, and its printed calibrated age is impossible for "
                    "its radiocarbon age. No determination is tied to the wall itself or to a named structural phase.")
    },
    {
      "part": "RGR-1 (habitation mound north of RGR-3)",
      "layout_phase": "Period I (Early Harappan), structural phase 2 (IAR 1998-99; 'phase II', sub-phases IIa and IIb, in Nath 2014), within sub-period I(b) 'formative urbanism'; Nath 1999 numbers the same planned phase 'Phase-I'",
      "what_was_built": ("The first planned layout on RGR-1 belongs to the Early Harappan period. Of three Early Harappan structural phases, the second "
                         "'revealed the beginning of planned settlement', with a public drain lined with burnt brick, a house drain joining it, houses "
                         "aligned on either side and a courtyard paved with burnt-brick bats sloping towards the drain (IAR 1998-99: 13; Nath 2014: 104, "
                         "115, 118, which speaks of 'a genius planning of ... street with nullah'). The 2014 report characterises Period I(b) as an "
                         "'organized settlement where in structures were laid parallel to streets running at right angle, besides developing the concept "
                         "of public drainage system' (p. 129), and states that after a flood ended Period I, phase III, the Period II settlers 'also "
                         "followed the phase III plan' (p. 105). In Period II the mound carried streets 1 to 3 around house complexes and a lapidary "
                         "workshop (pp. 113, 115-117); in the 1997-98 cutting G6 the Mature Harappan structural phases 1 to 4 were 'aligned, on either "
                         "side, to a lane (1.50 m wide)', and those of phase 5 'were not in exact alignment' (IAR 1997-98: 55-57; Nath 1998: 42). No "
                         "peripheral wall was found around RGR-1 in Period I (Nath 2014: 114)."),
      "locator": "iar1998-99 p. 13 (pdf p. 21); nath2014rakhigarhi pp. 104-105, 114-115, 129; nath1999rakhigarhi p. 47; iar1997-98 pp. 55-57 (pdf pp. 63-65)",
      "excavator_range_bce": [4000, 3000],
      "excavator_basis": EH_BASIS,
      "radiocarbon": rgr1_rc,
      "bayesian_start": None,
      "syntheses": [
        {"source": "dikshit2022origin", "page": "p. 169", "range_bce": None,
         "statement": ("Summarises Period I at Rakhigarhi as three structural phases with drainage systems, a courtyard floor, circular pits and fire "
                       "chambers, and lists six further BSIP determinations from RGR-1 without phase."),
         "disagreement": None}
      ],
      "conflicts": ("The planned Early Harappan phase is 'phase-2' in IAR 1998-99: 13 and phase II in Nath 2014: 104 and 115, but 'Phase-I' in Nath "
                    "1999: 47, which describes the same drain and courtyard. The thickness of the Early Harappan deposit is 'nearly two and a half "
                    "metre' in IAR 1998-99: 13, 'nearly three metres' in Nath 1999: 47 and 4 m of the 6 m deposit in Nath 2014: 94. Nath's only "
                    "Early Harappan date from this mound (BS-3344) has no depth. Dikshit's table prints field sample No. 43 twice at the same depth "
                    "with ages of 5230 ± 90 (BS-3314) and 3810 ± 70 (BS-3353); both cannot belong to one sample.")
    },
    {
      "part": "RGR-6 (Arda; separate Early Harappan mound)",
      "layout_phase": "Period I(b), formative urbanism (structural phases 4 to 6 in IAR 1999-2000; the 2014 report singles out phase V)",
      "what_was_built": ("On RGR-6 the excavators found Early Harappan houses on either side of a street 1.92 m wide, laid out in Period I(b) over "
                         "rectangular houses of Period I(a) whose walls 'were running right across the cutting of street'. The street was kept "
                         "through three successive structural phases: in phase 4 a room built of sun-dried bricks of 3:2:1 ratio, in phase 5 a house "
                         "of two rooms and a courtyard beside a lane 92 cm wide, with the same layout partly exposed across the lane, and in phase 6 "
                         "rooms within enclosure walls on both sides of the street (IAR 1999-2000: 30-31). The 2014 report says phase V 'give a clear "
                         "picture of planning settlement of early Harappan folk' with 'a good network of street and lane' and a house complex of seven "
                         "rooms opening onto them (Nath 2014: 122). Early Harappan occupation at RGR-6 ended with the start of Period II (p. 129)."),
      "locator": "iar1999-2000 pp. 30-31 (pdf pp. 38-39); nath2014rakhigarhi pp. 122, 129; nath2001rakhigarhi p. 43",
      "excavator_range_bce": [4000, 3000],
      "excavator_basis": EH_BASIS + " No determination from Period I(b) on RGR-6 itself is published.",
      "radiocarbon": rgr6_rc,
      "bayesian_start": None,
      "syntheses": [],
      "conflicts": ("Field sample No. 51 from RGR-6 is BS-3341 at 4.23 m with 5440 ± 290 in Nath 2014: 57, and BS-3342 at 4.32 m with "
                    "4950 ± 310 in Dikshit 2022: 169. IAR 1999-2000: 30 counts six structural phases at RGR-6 (three in each sub-period), while "
                    "the 2014 report speaks of five Early Harappan phases there (pp. 95, 122). Natural soil was not reached at 7.2 m (IAR 1999-2000: 30).")
    },
    {
      "part": "RGR-4 and RGR-5 (southern mounds under Rakhi Khas and Rakhi Shahpur)",
      "layout_phase": "Period II (Mature Harappan); no structural phase stated",
      "what_was_built": ("Before excavation Nath (1998: 41) recorded in a cliff section on the south-western part of the combined mound 'a massive "
                         "mud-brick fortification wall with successive mushtika beddings, overlain by successive mud-floors', with a burnt-brick drain "
                         "beside it, and took 'the evidence of fortification wall from RGR2, 3 and 4' as a sign of 'individual habitation-zones within "
                         "an integrated network of town planning'. Excavation in 1998-2000 found only Mature Harappan remains on RGR-4 and RGR-5 (IAR "
                         "1999-2000: 30): a trench on RGR-4 was opened to follow the fortification southward (Nath 1999: 46), RGR-4 gave 'structural "
                         "evidence of platforms and streets' (Nath 2001: 45) and RGR-5 gave bone and ivory working. A cutting on RGR-4 traced a large "
                         "podium first seen at the south-eastern corner of RGR-2 (Nath 2014: 96)."),
      "locator": "nath1998rakhigarhi p. 41; nath1999rakhigarhi p. 46; nath2001rakhigarhi p. 45; iar1999-2000 p. 30 (pdf p. 38); nath2014rakhigarhi p. 96",
      "excavator_range_bce": None,
      "excavator_basis": "No determination or range specific to these mounds; the Period II statement for the citadel applies (Nath 2014: 129).",
      "radiocarbon": [],
      "bayesian_start": None,
      "syntheses": [],
      "conflicts": ("The excavator never states in which phase the fortification seen in the RGR-4/5 section was built, and the reports do not say "
                    "whether the trench on RGR-4 found it.")
    },
    {
      "part": "whole town (Mature Harappan city, RGR-1 to RGR-5)",
      "layout_phase": "Period II (Mature Harappan)",
      "what_was_built": ("The excavator treats the integrated mounds RGR-1 to RGR-5 as one planned Mature Harappan city and divides it 'into citadel, "
                         "middle town and lower town' (Nath 2014: 93), naming only RGR-2 as the citadel. He infers that 'the Harappans must have "
                         "prepared a blueprint of the proposed town before providing all the civic amenities', citing platforms, streets and drains, "
                         "public wells, separate industrial areas, houses in rows, 'fortification walls of uniform width', the granary and the podiums "
                         "(p. 103), and states that the Period II settlers 'followed the phase III plan' of the Early Harappan town (p. 105)."),
      "locator": "nath2014rakhigarhi pp. 93, 103, 105",
      "excavator_range_bce": None,
      "excavator_basis": PERIOD_II_BASIS,
      "radiocarbon": town_rc,
      "bayesian_start": None,
      "syntheses": [
        {"source": "shinde2018cemetery", "page": "p. 10 of 30", "range_bce": None,
         "statement": ("Reports that AMS dates for charcoal 'from different depths at the Rakhigarhi site' at 9.1 and 20.6 m 'yielded calibrated dates "
                       "of 2273±38 years BCE and 2616 ±73 years BCE, respectively', citing Vahia et al. 2016."),
         "disagreement": ("Vahia et al. 2016: 28 give 2762 ± 73 BC for the 20.6 m sample, and their table gives 2762-2470 BC and 4616 ± 73 "
                          "BP for it; 2616 matches none of these.")},
        {"source": "shinde2018cemetery", "page": "p. 26 of 30", "range_bce": [2500, 2000],
         "statement": "Places the Rakhigarhi cemetery (RGR-7) in 'the Mature Harappan period, date-estimated to 2,500–2,000 BCE'.",
         "disagreement": "Not tied to the town's layout; it is a period estimate for the cemetery."},
        {"source": "shinde2019genome", "page": "Introduction and STAR Methods, 'Contextual date for individual I6113' (PMC HTML without page numbers)",
         "range_bce": [2800, 2300],
         "statement": ("States that 'seven dates from charcoal at depths of 9–23 meters have point estimates of 2800–2300 BCE, which largely "
                       "fall within the mature phase of the IVC', and that these come from 'the main habitation area'."),
         "disagreement": ("Vahia et al. 2016 publish no mound and a deepest sample of 20.6 m, and their own maximum ages run from 2351 to 2780 BC "
                          "rather than to 2800 BCE.")},
        {"source": "shinde2023perspectives", "page": "p. 11", "range_bce": [2600, 1900],
         "statement": ("In a regional summary for the Ghaggar basin sites including Rakhigarhi, gives the Early Harappan as 6000–2600 BCE and the "
                       "Mature Harappan as 2600–1900 BCE, divided into periods IIA and IIB (2600–2400 BCE) and IIC (2200–1900 BCE) 'on the "
                       "basis of a few accelerator mass spectrometry (AMS) dates', and says that streets and drainage systems appear 'from period IIA on'."),
         "disagreement": ("This later excavator's scheme starts the planned Mature Harappan phase about 2600 BCE and the Early Harappan about 6000 BCE; "
                          "Nath places the Early Harappan formative stage in the 4th millennium BCE and the first occupation in the 5th, and his Period II "
                          "dates are calibrated ages of 4560 and 4320 yrs BP. The summary does not say which dates or which site support each boundary.")}
      ],
      "conflicts": ("The two dated series cannot yet be joined: Nath's BSIP dates are tied to periods but come from three mounds with few depths, while "
                    "the IUAC AMS series of Vahia et al. has depths but no mound, trench or phase. Later papers by the Deccan College team restate the "
                    "AMS results inconsistently (2616 BCE in Shinde et al. 2018; 2800–2300 BCE over 9–23 m in Shinde et al. 2019).")
    }
  ],
  "first_occupation": {
    "phase": "Period I(a), pre-formative urbanism (Early Harappan), at RGR-6 and RGR-1; Appendix 2 of the 2014 report calls it the 'Sothi Phase'",
    "range_bce": [5000, 4000],
    "basis": ("Radiocarbon. Two BSIP determinations from RGR-6 (BS-3318, 5640 ± 110 BP; BS-3341, 5440 ± 290 BP), whose calibrated values "
              "the report gives as 6420 ± 110 and 6230 ± 320 yrs BP (Nath 2014: 57, 129). The report assigns the pre-formative stage to "
              "'circa 5th millennium BCE' (p. 76), which we entered as [5000, 4000]. Natural soil was not reached at RGR-6 (IAR 1999-2000: 30), so "
              "occupation may begin earlier there; on RGR-1 the Early Harappan deposit 'shows the beginning of occupation over the alluvium' "
              "(IAR 1998-99: 13)."),
    "locator": "nath2014rakhigarhi pp. 57, 76, 129, 336; iar1999-2000 pp. 30-31 (pdf pp. 38-39); iar1998-99 p. 13 (pdf p. 21)"
  },
  "sources": [
    {"id": "nath2014rakhigarhi",
     "citation": ("Nath, A. 2014. Excavations at Rakhigarhi [1997-98 to 1999-2000]. Draft report submitted to the Director General, Archaeological "
                  "Survey of India, with covering letter dated 31.12.2014 (Report Writing Unit, ASI Excavation Branch-II, Purana Qila, New Delhi). "
                  "Copy held by the Internet Archive (Digital Library of India), item excavationsatrakhigarhi19972000amarendranath_457_Z; Vahia et al. "
                  "2016 cite it at asi.nic.in/pdf_data/rakhigarhi_excavation_report_new.pdf."),
     "url_or_path": ("https://archive.org/details/excavationsatrakhigarhi19972000amarendranath_457_Z ; "
                     + R + "rakhigarhi/nath-excavations-1997-2000.pdf (text layer in .txt)"),
     "sha256": "b0274fcaf1747b4ede3d6d238c20dd43b5f3a6fca70dee642fec606575c54d47"},
    {"id": "nath1998rakhigarhi",
     "citation": "Nath, A. 1998. Rakhigarhi: A Harappan Metropolis in the Sarasvati-Drishadvati Divide. Puratattva 28 (1997-98): 39-45.",
     "url_or_path": ("https://archive.org/details/dli.ministry.29985 ; " + R + "shared-puratattva/puratattva28.pdf (scan; pp. 39-45 = pdf pp. 51-57) and "
                     + R + "shared-puratattva/puratattva28_djvu.txt (OCR)"),
     "sha256": "33da32ac82cadfc09b4722fb5e25f13fa2aac2043ec680d3d06ebf07609680a1"},
    {"id": "nath1999rakhigarhi",
     "citation": "Nath, A. 1999. Further Excavations at Rakhigarhi. Puratattva 29 (1998-99): 46-49.",
     "url_or_path": ("https://archive.org/details/dli.ministry.29986 ; " + R + "shared-puratattva/puratattva29.pdf (scan; pp. 46-49 = pdf pp. 60-63) and "
                     + R + "shared-puratattva/puratattva29_djvu.txt (OCR)"),
     "sha256": "c40650a294ff9234d486691a9b4892b1bdb134631a0960a1c5a0c4cbc9050760"},
    {"id": "nath2001rakhigarhi",
     "citation": "Nath, A. 2001. Rakhigarhi: 1999-2000. Puratattva 31 (2000-2001): 43-46.",
     "url_or_path": ("https://archive.org/details/puratattvano31indianarchaeologicalsocietybhu_392_L ; " + R
                     + "shared-puratattva/puratattva31.pdf (scan; pp. 43-46 = pdf pp. 59-62)"),
     "sha256": "9043597950b1b83b1ea447e643e3ef0e1671ea25bf9a7b3f9bc854cb39d90dab"},
    {"id": "iar1997-98",
     "citation": ("Archaeological Survey of India. Indian Archaeology 1997-98 — A Review. New Delhi: ASI. Entry 20, 'Excavation at Rakhigarhi, "
                  "District Hissar' (A. Nath and P. K. Mishra), pp. 55-63."),
     "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1997-1998.pdf ; " + R + "rakhigarhi/iar1997-98.pdf",
     "sha256": "26a4316a2212fe271740cdef7699efb901e9afc4965e266f8ef511a0abd9add4"},
    {"id": "iar1998-99",
     "citation": ("Archaeological Survey of India. Indian Archaeology 1998-99 — A Review. New Delhi: ASI. Entry 12, 'Excavation at Rakhigarhi, "
                  "District Hissar' (A. Nath), pp. 13-23."),
     "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1998-1999.pdf ; " + R + "rakhigarhi/iar1998-99.pdf",
     "sha256": "7ced1ba60f00da1f7045697d48c4ec4a82ebfed09823f18f9c569a3c91ed781a"},
    {"id": "iar1999-2000",
     "citation": ("Archaeological Survey of India. Indian Archaeology 1999-2000 — A Review. New Delhi: ASI. Entry 23, 'Excavation at Rakhigarhi, "
                  "District Hissar' (A. Nath), pp. 30-33."),
     "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/1999-2000.pdf ; " + R + "rakhigarhi/iar1999-2000.pdf",
     "sha256": "abe66bf6546405c8c663ee3a2a8a7a8b03118e3b0a6b51d1d99bb793f92e09eb"},
    {"id": "dikshit2022origin",
     "citation": ("Dikshit, K. N. 2022. The Origin of Indian Civilization in Sarasvati Valley. Abhidha Journal of Art, Archaeology and Cultural "
                  "Heritage 2(2): 156-215."),
     "url_or_path": ("https://abhidhajournal.com/wp-content/uploads/2024/06/Paper-10_-The-Origin-of-Indian-Civilization-in-Sarasvati-Valley-_v4.pdf ; "
                     + R + "shared-sarasvati/dikshit2022abhidha.pdf"),
     "sha256": "41266be600cd0e5febac2ee41e4c494c86bd95c60817b6eefc1601ad3476b544"},
    {"id": "vahia2016rakhigarhi",
     "citation": ("Vahia, M. N., Kumar, P., Bhogale, A., Kothari, D. C., Chopra, S., Shinde, V., Jadhav, N. and Shastri, R. 2016. Radiocarbon dating "
                  "of charcoal samples from Rakhigarhi, Haryana, India using accelerator mass spectrometer. Current Science 111(1): 27-28."),
     "url_or_path": "https://www.currentscience.ac.in/Volumes/111/01/0027.pdf ; " + R + "rakhigarhi/vahia2016currsci.pdf",
     "sha256": "88b9639872704270856f45b543457a8a4df1ea1990a9adbc41b0680e324a3375"},
    {"id": "shinde2018cemetery",
     "citation": ("Shinde, V. S., Kim, Y. J., Woo, E. J., Jadhav, N., Waghmare, P., Yadav, Y., et al. 2018. Archaeological and anthropological "
                  "studies on the Harappan cemetery of Rakhigarhi, India. PLoS ONE 13(2): e0192299. doi:10.1371/journal.pone.0192299"),
     "url_or_path": ("https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0192299 ; " + R + "rakhigarhi/shinde2018plosone.pdf"),
     "sha256": "7f341bef726fe6b9508d73295c5bcbb18685f722f925ceaa9c958155f1d762c2"},
    {"id": "shinde2019genome",
     "citation": ("Shinde, V., Narasimhan, V. M., Rohland, N., Mallick, S., Mah, M., Lipson, M., Nakatsuka, N., Adamski, N., et al. 2019. An Ancient "
                  "Harappan Genome Lacks Ancestry from Steppe Pastoralists or Iranian Farmers. Cell 179(3): 729-735.e10. doi:10.1016/j.cell.2019.08.048"),
     "url_or_path": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6800651/ ; " + R + "rakhigarhi/shinde2019cell-pmc.html",
     "sha256": "96af277e93e87330068487330c79435bada951b87aaa8ad76e72de1775a7aac5"},
    {"id": "shinde2023perspectives",
     "citation": ("Shinde, V. 2023. Introduction to the Harappan Culture: Recent Perspectives. In V. Shinde, D. H. Shin and B. Bhattacharyya (eds), "
                  "New Perspectives on the Harappan Culture in Light of Recent Excavations at Rakhigarhi: 2011–2017, Volume 1: Bioarchaeological "
                  "Research on the Rakhigarhi Necropolis, pp. 1-18. Oxford: Archaeopress. Consulted in the publisher's sample PDF."),
     "url_or_path": ("https://www.archaeopress.com/Archaeopress/DMS/01839B015BD74EFBAA938B5AC62EBB33/9781803275918-sample.pdf ; "
                     + R + "rakhigarhi/archaeopress-9781803275918-sample.pdf"),
     "sha256": "1d241a3a4047f6294f8cb361c2260c68b13cdd84059c20f90df1d87701a475f7"}
  ],
  "notes": NOTES_TEXT
}

json.dump(data, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("ok")
