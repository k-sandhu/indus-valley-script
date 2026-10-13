"""Pre-freeze audit for Study B.

Reads group labels, object types, damage structure (signs masked as X) and
South-Asian-only sign statistics. It computes no statistic that uses the sign
identities of any text found outside South Asia. Output: prefreeze-audit.json.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import ffcore as C


def main():
    faces = C.load_faces()
    sa = [f for f in faces if f["group"] == "south_asia"]
    out = {
        "input": {"path": str(C.FACES.relative_to(C.ROOT)).replace("\\", "/"),
                  "sha256": C.sha256_file(C.FACES), "faces": len(faces)},
        "group_counts": dict(Counter(f["group"] for f in faces)),
        "south_asia_by_region": dict(Counter(
            ("Baluchistan/Makran" if f["face"]["site"] in C.BALUCHISTAN_SITES else f["face"]["region"])
            for f in sa)),
        "peripheral_counts": dict(Counter(f["peripheral"] for f in sa if f["peripheral"])),
        "south_asia_full_comparators": sum(f["full"] for f in sa),
        "south_asia_media_full": dict(Counter(f["medium"] for f in sa if f["full"])),
        "south_asia_round_seals": [
            {"record_id": f["record_id"], "family": f["face"]["object_family_id"],
             "site": f["face"]["site"], "type": f["face"]["object_type"],
             "length": f["text"]["length"], "structure": C.structure_string(f["text"]),
             "full": f["full"]} for f in sa if f["medium"] == "round"],
    }

    # South-Asian-only positional statistics over unique complete codes.
    seen, init_all, term_all, init_seal, term_seal = set(), Counter(), Counter(), Counter(), Counter()
    n_texts = n_seal = 0
    for f in sa:
        if not f["full"]:
            continue
        code = f["face"]["text_code_visual_ltr"]
        if code in seen:
            continue
        seen.add(code)
        toks = f["text"]["lines"][0]
        n_texts += 1
        init_all[toks[0]] += 1
        term_all[toks[-1]] += 1
        if f["medium"] in C.SEAL_MEDIA:
            n_seal += 1
            init_seal[toks[0]] += 1
            term_seal[toks[-1]] += 1
    out["south_asia_positional"] = {
        "unique_complete_texts": n_texts, "unique_complete_seal_texts": n_seal,
        "top_initial": C.counter_top(init_all), "top_terminal": C.counter_top(term_all),
        "top_initial_seals": C.counter_top(init_seal), "top_terminal_seals": C.counter_top(term_seal),
        "initial_091_texts": init_all["091"], "initial_091_seal_texts": init_seal["091"],
    }

    # Foreign and unprovenanced-circular structure and comparator cells.
    pool = sa
    tests = [f for f in faces if f["group"] in ("west_asia", "central_asia")
             or (f["group"] == "unprovenanced" and f["medium"] == "round")]
    rows = []
    for f in sorted(tests, key=lambda x: C.natural_key(x["record_id"])):
        t = f["text"]
        n_ev = sum(1 for _ in C.events(t, 2))
        row = {
            "record_id": f["record_id"], "group": f["group"],
            "subregion": C.west_subregion(f["face"]) if f["group"] == "west_asia" else None,
            "site": f["face"]["site"], "object_type": f["face"]["object_type"],
            "medium": f["medium"], "length": t["length"], "single_line": t["single_line"],
            "structure": C.structure_string(t), "bigram_events": n_ev, "clean": f["clean"],
            "complete_flag": f["face"]["metadata"]["complete"],
            "direction": f["face"]["direction"],
            "duplicate_witness_of": C.DUPLICATE_WITNESS.get(f["record_id"]),
        }
        for ladder in ("primary", "square_only", "any_object"):
            if t["single_line"] and n_ev > 0:
                level, idx, tried = C.choose_cell(f["face"], t, pool, ladder)
                row[f"cell_{ladder}"] = {"level": level, "n": len(idx), "tried": tried}
            else:
                row[f"cell_{ladder}"] = None
        rows.append(row)
    out["test_faces"] = rows

    # Peripheral groups: how many texts are scorable and matched (structure only).
    per = defaultdict(lambda: Counter())
    for label in ["gujarat_kutch", "eastern_headwaters", "kalibangan", "baluchistan_makran",
                  "upper_indus", "chanhudaro_control", "south_asian_round"]:
        if label == "south_asian_round":
            group = [f for f in sa if f["medium"] == "round"]
            pool_g = [f for f in sa if f["medium"] != "round"]
        else:
            group = [f for f in sa if f["peripheral"] == label]
            pool_g = [f for f in sa if f["peripheral"] != label]
        group = C.dedupe_test_faces(group)
        c = per[label]
        c["faces_after_dedupe"] = len(group)
        for f in group:
            t = f["text"]
            n_ev = sum(1 for _ in C.events(t, 2))
            if not t["single_line"] or n_ev == 0:
                c["unscorable"] += 1
                continue
            level, idx, _ = C.choose_cell(f["face"], t, pool_g, "primary")
            c["matched" if level else "no_cell"] += 1
            c[f"level_{level}"] += 1
    out["peripheral_structure"] = {k: dict(v) for k, v in per.items()}

    path = C.HERE / "prefreeze-audit.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("group_counts", "south_asia_by_region",
                                          "peripheral_counts", "south_asia_positional",
                                          "peripheral_structure")}, indent=1))
    for r in rows:
        print(r["record_id"], r["group"], r["subregion"], r["site"], r["object_type"], r["length"],
              r["structure"], r["bigram_events"], r["clean"],
              None if r["cell_primary"] is None else (r["cell_primary"]["level"], r["cell_primary"]["n"]),
              None if r["cell_square_only"] is None else r["cell_square_only"]["n"])
    for r in out["south_asia_round_seals"]:
        print(r)


if __name__ == "__main__":
    main()
