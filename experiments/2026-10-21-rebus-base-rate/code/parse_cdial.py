"""Parse the DSAL pages of Turner's Comparative Dictionary of the Indo-Aryan Languages into JSONL.

Each entry keeps its number, the Old Indo-Aryan headword (marked when Turner
reconstructs it with an asterisk), every quoted gloss outside the bracketed
etymological notes, the languages whose italic forms it cites, and the
Indo-Aryan zones those languages belong to. Zones follow the grouping in
Masica, The Indo-Aryan Languages (1991): Dardic, Northwestern, Pahari, Central,
Eastern, Southern and Romani. Old and Middle Indo-Aryan stages (Pali, Prakrit,
Apabhraṃśa, Aśokan) and other families are not counted as zones.

    python -I experiments/2026-10-21-rebus-base-rate/code/parse_cdial.py
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
RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "cdial"
OUT = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1" / "cdial-entries.jsonl"

ZONES = {
    "Dardic": ["K", "Sh", "Kho", "Kal", "Phal", "Tir", "Gaw", "Bshk", "Tor", "Mai", "Chil", "Gau", "Kand", "Kaṭ",
               "Dm", "Paš", "Pash", "Shum", "Sv", "Wot", "Gil", "Kohi"],
    "Northwestern": ["L", "S", "P", "OP", "EP", "Lahnda", "Hindk"],
    "Pahari": ["WPah", "Ku", "Garh", "N", "Nep", "J"],
    "Central": ["H", "OH", "Aw", "OAw", "Brj", "G", "OG", "Marw", "OMarw", "Mārw", "Raj", "Bhil", "Bhīl"],
    "Eastern": ["B", "OB", "MB", "Or", "OOr", "A", "OA", "Bi", "Bhoj", "Mth", "Mag", "OMth"],
    "Southern": ["M", "OM", "Ko", "Konk", "Si", "OSi", "Md", "Kon"],
    "Romani": ["Gy", "Rom"],
}
ZONE_OF = {a: z for z, abbrs in ZONES.items() for a in abbrs}
LANG_BEFORE_FORM = re.compile(r"(?<![A-Za-zāīūṛṭḍśṣ])([A-ZĀḌṬŚṢ][A-Za-zāīūēōṛḍṭśṣ]{0,5})\.\s*"
                              r"(?:\([^()<>]*\)\s*)?(?:[a-zāīūēōṛḍṭśṣ.]{1,8}\.\s*)*<i>")
ENTRY_RE = re.compile(r"<hw>\s*<number>(.*?)</number>(.*?)</span>", re.S)


def clean(s):
    return html.unescape(re.sub(r"</?[A-Za-z][^>]*>", "", s))


def parse_entry(num, body, page):
    head = re.search(r"(\*?)\s*<b>(.*?)</b>", body, re.S)
    head_form = clean(head.group(2)).strip() if head else ""
    reconstructed = bool(head and head.group(1))
    no_brackets = re.sub(r"\[[^\[\]]*\]", " ", body)
    glosses = [clean(g).strip() for g in re.findall(r"'([^'<>]{1,160})'", no_brackets)]
    langs = sorted({m.group(1) for m in LANG_BEFORE_FORM.finditer(no_brackets)})
    zones = sorted({ZONE_OF[l] for l in langs if l in ZONE_OF})
    forms = []
    for f in re.split(r"[,/]", head_form):
        f = unicodedata.normalize("NFC", f.strip().strip("-").strip())
        f = f.replace("r̥", "ṛ").replace("l̥", "ḷ")
        if f and not re.search(r"[A-Z]", f):
            forms.append(f)
    return {"num": num, "page": page, "head": head_form, "head_forms": forms, "reconstructed": reconstructed,
            "glosses": glosses, "langs": langs, "subgroups": zones}


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
            for num, body in ENTRY_RE.findall(raw.decode("utf-8")):
                fh.write(json.dumps(parse_entry(clean(num).strip(), body, page), ensure_ascii=False) + "\n")
                n += 1
    print(json.dumps({"pages": len(pages), "entries": n, "pages_digest": hasher.hexdigest(),
                      "out": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    sys.exit(main())
