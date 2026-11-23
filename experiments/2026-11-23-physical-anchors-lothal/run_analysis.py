#!/usr/bin/env python3
"""
Execute Part A (Q-0011 H-904, Q-0012 M-1383) and Part B (Q-0019 Lothal attachment
geometry & frozen component-grouped permutation / LOCO-CV tests) strictly under
PROTOCOL.md (frozen 2026-11-23).
"""

import csv
import hashlib
import json
import math
import os
import random
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, accuracy_score

OUT_DIR = "experiments/2026-11-23-physical-anchors-lothal"
RAW_DIR = "data/raw/2026-11-23-physical-anchors-lothal"
LIPI_PATH = "data/normalized/lipi_observed_faces.jsonl"
LOTHAL_TABLE_PATH = "data/six-hour/lothal/table-coding/reviewed-pass.csv"
CISI1_BASIC_PATH = "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl"
CISI2_BASIC_PATH = "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi2-basic-data.jsonl"
SELECTED_TRACE_PATH = "experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/selected-trace-observations.json"
PROTOCOL_PATH = os.path.join(OUT_DIR, "PROTOCOL.md")

SEED = 20261123
B_PERM = 10000
B_PERM_LOGREG = 1000

# Canonical Wells/Lipi numeric stroke sign codes (001-045, excluding 000 = unknown/damaged)
STROKE_NUMERAL_CODES = {f"{i:03d}" for i in range(1, 46)}

# Frozen deterministic mapping from Frenez & Tosi (2005) Table 1 physical_type to reverse_class_6
REVERSE_CLASS_6_MAP = {
    "wooden_box": "wood_plank_peg",
    "locker": "wood_plank_peg",
    "structure": "wood_plank_peg",
    "peg_on_wall": "wood_plank_peg",
    "parallel_canes": "reed_cane_matting",
    "woven_straw": "reed_cane_matting",
    "wicker": "reed_cane_matting",
    "pottery": "jar_vessel_pottery",
    "leather_sack": "flexible_cloth_leather",
    "single_rope": "cord_rope_only",
    "undiagnostic": "unidentifiable_other",
    "other": "unidentifiable_other",
}

MOBILITY_MAP = {
    "wooden_box": "mobile_container",
    "pottery": "mobile_container",
    "parallel_canes": "mobile_container",
    "woven_straw": "mobile_container",
    "wicker": "mobile_container",
    "leather_sack": "mobile_container",
    "structure": "architectural_fixture",
    "locker": "architectural_fixture",
    "peg_on_wall": "architectural_fixture",
    "single_rope": "",
    "undiagnostic": "",
    "other": "",
}

CONTEXT_BASIS_MAP = {
    "W": "documented_findspot",
    "O": "documented_findspot",
    "W1": "stamp_derived_inference",
    "W2": "area_association",
    "?": "unresolved",
}

# Physical reverse notes extracted strictly from Frenez & Tosi (2005) prose (PDF pp. 12-19 / printed pp. 74-81)
# WITHOUT using inscription signs.
FRENEZ_PROSE_REVERSE = {
    "L-124": "Interwoven straw imprints on gently pressed rear (~2 cm mouth); proposed small vessel cover (p. 80-81; Fig. 7).",
    "L-125": "Thin parallel lines on back (not well-polished wood); string impressions on two breakage sides (p. 80).",
    "L-126": "Soft non-woven material forming irregular pleats on back; proposed leather sack/bag (p. 81; Fig. 7).",
    "L-130": "Double concave rough irregular rear, upper parallel stick marks, corner-like recess (p. 75-76; Fig. 4).",
    "L-133": "Curved vessel rim impression with wheel marks (p. 80; Fig. 7).",
    "L-134": "Impressions of thin parallel canes on two sides (p. 78).",
    "L-140": "Impressions of thin parallel canes on two sides (p. 78; Fig. 5).",
    "L-141": "Massive polygonal clay lump (~6x8x4 cm) with unclear angular imprints on upper edge (p. 76).",
    "L-142": "Plano-convex pill; flat rear with braided string impressions; 5 fingernail tallies (p. 79; Fig. 6).",
    "L-143": "Flat section; horizontal vegetal element (cane/reed bundle) tied with orthogonal cord (p. 78; Fig. 5).",
    "L-144": "Quadrangular locker using movable wooden stakes (p. 77; Fig. 5; Rao Fig. 38 B-2).",
    "L-145": "Parallelepiped below angle between 2 flat surfaces; rear unrecognizable; leather/string mark on side (p. 76; Fig. 4).",
    "L-146": "Two small canes tied with thin string and covered with fine fabric (p. 78; Fig. 7).",
    "L-148": "Flat front, rounded rear as if in small cavity; upper impression of pointed object/wooden peg (p. 77; Fig. 5).",
    "L-149": "Flat rear with vertical plank imprint between plank and orthogonal wooden frame edge; surface deposit (p. 77; Fig. 5).",
    "L-151": "Thin square clay sheet applied on very soft yielding material; no fastening traces (p. 81).",
    "L-154": "Peg-on-wall with stepped contour and flattened vegetal-fibre rope imprint (p. 74; Fig. 3).",
    "L-158": "Well-fashioned edges, square contour locker sealing (p. 77; Fig. 5).",
    "L-161": "Knotted strings on finely treated polished wood surface; fingernail tallies (p. 78-79; Fig. 6).",
    "L-162": "Knotted strings on finely treated polished wood surface; fingernail tallies (p. 78-79; Fig. 6).",
    "L-163": "Strings passing around edge of polished wooden box; fingernail tallies (p. 78-79; Fig. 6).",
    "L-164": "Knotted strings on finely treated polished wood surface; fingernail tallies (p. 78-79).",
    "L-165": "Knotted strings on polished wood surface; no preserved fingernail tallies (p. 78-79; Fig. 6).",
    "L-166": "Knotted strings on finely treated polished wood surface; fingernail tallies (p. 78-79).",
    "L-167": "Strings passing around edge of polished wooden box; fingernail tallies (p. 78-79).",
    "L-168": "Knotted strings on finely treated polished wood surface; fingernail tallies (p. 78-79; Fig. 6).",
    "L-169": "Knotted strings on finely treated polished wood surface; fingernail tallies (p. 78-79).",
    "L-170": "Knotted strings on polished wood surface; no preserved fingernail tallies (p. 78-79).",
    "L-171": "Knotted strings on finely treated polished wood surface (p. 78-79).",
    "L-172": "Knotted strings on finely treated polished wood surface (p. 78-79).",
    "L-173": "Peg-on-wall with round-section vegetal-fibre rope imprint (p. 74; Fig. 3).",
    "L-174": "Carefully modelled around rim of small vessel (~12 cm diameter); no clear cover traces (p. 80; Fig. 7).",
    "L-175": "Peg-on-wall with chaff imprints pressed around hole on rear face (p. 74; Fig. 3).",
    "L-177": "Curved impression of vessel rim (p. 80; Fig. 7).",
    "L-179": "Deep cone-arc recess of polished cylindrical peg (wood/stone) in hole through wooden planks; subtriangular cavity projection (p. 74; Fig. 3).",
    "L-180": "Impressions of thin parallel canes on two sides (p. 78).",
    "L-181": "Vessel shoulder with string imprints fastening cover (p. 80; Fig. 7).",
    "L-187": "Curved impression of vessel rim (p. 80; Fig. 7).",
    "L-188": "Vessel shoulder with string imprints fastening cover (p. 80).",
    "L-189": "Triangular cross-section; rear shows deep vertical parallel stick imprints like L-190; fingerprints on top (p. 75; Fig. 4).",
    "L-190": "T-shaped section pressed between two parallel rough wooden sticks (grating-like structure); rear fingerprints (p. 75; Fig. 4).",
    "L-193": "Rear shows two connected orthogonal pegs or bamboo canes; flat upper face with wooden marks (p. 76; Fig. 5).",
    "L-198": "Heavy concretions; rear shows incident corner elements/angles; possible wooden locker (p. 76; Fig. 5).",
    "L-204": "Rear surfaces bear wicker marks (vessel lid or wicker basket) (p. 81; Fig. 7).",
    "L-206": "Cone-arc shaped section applied onto regular polished cylindrical peg (probably wood); coarse clay obscured wall surface (p. 74; Fig. 3).",
    "L-207": "Massive polygonal clay lump (~6x8x4 cm); angular imprints on rear edges suggesting rectangular cavity (p. 76).",
    "L-208": "Directly moulded around thick rope (~1.5 cm diameter) with lateral fingerprints and no container contact (p. 81; Fig. 7).",
    "L-209": "Small crescent-shaped lump, sub-triangular section with locker-like side fracture (p. 77).",
    "L-211": "Pressed over knotted string tangle on corner of flat polished wooden box (p. 79-80; Fig. 6).",
}

# Prose vs Table 1 impression conflicts documented in prior independent review
PROSE_IMPRESSION_CONFLICTS = {
    "L-174": "Table 1 gives 1 impression; prose p. 80 gives 2 impressions of the same geometric seal.",
    "L-179": "Table 1 gives 1 impression; prose p. 74 gives 2 badly preserved impressions.",
}

# Rao 1985 vs CISI 1 / Frenez & Tosi discrepancies documented during audit
RAO_DISCREPANCIES = {
    "L-161": "Rao 1985 Plate CLXI F conflict: p. 325 assigns Pl. CLXI F to 1830 (L-161), while p. 319 assigns Pl. CLXI F to 1864 (L-164).",
    "L-164": "Rao 1985 Plate CLXI F conflict: p. 319 assigns Pl. CLXI F to 1864 (L-164, jar-stopper), while p. 325 assigns Pl. CLXI F to 1830 (L-161); Frenez & Tosi classify both as wooden_box.",
    "L-206": "Functional interpretation differs while geometry agrees: Rao 1985 p. 321/326 (no. 2077, Pl. CLXII D) describes deep groove from stick/reed on package; Frenez & Tosi p. 74 classify as cylindrical wooden peg-on-wall.",
    "L-126": "Rao 1985 p. 326 (no. 1877, Pl. CLXIII A.1) notes 'reed mark' on reverse; Frenez & Tosi p. 81 classify as pleated leather_sack.",
    "L-125": "Rao 1985 p. 327 (no. 1876, Pl. CLXIII B.4) notes 'plain' reverse; Frenez & Tosi p. 80 identify parallel wood lines and string impressions (wooden_box).",
    "L-128": "Rao 1985 p. 327 (no. 1873, Pl. CLXIII E.2) notes 'hollow reed mark'; Frenez & Tosi Table 1 classify as undiagnostic.",
    "L-190": "Rao 1985 p. 328 (no. 1870, Pl. CLXIV E.2) notes 'deep reed marks'; Frenez & Tosi p. 75 identify two parallel wooden sticks (structure).",
    "L-193": "Rao 1985 p. 322/326 (no. 1888, Pl. CLXII E) notes 'bamboo mat' / 'deep reed-mark'; Frenez & Tosi p. 76 identify orthogonal pegs/bamboo and flat wooden face (structure).",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_part_a(lipi_rows):
    by_fam = defaultdict(list)
    for r in lipi_rows:
        by_fam[r["object_family_id"]].append(r)

    # Corpus uniqueness checks
    h904_900_840 = []
    h904_900_700_840 = []
    for fam, frs in by_fam.items():
        if len(frs) < 2:
            continue
        has_900 = any("900" in (r.get("signs_reading_rtl") or []) for r in frs)
        has_900_700 = any("900" in (r.get("signs_reading_rtl") or []) and "700" in (r.get("signs_reading_rtl") or []) for r in frs)
        has_840 = any("840" in (r.get("signs_reading_rtl") or []) for r in frs)
        if has_900 and has_840:
            h904_900_840.append({
                "family_id": fam,
                "cisi": frs[0].get("source_cisi"),
                "faces": [r.get("signs_reading_rtl") for r in frs],
            })
        if has_900_700 and has_840:
            h904_900_700_840.append(fam)

    m1383_adj = []
    for r in lipi_rows:
        s = r.get("signs_reading_rtl") or []
        for i in range(len(s) - 1):
            if (s[i] == "017" and s[i + 1] == "031") or (s[i] == "031" and s[i + 1] == "017"):
                m1383_adj.append({
                    "family_id": r["object_family_id"],
                    "cisi": r.get("source_cisi"),
                    "site": r.get("site"),
                    "object_type": r.get("object_type"),
                    "signs_reading_rtl": s,
                })
                break

    # Exact algebraic solutions of Fuls's two equations: v = 2S - L and vL + 1 = 7S + 5
    # => (2L - 7)S = L^2 + 4 => d = 2L - 7 divides 65
    exact_solutions = []
    for d in [1, 5, 13, 65]:
        L = (d + 7) // 2
        S = (L * L + 4) // d
        v = 2 * S - L
        exact_solutions.append({
            "L": L,
            "S": S,
            "v": v,
            "m1383_7_plus_L": 7 + L,
            "in_fuls_15_20_range": 15 <= (7 + L) <= 20,
            "in_vidale1990_10_18_range": 10 <= (7 + L) <= 18,
            "satisfies_L_ge_10_digit_max": L >= 10,
        })

    h904_faces = [r for r in lipi_rows if r.get("source_cisi") == "H-904"]
    m1383_faces = [r for r in lipi_rows if r.get("source_cisi") == "M-1383"]
    lipi_3786_faces = [r for r in lipi_rows if r.get("object_family_id") == "3786"]

    cisi2_basic = {}
    with open(CISI2_BASIC_PATH, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("cisi") in ("H-904", "M-1383"):
                cisi2_basic[d["cisi"]] = d

    audit = {
        "audit_date": "2026-11-23",
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "lipi_corpus_sha256": sha256_file(LIPI_PATH),
        "lipi_totals": {"objects": len(by_fam), "faces": len(lipi_rows)},
        "Q_0011_H904_ICIT3786": {
            "verdict": "physical_and_graphic_verified_historical_id_provisional",
            "physical_join_status": "confirmed",
            "graphic_stroke_count_status": "confirmed_both_faces_from_cisi2_plate",
            "historical_icit_3786_join_status": "strongly_supported_unique_in_corpus_but_formally_provisional",
            "cisi_id": "H-904",
            "lipi_family_id": "1786",
            "lipi_family_3786_conflict": {
                "cisi": lipi_3786_faces[0]["source_cisi"],
                "site": lipi_3786_faces[0]["site"],
                "object_type": lipi_3786_faces[0]["object_type"],
                "excavation_idno": lipi_3786_faces[0]["metadata"].get("excavation-idno"),
                "faces": len(lipi_3786_faces),
                "signs_reading_rtl": lipi_3786_faces[0]["signs_reading_rtl"],
                "note": "Current Lipi family 3786 is M-1540, a single-face Mohenjo-daro copper tablet, proving numeric ID renumbering or a leading-digit typo relative to Fuls's 'ICIT 3786'.",
            },
            "primary_witnesses_inspected": {
                "cisi2_plate": {
                    "printed_page": 338,
                    "pdf_page": 373,
                    "caption": "H-904 A, H-904 B (HARAPPA 899-911 TABLETS incised no iconography)",
                    "local_render": f"{RAW_DIR}/cisi2_H904_plate_p373.png",
                    "local_zoom": f"{RAW_DIR}/cisi2_H904_plate_zoom.png",
                    "lipi_crops": ["data/lipi/public/seal_images/H-904_A.jpg", "data/lipi/public/seal_images/H-904_B.jpg"],
                },
                "cisi2_basic_data": {
                    "printed_page": 444,
                    "pdf_page": 479,
                    "local_zoom": f"{RAW_DIR}/cisi2_H904_basic_zoom.png",
                    "visual_reading": {
                        "col1_cisi": "H-904",
                        "col2_fc": "3477 (= 3000 + Vats 477)",
                        "col3_excavation": "J 213 [D/rect]",
                        "col4_museum": "HM 434, 52.10xx",
                        "col5_photographs": "P 1214",
                    },
                    "prior_automated_jsonl": {
                        "col2_fc": cisi2_basic["H-904"]["col2_fc"],
                        "col3_excavation": cisi2_basic["H-904"]["col3_excavation"],
                        "col4_museum": cisi2_basic["H-904"]["col4_museum"],
                        "col5_photographs": cisi2_basic["H-904"]["col5_photographs"],
                    },
                },
                "vats_1940": {
                    "text_table": "printed p. 349 / PDF p. 378, no. 477, find J213, Mound D, white steatite, type h, depth 2 ft 0 in, 0.65 x 0.28 in (= 16.5 x 7.1 mm)",
                    "plate": "Plate XCVI no. 477 / PDF p. 200; retained crop research/literature/metrology/primary_numeric/vats_h904/477_crop12x.png",
                },
            },
            "graphic_verification": {
                "face_A_cisi2_visual_ltr": ["740", "032", "840", "002"],
                "face_A_reading_rtl": h904_faces[0]["signs_reading_rtl"],
                "face_A_verified_strokes": {"long_strokes_W032": 2, "short_strokes_W002": 2},
                "face_B_cisi2_visual_ltr": ["700", "033", "900", "645", "368", "817"],
                "face_B_reading_rtl": h904_faces[1]["signs_reading_rtl"],
                "face_B_verified_strokes": {"long_strokes_W033": 3, "crescent_W900": 1},
                "resolution_of_fuls_W032_conflict": (
                    "CISI 2 photographs resolve both faces sharply. Face B clearly has three full-height long strokes (W033) "
                    "beside W700 and W900, while Face A clearly has two full-height long strokes (W032) and two shorter strokes (W002) "
                    "flanking W840. Fuls's prose coefficient '3' on the W700/W900 face is graphically confirmed on H-904 B; his prose "
                    "label 'W032' for those three long strokes is a typographical slip for W033."
                ),
                "extra_unmodelled_signs": {
                    "face_A": ["740"],
                    "face_B": ["817", "368", "645"],
                },
            },
            "corpus_uniqueness": {
                "objects_with_900_and_840_on_opposite_faces": len(h904_900_840),
                "objects_with_900_700_and_840_on_opposite_faces": len(h904_900_700_840),
                "matched_families": h904_900_840,
            },
            "missing_witness_to_close_historical_id": "Fuls (2020/2023) Figure 16 pixels or authenticated ICIT database crosswalk (HTTP 401).",
            "implication_for_F0006": (
                "Confirms that the physical stroke counts (3 long on B; 2 long and 2 short on A) exist on a real two-face white steatite "
                "tablet from Harappa (H-904), eliminating the two-stroke sensitivity branch for H-904. Does NOT establish Fuls's semantic "
                "equation 3L + v = 2L + 2S: four additional signs (740 on A; 817-368-645 on B) are omitted from the equation, and no "
                "archaeological evidence demonstrates equal quantities or commensurate units across the two faces."
            ),
        },
        "Q_0012_M1383_Bangle_Anchor": {
            "verdict": "physical_saggar_sealing_confirmed_bangle_count_unverified_and_insufficient",
            "physical_support_join_status": "confirmed_from_cisi2_plate_p182",
            "bangle_count_status": "unverified_in_all_held_primary_sources",
            "cisi_id": "M-1383",
            "lipi_family_id": "3679",
            "primary_witnesses_inspected": {
                "cisi2_plate": {
                    "printed_page": 182,
                    "pdf_page": 217,
                    "heading": "182 MOHENJO-DARO 1382-1383 SEAL IMPRESSIONS on pots, on tags",
                    "panels": [
                        "M-1383 A (1) (15%): full closed cylindrical stoneware-bangle firing container (saggar) with clay sealing at mouth",
                        "M-1383 A (2): close-up of unicorn-and-standard seal impression on mouth clay sealing",
                        "M-1383 B: broken mouth/lid section of the ceramic container",
                    ],
                    "local_render": f"{RAW_DIR}/cisi2_M1383_plate_p217.png",
                    "lipi_crops": ["data/lipi/public/seal_images/M-1383_A_2_.jpg", "data/lipi/public/seal_images/M-1383_B.jpg"],
                },
                "cisi2_basic_data": {
                    "printed_page": 439,
                    "pdf_page": 474,
                    "local_zoom": f"{RAW_DIR}/cisi2_M1383_basic_zoom.png",
                    "visual_reading": {
                        "col1_cisi": "M-1383",
                        "col2_fc": "0762",
                        "col3_excavation": "MN 82a (Moneer area, 1982 IsMEO/RWTH Aachen fieldwork)",
                        "col4_museum": "EXB (Excavation Branch, Karachi)",
                        "col5_photographs": "Aachen; A (1): VSI, p. 272, C 77 (Vergessene Stadte am Indus 1987)",
                    },
                },
                "lipi_record": {
                    "object_type": m1383_faces[0]["object_type"],
                    "material": m1383_faces[0]["metadata"].get("material"),
                    "symbol": m1383_faces[0]["symbol"],
                    "excavation_idno": m1383_faces[0]["metadata"].get("excavation-idno"),
                    "signs_visual_ltr": m1383_faces[0]["signs_visual_ltr"],
                    "signs_reading_rtl": m1383_faces[0]["signs_reading_rtl"],
                },
                "vidale_1987_interim2": {
                    "source": "Vidale 1987, 'More Evidence on a Protohistoric Ceramic Puzzle', Interim Reports Vol. 2, pp. 105-111",
                    "finding": "Describes a fused 1984/1985 DK-B,C kiln-slag block (2 bangles directly observed in 1 inner bowl; conjectural 5 bowls x 2 = 10 bangles, plus 7-bowl anomaly). No mention of M-1383, MN 82a, 82 fragments, or 15-20 bangles.",
                },
                "vidale_1990_ceramics_civilization": {
                    "source": "Vidale 1990, 'Stoneware Industry of the Indus Civilization', Ceramics and Civilization Vol. V, PDF pp. 9-10, Fig. 7",
                    "finding": "Reconstructs outer stoneware saggars containing 5-6 inner sub-cylindrical saggars each holding 2-3 bangles (= 10-18 bangles per outer saggar), sealed around the mouth with three oval unicorn-stamped clay sealings before firing. No mention of 82 fragments or a 15-20 count for MN 82a / M-1383.",
                },
                "mackay_1938_vol1": {
                    "finding": "Zero references to MN 82a or stoneware bangle saggars (MN 82a was recovered in 1982, 44 years after Mackay 1938).",
                },
            },
            "metadata_conflict_resolution": (
                "CISI 2 plate p. 182 completely resolves the prior Lipi 'TAG:R (clay tag)' vs. 'bangle firing pot' conflict: "
                "M-1383 A (1) at 15% scale physically depicts the closed cylindrical ceramic saggar, and M-1383 A (2) depicts the "
                "unicorn clay sealing applied directly onto its luted mouth. Lipi's 'TAG:R' classifies the impressed clay sealing on "
                "the saggar mouth. Visual inspection of M-1383 A (2) also confirms clear 740-575-017-031 on the intact left side and "
                "a diagonal crack/erosion across the first three reading-order signs (920-060-741) on the right."
            ),
            "corpus_uniqueness": {
                "faces_with_adjacent_017_031": len(m1383_adj),
                "matched_faces": m1383_adj,
            },
            "algebraic_sensitivity": {
                "exact_solutions_of_fuls_equations": exact_solutions,
                "count_surviving_fuls_15_20_range": sum(1 for x in exact_solutions if x["in_fuls_15_20_range"]),
                "count_surviving_vidale1990_10_18_range": sum(1 for x in exact_solutions if x["in_vidale1990_10_18_range"]),
                "critical_note": (
                    "Under Fuls's unverified 15-20 bangle bound (8 <= L <= 13), only (L, S, v) = (10, 8, 6) survives. "
                    "Under Vidale (1990)'s published technological range of 10-18 bangles per outer saggar (3 <= L <= 11), "
                    "THREE of the four exact solutions survive: (4, 20, 36) giving 11, (6, 8, 10) giving 13, and (10, 8, 6) giving 17."
                ),
            },
            "missing_witnesses_to_verify_count": [
                "Halim & Vidale 1984, 'Kilns, Bangles and Coated Vessels', Interim Reports Vol. 1, Aachen, pp. 63-97",
                "Vergessene Stadte am Indus (Mainz 1987), p. 272, catalogue item C 77",
                "Wells 2015, The Archaeology and Epigraphy of Indus Writing, pp. 94-95 (only preface sample held locally)",
            ],
            "implication_for_F0006": (
                "Even though M-1383 is confirmed to be a stoneware-bangle saggar sealing, the 82-fragment / 15-20 bangle count remains "
                "unverified in all held primary sources, Vidale's published saggar capacity (10-18) fails to isolate L=10 uniquely, "
                "and Vidale (1990) reports three oval impressions of a standard unicorn stamp seal per saggar mouth—undermining the "
                "premise that a reusable unicorn stamp seal's text encodes the exact bangle count of one firing batch."
            ),
        },
    }

    out_path = os.path.join(OUT_DIR, "anchors-audit-v1.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")
    return audit


def build_lothal_attachments():
    # Load Frenez & Tosi Table 1 (no signs!)
    table_rows = []
    with open(LOTHAL_TABLE_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            table_rows.append(r)
    assert len(table_rows) == 93, f"Expected 93 rows, got {len(table_rows)}"

    # Load CISI 1 basic data for L-124..L-216 (excavation/museum/photo only — no signs!)
    cisi1_basic = {}
    with open(CISI1_BASIC_PATH, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            c = d.get("cisi", "")
            if c.startswith("L-"):
                cisi1_basic[c] = d

    # Load figure presence from selected-trace-observations.json
    st = json.load(open(SELECTED_TRACE_PATH, encoding="utf-8"))
    fig_map = {}
    for finfo in st["figure_inventory"]:
        for oid in finfo["labelled_object_ids"]:
            fig_map[oid] = f"Fig.{finfo['figure']} (p.{finfo['printed_page']})"

    out_rows = []
    for r in table_rows:
        oid = r["object_id"]
        ptype = r["physical_type"]
        ccode = r["context_code"]
        rev6 = REVERSE_CLASS_6_MAP[ptype]
        diag5 = "" if rev6 == "unidentifiable_other" else rev6
        is_wood = "" if diag5 == "" else ("1" if rev6 == "wood_plank_peg" else "0")
        mob = MOBILITY_MAP[ptype]
        cb = cisi1_basic.get(oid, {})

        out_rows.append({
            "cisi_id": oid,
            "cisi1_fc": cb.get("col2_fc", ""),
            "excavation_no": cb.get("col3_excavation", ""),
            "museum_no": cb.get("col4_museum", ""),
            "impressions_table": int(r["impressions"]),
            "impressions_prose_conflict": PROSE_IMPRESSION_CONFLICTS.get(oid, ""),
            "frenez_physical_type": ptype,
            "reverse_class_6": rev6,
            "diagnostic_class_5": diag5,
            "is_wood_plank_peg": is_wood,
            "mobility_class": mob,
            "context_code": ccode,
            "context_basis": CONTEXT_BASIS_MAP[ccode],
            "frenez_table_printed_page": int(r["printed_page"]),
            "frenez_figure": fig_map.get(oid, ""),
            "prose_reverse_evidence": FRENEZ_PROSE_REVERSE.get(oid, ""),
            "rao_discrepancy_flag": RAO_DISCREPANCIES.get(oid, ""),
        })

    out_csv = os.path.join(OUT_DIR, "lothal-attachments-v1.csv")
    fieldnames = list(out_rows[0].keys())
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {out_csv} ({len(out_rows)} rows)")
    return out_rows


def weighted_nmi_and_cramers_v(x_vals, y_vals, weights):
    """Compute weighted Normalized Mutual Information (geometric mean) and bias-corrected Cramer's V."""
    total_w = float(sum(weights))
    if total_w <= 0:
        return 0.0, 0.0
    joint = defaultdict(float)
    px = defaultdict(float)
    py = defaultdict(float)
    for x, y, w in zip(x_vals, y_vals, weights):
        joint[(x, y)] += w
        px[x] += w
        py[y] += w

    if len(px) < 2 or len(py) < 2:
        return 0.0, 0.0

    mi = 0.0
    chi2 = 0.0
    for (x, y), wxy in joint.items():
        if wxy > 0:
            p_xy = wxy / total_w
            p_x = px[x] / total_w
            p_y = py[y] / total_w
            mi += p_xy * math.log(p_xy / (p_x * p_y))
    for x, wx in px.items():
        for y, wy in py.items():
            exp = wx * wy / total_w
            obs = joint.get((x, y), 0.0)
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    hx = -sum((wx / total_w) * math.log(wx / total_w) for wx in px.values() if wx > 0)
    hy = -sum((wy / total_w) * math.log(wy / total_w) for wy in py.values() if wy > 0)
    nmi = mi / math.sqrt(hx * hy) if (hx > 0 and hy > 0) else 0.0

    r, k = len(px), len(py)
    phi2 = chi2 / total_w
    # Standard Cramer's V (non-negative)
    denom = min(r - 1, k - 1)
    cramers_v = math.sqrt(phi2 / denom) if denom > 0 else 0.0
    return nmi, cramers_v


def weighted_spearman_abs(x_num, y_bin, weights):
    """Weighted Pearson correlation on rank-transformed x_num and binary y_bin (equals |Spearman rho| for unit weights)."""
    n = len(x_num)
    if n < 3 or len(set(x_num)) < 2 or len(set(y_bin)) < 2:
        return 0.0
    # Compute average ranks for x_num
    order = sorted(range(n), key=lambda i: x_num[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and x_num[order[j + 1]] == x_num[order[i]]:
            j += 1
        avg_r = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_r
        i = j + 1
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    rx = np.asarray(ranks, dtype=float)
    ry = np.asarray(y_bin, dtype=float)
    mx = np.sum(w * rx)
    my = np.sum(w * ry)
    vx = np.sum(w * (rx - mx) ** 2)
    vy = np.sum(w * (ry - my) ** 2)
    if vx <= 0 or vy <= 0:
        return 0.0
    cov = np.sum(w * (rx - mx) * (ry - my))
    return float(abs(cov / math.sqrt(vx * vy)))


def extract_features_and_components(attach_rows, lipi_rows):
    # Group Lipi faces by CISI id
    by_cisi = defaultdict(list)
    for r in lipi_rows:
        c = r.get("source_cisi")
        if c:
            by_cisi[c].append(r)

    joined_objects = []
    total_joined_faces = 0
    for ar in attach_rows:
        cid = ar["cisi_id"]
        faces = by_cisi.get(cid, [])
        if not faces:
            continue
        total_joined_faces += len(faces)

        # Eligible complete faces (same rule as prior graphic-coverage: clean_rtl_singleline and length >= 3)
        elig_faces = [f for f in faces if f.get("clean_rtl_singleline") and f.get("length", 0) >= 3]
        # Primary face for Population B: prefer longest complete clean face, else longest face with >= 1 non-000 sign
        def legible_signs(f):
            return [s for s in (f.get("signs_reading_rtl") or []) if s != "000"]

        if elig_faces:
            primary_face = sorted(elig_faces, key=lambda f: (-len(f["signs_reading_rtl"]), f["record_id"]))[0]
            is_pop_a = True
        else:
            leg_faces = [f for f in faces if len(legible_signs(f)) >= 1]
            if not leg_faces:
                continue
            primary_face = sorted(leg_faces, key=lambda f: (-len(legible_signs(f)), f["record_id"]))[0]
            is_pop_a = False

        raw_signs = primary_face.get("signs_reading_rtl") or []
        leg_signs = [s for s in raw_signs if s != "000"]
        closing_sign = raw_signs[-1] if (raw_signs and raw_signs[-1] != "000") else (leg_signs[-1] if leg_signs else "NONE")
        has_stroke = int(any(s in STROKE_NUMERAL_CODES for s in leg_signs))
        sym = primary_face.get("symbol", "-") or "-"
        if sym in ("-", "None", ""):
            motif = "None_or_dash"
        elif sym in ("Bull1", "Elep"):
            motif = sym
        else:
            motif = "Other"

        joined_objects.append({
            "cisi_id": cid,
            "n_faces_in_lipi": len(faces),
            "primary_record_id": primary_face["record_id"],
            "is_pop_a_complete": is_pop_a,
            "is_complete_face": int(bool(primary_face.get("complete_observed"))),
            "signs_reading_rtl": raw_signs,
            "legible_signs": leg_signs,
            "text_length": len(leg_signs),
            "closing_sign": closing_sign,
            "has_stroke_numeral": has_stroke,
            "animal_motif": motif,
            "raw_symbol": sym,
            "exact_string_key": "-".join(raw_signs) if is_pop_a else None,
            "frenez_physical_type": ar["frenez_physical_type"],
            "reverse_class_6": ar["reverse_class_6"],
            "diagnostic_class_5": ar["diagnostic_class_5"],
            "is_wood_plank_peg": int(ar["is_wood_plank_peg"]) if ar["is_wood_plank_peg"] != "" else None,
            "mobility_class": ar["mobility_class"] or None,
            "context_code": ar["context_code"],
            "context_basis": ar["context_basis"],
            "rao_discrepancy_flag": ar["rao_discrepancy_flag"],
        })

    # Build strict die/text components (Union-Find)
    parent_strict = {o["cisi_id"]: o["cisi_id"] for o in joined_objects}

    def find(p, x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(p, a, b):
        ra, rb = find(p, a), find(p, b)
        if ra != rb:
            if ra < rb:
                p[rb] = ra
            else:
                p[ra] = rb

    # Rule (a): identical complete clean reading-order sign sequence
    by_exact = defaultdict(list)
    for o in joined_objects:
        if o["exact_string_key"]:
            by_exact[o["exact_string_key"]].append(o["cisi_id"])
    for ids in by_exact.values():
        for i in range(1, len(ids)):
            union(parent_strict, ids[0], ids[i])

    # Rule (b): Frenez & Tosi (2005) explicit same-seal cohorts:
    # - Elephant cohort L-161..L-172 (p. 78)
    # - Most repeated unicorn seal (p. 84): L-124, L-125, L-126, L-189, L-190, L-193, L-195, L-197, L-198, L-206
    #   (L-124..L-129, L-190, L-191, L-193, L-197, L-206 are already G01 by exact string; L-189, L-195, L-198 join G01!)
    # - Also check exact identical strings among non-Pop-A legible faces of length >= 3
    explicit_cohorts = [
        [f"L-{i}" for i in range(161, 173)],
        ["L-124", "L-125", "L-126", "L-189", "L-190", "L-193", "L-195", "L-197", "L-198", "L-206"],
    ]
    present_ids = set(parent_strict.keys())
    for cohort in explicit_cohorts:
        members = [c for c in cohort if c in present_ids]
        for i in range(1, len(members)):
            union(parent_strict, members[0], members[i])

    # Also merge exact identical legible strings of length >= 3 across Population B
    by_leg3 = defaultdict(list)
    for o in joined_objects:
        if len(o["legible_signs"]) >= 3:
            by_leg3["-".join(o["legible_signs"])].append(o["cisi_id"])
    for ids in by_leg3.values():
        for i in range(1, len(ids)):
            union(parent_strict, ids[0], ids[i])

    # Conservative substring component partition
    parent_sub = dict(parent_strict)
    complete_objs = [o for o in joined_objects if o["is_pop_a_complete"]]
    for o in joined_objects:
        if o["is_pop_a_complete"]:
            continue
        sub = o["legible_signs"]
        if len(sub) < 3:
            continue
        sub_str = "-".join(sub)
        for co in complete_objs:
            full_str = "-".join(co["legible_signs"])
            if sub_str in full_str:
                # Motif compatibility: either same or one is None_or_dash
                m1, m2 = o["animal_motif"], co["animal_motif"]
                if m1 == m2 or m1 == "None_or_dash" or m2 == "None_or_dash":
                    union(parent_sub, co["cisi_id"], o["cisi_id"])

    for o in joined_objects:
        o["die_component_strict"] = find(parent_strict, o["cisi_id"])
        o["die_component_substring"] = find(parent_sub, o["cisi_id"])

    return joined_objects, total_joined_faces


def build_feature_matrix(train_objs, test_objs):
    """Build fold-safe numeric feature matrices without leaking closing_sign or frequent_signs from test."""
    # Closing signs occurring in >= 2 distinct components in train
    comp_closers = defaultdict(set)
    comp_signs = defaultdict(set)
    for o in train_objs:
        comp = o["_comp"]
        comp_closers[o["closing_sign"]].add(comp)
        for s in o["legible_signs"]:
            comp_signs[s].add(comp)
    kept_closers = sorted([k for k, cs in comp_closers.items() if len(cs) >= 2])
    kept_signs = sorted([s for s, cs in comp_signs.items() if len(cs) >= 3])
    motifs = ["Bull1", "Elep", "None_or_dash", "Other"]

    def featurize(objs):
        X = []
        for o in objs:
            row = [
                float(o["text_length"]),
                float(o["has_stroke_numeral"]),
                float(o["is_complete_face"]),
            ]
            # closing sign one-hot + OTHER
            c_hit = False
            for kc in kept_closers:
                v = 1.0 if o["closing_sign"] == kc else 0.0
                if v > 0:
                    c_hit = True
                row.append(v)
            row.append(0.0 if c_hit else 1.0)
            # animal motif one-hot
            for m in motifs:
                row.append(1.0 if o["animal_motif"] == m else 0.0)
            # frequent signs
            sset = set(o["legible_signs"])
            for ks in kept_signs:
                row.append(1.0 if ks in sset else 0.0)
            X.append(row)
        return np.asarray(X, dtype=float)

    return featurize(train_objs), featurize(test_objs)


def nb_predict_proba_and_label(train_objs, test_objs, target_key, comp_weights=True):
    """Smoothed categorical+binned Naive Bayes (alpha=1.0), fold-safe and ultra-fast for 10,000 permutations."""
    classes = sorted({o[target_key] for o in train_objs})
    if len(classes) == 1:
        return [classes[0]] * len(test_objs)

    # Fold-safe vocabularies
    comp_closers = defaultdict(set)
    comp_signs = defaultdict(set)
    for o in train_objs:
        comp = o["_comp"]
        comp_closers[o["closing_sign"]].add(comp)
        for s in o["legible_signs"]:
            comp_signs[s].add(comp)
    kept_closers = {k for k, cs in comp_closers.items() if len(cs) >= 2}
    kept_signs = sorted([s for s, cs in comp_signs.items() if len(cs) >= 3])

    def discretize(o):
        lb = "short_1_3" if o["text_length"] <= 3 else ("med_4_5" if o["text_length"] <= 5 else "long_6p")
        cl = o["closing_sign"] if o["closing_sign"] in kept_closers else "OTHER"
        feats = [
            ("len", lb),
            ("stroke", str(o["has_stroke_numeral"])),
            ("comp", str(o["is_complete_face"])),
            ("closer", cl),
            ("motif", o["animal_motif"]),
        ]
        sset = set(o["legible_signs"])
        for ks in kept_signs:
            feats.append((f"s_{ks}", "1" if ks in sset else "0"))
        return feats

    # Compute sample weights (component-equal so G01/G02 don't drown out singletons)
    comp_sizes = Counter(o["_comp"] for o in train_objs)
    w_train = [1.0 / comp_sizes[o["_comp"]] if comp_weights else 1.0 for o in train_objs]

    class_w = defaultdict(float)
    feat_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    feat_vals = defaultdict(set)
    for o, w in zip(train_objs, w_train):
        y = o[target_key]
        class_w[y] += w
        for fname, fval in discretize(o):
            feat_counts[fname][y][fval] += w
            feat_vals[fname].add(fval)

    total_w = sum(class_w.values())
    alpha = 1.0
    preds = []
    for o in test_objs:
        best_c = None
        best_lp = -1e18
        feats = discretize(o)
        for c in classes:
            lp = math.log((class_w[c] + alpha) / (total_w + alpha * len(classes)))
            for fname, fval in feats:
                k_vals = max(2, len(feat_vals[fname]))
                cnt = feat_counts[fname][c].get(fval, 0.0)
                lp += math.log((cnt + alpha) / (class_w[c] + alpha * k_vals))
            if lp > best_lp:
                best_lp = lp
                best_c = c
        preds.append(best_c)
    return preds


def fast_metrics(y_true, y_pred, weights, labels):
    """Exact balanced accuracy, accuracy, and macro-F1 matching sklearn (without sklearn validation overhead)."""
    tp = {c: 0.0 for c in labels}
    fp = {c: 0.0 for c in labels}
    fn = {c: 0.0 for c in labels}
    tot_c = {c: 0.0 for c in labels}
    corr_w = 0.0
    tot_w = 0.0
    for yt, yp, w in zip(y_true, y_pred, weights):
        tot_w += w
        tot_c[yt] += w
        if yt == yp:
            corr_w += w
            tp[yt] += w
        else:
            fn[yt] += w
            if yp in fp:
                fp[yp] += w
    acc = corr_w / tot_w if tot_w > 0 else 0.0
    recalls = [tp[c] / tot_c[c] for c in labels if tot_c[c] > 0]
    bal_acc = sum(recalls) / len(recalls) if recalls else 0.0
    f1s = []
    for c in labels:
        denom = 2.0 * tp[c] + fp[c] + fn[c]
        f1s.append((2.0 * tp[c] / denom) if denom > 0 else 0.0)
    macro_f1 = sum(f1s) / len(labels) if labels else 0.0
    return bal_acc, acc, macro_f1


def eval_loco_cv_fast_nb(work, comp_key, target_key, labels):
    """
    Exact O(K) Leave-One-Component-Out smoothed Naive Bayes (alpha=1.0),
    maintaining fold-safe closing_sign (>=2 train comps) and frequent_signs (>=3 train comps).
    Mathematically identical to refitting NB from scratch per fold.
    """
    # Group specimens by component
    by_comp = defaultdict(list)
    for o in work:
        by_comp[o[comp_key]].append(o)
    comps = sorted(by_comp.keys())

    # Precompute per-component target weight vector (sums to 1.0 per component)
    comp_yw = {}
    total_yw = defaultdict(float)
    for c in comps:
        ms = by_comp[c]
        w = 1.0 / len(ms)
        yw = defaultdict(float)
        for o in ms:
            yw[o[target_key]] += w
            total_yw[o[target_key]] += w
        comp_yw[c] = yw

    # Precompute per-component specimen feature bundles & global component frequencies
    # Note: inside a component, specimens may rarely differ in motif/completeness in Pop B;
    # we handle exact specimen-level weights within each component!
    closer_comps = defaultdict(set)
    sign_comps = defaultdict(set)
    comp_spec_feats = {}
    for c in comps:
        ms = by_comp[c]
        w = 1.0 / len(ms)
        slist = []
        for o in ms:
            closer_comps[o["closing_sign"]].add(c)
            sset = frozenset(o["legible_signs"])
            for s in sset:
                sign_comps[s].add(c)
            lb = "short_1_3" if o["text_length"] <= 3 else ("med_4_5" if o["text_length"] <= 5 else "long_6p")
            slist.append((o[target_key], w, lb, str(o["has_stroke_numeral"]), str(o["is_complete_face"]), o["closing_sign"], o["animal_motif"], sset))
        comp_spec_feats[c] = slist

    # Candidate signs appearing in >= 3 comps globally (only these can ever appear in >= 3 train comps)
    cand_signs = sorted([s for s, cs in sign_comps.items() if len(cs) >= 3])
    cand_closers = {k for k, cs in closer_comps.items() if len(cs) >= 2}

    # Global sufficient statistics for fixed features and candidate signs/closers
    g_len = defaultdict(lambda: defaultdict(float))
    g_str = defaultdict(lambda: defaultdict(float))
    g_cmp = defaultdict(lambda: defaultdict(float))
    g_mot = defaultdict(lambda: defaultdict(float))
    g_cl = defaultdict(lambda: defaultdict(float))
    g_sgn1 = defaultdict(lambda: defaultdict(float))

    c_len = {}
    c_str = {}
    c_cmp = {}
    c_mot = {}
    c_cl = {}
    c_sgn1 = {}

    for c in comps:
        d_len = defaultdict(lambda: defaultdict(float))
        d_str = defaultdict(lambda: defaultdict(float))
        d_cmp = defaultdict(lambda: defaultdict(float))
        d_mot = defaultdict(lambda: defaultdict(float))
        d_cl = defaultdict(lambda: defaultdict(float))
        d_sgn1 = defaultdict(lambda: defaultdict(float))
        for y, w, lb, st, cp, cl, mo, sset in comp_spec_feats[c]:
            d_len[y][lb] += w; g_len[y][lb] += w
            d_str[y][st] += w; g_str[y][st] += w
            d_cmp[y][cp] += w; g_cmp[y][cp] += w
            d_mot[y][mo] += w; g_mot[y][mo] += w
            d_cl[y][cl] += w; g_cl[y][cl] += w
            for s in cand_signs:
                if s in sset:
                    d_sgn1[s][y] += w; g_sgn1[s][y] += w
        c_len[c] = d_len; c_str[c] = d_str; c_cmp[c] = d_cmp
        c_mot[c] = d_mot; c_cl[c] = d_cl; c_sgn1[c] = d_sgn1

    y_true = []
    y_pred = []
    sample_comp_w = []
    alpha = 1.0

    for held in comps:
        # Train class weights
        tr_yw = {y: total_yw[y] - comp_yw[held].get(y, 0.0) for y in labels}
        active_classes = [y for y in labels if tr_yw[y] > 1e-12]
        tr_tot = sum(tr_yw[y] for y in active_classes)
        # Fold-safe vocabularies (exact!)
        kept_closers = {k for k in cand_closers if (len(closer_comps[k]) - (1 if held in closer_comps[k] else 0)) >= 2}
        kept_signs = [s for s in cand_signs if (len(sign_comps[s]) - (1 if held in sign_comps[s] else 0)) >= 3]

        # Count distinct observed values per feature in train
        def count_vals(g_d, c_d):
            vs = set()
            for y in active_classes:
                for val, totv in g_d[y].items():
                    if totv - c_d[y].get(val, 0.0) > 1e-12:
                        vs.add(val)
            return max(2, len(vs))

        k_len = count_vals(g_len, c_len[held])
        k_str = count_vals(g_str, c_str[held])
        k_cmp = count_vals(g_cmp, c_cmp[held])
        k_mot = count_vals(g_mot, c_mot[held])
        # For closer, count distinct mapped values in train
        cl_vals_tr = set()
        for y in active_classes:
            for cl, totv in g_cl[y].items():
                if totv - c_cl[held][y].get(cl, 0.0) > 1e-12:
                    cl_vals_tr.add(cl if cl in kept_closers else "OTHER")
        k_cl = max(2, len(cl_vals_tr))

        # Precompute OTHER closer count per class in train
        other_cl_tr = {}
        for y in active_classes:
            s_kept = sum(g_cl[y].get(kc, 0.0) - c_cl[held][y].get(kc, 0.0) for kc in kept_closers)
            other_cl_tr[y] = max(0.0, tr_yw[y] - s_kept)

        for y_obs, w_obs, lb, st, cp, cl, mo, sset in comp_spec_feats[held]:
            cl_m = cl if cl in kept_closers else "OTHER"
            best_c = active_classes[0]
            best_lp = -1e18
            for y in active_classes:
                cw = tr_yw[y]
                lp = math.log((cw + alpha) / (tr_tot + alpha * len(active_classes)))
                lp += math.log((max(0.0, g_len[y].get(lb, 0.0) - c_len[held][y].get(lb, 0.0)) + alpha) / (cw + alpha * k_len))
                lp += math.log((max(0.0, g_str[y].get(st, 0.0) - c_str[held][y].get(st, 0.0)) + alpha) / (cw + alpha * k_str))
                lp += math.log((max(0.0, g_cmp[y].get(cp, 0.0) - c_cmp[held][y].get(cp, 0.0)) + alpha) / (cw + alpha * k_cmp))
                lp += math.log((max(0.0, g_mot[y].get(mo, 0.0) - c_mot[held][y].get(mo, 0.0)) + alpha) / (cw + alpha * k_mot))
                if cl_m == "OTHER":
                    cl_cnt = other_cl_tr[y]
                else:
                    cl_cnt = max(0.0, g_cl[y].get(cl_m, 0.0) - c_cl[held][y].get(cl_m, 0.0))
                lp += math.log((cl_cnt + alpha) / (cw + alpha * k_cl))
                for s in kept_signs:
                    cnt1 = max(0.0, g_sgn1[s][y] - c_sgn1[held][s].get(y, 0.0))
                    cnt = cnt1 if (s in sset) else max(0.0, cw - cnt1)
                    lp += math.log((cnt + alpha) / (cw + alpha * 2.0))
                if lp > best_lp:
                    best_lp = lp
                    best_c = y
            y_true.append(y_obs)
            y_pred.append(best_c)
            sample_comp_w.append(w_obs)

    cb, ca, cf = fast_metrics(y_true, y_pred, sample_comp_w, labels)
    sb, sa, sf = fast_metrics(y_true, y_pred, [1.0] * len(y_true), labels)
    return {
        "component_weighted_balanced_accuracy": cb,
        "component_weighted_accuracy": ca,
        "component_weighted_macro_f1": cf,
        "specimen_weighted_balanced_accuracy": sb,
        "specimen_weighted_accuracy": sa,
        "specimen_weighted_macro_f1": sf,
    }


def eval_loco_cv(objs, comp_key, target_key, model="nb"):
    """Leave-One-Component-Out CV returning component-weighted & specimen-weighted balanced acc, acc, macro-F1."""
    work = [dict(o, _comp=o[comp_key]) for o in objs if o[target_key] is not None and o[target_key] != ""]
    comps = sorted({o["_comp"] for o in work})
    labels = sorted({o[target_key] for o in work})
    y_true = []
    y_pred = []
    y_maj = []
    y_comp_prior = []
    sample_comp_weights = []

    comp_sizes = Counter(o["_comp"] for o in work)
    for held in comps:
        train = [o for o in work if o["_comp"] != held]
        test = [o for o in work if o["_comp"] == held]
        assert all(o["_comp"] != held for o in train)

        maj_label = Counter(o[target_key] for o in train).most_common(1)[0][0]
        c_w_counts = defaultdict(float)
        tr_csizes = Counter(o["_comp"] for o in train)
        for o in train:
            c_w_counts[o[target_key]] += 1.0 / tr_csizes[o["_comp"]]
        comp_prior_label = max(sorted(c_w_counts.keys()), key=lambda k: c_w_counts[k])

        if model == "nb":
            preds = nb_predict_proba_and_label(train, test, target_key, comp_weights=True)
        elif model == "logreg":
            X_tr, X_te = build_feature_matrix(train, test)
            y_tr = [o[target_key] for o in train]
            tr_w = np.array([1.0 / tr_csizes[o["_comp"]] for o in train], dtype=float)
            if len(set(y_tr)) < 2:
                preds = [y_tr[0]] * len(test)
            else:
                clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=300, random_state=SEED)
                clf.fit(X_tr, y_tr, sample_weight=tr_w)
                preds = list(clf.predict(X_te))
        else:
            raise ValueError(model)

        for o, p in zip(test, preds):
            y_true.append(o[target_key])
            y_pred.append(p)
            y_maj.append(maj_label)
            y_comp_prior.append(comp_prior_label)
            sample_comp_weights.append(1.0 / comp_sizes[o["_comp"]])

    cb, ca, cf = fast_metrics(y_true, y_pred, sample_comp_weights, labels)
    sb, sa, sf = fast_metrics(y_true, y_pred, [1.0] * len(y_true), labels)
    mb, ma, _ = fast_metrics(y_true, y_maj, sample_comp_weights, labels)
    _, msa, _ = fast_metrics(y_true, y_maj, [1.0] * len(y_true), labels)
    pb, pa, _ = fast_metrics(y_true, y_comp_prior, sample_comp_weights, labels)

    return {
        "n_specimens": len(work),
        "n_components": len(comps),
        "n_classes": len(labels),
        "classes": labels,
        "component_weighted_balanced_accuracy": float(cb),
        "component_weighted_accuracy": float(ca),
        "component_weighted_macro_f1": float(cf),
        "specimen_weighted_balanced_accuracy": float(sb),
        "specimen_weighted_accuracy": float(sa),
        "specimen_weighted_macro_f1": float(sf),
        "baseline_majority_specimen_accuracy": float(msa),
        "baseline_majority_component_balanced_accuracy": float(mb),
        "baseline_comp_prior_component_balanced_accuracy": float(pb),
        "baseline_comp_prior_component_accuracy": float(pa),
    }


def permute_component_features(objs, comp_key, rng, strata_key=None):
    """
    Permute inscription feature bundles across components (preserving each component's
    internal physical attachment labels and specimen multiplicity intact).
    If strata_key is provided, permute only within strata of components (using modal stratum per component).
    """
    feat_fields = [
        "text_length", "closing_sign", "has_stroke_numeral",
        "animal_motif", "legible_signs", "is_complete_face"
    ]
    by_comp = defaultdict(list)
    for idx, o in enumerate(objs):
        by_comp[o[comp_key]].append(idx)

    comps = sorted(by_comp.keys())
    # Representative feature bundle for each component: list of feature dicts for its specimens;
    # when assigned to another component of potentially different size, use component's primary/modal feature bundle
    # (for strict components, all Pop-A specimens in a component share identical text; for Pop-B, take longest/modal).
    comp_rep = {}
    for c in comps:
        idxs = by_comp[c]
        # pick representative with largest text_length (deterministic tie-break by cisi_id)
        rep_idx = sorted(idxs, key=lambda i: (-objs[i]["text_length"], objs[i]["cisi_id"]))[0]
        comp_rep[c] = {k: objs[rep_idx][k] for k in feat_fields}

    if strata_key is None:
        perm_comps = list(comps)
        rng.shuffle(perm_comps)
        mapping = dict(zip(comps, perm_comps))
    else:
        strata = defaultdict(list)
        for c in comps:
            # modal stratum within component
            s_val = Counter(objs[i][strata_key] for i in by_comp[c]).most_common(1)[0][0]
            strata[s_val].append(c)
        mapping = {}
        for s_val, c_list in strata.items():
            p_list = list(c_list)
            rng.shuffle(p_list)
            for orig_c, src_c in zip(c_list, p_list):
                mapping[orig_c] = src_c

    out = []
    for o in objs:
        no = dict(o)
        src_feat = comp_rep[mapping[o[comp_key]]]
        for k in feat_fields:
            no[k] = src_feat[k]
        out.append(no)
    return out


def run_association_battery(objs, comp_key, target_key, label, B=B_PERM, strata_key=None):
    work = [o for o in objs if o[target_key] is not None and o[target_key] != ""]
    comps = sorted({o[comp_key] for o in work})
    comp_sizes = Counter(o[comp_key] for o in work)
    w_comp = [1.0 / comp_sizes[o[comp_key]] for o in work]
    w_spec = [1.0] * len(work)
    y_vals = [o[target_key] for o in work]

    # Precompute observed statistics
    # Frequent closing signs (>= 2 components)
    cl_comps = defaultdict(set)
    for o in work:
        cl_comps[o["closing_sign"]].add(o[comp_key])
    kept_cl = {k for k, cs in cl_comps.items() if len(cs) >= 2}

    def calc_stats(cur_objs):
        cl_vals = [o["closing_sign"] if o["closing_sign"] in kept_cl else "OTHER" for o in cur_objs]
        motif_vals = [o["animal_motif"] for o in cur_objs]
        stroke_vals = [o["has_stroke_numeral"] for o in cur_objs]
        len_vals = [o["text_length"] for o in cur_objs]

        stats = {}
        for wname, w in [("comp_w", w_comp), ("spec_w", w_spec)]:
            nmi_m, cv_m = weighted_nmi_and_cramers_v(motif_vals, y_vals, w)
            nmi_c, cv_c = weighted_nmi_and_cramers_v(cl_vals, y_vals, w)
            nmi_s, cv_s = weighted_nmi_and_cramers_v(stroke_vals, y_vals, w)
            stats[f"motif_nmi_{wname}"] = nmi_m
            stats[f"motif_cramers_v_{wname}"] = cv_m
            stats[f"closing_nmi_{wname}"] = nmi_c
            stats[f"closing_cramers_v_{wname}"] = cv_c
            stats[f"stroke_nmi_{wname}"] = nmi_s
            stats[f"stroke_cramers_v_{wname}"] = cv_s
            if len(set(y_vals)) == 2:
                y0 = sorted(set(y_vals))[1]
                y_bin = [1 if y == y0 else 0 for y in y_vals]
                stats[f"length_abs_spearman_{wname}"] = weighted_spearman_abs(len_vals, y_bin, w)
        return stats

    obs = calc_stats(work)
    rng = random.Random(SEED)
    ge_counts = Counter()
    null_means = defaultdict(float)

    for _ in range(B):
        p_objs = permute_component_features(work, comp_key, rng, strata_key=strata_key)
        p_stats = calc_stats(p_objs)
        for k, v in p_stats.items():
            null_means[k] += v
            if v >= obs[k] - 1e-12:
                ge_counts[k] += 1

    results = {}
    for k, v in obs.items():
        results[k] = {
            "observed": round(v, 6),
            "null_mean": round(null_means[k] / B, 6),
            "p_value": round((1 + ge_counts[k]) / (B + 1), 6),
        }
    return {
        "label": label,
        "comp_key": comp_key,
        "target_key": target_key,
        "n_specimens": len(work),
        "n_components": len(comps),
        "class_distribution": dict(Counter(y_vals)),
        "B": B,
        "strata_key": strata_key,
        "stats": results,
    }


def run_loco_permutation_test(objs, comp_key, target_key, model="nb", B=B_PERM):
    obs = eval_loco_cv(objs, comp_key, target_key, model=model)
    work = [o for o in objs if o[target_key] is not None and o[target_key] != ""]
    labels = sorted({o[target_key] for o in work})
    if model == "nb":
        fast_check = eval_loco_cv_fast_nb(work, comp_key, target_key, labels)
        for m in ("component_weighted_balanced_accuracy", "specimen_weighted_balanced_accuracy", "component_weighted_macro_f1"):
            assert abs(fast_check[m] - obs[m]) < 1e-10, f"Fast NB mismatch on {m}: {fast_check[m]} vs {obs[m]}"
    rng = random.Random(SEED + (1 if model == "nb" else 2))
    metrics = [
        "component_weighted_balanced_accuracy",
        "component_weighted_accuracy",
        "component_weighted_macro_f1",
        "specimen_weighted_balanced_accuracy",
        "specimen_weighted_accuracy",
    ]
    ge = Counter()
    null_sum = defaultdict(float)
    for _ in range(B):
        p_objs = permute_component_features(work, comp_key, rng)
        if model == "nb":
            p_res = eval_loco_cv_fast_nb(p_objs, comp_key, target_key, labels)
        else:
            p_res = eval_loco_cv(p_objs, comp_key, target_key, model=model)
        for m in metrics:
            null_sum[m] += p_res[m]
            if p_res[m] >= obs[m] - 1e-12:
                ge[m] += 1
    perm_summary = {}
    for m in metrics:
        perm_summary[m] = {
            "observed": round(obs[m], 6),
            "null_mean": round(null_sum[m] / B, 6),
            "p_value": round((1 + ge[m]) / (B + 1), 6),
        }
    print(f"  done LOCO {model} ({target_key}, n={len(work)}, K={obs['n_components']}, B={B}): comp_bal_acc={obs['component_weighted_balanced_accuracy']:.4f}, p={perm_summary['component_weighted_balanced_accuracy']['p_value']:.4f}", flush=True)
    return {"model": model, "B": B, "observed_full": obs, "permutation_test": perm_summary}


def run_within_component_dispersion_test(objs, comp_key, target_key, B=B_PERM):
    """Test whether multi-specimen components are more homogeneous or more dispersed than random groups of equal sizes."""
    work = [o for o in objs if o[target_key] is not None and o[target_key] != ""]
    by_comp = defaultdict(list)
    for o in work:
        by_comp[o[comp_key]].append(o[target_key])

    multi = {c: ys for c, ys in by_comp.items() if len(ys) >= 2}
    all_ys = [o[target_key] for o in work]

    def entropy(ys):
        n = len(ys)
        cnt = Counter(ys)
        return -sum((v / n) * math.log2(v / n) for v in cnt.values())

    def purity(ys):
        return Counter(ys).most_common(1)[0][1] / len(ys)

    rng = random.Random(SEED + 99)
    per_comp = {}
    for c, ys in sorted(multi.items()):
        obs_h = entropy(ys)
        obs_p = purity(ys)
        k = len(ys)
        le_h = 0
        ge_h = 0
        ge_p = 0
        null_h_sum = 0.0
        null_p_sum = 0.0
        for _ in range(B):
            samp = rng.sample(all_ys, k)
            h = entropy(samp)
            p = purity(samp)
            null_h_sum += h
            null_p_sum += p
            if h <= obs_h + 1e-12:
                le_h += 1
            if h >= obs_h - 1e-12:
                ge_h += 1
            if p >= obs_p - 1e-12:
                ge_p += 1
        per_comp[c] = {
            "n_diagnostic_specimens": k,
            "class_counts": dict(Counter(ys)),
            "observed_entropy_bits": round(obs_h, 4),
            "null_mean_entropy_bits": round(null_h_sum / B, 4),
            "p_more_homogeneous_entropy": round((1 + le_h) / (B + 1), 6),
            "p_more_dispersed_entropy": round((1 + ge_h) / (B + 1), 6),
            "observed_purity": round(obs_p, 4),
            "null_mean_purity": round(null_p_sum / B, 4),
            "p_more_pure": round((1 + ge_p) / (B + 1), 6),
        }
    return per_comp


def main():
    lipi_rows = [json.loads(line) for line in open(LIPI_PATH, encoding="utf-8")]
    run_part_a(lipi_rows)
    attach_rows = build_lothal_attachments()
    joined_objs, total_joined_faces = extract_features_and_components(attach_rows, lipi_rows)

    pop_a = [o for o in joined_objs if o["is_pop_a_complete"] and o["diagnostic_class_5"] != ""]
    pop_b = [o for o in joined_objs if o["diagnostic_class_5"] != ""]

    print(f"Joined Lothal objects: {len(joined_objs)} (faces={total_joined_faces})")
    print(f"Pop A (complete clean len>=3, diagnostic reverse): {len(pop_a)} specimens, {len({o['die_component_strict'] for o in pop_a})} strict components")
    print(f"Pop B (all legible >=1 sign, diagnostic reverse): {len(pop_b)} specimens, {len({o['die_component_strict'] for o in pop_b})} strict / {len({o['die_component_substring'] for o in pop_b})} substring components")

    # Summary of components in Pop A and Pop B
    def summarize_components(objs, comp_key):
        by_c = defaultdict(list)
        for o in objs:
            by_c[o[comp_key]].append(o)
        out = []
        for c, members in sorted(by_c.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            out.append({
                "component_id": c,
                "n_specimens": len(members),
                "cisi_ids": [m["cisi_id"] for m in members],
                "motifs": dict(Counter(m["animal_motif"] for m in members)),
                "lengths": sorted({m["text_length"] for m in members}),
                "diagnostic_class_5": dict(Counter(m["diagnostic_class_5"] for m in members)),
                "frenez_physical_type": dict(Counter(m["frenez_physical_type"] for m in members)),
                "context_codes": dict(Counter(m["context_code"] for m in members)),
            })
        return out

    # Sensitivity subsets
    pop_a_no_clxi = [o for o in pop_a if o["cisi_id"] not in ("L-161", "L-164")]
    pop_b_no_clxi = [o for o in pop_b if o["cisi_id"] not in ("L-161", "L-164")]
    pop_a_no_g02 = [o for o in pop_a if o["die_component_strict"] != "L-161"]
    pop_b_no_g02 = [o for o in pop_b if o["die_component_strict"] != "L-161"]
    pop_b_doc_ctx = [o for o in pop_b if o["context_code"] in ("W", "O")]

    # Run frozen tests
    results = {
        "run_date": "2026-11-23",
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "inputs_sha256": {
            "lothal_table": sha256_file(LOTHAL_TABLE_PATH),
            "lothal_attachments_v1_csv": sha256_file(os.path.join(OUT_DIR, "lothal-attachments-v1.csv")),
            "lipi_observed_faces": sha256_file(LIPI_PATH),
        },
        "seed": SEED,
        "B_perm": B_PERM,
        "stroke_numeral_codes_definition": "Wells/Lipi codes 001-045 (excluding 000 = unknown/damaged)",
        "all_93_distribution": {
            "total_sealings": len(attach_rows),
            "frenez_physical_type": dict(Counter(r["frenez_physical_type"] for r in attach_rows)),
            "reverse_class_6": dict(Counter(r["reverse_class_6"] for r in attach_rows)),
            "diagnostic_class_5": dict(Counter(r["diagnostic_class_5"] for r in attach_rows if r["diagnostic_class_5"])),
            "mobility_class": dict(Counter(r["mobility_class"] for r in attach_rows if r["mobility_class"])),
            "context_code": dict(Counter(r["context_code"] for r in attach_rows)),
            "joined_in_lipi_objects": len(joined_objs),
            "joined_in_lipi_faces": total_joined_faces,
            "pop_a_complete_eligible_total": sum(1 for o in joined_objs if o["is_pop_a_complete"]),
            "pop_a_diagnostic_specimens": len(pop_a),
            "pop_b_diagnostic_specimens": len(pop_b),
        },
        "components_summary": {
            "pop_a_strict": summarize_components(pop_a, "die_component_strict"),
            "pop_b_strict": summarize_components(pop_b, "die_component_strict"),
            "pop_b_substring": summarize_components(pop_b, "die_component_substring"),
        },
        "association_tests": {
            "pop_a_strict_diag5": run_association_battery(pop_a, "die_component_strict", "diagnostic_class_5", "Pop A strict vs diagnostic_class_5"),
            "pop_a_strict_wood": run_association_battery(pop_a, "die_component_strict", "is_wood_plank_peg", "Pop A strict vs is_wood_plank_peg"),
            "pop_a_strict_mobility": run_association_battery(pop_a, "die_component_strict", "mobility_class", "Pop A strict vs mobility_class"),
            "pop_b_strict_diag5": run_association_battery(pop_b, "die_component_strict", "diagnostic_class_5", "Pop B strict vs diagnostic_class_5"),
            "pop_b_strict_wood": run_association_battery(pop_b, "die_component_strict", "is_wood_plank_peg", "Pop B strict vs is_wood_plank_peg"),
            "pop_b_strict_mobility": run_association_battery(pop_b, "die_component_strict", "mobility_class", "Pop B strict vs mobility_class"),
            "pop_b_substring_diag5": run_association_battery(pop_b, "die_component_substring", "diagnostic_class_5", "Pop B substring vs diagnostic_class_5"),
            "pop_b_substring_wood": run_association_battery(pop_b, "die_component_substring", "is_wood_plank_peg", "Pop B substring vs is_wood_plank_peg"),
        },
        "loco_cv_tests": {
            "pop_a_strict_diag5_nb": run_loco_permutation_test(pop_a, "die_component_strict", "diagnostic_class_5", model="nb", B=B_PERM),
            "pop_a_strict_diag5_logreg": run_loco_permutation_test(pop_a, "die_component_strict", "diagnostic_class_5", model="logreg", B=B_PERM_LOGREG),
            "pop_a_strict_wood_nb": run_loco_permutation_test(pop_a, "die_component_strict", "is_wood_plank_peg", model="nb", B=B_PERM),
            "pop_a_strict_wood_logreg": run_loco_permutation_test(pop_a, "die_component_strict", "is_wood_plank_peg", model="logreg", B=B_PERM_LOGREG),
            "pop_b_strict_diag5_nb": run_loco_permutation_test(pop_b, "die_component_strict", "diagnostic_class_5", model="nb", B=B_PERM),
            "pop_b_strict_diag5_logreg": run_loco_permutation_test(pop_b, "die_component_strict", "diagnostic_class_5", model="logreg", B=B_PERM_LOGREG),
            "pop_b_strict_wood_nb": run_loco_permutation_test(pop_b, "die_component_strict", "is_wood_plank_peg", model="nb", B=B_PERM),
            "pop_b_strict_wood_logreg": run_loco_permutation_test(pop_b, "die_component_strict", "is_wood_plank_peg", model="logreg", B=B_PERM_LOGREG),
            "pop_b_strict_mobility_nb": run_loco_permutation_test(pop_b, "die_component_strict", "mobility_class", model="nb", B=B_PERM),
            "pop_b_substring_diag5_nb": run_loco_permutation_test(pop_b, "die_component_substring", "diagnostic_class_5", model="nb", B=B_PERM),
        },
        "sensitivity_controls": {
            "documented_context_W_vs_O_pop_b_diag5": run_association_battery(
                pop_b_doc_ctx, "die_component_strict", "diagnostic_class_5",
                "Pop B documented context (W vs O) within-stratum permutation", strata_key="context_code"
            ),
            "documented_context_W_vs_O_pop_b_wood": run_association_battery(
                pop_b_doc_ctx, "die_component_strict", "is_wood_plank_peg",
                "Pop B documented context (W vs O) within-stratum permutation (wood)", strata_key="context_code"
            ),
            "drop_rao_CLXI_F_L161_L164_pop_b_diag5": run_association_battery(
                pop_b_no_clxi, "die_component_strict", "diagnostic_class_5",
                "Pop B dropping L-161 & L-164 (Rao Plate CLXI F conflict)"
            ),
            "drop_rao_CLXI_F_L161_L164_pop_b_loco_nb": run_loco_permutation_test(
                pop_b_no_clxi, "die_component_strict", "diagnostic_class_5", model="nb", B=B_PERM
            ),
            "drop_entire_G02_elephant_pop_a_diag5": run_association_battery(
                pop_a_no_g02, "die_component_strict", "diagnostic_class_5",
                "Pop A dropping entire G02 elephant component"
            ),
            "drop_entire_G02_elephant_pop_b_diag5": run_association_battery(
                pop_b_no_g02, "die_component_strict", "diagnostic_class_5",
                "Pop B dropping entire G02 elephant component"
            ),
            "drop_entire_G02_elephant_pop_b_loco_nb": run_loco_permutation_test(
                pop_b_no_g02, "die_component_strict", "diagnostic_class_5", model="nb", B=B_PERM
            ),
        },
        "within_component_dispersion": {
            "pop_b_strict_diag5": run_within_component_dispersion_test(pop_b, "die_component_strict", "diagnostic_class_5", B=B_PERM),
            "pop_b_strict_frenez_12class": run_within_component_dispersion_test(pop_b, "die_component_strict", "frenez_physical_type", B=B_PERM),
        },
    }

    out_path = os.path.join(OUT_DIR, "lothal-test-v1.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")

    # Print key headline results
    print("\n=== HEADLINE LOCO-CV RESULTS ===")
    for k, v in results["loco_cv_tests"].items():
        p = v["permutation_test"]["component_weighted_balanced_accuracy"]
        p_s = v["permutation_test"]["specimen_weighted_balanced_accuracy"]
        base = v["observed_full"]["baseline_comp_prior_component_balanced_accuracy"]
        print(f"{k}: comp_bal_acc={p['observed']:.4f} (null={p['null_mean']:.4f}, p={p['p_value']:.4f}, base={base:.4f}) | spec_bal_acc={p_s['observed']:.4f} (p={p_s['p_value']:.4f})")

    print("\n=== HEADLINE ASSOCIATION RESULTS (Pop B strict vs diag5 & wood) ===")
    for test_k in ["pop_a_strict_diag5", "pop_b_strict_diag5", "pop_b_strict_wood", "pop_b_strict_mobility"]:
        print(f"-- {test_k} --")
        for sk, sv in results["association_tests"][test_k]["stats"].items():
            if "comp_w" in sk or "spearman" in sk:
                print(f"  {sk}: obs={sv['observed']:.4f}, null={sv['null_mean']:.4f}, p={sv['p_value']:.4f}")

    print("\n=== WITHIN-COMPONENT DISPERSION (Pop B strict, diag5 & 12-class) ===")
    for mode, d in results["within_component_dispersion"].items():
        print(f"-- {mode} --")
        for c, cv in d.items():
            print(f"  comp {c} (n={cv['n_diagnostic_specimens']}): H={cv['observed_entropy_bits']} (null={cv['null_mean_entropy_bits']}, p_homog={cv['p_more_homogeneous_entropy']}, p_disp={cv['p_more_dispersed_entropy']}), purity={cv['observed_purity']} | {cv['class_counts']}")


if __name__ == "__main__":
    main()
