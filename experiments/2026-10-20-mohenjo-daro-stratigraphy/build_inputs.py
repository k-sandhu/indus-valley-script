"""Build the discovery (Mackay 1938) and confirmation (Marshall 1931) object files.

One row per Lipi object family joined to a seal-table row, carrying the legend face
chosen by a fixed rule and the excavator's level. Rows with sign sequences are written
under data/raw/ (local only). The tracked summary holds counts and hashes.

The Marshall file is the input of this package's bench shots split. This script prints
only counts for it; no relation between Marshall texts and depth is computed here.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
JOIN = ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv"
EXPECTED = {
    "lipi_observed_faces.jsonl": "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def marshall_depth(text):
    """Marshall prints depth below the modern surface as 'N ft N in'. Returns feet or None."""
    m = re.fullmatch(r"(\d+) ft (\d+) in", text.strip())
    if m:
        return int(m.group(1)) + int(m.group(2)) / 12
    return None


def mackay_level(text, reference):
    """Mackay prints level in feet against the DK datum, or the SD bench mark 2.2 ft above it."""
    try:
        value = float(text)
    except ValueError:
        return None
    if reference.startswith("SD bench mark"):
        value += 2.2
    return value


def legend_face(faces):
    """Choose one legend per object: the longest complete text without unknown signs or
    blanks, then the longest text overall, then the lowest record id."""
    def key(f):
        clean = f["complete_observed"] and not f["has_unknown_sign"] and not f["has_blank_space"]
        return (clean, f["length"], [-int(x) if x.isdigit() else 0 for x in re.split(r"\D+", f["record_id"]) if x])
    return sorted(faces, key=key, reverse=True)[0]


def text_fields(face):
    signs = list(face["signs_reading_rtl"])
    complete = bool(face["complete_observed"]) and not face["has_blank_space"]
    ordered = complete and bool(face["single_line"])
    return {
        "signs": signs,
        "length": face["length"] if complete else None,
        "opening": signs[0] if ordered and signs and signs[0] != "000" else None,
        "closing": signs[-1] if ordered and signs and signs[-1] != "000" else None,
        "closing_pair": "-".join(signs[-2:]) if ordered and len(signs) >= 2 and "000" not in signs[-2:] else None,
        "clean": complete and not face["has_unknown_sign"],
        "ordered": ordered,
    }


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else PACKAGE / "inputs"
    if out_dir.exists():
        raise SystemExit(f"{out_dir} exists; write a new dated directory")
    if sha256(FACES) != EXPECTED["lipi_observed_faces.jsonl"]:
        raise SystemExit("Lipi face file hash changed")
    faces = [json.loads(line) for line in FACES.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_family = defaultdict(list)
    for f in faces:
        by_family[f["object_family_id"]].append(f)
    rows = list(csv.DictReader(JOIN.open(encoding="utf-8")))
    per_family = defaultdict(list)
    for r in rows:
        per_family[r["lipi_family_id"]].append(r)

    objects = {"mackay1938": [], "marshall1931": []}
    for fam, table_rows in sorted(per_family.items(), key=lambda kv: int(kv[0])):
        sources = {r["source"] for r in table_rows}
        if len(sources) != 1:
            raise SystemExit(f"family {fam} joined to both tables")
        source = sources.pop()
        levels = {r["level_ft"] for r in table_rows}
        first = sorted(table_rows, key=lambda r: r["catalogue_no"])[0]
        face = legend_face(by_family[fam])
        if source == "mackay1938":
            values = {mackay_level(r["level_ft"], r["level_reference"]) for r in table_rows}
        else:
            values = {(-marshall_depth(r["level_ft"]) if marshall_depth(r["level_ft"]) is not None else None)
                      for r in table_rows}
        height = values.pop() if len(values) == 1 else None
        strat = {
            "strat_source": source,
            "strat_catalogue_nos": sorted(r["catalogue_no"] for r in table_rows),
            "strat_area": first["area"],
            "strat_section": face["metadata"].get("area-section", ""),
            "strat_locus": first["locus"],
            "strat_level_raw": sorted(levels),
            "strat_datum": first["level_reference"],
            "strat_height_ft": height,
            "strat_surface": any(r["level_ft"].strip().lower() == "surface" for r in table_rows),
            "strat_seal_type": first["seal_type"],
        }
        row = dict(face)
        row["metadata"] = dict(face["metadata"], **strat)
        row["text"] = text_fields(face)
        objects[source].append(row)

    RAW.mkdir(parents=True, exist_ok=True)
    paths = {"mackay1938": RAW / "discovery-mackay1938.jsonl",
             "marshall1931": RAW / "confirmation-marshall1931.jsonl"}
    for source, path in paths.items():
        if path.exists():
            raise SystemExit(f"{path} exists; inputs are frozen")
        with path.open("x", encoding="utf-8", newline="\n") as f:
            for row in objects[source]:
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def counts(rows):
        seals = [r for r in rows if r["object_type"].startswith("SEAL")]
        with_height = [r for r in seals if r["metadata"]["strat_height_ft"] is not None]
        return {
            "objects": len(rows),
            "seals": len(seals),
            "seals_with_level": len(with_height),
            "seals_with_level_and_length": sum(r["text"]["length"] is not None for r in with_height),
            "seals_with_level_and_opening": sum(r["text"]["opening"] is not None for r in with_height),
            "seals_with_level_and_closing": sum(r["text"]["closing"] is not None for r in with_height),
            "surface_finds": sum(r["metadata"]["strat_surface"] for r in rows),
            "seals_with_level_by_area": dict(sorted(Counter(r["metadata"]["strat_area"] for r in with_height).items())),
            "object_types": dict(sorted(Counter(r["object_type"] for r in rows).items())),
        }

    summary = {
        "inputs": {"lipi_observed_faces.jsonl": sha256(FACES), "join-table.csv": sha256(JOIN)},
        "outputs": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in paths.values()},
        "mackay1938": counts(objects["mackay1938"]),
        "marshall1931": counts(objects["marshall1931"]),
        "rules": {
            "face": legend_face.__doc__.strip(),
            "height": "Mackay: level against the DK datum (SD bench mark rows +2.2 ft). Marshall: minus the depth below the modern surface. Larger is higher, so later in deposition.",
            "text": "length needs a complete legend without blanks; opening and closing also need a single line and a readable sign in that position; closing pair needs both last two signs readable.",
        },
    }
    out_dir.mkdir(parents=True)
    (out_dir / "inputs-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
