"""Turn a hand transcription of CISI 2 basic-data rows into JSON records with parsed fields.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/parse.py <out.jsonl> <in.txt> [<in.txt> ...]

Input lines are `col1 | col2 | col3 | col4 | col5` as printed (see PROTOCOL.md); lines starting
with `#` are comments, and the first comment line must name the printed page as `p. NNN`
and the PDF page as `PDF NNN`. Piece lines of one entry are joined with ` // `. Uncertain
characters are written `[a/b]`, `[?]` or `[??]`.

The parsed fields are derived only from the printed cells. Findspot, depth, material and
dimensions have no column in the CISI 2 basic data and are set to "not-printed".
"""
import json
import re
import sys
from pathlib import Path

INSTITUTIONS = {
    "MD": "Moenjo-daro Museum (old accession numbers)",
    "MM": "Moenjo-daro Museum (new accession numbers)",
    "NMP": "National Museum of Pakistan, Karachi",
    "L": "Lahore Museum",
    "HM": "Harappa Museum",
    "EXB": "Excavation Branch, Department of Archaeology and Museums, Karachi",
    "KHP": "Khairpur University",
    "LF": "Office of the Northern Circle, Department of Archaeology and Museums, Old Fort, Lahore",
    "PC": "private collection",
    "PSW": "Department of Archaeology, University of Peshawar",
    "SM": "Swat Museum (Saidu Sharif)",
    "SS": "Swat Museum (Saidu Sharif)",
}
CODE_RE = r"(?:MD|MM|NMP|L|HM|EXB|KHP|LF|PC|PSW|SM|SS)"
NUM_RE = r"(?:P-[\d\[\]/?]+|LU-[\d\[\]/?]+|[\d\[\]/?.]+[a-zA-Z]?(?: (?:[A-Z]+|\[[A-Z/]+\]))?)"
YEAR_ACC = re.compile(r"^\d{2}\.[\d\[\]/?]+$|^\d{2}\.\[\?\?\]$|^5[\d\[\]/]*\.[\d\[\]/?]+$")
PHOTO_CODES = ["JL", "P", "Si.", "AV", "EL", "Pu.", "Aachen", "Vidale", "FEM", "DPhUH", "Jarrige",
               "Dales", "Fairservis", "Knox", "Stacul", "Brunswig", "ASI", "F.R. Allchin"]


def uncertain(cell):
    return "[" in cell


def pieces(cell):
    return [p.strip() for p in cell.split(" // ")]


def parse_excavation(cell):
    out = []
    for p in pieces(cell):
        rec = {"printed": p}
        if p in ("", "-"):
            rec["status"] = "blank"
        elif p.startswith("???"):
            rec["status"] = "not-available"
        else:
            rec["status"] = "printed"
            m = re.match(r"^([A-Za-z]+(?:[-/][A-Za-z]+)*)[-\s]", p)
            rec["area_code"] = m.group(1) if m else None
            rec["surface_find"] = ("+" in p) or ("•" in p)
            lay = re.search(r"\(([^)]*)\)", p)
            rec["layer"] = lay.group(1) if lay else None
        out.append(rec)
    return out


def parse_museum(cell):
    """Return one list of (code, number, nmp_accession, former) dicts per piece line."""
    result = []
    for p in pieces(cell):
        former = False
        now = None
        text = p
        m = re.match(r"^\((.*)\)\s*now(?: in)?:?\s*(\S+)\s*$", text)
        if m:
            former, text, now = True, m.group(1), m.group(2)
        holdings = []
        pending = None
        for tok in [t.strip() for t in text.split(",") if t.strip()]:
            tok_clean = tok.rstrip(" ?").strip()
            mc = re.match(r"^(%s)(?:\s+(%s))?$" % (CODE_RE, NUM_RE), tok_clean)
            if mc:
                code, num = mc.group(1), mc.group(2)
                acc = None
                if num and YEAR_ACC.match(num) and code != "NMP":
                    acc, num = num, None
                h = {"code": code, "number": num, "nmp_accession": acc, "former": former,
                     "query_mark": tok.endswith("?")}
                if code == "NMP" and num:
                    h["nmp_accession"] = num
                holdings.append(h)
                pending = h if num is None and acc is None else None
            elif re.match(r"^%s$" % NUM_RE, tok_clean):
                if YEAR_ACC.match(tok_clean):
                    if holdings:
                        holdings[-1]["nmp_accession"] = tok_clean
                    else:
                        holdings.append({"code": None, "number": None, "nmp_accession": tok_clean,
                                         "former": former, "query_mark": False})
                elif pending is not None:
                    pending["number"] = tok_clean
                    pending = None
                else:
                    holdings.append({"code": None, "number": tok_clean, "nmp_accession": None,
                                     "former": former, "query_mark": False})
            else:
                holdings.append({"code": None, "number": None, "nmp_accession": None, "former": former,
                                 "unparsed": tok, "query_mark": False})
        if now:
            holdings.append({"code": now, "number": None, "nmp_accession": None, "former": False,
                             "query_mark": False, "current": True})
        result.append(holdings)
    return result


def photo_codes(cell):
    found = []
    for code in PHOTO_CODES:
        pat = r"(?<![A-Za-z])" + re.escape(code) + r"(?![A-Za-z])"
        if re.search(pat, cell):
            found.append(code)
    return found


def parse_line(line, page, pdf):
    cols = [c.strip() for c in line.split(" | ")]
    if len(cols) != 5:
        raise ValueError("expected 5 columns: %r" % line)
    c1, c2, c3, c4, c5 = cols
    m = re.match(r"^([A-Za-z?]+-\d+[a-z]?)\s*(.*)$", c1)
    cisi = m.group(1)
    piece_marks = re.findall(r"\((\d+)\)", m.group(2))
    exc = parse_excavation(c3)
    mus = parse_museum(c4)
    holdings = [h for piece in mus for h in piece]
    with_number = [h for h in holdings if h.get("number") or h.get("nmp_accession")]
    rec = {
        "cisi": cisi,
        "printed_page": page,
        "pdf_page": pdf,
        "pieces": piece_marks,
        "col1": c1, "col2_fc": c2, "col3_excavation": c3, "col4_museum": c4, "col5_photographs": c5,
        "uncertain_columns": [n for n, c in (("col1", c1), ("col2_fc", c2), ("col3_excavation", c3),
                                             ("col4_museum", c4), ("col5_photographs", c5)) if uncertain(c)],
        "parsed": {
            "fc_number": c2 if re.match(r"^[\d\[\]/?]{4,}$", c2) else None,
            "excavation": exc,
            "excavation_usable": any(e["status"] == "printed" for e in exc),
            "museum_holdings": mus,
            "holding_institutions": sorted({INSTITUTIONS.get(h["code"], h["code"]) for h in holdings
                                            if h.get("code") and not h.get("former")}),
            "museum_number_usable": bool(with_number),
            "institution_usable": any(h.get("code") for h in holdings),
            "photo_sources": photo_codes(c5),
            "findspot": "not-printed",
            "depth": "not-printed",
            "material": "not-printed",
            "dimensions": "not-printed",
        },
    }
    return rec


def main():
    out = Path(sys.argv[1])
    rows = []
    for path in sys.argv[2:]:
        page = pdf = None
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            if line.startswith("#"):
                mp = re.search(r"p\. (\d+)", line)
                md = re.search(r"PDF (\d+)", line)
                if mp and page is None:
                    page, pdf = int(mp.group(1)), int(md.group(1))
                continue
            rows.append(parse_line(line, page, pdf))
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(out, len(rows))


if __name__ == "__main__":
    main()
