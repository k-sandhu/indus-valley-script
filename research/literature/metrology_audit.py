"""Reproduce a source-preserved audit; no glyph OCR or claimed decipherment.

Only writes files under research/literature/metrology/. Author-reported capacities
are estimates from geometric models, not measured liquid fills. See README.md.
"""
from pathlib import Path
import csv, itertools, json, math

BASE = Path(__file__).resolve().parent
OUT = BASE / "metrology"
OUT.mkdir(exist_ok=True)

SOURCES = {
    "fuls2012": {
        "url": "https://www.academia.edu/8808307/VOLUMENMA%C3%9FE_VON_TONGEF%C3%84%C3%9FEN_DER_INDUSKULTUR",
        "access": "Author-posted indexed text; original PDF visual unavailable without sign-in.",
        "coordinates": "Preprint article pp.6-10, Tables1-3; final article listed pp.101-114 by author.",
        "do_not_assume_final_page_offset": True,
    },
    "cisi1": {
        "url": "https://ignca.gov.in/Asi_data/76884.pdf",
        "sha256": "47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d",
        "pages": "Printed233-234 (PDF269-270), printed372 (PDF408); K90 printed319 (PDF355).",
        "access": "Government scan; original photographs and numeric metadata visually inspected.",
        "duplicate_scan_offset": 431,
    },
    "vats1940_text": {
        "url": "https://ignca.gov.in/Asi_data/18220.pdf",
        "sha256": "022fc5761c16f63c36bb83429a4ecf1cd23ff33b0b13d12f1c0445962f0614ec",
        "pages": "Printed91 (PDF118), printed254-255 (PDF281-282).",
        "access": "Government scan; original text and table visually inspected.",
    },
    "vats1940_plates": {
        "url": "https://ignca.gov.in/Asi_data/9842.pdf",
        "sha256": "1855dc750a070c570eaecb78c8217dd350ad7e559a65898a57242545fb54a442",
        "pages": "PlateXXIIIa, PDF58; PDF59 blank, PDF60 is PlateXXIV.",
        "access": "Government scan; original excavation photograph visually inspected.",
    },
    "kenoyer_meadow1997": {
        "url": "https://www.harappa.com/sites/default/files/pdf/Kenoyer1997_Excavations%20at%20Harappa%201994-1995%20New%20Perspective.pdf",
        "sha256": "4ce604f7ed11d247a6ab88e49da946d00cdc1b2787b3dd2c58b327c95a7a51d3",
        "pages": "Printed161 (PDF23), Fig12.2 and catalogue row12.02; printed151 (PDF13) sump-pot and four-inscription prose.",
        "access": "Downloaded excavation-author primary paper; original profile and inscriptions visually inspected.",
    },
    "fuls2020": {
        "url": "https://www.researchgate.net/publication/373522958_Ancient_Writing_and_Modern_Technologies_-_Structural_Analysis_of_Numerical_Indus_Inscriptions",
        "pages": "Author2023 posting, article pp.28-29 (PDF14-15); alternative posting pp.70-71.",
        "access": "Author-posted indexed text and public web PDF; local downloader returned403.",
        "numeral_10_to_unit_4_04_is_explicitly_conditional": True,
    },
    "wells2018": {
        "url": "https://www.jstor.org/stable/j.ctv19vbgkc.46",
        "doi": "10.2307/j.ctv19vbgkc.46",
        "pages": "Chapter623-627 in indexed edition; publisher TOC lists631-636 in another edition.",
        "access": "Publisher/author metadata and indexed abstract; full chapter unavailable.",
        "abstract_states_base_volume_calculated_from_three_complete_vessels": True,
    },
}

# Fuls's indexed Table3, with interpretation fields separated from its data.
rows = [
    dict(object="H95-2661", shape="vase", volume_profile_l=88.3, n=4,
         inscription_author="only_strokes", unit_reported_l=22.1,
         primary_glyph_audit="four_tall_or_slanted_rim_strokes_no_U_in_this_cluster",
         class_eligibility="different_or_ambiguous", role="additional_prior_case",
         reason="No U in audited cluster; primary reports four inscriptions and reuse as sump pot."),
    dict(object="MD-1374", shape="vase", volume_profile_l=138.8, n=6,
         inscription_author="only_strokes", unit_reported_l=23.1,
         primary_glyph_audit="not_independently_inspected",
         class_eligibility="unverified_different", role="additional_prior_case",
         reason="Author describes three vertical plus three oblique marks; exact graphic and context unresolved."),
    dict(object="MD-63-3", shape="vase", volume_profile_l=40.3, n=None,
         inscription_author="complex_1_question", unit_reported_l=40.3,
         primary_glyph_audit="not_independently_inspected",
         class_eligibility="unresolved", role="additional_prior_case",
         reason="Source numeric denominator is1?; no validated comparable module."),
    dict(object="H-372", shape="round", volume_profile_l=121.0, n=3,
         inscription_author="U_plus_strokes", unit_reported_l=40.3,
         primary_glyph_audit="three_tall_strokes_and_open_U_or_V",
         class_eligibility="three_pot_fit_family", role="fit_case",
         reason="CISI original verifies coarse graphic; measurement-to-object catalogue identity discordant."),
    dict(object="H-371", shape="round", volume_profile_l=240.6, n=6,
         inscription_author="strokes_plus_U", unit_reported_l=40.1,
         primary_glyph_audit="six_tall_strokes_and_open_U_or_V",
         class_eligibility="three_pot_fit_family", role="fit_case",
         reason="CISI excavation1033a agrees with source; measurement raw replicates unavailable."),
    dict(object="H-370", shape="round", volume_profile_l=283.8, n=7,
         inscription_author="only_strokes", unit_reported_l=40.5,
         primary_glyph_audit="seven_tall_strokes_no_U_in_visible_cluster",
         class_eligibility="three_pot_fit_family_U_optional_by_author", role="fit_case",
         reason="U absence must be retained; catalogue excavation12908 disagrees with source1033b."),
    dict(object="K-90", shape="round", volume_profile_l=103.0, n=2,
         inscription_author="complex", unit_reported_l=51.5,
         primary_glyph_audit="two_tall_rim_strokes_separate_from_three_sign_body_text_with_U",
         class_eligibility="unresolved", role="additional_prior_case",
         reason="Separate graphic clusters; author assumes30cm photo scale not independently fixed by observed plate."),
    dict(object="MD-63-6", shape="vase", volume_profile_l=52.8, n=None,
         inscription_author="complex_1_question", unit_reported_l=52.8,
         primary_glyph_audit="not_independently_inspected",
         class_eligibility="unresolved", role="additional_prior_case",
         reason="Source denominator1?; additional signs and U do not establish same capacity module."),
]
for row in rows:
    row["source"] = "fuls2012_table3_preprint_p10"
    row["original_table_visual_alignment_verified"] = False
    row["volume_is_measured_liquid_fill"] = False
    row["eligible_independent_heldout_40_4_test"] = False
    row["per_stroke_computed_l"] = row["volume_profile_l"] / row["n"] if row["n"] else None

# Table1: H372 has one fewer numeric value than the four measurement columns.
# The field mapping below is explicitly provisional for that row only.
dimensions = [
    dict(object="H-372", source_excavation="12908", cisi_excavation=None,
         cisi_museum="M774609", cisi_photo="HU1307", source_values=[61.4,64,33.5],
         max_outer_diameter_cm=61.4, outer_height_cm=None, inner_height_cm=64.0,
         mouth_diameter_cm=33.5, dimension_alignment="provisional_missing_outer_height",
         identity_status="discordant_source12908_is_CISI_H370; do_not_reassign_measurements"),
    dict(object="H-371", source_excavation="1033a", cisi_excavation="1033a",
         cisi_museum="M774608", cisi_photo="HU1304", source_values=[85.6,91.4,74,43.5],
         max_outer_diameter_cm=85.6, outer_height_cm=91.4, inner_height_cm=74.0,
         mouth_diameter_cm=43.5, dimension_alignment="indexed_columns_unambiguous_but_PDF_not_seen",
         identity_status="excavation_agrees"),
    dict(object="H-370", source_excavation="1033b", cisi_excavation="12908",
         cisi_museum="M774607", cisi_photo="HU1302", source_values=[83.6,86.4,85,40.0],
         max_outer_diameter_cm=83.6, outer_height_cm=86.4, inner_height_cm=85.0,
         mouth_diameter_cm=40.0, dimension_alignment="indexed_columns_unambiguous_but_PDF_not_seen",
         identity_status="discordant_excavation_number"),
]
model_values = {
    "H-372": {"sphere_l":123.6,"ellipsoid_l":118.8,"profile_l":121.0,"n":3},
    "H-371": {"sphere_l":248.7,"ellipsoid_l":259.1,"profile_l":240.6,"n":6},
    "H-370": {"sphere_l":292.9,"ellipsoid_l":282.7,"profile_l":283.8,"n":7},
}
for r in model_values.values():
    vals=[r[k] for k in ("sphere_l","ellipsoid_l","profile_l")]
    r["model_envelope_l"]=[min(vals),max(vals)]
    r["per_stroke_model_envelope_l"]=[min(vals)/r["n"],max(vals)/r["n"]]
    r["envelope_is_confidence_interval"]=False

fit=[r for r in rows if r["role"]=="fit_case"]
counts=[r["n"] for r in fit]
volumes=[r["volume_profile_l"] for r in fit]
frozen=40.4
for r in fit:
    pred=frozen*r["n"]
    r["frozen_prediction_l"]=pred
    r["frozen_residual_l"]=r["volume_profile_l"]-pred
    r["frozen_relative_residual_percent"]=(r["volume_profile_l"]/pred-1)*100

least_squares_scale=sum(n*v for n,v in zip(counts,volumes))/sum(n*n for n in counts)
permutations=[]
for perm in itertools.permutations(counts):
    a=sum(n*v for n,v in zip(perm,volumes))/sum(n*n for n in perm)
    sse=sum((v-a*n)**2 for n,v in zip(perm,volumes))
    permutations.append({"assigned_n":perm,"fitted_scale_l":a,"sse_l2":sse})
permutations.sort(key=lambda r:r["sse_l2"])

audit={
    "version":1,
    "sources":SOURCES,
    "source_preserved_capacities":rows,
    "source_preserved_dimensions":dimensions,
    "reported_geometric_model_sensitivity":model_values,
    "fit_only":{
        "objects":[r["object"] for r in fit],
        "least_squares_zero_intercept_scale_l_per_long_stroke":least_squares_scale,
        "frozen_scale_l_per_long_stroke":frozen,
        "frozen_sse_l2":sum((v-frozen*n)**2 for n,v in zip(counts,volumes)),
        "fit_sse_l2":sum((v-least_squares_scale*n)**2 for n,v in zip(counts,volumes)),
        "number_distinct_count_permutations":len(permutations),
        "smallest_possible_nonrandomized_ordinary_permutation_p":1/len(permutations),
        "permutation_p_value_claimed":False,
        "permutation_caution":"Three selected published fitting cases; selection and geometric assumptions not randomized. Six permutations are only an illustrative combinatorial bound.",
        "permutation_assignments":permutations,
    },
    "identifiability":{
        "equation":"V_i = n_i * q_long * u_litres",
        "observable_product":"q_long*u_litres approximately40.4L",
        "invariance":"q_long->c*q_long; u_litres->u_litres/c",
        "equivalent_examples":[
            {"q_long":1,"u_litres":40.4},
            {"q_long":10,"u_litres":4.04},
            {"q_long":12,"u_litres":40.4/12},
        ],
        "example_role":"Mathematical alternatives, not asserted historical readings.",
        "numeric_value10_identified_by_three_capacities":False,
        "base_unit4_04_independently_measured":False,
        "unit4_04_is_conditional_on_longstroke10_in_Fuls2020":True,
    },
    "heldout_validation":{
        "eligible_independent_same_module_objects":0,
        "test_performed":False,
        "scope":"A commodity-specific or module-specific40.4L/stroke hypothesis. Additional vessels do not automatically falsify it.",
        "required_external_anchor":[
            "Raw repeated physical measures tied unambiguously to museum/excavation IDs.",
            "Frozen graphic eligibility, site/context and commodity scope before observing heldout capacities.",
            "Independent complete vessels, residues or contents supporting the same scope.",
            "Independent mixed short/long numeral evidence to identify q_long relative to shortstroke, not capacity alone.",
        ],
    },
    "source_internal_discordances":[
        "Fuls2012 prose p9 gives40.3-40.5L whereas Table3 includesH37140.1L.",
        "Fuls2012 prose p9 givesK90unit56.7L whereas Table3 gives51.5L=103/2.",
        "Fuls2012Table1 assignsH37212908/H3701033b, unlike CISI1 H37012908/H372unknown.",
        "Fuls2012 citesShah&Parpola1991 for oblique H370-372 images; inspected CISI1 isJoshi&Parpola1987.",
    ],
    "limitations":[
        "Index text may lose table spacing; no source measurement has been silently reassigned.",
        "Wall thickness, repeated-measurement scatter and complete profile coordinate files unavailable.",
        "Geometric model envelope is a sensitivity range, not sampling uncertainty.",
        "Museum photo shows glyphs, not vessel full three-dimensional capacity.",
        "Vats's post-cremation context and Kenoyer's reuse context are not demonstrated original contents.",
        "No phonetic reading, word translation or language identification follows from this audit.",
    ],
}

(OUT/"source_and_identifiability_audit.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding="utf-8")
with (OUT/"source_capacity_table.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
    w.writeheader();w.writerows(rows)
with (OUT/"source_dimension_table.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(dimensions[0]))
    w.writeheader();w.writerows(dimensions)
print(json.dumps({"fit_scale":least_squares_scale,"frozen_sse":audit["fit_only"]["frozen_sse_l2"],"eligible_heldout":0,"output":str(OUT)},indent=2))
