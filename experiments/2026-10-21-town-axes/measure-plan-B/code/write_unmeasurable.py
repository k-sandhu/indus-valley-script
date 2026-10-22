"""Write town JSON files for towns with no measurable plan (plan-B).

Usage: python .../code/write_unmeasurable.py SLUG [SLUG ...]
Reads code/specs/<slug>.json, which lists the sources examined and the reason, and writes
towns/<slug>.json with empty structures and systems and measurable = false.
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROLE = os.path.dirname(HERE)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


for slug in sys.argv[1:]:
    spec = json.load(open(os.path.join(HERE, "specs", slug + ".json"), encoding="utf-8"))
    srcs = []
    for s in spec["sources"]:
        o = dict(s)
        o.setdefault("kind", "plan")
        if o.get("file") and os.path.exists(o["file"]) and not o.get("sha256"):
            o["sha256"] = sha(o["file"])
        srcs.append(o)
    town = {"town": slug, "role": "plan-B",
            "measured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location": spec["location"], "sources": srcs, "structures": [], "systems": [],
            "main_system": None, "main_system_reason": spec.get("main_system_reason"),
            "published_values": spec.get("published_values", []), "measurable": False, "notes": spec["notes"]}
    with open(os.path.join(ROLE, "towns", slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(town, f, indent=1, ensure_ascii=False)
    print("wrote", slug, "(not measurable)")
