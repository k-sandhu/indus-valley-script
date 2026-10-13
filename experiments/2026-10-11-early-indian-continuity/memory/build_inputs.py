"""Freeze our source ledger, paraphrased observations and typed claims; raw witnesses stay local."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[2]
RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/memory"
REVIEW_RAW = ROOT / "data/raw/2026-10-11-early-indian-continuity/review"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(sid, title, author, year, url, witness, scope, rights, extra=None):
    path = (RAW / witness) if not witness.startswith("../review/") else REVIEW_RAW / witness.removeprefix("../review/")
    result = {"id": sid, "title": title, "author": author, "publication_year": year,
              "url": url, "witness_path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
              "inspection_scope": scope, "rights_observation": rights, "disposition": "local-only",
              "ancient_witness_independence": "Digital editions/translations are not additional ancient witnesses"}
    if extra:
        result.update(extra)
    return result


def main():
    targets = [OWN / n for n in ("sources.json", "observations.json", "claim-graph.json", "source-checks.json")]
    if any(p.exists() for p in targets):
        raise FileExistsError("Frozen inputs exist; preserve them and create an amended version")
    sources = [
        source("SB-E", "The Satapatha-Brahmana, Part I", "Julius Eggeling, translator", 1882,
               "https://sacred-texts.com/hin/sbr/sbe12/sbe1234.htm", "acquisition-v2/satapatha-flood-correct.html",
               "Mādhyandina1.8.1, all44paragraphs inspected; distinguish translator footnotes", "Archive labels source book public domain; acquired HTML retained locally",
               {"locator": "Sacred Books of the East12, pp216–232; web paragraph IDs1:8:1:1–44",
                "transcription_issue": "Paragraph6 reads Alarm's descent on this website; Sanskrit companion confirms manoravasarpaṇam, Manu's descent; no modern mountain identity inferred"}),
        source("SB-S", "Śatapathabrāhmaṇa, kāṇḍa1 (GRETIL electronic text)", "Input credits H.S.Ananthanarayana/W.P.Lehman", None,
               "https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/2_bra/satapath/sb_01_u.htm", "../review/sb01-gretil.html",
               "Only1.8.1.[5]–[7] inspected for mountain/tree/descent transcription control", "Source states reference-only copyright; local-only",
               {"witness_provider": "Independent reviewer acquisition; reused read-only"}),
        source("RV7-S", "Ṛgveda, Maṇḍala7 (GRETIL electronic text)", "GRETIL source-language edition", None,
               "https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/1_sam/1_rv/rv_hn07u.htm", "acquisition-v1/rigveda7-gretil.html",
               "7.95.1–2 source-language lines inspected alongside two digital presentations", "Redistribution terms unresolved; local-only"),
        source("RV7-M", "The Rigveda: Metrically Restored Text: Book7", "University of Texas Linguistics Research Center", None,
               "https://lrc.la.utexas.edu/books/rigveda/RV07", "acquisition-v1/rigveda7-texas.html",
               "7.95.1–2 restored/accented digital text; edition conventions do not supply a date", "Redistribution terms unresolved; local-only"),
        source("RV10-M", "The Rigveda: Metrically Restored Text: Book10", "University of Texas Linguistics Research Center", None,
               "https://lrc.la.utexas.edu/books/rigveda/RV10", "acquisition-v1/rigveda10-texas.html",
               "10.75.5–6 source-language river-name list inspected", "Redistribution terms unresolved; local-only"),
        source("RV7-E", "Rig-Veda, Book7: Hymn95, Sarasvatī", "Ralph T.H.Griffith, translator", None,
               "https://sacred-texts.com/hin/rigveda/rv07095.htm", "acquisition-v1/rigveda7-95-griffith.html",
               "All6verses inspected; conventional mountains-to-ocean translation retained as a reading", "Older translation; exact edition date and acquired HTML rights unresolved; local-only"),
        source("RV10-E", "Rig-Veda, Book10: Hymn75, The Rivers", "Ralph T.H.Griffith, translator", None,
               "https://sacred-texts.com/hin/rigveda/rv10075.htm", "acquisition-v1/rigveda10-75-griffith.html",
               "All9verses inspected; feature coding concentrates on5–6", "Older translation; exact edition date and acquired HTML rights unresolved; local-only"),
        source("TH09", "A Still Undeciphered Text: How the scientific approach to the Rigveda would open up Indo-European Studies", "Karen Thomson", 2009,
               "https://rigveda.co.uk/asut1.pdf", "acquisition-v1/thomson2009.pdf",
               "Title and pp29–32 inspected; p31 visually checked; limited source for an explicit translation dispute", "Redistribution terms unresolved; local-only",
               {"locator": "Journal of Indo-European Studies37(1–2), p31; PDF31of47", "limitation": "Alternative philological proposal recorded, not adjudicated or used as a replacement authenticated translation"}),
        source("DN-E", "Dīgha Nikāya27, Aggaññasutta: What Came First", "Bhikkhu Sujato, translator", None,
               "https://suttacentral.net/dn27/en/sujato", "acquisition-v1/dn27-en.json",
               "Segmented English witness; frame3–7,10–12 and rice/property/authority13–22 inspected", "License target retrieval failed; no redistribution assertion; local-only",
               {"digital_version": "Bilara-data published branch, acquisition content SHA256 pins payload, not an immutable branch name", "locator": "dn27:17.5–23;18.27–28;19.1–12;20.1–9;21.1–5"}),
        source("DN-P", "Dīgha Nikāya27, Aggaññasutta (Pali root)", "SuttaCentral Mahāsaṅgīti edition", None,
               "https://suttacentral.net/dn27/pli/ms", "acquisition-v1/dn27-pli.json",
               "Pali segments corresponding to18.27,19.1,20.3–4,21.1–3 inspected; no independent new philological translation", "License unresolved for acquired payload; local-only"),
        source("VD-E", "The Zend-Avesta, Part I: FargardII, Yima", "James Darmesteter, translator", 1880,
               "https://sacred-texts.com/book/the-zend-avesta-part-i/shell/fargard-ii-yima-gamshed", "acquisition-v4/vendidad2-darmesteter.html",
               "Translator introduction and paragraphs21–41 inspected; primary winter narrative kept separate from translator Noah comparison", "Older SBE4translation; acquired HTML local-only",
               {"locator": "Darmesteter paragraph numbering22(46)–30(87); printedpp16–18", "limitation": "No Avestan source-language recensional or absolute-date claim tested"}),
        source("S17", "Counter-intuitive influence of Himalayan river morphodynamics on Indus Civilisation urban settlements", "Ajit Singh and colleagues", 2017,
               "https://www.nature.com/articles/s41467-017-01643-9", "acquisition-v1/singh2017.html",
               "Main paper sample design, OSL chronology, provenance, statistical analysis and discussion inspected; supplementary tables not acquired or reanalysed", "Main article CC-BY4; downloaded witness retained locally",
               {"doi": "10.1038/s41467-017-01643-9", "locator": "Chronology of palaeochannel fluvial sands; Regional analysis; Fig8–10; Discussion", "date_type": "Estimated depositional/process ages in source kaBP; zircon/mica Ma are provenance ages"}),
        source("G12", "Fluvial landscapes of the Harappan civilization", "Liviu Giosan and colleagues", 2012,
               "https://www.pnas.org/doi/10.1073/pnas.1112743109", "acquisition-v1/giosan2012-author-summary.html",
               "Raw HTML contains full main article, including Methods and main results; Author Summary follows it. Main Ghaggar/Indus results and Methods inspected; supplement not acquired", "Article rights unresolved for redistribution; local-only",
               {"doi": "10.1073/pnas.1112743109", "locator": "Main paper ppE1688–E1694; Ghaggar-Hakra results and Methods", "filename_warning": "Original acquired filename says author-summary but payload includes full main paper"}),
        source("C19", "On the existence of a perennial river in the Harappan heartland", "Anirban Chatterjee, Jyotiranjan S.Ray, Anil D.Shukla and Kanchan Pande", 2019,
               "https://www.nature.com/articles/s41598-019-53489-4", "acquisition-v1/chatterjee2019.html",
               "Main stratigraphy, evolving river system, settlement interpretation and Methodology inspected; supplementary sample table not acquired or reanalysed", "Main article CC-BY4; downloaded witness retained locally",
               {"doi": "10.1038/s41598-019-53489-4", "locator": "Fig1–3; Stratigraphy; The evolving river system; Methodology", "date_type": "Shell radiocarbon/OSL depositional ages; Sr-Nd and detrital mica source tracing are distinct measurements"}),
        source("D19", "Revisiting the contemporaneity of a mighty river and the Harappans: Archaeological, stratigraphic and chronometric constraints", "Aditi Krishna Dave, Marie Agnes Courty, Kathryn E.Fitzsimmons and Ashok Kumar Singhvi", 2019,
               "https://research.monash.edu/en/publications/revisiting-the-contemporaneity-of-a-mighty-river-and-the-harappan/", "acquisition-v1/dave2019-record.html",
               "Author-institution abstract and publication metadata only; numerical sample ages not accessed", "Abstract©2018Elsevier, article2019; local-only",
               {"doi": "10.1016/j.quageo.2018.05.002", "locator": "Quaternary Geochronology49:230–235; Abstract", "study_reach": "Chautang near Hissar/Haryana, not every Ghaggar-Hakra reach"}),
        source("W97", "The Development of the Vedic Canon and its Schools: The Social and Political Milieu (Materials on Vedic Śākhās,8)", "Michael Witzel", 1997,
               "https://fid4sa-repository.ub.uni-heidelberg.de/110/1/VedicCanon_1997.pdf", "witzel-indexed-excerpt.json",
               "Indexed primary PDF excerpt at p258including note5 only; fullPDFdownloads blocked by TLS/Anubis. Search response is not a downloaded PDF", "Primary excerpt/search payload local-only",
               {"locator": "Inside the Texts, Beyond the Texts, pp257–345; inspectedp258n5", "limitation": "No assertion that the full article was read"}),
        source("L17", "Embodying the Vedas: Traditional Vedic Schools of Contemporary Maharashtra", "Borayin Larios", 2017,
               "https://doi.org/10.1515/9783110517323", "acquisition-v4/larios2017.pdf",
               "Title/license, sample selectionpp9–10, lesson/revisionpp103–115 and mnemonic devices inspected; p111render visually checked", "PDFcopyright2017CC-BY-NC-ND3.0; no redistributable derivative assumed; local-only",
               {"locator": "Printedpp9–10,103–115; PDF25–26,119–131; field illustrations/interviews2009 and2011", "measurement_scope": "Contemporary25school ethnographic sample; author explicitly disclaims statistical precision; does not establish every ancient link"}),
        source("A22", "Early Buddhist Texts: Their Composition and Transmission", "Mark Allon", 2022,
               "https://pmc.ncbi.nlm.nih.gov/articles/PMC8789374/", "../review/allon2021.html",
               "Introduction, Main Differences section, wording/plot comparisons and closing transmission discussion inspected; reused reviewer witness", "PMC displays time-limited COVID research-reuse permission; no current redistribution inference; local-only",
               {"doi": "10.1007/s10781-021-09499-6", "locator": "Journal of Indian Philosophy50:523–556; Main Differences; Sāmaññaphala introduction comparison", "filename_warning": "Local filename2021 reflects accepted/copyright/DOIyear; publication2022", "witness_provider": "Independent reviewer acquisition; reused read-only"}),
    ]
    attempts = []
    for path in sorted(RAW.glob("acquisition-v*/acquisition.json")):
        for record in json.loads(path.read_text(encoding="utf-8")):
            if not record.get("success"):
                attempts.append({"ledger": path.relative_to(ROOT).as_posix(), "name": record["name"], "url": record["requested_url"], "error_type": record.get("error_type"), "error": record.get("error")})
    invalid = {"path": "data/raw/2026-10-11-early-indian-continuity/memory/acquisition-v1/satapatha-flood.html",
               "sha256": digest(RAW / "acquisition-v1/satapatha-flood.html"),
               "reason": "HTTPsuccess but title/bodySB1.7.1; filename inferred wrongly from adjacent chapter; excluded from flood observations"}

    def obs(oid, case, kind, refs, locus, finding, implication, absent=None, dating=None):
        row = {"id": oid, "case": case, "evidence_type": kind, "source_ids": refs, "locus": locus,
               "observation": finding, "interpretive_limit": implication}
        if absent:
            row["bounded_absence"] = absent
        if dating:
            row["dating"] = dating
        return row

    observations = [
        obs("SB01", "Manu", "textual_content", ["SB-E", "SB-S"], "ŚB1.8.1.1–6",
            "Fish is reared through containers to sea; announces a relative year; ship is tied to fishhorn and then a tree at northern mountain; Manu survives/descent follows recession.",
            "Relative prediction has no independent calendar. Geographical identification of mountain needs evidence outside this wording.",
            "Passage1–6 supplies no historical king list, dated deposition layer or unique Harappan locality; later translator footnote references are outside this passage.",
            {"narrated_time": "relative such-and-such year and recession sequence", "composition_calendar": None, "physical_event_calendar": None}),
        obs("SB02", "Manu", "textual_content", ["SB-E"], "ŚB1.8.1.7–11",
            "Offered dairy produces daughter; she authorizes her use in the middle of sacrifice; passage identifies her with Iḍā and extends Manu's successful offspring/cattle to the current performer.",
            "The text binds a present rite to an ancestral precedent. It does not date first adoption of dairy offerings."),
        obs("SB03", "Manu", "textual_content", ["SB-E"], "ŚB1.8.1.12–18,28,38–39",
            "Five-part portions, handing to Hotṛ, ghee/lip actions and paired breathing formulas, protective low voice, Vedastudy/teaching and five eaters form specific instructions around an origin story.",
            "Operational detail is genuinely explicit. Its continuous performance from Harappa is a separate, unestablished route."),
        obs("RV01", "Sarasvati", "textual_content", ["RV7-S", "RV7-M", "RV7-E"], "RV7.95.1–2",
            "River/goddess praise includes strength, protection, mountain/samudra wording and gift to Nahuṣa. Conventional Griffith translation gives mountains-to-ocean.",
            "Poetic protection and nourishment cannot independently identify urban architecture or a hydrological discharge class.",
            "The inspected verses state no calendar or diagnostic depositional change.", {"narrated_time": "praise and attributed gift, not an annal", "composition_calendar": None}),
        obs("RV02", "Sarasvati", "philological_dispute", ["TH09", "RV7-S", "RV7-E"], "Thomson2009p31; RV7.95.2",
            "Thomson challenges the conventional direction through the ablative form samudrāt and its parallels. Conventional rendering and challenge are both retained.",
            "We did not adjudicate this linguistic dispute; neither branch licenses a calendar join to sampled river sediments."),
        obs("RV03", "Sarasvati", "textual_content", ["RV10-M", "RV10-E"], "RV10.75.5–6",
            "Named river invocation includes Gaṅgā, Yamunā, Sarasvatī, Śutudrī, Paruṣṇī and others; surrounding hymn centers Sindhu.",
            "Names and regional configuration offer more external testing opportunities than a general flood. Which name denotes which reach at composition remains an identification question.",
            "The list itself gives no river abandonment date.", {"narrated_time": "invocation", "composition_calendar": None}),
        obs("DN01", "Agganna", "textual_content", ["DN-E"], "DN27.3–7,10–12",
            "Discourse answers inherited superiority claims and explains mixed good/bad conduct across four classes; origin narrative occurs in recurring cosmic expansion with luminous beings.",
            "The account explicitly serves ethical status and cosmological explanation; a historical chronicle reading requires separate support."),
        obs("DN02", "Agganna", "textual_content", ["DN-E", "DN-P"], "DN27.17.5–23;18.27–28;19.1–12",
            "Rice collection is enlarged to multiple days; hoarding changes magically regenerative rice; beings divide rice and establish boundaries; repeated taking others' shares prompts reprimand and violence.",
            "The property/theft dependency is explicit. The disappearance of effortless rice is a moral/cosmic causal claim rather than measured agriculture."),
        obs("DN03", "Agganna", "textual_content", ["DN-E", "DN-P"], "DN27.20.1–9;21.1–5",
            "Community selects an attractive illustrious being to censure and expel appropriately, paying a rice share; Mahāsammata, khattiya and rājā receive explanatory derivations.",
            "Role and compensation relations are concrete; the passage does not authenticate elected Harappan kings or taxation.",
            "No Harappan personal name, place, administrative sign or calendar occurs in these inspected paragraphs.", {"narrated_time": "primordial social origins", "composition_calendar": None}),
        obs("VD01", "Yima_control", "comparative_motif", ["VD-E"], "VendidadII22(46)–30(87),Darmesteter numbering",
            "Divine warning concerns lethal winter and deep snow; preservation uses an enclosure containing selected people, animals and plant seeds, water and dwelling arrangements.",
            "Rescue/world renewal template overlaps broadly with Manu but agents, hazard and preservation device differ. Shared ancestry, diffusion and separate construction remain alternatives.",
            "The inspected primary paragraphs do not describe Manu's fish towing a ship; translator's Noah comparison is commentary.", {"narrated_time": "anticipated fatal winters", "composition_calendar": None}),
        obs("S17-01", "River", "physical_process_estimate", ["S17"], "Chronology of palaeochannel fluvial sands; Regional analysis; Discussion",
            "Main paper derives52OSLburialages from7cores; Kalibangan transect large-river deposits ceased betweenabout23and12.3ka, regional late activity inMNK6endsabout8ka; provenance supports former Sutlejcourse.",
            "These are measured stratigraphic/process/provenance claims for sampled locations, not dates of a named poem.",
            dating={"system": "source kaBP; BP not converted to BCE", "process_claim": "regional abandonment complete shortlyafterabout8ka", "provenance": "U-Pbzircon and Ar-Armica Maages identify source rocks, not sediment burial or hymn composition"}),
        obs("G12-01", "River", "physical_process_estimate", ["G12"], "Main Ghaggar-Hakra results; Methods",
            "SRTMmorphology plus AMSradiocarbon/OSL of deposits underpin claim against large glacier-fed HoloceneGhaggar-Hakra. Authors allow active monsoon-fed rivers with possible perennial groundwaterbaseflow; dated deposits differ by reach.",
            "Absence of glacier supply is not absence of all water or year-roundflow. Sample age is not the age of a river name.",
            dating={"system": "sourceyearsago retained", "examples": "FortAbbas sandydepositabout5400years; citedupperinterfluvedepositabout4300years; lowerreachsedimentationlateHolocene", "composition_calendar": None}),
        obs("C19-01", "River", "physical_process_estimate", ["C19"], "Stratigraphy; The evolving river system; Methodology; Fig1–3",
            "About300km basin synthesis combines shell AMSradiocarbon/quartzOSL with detritalmica and Sr-Ndprovenance; authors infer renewed Himalayan supply/perennialflow9–4.5ka through Sutlejdistributaries.",
            "The inferred year-roundwater model and Sarasvatī identification extend sediment/provenance evidence. Main channel abandonment and temporary distributary supply require reach-matched tests.",
            dating={"system": "sourcekaBP", "process_interval": [9.0, 4.5], "composition_calendar": None}),
        obs("D19-01", "River", "reported_process_claim", ["D19"], "InstitutionalAbstract",
            "ChautangnearHissar stratifiedquartzOSL study reports cessation of a major Himalayanfluvial system well beforeHarappa and criticizes direct settlement-number/river-strength inference.",
            "Only abstract accessed; no numerical age extracted. Chautang reach does not automatically adjudicate everyGhaggar deposit.",
            dating={"process_relative": "wellbeforeHarappanCivilization perauthors", "numerical_age": None}),
        obs("W97-01", "Professional_transmission", "scholarly_transmission_claim", ["W97"], "p258note5",
            "Indexed author excerpt qualifies very stable Vedic transmission as strictly applicable after collection/redaction, while arguing earlier changes minimal.",
            "Exactness after a corpus is fixed does not independently establish its precollection story age."),
        obs("L17-01", "Professional_transmission", "ethnographic_observation", ["L17"], "pp9–10,103–115",
            "In25contemporaryMaharashtraschools, observed lessons fragment and string text, revision corrects pronunciation/intonation, advancedstudents sometimes guide revision, printedbooks aid earlylearning.",
            "A measured present mechanism can motivate historical hypotheses; sample is not statistically representative and does not observe each ancient transmission interval.",
            dating={"publication_CE": 2017, "inspected_field_attestations_CE": [2009, 2011], "ancient_transmission_calendar": None}),
        obs("A22-01", "Professional_transmission", "comparative_textual_observation", ["A22"], "Main Differences section; Sāmaññaphala narrativecomparison",
            "Allon argues early sutras were fixed for communal memorization yet communities sanctioned revisions; parallels differ in names, events, lists, wording and plot; a developedGandhari narrative has a2cCEmanuscript witness.",
            "Narrative elaboration can precede a later simpler surviving version. This example concerns another discourse and cannot become a DN27manuscriptdate.",
            dating={"publication_CE": 2022, "other_discourse_manuscript": "2ndcenturyCE as reportedbyAllon", "DN27_composition_calendar": None}),
    ]
    nodes = [
        {"id": "rv7_composition", "kind": "text_composition", "absolute_date": None},
        {"id": "rv10_composition", "kind": "text_composition", "absolute_date": None},
        {"id": "sb_composition", "kind": "text_composition", "absolute_date": None},
        {"id": "dn27_composition", "kind": "text_composition", "absolute_date": None},
        {"id": "singh_process", "kind": "physical_process", "date": {"label": "abandonmentshortlyafterabout8kaBP", "observation": "S17-01"}},
        {"id": "chatterjee_process", "kind": "physical_process", "date": {"label": "revival9–4.5kaBP", "observation": "C19-01"}},
        {"id": "giosan_process", "kind": "physical_process", "date": {"label": "reach-specificdepositages", "observation": "G12-01"}},
        {"id": "river_identity", "kind": "proposed_identification"},
        {"id": "manu_story_time", "kind": "narrated_time", "date": {"label": "relativesuchandsuchyear", "observation": "SB01"}},
        {"id": "vedic_precision", "kind": "transmission_mechanism", "observation": "W97-01"},
        {"id": "larios_fieldwork", "kind": "modern_field_observation", "date": {"label": "inspected2009/2011attestations", "observation": "L17-01"}},
        {"id": "gandhari_samannaphala", "kind": "manuscript_witness", "date": {"label": "2ndcenturyCEreported", "observation": "A22-01"}},
        {"id": "samannaphala_composition", "kind": "text_composition", "absolute_date": None},
        {"id": "samannaphala_presence", "kind": "text_presence_bound", "absolute_date": None},
        {"id": "DN27_digital_export", "kind": "modern_digital_witness", "date": {"label": "download2026-10-11", "source": "DN-E"}},
        {"id": "dn27_present_export", "kind": "text_presence_bound", "absolute_date": None},
    ]
    edges = [
        {"from": n, "to": "river_identity", "kind": "assumed_named_river_match", "status": "proposed"}
        for n in ("singh_process", "chatterjee_process", "giosan_process")
    ] + [
        {"from": "river_identity", "to": "rv7_composition", "kind": "date_hymn_by_identification", "status": "proposed"},
        {"from": "river_identity", "to": "rv10_composition", "kind": "date_hymn_by_identification", "status": "proposed"},
        {"from": "manu_story_time", "to": "sb_composition", "kind": "equate_narrated_and_composed_time", "status": "proposed"},
        {"from": "vedic_precision", "to": "rv7_composition", "kind": "infer_origin_age_from_fidelity", "status": "proposed"},
        {"from": "larios_fieldwork", "to": "sb_composition", "kind": "infer_ancient_chain_from_modern_mechanism", "status": "proposed"},
        {"from": "gandhari_samannaphala", "to": "dn27_composition", "kind": "transfer_other_text_witness", "status": "proposed"},
        {"from": "gandhari_samannaphala", "to": "samannaphala_presence", "kind": "attests_own_text_by_witness_date", "status": "supported", "same_text": True},
        {"from": "DN27_digital_export", "to": "dn27_present_export", "kind": "attests_own_text_by_witness_date", "status": "supported", "same_text": True},
    ]
    graph = {"description": "Type gates prevent narrative or proposed identities from transmitting calendar bounds. Valid witness edges attest text presence, not first composition.",
             "nodes": nodes, "edges": edges,
             "routes_to_challenge": [[n, "river_identity", t] for n in ("singh_process", "chatterjee_process", "giosan_process") for t in ("rv7_composition", "rv10_composition")]
                                     + [["manu_story_time", "sb_composition"], ["vedic_precision", "rv7_composition"], ["larios_fieldwork", "sb_composition"], ["gandhari_samannaphala", "dn27_composition"]],
             "valid_controls": [["gandhari_samannaphala", "samannaphala_presence"], ["DN27_digital_export", "dn27_present_export"]]}
    checks = []
    check_defs = [
        ("SB01", "extract-v1/acquisition-v2-satapatha-flood-correct.txt", ["1:8:1:4", "1:8:1:6", "northern mountain"]),
        ("SB02", "extract-v1/acquisition-v2-satapatha-flood-correct.txt", ["1:8:1:11", "middle of the sacrifice"]),
        ("SB03", "extract-v1/acquisition-v2-satapatha-flood-correct.txt", ["1:8:1:18", "1:8:1:28", "1:8:1:38", "fivefold cutting"]),
        ("RV01", "extract-v1/acquisition-v1-rigveda7-gretil.txt", ["RV_7,095.02", "samudrāt"]),
        ("RV03", "extract-v1/acquisition-v1-rigveda10-75-griffith.txt", ["HYMN LXXV.", "Yamunā", "Sarasvatī", "Sindhu"]),
        ("VD01", "extract-v1/acquisition-v4-vendidad2-darmesteter.txt", ["22 (46)", "fatal winters", "25 (61)", "seeds"]),
        ("S17-01", "extract-v1/acquisition-v1-singh2017.txt", ["52 optically stimulated", "8.0", "regional"]),
        ("G12-01", "extract-v1/acquisition-v1-giosan2012-author-summary.txt", ["Methods", "groundwater-fed base flow", "accelerator mass spectrometry"]),
        ("C19-01", "extract-v1/acquisition-v1-chatterjee2019.txt", ["300", "distributaries", "Methodology"]),
        ("D19-01", "extract-v1/acquisition-v1-dave2019-record.txt", ["Chautang", "Hissar", "quartz"]),
    ]
    for oid, name, words in check_defs:
        path = RAW / name
        content = path.read_text(encoding="utf-8")
        checks.append({"observation": oid, "witness": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                       "kind": "locus/short-token presence control; meaning manually inspected", "required_tokens": words,
                       "tokens_present": [w.lower() in content.lower() for w in words]})
    for oid, names in [("DN01", ["dn27:3.6", "dn27:7.8", "dn27:10.1"]),
                       ("DN02", ["dn27:17.21", "dn27:18.27", "dn27:19.1"]),
                       ("DN03", ["dn27:20.3", "dn27:20.4", "dn27:21.1"])]:
        path = RAW / "acquisition-v1/dn27-en.json"; content = json.loads(path.read_text(encoding="utf-8"))
        checks.append({"observation": oid, "witness": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                       "kind": "JSON segment presence; meaning manually inspected", "required_tokens": names,
                       "tokens_present": [n in content for n in names]})
    for oid, fn, page, words in [("RV02", "acquisition-v1-thomson2009.json", 31, ["ablative", "7.95.2"]),
                               ("L17-01", "acquisition-v4-larios2017.json", 127, ["correct pronunciation", "advanced student"])]:
        path = RAW / "extract-v1" / fn; pages = json.loads(path.read_text(encoding="utf-8"))
        t = pages[page-1]["text"]
        checks.append({"observation": oid, "witness": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "pdf_page": page,
                       "kind": "Selected PDF page tokens plus visual inspection", "required_tokens": words,
                       "tokens_present": [w.lower() in t.lower() for w in words]})
    for oid, path, words in [("A22-01", REVIEW_RAW / "allon2021.txt", ["differences in the names of people and places", "2nd century CE Gandhari manuscript"]),
                             ("W97-01", RAW / "witzel-indexed-excerpt.json", ["Strictly speaking, only after the collection"]),
                             ("SB01", REVIEW_RAW / "sb01-gretil.txt", ["1.8.1.[6]", "manoravasarpaṇam"])]:
        t = path.read_text(encoding="utf-8")
        checks.append({"observation": oid, "witness": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                       "kind": "Exact token/locus control in bounded inspected source", "required_tokens": words,
                       "tokens_present": [w.lower() in t.lower() for w in words]})
    metadata = {"created_utc": datetime.now(timezone.utc).isoformat(), "protocol_sha256": digest(OWN / "PROTOCOL.md"),
                "status": "Frozen documentary inputs; subsequent corrections require an amendment", "raw_disposition": "local-only"}
    payloads = [{**metadata, "sources": sources, "failed_acquisitions": attempts, "wrong_target_excluded": [invalid]},
                {**metadata, "observations": observations}, {**metadata, **graph},
                {**metadata, "checks": checks, "all_token_checks_pass": all(all(r["tokens_present"]) for r in checks),
                 "meaning_validation": "Manual inspected loci and paraphrases; token checks alone cannot validate interpretation"}]
    for path, payload in zip(targets, payloads):
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": len(sources), "observations": len(observations), "checks": len(checks), "all_token_checks_pass": payloads[-1]["all_token_checks_pass"], "failed_acquisitions": len(attempts)}))


if __name__ == "__main__":
    main()
