"""Shared inputs for Study A: key reconstruction, skeleton projection and Kneser-Ney models.

The skeleton keeps only what Yajnadevam's key fixes: consonant classes pooled as in
decipher.csv, with vowels and word spaces removed.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import math
import os
import unicodedata
from collections import Counter, defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LIPI = os.path.join(ROOT, "data", "lipi")
# Another key in the same sign,xlit,canonical,regex format can be tested by setting IVS_KEY_CSV.
KEY_CSV = os.environ.get("IVS_KEY_CSV", os.path.join(LIPI, "src", "assets", "data", "xlits.csv"))
INSCRIPTIONS_CSV = os.path.join(LIPI, "src", "assets", "data", "inscriptions.csv")
GLOSSING_CSV = os.path.join(LIPI, "glossing.csv")
CLEAN_JSONL = os.path.join(ROOT, "data", "normalized", "lipi_clean_rtl_singleline.jsonl")
RAW = os.path.join(ROOT, "data", "raw", "2026-10-12-decipherment-claim-tests")
DCS_DIR = os.path.join(RAW, "dcs-sanskrit", "dcs", "data", "conllu", "files")
MW_TXT = os.path.join(RAW, "mw", "mw.txt")
HERE = os.path.dirname(os.path.abspath(__file__))

CLASSES = "kgcjtdnpbmyrlvs"  # fifteen pooled consonant classes
CID = {c: i for i, c in enumerate(CLASSES)}
NC = len(CLASSES)
BOS = NC  # start symbol id

DCS_TEXTS = [
    "Ṛgveda",
    "Atharvaveda (Śaunaka)",
    "Śatapathabrāhmaṇa",
    "Manusmṛti",
    "Arthaśāstra",
    "Rāmāyaṇa",
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# --------------------------------------------------------------------------- projection

# SLP1 letters used by the key, the published readings and Monier-Williams k1 headwords.
SLP1_CLASS = {
    "k": "k", "K": "k", "g": "g", "G": "g", "N": "n",
    "c": "c", "C": "c", "j": "j", "J": "j", "Y": "n",
    "w": "t", "W": "t", "q": "d", "Q": "d", "R": "n",
    "t": "t", "T": "t", "d": "d", "D": "d", "n": "n",
    "p": "p", "P": "p", "b": "b", "B": "b", "m": "m",
    "y": "y", "r": "r", "l": "l", "v": "v",
    "S": "s", "z": "s", "s": "s", "h": "s",
    "M": "n", "H": "s", "f": "r", "F": "r", "x": "l", "X": "l", "L": "l",
}
SLP1_VOWELS = set("aAiIuUeEoO~")


def slp1_skeleton(s: str) -> str:
    out = []
    for ch in s:
        if ch in SLP1_CLASS:
            out.append(SLP1_CLASS[ch])
        # vowels, separators, digits and punctuation carry no class
    return "".join(out)


IAST_SINGLE = {
    "k": "k", "g": "g", "ṅ": "n", "c": "c", "j": "j", "ñ": "n",
    "ṭ": "t", "ḍ": "d", "ṇ": "n", "t": "t", "d": "d", "n": "n",
    "p": "p", "b": "b", "m": "m", "y": "y", "r": "r", "l": "l", "v": "v",
    "ś": "s", "ṣ": "s", "s": "s", "h": "s",
    "ṃ": "n", "ṁ": "n", "ḥ": "s", "ṛ": "r", "ṝ": "r", "ḷ": "l", "ḹ": "l", "ḻ": "l",
}
IAST_VOWELS = set("aāiīuūeoēō")
ASPIRABLE = set("kgcjṭḍtdpb")


def iast_skeleton(text: str) -> str:
    """Project IAST text onto the fifteen classes; aspiration h after a stop is dropped."""
    text = unicodedata.normalize("NFC", text.lower())
    out = []
    prev = ""
    for ch in text:
        if ch == "h" and prev in ASPIRABLE:
            prev = "h"
            continue
        if ch in IAST_SINGLE:
            out.append(IAST_SINGLE[ch])
        prev = ch
    return "".join(out)


# Full phoneme tokenization for the with-vowels redundancy comparison.
IAST_DIGRAPHS = ["kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh", "ai", "au"]
IAST_PHONEMES = set("aāiīuūṛṝḷḹeokgṅcjñṭḍṇtdnpbmyrlvśṣshṃṁḥḻ ")


def iast_phonemes(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text.lower())
    toks: list[str] = []
    i = 0
    while i < len(text):
        two = text[i:i + 2]
        if two in IAST_DIGRAPHS:
            toks.append(two)
            i += 2
            continue
        ch = text[i]
        if ch == "ṁ":
            ch = "ṃ"
        if ch in IAST_PHONEMES:
            if ch == " " and (not toks or toks[-1] == " "):
                pass
            else:
                toks.append(ch)
        i += 1
    return toks


# --------------------------------------------------------------------------- key

def load_key() -> dict[str, dict]:
    with open(KEY_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    key = {r["sign"]: {"xlit": r["xlit"], "canonical": r["canonical"], "regex": r["regex"]} for r in rows}
    return key


def resolve_values(key: dict[str, dict]) -> dict[str, str]:
    """Reproduce the app's mkregex: empty xlit takes component xlits in reversed canonical order."""
    resolved: dict[str, str] = {}

    def value(sign: str, depth: int = 0) -> str:
        if sign in resolved:
            return resolved[sign]
        if sign not in key or depth > 10:
            return ""
        entry = key[sign]
        if entry["xlit"]:
            v = entry["xlit"]
        else:
            canon = entry["canonical"]
            if canon and "-" in canon:
                parts = canon.split("-")[::-1]
                v = "".join(value(p, depth + 1) for p in parts)
            elif canon and canon != sign and canon in key:
                v = value(canon, depth + 1)
            else:
                v = ""
        resolved[sign] = v
        return v

    for s in key:
        value(s)
    return resolved


def key_skeletons() -> dict[str, str]:
    vals = resolve_values(load_key())
    return {s: slp1_skeleton(v) for s, v in vals.items()}


def key_options() -> dict[str, tuple[str, ...]]:
    """Skeleton options per sign. The table's an/aṃ value may be read n or m (decipher.csv lists both)."""
    key = load_key()
    memo: dict[str, tuple[str, ...]] = {}

    def tokens(sign: str, depth: int = 0) -> list[str]:
        if sign not in key or depth > 10:
            return []
        e = key[sign]
        if e["xlit"]:
            return [e["xlit"]]
        canon = e["canonical"]
        if canon and "-" in canon:
            out = []
            for p in canon.split("-")[::-1]:
                out.extend(tokens(p, depth + 1))
            return out
        if canon and canon != sign and canon in key:
            return tokens(canon, depth + 1)
        return []

    for s in key:
        if s in ("000", "999"):
            continue
        opts = [""]
        for tok in tokens(s):
            choices = ["n", "m"] if tok == "an" else [slp1_skeleton(tok)]
            opts = [o + c for o in opts for c in choices]
        memo[s] = tuple(sorted(set(opts)))
    return memo


FREQ_BINS = [(1, 1), (2, 3), (4, 7), (8, 15), (16, 31), (32, 63), (64, 127), (128, 10 ** 9)]


def frequency_strata(texts) -> dict[str, int]:
    cnt = Counter(s for t in texts for s in t)
    out = {}
    for s, c in cnt.items():
        for b, (lo, hi) in enumerate(FREQ_BINS):
            if lo <= c <= hi:
                out[s] = b
                break
    return out


def permuted_options(options: dict, signs: list[str], strata: dict[str, int] | None, rng) -> dict:
    """Permute option tuples among the given signs, within strata when supplied."""
    new = dict(options)
    groups: dict[int, list[str]] = defaultdict(list)
    for s in signs:
        groups[strata[s] if strata is not None else 0].append(s)
    for members in groups.values():
        vals = [options[s] for s in members]
        perm = rng.permutation(len(vals))
        for s, k in zip(members, perm):
            new[s] = vals[k]
    return new


def app_transliteration(signs_reading: list[str], values: dict[str, str]) -> str:
    """Reproduce xlitize(): inherent a between signs and at the end, in reading order."""
    seq = [values[s] for s in signs_reading]
    out = seq[0]
    for v in seq[1:]:
        if not (out.endswith(("i", "u", "an", "as")) or out.endswith(".")) and v not in ("a", "i", "u"):
            out += "a"
        out += "-" + v
    if not out.endswith(("i", "u", "an", "as")):
        out += "a"
    return out


# --------------------------------------------------------------------------- corpus

def load_clean_records() -> list[dict]:
    with open(CLEAN_JSONL, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def unique_texts(min_len: int = 2) -> list[tuple[str, ...]]:
    """Unique reading-order sign sequences of the clean population, in first-seen order."""
    seen = {}
    for r in load_clean_records():
        t = tuple(r["signs_reading_rtl"])
        if len(t) >= min_len and t not in seen:
            seen[t] = r["record_id"]
    return list(seen.keys())


# --------------------------------------------------------------------------- DCS text

def dcs_files(text_name: str) -> list[str]:
    files = sorted(glob.glob(os.path.join(DCS_DIR, text_name, "*.conllu")))
    return files


def dcs_lines(path: str) -> list[str]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("# text = "):
                out.append(line[len("# text = "):].strip())
    return out


def dcs_split() -> dict[str, list[str]]:
    """Every tenth chapter file of each text is held out for evaluation."""
    split = {"train": [], "heldout": []}
    for name in DCS_TEXTS:
        for i, p in enumerate(dcs_files(name)):
            (split["heldout"] if i % 10 == 9 else split["train"]).append(p)
    return split


def dcs_lemmas_and_forms(paths: list[str]) -> tuple[Counter, Counter]:
    lemmas: Counter = Counter()
    forms: Counter = Counter()
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not line or line[0] in "#\n":
                    continue
                cols = line.rstrip("\n").split("\t")
                if len(cols) < 3 or not cols[0].isdigit():
                    continue
                forms[cols[1]] += 1
                lemmas[cols[2]] += 1
    return lemmas, forms


# --------------------------------------------------------------------------- Kneser-Ney

class KneserNey:
    """Interpolated Kneser-Ney over integer symbols 0..V-1 with start padding symbol V."""

    def __init__(self, order: int, vocab: int):
        self.n = order
        self.V = vocab
        self.counts = [defaultdict(Counter) for _ in range(order + 1)]  # counts[k][ctx][w]

    def fit(self, sequences):
        n = self.n
        bos = self.V
        highest = self.counts[n]
        for seq in sequences:
            padded = [bos] * (n - 1) + list(seq)
            for i in range(n - 1, len(padded)):
                ctx = tuple(padded[i - n + 1:i])
                highest[ctx][padded[i]] += 1
        # continuation counts for lower orders: number of distinct left extensions
        for k in range(n - 1, 0, -1):
            upper = self.counts[k + 1]
            lower = self.counts[k]
            for ctx, row in upper.items():
                sub = ctx[1:]
                for w in row:
                    lower[sub][w] += 1
        self._finalize()
        return self

    def _finalize(self):
        self.discount = {}
        for k in range(1, self.n + 1):
            cc = Counter()
            for row in self.counts[k].values():
                for c in row.values():
                    if c <= 2:
                        cc[c] += 1
            n1, n2 = cc[1], cc[2]
            self.discount[k] = n1 / (n1 + 2 * n2) if n1 + n2 > 0 else 0.5
        self.totals = [dict() for _ in range(self.n + 1)]
        self.types = [dict() for _ in range(self.n + 1)]
        for k in range(1, self.n + 1):
            for ctx, row in self.counts[k].items():
                self.totals[k][ctx] = sum(row.values())
                self.types[k][ctx] = len(row)
        self._cache = {}

    def prob(self, ctx: tuple, w: int) -> float:
        """P(w | ctx) where len(ctx) == n-1."""
        return self._p(len(ctx) + 1, ctx, w)

    def _p(self, k: int, ctx: tuple, w: int) -> float:
        key = (k, ctx, w)
        c = self._cache.get(key)
        if c is not None:
            return c
        if k == 1:
            row = self.counts[1].get((), Counter())
            tot = self.totals[1].get((), 0)
            d = self.discount[1]
            uniform = 1.0 / self.V
            if tot == 0:
                val = uniform
            else:
                val = max(row.get(w, 0) - d, 0) / tot + d * self.types[1][()] / tot * uniform
        else:
            tot = self.totals[k].get(ctx, 0)
            lower = self._p(k - 1, ctx[1:], w)
            if tot == 0:
                val = lower
            else:
                d = self.discount[k]
                row = self.counts[k][ctx]
                val = max(row.get(w, 0) - d, 0) / tot + d * self.types[k][ctx] / tot * lower
        self._cache[key] = val
        return val

    def logprob_seq(self, seq) -> float:
        bos = self.V
        padded = [bos] * (self.n - 1) + list(seq)
        lp = 0.0
        for i in range(self.n - 1, len(padded)):
            lp += math.log2(self.prob(tuple(padded[i - self.n + 1:i]), padded[i]))
        return lp

    def dense_table(self) -> np.ndarray:
        """log2 P(w | ctx) for every padded context, indexed base (V+1)."""
        base = self.V + 1
        m = self.n - 1
        table = np.empty((base ** m, self.V), dtype=np.float64)
        for idx in range(base ** m):
            digits = []
            x = idx
            for _ in range(m):
                digits.append(x % base)
                x //= base
            ctx = tuple(reversed(digits))
            # contexts with a real symbol before a start symbol never occur; fill harmlessly
            for w in range(self.V):
                table[idx, w] = math.log2(self.prob(ctx, w))
        return table


def encode(skeleton: str) -> list[int]:
    return [CID[c] for c in skeleton]
