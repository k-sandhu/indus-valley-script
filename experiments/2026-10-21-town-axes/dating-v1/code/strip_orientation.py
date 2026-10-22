"""Remove the few orientation statements that the regional agents carried into the town files.

The brief reserves the direction of walls and streets for the measuring agents, so
the dating files must not state it. Each replacement below keeps the dating content
(what was built, when, the page) and drops only the direction. Quotations are cut
with an ellipsis or turned into paraphrase so that no source wording is altered
silently. Run once: python -P code/strip_orientation.py
"""
import json
import pathlib

TOWNS = pathlib.Path(__file__).resolve().parent.parent / "towns"
EDITS = {
    "chanhu-daro": [
        ("'a wide thoroughfare whose direction was north-west to south-east'", "'a wide thoroughfare ...' (direction omitted)"),
        ("with a wide north-west to south-east street, a cross street", "with a wide thoroughfare, a cross street"),
        ("measuring 5 to 7 meters wide (from north to south)'", "measuring 5 to 7 meters wide ...' (direction omitted)"),
    ],
    "shikarpur": [("runs south to join the outer wall", "runs to join the outer wall")],
    "dholavira": [
        ("measures 283 to 285 m east-west and 45 to 47.50 m across", "measures 283 to 285 m by 45 to 47.50 m"),
        ("laid out on an east-west arterial street with staggered north-south streets", "laid out on an arterial street with staggered cross streets"),
        ("runs for a length of 781 m along the east-west axis on the north and 630.50 m along the north south on the west' (p. 112)",
         "runs for a length of 781 m ... on the north and 630.50 m ... on the west' (p. 112; direction words omitted)"),
    ],
    "kuntasi": [("roughly squarish (93 m N-S by 83 m E-W)", "roughly squarish (93 m by 83 m)")],
    "surkotada": [("giving an east-west width of 46 m", "giving a width of 46 m")],
}


def walk(x, old, new, hits):
    if isinstance(x, str):
        if old in x:
            hits.append(1)
            return x.replace(old, new)
        return x
    if isinstance(x, list):
        return [walk(v, old, new, hits) for v in x]
    if isinstance(x, dict):
        return {k: walk(v, old, new, hits) for k, v in x.items()}
    return x


def main():
    for town, edits in EDITS.items():
        f = TOWNS / f"{town}.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        for old, new in edits:
            hits = []
            d = walk(d, old, new, hits)
            print(town, len(hits), "replacement(s):", old[:60])
        f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
