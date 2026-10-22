"""Parse the DSAL pages of the Dravidian Etymological Dictionary into a local JSONL table.

Each DEDR entry becomes one record with its number, the languages and Dravidian
subgroups that attest it, and a list of word groups (language, forms, gloss).
Comparisons with other families, which DEDR places after " / " or "Cf. Skt.",
and the closing DED/DEN references are cut before parsing.

Subgroups follow Krishnamurti (2003): South Dravidian I (with Tulu), South
Dravidian II (South-Central), Central and North Dravidian.

    python -I experiments/2026-10-21-rebus-base-rate/code/parse_dedr.py
"""

import glob
import hashlib
import html
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "dedr"
OUT = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1" / "dedr-entries.jsonl"

SD1, SD2, CD, ND = "SD1", "SD2", "CD", "ND"
LANGS = {
    "Ta": ("Tamil", SD1), "Ma": ("Malayalam", SD1), "Ir": ("Irula", SD1), "PālKu": ("Pālu Kurumba", SD1),
    "ĀlKu": ("Ālu Kurumba", SD1), "Kurub": ("Betta Kurumba", SD1), "Ko": ("Kota", SD1), "To": ("Toda", SD1),
    "Ka": ("Kannada", SD1), "Koḍ": ("Kodagu", SD1), "Kod": ("Kodagu", SD1), "Tu": ("Tulu", SD1),
    "Bel": ("Belari", SD1), "Kor": ("Koraga", SD1), "Bad": ("Badaga", SD1),
    "Te": ("Telugu", SD2), "Go": ("Gondi", SD2), "Konḍa": ("Konda", SD2), "Pe": ("Pengo", SD2),
    "Manḍ": ("Manda", SD2), "Kui": ("Kui", SD2), "Kuwi": ("Kuwi", SD2),
    "Kol": ("Kolami", CD), "Nk": ("Naikri", CD), "Pa": ("Parji", CD), "Ga": ("Gadaba", CD), "Oll": ("Ollari", CD),
    "Kur": ("Kurux", ND), "Kuruḵẖ": ("Kurux", ND), "Oraon": ("Kurux", ND), "Malt": ("Malto", ND), "Br": ("Brahui", ND),
}
LANG_RE = re.compile(r"^\??\s*(" + "|".join(sorted((re.escape(k) for k in LANGS), key=len, reverse=True)) + r")\.?$")
TRAIL_LANG_RE = re.compile(r"(?:^|[\s.;?])(" + "|".join(sorted((re.escape(k) for k in LANGS), key=len, reverse=True)) + r")\.(?:\s*\([^()]*\))?\s*$")
APPENDIX_FIRST_PAGE = 509
ENTRY_RE = re.compile(r"<number>(.*?)</number>(.*?)</span>\s*</div>", re.S)


class Runs(HTMLParser):
    """Flatten entry HTML into (bold, italic, text) runs."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.b = 0
        self.i = 0
        self.runs = []

    def handle_starttag(self, tag, attrs):
        if tag == "b":
            self.b += 1
        elif tag == "i":
            self.i += 1

    def handle_endtag(self, tag):
        if tag == "b":
            self.b = max(0, self.b - 1)
        elif tag == "i":
            self.i = max(0, self.i - 1)

    def handle_data(self, data):
        if data:
            self.runs.append((self.b > 0, self.i > 0, data))


def cut_comparisons(body):
    """Drop cross-family comparisons and closing references from an entry body."""
    text = body
    # a slash section outside a bold form starts the comparison notes
    for m in re.finditer(r"\s/\s", text):
        before = text[:m.start()]
        if before.rfind("<b>") <= before.rfind("</b>"):
            text = before
            break
    m = re.search(r"\b(?:DED|DEN|DBIA)\b[^<]*$", text)
    if m:
        text = text[:m.start()]
    return text


def expand_optional(form):
    """'agacāṭ(a)lu' -> ['agacāṭalu', 'agacāṭlu']; other parentheses are removed."""
    m = re.search(r"(?<=\w)\((\w{1,3})\)|\((\w{1,3})\)(?=\w)", form)
    if not m:
        return [form]
    inner = m.group(1) or m.group(2)
    return expand_optional(form[:m.start()] + inner + form[m.end():]) + expand_optional(form[:m.start()] + form[m.end():])


def split_forms(s):
    s = re.sub(r"\([^()]*$", " ", s)          # parenthesis closed outside the bold run
    s = re.sub(r"\([^()]*[\s,;][^()]*\)", " ", s)   # stem and dialect notes such as (-pp-, -nt-)
    out = []
    for part in re.split(r"[,;/]", s):
        if part.strip().startswith("-"):           # a suffix or stem alternant, not a word
            continue
        for variant in expand_optional(part.strip()):
            variant = re.sub(r"\([^()]*\)", " ", variant)
            variant = re.sub(r"\[[^\[\]]*\]", " ", variant)
            variant = variant.replace(")", " ").replace("(", " ")
            variant = re.sub(r"\s+", " ", variant).strip(" .:?/")
            if not variant or re.search(r"[A-Z]", variant):
                continue
            if re.search(r"[a-zāīūēōṅñṭḍṇḷḻṟṉ]", variant):
                out.append(unicodedata.normalize("NFC", variant))
    return out


def parse_entry(num, body, page):
    runs = Runs()
    runs.feed(cut_comparisons(body))
    groups = []
    lang = None
    forms_buf = []
    gloss_buf = []

    def flush():
        nonlocal forms_buf, gloss_buf
        if forms_buf and lang:
            gloss = re.sub(r"\s+", " ", "".join(gloss_buf)).strip(" ;,.")
            if re.match(r"^[^()]*\)", gloss):        # tail of a parenthesis opened in the bold run
                gloss = re.sub(r"^[^()]*\)\s*", "", gloss)
            # forms separated by ';' inside one bold run have their own, elided glosses
            chunks = re.split(r";(?![^()]*\))", " ".join(forms_buf))
            for k, chunk in enumerate(chunks):
                forms = split_forms(chunk)
                if forms:
                    groups.append({"lang": lang, "forms": forms, "gloss": gloss if k == len(chunks) - 1 else ""})
        forms_buf, gloss_buf = [], []

    for bold, italic, text in runs.runs:
        t = text.strip()
        if italic:
            m = LANG_RE.match(t)
            if m:
                flush()
                lang = m.group(1)
                continue
            # a bold italic run ending in a language label ("Sesbania grandiflora. Ma.")
            m2 = TRAIL_LANG_RE.search(t)
            if m2 and bold:
                flush()
                lang = m2.group(1)
                continue
            # other italics are grammatical labels or Latin names: keep Latin names in glosses
            if not bold:
                gloss_buf.append(text)
            elif forms_buf and not gloss_buf:
                continue
            else:
                gloss_buf.append(text)
            continue
        if bold:
            if gloss_buf:
                flush()
            forms_buf.append(text)
        else:
            m = TRAIL_LANG_RE.search(text)
            if m and not forms_buf:
                lang = m.group(1)
                gloss_buf.append(text[:m.start()])
                flush()
                continue
            if m:
                gloss_buf.append(text[:m.start()])
                flush()
                lang = m.group(1)
                continue
            gloss_buf.append(text)
    flush()

    # "id." repeats the previous gloss of the entry
    last = ""
    for g in groups:
        if re.fullmatch(r"(?:id|ditto)\.?", g["gloss"].strip()) or g["gloss"].strip().startswith("id."):
            g["gloss_id"] = True
            g["gloss"] = last + g["gloss"].strip()[3:]
        elif g["gloss"]:
            last = g["gloss"]
    langs = sorted({g["lang"] for g in groups})
    subgroups = sorted({LANGS[l][1] for l in langs})
    return {"num": num, "page": page, "langs": langs, "subgroups": subgroups, "groups": groups}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pages = sorted(glob.glob(str(RAW / "page-*.html")))
    repeats = 0
    best = {}                                        # number -> fullest record printed under it
    hasher = hashlib.sha256()
    for path in pages:
        page = int(Path(path).stem.split("-")[1])
        raw = Path(path).read_bytes()
        hasher.update(hashlib.sha256(raw).digest())
        s = raw.decode("utf-8")
        for num, body in ENTRY_RE.findall(s):
            num = html.unescape(num).strip()
            if page >= APPENDIX_FIRST_PAGE:          # the appendix numbers its entries afresh
                num = "a" + num
            rec = parse_entry(num, body, page)
            if num in best:                          # DSAL prints some entries twice, once with supplements
                repeats += 1
                if len(rec["groups"]) <= len(best[num]["groups"]):
                    continue
            best[num] = rec
    with OUT.open("w", encoding="utf-8") as out:
        for rec in best.values():
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    n = len(best)
    print(json.dumps({"pages": len(pages), "entries": n, "repeated_numbers_merged": repeats, "pages_digest": hasher.hexdigest(),
                      "out": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    sys.exit(main())
