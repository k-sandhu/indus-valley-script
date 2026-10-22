"""Write experiments/2026-10-21-town-axes/dating-v1/towns/nausharo.json."""
import json
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Users\sandh\OneDrive\Projects\indus_valley_script")
OUT = ROOT / "experiments" / "2026-10-21-town-axes" / "dating-v1" / "towns" / "nausharo.json"
UTC = sys.argv[1]

BETA_NOTE = ("Measured by Beta Analytic (table note). The table gives the 14C age BP and a 68 % (1 sigma) calibrated "
             "range only, without naming the half-life, the calibration curve or the program, and without context or "
             "material; we therefore leave the 5568 fields and the curve empty. The sample comes from Period I on the "
             "north tepe, two or three sub-periods before the Period II layout (IB and IC precede ID, which precedes II), "
             "so it gives only an upper limit for the Indus layout. No determination from Period ID or Period II is "
             "published in the sources we could read.")

def beta(lab, phase, age, sigma, cal):
    return {"lab_no": lab, "material": None, "context": "Kachi-Bolan, Nausharo " + phase + " (site/period column of the table)",
            "phase": "Nausharo " + phase, "age_bp_printed": age, "sigma_printed": sigma, "half_life_printed": None,
            "age_bp_5568": None, "sigma_5568": None, "calibrated_published": cal + " (68 % (1 sigma) cal BC range; no 2 sigma range printed)",
            "curve": None, "source": "jarrige2011shahrisokhta", "page": "9 (Table 1)", "note": BETA_NOTE}

RC = [
    beta("Beta 18843", "IB", 4070, 70, "cal BC 2865-2498"),
    beta("Beta 18842", "IC", 4030, 70, "cal BC 2855-2470"),
    beta("Beta 18844", "IC", 4010, 80, "cal BC 2853-2463"),
]

SYN_KENOYER_II = {
    "source": "kenoyer2020origin", "page": "219 (Table 1)", "range_bce": [2600, 2450],
    "statement": ("Kenoyer's chronology table, citing Possehl 1994, Meadow and Kenoyer 2005 and Kenoyer 2015, equates "
                  "'Nausharo, Period II' with 'Harappa: Period 3A, Initial 2600-2450 BCE'."),
    "disagreement": ("About a century older than the excavator's 'sans doute entre 2 500 et 2 300 avant notre ère' for Period "
                     "II, and its start overlaps the excavator's 2600-2500 BC for Period ID."),
}
SYN_JDQ = {
    "source": "jarrige2011shahrisokhta", "page": "9, 27", "range_bce": None,
    "statement": ("The mission's later restatement: the calibrated 14C dates 'are consistent with the ceramic sequences "
                  "which would place Nausharo Period IB-D ... between 2800 and 2500 BC'; the Indus civilization's three "
                  "periods, 'approximately ... between 2500 and 1900/1800 BC' (Amri IIIA-C, Harappa 3A-C), match 'the "
                  "\"Harappan\" sequence defined at Nausharo, with Periods II, III and IV' (p. 9); Period ID 'can be dated "
                  "to between 2600 and 2500 BC' (p. 27). Period II therefore begins about 2500 BC."),
    "disagreement": None,
}
SYN_POSTER = {
    "source": "didier2014nausharo", "page": "poster panel (pdf p. 2)", "range_bce": [2500, 1900],
    "statement": ("The mission's 2014 poster dates Period ID 'between 2600 and 2500 BC', the Indus civilization at Nausharo "
                  "'(2500-1900 BC)', says the remains of Periods II and III 'show the features of a classical Indus "
                  "Civilization site with a planned architecture associated with drains and sanitary installations', and "
                  "captions the site plan with 'superimposed drains of periods II-III (2500-2100 BC)'."),
    "disagreement": None,
}

part_south = {
    "part": "south tepe: Period II Indus settlement (enclosure wall with gate, street-bounded block)",
    "layout_phase": "Period II (first Indus occupation)",
    "what_was_built": (
        "With Period II 'Nausharo devient un site de la civilisation de l'Indus'. The new settlement was laid out south of "
        "the Period I ruins 'sur un emplacement jusqu'alors vierge', 'directement sur le sol naturel'. On its south side "
        "stood a mud-brick wall preserved up to 3.80 m high and on average 3.50 m wide, with a gateway 3.12 m wide, reached "
        "by a ramp rebuilt several times, set in a thickening of the wall about 6 m wide. A housing block bordered by "
        "streets was partly excavated; its five building levels, unlike those of Period I, 's'inscrivent dans le plan "
        "général d'un bloc', the walls being raised several times within one general plan 'selon un principe commun aux "
        "villes de la civilisation de l'Indus'."),
    "locator": "jarrige1996nausharo pp. 855, 857",
    "excavator_range_bce": [2500, 2300],
    "excavator_basis": (
        "Ceramic cross-dating anchored on radiocarbon dates of the preceding period. Jarrige equates Period II with the "
        "'first Harappan occupation' at Chanhu-daro and Amri IIIA and dates it 'sans doute entre 2 500 et 2 300 avant notre "
        "ère' (jarrige1996nausharo p. 828); Period ID, a single architectural phase, has C14 dates 'entre 2 600 et 2 500 "
        "avant notre ère' and immediately precedes the start of the Indus civilization, 'daté autour de 2 500 avant notre "
        "ère' (pp. 827, 849). The Period ID determinations themselves are not listed in this paper or in the 2011 "
        "table."),
    "radiocarbon": RC,
    "bayesian_start": None,
    "syntheses": [SYN_JDQ, SYN_POSTER, SYN_KENOYER_II],
    "conflicts": (
        "The excavators place Period II at about 2500-2300 BC, after Period ID at 2600-2500 BC, and keep this in 2011 and "
        "2014. Kenoyer's table, which equates Period II with Harappa 3A, puts it at 2600-2450 BCE, so the start of the "
        "Indus layout at Nausharo differs by about a century between the two schemes. The only published determinations "
        "we found (Period IB and IC, 68 % ranges reaching 2498-2463 cal BC at their young ends) do not decide between them."),
}

part_north = {
    "part": "north tepe: Period II monumental building and platform-wall over the Period ID enclosure",
    "layout_phase": "Period II (first Indus occupation), on structures of Period ID",
    "what_was_built": (
        "Period ID, the last pre-Indus sub-period, had already built 'd'imposantes plates-formes en briques crues' on the "
        "ruins of Periods IB and IC, and a compartmented platform built into a wall 7.75 m wide that bounded the ID "
        "settlement (pp. 849, 851); Jarrige stresses that Period ID still lacks the division into "
        "quadrangular blocks and the baked-brick water works of the Indus towns (p. 854). In Period II the southern "
        "enclosure wall of the ID settlement 'est alors rehaussé pour former un mur plate-forme de briques crues de 11 "
        "mètres de large', with what seems to be a reservoir against one face whose water passed through the wall in a "
        "baked-brick drain, the same drain line reappearing 80 m further on where it crosses the enclosure wall of the "
        "Period II settlement (pp. 855-856). On the summit of the north tepe stood a monumental building with very massive "
        "walls and an entrance corridor, founded on timber beams and pebble packing laid on the levelled Period ID remains; "
        "'La poterie provenant de ce monument date de la période II'. Jarrige concludes that the Period II settlement 'a été "
        "dominée au nord par un ensemble monumental' (pp. 856-857)."),
    "locator": "jarrige1996nausharo pp. 849, 851, 854-857",
    "excavator_range_bce": [2500, 2300],
    "excavator_basis": "As for the Period II settlement: ceramic cross-dating, with Period ID radiocarbon-dated to 2600-2500 BC (jarrige1996nausharo pp. 827-828, 849).",
    "radiocarbon": [],
    "bayesian_start": None,
    "syntheses": [SYN_KENOYER_II],
    "conflicts": (
        "The platform tradition on the north tepe begins before the Indus phase (Period ID), so the date of 'the platform' "
        "depends on which structure is meant: the ID platforms and enclosure (2600-2500 BC by the excavators) or their "
        "Period II heightening into an 11 m platform-wall and the monumental building (2500-2300 BC by the excavators, "
        "2600-2450 BCE in Kenoyer's equation with Harappa 3A). The Period I radiocarbon dates are listed under the south "
        "tepe part."),
}

part_iii = {
    "part": "whole settlement (south and north tepe): Period III blocks and perpendicular streets",
    "layout_phase": "Period III (second Indus occupation)",
    "what_was_built": (
        "'Sur les ruines de la période II, après une vaste opération de remblaiement ou de nivellement, l'agglomération de "
        "période III se déploie, organisée en grands blocs quadrangulaires relativement réguliers d'environ 1 000 m2 de "
        "superficie, séparés les uns des autres par des rues et des ruelles perpendiculaires'; similar blocks appear on the "
        "north tepe after new levelling works over the ruined Period II monument (pp. 856-857, 859). Each block is divided "
        "into dwelling units with hearths and small baked-brick bathrooms draining into jars set in the lanes; one block "
        "(block no. 2) was cleared entirely, with a group of two-storey pottery kilns in one part. Successive raisings of floors, streets "
        "and lanes were planned for whole quarters, and 'la planification ... s'étend bien à l'ensemble de l'agglomération "
        "de la période III', a mud-brick version of the town planning of Mohenjo-daro except for water works in baked "
        "brick (p. 859)."),
    "locator": "jarrige1996nausharo pp. 856-859",
    "excavator_range_bce": [2300, 2100],
    "excavator_basis": (
        "Ceramic cross-dating: Period III corresponds to the urban apogee of Mohenjo-daro and Harappa 'à partir d'environ 2 "
        "300 avant notre ère' (jarrige1996nausharo p. 828), and its pottery is dated 'entre environ 2 300 et 2 100 avant "
        "notre ère' (p. 859). No radiocarbon determination is cited."),
    "radiocarbon": [],
    "bayesian_start": None,
    "syntheses": [
        {"source": "kenoyer2020origin", "page": "219 (Table 1)", "range_bce": [2450, 2200],
         "statement": "Kenoyer's table equates 'Nausharo, Period III' with 'Harappa: Period 3B, Middle 2450-2200 BCE'.",
         "disagreement": "Starts about a century and a half earlier than the excavator's c. 2300 BC."},
        {"source": "didier2014nausharo", "page": "poster panel (pdf p. 2)", "range_bce": [2300, 2100],
         "statement": "The mission's poster dates objects 'from period III (2300-2100 BC)' and the superimposed drains of Periods II-III to 2500-2100 BC.",
         "disagreement": None},
    ],
    "conflicts": (
        "The excavators date the Period III replanning to about 2300-2100 BC; Kenoyer's equation with Harappa 3B gives "
        "2450-2200 BCE. Neither figure rests on a published Nausharo determination from Period III."),
}

doc = {
    "town": "nausharo",
    "compiled_utc": UTC,
    "parts": [part_south, part_north, part_iii],
    "first_occupation": {
        "phase": "Period I (sub-periods IA to IC, then ID), on the north tepe",
        "range_bce": [3000, 2600],
        "basis": ("The excavator's equation of Period I with Mehrgarh VII: 'une première période, identique à la période "
                  "finale (période VII) de Mehrgarh, entre environ 3 000 et 2 600 avant notre ère', followed by Period ID "
                  "(2600-2500 BC by C14) (jarrige1996nausharo pp. 826-827). The 2014 poster gives Period I as 'similar to "
                  "those of Mehrgarh VI-VII (3100-2600)', its heading as 3100-2500 BC and IB-IC as 2900-2600 BC; the 2011 "
                  "paper places IB-ID between 2800 and 2500 BC on calibrated 14C dates."),
        "locator": "jarrige1996nausharo pp. 826-827; didier2014nausharo poster panel; jarrige2011shahrisokhta p. 9",
    },
    "sources": [
        {"id": "jarrige1996nausharo",
         "citation": ("Jarrige, J.-F. 1996. Les fouilles de Nausharo au Balochistan pakistanais et leur contribution à "
                      "l'étude de la civilisation de l'Indus. Comptes rendus des séances de l'Académie des Inscriptions et "
                      "Belles-Lettres 140(3): 821-878. doi:10.3406/crai.1996.15636"),
         "url_or_path": ("https://www.persee.fr/doc/crai_0065-0536_1996_num_140_3_15636 (read page by page in Persée's "
                         "open HTML view, ?pageId=T1_821 to T1_878; the PDF download sits behind a captcha and was not "
                         "used); local data/raw/2026-10-21-town-axes/dating/nausharo/jarrige1996crai-p821.html to "
                         "jarrige1996crai-p878.html, one SHA-256 per page in acquisitions.jsonl there"),
         "sha256": None},
        {"id": "jarrige2011shahrisokhta",
         "citation": ("Jarrige, J.-F., Didier, A. and Quivron, G. 2011. Shahr-i Sokhta and the chronology of the "
                      "Indo-Iranian regions. Paléorient 37(2): 7-34. doi:10.3406/paleo.2011.5420"),
         "url_or_path": ("https://shs.hal.science/halshs-02978691 (HAL deposit of the Persée PDF); local "
                         "data/raw/2026-10-21-town-axes/dating/nausharo/jarrige2011paleorient.pdf (printed page = PDF page + 3)"),
         "sha256": "2b532fb435f09aa095be65920470dd894f0ff61d8d64a0dc5305a2631221a063"},
        {"id": "didier2014nausharo",
         "citation": ("Didier, A. and Sarmiento Castillo, D. 2014. Excavations at Nausharo (1985-1996) and other sites "
                      "[poster, Mission archéologique de l'Indus, direction J.-F. Jarrige]. International Seminar 'French "
                      "Contributions to Pakistan Studies', Islamabad, Karachi and Banbhore, February 2014. HAL halshs-02986859."),
         "url_or_path": "https://shs.hal.science/halshs-02986859/file/PostersMAFBI%204.pdf; local data/raw/2026-10-21-town-axes/dating/nausharo/didier2014poster.pdf",
         "sha256": "c2d17b23efecc2e32e000c52732d7f9a67fec9ed37ca175095bdde1894ac8f6f"},
        {"id": "kenoyer2020origin",
         "citation": ("Kenoyer, J. M. 2020. The Origin and Development of the Indus Script: Insights from Harappa and other "
                      "Sites. In K. Lashari (ed.), Studies on Indus Script, pp. 217-236. Karachi: National Fund for Mohenjodaro."),
         "url_or_path": ("https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script-2.pdf; "
                         "local research/literature/sources/kenoyer2020_origin.pdf (held before this study)"),
         "sha256": "43cb37e69fb278e0301d01a0825146989f9ed0ac36db04003808a498d9e81a2e"},
    ],
    "notes": (
        "Nausharo shows the Indus layout arriving in two steps, and we record three parts. In Period II the first Indus "
        "settlement was founded on virgin ground south of the Period I mound, enclosed on its south side by a mud-brick "
        "wall with a gate and planned as street-bounded blocks; on the old north mound the Period ID enclosure wall was "
        "raised into an 11 m platform-wall and a monumental building was put up. In Period III, after both areas had been "
        "levelled, the whole settlement was rebuilt as regular blocks of about 1,000 square metres separated by "
        "perpendicular streets and lanes. Our main source is the excavator's own synthesis (Jarrige 1996), which we read "
        "in Persée's open page view because the PDF download is behind a captcha; the mission's annual reports in "
        "Pakistan Archaeology 10-22 (1986), 23 (1988), 24 (1989) and 25 (1990), the Mehrgarh Field Reports (1995), "
        "Jarrige's chapter in Urban Form and Meaning in South Asia (1993), Quivron's 1994 and 2000 pottery studies and "
        "Possehl's compilations were not available to us online, so the Period ID and Period II radiocarbon determinations "
        "that Jarrige mentions remain unlisted. The only Nausharo determinations we found are three Beta Analytic dates "
        "for Periods IB and IC in the 2011 Paléorient table; we attach them to the Period II part as an upper limit. No "
        "Bayesian model exists for the site as far as we could find. All dates in the excavators' texts are calendar "
        "dates 'avant notre ère' given without stating whether or how radiocarbon results were calibrated, except the "
        "2011 table, which prints 1-sigma calibrated ranges without naming the curve. Directions and axes of walls and "
        "blocks given in these sources are deliberately not recorded."),
}

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)
