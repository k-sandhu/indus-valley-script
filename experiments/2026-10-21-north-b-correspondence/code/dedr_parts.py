"""Parse DSAL pages of the Dravidian Etymological Dictionary into entry parts and language lines.

Implements the units of PROTOCOL.md: entries, lettered parts, language lines that
start at italic labels, forms from bold runs, doubt and borrowing flags, initial
classes and vowel context. Reads the pages fetched by REBUS-BASE-RATE-2026-10-21
after checking each against its logged hash, and writes a local JSONL table.

    python -I experiments/2026-10-21-north-b-correspondence/code/dedr_parts.py
"""

import hashlib
import html
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAGES = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "dedr"
OUT_DIR = ROOT / "data" / "raw" / "2026-10-21-north-b-correspondence" / "derived-v1"
APPENDIX_FIRST_PAGE = 509

# DEDR language labels (abbreviation list), with the variants DSAL prints without a dot
LABELS = {
    "Ta": "Tamil", "Ma": "Malayalam", "Ir": "Irula", "PālKu": "Pālu Kurumba", "ĀlKu": "Ālu Kurumba",
    "Ālku": "Ālu Kurumba", "Kurub": "Betta Kurumba", "Ko": "Kota", "To": "Toda", "Ka": "Kannada",
    "Koḍ": "Kodagu", "Tu": "Tulu", "Bel": "Belari", "Kor": "Koraga", "Te": "Telugu", "Kol": "Kolami",
    "Nk": "Naikri", "Pa": "Parji", "Ga": "Gadba", "Go": "Gondi", "Konḍa": "Konda", "Pe": "Pengo",
    "Manḍ": "Manda", "Manḍa": "Manda", "Kui": "Kui", "Kuwi": "Kuwi", "Kur": "Kurukh", "Malt": "Malto",
    "Br": "Brahui",
}
# DEDR lists languages in this order; a label set in plain type starts a line only if it moves forward
ORDER = ["Ta", "Ma", "Ir", "PālKu", "ĀlKu|Ālku", "Kurub", "Ko", "To", "Ka", "Koḍ", "Tu", "Bel", "Kor", "Te", "Kol",
         "Nk", "Pa", "Ga", "Go", "Konḍa", "Pe", "Manḍ|Manḍa", "Kui", "Kuwi", "Kur", "Malt", "Br"]
RANK = {lab: i for i, group in enumerate(ORDER) for lab in group.split("|")}
_ALT = "|".join(sorted((re.escape(k) for k in LABELS), key=len, reverse=True))
# a label inside an italic run: not preceded by a letter or dot, not followed by a letter
LABEL_RE = re.compile(r"(?<![\w.])(?P<q>\?\s*)?(?P<lab>" + _ALT + r")(?:\.|;|(?=[\s)(,]|$))(?!\w)")
PART_RE = re.compile(r"^\s*\((?P<letter>[a-z])\)\s*(?:\?\s*)?(?:" + _ALT + r")(?:\.|;|(?=[\s)(,]|$))(?!\w)")
ENTRY_RE = re.compile(r"<number>(.*?)</number>(.*?)</span>\s*</div>", re.S)
SPAN_SPLIT = '</span><span class="new_p">'
XREF_BEFORE = re.compile(r"(?:\b[cC]f|\b[sS]ee)\.?\s*(?:\d+\s*(?:\([a-z]\)\s*)?)?$")
# a label at the end of a plain run, optionally with a dialect or source note such as "(Hahn)"
PLAIN_LABEL_END = re.compile(r"(?<![\w.])(?P<q>\?\s*)?(?P<lab>" + _ALT + r")(?:\.|;)?\s*(?:\([^()]*\)\s*)?$")
# words after which a label introduces a citation rather than a line
XREF_CUE = re.compile(r"(?:\b(?:cf|Cf|esp|see|See|s\.v|viz|i\.e|e\.g|also)\.?|=)$")
ACCENTS = {"́", "̀", "́", "̀"}


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
            self.runs.append([self.b > 0, self.i > 0, data])


def flatten(body):
    r = Runs()
    r.feed(body.replace(SPAN_SPLIT, " "))
    r.close()
    return r.runs


def split_parts(runs):
    """Divide runs at '(a)', '(b)' ... markers that stand immediately before a language label."""
    parts = [["", []]]
    pending_plain = None                       # a plain run ending in '(x)' may mark the next label
    for bold, italic, text in runs:
        if italic:
            m = PART_RE.match(text)
            if m:
                parts.append([m.group("letter"), []])
                text = text[m.start("letter") + 2:]
            elif pending_plain is not None and LABEL_RE.match(text.lstrip()):
                letter, idx = pending_plain
                prev = parts[-1][1][idx]
                prev[2] = prev[2][: prev[2].rfind("(")]
                parts.append([letter, []])
        pending_plain = None
        if not italic:
            m = re.search(r"\((?P<letter>[a-z])\)\s*$", text)
            if m:
                pending_plain = (m.group("letter"), len(parts[-1][1]))
        parts[-1][1].append([bold, italic, text])
    # text before the first marker stays a part of its own unless it is empty
    if len(parts) > 1 and all(not t.strip() for _, _, t in parts[0][1]):
        parts = parts[1:]
    return parts


def cut_comparison(runs):
    """Drop everything from the first ' / ' outside a bold run (DEDR's comparison notes)."""
    out = []
    for bold, italic, text in runs:
        if not bold:
            m = re.search(r"\s/\s", text)
            if m:
                out.append([bold, italic, text[: m.start()]])
                return out, True
        out.append([bold, italic, text])
    return out, False


def strip_accents_nfd(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if ch not in ACCENTS)


def clean_form(raw):
    """Turn one comma-separated piece of a bold run into a form, or None."""
    s = raw
    s = re.sub(r"\(([^\s()]{1,2})\)(?=\w)", r"\1", s)          # (v)iṇ -> viṇ
    s = re.sub(r"\([^()]*\)", " ", s)
    s = re.sub(r"\[[^\[\]]*\]", " ", s)
    s = s.replace("(", " ").replace(")", " ")
    s = re.sub(r"\d", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .:/")
    if not s or s.startswith("-"):
        return None
    if re.search(r"[A-Z]", s):
        return None
    core = s.lstrip("?* ")
    if not core or core.startswith("-"):
        return None
    if not re.search(r"[a-zāīūēōṅñṭḍṇḷḻṟṉ]", unicodedata.normalize("NFC", core)):
        return None
    return unicodedata.normalize("NFC", s)


def split_bold(text):
    """Forms of one bold run, with doubt marks attached to each form."""
    t = re.sub(r"\([^()]*[\s,;][^()]*\)", " ", text)       # stem and dialect notes such as (-v-, -nt-)
    t = re.sub(r"\([^()]*$", " ", t)                        # parenthesis closed outside the run
    out = []
    for piece in re.split(r"[,;/]", t):
        doubt = bool(re.search(r"(?:^|\s)\?|\(\?\)|\?\s*$", piece))
        form = clean_form(piece)
        if form:
            out.append({"form": form.lstrip("?* ").strip(), "doubt": doubt})
    return out


def initial_letter(form):
    s = strip_accents_nfd(form)
    for ch in s:
        if unicodedata.category(ch).startswith("L"):
            return ch.lower()
    return ""


def initial_class(form):
    s = strip_accents_nfd(form)
    letters = [ch for ch in s if unicodedata.category(ch).startswith("L")]
    first = letters[0].lower() if letters else ""
    if first == "m":
        return "m", False
    if first == "b":
        return "b", len(letters) > 1 and letters[1] == "h"
    if first in ("v", "w"):
        return "v", False
    return "other", False


VOWELS = set("aeiou")


def vowel_context(form):
    """Vowel class after the initial consonant and whether a nasal is the next consonant."""
    s = strip_accents_nfd(form)
    s = "".join(ch for ch in s if not ch in "?*-( )")
    chars = list(s)
    i = 0
    while i < len(chars) and not unicodedata.category(chars[i]).startswith("L"):
        i += 1
    if i >= len(chars):
        return "none", False
    first = chars[i].lower()
    i += 1
    while i < len(chars) and unicodedata.combining(chars[i]):
        i += 1
    if first == "b" and i < len(chars) and chars[i] == "h":
        i += 1
    if first in VOWELS:
        return "none", False                 # the word begins with a vowel
    if i >= len(chars) or chars[i].lower() not in VOWELS:
        vclass = "none"
        j = i
    else:
        base = chars[i].lower()
        j = i + 1
        marks = []
        while j < len(chars) and unicodedata.combining(chars[j]):
            marks.append(chars[j])
            j += 1
        long_ = "̄" in marks
        if j < len(chars) and chars[j] in "·:":
            long_ = True
            j += 1
        if (base == "a" and not long_ and j < len(chars) and chars[j] in "iu"
                and not (j + 1 < len(chars) and unicodedata.combining(chars[j + 1]))):
            vclass = "diphthong"
            j += 1
        elif base in "ie":
            vclass = "long front" if long_ else "short front"
        else:
            vclass = "long back" if long_ else "short back"
    # next consonant after the vowel
    while j < len(chars) and (chars[j].lower() in VOWELS or unicodedata.combining(chars[j]) or chars[j] in "·:"):
        j += 1
    nasal = j < len(chars) and chars[j].lower() in ("m", "n", "ŋ")
    return vclass, nasal


def label_context(prior, part_text):
    """Whether a label after `prior` starts a line: after a gloss end, outside parentheses, after no cue word."""
    core = re.sub(r"[\s?]+$", "", prior)
    depth = part_text.count("(") - part_text.count(")")
    return (core == "" or core[-1] in ".;)") and not XREF_CUE.search(core) and depth <= 0


def parse_part(runs, log=None):
    """Language lines of one part, as a list of {lang, label, plain, label_doubt, forms, text}."""
    lines = []
    cur = None
    prev_text = ""                                   # plain or gloss text since the last bold run
    part_text = ""                                   # all text of the part so far
    quoted = False                                   # the next bold run cites a form of another entry

    def start(lab, q, plain):
        line = {"lang": LABELS[lab], "label": lab, "plain": plain, "label_doubt": q, "forms": [], "text": ""}
        lines.append(line)
        return line

    def plain_marks(text):
        if cur is not None:
            if cur["forms"] and re.match(r"^\s*(?:\?|\(\?\))", text) and prev_text == "":
                cur["forms"][-1]["doubt"] = True
            if cur["forms"] and "<" in text:
                cur["forms"][-1]["borrowed"] = True
            cur["text"] += text

    for idx, (bold, italic, text) in enumerate(runs):
        if italic:
            pos = 0
            for m in LABEL_RE.finditer(text):
                before = prev_text + text[pos:m.start()]
                core = re.sub(r"[\s?]+$", "", before)
                if XREF_CUE.search(core) or re.search(r"\d$", core):
                    # an italic label after "Cf." or an entry number cites another entry
                    quoted = True
                    if log is not None:
                        log.append(("italic citation", m.group("lab")))
                    continue
                q = bool(m.group("q")) or bool(re.search(r"(?:^|[\s.;,(])\?\s*$", before))
                if cur is not None:
                    cur["text"] += text[pos:m.start()]
                cur = start(m.group("lab"), q, False)
                quoted = False
                pos = m.end()
                prev_text = ""
            rest = text[pos:]
            if cur is not None:
                cur["text"] += rest
            prev_text += rest
            part_text += text
            continue
        if bold:
            if cur is None or quoted or XREF_BEFORE.search(prev_text):
                if cur is not None:
                    cur["text"] += text
                prev_text += text
                part_text += text
                quoted = False
                continue
            forms = split_bold(text)
            if forms and re.search(r"(?:^|[\s.;,(])\?\s*$", prev_text):
                forms[0]["doubt"] = True
            for f in forms:
                f["borrowed"] = False
            cur["forms"].extend(forms)
            cur["text"] += text
            prev_text = "" if forms else prev_text + text
            part_text += text
            continue
        # plain text. A label at its end followed by a bold run is either a line that DSAL set
        # without italics or, in a cross-reference context, a citation of another entry's form.
        m = PLAIN_LABEL_END.search(text)
        nxt = runs[idx + 1] if idx + 1 < len(runs) else None
        if m and nxt is not None and nxt[0] and not nxt[1] and split_bold(nxt[2]):
            before = text[: m.start()]
            forward = cur is None or RANK[m.group("lab")] > RANK[cur["label"]]
            if forward and label_context(prev_text + before, part_text + before):
                plain_marks(before)
                q = bool(m.group("q")) or bool(re.search(r"(?:^|[\s.;,(])\?\s*$", prev_text + before))
                cur = start(m.group("lab"), q, True)
                if log is not None:
                    log.append(("plain line", m.group("lab")))
                cur["text"] += text[m.end("lab"):]
                prev_text = ""
                part_text += text
                quoted = False
                continue
            quoted = True
            if log is not None:
                log.append(("plain citation", m.group("lab")))
        plain_marks(text)
        prev_text += text
        part_text += text
    for ln in lines:
        if re.search(r"\bborrowed\b|\bloan", ln["text"], re.I):
            for f in ln["forms"]:
                f["borrowed"] = True
        for f in ln["forms"]:
            f["doubt"] = f["doubt"] or ln["label_doubt"]
            f["initial_letter"] = initial_letter(f["form"])
            f["initial_class"], f["bh"] = initial_class(f["form"])
            f["vowel"], f["nasal_next"] = vowel_context(f["form"])
    return lines


def load_pages():
    log = {}
    for line in (PAGES / "requests.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("source") == "dedr" and rec.get("status") == 200:
            log[int(rec["page"])] = rec["sha256"]
    pages = []
    for path in sorted(PAGES.glob("page-*.html")):
        n = int(path.stem.split("-")[1])
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        if log.get(n) != h:
            raise SystemExit(f"hash mismatch on page {n}")
        pages.append((n, raw.decode("utf-8"), h))
    return pages


def entries_from_pages(pages):
    prints = {}
    order = []
    for n, s, _ in pages:
        for num, body in ENTRY_RE.findall(s):
            num = re.sub(r"\s+", "", html.unescape(num))
            key = ("a" if n >= APPENDIX_FIRST_PAGE else "") + num
            if key not in prints:
                prints[key] = []
                order.append(key)
            prints[key].append((n, body))
    return order, prints


def build(pages):
    order, prints = entries_from_pages(pages)
    records = []
    prefix_failures = []
    for key in order:
        # prints that are prefixes of a longer print are versions of one entry; a print that is not
        # is a different entry carrying the same number, kept under the key "<number>/2", "/3", ...
        clusters = []
        for v in sorted(prints[key], key=lambda v: -len(v[1])):
            for c in clusters:
                if c[0][1].startswith(v[1]):
                    c.append(v)
                    break
            else:
                clusters.append([v])
        if len(clusters) > 1:
            prefix_failures.append(key)
        for k, versions in enumerate(sorted(clusters, key=lambda c: (c[0][0], prints[key].index(c[0])))):
            longest = versions[0]
            ckey = key if k == 0 else f"{key}/{k + 1}"
            rec = parse_entry(ckey, longest[1], longest[0])
            rec["n_prints"] = len(versions)
            rec["misnumbered_print"] = k > 0
            if len(versions) > 1:
                rec["other_prints"] = [parse_entry(ckey, v[1], v[0]) for v in versions[1:]]
            records.append(rec)
    return records, prefix_failures


def parse_entry(key, body, page):
    runs = flatten(body)
    parts = []
    for letter, pruns in split_parts(runs):
        kept, cut = cut_comparison(pruns)
        lines = parse_part(kept)
        parts.append({"letter": letter, "cut": cut, "lines": lines})
    return {"entry": key, "page": page, "parts": parts}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pages = load_pages()
    records, prefix_failures = build(pages)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "dedr-parts.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    digest = hashlib.sha256()
    for n, _, h in pages:
        digest.update(h.encode())
    print(json.dumps({"pages": len(pages), "pages_digest": digest.hexdigest(), "entries": len(records),
                      "parts": sum(len(r["parts"]) for r in records),
                      "repeated_numbers": sum(1 for r in records if r["n_prints"] > 1),
                      "prefix_failures": prefix_failures,
                      "out_sha256": hashlib.sha256(out.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
