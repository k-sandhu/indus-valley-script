"""Freeze the source-scoped targets before tracing or numerical measurement."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
ROOT = PACKAGE.parents[1]
LOCAL = Path("D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west")


def h(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = HERE / "inventory-freeze.json"
    if target.exists():
        raise FileExistsError(target)
    protocol_hash = json.loads((PACKAGE / "PROTOCOL.sha256.json").read_text(encoding="utf-8"))["sha256"]
    assert h(PACKAGE / "PROTOCOL.md") == protocol_hash
    panels = [
        ("PW-P01", "harappa", "W-S04", 22, "p. 49, Fig. 4.12", "Period 2 natural-soil cart tracks", "phase-specific partial exposure", [175, 120, 1003, 1123], ["Cart-track set", "excavation edges", "local grid and natural soil"]),
        ("PW-P02", "harappa", "W-S04", 27, "p. 54, Fig. 4.16", "Period 3 house and upper street levels, 3C encroachment described on p. 56", "composite exposure", [128, 159, 1445, 1082], ["Street NS2355", "cart-track depressions", "encroachment drain", "encroachment paving", "ghost walls", "mud-brick foundation/platform", "brick walls", "pits and oven/kiln"]),
        ("PW-P03", "harappa", "W-S04", 26, "p. 53, Fig. 4.15", "Period 3; earlier gateway and wall repairs superimposed", "composite overall plan", [130, 264, 1435, 820], ["Wall [30]", "wall [40]", "gateway [84]", "earlier gateway [85]", "threshold [83]", "drain [244]", "streets EW990, EW989 and NS2338", "labelled repairs and additions"]),
        ("PW-P04", "harappa", "W-S04", 25, "p. 52, Fig. 4.14", "Wall [40] below wall [30]", "four adjoining section faces", [110, 280, 1440, 810], ["Wall [30]", "wall [40]", "natural soil", "not-excavated region", "root holes and washes"]),
        ("PW-P05", "harappa", "PW-HAR1997", 6, "p. 145, Fig. 3", "three gateway building phases; early and late 3C changes described on pp. 143-146", "composite exposure", [70, 140, 1450, 1005], ["Mound E and ET city walls", "pylons [53] and [82]", "three western drains", "central corbelled drain", "parallel streets", "doors [178] and [178S]", "wall [209]", "ET wall [15] and [16]"]),
        ("PW-P06", "harappa", "PW-HAR1997", 14, "p. 153, Fig. 6, upper plan", "Period 3B architecture cut by late 3C drain", "composite plan", [240, 180, 1385, 660], ["Wall [250]", "curtain wall [296]", "western street and cart tracks", "street [95]", "Room 92", "hearths", "drain channel"]),
        ("PW-P07", "harappa", "PW-HAR1997", 14, "p. 153, Fig. 6, lower section", "Period 2 beneath Period 3", "section with plan correlation", [240, 670, 1385, 1040], ["Wall [250]", "wall [296]", "street deposits", "Room 92", "street [95]", "Period 2 hearths and natural soil"]),
        ("PW-P08", "harappa", "HARP-TR54-TOP", None, "Harappa 2000-2001, slide 46", "Periods 2, 3A, 3B and 3C", "explicit multi-period composite", None, ["Period 2 masonry", "city-wall void", "3A mud-brick walls", "3B masonry and hearths", "3C robbed walls", "kiln dump", "sumps", "south extension"]),
        ("PW-P09", "harappa", "HARP-TR54-DETAIL", None, "Harappa 2000-2001, slide 48", "Period 3B, according to overview; individual superpositions remain", "partial detail plan", None, ["Wall voids [520], [603], [549], [548]", "walls [518], [604], [606]", "stairs [605]", "platform [613]", "rooms [517], [610], [611], [612]", "hearths and pits"]),
        ("PW-P10", "harappa", "HARP-TR54-WEST-SECTION", None, "Harappa 2000-2001, slide 83", "Period 2 material and Harappan masonry with later robbing", "section", None, ["platform/wall [491]", "wall [600]", "wall/platform [598]", "robbed wall [594]", "fill [597]", "brick-robber trench fill"]),
        ("PW-P11", "harappa", "HARP-TR39-P2", None, "Harappa Excavations 1995-2001, slide 26", "Period 2, with later Period 3 drain shown for context", "partial phase plan with later reference feature", None, ["mud-brick wall [550]", "walls [184], [530]", "Room [731] and wall [28]", "open drain", "hearths", "gully", "later baked-brick drain"]),
        ("PW-P12", "harappa", "HARP-TR39-P3", None, "Harappa Excavations 1995-2001, slide 63", "3B drain [8], 3C wall [50] and later wall fragments", "multi-period composite", None, ["drain [8]", "wall [50]", "walls/features [10]-[21]", "wall void [49]", "mud brick [56]", "gully"]),
        ("PW-P13", "harappa", "HARP-INSIDE-WALL250", None, "Harappa Excavations 1995-2001, slide 85", "superimposed Period 3C levels", "six partial views from 1999 and 2001 excavation seasons", None, ["upper and lower rooms", "wall voids", "mud-brick paving", "nodular debris", "late 3C drain"]),
        ("PW-P14", "harappa", "HARP-MOUND-E-ET", None, "Harappa Excavations 1995-2001, slide 72", "Periods 3B/3C plus deeper sounding", "composite excavation plan", None, ["wall [250]", "inside and outside streets", "Trenches 9, 10 and 11", "curtain wall and late drain"]),
        ("PW-P15", "dholavira", "W-S01", 112, "p. 96, Fig. 5.1", "Stages I-VII", "explicitly schematic section", [300, 180, 835, 1530], ["Stage I defence", "Stage II coats", "Stage IIIA and IIIB masonry", "successive pathways", "Stage IV-VII deposits", "unexcavated regions"]),
        ("PW-P16", "dholavira", "W-S01", 132, "p. 116, Fig. 6.9", "gate composite; two later blockings not assigned to a single stage", "composite plan", [176, 611, 982, 1480], ["chamber", "passage", "two later blocking labels", "door sills and steps", "fortification", "terrace and pathway"]),
        ("PW-P17", "dholavira", "W-S01", 137, "p. 121, Fig. 6.19", "earlier wall plaster and Late Harappan additions shown together", "composite plan", [630, 900, 1049, 1426], ["central passage", "flanking chambers", "landing and steps", "earlier-wall plaster", "Late Harappan walls", "terrace", "ceremonial pathway"]),
        ("PW-P18", "dholavira", "W-S01", 126, "p. 110, Fig. 6.3", "full Castle model", "reconstructed/general plan based on partial excavation", [140, 569, 1017, 1226], ["fortification", "interior axial divisions", "water features", "gates"]),
        ("PW-P19", "dholavira", "W-S01", 149, "p. 133, Fig. 6.26", "unseparated exposed Lower Town remains", "oblique photograph", [178, 19, 1048, 1490], ["reported arterial street", "flanking exposed structures"]),
        ("PW-P20", "dholavira", "W-S01", 160, "p. 144, Fig. 6.32", "well, tanks and drains without a phase legend", "composite plan with dashed continuations", [145, 240, 1008, 1335], ["well", "two tanks", "channels", "outer drain", "dashed continuations", "fortification"]),
        ("PW-P21", "lothal", "W-S02", 119, "p. 109, Fig. 17", "Phase IV, including IVa labels", "single phase-labelled plan", [103, 277, 1083, 1248], ["Streets 2 and 3", "houses 171.IVa and 172.IVa", "two labelled entrances", "passage", "verandah", "drain", "soakage jar", "source-labelled vat and altar"]),
        ("PW-P22", "lothal", "W-S02", 111, "p. 101, Fig. 16", "not separated in the drawing", "plan, section and isometric source illustration", [130, 120, 1080, 1403], ["public drain 15A", "cesspool", "damaged wall", "sockets and source-interpreted screen groove"]),
        ("PW-P23", "lothal", "W-S02", 134, "p. 124, Fig. 19", "first and second inlet arrangements shown together", "isometric source reconstruction", [200, 111, 986, 1447], ["first inlet", "second inlet", "western drain", "embankment", "basin and spillway"]),
    ]
    panel_records = [dict(id=a, town=b, source_id=c, pdf_page_index=d, locator=e, phase=f, panel_class=g, crop_pixels=h_, named_feature_inventory=i)
                     for a,b,c,d,e,f,g,h_,i in panels]
    endpoints = [
        ("PW-M01", "PW-P03", "Clear gateway [84] opening between opposed masonry faces", "single-panel dimension; reject if phase-specific faces cannot be identified"),
        ("PW-M02", "PW-P10", "Robber-trench width between walls [491] and [600] at the labelled 2.18 m cross-section", "digitization check against a published dimension"),
        ("PW-M03", "PW-P16", "East Gate passage width at its middle, clear of steps and blockings", "single-panel geometry, no claim of continued access"),
        ("PW-M04", "PW-P17", "North Gate passage width between flanking chambers", "coarse single-panel geometry limited by image resolution"),
        ("PW-M05", "PW-P20", "Internal well diameter", "single-panel dimension; no water-capacity calculation"),
        ("PW-M06", "PW-P21", "Passage width between houses 171.IVa and 172.IVa", "single-phase geometry; no pre/post narrowing rate"),
        ("PW-M07", "PW-P21", "Northern entrance of house 172.IVa facing Street 3", "opening geometry; no custody-change classification"),
        ("PW-R01", "PW-P01/PW-P02", "Area C independent-grid registration and common exposure", "similarity transform on surveyed grid crosses, no feature-based fit or survivor rate"),
    ]
    missing = [
        dict(id="PW-X01", town="dholavira", target="Lower Town trench 15x24 before/after Stage V street wall", reason="The target chapter gives 5.25 m earlier width and later encroachment but no phase-keyed plan; Fig. 6.26 is an unlocated street photograph."),
        dict(id="PW-X02", town="lothal", target="Complete street network and Phases II/III versus IV plans", reason="Held Volume I lacks plates, including Plate XXXVIII named for the street network; Fig. 17 is only Phase IV Block B."),
        dict(id="PW-X03", town="harappa", target="Street persistence minus internal partition persistence", reason="No selected pair yet supplies complete comparable exposure of both classes; preserve source sequences and registration only."),
        dict(id="PW-X04", town="harappa", target="Trench 39N Period 2 versus Period 3 full exposure", reason="Later source panel combines 3B and 3C; the panels cover different extents. Audit their phase and survey controls without computing a survival fraction."),
        dict(id="PW-X05", town="lothal", target="Dock/inlet lengths from Fig. 19", reason="The original figure is explicitly isometric; a printed scale bar alone does not remove projection foreshortening."),
    ]
    snapshots = [dict(path=str(p.relative_to(ROOT)).replace('\\','/'), sha256=h(p)) for p in [PACKAGE / "PROTOCOL.md", PACKAGE / "PROTOCOL.sha256.json", PACKAGE / "MEASUREMENT-RULES.md", HERE / "sources-initial.json", Path(__file__)]]
    snapshots += [dict(physical_path=str(p), sha256=h(p)) for p in sorted(LOCAL.glob("*-index-v*.json")) + sorted(LOCAL.glob("acquisition-routes-v*.json"))]
    data = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=protocol_hash,
                status_class="exploratory", freeze_stage="after source-panel visual audit, before endpoint digitization, registration fitting or numerical scoring",
                authors=[dict(model="GPT-6 family; exact serving variant unknown", harness="Codex desktop", agent="western_towns")],
                prior_exposure="Earlier town comparison, source examples and documentary histories are known. We have not read or received the newly assembled documentary overlay from the parallel module. No blinding or fresh confirmation is claimed.",
                completeness_scope="This is the bounded inventory of named features and numerical targets in the selected original panels. It is not a complete census of every line, every exposed structure, or either survivor class. That missing census blocks the persistence contrast.",
                selected_panels=panel_records, numerical_targets=[dict(id=a,panel=b,target=c,estimand_scope=d) for a,b,c,d in endpoints],
                source_failure_targets=missing, reading_uncertainty_rule="Use endpoint-radius and independently uncertain scale-endpoint bounds from MEASUREMENT-RULES.md; carry unknown source survey and scan errors separately.",
                stopping_rule="No extra town or endpoint is selected to improve the observed result. Preserve rejected targets with reasons. Later additions require a dated amendment before measurement.",
                snapshots=snapshots)
    target.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (HERE / "inventory-freeze.sha256.json").write_text(json.dumps(dict(path=target.name,sha256=h(target),created_utc=data["created_utc"]),indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(panels=len(panel_records),numerical_targets=len(endpoints),unavailable_targets=len(missing),sha256=h(target))))


if __name__ == "__main__":
    main()
