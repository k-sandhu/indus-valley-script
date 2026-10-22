"""Print a compact review summary of one or more dating-v1 town files.

Usage: python -P code/summarise_towns.py <town-slug> [<town-slug> ...]
Used by the coordinating pass to read each agent's file before integration.
"""
import json
import pathlib
import sys

T = pathlib.Path(__file__).resolve().parent.parent / "towns"


def s(x, n=300):
    return (str(x) if x is not None else "None")[:n]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for slug in sys.argv[1:]:
        d = json.loads((T / f"{slug}.json").read_text(encoding="utf-8"))
        print("=" * 30, slug)
        for p in d["parts"]:
            print("##", p["part"])
            print(" phase:", s(p["layout_phase"]))
            print(" built:", s(p["what_was_built"], 600))
            print(" locator:", s(p["locator"], 200))
            print(" range:", p["excavator_range_bce"], "|", s(p["excavator_basis"], 500))
            for r in p["radiocarbon"] or []:
                print("  RC", s(r.get("lab_no"), 40), "|", s(r.get("material"), 20), "|", s(r.get("phase"), 50), "|",
                      r.get("age_bp_printed"), r.get("sigma_printed"), r.get("half_life_printed"), "->",
                      r.get("age_bp_5568"), r.get("sigma_5568"), "|", s(r.get("calibrated_published"), 60), "|",
                      r.get("source"), s(r.get("page"), 30), "| via", r.get("cited_via"))
            print(" bayes:", s(json.dumps(p["bayesian_start"], ensure_ascii=False), 600))
            for y in p["syntheses"] or []:
                print("  SYN", y.get("source"), y.get("page"), y.get("range_bce"), "|", s(y.get("statement"), 250),
                      "| DIS:", s(y.get("disagreement"), 200))
            print(" conflicts:", s(p["conflicts"], 700))
        print("FIRST", s(json.dumps(d["first_occupation"], ensure_ascii=False), 700))
        for x in d["sources"]:
            print("SRC", x["id"], "|", s(x.get("citation"), 170), "|", s(x.get("url_or_path"), 110), "|", s(x.get("sha256"), 10))
        print("NOTES", s(d["notes"], 3000))


if __name__ == "__main__":
    main()
