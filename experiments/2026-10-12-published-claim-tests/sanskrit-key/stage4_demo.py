"""Stage 4: what the readability criterion admits under a random key.

One frequency-stratified permutation of the key, fixed by seed before inspection, is applied to the
longest unique texts. Each skeleton is segmented into attested DCS noun, adjective and verb lemmas
(most frequent lemma per skeleton; the score prefers longer, frequent stems) with an optional ending,
and each stem is glossed from Monier-Williams. The same procedure is applied to the key itself.
These are controls, not readings.
"""
import json
import math
import os
import re
import unicodedata
from collections import Counter

import numpy as np

from common import (HERE, MW_TXT, dcs_split, frequency_strata, iast_skeleton, key_options,
                    load_clean_records, permuted_options, unique_texts)

SEED = 20261012 + 424242
ENDINGS = {"": "", "s": "-ḥ", "m": "-m", "n": "-n", "y": "-ya", "t": "-t", "sy": "-sya"}
N_SHOW = 12

IAST2SLP = [("ai", "E"), ("au", "O"), ("kh", "K"), ("gh", "G"), ("ch", "C"), ("jh", "J"), ("ṭh", "W"),
            ("ḍh", "Q"), ("th", "T"), ("dh", "D"), ("ph", "P"), ("bh", "B"), ("ā", "A"), ("ī", "I"),
            ("ū", "U"), ("ṛ", "f"), ("ṝ", "F"), ("ḷ", "x"), ("ḹ", "X"), ("ṃ", "M"), ("ḥ", "H"), ("ṅ", "N"),
            ("ñ", "Y"), ("ṭ", "w"), ("ḍ", "q"), ("ṇ", "R"), ("ś", "S"), ("ṣ", "z")]
DROP_TAGS = ("s", "lex", "ab", "ls", "hom", "lang", "etym", "gk", "bot", "zoo", "s1")


def iast_to_slp1(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    for a, b in IAST2SLP:
        s = s.replace(a, b)
    return s


def clean_gloss(text: str) -> str | None:
    if "¦" in text:
        text = text.split("¦", 1)[1]
    for tag in DROP_TAGS:
        text = re.sub(r"<" + tag + r"[^>]*>.*?</" + tag + r">", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    for _ in range(3):
        text = re.sub(r"\([^()]*\)", "", text)
        text = re.sub(r"\[[^\[\]]*\]", "", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;.")
    pieces = [x.strip(" ,.") for x in text.split(";")]
    pieces = [x for x in pieces if re.search(r"[a-z]{3,}", x) and not x.startswith(("see", "=", "cf", "N. of"))]
    return pieces[0][:60] if pieces else None


def mw_glosses() -> dict[str, str]:
    out: dict[str, str] = {}
    pat = re.compile(r"<k1>([^<]+)<k2>")
    cur = None
    body: list[str] = []
    with open(MW_TXT, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<L>"):
                m = pat.search(line)
                cur = m.group(1) if m else None
                body = []
            elif line.startswith("<LEND>"):
                if cur and cur not in out:
                    g = clean_gloss(" ".join(body))
                    if g:
                        out[cur] = g
                cur = None
            elif cur:
                body.append(line.strip())
    return out


def content_lemmas(paths) -> Counter:
    """Lemma counts restricted to nouns, adjectives and verbs."""
    out: Counter = Counter()
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not line or line[0] in "#\n":
                    continue
                cols = line.rstrip("\n").split("\t")
                if len(cols) > 3 and cols[0].isdigit() and cols[3] in ("NOUN", "ADJ", "VERB"):
                    out[cols[2]] += 1
    return out


def best_segmentation(sk: str, lex: dict):
    """Maximize the sum of log lemma count + 4 per consonant - 14 per stem; optional final ending."""
    L = len(sk)
    NEG = -1e18
    best = [NEG] * (L + 1)
    back: list = [None] * (L + 1)
    best[0] = 0.0
    for i in range(1, L + 1):
        for j in range(max(0, i - 8), i):
            w = sk[j:i]
            if w in lex and best[j] > NEG:
                v = best[j] + math.log(lex[w][1]) + 4.0 * len(w) - 14.0
                if v > best[i]:
                    best[i] = v
                    back[i] = j
    cand = []
    for e in ENDINGS:
        j = L - len(e)
        if j > 0 and sk[j:] == e and best[j] > NEG:
            cand.append((best[j] - (0.5 if e else 0.0), j, e))
    if not cand:
        return None
    _, j, e = max(cand)
    parts = []
    while j > 0:
        i = back[j]
        parts.append(sk[i:j])
        j = i
    return parts[::-1], e


def main():
    split = dcs_split()
    lemmas = content_lemmas(split["train"] + split["heldout"])
    lex: dict[str, tuple[str, int]] = {}
    for lem, c in lemmas.items():
        sk = iast_skeleton(lem)
        if sk and c >= 3 and (sk not in lex or c > lex[sk][1]):
            lex[sk] = (lem, c)
    gl = mw_glosses()

    texts = unique_texts(min_len=2)
    first_id = {}
    for r in load_clean_records():
        t = tuple(r["signs_reading_rtl"])
        first_id.setdefault(t, (r["record_id"], r.get("source_cisi")))
    longest = sorted(texts, key=lambda t: (-len(t), t))[:N_SHOW]
    options = key_options()
    signs = sorted({s for t in texts for s in t})
    strata = frequency_strata(texts)
    rand = permuted_options(options, signs, strata, np.random.default_rng(SEED))

    def render(t, opts):
        sk = "".join(opts[s][0] for s in t)
        seg = best_segmentation(sk, lex)
        if seg is None:
            return {"skeleton": sk, "reading": None, "glosses": None}
        parts, e = seg
        words = [lex[p][0] for p in parts]
        glosses = [gl.get(iast_to_slp1(w), "?") for w in words]
        return {"skeleton": sk, "reading": "-".join(words) + ENDINGS[e], "glosses": glosses}

    rows = []
    for t in longest:
        rid, cisi = first_id[t]
        rows.append({"record_id": rid, "cisi": cisi, "signs": len(t),
                     "random_key": render(t, rand), "published_key": render(t, options)})
    readable = sum(1 for r in rows if r["random_key"]["reading"])
    out = {"seed": SEED, "lexicon_entries": len(lex), "readable_random_key": readable, "shown": len(rows),
           "lexicon": "most frequent DCS noun/adjective/verb lemma per skeleton (count >= 3); MW first gloss",
           "rows": rows}
    os.makedirs(os.path.join(HERE, "stage4"), exist_ok=True)
    with open(os.path.join(HERE, "stage4", "demo.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    lines = ["| Record | Signs | Random-key segmentation | Monier-Williams glosses |", "|---|---|---|---|"]
    for r in rows:
        rk = r["random_key"]
        g = " / ".join(rk["glosses"]) if rk["glosses"] else "no segmentation"
        lines.append(f"| {r['cisi'] or r['record_id']} | {r['signs']} | {rk['reading'] or '-'} | {g} |")
    with open(os.path.join(HERE, "stage4", "demo.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("readable", readable, "of", len(rows), "lexicon", len(lex))


if __name__ == "__main__":
    main()
