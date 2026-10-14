"""Shared pipeline helpers. Import from the scripts in this directory; no CLI."""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data/raw/2026-10-13-cisi-basic-data-full"
PILOT = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot/final.jsonl"
LIPI = ROOT / "data/normalized/lipi_observed_faces.jsonl"
WEBSITE = ROOT / "data/normalized/indus_website_observed.jsonl"
TABLE_JOIN = ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv"
SOURCE_SETS = ROOT / "experiments/2026-10-13-data-round-1-verification/combined-coverage-post-fix.json"
COLS = ["col1", "col2_fc", "col3_excavation", "col4_museum", "col5_photographs"]
SHORT = ["col1", "col2", "col3", "col4", "col5"]
# "both-consistent": both readings bracket the decided reading among their candidates, so neither is an error.
OUTCOMES = ["first-pass-right", "second-pass-right", "both-consistent", "both-wrong", "undecidable"]
RECHECK_OUTCOMES = ["confirmed", "corrected", "ambiguous", "source-defect"]


def inventory():
    spec = importlib.util.spec_from_file_location(
        "full_cisi_inventory", ROOT / "experiments/2026-10-12-data-inventory/coverage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INV = inventory()


def ws(value):
    return re.sub(r"\s+", " ", str(value if value is not None else "")).strip()


def uncertain(value):
    return "[" in (value or "")


def consistent(reading, truth):
    """Bracket candidates include truth; question marks inside brackets are wildcards."""
    if reading is None or truth is None:
        return reading is truth
    pattern = []
    for part in re.split(r"(\[[^\]]*\])", ws(reading)):
        if part.startswith("[") and part.endswith("]"):
            inner = part[1:-1]
            alternatives = inner.split("/")
            if "?" in inner:
                pattern.append(".*")
            else:
                pattern.append("(?:" + "|".join(re.escape(x) for x in alternatives) + ")")
        else:
            pattern.append(re.escape(part))
    return re.fullmatch("".join(pattern), ws(truth)) is not None


def column(value):
    if value in COLS:
        return SHORT[COLS.index(value)]
    if value in SHORT or value == "row":
        return value
    raise ValueError("invalid column name")


def identity(cell):
    # The catalogue sometimes prints a full stop for the hyphen (M.146) and readers write a
    # number printed inside square brackets with braces ({H-356}); both identify the entry.
    m = re.match(r"^\s*\{?([A-Za-z?]+)(?:[-.]|\[[-./]+\])\s*(\d+)([a-zA-Z]?)\}?(?=\s|/|\(|\}|$)", cell)
    if not m:
        raise ValueError("column 1 needs a definite CISI identifier before alignment")
    return f"{m[1]}-{int(m[2])}{m[3]}"


def base_key(raw):
    m = re.match(r"^\s*\{?([A-Za-z?]+)(?:[-.]|\[[-./]+\])?\s*0*(\d+)", raw or "")
    return f"{m[1]}-{int(m[2])}" if m else None


def sort_key(key):
    m = re.match(r"^([A-Za-z?]+)-(\d+)(.*)$", key)
    return (m[1], int(m[2]), m[3]) if m else (key, 0, "")


def family_sort(key):
    return (0, int(key)) if str(key).isdigit() else (1, str(key))


def cells(line):
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 5:
        raise ValueError("entry must contain five cells")
    for p in parts:
        if p.count("[") != p.count("]"):
            raise ValueError("unbalanced uncertainty brackets")
    return parts


def local_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / "data/raw").resolve()):
        raise ValueError("value-bearing output must stay under data/raw")
    return path


def write_json(path, value, local=False):
    path = local_path(path) if local else Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path = local_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance(paths):
    return {k: {"path": Path(p).resolve().relative_to(ROOT).as_posix(), "sha256": sha256(p)}
            for k, p in paths.items() if Path(p).exists()}


def verify_inputs(inputs):
    for entry in inputs.values():
        if sha256(ROOT / entry["path"]) != entry["sha256"]:
            raise ValueError("input changed during processing: " + entry["path"])


def records(path):
    value = load_json(path)
    value = value.get("items") if isinstance(value, dict) else value
    if not isinstance(value, list):
        raise ValueError("decision file must contain a list or an items list")
    return value


def arguments(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--out", type=Path, default=HERE, help="count-only reports directory")
    ap.add_argument("--blocks", type=Path, default=HERE / "blocks.json")
    ap.add_argument("--block", action="append", default=[], help="select block; repeat as needed")
    ap.add_argument("--allow-partial", action="store_true", help="explicitly permit unfinished blocks")
    return ap


def block_list(args):
    specs = load_json(args.blocks)
    if args.block:
        unknown = set(args.block) - {b["block"] for b in specs} - {"cisi1-corrigenda", "cisi2-corrigenda"}
        if unknown:
            raise ValueError("unknown block identifiers: " + ", ".join(sorted(unknown)))
        specs = [b for b in specs if b["block"] in args.block]
    for v in ("cisi1", "cisi2"):
        name = v + "-corrigenda"
        if not args.block or name in args.block:
            specs.append({"block": name, "volume": v, "kind": "corrigenda", "strips": 0})
    return specs


def read_times(comments):
    starts, finishes = [], []
    invalid = 0
    for comment in comments:
        m = re.match(r"#\s*(started|finished)\s*:?[ \t]+(.+)", comment, re.I)
        if not m:
            continue
        stamp = m[2].strip().replace(" UTC", "+00:00").replace("Z", "+00:00")
        try:
            value = dt.datetime.fromisoformat(stamp)
        except ValueError:
            invalid += 1
            continue
        (starts if m[1].lower() == "started" else finishes).append(value)
    elapsed = 0
    pairs = 0
    for start, finish in zip(starts, finishes):
        try:
            seconds = (finish - start).total_seconds()
        except TypeError:
            invalid += 1
            continue
        if seconds < 0:
            invalid += 1
        else:
            elapsed += seconds
            pairs += 1
    return {"seconds": elapsed if pairs else None, "minutes": round(elapsed / 60, 3) if pairs else None,
            "paired_sessions": pairs, "unpaired_markers": abs(len(starts) - len(finishes)),
            "invalid_markers_or_intervals": invalid}


def read_pass(path, corrigenda=False):
    """Collapse exact overlap duplicates and combine explicitly distinguished pieces."""
    comments, rows, order, variants, positions = [], {}, [], collections.defaultdict(list), {}
    sites, page, pdf, current_site = {}, None, None, None
    component_rows = collections.defaultdict(set)
    row_comments = collections.defaultdict(list)
    duplicate_exact = piece_lines = 0
    entries = 0
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            comments.append(line)
            mp, md = re.search(r"p\.\s*(\d+)", line), re.search(r"PDF\s*(\d+)", line)
            page = int(mp[1]) if mp and page is None else page
            pdf = int(md[1]) if md and pdf is None else pdf
            ms = re.match(r"#\s*site\s*:\s*(.+)", line, re.I)
            if ms:
                current_site = ms[1].strip()
            if order and re.match(r"#\s*continu(?:es|ed)\b", line, re.I):
                row_comments[order[-1]].append(line)
            continue
        try:
            cs = [line.strip()] if corrigenda else cells(line)
            if not corrigenda and re.fullmatch(r"\(\d+\)", cs[0]) and order:
                cs[0] = order[-1] + " " + cs[0]
            key = f"line-{entries + 1}" if corrigenda else identity(cs[0])
        except ValueError as e:
            raise ValueError(f"{Path(path).name}:{lineno}: {e}") from None
        entries += 1
        signature = tuple(ws(c) for c in cs)
        if signature in component_rows[key]:
            duplicate_exact += 1
            continue
        component_rows[key].add(signature)
        if key not in rows:
            rows[key] = cs
            order.append(key)
            positions[key] = entries - 1
            sites[key] = current_site
        elif [ws(x) for x in rows[key]] == [ws(x) for x in cs]:
            duplicate_exact += 1
        else:
            old_marks = re.findall(r"\((\d+)\)", rows[key][0])
            new_marks = re.findall(r"\((\d+)\)", cs[0])
            if old_marks and new_marks and not set(old_marks) & set(new_marks) and not variants[key]:
                if list(map(int, old_marks + new_marks)) != sorted(map(int, old_marks + new_marks)):
                    variants[key].append(cs)
                else:
                    extra = re.sub(r"^\s*[A-Za-z?]+-\s*\d+[a-zA-Z]?\s*", "", cs[0])
                    rows[key] = [rows[key][0] + " // " + extra] + [a + " // " + b for a, b in zip(rows[key][1:], cs[1:])]
                    piece_lines += 1
            elif cs not in variants[key]:
                variants[key].append(cs)
    return {"rows": rows, "order": order, "comments": comments, "page": page, "pdf": pdf,
            "sites": sites, "positions": positions, "input_entry_lines": entries,
            "variants": {k: v for k, v in variants.items() if v},
            "duplicates_exact": duplicate_exact, "piece_lines_combined": piece_lines,
            "reading_time": read_times(comments), "row_comments": dict(row_comments)}


def likely_strips(spec, key, passes):
    """Approximate location from order, with a neighbouring strip on each side."""
    count = spec.get("strips", 0)
    if not count:
        return []
    indices = set()
    for p in passes:
        if key in p["positions"]:
            relative = p["positions"][key] / max(1, p["input_entry_lines"])
            center = min(count, int(relative * count) + 1)
            indices.update(range(max(1, center - 1), min(count, center + 1) + 1))
    return [f"data/raw/2026-10-13-cisi-basic-data-full/strips/{spec['block']}/s{i:02d}.png"
            for i in sorted(indices)]


def load_merged(raw, require_both=True):
    rows = []
    for v in ("cisi1", "cisi2"):
        path = Path(raw) / f"{v}-basic-data.jsonl"
        if not path.exists():
            if require_both:
                raise ValueError("missing merged volume: " + v)
            continue
        rows.extend(dict(r, volume=v) for r in load_jsonl(path))
    # CISI 1 prints a few pointers to entries of CISI 2: a catalogue number in square brackets
    # ("{H-356}", a cross-reference row) and "deleted, see vol. 2" (M-595). They describe no
    # object of their own and are left out of joins and coverage.
    rows = [r for r in rows if not (r["volume"] == "cisi1" and (
        str(r.get("col1", "")).lstrip().startswith("{") or re.search(r"\bdeleted\b", str(r.get("col2_fc", "")), re.I)))]
    seen = set()
    for row in rows:
        if row["cisi"] in seen:
            raise ValueError("duplicate CISI identifier across volumes: " + row["cisi"])
        seen.add(row["cisi"])
    return rows


def source_index(faces, website):
    families, by_base, museum = collections.defaultdict(list), collections.defaultdict(set), collections.defaultdict(set)
    for f in faces:
        fam = str(f["object_family_id"])
        families[fam].append(f)
        key = base_key(INV.norm(f["metadata"].get("cisi")))
        if key:
            by_base[key].add(fam)
    bases = {fam: {base_key(INV.norm(f["metadata"].get("cisi"))) for f in fs} for fam, fs in families.items()}
    for r in website:
        key = INV.norm(r.get("source_cisi"))
        value = INV.norm((r.get("metadata") or {}).get("MUSEUM"))
        if key and INV.usable("MUSEUM", value):
            museum[key].add(value)
    return {"families": families, "by_base": by_base, "bases": bases, "museum": museum}


def join_status(row, index):
    fams = sorted(index["by_base"].get(base_key(row["cisi"]), ()), key=family_sort)
    if not fams:
        return "no-lipi-family", fams
    if len(fams) > 1 or any(len(index["bases"][fam]) > 1 for fam in fams):
        return "ambiguous", fams
    return "one-family", fams


def table_rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main_guard(main):
    try:
        main()
    except (ValueError, FileNotFoundError) as e:
        raise SystemExit(str(e)) from None
