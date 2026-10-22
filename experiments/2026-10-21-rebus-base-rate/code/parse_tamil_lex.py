"""Parse the DSAL pages of the University of Madras Tamil Lexicon (1924-1936) into JSONL.

For each entry we keep the Tamil-script headword, its romanisation, the
homograph index, the part of speech, the asterisk that the Lexicon prefixes to
words of foreign (mostly Sanskrit) origin, the English part of the definition
and the compound members. The Lexicon's romanisation separates compound members
with hyphens and writes a sandhi consonant between members as its own segment
("aṅkāṭi-k-kūli"); we drop those one-consonant segments and keep the members.

    python -I experiments/2026-10-21-rebus-base-rate/code/parse_tamil_lex.py
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
RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "tamil-lex"
OUT = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1" / "tamil-lex-entries.jsonl"

DIV_RE = re.compile(r"<div>\s*(.*?)</div>", re.S)
SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
VOWEL_RE = re.compile(r"[aāiīuūeēoōŭ]")


def strip_tags(s):
    return html.unescape(re.sub(r"</?[A-Za-z][^>]*>", "", s))


def english_gloss(body):
    s = re.sub(r"<tam>.*?</tam>", " ", body, flags=re.S)
    s = re.sub(r"<smallcap>.*?</smallcap>", " ", s, flags=re.S)
    s = strip_tags(s)
    s = re.sub(r"\[[^\[\]]*\]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if s.startswith("<"):
        m = re.search(r"\.\s+(?=[A-Z0-9])", s)
        s = s[m.end():] if m else ""
    s = re.sub(r"\([^()]*\)", " ", s)
    return re.sub(r"\s+", " ", s).strip(" ,;")


def members(translit):
    t = unicodedata.normalize("NFC", translit.strip())
    segs = [x for x in re.split(r"[-\s]+", t) if x]
    return [x for x in segs if VOWEL_RE.search(x)]


def parse_page(text, page):
    out = []
    for block in DIV_RE.findall(text):
        if "<hw>" not in block:
            continue
        star = bool(re.match(r"\s*(?:<span[^>]*>)?\s*\*", block))
        hw = re.search(r"<hw>(.*?)</hw>", block, re.S)
        if not hw:
            continue
        tam = re.search(r"<tam>(.*?)</tam>", hw.group(1), re.S)
        tr = re.search(r"<t>(.*?)</t>", hw.group(1), re.S)
        if not tam or not tr:
            continue
        head = strip_tags(tam.group(1)).strip()
        hom = "".join(c for c in head if c in SUPERSCRIPTS)
        head = "".join(c for c in head if c not in SUPERSCRIPTS)
        translit = strip_tags(tr.group(1)).strip()
        rest = block[hw.end():]
        pos = re.search(r"<pos>(.*?)</pos>", rest, re.S)
        body = rest[pos.end():] if pos else rest
        body = re.sub(r"^\s*</i>\s*\.?", "", body)
        out.append({
            "page": page, "head": unicodedata.normalize("NFC", head), "hom": hom,
            "translit": unicodedata.normalize("NFC", translit), "star": star,
            "pos": strip_tags(pos.group(1)).strip() if pos else None,
            "members": members(translit),
            "verb": translit.endswith("-") or head.endswith("தல்"),
            "gloss": english_gloss(body)[:600],
            "tamil_text": " ".join(strip_tags(x) for x in re.findall(r"<tam>(.*?)</tam>", body, re.S))[:2000],
        })
    return out


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pages = sorted(glob.glob(str(RAW / "page-*.html")))
    hasher = hashlib.sha256()
    n = 0
    with OUT.open("w", encoding="utf-8") as fh:
        for path in pages:
            page = int(Path(path).stem.split("-")[1])
            raw = Path(path).read_bytes()
            hasher.update(hashlib.sha256(raw).digest())
            for rec in parse_page(raw.decode("utf-8"), page):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
    print(json.dumps({"pages": len(pages), "entries": n, "pages_digest": hasher.hexdigest(),
                      "out": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    sys.exit(main())
