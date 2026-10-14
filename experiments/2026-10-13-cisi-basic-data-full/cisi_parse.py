"""Parse either volume's five printed cells without filling from another source.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/cisi_parse.py --volume cisi1 --out <local.jsonl> <pass.txt> [...]
Output JSONL and its .parse-report.json sidecar contain values and must be local.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from cisi_common import (COLS, identity, local_path, main_guard, read_pass,
                         uncertain, write_json, write_jsonl)

INSTITUTIONS = {
    "MD": "Moenjo-daro Museum (old accession numbers)",
    "MM": "Moenjo-daro Museum (new accession numbers)",
    "NMP": "National Museum of Pakistan, Karachi", "L": "Lahore Museum",
    "HM": "Harappa Museum", "EXB": "Excavation Branch, Department of Archaeology and Museums, Karachi",
    "KHP": "Khairpur University", "LF": "Office of the Northern Circle, Department of Archaeology and Museums, Old Fort, Lahore",
    "PC": "private collection", "PSW": "Department of Archaeology, University of Peshawar",
    "SM": "Swat Museum (Saidu Sharif)", "SS": "Swat Museum (Saidu Sharif)",
}
CISI1_CODES = {"ABD", "AI", "AM Trichur", "ASI", "ASI-EBS", "ASI-VC", "DAH", "DC Pune",
               "Hardwar", "IM", "KC", "KM", "KRI", "LCKN", "LTH", "MDS", "NMI", "PTN",
               "PWM", "Rohtak", "Sali", "Saraswati", "SRG"}
KNOWN_CODES = set(INSTITUTIONS) | CISI1_CODES
PHOTO_CODES = {"JL", "P", "Si.", "AV", "EL", "Pu.", "Aachen", "Vidale", "FEM", "DPhUH",
               "Jarrige", "Dales", "Fairservis", "Knox", "Stacul", "Brunswig", "ASI", "F.R. Allchin",
               "HU", "KVR", "EH", "CE", "MIC", "Rao", "Thapar", "Yule", "Allchin", "Baloch",
               "Casal", "CISI", "D&K", "Dani", "FC", "FdP", "Franke", "Khan", "LF", "Mahadevan",
               "PA", "VSI", "Wheeler"}
YEAR_ACC = re.compile(r"^\d{2}\.[\d\[\]/?]+$|^5[\d\[\]/]*\.[\d\[\]/?]+$")


def pieces(cell):
    return [p.strip() for p in re.split(r"\s*//\s*", cell)]


def excavation_numbers(text):
    """Split explicit separators and successive marked numbers, preserving each witness."""
    chunks = re.split(r"\s*[,;]\s*|\s+(?:and|&|/)\s+", text)
    out = []
    for chunk in chunks:
        marked = re.split(r"(?<=\))\s+(?=[A-Za-z\d])", chunk)
        for part in marked:
            # A fresh area code before a number also separates unpunctuated continuations.
            out.extend(p.strip() for p in re.split(r"\s+(?=[A-Za-z]+(?:[-/][A-Za-z]+)*[-\s]+[\d\[])", part) if p.strip())
    return out


def parse_excavation(cell):
    out = []
    for p in pieces(cell):
        rec = {"printed": p}
        if p in ("", "-", "--"):
            rec["status"] = "blank"
        elif p.startswith("???") or p == "?":
            rec["status"] = "not-available"
        else:
            rec["status"] = "printed"
            m = re.match(r"^([A-Za-z]+(?:[-/][A-Za-z]+)*)[-\s]", p)
            rec["area_code"] = m[1] if m else None
            rec["surface_find"] = "+" in p or "•" in p
            parentheses = re.findall(r"\(([^)]*)\)", p)
            rec["markers"] = [x for x in parentheses if x in ("o", "t")]
            rec["layer"] = next((x for x in parentheses if x not in ("o", "t")), None)
            rec["numbers"] = []
            for part in excavation_numbers(p):
                marker = re.search(r"\(([ot])\)", part)
                bare = re.sub(r"\s*\([ot]\)", "", part).strip()
                area = re.match(r"^([A-Za-z]+(?:[-/][A-Za-z]+)*)[-\s]", bare)
                rec["numbers"].append({"printed": part, "number_text": bare,
                                       "marker": marker[1] if marker else None,
                                       "area_code": area[1] if area else None})
        out.append(rec)
    return out


def number_shaped(text):
    return bool(text and (re.search(r"\d", text) or re.search(r"\[(?:\?+|[^\]]*\d[^\]]*)\]", text)))


def parse_museum(cell, volume="cisi2"):
    result = []
    for p in pieces(cell):
        text, former, now = p, False, None
        m = re.match(r"^\((.*)\)\s*now(?: in)?\s*:?\s*(.+?)\s*$", text, re.I)
        if m:
            former, text, now = True, m[1], m[2]
        holdings, pending, last_code = [], None, None
        for tok in [t.strip() for t in re.split(r"[,;]", text) if t.strip() and t.strip() not in ("-", "--", "???")]:
            query = tok.endswith("?") and not tok.endswith("]")
            clean = tok.rstrip(" ?").strip() if query else tok
            code, num = None, None
            for known in sorted(KNOWN_CODES, key=lambda x: (-len(x), x)):
                if clean == known or clean.startswith(known + " "):
                    code, num = known, clean[len(known):].strip() or None
                    break
            if code is None:
                # Generic leading institution, including multiword codes, followed by a number.
                mc = re.match(r"^([A-Za-z][A-Za-z.&/-]*(?:\s+[A-Za-z][A-Za-z.&/-]*)*)\s+(?=[\d\[])(.+)$", clean)
                if mc:
                    code, num = mc[1], mc[2]
                elif re.fullmatch(r"[A-Za-z][A-Za-z.&/-]*(?:\s+[A-Za-z][A-Za-z.&/-]*)*", clean):
                    code = clean
            if code:
                h = {"code": code, "number": num if number_shaped(num) else None,
                     "nmp_accession": None, "former": former, "query_mark": query,
                     "unknown_code": code not in KNOWN_CODES}
                if num and not number_shaped(num):
                    h["unparsed"] = num
                if num and (code == "NMP" or (volume == "cisi2" and YEAR_ACC.fullmatch(num))):
                    h["nmp_accession"] = num
                    if code != "NMP":
                        h["number"] = None
                holdings.append(h)
                pending = h if num is None else None
                last_code = code
            elif number_shaped(clean):
                if volume == "cisi2" and YEAR_ACC.fullmatch(clean):
                    if holdings:
                        holdings[-1]["nmp_accession"] = clean
                    else:
                        holdings.append({"code": None, "number": None, "nmp_accession": clean,
                                         "former": former, "query_mark": query})
                elif pending is not None:
                    pending["number"] = clean
                    pending = None
                else:
                    holdings.append({"code": last_code, "number": clean, "nmp_accession": None,
                                     "former": former, "query_mark": query})
            else:
                holdings.append({"code": None, "number": None, "nmp_accession": None,
                                 "former": former, "query_mark": query, "unparsed": tok})
        if now:
            holdings.append({"code": now, "number": None, "nmp_accession": None, "former": False,
                             "query_mark": False, "current": True, "unknown_code": now not in KNOWN_CODES})
        result.append(holdings)
    return result


def photo_codes(cell):
    return sorted(code for code in PHOTO_CODES
                  if re.search(r"(?<![A-Za-z])" + re.escape(code) + r"(?![A-Za-z])", cell))


def parse_line(line, page=None, pdf=None, volume="cisi2", site=None):
    from cisi_common import cells
    cs = cells(line)
    c1, c2, c3, c4, c5 = cs
    exc, mus = parse_excavation(c3), parse_museum(c4, volume)
    holdings = [h for part in mus for h in part]
    fc_readings = list(dict.fromkeys(p for p in pieces(c2) if p))
    fc = fc_readings[0] if len(fc_readings) == 1 else None
    if fc and (not re.fullmatch(r"[\d\[\]/?]+", fc) or (not uncertain(fc) and len(fc) != 4)):
        fc = None
    unknown_photos = sorted(set(re.findall(r"(?:^|[;:,]|//)\s*([A-Za-z][A-Za-z.&-]*)\s+(?=\d|\[)", c5)) - PHOTO_CODES)
    return {
        "cisi": identity(c1), "volume": volume, "site_heading": site,
        "printed_page": page, "pdf_page": pdf, "pieces": re.findall(r"\((\d+)\)", c1),
        **dict(zip(COLS, cs)), "uncertain_columns": [k for k, v in zip(COLS, cs) if uncertain(v)],
        "parsed": {
            "fc_number": fc,
            "excavation": exc, "excavation_usable": any(e["status"] == "printed" for e in exc),
            "museum_holdings": mus,
            "holding_institutions": sorted({INSTITUTIONS.get(h["code"], h["code"]) for h in holdings if h.get("code") and not h.get("former")}),
            "museum_number_usable": any(h.get("number") or h.get("nmp_accession") for h in holdings),
            "institution_usable": any(h.get("code") for h in holdings), "photo_sources": photo_codes(c5),
            "unknown_museum_codes": sorted({h["code"] for h in holdings if h.get("unknown_code")}),
            "unknown_photo_codes": unknown_photos,
            "unparsed_museum_fragments": [h["unparsed"] for h in holdings if h.get("unparsed")],
            "findspot": "not-printed", "depth": "not-printed", "material": "not-printed", "dimensions": "not-printed",
        },
    }


def parse_pass(path, volume):
    p = read_pass(path)
    if p["variants"]:
        raise ValueError("conflicting duplicate rows require adjudication: " + ", ".join(p["variants"]))
    return [parse_line(" | ".join(p["rows"][k]), p["page"], p["pdf"], volume, p["sites"].get(k)) for k in p["order"]]


def parser_report(rows):
    return [{"cisi": r["cisi"], "unknown_museum_codes": r["parsed"].get("unknown_museum_codes", []),
             "unknown_photo_codes": r["parsed"].get("unknown_photo_codes", []),
             "unparsed_museum_fragments": r["parsed"].get("unparsed_museum_fragments", [])}
            for r in rows if any(r["parsed"].get(k) for k in ("unknown_museum_codes", "unknown_photo_codes", "unparsed_museum_fragments"))]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--volume", choices=["cisi1", "cisi2"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("inputs", nargs="+", type=Path)
    args = ap.parse_args()
    local_path(args.out)
    rows = [r for path in args.inputs for r in parse_pass(path, args.volume)]
    write_jsonl(args.out, rows)
    write_json(args.out.with_suffix(".parse-report.json"), parser_report(rows), local=True)
    print(f"Parsed {len(rows)} rows; {len(parser_report(rows))} rows need parser review.")


if __name__ == "__main__":
    main_guard(main)
