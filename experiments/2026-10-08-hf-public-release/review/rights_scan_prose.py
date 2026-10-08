"""Reviewer scan: do staged text strings reproduce runs of words from local third-party text?

Staged strings: every parquet string cell (JSON cells are parsed and their nested strings compared), every string value in the
release's JSON files, and the text of every release Markdown/CFF/NOTICE/LICENSE file. Bibliographic fields (titles, authors, venue,
URLs, locators, image paths) are excluded because a bibliographic title is allowed to match its source.

Witnesses: all text-like files (.txt .json .jsonl .html .htm .xml .md .csv .tsv .body .js .sql .log) under research/literature and under the
local raw directories of the evidence census, source recovery, dataset landscape, weight metrology, sign-context, connections, field
recommendations, byproduct inventory, chronology, backward chronology, resemblance baseline, object ledger and Helsinki digitization
packages, excluding Package O's own directories. This is about 0.4 GB, against 496 witnesses (focused-pass bodies, synthesis and weight
metrology text, Koskenniemi texts) in the package's own screen, which used 15-word windows. This scan uses 8-word windows.

Matches are written to the raw directory (they may contain third-party text); the summary written to review/ holds counts and locators only.

Run from the repository root:
  python -B experiments/2026-10-08-hf-public-release/review/rights_scan_prose.py
"""
import collections
import html
import json
import os
import re
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
REL = PKG / "release"
RAWOUT = ROOT / "data/raw/2026-10-08-hf-public-release/review-scan"
RAWOUT.mkdir(parents=True, exist_ok=True)
N = 8
SKIP = {"title", "authors", "authors_editors", "venue", "source_url", "url", "license", "source_locator", "source_file", "source_path",
        "input_pointer", "method_path", "image_path", "image_paths", "data_file", "museum_url", "evidence", "path"}
TOK = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def tokens(text):
    return TOK.findall(html.unescape(text).lower())


def strings(obj, key=""):
    if isinstance(obj, str):
        if key not in SKIP:
            yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v, key)


staged = []  # (locator, text)
for pf in sorted((REL / "data").glob("*.parquet")):
    t = pq.read_table(pf).to_pylist()
    for i, row in enumerate(t):
        for col, val in row.items():
            if col in SKIP:
                continue
            if isinstance(val, str):
                if col.endswith("_json") or val[:1] in "[{":
                    try:
                        for s in strings(json.loads(val)):
                            staged.append((f"{pf.name}[{i}].{col}", s))
                        continue
                    except Exception:
                        pass
                staged.append((f"{pf.name}[{i}].{col}", val))
            elif isinstance(val, list) and val and isinstance(val[0], str) and col not in SKIP:
                for s in val:
                    staged.append((f"{pf.name}[{i}].{col}", s))
for f in sorted(REL.rglob("*")):
    if not f.is_file():
        continue
    rel = f.relative_to(REL).as_posix()
    if f.suffix == ".json":
        try:
            for s in strings(json.loads(f.read_text(encoding="utf-8-sig"))):
                staged.append((rel, s))
        except Exception:
            staged.append((rel, f.read_text(encoding="utf-8", errors="replace")))
    elif f.suffix in (".md", ".cff", ".txt", ".py") or f.name in ("LICENSE", "NOTICE", "LICENSE-MIT"):
        staged.append((rel, f.read_text(encoding="utf-8-sig")))

windows = collections.defaultdict(set)
anchors = set()
n_tokens = 0
for loc, text in staged:
    ts = tokens(text)
    n_tokens += len(ts)
    for i in range(len(ts) - N + 1):
        w = tuple(ts[i:i + N])
        windows[w].add(loc)
        anchors.add(w[:2])
print("staged strings", len(staged), "tokens", n_tokens, "distinct 8-word windows", len(windows))

ROOTS = ["research/literature", "data/raw/2026-10-06-evidence-census", "data/raw/2026-10-02-source-recovery", "data/raw/2026-10-02-dataset-landscape",
         "data/raw/2026-10-06-weight-metrology", "data/raw/2026-10-06-sign-context-and-seals", "data/raw/2026-10-02-connections-and-priority",
         "data/raw/2026-10-06-field-recommendations", "data/raw/2026-10-06-byproduct-inventory", "data/raw/2026-10-06-chronology-region",
         "data/raw/2026-10-06-backward-chronology", "data/raw/2026-10-06-resemblance-baseline", "data/raw/2026-10-07-object-ledger",
         "data/raw/2026-10-07-helsinki1979-digitization", "data/raw/2026-10-08-helsinki1979-row-verification"]
EXTS = {".txt", ".json", ".jsonl", ".html", ".htm", ".xml", ".md", ".csv", ".tsv", ".body", ".js", ".sql", ".log"}
matches = []
nfiles = 0
nbytes = 0
for r in ROOTS:
    for dp, dn, fn in os.walk(ROOT / r):
        for f in fn:
            p = Path(dp) / f
            if p.suffix.lower() not in EXTS:
                continue
            try:
                size = p.stat().st_size
                if size > 200_000_000:
                    continue
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            nfiles += 1
            nbytes += size
            ts = tokens(re.sub(r"<[^>]+>", " ", text))
            seen = set()
            for i in range(len(ts) - N + 1):
                if (ts[i], ts[i + 1]) in anchors:
                    w = tuple(ts[i:i + N])
                    if w in windows and w not in seen:
                        seen.add(w)
                        matches.append(dict(witness=p.relative_to(ROOT).as_posix(), words=" ".join(w), staged=sorted(windows[w])))
print("witness files", nfiles, "bytes", nbytes, "matching windows", len(matches))

# group matches by staged location
by_loc = collections.Counter()
by_wit = collections.Counter()
for m in matches:
    for l in m["staged"]:
        by_loc[l.split("[")[0] if "[" in l else l] += 1
    by_wit[m["witness"]] += 1
(RAWOUT / "prose-8word-matches.json").write_text(json.dumps(matches, indent=1), encoding="utf-8")
summary = dict(window_words=N, staged_strings=len(staged), staged_tokens=n_tokens, distinct_windows=len(windows), witness_files=nfiles, witness_bytes=nbytes,
               matching_windows=len(matches), matches_by_staged_file=dict(by_loc.most_common(30)), matches_by_witness=dict(by_wit.most_common(15)))
(PKG / "review/rights-scan-prose.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
