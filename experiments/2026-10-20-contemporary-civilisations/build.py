"""Build civilisations.html from civilisations.json (see NOTES.md for sources and methods).

Adds display fields only: short names, the kind of area each extent measures, and the densely settled
Indus core that Fisher (2018) separates from the wider distribution of sites, quoted in the Indus
extent basis. No number in civilisations.json is changed.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "civilisations.json"
TEMPLATE = HERE / "template.html"
OUT = HERE / "civilisations.html"

SHORT = {
    "indus-mature-harappan": "Indus (Mature Harappan)",
    "southern-mesopotamia-ed3-akkad": "S. Mesopotamia, ED III–Akkad",
    "ur-iii-state": "Ur III state",
    "upper-mesopotamia-syria-eb4": "Upper Mesopotamia and Syria",
    "southern-levant-eb3": "Southern Levant, EB III",
    "egypt-old-to-early-middle-kingdom": "Egypt, Old–early Middle Kingdom",
    "kerma-ancien-moyen": "Kerma, Nubia",
    "dilmun-early": "Dilmun",
    "umm-an-nar-magan": "Umm an-Nar (Magan)",
    "elam-susiana": "Elam and Susiana",
    "helmand-shahr-i-sokhta": "Helmand (Shahr-i Sokhta)",
    "halil-rud-jiroft": "Halil Rud (Jiroft)",
    "oxus-bmac": "Oxus (BMAC)",
    "namazga-v-turkmenistan": "Namazga V, Turkmenistan",
    "eba-anatolia": "Early Bronze Anatolia",
    "minoan-crete-prepalatial": "Minoan Crete",
    "bell-beaker-unetice-central-germany": "Bell Beaker–Únětice",
    "el-argar-early": "El Argar, Iberia",
    "longshan-northern-china": "Longshan China",
    "late-liangzhu": "Late Liangzhu",
    "shijiahe": "Shijiahe",
    "norte-chico-caral-supe": "Caral-Supe, Peru",
}

# What each published extent measures, read from its `basis` field.
EXTENT_KIND = {
    "indus-mature-harappan": "spread of sites",
    "southern-mesopotamia-ed3-akkad": "political control",
    "ur-iii-state": "political control",
    "upper-mesopotamia-syria-eb4": "Ebla's core territory",
    "egypt-old-to-early-middle-kingdom": "floodplain",
    "dilmun-early": "land area",
    "elam-susiana": "political control",
    "halil-rud-jiroft": "survey area",
    "minoan-crete-prepalatial": "island area",
    "late-liangzhu": "settled plain",
}

LEDE = ("While the Indus cities flourished, people in Mesopotamia, Egypt, Iran, Central Asia, the Gulf, "
        "Anatolia, Crete, China, Peru and Europe were also building large settlements. This page sets 22 of "
        "these societies side by side for the centuries 2600–1900 BCE: where they were, how large their "
        "biggest settlements and territories were, how many people lived in them, and what their cities had. "
        "Every number is a published estimate with its source; most are ranges, because authors measure "
        "different things.")

READING = [
    "The Indus stands out for its spread. One material culture reached across 650,000–1,000,000 km², "
    "comparable only with the land the kings of Akkad controlled at their height. Its densely settled core "
    "of 30,000–100,000 km² is the figure to set beside Egypt's 17,000–22,400 km² of floodplain, and even "
    "that core is larger.",
    "Its largest cities were big but not the biggest. Mohenjo-daro covered 200–250 ha. Early Dynastic Uruk, "
    "Lagash and Umma each covered 400–600 ha, Shimao in northern China about 400 ha, and Liangzhu's walled "
    "and outer city 630–800 ha, though Liangzhu's walls were built before 2600 BCE. The Indus had several "
    "cities of the same rank, Mohenjo-daro, Harappa, Rakhigarhi, Dholavira and Ganweriwala, spread over the "
    "whole region, as southern Mesopotamia had several large cities close together.",
    "The difference is in what the cities contained. The Indus row is coded with writing, seals, sealings, "
    "standard weights, planned streets and drainage, but no building identified as a palace and no rich "
    "tomb. Every other society coded with writing has at least one of the two, palaces or royal and elite "
    "tombs, at least in part. This fits the seal evidence: short legends that recur across cities as often "
    "as random placement predicts, as titles held by many people would, and sealings that travelled between "
    "cities. One reading, which the "
    "project holds as a conjecture, is that Indus authority sat in offices and institutions spread across "
    "many cities rather than in a royal court. Two observations would test it. Excavating a large "
    "unexcavated city such as Ganweriwala would find a palace or a rich tomb if one existed. And a deposit "
    "of sealings from one storeroom should carry titles that also appear on seals in other cities.",
]

METHOD = ("Sources were read on 20 October 2026; NOTES.md in this package describes how areas and populations "
          "were estimated and where the sources disagree. Population figures are estimates, mostly area "
          "multiplied by an assumed number of people per hectare. Extents measure different things: the spread "
          "of sites, political control, or settled land. 48 of the 64 map positions come from Wikipedia or "
          "Wikidata, and three are approximate.")


def main():
    civs = json.loads(SRC.read_text(encoding="utf-8"))
    for c in civs:
        c["short"] = SHORT.get(c["id"], c["name"])
    extents = []
    for c in civs:
        e = c.get("extent_km2") or {}
        lo, hi = e.get("low"), e.get("high")
        if lo is None and hi is None:
            continue
        lo, hi = lo if lo is not None else hi, hi if hi is not None else lo
        extents.append({"id": c["id"], "name": c["name"], "short": c["short"], "low": lo, "high": hi,
                        "kind": EXTENT_KIND.get(c["id"], "extent"), "basis": e.get("basis")})
        if c["id"] == "indus-mature-harappan":
            assert "30,000–100,000" in e.get("basis", ""), "Fisher's core figure is no longer in the Indus basis"
            extents.append({"id": c["id"] + "-core", "name": "Indus, densely settled core (Fisher 2018)",
                            "short": "Indus, settled core", "low": 30000, "high": 100000,
                            "kind": "settled core", "basis": e.get("basis")})
    extents.sort(key=lambda r: -r["high"])
    payload = {"civilisations": civs, "extents": extents, "lede": LEDE, "reading": READING, "method": METHOD}
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(payload, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.name}: {len(civs)} civilisations, {len(extents)} extents")


if __name__ == "__main__":
    main()
