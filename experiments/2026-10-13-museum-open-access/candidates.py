"""Descriptive candidate search: local families compatible with a museum record.

A family is a candidate when its site is compatible (equal, or any site when the museum gives
none), its object type matches, its motif code is compatible with the museum's description,
its face size agrees within the tolerance on both axes (when both records give sizes) and,
when we counted signs on an open museum photograph, its longest face has that many signs
within the stated tolerance. Candidates are leads; they become joins only through the rules
in PROTOCOL.md.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/candidates.py SITE TYPE MOTIF W_MM H_MM SIGNS [TOL_MM] [SIGN_TOL]
    e.g. ... candidates.py Chanhu-daro SEAL:S unicorn 25 25 6
SITE may be 'any'; MOTIF one of the keys of MOTIFS or 'any'; sizes and SIGNS may be 0 for unknown.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lipi_index import brief, load  # noqa: E402

MOTIFS = {
    "unicorn": ("Bull1",),
    "short-horned bull": ("Gaur", "Bull", "Bull:i", "Bull2", "Bull3"),
    "zebu": ("Zebu",),
    "buffalo": ("Buff", "Buffalo"),
    "rhinoceros": ("Rhin",),
    "elephant": ("Elep",),
    "tiger": ("Tigr",),
    "goat": ("Goat", "Mark", "Ibex"),
    "none": ("None",),
    "scene": ("Scene", "Othr", "Mult"),
}


def fnum(x):
    try:
        return float(str(x).split("-")[0].strip())
    except ValueError:
        return 0.0


def search(site, typ, motif, w, h, signs, tol=2.0, sign_tol=0, fams=None):
    fams = fams or load()
    out = []
    for f in fams.values():
        if site != "any" and f["site"] != site:
            continue
        if typ != "any" and not str(f.get("type") or "").startswith(typ):
            continue
        sym = str(f.get("symbol") or "")
        if motif != "any" and not any(sym == m or sym.startswith(m + ":") or sym.startswith(m) for m in MOTIFS[motif]):
            continue
        fw, fh = fnum(f.get("h_mm")), fnum(f.get("v_mm"))
        size_ok = None
        if w and h and (fw or fh):
            dims = sorted([x for x in (fw, fh) if x])
            want = sorted([w, h])
            if len(dims) == 2:
                size_ok = abs(dims[0] - want[0]) <= tol and abs(dims[1] - want[1]) <= tol
            else:
                size_ok = any(abs(dims[0] - x) <= tol for x in want)
            if not size_ok:
                continue
        if signs and max(f["lengths"]) and abs(max(f["lengths"]) - signs) > sign_tol:
            continue
        out.append({**brief(f), "size_checked": size_ok})
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    res = search(a[0], a[1], a[2], float(a[3]), float(a[4]), int(a[5]),
                 float(a[6]) if len(a) > 6 else 2.0, int(a[7]) if len(a) > 7 else 0)
    for r in res:
        print(json.dumps(r, ensure_ascii=False))
    print(len(res), "candidates")
