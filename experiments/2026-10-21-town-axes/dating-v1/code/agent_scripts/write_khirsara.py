import json, pathlib, sys

OUT = pathlib.Path(sys.argv[1])
UTC = sys.argv[2]
IAR = "data/raw/2026-10-21-town-axes/dating/shared-iar/"
CEN = "data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/"

HL = ("The paper says ages were normalised to delta 13C = -25.0 per mil following Stuiver and Polach (1977) and calibrated with OxCal v4.1.7 and IntCal13 (p. 6), "
      "which treats them as conventional 5568-year ages; the half-life itself is not printed, so we leave half_life_printed null and copy the age. ")
PHASE = "not stated per sample; the authors place the whole dated sequence in Mature Harappan Phases 1A, TP and 1B"


def rc(lab, mat, ctx, age, sig, bc, bp, table, page, note):
    return {"lab_no": lab, "material": mat, "context": ctx, "phase": PHASE,
            "age_bp_printed": age, "sigma_printed": sig, "half_life_printed": None,
            "age_bp_5568": age, "sigma_5568": sig,
            "calibrated_published": f"{bc} cal BC; {bp} cal BP (2 sigma, 95.4%)",
            "curve": "IntCal13, OxCal v4.1.7",
            "source": "pokharia2017khirsara", "page": f"{page}, {table}", "note": HL + note}


Z38 = ("Index trench Z38/1 was dug in or next to the citadel and reached bedrock at 6.36 m (iar2010-11 pdf p. 32), so this sample comes from the lowest metre or so "
       "of the deposit; the source does not assign it to a structural phase. ")

citadel_rc = [
    rc("BS-3362", "wood charcoal", "Trench Z-38/1, depth 530-560 cm", 3900, 70, "2198-2505", "4147-4454", "Table 2", 9,
       Z38 + "BSIP liquid-scintillation date."),
    rc("BS-3358", "wood charcoal", "Trench Z-38/1, depth 500-550 cm", 3860, 70, "2136-2492", "4085-4441", "Table 2", 9,
       Z38 + "BSIP liquid-scintillation date."),
    rc("BS-3310", "wood charcoal", "Trench Z-38/1, depth 450-460 cm", 3920, 90, "2137-2666", "4086-4615", "Table 2", 9,
       Z38 + "BSIP liquid-scintillation date."),
    rc("Beta-427231", "charred grain (Table 4 title: 'Barley and Wheat respectively'; this is the first, asterisked, sample)", "Trench Z-38/1, depth 530-560 cm",
       3750, 30, "2038-2231", "3987-4180", "Table 4", 10,
       Z38 + "AMS date on a crop grain from the same depth as BS-3362 but about 150 radiocarbon years younger; the paper does not discuss the difference."),
    rc("Beta-422014", "charred grain (wheat, by the order given in the Table 4 title)", "Trench Z-38/1, depth 530-560 cm",
       3760, 30, "2091-2287", "3993-4236", "Table 4", 10,
       Z38 + "AMS date on a crop grain from the same depth as BS-3362."),
]

town_rc = [
    rc("GdA-2847", "soil sediment (bulk organic matter)", "Trench AF-35/1, depth 400 cm", 4155, 25, "2659-2876", "4608-4825", "Table 3", 9,
       "Gliwice AMS date, the oldest determination published for the site and the lowest of the dated levels in trench AF-35; the authors' Phase 1A begins at "
       "'~4600' yrs BP, which matches this calibrated range. Bulk sediment can contain carbon older than the layer."),
]

whole = {
    "part": "whole town: the outer fortification enclosing about 310 x 270 m",
    "layout_phase": ("first construction phase of the main fortification (the original wall, 3.40 m thick), within the Mature Harappan occupation; the excavators "
                     "do not say in print which of the site's five structural phases it belongs to"),
    "what_was_built": (
        "In the first season the excavators found 'The massive fortification built of stones with dressed outer face', 'roughly rectangular in plan' and measuring "
        "310 x 270 m (iar2009-10 p. 16). Across the northern wall they found that 'the fortification was repaired and widened at least thrice in the subsequent phases': "
        "'The thickness of main fortification was originally 3.40m', with thick mud plaster on its outer face; 'a formidable masonry wall with a thickness of 2.80m was added "
        "to the main fortification on the northern side, in the second phase', resting on a hard rammed base of silt, lime and mud over bedrock, together with a salient; a "
        "0.90 m reinforcement was added on the inner side in a third phase; the extant height including foundation is about 7.20 m (p. 17). The eastern wall, 7.10 m wide, "
        "'was constructed in three stages'; the southern wall, 4.40 m wide, has an entrance at the south-eastern corner with a stepped pathway and guard rooms, closed in a "
        "later phase; a north-eastern bastion of 8.80 x 7.60 m and a protection wall about 2.30 m wide, 5.80 m outside the fortification, 'probably raised to provide "
        "protection to the site from the danger of floods' (pp. 19-20). A 'Ware House' of parallel stone walls on a rammed mud platform stands near the south-eastern "
        "entrance (pp. 20-21). Later seasons exposed bastions on the southern wall and an inner fortification wall near a probable south-eastern gate (iar2012-13 p. 28). "
        "The excavators' summary is 'a fortified settlement showing planned wall-structures, water-well with a rectangular trough, a citadel, the ware house, factory site "
        "and habitational annexes' (pokharia2017khirsara p. 4)."),
    "locator": "iar2009-10 pp. 16-21; iar2012-13 p. 28; pokharia2017khirsara p. 4",
    "excavator_range_bce": None,
    "excavator_basis": (
        "Radiocarbon. The excavators and their co-authors date the sequence in years BP only: 'the early Phase IA (~4600-4300 yrs BP), and the mature Phase IB "
        "(~4100-3900 yrs BP) separated by a Transitional Phase (TP) (~4300-4100 yrs BP)' (pokharia2017khirsara p. 9), and the site 'continued to flourish for ~700 years "
        "from ca. ~4600 to ~3900yrs BP', with urbanization 'around ~4,600yrs BP (~2600 BC)' (p. 14). Phase 1A contains three of the five structural phases (p. 13). "
        "No range in years BC is printed for the first construction of the fortification, so we leave the field null."),
    "radiocarbon": town_rc,
    "bayesian_start": None,
    "syntheses": [
        {"source": "iar2013-14", "page": "pdf p. 204 (Palaeobotanical and Pollen Analytical Investigations, entry 1)", "range_bce": [2500, 2000],
         "statement": ("The Birbal Sahni Institute's annual note on the Khirsara plant remains describes 'the exploitation of botanical resources by ancient settlers at the "
                       "site from 2500-2000 B.C.'"),
         "disagreement": ("Starts the occupation a century later than the '~2600 BC' of pokharia2017khirsara, written by the same palaeobotanist with the excavators; "
                          "no basis is given.")}
    ],
    "conflicts": (
        "The first-season report numbers the wall's own construction phases (original wall, additions in a second and third phase), while the 2010-11 report numbers five "
        "structural phases for the whole site and pokharia2017khirsara groups them into Phase 1A (three) and Phase 1B (two); no source maps one numbering onto the other for "
        "the outer wall. The site's size is printed as 310 x 270 m (iar2009-10) and about 310 x 230 m (pokharia2017khirsara p. 4). The only calendar statements are the "
        "'~2600 BC' start in pokharia2017khirsara and 2500-2000 B.C. in iar2013-14.")
}

citadel = {
    "part": "citadel on the southern side, inside the general fortification",
    "layout_phase": "second structural phase (of five), within Phase 1A of pokharia2017khirsara",
    "what_was_built": (
        "The 2010-11 season found 'the existence of a well laid citadel within general fortification on the southern side', whose walls have a core 'built of multi-coloured "
        "mud brick' with 'roughly dressed stone veneering which rests over the bed rock'; the northern citadel wall is about 87 m long, and a large multi-coloured mud-brick "
        "floor lies against the inner side of the eastern wall. 'The foundation of citadel was laid in second structural phase which overlies a thick layer of hard rammed base "
        "of the bed rock', with large roughly dressed stones in the base and later additions and alterations; the mud bricks are in the ratio 1:2:4 (iar2010-11 pdf pp. 32-33). "
        "The index trench Z38/1 showed 'the evidences of first human activity right on the top of the bed rock' and 'five distinct structural phases', the site being "
        "'first occupied by the Harappans of Urban phase i.e. the Mature Harappans' (pdf p. 32). A narrow entrance 1.40 m wide in the northern citadel wall, later closed, was "
        "found in 2012-13 (iar2012-13 p. 28). Phase 1A structures, three structural phases in all, 'were raised with sandstone with mud-mortar and multi-color mud bricks, "
        "frequently used in the citadel area' (pokharia2017khirsara p. 13)."),
    "locator": "iar2010-11 pdf pp. 32-33; iar2012-13 p. 28; pokharia2017khirsara p. 13",
    "excavator_range_bce": None,
    "excavator_basis": ("Radiocarbon, printed in years BP only: Phase 1A '~4600-4300 yrs BP' (pokharia2017khirsara p. 9). The second structural phase lies inside Phase 1A, "
                        "but no date is printed for it."),
    "radiocarbon": citadel_rc,
    "bayesian_start": None,
    "syntheses": [],
    "conflicts": ("The grain dates from 530-560 cm in Z-38/1 (Beta-427231, Beta-422014; 3750-3760 BP, 2287-2038 cal BC) are about 150 years younger than the charcoal date "
                  "BS-3362 from the same depth (3900 BP, 2505-2198 cal BC) and fall in the span the authors call the Transitional Phase and Phase 1B, although the deposit "
                  "lies near the base of the sequence; the paper does not discuss this.")
}

factory = {
    "part": "factory area north of the citadel, with its own fortification",
    "layout_phase": "the phase after the 'early phase' structures (IAR 2012-13); IAR 2010-11 says the main factory structure was built in the second phase",
    "what_was_built": (
        "North of the citadel the 2010-11 season exposed a 'Factory Site or Industrial Area' of large interconnected rooms with stone-paved floors and furnaces, two structures "
        "separated by a 5 m lane, and noted that 'the main structure was built in the second phase' (iar2010-11 pdf p. 33). In 2012-13 the excavators found below it 'early "
        "phase structures in the form of small rooms' with hearths and rammed kankar floors, and state that 'In the next phase, the foundation for "
        "the factory was laid and raised over the early phase structures. During this phase, a separate fortification was raised for the factory area with a double entrance "
        "from the north', with a street about 4.70 m wide leading from the entrance and a guard room (iar2012-13 p. 29). A series of kilns outside the main wall was "
        "enclosed by a second fortification wall 2.60 m wide (p. 30)."),
    "locator": "iar2010-11 pdf p. 33; iar2012-13 pp. 29-30",
    "excavator_range_bce": None,
    "excavator_basis": "No date is printed for the factory area or its enclosure; it belongs to the Mature Harappan sequence dated in pokharia2017khirsara (p. 9).",
    "radiocarbon": [],
    "bayesian_start": None,
    "syntheses": [],
    "conflicts": ("None between sources; the two season reports agree that the factory complex was built in the second phase of occupation, over earlier small rooms. "
                  "We do not know whether the factory-area fortification is the same construction phase as the citadel foundation.")
}

doc = {
    "town": "khirsara",
    "compiled_utc": UTC,
    "parts": [whole, citadel, factory],
    "first_occupation": {
        "phase": "first structural phase (Mature Harappan, Phase 1A), directly on bedrock",
        "range_bce": [2600, None],
        "basis": (
            "Radiocarbon, as summarised by the excavators' co-authors: urbanization 'around ~4,600yrs BP (~2600 BC)' and Phase 1A '~4600-4300 yrs BP' "
            "(pokharia2017khirsara pp. 9, 14), the oldest published determination being GdA-2847 (4155±25 BP, 2876-2659 cal BC) from the lowest dated level in trench AF-35. "
            "The excavators found the first human activity 'right on the top of the bed rock' and state that the site 'was first occupied by the Harappans of Urban phase "
            "i.e. the Mature Harappans', with no earlier culture (iar2010-11 pdf p. 32)."),
        "locator": "iar2010-11 pdf p. 32; pokharia2017khirsara pp. 9, 14"
    },
    "sources": [
        {"id": "pokharia2017khirsara",
         "citation": ("Pokharia, A. K., R. Agnihotri, S. Sharma, S. Bajpai, J. Nath, R. N. Kumaran and B. C. Negi 2017. Altered cropping pattern and cultural continuation with "
                      "declined prosperity following abrupt and extreme arid event at ~4,200 yrs BP: Evidence from an Indus archaeological site Khirsara, Gujarat, western India. "
                      "PLoS ONE 12(10): e0185684. doi:10.1371/journal.pone.0185684. Pages cited as numbered in the PDF (N / 17)."),
         "url_or_path": "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0185684&type=printable; data/raw/2026-10-21-town-axes/dating/khirsara/pokharia2017khirsara.pdf",
         "sha256": "6bfac8a62ed8fa170bcc5ee719c38f077e9a75876768f393f96f6792333aaf47"},
        {"id": "iar2009-10",
         "citation": ("Archaeological Survey of India 2016. Indian Archaeology 2009-10 - A Review. New Delhi: Archaeological Survey of India. Entry 7, 'Excavation at Khirsara, "
                      "District Kachchh' (Excavation Branch-V, Vadodara, Jitendra Nath and others), pp. 16-25."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2009-2010.pdf; " + CEN + "IAR2009-10.pdf",
         "sha256": "16574ffcfc86cb9e635370ef4d7333d2266af61f2a80a4e486c4df26ecd36c73"},
        {"id": "iar2010-11",
         "citation": ("Archaeological Survey of India 2016. Indian Archaeology 2010-11 - A Review. New Delhi: Archaeological Survey of India. Entry 6, 'Excavation at Khirsara, "
                      "District Kachchh' (Jitendra Nath and others), pdf pp. 32-34 of the copy (two-column pages whose printed page numbers are irregular)."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2010-2011.pdf; " + IAR + "iar2010-11.pdf",
         "sha256": "c26aaea99cbf0331e0bd891a3e1f3da842ff102307cd314c07ac98af13b3b29a"},
        {"id": "iar2012-13",
         "citation": ("Archaeological Survey of India 2015. Indian Archaeology 2012-13 - A Review. New Delhi: Archaeological Survey of India. Entry 10, 'Excavations at Khirsara, "
                      "District Kachchh' (Jitendra Nath and others), pp. 28-30."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2012-2013.pdf; " + IAR + "iar2012-13.pdf",
         "sha256": "43a3aa12807f45870a8e73f6bf9b3688938f23bccd6a344b1671e0742bf746be"},
        {"id": "iar2013-14",
         "citation": ("Archaeological Survey of India. Indian Archaeology 2013-14 - A Review. New Delhi: Archaeological Survey of India. Section 5, 'Palaeobotanical and Pollen "
                      "Analytical Investigations' (Birbal Sahni Institute of Palaeobotany; A. K. Pokharia), entry 1, Khirsara, pdf p. 204."),
         "url_or_path": "https://www.asiaurangabadcircle.com/assets/files/publications/2013-2014.pdf; " + IAR + "iar2013-14.pdf",
         "sha256": "4f5d86c38dd1f05671ba4a4c5a9749e7b09e61fce7f05639b861c7d8c54e7b41"}
    ],
    "notes": (
        "Khirsara (Gadh Wali Wadi, Nakhatrana taluka, Kachchh) was excavated by Excavation Branch-V of the Archaeological Survey of India, Vadodara, under Jitendra Nath in "
        "four seasons from 2009-10 to 2012-13. The excavators describe a single-culture Mature Harappan site with five structural phases on bedrock; their palaeobotanical "
        "co-authors group these into Phase 1A (three structural phases), a Transitional Phase and Phase 1B (two). We record three parts: the outer fortification, the citadel "
        "founded in the second structural phase, and the factory area with its own enclosure built in the phase after the earliest rooms. "
        "The radiocarbon list holds the three BSIP charcoal dates and two Beta grain dates from the index trench Z-38/1 near the base of the deposit, under the citadel part, "
        "and the oldest date from trench AF-35 (GdA-2847), under the whole town. We left out the determinations from shallower levels (190-275 cm), whose phase the paper does not "
        "state and whose calibrated ranges fall mostly after the authors' Phase 1A: GdA-2850 (AF-35, 220 cm, 3810±25 BP) and GdA-2849 (AF-35, 275 cm, 3805±25 BP), BS-3466 (AF-35, 190 cm, 3230±70 BP), BS-3471 (AE-35/4, "
        "221-251 cm, 3290±70 BP), BS-3469 (AE-35/4, 210-240 cm, 3390±70 BP), BS-3354 (Z-37/2, 205-215 cm, 3390±70 BP) and BS-3468 (S-37/1, 200-210 cm, 3800±80 BP) "
        "(pokharia2017khirsara p. 9, Tables 2-3). The local census copy of the PLOS ONE article (" + CEN + "KHIRSARA2017.html) is the same paper in HTML; we downloaded the "
        "PDF for page numbers. No final report, no per-sample phase attribution and no Bayesian model were found; Indian Archaeology - A Review for 2011-12 is not on the copy "
        "site we used. Some sources state wall directions; following our method we did not record them.")
}

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)
