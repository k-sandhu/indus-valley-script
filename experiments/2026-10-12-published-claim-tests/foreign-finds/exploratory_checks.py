"""Post-outcome exploratory checks for Study B (not part of the frozen protocol).

E1  The family/identical-code grouping chains 1,595 South Asian faces (mostly
    Harappa tablets) into one component, so fold 4 holds 2,015 faces. Recompute
    H1 and H2 using only comparators outside that component.
E2  Split the South Asian round-seal group into circular (SEAL:C) and
    cylinder (SEAL:CY) faces.
E3  Locate adjacent 740-740 in South Asian and unprovenanced texts.
E4  Share of transitions that South Asian round seals have in common with the
    West Asian round seals, against length-matched South Asian non-round seals.
E5  Coarser sign alphabet: map each Wells code to its Mayig class where the
    crosswalk lists one (497 of 712 codes, 331 classes), regroup folds on the
    mapped code strings, and recompute H1, H2 and the South Asian round group.
Output: run-2026-10-12/exploratory-checks.json
"""
from __future__ import annotations

import copy
import json
from collections import defaultdict

import numpy as np

import analysis as A
import ffcore as C


def giant_component(pool_faces):
    uf = C.UnionFind()
    byf, byc = {}, {}
    for p in pool_faces:
        rid = p["record_id"]
        uf.find(rid)
        fam, code = p["face"]["object_family_id"], p["face"]["text_code_visual_ltr"]
        if fam in byf:
            uf.union(byf[fam], rid)
        else:
            byf[fam] = rid
        if code in byc:
            uf.union(byc[code], rid)
        else:
            byc[code] = rid
    comp = defaultdict(set)
    for p in pool_faces:
        comp[uf.find(p["record_id"])].add(p["record_id"])
    return max(comp.values(), key=len)


def main():
    faces = C.load_faces()
    V = len(C.vocabulary(faces))
    sa = [f for f in faces if f["group"] == "south_asia"]
    west = [f for f in faces if f["group"] == "west_asia" and f["record_id"] not in C.DUPLICATE_WITNESS]
    out = {"status": "Exploratory, computed after the frozen outcomes in run-2026-10-12/summary.json"}

    # E1
    big = giant_component(sa)
    pool = A.Pool("south_asia", sa, V)
    original = C.choose_cell

    def filtered(test_face, test_text, pool_faces, ladder):
        level, idx, tried = original(test_face, test_text, pool_faces, ladder)
        idx = [i for i in idx if pool_faces[i]["record_id"] not in big]
        return level, idx, tried

    C.choose_cell = filtered
    try:
        rows = A.score_tests(west, pool)
    finally:
        C.choose_cell = original
    e1 = {"giant_component_faces": len(big),
          "fold_of_giant_component": sorted({f for p, f in zip(sa, pool.folds) if p["record_id"] in big}),
          "min_comparators_after_filter": min(r["n_comp"] for r in rows if r.get("scorable")),
          "H1": A.clean(A.group_stat(rows, "surprisal", 500)),
          "H2": A.clean(A.group_stat([r for r in rows if r["medium"] == "round"], "surprisal", 501))}
    out["E1_comparators_outside_giant_component"] = e1

    # E2 (reads the local peripheral rows written by analysis.py)
    rows = [json.loads(l) for l in (A.RAW_OUT / "peripheral_rows.jsonl").open(encoding="utf-8")]
    rnd = [r for r in rows if r["peripheral_group"] == "south_asian_round" and r.get("scorable")]
    e2 = {}
    for t in ("SEAL:C", "SEAL:CY"):
        sub = [r for r in rnd if r["object_type"] == t]
        e2[t] = {"n": len(sub), "U": float(np.mean([r["u_surprisal"] for r in sub])),
                 "delta_bits": float(np.mean([r["delta_surprisal"] for r in sub])),
                 "sites": sorted({r["site"] for r in sub}),
                 "per_face_u": {r["record_id"]: round(r["u_surprisal"], 4) for r in sub}}
    out["E2_south_asian_round_by_type"] = e2

    # E3
    def adj(f):
        return any(a == "740" and b == "740" for run, _, _ in C.spans(f["text"]) for a, b in zip(run, run[1:]))
    out["E3_adjacent_740_740"] = [
        {"record_id": f["record_id"], "group": f["group"], "site": f["face"]["site"],
         "object_type": f["face"]["object_type"], "complete_flag": f["face"]["metadata"]["complete"],
         "structure": C.structure_string(f["text"]), "cisi": f["face"]["source_cisi"]}
        for f in faces if adj(f)]

    # E4: transitions shared with the West Asian round seals. For each complete
    # South Asian seal text, the share of its events (start, internal, end) that
    # occur among the events of the West Asian round-seal texts; South Asian
    # non-round seals are reweighted to the round seals' length distribution.
    west_round = [f for f in west if f["medium"] == "round"]
    wr_events = {(h[-1], w) for f in west_round for h, w in C.events(f["text"], 2)}

    def share(f):
        ev = list(C.events(f["text"], 2))
        return sum((h[-1], w) in wr_events for h, w in ev) / len(ev)

    seen, sa_full = set(), []
    for f in sa:
        c = f["face"]["text_code_visual_ltr"]
        if f["full"] and f["medium"] in C.SEAL_MEDIA and c not in seen:
            seen.add(c)
            sa_full.append(f)
    rnd_full = [f for f in sa_full if f["medium"] == "round"]
    other = [f for f in sa_full if f["medium"] != "round"]
    by_len = defaultdict(list)
    for f in other:
        by_len[f["text"]["length"]].append(share(f))
    rs = [share(f) for f in rnd_full]
    ref = [float(np.mean(by_len[f["text"]["length"]])) for f in rnd_full if by_len[f["text"]["length"]]]
    out["E4_shared_transitions_with_west_round"] = {
        "west_round_texts": len(west_round), "west_round_distinct_events": len(wr_events),
        "south_asian_round_complete_unique": len(rnd_full),
        "mean_share_south_asian_round": float(np.mean(rs)),
        "mean_share_length_matched_south_asian_nonround_seals": float(np.mean(ref)),
        "south_asian_nonround_complete_unique": len(other),
        "note": "Descriptive only; West Asian round texts number 18 faces and no interval is given."}

    # E5: coarse alphabet through the Mayig crosswalk.
    cw = json.loads((C.ROOT / "data" / "normalized" / "mayig_wells_class_crosswalk.json")
                    .read_text(encoding="utf-8"))["by_wells_id"]
    cmap = {w: "M" + v[0] for w, v in cw.items() if v}

    def coarse(f):
        g = dict(f)
        t = copy.deepcopy(f["text"])
        t["lines"] = [[cmap.get(x, x) for x in line] for line in t["lines"]]
        face = dict(f["face"])
        code = f["face"]["text_code_visual_ltr"]
        edge_l = code[0] if code[0] in "+]" else ""
        edge_r = code[-1] if code[-1] in "+[" else ""
        vis = [list(reversed(line)) for line in reversed(t["lines"])]
        face["text_code_visual_ltr"] = edge_l + "/".join("-".join(l) for l in vis) + edge_r
        g["face"], g["text"] = face, t
        return g

    cfaces = [coarse(f) for f in faces]
    cV = len({x for f in cfaces for x in C.known_signs(f["text"])}) + 1
    csa = [f for f in cfaces if f["group"] == "south_asia"]
    cwest = [f for f in cfaces if f["group"] == "west_asia" and f["record_id"] not in C.DUPLICATE_WITNESS]
    cpool = A.Pool("coarse", csa, cV)
    rows = A.score_tests(cwest, cpool)
    rnd = [f for f in csa if f["medium"] == "round"]
    rid = {f["record_id"] for f in rnd}
    rpool = A.Pool("coarse_round", [f for f in csa if f["record_id"] not in rid], cV)
    rrows = A.score_tests(C.dedupe_test_faces(rnd), rpool)
    out["E5_coarse_alphabet"] = {
        "mapped_wells_codes": len(cmap), "vocabulary_size_including_end": cV,
        "H1": A.clean(A.group_stat(rows, "surprisal", 510)),
        "H2": A.clean(A.group_stat([r for r in rows if r["medium"] == "round"], "surprisal", 511)),
        "H1_unseen": A.clean(A.group_stat(rows, "unseen", 512, null=False)),
        "south_asian_round": A.clean(A.group_stat(rrows, "surprisal", 513, null=False)),
        "south_asian_circular_only_U": float(np.mean([r["u_surprisal"] for r in rrows
                                                      if r.get("scorable") and r["object_type"] == "SEAL:C"])),
        "per_object_u": {r["record_id"]: round(r["u_surprisal"], 4) for r in rows if r.get("scorable")}}

    path = A.OUT / "exploratory-checks.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
