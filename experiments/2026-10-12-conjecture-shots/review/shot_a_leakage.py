"""Exploratory review analysis: could the confirmation half have reached Shot A's choice of
the four closing signs?

Checks, for the 11 confirmation seals of P4 and for the confirmation size population:
- exact legends shared with any discovery face (any object type, complete or not, with or
  without unknown signs), which the component rule does not join in every case;
- CISI identifiers that differ only by a suffix or case across halves;
- discovery seals at the same site with the same face dimensions and the same last two
  signs (possible duplicate catalogue entries of one object);
- discovery faces of any object type that end in the same last two signs as a
  confirmation high-set seal, by object type.

Outputs: review/shot-a-leakage.json (counts and CISI identifiers) and
data/raw/.../review/shot-a-leakage-matches.json (matching legends; local).
"""
import collections
import json
import re

from review_common import load_all, write_json, write_raw, STATUS
from shot_a_robustness import build, frozen_population, HIGH


def base_cisi(c):
    m = re.match(r"^([A-Za-z]+)-?(\d+)", (c or "").strip())
    return f"{m.group(1).upper()}-{int(m.group(2))}" if m else None


def main():
    rows = load_all()
    tab = build(rows)
    conf = frozen_population([t for t in tab if t["half"] == "confirmation"])
    disc_rows = [r for r in rows if r["half"] == "discovery"]
    disc_text = collections.defaultdict(list)
    disc_end2 = collections.defaultdict(list)
    for r in disc_rows:
        s = r["signs_reading_rtl"]
        disc_text["-".join(s)].append(r)
        if len(s) >= 2:
            disc_end2[tuple(s[-2:])].append(r)

    out = {"status": STATUS}
    # exact legends of the confirmation population found among discovery faces
    shared = [t for t in conf if "-".join(t["signs"]) in disc_text]
    out["confirmation_population_legends_found_in_discovery"] = {
        "seals": len(shared), "of": len(conf),
        "by_discovery_object_type": dict(collections.Counter(
            r["object_type"].split(":")[0] for t in shared for r in disc_text["-".join(t["signs"])]))}
    hi = [t for t in conf if t["last"] in HIGH]
    raw = []
    hi_rows = []
    for t in hi:
        exact = disc_text.get("-".join(t["signs"]), [])
        end2 = disc_end2.get(tuple(t["signs"][-2:]), [])
        same_dims = []
        for r in disc_rows:
            if not r["object_type"].startswith("SEAL") or r["site"] != t["site"]:
                continue
            try:
                h, v = float(r["metadata"].get("horizontal(mm)")), float(r["metadata"].get("vertical(mm)"))
            except (TypeError, ValueError):
                continue
            s = r["signs_reading_rtl"]
            if abs(h - t["h"]) < 0.05 and abs(v - t["v"]) < 0.05 and len(s) >= 1 and s[-1] == t["last"]:
                same_dims.append(r)
        hi_rows.append({"cisi": t["cisi"], "last": t["last"],
                        "exact_legend_in_discovery": len(exact),
                        "discovery_faces_ending_same_two_signs": dict(collections.Counter(r["object_type"].split(":")[0] for r in end2)),
                        "discovery_seals_same_site_same_dims_same_last_sign": [r.get("source_cisi") for r in same_dims]})
        raw.append({"cisi": t["cisi"], "legend": t["signs"],
                    "exact_matches": [(r.get("source_cisi"), r["object_type"], r["signs_reading_rtl"]) for r in exact],
                    "same_two_sign_ending": [(r.get("source_cisi"), r["object_type"], r["signs_reading_rtl"]) for r in end2],
                    "same_dims_same_last": [(r.get("source_cisi"), r["object_type"], r["signs_reading_rtl"]) for r in same_dims]})
    out["confirmation_high_set_seals"] = hi_rows

    # CISI identifiers shared across halves after normalising suffix and case
    halves_of = collections.defaultdict(set)
    for r in rows:
        b = base_cisi(r.get("source_cisi"))
        if b:
            halves_of[b].add(r["half"])
    both = sorted(b for b, h in halves_of.items() if len(h) == 2)
    hi_base = {base_cisi(t["cisi"]) for t in tab if t["text_ok"] and t["signs"] and t["last"] in HIGH and t["type"] in ("SEAL:S", "SEAL:R")}
    out["cisi_base_numbers_in_both_halves"] = {"count": len(both), "examples": both[:20],
                                               "involving_high_set_seals": sorted(set(both) & hi_base)}
    write_json("shot-a-leakage.json", out)
    write_raw("shot-a-leakage-matches.json", {"status": STATUS, "seals": raw})
    print(json.dumps(out, indent=1)[:4000])


if __name__ == "__main__":
    main()
