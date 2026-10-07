"""Rebuild the corrected inventory from its preserved first pass and saved outputs.

Run from the repository root. This reads existing endpoints; it runs no analysis.
Only this package's inventory.json and sources.json are written.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-06-byproduct-inventory"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    inv = load(PACKAGE / "first-pass/inventory.json")
    src = load(PACKAGE / "first-pass/sources.json")
    cs = {c["id"]: c for c in inv["candidates"]}
    sh = "experiments/2026-10-02-six-hour/"
    cp = "experiments/2026-10-02-connections-and-priority/"
    sr = "experiments/2026-10-02-source-recovery/"
    checks = []

    def read(p):
        return load(ROOT / p)

    def bind(cid, key, path, pointer, value=None, transform="exact"):
        obj = read(path)
        for part in pointer.strip("/").split("/"):
            obj = obj[int(part)] if isinstance(obj, list) else obj[part]
        if value is None:
            value = len(obj) if transform == "length" else obj
        cs[cid]["numbers"][key] = value
        checks.append(dict(candidate_id=cid, inventory_key=key, source_path=path,
                           source_pointer=pointer, transform=transform, expected=value))
        locator = path + "#" + pointer
        if locator not in cs[cid]["evidence_fields"]:
            cs[cid]["evidence_fields"].append(locator)

    # All candidates explicitly carry a registry list, including standalone records.
    for c in cs.values():
        c.setdefault("registry_ids", [])
        c["assessment_status"] = "Exploratory"
        c["provenance_notes"] = []
        c["related_candidates"] = []
        c["venue_options_unverified"] = []
        c["evidence_fields"] = []

    c = cs["PUBLIC-INDEX-COVERAGE"]
    c.update(title="Evidence-census package: held placeholder", established="Await the separate evidence-census package's completed outputs and review. No result from B1 or B2 is assessed here.", numbers={}, evidence=["experiments/2026-10-06-evidence-census/"], evidence_fields=[], status="Proposed", registry_ids=[], smallest_form="Pending completed package and review", venues=[], venue_sources=[], remaining_work="Reassess only after the package is complete and reviewed.", missing_validation="Completed package outputs and independent review are required.")
    c["novelty"] = dict(judgment="No judgment made.", precedent_search="Not done; held placeholder", sources=[])
    c["ranking_eligible"] = False

    c = cs["FULS-ARITHMETIC"]
    c.update(title="Fuls numerical premises, exact arithmetic and capacity audit", established="In variable order (L,S,v), the assumed equations v=2S-L and vL+1=7S+5 have four positive-integer solutions: (4,20,36), (6,8,10), (10,8,6), (36,20,4). Restricting L to 8–13 selects (10,8,6). The footnote's even-S inference fails for the first equality alone; S is even in every joint solution, so correcting that step changes no joint conclusion. The companion capacity audit fits three selected published profile-derived volumes at 40.3531914893617 L/stroke, with residuals -0.2, -1.8 and +1.0 L at 40.4. It documents excavation-ID and K90 prose/table conflicts, and no eligible independent held-out vessel.", evidence=["research/methods/NUMERICAL_CONSTRAINT_AUDIT.md", "research/methods/results/numerical_equalities/numerical_equalities_audit.json", "research/methods/results/numerical_equalities/numerical_count_delta_sensitivity.json", "research/literature/metrology/source_and_identifiability_audit.json", "research/literature/metrology/numerical_source_premises.json", "research/literature/metrology/README.md"], smallest_form="One source commentary joining the arithmetic, capacity and object-premise audits", venues=[], venue_sources=[], remaining_work="One to two weeks for original-source and specialist review; correspondence route requires the original volume's editors or author.")
    c["numbers"]["variable_order"] = ["L", "S", "v"]
    c["numbers"]["range_L"] = [8, 13]
    c["numbers"]["all_solutions"] = [[4,20,36],[6,8,10],[10,8,6],[36,20,4]]
    mpath="research/literature/metrology/source_and_identifiability_audit.json"
    bind(c["id"],"capacity_fit_L_per_stroke",mpath,"/fit_only/least_squares_zero_intercept_scale_l_per_long_stroke")
    bind(c["id"],"heldout_same_module_vessels",mpath,"/heldout_validation/eligible_independent_same_module_objects")
    c["numbers"].update(capacity_vessels=["H-372","H-371","H-370"], profile_capacities_L=[121.0,240.6,283.8], long_stroke_counts=[3,6,7], residuals_at_40_4_L=[-0.2,-1.8,1.0], K90_prose_table_unit_L=[56.7,51.5], two_stroke_alternative_solution=[4,4,8])
    c["evidence_fields"] += ["all_admissible_solutions", "range_sensitivities.L_8_to_13", "first_equality_parity_audit", "source_preserved_capacities[].frozen_residual_l", "source_internal_discordances", "premises", "conditional_algebra_result"]
    c["provenance_notes"] = ["Fuls's 2020 chapter is the proposal under audit. Its author-posted reprint was reopened as indexed PDF text in this correction, at printed pp. 29–32; the volume is Studies on Indus Script, pp. 57–90. Figure-level archaeological interpretations remain unverified.", "The capacity values are geometric reconstructions from three selected fitting vessels, not liquid-fill measurements or a held-out validation. H370/H372 excavation IDs disagree between sources; measurements are not reassigned.", "The saved premise audit found no M1383 join, 82-fragment count or 15–20-total claim in the inspected Vidale chapter; Fuls attributes the count premise to Wells 2015. The current numeric ID 3786 denotes M1540; H904 matches the cited plate candidate. A two-stroke variant yields (4,4,8), outside S>=8."]
    c["novelty"] = dict(judgment="A targeted erratum query returned no directly relevant correction. This limited query cannot establish priority. Fuls and Wells supply the prior proposal; the conditional enumeration and source-conflict table are the assessed work.", precedent_search="Partly checked; one targeted erratum query and original proposal reopened", sources=["SRC-18","SRC-32"])
    c["missing_validation"] = "Specialist review of the source identities, graphic counts, count range and vessel scope; obtain measurement records and independent comparable vessels. Source text was reopened, but archaeological premises are not authenticated by the algebra."
    c["submission_route"] = "Draft correspondence for the original proposal's author and volume editors; no verified standalone article-type fit is claimed."

    c=cs["SUSA-SOURCE-CENSUS"]
    c["status"]="Exploratory"
    c["established"]="The post-outcome 2022 catalogue census has 69 coded Susa entries and 57 eligible mass/mark ratios. Soutzo's no. 13820 is listed at 2,769 g, while Ascalone 2022 entry 603, which cites that number, gives 3,067 g, limestone, six strokes and Louvre Sb 9340. The two source assertions differ in mass, material and marks; no independently checked museum concordance establishes that they describe the same surviving object. Two 1911 unmarked-duck descriptions also conflict with later stroke counts."
    c["provenance_notes"]=["The census was designed after inspecting masses. Three named source mass differences are -10.75, -9.5 and +298 g; the first concerns a four-mark ovoid.","The source audit compares catalogue assertions. Museum identity, conservation and reweighing histories remain unresolved."]
    c["novelty"]=dict(judgment="Soutzo 1911 already reads duck marks as weight multiples, and Ascalone/Peyronel 1999 treats Susa, Gulf and Indus weight systems. General mass-per-mark novelty is therefore unavailable. The exact 1911/2022 source conflict remains a candidate correction requiring museum concordance; the 1999 article was found in metadata only.",precedent_search="On-subject search completed; primary 1911 local text inspected and 1999 metadata found, full 1999 article unavailable",sources=["SRC-25","SRC-26","SRC-06"])
    c["related_candidates"]=["MARKED-WEIGHT-CENSUS"]
    c["evidence_fields"]=["marked_entry_count","complete_single_graphic_entry_count","comparisons[2].original_source","comparisons[2].modern_source", "observations.json: source-specific duck descriptions"]
    c["smallest_form"]="Source-conflict table for catalogue maintainers; a data paper only after rights-cleared deposit"

    c=cs["CATALOGUE-CROSSCHECKS"]
    c["established"]="Two AI-model transcriptions of the same Lothal table sum to 133 impressions and 62 single-impression objects, compared with 130 and 63 in that chapter's prose; the second reader knew the first aggregates. Tamil Nadu 4.19C has six components in one of three purposively checked printed rows and five in the deployed array; the 5.0-to-5.7 variant mapping could reflect representation or edition differences. Separately, two web routes differ in four literal identifier cells because of spaces or a dot. Gonur's source reports 26 tokens, while two AI readers counted 23 representations in each panel; unspecified figure selection leaves a sample explanation open."
    c["evidence"] += [sh+"lothal-physical-use/independent-review/source-assertions.json",cp+"south-india/aggregate-v1/results.json",cp+"south-india/stroke-membership-v2/results.json",sr+"oxus/results-v2.json"]
    c["evidence_fields"]=["source-assertions.json: table/prose assertions", "cross_route_cells_differing", "site_route_occurrence_total", "family_route_occurrence_total", "printed_source_checks[2]", "results-v2.json: gonur_hoard_source"]
    c["novelty"]=dict(judgment="The Lothal chapter and Frenez's thesis are earlier source ledgers; the thesis was identified from its author's CV but not read. Tamil Nadu's portal links the 2025 morphological study, while the project compared later print volumes; edition reconciliation is missing. Bonora et al. 2014 is prior token scholarship. No query establishes that any discrepancy is a previously unpublished error.",precedent_search="On-subject search completed; Lothal chapter metadata, thesis CV and Gonur article record opened; Tamil Nadu source located",sources=["SRC-27","SRC-28","SRC-30","SRC-31"])
    c["provenance_notes"]=["Lothal counts are model readings of one published table, not independent excavation counts. Tamil Nadu route differences compare family and site web routes, not print and web. Gonur panels may illustrate a subset."]
    c["related_candidates"]=["LOTHAL-OBSERVATION-FRAME","SOUTH-INDIA-STROKE-POPULATION","GONUR-ALTYN-RECOVERY"]
    c["smallest_form"]="Separate correction requests to source owners; data paper only if a reusable discrepancy dataset is deposited"

    c=cs["CONTEXT-COMPLETENESS"]
    c["numbers"]["depth_placeholders_missed_by_old_rule"]=c["numbers"].pop("misread_depth_placeholders")
    c["numbers"]["joint_context_rows_by_site"]={"Harappa":751,"Mohenjo-daro":682,"other":11}
    c["established"]="In the pinned derivative export, 5,680 rows represent 4,695 provisional numeric families. Requiring informative site, area, room/grid, excavation label, depth and chronology yields 1,444 rows and 1,163 families: 751 Harappa, 682 Mohenjo-daro and 11 other rows. Of 69 source-cohort objects, 60 join the export and two of those 60 enter the primary benchmark. The old missingness rule counted 2,870 dash-only depth placeholders as present. These are export-field availability statistics, not estimates of surviving excavation documentation."
    c["novelty"]=dict(judgment="Fuls's ICIT documentation already describes unavailable chronology and uneven excavation/site representation. The possible contribution is a pinned-export field-by-field audit and cohort-filter table. A targeted context-completeness query did not establish priority for this exact audit.",precedent_search="On-subject search and official ICIT documentation opening completed; precise audit novelty unchecked",sources=["SRC-29"])
    c["provenance_notes"]=["Families are provisional export groupings. Cohort filtering is tied to a particular length/direction/completeness benchmark; it does not count all context-rich archaeological objects."]
    c["evidence_fields"]=["counts", "joint_availability", "field_availability.depth", "source-cohorts/results.json: cohort join and eligibility counts"]

    c=cs["CHART-687"]
    c["evidence"]=[p for p in c["evidence"] if p not in ["research/chart_reference/README.md","research/chart_reference/duplicate_labels/adjudication.json"]]
    c["evidence"] += ["output/chart_atlas/reference.json","research/corpus/primary/chart_complete/consolidated_atlas_audit.json","research/literature/chart_complete/duplicate_labels/adjudication.json"]
    c["numbers"]["post_comparison_lower_code_ambiguities"]=16
    c["numbers"]["ambiguous_cells_by_page"]={"PDF20":2,"PDF21":14}
    c["established"]="An AI-model annotation atlas links all 687 cells of the two-page Helsinki 1979 interim-edition chart to source crops. AI numeric references cover 175 cells on PDF20 and 337 on PDF21; a different AI agent read the other 175. The 22 initial disagreements concern 337 PDF21 labels. The consolidated atlas retains 16 lower-code ambiguities (14 PDF21, two PDF20). A fresh 20-cell PDF21 comparison gives 16 joint, 19 rank and 17 code agreements. These are model numeric-label comparisons, with no expert certification of digits or glyph identity."
    c["evidence_fields"]=["frame_cells","ambiguous_lower_code_cells", "atlas_images_checked", "reference.json: adjudication_limit", "fresh20_before_correction.json: numeric comparisons"]
    c["provenance_notes"]=["Numeric references and the Helsinki 1979 source edition have recorded CC BY 4.0 reuse bases; retain attribution and distinguish that licensed edition from unrelated photograph rights. The reference/adjudication source limits explicitly identify AI visual readers."]
    c["novelty"]=dict(judgment="Existing sign lists and ICIT precede this atlas. This correction drops unrelated weights and journal-list sources. No subject search establishes novelty for a double-reading numeric-label audit; the publishable claim is a documented annotation resource.",precedent_search="Exact chart-annotation precedent check not done; existing catalogue identified",sources=["SRC-32","SRC-36"])
    c["smallest_form"]="Data paper describing deposited crop-linked numeric annotations and retained uncertainty"

    c=cs["HARAPPA-FRAME"]
    c["status"]="Exploratory"
    c["evidence"] += [cp+"harappa-short-records/main-v2/results.json",cp+"harappa-short-records/REPORT.md"]
    bind(c["id"],"direct_stroke_counts",cp+"harappa-short-records/main-v2/results.json","/native_source/directly_counted_faces")
    bind(c["id"],"readable_3_4_3_profiles",cp+"harappa-short-records/main-v2/results.json","/native_source/complete_count_profile_objects")
    for k,p in [("tablets_sharing_three_exact_modules","/exact_unordered_module_set_class_sizes/0"),("all_pairs","/pair_counts/all_object_pairs"),("pairs_same_modules","/pair_counts/exact_same_modules"),("pairs_one_module_changed","/pair_counts/exact_one_module_changed"),("pairs_two_modules_changed","/pair_counts/exact_two_modules_changed")]: bind(c["id"],k,cp+"harappa-short-records/main-v2/results.json",p)
    c["established"]="The source-linked frame has 22 tablets and 66 faces, with 16 tablets in the published unit-8040 clump. HARP-SHORT-01 extends the earlier seven-face/two-profile endpoint to 32 directly counted faces and five fully readable (C,A,D)=(3,4,3) profiles. In the derivative coding, 20 tablets share the same unordered set of three exact modules; among 231 pairs, 190 are identical, 40 differ in one module and one in two. Imported face order is serialization; physical prism order is not established."
    c["novelty"]=dict(judgment="Meadow and Kenoyer's published frame supplies the object, unit and production-group observations. The exact contribution is recoding and joining that frame; exact-frame priority and overlap with CISI 3.1's registration list remain unchecked.",precedent_search="Principal source known; exact-frame novelty unchecked",sources=[])
    c["provenance_notes"]=["The newer counts and module comparisons come from an Exploratory source/corpus refinement. Direct counts are AI readings of the published drawings; fine allograph assignments remain derivative and need archaeological review."]

    c=cs["LOTHAL-OBSERVATION-FRAME"]
    c["evidence"] += [sh+"lothal-physical-use/independent-review/main-refined/results.json",cp+"lothal-contact/results.json"]
    c["established"]="The AI-transcribed 93-object source table sums to 133 impressions. The export joins 68 objects; 29 eligible objects form nine strings. G01 occurs on 11 objects across seven published physical categories. For four selected G02 zones, two AI readers' count envelopes are 2–4, 3–5, 3–5 and 2–3, whose arithmetic intersection is three. Two zones are upper margins, one is a lower-left side strip and one a right margin; comparable coverage and whole-object totals are not established. L206 is one resolved contact example viewed twice, among five pictured G01 objects."
    c["numbers"]["joined_objects"]=68
    c["numbers"]["G02_selected_zone_reader_envelopes"]=[[2,4],[3,5],[3,5],[2,3]]
    c["novelty"]=dict(judgment="Frenez and Tosi's 2005 source chapter and Frenez's 2005 thesis precede the frame. The possible contribution is machine-readable table recoding, count reconciliation and source-zone locators; the thesis ledger was not inspected here, so priority remains unchecked.",precedent_search="On-subject search partly checked; chapter record and thesis CV opened",sources=["SRC-27","SRC-28"])
    c["evidence_fields"]=["groups[0]", "G02.reader_envelope_visible_zone_intervals", "G02.zone_comparability_established", "G02.whole_object_totals_observed", "G01.board_edge_only_incompatible_objects"]
    c["provenance_notes"]=["Both table and image readers were AI models. The second table reader knew the first aggregates; source-zone intervals are reader envelopes, not confidence intervals. The same count discrepancy is summarized at rank 3."]
    c["related_candidates"]=["CATALOGUE-CROSSCHECKS"]

    c=cs["KANMER-PENDANT-FRAME"]
    c["numbers"]["individual_hole_axis_or_quantified_wear_measurements"]=c["numbers"].pop("hole_or_wear_measurements")
    c["numbers"]["shared_reported_perforation_diameter_mm"]=4.15
    c["established"]="The frame covers eight related objects, including four clay pendants. All four have numbered reverse photographs; three have registrations, dimensions/mass and individual trench/layer records. Those three measure 32.5–34.1 mm long, 34.5–35.4 mm wide, 15.7–16.6 mm thick and 15.0–15.7 g. No individual hole, axis or quantified-wear measurement or direct laboratory date is available; a shared 4.15 mm perforation diameter is reported. A handling experiment remains Proposed."
    c["provenance_notes"]=["A shared 4.15 mm perforation diameter is reported, although individual hole/axis/wear measurements are absent. The 1.15% width CV is a population CV over three objects. Proposed physical handling trials were not run."]
    c["missing_validation"]="Original object access, individual hole/axis/quantified wear measurements and a prospectively specified handling experiment. A shared perforation diameter alone does not supply object-specific wear."
    c["venue_options_unverified"]=["EXARC Journal: physical experimental report; contributor page timed out, and its search snippet flags restrictions on AI-generated ideas."]

    c=cs["SOUTH-INDIA-STROKE-POPULATION"]
    c["established"]="The post-outcome stroke-membership refinement counts 480 plain-stroke occurrences, 194 compound forms and 142 simple stroke-plus-one-component forms. The first endpoint used 115 forms. Four identifier-cell differences compare site and family web routes (9,349 and 9,345 occurrences), with whitespace or a dot in the keys. A separate purposive print check finds six components for 4.19C versus five in the deployed web array."
    c["evidence_fields"]=["cross_route_cells_differing", "site_route_occurrence_total", "family_route_occurrence_total", "printed_source_checks[2]", "stroke-membership-v2/results.json: count summaries"]
    c["provenance_notes"]=["194 and 142 count forms; 480 counts occurrences. Membership v2 was defined after inspecting the first endpoint. The print difference may reflect edition or representation; source-owner review is missing."]
    c["novelty"]=dict(judgment="The official portal and 2025 morphology book already catalogue Tamil Nadu graffiti. This is a pinned-implementation audit and post-outcome population refinement, with no completed check for prior publication of the exact discrepancy.",precedent_search="Partly checked; subject sources located",sources=["SRC-30"])
    c["related_candidates"]=["CATALOGUE-CROSSCHECKS"]

    c=cs["GONUR-ALTYN-RECOVERY"]
    c["provenance_notes"]=["23 and 23 are AI readings of two panels in one publication. Figure selection is unspecified; they do not establish that the reported 26-object assemblage contains only 23 tokens."]
    c["novelty"]=dict(judgment="Bonora et al. 2014 is earlier regional token scholarship; object-level catalogue recovery is the practical contribution. Exact figure/hoard discrepancy priority remains unchecked.",precedent_search="Partly checked; regional article record opened",sources=["SRC-31"])
    c["related_candidates"]=["CATALOGUE-CROSSCHECKS","MARKED-WEIGHT-CENSUS"]
    c["smallest_form"]="Illustrated source appendix or catalogue-owner query; data paper only after a reusable source-locator dataset is deposited"

    c=cs["MARKED-WEIGHT-CENSUS"]
    c["evidence"] += [cp+"regional-west/numerical-compatibility.json"]
    c["established"]="The exploratory census has 69 coded Susa entries and 57 ratios; the catalogue audit also covers 938 Greater Indus entries, including 870 Dholavira records. The 1.921% symmetric variation duck group uses Sb 9340 at 3,067 g and six strokes, whose older mass/mark assertions conflict. The published 25:1:2 reconstruction for three other Susa objects requires 0.944619% minimum symmetric relative variation or 1.871560% loss-only tolerance. At the proposed coefficients, 25*(27.25/2)=340.625 g, against the recorded 334.25 g. The readable Girsu controls imply 8.253 and 8.310 g. These are conditional reconstructions of published proposals; creation dates and independent unit anchors remain absent."
    npath=cp+"regional-west/numerical-compatibility.json"
    bind(c["id"],"susa_25_1_2_minimum_symmetric_relative_tolerance",npath,"/susa_quarter_mina_hypothesis/minimum_symmetric_relative_tolerance/decimal")
    bind(c["id"],"susa_25_1_2_minimum_loss_only_relative_tolerance",npath,"/susa_quarter_mina_hypothesis/minimum_loss_only_relative_tolerance/decimal")
    bind(c["id"],"mass_from_25_half_units_g",npath,"/sb13677_expected_mass_from_sb17774_g/decimal")
    for i in [0,1]: bind(c["id"],f"girsu_implied_unit_{i+1}_g",npath,f"/girsu_readable_shekel_control/objects/{i}/implied_unit_g/decimal")
    c["provenance_notes"]=["The census groups were designed after seeing the catalogue masses. Its source report suggests a shared large unit for the ducks and other unit levels for broader groups; it does not conclude that all Susa groups use a single unit or reject every such interpretation.","The tight duck group depends on a disputed source assertion; source conflict rank 2 must be resolved before treating its coefficient of variation as physical standardization evidence. The 25:1:2 coefficients are attributed historical hypotheses."]
    c["novelty"] = dict(cs["SUSA-SOURCE-CENSUS"]["novelty"])
    c["related_candidates"]=["SUSA-SOURCE-CENSUS","GONUR-ALTYN-RECOVERY"]

    c=cs["STAMP-CONTACT-SIMULATION"]
    c["established"]="A displacement-controlled geometric visibility model calculates which invented line graphics survive flat-stamp contact with curved clay; it predicts no force or pressure. The reviewed exact-stroke-length endpoint has 4,320 primary configurations, with 8,748 original nuisance configurations. In the eight-slot frame, endpoint total variation is zero for centred or balanced intact pools and balanced break sides. Positive tilt gives 0.0289415 at one surviving graphic and 0.0308466 at three; balanced tilt with the left quarter removed gives 0.0098707 and 0.00748721. Effect sizes apply to the declared grid and weighting; no physical trial has been completed."
    c["evidence"] += [sh+"stamp-geometry/METHODS.md",sh+"stamp-geometry/reviewed/results.json",sh+"stamp-geometry/analytic-refinement/results.json",sh+"stamp-geometry/main/results.json"]
    bind(c["id"],"primary_configurations",sh+"stamp-geometry/reviewed/results.json","/primary_configurations")
    bind(c["id"],"nuisance_configurations",sh+"stamp-geometry/main/results.json","/nuisance_configurations")
    for m in [1,3]:
        for pool in ["centred_no_damage","balanced_tilt_no_damage","positive_tilt_no_damage","balanced_tilt_left_break","balanced_tilt_both_break_sides"]:
            bind(c["id"],f"eight_slot_min_{m}_{pool}_endpoint_tv",sh+"stamp-geometry/reviewed/results.json",f"/minimum_visible_graphics_pools/{m}/8/{pool}/left_right_endpoint_tv")
    c["provenance_notes"]=["All graphics are invented. Exact segment integration is a separate refinement of the preserved sampled endpoint, not a physical validation. Survival and endpoint probabilities depend on the declared geometry and pool weights."]
    c["venue_options_unverified"]=cs["KANMER-PENDANT-FRAME"]["venue_options_unverified"][:]

    c=cs["KHIPU-REPLICATION"]
    c["provenance_notes"]=["The analyst had seen the published targets before the protocol. This replicates the Khipu Field Guide's Puruchuco notebook; it is source-informed reproduction. Santa Valley research in SRC-09 concerns another khipu set."]
    c["novelty"]=dict(judgment="The Khipu Field Guide already replicates Puruchuco, and Urton/Brezine published its account hierarchy. The contribution is a documented rerun with grouping controls, not a first account match.",precedent_search="Direct replication sources identified; notebook and publication metadata located",sources=["SRC-33","SRC-34"])
    c["smallest_form"]="Replication appendix to a completed Andean research paper; no standalone teaching-note venue verified"

    for cid in ["COLLECTIVE-CONSERVATION","IDENTIFIABILITY-AND-OBSERVATION-DESIGN"]:
        c=cs[cid]
        c["numbers"]["headline_gate_pct"]=50
        c["numbers"]["primary_gate_pct"]=75
        c["numbers"]["primary_75_local_correct_wrong_ambiguous_rejected"]=[1,2,0,197]
        c["numbers"]["primary_75_pooled_correct_wrong_ambiguous_rejected"]=[1,0,0,199]
        c["provenance_notes"]=["The 133/9/58 to 190/1/9 gain in 200 four-swap worlds is at the secondary 50% support gate. At the primary 75% gate, local correct/wrong/ambiguous/rejected outcomes are 1/2/0/197 and pooled outcomes 1/0/0/199. Every world is generated; independently measured completeness is an assumption."]
        c["evidence_fields"]=["rows[71]", "rows[79]", "rows[87]", "rows[95]", "selected-case-arithmetic.json: independent count checks"]
        c["evidence"] += [sh+"khipu-control/conservation-check/main-v1/selected-case-arithmetic.json"]
        c["related_candidates"]=["COLLECTIVE-CONSERVATION" if cid.startswith("IDENT") else "IDENTIFIABILITY-AND-OBSERVATION-DESIGN"]
    cs["COLLECTIVE-CONSERVATION"]["established"]="In 200 synthetic four-swap worlds, the secondary 50% support gate changes correct/wrong/ambiguous outcomes from local 133/9/58 to complete-pool 190/1/9. At the primary 75% gate, outcomes are 1/2/0/197 rejected locally and 1/0/0/199 rejected with the pool. Three independent count checks reject the remaining wrong 50%-gate ray; pooled completeness and those counts are declared observation inputs."
    c=cs["IDENTIFIABILITY-AND-OBSERVATION-DESIGN"]
    c["established"]="The saved synthetic observation-design study distinguishes ratio constraints from an absolute count anchor. It reuses rank 15's secondary 50%-gate conservation run, and all nine wrong local rays fail one anchored count in the post-outcome validation exercise. A first unanchored count requires two checks. The separate vessel-capacity audit identifies only the product of numerical multiplier and litre unit from selected fit cases."
    c["evidence"] += [mpath]
    c["provenance_notes"].append("Observation-design choices were developed after seeing outcomes. The vessel-capacity claim is in the separate metrology audit, also included at rank 1; rank 18 is not a second independent conservation experiment.")

    c=cs["PERMUTATION-CALIBRATION"]
    c["status"]="Synthetic"
    c["provenance_notes"]=["All calibration corpora are synthetic. The 94.2%/1.0% agreement statistic is post-outcome development; the original nested statistic remains 4%/3%. Saved replay verification establishes computation under those specified models."]
    c["evidence"] += [sh+"null-calibration/main/results.json",sh+"null-calibration/noisy-faces/main/results.json",sh+"null-calibration/shared-quality/agreement-diagnostic/main/results.json"]
    c["evidence_fields"]=["main/results.json: rejection_counts", "noisy-faces/main/results.json: rejection_counts", "shared-quality/agreement-diagnostic/main/results.json: reference and exact-tail summaries"]
    c=cs["EXACT-FINITE-LAWS"]
    c["established"]="The saved finite examples enumerate 8,000 balanced binary tables and 2,880 uniqueness-conditioned tables. A deduplication example starts with seven draws and retains six unique balanced strings with unequal selected-law support masses. Integer continuation counting supplies an exact law under unequal copy constraints; prospective applicability depends on a justified acquisition process."
    c["novelty"]=dict(judgment="No close finite-law literature comparison was completed. The cited Indus n-gram paper is removed; exact examples are ready as a methods appendix or software documentation, with standalone novelty unchecked.",precedent_search="Not done for exact sampling-law precedents",sources=[])
    c["evidence_fields"]=["unequal-copy-counts/results.json: legal completions", "dedup-selection/results.json: support masses", "papers/002-conditional-reference-laws/methods.md: finite examples"]

    c=cs["PROVENANCE-VERIFICATION-TOOLS"]
    c["established"]="The historical manifest lists 1,568 file hashes; saved root verification summaries report 23 root and eight methods checks. This package confirms the manifest count and saved summaries, without rerunning every hash or establishing independence of the verifier authors. These tools support source/version preservation and audit navigation."
    c["provenance_notes"]=["The count of hashes is not a fresh verification that every source file still matches. Verification reports and manifests have different roles; some source witnesses are local-only."]
    c["remaining_work"]="At least six months of public development history after any user-authorized release, plus reusable software packaging, licensing and documented research use for JOSS. The present private repository is not eligible for immediate submission."

    c=cs["ACQUISITION-FAILURE-REGISTER"]
    c["title"]="Source acquisition failures and unresolved object locators"
    c["evidence"] += [sh+"tell-jokha-contact/README.md",sh+"tell-jokha-contact/observations.json",sh+"tell-jokha-contact/access-log.json"]
    c["established"]="Saved logs document failed downloads and source-recovery routes; no normalized project-wide failure count is claimed. The Tell Jokha lead reaches a Frenez 2023 reproduced photograph and the original report locator p.59, Figure 6.61, while registration, material, surface-find record and dating basis remain unverified. These are acquisition outcomes and locators."
    c["evidence_fields"]=["primary-source-search.json: acquisition outcomes", "tell-jokha-contact/observations.json: source locator", "tell-jokha-contact/access-log.json: access attempts"]
    c["provenance_notes"]=["COMM-02 supports the Tell Jokha locator subsection; it does not support all failure logs. No person was contacted and no restricted account was created."]
    c["smallest_form"]="Source-recovery appendix; standalone publication not recommended"

    c=cs["REFERENCE-MAPPING-SIMULATION"]
    c["provenance_notes"]=["Every mapping world is generated. The latent-generator identification endpoint is post-outcome development. NUM-02 covers the sibling graph-mapping optimizer rather than the selector's 309/384 result."]
    c["evidence"] += [sh+"graph-mapping/main/results.json",sh+"graph-mapping/FINDINGS.md"]
    c["smallest_form"]="Synthetic benchmark appendix or statistical software documentation"

    c=cs["STRUCTURAL-PREDICTION-METHODS"]
    c["status"]="Exploratory"
    c["evidence"] += ["research/methods/results/gap_design_matched/gap_design_matched.json"]
    c["evidence_fields"]=["gap_design_matched.json: exact estimator and constant-one accuracy", "nested_results.json: unique-text gain", "benchmark.json: mask count and top-one accuracy"]
    c["provenance_notes"]=["This registry bundle includes frozen, failed, synthetic, exploratory and superseded endpoints; legacy labels are retained per entry. The 46.30% gap-count score is the design-matched endpoint, not the earlier unmatched 43.05% score. The failed comparison remains beside the 51.07% constant-one baseline."]
    c["smallest_form"]="Conference research paper with grouped prediction controls and a retained negative gap comparison"
    c["evidence_fields"]=["design_matched_models.local.exact_count_accuracy", "design_matched_models.local.constant_one_glyph_design_control_accuracy", "nested_results.json: exact gain field retained in the contribution assessment", "benchmark.json: mask count and top-one accuracy"]

    def add(rank,cid,title,field,established,numbers,evidence,fields,status,missing,form,effort):
        c=dict(rank=rank,id=cid,title=title,field=field,audience=field+" researchers and data curators",established=established,numbers=numbers,evidence=evidence,evidence_fields=fields,status=status,assessment_status="Exploratory",novelty=dict(judgment="Exact-result publication priority has not been checked; useful source-audit evidence is retained.",precedent_search="Not done for the exact result",sources=[]),missing_validation=missing,smallest_form=form,venues=[],venue_sources=[],remaining_work=effort,registry_ids=[],provenance_notes=[],related_candidates=[],venue_options_unverified=[])
        cs[cid]=c;inv["candidates"].append(c)
        return c

    c=add(24,"CISI1-SCAN-AND-ERRATA","CISI Volume 1 scan duplication and counting conventions","Digital archaeology; library digitization", "The IGNCA-hosted CISI1 PDF has 862 pages. All embedded page-image lists on pages 1–431 equal those on pages 432–862: 431 duplicate groups at offset 431. Printed p.375 also carries catalogue corrigenda, including deletion of H266–H275 and relabelling H356A/B/C as H354A/B/C bis. Those printed corrigenda are prior editorial corrections; the project contribution is the scan-identity audit and explicit counting-unit notes.",{},["research/literature/cisi1_page_image_audit.json","research/literature/cisi1_counting_and_errata.md"],["pages", "duplicate_groups", "cisi1_counting_and_errata.md: Exact scan repetition; Primary counting conventions"],"Verified computation","Recheck current host file hashes; curator/editor review before any erratum request.","Host correction request or corpus-note appendix","One to three days for exact-file check and a concise curator draft")
    bind(c["id"],"scan_pages","research/literature/cisi1_page_image_audit.json","/pages",value=862,transform="length")
    bind(c["id"],"duplicate_groups","research/literature/cisi1_page_image_audit.json","/duplicate_groups",value=431,transform="length")
    c["numbers"]["duplicate_offset"]=431
    c["provenance_notes"]=["This is equality of embedded image lists for one acquired PDF, not evidence for more archaeological objects. Existing book corrigenda are cited rather than claimed as new discoveries."]

    c=add(25,"CROSS-CATALOGUE-JOIN-AUDIT","Version joins and source-plate compatibility across derivative catalogues","Digital epigraphy; archaeological data quality","Among 2,375 older-export rows carrying a CISI reference, 2,374 find a Lipi object, 2,243 match some face exactly and 2,293 after eroded 000 is ignored. All 179 Mayig objects find a Lipi identity. A qualitative AI plate audit finds 17 compatible and seven discrepant objects among 24 source-complete cases. The earlier export and Lipi share a maintainer: their agreement measures version stability. Any-face matches leave side identity unresolved; the plate judgments need expert review.",{},["research/corpus/CORPUS_REPORT.md","data/normalized/crosscorpus_summary.json","research/corpus/plate_audit/adjudications.json","research/corpus/plate_audit/README.md"],["old_to_lipi_cisi_join", "mayig_to_lipi_cisi_join", "adjudications.json: sample; rows"],"Exploratory","Expert plate adjudication, exact-side joins, and rights review for any deposited rows.","Data paper about a deposited join/disagreement dataset","Two to four weeks for side-level review and a releaseable aggregate/register")
    for k,p in [("older_rows_with_CISI","/old_to_lipi_cisi_join/has_nonempty_cisi"),("older_rows_joined","/old_to_lipi_cisi_join/cisi_found"),("older_exact_any_face","/old_to_lipi_cisi_join/exact_sequence_match_any_face"),("older_compatible_ignoring_000","/old_to_lipi_cisi_join/match_after_ignoring_eroded_000"),("mayig_joined","/mayig_to_lipi_cisi_join/cisi_found")]: bind(c["id"],k,"data/normalized/crosscorpus_summary.json",p)
    c["numbers"].update(source_complete_plate_objects=24,plate_compatible=17,plate_discrepant=7)
    c["provenance_notes"]=["Only aggregate results are copied here; source rows and images remain local. Mayig is another annotation of shared photographs, not an independent excavation corpus."]

    c=add(26,"DATASET-LANDSCAPE","Completed October 2 dataset and rights landscape","Digital archaeology; data stewardship","The completed October 2 comparison covers 18 resources and reports 39 passing local count/missingness checks. Its historical CAA 2023 ICIT witness gives 4,665 objects, 5,650 texts, 17,966 legible sign occurrences and 16,015 images. These are dated source counts; no current census or new integrated corpus is established. The source comparison distinguishes reuse rights and count denominators, and proposes a 200-object pilot.",{},["experiments/2026-10-02-dataset-landscape/README.md","experiments/2026-10-02-dataset-landscape/landscape.json","experiments/2026-10-02-dataset-landscape/main-v1/local-input-audit.json","experiments/2026-10-02-dataset-landscape/verification-v1.json"],["sources", "sources[0].counts", "checks", "all_checks_passed"],"Verified computation","Update resource-by-resource terms, obtain current ICIT export if available, and implement the proposed common object register.","Data paper only after depositing a reusable bibliographic/rights register","One to three weeks for dated metadata verification; substantially longer for a new integrated corpus")
    lpath="experiments/2026-10-02-dataset-landscape/landscape.json"
    bind(c["id"],"resources",lpath,"/sources",transform="length")
    bind(c["id"],"passing_checks","experiments/2026-10-02-dataset-landscape/main-v1/local-input-audit.json","/checks",transform="length")
    for k in ["objects","texts","legible_sign_occurrences","photos_and_drawings"]: bind(c["id"],"ICIT_2023_"+k,lpath,"/sources/0/counts/"+k)
    c["provenance_notes"]=["Historical ICIT figures were visually checked in the earlier study at CAA 2023 abstract 76, page 281; this correction reads the preserved aggregate. The current resource internals and broad image rights were not audited."]
    c["novelty"]=dict(judgment="ICIT, CISI and the Helsinki editions are established predecessors. The contribution is a dated resource/rights comparison; no claim that an integrated corpus is absent or that the local collection is superior is supported.",precedent_search="Completed in saved October 2 landscape; no new exhaustive resource sweep",sources=["SRC-29","SRC-35","SRC-36"])

    # Explicit source checks for the main corrected values and new aggregate records.
    bind("CHART-687","post_comparison_lower_code_ambiguities","research/corpus/primary/chart_complete/consolidated_atlas_audit.json","/ambiguous_lower_code_cells",value=16)
    for key, pointer, expected in [("rows","/counts/rows",5680),("numeric_families","/counts/families",4695),("joint_context_rows","/joint_availability/site_area_excavation_depth_room_any_chronology/rows",1444),("joint_context_families","/joint_availability/site_area_excavation_depth_room_any_chronology/families_any_face",1163)]:
        bind("CONTEXT-COMPLETENESS",key,sh+"context-audit/main/results.json",pointer,value=expected)
    for key,pointer,expected in [("objects","/objects",93),("table_impressions","/source_impressions",133),("joined_objects","/joined_objects",68),("eligible_joined_objects","/principal_objects",29),("eligible_string_groups","/distinct_complete_strings",9)]:
        bind("LOTHAL-OBSERVATION-FRAME",key,sh+"lothal-physical-use/independent-review/main-refined/results.json",pointer,value=expected)
    for key,pointer,expected in [("source_complete_plate_objects","/sample/lipi_complete_single_line",24),("plate_compatible","/sample/all_token_candidate_compatible",17),("plate_discrepant","/sample/complete_candidate_incompatible",7)]:
        bind("CROSS-CATALOGUE-JOIN-AUDIT",key,"research/corpus/plate_audit/adjudications.json",pointer,value=expected)
    for key,pointer,expected in [("gap_estimator_pct","/design_matched_models/local/exact_count_accuracy",46.30),("constant_one_pct","/design_matched_models/local/constant_one_glyph_design_control_accuracy",51.07)]:
        bind("STRUCTURAL-PREDICTION-METHODS",key,"research/methods/results/gap_design_matched/gap_design_matched.json",pointer,value=expected,transform="percent_round_2")
    for cid in ["COLLECTIVE-CONSERVATION","IDENTIFIABILITY-AND-OBSERVATION-DESIGN"]:
        cs[cid]["evidence_fields"]=[sh+"khipu-control/conservation-check/main-v1/aggregate.json#/rows/71",sh+"khipu-control/conservation-check/main-v1/aggregate.json#/rows/79",sh+"khipu-control/conservation-check/main-v1/aggregate.json#/rows/87",sh+"khipu-control/conservation-check/main-v1/aggregate.json#/rows/95",sh+"khipu-control/conservation-check/main-v1/selected-case-arithmetic.json#/checks"]
    cs["PERMUTATION-CALIBRATION"]["evidence_fields"]=[sh+"null-calibration/main/results.json#/aggregate",sh+"null-calibration/noisy-faces/main/results.json#/aggregate",sh+"null-calibration/shared-quality/agreement-diagnostic/main/results.json#/aggregate",sh+"null-calibration/shared-quality/agreement-diagnostic/main/results.json#/exact_aggregate"]
    cs["EXACT-FINITE-LAWS"]["evidence_fields"]=[sh+"null-calibration/unequal-copy-counts/results.json#/legal_columns",sh+"null-calibration/unequal-copy-counts/results.json#/both_margin_three_column_tables",sh+"null-calibration/dedup-selection/results.json#/raw_draws",sh+"null-calibration/dedup-selection/results.json#/retained_distinct_strings",sh+"null-calibration/dedup-selection/results.json#/supports"]
    cs["SUSA-SOURCE-CENSUS"]["evidence_fields"]=[cp+"regional-west/marked-weight-census-v2.json#/marked_entry_count",cp+"regional-west/marked-weight-census-v2.json#/complete_single_graphic_entry_count",sr+"susa/mass-source-audit.json#/comparisons/2/earlier_mass_g",sr+"susa/mass-source-audit.json#/comparisons/2/later_mass_g",sr+"susa/mass-source-audit.json#/comparisons/2/identity_scope"]
    cs["GONUR-ALTYN-RECOVERY"]["evidence_fields"]=[sr+"oxus/results-v2.json#/checks",sr+"oxus/observations.json: saved AI panel readings"]
    cs["CATALOGUE-CROSSCHECKS"]["evidence_fields"]=[sh+"lothal-physical-use/independent-review/source-assertions.json: table and prose assertions",cp+"south-india/aggregate-v1/results.json#/cross_route_cells_differing",cp+"south-india/aggregate-v1/results.json#/site_route_occurrence_total",cp+"south-india/aggregate-v1/results.json#/family_route_occurrence_total",cp+"south-india/stroke-membership-v2/results.json#/printed_source_checks/2",sr+"oxus/results-v2.json#/checks"]
    cs["KANMER-PENDANT-FRAME"]["evidence_fields"]=[sh+"kanmer-physical-use/main/results.json#/core_field_coverage",sh+"kanmer-physical-use/main/results.json#/nominal_core_dimensions_mm",sh+"kanmer-physical-use/main/results.json#/nominal_core_mass_g"]
    cs["KHIPU-REPLICATION"]["evidence_fields"]=[sh+"khipu-control/source-aggregate.json#/published_alignment_scores",sh+"khipu-control/source-aggregate.json#/column_denominator",sh+"khipu-control/source-aggregate.json#/methods",sh+"khipu-control/REPORT.md: numerical replication table"]
    cs["CHART-687"]["evidence_fields"]=["research/corpus/primary/chart_complete/consolidated_atlas_audit.json#/frame_cells","research/corpus/primary/chart_complete/consolidated_atlas_audit.json#/ambiguous_lower_code_cells","research/corpus/primary/chart_complete/consolidated_atlas_audit.json#/atlas_images_checked","research/chart_reference/fresh20_before_correction.json#/joint_agreement","research/chart_reference/fresh20_before_correction.json#/rank_agreement","research/chart_reference/fresh20_before_correction.json#/code_agreement"]

    # Correct primary bookkeeping; multi-topic entries also have explicit cross-links.
    owners={i["registry_id"]:i["candidate_id"] for i in inv["registry_coverage"]["items"]}
    for n in [2,5,7,8,10,11]: owners[f"NULL-{n:02d}"]="PERMUTATION-CALIBRATION"
    for n in [1,3,4,6,9]: owners[f"NULL-{n:02d}"]="EXACT-FINITE-LAWS"
    owners.update({"CONTEXT-01":"CONTEXT-COMPLETENESS","ARCH-02":"LOTHAL-OBSERVATION-FRAME","NUM-02":"REFERENCE-MAPPING-SIMULATION","DATASET-LANDSCAPE-01":"DATASET-LANDSCAPE","REGIONNUM-01":"MARKED-WEIGHT-CENSUS","ROOT-19":"CISI1-SCAN-AND-ERRATA","COMM-02":"ACQUISITION-FAILURE-REGISTER"})
    registry=read("knowledge/experiments/registry.json")
    entries={e["id"]:e for e in registry["experiments"]}
    for item in inv["registry_coverage"]["items"]:
        item["candidate_id"]=owners[item["registry_id"]]
        item["original_status"]=entries[item["registry_id"]]["status"]
        item["role"]="Primary checklist home; inspect original evidence and status for each endpoint"
    for c in cs.values():
        c["registry_ids"]=[k for k,v in owners.items() if v==c["id"]]
        c["original_registry_statuses"]={k:entries[k]["status"] for k in c["registry_ids"]}
        c.setdefault("ranking_eligible",True)
        if not c["evidence_fields"]:
            c["evidence_fields"]=[p+": saved report/result summary; exact field-level binding not reconstructed in this correction" for p in c["evidence"] if p.endswith(".md")]
    cs["IDENTIFIABILITY-AND-OBSERVATION-DESIGN"]["related_registry_ids"]=["KHI-04"]
    cs["GONUR-ALTYN-RECOVERY"]["related_registry_ids"]=["REGIONNUM-01"]
    cs["SUSA-SOURCE-CENSUS"]["related_registry_ids"]=["REGIONNUM-01"]
    inv["registry_coverage"]["statement"]="Every registered ID has one primary checklist home; original statuses are retained. REGIONNUM-01 also supports ranks 2 and 11, and KHI-04 supports rank 18; related_registry_ids record those cross-links without duplicating primary ownership. Rank 6 is held and contains no evidence-census result."
    inv["registry_coverage"]["mapped_candidates"]=sum(bool(c["registry_ids"]) for c in cs.values())
    inv["registry_coverage"]["registry_entries"]=len(owners)

    # Match declared forms only to article types confirmed on an opened venue page.
    for c in cs.values():
        c["venues"]=[]; c["venue_sources"]=[]
    data_ids=["SUSA-SOURCE-CENSUS","CATALOGUE-CROSSCHECKS","CONTEXT-COMPLETENESS","CHART-687","HARAPPA-FRAME","LOTHAL-OBSERVATION-FRAME","SOUTH-INDIA-STROKE-POPULATION","CROSS-CATALOGUE-JOIN-AUDIT","DATASET-LANDSCAPE"]
    for cid in data_ids:
        cs[cid]["venues"]=["Internet Archaeology: data paper, conditional on a reusable licensed dataset deposit", "Journal of Open Archaeology Data: data paper, conditional on an openly archived dataset"]
        cs[cid]["venue_sources"]=["SRC-02","SRC-05"]
    cs["MARKED-WEIGHT-CENSUS"]["venues"]=["Iran: shorter notice concerning Susa; separate Greater Indus material would need another venue"]
    cs["MARKED-WEIGHT-CENSUS"]["venue_sources"]=["SRC-23"]
    for cid in ["PERMUTATION-CALIBRATION","EXACT-FINITE-LAWS"]:
        cs[cid]["venues"]=["Journal of Statistical Software: software article, conditional on a reusable GPL-compatible package and article"]
        cs[cid]["venue_sources"]=["SRC-20"]
    cs["PROVENANCE-VERIFICATION-TOOLS"]["venues"]=["Journal of Open Source Software: software paper only after open-source licensing, research use and at least six months of public development history"]
    cs["PROVENANCE-VERIFICATION-TOOLS"]["venue_sources"]=["SRC-17"]
    cs["STRUCTURAL-PREDICTION-METHODS"]["venues"]=["International Conference on Natural Language Processing for the Digital Humanities (NLP4DH): research paper; confirm the next call's format"]
    cs["STRUCTURAL-PREDICTION-METHODS"]["venue_sources"]=["SRC-16"]
    for cid in ["KANMER-PENDANT-FRAME","STAMP-CONTACT-SIMULATION","KHIPU-REPLICATION","COLLECTIVE-CONSERVATION","IDENTIFIABILITY-AND-OBSERVATION-DESIGN","FONT-OCR-FAILURE","REFERENCE-MAPPING-SIMULATION"]:
        cs[cid]["venue_fit_limit"]="No presently verified standalone article-type fit. Develop the specified experiment, substantive research paper or appendix before selecting a venue."
    cs["PERMUTATION-CALIBRATION"]["venue_options_unverified"]=["Journal of Computational and Graphical Statistics: relevant methods scope, but publisher page not opened in this revision."]
    inv["date"]="2026-10-07"
    inv["revision"]="Coordinator corrections after Sonnet review; first pass retained"
    inv["ranking_criteria"]=["Subject-specific plausible contribution after recorded precedents", "Readiness of saved evidence and source witnesses", "Usefulness to a named field audience", "Remaining external validation and deposit requirements"]
    inv["ranking_limit"]="Ranks 1–23 are stable first-pass reference positions after correction, with rank 6 held; records 24–26 are additions. Use the report's field-specific priority statements. The original ordinal ordering has not been recomputed as a score ranking."
    priority=["CHART-687","CONTEXT-COMPLETENESS","CISI1-SCAN-AND-ERRATA","FULS-ARITHMETIC","CROSS-CATALOGUE-JOIN-AUDIT","CATALOGUE-CROSSCHECKS","SUSA-SOURCE-CENSUS","HARAPPA-FRAME","DATASET-LANDSCAPE","LOTHAL-OBSERVATION-FRAME","MARKED-WEIGHT-CENSUS","SOUTH-INDIA-STROKE-POPULATION","GONUR-ALTYN-RECOVERY","FONT-OCR-FAILURE","STAMP-CONTACT-SIMULATION","KHIPU-REPLICATION","PERMUTATION-CALIBRATION","EXACT-FINITE-LAWS","KANMER-PENDANT-FRAME","IDENTIFIABILITY-AND-OBSERVATION-DESIGN","COLLECTIVE-CONSERVATION","STRUCTURAL-PREDICTION-METHODS","PROVENANCE-VERIFICATION-TOOLS","REFERENCE-MAPPING-SIMULATION","ACQUISITION-FAILURE-REGISTER"]
    inv["recommended_priority_order"]=priority
    for position,cid in enumerate(priority,1): cs[cid]["priority_position"]=position
    cs["PUBLIC-INDEX-COVERAGE"]["priority_position"]=None
    inv["priority_basis"]="Qualitative post-review order for the smallest credible deliverable, balancing recorded precedent, readiness, field use and remaining work. Stable rank numbers preserve review references; priority_position is the amended recommendation. No numerical score or novelty-priority certification is claimed."
    cs["FULS-ARITHMETIC"]["primary_sources"]=["SRC-18","SRC-32"]
    cs["FULS-ARITHMETIC"]["novelty"]["sources"]=[]
    for cid in ["SUSA-SOURCE-CENSUS","MARKED-WEIGHT-CENSUS"]:
        cs[cid]["primary_sources"]=["SRC-06"]
        cs[cid]["novelty"]["sources"]=["SRC-25","SRC-26"]
    for c in cs.values():
        c["novelty"]["sources"]=["SRC-02" if sid=="SRC-14" else sid for sid in c["novelty"]["sources"]]
    inv["search_boundary"]="On-subject correction searches are logged locally; partly checked means the exact priority claim remains unresolved. Failed opens and full-text/metadata differences are recorded."
    inv["correction_claim_checks"]=checks

    # Bibliographic corrections and explicit opening provenance.
    ss={s["id"]:s for s in src["sources"]}
    ss["SRC-03"].update(title="Extracting the social relevance of artefact distribution in Roman military forts",authors=["Penelope M. Allison","Andrew S. Fairbairn","Steven J.R. Ellis","Christopher W. Blackall"],venue="Internet Archaeology 17; section 7.1",opened=True,access="Section 7.1 reopened in this correction; article metadata confirmed by the journal table of contents search result.")
    ss["SRC-04"]["authors"]=[a.replace("Jan Kol??","Jan Kol\u00e1\u0159").replace("Jelena Bulatovi?","Jelena Bulatovi\u0107") for a in ss["SRC-04"]["authors"]]
    ss["SRC-06"]["title"]=ss["SRC-06"]["title"].replace("Iran and Greater","Iran & Greater")
    ss["SRC-06"]["rights_note"]="Review opened the archive.org record and found CC BY-ND 4.0; transformed catalogue payloads still need an asset-specific reuse assessment."
    ss["SRC-07"].update(authors=["Meredith Laing"],venue="Oxford Journal of Archaeology 41(4):350–372",access="First pass reported an article opening; Sonnet review verified corrected author and citation in Crossref. This revision found matching author/title metadata in a search result and did not reopen the full article.")
    ss["SRC-09"].update(opened=True,access="arXiv abstract reopened in this correction; it concerns Santa Valley khipus, not the Puruchuco replication.")
    ss["SRC-10"].update(authors=["Nisha Yadav","Hrishikesh Joglekar","Rajesh P.N. Rao","Mayank N. Vahia","Ronojoy Adhikari","Iravatham Mahadevan"],access="Originally opened in the October 6 contribution assessment; reopened on the PLOS publisher page in this correction.")
    ss["SRC-12"]["access"]="Abstract opened in the earlier October 6 contribution assessment and by the Sonnet reviewer; not reopened in this correction."
    ss["SRC-18"].update(venue="Studies on Indus Script, National Fund for Mohenjodaro, 2020, pp.57–90; author-posted reprint pp.15–48",access="Earlier project audit used indexed primary PDF text; the Sonnet reviewer encountered 403. This correction successfully reopened the 34-page indexed author PDF and inspected text at printed pp.29–32. No new source-figure authentication is claimed.")
    ss["SRC-24"]["venue"]="International Journal of Statistics in Medical Research 3(2):145–152"
    ss["SRC-05"].update(url="https://openarchaeologydata.metajnl.com/",opened=True,access="Official journal homepage opened in this correction; it states the data-paper and archived-open-data format. The attempted /about route timed out.")
    for sid in ["SRC-02","SRC-15","SRC-16","SRC-17","SRC-20","SRC-23"]:
        ss[sid]["opened"]=True
        ss[sid]["access"]="Official venue page opened in this correction; relevant article-type and eligibility rules are summarized in REPORT.md."
    ss["SRC-15"]["url"]="https://academic.oup.com/dsh/pages/About"
    ss["SRC-16"].update(title="Proceedings of the 6th International Conference on Natural Language Processing for the Digital Humanities",url="https://aclanthology.org/events/nlp4dh-2026/",venue="NLP4DH 2026; conference proceedings")
    ss["SRC-19"]["access"]="Official journal and contributor pages timed out in this correction. Search result shows experimental archaeology scope and a restriction on AI-generated ideas. It is retained as an unverified venue option, not a presently recommended submission."
    ss.pop("SRC-14")
    for s in ss.values():
        s["opened_in_this_revision"]=s["id"] in ["SRC-02","SRC-03","SRC-05","SRC-09","SRC-10","SRC-15","SRC-16","SRC-17","SRC-18","SRC-20","SRC-23"]
        s["opened_scope"]= "Earlier project or review plus current opening" if s["opened_in_this_revision"] else "Earlier project/review or snippet only; see access"

    def source(sid,title,authors,year,venue,url,opened,access,relevance):
        ss[sid]=dict(id=sid,title=title,authors=authors,year=year,venue=venue,url=url,opened=opened,opened_in_this_revision=opened,access=access,relevance=relevance)
    source("SRC-25","\u00c9tude des monuments pond\u00e9raux de Suze",["Michel C. Soutzo"],1911,"M\u00e9moires de la D\u00e9l\u00e9gation en Perse 12","https://archive.org/download/mmoires12franuoft/mmoires12franuoft.pdf",True,"Preserved local primary text inspected at no.14201/no.6327 and the concluding mina discussion; the archive record could not be opened by the web tool. BnF search metadata confirms title/year.","Soutzo already interprets marks as multiples of a weight unit; antecedent to any mass-per-mark census claim.")
    source("SRC-26","Typological and Quantitative Approach to the Ancient Weight Systems. Susa, Persian Gulf and Indus Valley from the End of the III Mill. to the Beginning of the II Mill. BC",["Enrico Ascalone","Luca Peyronel"],1999,"Altorientalische Forschungen 26(2):352–376; one institutional record gives 352–377","https://doi.org/10.1524/aofo.1999.26.2.352",False,"Institutional search records found; both Milan and Rome page openings returned 403. Full article not inspected, and the final page is inconsistent between metadata records.","Direct subject precedent for Susa/Gulf/Indus weight-system analysis.")
    source("SRC-27","Le Cretule di Lothal: Documenti amministrativi da un sito della Civilt\u00e0 dell’Indo ai confini orientali del Mare Arabico",["Dennys Frenez"],2005,"MA thesis, University of Bologna","https://www.unibo.it/it/ateneo/amministrazione-trasparente/consulenti-e-collaboratori/tabella-incarichi-scaduti/2024?format=cv&id=42247",False,"Author's 2024 institutional CV opened, p.1, confirms title and degree. Thesis full text was not located in this correction's web searches; a Zenodo API search returned HTTP400. The Sonnet review reports a Zenodo thesis opening, but supplies no exact record URL.","Earlier Lothal ledger requiring inspection before discrepancy or frame priority is claimed.")
    ss["SRC-27"]["metadata_opened"]=True
    source("SRC-28","Lothal Sealings: Records from an Indus Civilization town at the eastern end of the maritime trade networks across the Arabian Sea",["Dennys Frenez","Maurizio Tosi"],2005,"Studi in Onore di Enrica Fiandra. Contributi di archeologia egea e vicinorientale, pp.65–103; De Boccard","https://zenodo.org/records/5514283",True,"Zenodo chapter record opened; full chapter not newly read here. Saved source-table analyses already transcribe the chapter.","Primary prior Lothal sealing frame; scope and authors confirmed.")
    source("SRC-29","Documentation of the Online Indus Writing Database",["Andreas Fuls"],2010,"ICIT official documentation, 16-page PDF","https://www.epigraphica.de/indus/help_onlinedatabase.pdf",True,"Official PDF opened. Section Time, PDF p.7, describes unassigned chronology; Mapping the Frequency, pp.8–9, describes site/archaeological-project imbalance.","Indus-specific precedent for metadata completeness and geographic distribution limits.")
    source("SRC-30","Indus Signs and Graffiti Marks of Tamil Nadu: A Morphological Study",["K. Rajan","R. Sivanantham"],2025,"Government of Tamil Nadu, Department of Archaeology","https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2025/08/TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study.pdf",False,"Official library PDF title-page search result found; official portal search result links the book and gives project provenance. Portal opened with no extractable text. Book and later print-volume concordance not read in this correction.","Edition and implementation reconciliation required before treating the 4.19C difference as an error.")
    source("SRC-31","On the use of tokens and seals along the Kopet Dagh piedmont, Turkmenistan (ca 6000-3000 BCE)",["Gian Luca Bonora","Massimo Vidale","Maurizio Mariottini","Giuseppe Guida"],2014,"Pal\u00e9orient 40(1):55–71","https://www.persee.fr/doc/paleo_0153-9345_2014_num_40_1_5616",True,"Pers\u00e9e article record opened; indexed author text located in search. Its regional token discussion is prior scholarship; the exact Gonur panel discrepancy was not resolved.","On-subject token precedent, not independent validation of the 26/23 comparison.")
    source("SRC-32","Indus writing: Publications using the ICIT",["Andreas Fuls"],"accessed 2026-10-07","Author's official bibliography","https://www.epigraphica.de/indus/menueindus.htm",True,"Official author page opened; it records the 2012 vessel-capacity chapter, 2020 numerical chapter and 2023 sign catalogue.","Confirms original publication venues and prior sign/corpus scholarship.")
    source("SRC-33","12 - Replicating Purucucho",["Khipu Field Guide notebook authors; individual attribution not verified"],"undated; accessed 2026-10-07","Khipu Field Guide, appendix notebook","https://www.khipufieldguide.com/notebook/appendix/index.html",False,"Official appendices search result identifies the replication notebook. The saved project protocol cites the notebook; current full notebook and author attribution not inspected.","Direct prior replication route for Puruchuco, distinct from Santa Valley.")
    source("SRC-34","Khipu accounting in ancient Peru",["Gary Urton","Carrie J. Brezine"],2005,"Science 309(5737):1065–1067","https://doi.org/10.1126/science.1113426",False,"PubMed search record provides title, authors, citation and abstract; full Science article not opened in this correction.","Published Puruchuco account-hierarchy precedent.")
    source("SRC-35","The Interactive Corpus of Indus Texts (ICIT) as an epigraphical database and online tool for Indus script research",["Andreas Fuls"],2023,"CAA 2023 abstract book, abstract 76, p.281","https://2023.caaconference.org/wp-content/uploads/sites/29/2023/04/abstract_book_v13.pdf#page=281",False,"Historical witness rendered and visually checked by the October 2 dataset-landscape study; this correction inspected its saved aggregate and found the conference abstract in web results.","Dated ICIT denominator and predecessor description, not current dataset coverage.")
    source("SRC-36","Corpus of Texts in the Indus Script",["Kimmo Koskenniemi","Asko Parpola"],1979,"Department of Asian and African Studies, University of Helsinki","https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/",False,"Official publication and CC BY 4.0 licence were inspected in the prior corpus/landscape studies and repository redistribution record; this correction uses those saved witnesses.","Chart source and recorded licence basis; existing printed sign chart predates the atlas.")
    old_log=load(RAW/"search-log.json")
    historical=list(dict.fromkeys(src["searches"]+old_log["queries"]))
    src["searches"]=historical
    src["search_reconciliation"]=dict(historical_distinct_queries=len(historical),historical_sources=["first-pass/sources.json","data/raw/2026-10-06-byproduct-inventory/search-log.json"],correction_log="data/raw/2026-10-06-byproduct-inventory/correction-web-log.json",limit="Historical strings reconciled literally; unknown ordering and unlogged historical failures cannot be reconstructed.")
    src["duplicate_source_aliases"]={"SRC-14":"SRC-02"}
    src["sources"]=list(ss.values())
    save(PACKAGE/"inventory.json",inv)
    save(PACKAGE/"sources.json",src)
    print(f"Corrected {len(cs)} candidates; {len(owners)} registry homes; {len(ss)} source records")


if __name__ == "__main__":
    main()
