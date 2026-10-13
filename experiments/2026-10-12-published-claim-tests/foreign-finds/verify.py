"""Independent recomputation of Study B headline numbers.

Does not import ffcore.py or analysis.py. It re-parses the faces file, rebuilds
groups, folds, the Kneser-Ney bigram model, comparator cells and the matched
statistic, then compares with run-2026-10-12/summary.json.
Output: verify-2026-10-12.json
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FACES = ROOT / "data" / "normalized" / "lipi_observed_faces.jsonl"
SUMMARY = HERE / "run-2026-10-12" / "summary.json"
BREAK = {"000", "999"}
START, END = "#S", "#E"


def nat(rid):
    return tuple(int(x) if x.isdigit() else x for x in rid.split("."))


def parse(face):
    code = face["text_code_visual_ltr"]
    left = code[0] if code[0] in "+]" else ""
    right = code[-1] if code[-1] in "+[" else ""
    inner = code[len(left):len(code) - len(right)]
    vis_lines = [[t.zfill(3) for t in re.findall(r"\d+", ln)] for ln in inner.split("/")]
    lines = [ln[::-1] for ln in vis_lines[::-1]]
    toks = [t for ln in vis_lines for t in ln]
    trust = face["metadata"]["complete"].strip().upper() == "Y" or "000" in toks or "[" in code or "]" in code
    return {"lines": lines, "sk": right == "+" and trust, "ek": left == "+" and trust, "n": len(toks)}


def pairs(t):
    out = []
    multi = len(t["lines"]) > 1
    for ln in t["lines"]:
        units = ([START] if (t["sk"] and not multi) else []) + ln + ([END] if (t["ek"] and not multi) else [])
        for a, b in zip(units, units[1:]):
            if a not in BREAK and b not in BREAK:
                out.append((a, b))
    return out


def group_of(f):
    r, s = f["region"], f["site"]
    if r in {"Lower Indus", "Inter-Riverine", "Gujarat/Kutch", "Eastern Headwaters", "Upper Indus", "South India"}:
        return "SA"
    if r == "Iranian Plateau":
        return "SA" if s in {"Nindowari-damb", "Sibri", "Ornach area", "Miri Qalat", "Murda Sang"} else "WA"
    if r in {"Persian Gulf", "Mesopotamia"}:
        return "WA"
    return "CA" if r == "Central Asia" else "OTHER"


def kind(t):
    t = {"POsT:T:g": "POT:T:g", "POT:T:S": "POT:T:s"}.get(t, t)
    if t == "SEAL:S":
        return "sq"
    if t in ("SEAL:C", "SEAL:CY"):
        return "rd"
    if t.startswith("SEAL"):
        return "so"
    for p, k in (("POT", "pot"), ("TAG", "tag"), ("TAB", "tab")):
        if t.startswith(p):
            return k
    return "misc"


SEALS = {"sq", "rd", "so"}


def ladder(k):
    if k == "sq":
        return [lambda m: m == "sq", lambda m: m in SEALS, lambda m: True]
    if k in ("rd", "so"):
        return [lambda m: m in SEALS, lambda m: True]
    if k in ("pot", "tag", "tab"):
        return [lambda m, k=k: m == k, lambda m: m not in SEALS, lambda m: True]
    return [lambda m: m not in SEALS, lambda m: True]


def window(test, comp):
    L, M = test["n"], len(comp)
    if test["sk"] and test["ek"]:
        if M != L:
            return None
        w = comp
    elif M < L:
        return None
    elif test["sk"]:
        w = comp[:L]
    elif test["ek"]:
        w = comp[M - L:]
    else:
        o = (M - L) // 2
        w = comp[o:o + L]
    mask = test["lines"][0]
    return {"lines": [[m if m in BREAK else x for m, x in zip(mask, w)]], "sk": test["sk"], "ek": test["ek"], "n": L}


class KN:
    def __init__(self, texts, vocab_n):
        c = Counter(p for t in texts for p in pairs(t))
        self.c, self.V = c, vocab_n
        self.tot, self.typ = defaultdict(int), defaultdict(int)
        cont = defaultdict(int)
        for (a, b), n in c.items():
            self.tot[a] += n
            self.typ[a] += 1
            cont[b] += 1
        n1 = sum(1 for v in c.values() if v == 1)
        n2 = sum(1 for v in c.values() if v == 2)
        self.d2 = n1 / (n1 + 2 * n2)
        m1 = sum(1 for v in cont.values() if v == 1)
        m2 = sum(1 for v in cont.values() if v == 2)
        self.d1 = m1 / (m1 + 2 * m2)
        self.cont, self.B, self.W = cont, len(c), len(cont)

    def lp(self, a, b):
        pc = max(self.cont.get(b, 0) - self.d1, 0) / self.B + self.d1 * self.W / self.B / self.V
        if self.tot.get(a, 0) == 0:
            return -math.log2(pc)
        T = self.tot[a]
        return -math.log2(max(self.c.get((a, b), 0) - self.d2, 0) / T + self.d2 * self.typ[a] / T * pc)

    def score(self, t):
        ps = pairs(t)
        return sum(self.lp(a, b) for a, b in ps) / len(ps) if ps else None

    def unseen(self, t):
        ps = pairs(t)
        return sum(self.c.get(p, 0) == 0 for p in ps) / len(ps) if ps else None


def folds_for(pool):
    adj = defaultdict(set)
    byfam, bycode = defaultdict(list), defaultdict(list)
    for f in pool:
        byfam[f["object_family_id"]].append(f["record_id"])
        bycode[f["text_code_visual_ltr"]].append(f["record_id"])
    for grp in list(byfam.values()) + list(bycode.values()):
        for x in grp[1:]:
            adj[grp[0]].add(x)
            adj[x].add(grp[0])
    fold, seen = {}, set()
    for f in pool:
        s = f["record_id"]
        if s in seen:
            continue
        comp, q = [], deque([s])
        seen.add(s)
        while q:
            x = q.popleft()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    q.append(y)
        k = int(hashlib.sha256(("ff-" + min(comp, key=nat)).encode()).hexdigest(), 16) % 10
        for x in comp:
            fold[x] = k
    return fold


def evaluate(tests, pool, vocab_n, stat="score"):
    fold = folds_for(pool)
    train = {k: {} for k in range(10)}
    for f in pool:
        for k in range(10):
            if fold[f["record_id"]] != k:
                train[k].setdefault(f["text_code_visual_ltr"], f["_t"])
    base = {k: KN(list(train[k].values()), vocab_n) for k in range(10)}
    comps = [f for f in pool if f["complete_observed"] and len(f["_t"]["lines"]) == 1 and f["_t"]["sk"]
             and f["_t"]["ek"] and not (set(f["_t"]["lines"][0]) & BREAK)]
    res = []
    for f in tests:
        t = f["_t"]
        if len(t["lines"]) > 1 or not pairs(t):
            continue
        cell = None
        for cond in ladder(kind(f["object_type"])):
            cand = [(c, window(t, c["_t"]["lines"][0])) for c in comps if cond(kind(c["object_type"]))]
            cand = [(c, w) for c, w in cand if w is not None]
            if len(cand) >= 20:
                cell = cand
                break
        if cell is None:
            continue
        code = f["text_code_visual_ltr"]
        models = {k: (KN([x for cc, x in train[k].items() if cc != code], vocab_n) if code in train[k] else base[k])
                  for k in range(10)}
        fn = (lambda m, x: m.score(x)) if stat == "score" else (lambda m, x: m.unseen(x))
        tv = {k: fn(models[k], t) for k in range(10)}
        xs = np.array([fn(base[fold[c["record_id"]]], w) for c, w in cell])
        xt = np.array([tv[fold[c["record_id"]]] for c, w in cell])
        a, b = np.round(xt, 12), np.round(xs, 12)
        u = float(np.mean((a > b) + 0.5 * (a == b)))
        n = len(b)
        loo = np.array([(np.sum(b < v) + 0.5 * (np.sum(b == v) - 1)) / (n - 1) for v in b])
        res.append({"id": f["record_id"], "fam": f["object_family_id"], "site": f["site"],
                    "kind": kind(f["object_type"]), "u": u, "d": float(np.mean(xt - xs)), "loo": loo,
                    "ncomp": n})
    return res


def mc_p(res, draws=20000, seed=777):
    rng = np.random.default_rng(seed)
    acc = np.zeros(draws)
    for r in res:
        acc += r["loo"][rng.integers(0, len(r["loo"]), draws)]
    acc /= len(res)
    U = np.mean([r["u"] for r in res])
    return float((1 + np.sum(acc >= U - 1e-12)) / (1 + draws)), [float(np.quantile(acc, .025)), float(np.quantile(acc, .975))]


def boot(res, draws=10000, seed=4242):
    rng = np.random.default_rng(seed)
    u = np.array([r["u"] for r in res])
    v = np.array([u[rng.integers(0, len(u), len(u))].mean() for _ in range(draws)])
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def main():
    faces = [json.loads(l) for l in FACES.open(encoding="utf-8")]
    for f in faces:
        f["_t"] = parse(f)
        f["_g"] = group_of(f)
    vocab_n = len({t for f in faces for ln in f["_t"]["lines"] for t in ln if t not in BREAK}) + 1
    sa = [f for f in faces if f["_g"] == "SA"]
    wa = [f for f in faces if f["_g"] == "WA" and f["record_id"] != "6000.1"]
    S = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks = []

    def chk(name, mine, theirs, tol):
        ok = abs(mine - theirs) <= tol
        checks.append({"check": name, "verify": mine, "analysis": theirs, "tolerance": tol, "pass": bool(ok)})

    chk("vocabulary size", vocab_n, S["vocabulary_size_including_end"], 0)
    chk("pool faces", len(sa), S["pool"]["faces"], 0)
    h1 = evaluate(wa, sa, vocab_n)
    h2 = [r for r in h1 if r["kind"] == "rd"]
    for name, res, key in (("H1", h1, "H1_west_all"), ("H2", h2, "H2_west_round")):
        P = S["primary"][key]
        chk(f"{name} n", len(res), P["n"], 0)
        chk(f"{name} U", float(np.mean([r["u"] for r in res])), P["U"], 1e-9)
        chk(f"{name} delta bits", float(np.mean([r["d"] for r in res])), P["delta"], 1e-9)
        p, q = mc_p(res)
        chk(f"{name} null p (independent seed)", p, P["p_one_sided_U"], 2e-4)
        chk(f"{name} null q2.5", q[0], P["null_U_q025_q975"][0], 0.01)
        chk(f"{name} null q97.5", q[1], P["null_U_q025_q975"][1], 0.01)
        ci = boot(res)
        chk(f"{name} bootstrap lower", ci[0], P["U_ci95"][0], 0.012)
        chk(f"{name} bootstrap upper", ci[1], P["U_ci95"][1], 0.012)
    un = evaluate(wa, sa, vocab_n, stat="unseen")
    chk("H1 unseen-transition U", float(np.mean([r["u"] for r in un])), S["secondary"]["H1_west_all"]["unseen"]["U"], 1e-9)
    # Peripheral comparison: Gujarat/Kutch held out; South Asian round seals held out.
    gk = [f for f in sa if f["region"] == "Gujarat/Kutch"]
    gk_ids = {f["record_id"] for f in gk}
    seen, gk_tests = set(), []
    for f in sorted(gk, key=lambda x: nat(x["record_id"])):
        key = (f["object_family_id"], f["text_code_visual_ltr"])
        if key not in seen:
            seen.add(key)
            gk_tests.append(f)
    g = evaluate(gk_tests, [f for f in sa if f["record_id"] not in gk_ids], vocab_n)
    chk("Gujarat/Kutch n", len(g), S["peripheral"]["gujarat_kutch"]["all_media"]["n"], 0)
    chk("Gujarat/Kutch U", float(np.mean([r["u"] for r in g])), S["peripheral"]["gujarat_kutch"]["all_media"]["U"], 1e-9)
    rd = [f for f in sa if kind(f["object_type"]) == "rd"]
    rd_ids = {f["record_id"] for f in rd}
    r = evaluate(rd, [f for f in sa if f["record_id"] not in rd_ids], vocab_n)
    chk("South Asian round U", float(np.mean([x["u"] for x in r])), S["peripheral"]["south_asian_round"]["all_media"]["U"], 1e-9)
    out = {"summary_sha256": hashlib.sha256(SUMMARY.read_bytes()).hexdigest(),
           "passed": sum(c["pass"] for c in checks), "failed": sum(not c["pass"] for c in checks),
           "checks": checks}
    (HERE / "verify-2026-10-12.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for c in checks:
        print(("PASS" if c["pass"] else "FAIL"), c["check"], c["verify"], c["analysis"])
    print(out["passed"], "passed,", out["failed"], "failed")


if __name__ == "__main__":
    main()
