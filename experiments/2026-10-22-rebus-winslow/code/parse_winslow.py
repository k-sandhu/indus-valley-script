"""Parse the DSAL pages of Winslow's Tamil-English dictionary (1862) into JSONL.

Winslow arranges derivatives and compounds under their primitives: a principal
headword in large type gives its Tamil form and a romanisation, and the
compounds formed on it follow as run-on sub-entries (<p2>) in Tamil script only,
with no romanisation and no mark at the junction of the members. A compound is
usually nested under its first member; compounds "of a genus and species" are
nested under the genus, their last member (Directions for using the Lexicon,
p. xi). Some principals are compounds themselves and name their members in a
bracketed etymology, "[ex அகம், inside, et பகை.]".

We therefore recover two-member compounds in three ways:

  first   a sub-entry that begins with a sandhi form of its principal, followed
          by a word: añcaṉa-k-kalikkam under añcaṉam
  second  a sub-entry that ends with its principal, preceded by a word:
          cāḻai-y-akatti under akatti
  ety     a principal whose etymology names two Tamil members and whose form
          splits into them by the same junction rule

The member that is not the principal must be a principal headword of the
dictionary, as written (second member) or in one of its sandhi forms as a first
member (first_variants: mara- < maram, veṇ- < veḷ, āṭṭu- < āṭu, kall- < kal).
The junction rule removes the sandhi doubling of an initial stop (-k-k-) and the
glides y and v between vowels, and keeps the members as written, as the Tamil
Lexicon's hyphenation does ("veṇ-mīṉ"), so that rebus.sandhi_bases and the
Compounds class of the 2026-10-21 study apply to them unchanged.

    python -I experiments/2026-10-22-rebus-winslow/code/parse_winslow.py
"""

import glob
import hashlib
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "code"))
import parse_tamil_lex  # noqa: E402
import rebus  # noqa: E402

RAW = ROOT / "data" / "raw" / "2026-10-22-rebus-winslow"
PAGES = RAW / "sources-v1" / "winslow"
OUT = RAW / "derived-v1" / "winslow-entries.jsonl"

DIV_RE = re.compile(r"<div>\s*(.*?)</div>", re.S)
P2_RE = re.compile(r"<p2>(.*?)</p2>", re.S)
# Winslow gives every letter, ending, particle and prefix its own principal entry, and
# its first sense names it as such ("A syllabic letter composed of", "The eleventh
# vowel"; without a part of speech: "An increment", "A Sanscrit prefix in Tamil").
# These grammatical entries are not words of the compound vocabulary.
LETTER_RE = re.compile(
    r"^(?:s\.\s*)?(?:A|An|The)\s+(?:\w+\s+){0,3}(?:syllabic|compound)\s+letter"
    r"|^(?:s\.\s*)?(?:A|An|The)\s+(?:\w+\s+)?letter\s+(?:composed|compounded|formed|consisting)"
    r"|^(?:A|An|The)\s+(?:short\s+|long\s+)?letter,?\s+similar"
    r"|^(?:A|An|The)\s+(?:\w+\s+){0,3}(?:vowel|consonant)\b"
    r"|^(?:Short|Long)\s+\w+,\s+the\s+\w+\s+vowel", re.I)
PARTICLE_RE = re.compile(
    r"^(?:part\.\s*|pron\.\s*)?(?:(?:A|An|The)\s+)?(?:\w+\s+){0,2}"
    r"(?:termination|increment|particle|affix|suffix|prefix|expletive|sign\s+of)s?\b", re.I)
# origin marks of non-Dravidian loans; Winslow's asterisk marks Sanskrit primitives
FOREIGN_RE = re.compile(r"\((?:Hin|Hind|Ar|Pers|For|Mah|St|Sans|Sa|Port|Eng|Dut|Fr|Lat|Mal\. & Hin)\.?\)", re.I)

# ---------------------------------------------------------------- transliteration

CONS = {"க": "k", "ங": "ṅ", "ச": "c", "ஞ": "ñ", "ட": "ṭ", "ண": "ṇ", "த": "t", "ந": "n", "ப": "p", "ம": "m",
        "ய": "y", "ர": "r", "ல": "l", "வ": "v", "ழ": "ḻ", "ள": "ḷ", "ற": "ṟ", "ன": "ṉ", "ஜ": "j", "ஷ": "ṣ",
        "ஸ": "s", "ஹ": "h", "ஶ": "ś"}
VOWELS = {"அ": "a", "ஆ": "ā", "இ": "i", "ஈ": "ī", "உ": "u", "ஊ": "ū", "எ": "e", "ஏ": "ē", "ஐ": "ai",
          "ஒ": "o", "ஓ": "ō", "ஔ": "au"}
SIGNS = {"ா": "ā", "ி": "i", "ீ": "ī", "ு": "u", "ூ": "ū", "ெ": "e", "ே": "ē", "ை": "ai", "ொ": "o",
         "ோ": "ō", "ௌ": "au"}
VIRAMA = "்"


def translit(tamil):
    """Romanise Tamil script in the DSAL scheme (ṉ, ṟ, ḻ, ai, au); other characters are dropped."""
    s = unicodedata.normalize("NFC", tamil)
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if c in CONS:
            if nxt == VIRAMA:
                out.append(CONS[c])
                i += 2
            elif nxt in SIGNS:
                out.append(CONS[c] + SIGNS[nxt])
                i += 2
            else:
                out.append(CONS[c] + "a")
                i += 1
            continue
        if c in VOWELS:
            v = VOWELS[c]
            if out and out[-1].endswith("a") and v in ("i", "u"):
                v = {"i": "ï", "u": "ü"}[v]            # hiatus, kept apart from the diphthongs ai and au
            out.append(v)
        elif c == "ஃ":
            out.append("ḵ")
        elif c.isspace():
            out.append(" ")
        i += 1
    return re.sub(r"\s+", " ", "".join(out)).strip()


# ---------------------------------------------------------------- junction rule

VOWEL_CHARS = "aāiīuūeēoōïü"
STOPS = "kctp"
Y_AFTER = ("i", "ī", "e", "ē", "ai")
V_AFTER = ("a", "ā", "u", "ū", "o", "ō")
SHORT_V = "aiueo"
# nasal + stop clusters that harden to a geminate stop in a first member (maruntu > maruttu-)
HARDEN = {"ntu": "ttu", "mpu": "ppu", "ṅku": "kku", "ñcu": "ccu", "ṇṭu": "ṭṭu", "ṉṟu": "ṟṟu"}


def key(s):
    """Comparison key: the DSAL text writes every initial e as ē (ஏ), so e and ē, o and ō are merged."""
    return s.replace("ē", "e").replace("ō", "o")


def stem(form):
    return rebus.tl_norm(form, "T1s")


def has_vowel(s):
    return any(c in VOWEL_CHARS for c in s)


def syllables(s):
    return len(re.findall(r"ai|au|[aāiīuūeēoōïü]", s))


def first_variants(w):
    """Surface forms of a word w as the first member of a compound, by the common sandhi rules."""
    out = {w}
    if len(w) >= 3 and w.endswith("m") and w[-2] in VOWEL_CHARS:
        out |= {w[:-1], w[:-1] + "ṅ", w[:-1] + "ñ", w[:-1] + "n"}          # mara-, kuḷaṅ-
        if w.endswith("am"):
            out |= {w[:-2] + "att", w[:-2] + "attu"}                         # akatt- < akam
    if len(w) >= 3 and w.endswith("u") and w[-2] not in VOWEL_CHARS:
        out.add(w[:-1])                                                    # añc- < añcu before a vowel
        if w[-2] in "ṭṟ" and w[-3] in VOWEL_CHARS:
            out |= {w[:-2] + w[-2] * 2 + "u", w[:-2] + w[-2] * 2}          # āṭṭu- < āṭu
        for a, b in HARDEN.items():
            if w.endswith(a):
                out |= {w[:-3] + b, w[:-3] + b[:-1]}
    last = w[-1:]
    if last == "ḷ":
        out |= {w[:-1] + "ṭ", w[:-1] + "ṇ"}                                  # veṇ- < veḷ
    elif last == "l":
        out |= {w[:-1] + "ṟ", w[:-1] + "ṉ"}
    elif last == "ṇ":
        out.add(w[:-1] + "ṭ")
    elif last == "ṉ":
        out.add(w[:-1] + "ṟ")                                              # mīṟ- < mīṉ
        if w.endswith("aṉ") and len(w) >= 4:
            out.add(w[:-1])                                                # muruka- < murukaṉ
    if re.fullmatch(r"[^aāiīuūeēoō]?[aiueo][^aāiīuūeēoō]", w) and last not in VOWEL_CHARS:
        out.add(w + last)                                                  # kall- < kal before a vowel
    return out


def after_junction(rest, v):
    """Possible second members after the first member v: undo a doubled initial stop or a glide."""
    out = [rest]
    if len(rest) >= 2 and rest[0] == rest[1] and rest[0] in STOPS:
        out.append(rest[1:])
    if len(rest) >= 2 and rest[1] in VOWEL_CHARS:
        if rest[0] == "y" and v.endswith(Y_AFTER):
            out.append(rest[1:])
        elif rest[0] == "v" and v.endswith(V_AFTER):
            out.append(rest[1:])
    return out


def before_junction(head, r):
    """Possible first members before a second member r at the end of a compound."""
    out = []
    if r[:1] in STOPS and head.endswith(r[0]) and len(head) >= 2:
        out.append(head[:-1])                                              # aṟu-k-kaṭavuḷ
    if r[:1] in VOWEL_CHARS and len(head) >= 2 and head[-1] in "yv" and head[-2] in VOWEL_CHARS:
        out.append(head[:-1])                                              # cāḻai-y-akatti
    return out + [head]


class Words:
    """Principal headwords of the dictionary and their surface forms as first members."""

    def __init__(self, forms):
        self.words = {key(f) for f in forms if f}
        self.firsts = set()
        for f in forms:
            if f:
                self.firsts |= {key(v) for v in first_variants(f)}

    def second(self, r):
        return has_vowel(r) and key(r) in self.words

    def first(self, p):
        return has_vowel(p) and key(p) in self.firsts


def split_first(s, root, ok_right):
    """s = a surface form of root + a second member.

    A second member that begins with a consonant is preferred (kaḷa-mati over
    kaḷam-ati, kāla-vakai over kāla-v-akai), then the longest surface form."""
    ks = key(s)
    found = []
    for v in first_variants(root):
        if len(v) >= len(s) or not ks.startswith(key(v)) or not has_vowel(v):
            continue
        for r in after_junction(s[len(v):], v):
            if ok_right(r):
                found.append((r[0] in VOWEL_CHARS, -len(v), r, s[:len(v)]))
    if not found:
        return None
    _, _, r, v = min(found)
    return v, r


def split_second(s, root, ok_left):
    """s = a first member + root."""
    ks, kr = key(s), key(root)
    for r_surface in (root, root[0] + root if root[:1] in STOPS else None):
        if not r_surface or len(r_surface) >= len(s) or not ks.endswith(key(r_surface)):
            continue
        for p in before_junction(s[:len(s) - len(r_surface)], root) if r_surface == root else [s[:len(s) - len(r_surface)]]:
            if ok_left(p):
                return p, s[len(s) - len(root):]
    return None


def segment(s, roots, words):
    """Two members of a sub-entry s nested under a principal with forms `roots`."""
    toks = s.split()
    if len(toks) == 2:
        for root in roots:
            if key(toks[0]) in {key(v) for v in first_variants(root)} and words.second(toks[1]):
                return toks, "phrase"
            if key(toks[1]) == key(root) and words.first(toks[0]):
                return toks, "phrase"
        return None, None
    if len(toks) != 1:
        return None, None
    for root in roots:
        got = split_first(s, root, words.second)
        if got:
            return list(got), "first"
    for root in roots:
        got = split_second(s, root, words.first)
        if got:
            return list(got), "second"
    return None, None


def segment_ety(s, a, b):
    """A principal s whose etymology names members a and b; b may be inflected (iṭu > iṭa)."""
    sb = stem(b)
    got = split_first(s, a, lambda r: key(r) == key(b) or stem(r) == sb)
    if got:
        return list(got)
    fa = {key(v) for v in first_variants(a)}
    got = split_second(s, b, lambda p: key(p) in fa)
    return list(got) if got else None


# ---------------------------------------------------------------- page parsing

def strip_tags(s):
    return html.unescape(re.sub(r"</?[A-Za-z][^>]*>", "", s))


def gloss_text(body):
    s = re.sub(r"<tam>.*?</tam>", " ", body, flags=re.S)
    s = re.sub(r"<smallcaps?>.*?</smallcaps?>", " ", s, flags=re.S)
    s = strip_tags(s)
    s = re.sub(r"\[[^\[\]]*\]", " ", s)
    s = re.sub(r"\([^()]*\)", " ", s)
    return re.sub(r"\s+", " ", s).strip(" ,;.")[:600]


def pos_of(rest):
    """Part of speech: the <pos> tag, or the first italic when it is a verb label."""
    m = re.search(r"<i>(.*?)</i>", rest, re.S)
    if not m:
        return None, ""
    inner = m.group(1)
    p = re.search(r"<pos>(.*?)</pos>", inner, re.S)
    label = strip_tags(p.group(1) if p else inner).strip()
    if not p and not re.match(r"(?:v\.\s*[an]\.|inf\.|s\.|adj\.|adv\.|v\. noun)", label):
        return None, strip_tags(inner)
    return label, strip_tags(inner)


def grammatical(gloss, label):
    """True when the first sense of a principal describes a letter, ending, particle or prefix."""
    g = gloss or ""
    if label and g.startswith(label):
        g = g[len(label):].strip(" ,.")
    first = re.split(r"\s2\.\s", g, maxsplit=1)[0]
    return bool(LETTER_RE.search(first)) or (label is None and bool(PARTICLE_RE.search(first)))


def norm_pos(label):
    if not label:
        return None, False
    lab = label.strip()
    if lab.startswith("s."):
        return "n", False
    verb = bool(re.match(r"v\.\s*[an]\.|v\. a\. & n\.|inf\.", lab)) and not lab.startswith("v. noun")
    return lab, verb


def parse_page(text, page):
    principals, subs = [], []
    for block in DIV_RE.findall(text):
        if "<hw>" not in block:
            continue
        star = bool(re.match(r"\s*(?:<span[^>]*>)?\s*\*", block))
        hw = re.search(r"<hw>(.*?)</hw>", block, re.S)
        bs = [strip_tags(x).strip() for x in re.findall(r"<b>(.*?)</b>", hw.group(1), re.S)]
        pairs = [(unicodedata.normalize("NFC", bs[k]), unicodedata.normalize("NFC", bs[k + 1]))
                 for k in range(0, len(bs) - 1, 2)]
        if not pairs:
            continue
        rest = block[hw.end():]
        first_p2 = rest.find("<p2>")
        main = rest if first_p2 < 0 else rest[:first_p2]
        label, italic = pos_of(main)
        pos, verb = norm_pos(label)
        foreign = bool(FOREIGN_RE.search(strip_tags(main[:200])))
        ety = re.search(r"\[\s*<i>ex\.?</i>\s*<tam>([^<]*)</tam>[^\[\]]*?<i>et\.?</i>\s*<tam>([^<]*)</tam>", main, re.S)
        rec = {"page": page, "kind": "principal", "forms": pairs, "star": star or foreign, "asterisk": star,
               "foreign_mark": foreign, "pos": pos, "pos_source": label, "verb": verb,
               "ety": [unicodedata.normalize("NFC", ety.group(1).strip()),
                       unicodedata.normalize("NFC", ety.group(2).strip())] if ety else None,
               "gloss": gloss_text(main)}
        rec["grammatical"] = grammatical(rec["gloss"], label)
        principals.append(rec)
        for p2 in P2_RE.findall(rest):
            m = re.match(r"\s*(\*?)\s*((?:<tam>[^<]*</tam>\s*[–-]?\s*)+)", p2)
            if not m:
                continue
            heads = [unicodedata.normalize("NFC", strip_tags(x).strip()) for x in re.findall(r"<tam>([^<]*)</tam>", m.group(2))]
            after = p2[m.end():]
            slabel = None
            pm = re.match(r"\s*[,.]?\s*<i>\s*<pos>(.*?)</pos>", after, re.S)
            if pm:
                slabel = strip_tags(pm.group(1)).strip()
            spos, sverb = norm_pos(slabel)
            subs.append({"page": page, "kind": "sub", "heads": [h for h in heads if h], "root_forms": pairs,
                         "root_grammatical": rec["grammatical"],
                         "star": bool(m.group(1)), "pos": spos, "pos_source": slabel, "verb": sverb,
                         "gloss": gloss_text(after)})
    return principals, subs


def build(pages):
    principals, subs = [], []
    for page, text in pages:
        p, s = parse_page(text, page)
        principals += p
        subs += s
    words = Words([rom for r in principals if not r["grammatical"] for _, rom in r["forms"]])
    out = []
    for r in principals:
        for tam, rom in r["forms"]:
            members = parse_tamil_lex.members(rom)
            seg = None
            if r["ety"] and len(members) == 1:
                got = segment_ety(rom, translit(r["ety"][0]), translit(r["ety"][1]))
                if got:
                    members, seg = got, "ety"
            out.append({"page": r["page"], "kind": "principal", "head": tam, "translit_plain": rom,
                        "translit": "-".join(members) if seg else rom, "members": members, "seg": seg,
                        "star": r["star"], "asterisk": r["asterisk"], "foreign_mark": r["foreign_mark"],
                        "grammatical": r["grammatical"], "pos": r["pos"], "pos_source": r["pos_source"],
                        "verb": r["verb"], "ety": r["ety"], "gloss": r["gloss"]})
    for r in subs:
        roots = [rom for _, rom in r["root_forms"]]
        for tam in r["heads"]:
            rom = translit(tam)
            members, seg = (None, None)
            if r["pos"] is not None and rom and not r["root_grammatical"]:
                members, seg = segment(rom, roots, words)
                # a verbal noun ends in a verbal-noun suffix (-al, -tal, -kai, -pu), not a word
                if members and (r["pos_source"] or "").startswith("v. noun") and syllables(members[1]) < 2:
                    members, seg = None, None
            out.append({"page": r["page"], "kind": "sub", "head": tam, "translit_plain": rom,
                        "translit": "-".join(members) if members else rom, "members": members or [],
                        "seg": seg, "root": roots[0], "root_grammatical": r["root_grammatical"],
                        "star": r["star"], "asterisk": r["star"], "foreign_mark": False,
                        "grammatical": False, "pos": r["pos"], "pos_source": r["pos_source"],
                        "verb": r["verb"], "gloss": r["gloss"]})
    return out


def load_pages():
    pages = []
    hasher = hashlib.sha256()
    for path in sorted(glob.glob(str(PAGES / "page-*.html"))):
        raw = Path(path).read_bytes()
        hasher.update(hashlib.sha256(raw).digest())
        pages.append((int(Path(path).stem.split("-")[1]), raw.decode("utf-8")))
    return pages, hasher.hexdigest()


def main():
    if OUT.exists():
        print("refusing to overwrite", OUT)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pages, digest = load_pages()
    out = build(pages)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n2 = sum(1 for r in out if len(r["members"]) == 2)
    by = {}
    for r in out:
        if len(r["members"]) == 2:
            key = r["seg"] or "principal-tokens"
            by[key] = by.get(key, 0) + 1
    print(json.dumps({"pages": len(pages), "pages_with_entries": sum(1 for _, t in pages if "<hw>" in t),
                      "records": len(out), "principals": sum(1 for r in out if r["kind"] == "principal"),
                      "sub_entries": sum(1 for r in out if r["kind"] == "sub"), "two_member": n2,
                      "two_member_by_rule": by, "pages_digest": digest,
                      "out": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
