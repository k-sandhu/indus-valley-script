"""Rebuild the western-town assertion ledger from the recorded source readings.

Source bytes, OCR and renderings remain local-only. No source images are copied.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = Path(r"D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/western")


def source(sid, title, authors, year, url, logical=None, **extra):
    row = dict(id=sid, title=title, authors=authors, year=year, url=url,
               access_date="2026-10-24", rights="unresolved; local-only",
               logical_path=logical, physical_path=None, sha256=None,
               source_class="primary excavation author", **extra)
    if logical:
        p = ROOT / logical
        row.update(physical_path=str(p.resolve()), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
    return row


SOURCES = [
    source("W-S01", "Excavations at Dholavira (1989-90 to 2004-2005)", "R. S. Bisht", 2015,
           "https://archive.org/details/dholavirareportpreliminaryjan2015_860_K",
           "data/raw/2026-10-21-town-orientations-verification/dating/dholavira2015.pdf",
           edition_caution="Preliminary January 2015 scan; identity with final published edition unresolved.",
           read_locator="printed pp. 33-34, 76-77, 91-105, 134-137, 156-158; PDF indices printed+16"),
    source("W-S02", "Lothal: A Harappan Port Town (1955-62), Volume I", "S. R. Rao", 1979,
           "https://archive.org/details/masi78lothalaharappanporttownraos.r.part1platesmissing_443_k",
           "data/raw/2026-10-21-town-orientations-verification/dating/lothal1979.pdf",
           edition_caution="Text scan lacks plate volume. Prose on pp. 86-87 reverses Street 1/6 compass directions.",
           read_locator="printed pp. 18-19, 29, 44, 85-87, 125-126; PDF indices printed+10"),
    source("W-S03", "Indus Urbanism: New Perspectives on its Origin and Character", "Jonathan Mark Kenoyer", "2005 revised manuscript, hosted as 2008",
           "https://www.harappa.com/sites/default/files/pdf/Kenoyer2008%20Indus%20Cities%20Sackler%20Colloquiumfinalrevised.pdf",
           "data/raw/2026-10-21-town-orientations-verification/dating/kenoyer2008-cities.pdf",
           edition_caution="PDF header gives Final Revisions: Oct. 1, 2005; manuscript pagination is used, not asserted as final book pagination.",
           read_locator="manuscript pp. 3, 6-9, 11, 16-19; PDF indices printed-1"),
    source("W-S04", "Urban Process in the Indus Tradition: A Preliminary Model from Harappa", "Jonathan Mark Kenoyer", 1991,
           "https://www.harappa.com/sites/default/files/pdf/Harappa1986-90_04_Kenoyer-UrbanProcess_1.pdf",
           "data/raw/2026-10-21-town-axes/dating/harappa/kenoyer1991urban.pdf",
           edition_caution="Legacy period labels in this chapter predate the current Ravi/Kot Diji chronology; do not equate its Period 1/2 labels without a crosswalk.",
           read_locator="printed pp. 32-34; PDF indices printed-27"),
    source("W-S05", "The Integration and Diversity in the Indus Tradition (2600-1900 BCE): Comparing Cities, Towns and Villages", "Jonathan Mark Kenoyer", "2021-22",
           "https://www.heritageuniversityofkerala.com/JournalPDF/Volume9/1.pdf",
           "data/raw/2026-10-24-urban-form-and-inscription-ecology/western/kenoyer2021integration.pdf",
           read_locator="printed pp. 4-5, 8-10; PDF indices printed-1"),
    source("W-S06", "Water supply and sewage disposal at Mohenjo-Daro", "M. Jansen", 1989,
           "https://doi.org/10.1080/00438243.1989.9980100",
           "data/raw/2026-10-24-urban-form-and-inscription-ecology/western/jansen1989water.pdf",
           acquisition_url="https://sleigh-munoz.co.uk/wash/Mara/History/Mojenjodaro2.pdf",
           read_locator="printed pp. 179-180, 182, 185, 189-190; PDF indices printed-177; English OCR local-only"),
    source("W-S07", "Inequality declined in the Bronze Age city of Mohenjo-daro", "Adam S. Green, Iqtedar Alam and Cameron Petrie", 2026,
           "https://doi.org/10.15184/aqy.2026.10359",
           "data/raw/2026-10-24-urban-form-and-inscription-ecology/western/green2026.pdf",
           read_locator="printed pp. 1244-1250, especially Table 1 p. 1247; PDF indices printed-1239",
           evidence_role="New primary GIS reanalysis of legacy excavation plans, not a new excavation census.",
           edition_caution="Table 1 and prose disagree on one Gini value; n totals do not reconcile within the reviewed article. See table1-conflicts.json."),
    source("W-S08", "Chanhu-Daro Excavations 1935-36", "Ernest J. H. Mackay", 1943,
           "https://archive.org/details/in.ernet.dli.2015.105167",
           "research/literature/sources/mackay_1943_chandaro.pdf",
           read_locator="Preface p. v and printed pp. 1-4; main text PDF indices printed+20; original images and archive OCR checked",
           edition_caution="Printed Mound II area of 3,850 square feet appears problematic relative to circumference and plans; not used as an area denominator."),
    source("W-S09", "A Stone Bead Production Complex from the Beginning of the Indus Civilization at Chanhu-Daro (Sindh, Pakistan)",
           "Florine Marchand, Aurore Didier, David Sarmiento-Castillo, Zakir Khan and Ali K Lashari", 2026,
           "https://doi.org/10.63163/jpehss.v4i1.1141",
           "data/raw/2026-10-21-town-axes/dating/chanhu-daro/marchand2026beads.pdf",
           read_locator="pp. 1-2, Fig. 1 and notes 6-10; PDF indices printed-1",
           edition_caution="Original field-team article in a multidisciplinary journal. Publication record verified 31 March 2026. Independent venue or radiocarbon-method review not performed."),
    source("W-S10", "New evidence of a pre-Indus Settlement at Chanhu-daro and the site's chronological evolution to the post-Indus period",
           "Aurore Didier, Alexandre Houdas, Syed Faraz Ali, Zahir Hussein, Zakir Khan and collaborators", 2026,
           "https://hal.science/hal-05691435",
           "data/raw/2026-10-21-town-axes/dating/chanhu-daro/hal_api_chanhu_abstracts.json",
           source_class_note="Primary excavation-team conference abstract, not an inspected full excavation report.",
           read_locator="HAL API response.docs record halId_s=hal-05691435, abstract_s[0]",
           edition_caution="Abstract-level preliminary statements only; no exact loci, lab codes or sections supplied."),
    source("W-S11", "Measuring the Harappan world: Insights into the Indus order and cosmology", "J. Mark Kenoyer", 2010,
           "https://www.harappa.com/sites/default/files/pdf/Kenoyer%202010%20Measuring%20the%20Harappan%20World.pdf",
           read_locator="printed pp. 118-120; web PDF indices 13-15",
           access_status="Web PDF text inspected; direct acquisition returned HTTP 403.",
           missing_reason="No local source bytes acquired for this publication; local hash unavailable.")
]
for s in SOURCES:
    if s["id"] == "W-S07":
        s["source_class"] = "primary published reanalysis"
        s["rights"] = "CC BY-NC-ND 4.0; local-only research handling; source figures may contain separately copyrighted basemaps"
    if s["id"] == "W-S10":
        s["source_class"] = "primary preliminary conference abstract"

OBS = []
SEQ = {}


def readable(value):
    if not isinstance(value, str):
        return value
    value = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", value)
    value = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", value)
    value = re.sub(r",(?=\S)", ", ", value)
    for before, after in [("PhaseII", "Phase II"), ("PhaseI", "Phase I"), ("PhaseIV", "Phase IV"),
                          ("PhaseV", "Phase V"), ("MoundI", "Mound I"), ("MoundE", "Mound E"),
                          ("MoundAB", "Mound AB"), ("Trenches2", "Trenches 2"),
                          ("atMound", "at Mound"), ("DK-GSouth", "DK-G South"),
                          ("MoundsE", "Mounds E"), ("MainStreet", "Main Street"),
                          ("BuildingA", "Building A"), ("BuildingB", "Building B"),
                          ("BuildingsD", "Buildings D"), ("GreatBath", "Great Bath"),
                          ("Table1", "Table 1"), ("Table 1,p", "Table 1, p"),
                          ("PDFindex", "PDF index"), ("Rcode", "R code")]:
        value = value.replace(before, after)
    return value


def add(town, phase, feature, assertion, sid, page, *, status="excavator-reported observation", basis="Stratigraphic phase assigned by source; no new absolute dating", uncertainty="Source gives no statistical measurement error", missing=None, **kw):
    code = {"dholavira": "DHO", "lothal": "LOT", "harappa": "HAR", "mohenjo-daro": "MD", "chanhu-daro": "CHD"}[town]
    SEQ[code] = SEQ.get(code, 0) + 1
    row = dict(id=f"W-{code}-{SEQ[code]:03d}", town=town, phase=phase,
               feature=feature, assertion=assertion, source_id=sid, locator=page,
               evidence_status=status, dating_basis=basis, uncertainty=uncertainty,
               missing_reason=missing, observer="Codex western-town source module, 2026-10-24")
    row.update(kw)
    for key in ("assertion", "dating_basis", "uncertainty", "missing_reason", "denominator", "locator"):
        if key in row:
            row[key] = readable(row[key])
    OBS.append(row)


# Dholavira. Counts preserve excavated extent, source estimates and ambiguities.
add("dholavira", "site, multi-period", "location", "The site is on Khadir island between the Manhar and Mansar seasonal channels.", "W-S01", "p. 33, PDF index 49; p. 76, index 92", latitude_dms="23°53′10″N", longitude_dms="70°13′E", coordinate_precision="source seconds/minutes; survey accuracy unstated")
add("dholavira", "site, multi-period", "area", "Ancient ruins including the cemetery cover more than 70 ha.", "W-S01", "p. 33, PDF index 49", value=70, operator=">", unit="ha", denominator="All visible ruins including cemetery, not simultaneous inhabited area")
add("dholavira", "site, multi-period", "area_scope_conflict", "Page33 assigns about half of the more-than70ha ancient remains to the fortified settlement, while page158 uses about49ha for the heyday city.", "W-S01", "pp.33,158; PDFindices49,174",status="source area-scope discrepancy",uncertainty="Different extent descriptions and numerical approximations are retained; no preferred footprint selected")
add("dholavira", "full urban form", "area", "The report estimates about 49 ha for the city at its height.", "W-S01", "p. 158, PDF index 174", value=49, operator="approximately", unit="ha", denominator="Heyday city area in water-storage estimate", status="excavator estimate", uncertainty="Approximate; differs from p.33 statement that fortified settlement takes half of >70 ha")
add("dholavira", "full urban form", "enclosure_dimensions", "Lengths measured between retained inner corners are 771.10 m east-west and 616.87 m north-south.", "W-S01", "p. 93, PDF index 109", values=[771.10,616.87], unit="m", denominator="Northern and western enclosure arms between inner corners", uncertainty="Three corners confirmed; southeast corner not found; precision printed is not an error interval")
add("dholavira", "Stage I", "fortification", "The southern wall beneath the castle has an 11 m basal width and about 6.5 m surviving height.", "W-S01", "p. 95 and Fig. 5.1 p.96, PDF indices111-112", dimensions_m={"base_width":11,"surviving_height":6.5}, denominator="One section near southwest castle corner")
add("dholavira", "Stage I", "construction_material", "Buildings use standardized 9×18×36 cm bricks and dressed and undressed stone.", "W-S01", "p.95, PDF index111", materials=["brick, firing unspecified here","dressed stone","undressed stone"], brick_dimensions_cm=[9,18,36])
add("dholavira", "Stage II", "fortification_rebuilding", "A 2.80 m brick masonry addition thickens the Stage I wall on its inner side.", "W-S01", "p.97, PDF index113; Fig.5.3 p.98", value=2.80, unit="m", denominator="One southern defence addition", transition="line retention with inward thickening")
add("dholavira", "Stage II", "maintenance_count", "The added wall face carries at least thirteen white and pink clay plaster applications.", "W-S01", "p.97, PDF index113", value=13, operator=">=", unit="plaster applications", denominator="Stage II inner wall face; applications are not dated years")
add("dholavira", "Stage II", "residential_expansion", "A residential area extends north of the walled nucleus.", "W-S01", "pp.97-98, PDF indices113-114", transition="settlement expansion outside nucleus")
add("dholavira", "Stage III", "clearance_and_replanning", "The Stage II residential area to the north is cleared to create the multipurpose ground.", "W-S01", "p.99, PDF index115", transition="residential growth followed by planned clearance", uncertainty="No assertion that previous housing was unplanned; ground functions remain inferred")
add("dholavira", "Stage III", "fortification_rebuilding", "About 4.5 m of inward brick masonry converts the earlier walled nucleus into the castle.", "W-S01", "p.99, PDF index115", value=4.5, unit="m", denominator="Southern fortification addition; IIIA/IIIB split not given")
add("dholavira", "Stage III", "urban_expansion", "The bailey is added to the west, a walled town is founded to the north, and an outer enclosure surrounds the enlarged complex.", "W-S01", "p.99, PDF index115; Fig.5.2 p.97", transition="addition of coordinated urban divisions", uncertainty="Named divisions are excavator conventions; this statement alone does not date every surviving face")
add("dholavira", "later Stage III", "urban_expansion_after_damage", "Repairs after major damage accompany addition of the lower town and eastward extension of the city enclosure.", "W-S01", "p.99, PDF index115", transition="damage, repair and enlarged enclosure", status="excavator stratigraphic reconstruction", uncertainty="Catastrophe interpreted by source; independent event dating absent")
add("dholavira", "Stage IV", "layout_maintenance", "Gateway, fortification and drainage features of the urban plan continue in use.", "W-S01", "p.100, PDF index116")
add("dholavira", "Stage IV", "inscription_context", "The report places use of the large ten-sign inscription in Stage IV.", "W-S01", "p.100, PDF index116", status="excavator phase attribution", uncertainty="Use-stage attribution does not itself supply a securely dated fabrication event")
add("dholavira", "Stages IV-V, excavated lower town", "street_count", "Fourteen small streets are exposed, six branching from the east-west arterial street and eight from the north-south one.", "W-S01", "p.134, PDF index150, §6.5.4.3", value=14, unit="exposed small streets", denominator="Excavated Lower Town, publication extent; not all streets of the city")
add("dholavira", "Stages IV-V, excavated lower town", "housing_block_count", "Around seventeen housing blocks have been identified.", "W-S01", "p.135, PDF index151, §6.5.4.6", value=17, operator="approximately", unit="housing blocks", denominator="Excavated Lower Town; blocks are not houses", uncertainty="Source's smallest/largest block figures use unclear linear/area units and are not converted")
add("dholavira", "Stages IV-V, excavated lower town", "street_width", "The reported arterial street has widths 4.75–5.05 m; other arterial candidates are 5.2–5.8 m wide.", "W-S01", "p.134, PDF index150", range_m=[4.75,5.05], additional_range_m=[5.2,5.8], denominator="Exposed street segments, not whole-town average")
add("dholavira", "Stages IV-V, excavated lower town", "lane_width", "Lanes are 1.2–1.7 m wide, while two exposed by-lanes are 0.90 m wide.", "W-S01", "p.134, PDF index150, §§6.5.4.4-5", lane_range_m=[1.2,1.7], by_lane_width_m=.90, denominator="Reported exposed lower-town lanes")
add("dholavira", "Stages IV-V, excavated lower town", "construction_material", "Lower-town walls use rubble and ashlar masonry in mud mortar, sometimes with 40×20×10 cm mud bricks.", "W-S01", "p.135, PDF index151", materials=["rubble stone","ashlar stone","mud mortar","mud brick"], brick_dimensions_cm=[40,20,10])
add("dholavira", "Stages IV-V, excavated lower town", "sanitation", "Short house drains discharge to partly buried soakage jars by sub-streets.", "W-S01", "p.135, PDF index151", denominator="Excavated lower-town housing; excludes castle system")
add("dholavira", "probably later Stage V", "street_encroachment", "The report identifies encroachments at several lower-town streets.", "W-S01", "p.134, PDF index150", status="observation with tentative phase attribution", transition="planned street space subsequently occupied", uncertainty="Later Stage V attribution is explicitly probable, not fixed")
add("dholavira", "Stage V", "named_street_encroachment", "A Stage V wall narrows the originally 5.25 m wide north-south street at Trench 15x24.", "W-S01", "p.137, PDF index153, example (5)", value=5.25, unit="m original width", denominator="One named trench and street", transition="street narrowed by later wall", missing="Later remaining width not reported")
add("dholavira", "Stages IV-V", "street_side_platforms", "Platforms outside houses occupy earlier street space in the lower town.", "W-S01", "p.135, PDF index151", transition="street narrowing through platform additions", uncertainty="Sitting, entertainment and selling are alternative source interpretations, not measured uses")
add("dholavira", "Stage VI", "urban_contraction", "Settlement contracts to the citadel and southern middle town; some old enclosures remain and a new northern boundary is built.", "W-S01", "p.103, PDF index119", transition="contraction, selective reuse and new delimitation")
add("dholavira", "Stage VI", "construction_change", "The report describes a different domestic layout and abandonment of brick use.", "W-S01", "p.103, PDF index119", transition="change in building practice", uncertainty="Stage-level report; no city-wide count of brick-free houses")
add("dholavira", "Stage VI", "seal_form_change", "Inscribed seals become long rectangular forms without animal motifs, with flat, triangular or wagon-vault backs.", "W-S01", "p.103, PDF index119", status="excavator typological observation", uncertainty="No object-by-object counts supplied in this passage")
add("dholavira", "Stage VII", "house_form_change", "After an occupation gap of unknown length, circular houses appear.", "W-S01", "p.104, PDF index120", transition="reoccupation with changed house form", uncertainty="Gap duration unknown; circular form does not quantify household autonomy")
add("dholavira", "urban heyday, several stages", "reservoir_count", "The report reconstructs sixteen or more reservoirs within the city walls.", "W-S01", "p.157, PDF index173", value=16, operator=">=", unit="reservoirs", denominator="Excavator reconstruction of walled city, some awaiting excavation", status="excavator reconstruction", uncertainty="Not sixteen fully excavated and independently dated reservoirs")
add("dholavira", "urban heyday", "reservoir_area", "Reservoirs tentatively occupy about 10 ha of a 49 ha city, revising an earlier 17 ha estimate.", "W-S01", "p.158, PDF index174", value=10, unit="ha", denominator="Approximately49ha heyday city", superseded_estimate_ha=17, status="excavator estimate", uncertainty="Tentative area budget; not contemporaneity-certified capacity")
add("dholavira", "multi-stage water works", "dam_count", "The report identifies evidence of three dams across the Manhar and two across the Mansar.", "W-S01", "pp.156-157, PDF indices172-173", value=5, unit="dam locations", denominator="Two channels surveyed; no single-phase contemporaneity established")
for phase,a,b in [("I",3000,2900),("II",2900,2800),("III",2800,2500),("IV",2500,2100),("V",2100,2000),("VI",1950,1800),("VII",1500,1450)]:
    add("dholavira", "Stage "+phase, "occupation_interval", f"The report assigns Stage {phase} approximately {a}–{b} BCE.", "W-S01", "chronology table pp.104-105, PDF indices120-121", status="source chronological model", basis="Stratigraphy and typological comparisons; limited thermoluminescence checks discussed separately", uncertainty="Approximate source BCE range; not a calibrated construction boundary", start_bce=a,end_bce=b)

# Harappa: retain edition identity and both incremental expansion and later enclosure.
add("harappa", "site, multi-period", "area", "The excavation project's 1991 estimate is at least150ha, replacing uncertain geometric extrapolations from a3.5mile circuit.", "W-S04", "pp.32-33, PDF indices5-6", value=150, operator=">=", unit="ha", denominator="Estimated site spread, not simultaneous occupied area", status="excavation-project estimate")
add("harappa", "site, multi-period", "location", "The settlement occupies a low Pleistocene terrace between the Ravi and ancient Beas river systems.", "W-S03", "manuscript p.6, PDFindex5",uncertainty="Palaeochannel history is a separate question; this is the source's geographical description")
add("harappa", "Ravi, Period1A-B", "occupation_interval", "The2005 revised manuscript places Ravi occupation earlier than3900BC to about2800BC.", "W-S03", "Table2,manuscript p.6, PDFindex5",status="historical source chronological model",basis="Excavation-project chronology current to the manuscript revision",uncertainty="Older date model; no new calendar boundary or preferred earliest occupation date assigned",end_bce=2800,start_bce=3900,start_operator=">")
add("harappa", "Ravi, Period1", "early_house_material", "Early huts have wooden posts and plastered reed walls.", "W-S03", "manuscript p.7, PDFindex6",materials=["wooden posts","plastered reeds"],uncertainty="Mud-brick fragments identified as a possible kiln do not establish mud-brick houses in these excavated levels")
add("harappa", "Harappan, Period3", "occupation_interval", "The source places the mature urban phase around2600–1900BCE.", "W-S03", "Table1,manuscript p.3 and Table2,p.6,PDFindices2,5",start_bce=2600,end_bce=1900,status="source phase chronology",basis="Conventional archaeological phase ranges; radiometric evidence not newly analyzed",uncertainty="Approximately700year cultural phase, not demonstrated duration of each neighborhood")
add("harappa", "Late Harappan, Periods4-5", "occupation_interval", "The source places the transitional phase around1900–1800BC and the late phase about1800BC to after1300BC.", "W-S03", "Table2,manuscript p.6,PDFindex5",status="source phase chronology",basis="Source archaeological sequence with question marks on1800BC division",uncertainty="Retain source uncertainty and open terminal bound; occupation is not simply finished in1900BCE")
add("harappa", "Kot Diji, Period2", "settlement_extent", "Settlement extends over more than25ha on Mounds AB,E and parts of ET.", "W-S03", "manuscript p.9, PDF index8", value=25, operator=">", unit="ha", denominator="Kot Diji settlement extent", status="excavation-project estimate", basis="Period2 stratigraphy, source conventional c2800–2600BCE")
add("harappa", "Kot Diji, Period2", "construction_material", "Houses, platforms and perimeter walls use two sizes of mud bricks with1:2:4 proportions.", "W-S03", "manuscript p.9, PDF index8", materials=["mud brick"], brick_ratio=[1,2,4])
add("harappa", "Kot Diji, Period2", "layout", "North-south and east-west streets and houses occur before the mature Harappan expansion.", "W-S03", "manuscript p.9, PDF index8", uncertainty="Orientation is source description, not a new surveyed north measurement")
add("harappa", "Harappan, Period3", "settlement_extent", "The city grows to about150ha with three large mounds and associated suburbs.", "W-S03", "manuscript p.11, PDF index10", value=150, operator="approximately", unit="ha", denominator="Source synthesis of mature urban extent", status="excavation-project reconstruction")
add("harappa", "Harappan, Period3", "house_material_and_amenities", "Fired-brick multistorey houses include bathing areas, latrines and drains connected to larger drains.", "W-S03", "manuscript p.11, PDF index10", materials=["fired brick"], denominator="Reported houses; no total or prevalence denominator supplied")
add("harappa", "Harappan, Period3", "street_width", "Some main streets exceed8m in width.", "W-S03", "manuscript p.11, PDF index10", value=8, operator=">", unit="m", denominator="Some major streets, not all streets")
add("harappa", "Harappan, Period3", "street_form", "Some main streets have central dividers.", "W-S03", "manuscript p.11, PDF index10", uncertainty="Regulation of two-way ox-cart traffic is source interpretation")
add("harappa", "Harappan, expanding urban settlement", "extra_mural_growth", "Occupation outside Mound E's enclosure is subsequently incorporated inside a newly built wall.", "W-S05", "p.9, PDF index8", transition="extra-mural growth followed by enclosure", status="excavation-director synthesis", uncertainty="Sequence is relative; this passage supplies no duration or detailed street plan")
add("harappa", "Harappan, expanding urban settlement", "extra_mural_growth", "Mound F north of Mound AB follows the same growth-then-enclosure pattern.", "W-S05", "p.9, PDF index8", transition="extra-mural growth followed by enclosure", status="excavation-director synthesis")
add("harappa", "Harappan", "unresolved_boundary", "The reviewed synthesis reports no demonstrated enclosure for Area J or western habitation on former dump areas.", "W-S05", "p.9, PDF index8", status="reported evidence gap", missing="No wall demonstrated there; absence of discovery is not proof of an unenclosed quarter")
add("harappa", "Late Harappan", "street_encroachment", "The manuscript reports houses and workshops encroaching on streets.", "W-S03", "manuscript p.16, PDF index15", transition="street occupation after urban layout", status="excavation-director synthesis", uncertainty="Overcrowding and refugee arrival are interpretations; brick robbing removed much late occupation")
add("harappa", "Harappan3A onward", "fired_brick_adoption", "Fired bricks enter gradually through drains and then buildings after the beginning of3A.", "W-S11", "p.118, web PDF index13", transition="selective material adoption", uncertainty="Gradual source sequence; not a precise initial year")
add("harappa", "Harappan3B", "brick_dimensions", "Pristine gateway structures around2450BCE use7×14×28cm fired bricks.", "W-S11", "p.118, web PDF index13", brick_dimensions_cm=[7,14,28], materials=["fired brick"], denominator="MoundE/ET gateway, selected original constructions", uncertainty="Approximate phase chronology; not all3Bbricks")
add("harappa", "Harappan3C", "brick_dimensions", "Late gateway walls around2000–1900BCE use about5×12×24cm fired bricks.", "W-S11", "pp.118-119, web PDF indices13-14", brick_dimensions_cm=[5,12,24], materials=["fired brick"], denominator="Late gateway walls; retained printed values", uncertainty="Source calls ratio unchanged although5:12:24 is approximate, not exact1:2:4")
add("harappa", "Harappan3", "gate_and_street_width", "MoundE's southern gateway is2.8m wide, while the street entering the settlement is5m wide.", "W-S11", "pp.119-120, web PDF indices14-15", gate_width_m=2.8,street_width_m=5, denominator="One southern gateway and its interior street")
add("harappa", "Harappan3", "gate_width", "The eastern gateway by MoundsE/ET is2.6m wide.", "W-S11", "p.120, web PDF index15", value=2.6,unit="m", denominator="One eastern gateway")
add("harappa", "Harappan3", "well_dimensions", "A MoundAB well has1.2m internal diameter with36 wedge-shaped bricks per course.", "W-S11", "p.119, web PDF index14", internal_diameter_m=1.2,bricks_per_course=36, denominator="One well; not a site-wide well count")
add("harappa", "Harappan3", "well_dimensions", "Other reported wells range from1 to2m internal diameter.", "W-S11", "p.119, web PDF index14", range_m=[1,2],denominator="Reported wells on major mounds; sample n unspecified")
add("harappa", "Harappan3", "fortification_material", "Large10×20×40cm mud bricks are faced by smaller7×14×28cm fired bricks in the city walls.", "W-S11", "p.119, web PDF index14", materials=["mud brick core","fired brick facing"], denominator="Source description of Harappan city walls; later rebuilding varies")
add("harappa", "Early Harappan to Harappan", "wall_line_retention", "The later MoundE wall is offset eastward while retaining the earlier alignment, reported10°west of true north.", "W-S11", "p.119, web PDF index14", transition="offset rebuilding with alignment retention", source_north_reference="true north", value=-10,unit="degrees deviation", uncertainty="No statistical angular error stated; direct source measurement, not new computation")

# Lothal: a village-to-urban change and phase-specific encroachment.
add("lothal", "Phase I", "planning_evidence_gap", "The early village's street alignment is unknown because mud buildings were destroyed and excavation was limited.", "W-S02", "p.85, PDF index95", status="explicit source evidence gap", missing="Destroyed early mud architecture and limited exposed area", uncertainty="Cannot classify PhaseI as organic solely because its plan is missing")
add("lothal", "Phase I", "flood_protection", "The village occupied a low natural tell protected by a mud bund52ft wide at base and42ft at top.", "W-S02", "p.85, PDF index95", dimensions_ft={"base":52,"top":42},materials=["mud bund"])
add("lothal", "Phase II", "replanning", "After flood damage, builders reinforced the perimeter and raised housing on mud-brick platforms.", "W-S02", "pp.29,85, PDF indices39,95", transition="damaged settlement followed by major coordinated rebuilding", basis="Source structural sequence; c2350BC is Rao's cross-dated phase chronology")
add("lothal", "PhaseII onward", "block_count", "Seven rectangular blocks have been traced.", "W-S02", "pp.85-86, PDF indices95-96", value=7,unit="exposed blocks",denominator="Excavation extent at publication; not houses or full town blocks")
add("lothal", "PhaseII onward", "platform_height", "Houses stand on platforms4–12ft high.", "W-S02", "p.85, PDF index95", range_ft=[4,12],materials=["mud brick","mud"],denominator="Reported raised housing blocks")
add("lothal", "multi-phase structural remains", "street_count", "Nine streets and twelve lanes have been traced.", "W-S02", "p.87, PDF index97", count_streets=9,count_lanes=12,denominator="Exposed network at report publication; phase membership not individually enumerated")
add("lothal", "PhasesII-III", "layout_persistence", "The report describes retention of block and house layouts through reconstruction, with little subdivision of large rooms and courts.", "W-S02", "p.86, PDF index96", transition="rebuilding with layout retention", status="excavator interpretation of repeated plans", uncertainty="No measured persistence fraction or complete room census supplied")
add("lothal", "before PhaseIV", "encroachment_record", "Rao reports no observed street encroachment before PhaseIV.", "W-S02", "p.87, PDF index97", status="excavator negative observation", denominator="Exposed street segments", uncertainty="Publication statement, not evidence for complete town coverage")
add("lothal", "PhaseIV", "street_encroachment", "Street encroachment appears in PhaseIV, with attempts to retain the original alignments.", "W-S02", "p.87, PDF index97", transition="encroachment within persistent street alignment")
add("lothal", "PhaseV, PeriodB", "construction_change", "Later inhabitants use mainly mud houses; the report describes no new coherent street layout.", "W-S02", "p.87, PDF index97", transition="changed building and street practice", uncertainty="Rao's judgment about inhabitants' resources or inclination is not an observed variable")
add("lothal", "PeriodB", "sanitation_maintenance", "Soakage jars and occasional small brick-bat drains continue in use.", "W-S02", "p.87, PDF index97", materials=["pottery jars","reused brick fragments"],transition="sanitation persists with changed construction")
add("lothal", "Acropolis, multi-phase", "sanitation_layout", "Baths at the rear of houses mostly drain along lanes rather than main streets; the lower town uses soakage jars by house outlets.", "W-S02", "p.87, PDF index97", denominator="Reported exposed Acropolis and lower-town structures")
add("lothal", "PhaseIIa", "basin_construction", "The report assigns construction of the basin called the dock to PhaseIIa.", "W-S02", "p.125, PDF index135; p.44, PDF index54", basis="Source phase chronology based on cross-dating and radiocarbon anchors, not a directly dated foundation", uncertainty="Dock function is an interpretation; source plate volume missing")
add("lothal", "PhaseIV", "hydraulic_rebuilding", "An eastern inlet replaces earlier inlet arrangements after PhaseIIIb damage; drains through the western wall are closed.", "W-S02", "pp.125-126, PDF indices135-136; Fig.19 p.124", transition="inlet reconfiguration and drain blocking")
add("lothal", "multi-phase structural remains", "source_direction_conflict", "Pages86 and87 reverse the stated compass directions of Street1 and Street6.", "W-S02", "pp.86-87, PDF indices96-97", status="source contradiction", missing="PlateXXXVIII and a surveyed street-label match are needed", uncertainty="Neither prose version selected as correct")
add("lothal", "town, multi-period", "extent", "The report describes a roughly1800ft north-south by1200ft east-west town, with remains beyond the current mound.", "W-S02", "p.85, PDF index95", dimensions_ft=[1800,1200],denominator="Reconstructed town spread including peripheral indications; not excavated area", uncertainty="Rounded dimensions and unexcavated outskirts; no population density derived")
add("lothal", "PhaseI onward", "chronology_model", "Rao derives PhaseI around2450BC, PhaseII around2350BC, and the end ofVb around1600BC.", "W-S02", "p.44, PDF index54", status="source chronological model", basis="Cross-dating, assumed durations of building phases and historical radiocarbon arithmetic", uncertainty="Older sourceBC chronology, not modern calibrated occupation boundaries; source has inconsistentIIA wording")
add("lothal", "site, multi-period", "location", "The mound lies in the Bhal alluvial lowland at the boundary of Saragwala and Laxmipura villages.", "W-S02", "p.18, PDFindex28, §A Location; environs p.19",latitude_dms="22°31′25″N",longitude_dms="72°14′25″E",coordinate_precision="Historical report coordinate; survey accuracy unstated",uncertainty="Reported coordinate retained as its own assertion; no new modern georeferencing or river-course reconstruction")

# Mohenjo-daro: distinguish observed infrastructure, extrapolations and reanalysis.
add("mohenjo-daro", "site, multi-period", "location_extent", "The urban remains extend over250ha west of the Indus in the southern alluvial plain.", "W-S03", "manuscript p.17, PDF index16", value=250,operator=">",unit="ha",denominator="Source estimate of ruins, not excavated or simultaneously occupied area",status="source settlement estimate",uncertainty="Boundaries obscured by alluvium and water table")
add("mohenjo-daro", "before mature Harappan", "early_occupation", "A2021excavation-director synthesis identifies KotDiji-phase pottery beneath both western and lower-city areas, including old deep cores.", "W-S05", "p.5,PDFindex4,Fig.3p.6",status="excavation-director synthesis including ongoing unpublished ceramic study",basis="Ceramic attribution from deep excavations and1964–65cores",uncertainty="Does not reconstruct a preurban street plan or precisely date the city's founding; deeper deposits lie below water table")
add("mohenjo-daro", "mature urban architecture", "well_count_estimate", "Jansen extrapolates at least700wells from available well distributions to the unexcavated built-up area.", "W-S06", "p.180, PDF index3", value=700,operator=">=",unit="estimated wells",denominator="Extrapolated whole built-up city",status="published extrapolation",uncertainty="Not700 excavated, phase-contemporary wells; no confidence interval")
add("mohenjo-daro", "mature urban architecture", "well_catchment_estimate", "The available distribution implies an average25m catchment radius per well.", "W-S06", "p.180, PDF index3",value=25,unit="m",denominator="Average from available data; spatial estimator, not measured service ownership",status="published estimate")
add("mohenjo-daro", "mature urban architecture", "bathing_platform", "Domestic bathing platforms are generally at most2m² and drain through a wall outlet.", "W-S06", "p.179, PDF index2",value=2,operator="<=",unit="m²",denominator="Typical feature description; no prevalence census")
add("mohenjo-daro", "GreatBath complex", "water_structure_dimensions", "The GreatBath complex covers about1700m², with a basin approximately12×7m and2.4m deep.", "W-S06", "pp.182,185, PDF indices5,8",complex_area_m2=1700,basin_dimensions_m=[12,7,2.4],denominator="One complex; pool and whole-building footprint distinguished")
add("mohenjo-daro", "GreatBath complex", "waterproofing_material", "The basin uses carefully laid bricks with gypsum mortar and a bitumen layer between brick shells.", "W-S06", "p.185, PDF index8",materials=["fired brick","gypsum mortar","bitumen"],uncertainty="Religious use remains an interpretation; no cult-specific material identified in this account")
add("mohenjo-daro", "mature urban architecture", "drain_dimensions", "Typical covered street drains are17–25cm broad and15–50cm high.", "W-S06", "p.189, PDF index12",width_cm=[17,25],height_cm=[15,50],materials=["brick","clay mortar","removable covers"],denominator="Typical drain cross sections reported; not every segment")
add("mohenjo-daro", "mature urban architecture", "drain_maintenance", "Removable covers and settling pits provide access to deposits that require periodic clearance.", "W-S06", "p.189, PDF index12",status="observed design with maintenance inference",uncertainty="Institution, workforce and financing are unknown")
add("mohenjo-daro", "successive DK-G occupations", "drain_rebuilding", "Three successive drain rebuilding phases occur at differing levels within DK-G.", "W-S06", "p.190, PDF index13",value=3,unit="drain rebuilding phases",denominator="DK-G deep excavation, not city-wide phases",transition="local infrastructure rebuilt asynchronously",uncertainty="Absolute elevation cannot establish site-wide contemporaneity")
add("mohenjo-daro", "IntermediateIII to LateII/I, DK-GSouth", "layout_regularization", "GIS reanalysis finds later houses more closely aligned with the streets.", "W-S07", "p.1242,Fig.3 p.1243; discussion p.1249",status="published primary reanalysis",transition="increasing street-house alignment",basis="Legacy relative phases reconstructed from Mackay; absolute century labels assigned by model",uncertainty="No new orientation values measured in this module")

SERIES=[]
for phase,date,n,med,gini,ml,lsd in [("Intermediate III",2500,12,161.39,.39,4.98,.73),("Intermediate II",2400,36,117.06,.32,4.84,.55),("Intermediate I",2300,34,112.69,.32,4.83,.56),("Late III",2200,15,98.02,.30,4.73,.55),("Late II and I",2100,35,141.13,.23,4.91,.44)]:
    base=dict(phase=phase,area="DK-G South",approximate_bce=date,n=n,median_area_m2=med,gini=gini,mean_log_area=ml,log_standard_deviation=lsd,source_id="W-S07",locator="Table1,p.1247; PDFindex8",date_status="model-assigned century, not measured calendar date")
    SERIES.append(base)
    for feature,val,unit in [("residence_sample_count",n,"residence areas in phase sample"),("median_residence_area",med,"m²"),("residence_area_gini",gini,"Gini coefficient")]:
        add("mohenjo-daro",phase+", DK-GSouth",feature,"Published phase sample statistic.","W-S07","Table1,p.1247; PDFindex8",status="published statistic from legacy-plan reanalysis",basis="Relative phase; century label assigned by dividing assumed c2500–1900 occupation span",uncertainty="Grouping depends on original excavators' residence definitions; Gini study uses80%confidence intervals, not transcribed here",value=val,unit=unit,n=n,denominator="Residence polygons in this DK-GSouth phase sample",approximate_bce=date)
add("mohenjo-daro", "legacy excavation plans", "residence_definition", "The2026 study uses the excavators' room groupings as residences and identifies possible public buildings in some area samples.", "W-S07", "pp.1245-1246,1250; PDFindices6-7,11",status="published method and limitation",uncertainty="Alternative household groupings can change areas and inequality estimates")
add("mohenjo-daro", "legacy excavation plans", "sample_count_conflict", "Methods report309residence areas; Table1 area rows and phase rows do not reconcile with that count.", "W-S07", "pp.1246-1247; PDFindices7-8",status="source audit discrepancy",missing="Supplementary residence list and Rcode requested via public links but returned403",uncertainty="No corrected denominator inferred")

# Chanhudaro: updated excavation extent is distinct from old mound morphology.
add("chanhu-daro", "site, multi-period", "location", "The site is near Sakrand and Nawabshah, about20km from the present Indus bank.", "W-S09", "p.1, PDFindex0",uncertainty="Modern bank separation, not ancient river distance")
add("chanhu-daro", "visible mounds", "mound_count", "The1935–36 report distinguishes three mounds, with erosion and flood incision contributing to their separation.", "W-S08", "Preface p.v and PlateI",value=3,unit="present archaeological mounds",denominator="Topographic mounds, not proven civic divisions",status="excavator description with geomorphic interpretation")
add("chanhu-daro", "undifferentiated earlier architecture", "wall_extent", "A substantial wall in TrenchA(0) was traced about80ft before cultivation and a tomb enclosure stopped excavation.", "W-S08", "pp.1-2, PDFindices21-22, PlatesIII,X",value=80,unit="ft exposed length",denominator="One partly exposed wall",uncertainty="Building function and continuation unresolved")
add("chanhu-daro", "undifferentiated earlier architecture", "wall_function_gap", "Mackay leaves the purpose of the large TrenchA wall unresolved.", "W-S08", "p.2, PDFindex22",status="explicit source uncertainty",missing="Insufficient wall exposed to identify its structure or defensive role")
add("chanhu-daro", "successive TrenchB(5) levels", "drain_rebuilding", "An upper brick drain overlies a different lower drain made from tapered pottery segments.", "W-S08", "p.3, PDFindex23, PlatesVI.4,XI.d",transition="sanitation rebuilt in different materials",materials=["brick","pottery segments"],uncertainty="Legacy levels have no independently supplied phase-to-calendar join here")
add("chanhu-daro", "first Indus period", "occupation_interval", "Mud-brick levels exposed in2016–2020 are dated around2500–2300BCE in the body text.", "W-S09", "p.2; abstract p.1",start_bce=2500,end_bce=2300,status="field-team chronological attribution",basis="Pottery and radiocarbon analysis cited to Didier etal.2021; determinations not printed here",uncertainty="Abstract gives2600/2500–2300; retain alternative initial bound; no new calibration")
add("chanhu-daro", "first Indus period", "excavated_area", "Trenches2and3 exposed about4200m² of mud-brick architecture in2016–2020.", "W-S09", "p.2,Fig.1,note9",value=4200,unit="m² excavated",denominator="2016–2020exposure ofTrenches2/3",materials=["mud brick"],uncertainty="Exposure area; not city area or one building")
add("chanhu-daro", "first Indus period", "excavated_area_update", "The exposure expanded to6500m² by the2022season.", "W-S09", "p.2,note9andFig.1",value=6500,unit="m² excavated",denominator="Updated2016–2022excavation surface; not additive to4200",uncertainty="Same expanding exposure, not independent sample")
add("chanhu-daro", "first Indus period", "block_count", "At least seven blocks were identified and largely excavated beside MainStreet1.", "W-S09", "p.2,Fig.1",value=7,operator=">=",unit="blocks",denominator="ExposedTrenches2/3, not a full-city block census")
add("chanhu-daro", "first Indus period", "street_width", "MainStreet1 is5–7m wide.", "W-S09", "p.2,Fig.1",range_m=[5,7],denominator="One exposed main street")
add("chanhu-daro", "first Indus period", "storage_cell_count", "BuildingA in the eastern craft quarters has twelve storage cells and larger workshop rooms.", "W-S09", "p.2,Fig.1",value=12,unit="storage cells",denominator="One buildingA inBlocks2/3; not town storage buildings",uncertainty="Storage and workshop uses are functional attributions based on contextual finds")
add("chanhu-daro", "first Indus period", "house_workshop_association", "BuildingsD–H combine houses and workshops around quadrangular orL-shaped courts, with storage and waste areas.", "W-S09", "p.2,Fig.1",denominator="Named excavated complexes; not all town houses",status="field-team spatial and functional reconstruction")
add("chanhu-daro", "first Indus period", "craft_zoning", "BuildingB also supports crafting and areaC is identified with specialized firing activity.", "W-S09", "p.2,Fig.1",status="field-team functional attribution",uncertainty="Manufacturing interpretation must retain tools, waste, heat and deposit evidence; a plan alone is insufficient")
add("chanhu-daro", "pre-Indus through post-Indus", "new_sequence", "The2026excavation-team abstract reports pre-Indus mud-brick levels below the first Indus settlement atMoundI.", "W-S10", "HALabstract_s[0],hal-05691435",status="preliminary excavation-team abstract",basis="2023–2025stratigraphy; firsthalf3rdmillenniumBCE label",uncertainty="Full sections, determinations and source-method details not available in the inspected abstract")
add("chanhu-daro", "MoundI, multi-stage", "retaining_wall", "A massive mud-brick retaining wall with fired-brick exterior facing is reported at the foot ofMoundI.", "W-S10", "HALabstract_s[0],hal-05691435",status="preliminary excavation-team abstract",materials=["mud brick core","fired brick facing"],missing="Specific construction phase, dimensions and relationship to earlier TrenchA wall unresolved")


def main():
    (HERE/"sources.json").write_text(json.dumps(dict(schema_version=1,sources=SOURCES,new_acquisitions_manifest=str(RAW/"acquisitions.json")),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (HERE/"observations.json").write_text(json.dumps(dict(schema_version=1,scope="Five western and southern urban histories; assertion register, not an exhaustive building census",observations=OBS),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (HERE/"mohenjo-daro-residential-series.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(SERIES[0]));w.writeheader();w.writerows(SERIES)
    conflicts=dict(source_id="W-S07",table="Table1,p.1247",conflicts=[
        dict(field="DK-GNorthGini",table_printed=".044",prose="0.44",web_long_description="0.44",decision="Retain conflict; no correction silently imposed"),
        dict(field="sample_n",methods_total=309,table_all_row=162,cross_sectional_area_rows_sum=170,phase_rows_sum=132,decision="Sample relationships unresolved; do not sum into a house census")],supplement_status="Both public supplementary files returnedHTTP403on2026-10-24",date_model="Approximate centuries assigned by dividing assumed2500–1900BC occupation span among relative phases")
    (HERE/"table1-conflicts.json").write_text(json.dumps(conflicts,indent=2)+"\n",encoding="utf-8")
    ids={s['id'] for s in SOURCES}
    assert len({o['id'] for o in OBS})==len(OBS)
    assert all(o['source_id'] in ids and o['locator'] and o['uncertainty'] and o['dating_basis'] for o in OBS)
    counts={t:sum(o['town']==t for o in OBS) for t in sorted({o['town'] for o in OBS})}
    (HERE/"validation.json").write_text(json.dumps(dict(status="pass",assertion_count=len(OBS),source_count=len(SOURCES),town_counts=counts,source_hashes_checked=sum(bool(s['sha256']) for s in SOURCES),rights="No acquired source bytes, images, OCR or source-derived plans included in module"),indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(assertions=len(OBS),sources=len(SOURCES),town_counts=counts)))


if __name__=="__main__":
    main()
