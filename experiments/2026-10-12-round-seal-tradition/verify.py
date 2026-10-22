"""Independent check of the round-seal results.

Does not import analysis.py, twins.py or Study B's ffcore.py. It re-parses the Lipi faces, rebuilds the
T1 matched windows from the saved selections, refits its own Kneser-Ney bigram and recomputes the
observed T1 statistics, the per-object values, the bootstrap intervals, the Holm adjustment and the
Fisher tests. Output: verify-2026-10-12.json.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict

import numpy as np

import paths  # file locations only

FACES = paths.DATA / "data" / "normalized" / "lipi_observed_faces.jsonl"
RUN = paths.HERE / "run-2026-10-12"
SA_REGIONS = {"Lower Indus", "Inter-Riverine", "Gujarat/Kutch", "Eastern Headwaters", "Upper Indus", "South India"}
BALUCH = {"Nindowari-damb", "Sibri", "Ornach area", "Miri Qalat", "Murda Sang"}
TOL = 1e-9


def parse(face):
    code = face["text_code_visual_ltr"]
    first, last = code[0], code[-1]
    body = code[1:] if first in "+]" else code
    body = body[:-1] if body and body[-1] in "+[" else body
    lines = [[t.zfill(3) for t in ln.split("-") if t] for ln in body.split("/")]
    toks = [t for ln in lines for t in ln]
    trust = face["metadata"].get("complete", "").strip().upper() == "Y" or "000" in toks or "[" in code or "]" in code
    return {"lines": [list(reversed(ln)) for ln in reversed(lines)], "single": len(lines) == 1,
            "sk": last == "+" and trust, "ek": first == "+" and trust, "n": len(toks)}


def events(t):
    out = []
    for line in t["lines"]:
        i, n = 0, len(line)
        while i < n:
            if line[i] in ("000", "999"):
                i += 1
                continue
            j = i
            while j < n and line[j] not in ("000", "999"):
                j += 1
            seq = (["<s>"] if (t["single"] and t["sk"] and i == 0) else []) + line[i:j] + \
                  (["</s>"] if (t["single"] and t["ek"] and j == n) else [])
            out += list(zip(seq[:-1], seq[1:]))
            i = j
    return out


def window(t, toks):
    L, M = t["n"], len(toks)
    if t["sk"] and t["ek"]:
        w = toks
    elif t["sk"]:
        w = toks[:L]
    elif t["ek"]:
        w = toks[M - L:]
    else:
        w = toks[(M - L) // 2:(M - L) // 2 + L]
    mask = t["lines"][0]
    return {"lines": [[m if m in ("000", "999") else x for m, x in zip(mask, w)]], "single": True,
            "sk": t["sk"], "ek": t["ek"], "n": L}


def kn(evlists, V):
    c2 = Counter()
    for e in evlists:
        c2.update(e)
    cu, nu, cont, uni = Counter(), Counter(), Counter(), Counter()
    for (u, w), c in c2.items():
        cu[u] += c
        nu[u] += 1
        cont[w] += 1
        uni[w] += c

    def disc(counter):
        cc = Counter(counter)
        return cc[1] / (cc[1] + 2 * cc[2]) if cc[1] + 2 * cc[2] else 0.5
    D2, D1, Du = disc(c2.values()), disc(cont.values()), disc(uni.values())
    T, Tt, Ut, Uty = len(c2), len(cont), sum(uni.values()), len(uni)

    def pc(w):
        return max(cont.get(w, 0) - D1, 0) / T + D1 * Tt / T / V

    def p(u, w):
        if cu.get(u, 0) == 0:
            return pc(w)
        return max(c2.get((u, w), 0) - D2, 0) / cu[u] + D2 * nu[u] / cu[u] * pc(w)

    def pu(w):
        return max(uni.get(w, 0) - Du, 0) / Ut + Du * Uty / Ut / V
    return p, pu, c2


def main():
    faces = [json.loads(l) for l in FACES.open(encoding="utf-8")]
    by = {f["record_id"]: f for f in faces}
    V = len({t for f in faces for ln in parse(f)["lines"] for t in ln if t not in ("000", "999")}) + 1
    pool = {}
    for f in faces:
        sa = f["region"] in SA_REGIONS or (f["region"] == "Iranian Plateau" and f["site"] in BALUCH)
        typ = f["object_type"]
        seal_nonround = typ == "SEAL:S" or (typ.startswith("SEAL") and typ not in ("SEAL:C", "SEAL:CY"))
        t = parse(f)
        full = (t["single"] and f["complete_observed"] and t["sk"] and t["ek"]
                and "000" not in t["lines"][0] and "999" not in t["lines"][0])
        if sa and seal_nonround and full and f["text_code_visual_ltr"] not in {p["code"] for p in pool.values()}:
            pool[f["record_id"]] = {"code": f["text_code_visual_ltr"], "toks": t["lines"][0]}
    rec = json.loads((paths.RAW / "run-2026-10-12" / "t1-matched-sets.json").read_text(encoding="utf-8"))
    flat = rec["flat_rids"]
    units = []
    for rid in flat:
        t = parse(by[rid])
        e = events(t)
        units.append({"rid": rid, "fam": by[rid]["object_family_id"], "code": by[rid]["text_code_visual_ltr"],
                      "t": t, "ev": e, "ss": [x for x in e if x[0] != "<s>" and x[1] != "</s>"]})
    matched = []
    for sel in rec["matched_pool_rids"]:
        ms = []
        for u, prid in zip(units, sel):
            w = window(u["t"], pool[prid]["toks"])
            ms.append({"code": pool[prid]["code"], "ev": events(w)})
        matched.append(ms)
    fams = []
    for u in units:
        if u["fam"] not in fams:
            fams.append(u["fam"])
    per_obj = {}
    for fam in fams:
        test = [u for u in units if u["fam"] == fam]
        codes = {u["code"] for u in test}
        idx = [j for j, u in enumerate(units) if u["fam"] != fam and u["code"] not in codes]
        p_i, pu_i, c_i = kn([units[j]["ev"] for j in idx], V)
        mods = [kn([ms[j]["ev"] for j in idx if ms[j]["code"] not in codes], V) for ms in matched]
        d, du, da = [], [], []
        for u in test:
            if not u["ev"]:
                continue
            s = np.mean([-math.log2(p_i(a, b)) for a, b in u["ev"]])
            su = np.mean([-math.log2(pu_i(b)) for _, b in u["ev"]])
            sm = np.mean([np.mean([-math.log2(m[0](a, b)) for a, b in u["ev"]]) for m in mods])
            sum_ = np.mean([np.mean([-math.log2(m[1](b)) for _, b in u["ev"]]) for m in mods])
            d.append(s - sm)
            du.append(su - sum_)
            if u["ss"]:
                a = np.mean([c_i.get(x, 0) > 0 for x in u["ss"]])
                b = np.mean([np.mean([m[2].get(x, 0) > 0 for x in u["ss"]]) for m in mods])
                da.append(a - b)
        if d:
            per_obj[test[0]["rid"]] = (float(np.mean(d)), float(np.mean(du)), float(np.mean(da)) if da else None)
    summ = json.loads((RUN / "tradition-summary.json").read_text(encoding="utf-8"))
    obs = summ["tests"]["T1"]["observed"]
    checks = []

    def check(name, a, b, tol=TOL):
        ok = (a is None and b is None) or (a is not None and b is not None and abs(a - b) <= tol)
        checks.append({"check": name, "independent": a, "reported": b, "pass": bool(ok)})

    check("T1 objects with events", len(per_obj), obs["n_objects"], 0)
    check("T1 mean delta, bigram", float(np.mean([v[0] for v in per_obj.values()])), obs["delta"])
    check("T1 mean delta, unigram", float(np.mean([v[1] for v in per_obj.values()])), obs["delta_unigram"])
    check("T1 mean delta, transitions", float(np.mean([v[2] for v in per_obj.values() if v[2] is not None])),
          obs["delta_transitions"])
    rows = [r for r in csv.DictReader((paths.HERE / "run-2026-10-12" / "objects.csv").open(encoding="utf-8"))
            if r["test"] == "T1" and r["delta_bigram"]]
    worst = max(abs(float(r["delta_bigram"]) - per_obj[r["record_ids"].split(";")[0]][0]) for r in rows)
    check("T1 per-object delta, largest difference (6-decimal CSV)", worst, 0.0, 1e-6)
    vals = np.array([float(r["delta_bigram"]) for r in rows])
    rng = np.random.default_rng(20261016)
    idx = rng.integers(0, len(vals), size=(10000, len(vals)))
    bm = vals[idx].mean(axis=1)
    lo, hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
    rep = summ["tests"]["T1"]["delta"]["bootstrap_95"]
    check("T1 bootstrap lower (from 6-decimal values)", lo, rep[0], 1e-5)
    check("T1 bootstrap upper (from 6-decimal values)", hi, rep[1], 1e-5)
    ps = {k: summ["tests"][k]["delta"]["p_one_sided"] for k in ("T2", "T3a", "T3b")}
    order = sorted(ps, key=ps.get)
    run, holm = 0.0, {}
    for i, k in enumerate(order):
        run = max(run, min(1.0, (3 - i) * ps[k]))
        holm[k] = run
    for k in holm:
        check(f"Holm {k}", holm[k], summ["holm_secondary"][k])
    tw = RUN / "twins-summary.json"
    if tw.exists():
        ts = json.loads(tw.read_text(encoding="utf-8"))

        def fisher_greater(k, n, ks, ns):
            tot, K = n + ns, k + ks
            denom = math.comb(tot, K)
            return sum(math.comb(n, x) * math.comb(ns, K - x) for x in range(k, min(n, K) + 1)) / denom
        for key in ("primary", "sensitivity_unconfirmed_lipi_readings_included", "sensitivity_without_pseudo_or_fill"):
            (k, n), (ks, ns) = ts[key]["west_asia"], ts[key]["south_asia"]
            check(f"Fisher {key}", fisher_greater(k, n, ks, ns), ts[key]["p_one_sided"], 1e-12)
        check("twins primary count recomputed from rows",
              sum(r["confirmed_091"] for r in ts["west_asia_rows"]), ts["primary"]["west_asia"][0], 0)
    out = {"checks": checks, "passed": sum(c["pass"] for c in checks), "failed": sum(not c["pass"] for c in checks)}
    (paths.HERE / "verify-2026-10-12.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"passed": out["passed"], "failed": out["failed"]}))
    for c in checks:
        if not c["pass"]:
            print("FAIL", c)


if __name__ == "__main__":
    main()
