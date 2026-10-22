"""Part 3a: do round-seal texts form a shared sequence tradition?

Implements PROTOCOL.md (frozen 12 October 2026) and AMENDMENT-2026-10-12-before-computation.md.
Usage:
    python analysis.py            # writes run-2026-10-12/tradition-summary.json and objects.csv
The matched-set selections for T1 are written locally so that verify.py can recompute them.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import Counter
from multiprocessing import Pool

import numpy as np

import paths

C = paths.import_ffcore()

RUN = paths.HERE / "run-2026-10-12"
RAW_RUN = paths.RAW / "run-2026-10-12"
D_MATCHED = 50
N_NULL = 1000
N_BOOT = 10000
SEED_MATCH, SEED_NULL, SEED_BOOT = 20261014, 20261015, 20261016
SEED_SUBSET, SEED_CONTROL_NULL = 20261018, 20261019
N_CONTROL_SUBSETS, N_CONTROL_NULL, CONTROL_SIZE = 100, 500, 29
BOS, EOS = C.BOS, C.EOS

T1_WA = ["147.1", "148.1", "2153.1", "3863.1", "3881.1", "3897.1", "3898.1", "3899.1", "5222.1", "5225.1",
         "5227.1", "5228.1", "5229.1", "5231.1", "5232.1", "5551.1"]
T1_SA = ["114.1", "122.1", "2419.1", "2419.2", "2911.1", "2912.1", "2913.1", "2977.1", "3668.1", "4247.1"]
T1_UN = ["3887.1", "3889.1", "5223.1", "5224.1"]
S4_ADD = ["3882.1", "1387.1", "1388.1", "1388.2", "1924.1", "3669.1", "5468.1", "3888.1", "5557.1"]
MIRRORED = ["148.1", "3863.1"]


# ============================================================ texts
def reverse_code(code: str) -> str:
    """Mirror an ICIT code string: reverse sign order and swap the edge marks."""
    left, right = code[0], code[-1]
    body = code[1:-1]
    lines = [line.split("-") for line in body.split("/")]
    new_body = "/".join("-".join(reversed(line)) for line in reversed(lines))
    new_left = {"+": "+", "[": "]"}[right]
    new_right = {"+": "+", "]": "["}[left]
    return new_left + new_body + new_right


def face_with_code(face: dict, code: str) -> dict:
    """A copy of a Lipi face carrying a checked code; '+' edges of the checked code are trusted."""
    f = json.loads(json.dumps(face))
    body = code[1:] if code[0] in "+]" else code
    body = body[:-1] if body and body[-1] in "+[" else body
    f["text_code_visual_ltr"] = code
    f["signs_visual_ltr"] = [t.zfill(3) for line in body.split("/") for t in line.split("-") if t]
    f["metadata"] = dict(f["metadata"], complete="Y")
    return f


def unit(rid: str, face: dict) -> dict:
    t = C.parse_code(face)
    ev = list(C.events(t, 2))
    events = [(h[-1], w) for h, w in ev]
    return {"rid": rid, "family": face["object_family_id"], "code": face["text_code_visual_ltr"],
            "text": t, "events": events,
            "ss": [(u, w) for u, w in events if u != BOS and w != EOS]}


# ============================================================ models
class KN:
    """Interpolated Kneser-Ney bigram with Study B's formulas, plus a unigram companion."""

    def __init__(self, c2: Counter, V: int):
        self.c2, self.V = c2, V
        cu, nu, cont, uni, cc = Counter(), Counter(), Counter(), Counter(), Counter()
        for (u, w), c in c2.items():
            cu[u] += c
            nu[u] += 1
            cont[w] += 1
            uni[w] += c
            cc[c] += 1
        self.cu, self.nu, self.cont, self.uni = cu, nu, cont, uni
        self.D2 = cc[1] / (cc[1] + 2 * cc[2]) if cc[1] + 2 * cc[2] > 0 else 0.5
        ccc = Counter(cont.values())
        self.D1 = ccc[1] / (ccc[1] + 2 * ccc[2]) if ccc[1] + 2 * ccc[2] > 0 else 0.5
        self.cont_total, self.cont_types = len(c2), len(cont)
        ucc = Counter(uni.values())
        self.Du = ucc[1] / (ucc[1] + 2 * ucc[2]) if ucc[1] + 2 * ucc[2] > 0 else 0.5
        self.uni_total, self.uni_types = sum(uni.values()), len(uni)

    def p_cont(self, w):
        return (max(self.cont.get(w, 0) - self.D1, 0.0) / self.cont_total
                + self.D1 * self.cont_types / self.cont_total / self.V)

    def p(self, u, w):
        cu = self.cu.get(u, 0)
        if cu == 0:
            return self.p_cont(w)
        return (max(self.c2.get((u, w), 0) - self.D2, 0.0) / cu
                + self.D2 * self.nu[u] / cu * self.p_cont(w))

    def p_uni(self, w):
        return (max(self.uni.get(w, 0) - self.Du, 0.0) / self.uni_total
                + self.Du * self.uni_types / self.uni_total / self.V)

    def score(self, u_: dict):
        ev = u_["events"]
        s = sum(-math.log2(self.p(u, w)) for u, w in ev) / len(ev)
        su = sum(-math.log2(self.p_uni(w)) for _, w in ev) / len(ev)
        att = (sum(1 for x in u_["ss"] if self.c2.get(x, 0) > 0) / len(u_["ss"])) if u_["ss"] else None
        return s, su, att


def fit(units, V):
    c2 = Counter()
    for x in units:
        c2.update(x["events"])
    return KN(c2, V)


# ============================================================ data
_DATA = None


def data():
    global _DATA
    if _DATA is not None:
        return _DATA
    faces = C.load_faces()
    by_id = {f["record_id"]: f for f in faces}
    V = len(C.vocabulary(faces))
    # protocol population check
    rule = sorted((f["record_id"] for f in faces
                   if C.normalized_type(f["face"]) == "SEAL:C" and f["group"] in ("west_asia", "south_asia",
                                                                                   "unprovenanced")
                   and f["text"]["single_line"] and f["record_id"] not in C.DUPLICATE_WITNESS),
                  key=C.natural_key)
    assert rule == sorted(T1_WA + T1_SA + T1_UN, key=C.natural_key), rule
    pool, seen = [], set()
    for f in faces:
        if f["group"] == "south_asia" and f["full"] and f["medium"] in ("square", "seal_other"):
            code = f["face"]["text_code_visual_ltr"]
            if code not in seen:
                seen.add(code)
                pool.append({"rid": f["record_id"], "code": code, "tokens": f["text"]["lines"][0],
                             "region": f["face"]["region"]})
    checks = json.loads((paths.RAW / "checks" / "reader1.json").read_text(encoding="utf-8"))["records"]
    joins = list(csv.DictReader((paths.HERE / "joins.csv").open(encoding="utf-8")))
    _DATA = {"faces": faces, "by_id": by_id, "V": V, "pool": pool, "checks": checks, "joins": joins}
    return _DATA


def lipi_unit(rid):
    return unit(rid, data()["by_id"][rid]["face"])


def checked_unit(rid, mirrored=False):
    d = data()
    face = d["by_id"][rid]["face"]
    chk = d["checks"].get(rid, {}).get("checked_code")
    code = chk or face["text_code_visual_ltr"]
    if mirrored and rid in MIRRORED:
        code = reverse_code(code)
    if code == face["text_code_visual_ltr"]:
        return unit(rid, face)
    return unit(rid, face_with_code(face, code))


def objects_from(rids, maker=lipi_unit):
    """Group faces into objects by family, preserving order."""
    groups = {}
    for rid in rids:
        u = maker(rid)
        groups.setdefault(u["family"], []).append(u)
    return list(groups.values())


def group_of(rid):
    return data()["by_id"][rid]["group"]


# ============================================================ matched sets
_CAND = {}


def structure_key(t):
    mask = tuple(x if x in (C.UNKNOWN, C.BLANK) else "X" for x in t["lines"][0])
    return (mask, t["start_known"], t["end_known"], t["length"])


def candidates(u, excluded=frozenset()):
    """Pool texts that can carry u's length, damage mask and edge flags (cached by structure)."""
    key = structure_key(u["text"])
    if key not in _CAND:
        pool = data()["pool"]
        _CAND[key] = [k for k, p in enumerate(pool) if C.comparator_window(u["text"], p["tokens"]) is not None]
    base = _CAND[key]
    return [k for k in base if k not in excluded] if excluded else base


def window_unit(u, k, tag):
    p = data()["pool"][k]
    t = C.comparator_window(u["text"], p["tokens"])
    events = [(h[-1], w) for h, w in C.events(t, 2)]
    return {"rid": f"{tag}:{p['rid']}", "family": f"{tag}:{p['rid']}", "code": p["code"], "text": t,
            "events": events, "ss": [(a, b) for a, b in events if a != BOS and b != EOS], "pool_index": k}


def draw_matched(train_units, rng, excluded=frozenset(), cache=None):
    """One matched set: a pool window for every training unit (same length, mask and edges)."""
    out = []
    for u in train_units:
        key = structure_key(u["text"])
        if cache is not None and key in cache:
            cand = cache[key]
        else:
            cand = candidates(u, excluded)
            if cache is not None:
                cache[key] = cand
        out.append(window_unit(u, rng.choice(cand), "m"))
    return out


# ============================================================ evaluations
def _object_values(test_obj, model_int, matched_models):
    deltas, udeltas, adeltas, sints, smats = [], [], [], [], []
    for u in test_obj:
        if not u["events"]:
            continue
        s, su, a = model_int.score(u)
        ms = [m.score(u) for m in matched_models]
        sm = float(np.mean([x[0] for x in ms]))
        deltas.append(s - sm)
        udeltas.append(su - float(np.mean([x[1] for x in ms])))
        sints.append(s)
        smats.append(sm)
        if a is not None:
            adeltas.append(a - float(np.mean([x[2] for x in ms])))
    if not deltas:
        return None
    return {"delta": float(np.mean(deltas)), "delta_unigram": float(np.mean(udeltas)),
            "delta_transitions": float(np.mean(adeltas)) if adeltas else None,
            "s_internal": float(np.mean(sints)), "s_matched": float(np.mean(smats)),
            "events": sum(len(u["events"]) for u in test_obj)}


def evaluate_loo(objects, rng, excluded=frozenset(), record=None):
    """Leave-one-object-out: internal model vs matched South Asian models of the same structure."""
    V = data()["V"]
    flat = [u for obj in objects for u in obj]
    cache = {}
    matched_sets = [draw_matched(flat, rng, excluded, cache) for _ in range(D_MATCHED)]
    if record is not None:
        record["matched_pool_rids"] = [[m["rid"].split(":", 1)[1] for m in ms] for ms in matched_sets]
        record["flat_rids"] = [u["rid"] for u in flat]
    results = []
    for i, obj in enumerate(objects):
        codes = {u["code"] for u in obj}
        fam = obj[0]["family"]
        train = [u for u in flat if u["family"] != fam and u["code"] not in codes]
        idx = [j for j, u in enumerate(flat) if u["family"] != fam and u["code"] not in codes]
        m_int = fit(train, V)
        m_mat = []
        for ms in matched_sets:
            m_mat.append(fit([ms[j] for j in idx if ms[j]["code"] not in codes], V))
        results.append(_object_values(obj, m_int, m_mat))
    return results


def evaluate_cross(train_units, test_objects, rng, excluded=frozenset()):
    V = data()["V"]
    cache = {}
    matched_sets = [draw_matched(train_units, rng, excluded, cache) for _ in range(D_MATCHED)]
    results = []
    for obj in test_objects:
        codes = {u["code"] for u in obj}
        m_int = fit([u for u in train_units if u["code"] not in codes], V)
        m_mat = [fit([m for m in ms if m["code"] not in codes], V) for ms in matched_sets]
        results.append(_object_values(obj, m_int, m_mat))
    return results


def aggregate(results):
    vals = [r for r in results if r is not None]
    d = [r["delta"] for r in vals]
    du = [r["delta_unigram"] for r in vals]
    da = [r["delta_transitions"] for r in vals if r["delta_transitions"] is not None]
    return {"n_objects": len(d), "delta": float(np.mean(d)), "delta_unigram": float(np.mean(du)),
            "delta_transitions": float(np.mean(da)) if da else None, "n_objects_transitions": len(da)}


def pseudo_objects(objects, rng):
    """Replace every face with a random pool window of the same structure; keep object grouping."""
    used, out = set(), []
    for obj in objects:
        new = []
        for u in obj:
            k = rng.choice(candidates(u, frozenset(used)))
            used.add(k)
            w = window_unit(u, k, "p")
            w["family"] = "p:" + obj[0]["family"]
            new.append(w)
        out.append(new)
    return out, frozenset(used)


# ============================================================ tests
def build_tests():
    lipi = objects_from(T1_WA + T1_SA + T1_UN)
    s1 = objects_from(T1_WA + T1_SA + T1_UN, lambda r: checked_unit(r))
    s1b = objects_from(T1_WA + T1_SA + T1_UN, lambda r: checked_unit(r, mirrored=True))
    status = data()["checks"]
    s2_rids = [r for r in T1_WA + T1_SA + T1_UN
               if status.get(r, {}).get("status") not in ("pseudo-inscription", "fill")]
    laursen = {row["record_id"] for row in data()["joins"]
               if row["laursen_no"].isdigit() and (1 <= int(row["laursen_no"]) <= 27 or row["laursen_no"] == "56")
               and row["join_status"].startswith("established")}
    s3_rids = [r for r in T1_WA + T1_SA + T1_UN if r in laursen]
    s4_rids = T1_WA + T1_SA + T1_UN + [r for r in S4_ADD if data()["by_id"][r]["text"]["single_line"]]
    return {
        "T1": ("loo", lipi),
        "T2": ("loo", objects_from(T1_WA)),
        "T3a": ("cross", [u for o in objects_from(T1_WA) for u in o], objects_from(T1_SA)),
        "T3b": ("cross", [u for o in objects_from(T1_SA) for u in o], objects_from(T1_WA)),
        "S1": ("loo", s1),
        "S1b": ("loo", s1b),
        "S2": ("loo", objects_from(s2_rids)),
        "S3": ("loo", objects_from(s3_rids)),
        "S4": ("loo", objects_from(s4_rids)),
    }


_TESTS = None


def tests():
    global _TESTS
    if _TESTS is None:
        _TESTS = build_tests()
    return _TESTS


def observed(name, record=None):
    spec = tests()[name]
    rng = random.Random(f"{SEED_MATCH}-{name}")
    if spec[0] == "loo":
        return evaluate_loo(spec[1], rng, record=record)
    return evaluate_cross(spec[1], spec[2], rng)


def null_draw(args):
    name, b = args
    spec = tests()[name]
    rng = random.Random(f"{SEED_NULL}-{name}-{b}")
    if spec[0] == "loo":
        pseudo, used = pseudo_objects(spec[1], rng)
        return aggregate(evaluate_loo(pseudo, rng, excluded=used))
    pseudo, used = pseudo_objects([[u] for u in spec[1]], rng)
    return aggregate(evaluate_cross([o[0] for o in pseudo], spec[2], rng, excluded=used))


def bootstrap(results, key, seed):
    vals = np.array([r[key] for r in results if r is not None and r[key] is not None])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(vals), size=(N_BOOT, len(vals)))
    means = vals[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def summarise(name, results, nulls):
    agg = aggregate(results)
    out = {"observed": agg}
    for key, tail in (("delta", "low"), ("delta_unigram", "low"), ("delta_transitions", "high")):
        nv = np.array([n[key] for n in nulls if n[key] is not None])
        obs = agg[key]
        if obs is None or not len(nv):
            continue
        k = int((nv <= obs).sum()) if tail == "low" else int((nv >= obs).sum())
        out[key] = {"value": obs, "p_one_sided": (1 + k) / (1 + len(nv)), "null_n": int(len(nv)),
                    "null_mean": float(nv.mean()), "null_q05": float(np.percentile(nv, 5)),
                    "null_q95": float(np.percentile(nv, 95)),
                    "bootstrap_95": bootstrap(results, key, SEED_BOOT)}
    return out


# ============================================================ positive controls
def control_population(kind):
    d = data()
    pool_len = Counter(len(p["tokens"]) for p in d["pool"])
    seen, out = set(), []
    for f in d["faces"]:
        if not f["full"]:
            continue
        if kind == "C1":
            ok = f["face"]["site"] == "Mohenjo-daro" and C.normalized_type(f["face"]) == "TAB:C"
        else:
            ok = (f["group"] == "south_asia" and f["face"]["region"] == "Gujarat/Kutch"
                  and f["medium"] in ("square", "seal_other"))
        code = f["face"]["text_code_visual_ltr"]
        if ok and code not in seen and pool_len[f["text"]["length"]] >= 20:
            seen.add(code)
            out.append(f["record_id"])
    return out


def control_excluded(kind):
    if kind == "C2":
        return frozenset(k for k, p in enumerate(data()["pool"]) if p["region"] == "Gujarat/Kutch")
    return frozenset()


def control_subset(kind, s):
    rids = control_population(kind)
    rng = random.Random(f"{SEED_SUBSET}-{kind}-{s}")
    return [[lipi_unit(r)] for r in rng.sample(rids, CONTROL_SIZE)]


def control_draw(args):
    kind, s = args
    objs = control_subset(kind, s)
    rng = random.Random(f"{SEED_MATCH}-{kind}-{s}")
    return aggregate(evaluate_loo(objs, rng, excluded=control_excluded(kind)))


def control_null_draw(args):
    kind, b = args
    objs = control_subset(kind, 0)
    rng = random.Random(f"{SEED_CONTROL_NULL}-{kind}-{b}")
    pseudo, used = pseudo_objects(objs, rng)
    return aggregate(evaluate_loo(pseudo, rng, excluded=used | control_excluded(kind)))


# ============================================================ main
def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def object_rows(name, results):
    spec = tests()[name]
    objs = spec[1] if spec[0] == "loo" else spec[2]
    joins = {row["record_id"]: row for row in data()["joins"]}
    rows = []
    for obj, r in zip(objs, results):
        rid = obj[0]["rid"]
        rows.append({"test": name, "record_ids": ";".join(u["rid"] for u in obj), "group": group_of(rid),
                     "site": data()["by_id"][rid]["face"]["site"],
                     "laursen_no": joins.get(rid, {}).get("laursen_no", ""),
                     "events": r["events"] if r else 0,
                     "delta_bigram": f"{r['delta']:.6f}" if r else "",
                     "delta_unigram": f"{r['delta_unigram']:.6f}" if r else "",
                     "delta_transitions": (f"{r['delta_transitions']:.6f}"
                                           if r and r["delta_transitions"] is not None else ""),
                     "s_internal": f"{r['s_internal']:.6f}" if r else "",
                     "s_matched": f"{r['s_matched']:.6f}" if r else ""})
    return rows


def main(workers=8):
    RUN.mkdir(exist_ok=True)
    RAW_RUN.mkdir(parents=True, exist_ok=True)
    names = list(tests())
    summary = {"design": {"matched_sets": D_MATCHED, "null_draws": N_NULL, "bootstrap_draws": N_BOOT,
                          "seeds": {"matched": SEED_MATCH, "null": SEED_NULL, "bootstrap": SEED_BOOT,
                                    "control_subsets": SEED_SUBSET, "control_null": SEED_CONTROL_NULL},
                          "vocabulary": data()["V"], "pool_texts": len(data()["pool"])},
               "tests": {}}
    rows = []
    record = {}
    with Pool(workers) as pool:
        for name in names:
            res = observed(name, record=record if name == "T1" else None)
            nulls = pool.map(null_draw, [(name, b) for b in range(N_NULL)], chunksize=10)
            summary["tests"][name] = summarise(name, res, nulls)
            rows += object_rows(name, res)
            print(name, json.dumps(summary["tests"][name]["observed"]), flush=True)
        controls = {}
        for kind in ("C1", "C2"):
            subs = pool.map(control_draw, [(kind, s) for s in range(N_CONTROL_SUBSETS)], chunksize=5)
            nulls = pool.map(control_null_draw, [(kind, b) for b in range(N_CONTROL_NULL)], chunksize=10)
            dv = np.array([x["delta"] for x in subs])
            nv = np.array([x["delta"] for x in nulls])
            q05 = float(np.percentile(nv, 5))
            controls[kind] = {"population_texts": len(control_population(kind)), "subset_size": CONTROL_SIZE,
                              "subsets": N_CONTROL_SUBSETS, "median_delta": float(np.median(dv)),
                              "delta_q10_q90": [float(np.percentile(dv, 10)), float(np.percentile(dv, 90))],
                              "median_delta_transitions": float(np.median([x["delta_transitions"] for x in subs])),
                              "median_delta_unigram": float(np.median([x["delta_unigram"] for x in subs])),
                              "null_draws": N_CONTROL_NULL, "null_q05": q05, "null_mean": float(nv.mean()),
                              "share_below_null_q05": float((dv < q05).mean())}
            print(kind, json.dumps(controls[kind]), flush=True)
        summary["positive_controls"] = controls
    sec = {k: summary["tests"][k]["delta"]["p_one_sided"] for k in ("T2", "T3a", "T3b")}
    summary["holm_secondary"] = holm(sec)
    t1 = summary["tests"]["T1"]
    summary["decisions"] = {
        "T1_shared_tradition": bool(t1["delta"]["p_one_sided"] < 0.05 and t1["delta"]["bootstrap_95"][1] < 0),
        "T1_sequence_component": bool(t1.get("delta_transitions", {}).get("p_one_sided", 1) < 0.05),
        "T3a_link": bool(summary["holm_secondary"]["T3a"] < 0.05
                         and summary["tests"]["T3a"]["delta"]["bootstrap_95"][1] < 0),
        "T3b_link": bool(summary["holm_secondary"]["T3b"] < 0.05
                         and summary["tests"]["T3b"]["delta"]["bootstrap_95"][1] < 0),
        "T2_west_asian_tradition": bool(summary["holm_secondary"]["T2"] < 0.05
                                        and summary["tests"]["T2"]["delta"]["bootstrap_95"][1] < 0),
    }
    for k in ("S1", "S1b", "S2", "S3", "S4"):
        s = summary["tests"][k]
        summary["decisions"][f"{k}_shared_tradition"] = bool(s["delta"]["p_one_sided"] < 0.05
                                                             and s["delta"]["bootstrap_95"][1] < 0)
    (RUN / "tradition-summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    with (RUN / "objects.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (RAW_RUN / "t1-matched-sets.json").write_text(json.dumps(record) + "\n", encoding="utf-8")
    print(json.dumps(summary["decisions"], indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
