"""Independent check of the main numbers of the rebus base-rate study.

This script shares only the parsed input tables with the measurement code. It
reimplements Tamil segmentation, the length-free rule, sandhi bases, stem
anchoring, the compound sets, the replacement pools, the I1 search and its exact
null, and the Dravidian single-homophone rate under T0, then compares each number
with the frozen outputs.

    python experiments/2026-10-21-rebus-base-rate/code/verify.py RESULTS_DIR OUT_JSON
"""

import bisect
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DER = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1"
SANGAM = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "sangam"
PKG = ROOT / "experiments" / "2026-10-21-rebus-base-rate"

LONG = str.maketrans({"ā": "a", "ī": "i", "ū": "u", "ē": "e", "ō": "o"})
VOW = set("aeiou")


def tokens(word):
    """Every letter starts a segment, combining marks stay with it, a raised dot marks length."""
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


def main(results_dir, out_path):
    results_dir, out_path = Path(results_dir).resolve(), Path(out_path).resolve()
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    inter = json.loads((results_dir / "interlocks.json").read_text(encoding="utf-8"))
    homo = json.loads((results_dir / "homophones.json").read_text(encoding="utf-8"))
    tl = [json.loads(l) for l in (DER / "tamil-lex-entries.jsonl").open(encoding="utf-8")]
    dedr = [json.loads(l) for l in (DER / "dedr-entries.jsonl").open(encoding="utf-8")]
    checks = {}

    # compounds and anchoring
    comps = []
    for e in tl:
        m = members(e["translit"])
        if len(m) == 2:
            comps.append((m[0], m[1], e["translit"]))
    first, last = {}, {}
    for k, (a, b, _) in enumerate(comps):
        for st in {t1(x) for x in bases(a)}:
            first.setdefault(st, []).append(k)
        last.setdefault(t1(b), []).append(k)

    def A(w):
        return [comps[k] for k in first.get(t1(w), [])]

    def B(w):
        return [comps[k] for k in last.get(t1(w), [])]

    def shared(w1, w2):
        excl = {t0(x) for w in (w1, w2) for x in bases(w)}
        na = {t0(x[1]) for x in A(w1)}
        nb = {t0(y) for x in B(w2) for y in bases(x[0])}
        return (na & nb) - excl

    real = shared("muruku", "mīṉ")
    checks["two_member_compounds"] = {"verify": len(comps), "frozen": inter["lexicon"]["two_member_compounds"]}
    checks["real_I1_T0s"] = {"verify": sorted("".join(x) for x in real),
                             "frozen": sorted(inter["real"]["I1_T0s"]["shared"].keys())}
    checks["A_B_sizes"] = {"verify": [len(A("muruku")), len(B("mīṉ"))],
                           "frozen": [inter["real"]["A_size"], inter["real"]["B_size"]]}

    # replacement pools
    dedr_t0 = set()
    for r in dedr:
        if len({g for g in r["subgroups"]}) >= 2:
            for g in r["groups"]:
                if g["lang"] == "Ta":
                    for f in g["forms"]:
                        dedr_t0.add(t0(f))
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
        if not h:
            return 0
        return bisect.bisect_left(toks, h + "\U0010ffff") - bisect.bisect_left(toks, h)

    cands = {}
    for e in tl:
        if len(members(e["translit"])) != 1 or e["star"] or (e["pos"] or "") != "n" or e["verb"]:
            continue
        if t0(e["translit"]) not in dedr_t0:
            continue
        st = t1(e["translit"])
        if st not in cands:
            cands[st] = (e["translit"], len(first.get(st, [])), len(last.get(st, [])), freq(e["head"]))

    def real_feat(word):
        e = next(x for x in tl if x["translit"] == word and len(members(x["translit"])) == 1)
        return (word, len(first.get(t1(word), [])), len(last.get(t1(word), [])), freq(e["head"]))

    def pool(word, which, k=50):
        rw = real_feat(word)
        items = [c for st, c in cands.items() if st != t1(word)]
        lp = [math.log1p(c[which]) for c in items]
        lf = [math.log1p(c[3]) for c in items]

        def sd(v):
            m = sum(v) / len(v)
            return math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) or 1.0
        sp, sf = sd(lp), sd(lf)
        d = [math.sqrt(((a - math.log1p(rw[which])) / sp) ** 2 + ((b - math.log1p(rw[3])) / sf) ** 2) for a, b in zip(lp, lf)]
        order = sorted(range(len(items)), key=lambda i: (d[i], items[i][0]))
        return [items[i][0] for i in order[:k]]

    p1, p2 = pool("muruku", 1), pool("mīṉ", 2)
    checks["pool_W1"] = {"verify_equals_frozen": p1 == [x["word"] for x in inter["replacement_pools"]["muruku"]]}
    checks["pool_W2"] = {"verify_equals_frozen": p2 == [x["word"] for x in inter["replacement_pools"]["mīṉ"]]}
    hits = sum(bool(shared(a, b)) for a in p1 for b in p2)
    checks["I1_null_T0s_K50"] = {"verify": hits / (len(p1) * len(p2)), "frozen": inter["null"]["I1_T0s"]["K50"]["rate"]}

    # Dravidian single-homophone rate under T0, all words
    pools = json.loads((PKG / "pools-v1.json").read_text(encoding="utf-8"))

    def items(text):
        out = set()
        text = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", " ", text or "")
        for part in re.split(r"[,;:]", text):
            p = re.sub(r"\s+", " ", part.strip().lower().strip(" .?!'\""))
            p = re.sub(r"^(to be |to |the |be )", "", p).strip()
            if p:
                out.add(p)
        return out

    lex = []
    for r in dedr:
        if len(r["subgroups"]) < 2 or not r["groups"]:
            continue
        head = next((g for g in r["groups"] if g["lang"] == "Ta"), r["groups"][0])
        its = set()
        for g in r["groups"]:
            its |= items(g["gloss"])
        lex.append(({t0(f) for f in head["forms"] if t0(f)}, its))

    def forms_for(key):
        fs = set()
        found = False
        for forms, its in lex:
            if key in its or key + "s" in its or key + "es" in its:
                fs |= forms
                found = True
        return fs if found else None

    P = [f for f in (forms_for(c["key"]) for c in pools["picture"]) if f is not None]
    M = [f for f in (forms_for(c["key"]) for c in pools["name"]) if f is not None]
    k = sum(1 for a in P for b in M if a & b)
    checks["dravidian_rate_T0"] = {"verify": k / (len(P) * len(M)),
                                   "frozen": homo["languages"]["dravidian-dedr"]["tolerances"]["T0"]["rate_any"]}

    def agree(c):
        if "verify_equals_frozen" in c:
            return c["verify_equals_frozen"]
        v, f = c["verify"], c["frozen"]
        if isinstance(v, float):
            return abs(v - f) < 1e-12
        return v == f

    for c in checks.values():
        c["agree"] = agree(c)
    out = {"schema_version": "1.0", "task": "rebus-base-rate/verification", "results_dir": str(results_dir.relative_to(ROOT)).replace("\\", "/"),
           "checks": checks, "all_agree": all(c["agree"] for c in checks.values())}
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
