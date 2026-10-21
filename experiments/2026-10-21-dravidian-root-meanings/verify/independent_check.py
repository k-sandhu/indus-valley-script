"""Independent check of the frozen root probabilities, written by the coordinating session.

The study's reconstruction code was written by Codex (code/recon.py). This file reimplements
the primary model from the protocol without reading that code: a NEXUS/Newick reader, the
symmetric two-state model (Mk1) with a flat root prior and the rate fitted by maximum
likelihood on the tree rescaled to root height 1, and Fitch parsimony at the root. It reads
a codings file of the form {"meaning": {"tip label": 1 | 0 | null, ...}, ...} and prints, for
each meaning, the fitted rate, the root probability and the Fitch root set.

    python -I experiments/2026-10-21-dravidian-root-meanings/verify/independent_check.py TREE.nex CODINGS.json OUT.json
"""

import json
import math
import re
import site
import sys

# Isolated mode (-I) drops the user site-packages, where NumPy and SciPy are installed here;
# add that trusted location back without adding the working or script directory.
sys.path.append(site.getusersitepackages())

import numpy as np  # noqa: E402
from scipy.optimize import minimize_scalar


def read_nexus_tree(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    translate = {}
    m = re.search(r"(?is)translate(.*?);", text)
    if m:
        for item in m.group(1).split(","):
            parts = item.strip().split(None, 1)
            if len(parts) == 2:
                translate[parts[0]] = parts[1].strip().strip("'\"")
    tm = re.search(r"(?is)\btree\s+[^=]+=\s*(?:\[&[RU]\]\s*)?(.*?;)", text)
    newick = re.sub(r"\[[^\]]*\]", "", tm.group(1))
    return parse_newick(newick, translate)


def parse_newick(s, translate):
    # Nodes: dict(children=[...], length=float, name=str)
    pos = 0

    def node():
        nonlocal pos
        n = {"children": [], "length": 0.0, "name": None}
        if s[pos] == "(":
            pos += 1
            while True:
                n["children"].append(node())
                if s[pos] == ",":
                    pos += 1
                    continue
                if s[pos] == ")":
                    pos += 1
                    break
        start = pos
        while s[pos] not in ",():;":
            pos += 1
        label = s[start:pos].strip()
        if label:
            n["name"] = translate.get(label, label)
        if s[pos] == ":":
            pos += 1
            start = pos
            while s[pos] not in ",();":
                pos += 1
            n["length"] = float(s[start:pos])
        return n

    root = node()
    return root


def tips(n):
    return [n["name"]] if not n["children"] else [t for c in n["children"] for t in tips(c)]


def height(n):
    return 0.0 if not n["children"] else max(c["length"] + height(c) for c in n["children"])


def partials(n, data, q, scale):
    """Conditional likelihoods (L0, L1) of the subtree below n, with log scaling."""
    if not n["children"]:
        v = data.get(n["name"])
        return (np.array([1.0, 1.0]) if v is None else np.array([1.0 - v, float(v)])), 0.0
    out = np.ones(2)
    logs = 0.0
    for c in n["children"]:
        lc, sc = partials(c, data, q, scale)
        t = c["length"] / scale
        same = 0.5 + 0.5 * math.exp(-2.0 * q * t)
        diff = 1.0 - same
        out *= np.array([same * lc[0] + diff * lc[1], diff * lc[0] + same * lc[1]])
        logs += sc
    m = out.max()
    return out / m, logs + math.log(m)


def loglik(root, data, q, scale):
    L, s = partials(root, data, q, scale)
    return math.log(0.5 * L[0] + 0.5 * L[1]) + s


def fit(root, data):
    scale = height(root)
    grid = np.linspace(math.log(1e-6), math.log(1e3), 121)
    vals = [loglik(root, data, math.exp(g), scale) for g in grid]
    i = int(np.argmax(vals))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    res = minimize_scalar(lambda g: -loglik(root, data, math.exp(g), scale), bounds=(lo, hi), method="bounded",
                          options={"xatol": 1e-10})
    g = res.x if -res.fun >= vals[i] else grid[i]
    q = math.exp(g)
    L, _ = partials(root, data, q, scale)
    p1 = L[1] / (L[0] + L[1])
    return q, loglik(root, data, q, scale), p1


def fitch(n, data):
    if not n["children"]:
        v = data.get(n["name"])
        return {0, 1} if v is None else {int(v)}
    sets = [fitch(c, data) for c in n["children"]]
    inter = set.intersection(*sets)
    return inter if inter else set.union(*sets)


def main():
    tree_path, codings_path, out_path = sys.argv[1:4]
    root = read_nexus_tree(tree_path)
    codings = json.load(open(codings_path, encoding="utf-8"))
    names = set(tips(root))
    out = {}
    for meaning, data in codings.items():
        unknown = set(data) - names
        if unknown:
            raise SystemExit(f"{meaning}: labels not in tree: {sorted(unknown)}")
        observed = [v for v in data.values() if v is not None]
        q, ll, p1 = fit(root, data)
        out[meaning] = {"n1": sum(1 for v in observed if v == 1), "n0": sum(1 for v in observed if v == 0),
                        "q": q, "loglik": ll, "root_p1": p1, "fitch_root": sorted(fitch(root, data))}
    json.dump(out, open(out_path, "x", encoding="utf-8"), indent=2)
    for k, v in out.items():
        print(f"{k:24s} n1={v['n1']:2d} n0={v['n0']:2d} q={v['q']:.4g} root={v['root_p1']:.4f} fitch={v['fitch_root']}")


if __name__ == "__main__":
    main()
