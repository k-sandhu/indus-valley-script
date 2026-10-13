"""Stage 3e (secondary): can the same freedom fit the Indus corpus to other languages?

Each language's running text is projected onto at most fifteen consonant classes with vowels and
spaces removed, and an order-5 Kneser-Ney model is trained on it. Indus signs then receive a free
assignment: every sign takes one consonant class (no empty values), optimized by simulated annealing
for order gain. Fits on the full corpus, fits on half A evaluated on half B, and fits on
order-scrambled corpora are compared with each language's own held-out line-initial spans and with
i.i.d. strings at that language's class frequencies.
"""
import io
import json
import math
import os
import re
import sys
import time
import unicodedata
import zipfile
from collections import Counter
from multiprocessing import Pool

import numpy as np

from common import (HERE, RAW, ROOT, KneserNey, dcs_lines, dcs_split, iast_skeleton, unique_texts)
from stage3_fit import scramble, split_half

SEED = 20261012
OTHER = os.path.join(RAW, "other-languages")
SUMERIAN_ZIP = os.path.join(ROOT, "data", "raw", "2026-10-12-bronze-age-comparison", "acquisition",
                            "sumerian-ur3-v1", "response.bin")

# ----------------------------------------------------------------------------- projections

SANSKRIT_CLASSES = "kgcjtdnpbmyrlvs"


def sanskrit_lines():
    split = dcs_split()
    for p in split["train"] + split["heldout"]:
        for line in dcs_lines(p):
            yield line.split()  # words; skeleton per word below


def sanskrit_word(w):
    return iast_skeleton(w)


LATIN_MAP = {"b": "b", "c": "c", "k": "c", "q": "c", "d": "d", "f": "f", "g": "g", "h": "h", "l": "l",
             "m": "m", "n": "n", "p": "p", "r": "r", "s": "s", "z": "s", "t": "t", "v": "v", "x": "cs", "j": "j"}


def latin_word(w):
    w = unicodedata.normalize("NFD", w.lower())
    out = []
    for i, ch in enumerate(w):
        if ch == "u" and i > 0 and w[i - 1] == "q":
            continue
        if ch in LATIN_MAP:
            out.append(LATIN_MAP[ch])
    return "".join(out)


def latin_lines():
    for fn in sorted(os.listdir(OTHER)):
        if not fn.endswith(".xml"):
            continue
        with open(os.path.join(OTHER, fn), encoding="utf-8") as f:
            text = f.read()
        body = text.split("<body", 1)[-1]
        body = re.sub(r"<note[^>]*>.*?</note>", " ", body, flags=re.S)
        body = re.sub(r"<[^>]+>", " ", body)
        for sent in re.split(r"[.;:!?]", body):
            words = re.findall(r"[A-Za-z]+", sent)
            if words:
                yield words


# Tamil: consonant letters, with rare nasals merged so that fifteen classes remain.
TAMIL_CONS = {"க": "k", "ங": "n", "ச": "c", "ஞ": "n", "ட": "T", "ண": "N", "த": "t", "ந": "n", "ப": "p",
              "ம": "m", "ய": "y", "ர": "r", "ல": "l", "வ": "v", "ழ": "z", "ள": "L", "ற": "R", "ன": "n",
              "ஜ": "c", "ஷ": "c", "ஸ": "c", "ஹ": "k"}


def tamil_word(w):
    return "".join(TAMIL_CONS[ch] for ch in w if ch in TAMIL_CONS)


def tamil_lines():
    import pyarrow.parquet as pq
    tab = pq.read_table(os.path.join(OTHER, "sangam.parquet"), columns=["tamil_text"]).to_pylist()
    for row in tab:
        for line in (row["tamil_text"] or "").split("\n"):
            words = [w for w in re.split(r"[\s,.;:!?–—\-‘’“”\"'()]+", line) if w]
            if words:
                yield words


SUMERIAN_MAP = {"b": "b", "d": "d", "g": "g", "ĝ": "N", "h": "h", "ḫ": "h", "k": "k", "l": "l", "m": "m",
                "n": "n", "p": "p", "r": "r", "s": "s", "ṣ": "s", "š": "S", "t": "t", "ṭ": "t", "z": "z"}


def sumerian_word(w):
    w = re.sub(r"\{[^}]*\}", "", w)
    w = unicodedata.normalize("NFC", w.lower())
    return "".join(SUMERIAN_MAP[ch] for ch in w if ch in SUMERIAN_MAP)


def sumerian_lines(max_texts=12000):
    z = zipfile.ZipFile(SUMERIAN_ZIP)
    names = sorted(n for n in z.namelist() if "/corpusjson/P" in n)
    rng = np.random.default_rng(SEED + 31)
    pick = sorted(rng.choice(len(names), size=min(max_texts, len(names)), replace=False))
    for i in pick:
        try:
            d = json.loads(z.read(names[i]))
        except Exception:
            continue
        lines, cur = [], []

        def walk(n):
            nonlocal cur
            if isinstance(n, dict):
                if n.get("node") == "d" and n.get("type") == "line-start":
                    if cur:
                        lines.append(cur)
                    cur = []
                if n.get("node") == "l":
                    f = n.get("f", {})
                    form = f.get("form") or ""
                    if f.get("lang", "sux").startswith("sux") and not re.match(r"^\d", form):
                        cur.append(form)
                for v in (n.get("cdl") or []):
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)

        walk(d)
        if cur:
            lines.append(cur)
        for ln in lines:
            yield ln


LANGS = {
    "sanskrit": (sanskrit_lines, sanskrit_word),
    "latin": (latin_lines, latin_word),
    "tamil": (tamil_lines, tamil_word),
    "sumerian": (sumerian_lines, sumerian_word),
}


# ----------------------------------------------------------------------------- language model

class Lang:
    def __init__(self, name):
        gen, wordfn = LANGS[name]
        lines = []
        for words in gen():
            sks = [wordfn(w) for w in words]
            sks = [s for s in sks if s]
            if sks:
                lines.append(sks)
        classes = sorted({c for ws in lines for w in ws for c in w})
        self.name = name
        self.classes = classes
        self.V = len(classes)
        self.cid = {c: i for i, c in enumerate(classes)}
        enc = [[[self.cid[c] for c in w] for w in ws] for ws in lines]
        self.train = [sum(ws, []) for i, ws in enumerate(enc) if i % 10 != 9]
        self.held_lines = [ws for i, ws in enumerate(enc) if i % 10 == 9]
        m = KneserNey(5, self.V).fit(self.train)
        self.base = self.V + 1
        self.mod = self.base ** 4
        self.table = m.dense_table().tolist()
        uni = Counter(c for s in self.train for c in s)
        tot = sum(uni.values())
        self.p1 = [uni[i] / tot for i in range(self.V)]
        self.U = [math.log2(p) for p in self.p1]
        c = 0
        for _ in range(4):
            c = c * self.base + self.V
        self.bos = c
        held = [sum(ws, []) for ws in self.held_lines]
        tot_lp = sum(m.logprob_seq(s) for s in held)
        n = sum(map(len, held))
        self.heldout_H = -tot_lp / n
        self.n_train = sum(map(len, self.train))

    def score(self, seq):
        T, U, ctx = self.table, self.U, self.bos
        llr = ll = 0.0
        for x in seq:
            lp = T[ctx][x]
            ll += lp
            llr += lp - U[x]
            ctx = (ctx * self.base + x) % self.mod
        return llr, ll, len(seq)

    def stats(self, seqs):
        a = b = 0.0
        n = 0
        for s in seqs:
            x, y, k = self.score(s)
            a += x
            b += y
            n += k
        return {"G": a / n if n else 0.0, "LL": b / n if n else 0.0, "n": n}

    def references(self, key_lengths, rng):
        out = {}
        for k in (1, 2, 3):
            spans = [sum(ws[:k], []) for ws in self.held_lines if len(ws) >= k]
            idx = rng.choice(len(spans), size=min(5000, len(spans)), replace=False)
            sel = [spans[i] for i in idx]
            st = self.stats(sel)
            st["mean_consonants"] = float(np.mean([len(s) for s in sel]))
            out[f"line_initial_{k}"] = st
        iid = [list(rng.choice(self.V, size=L, p=self.p1)) for L in key_lengths if L > 0]
        out["iid_key_lengths"] = self.stats(iid)
        return out


# ----------------------------------------------------------------------------- free-assignment annealing

class FreeAnnealer:
    def __init__(self, lang, texts, assign, rng):
        self.L = lang
        self.texts = texts
        self.a = dict(assign)
        self.rng = rng
        self.signs = sorted({s for t in texts for s in t})
        self.where = {s: [] for s in self.signs}
        for i, t in enumerate(texts):
            for s in set(t):
                self.where[s].append(i)
        self.cache = [lang.score([self.a[s] for s in t]) for t in texts]
        self.A = sum(c[0] for c in self.cache)
        self.N = sum(c[2] for c in self.cache)

    def G(self):
        return self.A / self.N

    def run(self, steps, t0, t1):
        rng = self.rng
        V = self.L.V
        ns = len(self.signs)
        lr = math.log(t1 / t0)
        acc = 0
        for step in range(steps):
            temp = t0 * math.exp(lr * step / steps)
            s = self.signs[rng.integers(ns)]
            old = self.a[s]
            new = int(rng.integers(V))
            if new == old:
                continue
            self.a[s] = new
            dA = 0.0
            upd = {}
            for k in self.where[s]:
                sc = self.L.score([self.a[x] for x in self.texts[k]])
                upd[k] = sc
                dA += sc[0] - self.cache[k][0]
            delta = dA / self.N  # lengths are fixed: one consonant per sign
            if delta >= 0 or rng.random() < math.exp(delta / temp):
                self.A += dA
                for k, sc in upd.items():
                    self.cache[k] = sc
                acc += 1
            else:
                self.a[s] = old
        return acc


_LANG = {}


def _init(langs):
    _LANG.update(langs)


def eval_assign(lang, texts, a):
    return lang.stats([[a[s] for s in t] for t in texts])


def job(args):
    name, label, seed, fit, evals, steps = args
    lang = _LANG[name]
    rng = np.random.default_rng(seed)
    allsigns = sorted({s for ts in list(evals.values()) + [fit] for t in ts for s in t})
    start = {s: int(rng.choice(lang.V, p=lang.p1)) for s in allsigns}
    ann = FreeAnnealer(lang, fit, start, rng)
    g0 = ann.G()
    acc = ann.run(steps, 2e-3, 2e-6)
    res = {"language": name, "label": label, "seed": seed, "accepted": acc, "G_start": g0, "G_fit": ann.G()}
    for k, ts in evals.items():
        res["eval_" + k] = eval_assign(lang, ts, ann.a)
    return res


def main():
    t0 = time.time()
    names = sys.argv[1:] or list(LANGS)
    texts = unique_texts(min_len=2)
    A, B = split_half(texts)
    langs = {}
    for n in names:
        langs[n] = Lang(n)
        print(n, langs[n].V, langs[n].classes, "train", langs[n].n_train, "H", round(langs[n].heldout_H, 3),
              round(time.time() - t0, 1), flush=True)
    key_lengths = [len(t) for t in texts]  # one consonant per sign under free assignment
    summary = {"languages": {}}
    for n, L in langs.items():
        rng = np.random.default_rng(SEED + 77)
        summary["languages"][n] = {
            "classes": "".join(L.classes), "V": L.V, "train_consonants": L.n_train,
            "heldout_cross_entropy": L.heldout_H, "redundancy": 1 - L.heldout_H / math.log2(L.V),
            "references": L.references(key_lengths, rng),
        }
    for L in langs.values():  # workers need only the probability tables
        L.train = None
        L.held_lines = None
    steps = int(os.environ.get("ANNEAL_STEPS", "300000"))
    jobs = []
    for n in names:
        for r in range(3):
            jobs.append((n, "real", SEED + 100 * r + 1, texts, {"all": texts}, steps))
        for r in range(3):
            jobs.append((n, "fitA", SEED + 100 * r + 2, A, {"A": A, "B": B}, steps))
        for r in range(2):
            sc = scramble(texts, SEED + 2000 + r)
            jobs.append((n, "scrambled", SEED + 100 * r + 3, sc, {"scrambled": sc, "real": texts}, steps))
    with Pool(int(os.environ.get("WORKERS", "8")), initializer=_init, initargs=(langs,)) as pool:
        res = pool.map(job, jobs, chunksize=1)
    summary["anneal"] = res
    summary["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(HERE, "stage3e"), exist_ok=True)
    with open(os.path.join(HERE, "stage3e", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    for n in names:
        ref = summary["languages"][n]["references"]
        print(n, {k: round(v["G"], 3) for k, v in ref.items()})
    for r in res:
        print(r["language"], r["label"], round(r["G_fit"], 3),
              {k: round(v["G"], 3) for k, v in r.items() if k.startswith("eval_")})


if __name__ == "__main__":
    main()
