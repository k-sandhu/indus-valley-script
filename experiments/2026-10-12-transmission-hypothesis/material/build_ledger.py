"""Build new source and observation ledgers; do not overwrite frozen endpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

RAW = Path("data/raw/2026-10-12-transmission-hypothesis/material")


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def w(rel, role="inspected primary witness"):
    p = RAW / rel
    return {"path": p.as_posix(), "sha256": digest(p), "bytes": p.stat().st_size,
            "role": role, "rights": "rights-unverified; local-only source witness or derivative"}


def s(sid, title, citation, year, url, lineage, scope, witnesses, notes):
    return {"source_id": sid, "title": title, "citation": citation, "publication_year": year,
            "url": url, "lineage": lineage, "reading_scope": scope, "witnesses": [w(*a) for a in witnesses],
            "notes": notes, "status": "included at declared reading depth"}


def sources():
    return [
        s("MS01", "Tubular drill hole", "Harappa Archaeological Research Project, author-hosted caption, Around the Indus in 90 Slides 2, slide 87.", None,
          "https://www.harappa.com/slide/tubular-drill-hole", "HARP 1996 Trench 38 bead-pot context",
          "Entire caption in acquired HTML; drilling, source-color and supply-loss interpretations separated. Photograph not independently examined.",
          [("acquisition-v1/harappa-tubular-drill.html", "author-hosted primary excavation caption")],
          "Publication date not established; 1996 is excavation. Caption's circa 1700 BCE is a context/phase attribution. Color alone is not geological provenance; raw material for specialized drills is unresolved."),
        s("MS02", "Single Bead Pot (Collection)", "Harappa.com, author-hosted excavation description and image-alt captions, accessed 12 October 2026.", None,
          "https://www.harappa.com/blog/single-bead-pot-collection", "HARP 1996 Trench 38 bead-pot context",
          "Entire prose and all unique substantive image-alt captions. Normal text extraction omitted alt captions; a separate derivative preserves them.",
          [("acquisition-v2/harappa-bead-collection.html", "primary excavation-description page"),
           ("html-caption-extract-v1/harappa-bead-collection.json", "source text plus unique image-alt attributes")],
          "The page identifies a curated collection containing material from all Harappan occupation phases. It shares the MS01 object context and is counterevidence to dating every object's manufacture by the pot's deposition."),
        s("MS03", "Excavations at Hulas (1978–1983) (From Harappan times to Early Medieval)",
          "K. N. Dikshit, with contributions by V. C. Sharma, Y. S. Rawat, K. K. Sharma, K. S. Saraswat and I. Mahadevan. Memoirs of the Archaeological Survey of India 113 (2020).", 2020,
          "https://asi.nic.in/pdf/EXCAVATIONS-AT-HULAS.pdf", "ASI Hulas 1978–1983 excavation and associated botanical sample",
          "PDF pp.1–2, 7, 83–84, 161–162, 207–209, 235–237, 244–247 and 255–256. Printed pp.71–72, 149–150, 195–197, 223–225, 232–235 and 243–244. Printed pp.72, 223, 232 visually checked. Not a full 258-page reading.",
          [("acquisition-v1/hulas-full.pdf", "official ASI report")],
          "2020 is the printed copyright year; online crawl date is not publication. Saraswat's appendix uses the 1978–79 sample and a typological circa 1700–1000 BCE bracket; the main chronology discusses much earlier uncalibrated dates and a separate PGW settlement area. Its old river/ethnic explanations are not adopted. The original 1993 Puratattva article was not acquired or counted independently."),
        s("MS04", "Excavation at Bhagwanpura 1975–76 and Other Explorations & Excavations 1975–81 in Haryana, Jammu & Kashmir and Punjab",
          "Jagat Pati Joshi, with Madhu Bala and scientific contributors. Memoirs of the Archaeological Survey of India 89 (1993), especially pp.17–30, 117–122, 185, 201 and B. N. Tandon's pottery study pp.209–215.", 1993,
          "https://ignca.gov.in/Asi_data/80282.pdf", "ASI Bhagwanpura 1975–1976 excavation and selected scientific specimens",
          "Cover and contents; PDF pp.38–42, 46–49, 52–56, 153–159, 231, 235, 247, 257–258, 261–264. Printed pp.17–21, 23–26, 27–31, 117–123, 185, 189, 201, 209–210 and 213–216. Key pp.27, 30, 120, 122, 185 and 213 visually checked; acquisition/OCR covers additional pages without claiming full reading.",
          [("acquisition-v1/bhagwanpura-full.pdf", "official report scan hosted by IGNCA")],
          "The 421-page scan includes plates. Pottery labels, reported cultural coexistence and proposed teaching are distinct. BPR-208 is called quartz on p.118 and banded agate on p.122, both unfinished from mid-IB; it is not counted as two independent objects. Bulk composition of twelve sherds lacks a geological source-control frame and precise phase assignment in the inspected analysis. TL errors, differing depth trends and a measurement-year BP baseline preclude converting its table into a precise teaching chronology."),
        s("MS05", "Sanghol Excavations 1987: Some New Evidences",
          "C. Margabandhu and G. S. Gaur. Puratattva 17 (nominal 1986–87; printed 1988): 1–4.", 1988,
          "https://ignca.gov.in/Asi_data/75639.pdf", "ASI and Punjab archaeology Sanghol 1986–1987 excavation",
          "Issue cover, imprint, contents and full article, PDF pp.10–13/printed pp.1–4. Printed p.3 visually checked.",
          [("acquisition-v1/sanghol1987.pdf", "whole issue scan; only named article inspected")],
          "1987 is fieldwork, 1986–87 the nominal issue and 1988 the imprint. The overlap at SGL-9 retains a PGW question mark and a levelling qualification. The proposed bead/terracotta factory belongs to the Kushana phase, not the Late Harappan domestic phase."),
        s("MS06", "Archaeobotanical data from a Baran settlement (4,300–3,400 yrs bp) in the Ghaggar basin (northwestern India) reveals continuity of the Indus crop package after the Meghalayan stage drought",
          "Mansi Swaroop, Shalini Sharma, Ruchita Yadav, Xiaoyan Yang, Guanghui Dong, Akinori Uesugi, Srinivas Bikkina, Alka Srivastava, Rahul Kumar and Anil K. Pokharia. Vegetation History and Archaeobotany, published 23 July 2026. DOI 10.1007/s00334-026-01140-4.", 2026,
          "https://doi.org/10.1007/s00334-026-01140-4", "Jognakhera YA1/IV botanical samples and three new grain dates",
          "Publisher metadata/abstract/rights; author PDF via web tool, zero-based pages 4–6 (one-based PDF pp.5–7), methods, results, Fig.3 caption and chronology. Publisher supplementary DOCX Tables S1–S3 read in original XML row order. Main PDF bytes were not acquired and no full-paper reading is claimed.",
          [("web-witness-v1/jognakhera-selected-loci.txt", "selected web-tool-converted PDF text; not original PDF bytes"),
           ("web-witness-v1/jognakhera-bibliography.txt", "publisher version/date and rights text via web tool"),
           ("acquisition-v3/jognakhera2026-supplement.docx", "publisher's original supplementary document")],
          "Added after candidate-family freeze within fixed C3. Normal publisher routes gave challenges and normal author-PDF acquisition returned 403; web inspection succeeded. Three direct crop dates improve chronology, while Table S2 gives site rather than individual sampled-layer codes for those dates. Summer/winter legumes do not alone identify same-plot rotation. River identity, migration and linguistic identity are not established by the sample. No crop-percentage or rice-domestication reanalysis was performed."),
        s("MS07", "Excavations at Harappa 2000–2001: New Insights on Chronology and City Organization",
          "Richard H. Meadow and Jonathan Mark Kenoyer. In C. Jarrige and V. Lefevre, eds., South Asian Archaeology 2001 (2005), cited pp.207–226; inspected scan has 19 pages.", 2005,
          "https://www.harappa.com/sites/default/files/pdf/Kenoyer2005_Excavations%20at%20Harappa%202000-2001%20New%20insights%20on.pdf", "HARP Harappa excavation programme",
          "PDF pp.1–3, 7, 9 and 18, printed pp.207–209, 213, 215 and 224. Printed p.209/Table2 and Ravi production context visually checked. Other OCR search hits were used for location, not coded as intermediate evidence.",
          [("acquisition-v2/kenoyer2005-harappa.pdf", "author-hosted primary field paper")],
          "The early Ravi production context is a recovery/association control, not a posturban intermediate. Period-5 age in Table2 dates its carbon context, not the manufacture of every bead-pot object. Terminal Late Harappa date remains unresolved. The bead-pot and earlier records share HARP ancestry."),
        s("MS08", "Harappa: New Discoveries on Its Origins and Growth",
          "Jonathan Mark Kenoyer and Richard H. Meadow. Lahore Museum Bulletin XI(1), January–June 1999, pp.1–11 in inspected scan.", 1999,
          "https://www.harappa.com/sites/default/files/pdf/Kenoyer1999_Harappa%20New%20Discoveries%20on%20its%20origins%20and%20growt.pdf", "HARP Harappa excavation programme",
          "Cover, title and chronology Table1, PDF pp.1–3/printed pp.1–2; OCR of all 12 pages for discovery only.",
          [("acquisition-v2/kenoyer1999-harappa.pdf", "author-hosted earlier primary field synthesis")],
          "Its open Late Harappa terminal bound differs from the later framework. Neither tabulation establishes an exact endpoint or dates a technical recipe. This is a chronology comparison, not an extra independent posturban workshop."),
    ]


def o(oid, sid, candidates, locus, unit, phase, kind, claim, author, inference, limits, operations=(), edges=(), dates=None):
    return {"observation_id": oid, "source_id": sid, "candidates": list(candidates), "locus": locus,
            "context": unit, "phase": phase, "observation_kind": kind, "source_observation": claim,
            "source_author_inference": author, "current_inference": inference, "limits_and_rivals": limits,
            "operations": list(operations), "ordered_relations": list(edges), "date_evidence": dates,
            "carrier_institution_observed": None, "teaching_relationship_observed": None,
            "language_or_ethnicity_identified": False, "diagnostic_cross_domain_join": False}


def observations():
    return [
        o("MO01", "MS01", ["C1"], "Entire caption, slide87", "Unfinished bead in Trench38 bead pot", "Source-assigned Late Harappan, circa1700BCE", "captioned artifact and technological interpretation", "An unfinished carnelian bead has a tubular perforation.", "Caption suggests later bead workshops and changed drilling technology.", "A working stage is represented on the object; mixed collection must constrain its manufacture attribution.", "Imported roughout, curated earlier unfinished object and local work all remain possible without associated waste/tools.", ["tubular_drilling"], dates={"kind":"caption_context_attribution","approximate_BCE":1700,"object_manufacture_date":"unresolved"}),
        o("MO02", "MS01", ["C1"], "Entire caption, slide87", "Same unfinished bead", "Same context as MO01", "source-author supply inference", "The caption describes unusual color and a different drilling form.", "Color is interpreted as a non-Gujarat source and drilling as response to lost specialized-stone supply.", "Separate a proposed supply explanation from observed form.", "Color can change with treatment; geological source, drill material and supply interruption were not directly established in the inspected caption.", ["material_selection"]),
        o("MO03", "MS02", ["C1"], "Prose and final unique substantive image-alt caption", "Trench38 small pot and its 133 decorative objects", "Pot assigned around1700BCE; contents from multiple phases", "curated collection", "The description says the pot's contents belong to all Harappan occupation phases.", "A bead collector retained diverse objects.", "Deposition of the collection cannot assign one manufacture date to each object.", "The same context as MO01–MO02 is not independent replication.", dates={"kind":"collection_deposition_attribution","approximate_BCE":1700,"contents_manufacture_dates":"mixed; unresolved by deposition"}),
        o("MO04", "MS07", ["C1"], "Printed p.209/PDF p.3, Table2 and adjacent chronology", "Period5 carbon sample H1999/9803[410]", "Harappa Period5", "source-reported physical date", "Table2 reports a Period5 calibrated range of 1880–1680BCE at its stated at-least90% probability scope.", "Cemetery H phase was established by approximately1700calBCE; terminal date remains poorly preserved.", "An intermediate settlement phase has dating support.", "The carbon context is not a direct bead-manufacture date or a verified association with the selected pot.", dates={"kind":"source_calibrated_context_date","range_cal_BCE":[1880,1680],"probability_scope":"at least90%, source Table2"}),
        o("MO05", "MS08", ["C1"], "Printed p.2/PDF p.3, Table1", "Harappa phase framework", "Period5", "chronology scope control", "The earlier framework leaves a terminal bound extending below1300BCE; the later framework and discussion leave the endpoint unresolved.", "Continuing chronological refinement.", "A phase table does not provide a fixed duration for technical transmission.", "MS07–MS08 share excavation ancestry and are not two confirmations of one date."),
        o("MO06", "MS03", ["C2"], "Printed p.72/PDF p.84", "Hulas PeriodI pottery", "PeriodI, Harappan-classified assemblage", "technological traces and reconstruction", "Striations, separate neck/body joining and trimming are described, with sand/lime/husk temper and surface finishing.", "Wheel forming, luting and finishing are reconstructed; firing method remains unclear.", "The report preserves a linked manufacture candidate beyond vessel names.", "Finished pots can travel; these generic operations do not identify maker ancestry or a local teaching chain.", ["clay_preparation","forming","joining","trimming","firing"], [{"before":"joining","after":"trimming","basis":"source technological reconstruction"}]),
        o("MO07", "MS03", ["C2","C3"], "AppendixIII pp.223–224 and232–233/PDF pp.235–236,244–245", "Hulas potsherds and burnt plaster carrying plant impressions", "Appendix Late Harappan attribution", "material impressions and temper interpretation", "Rice-husk impressions occur in potsherds and burnt mud-plaster pieces.", "Husk was used as clay temper and interpreted as an agricultural by-product.", "Candidate connection between plant handling and construction/craft material preparation.", "Deliberate addition, processing location and cultivation require controls against naturally included plant material, imported crops and wild collection.", ["plant_material_handling","clay_tempering"], [{"before":"plant_material_in_clay","after":"fired_clay_or_burnt_plaster","basis":"material inclusion; intention unresolved"}]),
        o("MO08", "MS03", ["C3"], "AppendixIII printed p.232/PDF p.244", "Rice impressions and cited clay-source alternative", "Hulas and comparative Harappan impressions", "identification and formation control", "The author discusses the difficulty separating wild/cultivated rice from impressions and the possibility of rice-bearing marsh clay.", "Hulas rice cultivation is favored in the subsequent argument.", "Presence of an impression does not decide cultivation or a transmission route.", "The marsh-clay discussion initially addresses comparative Gujarat cases; applying it to Hulas is a prospective formation control, not an excavated Hulas fact."),
        o("MO09", "MS03", ["C3"], "AppendixIII printed pp.223–224,234/PDF pp.235–236,246", "Botanical soil samples from one field season", "PeriodI sampled horizons", "recovery and preservation scope", "Visible remains and water separation through a25-mesh sieve recovered material around0.7mm; carbonization damaged identification. The study used one season's sample.", "Recognizable remains approximate part of plant use.", "Recovery, burning and aggregation constrain operation comparisons.", "No standardized yield, same-field rotation or independent-trial seed count is inferred."),
        o("MO10", "MS03", ["C2","C3"], "Printed pp.195–197 and223/PDF pp.207–209,235", "Hulas site and separately placed period areas", "PeriodI and later PGW", "internal chronology and spatial control", "The appendix's typological circa1700–1000BCE attribution differs from main discussion of much earlier uncalibrated dates; the later PGW occupation is in a different part of the mound.", "Authors offer different broad regional phase interpretations.", "Hulas is a source-reported intermediate candidate with unresolved precise dating and succession.", "Do not join phases into uninterrupted same-household learning or adopt the older river-event dating argument.", dates={"kind":"conflicting_source_assignments","appendix_typology_BCE":[1700,1000],"main_uncalibrated_BCE":["2560±155","2005±115"],"resolution":"unresolved; no harmonized age fit"}),
        o("MO11", "MS03", ["C3"], "AppendixIII printed p.234/PDF p.246", "Hulas walnut and almond remains", "Sampled PeriodI deposits", "source botanical record and ecological interpretation", "Walnut and almond remains are described.", "Ecological distribution is used to propose distant supply.", "Imported food is a plausible component of the assemblage.", "A food taxon's presence does not locate the knowledge or field that produced it; trade route and elite status are not independently observed."),
        o("MO12", "MS04", ["C1"], "Printed p.120/PDF p.156, Fig35 item17", "BPR-36 from a late level of Sub-periodIB", "Sub-periodIB", "catalogued unfinished working stage", "The catalogue identifies a roughly faceted unfinished black-jasper bead.", "Unfinished beads and raw material support proposed bead making at the site.", "The later assemblage contains a source-qualified working-stage object rather than only completed ornaments.", "Imported/curated roughouts and movement of craftspeople remain rivals; associated waste/tools and exact date are not supplied here.", ["rough_facet_shaping"], dates={"kind":"stratigraphic_cultural_assignment","subperiod":"IB late level","direct_object_date":None}),
        o("MO13", "MS04", ["C1"], "Printed pp.118,122/PDF pp.154,158", "BPR-208, mid-level Sub-periodIB", "Sub-periodIB", "unfinished object with catalogue collision", "BPR-208 is described as unfinished quartz in one list and unfinished banded agate in another.", "Both entries place it in mid-IB.", "Retain one accession-level record pending object verification.", "Do not count two independent specimens or resolve the material by preference.", ["unfinished_shaping"], dates={"kind":"stratigraphic_cultural_assignment","subperiod":"IB mid-level","direct_object_date":None}),
        o("MO14", "MS04", ["C1","C2"], "Printed p.30/PDF p.55, Arts and Crafts", "Bhagwanpura craft assemblage", "Sub-periodIB discussion", "source-reported production indicators", "Unfinished beads, raw material and pottery dabbers are reported.", "The authors infer bead making and local pottery manufacture.", "Production is a testable local working hypothesis.", "No complete linked waste/tool sequence or observed teacher relation appears in this locus; broad local transmission and regional transfer both fit.", ["bead_working","pottery_forming"]),
        o("MO15", "MS04", ["C2"], "Printed pp.20,30/PDF pp.41,55", "Grey/red pottery forms", "Sub-periodIB", "form comparison and attributed influence", "Some grey-ware shapes resemble the Late Harappan bowls, jars, basins and dishes-on-stand.", "The authors describe copying and interaction between potters.", "Opportunity for transfer is compatible with the forms.", "Shared function, imports and convergence remain; the forms are not calibrated as rare technical signatures.", ["vessel_form_choice"]),
        o("MO16", "MS04", ["C2"], "B.N.Tandon chapter pp.209–210,213–215/PDF pp.257–258,261–263", "Twelve selected pottery specimens", "Individual phase/findspot joins not supplied in inspected analysis", "material analysis and process inference", "Bulk composition, sections and physical properties are compared across differently colored sherds; wheel manufacture is reported.", "Tandon proposes similar source clay and different thermal conditions.", "Raw-body and firing choices are separate comparison dimensions.", "Bulk similarity without geological controls cannot establish local provenance; mixed unidentified phases do not yield a dated recipe succession.", ["clay_preparation","wheel_forming","firing_control"]),
        o("MO17", "MS04", ["C3"], "Printed pp.18,27–29/PDF pp.39,52,54", "Four saddle querns and pestles on a hut floor", "Early structural phase withinIB", "tools and household-context interpretation", "Grinding tools occur together on a hut floor; the report says grains were not recovered at Bhagwanpura.", "A grain-grinder's household and flour/paste making are proposed.", "A bounded working-place candidate is more informative than generic farming labels.", "Use residues and wear are needed to distinguish grain from other grinding; this does not observe sowing, ploughing or irrigation.", ["grinding"]),
        o("MO18", "MS04", ["C2","C3"], "Printed pp.17–20,23–26/PDF pp.38–41,46–49", "Local stratigraphic sequence and flood horizons", "IA followed byIB", "co-occurrence and chronology claim", "The report describes no stratigraphic break at the transition and changing associated wares after flood episodes.", "It identifies interacting cultural populations and proposed learning.", "Local contact is an opportunity hypothesis requiring technical and person-level evidence.", "Pottery labels do not identify language/ethnicity; flood mixing and changing use need local context checks."),
        o("MO19", "MS04", ["C1","C2","C3"], "TL chapter p.185 andTable6 p.201/PDF pp.231,247", "Pottery dates and depth series", "IA/IB sample series", "physical-dating limitation", "TL analysis reports broad errors and different depth trends for grey and red pottery; its BP table uses1978 as measurement date.", "Water-content variation is a major dating uncertainty.", "The source cannot supply a precise instruction interval or one date for every artifact.", "The table is not recalibrated or converted by assuming a1950 BP baseline.", dates={"kind":"source_TL_series","measurement_year_CE":1978,"reported_accuracy_range_percent":[9,19],"object_specific_transfer_date":None}),
        o("MO20", "MS05", ["C2","C3"], "Printed p.3/PDF p.12, Late Harappan section", "Bara domestic phases", "Six reported structural phases", "domestic architecture", "Mud-walled rooms, circular bins and hearths occur in the reported Bara sequence.", "Bins are described as corn storage.", "Repeated household material tasks supply possible carrier settings.", "Contents, use residues and transmission between occupants are not measured; room size is not converted to population.", ["storage","hearth_use"]),
        o("MO21", "MS05", ["C1","C2","C3"], "Printed pp.3–4/PDF pp.12–13, SGL9/SGL6", "Sanghol phase association and later factory claim", "Bara/overlap/later Kushana phases", "phase-scope control", "The SGL9 overlap list marks PGW with a question mark and notes levelling; the bead/terracotta factory suggestion concerns Kushana buildings.", "Further exposure is requested to establish overlap.", "Keep possible overlap and later production at different dates.", "A Kushana factory does not demonstrate an intermediate Late Harappan workshop; phase co-occurrence is not teaching."),
        o("MO22", "MS06", ["C3"], "Main PDF pp.5–7 methods/results; supplementaryTableS1", "Jognakhera YA1/IV layers5–12; eight botanical samples", "Bara-classified deposits", "recovery and contextual plant occurrence", "Eight0.5mm-flotation samples contain crops, legumes and weeds, with context codes inTableS1.", "Winter and summer crops are treated as a continuing farming package.", "The later regional plant-use sequence has specified recovery and contextual observations.", "Aggregated counts do not observe same-plot cultivation, a teacher or an independently traced origin.", ["plant_handling"]),
        o("MO23", "MS06", ["C3"], "SupplementaryTableS2 andmainPDF p.7, Chronology", "Three newly dated Jognakhera crop specimens", "Multiple dated endpoints", "direct specimen dating", "Source-calibrated ranges are barley2471–2298, Vigna1880–1691 andrice1517–1428calBCE at95.4% scope.", "These dates anchor a broad cultural sequence.", "The study adds directly dated second-millennium crop-use observations.", "TableS2 gives site-level context rather than each sampled-layer join. Date a specimen, not an uninterrupted farming/teaching sequence.", dates={"kind":"source_AMS_short_lived_specimens","probability":0.954,"barley_cal_BCE":[2471,2298],"Vigna_cal_BCE":[1880,1691],"rice_cal_BCE":[1517,1428],"sample_layer_join":"not supplied in inspected TableS2"}),
        o("MO24", "MS06", ["C3"], "MainPDF p.6 Fig3f caption; supplementaryTableS3", "Congealed rice-husk mass and recovered legumes", "Sampled deposits; individual residue date unresolved", "processing-residue candidate", "A congealed husk mass is illustrated and named, alongside cereal and legume remains.", "The crop pattern is interpreted as double cropping and rotation.", "A processing-stage residue can be targeted for an operation comparison.", "The mass does not establish the sequence of husking, its place in cultivation or source of the food; crop co-presence does not identify rotation.", ["husk_handling"]),
        o("MO25", "MS06", ["C3"], "Publisher abstract andmainPDF p.7 Discussion", "Crop-package and geographic comparison", "Late urban to posturban comparison", "source-author historical inference", "The article compares regional crop/ceramic patterns and directly dated rice.", "Rotation, eastward migration and cultural continuity are proposed.", "Separate availability of a regional package from its carrier and transmission route.", "Imports, contact, varied fields and similar ecological solutions remain; river identity and population migration are not identified by the plant sample."),
        o("MO26", "MS07", ["C1"], "Printed p.209/PDF p.3, Ravi section", "Early Ravi living surfaces, pits/hearths and screened debris", "Preurban Ravi phase; control only", "manufacturing association control", "Jasper drills, agate flakes and unfinished beads were recovered from associated living surfaces with systematic screening and microstratigraphy.", "An early bead-making area is reconstructed.", "This shows the kind of association needed to strengthen the later working-stage candidates.", "The control is thousands of years earlier and is not an intermediate bridging observation.", ["drill_use","stone_flaking","unfinished_bead_working"]),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    names = ["sources.json", "observations.json", "acquisition-index.json"]
    if any((args.output_dir/n).exists() for n in names):
        raise SystemExit("Refusing overwrite of a documentary endpoint")
    ss = sources(); oo = observations(); sm = {x["source_id"]:x for x in ss}
    for rec in oo:
        src = sm[rec["source_id"]]
        rec["lineage"] = src["lineage"]
        rec["witness_hash"] = src["witnesses"][0]["sha256"]
        if rec["observation_id"] == "MO23":rec["witness_hash"] = src["witnesses"][2]["sha256"]
    acq = [{**x,"manifest":p.as_posix()} for p in sorted(RAW.glob("acquisition-v*/acquisition.json")) for x in json.loads(p.read_text(encoding="utf-8"))]
    payloads = [{"date":"2026-10-12","sources":ss,"dependence":"Eight work/page records include four site lineages; HARP records overlap, and chapter/edition counts are not independent evidence."},
                {"date":"2026-10-12","coding_status":"frozen descriptive documentary records","observations":oo},
                {"date":"2026-10-12","attempts":acq,"access_notes":["Publisher .pdf/html responses for MS06 were challenge HTML, not article witnesses.","Normal author PDF route returned403; web-tool selected-text inspection succeeded. Its saved text is not original PDF bytes.","Publisher supplement was acquired intact.","Low PDF text-layer recovery was followed by preserved selected-page Tesseract OCR and visual checks."]}]
    for name,payload in zip(names,payloads):
        (args.output_dir/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"sources":len(ss),"observations":len(oo),"acquisition_attempts":len(acq)}))


if __name__ == "__main__":main()
