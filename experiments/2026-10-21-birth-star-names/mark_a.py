"""Marker A: apply the stem table of MARKING-RULE.md to the extracted donor rows.

The Sanskrit equivalent decides when it carries a stem; otherwise the Prakrit name does.
Forms are compared as lowercase ASCII skeletons with sh -> s and ch -> c, which absorbs most
OCR damage to diacritics. Standard library only; run with python -I.
"""
import argparse
import csv
import re
import unicodedata
from pathlib import Path

HONORIFIC = re.compile(r"^(?:ayya|aya|arya|aryya|bhadamta|bhadanta|bhayamta)", re.I)

# Label, regex on the skeleton (anchored at the start of the name), ambiguous?
STEMS = [
    ("krittika", r"(?:krttik|krittik|kattik|katik|karttik|kartik)", False),
    ("krittika", r"bahul", True),
    ("rohini", r"(?:rohin|rohan|rauhin)", False),
    ("mrigashiras", r"(?:mrgasir|mrigasir|magasir|margasir|agrahayan)", False),
    ("ardra", r"(?:ardr|adda)", False),
    ("punarvasu", r"(?:punarvas|punavas|punabas|punabbas)", False),
    ("pushya", r"(?:pusy|pusa|pussa|phus|posa|posi|tisy|tisa|tissa|taisy|paus)", False),
    ("ashlesha", r"(?:asles|asesa|assesa|silesa)", False),
    ("magha", r"(?:magha|magh$)", True),
    ("phalguni", r"(?:phalgu|phagu|phaggu)", False),
    ("hasta", r"(?:hasta|hatha|hattha)", True),
    ("chitra", r"(?:citr|citta|cita|caitr)", True),
    ("svati", r"(?:svati|sati)", False),
    ("vishakha", r"(?:visakh|visah|vesakh|vaisakh)", False),
    ("anuradha", r"anuradh", False),
    ("jyeshtha", r"(?:jyes|jeth|jetth|jesth|jest)", True),
    ("mula", r"mula", True),
    ("ashadha", r"(?:asadh|asagh|asad)", False),
    ("abhijit", r"abhij", False),
    ("shravana", r"(?:sravan|savan)", True),
    ("shravishtha", r"(?:sravist|savith|savit|dhanist|dhanith)", False),
    ("shatabhishaj", r"satabhis", False),
    ("proshthapada", r"(?:prost|praust|pothay|pothap|bhadrapad|bhadapad|bhaddapad)", False),
    ("revati", r"(?:revat|raivat)", False),
    ("ashvini", r"(?:asvin|asvayuj|asini|assayuj)", False),
    ("bharani", r"bharan", False),
]
# Names the rule excludes although they begin like a stem.
EXCLUDE = re.compile(r"^(?:satakan|satavahan|satakarn|sataka|pusk|posath|tisar|cittak)")


def skeleton(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z]", "", s)
    s = HONORIFIC.sub("", s) if len(s) > 6 else s
    return s.replace("sh", "s").replace("ch", "c")


def mark(form):
    sk = skeleton(form)
    if not sk or EXCLUDE.match(sk):
        return None
    for label, pattern, ambiguous in STEMS:
        if re.match(pattern, sk):
            return label, ("ambiguous" if ambiguous else "strict"), sk
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    rows = list(csv.DictReader(args.rows.open(encoding="utf-8")))
    out = []
    for r in rows:
        hit, source = None, ""
        for field in ("sanskrit", "sanskrit_b"):
            # Lüders sometimes offers two Sanskrit equivalents joined by "or".
            options = re.split(r"\s+or\s+", r[field] or "")
            hits = [mark(o) for o in options]
            hit = next((h for h in hits if h), None)
            if hit:
                source = field
                if len(options) > 1 and not all(hits):
                    hit = (hit[0], "ambiguous", hit[2] + ";alternative")
                break
        # The rule: the Sanskrit equivalent decides when Lüders gives one. OCR often garbles it,
        # so a Prakrit stem still counts when both scans read the Prakrit name with that stem.
        has_sanskrit = any(len(skeleton(r[f])) >= 3 for f in ("sanskrit", "sanskrit_b"))
        if not hit:
            pa, pb = mark(r["name"]), mark(r["name_b"])
            if not has_sanskrit:
                hit, source = (pa, "name") if pa else (pb, "name_b")
            elif pa and pb and pa[0] == pb[0]:
                hit, source = pa, "name+name_b"
        out.append({"row_id": r["row_id"], "asterism": hit[0] if hit else "",
                    "strength": hit[1] if hit else "", "note": f"{source}:{hit[2]}" if hit else ""})
    with args.out.open("x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["row_id", "asterism", "strength", "note"])
        w.writeheader()
        w.writerows(out)
    print(sum(1 for o in out if o["asterism"]), "rows marked of", len(out))


if __name__ == "__main__":
    main()
