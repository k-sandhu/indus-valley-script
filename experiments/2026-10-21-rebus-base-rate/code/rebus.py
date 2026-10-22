"""Parpola's homophone procedure as a program, and the measurements of the rebus base-rate study.

The procedure (Parpola 2010, pp. 14-28): a picture word and a target meaning are
homophones when their forms match with vowel and consonant length free; both
words must be attested in at least two subgroups of the family; compounds
attested in Old Tamil may be used. Readings must interlock: a compound X-W2 and a
compound W1-X with the same member X.

Forms are segmented per language, normalised by a ladder of merges and compared
as tuples of segment classes:

    T0  the stated rule: vowel length and gemination free (merge step L)
    T0s T0 plus further merges, for each language, until its per-segment
        collision probability reaches that of Tamil under T0 (the inventory scaling)
    T1s T0s plus the stem tolerance Parpola uses in practice: a final -m after a
        vowel and then a final vowel are dropped while at least two segments remain
        (vaṭam ~ vaṭa, veḷ ~ veḷi, muruku ~ muruka-)

In the Tamil Lexicon compound search, members also receive their sandhi bases
(veṇ- < veḷ, vaṭa- < vaṭam, muruka- < murukaṉ).
"""

import csv
import functools
import hashlib
import io
import json
import math
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate"
SRC = RAW / "sources-v1"
DER = RAW / "derived-v1"

# ---------------------------------------------------------------- segmentation

VOWEL_BASES = set("aeiouəɛɔæɨʉɯʊɪʌɑɒøœ")   # "y" is the palatal glide in every transcription used here
LONG_MAP = {"ā": "a", "ī": "i", "ū": "u", "ē": "e", "ō": "o", "ṝ": "ṛ", "ḹ": "ḷ", "ȳ": "y"}


def _strip_accents(s):
    """Remove Vedic accent marks from vowels (and vocalic r, l) but keep the acute of ś."""
    out = []
    base = ""
    for c in unicodedata.normalize("NFD", s):
        if unicodedata.combining(c):
            if c in "́̀́̀̋̏" and base in "aeiourlAEIOURL":
                continue
        else:
            base = c
        out.append(c)
    return unicodedata.normalize("NFC", "".join(out))


def seg_indic(form):
    """Segment IAST-style romanisation (DEDR, Tamil Lexicon, CDIAL)."""
    s = _strip_accents(form.lower())
    s = s.replace("r̤", "ḻ").replace("ṁ", "ṃ").replace("ŭ", "u").replace("ů", "u").replace("ĕ", "e").replace("ŏ", "o")
    s = re.sub(r"[^a-zāīūēōṛṝḷḹṃḥśṣṅñṭḍṇḻḷṟṉḵ·ïëüöäɛəɔ]", "", s)
    out = []
    i = 0
    while i < len(s):
        two = s[i:i + 2]
        if two in ("ai", "au"):
            out.append(two)
            i += 2
            continue
        if len(two) == 2 and two[1] == "h" and two[0] in "kgcjṭḍtdpb":
            out.append(two)
            i += 2
            continue
        c = s[i]
        if c == "·":                      # length mark after a vowel (Kota, Toda)
            if out:
                out[-1] = out[-1] + "ː"
            i += 1
            continue
        out.append(c)
        i += 1
    return out


def seg_ipa(form):
    """Segment IPA-like transcriptions (Munda): base character plus diacritics and modifiers."""
    s = unicodedata.normalize("NFD", form.strip().lower())
    s = re.sub(r"[\s\-‐-―\(\)\*\[\]/~=.,;!?0-9ˈˌ]", "", s)
    out = []
    for c in s:
        if out and (unicodedata.combining(c) or c in "ːˑ:ʰʱʲʷˀ'’ʼ"):
            out[-1] += c
        else:
            out.append(c)
    return [unicodedata.normalize("NFC", x) for x in out]


def seg_sumerian(cf):
    s = cf.lower().replace("ĝ", "ŋ").replace("ḫ", "h").replace("ʾ", "ʔ")
    return [c for c in s if c.isalpha() or c == "ʔ"]


def is_vowel(tok):
    base = unicodedata.normalize("NFD", tok)[:1]
    return tok in ("ai", "au") or base in VOWEL_BASES or tok in LONG_MAP or tok[:1] in "āīūēō"


# ---------------------------------------------------------------- merge ladder

def step_L(tok):
    t = tok.replace("ː", "").replace(":", "").replace("ˑ", "")
    t = unicodedata.normalize("NFD", t).replace("̄", "")
    t = unicodedata.normalize("NFC", t)
    return LONG_MAP.get(t, t)


def step_A(tok):
    if len(tok) == 2 and tok[1] == "h" and tok[0] in "kgcjṭḍtdpb":
        tok = tok[0]
    return "".join(c for c in tok if c not in "ʰʱʲʷˀ'’ʼ")


VOICE = {"b": "p", "d": "t", "g": "k", "ɡ": "k", "j": "c", "ɟ": "c", "ḍ": "ṭ", "ɖ": "ʈ", "z": "s", "ʒ": "ʃ",
         "ž": "š", "ɣ": "x", "ǰ": "č", "ʑ": "ɕ", "ɦ": "h", "β": "f", "ð": "θ"}
RETRO = {"ṭ": "t", "ʈ": "t", "ṇ": "n", "ɳ": "n", "ṣ": "s", "ʂ": "s", "ḷ": "l", "ɭ": "l", "ɽ": "r", "ḻ": "l",
         "ṟ": "r", "ṉ": "n", "ʐ": "z", "ɻ": "r"}
SIBIL = {"ś": "s", "ṣ": "s", "š": "s", "ʃ": "s", "ɕ": "s", "ç": "s", "ʂ": "s"}
NASAL = {"ṅ": "n", "ñ": "n", "ṇ": "n", "ṉ": "n", "ɲ": "n", "ŋ": "n", "ɳ": "n", "ṃ": "n"}
LIQUID = {"l": "r", "ḷ": "r", "ḻ": "r", "ṟ": "r", "ɾ": "r", "ɭ": "r", "ɽ": "r", "ɹ": "r", "ʎ": "r"}
VHEIGHT = {"e": "i", "o": "u", "ɛ": "i", "ɔ": "u", "ə": "a", "æ": "a", "ɨ": "i", "ʊ": "u", "ɪ": "i", "ʌ": "a",
           "ɑ": "a", "ɒ": "u", "ï": "i", "ë": "i", "ö": "u", "ü": "u", "ä": "a"}


def _map_base(table):
    def f(tok):
        if tok in table:
            return table[tok]
        d = unicodedata.normalize("NFD", tok)
        if d and d[0] in table and len(tok) > 1 and tok not in ("ai", "au"):
            return unicodedata.normalize("NFC", table[d[0]] + d[1:])
        return tok
    return f


def step_R(tok):
    """Retroflex and alveolar with dental: map the base and drop dental or apical diacritics."""
    tok = _map_base(RETRO)(tok)
    d = unicodedata.normalize("NFD", tok)
    if len(d) > 1 and d[0] not in VOWEL_BASES:
        d = d[0] + "".join(c for c in d[1:] if c not in "̪̺̟")
    return unicodedata.normalize("NFC", d)


LADDER = [("L", step_L), ("A", step_A), ("V", _map_base(VOICE)), ("R", step_R),
          ("S", _map_base(SIBIL)), ("N", _map_base(NASAL)), ("Q", _map_base(LIQUID)), ("E", _map_base(VHEIGHT))]
LADDER_NAMES = [n for n, _ in LADDER]


def normalise(tokens, steps):
    toks = list(tokens)
    for name, fn in LADDER:
        if name in steps:
            toks = [fn(t) for t in toks]
            toks = [t for t in toks if t]
    out = []
    for t in toks:                         # gemination free (and identical vowel sequences)
        if out and out[-1] == t:
            continue
        out.append(t)
    return tuple(out)


def stem(norm):
    """T1: drop a final -m after a vowel, then a final vowel, keeping at least two segments."""
    t = list(norm)
    if len(t) >= 4 and t[-1] == "m" and is_vowel(t[-2]):
        t.pop()
    if len(t) >= 3 and is_vowel(t[-1]):
        t.pop()
    return tuple(t)


def collision(forms):
    c = Counter(tok for f in forms for tok in f)
    n = sum(c.values())
    return sum((v / n) ** 2 for v in c.values()) if n else float("nan")


def scale_steps(token_forms, target):
    """Smallest prefix of the ladder whose per-segment collision probability reaches the target."""
    trail = []
    for k in range(1, len(LADDER) + 1):
        steps = LADDER_NAMES[:k]
        c = collision([normalise(f, steps) for f in token_forms])
        trail.append({"steps": "".join(steps), "collision": c})
        if c >= target:
            return steps, trail
    return LADDER_NAMES, trail


# ---------------------------------------------------------------- glosses

GLOSS_SPLIT = re.compile(r"[,;:]")


def gloss_items(text):
    items = set()
    text = re.sub(r"\([^()]*\)", " ", text or "")
    text = re.sub(r"\[[^\[\]]*\]", " ", text)
    for part in GLOSS_SPLIT.split(text):
        p = part.strip().lower().strip(" .?!'\"")
        p = re.sub(r"^(?:to be |to |the |be )", "", p)
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            items.add(p)
    return items


def matches(key, items):
    return key in items or key + "s" in items or key + "es" in items


# ---------------------------------------------------------------- lexicons
# A lexeme: {"id", "forms": [token tuples], "items": set of gloss items, "attested": bool,
#            "weight": number used to choose one lexeme per concept, "cids": optional Concepticon IDs}

DEDR_LANG_ORDER = ["Ta", "Ma", "Ir", "Ko", "To", "Ka", "Koḍ", "Tu", "Te", "Kol", "Nk", "Pa", "Ga", "Go", "Konḍa",
                   "Pe", "Manḍ", "Kui", "Kuwi", "Kur", "Malt", "Br"]


def load_dedr(strict=False):
    rows = [json.loads(l) for l in (DER / "dedr-entries.jsonl").open(encoding="utf-8")]
    lex = []
    for r in rows:
        groups = r["groups"]
        if not groups:
            continue
        head_lang = "Ta" if any(g["lang"] == "Ta" for g in groups) else groups[0]["lang"]
        attested = len(r["subgroups"]) >= 2
        if strict:
            for k, g in enumerate(groups):
                if g["lang"] != head_lang:
                    continue
                lex.append({"id": f"DEDR{r['num']}.{k}", "forms": [tuple(seg_indic(f)) for f in g["forms"]],
                            "items": gloss_items(g["gloss"]), "attested": attested, "weight": len(r["langs"]),
                            "head_lang": head_lang, "entry": r["num"]})
            continue
        head = next(g for g in groups if g["lang"] == head_lang)
        items = set()
        for g in groups:
            items |= gloss_items(g["gloss"])
        lex.append({"id": f"DEDR{r['num']}", "forms": [tuple(seg_indic(f)) for f in head["forms"]],
                    "items": items, "attested": attested, "weight": len(r["langs"]), "head_lang": head_lang,
                    "entry": r["num"], "tamil_forms": [f for g in groups if g["lang"] == "Ta" for f in g["forms"]]})
    return [x for x in lex if any(x["forms"])]


def load_cdial():
    rows = [json.loads(l) for l in (DER / "cdial-entries.jsonl").open(encoding="utf-8")]
    lex = []
    for r in rows:
        items = set()
        for g in r["glosses"]:
            items |= gloss_items(g)
        forms = [tuple(seg_indic(f)) for f in r["head_forms"]]
        lex.append({"id": f"CDIAL{r['num']}", "forms": [f for f in forms if f], "items": items,
                    "attested": len(r["subgroups"]) >= 2, "weight": len(r["langs"]), "entry": r["num"]})
    return [x for x in lex if x["forms"]]


EPSD_POS = {"N", "V/t", "V/i", "AJ", "AV", "NU"}


def load_epsd2():
    lex = []
    for line in (DER / "epsd2-lemmas.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        cf = r.get("cf") or ""
        if r.get("pos") not in EPSD_POS or not cf or re.search(r"[A-Z0-9₀-₉.\s@×&|+]", cf):
            continue
        items = set()
        for s in r.get("senses") or []:
            items |= gloss_items(s.get("mng") or "")
        if not items:
            items = gloss_items(r.get("gw") or "")
        icount = int(r.get("icount") or 0)
        lex.append({"id": r["id"], "forms": [tuple(seg_sumerian(cf))], "items": items,
                    "attested": icount >= 2, "weight": icount, "cf": cf})
    return [x for x in lex if x["forms"][0]]


MUNDA_NORTH = {"sa", "mu", "ho", "kw", "ko"}
MUNDA_SOUTH = {"kh", "ju", "so", "go", "gu", "gt", "re"}


def load_munda():
    path = SRC / "munda" / "pMunda_cognate_set_2019-08-29.csv"
    text = path.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    lex = []
    for row in reader:
        rec = dict(zip(header, row))            # the second 'gloss' column repeats the first
        langs = {h.split("_")[0] for h, v in zip(header, row)
                 if h.endswith("_form") and not h.startswith("mkcd") and v and v != "—"}
        north, south = langs & MUNDA_NORTH, langs & MUNDA_SOUTH
        form = None
        for lang in ("sa", "mu", "ho"):
            v = rec.get(f"{lang}_form")
            if v and v != "—":
                form = v.split(",")[0].split(";")[0].strip()
                break
        if not form:
            continue
        lex.append({"id": rec["ID"], "forms": [tuple(seg_ipa(form))], "items": gloss_items(row[1]),
                    "attested": bool(north and south), "weight": len(langs), "pmunda": rec.get("pmunda")})
    return [x for x in lex if x["forms"][0]]


BURUSHASKI = {"Hunza": ["Hussainabad", "Murtazabad", "Haiderabad", "Ganish", "NazimabadUpperSust"],
              "Nagar": ["UyumNagar", "Hoper"], "Yasin": ["YasinCenter", "ThuiYasin"]}


def _backstrom_tables():
    z = zipfile.ZipFile(SRC / "backstrom" / "backstromnorthernpakistan-v1.1.zip")
    base = next(n for n in z.namelist() if n.endswith("cldf/forms.csv")).rsplit("/", 1)[0]
    forms = list(csv.DictReader(io.TextIOWrapper(z.open(base + "/forms.csv"), encoding="utf-8")))
    params = {p["ID"]: p for p in csv.DictReader(io.TextIOWrapper(z.open(base + "/parameters.csv"), encoding="utf-8"))}
    return forms, params


def clts_segments(text):
    """Lexibank segments: keep the target of 'source/target' pairs, drop stress and boundary marks."""
    out = []
    for tok in text.split():
        tok = tok.split("/")[-1].replace("ˈ", "").replace("ˌ", "")
        if tok and tok not in ("+", "_", "#"):
            out.append(unicodedata.normalize("NFC", tok))
    return tuple(out)


def load_burushaski():
    forms, params = _backstrom_tables()
    dialect_of = {v: d for d, vs in BURUSHASKI.items() for v in vs}
    counts = Counter(f["Language_ID"] for f in forms if f["Language_ID"] in BURUSHASKI["Hunza"])
    rep = sorted(counts, key=lambda v: (-counts[v], v))[0]
    by_concept = defaultdict(lambda: {"dialects": set(), "rep": []})
    for f in forms:
        d = dialect_of.get(f["Language_ID"])
        if not d:
            continue
        cid = params[f["Parameter_ID"]].get("Concepticon_ID") or ""
        if not cid:
            continue
        by_concept[cid]["dialects"].add(d)
        if f["Language_ID"] == rep and f["Segments"]:
            by_concept[cid]["rep"].append(clts_segments(f["Segments"]))
    lex = []
    for cid, v in by_concept.items():
        if not v["rep"]:
            continue
        lex.append({"id": f"BUR{cid}", "forms": sorted(set(v["rep"])), "items": set(), "cids": {cid},
                    "attested": len(v["dialects"]) >= 2, "weight": len(v["dialects"])})
    return lex, rep


# ---------------------------------------------------------------- single-homophone measurement

def concept_index(lex, concepts):
    """Lexemes matched to each concept (attested lexemes only)."""
    idx = {}
    for c in concepts:
        hits = []
        for e in lex:
            if not e["attested"]:
                continue
            if e.get("cids") is not None:
                if c["id"] in e["cids"]:
                    hits.append(e)
            elif matches(c["key"], e["items"]):
                hits.append(e)
        if hits:
            idx[c["id"]] = hits
    return idx


def pair_matrix(idx, pics, names, norm, one_per_concept=False):
    """Boolean matrices (any homophone, homonym from a different lexeme) over evaluable pairs."""
    def forms_of(cid):
        hits = idx[cid]
        if one_per_concept:
            hits = [max(hits, key=lambda e: (e["weight"], e["id"]))]
            return {norm(hits[0]["forms"][0]): {hits[0]["id"]}}
        d = defaultdict(set)
        for e in hits:
            for f in e["forms"]:
                if f:
                    d[norm(f)].add(e["id"])
        return d

    P = [c["id"] for c in pics if c["id"] in idx]
    M = [c["id"] for c in names if c["id"] in idx]
    FP = {p: forms_of(p) for p in P}
    FM = {m: forms_of(m) for m in M}
    any_m = [[False] * len(M) for _ in P]
    hom_m = [[False] * len(M) for _ in P]
    examples = []
    for i, p in enumerate(P):
        fp = FP[p]
        for j, m in enumerate(M):
            fm = FM[m]
            shared = fp.keys() & fm.keys()
            if not shared:
                continue
            any_m[i][j] = True
            for f in shared:
                if fp[f] != fm[f] or len(fp[f] | fm[f]) > 1:
                    hom_m[i][j] = True
                    break
            if len(examples) < 4000:
                examples.append({"picture": p, "name": m, "forms": ["".join(f) for f in sorted(shared)][:3],
                                 "lexemes": sorted(set().union(*(fp[f] | fm[f] for f in shared)))[:6]})
    return P, M, any_m, hom_m, examples


# ---------------------------------------------------------------- Tamil Lexicon compounds

SANDHI_FIRST = {"ṇ": ["ḷ"], "ṉ": ["l"], "ṅ": ["m"], "ñ": ["m"], "n": ["m"], "ṭ": ["ḷ"], "ṟ": ["l"]}


def sandhi_bases(member):
    """Base forms of a compound's first member: veṇ -> veḷ, vaṭa -> vaṭam, muruka -> murukaṉ."""
    out = {member}
    if member.endswith("a"):
        out |= {member + "m", member + "ṉ"}
    last = member[-1:]
    for alt in SANDHI_FIRST.get(last, []):
        out.add(member[:-1] + alt)
    return out


@functools.lru_cache(maxsize=None)
def tl_norm(form, tol):
    toks = normalise(seg_indic(form), ["L"])
    return stem(toks) if tol == "T1s" else toks


class Compounds:
    """Two-member compounds of the Tamil Lexicon, indexed by the T1 stem of each member."""

    def __init__(self, entries):
        self.c2 = []
        for e in entries:
            m = e["members"]
            if len(m) == 2 and all(len(x) >= 1 for x in m):
                self.c2.append(e)
        self.first = defaultdict(list)
        self.last = defaultdict(list)
        for k, e in enumerate(self.c2):
            m1, m2 = e["members"]
            for st in {tl_norm(b, "T1s") for b in sandhi_bases(m1)}:
                self.first[st].append(k)
            self.last[tl_norm(m2, "T1s")].append(k)

    def anchor(self, word):
        return tl_norm(word, "T1s")

    def prod_first(self, word):
        return len(self.first.get(self.anchor(word), ()))

    def prod_last(self, word):
        return len(self.last.get(self.anchor(word), ()))

    def A(self, w1):
        return [self.c2[k] for k in self.first.get(self.anchor(w1), ())]

    def B(self, w2):
        return [self.c2[k] for k in self.last.get(self.anchor(w2), ())]


def shared_members(A, B, tol, exclude):
    """Members X with W1-X in A and X-W2 in B, compared under the tolerance."""
    na = defaultdict(set)
    for e in A:
        x = e["members"][1]
        na[tl_norm(x, tol)].add(e["translit"])
    nb = defaultdict(set)
    for e in B:
        y = e["members"][0]
        for b in sandhi_bases(y):
            nb[tl_norm(b, tol)].add(e["translit"])
    keys = (na.keys() & nb.keys()) - exclude
    return {"".join(k): {"w1_compounds": sorted(na[k]), "w2_compounds": sorted(nb[k])} for k in sorted(keys)}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [(c - r) / d, (c + r) / d]
