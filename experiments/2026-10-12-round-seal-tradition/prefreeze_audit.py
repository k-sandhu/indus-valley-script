"""Structure-only audit before the round-seal protocol is frozen.

Reads record metadata, damage structures with sign identities masked, matched-pool
sizes and South Asian positional counts. It prints no sign of any round-seal or
West Asian text. Output: prefreeze-audit.json (tracked; contains no sequences).
"""
from __future__ import annotations

import json
from collections import Counter

import paths

C = paths.import_ffcore()
HUMAN_FIGURE_CODES = {"090", "091", "093", "094", "095", "097", "104", "118", "137"}


def n_events(text):
    return sum(1 for _ in C.events(text, 2))


def unique_full(faces, sel):
    seen, out = set(), []
    for f in faces:
        if sel(f) and f["full"]:
            code = f["face"]["text_code_visual_ltr"]
            if code not in seen:
                seen.add(code)
                out.append(f)
    return out


def main():
    faces = C.load_faces()
    round_faces = [f for f in faces if C.normalized_type(f["face"]) in ("SEAL:C", "SEAL:CY")]
    rows = []
    for f in sorted(round_faces, key=lambda x: C.natural_key(x["record_id"])):
        t, m = f["text"], f["face"]["metadata"]
        rows.append({
            "record_id": f["record_id"], "family": f["face"]["object_family_id"],
            "group": f["group"], "site": f["face"]["site"], "type": C.normalized_type(f["face"]),
            "cisi_field": m.get("cisi"), "excavation_idno": m.get("excavation-idno"),
            "area_section": m.get("area-section"), "symbol": f["face"]["symbol"],
            "length": t["length"], "structure": C.structure_string(t),
            "single_line": t["single_line"], "events": n_events(t),
        })

    pool = unique_full(faces, lambda f: f["group"] == "south_asia" and f["medium"] in ("square", "seal_other"))
    tabc = unique_full(faces, lambda f: f["face"]["site"] == "Mohenjo-daro"
                       and C.normalized_type(f["face"]) == "TAB:C")
    guj = unique_full(faces, lambda f: f["group"] == "south_asia" and f["face"]["region"] == "Gujarat/Kutch"
                      and f["medium"] in ("square", "seal_other"))
    sa_unique = unique_full(faces, lambda f: f["group"] == "south_asia")
    initial_human = Counter(f["text"]["lines"][0][0] for f in sa_unique
                            if f["text"]["lines"][0][0] in HUMAN_FIGURE_CODES)
    initial_091_ids = sorted((f["record_id"] for f in sa_unique if f["text"]["lines"][0][0] == "091"),
                             key=C.natural_key)
    wa_start = sorted((f["record_id"] for f in faces
                       if f["group"] == "west_asia" and f["record_id"] not in C.DUPLICATE_WITNESS
                       and f["text"]["single_line"] and f["text"]["start_known"]
                       and f["text"]["lines"][0][0] not in (C.UNKNOWN, C.BLANK)), key=C.natural_key)

    out = {
        "inputs": {"faces": "data/normalized/lipi_observed_faces.jsonl", "faces_sha256": paths.FROZEN["faces"],
                   "ffcore": paths.STUDY_B_REL.as_posix() + "/ffcore.py",
                   "ffcore_sha256": paths.FROZEN["ffcore.py"]},
        "round_records": rows,
        "counts": {
            "circular_by_group": dict(Counter(r["group"] for r in rows if r["type"] == "SEAL:C")),
            "cylinder_by_group": dict(Counter(r["group"] for r in rows if r["type"] == "SEAL:CY")),
        },
        "matched_pool": {"definition": "South Asian complete single-line non-round seal texts, unique code strings",
                         "n": len(pool),
                         "by_length": dict(sorted(Counter(f["text"]["length"] for f in pool).items()))},
        "positive_control_candidates": {"mohenjodaro_copper_tablets_unique_full": len(tabc),
                                        "gujarat_kutch_seals_unique_full": len(guj)},
        "south_asia_unique_full_texts": len(sa_unique),
        "south_asia_initial_human_figure_codes": dict(sorted(initial_human.items())),
        "south_asia_initial_091_record_ids": initial_091_ids,
        "west_asia_known_start_record_ids": wa_start,
    }
    (paths.HERE / "prefreeze-audit.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for r in rows:
        print(r["record_id"], r["group"], r["site"], r["type"], r["cisi_field"], r["length"],
              r["structure"], r["events"])
    print(json.dumps({k: out[k] for k in ("counts", "matched_pool", "positive_control_candidates",
                                          "south_asia_unique_full_texts",
                                          "south_asia_initial_human_figure_codes",
                                          "south_asia_initial_091_record_ids")}, indent=1))
    print("West Asian known-start texts:", len(wa_start))


if __name__ == "__main__":
    main()
