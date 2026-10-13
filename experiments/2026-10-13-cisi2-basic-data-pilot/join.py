"""Join transcribed CISI 2 basic-data rows to Lipi object families and measure coverage.

Usage (from the repository root):
  python -I experiments/2026-10-13-cisi2-basic-data-pilot/join.py <rows.jsonl>

<rows.jsonl> is a parsed transcription (parse.py output). Writes, in this directory,
coverage.json (aggregate counts) and object-flags.csv (per CISI number and Lipi family:
which fields each source supplies and the kind of any disagreement; no values). Writes the
value-level comparison to data/raw/2026-10-13-cisi2-basic-data-pilot/join-detail.jsonl
(local only). Usable-value rules are imported from the data inventory's coverage.py.
"""
import collections
import csv
import hashlib
import importlib.util
import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot"
LIPI = ROOT / "data/normalized/lipi_observed_faces.jsonl"
WEBSITE = ROOT / "data/normalized/indus_website_observed.jsonl"
LIPI_SHA256 = "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db"

spec = importlib.util.spec_from_file_location(
    "inventory_coverage", ROOT / "experiments/2026-10-12-data-inventory/coverage.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)

# Older-export museum prefixes mapped to the CISI 2 codes they correspond to.
WEBSITE_CODE_MAP = {"MJD": "MD", "MM": "MM", "LHR": "L", "NMK": "NMP", "NMP": "NMP", "HM": "HM", "HRP": "HM"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def base_key(raw):
    m = re.match(r"^\s*([A-Za-z?]+)-?\s*0*(\d+)", raw or "")
    return "%s-%s" % (m.group(1), m.group(2)) if m else None


def squash(text):
    return re.sub(r"[\s\-/.,\[\]]", "", text or "").upper()


def has_uncertain(text):
    return "[" in (text or "")


def website_pairs(value):
    """(code, number) pairs from an older-export MUSEUM string: a museum code of two to four
    capitals followed by a number, which may contain dots (an NMP accession)."""
    pairs = []
    for code, num in re.findall(r"\b([A-Z]{2,4})\s*([\d.]+[a-z]?)", value or ""):
        pairs.append((WEBSITE_CODE_MAP.get(code, code), num.replace(".", "")))
    return pairs


def cisi_pairs(row):
    pairs = []
    for piece in row["parsed"]["museum_holdings"]:
        for h in piece:
            code = h.get("code")
            if h.get("number"):
                pairs.append((code, re.sub(r"^(P|LU)-", "", h["number"]).replace(".", "").replace(" ", "")))
            if h.get("nmp_accession"):
                pairs.append(("NMP", h["nmp_accession"].replace(".", "")))
    return pairs


def expand(text):
    """Readings allowed by [a/b] brackets ('1[a/b]' -> {'1a', '1b'}); [?] gives none."""
    parts = re.split(r"(\[[^\]]*\])", text or "")
    options = []
    for part in parts:
        if part.startswith("["):
            if "?" in part:
                return set()
            options.append(part[1:-1].split("/"))
        else:
            options.append([part])
    return {"".join(c) for c in itertools.product(*options)}


def fc_tails(fc, allow_uncertain=False):
    """Digits that the Lipi string appends: the FC number without its first digit, with and
    without leading zeros (a four-digit FC number 1abc gives 'abc' and 'abc' stripped of
    leading zeros). Old-excavation FC numbers below 1000 append nothing. With allow_uncertain, every reading of a bracketed
    FC number contributes its tails."""
    if not fc or (has_uncertain(fc) and not allow_uncertain):
        return {""}
    tails = set()
    for reading in expand(fc):
        if not reading.isdigit() or reading.startswith("0"):
            tails.add("")
            continue
        rest = reading[1:]
        tails |= {rest, str(int(rest)) if int(rest) else ""}
    return tails or {""}


def strip_area(text):
    return re.sub(r"^[A-Z]+", "", text)


def compare_excavation(row, lipi_value, all_keys):
    """Classify the Lipi excavation-idno against the printed CISI 2 excavation number.

    all_keys maps each other entry's CISI number to its set of expected Lipi strings
    (printed number plus FC tail)."""
    printed = [e["printed"] for e in row["parsed"]["excavation"] if e["status"] == "printed"]
    if not printed or not lipi_value:
        return None
    if any(has_uncertain(p) for p in printed):
        return "cisi-cell-uncertain"
    lv = squash(lipi_value)
    fc = row["col2_fc"]
    tails = fc_tails(fc)
    for p in printed:
        pv = squash(p)
        if lv == pv:
            return "exact"
        if any(lv == pv + t for t in tails if t):
            return "lipi-adds-fc-tail"
        if any(strip_area(lv) == strip_area(pv) + t for t in tails):
            return "area-prefix-differs"
    if not re.search(r"[A-Z]", lv) or not re.search(r"\d{2}", strip_area(lv)):
        return "lipi-incomplete"
    for other, keys in all_keys.items():
        if other != row["cisi"] and lv in keys:
            return "matches-another-entry"
    if has_uncertain(fc):
        return "cisi-fc-uncertain"
    for p in printed:
        pv = squash(p)
        if lv.startswith(pv) and lv != pv:
            return "same-number-tail-differs"
        if any(t and lv.endswith(t) for t in tails):
            return "number-differs-tail-agrees"
    return "different"


def main():
    rows_path = Path(sys.argv[1]).resolve()
    rows = [json.loads(l) for l in rows_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    lipi_hash = sha256(LIPI)
    faces = [json.loads(l) for l in LIPI.read_text(encoding="utf-8").splitlines() if l.strip()]
    website = [json.loads(l) for l in WEBSITE.read_text(encoding="utf-8").splitlines() if l.strip()]

    fam_faces = collections.defaultdict(list)
    base_to_fams = collections.defaultdict(set)
    for f in faces:
        key = base_key(inv.norm(f["metadata"].get("cisi")))
        fam_faces[f["object_family_id"]].append(f)
        if key:
            base_to_fams[key].add(f["object_family_id"])
    fam_bases = {fam: {base_key(inv.norm(f["metadata"].get("cisi"))) for f in fs} for fam, fs in fam_faces.items()}
    museum_by_key = collections.defaultdict(set)
    for r in website:
        key = inv.norm(r.get("source_cisi"))
        m = inv.norm((r.get("metadata") or {}).get("MUSEUM"))
        if key and m and m.lower() not in inv.PLACEHOLDERS:
            museum_by_key[key].add(m)

    all_exc = {r["cisi"]: {squash(e["printed"]) + t for e in r["parsed"]["excavation"]
                           if e["status"] == "printed" and not has_uncertain(e["printed"])
                           for t in fc_tails(r["col2_fc"], allow_uncertain=True)} for r in rows}

    flags, details = [], []
    status_counts = collections.Counter()
    before = collections.Counter()
    after = collections.Counter()
    disagree = {"excavation": collections.Counter(), "museum": collections.Counter()}
    joined = 0
    for row in rows:
        fams = sorted(base_to_fams.get(row["cisi"], set()), key=int)
        if not fams:
            status_counts["no-lipi-family"] += 1
            flags.append({"cisi": row["cisi"], "lipi_family": "", "join": "no-lipi-family"})
            continue
        if len(fams) > 1 or any(len(fam_bases[f]) > 1 for f in fams):
            status_counts["ambiguous"] += 1
            flags.append({"cisi": row["cisi"], "lipi_family": ";".join(fams), "join": "ambiguous"})
            continue
        fam = fams[0]
        fs = fam_faces[fam]
        joined += 1
        status_counts["one-family"] += 1

        def any_usable(field):
            return any(inv.usable(field, f["metadata"].get(field)) for f in fs)

        lipi_exc = next((inv.norm(f["metadata"].get("excavation-idno")) for f in fs
                         if inv.usable("excavation-idno", f["metadata"].get("excavation-idno"))), None)
        keys = {inv.norm(f["metadata"].get("cisi")) for f in fs}
        web_museum = sorted({m for k in keys for m in museum_by_key.get(k, ())})
        b = {
            "excavation": bool(lipi_exc),
            "museum_number": bool(web_museum),
            "holding_institution": bool(web_museum),
            "fc_number": False,
            "findspot": any(any_usable(x) for x in ("area-section", "block-house", "room-grid")),
            "depth": any_usable("depth"),
            "material": any_usable("material"),
            "dimensions_any": any(any_usable(x) for x in inv.DIM_FIELDS),
            "dimensions_all3": all(any_usable(x) for x in inv.DIM_FIELDS),
        }
        p = row["parsed"]
        c = {
            "excavation": p["excavation_usable"],
            "museum_number": p["museum_number_usable"],
            "holding_institution": p["institution_usable"],
            "fc_number": bool(p["fc_number"]),
            "findspot": False, "depth": False, "material": False,
            "dimensions_any": False, "dimensions_all3": False,
        }
        a = {k: b[k] or c[k] for k in b}
        for k in b:
            before[k] += b[k]
            after[k] += a[k]
        exc_cmp = compare_excavation(row, lipi_exc, all_exc)
        if exc_cmp:
            disagree["excavation"][exc_cmp] += 1
        mus_cmp = None
        if web_museum and c["museum_number"]:
            wp = [pair for m in web_museum for pair in website_pairs(m)]
            cp = cisi_pairs(row)
            if any(has_uncertain(n) for _, n in cp) and not set(wp) & set(cp):
                mus_cmp = "cisi-cell-uncertain"
            elif set(wp) & set(cp):
                mus_cmp = "agree"
            elif {n for _, n in wp} & {n for _, n in cp}:
                mus_cmp = "same-number-different-code"
            else:
                mus_cmp = "different"
            disagree["museum"][mus_cmp] += 1
        flags.append({
            "cisi": row["cisi"], "lipi_family": fam, "join": "one-family",
            "lipi_faces": len(fs),
            **{"before_" + k: int(v) for k, v in b.items()},
            **{"cisi2_" + k: int(v) for k, v in c.items()},
            "excavation_comparison": exc_cmp or "",
            "museum_comparison": mus_cmp or "",
            "uncertain_columns": ";".join(row["uncertain_columns"]),
        })
        details.append({"cisi": row["cisi"], "lipi_family": fam, "lipi_excavation": lipi_exc,
                        "cisi_excavation": row["col3_excavation"], "fc": row["col2_fc"],
                        "website_museum": web_museum, "cisi_museum": row["col4_museum"],
                        "excavation_comparison": exc_cmp, "museum_comparison": mus_cmp})

    # Lipi families in the block's number range that have no transcribed row.
    nums = [int(r["cisi"].split("-")[1]) for r in rows]
    lo, hi = min(nums), max(nums)
    in_range = {k for k in base_to_fams if k.startswith("M-") and lo <= int(k.split("-")[1]) <= hi}
    missing_rows = sorted(in_range - {r["cisi"] for r in rows}, key=lambda k: int(k.split("-")[1]))

    # Corpus-wide museum coverage (object level), reproducing the inventory's rule, and the
    # number of objects the block adds.
    corpus_museum = 0
    for fam, fs in fam_faces.items():
        if any(inv.norm(f["metadata"].get("cisi")) in museum_by_key for f in fs):
            corpus_museum += 1
    gained_museum = sum(1 for f in flags if f.get("join") == "one-family"
                        and f.get("cisi2_museum_number") and not f.get("before_museum_number"))
    corpus = {
        "objects": len(fam_faces),
        "museum_number_objects_before": corpus_museum,
        "museum_number_objects_added_by_block": gained_museum,
        "museum_number_objects_after": corpus_museum + gained_museum,
        "museum_percent_before": round(100 * corpus_museum / len(fam_faces), 1),
        "museum_percent_after": round(100 * (corpus_museum + gained_museum) / len(fam_faces), 1),
        "fc_number_objects_after": sum(1 for f in flags if f.get("cisi2_fc_number")),
    }

    out = {
        "corpus_level": corpus,
        "input_rows": str(rows_path.relative_to(ROOT)).replace("\\", "/"),
        "input_rows_sha256": sha256(rows_path),
        "lipi_faces_sha256": lipi_hash,
        "lipi_faces_hash_matches_inventory": lipi_hash == LIPI_SHA256,
        "rows": len(rows),
        "range": "M-%d to M-%d" % (lo, hi),
        "join_status": dict(status_counts),
        "lipi_families_in_range_without_row": missing_rows,
        "joined_objects": joined,
        "coverage_before": dict(before),
        "coverage_after": dict(after),
        "coverage_gain": {k: after[k] - before[k] for k in before},
        "coverage_before_percent": {k: round(100 * v / joined, 1) for k, v in before.items()},
        "coverage_after_percent": {k: round(100 * v / joined, 1) for k, v in after.items()},
        "cisi2_supplies": {k: sum(1 for f in flags if f.get("cisi2_" + k)) for k in before},
        "comparisons": {k: dict(v) for k, v in disagree.items()},
        "rules": {
            "join": "Lipi metadata cisi, whitespace-normalized, base number (prefix and digits without leading zeros) equals the printed CISI number; one family per number, one number per family.",
            "before": "Lipi usable excavation-idno; older-export MUSEUM for the same raw CISI key (museum number and institution); Lipi area-section, block-house or room-grid (findspot); depth; material; positive millimetre dimensions; usable as in the data inventory.",
            "after": "before, or a usable value in the CISI 2 row: printed excavation number (not ???), a museum code with a number or NMP accession, a museum code, a four-digit FC number. CISI 2 prints no findspot, depth, material or dimension column.",
            "excavation_comparison": "exact: equal after removing spaces, hyphens, slashes, dots, commas and case; lipi-adds-fc-tail: the Lipi string is the printed number followed by the FC number without its first digit (with or without leading zeros); area-prefix-differs: the same after removing the leading letters of both; lipi-incomplete: the Lipi string lacks the area letters or the number; matches-another-entry: the Lipi string equals another entry's printed number plus FC tail; cisi-fc-uncertain: the FC cell is bracketed and no rule above applies; same-number-tail-differs: the Lipi string starts with the printed number but the appended digits differ from the FC tail; number-differs-tail-agrees: the appended digits match the FC tail but the number differs; different: none of these; cisi-cell-uncertain: the printed excavation cell has a bracketed character.",
            "museum_comparison": "agree: an older-export (code, number) pair equals a CISI 2 pair after mapping MJD to MD, LHR to L, NMK to NMP and removing dots and P- prefixes; same-number-different-code; different; cisi-cell-uncertain.",
        },
    }
    (HERE / "coverage.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    cols = sorted({k for f in flags for k in f}, key=lambda k: (k not in ("cisi", "lipi_family", "join"), k))
    with (HERE / "object-flags.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for f in flags:
            w.writerow(f)
    (LOCAL / "join-detail.jsonl").write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in details),
                                             encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("rows", "join_status", "coverage_before", "coverage_after", "comparisons")}, indent=1))


if __name__ == "__main__":
    main()
