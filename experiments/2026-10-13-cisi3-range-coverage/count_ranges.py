"""Count local objects in the CISI number ranges that continue past CISI 1 and 2.

For each catalogue prefix whose CISI 1 and 2 range the evidence census measured,
every integer above the highest CISI 1 or 2 entry, up to the highest number the
pinned export carries, is counted as one slot of the later CISI volume that covers
the site. A slot is present when at least one local face cites it. The volumes
themselves are not held, so the slot bounds are inferred from the export.

Each absent slot is described by the object classes of the nearest present numbers
below and above it in the same range (pottery, seal-tablet or other); when they
agree the slot is labelled with that class, otherwise `mixed`.

Usage: python -P experiments/2026-10-13-cisi3-range-coverage/count_ranges.py --out <new tracked dir> --local <new local dir>
"""
import argparse
import csv
import hashlib
import json
import platform
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FACES = ROOT / "data" / "normalized" / "lipi_observed_faces.jsonl"
FACES_SHA256 = "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db"
CATALOGUE = ROOT / "experiments" / "2026-10-06-evidence-census" / "synthesis" / "catalogue-coverage.csv"
# Later volume covering each site, from the volume titles recorded for cisi-3-1 and cisi-3-2 in data/MANIFEST.json.
VOLUME = {"M": "CISI 3.1", "H": "CISI 3.1", "K": "CISI 3.2", "C": "CISI 3.2", "Ns": "CISI 3.2", "Rjd": "CISI 3.2"}
KEY = re.compile(r"^([A-Za-z]+)-(\d+)")
# Object classes from the first segment of the export's `type` code.
CLASS = {"POT": "pottery", "SEAL": "seal-tablet", "TAB": "seal-tablet", "TAG": "seal-tablet"}


def object_class(type_code):
    return CLASS.get((type_code or "").split(":")[0], "other")


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cisi12_ends():
    ends, sites = {}, {}
    with CATALOGUE.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            p = row["matching_prefix"]
            ends[p] = max(ends.get(p, 0), int(row["last"]))
            sites[p] = row["site"]
    return ends, sites


def read_faces():
    numbers = defaultdict(lambda: defaultdict(lambda: {"families": set(), "faces": 0, "classes": set()}))
    site_of = defaultdict(set)
    unparsed = defaultdict(int)
    families = set()
    faces = 0
    with FACES.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            faces += 1
            families.add(r["object_family_id"])
            ref = str(r.get("source_cisi") or "").strip()
            m = KEY.match(ref)
            if not m:
                unparsed[ref] += 1
                continue
            p, n = m.group(1), int(m.group(2))
            cell = numbers[p][n]
            cell["families"].add(r["object_family_id"])
            cell["faces"] += 1
            cell["classes"].add(object_class(r.get("object_type")))
            site_of[p].add(r.get("site") or "")
    return numbers, site_of, dict(unparsed), len(families), faces


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="new tracked output directory (counts and absent numbers)")
    ap.add_argument("--local", required=True, help="new local-only directory for the per-number table")
    args = ap.parse_args()
    out, local_out = Path(args.out), Path(args.local)
    for d in (out, local_out):
        if d.exists() and any(d.iterdir()):
            sys.exit(f"refusing to write into non-empty {d}")
    got = sha256(FACES)
    if got != FACES_SHA256:
        sys.exit(f"{FACES} has SHA256 {got}, expected {FACES_SHA256}")
    out.mkdir(parents=True, exist_ok=True)
    local_out.mkdir(parents=True, exist_ok=True)

    ends, census_sites = cisi12_ends()
    numbers, site_of, unparsed, n_families, n_faces = read_faces()

    ranges, slots, outside = [], [], []
    for p in sorted(numbers, key=lambda q: (-len(numbers[q]), q)):
        local = numbers[p]
        sites = ";".join(sorted(site_of[p]))
        if p not in ends:
            fams = set().union(*(c["families"] for c in local.values()))
            outside.append([p, sites, len(local), len(fams), sum(c["faces"] for c in local.values()),
                            min(local), max(local), "no CISI 1 or 2 range measured in the evidence census"])
            continue
        beyond = sorted(n for n in local if n > ends[p])
        if not beyond:
            continue
        first, last = ends[p] + 1, beyond[-1]
        fams, faces = set(), 0
        absent_context = {"pottery": 0, "seal-tablet": 0, "other": 0, "mixed": 0}
        for n in range(first, last + 1):
            cell = local.get(n)
            if cell:
                fams |= cell["families"]
                faces += cell["faces"]
                slots.append([p, n, 1, ";".join(sorted(cell["families"], key=int)), cell["faces"],
                              ";".join(sorted(cell["classes"])), "", "", ""])
                continue
            below = max((m for m in beyond if m < n), default=None)
            above = min(m for m in beyond if m > n)
            near = set(local[above]["classes"]) | (set(local[below]["classes"]) if below else set())
            context = near.pop() if len(near) == 1 else "mixed"
            absent_context[context] += 1
            slots.append([p, n, 0, "", 0, "", below or "", above, context])
        total = last - first + 1
        ranges.append({"prefix": p, "site": census_sites[p], "later_volume": VOLUME.get(p, "unassigned"),
                       "cisi12_last": ends[p], "slot_first": first, "slot_last": last, "slots": total,
                       "numbers_present": len(beyond), "numbers_absent": total - len(beyond),
                       "share_present": round(len(beyond) / total, 4), "families": len(fams), "faces": faces,
                       **{f"absent_between_{k}": v for k, v in absent_context.items()}})

    write_csv(out / "range-coverage.csv", list(ranges[0]), [list(r.values()) for r in ranges])
    # The per-number table carries Lipi object classes for present numbers, so it stays local.
    slots_path = local_out / "number-slots.csv"
    write_csv(slots_path, ["prefix", "number", "present", "object_family_ids", "faces", "classes",
                           "nearest_present_below", "nearest_present_above", "absent_context"], slots)
    write_csv(out / "absent-numbers.csv",
              ["prefix", "number", "nearest_present_below", "nearest_present_above", "absent_context"],
              [[s[0], s[1], s[6], s[7], s[8]] for s in slots if s[2] == 0])
    write_csv(out / "outside-measured-ranges.csv",
              ["prefix", "sites", "numbers", "families", "faces", "min_number", "max_number", "reason"], outside)

    by_volume = {}
    for r in ranges:
        counted = [k for k in r if k in ("slots", "numbers_present", "numbers_absent", "families", "faces")
                   or k.startswith("absent_between_")]
        v = by_volume.setdefault(r["later_volume"], {"prefixes": [], **{k: 0 for k in counted}})
        v["prefixes"].append(r["prefix"])
        for k in counted:
            v[k] += r[k]
    for v in by_volume.values():
        v["share_present"] = round(v["numbers_present"] / v["slots"], 4)

    summary = {
        "package": "experiments/2026-10-13-cisi3-range-coverage",
        "rule": ("For each prefix with a CISI 1 or 2 range in the census catalogue-coverage table, slots run from the "
                 "highest CISI 1 or 2 number plus one to the highest base number in the export; a slot is present when "
                 "a local face cites it. Letter suffixes are dropped (H-1951A counts as 1951). An absent slot takes the "
                 "object class of the nearest present numbers below and above it when they agree, otherwise mixed; "
                 "classes come from the first segment of the export's type code (POT pottery; SEAL, TAB, TAG "
                 "seal-tablet; anything else other)."),
        "inputs": {
            str(FACES.relative_to(ROOT)).replace("\\", "/"): got,
            str(CATALOGUE.relative_to(ROOT)).replace("\\", "/"): sha256(CATALOGUE),
        },
        "script_sha256": sha256(Path(__file__)),
        "local_number_slots": {str(slots_path).replace("\\", "/"): sha256(slots_path)},
        "python": platform.python_version(),
        "export_faces": n_faces,
        "export_families": n_families,
        "faces_without_parsable_cisi": sum(unparsed.values()),
        "unparsed_references": unparsed,
        "ranges": ranges,
        "by_volume": by_volume,
        "prefixes_outside_measured_ranges": len(outside),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for r in ranges:
        print(f"{r['prefix']:4} {r['later_volume']:9} {r['prefix']}-{r['slot_first']}..{r['slot_last']}: "
              f"{r['numbers_present']}/{r['slots']} present ({r['share_present']:.1%}), {r['faces']} faces; absent "
              + ", ".join(f"{k[15:]} {v}" for k, v in r.items() if k.startswith("absent_between_")))
    for k, v in by_volume.items():
        print(f"{k}: {v['numbers_present']}/{v['slots']} ({v['share_present']:.1%}); absent "
              + ", ".join(f"{c[15:]} {n}" for c, n in v.items() if c.startswith("absent_between_")))


if __name__ == "__main__":
    main()
