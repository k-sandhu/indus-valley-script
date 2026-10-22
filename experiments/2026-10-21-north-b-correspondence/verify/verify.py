"""Second implementation of the NORTH-B-CORRESPONDENCE-2026-10-21 counts (protocol step 6).

Written from PROTOCOL.md and PARSE-CHECK.md alone, without the first implementation's
code or outputs. It reads the 514 DSAL pages of DEDR saved by REBUS-BASE-RATE-2026-10-21,
checks each page against the SHA-256 in the request log, parses entries, lettered parts,
language lines and bold forms, and counts the initial of the first Kurukh and Malto forms
in parts whose first Tamil form begins with m- or v-.

Run from the repository root, in isolated mode because the pages are downloaded files:

    python -I experiments/2026-10-21-north-b-correspondence/verify/verify.py \
        --pages data/raw/2026-10-21-rebus-base-rate/sources-v1/dedr \
        --log data/raw/2026-10-21-rebus-base-rate/sources-v1/dedr/requests.jsonl \
        --out experiments/2026-10-21-north-b-correspondence/verify/verification-v1.json \
        --local data/raw/2026-10-21-north-b-correspondence/verify-v1

The tracked output holds counts, entry numbers and initial classes only. Parsed lines and
forms (DEDR is all rights reserved) go to the local directory given by --local.

Besides the main reading, the script reruns the count under alternative readings of the
points the protocol and PARSE-CHECK.md leave open (see VERIFY-NOTES.md) and reports the
pass-rule lists and the primary table for each.

Standard library only. Python 3.13.
"""

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# Options: the main reading and the alternatives run as sensitivity checks
# ---------------------------------------------------------------------------

MAIN = {
    # bold and italic depth restart at every new_p span (False: carried on, as a browser would)
    "reset_style_per_span": True,
    # italic labels written "Kur", "Malt;", "Ta:" are labels (False: canonical spelling only)
    "italic_label_variants": True,
    # a bold run that opens with a language label is a cross-reference and gives no form
    "drop_bold_label_runs": True,
    # the bold run right after an italic citation label (correction 3) gives no form
    "drop_after_italic_citation": True,
    # correction 1 applies to plain labels of every language (False: Ta, Kur, Malt, Br only)
    "plain_lines_all_languages": True,
    # comparison notes start at "/" with space on both sides, or with space on one side when
    # a capital, "?", "<", ">", "(" or "[" follows ("/Cf.", "id./ Cf."); False: " / " only
    "slash_variants": True,
    # parenthesised groups detached from a word are notes and give no form (False: a group
    # whose text does not begin or end with a hyphen is read as a further form)
    "drop_parenthesised_groups": True,
}
VARIANTS_TO_RUN = [
    ("style_carried_across_spans", {"reset_style_per_span": False}),
    ("canonical_italic_labels_only", {"italic_label_variants": False}),
    ("bold_label_runs_kept_as_forms", {"drop_bold_label_runs": False}),
    ("forms_after_italic_citations_kept", {"drop_after_italic_citation": False}),
    ("plain_lines_four_languages_only", {"plain_lines_all_languages": False}),
    ("literal_space_slash_space_only", {"slash_variants": False}),
    ("parenthesised_variants_as_forms", {"drop_parenthesised_groups": False}),
]

# ---------------------------------------------------------------------------
# Language labels
# ---------------------------------------------------------------------------

# DEDR's order of languages, used by parse correction 1 (a plain label starts a line
# only when its language comes later than the current line's).
LANG_ORDER = [
    "Ta", "Ma", "Ir", "PālKu", "ĀlKu", "Kurub", "Ko", "To", "Ka", "Koḍ", "Tu", "Bel",
    "Kor", "Te", "Kol", "Nk", "Pa", "Ga", "Go", "Konḍa", "Pe", "Manḍ", "Kui", "Kuwi",
    "Kur", "Malt", "Br",
]
ORDER = {name: k for k, name in enumerate(LANG_ORDER)}
UNDOTTED = {"Konḍa", "Kui", "Kuwi"}
FOUR = {"Ta", "Kur", "Malt", "Br"}
# Misspellings that DSAL sets in italics as labels; they end lines like any other label.
SPELLINGS = {
    "Ālku": "ĀlKu", "Kod": "Koḍ", "Koḏ": "Koḍ", "Koṇḍa": "Konḍa", "Konḏa": "Konḍa",
    "Mand": "Manḍ", "Manḍa": "Manḍ", "Ṭe": "Te",
}
_ALL = sorted(set(LANG_ORDER) | set(SPELLINGS), key=len, reverse=True)
_CANON = "|".join(
    re.escape(n) + (r"\.?" if n in UNDOTTED else r"\.")
    for n in sorted(LANG_ORDER, key=len, reverse=True)
)
_END = r"(?=$|[\s(),\]?])"
# Italic labels with variants: period missing or replaced by ":" or ";" ("Kur", "Malt;").
ITALIC_LABEL_RE = re.compile(r"(?<![\w.'’-])(" + "|".join(map(re.escape, _ALL)) + r")([.:;]?)" + _END)
CANON_LABEL_RE = re.compile(r"(?<![\w.'’-])(" + _CANON + r")" + _END)
BOLD_LABEL_START_RE = re.compile(r"^\s*\??\s*(" + _CANON + r")(?=\s)")


def canon(name):
    name = name.rstrip(".:;")
    return SPELLINGS.get(name, name)


# Cue words of parse corrections 1 and 3.
CUE_RE = re.compile(
    r"(?:^|[\s(\[;,])(?:cf\.|esp\.|see|s\.\s?v\.|viz\.|i\.\s?e\.|e\.\s?g\.|also|=)$", re.I
)
NUMBER_END_RE = re.compile(r"(?:^|[^\w.])\d+[a-z]?$")
PART_MARK_RE = re.compile(r"\(([a-z])\)\s*(?:\?\s*)?$")
DED_RE = re.compile(r"(?<![A-Za-z])(?:DEDS|DED|DEN|DBIA)(?![a-z])")

NORTH = ("Kur", "Malt")
CLASSES = ("m", "b", "v", "other")

# ---------------------------------------------------------------------------
# HTML reading
# ---------------------------------------------------------------------------

KNOWN_TAGS = (
    "html|head|meta|link|script|title|body|div|h1|a|hr|span|number|b|i|super|at|c|br|xref"
)
# A "<" that does not open a known tag is DEDR text (the borrowing sign, "<Santali").
BARE_LT_RE = re.compile(r"<(?!/?(?:" + KNOWN_TAGS + r")\b|!)", re.I)


class PageParser(HTMLParser):
    """Collects entry blocks: each plain <div> holding new_p spans is one print of an entry.

    Bold and italic state is a depth count, so misnested tags (<i><b>Ta.</i> a</b>) resolve
    by character. In the main reading the count restarts at every new_p span, so an unclosed
    tag in one entry does not spread to the next."""

    def __init__(self, reset):
        super().__init__(convert_charrefs=True)
        self.reset = reset
        self.blocks = []
        self.block = None
        self.span = None
        self.depth = 0
        self.b = 0
        self.i = 0
        self.in_number = False
        self.number = None

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            self.block = {"number": None, "spans": []}
            self.blocks.append(self.block)
            return
        if tag == "span":
            if self.span is not None:
                self.depth += 1
            elif dict(attrs).get("class") == "new_p":
                if self.block is None:
                    self.block = {"number": None, "spans": []}
                    self.blocks.append(self.block)
                self.span = []
                self.block["spans"].append(self.span)
                self.depth = 1
                if self.reset:
                    self.b = 0
                    self.i = 0
            return
        if tag == "b":
            self.b += 1
        elif tag == "i":
            self.i += 1
        elif tag == "number" and self.span is not None:
            self.in_number = True
            self.number = ""

    def handle_endtag(self, tag):
        if tag == "b":
            self.b = max(0, self.b - 1)
        elif tag == "i":
            self.i = max(0, self.i - 1)
        if self.span is None:
            return
        if tag == "span":
            self.depth -= 1
            if self.depth <= 0:
                self.span = None
        elif tag == "number":
            self.in_number = False
            if self.block["number"] is None:
                num = self.number.strip()
                # "4896(a)": the letter of the first part sits inside the number tag
                m = re.match(r"^(\d+)\s*\(([a-z])\)$", num)
                if m:
                    num = m.group(1)
                    self.span.append(("(%s) " % m.group(2), False, False))
                self.block["number"] = num

    def handle_data(self, data):
        if self.span is None:
            return
        if self.in_number:
            self.number += data
            return
        self.span.append((data, self.b > 0, self.i > 0))


def check_and_load(pages_dir, log_path):
    """Check every page against its logged SHA-256; return the decoded pages."""
    log = {}
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                log[int(rec["page"])] = rec["sha256"]
    pages = {}
    for page in range(1, 515):
        path = os.path.join(pages_dir, "page-%05d.html" % page)
        with open(path, "rb") as fh:
            raw = fh.read()
        digest = hashlib.sha256(raw).hexdigest()
        if log.get(page) != digest:
            sys.exit("hash mismatch or missing log entry for page %d: %s" % (page, digest))
        pages[page] = BARE_LT_RE.sub("&lt;", raw.decode("utf-8"))
    return pages, len(log)


def read_prints(pages, reset):
    prints = []
    for page in range(1, 515):
        parser = PageParser(reset)
        parser.feed(pages[page])
        parser.close()
        for blk in parser.blocks:
            if not blk["spans"]:
                continue
            if blk["number"] is None:
                sys.exit("entry block without a number on page %d" % page)
            key = ("a" if page >= 509 else "") + blk["number"]
            prints.append({"key": key, "page": page, "spans": blk["spans"]})
    return prints


def flat_text(spans):
    return " ".join("".join(t for t, _, _ in sp) for sp in spans)


def norm_ws(s):
    return " ".join(s.split())


def group_prints(prints):
    """Longest print per number; prints that are not prefixes of it become separate entries."""
    by_key = collections.OrderedDict()
    for p in prints:
        by_key.setdefault(p["key"], []).append(p)
    entries = collections.OrderedDict()
    report = {"repeated_numbers": 0, "prefix_ok": 0, "misnumbered": []}
    for key, plist in by_key.items():
        if len(plist) > 1:
            report["repeated_numbers"] += 1
        groups = []
        for p in plist:
            t = norm_ws(flat_text(p["spans"]))
            for g in groups:
                if t.startswith(g["text"]) or g["text"].startswith(t):
                    g["prints"].append(p)
                    if len(t) > len(g["text"]):
                        g["text"] = t
                    break
            else:
                groups.append({"text": t, "prints": [p]})
        if len(plist) > 1 and len(groups) == 1:
            report["prefix_ok"] += 1
        if len(groups) > 1:
            report["misnumbered"].append(key)
        for k, g in enumerate(groups):
            name = key if k == 0 else "%s/%d" % (key, k + 1)
            longest = max(g["prints"], key=lambda p: len(norm_ws(flat_text(p["spans"]))))
            entries[name] = {"prints": g["prints"], "longest": longest}
    return entries, report


# ---------------------------------------------------------------------------
# Parsing one print into parts, lines and forms
# ---------------------------------------------------------------------------


def runs(mask):
    out = []
    k, n = 0, len(mask)
    while k < n:
        if mask[k]:
            s = k
            while k < n and mask[k]:
                k += 1
            out.append((s, k))
        else:
            k += 1
    return out


def is_letter(ch):
    return unicodedata.category(ch)[0] in "LM"


def paren_groups(text):
    stack, groups, unmatched_close = [], [], []
    for k, ch in enumerate(text):
        if ch == "(":
            stack.append(k)
        elif ch == ")":
            if stack:
                a = stack.pop()
                if not stack:
                    groups.append((a, k))
            else:
                unmatched_close.append(k)
    return groups, stack, unmatched_close


class Print:
    """One print of an entry as a flat string with per-character bold and italic flags.
    Spans are joined with a blank separator in plain type."""

    def __init__(self, spans, opts):
        self.opts = opts
        chunks, bold, ital, starts = [], [], [], []
        pos = 0
        for n, sp in enumerate(spans):
            if n:
                chunks.append("\n\n")
                bold += [False, False]
                ital += [False, False]
                pos += 2
            starts.append(pos)
            for t, b, i in sp:
                chunks.append(t)
                bold += [b] * len(t)
                ital += [i] * len(t)
                pos += len(t)
        self.T = "".join(chunks)
        self.B = bold
        self.I = ital
        self.span_starts = starts
        n = len(self.T)
        self.bold_runs = runs([self.B[k] and not self.I[k] for k in range(n)])
        self.plain_runs = runs([not self.B[k] and not self.I[k] for k in range(n)])
        self.italic_runs = runs(self.I)
        bold_start = {s: (s, e) for s, e in self.bold_runs}
        self.run_after = {e: bold_start.get(e) for _, e in self.plain_runs + self.italic_runs}

    def span_start(self, pos):
        s = 0
        for st in self.span_starts:
            if st <= pos:
                s = st
        return s

    def before(self, pos):
        return self.T[self.span_start(pos):pos]

    def italic_labels(self):
        rx = ITALIC_LABEL_RE if self.opts["italic_label_variants"] else CANON_LABEL_RE
        out = []
        for s, e in self.italic_runs:
            for m in rx.finditer(self.T[s:e]):
                out.append({"pos": s + m.start(), "end": s + m.end(), "lang": canon(m.group(1)),
                            "kind": "italic", "run": (s, e)})
        return out

    def plain_labels(self):
        out = []
        for s, e in self.plain_runs:
            for m in CANON_LABEL_RE.finditer(self.T[s:e]):
                out.append({"pos": s + m.start(), "end": s + m.end(), "lang": canon(m.group(1)),
                            "kind": "plain", "run": (s, e)})
        return out

    def bold_after(self, lab):
        """The bold run right after a label that ends its run (only spaces between)."""
        s, e = lab["run"]
        if self.T[lab["end"]:e].strip():
            return None
        return self.run_after.get(e)

    def is_cited(self, lab):
        prev = self.before(lab["pos"]).rstrip()
        return bool(CUE_RE.search(prev) or NUMBER_END_RE.search(prev))

    def forms_in_run(self, s, e):
        """Split one bold run into forms, with positions and the doubt marks they carry."""
        text = self.T[s:e]
        chars = list(text)
        keep = [True] * len(chars)
        groups, open_left, close_left = paren_groups(text)
        extra = []  # parenthesised variants read as forms (alternative reading only)
        for a, b in groups:
            inner = text[a + 1:b].strip()
            if inner == "?":
                for k in range(a, b + 1):
                    chars[k] = " "
                chars[a + 1] = "?"
                continue
            attached = (a > 0 and is_letter(text[a - 1])) or (b + 1 < len(text) and is_letter(text[b + 1]))
            if attached:
                keep[a] = keep[b] = False  # optional letters: brackets go, letters stay
                continue
            for k in range(a, b + 1):
                keep[k] = False  # parenthesised stem, dialect or variant note
            if not self.opts["drop_parenthesised_groups"]:
                body = inner.lstrip("? ").strip()
                if body and not body.startswith("-") and not body.endswith("-") and any(is_letter(c) for c in body):
                    extra.append({"text": body, "start": s + a + 1, "end": s + b,
                                  "doubt_form": inner.startswith("?"), "run": (s, e)})
        # a bracket left open (the group continues past an italic word) cuts the run there;
        # a stray closing bracket drops what precedes it in the run
        for a in open_left:
            for k in range(a, len(chars)):
                keep[k] = False
        for b in close_left:
            for k in range(0, b + 1):
                keep[k] = False
        pieces, cur, cur_pos = [], [], []
        for k, ch in enumerate(chars):
            if not keep[k]:
                continue
            if ch in ",;/":
                pieces.append((cur, cur_pos))
                cur, cur_pos = [], []
            else:
                cur.append(ch)
                cur_pos.append(s + k)
        pieces.append((cur, cur_pos))
        forms = []
        for cs, ps in pieces:
            txt = "".join(cs)
            if not txt.strip():
                continue
            lead = len(txt) - len(txt.lstrip())
            trail = len(txt.rstrip())
            body = txt.strip()
            doubt = False
            if body.startswith("?"):
                doubt = True
                body2 = body.lstrip("? ")
                lead += len(body) - len(body2)
                body = body2
            if body.endswith("?"):
                doubt = True
                body = body.rstrip("? ")
            if not body or body.startswith("-") or not any(is_letter(c) for c in body):
                continue
            forms.append({"text": body, "start": ps[min(lead, len(ps) - 1)], "end": ps[trail - 1] + 1,
                          "doubt_form": doubt, "run": (s, e)})
        forms += extra
        forms.sort(key=lambda f: f["start"])
        return forms


def parse_print(pr):
    """Return the parts of one print: [{"letter", "lines": [{lang, line_doubt, forms}]}]."""
    opts = pr.opts
    ital = pr.italic_labels()
    plain = pr.plain_labels()
    ital_starts, ital_cites = [], []
    for lab in ital:
        (ital_cites if pr.is_cited(lab) else ital_starts).append(lab)
    marks = []
    for lab in ital_starts:
        m = PART_MARK_RE.search(pr.before(lab["pos"]))
        if m:
            marks.append((lab["pos"] - len(m.group(0)), m.group(1)))
    bounds = [(0, "")] + sorted(marks)
    parts = []
    for k, (ps, letter) in enumerate(bounds):
        pe = bounds[k + 1][0] if k + 1 < len(bounds) else len(pr.T)
        if pe <= ps:
            continue
        parts.append(parse_part(pr, ps, pe, letter, ital_starts, ital_cites, plain, opts))
    if len(parts) > 1 and parts[0]["letter"] == "" and not parts[0]["lines"]:
        parts = parts[1:]
    return parts


def comparison_cut(pr, ps, pe, ital_all, opts):
    """Start of DEDR's comparison notes in a part: the first "/" outside bold that opens
    them, or the closing DED/DEN/DBIA reference (one after which no italic label follows)."""
    T, B = pr.T, pr.B
    cut = pe
    for k in range(ps, pe):
        if T[k] != "/" or B[k]:
            continue
        sb = k > ps and T[k - 1].isspace()
        sa = k + 1 < pe and T[k + 1].isspace()
        nxt = T[k + 1:pe].lstrip()[:1]
        if (sb and sa) or (opts["slash_variants"] and (sb or sa) and (nxt.isupper() or nxt in "?<>([")):
            cut = k
            break
    later_labels = [l["pos"] for l in ital_all if ps <= l["pos"] < pe]
    for m in DED_RE.finditer(T, ps, pe):
        p = m.start()
        if B[p]:
            continue
        if not any(q > p for q in later_labels):
            cut = min(cut, p)
            break
    return cut


def parse_part(pr, ps, pe, letter, ital_starts, ital_cites, plain, opts):
    T = pr.T
    cut = comparison_cut(pr, ps, pe, ital_starts + ital_cites, opts)
    events = [l for l in ital_starts if ps <= l["pos"] < cut]
    events += [l for l in plain if ps <= l["pos"] < cut]
    events.sort(key=lambda l: l["pos"])
    cited_runs = set()
    if opts["drop_after_italic_citation"]:
        for lab in ital_cites:
            if ps <= lab["pos"] < cut:
                r = pr.bold_after(lab)
                if r:
                    cited_runs.add(r)
    if opts["drop_bold_label_runs"]:
        for s, e in pr.bold_runs:
            if ps <= s < cut and BOLD_LABEL_START_RE.match(T[s:e]):
                cited_runs.add((s, e))
    line_starts = []
    current = None
    for lab in events:
        if lab["kind"] == "italic":
            line_starts.append(lab)
            current = lab["lang"]
            continue
        # a plain label: a line (correction 1) or a citation (correction 2)
        nxt = pr.bold_after(lab)
        starts = False
        if nxt is not None and (opts["plain_lines_all_languages"] or lab["lang"] in FOUR):
            prev = pr.before(lab["pos"]).rstrip()
            gloss_end = prev[-1:] in (".", ";", ")")
            cue = bool(CUE_RE.search(prev))
            base = line_starts[-1]["end"] if line_starts else ps
            depth = 0
            for ch in T[base:lab["pos"]]:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth = max(0, depth - 1)
            later = current is None or ORDER[lab["lang"]] > ORDER[current]
            has_form = nxt not in cited_runs and bool(pr.forms_in_run(*nxt))
            starts = gloss_end and not cue and depth == 0 and later and has_form
        if starts:
            line_starts.append(lab)
            current = lab["lang"]
        elif nxt is not None:
            cited_runs.add(nxt)
    lines = []
    for k, lab in enumerate(line_starts):
        ls = lab["end"]
        le = line_starts[k + 1]["pos"] if k + 1 < len(line_starts) else cut
        prev = pr.before(lab["pos"]).rstrip()
        after_in_run = T[lab["end"]:lab["run"][1]] if lab["kind"] == "italic" else ""
        line_doubt = prev.endswith("?") or after_in_run.lstrip().startswith("?")
        forms = []
        for s, e in pr.bold_runs:
            if e <= ls or s >= le or (s, e) in cited_runs:
                continue
            forms += pr.forms_in_run(max(s, ls), min(e, le))
        for j, f in enumerate(forms):
            # "?" or "(?)" immediately before the form
            if T[pr.span_start(f["start"]):f["start"]].rstrip().endswith("?"):
                f["doubt_form"] = True
            # "?" or "(?)" after the last form of a bold run, before its gloss begins
            if j + 1 == len(forms) or forms[j + 1]["run"] != f["run"]:
                tail = T[f["end"]:le]
                k2 = 0
                while k2 < len(tail) and not is_letter(tail[k2]):
                    k2 += 1
                if k2 < len(tail) and "?" in tail[:k2]:
                    f["doubt_form"] = True
        text = T[lab["pos"]:le].lower()
        line_borrowed = "borrowed" in text or "loan" in text
        for j, f in enumerate(forms):
            gap_end = forms[j + 1]["start"] if j + 1 < len(forms) else le
            f["borrowed"] = line_borrowed or "<" in T[f["end"]:gap_end]
            f["doubtful"] = line_doubt or f["doubt_form"]
        lines.append({"lang": lab["lang"], "label_kind": lab["kind"], "start": lab["pos"], "end": le,
                      "line_doubt": line_doubt, "forms": forms})
    return {"letter": letter, "lines": lines}


# ---------------------------------------------------------------------------
# Initials and vowel context
# ---------------------------------------------------------------------------

ACCENTS = {"́", "̀"}


def initial_info(form):
    s = unicodedata.normalize("NFD", form).replace("(", "").replace(")", "")
    k = 0
    while k < len(s) and not unicodedata.category(s[k]).startswith("L"):
        k += 1
    s = "".join(ch for ch in s[k:].lower() if ch not in ACCENTS)
    if not s:
        return None
    clusters = []  # base letter with its combining marks and length dot
    for ch in s:
        if clusters and (unicodedata.category(ch).startswith("M") or ch in "·:"):
            clusters[-1][1].append("·" if ch in "·:" else ch)
        else:
            clusters.append([ch, []])
    first = clusters[0][0]
    bh = first == "b" and len(clusters) > 1 and clusters[1][0] == "h"
    cls = "m" if first == "m" else "b" if first == "b" else "v" if first in "vw" else "other"
    k = 2 if bh else 1
    vowel, nasal = "none", False
    if k < len(clusters) and clusters[k][0] in "aeiou":
        base, marks = clusters[k]
        long_ = "̄" in marks or "·" in marks
        nk = k + 1
        if (base == "a" and not long_ and nk < len(clusters) and clusters[nk][0] in "iu"
                and "̄" not in clusters[nk][1]):
            vowel = "diphthong"
            nk += 1
        elif base in "ie":
            vowel = "long front" if long_ else "short front"
        else:
            vowel = "long back" if long_ else "short back"
        while nk < len(clusters) and not clusters[nk][0].isalpha():
            nk += 1
        if nk < len(clusters):
            nasal = clusters[nk][0] in ("m", "n", "ŋ")
    return {"class": cls, "letter": first, "bh": bh, "vowel": vowel, "next_nasal": nasal}


# ---------------------------------------------------------------------------
# Counting
# ---------------------------------------------------------------------------


def lang_forms(part, lang):
    out = []
    for ln in part["lines"]:
        if ln["lang"] == lang:
            out.extend(ln["forms"])
    return out


def first(forms, undoubted):
    for f in forms:
        if f["borrowed"] or (undoubted and f["doubtful"]):
            continue
        return f
    return None


def entry_sort_key(name):
    m = re.match(r"(a?)(\d+)(?:/(\d+))?", name)
    return (m.group(1) == "a", int(m.group(2)), int(m.group(3) or 1))


def parse_all(pages, opts):
    prints = read_prints(pages, opts["reset_style_per_span"])
    entries, report = group_prints(prints)
    parsed = collections.OrderedDict()
    for name, ent in entries.items():
        pr = Print(ent["longest"]["spans"], opts)
        parsed[name] = {"page": ent["longest"]["page"], "print": pr, "parts": parse_print(pr)}
    return prints, entries, report, parsed


def part_records(parsed):
    records = []
    for name, ent in parsed.items():
        for part in ent["parts"]:
            ta = first(lang_forms(part, "Ta"), undoubted=False)
            ti = initial_info(ta["text"]) if ta else None
            if ti is None or ti["letter"] not in ("m", "v"):
                continue
            rec = {"entry": name, "part": part["letter"], "tamil": ti["letter"], "tamil_form": ta["text"],
                   "tamil_vowel": ti["vowel"], "tamil_next_nasal": ti["next_nasal"], "north": {}, "south": {}}
            for lang in NORTH:
                forms = lang_forms(part, lang)
                nb = [f for f in forms if not f["borrowed"]]
                fu, fd = first(forms, True), first(forms, False)
                rec["north"][lang] = {
                    "present": bool(nb),
                    "first_undoubted": None if fu is None else dict(initial_info(fu["text"]), form=fu["text"]),
                    "first_doubt_allowed": None if fd is None else dict(
                        initial_info(fd["text"]), form=fd["text"], doubtful=fd["doubtful"]),
                    "all_nonborrowed": [dict(initial_info(f["text"]), form=f["text"], doubtful=f["doubtful"])
                                        for f in nb],
                    "borrowed": [f["text"] for f in forms if f["borrowed"]],
                }
            for lang in ("Te", "Ka", "Go"):
                fd = first(lang_forms(part, lang), False)
                rec["south"][lang] = None if fd is None else initial_info(fd["text"])["class"]
            rec["population"] = rec["north"]["Kur"]["present"] or rec["north"]["Malt"]["present"]
            records.append(rec)
    return records


def table(pop, exclude_4876, key):
    out = {t: {lang: {c: 0 for c in CLASSES} for lang in ("Kur", "Malt", "pooled")} for t in ("m", "v")}
    for r in pop:
        if exclude_4876 and r["entry"] == "4876":
            continue
        for lang in NORTH:
            f = r["north"][lang][key]
            if f is not None:
                out[r["tamil"]][lang][f["class"]] += 1
                out[r["tamil"]]["pooled"][f["class"]] += 1
    return out


def entries_where(pop, tamil, test, exclude_4876=False):
    return sorted({r["entry"] for r in pop if r["tamil"] == tamil and test(r)
                   and not (exclude_4876 and r["entry"] == "4876")}, key=entry_sort_key)


def is_b(f):
    return f is not None and f["class"] == "b"


def summarise(records):
    pop = [r for r in records if r["population"]]
    m_first = entries_where(pop, "m", lambda r: any(is_b(r["north"][l]["first_undoubted"]) for l in NORTH), True)
    m_any = entries_where(pop, "m", lambda r: any(is_b(f) for l in NORTH for f in r["north"][l]["all_nonborrowed"]))
    v_first = entries_where(pop, "v", lambda r: any(is_b(r["north"][l]["first_doubt_allowed"]) for l in NORTH))
    if len(m_first) >= 2:
        outcome = "pass"
    elif not [e for e in m_any if e != "4876"] and v_first:
        outcome = "failure"
    else:
        outcome = "unresolved"
    return pop, {
        "tamil_m_entries_b_first_undoubted_excluding_4876": m_first,
        "tamil_m_entries_b_any_nonborrowed_form": m_any,
        "tamil_v_entries_b_first_form_doubt_allowed": v_first,
        "outcome": outcome,
    }


def detail_list(pop, tamil, north_class):
    out = []
    for r in pop:
        if r["tamil"] != tamil:
            continue
        for lang in NORTH:
            d = r["north"][lang]
            hits = [f for f in d["all_nonborrowed"] if f["class"] == north_class]
            if not hits:
                continue
            fu, fd = d["first_undoubted"], d["first_doubt_allowed"]
            out.append({
                "entry": r["entry"], "part": r["part"], "language": lang,
                "first_undoubted_is_hit": bool(fu and fu["class"] == north_class),
                "first_doubt_allowed_is_hit": bool(fd and fd["class"] == north_class),
                "first_doubt_allowed_doubtful": bool(fd and fd["doubtful"]),
                "hit_forms": len(hits), "hit_forms_doubtful": sum(1 for f in hits if f["doubtful"]),
                "bh": any(f["bh"] for f in hits),
                "tamil_vowel": r["tamil_vowel"], "tamil_next_nasal": r["tamil_next_nasal"],
                "north_vowel": hits[0]["vowel"], "north_next_nasal": hits[0]["next_nasal"],
                "first_form_class_Te_Ka_Go": r["south"],
            })
    return out


def population_counts(records, pop):
    out = {}
    for t in ("m", "v"):
        rs = [r for r in pop if r["tamil"] == t]
        out[t] = {
            "parts_with_tamil_first_form_initial": sum(1 for r in records if r["tamil"] == t),
            "population_parts": len(rs),
            "population_entries": len({r["entry"] for r in rs}),
            "population_parts_excluding_4876": sum(1 for r in rs if r["entry"] != "4876"),
            "population_entries_excluding_4876": len({r["entry"] for r in rs if r["entry"] != "4876"}),
        }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pages", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--local", required=True)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    pages, n_logged = check_and_load(args.pages, args.log)
    prints, entries, print_report, parsed = parse_all(pages, MAIN)
    records = part_records(parsed)
    pop, rule = summarise(records)

    lines_found = collections.Counter()
    plain_lines = []
    for name, ent in parsed.items():
        for part in ent["parts"]:
            for ln in part["lines"]:
                if ln["lang"] in FOUR:
                    lines_found[ln["lang"]] += 1
                    if ln["label_kind"] == "plain":
                        plain_lines.append("%s %s" % (ln["lang"], name))

    sensitivity = {}
    for vname, change in VARIANTS_TO_RUN:
        opts = dict(MAIN, **change)
        _, _, _, vparsed = parse_all(pages, opts)
        vrec = part_records(vparsed)
        vpop, vrule = summarise(vrec)
        sensitivity[vname] = {
            "change": change,
            "pass_rule": vrule,
            "population": {t: {"parts": sum(1 for r in vpop if r["tamil"] == t),
                               "entries": len({r["entry"] for r in vpop if r["tamil"] == t})} for t in ("m", "v")},
            "primary_table_excluding_4876": table(vpop, True, "first_undoubted"),
            "same_as_main": (vrule == rule and table(vpop, True, "first_undoubted") == table(pop, True, "first_undoubted")),
        }

    with open(os.path.abspath(__file__), "rb") as fh:
        own_hash = hashlib.sha256(fh.read()).hexdigest()
    result = {
        "study": "NORTH-B-CORRESPONDENCE-2026-10-21",
        "step": "protocol step 6: second implementation, written from PROTOCOL.md and PARSE-CHECK.md",
        "implementation": "experiments/2026-10-21-north-b-correspondence/verify/verify.py",
        "implementation_sha256": own_hash,
        "source": {
            "pages": 514, "log_records": n_logged, "pages_hash_checked": 514, "hash_mismatches": 0,
            "entry_prints": len(prints),
            "entry_numbers": len({p["key"] for p in prints}),
            "appendix_prints": sum(1 for p in prints if p["key"].startswith("a")),
            "appendix_entry_numbers": len({p["key"] for p in prints if p["key"].startswith("a")}),
            "repeated_numbers": print_report["repeated_numbers"],
            "repeated_numbers_shorter_prints_prefix": print_report["prefix_ok"],
            "misnumbered_prints_kept_as_separate_entries": print_report["misnumbered"],
            "entries_counted": len(entries),
        },
        "parse_check": {
            "lines_found_Ta_Kur_Malt_Br": dict(lines_found),
            "plain_type_lines_Ta_Kur_Malt_Br": plain_lines,
        },
        "population": population_counts(records, pop),
        "primary_table_first_undoubted": {
            "excluding_4876": table(pop, True, "first_undoubted"),
            "including_4876": table(pop, False, "first_undoubted")},
        "table_first_form_doubt_allowed": {
            "excluding_4876": table(pop, True, "first_doubt_allowed"),
            "including_4876": table(pop, False, "first_doubt_allowed")},
        "entry_level_b_first_undoubted": {
            t: {"excluding_4876": entries_where(pop, t, lambda r: any(is_b(r["north"][l]["first_undoubted"]) for l in NORTH), True),
                "including_4876": entries_where(pop, t, lambda r: any(is_b(r["north"][l]["first_undoubted"]) for l in NORTH))}
            for t in ("m", "v")},
        "pass_rule": rule,
        "parts_b_for_tamil_m": detail_list(pop, "m", "b"),
        "parts_m_for_tamil_v": detail_list(pop, "v", "m"),
        "sensitivity": sensitivity,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # local, untracked: forms and lines (DEDR is all rights reserved)
    os.makedirs(args.local, exist_ok=True)
    with open(os.path.join(args.local, "parts.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(args.local, "lines.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for name, ent in parsed.items():
            pr = ent["print"]
            for part in ent["parts"]:
                for ln in part["lines"]:
                    fh.write(json.dumps({
                        "entry": name, "part": part["letter"], "lang": ln["lang"],
                        "kind": ln["label_kind"], "line_doubt": ln["line_doubt"],
                        "text": norm_ws(pr.T[ln["start"]:ln["end"]]),
                        "forms": [[f["text"], f["doubtful"], f["borrowed"]] for f in ln["forms"]],
                    }, ensure_ascii=False) + "\n")

    print("outcome:", rule["outcome"])
    print("population:", json.dumps(result["population"]))
    for k, v in rule.items():
        if k != "outcome":
            print(k, v)
    for k, v in sensitivity.items():
        print("variant", k, "same as main" if v["same_as_main"] else "DIFFERS", v["pass_rule"]["outcome"])


if __name__ == "__main__":
    main()
