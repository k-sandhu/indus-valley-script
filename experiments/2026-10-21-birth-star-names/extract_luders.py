"""Extract donor names from the OCR text of Lüders's 1912 List of Brahmi Inscriptions.

Each scan is parsed on its own. A donor occurrence is a personal name standing as the giver
in a "gift of" clause (PROTOCOL.md, Part 1). The two scans are then aligned entry by entry.
Standard library only. Run with python -I; the OCR files are untrusted input.
"""
import argparse
import csv
import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path

# Lowercase words that may stand between "gift of" and the donor's name.
KIN = {"mother", "father", "wife", "son", "sons", "daughter", "daughters", "sister", "brother",
       "pupil", "pupils", "disciple", "grandson", "granddaughter", "nephew", "niece", "husband",
       "daughter-in-law", "son-in-law", "mother-in-law", "companion", "family", "village", "town",
       "guild", "inhabitants", "people", "relatives", "congregation", "community", "members",
       "children", "friends", "servant", "slave", "heirs", "teacher", "attendant", "wives",
       "brothers", "sisters"}
STOP_BEFORE_NAME = {"from", "in", "at", "to", "for", "who", "whose", "which"}
# Capitalised words that describe the donor rather than name him or her.
CAP_ROLES = {"Buddhist", "Jaina", "Sakya", "Sakya-monk", "Brahman", "Brahmana", "Greek", "Yavana",
             "Saka", "Kshatrapa", "Mahakshatrapa", "Pallava", "Yona", "Kushana", "Prakrit",
             "Sanskrit", "Fragment", "Gift", "The", "A", "An"}
HONORIFIC = re.compile(r"^(?:Ayya|Aya|Arya|Aryya|Ayyaya|Bhadamta|Bhadanta|Bhayamta)-", re.I)
TOKEN = re.compile(r"\([^()]{0,80}\)|\{[^{}()]{0,80}[)}]|\[[^\]]{0,40}\]|[^\s()\[\]{},.;:]+|[,.;:]")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def list_portion(text):
    """Keep the list itself, up to the first index heading."""
    cut = text.find("INDEX OF PERSONAL NAMES")
    return text[:cut] if cut > 0 else text


def join_lines(text):
    text = text.replace("­", "")
    # A hyphen at a line end before a lowercase letter splits a word.
    text = re.sub(r"-\s*\n\s*(?=[a-zāīūṛṅñṭḍṇśṣéèê])", "", text)
    text = re.sub(r"-\s*\n\s*", "-", text)
    return re.sub(r"\s*\n\s*", " ", text)


HEADER = re.compile(r"(?m)^[ \t]*(\d{1,4})[\]\)]?[ \t]*[\.,][ \t]+(?:\((\d{3,4})\)\.?[ \t]+)?(?=[A-Z\"'‘“]|1[89]\d\d)")
ADDENDA = re.compile(r"(?m)^[ \t]*\d{2,4}\S{0,2}[ \t]*[\.,][ \t]*\((\d{4})\)")


def chain(cands):
    """Longest chain of headers whose numbers rise by 1 to 80 in text order."""
    best = [1] * len(cands)
    prev = [-1] * len(cands)
    for j in range(len(cands)):
        for i in range(j):
            if 1 <= cands[j][1] - cands[i][1] <= 80 and best[i] + 1 > best[j]:
                best[j], prev[j] = best[i] + 1, i
    j = max(range(len(cands)), key=lambda k: best[k]) if cands else -1
    out = []
    while j >= 0:
        out.append(cands[j])
        j = prev[j]
    return out[::-1]


def entries(raw):
    """Split the list into numbered entries along the longest rising chain of entry numbers."""
    body = list_portion(raw)
    cands = sorted({(m.start(), int(m.group(2) or m.group(1))) for m in HEADER.finditer(body)}
                   | {(m.start(), int(m.group(1))) for m in ADDENDA.finditer(body) if 1346 <= int(m.group(1)) <= 1460})
    marks = chain(cands)
    out = []
    for i, (pos, n) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        out.append((n, join_lines(body[pos:end])))
    return out


def is_name(tok):
    core = HONORIFIC.sub("", tok.strip("'‘’\"*"))
    return (len(core) >= 2 and core[0].isupper() and core not in CAP_ROLES
            and not core.isupper() or (len(core) >= 3 and core[:1].isupper() and core[1:].islower()))


OBJECT_START = re.compile(r"^(?:a|an|two|three|four|five|this|these|one|some)\s", re.I)


def donor_part(clause, by_only=False):
    """The words naming the giver: after 'by' when the clause first names an object."""
    sentence = re.split(r"(?<![A-Z][a-z])(?<!\b[A-Z])\.\s", clause[:400], maxsplit=1)[0]
    by = re.search(r"\bby\s+", sentence)
    if by_only or OBJECT_START.match(sentence):
        return sentence[by.end():] if by else None
    return clause


def parse_clause(clause, by_only=False):
    """Return (donors, other_names, status) for the words after 'gift of'."""
    part = donor_part(clause, by_only)
    if part is None:
        return [], [], "object-without-donor"
    toks = TOKEN.findall(part[:260])
    donors, others = [], []
    i, status, seen_object = 0, "no-name", False
    while i < len(toks):
        t = toks[i]
        if t in (".", ";", ":"):
            break
        if t.startswith(("(", "{", "[")):
            i += 1
            continue
        low = t.lower()
        if low == "by":
            seen_object = True
            i += 1
            continue
        if t[:1].islower() or t in ("&",):
            if low in KIN or low.rstrip("s") in KIN:
                # A relative or collective gives the gift; any later name is not the donor.
                status = "relative-or-collective"
                rest = " ".join(x for x in toks[i:i + 12] if not x.startswith(("(", "{", "[")))
                others += [w for w in rest.split() if w[:1].isupper() and w not in CAP_ROLES][:1]
                break
            if low in STOP_BEFORE_NAME and not seen_object:
                status = "no-personal-name"
                break
            i += 1
            continue
        if t == ",":
            if donors:
                break
            i += 1
            continue
        if t in CAP_ROLES:
            i += 1
            continue
        if is_name(t):
            name = HONORIFIC.sub("", t.strip("'‘’\"*"))
            skt = ""
            if i + 1 < len(toks) and toks[i + 1][:1] in "({" and len(toks[i + 1]) > 2 and toks[i + 1][1:2].isalpha() and toks[i + 1][1:2].isupper():
                skt = HONORIFIC.sub("", toks[i + 1][1:-1].strip())
                i += 1
            donors.append({"name": name, "sanskrit": skt})
            status = "named"
            # A second donor joined by "and", possibly after lowercase role words.
            j = i + 1
            if j < len(toks) and toks[j] == "and":
                j += 1
                while j < len(toks) and toks[j][:1].islower() and toks[j].lower() not in KIN and toks[j] not in ("her", "his", "their"):
                    j += 1
                while j < len(toks) and toks[j].startswith(("(", "{")):
                    j += 1
                if j < len(toks) and is_name(toks[j]) and toks[j] not in CAP_ROLES:
                    name2 = HONORIFIC.sub("", toks[j].strip("'‘’\"*"))
                    skt2 = ""
                    if j + 1 < len(toks) and toks[j + 1][:1] in "({" and toks[j + 1][1:2].isupper():
                        skt2 = HONORIFIC.sub("", toks[j + 1][1:-1].strip())
                    donors.append({"name": name2, "sanskrit": skt2})
            break
        i += 1
    return donors, others, status


def skeleton(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("sh", "s").replace("ch", "c").replace("ri", "r")
    return re.sub(r"[^a-z]", "", s)


def extract(path, label):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    rows, clauses = [], 0
    parsed = entries(raw)
    for n, text in parsed:
        head = re.sub(r"^\s*\d{1,4}\S*\s*[\.,]\s*(\(\d+\)\.?\s*)?(S\.\s*[\d.]+\s*[—-]+\s*)?", "", text)
        site = re.split(r"[.—–,(]| stone| Buddhist| Jaina| image| pillar| rail| cave", head, maxsplit=1)[0].strip()[:40]
        for k, m in enumerate(re.finditer(r"\b(?:[Gg]ift|[Dd]edication|[Ee]rection)\s+of\s+", text)):
            clauses += 1
            by_only = not m.group(0).lower().startswith("gift")
            donors, others, status = parse_clause(text[m.end():], by_only)
            context = text[max(0, m.start() - 20): m.end() + 160]
            base = {"scan": label, "entry": n, "clause": k, "pos": m.start(), "status": status,
                    "others": "|".join(others), "site_heading": site, "context": context}
            if not donors:
                rows.append(dict(base, slot=0, name="", sanskrit=""))
            for d, donor in enumerate(donors):
                rows.append(dict(base, slot=d, name=donor["name"], sanskrit=donor["sanskrit"]))
    return rows, clauses, len(parsed)


def needleman_wunsch(sa, sb, band=120):
    """Global alignment of two clause sequences; a pair scores its text similarity minus 0.5."""
    n, m = len(sa), len(sb)
    score = {(0, 0): 0.0}
    back = {}
    for i in range(n + 1):
        lo, hi = max(0, int(i * m / max(n, 1)) - band), min(m, int(i * m / max(n, 1)) + band)
        for j in range(lo, hi + 1):
            if i == 0 and j == 0:
                continue
            best, arg = -1e9, None
            if i > 0 and j > 0 and (i - 1, j - 1) in score:
                s = difflib.SequenceMatcher(None, sa[i - 1], sb[j - 1], autojunk=False).ratio() - 0.5
                if score[(i - 1, j - 1)] + s > best:
                    best, arg = score[(i - 1, j - 1)] + s, (i - 1, j - 1)
            if i > 0 and (i - 1, j) in score and score[(i - 1, j)] > best:
                best, arg = score[(i - 1, j)], (i - 1, j)
            if j > 0 and (i, j - 1) in score and score[(i, j - 1)] > best:
                best, arg = score[(i, j - 1)], (i, j - 1)
            if arg is not None:
                score[(i, j)], back[(i, j)] = best, arg
    pairs, cell = {}, (n, m)
    while cell in back:
        prev = back[cell]
        if prev == (cell[0] - 1, cell[1] - 1):
            pairs[prev[0]] = prev[1]
        cell = prev
    return pairs


def clause_groups(rows):
    groups, order = {}, []
    for r in rows:
        k = (r["entry"], r["clause"], r["pos"])
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(r)
    return [groups[k] for k in order]


def align(a_rows, b_rows):
    """Pair the gift clauses of the two scans by sequence alignment of their text."""
    ga, gb = clause_groups(a_rows), clause_groups(b_rows)
    sa = [skeleton(g[0]["context"][20:120]) for g in ga]
    sb = [skeleton(g[0]["context"][20:120]) for g in gb]
    pairs = needleman_wunsch(sa, sb)
    used_b = set(pairs.values())
    out = []
    for i, g in enumerate(ga):
        other = gb[pairs[i]] if i in pairs else []
        for d, r in enumerate(g):
            o = other[d] if d < len(other) else None
            na, nb = skeleton(r["name"]), skeleton(o["name"]) if o else ""
            ratio = difflib.SequenceMatcher(None, na, nb).ratio() if na and nb else 0.0
            out.append(dict(r, entry_b=o["entry"] if o else "", name_b=o["name"] if o else "",
                            sanskrit_b=o["sanskrit"] if o else "", status_b=o["status"] if o else ("unpaired" if not other else "no-slot"),
                            context_b=o["context"] if o else "", name_similarity=round(ratio, 3)))
        for d in range(len(g), len(other)):
            o = other[d]
            out.append(dict({k: "" for k in g[0]}, scan="B-extra-slot", entry=g[0]["entry"], clause=g[0]["clause"], slot=d,
                            entry_b=o["entry"], name_b=o["name"], sanskrit_b=o["sanskrit"], status_b=o["status"],
                            site_heading=g[0]["site_heading"], context_b=o["context"], name_similarity=0.0))
    for j, g in enumerate(gb):
        if j not in used_b:
            for o in g:
                out.append(dict({k: "" for k in ga[0][0]}, scan="B-only", entry=o["entry"], clause=o["clause"], slot=o["slot"],
                                entry_b=o["entry"], name_b=o["name"], sanskrit_b=o["sanskrit"], status_b=o["status"],
                                site_heading=o["site_heading"], context_b=o["context"], name_similarity=0.0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-a", type=Path, required=True)
    ap.add_argument("--scan-b", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    a, ca, ea = extract(args.scan_a, "A")
    b, cb, eb = extract(args.scan_b, "B")
    merged = align(a, b)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(merged[0].keys()))
        w.writeheader()
        w.writerows(merged)
    named = [r for r in merged if r["status"] == "named" or r.get("status_b") == "named"]
    summary = {
        "inputs": {"scan_a": str(args.scan_a.name), "scan_a_sha256": sha256(args.scan_a),
                   "scan_b": str(args.scan_b.name), "scan_b_sha256": sha256(args.scan_b)},
        "script_sha256": sha256(__file__),
        "entries_parsed": {"A": ea, "B": eb}, "gift_clauses": {"A": ca, "B": cb},
        "rows": len(merged), "rows_with_a_donor_in_either_scan": len(named),
        "agreeing_names_similarity_ge_0.8": sum(r["name_similarity"] >= 0.8 for r in merged),
        "status_counts_A": {s: sum(r["status"] == s for r in merged) for s in sorted({r["status"] for r in merged})},
    }
    with args.summary.open("x", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
