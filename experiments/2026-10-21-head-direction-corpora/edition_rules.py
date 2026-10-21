"""Editorial-mark rules of AMENDMENT-3.md: read a printed legend as the die carries it.

Imported by normalize_brahmi.py; no command line. Functions take the printed legend and the
edition's line strings and return lines of words in the edition's transliteration (before the
conversion to IAST), with the flags that set `completeness` and `reading_doubtful`.

Rules (AMENDMENT-3.md):
  R1 one record per impression (explode_impressions);
  R2 square brackets: letters kept as restorations, except with an asterisk (letters the engraver
     omitted, supplied by the editor), which are dropped; round brackets and their content are dropped
     (corrections, alternative readings, "or ..." and "?"), except in Spooner's list, where they hold
     restored letters and are kept; any "?" marks the reading as doubtful;
  R3 lacunae (two or more dots, an ellipsis, or a dash not at a line end) split words and set the
     damage flags, at the edge when no letter precedes or follows them;
  R4 a hyphen or dash at the end of a printed line joins the word to the first word of the next line;
  R5 full stops, commas, semicolons, colons, vertical bars and stray asterisks are removed;
  R6 Marshall (asi-ar-1911-12) sets brackets apart from their letters: a space before an opening
     bracket that follows a letter, a space after a closing square bracket whose content ends in a
     bare consonant, and the spaces around "(?)" are removed.
"""
import copy
import re
import unicodedata

GAP = "⁘"  # placeholder for a lacuna; never a letter
# Spooner (1913-14) prints restored letters in round brackets, e.g. (A)matya; the other editors use them
# for corrections, alternatives and doubts (AMENDMENT-3.md, R2).
ROUND_IS_RESTORATION = {"asi-ar-1913-14"}
VOWELS = set("aāiīuūṛṝḷḹeēoō")
BARE_FINAL_MARKS = set("ḥṃṁ")


def explode_impressions(row):
    """R1: one transcription row per impression when the entry lists impressions with legends."""
    details = row.get("impression_details")
    if not details:
        return [row]
    out = []
    for detail in details:
        new = copy.deepcopy(row)
        new.pop("impression_details", None)
        new["sub_entry"] = detail.get("sub_entry")
        new["legend_as_printed"] = detail.get("legend_as_printed")
        new["legend_lines_as_printed"] = detail.get("legend_lines_as_printed")
        if detail.get("translation_as_printed") is not None:
            new["translation_as_printed"] = detail["translation_as_printed"]
        if detail.get("no_legend"):
            new["legend_as_printed"] = None
        new["impression_of_entry"] = row.get("entry")
        new["impressions_on_object"] = len(details)
        out.append(new)
    return out


def _marshall_spacing(text):
    text = re.sub(r"(?<=[^\W\d_])\s+(?=\[)", "", text)
    text = re.sub(r"(?<=[^\W\d_])\s+(?=\()", "", text)

    def after_square(m):
        content = m.group(1)
        letters = re.sub(r"[^\w]", "", content.replace("*", ""))
        bare = bool(letters) and letters[-1].lower() not in VOWELS and letters[-1] not in BARE_FINAL_MARKS
        return "[" + content + "]" + ("" if bare else m.group(2))
    text = re.sub(r"\[([^\]]*)\](\s+)(?=[^\W\d_])", after_square, text)
    text = re.sub(r"\(\s*\?\s*\)\s+(?=[^\W\d_])", "(?)", text)
    return text


LINE_END = re.compile(r"[-—–]\s*[.,;:]?$")


def _clean_line(line, flags, source=None):
    """R2, R3 and R5 on one printed line; returns the text with GAP tokens."""
    if "?" in line:
        flags["doubtful"] = True
    if re.search(r"\(\s*or\b", line):
        flags["doubtful"] = True
    flags["dropped_round"] += len(re.findall(r"\([^)]*\)", line))

    def inherent(m, content):
        """A dropped vowel after a bare consonant leaves the consonant's inherent a (R2)."""
        before = m.string[m.start() - 1] if m.start() else ""
        letters = re.sub(r"[^\w]", "", content.replace("*", ""))
        if before and before.isalpha() and before.lower() not in VOWELS and letters[:1].lower() in VOWELS:
            return "a"
        return ""
    if source in ROUND_IS_RESTORATION:
        def round_restored(m):
            content = m.group(1)
            if re.fullmatch(r"\s*\?\s*", content) or re.match(r"\s*or\b", content):
                return ""
            flags["restored"] = True
            return content.replace("?", "")
        line = re.sub(r"\(([^)]*)\)", round_restored, line)
    else:
        line = re.sub(r"\(([^)]*)\)", lambda m: inherent(m, m.group(1)), line)

    def square(m):
        content = m.group(1)
        if "*" in content:
            flags["omitted_supplied"] = True
            return inherent(m, content)
        flags["restored"] = True
        return content.replace("?", "")
    line = re.sub(r"\[([^\]]*)\]\*?", square, line)
    line = line.replace("*", "").replace("?", "")
    line = re.sub(r"(?:\.\s*){2,}|…+|[—–]", " " + GAP + " ", line)
    line = re.sub(r"[·'’‘\"“”]", "", line)  # raised dots and quotation marks are not letters
    return re.sub(r"[.,;:|/]", " ", line)


def read_legend(text, printed_lines, source):
    """Return the lines of words and the rule flags.

    `lines` lists words per printed line; a word broken at a line end (R4) sits whole in the line
    where it starts, and `breaks` gives every printed line break as (word index, prefix), so the
    caller can place a break inside a word in sign units.
    """
    flags = {"doubtful": False, "restored": False, "omitted_supplied": False,
             "gap_edge": False, "gap_internal": False, "joins": 0, "dropped_round": 0}
    if not text or not str(text).strip():
        return {**flags, "lines": [], "breaks": []}
    text = unicodedata.normalize("NFC", str(text))
    raw_lines = list(printed_lines) if printed_lines else text.split("\n")
    raw_lines = [unicodedata.normalize("NFC", x).strip() for x in raw_lines]
    raw_lines = [x for x in raw_lines if x]
    if source == "asi-ar-1911-12":
        raw_lines = [_marshall_spacing(x) for x in raw_lines]
    if source in ROUND_IS_RESTORATION:
        # Spooner sets his round brackets apart from the word they complete.
        raw_lines = [re.sub(r"(?<=[^\W\d_])\s+(?=\((?!\s*\?)[^\W\d_])", "", x) for x in raw_lines]
        raw_lines = [re.sub(r"(?<=\))\s+(?=[^\W\d_](?<![A-ZĀĪŪŚṢṆṬḌ]))", "", x) for x in raw_lines]
    # R2: supplied letters at the very start or end of the legend stand for letters lost at the
    # edge, unless they are only a visarga or anusvara, which engravers often omit.
    whole = " ".join(raw_lines)
    for m in re.finditer(r"\[([^\]]*)\]\*?", whole):
        content = m.group(1)
        starred = "*" in content or whole[m.end() - 1:m.end() + 1] == "]*"
        letters = re.sub(r"[^\w]", "", content.replace("*", ""))
        if not starred or not letters or set(letters.lower()) <= {"ḥ", "ṃ", "ṁ", "m"}:
            continue
        before = re.sub(r"\[[^\]]*\]", "", whole[:m.start()])
        after = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", whole[m.end():])
        if not re.search(r"[^\W\d_]", before) or not re.search(r"[^\W\d_]", after):
            flags["gap_edge"] = True
    broken = [bool(LINE_END.search(x)) and k + 1 < len(raw_lines) for k, x in enumerate(raw_lines)]
    cleaned = [_clean_line(LINE_END.sub("", x) if broken[k] else x, flags, source) for k, x in enumerate(raw_lines)]
    tokens = [t for line in cleaned for t in line.split()]
    letters = [i for i, t in enumerate(tokens) if t != GAP]
    for i, t in enumerate(tokens):
        if t == GAP:
            if not letters or i < letters[0] or i > letters[-1]:
                flags["gap_edge"] = True
            else:
                flags["gap_internal"] = True
    printed = [[w.strip("-") for w in line.split() if w != GAP] for line in cleaned]
    printed = [[w for w in line if w] for line in printed]
    # R4: a word continued at a line end joins the first word of the next printed line, also
    # across several lines; `breaks` lists every printed line break as (word index, prefix),
    # the prefix being the part of the word before the break, or None for a break between words.
    words, lines, breaks, continuing = [], [], [], False
    for k, ws in enumerate(printed):
        ws = list(ws)
        if continuing and ws and words:
            prefix = words[-1]
            words[-1] = prefix + ws.pop(0)
            lines[-1][-1] = words[-1]
            breaks.append((len(words) - 1, prefix))
            flags["joins"] += 1
        elif ws and words:
            breaks.append((len(words), None))
        if ws:
            lines.append(ws)
            words.extend(ws)
        continuing = broken[k] and bool(words)
    return {**flags, "lines": lines, "breaks": breaks}


def completeness_from(flags, entry):
    """Completeness of SCHEMA.md from the rule flags and the transcriber's fields."""
    if not flags["lines"]:
        return "illegible" if entry.get("illegible_part") or entry.get("legend_present") else "no-legend"
    if flags["gap_edge"]:
        return "damaged-edge"
    illegible = entry.get("illegible_part")
    if illegible and illegible is not True:
        if re.search(r"\b(first|last|beginning|end|edge|initial|final)\b", str(illegible).lower()):
            return "damaged-edge"
    if flags["gap_internal"] or illegible:
        return "damaged-internal"
    if flags["restored"] or entry.get("restored"):
        return "restored"
    return "complete"
