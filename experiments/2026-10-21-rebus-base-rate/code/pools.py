"""Concept pools for the rebus base-rate study, built from Concepticon 3.4.0 and NoRaRe 1.1.

Picturable nouns: Concepticon concept sets of the ontological category Person/Thing
in concrete semantic fields whose English word has a Brysbaert et al. (2014)
concreteness mean of at least 4.5 and a dominant part of speech of noun.

Meanings suitable for names: six classes (deity, celestial body, colour,
direction, kinship, quality), defined by fixed lists and field rules below.
The two pools are disjoint: a concept that qualifies as a name meaning is
removed from the picturable pool.

Each concept gets English match keys: the gloss with parenthetical notes removed.
Concept sets whose gloss joins alternatives with " OR " are left out, and when two
concepts of one pool share a key, the one without a parenthetical note is kept.

    python -I experiments/2026-10-21-rebus-base-rate/code/pools.py   # writes pools-v1.json
"""

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1"
PKG = ROOT / "experiments" / "2026-10-21-rebus-base-rate"

PICTURE_FIELDS = {
    "Animals", "The body", "Agriculture and vegetation", "The physical world", "Food and drink",
    "Basic actions and technology", "Clothing and grooming", "The house", "Warfare and hunting",
    "Motion", "Possession",
}
CONCRETENESS_MIN = 4.5

DEITY = ["GOD", "DEITY", "SPIRIT", "DEMON", "DEVIL", "GHOST", "SOUL", "MYTHICAL BEING", "ELF", "FAIRY",
         "HEAVEN", "HOLY", "BLESSED"]
CELESTIAL = ["STAR", "SUN", "MOON", "SKY", "PLANET", "MILKY WAY", "POLAR STAR", "URSA MAJOR",
             "ORION'S CONSTELLATION", "ORION'S BELT", "STARLIGHT", "MORNING STAR", "EVENING STAR",
             "PLEIADES", "VENUS", "CONSTELLATION", "COMET", "FULL MOON", "NEW MOON", "SUNLIGHT", "MOONLIGHT"]
DIRECTION = ["NORTH", "SOUTH", "EAST", "WEST", "LEFT", "RIGHT", "UP", "DOWN", "ABOVE", "BELOW",
             "FRONT", "BACK (DIRECTION)", "MIDDLE", "CENTRE", "HIGH", "LOW"]


def key_of(gloss):
    k = re.sub(r"\([^()]*\)", " ", gloss).lower()
    k = re.sub(r"[^a-z' -]", " ", k)
    return re.sub(r"\s+", " ", k).strip()


def load():
    rows = [r for r in csv.DictReader((SRC / "concepticon" / "concepticon.tsv").open(encoding="utf-8"), delimiter="\t")
            if not r["REPLACEMENT_ID"]]
    conc = {}
    for r in csv.DictReader((SRC / "norare" / "Brysbaert-2014-Concreteness.tsv").open(encoding="utf-8"), delimiter="\t"):
        conc[r["CONCEPTICON_ID"]] = r
    return rows, conc


def colour(r):
    return r["ONTOLOGICAL_CATEGORY"] == "Property" and re.search(r"colou?r", r["DEFINITION"], re.I) \
        and r["GLOSS"] not in ("ROTTEN",)


def build():
    rows, conc = load()
    by_gloss = {r["GLOSS"]: r for r in rows}
    name = {}

    def add(r, cls):
        if " OR " in r["GLOSS"]:
            return
        name.setdefault(r["ID"], {"id": r["ID"], "gloss": r["GLOSS"], "class": cls, "key": key_of(r["GLOSS"]),
                                  "field": r["SEMANTICFIELD"], "category": r["ONTOLOGICAL_CATEGORY"]})

    missing = []
    for cls, glosses in (("deity", DEITY), ("celestial", CELESTIAL), ("direction", DIRECTION)):
        for g in glosses:
            if g in by_gloss:
                add(by_gloss[g], cls)
            else:
                missing.append(g)
    for r in rows:
        if colour(r):
            add(r, "colour")
    for r in rows:
        if r["SEMANTICFIELD"] == "Kinship" and r["ONTOLOGICAL_CATEGORY"] == "Person/Thing":
            add(r, "kinship")
    for r in rows:
        if r["ONTOLOGICAL_CATEGORY"] == "Property" and not colour(r):
            add(r, "quality")

    picture = {}
    for r in rows:
        if r["ID"] in name or " OR " in r["GLOSS"]:
            continue
        if r["ONTOLOGICAL_CATEGORY"] != "Person/Thing" or r["SEMANTICFIELD"] not in PICTURE_FIELDS:
            continue
        c = conc.get(r["ID"])
        if not c or c["ENGLISH_POS"] != "Noun":
            continue
        if float(c["ENGLISH_CONCRETENESS_MEAN"]) < CONCRETENESS_MIN:
            continue
        picture[r["ID"]] = {"id": r["ID"], "gloss": r["GLOSS"], "class": "picture", "key": key_of(c["ENGLISH"]),
                            "field": r["SEMANTICFIELD"], "concreteness": float(c["ENGLISH_CONCRETENESS_MEAN"])}

    def dedupe(pool):
        seen = {}
        for cid, c in sorted(pool.items(), key=lambda kv: ("(" in kv[1]["gloss"], int(kv[0]))):
            if c["key"] and c["key"] not in seen:
                seen[c["key"]] = c
        return sorted(seen.values(), key=lambda c: int(c["id"]))

    return dedupe(picture), dedupe(name), missing


def main():
    picture, name, missing = build()
    out = {
        "schema": "rebus-base-rate pools v1",
        "inputs": {p: hashlib.sha256((SRC / p).read_bytes()).hexdigest()
                   for p in ("concepticon/concepticon.tsv", "norare/Brysbaert-2014-Concreteness.tsv")},
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "rules": {"picture_fields": sorted(PICTURE_FIELDS), "concreteness_min": CONCRETENESS_MIN,
                  "deity": DEITY, "celestial": CELESTIAL, "direction": DIRECTION,
                  "listed_glosses_absent_from_concepticon": missing},
        "counts": {"picture": len(picture), "name": len(name),
                   "name_by_class": {c: sum(1 for x in name if x["class"] == c)
                                     for c in ("deity", "celestial", "colour", "direction", "kinship", "quality")}},
        "picture": picture, "name": name,
    }
    target = PKG / "pools-v1.json"
    local = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1" / "pools-full-v1.json"
    if target.exists() or local.exists():
        print("refusing to overwrite", target, local)
        return 1
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    # The tracked copy omits the NoRaRe concreteness values (CC BY-NC 4.0); Concepticon IDs and
    # glosses are CC BY 4.0 (List, Rzymski, Tjuka and others, Concepticon 3.4.0).
    tracked = dict(out)
    tracked["attribution"] = ("Concept sets from Concepticon 3.4.0 (concepticon.clld.org), CC BY 4.0. Concreteness "
                              "filter from NoRaRe 1.1, Brysbaert et al. (2014) mapping, CC BY-NC 4.0; values kept local.")
    tracked["picture"] = [{k: v for k, v in c.items() if k != "concreteness"} for c in out["picture"]]
    tracked["full_local_copy"] = {"path": str(local.relative_to(ROOT)).replace("\\", "/"),
                                  "sha256": hashlib.sha256(local.read_bytes()).hexdigest()}
    target.write_text(json.dumps(tracked, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["counts"]), out["rules"]["listed_glosses_absent_from_concepticon"])


if __name__ == "__main__":
    sys.exit(main())
