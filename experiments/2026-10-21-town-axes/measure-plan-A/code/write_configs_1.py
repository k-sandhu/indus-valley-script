"""Write the town configs for the plan-A measurement (first batch of towns).

Existing interpretive fields of a config (main system, reason, notes, manual
systems, published values) are kept when the script is rerun.
"""
import json, os
OUT = "experiments/2026-10-21-town-axes/measure-plan-A/config"
RES = "experiments/2026-10-21-town-axes/measure-plan-A/results"
D = "data/raw/2026-10-21-town-axes/plan-A/downloads"
WIKI = ("Wikipedia article coordinates retrieved 2026-10-21 through the MediaWiki API (record in "
        "data/raw/2026-10-21-town-axes/plan-A/wikipedia_coordinates.json); the plan measurements do not depend on them")
GUESS = ("town-list starting guess, not independently verified (no published coordinate retrieved); "
         "the plan measurements do not depend on it")
MARSHALL = ("Marshall, J. (ed.) 1931. Mohenjo-daro and the Indus Civilization, vol. III (plates). London: Arthur "
            "Probsthain. Internet Archive item in.gov.ignca.48270, single-page JP2 at 300 ppi")
BISHT = ("Bisht, R. S. 2015. Excavations at Dholavira (1989-90 to 2004-2005). Preliminary report, January 2015. "
         "New Delhi: Archaeological Survey of India. Internet Archive upload 'Dholavira Report (preliminary, Jan 2015)' "
         "(dholavirareportpreliminaryjan2015_860_K)")
BISHT_FILE = "data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf"
RAO = ("Rao, S. R. 1979. Lothal: A Harappan Port Town (1955-62), vol. I. Memoirs of the Archaeological Survey of "
       "India 78. New Delhi: ASI. Internet Archive item masi78lothalaharappanporttownraos.r.part1platesmissing_443_k")


def src(i, cit, loc, f, idx, label, cls="unspecified", year=None, scale="", res=None, printed=None):
    s = {"id": i, "citation_or_service": cit, "locator": loc, "file": f, "pdf_page_index": idx,
         "north_reference": cls, "north_label_text": label, "survey_year": year, "scale_bar": scale}
    if printed is not None:
        s["printed_page"] = printed
    if res:
        s["result"] = f"{RES}/{res}.json"
    return s


def town(slug, lat, lon, basis, sources):
    return {"town": slug, "location": {"lat": lat, "lon": lon, "basis": basis}, "sources": sources,
            "main_system": None, "main_system_reason": "", "published_values": [], "notes": ""}


towns = {}
towns["mohenjo-daro"] = town("mohenjo-daro", 27.32917, 68.13889, WIKI, [
    src("src1", MARSHALL, "Pl. XXXIX, 'HR Area. A and B Sections, Plan' (plate number from the volume's list of plates); "
        "folding plate, PDF page index 56 of 48270.pdf, JP2 leaf 48270_0056", f"{D}/marshall1931v3/jp2/48270_0056.jp2",
        56, "N", scale="0 to 50 feet", res="mohenjo-daro_marshall_hr"),
    src("src2", MARSHALL, "'VS Area, Plan. A and B Sections' (title from the list of plates; the sheet edge carries "
        "'Pl. LIII', read from the scan with low confidence); folding plate, PDF page index 83, JP2 leaf 48270_0083",
        f"{D}/marshall1931v3/jp2/48270_0083.jp2", 83, "N", scale="10-foot scale, read approximately",
        res="mohenjo-daro_marshall_vs"),
    src("src3", MARSHALL, "'SD Area, Plan of Great Bath and adjoining buildings' (title from the list of plates; plate "
        "number not read from the scan); folding plate, PDF page index 26, JP2 leaf 48270_0026",
        f"{D}/marshall1931v3/jp2/48270_0026.jp2", 26, "N", scale="feet scale, read approximately",
        res="mohenjo-daro_marshall_sd_bath"),
    src("src4", MARSHALL, "'DK Area. Plan of B and C Sections' (title from the list of plates; plate number not read "
        "from the scan); folding plate drawn with north to the left, PDF page index 99, JP2 leaf 48270_0099",
        f"{D}/marshall1931v3/jp2/48270_0099.jp2", 99, "N", scale="0 to 50 feet", res="mohenjo-daro_marshall_dk_bc"),
])
towns["harappa"] = town("harappa", 30.62889, 72.86389, WIKI, [
    src("src1", "Vats, M. S. 1940. Excavations at Harappa, vol. II (plates). Delhi: Manager of Publications. Internet "
        "Archive item in.gov.ignca.9842, single-page JP2",
        "Plan of the Great Granary on Mound F (folding plate drawn with north to the left; plate number not read from "
        "the scan), PDF page index 17, JP2 leaf 9842_0017", f"{D}/vats1940/jp2/9842_0017.jp2", 17, "N",
        scale="present; the plan's survey grid was used as the frame check", res="harappa_vats_granary"),
    src("src2", "Wheeler, R. E. M. 1947. Harappa 1946: the defences and cemetery R 37. Ancient India 3: 58-130. "
        "Internet Archive item in.gov.ignca.18127, single-page JP2 at 600 ppi",
        "Pl. XV, general plan of Harappa with the citadel (Mound AB) and Mound F (folding plate), PDF page index 89, "
        "JP2 leaf 18127_0089", f"{D}/wheeler1947/jp2/18127_0089.jp2", 89,
        "(eight-point compass rose with an arrowhead, no letter)", year=1946, scale="0 to 150 metres",
        res="harappa_wheeler1947_pl15"),
])
towns["kalibangan"] = town("kalibangan", 29.47417, 74.13028, WIKI, [
    src("src1", "Lal, B. B., J. P. Joshi, B. K. Thapar and Madhu Bala 2003. Excavations at Kalibangan: The Early "
        "Harappans (1960-1969). Memoirs of the Archaeological Survey of India 98. New Delhi: ASI. Internet Archive item "
        "masi98excavationsatkalibhanganearlyharappanslalb.b.etall_747_Z",
        "Fig. 1, contour plan of KLB-1 and KLB-2 with the fortification of KLB-1, PDF page index 32",
        f"{D}/kalibangan2003/masi98.pdf", 32, "N", scale="0 to 75 M", res="kalibangan_masi98_fig1"),
    src("src2", "Excavations at Kalibangan, District Ganganagar. In Indian Archaeology 1968-69 - A Review, "
        "pp. 29-31. New Delhi: ASI (1971). Internet Archive item indianarchaeology196869areview_151_x",
        "Plan 'Kalibangan, District Ganganagar, Rajasthan: Harappan Settlement', printed p. 30, PDF page index 37 "
        "(printed sideways; measured on the page image rotated 90 degrees clockwise)",
        f"{D}/iar/iar1968-69.pdf", 37, "N", year=None, scale="50 - 0 - 100 metres",
        res="kalibangan_iar1968-69", printed=30),
])
towns["lothal"] = town("lothal", 22.52139, 72.24944, WIKI, [
    src("src1", RAO, "Fig. 17, 'Lothal 1955-62, Plan of B Block (Phase IV)', printed p. 109, PDF page index 119",
        f"{D}/lothal1979/masi78p1.pdf", 119, "(compass rose with an arrowed shaft, no letter)",
        scale="scale of feet 5-0-15; scale of metres 1-0-5", res="lothal_rao1979_fig17", printed=109),
    src("src2", RAO, "Fig. 18, 'Lothal 1955-62, Warehouse (plan)', printed p. 112, PDF page index 122 (figure printed "
        "sideways)", f"{D}/lothal1979/masi78p1.pdf", 122, "(compass rose with an arrowed shaft, no letter)",
        scale="scale of metres 0-7; scale of feet", res="lothal_rao1979_fig18", printed=112),
])
towns["dholavira"] = town("dholavira", 23.88861, 70.21364, WIKI, [
    src("src1", BISHT, "Fig. 6.1, 'Plan of Dholavira showing the ratios and proportions' (digital colour plan), printed "
        "p. 108, PDF page index 124", BISHT_FILE, 124, "(compass rose with an arrow, no letter)",
        scale="0 to 200 m", res="dholavira_bisht2015_fig6-1", printed=108),
    src("src2", BISHT, "Fig. 6.3, 'Plan of the Castle, Dholavira' (hand-coloured ink drawing), printed p. 110, PDF page "
        "index 126", BISHT_FILE, 126, "(compass rose with a fleur-de-lis pointer, no letter)",
        scale="10 - 0 - 10 metres", res="dholavira_bisht2015_fig6-3", printed=110),
    src("src3", BISHT, "Fig. 2.4, 'Plan showing the various divisions of city of Dholavira' (schematic plan titled "
        "'Dholavira 1990-1998'), printed p. 36, PDF page index 52", BISHT_FILE, 52, "N",
        scale="0 to 150 meters", res="dholavira_bisht2015_fig2-4", printed=36),
])
towns["surkotada"] = town("surkotada", 23.6304, 70.8407, WIKI, [
    src("src1", "Joshi, J. P. 1990. Excavation at Surkotada 1971-72 and Exploration in Kutch. Memoirs of the "
        "Archaeological Survey of India 87. New Delhi: ASI. Internet Archive item "
        "masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t",
        "Fig. 8, 'Plan of structures', titled 'Surkotada: 1971-72, Kutch District, Gujarat' (folding plate), PDF page "
        "index 61", f"{D}/surkotada1990/masi87.pdf", 61, "N", year=1972, scale="0 to 30 metres",
        res="surkotada_joshi1990_plan"),
])
towns["chanhu-daro"] = town("chanhu-daro", 26.174, 68.323, GUESS, [
    src("src1", "Mackay, E. J. H. 1943. Chanhu-daro Excavations 1935-36. American Oriental Series 20. New Haven: "
        "American Oriental Society. Local scan research/literature/sources/mackay_1943_chandaro.pdf",
        "Pl. IV, 'Chanhu-daro: Mound II Harappa II level' (folding plate), PDF page index 367",
        "research/literature/sources/mackay_1943_chandaro.pdf", 367, "MAG. NORTH NOV 2ND 1935", cls="magnetic",
        year=1935, scale="10 - 0 - 40 feet", res="chanhu-daro_mackay1943_pl4"),
])
towns["banawali"] = town("banawali", 29.598, 75.393, GUESS, [
    src("src1", "Bisht, R. S. Excavations at Banawali, District Hissar. In Indian Archaeology 1987-88 - A Review "
        "(entry 39), pp. 21-27. New Delhi: ASI. Local scan data/raw/2026-10-06-evidence-census/sites-deep/"
        "c-north-india/iar1987.pdf", "Fig. 1, 'Banawali Excavations' (site plan), printed p. 22, PDF page index 29",
        "data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/iar1987.pdf", 29, "N", scale="0 to 50 m",
        res="banawali_iar1987_fig1", printed=22),
])

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, v in towns.items():
        p = os.path.join(OUT, k + ".json")
        if os.path.exists(p):
            old = json.load(open(p, encoding="utf-8"))
            for key in ("main_system", "main_system_reason", "notes", "systems", "published_values", "gap_deg"):
                if old.get(key):
                    v[key] = old[key]
            for s_new in v["sources"]:
                for s_old in old.get("sources", []):
                    if s_old["id"] == s_new["id"]:
                        for key in ("line_meta", "exclude", "render_check"):
                            if key in s_old:
                                s_new[key] = s_old[key]
        json.dump(v, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(p)
