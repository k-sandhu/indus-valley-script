"""Independent check of the blind template results.

Shares only the parsed input tables and the frozen template list with the measurement
code. Segmentation, the length-free rule, stems, sandhi bases and compound members are
taken from the independent reimplementation of experiments/2026-10-21-rebus-base-rate/code/verify.py
(copied, not imported); the template search, word resolution, replacement pools, random
rates and the ratio are written here afresh.

    python experiments/2026-10-22-rebus-blind-templates/code/verify.py TEMPLATES.json RESULTS_DIR OUT_JSON
"""

import bisect
import json
import math
import random
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DER = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1"
SANGAM = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "sangam"
LONG = str.maketrans({"ā": "a", "ī": "i", "ū": "u", "ē": "e", "ō": "o"})
VOW = set("aeiou")


# ---- copied from the base-rate verify.py (independent of rebus.py)
def tokens(word):
    w = unicodedata.normalize("NFC", word.lower()).replace("r̤", "ḻ").replace("ṁ", "ṃ")
    w = w.replace("ŭ", "u").replace("ů", "u").replace("ĕ", "e").replace("ŏ", "o")
    out, i = [], 0
    while i < len(w):
        c = w[i]
        if w[i:i + 2] in ("ai", "au"):
            out.append(w[i:i + 2])
            i += 2
            continue
        if c == "·" and out:
            out[-1] += ":"
        elif unicodedata.category(c).startswith("L"):
            out.append(c)
        elif unicodedata.category(c).startswith("M") and out:
            out[-1] = unicodedata.normalize("NFC", out[-1] + c)
        i += 1
    return out


def t0(word):
    out = []
    for t in tokens(word):
        t = unicodedata.normalize("NFC", unicodedata.normalize("NFD", t.replace(":", "")).replace("̄", ""))
        t = t.translate(LONG)
        if not out or out[-1] != t:
            out.append(t)
    return tuple(out)


def t1(word):
    t = list(t0(word))
    if len(t) >= 4 and t[-1] == "m" and (t[-2] in VOW or t[-2] in ("ai", "au")):
        t.pop()
    if len(t) >= 3 and (t[-1] in VOW or t[-1] in ("ai", "au")):
        t.pop()
    return tuple(t)


def bases(m):
    out = {m}
    if m.endswith("a"):
        out.update({m + "m", m + "ṉ"})
    alt = {"ṇ": "ḷ", "ṉ": "l", "ṅ": "m", "ñ": "m", "n": "m", "ṭ": "ḷ", "ṟ": "l"}.get(m[-1:])
    if alt:
        out.add(m[:-1] + alt)
    return out


def members(translit):
    return [x for x in re.split(r"[-\s]+", unicodedata.normalize("NFC", translit)) if x and re.search(r"[aāiīuūeēoōŭ]", x)]


# ---- new for this package
def main(spec_path, results_dir, out_path):
    out_path = Path(out_path)
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    res = json.loads((Path(results_dir) / "templates.json").read_text(encoding="utf-8"))
    tl = [json.loads(l) for l in (DER / "tamil-lex-entries.jsonl").open(encoding="utf-8")]
    dedr = [json.loads(l) for l in (DER / "dedr-entries.jsonl").open(encoding="utf-8")]

    comps = [(m[0], m[1]) for m in (members(e["translit"]) for e in tl) if len(m) == 2]
    first_forms, second_forms, nfirst, nlast = {}, {}, {}, {}
    for a, b in comps:
        for st in {t1(x) for x in bases(a)}:
            nfirst[st] = nfirst.get(st, 0) + 1
            second_forms.setdefault(st, set()).add(t0(b))
        nlast[t1(b)] = nlast.get(t1(b), 0) + 1
        first_forms.setdefault(t1(b), set()).update(t0(x) for x in bases(a))

    def holds(w1, w2):
        return t0(w1) in first_forms.get(t1(w2), set()) or t0(w2) in second_forms.get(t1(w1), set())

    idents = spec["identifications"]
    checks = {}
    real = {t["id"]: any(holds(a, b) for a in idents[t["first"]]["words"] for b in idents[t["second"]]["words"])
            for t in spec["templates"]}
    frozen_real = {r["id"]: r["parpola_holds"] for r in res["results"]["primary"]["per_template"]}
    checks["parpola_hits_per_template"] = {"agree": real == frozen_real, "verify_hits": sum(real.values()),
                                           "frozen_hits": sum(frozen_real.values()),
                                           "disagreements": sorted(k for k in real if real[k] != frozen_real.get(k))}

    # replacement pools
    dedr_t0 = {t0(f) for r in dedr if len(set(r["subgroups"])) >= 2 for g in r["groups"] if g["lang"] == "Ta" for f in g["forms"]}
    toks = []
    for p in sorted(SANGAM.glob("pmuni*.html")):
        text = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
        toks.extend(re.findall(r"[஀-௿]+", text))
    toks.sort()
    signs = set(chr(c) for c in range(0x0BBE, 0x0BCE)) | {"ௗ"}

    def freq(head):
        h = re.sub(r"-.*$", "", head)
        while h and h[-1] in signs:
            h = h[:-1]
        return bisect.bisect_left(toks, h + "\U0010ffff") - bisect.bisect_left(toks, h) if h else 0

    singles = [e for e in tl if len(members(e["translit"])) == 1]
    cands = {}
    for e in singles:
        if e["star"] or (e["pos"] or "") != "n" or e["verb"] or t0(e["translit"]) not in dedr_t0:
            continue
        st = t1(e["translit"])
        if st not in cands:
            cands[st] = (e["translit"], nfirst.get(st, 0), nlast.get(st, 0), freq(e["head"]))

    def feat(word):
        e = next((x for x in singles if x["translit"] == word), None) or next((x for x in singles if t0(x["translit"]) == t0(word)), None)
        return (word, nfirst.get(t1(word), 0), nlast.get(t1(word), 0), freq(e["head"]) if e else 0)

    def sd(v):
        m = sum(v) / len(v)
        return math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) or 1.0

    items = list(cands.items())

    def pool(word, which, k=50):
        rw = feat(word)
        its = [c for st, c in items if st != t1(word)]
        lp, lf = [math.log1p(c[which]) for c in its], [math.log1p(c[3]) for c in its]
        sp, sf = sd(lp), sd(lf)
        d = [math.sqrt(((a - math.log1p(rw[which])) / sp) ** 2 + ((b - math.log1p(rw[3])) / sf) ** 2) for a, b in zip(lp, lf)]
        return [its[i][0] for i in sorted(range(len(its)), key=lambda i: (d[i], its[i][0]))[:k]]

    pools = {"first": {}, "second": {}}
    for t in spec["templates"]:
        for w in idents[t["first"]]["words"]:
            pools["first"].setdefault(w, pool(w, 1))
        for w in idents[t["second"]]["words"]:
            pools["second"].setdefault(w, pool(w, 2))
    frozen_pools = res["replacement_pools"]
    checks["replacement_pools"] = {"agree": all(pools[s][w] == [c["word"] for c in frozen_pools[s][w]] for s in pools for w in pools[s]),
                                   "words": {s: sorted(pools[s]) for s in pools}}

    # random rates: exact for one word per slot, 20,000 draws otherwise
    rng = random.Random(7)
    rates, frozen_rates, diffs = {}, {r["id"]: r["random_rate"] for r in res["results"]["primary"]["per_template"]}, {}
    for t in spec["templates"]:
        f1, f2 = idents[t["first"]]["words"], idents[t["second"]]["words"]
        p1, p2 = [pools["first"][w] for w in f1], [pools["second"][w] for w in f2]
        if len(p1) == 1 and len(p2) == 1:
            r = sum(holds(a, b) for a in p1[0] for b in p2[0]) / (len(p1[0]) * len(p2[0]))
            tol = 1e-12
        else:
            n = 20000
            r = sum(any(holds(a, b) for a in [rng.choice(p) for p in p1] for b in [rng.choice(p) for p in p2]) for _ in range(n)) / n
            fr = frozen_rates[t["id"]]
            tol = 4 * math.sqrt(max(fr * (1 - fr), 1e-6) * (1 / n + 1 / 5000))
        rates[t["id"]] = r
        diffs[t["id"]] = {"verify": r, "frozen": frozen_rates[t["id"]], "agree": abs(r - frozen_rates[t["id"]]) <= tol}
    checks["random_rates"] = {"agree": all(v["agree"] for v in diffs.values()), "per_template": diffs}
    H, R = sum(real.values()), sum(rates.values())
    checks["ratio"] = {"verify": H / R if R else None, "frozen": res["results"]["primary"]["ratio"],
                       "agree": R > 0 and abs(H / R - res["results"]["primary"]["ratio"]) <= 0.05 * max(1.0, H / R)}
    out = {"schema_version": "1.0", "task": "rebus-blind-templates/verification", "synthetic": False,
           "checks": checks, "all_agree": all(c["agree"] for c in checks.values())}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v["agree"] for k, v in checks.items()}, indent=1), "all", out["all_agree"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
