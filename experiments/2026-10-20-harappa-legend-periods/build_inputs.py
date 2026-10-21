"""Build the discovery and confirmation seal files for the Harappa legend-periods shot.

One row per Harappa seal family that carries a chronology label in the Lipi export,
with the legend face chosen by the rule of the Mohenjo-daro stratigraphy package and
the fields that place the seal in time:

- Vats stratum: M. S. Vats numbered the occupation strata of each mound from the top
  (Stratum I latest). The export prints the stratum in `phase` and a HARP period in
  `time` that it assigns to each stratum of each mound.
- HARP period: seals from the Harappa Archaeological Research Project (CISI numbers
  H-1521 to H-2583) carry a period label (3A, 3B, 3B/C, 3C) in `time`.

The confirmation population is every seal from Mound F with a Vats stratum: one mound,
one excavator, one label source. Mound F seals with a period label but no stratum are
held out of both populations. Every other labelled Harappa seal is discovery material.

Rows with sign sequences are written under data/raw/ (local only). The tracked summary
holds counts and hashes; for the confirmation file it prints only the counts the design
needs (frames and strata), never legends, formats or motifs against strata.

    python -P experiments/2026-10-20-harappa-legend-periods/build_inputs.py
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-20-harappa-legend-periods"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
FACES_SHA256 = "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db"

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
# Order of the export's HARP period labels, earliest first. Sub-phases keep their
# numbered order inside a period; 3B/C lies between 3B and 3C.
PERIOD_ORDER = {"Period 3A": 1.0, "Period 3B": 2.0, "Period 3B-1": 2.1, "Period 3B-2": 2.2,
                "Period 3B/C": 2.5, "Period 3": None, "Period 3C": 3.0, "Period 3C-1": 3.1,
                "Period 3C-2": 3.2, "Period 3C-3": 3.3, "Period 3C-4": 3.4, "Period 4": 4.0,
                "Period 5A": 5.1, "Period 5B": 5.2}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


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


def h_number(cisi):
    m = re.fullmatch(r"H-(\d+)[a-zA-Z]?", (cisi or "").strip())
    return int(m.group(1)) if m else None


def mound(area_section):
    a = (area_section or "").strip()
    for prefix, name in (("AB", "AB"), ("ET", "E"), ("EC", "E"), ("E", "E"), ("F", "F"), ("G", "G"),
                         ("H", "H"), ("J", "J"), ("D", "D"), ("C", "C")):
        if a.startswith(prefix):
            return name
    return "unknown"


def depth_ft(text):
    m = re.fullmatch(r"-?\s*(\d+(?:\.\d+)?)\.*\d*\s*(ft|FT)", (text or "").strip().replace("..", "."))
    if m:
        return float(m.group(1))
    return None


def chronology(face):
    m = face["metadata"]
    phase = m["phase"].strip()
    st = re.fullmatch(r"Stratum ([IVX]+)", phase)
    number = h_number(m["cisi"])
    harp = number is not None and 1521 <= number <= 2583
    period = m["time"].strip()
    if st:
        source = "vats_stratum"
    elif harp and period not in ("", "-"):
        source = "harp_period"
    elif period not in ("", "-"):
        source = "export_period_only"
    else:
        source = None
    return {
        "chron_source": source,
        "chron_mound": mound(m["area-section"]),
        "chron_frame_cell": (m["area-section"] or "").strip(),
        "chron_stratum": ROMAN[st.group(1)] if st else None,
        "chron_period_label": period if period not in ("", "-") else None,
        "chron_period_order": PERIOD_ORDER.get(period),
        "chron_depth_ft": depth_ft(m["depth"]),
        "chron_h_number": number,
        "chron_harp_range": harp,
    }


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else PACKAGE / "inputs"
    if out_dir.exists():
        raise SystemExit(f"{out_dir} exists; write a new dated directory")
    if sha256(FACES) != FACES_SHA256:
        raise SystemExit("Lipi face file hash changed")
    faces = [json.loads(line) for line in FACES.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_family = defaultdict(list)
    for f in faces:
        if f["site"] == "Harappa" and f["object_type"].startswith("SEAL"):
            by_family[f["object_family_id"]].append(f)

    groups = {"discovery": [], "confirmation": [], "held_out": [], "undated": []}
    for fam, members in sorted(by_family.items(), key=lambda kv: int(kv[0])):
        face = legend_face(members)
        chron = chronology(face)
        row = dict(face)
        row["metadata"] = dict(face["metadata"], **chron)
        row["text"] = text_fields(face)
        if chron["chron_source"] is None:
            groups["undated"].append(row)
        elif chron["chron_mound"] == "F" and chron["chron_source"] == "vats_stratum":
            groups["confirmation"].append(row)
        elif chron["chron_mound"] == "F" and chron["chron_source"] == "export_period_only":
            groups["held_out"].append(row)
        else:
            groups["discovery"].append(row)

    RAW.mkdir(parents=True, exist_ok=True)
    paths = {"discovery": RAW / "discovery-harappa-labelled.jsonl",
             "confirmation": RAW / "confirmation-mound-f-vats.jsonl"}
    for name, path in paths.items():
        if path.exists():
            raise SystemExit(f"{path} exists; inputs are frozen")
        with path.open("x", encoding="utf-8", newline="\n") as f:
            for row in groups[name]:
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def text_counts(rows):
        return {"families": len(rows),
                "with_length": sum(r["text"]["length"] is not None for r in rows),
                "with_opening": sum(r["text"]["opening"] is not None for r in rows),
                "with_closing": sum(r["text"]["closing"] is not None for r in rows)}

    disc = groups["discovery"]
    conf = groups["confirmation"]
    summary = {
        "inputs": {"lipi_observed_faces.jsonl": sha256(FACES)},
        "outputs": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in paths.values()},
        "harappa_seal_families": len(by_family),
        "families_by_group": {k: len(v) for k, v in groups.items()},
        "discovery": dict(text_counts(disc),
                          by_source_and_mound=dict(sorted(Counter(f"{r['metadata']['chron_source']}/{r['metadata']['chron_mound']}" for r in disc).items())),
                          object_types=dict(sorted(Counter(r["object_type"] for r in disc).items()))),
        "confirmation": dict(text_counts(conf),
                             by_frame_cell=dict(sorted(Counter(r["metadata"]["chron_frame_cell"] for r in conf).items())),
                             by_stratum=dict(sorted(Counter(r["metadata"]["chron_stratum"] for r in conf).items())),
                             stratum_to_period_label=sorted({(r["metadata"]["chron_stratum"], r["metadata"]["chron_period_label"]) for r in conf},
                                                            key=lambda x: -x[0])),
        "held_out": {"families": len(groups["held_out"]),
                     "reason": "Mound F seals with an export period label (3B/C) but no Vats stratum: same mound and excavator as the confirmation population, without its clock"},
        "rules": {
            "face": legend_face.__doc__.strip(),
            "confirmation": "Mound F (area-section beginning with F) and a Vats stratum in the phase field",
            "discovery": "every other Harappa seal family with a Vats stratum, a HARP period label or an export period label",
            "text": "length needs a complete legend without blanks; opening and closing also need a single line and a readable sign in that position; closing pair needs both last two signs readable.",
        },
    }
    out_dir.mkdir(parents=True)
    (out_dir / "inputs-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
