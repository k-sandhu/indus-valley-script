"""Reviewer scan: do staged tables contain sign sequences that match records of the unlicensed derivatives?

Unlicensed (or unresolved-rights) sequence sources compared against:
  data/normalized/lipi_observed_faces.jsonl, lipi_observed_parts.jsonl, lipi_clean_rtl_singleline.jsonl (no licence)
  data/normalized/mayig_faces.jsonl, mayig_lines.jsonl (MIT, CISI photo rights unresolved; codes P### -> ###)
  data/normalized/indus_website_observed.jsonl (GPL-3.0 upstream)

Staged sign-code sequences are collected from every parquet table and every JSON file in release/:
  1. unit sequences: strict candidate sets, shape-only sets, top-1 and top-5 template candidate sets
     from reference_json, prediction_json and reading_json (one set per drawn unit, in visual order);
  2. chart cell codes read in page/column/row order and in page/row/column order (rank and code);
  3. every list of three or more integers found anywhere in the parsed JSON (generic scan).
A hit is a run of >= 3 consecutive positions whose candidate set contains the corresponding Lipi/Mayig/website code,
in either reading direction. Candidate sets are matched by intersection, which is the most permissive reading.

Control: the same sets are shuffled within each sequence (30 shuffles) and re-scanned. Because the 1979 chart numbering and the
Lipi numbering are different code spaces, coincidental runs are expected at a measurable rate; copying would exceed it.

The summary written to review/ lists counts and staged-side locators only. Matched unlicensed sequences themselves stay in the raw
directory (data/raw/2026-10-08-hf-public-release/review-scan/), because the review directory is tracked.

Run from the repository root:
  python -B experiments/2026-10-08-hf-public-release/review/rights_scan_sequences.py
"""
import collections
import itertools
import json
import random
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
REL = PKG / "release"
NORM = ROOT / "data/normalized"
RAWOUT = ROOT / "data/raw/2026-10-08-hf-public-release/review-scan"
RAWOUT.mkdir(parents=True, exist_ok=True)
random.seed(20261008)


def to_int(tok):
    t = str(tok).strip()
    if t.startswith("P") and t[1:].isdigit():
        t = t[1:]
    return int(t) if t.isdigit() else None


# ---------- unlicensed sequence index ----------
SOURCES = {
    "lipi_faces": ("lipi_observed_faces.jsonl", "signs_visual_ltr"),
    "lipi_parts": ("lipi_observed_parts.jsonl", "signs_visual_ltr"),
    "lipi_clean": ("lipi_clean_rtl_singleline.jsonl", "signs_visual_ltr"),
    "mayig_faces": ("mayig_faces.jsonl", "signs_visual_ltr"),
    "mayig_lines": ("mayig_lines.jsonl", "signs_visual_ltr"),
    "indus_website": ("indus_website_observed.jsonl", "signs_visual_ltr"),
}
seqs = []        # list of (source, tuple)
seen = set()
for name, (fn, key) in SOURCES.items():
    n_records = 0
    for line in (NORM / fn).open(encoding="utf-8"):
        rec = json.loads(line)
        n_records += 1
        raw = rec.get(key) or []
        t = tuple(to_int(x) if to_int(x) is not None else -1 for x in raw)
        if len(t) >= 1 and (name.split("_")[0], t) not in seen:
            seen.add((name.split("_")[0], t))
            seqs.append((name.split("_")[0], t))
    print(name, n_records, "records")
print("distinct sequences by family:", collections.Counter(s for s, _ in seqs))

index = collections.defaultdict(list)  # 3-gram -> [(seq_id, pos)]
all_seqs = []
for fam, t in seqs:
    for direction, u in (("ltr", t), ("rtl", tuple(reversed(t)))):
        sid = len(all_seqs)
        all_seqs.append((fam, direction, u))
        for p in range(len(u) - 2):
            g = u[p:p + 3]
            if -1 in g:
                continue
            index[g].append((sid, p))
print("3-gram index:", len(index), "keys;", len(all_seqs), "directional sequences")


def runs(sets, cap=3000):
    """Maximal runs (>=3) of consecutive positions matching an unlicensed sequence. Returns list of (start, length, family, direction, sid)."""
    out = []
    n = len(sets)
    for i in range(n - 2):
        trip = sets[i:i + 3]
        if any(not s for s in trip):
            continue
        size = len(trip[0]) * len(trip[1]) * len(trip[2])
        if size > cap:
            continue
        for g in itertools.product(*trip):
            for sid, p in index.get(g, ()):
                fam, d, u = all_seqs[sid]
                if i > 0 and p > 0 and u[p - 1] in sets[i - 1]:
                    continue  # not maximal on the left
                length = 3
                while i + length < n and p + length < len(u) and u[p + length] in sets[i + length]:
                    length += 1
                out.append((i, length, fam, d, sid))
    return out


# ---------- staged sequences ----------
staged = []  # dicts: category, locator, sets


def add(category, locator, sets):
    if len(sets) >= 3:
        staged.append(dict(category=category, locator=locator, sets=[set(s) for s in sets]))


def unit_sets(units, kind):
    out = []
    for u in units:
        if kind == "strict":
            out.append(set(int(c) for c in u.get("strict_candidate_codes", []) or []))
        elif kind == "shape":
            out.append(set(int(c) for c in (u.get("shape_only_candidate_codes") or u.get("strict_candidate_codes") or [])))
        elif kind == "top1":
            a = u.get("alternatives") or []
            out.append(set(int(c) for c in a[0]["codes"]) if a else set())
        elif kind == "top5":
            a = u.get("alternatives") or []
            out.append(set(int(c) for x in a[:5] for c in x["codes"]))
    return out


generic_lists = []


def walk(obj, path, locator):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}/{k}", locator)
    elif isinstance(obj, list):
        if len(obj) >= 3 and all(isinstance(x, int) and not isinstance(x, bool) for x in obj):
            generic_lists.append((locator, path, obj))
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]", locator)
    elif isinstance(obj, str) and obj[:1] in "[{" and len(obj) > 2:
        try:
            walk(json.loads(obj), path, locator)
        except Exception:
            pass


# parquet tables
for pf in sorted((REL / "data").glob("*.parquet")):
    table = pf.stem
    rows = pq.read_table(pf).to_pylist()
    for ri, row in enumerate(rows):
        for col, val in row.items():
            if isinstance(val, str) and val[:1] in "[{":
                try:
                    obj = json.loads(val)
                except Exception:
                    continue
                loc = f"{table}[{ri}].{col}"
                if isinstance(obj, dict) and isinstance(obj.get("units"), list):
                    kinds = ["strict", "shape"] if col in ("reference_json", "reading_json") else (["top1", "top5"] if col == "prediction_json" else [])
                    for kd in kinds:
                        add(f"unit_{kd}:{table}.{col}", loc, unit_sets(obj["units"], kd))
                walk(obj, "", loc)
            elif isinstance(val, list) and val and all(isinstance(x, int) for x in val):
                if len(val) >= 3:
                    generic_lists.append((f"{table}[{ri}].{col}", "", val))

# chart cells in reading orders
chart = pq.read_table(REL / "data/chart_reference.parquet").to_pylist()
for field in ("code", "rank"):
    def cellset(r):
        return {r[field]} | set(r["alternatives" if field == "code" else "rank_alternatives"])
    by_col = collections.defaultdict(list)
    by_row = collections.defaultdict(list)
    for r in chart:
        by_col[(r["pdf_page"], r["column"])].append(r)
        by_row[(r["pdf_page"], r["row"])].append(r)
    for k, v in by_col.items():
        v.sort(key=lambda r: r["row"])
        add(f"chart_{field}_column_order", f"chart_reference page {k[0]} column {k[1]}", [cellset(r) for r in v])
    for k, v in by_row.items():
        v.sort(key=lambda r: r["column"])
        add(f"chart_{field}_row_order", f"chart_reference page {k[0]} row {k[1]}", [cellset(r) for r in v])
    ordered = sorted(chart, key=lambda r: (r["pdf_page"], r["column"], r["row"]))
    add(f"chart_{field}_global_order", "chart_reference all cells in page/column/row order", [cellset(r) for r in ordered])

# all JSON files in release
for jf in sorted(REL.rglob("*.json")):
    try:
        obj = json.loads(jf.read_text(encoding="utf-8-sig"))
    except Exception as e:
        print("unparsable", jf, e)
        continue
    walk(obj, "", str(jf.relative_to(REL)))

for loc, path, lst in generic_lists:
    add("generic_int_list", f"{loc}{path}", [{x} for x in lst])

# ---------- scan ----------
summary = collections.OrderedDict()
details = []
by_cat = collections.defaultdict(list)
for s in staged:
    by_cat[s["category"].split(":")[0] if s["category"].startswith("unit_") else s["category"]].append(s)

for cat, items in sorted(by_cat.items()):
    actual = collections.Counter()
    maxrun = 0
    families = collections.Counter()
    n_hit = {3: 0, 4: 0, 5: 0, 6: 0}
    skipped = 0
    for s in items:
        r = runs(s["sets"])
        if r:
            best = max(x[1] for x in r)
            maxrun = max(maxrun, best)
            for th in n_hit:
                if best >= th:
                    n_hit[th] += 1
            for x in r:
                families[x[2]] += 1
            details.append(dict(category=cat, staged_locator=s["locator"], staged_len=len(s["sets"]), best_run=best, families=sorted({x[2] for x in r}),
                                staged_sets=[sorted(x) for x in s["sets"][:20]],
                                matched=[dict(start=x[0], length=x[1], family=x[2], direction=x[3], unlicensed_seq=list(all_seqs[x[4]][2])) for x in r][:5]))
    # control: shuffle sets within each sequence
    ctrl = {3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}
    K = 30
    for _ in range(K):
        for s in items:
            sh = s["sets"][:]
            random.shuffle(sh)
            r = runs(sh)
            if r:
                best = max(x[1] for x in r)
                for th in ctrl:
                    if best >= th:
                        ctrl[th] += 1 / K
    summary[cat] = dict(sequences=len(items), total_positions=sum(len(s["sets"]) for s in items),
                        sequences_with_run_ge={str(k): v for k, v in n_hit.items()},
                        control_shuffled_expected_sequences_with_run_ge={str(k): round(v, 2) for k, v in ctrl.items()},
                        longest_run=maxrun, hit_runs_by_family=dict(families))
    print(cat, json.dumps(summary[cat]))

# whole-sequence equality of complete singleton staged reference rows with any unlicensed sequence (either direction)
fullset = {u for _, _, u in all_seqs}
sing = 0
equal = 0
for s in staged:
    if s["category"] == "unit_strict:benchmark_rows_v1.reference_json" or s["category"] == "unit_strict:benchmark_rows_v2.reference_json":
        if all(len(x) == 1 for x in s["sets"]):
            sing += 1
            if tuple(next(iter(x)) for x in s["sets"]) in fullset:
                equal += 1
summary["_complete_singleton_benchmark_reference_rows_equal_to_a_whole_unlicensed_sequence"] = dict(complete_singleton_rows=sing, equal=equal)
summary["_unlicensed_index"] = dict(distinct_sequences_by_family=dict(collections.Counter(f for f, _ in seqs)), directional_sequences=len(all_seqs), three_gram_keys=len(index))

# positive control: the scanner must find sequences that really are in the index, even when embedded in staged-like noise
pos = [t for _, t in seqs if len(t) >= 4 and -1 not in t]
random.shuffle(pos)
found = 0
tested = 0
for t in pos[:200]:
    sets = [{901}, {902}] + [{x} for x in t] + [{903}]
    r = runs(sets)
    tested += 1
    if any(x[1] >= len(t) for x in r):
        found += 1
summary["_positive_control_planted_unlicensed_sequences"] = dict(tested=tested, detected_in_full=found)
print("positive control:", tested, "planted sequences, detected in full:", found)
# candidate-set control: planted sequence in which two positions are replaced by 3-code sets that contain the true code
found2 = 0
for t in pos[:200]:
    sets = [{x} for x in t]
    sets[1] = {t[1], 5, 6}
    sets[-1] = {t[-1], 7, 8}
    r = runs(sets)
    if any(x[1] >= len(t) for x in r):
        found2 += 1
summary["_positive_control_with_ambiguous_positions"] = dict(tested=len(pos[:200]), detected_in_full=found2)
print("ambiguous-position positive control:", found2)

(PKG / "review/rights-scan-sequences.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
(RAWOUT / "sequence-hit-details.json").write_text(json.dumps(details, indent=1), encoding="utf-8")
print("hit detail records:", len(details))
print("complete singleton benchmark reference rows:", sing, "whole-sequence equal:", equal)
