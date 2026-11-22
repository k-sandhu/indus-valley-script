"""Build the reconciled Indus site and survey-effort gazetteer (v1).

Reads held local registers under experiments/ and data/raw/, applies the
reconciliation, four-unit separation, conflict-preservation, excavation-status,
and survey-effort rules frozen in PROTOCOL.md, writes a local-only raw
concordance extract to data/raw/2026-11-22-site-survey-gazetteer/, and emits
CC0-safe tracked derived tables under experiments/2026-11-22-site-survey-gazetteer/.

Standard library only (Python 3.13). Deterministic output.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]
RAW_OUT_DIR = ROOT / "data" / "raw" / "2026-11-22-site-survey-gazetteer"
PHYSICAL_RAW_PREFIX = Path(r"D:\projects\indus_valley_script\data\raw\2026-11-22-site-survey-gazetteer")

BUILD_DATE = "2026-11-22"
SCHEMA_VERSION = "1.0"

INPUT_PATHS = {
    "atlas_data": ROOT / "experiments/2026-10-26-indus-living-atlas/mapping/run-v2/atlas-data.json",
    "living_towns": ROOT / "experiments/2026-10-26-indus-living-atlas/living-towns/towns.json",
    "q1032_towns": ROOT / "experiments/2026-10-24-q1032-town-axis-register/run-v5/town-axis-table.json",
    "census_coverage": ROOT / "experiments/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/coverage.json",
    "census_site_register": ROOT / "experiments/2026-10-06-evidence-census/sites-and-publications/site-register.json",
    "post_catalogue_sites": ROOT / "experiments/2026-10-21-post-catalogue-finds/sites.csv",
    "post_catalogue_objects": ROOT / "experiments/2026-10-21-post-catalogue-finds/objects.csv",
    "prospection_candidates": ROOT / "experiments/2026-10-11-settlement-prospection/candidates-v5.json",
    "prospection_sources": ROOT / "experiments/2026-10-11-settlement-prospection/sources-v6.json",
    "satellite_atlas": ROOT / "experiments/2026-10-12-satellite-prospection/exports-v2/atlas-data-v2.json",
    "satellite_recon": ROOT / "experiments/2026-10-12-satellite-prospection/exports-v2/reconnaissance-register.csv",
    "satellite_blocks_v1": ROOT / "experiments/2026-10-12-satellite-prospection/blocks-v1.json",
    "satellite_blocks_v2": ROOT / "experiments/2026-10-12-satellite-prospection/blocks-v2.json",
    "orengo_aoi": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_ORENGO_SOURCE_AOI.geojson",
    "singh_cores": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_SINGH_CORES_DERIVED.json",
    "mahsa_b02": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_MAHSA_MAPQUERY_B02.json",
    "mahsa_b04": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_MAHSA_MAPQUERY_B04.json",
    "mahsa_hanumangarh": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_MAHSA_STRINGQUERY_Hanumangarh.json",
    "mahsa_pilibanga": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_MAHSA_STRINGQUERY_Pilibanga.json",
    "mahsa_juna_khatiya": ROOT / "data/raw/2026-10-12-satellite-prospection/SPATIAL_CONCORDANCE_MAHSA_TERMS_Juna_Khatiya.json",
    "rajesh_2025": ROOT / "data/raw/2026-10-11-settlement-prospection/RAJESH2025.pages.json",
}

# Cross-register ID reconciliations (PROTOCOL.md Section 4)
Q1032_TO_CANONICAL = {
    "desalpur": "desalpar",
    "gola-dhoro": "gola-dhoro-bagasra",
}

LIVING_TOWN_TO_CANONICAL = {
    "LT-01": "peshawar",
    "LT-02": "multan",
    "LT-03": "taxila",
    "LT-04": "harappa",
    "LT-05": "varanasi",
    "LT-06": "ujjain",
    "LT-07": "mathura",
    "LT-08": "patna-pataliputra",
    "LT-09": "rajgir-rajagriha",
    "LT-10": "srinagar-burzahom",
    "LT-11": "ropar-rupar",
    "LT-12": "vadnagar",
    "LT-13": "lumbini",
    "LT-14": "tilaurakot-kapilavastu",
    "LT-15": "anuradhapura",
    "LT-16": "mahasthangarh-mahasthan",
    "LT-17": "dholavira",
    "LT-18": "mohenjo-daro",
}

POST_CATALOGUE_SITE_TO_CANONICAL = {
    "Baror": "baror",
    "Bet Dwarka": "bet-dwarka",
    "Bhirrana": "bhirrana",
    "Desalpar": "desalpar",
    "Dhalewan": "dhalewan",
    "Dholavira": "dholavira",
    "Farmana": "farmana",
    "Ganweriwala": "ganweriwala",
    "Gola Dhoro (Bagasra)": "gola-dhoro-bagasra",
    "Harappa": "harappa",
    "Hulas": "hulas",
    "Indiranagar (Kanpur)": "indiranagar-kanpur",
    "Juni Kuran": "juni-kuran",
    "Kanmer": "kanmer",
    "Karanpura": "karanpura",
    "Khirsara": "khirsara",
    "Lakhanjo-daro": "lakhanjo-daro",
    "Mitathal": "mitathal",
    "Mohenjo-daro": "mohenjo-daro",
    "Nagwada": "nagwada",
    "Nuhato": "nuhato",
    "Rakhigarhi": "rakhigarhi",
    "Rupar": "ropar-rupar",
    "Shikarpur": "shikarpur",
    "Surkotada": "surkotada",
    "Tarkhanewala Dera": "tarkhanewala-dera",
}

SITE_REGISTER_SPELLING_TO_CANONICAL = {
    "Bala-kot": "balakot",
    "Binjor": "binjor-4msr",
    "Desalpur": "desalpar",
    "Gharo Bhiro": "nuhato",
    "Girsu": "girsu-tello",
    "Kot-Diji": "kot-diji",
    "Nindowari-damb": "nindowari",
    "Ra's al-Jinz": "ras-al-jinz",
    "Ra's al-Junayz": "ras-al-jinz",
    "Rahman-deri": "rehman-dheri",
    "Rodji": "rojdi",
    "Rupar": "ropar-rupar",
    "Tarkhanewala-dera": "tarkhanewala-dera",
    "Tell Jokha": "umma",
    "Tell Umma": "umma",
    "Tello": "girsu-tello",
}

SAT_REF_TO_CANONICAL = {
    "GAN-DOAM": "ganweriwala",
    "GAN-GULZAR": "ganweriwala",
    "HAR-DOAM": "harappa",
    "HAR-UESUGI": "harappa",
    "JUN-TABLE": "juna-khatiya",
    "PAD-TABLE": "padta-bet",
    "DWA-TABLE": "dwajagadh",
    "KAL-SINGH": "kalibangan",
    "KAL-NIGAM": "kalibangan",
}

# Explicit status overrides grounded in PROTOCOL.md Section 6 and held witnesses
BURIED_UNDER_LIVING_TOWN_IDS = {
    "lakhanjo-daro": True,
    "rakhigarhi": True,
    "chandigarh": True,
    "manda": True,
    "peshawar": True,
    "multan": False,
    "varanasi": True,
    "mathura": True,
    "patna-pataliputra": True,
    "vadnagar": True,
    "srinagar-burzahom": True,
}

PARTIAL_LIVING_TOWN_OVERLAP_IDS = {
    "harappa",
    "ropar-rupar",
    "ujjain",
    "rajgir-rajagriha",
    "tilaurakot-kapilavastu",
    "anuradhapura",
    "mahasthangarh-mahasthan",
}

NEARBY_DISTINCT_SETTLEMENT_IDS = {
    "dholavira",
    "mohenjo-daro",
    "taxila",
    "lumbini",
}

REGIONAL_PROVENANCE_IDS = {"dilmun", "luristan"}

SURFACE_SURVEYED_ATLAS_IDS = {
    "judeirjo-daro",
    "lohumjo-daro",
    "ornach-area",
    "rajanpur",
    "sotka-koh",
    "wattoowala",
}

EXCAVATED_ATLAS_OVERRIDE_IDS = {
    "bet-dwarka",
    "navinal",
    "failaka",
    "qala-at-al-bahrain",
    "hili",
    "bat",
    "sarazm",
    "hajar",
}

UNKNOWN_ATLAS_IDS = {
    "derawar-ther",
    "guddal-a",
    "rappwala-ther",
    "babylon",
    "saar",
    "tell-abraq",
    "karzakan",
    "janabiyah",
    "kalba",
    "dilmun",
    "luristan",
}

# Survey campaigns catalogue (PROTOCOL.md Section 7)
SURVEY_CAMPAIGNS = [
    {
        "campaign_id": "SC-MUGHAL-CHOLISTAN",
        "name": "Mughal Cholistan archaeological survey",
        "investigators": "M. Rafique Mughal",
        "years": "1974-1977",
        "region": "Cholistan Desert, Punjab, Pakistan",
        "method": "Systematic pedestrian surface survey along the Hakra paleochannel system",
        "source_ids": ["R08"],
        "window_ids": ["P01", "P02"],
        "coverage_notes": "Baseline surface inventory of Cholistan mounds; 25 large reference mounds reused to train Orengo et al. 2020 detector.",
    },
    {
        "campaign_id": "SC-ORENGO-CHOLISTAN-2020",
        "name": "Orengo et al. 2020 Cholistan multi-sensor mound detection",
        "investigators": "Hector A. Orengo, Francesc C. Conesa, Arnau Garcia-Molsosa, Adam S. Green, Cameron A. Petrie and colleagues",
        "years": "2020",
        "region": "Cholistan Desert, Pakistan",
        "method": "Random-forest classification of multi-temporal Sentinel-1 SAR and Sentinel-2 optical imagery",
        "source_ids": ["R08", "SPC07"],
        "window_ids": ["P01", "P02"],
        "coverage_notes": "Proposed 337 mound clusters (71 matched earlier records including 25 reference mounds; 266 unmatched proposals awaiting ground check and chronology).",
    },
    {
        "campaign_id": "SC-GULZAR-GANWERIWALA",
        "name": "Ganweriwala surface surveys and 2024 excavation",
        "investigators": "Farzand Masih, Toshiki Osada, J. Mark Kenoyer (2007); Sidra Gulzar (2015); University of Lahore / THAAP (2024)",
        "years": "2007, 2015, 2024",
        "region": "Ganweriwala, Cholistan, Pakistan",
        "method": "Total-station surface survey (66.7 ha cultural spread) and 2024 excavation season",
        "source_ids": ["R05", "R06", "R07", "SPC01", "SPC02"],
        "window_ids": ["P02"],
        "coverage_notes": "Three non-equivalent area figures (81.5 ha legacy, 66.7 ha 2015 cultural spread, circa 33 ha 2020 visible mound) and a 13.7 km DOAM vs survey-paper coordinate discrepancy.",
    },
    {
        "campaign_id": "SC-GREEN-2019-HARYANA-PUNJAB",
        "name": "Green et al. 2019 TwoRains historical-map field survey",
        "investigators": "Adam S. Green, Hector A. Orengo, Aftab Alam, Arnau Garcia-Molsosa, R. N. Singh, Cameron A. Petrie and colleagues",
        "years": "2017-2018",
        "region": "Haryana and Punjab plains, India",
        "method": "Ground verification of Survey of India 19th-20th century topographic mound symbols plus off-map encounters",
        "source_ids": ["R09", "R10", "R12"],
        "window_ids": ["P03", "P04", "P05", "P06"],
        "coverage_notes": "Checked 779 historical-map features: 199 archaeological positives across multiple periods (169 unlinked to earlier reports) plus 64 off-map locations. Stopping rules in 2017 and map filtering in 2018 restrict transfer of checked rates.",
    },
    {
        "campaign_id": "SC-PETRIE-LWS-TWORAINS",
        "name": "Land, Water and Settlement and TwoRains projects (Cambridge and BHU)",
        "investigators": "Cameron A. Petrie, Ravindra N. Singh, Danika Parikh, Jennifer Bates and colleagues",
        "years": "2008-2023",
        "region": "Rakhigarhi, Masudpur, Lohari Ragho, Bahola, Alamgirpur, Haryana and western Uttar Pradesh, India",
        "method": "Multi-season village survey, mound remapping, test excavations, and archaeobotanical flotation",
        "source_ids": ["R09", "R23", "R24", "R29"],
        "window_ids": ["P03", "P07"],
        "coverage_notes": "Recorded 127 all-period locations within 15 km of Rakhigarhi and remapped Masudpur from 4 legacy mounds at one coordinate to 13 discrete mounds.",
    },
    {
        "campaign_id": "SC-GARCIA-MOLSOSA-2023-PUNJAB",
        "name": "Garcia-Molsosa et al. 2023 Harappa and Punjab alluvial floodplain survey integration",
        "investigators": "Arnau Garcia-Molsosa, Hector A. Orengo, Cameron A. Petrie",
        "years": "2023",
        "region": "Harappa, Khanewal, East Multan and Tulamba, Punjab, Pakistan",
        "method": "Automated historical-map feature extraction (13,130 raw features; 646 retained) compared against 240 PAS sites and alluvial geomorphology",
        "source_ids": ["R11", "SPC08"],
        "window_ids": ["P08", "P09"],
        "coverage_notes": "Matched 123 of 240 PAS all-period sites (51.3%) to historical-map features; distinguished older protohistoric-bearing alluvium from younger scouring channels.",
    },
    {
        "campaign_id": "SC-HARP-HARAPPA",
        "name": "Harappa Archaeological Research Project (HARP) and earlier ASI excavations",
        "investigators": "Daya Ram Sahni, M. S. Vats, R. E. M. Wheeler, George F. Dales, Richard H. Meadow, Jonathan Mark Kenoyer",
        "years": "1921-present (HARP 1986-present)",
        "region": "Harappa, Sahiwal district, Punjab, Pakistan",
        "method": "Long-term stratigraphic urban excavation, surface survey, and conservation",
        "source_ids": ["R30", "R63", "SPC03"],
        "window_ids": ["P08"],
        "coverage_notes": "Approximately one quarter of the ancient city lies beneath modern Harappa town (Kenoyer 1991, p. 57).",
    },
    {
        "campaign_id": "SC-SINGH-GHAGGAR-CORES",
        "name": "Singh et al. 2017 and 2021 Ghaggar-Hakra fluvial coring and OSL dating",
        "investigators": "Ajit Singh, Kristina J. Thomsen, Rajiv Sinha, Sanjeev Gupta and colleagues",
        "years": "2017, 2021",
        "region": "Kalibangan, Hanumangarh, Sirsa and Haryana foothill paleochannels, India",
        "method": "Deep sediment coring (36 to 51 m), OSL chronology, and provenance geochemistry",
        "source_ids": ["R15", "R16", "SC15"],
        "window_ids": ["P03", "P04", "P06"],
        "coverage_notes": "Eight held derived core locations (GS-7, GS-10, GS-11, GS-13, GS-14 near Kalibangan; KNL-1, MNK-6, SRH-5 in Haryana and Punjab). Establishes Sutlej diversion shortly after 8 ka and episodic foothill floods around 3.9 to 3.8 ka.",
    },
    {
        "campaign_id": "SC-GIOSAN-2012-FLUVIAL",
        "name": "Giosan et al. 2012 regional fluvial landscape reconstruction",
        "investigators": "Liviu Giosan, Peter D. Clift, Mark G. Macklin, Dorian Q. Fuller and colleagues",
        "years": "2012",
        "region": "Indus Basin from Punjab incised valleys through Sindh to the delta",
        "method": "SRTM elevation analysis, fluvial geomorphology, and OSL sediment dating",
        "source_ids": ["R17"],
        "window_ids": ["P08", "P11"],
        "coverage_notes": "Separates incised Punjab valleys, the stable upper Sindh Indus mega-ridge, and late Holocene burial in southwestern Sindh.",
    },
    {
        "campaign_id": "SC-MAHSA-HERITAGE-DB",
        "name": "Mapping Archaeological Heritage in South Asia (MAHSA)",
        "investigators": "Cameron A. Petrie and MAHSA consortium (Cambridge, Barcelona, partner institutions)",
        "years": "2020-2026",
        "region": "Indus River Basin and surrounding regions of India and Pakistan",
        "method": "Arches heritage database compiling legacy site inventories, Survey of India historical map digitization, and field verification",
        "source_ids": ["R13", "R14", "R27", "SPC10", "SPC11"],
        "window_ids": ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10", "P11", "P12", "P13"],
        "coverage_notes": "Approximately 10,000 all-period legacy entries reported in 2025. Bulk database not acquired; local API checks held for B02, B04, Hanumangarh, Pilibanga, and Juna Khatiya returned historical map sheet records (Cutch No. 6, Rajputana 44 P 01, Punjab/Rajputana 44 P 05) and no bulk site dump.",
    },
    {
        "campaign_id": "SC-SINDH-SUKKUR-RESCUE",
        "name": "Sindh Directorate of Antiquities and SALU urban rescue at Lakhanjo-daro and Rohri Hills",
        "investigators": "Shah Abdul Latif University, Directorate of Antiquities Government of Sindh, Paolo Biagi, Elisabetta Starnini",
        "years": "1985-2022",
        "region": "Sukkur SITE industrial estate and Rohri Hills, Sindh, Pakistan",
        "method": "Urban salvage trenching (including four 2017 trenches) and flint-quarry landscape survey",
        "source_ids": ["R21", "R22"],
        "window_ids": ["P10"],
        "coverage_notes": "Documents industrial truncation of upper deposits alongside surviving lower craft and seal-workshop contexts, plus Rohri Hills quarry landscapes.",
    },
    {
        "campaign_id": "SC-BISHT-ASI-KUTCH",
        "name": "ASI Kutch explorations and Dholavira excavations",
        "investigators": "J. P. Joshi (1967-1972); R. S. Bisht and ASI (1989-2005)",
        "years": "1967-2005",
        "region": "Khadir Island, Bela Bet, Surkotada and Kutch mainland, Gujarat, India",
        "method": "Regional surface reconnaissance and thirteen seasons of urban and cemetery excavation at Dholavira",
        "source_ids": ["R19", "R72"],
        "window_ids": ["P13"],
        "coverage_notes": "Anchors Kutch island-belt urbanism and early exploration of Lodrani, Surkotada, and Dholavira.",
    },
    {
        "campaign_id": "SC-KUTCH-KERALA-GIAP-NOGAP",
        "name": "University of Kerala, KSKV Kachchh, MSU Baroda, NoGAP and GIAP Kutch surveys and excavations",
        "investigators": "S. V. Rajesh, G. S. Abhayan, P. Ajithprasad, Francesc C. Conesa, Juan Jose Garcia-Granero and collaborators",
        "years": "2008-2026",
        "region": "Western Kutch (Juna Khatiya, Padta Bet, Lakhapar), Bela Bet (Kotada in Lodrani), and North Gujarat",
        "method": "CORONA and historical-map prospection, systematic pedestrian survey, cemetery and habitation excavation",
        "source_ids": ["R18", "R19", "R20", "R28", "SPC05", "SPC06"],
        "window_ids": ["P12", "P13", "P14"],
        "coverage_notes": "Documented Juna Khatiya cemetery, Padta Bet and Dwajagadh habitation sites, Lakhapar (2026 excavation), and Kotada in Lodrani (alias Morodharo, 2014-2024 explorations).",
    },
    {
        "campaign_id": "SC-CONESA-2014-NORTH-GUJARAT",
        "name": "Conesa et al. 2014 North Gujarat SAR landscape survey",
        "investigators": "Francesc C. Conesa, Marco Madella, P. Ajithprasad and colleagues",
        "years": "2014",
        "region": "Lower Banas, Saraswati and Rupen dune systems, North Gujarat, India",
        "method": "Multi-temporal SAR seasonal water mapping and NoGAP field integration",
        "source_ids": ["R18"],
        "window_ids": ["P14"],
        "coverage_notes": "Maps seasonal dune and interdune hydrology to target Holocene settlement surfaces.",
    },
    {
        "campaign_id": "SC-SAURASHTRA-KHAMBHAT-COASTAL",
        "name": "Saurashtra and Gulf of Khambhat coastal and estuarine investigations",
        "investigators": "S. R. Rao; Anjum Farooqui, A. S. Gaur, Vandana Prasad (2013); Archana Das et al. (2022); Ekta Gupta, V. N. Prabhakar (2024); Chintan Vedpathak et al. (2026); NIOT (2003)",
        "years": "1955-2026",
        "region": "Kaj, Kanjetar, Lothal, Vadgam, Nal corridor, Gulf of Khambhat, Gujarat, India",
        "method": "Coastal excavation, palynology, AMS-dated estuarine trenching, sea-level index-point synthesis, and offshore sonar/coring",
        "source_ids": ["R25", "R32", "R34", "R54", "R55", "R71"],
        "window_ids": ["P15", "P20"],
        "coverage_notes": "Establishes local marine-to-estuarine retreat downstream of Lothal (4150 +/- 230 BP to 3625 +/- 200 BP) and validates Lothal and Vadgam sea-level index points; offshore Gulf of Khambhat habitation remains unestablished.",
    },
    {
        "campaign_id": "SC-MAFI-BOLAN-KIRTHAR",
        "name": "French Archaeological Mission to the Indus Basin (MAFI) and DOAM surveys",
        "investigators": "Jean-Francois Jarrige, Monique Lechevallier, Aurore Didier, Benjamin Mutin, Pakistan DOAM, Government of Sindh",
        "years": "1974-2025",
        "region": "Bolan plain (Mehrgarh, Nausharo, Sibri), Chanhu-daro, and Kirthar piedmont (Ghazi Shah, Kai)",
        "method": "Long-term stratigraphic excavation, piedmont survey, archaeometry, and revised radiocarbon dating",
        "source_ids": ["R37", "R39", "R40", "R41", "R42", "R43", "R45", "R49"],
        "window_ids": ["P17", "P18"],
        "coverage_notes": "Anchors Bolan alluvial burial (Mehrgarh) and spring-adjacent piedmont sequences (Ghazi Shah); Kai natural cave lacks an authenticated Indus date.",
    },
    {
        "campaign_id": "SC-MAKRAN-BESENVAL-DALES",
        "name": "Makran coastal and Kech-Makran valley surveys",
        "investigators": "Aurel Stein; George F. Dales (1962); Roland Besenval (1987-1997); Aurore Didier (2014)",
        "years": "1928, 1960-1962, 1987-2014",
        "region": "Kech-Turbat valley (Miri Qalat) and Makran coast (Sutkagen-dor, Sotka Koh, Pasni)",
        "method": "Valley and coastal reconnaissance, stratigraphic excavation at Miri Qalat, tectonic uplift comparison",
        "source_ids": ["R26", "R48", "R50", "R64", "R65", "R66"],
        "window_ids": ["P16", "P21"],
        "coverage_notes": "Approximately 30 Kech-Makran valley sites documented within local traditions; tectonic uplift (1 to 3 m in 1945) and alluvial progradation shift former coastlines inland.",
    },
    {
        "campaign_id": "SC-BIAGI-SINDH-SIRANDA",
        "name": "Biagi coastal shell-midden and Lower Sindh surveys",
        "investigators": "Paolo Biagi and collaborators",
        "years": "1990s-2024",
        "region": "Siranda lake, Sonmiani lagoon, Las Bela, Lower Sindh, Pakistan",
        "method": "Coastal surface survey, shell-midden documentation, and conventional radiocarbon sampling",
        "source_ids": ["R31"],
        "window_ids": ["P19"],
        "coverage_notes": "Records shell middens, lithic scatters, and local stone structures; conventional shell dates lack standardized marine reservoir calibration in our held summary.",
    },
    {
        "campaign_id": "SC-SATPROSP-2026-BLOCKS",
        "name": "Project 2026-10-12 four-block satellite terrain screening",
        "investigators": "Indus Valley Script project (2026-10-12-satellite-prospection)",
        "years": "2026",
        "region": "Blocks B01 (Ganweriwala), B02 (Harappa), B03 (Juna Khatiya-Padta Bet), B04 (Kalibangan-Pilibanga)",
        "method": "Copernicus GLO-30 terrain prominence, ESA WorldCover masking, and multi-season Sentinel-2 L2A screening across 740 km2",
        "source_ids": ["D01", "D02", "D03", "D13"],
        "window_ids": ["P01", "P02", "P06", "P08", "P12"],
        "coverage_notes": "Reviewed 47 candidates: 42 rejected, 1 known (Kalibangan), 2 context (including B04-T0257 reserve), and 2 unverified screening leads (B01-T0115, B04-T0180). No field verification performed.",
    },
]

# Per-window survey-effort classification and absence interpretation (PROTOCOL.md Section 7)
WINDOW_SURVEY_METADATA = {
    "P01": {
        "survey_effort_class": "historical_map_and_remote_screening",
        "absence_interpretation": "High documented remote-sensing density (337 Orengo et al. 2020 clusters, 266 unmatched to earlier Cholistan lists), but ground-verified phase attributions and exact cluster coordinates are not held locally. Empty spaces inside P01 outside Mughal's Hakra survey corridor reflect unacquired records and sand-dune cover rather than confirmed absence.",
    },
    "P02": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Ganweriwala itself has 2007 and 2015 surface surveys plus 2024 excavation, and block B01 screened 200 km2 around the DOAM coordinate (retaining B01-T0115). Absence of recorded sites around Ganweriwala margins reflects dune cover and unacquired Cholistan coordinates rather than sterile ground.",
    },
    "P03": {
        "survey_effort_class": "intensive_ground_survey",
        "absence_interpretation": "Directly covered by Green et al. 2019 historical-map field checks and TwoRains work. Negative checked map features document local non-archaeological features, while off-map encounters (64 across the Green survey) show that unmapped flat or levelled sites remain under-sampled.",
    },
    "P04": {
        "survey_effort_class": "intensive_ground_survey",
        "absence_interpretation": "Covered by Green et al. 2019 historical-map checks and MAHSA digitization; agricultural levelling and stopping rules after ten negatives per grid cell limit inference of true settlement absence between checked symbols.",
    },
    "P05": {
        "survey_effort_class": "intensive_ground_survey",
        "absence_interpretation": "Covered by Green et al. 2019 checks; few corpus-inscribed sites fall inside the box because the inscription corpus tracks excavated major sites rather than regional surface scatters.",
    },
    "P06": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Kalibangan and Karanpura fall inside P06 (with Baror, Binjor, and Tarkhanewala Dera immediately west of 74.0 E), Singh et al. 2017 cored five GS boreholes near Kalibangan, and block B04 screened 196 km2 (retaining B04-T0180 and B04-T0257). Low recorded counts away from the paleochannel reflect alluvial burial, irrigated cultivation, and unacquired MAHSA site entries (local Hanumangarh API query returned map sheets only).",
    },
    "P07": {
        "survey_effort_class": "intensive_ground_survey",
        "absence_interpretation": "Intensively surveyed by Cambridge and BHU (127 all-period locations within 15 km of Rakhigarhi; Masudpur remapped into 13 mounds). Only a small subset of those 127 surveyed locations enters the inscription-focused gazetteer; low corpus counts reflect non-excavated rural mounds rather than unsurveyed territory.",
    },
    "P08": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Harappa is intensively excavated (HARP) and Garcia-Molsosa et al. 2023 compared 646 map features against 240 PAS sites across the floodplain, plus block B02 screened 144 km2. Apparent gaps on younger alluvial belts reflect channel scouring and burial rather than lack of protohistoric interest.",
    },
    "P09": {
        "survey_effort_class": "historical_map_and_remote_screening",
        "absence_interpretation": "Overlaps Garcia-Molsosa et al. 2023 map-extraction frame (P08/P09 shared landforms) and includes Multan's unexcavated early sequence; absence of corpus-inscribed Indus sites reflects lack of acquired PAS coordinates, younger alluvial reworking, and urban burial.",
    },
    "P10": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Contains excavated Kot Diji and salvage-trenched Lakhanjo-daro in the Sukkur SITE industrial zone (with Naru-Waro-dharo immediately west of 68.7 E) plus Biagi's Rohri Hills quarry surveys. Absence of surface finds inside Sukkur reflects industrial construction cover and truncation, not absence of ancient occupation.",
    },
    "P11": {
        "survey_effort_class": "reconnaissance_or_geomorphic_only",
        "absence_interpretation": "Contains major excavated sites along the margins (Amri, Chanhu-daro, Lohumjo-daro), while lower Sindh backswamps and migrating channels have only regional geomorphic synthesis (Giosan et al. 2012) and no systematic coring archive in our held records. Empty interior cells are unsurveyed or buried beneath late Holocene alluvium.",
    },
    "P12": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Active fieldwork by University of Kerala, KSKV Kachchh, and GIAP at Juna Khatiya, Padta Bet, Dwajagadh, and Lakhapar inside P12 (with Desalpar and Khirsara just south of 23.5 N), plus block B03 screening (200 km2) and held MAHSA historical map sheet Cutch No. 6. Gaps outside surveyed catchments remain untested for small habitation sites paired with cemeteries.",
    },
    "P13": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Anchored inside P13 by 2014-2024 explorations at Kotada in Lodrani (Morodharo) on Bela Bet, with ASI excavations at Dholavira, Pabumath, and Surkotada in adjacent Kutch blocks. Tributary margins outside known fortified mounds lack systematic published survey coverage in our held holdings.",
    },
    "P14": {
        "survey_effort_class": "historical_map_and_remote_screening",
        "absence_interpretation": "Covered by Conesa et al. 2014 SAR hydrology mapping and Nagwada excavation near the southern edge, but full NoGAP surface-survey site tables are not held locally. Empty interior cells reflect unacquired survey records and aeolian dune concealment.",
    },
    "P15": {
        "survey_effort_class": "reconnaissance_or_geomorphic_only",
        "absence_interpretation": "Anchored by Prabhas Patan and coastal excavations at Kaj and Kanjetar (Farooqui et al. 2013, coordinates unheld). Absence of recorded sites across intervening mid-Saurashtra estuaries reflects lack of systematic coastal-corridor survey data and Holocene shoreline shift.",
    },
    "P16": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Anchored by French excavations at Miri Qalat and Besenval's regional reconnaissance (~30 multi-period valley sites, individual coordinates not held). Empty cells reflect unacquired survey lists and flash-flood alluvial burial in tributary fans.",
    },
    "P17": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Anchored by French Mission excavations at Mehrgarh, Nausharo, Sibri, and Pirak. Fan margins away from the Bolan river-cut sections remain concealed beneath thick piedmont alluvium where surface survey has low detection probability.",
    },
    "P18": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Covered by MAFI Kirthar piedmont work, DOAM Ghazi Shah inventory, and Sindh 2015 cultural property inventory (including Kai cave). Piedmont fans and interfluves remain unevenly surveyed; absence of dated Indus cave occupation reflects lack of stratified dating rather than exhaustive testing.",
    },
    "P19": {
        "survey_effort_class": "reconnaissance_or_geomorphic_only",
        "absence_interpretation": "Anchored by Balakot and Bakkar Buthi plus Biagi's shell-midden reconnaissance around Siranda and Sonmiani (individual midden coordinates not held). Gaps reflect delta advance, dune cover, and unacquired survey tables.",
    },
    "P20": {
        "survey_effort_class": "targeted_excavation_and_local_survey",
        "absence_interpretation": "Anchored by Lothal, Rangpur, Kanewal, and recent estuarine coring and sea-level synthesis (Das et al. 2022; Gupta et al. 2024; Vedpathak et al. 2026). Low counts along buried paleochannels and offshore areas reflect estuarine siltation and submergence rather than confirmed absence.",
    },
    "P21": {
        "survey_effort_class": "reconnaissance_or_geomorphic_only",
        "absence_interpretation": "Anchored by Sutkagen-dor and Sotka Koh from Dales 1962 coastal reconnaissance and tectonic uplift observations at Pasni. Intervening Makran coastal terraces and inland paleoshorelines have no systematic modern survey inventory in our held records.",
    },
}

# Additional documented non-corpus Indus/survey localities (PROTOCOL.md Section 3)
EXTRA_PROSPECTION_LOCALITIES = [
    {
        "id": "padta-bet",
        "name": "Padta Bet",
        "alts": ["Padta-Bet"],
        "country": "India",
        "region": "Gujarat/Kutch",
        "province": "Gujarat",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "excavated",
        "has_excavation_record": True,
        "living_town_overlap": "none",
        "coords": [
            {
                "lat": 23.69645277777778,
                "lon": 68.97338055555555,
                "datum": "WGS84",
                "precision_class": "surveyed_sub_100m",
                "source_register": "2026-10-12-satellite-prospection",
                "source_citation": "SPC05 (Social Orbit 2020 table; 2019 field survey reference PAD-TABLE)",
                "evidence_status": "field-survey-reference",
                "selection_role": "primary_retained",
                "basis": "2019 Kutch field-team survey reference point for Padta Bet habitation site near Juna Khatiya.",
            }
        ],
        "physical_units": [
            {
                "unit_type": "settlement_mound",
                "label": "Padta Bet habitation mound",
                "extent_note": "Habitation settlement associated with Juna Khatiya Early Harappan cemetery catchment; total phase area not quantified in held extract.",
                "source_ids": ["R20", "SPC05"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Early and Mature Harappan regional association",
                "start_bce": None,
                "end_bce": None,
                "area_ha": None,
                "measurement_definition": "Chronological attribution from GIAP 2024 project notice and SPC05; phase-specific footprint not acquired.",
                "source_ids": ["R20", "SPC05"],
            }
        ],
        "excavated_deposits": [
            {
                "years": "2019-2024",
                "label": "Excavation and survey by University of Kerala, KSKV Kachchh University, and GIAP",
                "source": "GIAP 2024 announcement (R20) and Social Orbit 2020 table (SPC05)",
            }
        ],
        "survey_campaigns": ["SC-KUTCH-KERALA-GIAP-NOGAP", "SC-SATPROSP-2026-BLOCKS", "SC-MAHSA-HERITAGE-DB"],
        "source_registers": ["2026-10-12-satellite-prospection", "2026-10-11-settlement-prospection"],
    },
    {
        "id": "dwajagadh",
        "name": "Dwajagadh",
        "alts": ["Dhwajagadh"],
        "country": "India",
        "region": "Gujarat/Kutch",
        "province": "Gujarat",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "surface_surveyed",
        "has_excavation_record": False,
        "living_town_overlap": "none",
        "coords": [
            {
                "lat": 23.720469444444443,
                "lon": 68.97780555555556,
                "datum": "WGS84",
                "precision_class": "surveyed_sub_100m",
                "source_register": "2026-10-12-satellite-prospection",
                "source_citation": "SPC05 (Social Orbit 2020 table; 2019 field survey reference DWA-TABLE)",
                "evidence_status": "field-survey-reference",
                "selection_role": "primary_retained",
                "basis": "2019 Kutch field-team survey reference point in the Juna Khatiya-Padta Bet catchment.",
            }
        ],
        "physical_units": [
            {
                "unit_type": "surface_scatter_or_mound",
                "label": "Dwajagadh surveyed locality",
                "extent_note": "Recorded in 2019 Kutch survey table; dimensions not held locally.",
                "source_ids": ["SPC05"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Pre-Urban / Early Harappan Gujarat assessment",
                "start_bce": None,
                "end_bce": None,
                "area_ha": None,
                "measurement_definition": "Included in SPC05 Pre-Urban Harappan Gujarat table; no phase footprint acquired.",
                "source_ids": ["SPC05"],
            }
        ],
        "excavated_deposits": [],
        "survey_campaigns": ["SC-KUTCH-KERALA-GIAP-NOGAP", "SC-SATPROSP-2026-BLOCKS"],
        "source_registers": ["2026-10-12-satellite-prospection"],
    },
    {
        "id": "kotada-lodrani",
        "name": "Kotada (Lodrani)",
        "alts": ["Morodharo", "Kotda", "Kotada", "Lodrani"],
        "country": "India",
        "region": "Gujarat/Kutch",
        "province": "Gujarat",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "surface_surveyed",
        "has_excavation_record": False,
        "living_town_overlap": "none",
        "coords": [
            {
                "lat": 23.91377,
                "lon": 70.650247,
                "datum": "WGS84",
                "precision_class": "surveyed_sub_100m",
                "source_register": "2026-10-11-settlement-prospection",
                "source_citation": "Rajesh et al. 2025 (R19), Man and Environment, pp. 1 and 3: 23° 54' 49.5720\" N, 70° 39' 00.8892\" E (62 m AMSL)",
                "evidence_status": "field-survey-reference",
                "selection_role": "primary_retained",
                "basis": "Published GPS coordinate of Kotada in Lodrani on Bela Bet; identical coordinate cited for the 2024 Morodharo social-media announcement (Yadav 2024).",
            }
        ],
        "physical_units": [
            {
                "unit_type": "fortified_enclosure",
                "label": "Kotada stone fortification enclosure",
                "extent_note": "100 x 60 m fortified stone enclosure (0.6 ha) with internal well, located 280 m northwest of Sandhan stream; does not delimit the broader multi-period settlement.",
                "source_ids": ["R19"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Fortified enclosure footprint (structural feature, not full settlement)",
                "start_bce": None,
                "end_bce": None,
                "area_ha": 0.6,
                "measurement_definition": "100 x 60 m stone fortification perimeter only; broader Early/Mature Harappan and medieval scatter extent remains unmeasured.",
                "source_ids": ["R19"],
            },
            {
                "label": "Early and Mature Harappan ceramic and radiocarbon attribution plus brief medieval reoccupation",
                "start_bce": 3350,
                "end_bce": 1900,
                "area_ha": None,
                "measurement_definition": "Two radiocarbon dates plus Classical Harappan, Anarta, Reserved Slip Ware, and medieval surface ceramics reported in Rajesh et al. 2025.",
                "source_ids": ["R19"],
            },
        ],
        "excavated_deposits": [],
        "survey_campaigns": ["SC-BISHT-ASI-KUTCH", "SC-KUTCH-KERALA-GIAP-NOGAP", "SC-MAHSA-HERITAGE-DB"],
        "source_registers": ["2026-10-11-settlement-prospection"],
    },
    {
        "id": "ghazi-shah",
        "name": "Ghazi Shah",
        "alts": ["Ghazi Shah Mound", "Piyare-ji-Mari"],
        "country": "Pakistan",
        "region": "Lower Indus",
        "province": "Sindh",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "excavated",
        "has_excavation_record": True,
        "living_town_overlap": "none",
        "coords": [
            {
                "lat": 26.454762389,
                "lon": 67.464134722,
                "datum": "WGS84",
                "precision_class": "surveyed_sub_100m",
                "source_register": "2026-10-11-settlement-prospection",
                "source_citation": "Department of Archaeology and Museums, Pakistan (R41): Ghazi Shah inventory entry",
                "evidence_status": "government-inventory",
                "selection_role": "primary_retained",
                "basis": "Government inventory coordinate beside perennial spring at the Bhit Range foot, Dadu district.",
            }
        ],
        "physical_units": [
            {
                "unit_type": "settlement_mound",
                "label": "Ghazi Shah piedmont mound",
                "extent_note": "Inventory dimensions 160 x 130 m (approximately 2.08 ha) and 11 m height beside a perennial spring; inventory bounds, not a phase-specific boundary.",
                "source_ids": ["R41"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Amri and Mature Indus levels (inventory mound dimensions)",
                "start_bce": None,
                "end_bce": None,
                "area_ha": 2.08,
                "measurement_definition": "160 x 130 m mound dimensions from DOAM inventory (R41); phase-specific occupied areas remain separate.",
                "source_ids": ["R41", "R42"],
            }
        ],
        "excavated_deposits": [
            {
                "years": "1930s; 1985-1987; recent MAFI work reported 2025",
                "label": "N. G. Majumdar trials, Flam excavations, and recent MAFI archaeometric sampling",
                "source": "DOAM Pakistan (R41); MAFI / AIBL (R37); Syvilay et al. 2025 abstract (R42)",
            }
        ],
        "survey_campaigns": ["SC-MAFI-BOLAN-KIRTHAR"],
        "source_registers": ["2026-10-11-settlement-prospection"],
    },
    {
        "id": "lakhapar",
        "name": "Lakhapar",
        "alts": [],
        "country": "India",
        "region": "Gujarat/Kutch",
        "province": "Gujarat",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "excavated",
        "has_excavation_record": True,
        "living_town_overlap": "unknown",
        "coords": [],
        "physical_units": [
            {
                "unit_type": "settlement_mound",
                "label": "Lakhapar excavated locality",
                "extent_note": "Exact site coordinates and footprint not held in local acquisition.",
                "source_ids": ["R28"],
            }
        ],
        "phase_footprints": [],
        "excavated_deposits": [
            {
                "years": "2026",
                "label": "Excavation by Assumption College and University of Kerala field program",
                "source": "Assumption College / University of Kerala 2026 field program notice (R28)",
            }
        ],
        "survey_campaigns": ["SC-KUTCH-KERALA-GIAP-NOGAP"],
        "source_registers": ["2026-10-11-settlement-prospection"],
        "window_override": ["P12"],
    },
    {
        "id": "bahola",
        "name": "Bahola",
        "alts": ["BHA"],
        "country": "India",
        "region": "Eastern Headwaters",
        "province": "Haryana",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "excavated",
        "has_excavation_record": True,
        "living_town_overlap": "unknown",
        "coords": [],
        "physical_units": [
            {
                "unit_type": "village_mound",
                "label": "Bahola small village mound",
                "extent_note": "1 to 2 ha small village site in Karnal district, Haryana (Bates et al. 2017, p. 10); exact coordinates not printed in held paper.",
                "source_ids": ["R24"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Late Harappan and Painted Grey Ware occupation",
                "start_bce": 1900,
                "end_bce": 1300,
                "area_ha": 1.5,
                "measurement_definition": "Midpoint reference note for reported 1 to 2 ha mound size in Bates et al. 2017 (R24); range 1-2 ha retained in note.",
                "source_ids": ["R24"],
            }
        ],
        "excavated_deposits": [
            {
                "years": "2012",
                "label": "Land, Water and Settlement survey, excavation, and flotation (30 macrobotanical contexts)",
                "source": "Bates, Petrie and Singh 2017 (R24)",
            }
        ],
        "survey_campaigns": ["SC-PETRIE-LWS-TWORAINS"],
        "source_registers": ["2026-10-11-settlement-prospection"],
    },
    {
        "id": "kaj",
        "name": "Kaj",
        "alts": [],
        "country": "India",
        "region": "Gujarat/Kutch",
        "province": "Gujarat",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "excavated",
        "has_excavation_record": True,
        "living_town_overlap": "unknown",
        "coords": [],
        "physical_units": [
            {
                "unit_type": "coastal_settlement",
                "label": "Kaj coastal and lacustrine Harappan locality",
                "extent_note": "Mid-Saurashtra coastal sequence; exact coordinates not held locally.",
                "source_ids": ["R25"],
            }
        ],
        "phase_footprints": [],
        "excavated_deposits": [
            {
                "years": "before 2013",
                "label": "Excavation and palynological environmental study",
                "source": "Farooqui, Gaur and Prasad 2013 (R25)",
            }
        ],
        "survey_campaigns": ["SC-SAURASHTRA-KHAMBHAT-COASTAL"],
        "source_registers": ["2026-10-11-settlement-prospection"],
        "window_override": ["P15"],
    },
    {
        "id": "kanjetar",
        "name": "Kanjetar",
        "alts": [],
        "country": "India",
        "region": "Gujarat/Kutch",
        "province": "Gujarat",
        "unit_class": "recorded_locality",
        "domain_role": "indus_prospection_or_survey_locality",
        "excavation_status": "excavated",
        "has_excavation_record": True,
        "living_town_overlap": "unknown",
        "coords": [],
        "physical_units": [
            {
                "unit_type": "coastal_settlement",
                "label": "Kanjetar coastal Harappan locality",
                "extent_note": "Mid-Saurashtra coastal sequence; exact coordinates not held locally.",
                "source_ids": ["R25"],
            }
        ],
        "phase_footprints": [],
        "excavated_deposits": [
            {
                "years": "before 2013",
                "label": "Excavation and palynological environmental study",
                "source": "Farooqui, Gaur and Prasad 2013 (R25)",
            }
        ],
        "survey_campaigns": ["SC-SAURASHTRA-KHAMBHAT-COASTAL"],
        "source_registers": ["2026-10-11-settlement-prospection"],
        "window_override": ["P15"],
    },
]

# Unverified remote-sensing mound clusters (PROTOCOL.md Sections 2, 3, 6)
ORENGO_REMOTE_PROPOSALS = [
    {
        "id": "khundowala",
        "name": "Khundowala",
        "alts": [],
        "country": "Pakistan",
        "region": "Inter-Riverine",
        "province": "Punjab",
        "area_ha": 29.0,
        "note": "Remote-sensing mound cluster (~29 ha) proposed by Orengo et al. 2020 (R08), named after nearest historical-map toponym; exact coordinates not published in held witness; period and archaeological identity untested.",
        "window_override": ["P01"],
    },
    {
        "id": "mulhiawala",
        "name": "Mulhiawala",
        "alts": [],
        "country": "Pakistan",
        "region": "Inter-Riverine",
        "province": "Punjab",
        "area_ha": 20.5,
        "note": "Remote-sensing mound cluster (~20.5 ha) in southeastern margin of Cholistan proposed by Orengo et al. 2020 (R08); exact coordinates not published in held witness; period and archaeological identity untested.",
        "window_override": ["P01"],
    },
]

# Explicit supplementary aliases & homonym disambiguation rules (PROTOCOL.md Section 4)
SUPPLEMENTARY_ALIASES = [
    ("kotada-lodrani", "Morodharo", "rediscovery_name", ["2026-10-11-settlement-prospection"], False, "2024 social-media rediscovery name for the already-documented Kotada in Lodrani fortified settlement (Rajesh et al. 2025, R19)."),
    ("kotada-lodrani", "Kotda", "spelling_variant", ["2026-10-11-settlement-prospection"], True, "Kutchi fortified-mound toponym; distinguish from Dholavira (Kotada) and Kotada Bhadli."),
    ("kotada-lodrani", "Kotada", "ambiguous_toponym", ["2026-10-11-settlement-prospection"], True, "Toponym on 1884-85 Survey of India map for Lodrani, Bela Bet; homonymous with Dholavira (Kotada) on Khadir Island."),
    ("kotada-lodrani", "Lodrani", "modern_municipality_context", ["2026-10-11-settlement-prospection"], False, "Village name containing Kotada and multiple other archaeological localities in Bela Bet."),
    ("dholavira", "Kotada", "ambiguous_toponym", ["2026-10-26-indus-living-atlas", "2026-10-11-settlement-prospection"], True, "Local fortified-mound toponym for Dholavira on Khadir Island; homonymous with Kotada (Lodrani) on Bela Bet."),
    ("gola-dhoro-bagasra", "gola-dhoro", "catalogue_code", ["2026-10-24-q1032-town-axis-register"], False, "Town slug in Q-1032 register, now reconciled with Atlas entity gola-dhoro-bagasra."),
    ("gola-dhoro-bagasra", "Bagasra", "local_mound_name", ["2026-10-26-indus-living-atlas", "2026-10-21-post-catalogue-finds"], True, "Village in Maliya Taluka, Morbi district near Gola Dhoro; do not confuse with Bagasara town in Amreli district (21.4833 N, 70.9500 E, 178 km south)."),
    ("gola-dhoro-bagasra", "Gola Dhoro", "local_mound_name", ["2026-10-26-indus-living-atlas", "2026-10-24-q1032-town-axis-register"], False, "Excavated archaeological mound near Bagasra village."),
    ("ropar-rupar", "Rupnagar / Ropar", "modern_municipality_context", ["2026-10-26-indus-living-atlas-living-towns"], False, "Living-town record LT-11 reconciled with Atlas site ropar-rupar."),
    ("ropar-rupar", "Rupnagar", "modern_municipality_context", ["2026-10-26-indus-living-atlas", "2026-10-11-settlement-prospection"], False, "Modern Punjab district town surrounding the protected Ropar mound."),
    ("ropar-rupar", "Rupar", "spelling_variant", ["2026-10-26-indus-living-atlas", "2026-10-21-post-catalogue-finds", "2026-10-06-evidence-census"], False, "Standard archaeological spelling in CISI and post-catalogue finds."),
    ("chanhu-daro", "Chanhujo-daro", "spelling_variant", ["2026-10-26-indus-living-atlas", "lipi-and-website-corpora"], False, "Variant spelling used in the older Indus website SQL export and Lipi reconciliation."),
    ("lakhanjo-daro", "Lakhian jo Daro", "spelling_variant", ["2026-10-11-settlement-prospection"], False, "Spelling used by Directorate of Antiquities, Government of Sindh (R21)."),
    ("lakhanjo-daro", "Sukkur", "modern_municipality_context", ["2026-10-11-settlement-prospection"], True, "Modern city and SITE industrial estate enclosing Lakhanjo-daro; municipal name is broader than the ancient site."),
    ("desalpar", "desalpur", "catalogue_code", ["2026-10-24-q1032-town-axis-register"], False, "Town slug in Q-1032 register, now reconciled with Atlas entity desalpar."),
    ("desalpar", "Desalpur", "spelling_variant", ["2026-10-26-indus-living-atlas", "2026-10-06-evidence-census", "2026-10-24-q1032-town-axis-register"], True, "Do not confuse with Wikidata Desalpur village at 23.1983 N, 69.4419 E (~40 km SE of the Desalpar-Gunthli mound)."),
    ("shikarpur", "Valamio Timbo", "local_mound_name", ["2026-10-24-q1032-town-axis-register"], False, "Local name of the excavated Harappan mound near Shikarpur, Bhachau, Kutch."),
    ("shikarpur", "Valmio Timbo", "spelling_variant", ["2026-10-24-q1032-town-axis-register"], False, "Variant spelling in Bhan and Ajithprasad 2007-2008 report, p. 3."),
    ("tarkhanewala-dera", "Chak 86", "subsite_mound_name", ["2026-10-24-q1032-town-axis-register"], False, "Paired adjacent locality in Trivedi 2009 excavation report (PDF p. 23)."),
    ("rakhigarhi", "Rakhi-Shahpur", "modern_municipality_context", ["2026-10-11-settlement-prospection"], False, "Modern village overlying part of Rakhigarhi mounds (R62)."),
    ("rakhigarhi", "Rakhi-Khas", "modern_municipality_context", ["2026-10-11-settlement-prospection"], False, "Modern village overlying part of Rakhigarhi mounds (R62)."),
    ("manda", "Akhnoor Fort", "modern_municipality_context", ["2026-10-11-settlement-prospection"], False, "Fort overlying the Manda archaeological sequence (R67)."),
    ("indiranagar-kanpur", "Kanpur (Indiranagar mound)", "local_mound_name", ["2026-10-21-post-catalogue-finds"], False, "Published label in Man and Environment 32 (2007), p. 120."),
]

# Documented multi-definition area/physical-unit notes (PROTOCOL.md Section 2)
SPECIAL_UNIT_ENRICHMENTS = {
    "ganweriwala": {
        "physical_units": [
            {
                "unit_type": "settlement_mound_complex",
                "label": "Ganweriwala mounded and dune-covered complex",
                "extent_note": "Partially covered by sand dunes; visible mounded core ~33 ha (Orengo et al. 2020) inside broader 66.7 ha surface cultural-material spread (Gulzar 2018).",
                "source_ids": ["R07", "R08"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Legacy published site area estimate",
                "start_bce": None,
                "end_bce": None,
                "area_ha": 81.5,
                "measurement_definition": "Historical area figure cited in Gulzar 2018 (R07) with uncertain boundary procedure; not directly comparable to visible mound area.",
                "source_ids": ["R07"],
            },
            {
                "label": "December 2015 surface cultural-material spread",
                "start_bce": None,
                "end_bce": None,
                "area_ha": 66.7,
                "measurement_definition": "Total-station surface spread of cultural material measured by Sidra Gulzar (2018, R07).",
                "source_ids": ["R07"],
            },
            {
                "label": "2020 satellite-visible mounded area",
                "start_bce": None,
                "end_bce": None,
                "area_ha": 33.0,
                "measurement_definition": "Visible mounded surface area reported in Orengo et al. 2020 (R08); excludes dune-buried margins.",
                "source_ids": ["R08"],
            },
        ],
    },
    "masudpur": {
        "physical_units": [
            {
                "unit_type": "multi_mound_cluster",
                "label": "Masudpur 13 mapped mounds (including Masudpur I / Sampolia Khera ~6 ha and Masudpur VII / Bhimwada Jodha ~1 ha)",
                "extent_note": "Cambridge 2009 season remapped 4 legacy mounds listed at one coordinate into 13 discrete mapped mounds (3.25x unit split); not 13 simultaneous villages.",
                "source_ids": ["R24", "R29"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Masudpur I (Sampolia Khera) Mature Harappan mound",
                "start_bce": 2500,
                "end_bce": 1900,
                "area_ha": 6.0,
                "measurement_definition": "Large village mound area reported in Bates et al. 2017 (R24, p. 9).",
                "source_ids": ["R24"],
            },
            {
                "label": "Masudpur VII (Bhimwada Jodha) Early-Mature-Late Harappan mound",
                "start_bce": 3200,
                "end_bce": 1300,
                "area_ha": 1.0,
                "measurement_definition": "Small village mound area reported in Bates et al. 2017 (R24, p. 9).",
                "source_ids": ["R24"],
            },
        ],
    },
    "shortughai": {
        "physical_units": [
            {
                "unit_type": "settlement_mound",
                "label": "Shortughai mounded area (~2.5 ha)",
                "extent_note": "DAFA account reports 2.5 ha site area with 993 m2 opened across 1976-1979 excavations (~90,000 sherds).",
                "source_ids": ["R69"],
            }
        ],
        "phase_footprints": [
            {
                "label": "Shortughai overall settlement area (DAFA)",
                "start_bce": None,
                "end_bce": None,
                "area_ha": 2.5,
                "measurement_definition": "Total reported mound area (2.5 ha) vs 993 m2 excavated exposure (3.97% opened) in DAFA account (R69).",
                "source_ids": ["R69"],
            }
        ],
    },
    "lakhanjo-daro": {
        "physical_units": [
            {
                "unit_type": "urban_salvage_mounds",
                "label": "Lakhanjo-daro mounds within Sukkur SITE industrial estate",
                "extent_note": "Modern industrial buildings and pits disturbed upper strata while lower craft and seal-workshop contexts survive locally; unauthenticated 300 ha figure is not adopted as a measured phase footprint.",
                "source_ids": ["R21"],
            }
        ],
        "phase_footprints": [],
    },
    "mohenjo-daro": {
        "physical_units": [
            {
                "unit_type": "urban_mound_and_subsurface_deposits",
                "label": "Mohenjo-daro exposed mounds plus buried plain deposits to 11.9 m depth",
                "extent_note": "Dales 1965 borings recovered cultural debris to 39 ft (~11.9 m) below surrounding plain, with 1965 water table around 15 ft below plain.",
                "source_ids": ["R04", "R61"],
            }
        ],
        "phase_footprints": [],
    },
    "dholavira": {
        "physical_units": [
            {
                "unit_type": "walled_urban_and_cemetery_complex",
                "label": "Dholavira walled city (Citadel, Middle Town, Lower Town, reservoirs) and western cemetery",
                "extent_note": "Thirteen ASI excavation seasons (1989-2005); UNESCO record documents conserved architectural exposures on Khadir Island.",
                "source_ids": ["R72"],
            }
        ],
        "phase_footprints": [],
    },
    "harappa": {
        "physical_units": [
            {
                "unit_type": "multi_mound_urban_complex",
                "label": "Harappa mounds (AB, E, ET, F, Cemetery R-37, Cemetery H) plus modern town overlap",
                "extent_note": "Brick quarrying for Lahore-Multan railway damaged upper structures; approximately one quarter of ancient settlement lies beneath modern Harappa town (Kenoyer 1991, p. 57).",
                "source_ids": ["R30", "R63"],
            }
        ],
        "phase_footprints": [],
    },
    "rakhigarhi": {
        "physical_units": [
            {
                "unit_type": "multi_mound_urban_complex",
                "label": "Rakhigarhi mounds (RGR-1 through RGR-7) partly under Rakhi-Shahpur and Rakhi-Khas villages",
                "extent_note": "Modern villages overlie portions of the archaeological mound complex (R62); 127 all-period locations surveyed within a 15 km radius (R29).",
                "source_ids": ["R29", "R62"],
            }
        ],
        "phase_footprints": [],
    },
    "shikarpur": {
        "physical_units": [
            {
                "unit_type": "settlement_mound",
                "label": "Valamio Timbo oval wooded mound",
                "extent_note": "Approximately 190 x 220 m (~4 ha) mound south of National Highway 41 (Q-1032 visual inspection and Bhan & Ajithprasad 2007-08).",
                "source_ids": ["Q-1032"],
            }
        ],
        "phase_footprints": [],
    },
    "banawali": {
        "physical_units": [
            {
                "unit_type": "settlement_mound",
                "label": "Banawali protected oval mound",
                "extent_note": "Approximately 250 x 260 m (~6 ha) grass-covered protected mound located at 29.5984 N, 75.3923 E in Q-1032 imagery checks.",
                "source_ids": ["Q-1032"],
            }
        ],
        "phase_footprints": [],
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_alias(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    ascii_only = ascii_only.lower().strip()
    ascii_only = re.sub(r"['’`\".,()\[\]]", " ", ascii_only)
    ascii_only = re.sub(r"[-_/]+", " ", ascii_only)
    ascii_only = re.sub(r"\s+", " ", ascii_only).strip()
    return ascii_only


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_km = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * r_km * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def point_in_bbox(lat: float, lon: float, bbox: list[float]) -> bool:
    min_lon, min_lat, max_lon, max_lat = bbox
    return (min_lon <= lon <= max_lon) and (min_lat <= lat <= max_lat)


def bbox_overlaps(b1: list[float], b2: list[float]) -> bool:
    return not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1])


def infer_atlas_precision(lat: float | None, lon: float | None, coord_kind: str, coord_note: str) -> str:
    if lat is None or lon is None:
        return "unlocated"
    note_l = (coord_note or "").lower()
    if "approximate" in (coord_kind or "").lower() or "approximate" in note_l:
        return "gazetteer_unquantified"
    if "gazetteer" in (coord_kind or "").lower():
        return "gazetteer_unquantified"
    # Check if rounded to 2 decimals or arcminute (multiples of 1/60)
    if abs(lat * 60 - round(lat * 60)) < 1e-3 and abs(lon * 60 - round(lon * 60)) < 1e-3:
        if abs(lat * 3600 - round(lat * 3600)) < 1e-2 and (abs(lat * 60 - round(lat * 60)) < 1e-4):
            return "catalogued_arcminute"
    return "catalogued_arcsecond"


def infer_q1032_precision(status: str, basis: str) -> str:
    b_l = (basis or "").lower()
    if status == "observed-image-location" or "mound centre read on the imagery" in b_l or "centre of the walled enclosure" in b_l or "corrected site identified" in b_l:
        return "image_located_site"
    if "arcminute" in b_l or "approximate published coordinates" in b_l or "coarse precision" in b_l:
        return "catalogued_arcminute"
    if "approximate report coordinate" in b_l:
        return "gazetteer_unquantified"
    return "catalogued_arcsecond"


def classify_atlas_excavation_status(site_id: str, fieldwork: list[dict[str, Any]]) -> tuple[str, bool, str]:
    if site_id in BURIED_UNDER_LIVING_TOWN_IDS:
        return "buried_under_living_town", BURIED_UNDER_LIVING_TOWN_IDS[site_id], "predominantly_buried_under_living_town"

    if site_id in PARTIAL_LIVING_TOWN_OVERLAP_IDS:
        lt_overlap = "partial_modern_overlap"
    elif site_id in NEARBY_DISTINCT_SETTLEMENT_IDS:
        lt_overlap = "nearby_distinct_settlement"
    else:
        lt_overlap = "none"

    if site_id in UNKNOWN_ATLAS_IDS:
        return "unknown", False, "unknown" if site_id in REGIONAL_PROVENANCE_IDS else lt_overlap
    if site_id in SURFACE_SURVEYED_ATLAS_IDS:
        return "surface_surveyed", False, lt_overlap
    if site_id in EXCAVATED_ATLAS_OVERRIDE_IDS:
        return "excavated", True, lt_overlap

    fw_text = " ".join((fw.get("label", "") + " " + fw.get("years", "")) for fw in fieldwork).lower()
    if any(w in fw_text for w in ("excavat", "trench", "trial", "cutting", "campaign", "season", "test pit", "dig")):
        return "excavated", True, lt_overlap
    if any(w in fw_text for w in ("survey", "explor", "surface", "discovered")):
        return "surface_surveyed", False, lt_overlap
    return "unknown", False, lt_overlap


def add_coord_assertion(
    assertions: list[dict[str, Any]],
    *,
    lat: float | None,
    lon: float | None,
    datum: str,
    precision_class: str,
    source_register: str,
    source_citation: str,
    evidence_status: str,
    selection_role: str,
    basis: str,
) -> None:
    if lat is None or lon is None:
        return
    lat_f = round(float(lat), 6)
    lon_f = round(float(lon), 6)
    for existing in assertions:
        if (
            abs(existing["lat"] - lat_f) < 1e-6
            and abs(existing["lon"] - lon_f) < 1e-6
            and existing["source_register"] == source_register
            and existing["evidence_status"] == evidence_status
        ):
            existing["source_occurrences"] += 1
            if source_citation and source_citation not in existing["source_citation"]:
                existing["source_citation"] = existing["source_citation"] + "; " + source_citation
            return
    assertions.append(
        {
            "lat": lat_f,
            "lon": lon_f,
            "datum": datum,
            "precision_class": precision_class,
            "source_register": source_register,
            "source_citation": source_citation,
            "evidence_status": evidence_status,
            "selection_role": selection_role,
            "basis": basis,
            "source_occurrences": 1,
        }
    )


def compute_coord_conflict_metrics(
    assertions: list[dict[str, Any]],
    documented_conflict_warning: bool,
) -> dict[str, Any]:
    if not assertions:
        return {
            "assertion_count": 0,
            "distinct_point_count": 0,
            "max_coord_spread_km": None,
            "active_coord_spread_km": None,
            "has_coordinate_conflict": documented_conflict_warning,
            "coord_conflict_tier": "documented_unquantified_conflict" if documented_conflict_warning else "unlocated",
            "max_spread_pair": None,
        }
    distinct_pts = sorted({(a["lat"], a["lon"]) for a in assertions})
    active_assertions = [a for a in assertions if a["selection_role"] != "excluded_retained"]

    max_d = 0.0
    max_pair = None
    for i in range(len(assertions)):
        for j in range(i + 1, len(assertions)):
            d = haversine_km(assertions[i]["lat"], assertions[i]["lon"], assertions[j]["lat"], assertions[j]["lon"])
            if d > max_d:
                max_d = d
                max_pair = [
                    {
                        "lat": assertions[i]["lat"],
                        "lon": assertions[i]["lon"],
                        "source_register": assertions[i]["source_register"],
                        "selection_role": assertions[i]["selection_role"],
                    },
                    {
                        "lat": assertions[j]["lat"],
                        "lon": assertions[j]["lon"],
                        "source_register": assertions[j]["source_register"],
                        "selection_role": assertions[j]["selection_role"],
                    },
                ]

    active_max_d = 0.0
    for i in range(len(active_assertions)):
        for j in range(i + 1, len(active_assertions)):
            d = haversine_km(
                active_assertions[i]["lat"],
                active_assertions[i]["lon"],
                active_assertions[j]["lat"],
                active_assertions[j]["lon"],
            )
            if d > active_max_d:
                active_max_d = d

    max_d = round(max_d, 3)
    active_max_d = round(active_max_d, 3)

    if len(assertions) == 1:
        tier = "documented_unquantified_conflict" if documented_conflict_warning else "single_assertion"
    elif max_d >= 1.0:
        tier = "material_conflict_ge_1km"
    elif max_d >= 0.1:
        tier = "minor_offset_0.1_to_1km"
    else:
        tier = "documented_unquantified_conflict" if documented_conflict_warning else "consistent_lt_0.1km"

    has_conflict = documented_conflict_warning or (max_d >= 1.0)
    return {
        "assertion_count": len(assertions),
        "distinct_point_count": len(distinct_pts),
        "max_coord_spread_km": max_d,
        "active_coord_spread_km": active_max_d,
        "has_coordinate_conflict": has_conflict,
        "coord_conflict_tier": tier,
        "max_spread_pair": max_pair if max_d > 0 else None,
    }


def main() -> None:
    # 1. Verify and hash all inputs
    input_manifest = {}
    for key, path in sorted(INPUT_PATHS.items()):
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path}")
        rel = path.relative_to(ROOT).as_posix()
        entry = {
            "logical_path": rel,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        if rel.startswith("data/raw/"):
            entry["physical_path"] = str(Path(r"D:\projects\indus_valley_script") / Path(rel))
        input_manifest[key] = entry

    atlas_data = load_json(INPUT_PATHS["atlas_data"])
    living_towns = load_json(INPUT_PATHS["living_towns"])
    q1032_data = load_json(INPUT_PATHS["q1032_towns"])
    census_cov = load_json(INPUT_PATHS["census_coverage"])
    census_sreg = load_json(INPUT_PATHS["census_site_register"])
    prosp_cand = load_json(INPUT_PATHS["prospection_candidates"])
    prosp_sources = load_json(INPUT_PATHS["prospection_sources"])
    sat_atlas = load_json(INPUT_PATHS["satellite_atlas"])
    sat_blocks_v1 = load_json(INPUT_PATHS["satellite_blocks_v1"])
    sat_blocks_v2 = load_json(INPUT_PATHS["satellite_blocks_v2"])
    orengo_aoi = load_json(INPUT_PATHS["orengo_aoi"])
    singh_cores = load_json(INPUT_PATHS["singh_cores"])
    rajesh_pages = load_json(INPUT_PATHS["rajesh_2025"])

    with INPUT_PATHS["post_catalogue_sites"].open(encoding="utf-8") as f:
        pcf_sites_rows = [r for r in csv.DictReader(f) if r["site"] != "All sites"]
    with INPUT_PATHS["post_catalogue_objects"].open(encoding="utf-8") as f:
        pcf_objects_rows = list(csv.DictReader(f))
    with INPUT_PATHS["satellite_recon"].open(encoding="utf-8") as f:
        sat_recon_rows = list(csv.DictReader(f))

    mahsa_files = {
        "B02_mapquery": load_json(INPUT_PATHS["mahsa_b02"]),
        "B04_mapquery": load_json(INPUT_PATHS["mahsa_b04"]),
        "Hanumangarh_stringquery": load_json(INPUT_PATHS["mahsa_hanumangarh"]),
        "Pilibanga_stringquery": load_json(INPUT_PATHS["mahsa_pilibanga"]),
        "Juna_Khatiya_terms": load_json(INPUT_PATHS["mahsa_juna_khatiya"]),
    }

    # Index helper tables
    q1032_by_canonical = {}
    for t in q1032_data["towns"]:
        cid = Q1032_TO_CANONICAL.get(t["town"], t["town"])
        q1032_by_canonical[cid] = t

    census_by_name = {s["site"]: s for s in census_cov["sites"]}
    sreg_by_canonical = {}
    atlas_name_to_id = {s["name"]: s["id"] for s in atlas_data["sites"]}
    for sr in census_sreg["sites"]:
        if sr["site"] == "Unknown":
            continue
        cid = SITE_REGISTER_SPELLING_TO_CANONICAL.get(sr["site"], atlas_name_to_id.get(sr["site"]))
        if cid:
            sreg_by_canonical.setdefault(cid, []).append(sr)

    pcf_by_canonical = {}
    for r in pcf_sites_rows:
        cid = POST_CATALOGUE_SITE_TO_CANONICAL[r["site"]]
        pcf_by_canonical[cid] = r

    lt_by_canonical = {}
    for r in living_towns["records"]:
        cid = LIVING_TOWN_TO_CANONICAL[r["id"]]
        lt_by_canonical[cid] = r

    sat_sources_by_id = {s["id"]: s for s in sat_atlas["sources"]}
    sat_refs_by_canonical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feat in sat_atlas["feature_collection"]["features"]:
        props = feat["properties"]
        fid = props.get("id")
        if fid in SAT_REF_TO_CANONICAL:
            sat_refs_by_canonical[SAT_REF_TO_CANONICAL[fid]].append(feat)

    # Write local-only raw provenance extract under D: (data/raw/2026-11-22-site-survey-gazetteer/)
    RAW_OUT_DIR.mkdir(parents=True, exist_ok=True)
    rajesh_list = rajesh_pages["pages"] if isinstance(rajesh_pages, dict) and "pages" in rajesh_pages else rajesh_pages
    rajesh_p1 = next((p["text"][:450] for p in rajesh_list if p.get("pdf_page") == 1), "")
    orengo_coords = orengo_aoi["features"][0]["geometry"]["coordinates"][0]
    orengo_bbox = [
        round(min(c[0] for c in orengo_coords), 6),
        round(min(c[1] for c in orengo_coords), 6),
        round(max(c[0] for c in orengo_coords), 6),
        round(max(c[1] for c in orengo_coords), 6),
    ]
    mahsa_probe_summary = {}
    for label, payload in mahsa_files.items():
        if "results" in payload and isinstance(payload["results"], dict):
            hits = payload["results"].get("hits", {}).get("hits", [])
            hit_items = []
            for h in hits:
                src = h.get("_source", {})
                pts = [p.get("point") for p in (src.get("points") or []) if isinstance(p, dict) and p.get("point")]
                hit_items.append({"resource_id": h.get("_id"), "displayname": src.get("displayname"), "points": pts})
            mahsa_probe_summary[label] = {
                "total_results": payload.get("total_results", len(hits)),
                "hits": hit_items,
            }
        else:
            mahsa_probe_summary[label] = {
                "terms_count": len(payload.get("terms") or []),
                "terms": [t.get("text") for t in (payload.get("terms") or [])],
            }

    raw_extract_payload = {
        "schema_version": SCHEMA_VERSION,
        "created_date": BUILD_DATE,
        "storage_note": "Local-only raw concordance extract; kept out of Git per knowledge/provenance/REDISTRIBUTION.md.",
        "logical_path": "data/raw/2026-11-22-site-survey-gazetteer/raw-concordance-extract-v1.json",
        "physical_path": str(PHYSICAL_RAW_PREFIX / "raw-concordance-extract-v1.json"),
        "input_hashes": input_manifest,
        "orengo_aoi_bbox_lonlat": orengo_bbox,
        "orengo_aoi_vertex_count": len(orengo_coords),
        "singh_cores_count": len(singh_cores["points"]),
        "singh_cores": singh_cores["points"],
        "mahsa_probes": mahsa_probe_summary,
        "rajesh_2025_page1_excerpt": rajesh_p1,
    }
    raw_extract_path = RAW_OUT_DIR / "raw-concordance-extract-v1.json"
    raw_extract_path.write_text(json.dumps(raw_extract_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 2. Build reconciled records
    records: list[dict[str, Any]] = []
    alias_entries: dict[tuple[str, str], dict[str, Any]] = {}

    def register_alias(
        canonical_id: str,
        canonical_name: str,
        alias_string: str,
        relation: str,
        sources: list[str],
        ambiguous: bool = False,
        note: str = "",
    ) -> None:
        cleaned = alias_string.strip()
        if not cleaned:
            return
        key = (canonical_id, cleaned)
        if key not in alias_entries:
            alias_entries[key] = {
                "canonical_id": canonical_id,
                "canonical_name": canonical_name,
                "alias_string": cleaned,
                "normalized_alias": normalize_alias(cleaned),
                "alias_relation": relation,
                "source_registers": sorted(set(sources)),
                "ambiguous_homonym": ambiguous,
                "disambiguation_note": note,
            }
        else:
            existing = alias_entries[key]
            existing["source_registers"] = sorted(set(existing["source_registers"]) | set(sources))
            if ambiguous:
                existing["ambiguous_homonym"] = True
            if note and note not in existing["disambiguation_note"]:
                existing["disambiguation_note"] = (existing["disambiguation_note"] + " " + note).strip()
            # Prefer specific relation over generic spelling_variant
            if existing["alias_relation"] == "spelling_variant" and relation != "spelling_variant":
                existing["alias_relation"] = relation

    # 2A. Process 115 Living Atlas / Evidence Census entities
    for s in atlas_data["sites"]:
        cid = s["id"]
        name = s["name"]
        unit_class = "regional_provenance_label" if cid in REGIONAL_PROVENANCE_IDS else "recorded_locality"
        source_regs = ["2026-10-26-indus-living-atlas", "2026-10-06-evidence-census"]
        if cid in sreg_by_canonical:
            source_regs.append("2026-10-06-evidence-census-site-register")

        # Register canonical name + atlas alts
        register_alias(cid, name, name, "canonical_name", ["2026-10-26-indus-living-atlas", "2026-10-06-evidence-census"])
        for alt in s.get("alts") or []:
            rel = "catalogue_code" if (len(alt) <= 4 and alt.isalpha()) else "spelling_variant"
            if alt == "Kotada" and cid == "dholavira":
                rel = "ambiguous_toponym"
            register_alias(cid, name, alt, rel, ["2026-10-26-indus-living-atlas"], ambiguous=(alt == "Kotada"))

        # Register site-register spelling variants
        for sr in sreg_by_canonical.get(cid, []):
            if sr["site"] != name:
                register_alias(cid, name, sr["site"], "spelling_variant", ["2026-10-06-evidence-census-site-register"])

        # Coordinate assertions
        assertions: list[dict[str, Any]] = []
        atlas_lat, atlas_lon = s.get("lat"), s.get("lon")
        atlas_prec = infer_atlas_precision(atlas_lat, atlas_lon, s.get("coord_kind", ""), s.get("coord_note", ""))

        # Primary selection overrides (PROTOCOL.md Section 5)
        use_q1032_primary = cid in {"banawali", "surkotada", "sutkagen-dor"}

        if atlas_lat is not None and atlas_lon is not None:
            add_coord_assertion(
                assertions,
                lat=atlas_lat,
                lon=atlas_lon,
                datum="WGS84",
                precision_class=atlas_prec,
                source_register="2026-10-26-indus-living-atlas",
                source_citation=s.get("coord_source") or "Living Atlas v2 inherited coordinate",
                evidence_status=s.get("coord_kind") or "inherited-atlas",
                selection_role="competing_retained" if use_q1032_primary else "primary_retained",
                basis=s.get("coord_note") or "Retained coordinate in 2026-10-26 Living Atlas.",
            )

        # If Living Atlas applied an overlay change (Surkotada, Farmana), preserve the original 8 Oct point too
        orig = s.get("original_coordinate") or {}
        if orig.get("lat") is not None and orig.get("lon") is not None:
            if atlas_lat is None or abs(float(orig["lat"]) - float(atlas_lat)) > 1e-6 or abs(float(orig["lon"]) - float(atlas_lon)) > 1e-6:
                add_coord_assertion(
                    assertions,
                    lat=orig["lat"],
                    lon=orig["lon"],
                    datum="WGS84",
                    precision_class=infer_atlas_precision(orig["lat"], orig["lon"], orig.get("kind", ""), ""),
                    source_register="2026-10-08-site-map",
                    source_citation="Inherited 8 October site-map coordinate prior to 26 October overlay",
                    evidence_status=orig.get("kind") or "superseded-atlas",
                    selection_role="superseded_retained",
                    basis="Superseded by 26 October Living Atlas overlay from Q-1032 register.",
                )

        # Merge Q-1032 town-axis register if matched
        q_row = q1032_by_canonical.get(cid)
        q_summary = None
        if q_row:
            source_regs.append("2026-10-24-q1032-town-axis-register")
            q_status = q_row.get("coordinate_value_status") or "unknown"
            q_coord_obj = q_row.get("coordinate") or {}
            if q_row.get("latitude") is not None and q_row.get("longitude") is not None:
                q_role = "primary_retained" if use_q1032_primary else "competing_retained"
                add_coord_assertion(
                    assertions,
                    lat=q_row["latitude"],
                    lon=q_row["longitude"],
                    datum=q_row.get("coordinate_datum") or "WGS84",
                    precision_class=infer_q1032_precision(q_status, q_coord_obj.get("basis", "")),
                    source_register="2026-10-24-q1032-town-axis-register",
                    source_citation="Q-1032 town-axis register v5 retained town coordinate",
                    evidence_status=q_status,
                    selection_role=q_role,
                    basis=(q_coord_obj.get("basis") or "Q-1032 retained coordinate")[:240],
                )
            for cand in q_row.get("coordinate_candidates") or []:
                clat, clon = cand.get("lat"), cand.get("lon")
                if clat is None or clon is None:
                    continue
                cbasis = str(cand.get("basis") or "")
                cbasis_l = cbasis.lower()
                # Check if explicitly excluded town locator (Bagasara town in Amreli district for Gola Dhoro)
                if cid == "gola-dhoro-bagasra" and abs(float(clat) - 21.4833) < 0.05:
                    crole = "excluded_retained"
                    cev = "excluded-town-locator"
                elif cid == "farmana" and abs(float(clon) - 76.5667) < 0.05:
                    crole = "superseded_retained"
                    cev = "superseded-wikipedia-coordinate"
                elif cid == "surkotada" and float(clon) < 70.86:
                    crole = "superseded_retained"
                    cev = "superseded-gazetteer-coordinate"
                else:
                    crole = "competing_retained"
                    cev = "q1032-candidate"
                add_coord_assertion(
                    assertions,
                    lat=clat,
                    lon=clon,
                    datum="WGS84",
                    precision_class=infer_q1032_precision(cev, cbasis),
                    source_register="2026-10-24-q1032-town-axis-register",
                    source_citation="Q-1032 town-axis register v5 coordinate candidate",
                    evidence_status=cev,
                    selection_role=crole,
                    basis=cbasis[:240],
                )
            q_summary = {
                "town_slug": q_row["town"],
                "required_q1032": bool(q_row.get("required")),
                "imagery_lines": q_row.get("imagery_lines", 0),
                "plan_lines": q_row.get("plan_lines", 0),
                "dated_part_assertions": q_row.get("dated_part_assertions", 0),
                "radiocarbon_assertions": q_row.get("radiocarbon_assertions", 0),
            }

        # Merge satellite-prospection known reference points if matched
        for feat in sat_refs_by_canonical.get(cid, []):
            props = feat["properties"]
            lon_s, lat_s = feat["geometry"]["coordinates"][:2]
            sid_s = props.get("source_id") or ""
            stitle = sat_sources_by_id.get(sid_s, {}).get("title", sid_s)
            if "2026-10-12-satellite-prospection" not in source_regs:
                source_regs.append("2026-10-12-satellite-prospection")
            add_coord_assertion(
                assertions,
                lat=lat_s,
                lon=lon_s,
                datum="WGS84",
                precision_class="surveyed_sub_100m" if "DOAM" in props.get("id", "") or "TABLE" in props.get("id", "") else "catalogued_arcminute",
                source_register="2026-10-12-satellite-prospection",
                source_citation=f"{props.get('id')} ({sid_s}: {stitle})",
                evidence_status="satellite-prospection-reference",
                selection_role="competing_retained",
                basis=props.get("name") or "Known archaeological reference in 2026-10-12 satellite prospection atlas.",
            )

        # Merge Living Towns review if matched (Harappa, Ropar, Dholavira, Mohenjo-daro)
        lt_row = lt_by_canonical.get(cid)
        lt_summary = None
        if lt_row:
            source_regs.append("2026-10-26-indus-living-atlas-living-towns")
            if lt_row["name"] != name:
                register_alias(cid, name, lt_row["name"], "modern_municipality_context", ["2026-10-26-indus-living-atlas-living-towns"])
            lt_summary = {
                "living_town_id": lt_row["id"],
                "category": lt_row["category"],
                "continuity_status": lt_row["continuity_status"],
                "indus_overlap": lt_row["indus_overlap"],
                "spatial_relation": lt_row["spatial_relation"],
            }

        # Merge Post-Catalogue Finds if matched
        pcf_row = pcf_by_canonical.get(cid)
        pcf_summary = None
        if pcf_row:
            source_regs.append("2026-10-21-post-catalogue-finds")
            if pcf_row["site"] != name:
                register_alias(cid, name, pcf_row["site"], "spelling_variant", ["2026-10-21-post-catalogue-finds"])
            if pcf_row.get("site_code"):
                register_alias(cid, name, pcf_row["site_code"], "catalogue_code", ["2026-10-21-post-catalogue-finds"])
            pcf_summary = {
                "site_code": pcf_row["site_code"],
                "rows_total": int(pcf_row["rows_total"]),
                "rows_main": int(pcf_row["rows_main"]),
                "absent_lower": int(pcf_row["absent_lower"]),
                "absent_upper": int(pcf_row["absent_upper"]),
            }

        # Select primary coordinate cleanly (guaranteed verbatim member of assertions)
        primary_assertion = next((a for a in assertions if a["selection_role"] == "primary_retained"), None)
        if primary_assertion is None and assertions:
            assertions[0]["selection_role"] = "primary_retained"
            primary_assertion = assertions[0]

        warnings = list(s.get("warnings") or [])
        documented_conflict_warning = cid in {"nindowari", "tell-abraq"}
        conflict_metrics = compute_coord_conflict_metrics(assertions, documented_conflict_warning)

        exc_status, has_exc, lt_overlap = classify_atlas_excavation_status(cid, s.get("fieldwork") or [])

        # Four-unit structured fields
        phys_units = list(SPECIAL_UNIT_ENRICHMENTS.get(cid, {}).get("physical_units", []))
        if not phys_units:
            phys_units.append(
                {
                    "unit_type": "regional_provenance" if unit_class == "regional_provenance_label" else "undelimited_site_locality",
                    "label": f"{name} (individual mound boundaries not delimited in held register)",
                    "extent_note": "Mound and scatter extent not separately measured in held local records.",
                    "source_ids": ["2026-10-26-indus-living-atlas"],
                }
            )

        phase_footprints = list(SPECIAL_UNIT_ENRICHMENTS.get(cid, {}).get("phase_footprints", []))
        for ph in s.get("phases") or []:
            phase_footprints.append(
                {
                    "label": ph.get("label") or ph.get("phase") or "Recorded phase",
                    "start_bce": ph.get("start"),
                    "end_bce": ph.get("end"),
                    "area_ha": None,
                    "measurement_definition": f"Chronological range inherited from Living Atlas ({ph.get('scope') or ph.get('basis') or 'site chronology'}); spatial footprint area not measured.",
                    "source_ids": [ph.get("source") or "2026-10-26-indus-living-atlas"],
                }
            )

        exc_deposits = [
            {
                "years": fw.get("years") or "",
                "label": fw.get("label") or "",
                "source": fw.get("source") or "",
            }
            for fw in (s.get("fieldwork") or [])
        ]

        cov_row = census_by_name.get(name, {})
        inscribed_corpus = {
            "local_lipi_faces": cov_row.get("local_faces", 0),
            "local_lipi_families": cov_row.get("local_families", 0),
            "local_cisi_identifiers": cov_row.get("local_cisi_identifiers", 0),
            "im77_main_selected_objects": cov_row.get("IM77_main_selected_objects"),
            "post_catalogue": pcf_summary,
        }

        records.append(
            {
                "id": cid,
                "name": name,
                "unit_class": unit_class,
                "domain_role": "indus_or_contact_inscribed_locality",
                "country": s.get("country") or "",
                "region": s.get("region") or "",
                "province": s.get("province") or "",
                "primary_lat": primary_assertion["lat"] if primary_assertion else None,
                "primary_lon": primary_assertion["lon"] if primary_assertion else None,
                "primary_precision_class": primary_assertion["precision_class"] if primary_assertion else "unlocated",
                "primary_coord_source": primary_assertion["source_register"] if primary_assertion else "unlocated",
                "coordinate_assertions": assertions,
                "coordinate_conflict": conflict_metrics,
                "excavation_status": exc_status,
                "has_excavation_record": has_exc,
                "living_town_overlap": lt_overlap,
                "physical_units": phys_units,
                "phase_footprints": phase_footprints,
                "excavated_deposits": exc_deposits,
                "inscribed_corpus": inscribed_corpus,
                "q1032_register": q_summary,
                "living_town_review": lt_summary,
                "warnings": warnings,
                "source_registers": sorted(set(source_regs)),
                "prospection_window_ids": [],
                "survey_effort_campaigns": [],
            }
        )

    # 2B. Add 14 non-overlapping Living Town continuity reference localities
    existing_ids = {r["id"] for r in records}
    for lt in living_towns["records"]:
        cid = LIVING_TOWN_TO_CANONICAL[lt["id"]]
        if cid in existing_ids:
            continue
        name = lt["name"]
        register_alias(cid, name, name, "canonical_name", ["2026-10-26-indus-living-atlas-living-towns"])
        register_alias(cid, name, lt["id"], "catalogue_code", ["2026-10-26-indus-living-atlas-living-towns"])
        if " / " in name:
            for part in name.split(" / "):
                register_alias(cid, name, part.strip(), "spelling_variant", ["2026-10-26-indus-living-atlas-living-towns"])
        if lt.get("evidence_place") and lt["evidence_place"] != name:
            register_alias(cid, name, lt["evidence_place"], "subsite_mound_name", ["2026-10-26-indus-living-atlas-living-towns"])

        assertions = []
        add_coord_assertion(
            assertions,
            lat=lt["lat"],
            lon=lt["lon"],
            datum="WGS84",
            precision_class="approximate_regional_5km",
            source_register="2026-10-26-indus-living-atlas-living-towns",
            source_citation=f"Living Towns register {lt['id']} (5 km regional index pin)",
            evidence_status="regional-index-pin",
            selection_role="primary_retained",
            basis=lt["spatial_relation"],
        )

        if cid in BURIED_UNDER_LIVING_TOWN_IDS:
            exc_status = "buried_under_living_town"
            has_exc = BURIED_UNDER_LIVING_TOWN_IDS[cid]
            lt_overlap = "predominantly_buried_under_living_town"
        elif cid in PARTIAL_LIVING_TOWN_OVERLAP_IDS:
            exc_status = "excavated"
            has_exc = True
            lt_overlap = "partial_modern_overlap"
        elif cid in NEARBY_DISTINCT_SETTLEMENT_IDS:
            exc_status = "excavated"
            has_exc = True
            lt_overlap = "nearby_distinct_settlement"
        else:
            exc_status = "excavated"
            has_exc = True
            lt_overlap = "partial_modern_overlap"

        phase_footprints = []
        for sp in lt.get("occupation_spans") or []:
            phase_footprints.append(
                {
                    "label": sp.get("label") or sp.get("phase") or "Occupation span",
                    "start_bce": sp.get("start_bce"),
                    "end_bce": sp.get("end_bce"),
                    "area_ha": None,
                    "measurement_definition": f"Chronological span at {lt['evidence_place']} from Living Towns review; spatial footprint area not measured.",
                    "source_ids": lt.get("source_ids") or [],
                }
            )

        records.append(
            {
                "id": cid,
                "name": name,
                "unit_class": "recorded_locality",
                "domain_role": "living_town_continuity_reference",
                "country": lt["country"],
                "region": "South Asia Continuity Comparison",
                "province": "",
                "primary_lat": assertions[0]["lat"],
                "primary_lon": assertions[0]["lon"],
                "primary_precision_class": "approximate_regional_5km",
                "primary_coord_source": "2026-10-26-indus-living-atlas-living-towns",
                "coordinate_assertions": assertions,
                "coordinate_conflict": compute_coord_conflict_metrics(assertions, False),
                "excavation_status": exc_status,
                "has_excavation_record": has_exc,
                "living_town_overlap": lt_overlap,
                "physical_units": [
                    {
                        "unit_type": "urban_or_monumental_locus",
                        "label": lt["evidence_place"],
                        "extent_note": lt["spatial_relation"],
                        "source_ids": lt.get("source_ids") or [],
                    }
                ],
                "phase_footprints": phase_footprints,
                "excavated_deposits": [
                    {
                        "years": "Multiple published seasons (see living-towns/sources.json)",
                        "label": f"Audited archaeological evidence at {lt['evidence_place']}" if has_exc else f"No primary Indus-period excavation sequence acquired for {lt['evidence_place']}",
                        "source": ", ".join(lt.get("source_ids") or []),
                    }
                ],
                "inscribed_corpus": {
                    "local_lipi_faces": 0,
                    "local_lipi_families": 0,
                    "local_cisi_identifiers": 0,
                    "im77_main_selected_objects": None,
                    "post_catalogue": None,
                },
                "q1032_register": None,
                "living_town_review": {
                    "living_town_id": lt["id"],
                    "category": lt["category"],
                    "continuity_status": lt["continuity_status"],
                    "indus_overlap": lt["indus_overlap"],
                    "spatial_relation": lt["spatial_relation"],
                },
                "warnings": [f"5 km approximate regional index pin; {lt['spatial_relation']}"],
                "source_registers": ["2026-10-26-indus-living-atlas-living-towns"],
                "prospection_window_ids": [],
                "survey_effort_campaigns": [],
            }
        )
        existing_ids.add(cid)

    # 2C. Add 2 non-overlapping Post-Catalogue Finds localities (Dhalewan, Indiranagar (Kanpur))
    pcf_extra_meta = {
        "dhalewan": {
            "region": "Eastern Headwaters",
            "province": "Punjab",
            "excavation_status": "excavated",
            "has_excavation_record": True,
            "living_town_overlap": "unknown",
            "deposits": [
                {
                    "years": "1999-2000 & 2001-2002",
                    "label": "Excavation reported in 2018 Dhalewan report (Period IB and Period IC Phase II inscribed finds)",
                    "source": "new-dhalewan-report (2018), pp. 285, 293, 297",
                }
            ],
        },
        "indiranagar-kanpur": {
            "region": "North India",
            "province": "Uttar Pradesh",
            "excavation_status": "unknown",
            "has_excavation_record": False,
            "living_town_overlap": "unknown",
            "deposits": [],
        },
    }
    for r in pcf_sites_rows:
        cid = POST_CATALOGUE_SITE_TO_CANONICAL[r["site"]]
        if cid in existing_ids:
            continue
        meta = pcf_extra_meta[cid]
        name = r["site"]
        register_alias(cid, name, name, "canonical_name", ["2026-10-21-post-catalogue-finds"])
        register_alias(cid, name, r["site_code"], "catalogue_code", ["2026-10-21-post-catalogue-finds"])
        records.append(
            {
                "id": cid,
                "name": name,
                "unit_class": "recorded_locality",
                "domain_role": "indus_or_contact_inscribed_locality",
                "country": r["country"],
                "region": meta["region"],
                "province": meta["province"],
                "primary_lat": None,
                "primary_lon": None,
                "primary_precision_class": "unlocated",
                "primary_coord_source": "unlocated",
                "coordinate_assertions": [],
                "coordinate_conflict": compute_coord_conflict_metrics([], False),
                "excavation_status": meta["excavation_status"],
                "has_excavation_record": meta["has_excavation_record"],
                "living_town_overlap": meta["living_town_overlap"],
                "physical_units": [
                    {
                        "unit_type": "undelimited_site_locality",
                        "label": f"{name} (coordinates and mound extent not yet acquired in held registers)",
                        "extent_note": "Added from post-catalogue inscribed-finds census; primary site coordinate requires acquisition.",
                        "source_ids": ["2026-10-21-post-catalogue-finds"],
                    }
                ],
                "phase_footprints": [],
                "excavated_deposits": meta["deposits"],
                "inscribed_corpus": {
                    "local_lipi_faces": 0,
                    "local_lipi_families": 0,
                    "local_cisi_identifiers": 0,
                    "im77_main_selected_objects": None,
                    "post_catalogue": {
                        "site_code": r["site_code"],
                        "rows_total": int(r["rows_total"]),
                        "rows_main": int(r["rows_main"]),
                        "absent_lower": int(r["absent_lower"]),
                        "absent_upper": int(r["absent_upper"]),
                    },
                },
                "q1032_register": None,
                "living_town_review": None,
                "warnings": ["Unlocated in held local registers; acquire primary excavation report coordinate."],
                "source_registers": ["2026-10-21-post-catalogue-finds"],
                "prospection_window_ids": [],
                "survey_effort_campaigns": [],
            }
        )
        existing_ids.add(cid)

    # 2D. Add 8 documented non-corpus Indus/survey localities
    for ex in EXTRA_PROSPECTION_LOCALITIES:
        cid = ex["id"]
        name = ex["name"]
        register_alias(cid, name, name, "canonical_name", ex["source_registers"])
        for alt in ex["alts"]:
            register_alias(cid, name, alt, "spelling_variant", ex["source_registers"], ambiguous=(alt in {"Kotada", "Kotda"}))
        assertions = []
        for c in ex["coords"]:
            add_coord_assertion(assertions, **c)
        prim = assertions[0] if assertions else None
        records.append(
            {
                "id": cid,
                "name": name,
                "unit_class": ex["unit_class"],
                "domain_role": ex["domain_role"],
                "country": ex["country"],
                "region": ex["region"],
                "province": ex["province"],
                "primary_lat": prim["lat"] if prim else None,
                "primary_lon": prim["lon"] if prim else None,
                "primary_precision_class": prim["precision_class"] if prim else "unlocated",
                "primary_coord_source": prim["source_register"] if prim else "unlocated",
                "coordinate_assertions": assertions,
                "coordinate_conflict": compute_coord_conflict_metrics(assertions, False),
                "excavation_status": ex["excavation_status"],
                "has_excavation_record": ex["has_excavation_record"],
                "living_town_overlap": ex["living_town_overlap"],
                "physical_units": ex["physical_units"],
                "phase_footprints": ex["phase_footprints"],
                "excavated_deposits": ex["excavated_deposits"],
                "inscribed_corpus": {
                    "local_lipi_faces": 0,
                    "local_lipi_families": 0,
                    "local_cisi_identifiers": 0,
                    "im77_main_selected_objects": None,
                    "post_catalogue": None,
                },
                "q1032_register": None,
                "living_town_review": None,
                "warnings": [] if prim else ["Coordinates not published in held local witness."],
                "source_registers": sorted(set(ex["source_registers"])),
                "prospection_window_ids": list(ex.get("window_override", [])),
                "survey_effort_campaigns": list(ex["survey_campaigns"]),
            }
        )
        existing_ids.add(cid)

    # 2E. Add 5 unverified remote-sensing mound proposals (3 from reconnaissance-register.csv + 2 from Orengo 2020)
    for row in sat_recon_rows:
        cid = row["id"].lower()
        name = row["id"]
        register_alias(cid, name, name, "canonical_name", ["2026-10-12-satellite-prospection"])
        assertions = []
        add_coord_assertion(
            assertions,
            lat=float(row["latitude"]),
            lon=float(row["longitude"]),
            datum="WGS84",
            precision_class="image_located_site",
            source_register="2026-10-12-satellite-prospection",
            source_citation=f"2026-10-12-satellite-prospection reconnaissance-register.csv ({row['block_id']}, status={row['status']})",
            evidence_status="remote-sensing-proposal",
            selection_role="primary_retained",
            basis=f"Copernicus GLO-30 + Sentinel-2 screening candidate ({row['threshold_support_ha']} ha support, {row['peak_minus_annulus_m']} m relief; {row['reference_distance_m']} m from {row['nearest_reference_id']}).",
        )
        country = "Pakistan" if row["block_id"] == "B01" else "India"
        region = "Inter-Riverine" if row["block_id"] == "B01" else "North India"
        records.append(
            {
                "id": cid,
                "name": name,
                "unit_class": "physical_mound_or_scatter",
                "domain_role": "remote_sensing_proposal",
                "country": country,
                "region": region,
                "province": "Punjab" if country == "Pakistan" else "Rajasthan",
                "primary_lat": assertions[0]["lat"],
                "primary_lon": assertions[0]["lon"],
                "primary_precision_class": "image_located_site",
                "primary_coord_source": "2026-10-12-satellite-prospection",
                "coordinate_assertions": assertions,
                "coordinate_conflict": compute_coord_conflict_metrics(assertions, False),
                "excavation_status": "remote_proposal_unverified",
                "has_excavation_record": False,
                "living_town_overlap": "none",
                "physical_units": [
                    {
                        "unit_type": "remote_sensing_mound_proposal",
                        "label": f"{name} terrain prominence candidate ({row['status']})",
                        "extent_note": f"Threshold support {row['threshold_support_ha']} ha, peak-minus-annulus {row['peak_minus_annulus_m']} m; alternative explanation: {row['alternative']}.",
                        "source_ids": ["2026-10-12-satellite-prospection"],
                    }
                ],
                "phase_footprints": [],
                "excavated_deposits": [],
                "inscribed_corpus": {
                    "local_lipi_faces": 0,
                    "local_lipi_families": 0,
                    "local_cisi_identifiers": 0,
                    "im77_main_selected_objects": None,
                    "post_catalogue": None,
                },
                "q1032_register": None,
                "living_town_review": None,
                "warnings": [f"Unverified remote-sensing proposal ({row['strength']}); {row['novelty_status']}."],
                "source_registers": ["2026-10-12-satellite-prospection"],
                "prospection_window_ids": [],
                "survey_effort_campaigns": ["SC-SATPROSP-2026-BLOCKS"],
            }
        )

    for op in ORENGO_REMOTE_PROPOSALS:
        cid = op["id"]
        name = op["name"]
        register_alias(cid, name, name, "canonical_name", ["2026-10-11-settlement-prospection"])
        records.append(
            {
                "id": cid,
                "name": name,
                "unit_class": "physical_mound_or_scatter",
                "domain_role": "remote_sensing_proposal",
                "country": op["country"],
                "region": op["region"],
                "province": op["province"],
                "primary_lat": None,
                "primary_lon": None,
                "primary_precision_class": "unlocated",
                "primary_coord_source": "unlocated",
                "coordinate_assertions": [],
                "coordinate_conflict": compute_coord_conflict_metrics([], False),
                "excavation_status": "remote_proposal_unverified",
                "has_excavation_record": False,
                "living_town_overlap": "none",
                "physical_units": [
                    {
                        "unit_type": "remote_sensing_mound_proposal",
                        "label": f"{name} Cholistan satellite cluster (~{op['area_ha']} ha)",
                        "extent_note": op["note"],
                        "source_ids": ["R08"],
                    }
                ],
                "phase_footprints": [],
                "excavated_deposits": [],
                "inscribed_corpus": {
                    "local_lipi_faces": 0,
                    "local_lipi_families": 0,
                    "local_cisi_identifiers": 0,
                    "im77_main_selected_objects": None,
                    "post_catalogue": None,
                },
                "q1032_register": None,
                "living_town_review": None,
                "warnings": ["Unverified remote-sensing proposal; coordinates not published in held Orengo 2020 witness."],
                "source_registers": ["2026-10-11-settlement-prospection"],
                "prospection_window_ids": list(op["window_override"]),
                "survey_effort_campaigns": ["SC-ORENGO-CHOLISTAN-2020", "SC-MUGHAL-CHOLISTAN"],
            }
        )

    # Apply explicit supplementary aliases and homonym flags
    rec_by_id = {r["id"]: r for r in records}
    for cid, alias_str, rel, srcs, ambig, note in SUPPLEMENTARY_ALIASES:
        register_alias(cid, rec_by_id[cid]["name"], alias_str, rel, srcs, ambig, note)

    # Detect any remaining cross-canonical normalized-alias collisions automatically
    norm_to_cids: dict[str, set[str]] = defaultdict(set)
    for item in alias_entries.values():
        norm_to_cids[item["normalized_alias"]].add(item["canonical_id"])
    for item in alias_entries.values():
        cids = sorted(norm_to_cids[item["normalized_alias"]])
        if len(cids) > 1:
            item["ambiguous_homonym"] = True
            if not item["disambiguation_note"]:
                item["disambiguation_note"] = f"Shared normalized form across canonical IDs: {', '.join(cids)}."

    # 3. Assign P01-P21 prospection windows and survey-effort campaigns to localities & build survey-effort-v1.json
    sat_blocks_all = {}
    for b in sat_blocks_v1.get("blocks", []) + sat_blocks_v2.get("blocks", []):
        sat_blocks_all[b["id"]] = b
    sat_blocks_v2_bboxes = {b["id"]: b["bbox_lonlat"] for b in sat_atlas["study_blocks"]}

    campaigns_by_window: dict[str, list[str]] = defaultdict(list)
    for camp in SURVEY_CAMPAIGNS:
        for wid in camp["window_ids"]:
            campaigns_by_window[wid].append(camp["campaign_id"])

    window_profiles: list[dict[str, Any]] = []
    for target in prosp_cand["targets"]:
        wid = target["id"]
        bbox = target["bbox_lonlat"]
        matched_records = []
        for rec in records:
            in_win = wid in rec["prospection_window_ids"]
            if rec["primary_lat"] is not None and rec["primary_lon"] is not None:
                if point_in_bbox(rec["primary_lat"], rec["primary_lon"], bbox):
                    in_win = True
            if in_win:
                if wid not in rec["prospection_window_ids"]:
                    rec["prospection_window_ids"].append(wid)
                for camp_id in campaigns_by_window[wid]:
                    if camp_id not in rec["survey_effort_campaigns"]:
                        rec["survey_effort_campaigns"].append(camp_id)
                matched_records.append(rec)

        # Spatial concordance overlap checks
        cores_in_win = [
            pt["name"]
            for pt in singh_cores["points"]
            if point_in_bbox(pt["lat"], pt["lon"], bbox)
        ]
        blocks_in_win = [
            bid
            for bid, b_bbox in sorted(sat_blocks_v2_bboxes.items())
            if bbox_overlaps(bbox, b_bbox) or wid in sat_blocks_all.get(bid, {}).get("region_ids", [])
        ]
        orengo_overlap = bbox_overlaps(bbox, orengo_bbox)

        mahsa_hits_in_win = []
        for m_label, m_info in mahsa_probe_summary.items():
            for h in m_info.get("hits", []):
                for pt in h.get("points", []):
                    if point_in_bbox(pt["lat"], pt["lon"], bbox):
                        mahsa_hits_in_win.append(
                            {
                                "probe": m_label,
                                "displayname": h["displayname"],
                                "lat": pt["lat"],
                                "lon": pt["lon"],
                            }
                        )

        by_unit = Counter(r["unit_class"] for r in matched_records)
        by_exc = Counter(r["excavation_status"] for r in matched_records)
        meta = WINDOW_SURVEY_METADATA[wid]

        window_profiles.append(
            {
                "window_id": wid,
                "name": target["name"],
                "bbox_lonlat": bbox,
                "evidence_class": target["evidence_class"],
                "information_level": target["information_level"],
                "preservation_evidence_level": target["preservation_evidence_level"],
                "feasibility_level": target["feasibility_level"],
                "source_ids": target["source_ids"],
                "survey_effort_class": meta["survey_effort_class"],
                "documented_campaigns": sorted(campaigns_by_window[wid]),
                "matched_gazetteer_count": len(matched_records),
                "matched_gazetteer_ids": sorted(r["id"] for r in matched_records),
                "matched_by_unit_class": dict(sorted(by_unit.items())),
                "matched_by_excavation_status": dict(sorted(by_exc.items())),
                "held_spatial_concordance": {
                    "orengo_2020_aoi_overlaps": orengo_overlap,
                    "singh_2017_cores_inside": sorted(cores_in_win),
                    "satellite_blocks_2026_10_12": sorted(set(blocks_in_win)),
                    "mahsa_held_probe_hits_inside": mahsa_hits_in_win,
                },
                "absence_interpretation": meta["absence_interpretation"],
            }
        )

    # Sort deterministic fields and attach per-record aliases
    aliases_by_cid: dict[str, list[str]] = defaultdict(list)
    for item in alias_entries.values():
        if item["alias_relation"] != "canonical_name":
            aliases_by_cid[item["canonical_id"]].append(item["alias_string"])

    records.sort(key=lambda r: r["id"])
    for rec in records:
        rec["prospection_window_ids"] = sorted(set(rec["prospection_window_ids"]))
        rec["survey_effort_campaigns"] = sorted(set(rec["survey_effort_campaigns"]))
        rec["aliases"] = sorted(set(aliases_by_cid.get(rec["id"], [])))
        if rec["survey_effort_campaigns"]:
            rec["survey_effort_coverage"] = "linked_to_documented_regional_campaign"
        elif rec["has_excavation_record"]:
            rec["survey_effort_coverage"] = "site_excavation_only_no_regional_window_tag"
        elif rec["excavation_status"] == "surface_surveyed":
            rec["survey_effort_coverage"] = "local_surface_survey_outside_p01_p21"
        else:
            rec["survey_effort_coverage"] = "undocumented_prior_survey_in_held_registers"

    # Sort aliases deterministically and assign IDs
    sorted_aliases = sorted(
        alias_entries.values(),
        key=lambda a: (a["canonical_id"], 0 if a["alias_relation"] == "canonical_name" else 1, a["alias_string"].lower()),
    )
    for idx, item in enumerate(sorted_aliases, 1):
        item["alias_id"] = f"AL-{idx:04d}"

    # 4. Write tracked CC0-safe outputs
    gazetteer_payload = {
        "schema_version": SCHEMA_VERSION,
        "created_date": BUILD_DATE,
        "scientific_confirmation": False,
        "protocol_path": "experiments/2026-11-22-site-survey-gazetteer/PROTOCOL.md",
        "units_definition": {
            "recorded_locality": "Named place entry in a catalogue, inventory, report, or continuity register.",
            "physical_mound_or_scatter": "Discrete topographic mound, artifact scatter, enclosure, cemetery, quarry, or remote-sensing proposal.",
            "phase_footprint": "Occupied area or chronological envelope attributed to a specific phase or measurement definition.",
            "excavated_deposit": "Documented excavation campaign, trench, salvage cutting, borehole, or stratigraphic exposure.",
        },
        "summary": {
            "total_records": len(records),
            "located_records": sum(1 for r in records if r["primary_lat"] is not None),
            "unlocated_records": sum(1 for r in records if r["primary_lat"] is None),
            "total_coordinate_assertions": sum(len(r["coordinate_assertions"]) for r in records),
            "records_with_multiple_coord_assertions": sum(1 for r in records if len(r["coordinate_assertions"]) > 1),
            "records_with_coordinate_conflict": sum(1 for r in records if r["coordinate_conflict"]["has_coordinate_conflict"]),
            "total_alias_rows": len(sorted_aliases),
            "non_canonical_aliases": sum(1 for a in sorted_aliases if a["alias_relation"] != "canonical_name"),
            "ambiguous_homonym_rows": sum(1 for a in sorted_aliases if a["ambiguous_homonym"]),
        },
        "records": records,
    }

    gazetteer_json_path = PKG / "gazetteer-v1.json"
    gazetteer_json_path.write_text(json.dumps(gazetteer_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # gazetteer-v1.csv
    csv_cols = [
        "id",
        "name",
        "unit_class",
        "domain_role",
        "country",
        "region",
        "province",
        "primary_lat",
        "primary_lon",
        "primary_precision_class",
        "primary_coord_source",
        "coord_assertion_count",
        "distinct_coord_point_count",
        "max_coord_spread_km",
        "active_coord_spread_km",
        "has_coordinate_conflict",
        "coord_conflict_tier",
        "excavation_status",
        "has_excavation_record",
        "living_town_overlap",
        "physical_unit_count",
        "phase_footprint_count",
        "excavated_deposit_count",
        "local_lipi_faces",
        "local_lipi_families",
        "post_catalogue_main_rows",
        "q1032_in_register",
        "prospection_window_ids",
        "survey_effort_campaigns",
        "survey_effort_coverage",
        "alias_count",
        "source_registers",
    ]
    gazetteer_csv_path = PKG / "gazetteer-v1.csv"
    with gazetteer_csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_cols)
        w.writeheader()
        for r in records:
            cc = r["coordinate_conflict"]
            ic = r["inscribed_corpus"]
            w.writerow(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "unit_class": r["unit_class"],
                    "domain_role": r["domain_role"],
                    "country": r["country"],
                    "region": r["region"],
                    "province": r["province"],
                    "primary_lat": "" if r["primary_lat"] is None else r["primary_lat"],
                    "primary_lon": "" if r["primary_lon"] is None else r["primary_lon"],
                    "primary_precision_class": r["primary_precision_class"],
                    "primary_coord_source": r["primary_coord_source"],
                    "coord_assertion_count": cc["assertion_count"],
                    "distinct_coord_point_count": cc["distinct_point_count"],
                    "max_coord_spread_km": "" if cc["max_coord_spread_km"] is None else cc["max_coord_spread_km"],
                    "active_coord_spread_km": "" if cc["active_coord_spread_km"] is None else cc["active_coord_spread_km"],
                    "has_coordinate_conflict": str(cc["has_coordinate_conflict"]).lower(),
                    "coord_conflict_tier": cc["coord_conflict_tier"],
                    "excavation_status": r["excavation_status"],
                    "has_excavation_record": str(r["has_excavation_record"]).lower(),
                    "living_town_overlap": r["living_town_overlap"],
                    "physical_unit_count": len(r["physical_units"]),
                    "phase_footprint_count": len(r["phase_footprints"]),
                    "excavated_deposit_count": len(r["excavated_deposits"]),
                    "local_lipi_faces": ic["local_lipi_faces"],
                    "local_lipi_families": ic["local_lipi_families"],
                    "post_catalogue_main_rows": ic["post_catalogue"]["rows_main"] if ic["post_catalogue"] else 0,
                    "q1032_in_register": str(r["q1032_register"] is not None).lower(),
                    "prospection_window_ids": ";".join(r["prospection_window_ids"]),
                    "survey_effort_campaigns": ";".join(r["survey_effort_campaigns"]),
                    "survey_effort_coverage": r["survey_effort_coverage"],
                    "alias_count": len(r["aliases"]),
                    "source_registers": ";".join(r["source_registers"]),
                }
            )

    # aliases-v1.csv
    alias_cols = [
        "alias_id",
        "alias_string",
        "normalized_alias",
        "canonical_id",
        "canonical_name",
        "alias_relation",
        "source_registers",
        "ambiguous_homonym",
        "disambiguation_note",
    ]
    aliases_csv_path = PKG / "aliases-v1.csv"
    with aliases_csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alias_cols)
        w.writeheader()
        for a in sorted_aliases:
            w.writerow(
                {
                    "alias_id": a["alias_id"],
                    "alias_string": a["alias_string"],
                    "normalized_alias": a["normalized_alias"],
                    "canonical_id": a["canonical_id"],
                    "canonical_name": a["canonical_name"],
                    "alias_relation": a["alias_relation"],
                    "source_registers": ";".join(a["source_registers"]),
                    "ambiguous_homonym": str(a["ambiguous_homonym"]).lower(),
                    "disambiguation_note": a["disambiguation_note"],
                }
            )

    # survey-effort-v1.json
    survey_effort_payload = {
        "schema_version": SCHEMA_VERSION,
        "created_date": BUILD_DATE,
        "scope": "Documented regional survey campaigns and prospection-window effort profiles separating observed absence from unsurveyed or concealed landscapes.",
        "campaigns_count": len(SURVEY_CAMPAIGNS),
        "windows_count": len(window_profiles),
        "held_spatial_concordance_summary": {
            "orengo_2020_aoi_bbox_lonlat": orengo_bbox,
            "orengo_2020_aoi_vertex_count": len(orengo_coords),
            "singh_2017_derived_cores": len(singh_cores["points"]),
            "satellite_prospection_blocks": sorted(sat_blocks_v2_bboxes.keys()),
            "mahsa_api_probes_held": {
                k: {
                    "hits_or_terms": len(v.get("hits", [])) if "hits" in v else v.get("terms_count", 0),
                    "note": "Historical map sheet metadata or term hits only; bulk MAHSA site inventory not acquired.",
                }
                for k, v in mahsa_probe_summary.items()
            },
        },
        "campaigns": SURVEY_CAMPAIGNS,
        "prospection_windows": window_profiles,
    }
    survey_effort_path = PKG / "survey-effort-v1.json"
    survey_effort_path.write_text(json.dumps(survey_effort_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # coverage-v1.json
    material_conflicts = sorted(
        [
            {
                "id": r["id"],
                "name": r["name"],
                "max_coord_spread_km": r["coordinate_conflict"]["max_coord_spread_km"],
                "active_coord_spread_km": r["coordinate_conflict"]["active_coord_spread_km"],
                "assertion_count": r["coordinate_conflict"]["assertion_count"],
                "tier": r["coordinate_conflict"]["coord_conflict_tier"],
            }
            for r in records
            if r["coordinate_conflict"]["has_coordinate_conflict"]
        ],
        key=lambda x: (-(x["max_coord_spread_km"] or 0.0), x["id"]),
    )

    output_hashes = {}
    for p in [gazetteer_json_path, gazetteer_csv_path, aliases_csv_path, survey_effort_path]:
        output_hashes[p.name] = {
            "logical_path": p.relative_to(ROOT).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        }
    output_hashes["raw-concordance-extract-v1.json"] = {
        "logical_path": raw_extract_path.relative_to(ROOT).as_posix(),
        "physical_path": str(PHYSICAL_RAW_PREFIX / "raw-concordance-extract-v1.json"),
        "local_only": True,
        "bytes": raw_extract_path.stat().st_size,
        "sha256": sha256_file(raw_extract_path),
    }

    coverage_payload = {
        "schema_version": SCHEMA_VERSION,
        "created_date": BUILD_DATE,
        "totals": {
            "reconciled_records": len(records),
            "located_records": sum(1 for r in records if r["primary_lat"] is not None),
            "unlocated_records": sum(1 for r in records if r["primary_lat"] is None),
            "total_coordinate_assertions": sum(len(r["coordinate_assertions"]) for r in records),
            "records_with_multiple_coord_assertions": sum(1 for r in records if len(r["coordinate_assertions"]) > 1),
            "records_with_coordinate_conflict": len(material_conflicts),
            "material_conflicts_ge_1km": sum(1 for r in records if r["coordinate_conflict"]["coord_conflict_tier"] == "material_conflict_ge_1km"),
            "documented_unquantified_conflicts": sum(1 for r in records if r["coordinate_conflict"]["coord_conflict_tier"] == "documented_unquantified_conflict"),
            "minor_offsets_0.1_to_1km": sum(1 for r in records if r["coordinate_conflict"]["coord_conflict_tier"] == "minor_offset_0.1_to_1km"),
            "total_alias_rows": len(sorted_aliases),
            "non_canonical_aliases": sum(1 for a in sorted_aliases if a["alias_relation"] != "canonical_name"),
            "ambiguous_homonym_rows": sum(1 for a in sorted_aliases if a["ambiguous_homonym"]),
            "survey_campaigns": len(SURVEY_CAMPAIGNS),
            "prospection_windows": len(window_profiles),
            "records_inside_p01_p21": sum(1 for r in records if r["prospection_window_ids"]),
            "records_with_survey_campaign_tag": sum(1 for r in records if r["survey_effort_campaigns"]),
        },
        "reconciliation_joins": {
            "atlas_and_census_entities_in": len(atlas_data["sites"]),
            "q1032_towns_matched": sum(1 for r in records if r["q1032_register"] is not None),
            "q1032_newly_reconciled_by_alias": sorted(Q1032_TO_CANONICAL.keys()),
            "living_towns_total": len(living_towns["records"]),
            "living_towns_merged_onto_indus_sites": 4,
            "living_towns_added_as_references": 14,
            "post_catalogue_site_rows_in": len(pcf_sites_rows),
            "post_catalogue_merged_onto_atlas": len(pcf_sites_rows) - 2,
            "post_catalogue_newly_added_localities": 2,
            "extra_prospection_localities_added": len(EXTRA_PROSPECTION_LOCALITIES),
            "remote_sensing_proposals_added": len(sat_recon_rows) + len(ORENGO_REMOTE_PROPOSALS),
        },
        "breakdowns": {
            "by_unit_class": dict(sorted(Counter(r["unit_class"] for r in records).items())),
            "by_domain_role": dict(sorted(Counter(r["domain_role"] for r in records).items())),
            "by_excavation_status": dict(sorted(Counter(r["excavation_status"] for r in records).items())),
            "by_has_excavation_record": {
                "true": sum(1 for r in records if r["has_excavation_record"]),
                "false": sum(1 for r in records if not r["has_excavation_record"]),
            },
            "by_living_town_overlap": dict(sorted(Counter(r["living_town_overlap"] for r in records).items())),
            "by_primary_precision_class": dict(sorted(Counter(r["primary_precision_class"] for r in records).items())),
            "by_coord_conflict_tier": dict(sorted(Counter(r["coordinate_conflict"]["coord_conflict_tier"] for r in records).items())),
            "by_country": dict(sorted(Counter(r["country"] for r in records).items())),
            "by_survey_effort_coverage": dict(sorted(Counter(r["survey_effort_coverage"] for r in records).items())),
            "windows_by_survey_effort_class": dict(sorted(Counter(w["survey_effort_class"] for w in window_profiles).items())),
            "aliases_by_relation": dict(sorted(Counter(a["alias_relation"] for a in sorted_aliases).items())),
        },
        "coordinate_conflicts_detail": material_conflicts,
        "inputs": input_manifest,
        "outputs": output_hashes,
    }

    coverage_path = PKG / "coverage-v1.json"
    coverage_path.write_text(json.dumps(coverage_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(coverage_payload["totals"], indent=2))
    print("\nBreakdowns:")
    print(json.dumps(coverage_payload["breakdowns"], indent=2))
    print("\nCoordinate conflicts:")
    for mc in material_conflicts:
        print(f"  {mc['id']:22s} | max={mc['max_coord_spread_km']} km | active={mc['active_coord_spread_km']} km | n={mc['assertion_count']} | {mc['tier']}")


if __name__ == "__main__":
    main()
