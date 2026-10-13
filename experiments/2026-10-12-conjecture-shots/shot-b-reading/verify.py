"""Independent recomputation of the Shot B primary test (S, z1, z2, pass decision).

Written after the confirmation run from the text of PREDICTIONS.md, without importing
or calling confirm.py. Differences from confirm.py are deliberate where the
specification leaves room: units are built with plain dictionaries, the size regression
uses scikit-learn, the bias of the G statistic is estimated with 4,000 draws from a
different seed, and the rearrangement null uses a different generator seed. Exact
agreement is expected for the size contrast T2 and close agreement (Monte Carlo
error only) for T1, z1, z2, S and its percentile. Reading the confirmation half again
is logged in confirmation-access.jsonl.

Writes verification.json.
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import shots_common  # noqa: E402

MISS = {"", "-", "None", "?", "NA", "N/A", "n/a", "none", "unknown", "Unknown"}


def val(x):
    if x is None:
        return None
    x = str(x).strip()
    return None if x in MISS else x


def pos_num(x):
    x = val(x)
    if x is None or not re.fullmatch(r"\d+(\.\d+)?", x) or float(x) <= 0:
        return None
    return float(x)


gm = json.loads((HERE / "GLOSS-MAP.json").read_text(encoding="utf-8"))
signs = gm["signs"]
codes = [x["code"] for x in signs]
idx = {c: i for i, c in enumerate(codes)}
is_local = np.array([x["class"] in ("NAME", "COMM") for x in signs])
is_off = np.array([x["class"] in ("AFF", "TITLE") or x["code"] in ("400", "621") for x in signs])
assert all(is_off[i] == x["official"] for i, x in enumerate(signs))
assert all(is_local[i] == (x["locality"] == "local") for i, x in enumerate(signs))

faces = shots_common.load_half("confirmation", HERE)

# seal families -----------------------------------------------------------------------
fam_faces = defaultdict(list)
for f in faces:
    fam_faces[f["object_family_id"]].append(f)
seals = []
for fid, fs in fam_faces.items():
    if not fs[0]["object_type"].startswith("SEAL"):
        continue
    sset = {s for f in fs for s in f["signs_reading_rtl"] if s != "000"}
    sites = Counter(v for v in (val(f.get("site")) for f in fs) if v)
    area = None
    for f in fs:
        h, v = pos_num(f["metadata"].get("horizontal(mm)")), pos_num(f["metadata"].get("vertical(mm)"))
        if h and v:
            area = h * v
            break
    t = fs[0]["object_type"]
    seals.append({"comp": fs[0]["component"], "signs": sset, "site": sites.most_common(1)[0][0] if sites else None,
                  "area": area, "len": max(f["length"] for f in fs),
                  "sub": "S" if t.startswith("SEAL:S") else "R" if t.startswith("SEAL:R") else "other"})

# P1 per-sign site concentration ------------------------------------------------------------
site_units = defaultdict(set)
for s in seals:
    if s["site"]:
        site_units[(s["comp"], s["site"])] |= s["signs"]
unit_list = list(site_units.items())
site_n = Counter(site for (c, site), _ in unit_list)
keep = sorted(k for k, n in site_n.items() if n >= 20)
cats = keep + ["other"]
bg = np.array([sum(n for k, n in site_n.items() if (k if k in keep else "other") == c) for c in cats], float)
bg /= bg.sum()
rng_g = np.random.default_rng(99)
gcache = {}


def gval(o, n):
    e = n * bg
    m = o > 0
    return 2 * np.sum(o[m] * np.log(o[m] / e[m]))


def gmean(n):
    if n not in gcache:
        d = rng_g.multinomial(n, bg, size=4000).astype(float)
        gcache[n] = float(np.mean([gval(r, n) for r in d]))
    return gcache[n]


e1 = np.full(len(codes), np.nan)
for c in codes:
    o = np.zeros(len(cats))
    for (comp, site), ss in unit_list:
        if c in ss:
            o[cats.index(site if site in keep else "other")] += 1
    n = int(o.sum())
    if n >= 8:
        e1[idx[c]] = (gval(o, n) - gmean(n)) / (2 * n)

# P2 per-sign size residual ----------------------------------------------------------------
by_comp = defaultdict(list)
for s in seals:
    if s["area"]:
        by_comp[s["comp"]].append(s)
X, y, comp_signs = [], [], []
for comp, ss in by_comp.items():
    sub = Counter(s["sub"] for s in ss).most_common(1)[0][0]
    L = min(max(s["len"] for s in ss), 12)
    X.append([sub == "R", sub == "S"] + [L == k for k in range(2, 13)])
    y.append(float(np.mean([math.log2(s["area"]) for s in ss])))
    comp_signs.append(set().union(*(s["signs"] for s in ss)))
X, y = np.array(X, float), np.array(y)
res = y - LinearRegression().fit(X, y).predict(X)
e2 = np.full(len(codes), np.nan)
for c in codes:
    r = [res[i] for i, ss in enumerate(comp_signs) if c in ss]
    if len(r) >= 8:
        e2[idx[c]] = float(np.mean(r))


def contrast(e, a, b):
    ok = ~np.isnan(e)
    if not (ok & a).any() or not (ok & b).any():
        return np.nan
    return e[ok & a].mean() - e[ok & b].mean()


T1 = contrast(e1, is_local, ~is_local)
T2 = contrast(e2, is_off, ~is_off)

# rearrangement null ---------------------------------------------------------------------
cells = defaultdict(list)
for i, x in enumerate(signs):
    cells[(x["band"]["frequency"], x["band"]["position"])].append(i)
rng = np.random.default_rng(424242)
N = 10000
t1s, t2s = np.empty(N), np.empty(N)
for j in range(N):
    perm = np.arange(len(codes))
    for members in cells.values():
        m = np.array(members)
        perm[m] = m[rng.permutation(len(m))]
    t1s[j] = contrast(e1, is_local[perm], ~is_local[perm])
    t2s[j] = contrast(e2, is_off[perm], ~is_off[perm])
z1 = (T1 - t1s.mean()) / t1s.std()
z2 = (T2 - t2s.mean()) / t2s.std()
Snull = (t1s - t1s.mean()) / t1s.std() + (t2s - t2s.mean()) / t2s.std()
S = z1 + z2
out = {
    "method": "independent recomputation from PREDICTIONS.md; confirm.py not imported",
    "seal_families": len(seals), "site_units": len(unit_list), "size_units": len(y),
    "eligible_site": int((~np.isnan(e1)).sum()), "eligible_size": int((~np.isnan(e2)).sum()),
    "T1": T1, "T2": T2, "z1": z1, "z2": z2, "S": S,
    "S_null_95th": float(np.percentile(Snull, 95)),
    "percentile_of_S": float(100 * np.mean(Snull < S)),
    "distance_sd": float((S - Snull.mean()) / Snull.std()),
    "pass": bool(S > np.percentile(Snull, 95)),
}
conf = json.loads((HERE / "confirmation" / "results.json").read_text(encoding="utf-8"))
c1, c2, cp = conf["components"]["P1_site_local_vs_pan"], conf["components"]["P2_size_official_vs_other"], conf["primary"]
out["confirm_py"] = {"T1": c1["actual"], "T2": c2["actual"], "z1": c1["z"], "z2": c2["z"], "S": cp["S"],
                     "percentile_of_S": cp["percentile_of_S"], "distance_sd": cp["distance_sd"], "pass": cp["pass"]}
out["agreement"] = {
    "T2_abs_diff": abs(T2 - c2["actual"]),
    "T1_abs_diff": abs(T1 - c1["actual"]),
    "z1_abs_diff": abs(z1 - c1["z"]), "z2_abs_diff": abs(z2 - c2["z"]), "S_abs_diff": abs(S - cp["S"]),
    "pass_decision_same": out["pass"] == cp["pass"],
    "tolerance_rule": "T2 to 1e-9; T1 to 0.002 (Monte Carlo bias correction); z and S to 0.1",
}
a = out["agreement"]
out["verified"] = bool(a["T2_abs_diff"] < 1e-9 and a["T1_abs_diff"] < 0.002 and a["z1_abs_diff"] < 0.1
                       and a["z2_abs_diff"] < 0.1 and a["S_abs_diff"] < 0.1 and a["pass_decision_same"])
(HERE / "verification.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
print(json.dumps(out, indent=1, default=float))
