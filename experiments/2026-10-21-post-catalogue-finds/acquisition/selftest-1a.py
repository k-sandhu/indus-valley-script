"""Verify acquisition pins, page references and sampled text exclusion."""
import argparse
import bisect
import collections
import csv
import hashlib
import json
import pathlib
import random
import re
import sys
import subprocess

sys.dont_write_bytecode = True


def hash_file(path):
    hs = {k: hashlib.new(k) for k in ("sha256", "md5", "sha1")}
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            for h in hs.values():
                h.update(b)
    return {k: v.hexdigest() for k, v in hs.items()}


def tokens(text):
    return re.findall(r"\w+", text.lower())


def main():
    ap = argparse.ArgumentParser()
    for name in ("root", "raw", "records"):
        ap.add_argument("--" + name, type=pathlib.Path, required=True)
    args = ap.parse_args()
    root, raw, records = args.root.resolve(), args.raw.resolve(), args.records.resolve()
    checks, errors = collections.Counter(), []
    data = json.loads((records / "manifest-proposals-1a.json").read_text(encoding="utf-8"))
    for e in data["sources"]:
        if e.get("status") != "held":
            checks["unacquired_assets"] += 1
            continue
        for rel in e.get("local_paths", []):
            path = root / rel
            if not path.exists():
                errors.append(dict(check="asset-missing", source_id=e["id"]))
                continue
            hs = hash_file(path)
            checks["acquired_assets_sha256_checked"] += 1
            if hs["sha256"] != e["hashes"][rel]:
                errors.append(dict(check="sha256", source_id=e["id"]))
            for alg in ("md5", "sha1"):
                pin = e["fetch"].get("archive_" + alg)
                if pin:
                    checks["archive_" + alg + "_checked"] += 1
                    if hs[alg] != pin:
                        errors.append(dict(check=alg, source_id=e["id"]))
    manifest = json.loads((root / "data/MANIFEST.json").read_text(encoding="utf-8"))
    pins = {}
    for e in manifest["sources"]:
        pins.update(e.get("hashes", {}))
    held = json.loads((records / "held-verification-1a.json").read_text(encoding="utf-8"))
    for e in held:
        path = root / e["local_path"]
        if not path.exists():
            errors.append(dict(check="held-missing", source_id=e["source_id"]))
            continue
        actual = hash_file(path)["sha256"]
        checks["held_sha256_checked"] += 1
        if actual != e["sha256"]:
            errors.append(dict(check="held-recorded-sha256", source_id=e["source_id"]))
        expected = pins.get(e["local_path"])
        if expected:
            checks["held_manifest_sha256_checked"] += 1
            if actual != expected:
                errors.append(dict(check="held-manifest-sha256", source_id=e["source_id"]))
        else:
            checks["held_without_manifest_pin"] += 1
    states = json.loads((records / "processing-summary-1a.json").read_text(encoding="utf-8"))
    with (records / "source-register-1a.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    state_by_id = {r["source_id"]: r for r in states}
    for row in rows:
        sid = row["source_id"]
        target = raw / "text" / sid
        checks["registered_sources"] += 1
        files = list(target.glob("p[0-9][0-9][0-9][0-9].txt"))
        if not target.is_dir():
            errors.append(dict(check="text-directory-missing", source_id=sid))
        n = int(row.get("pdf_pages") or 0)
        state = state_by_id[sid]
        if n != len(files):
            errors.append(dict(check="page-count", source_id=sid, expected=n, actual=len(files)))
        if not files:
            if state.get("text_reason"):
                checks["source_text_exceptions_recorded"] += 1
            else:
                errors.append(dict(check="text-exception-unrecorded", source_id=sid))
        if state.get("needs_ocr") or state.get("ocr_failed_pages") or not state.get("text_complete"):
            errors.append(dict(check="text-incomplete", source_id=sid))
        checks["page_files_checked"] += len(files)
        source_path = root / row.get("local_path", "")
        if source_path.suffix.lower() == ".pdf" and not state.get("no_sweep") and source_path.exists():
            result = subprocess.run(["pdfinfo", str(source_path)], capture_output=True, timeout=120)
            found = re.search(rb"^Pages:\s*(\d+)", result.stdout, re.M)
            checks["pdf_page_counts_checked"] += 1
            if not found or int(found[1]) != n:
                errors.append(dict(check="actual-pdf-page-count", source_id=sid))
    with (records / "candidate-pages-1a.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            path = raw / "text" / row["source_id"] / ("p" + str(int(row["pdf_page"])).zfill(4) + ".txt")
            checks["candidate_rows_checked"] += 1
            if not path.is_file():
                errors.append(dict(check="candidate-page-missing", source_id=row["source_id"], page=row["pdf_page"]))
    # Review all files in the tracked-output directory, including untracked additions.
    index = collections.defaultdict(set)
    index13 = collections.defaultdict(set)
    for path in records.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        words = tokens(path.read_text(encoding="utf-8", errors="replace"))
        checks["tracked_files_scanned"] += 1
        for i in range(max(0, len(words) - 11)):
            index[hashlib.sha256(" ".join(words[i:i+12]).encode()).digest()].add(path.name)
        for i in range(max(0, len(words) - 12)):
            index13[hashlib.sha256(" ".join(words[i:i+13]).encode()).digest()].add(path.name)
    allowed = set()
    bibliographic_values = []
    for row in rows:
        bibliographic_values.extend(str(row.get(k, "")) for k in ("title", "authors_or_editors", "year_or_volume"))
    for entry in data["sources"]:
        bibliographic_values.extend(str(entry.get(k, "")) for k in ("title", "authors_or_editors", "year_or_volume"))
    with (records / "new-site-leads-1a.csv").open(encoding="utf-8", newline="") as f:
        bibliographic_values.extend(row["heading_as_printed"] for row in csv.DictReader(f))
    for value in bibliographic_values:
        words = tokens(value)
        for i in range(max(0, len(words)-11)):
            allowed.add(hashlib.sha256(" ".join(words[i:i+12]).encode()).digest())
    rng = random.Random(20261021)
    leak_samples = []
    for row in rows:
        sid = row["source_id"]
        files = sorted((raw / "text" / sid).glob("p[0-9][0-9][0-9][0-9].txt"))
        page_words, cumulative, total = [], [], 0
        for path in files:
            words = tokens(path.read_text(encoding="utf-8"))
            windows = max(0, len(words)-11)
            if windows:
                page_words.append(words)
                total += windows
                cumulative.append(total)
        available = total
        chosen = rng.sample(range(available), min(200, available))
        checks["sources_sampled"] += bool(chosen)
        checks["random_12_word_windows_checked"] += len(chosen)
        matches = 0
        for offset in chosen:
            page_index = bisect.bisect_right(cumulative, offset)
            i = offset - (cumulative[page_index-1] if page_index else 0)
            words = page_words[page_index]
            key = hashlib.sha256(" ".join(words[i:i+12]).encode()).digest()
            if key in index:
                checks["sampled_12_word_matches"] += 1
                if key in allowed:
                    checks["allowed_bibliographic_or_heading_matches"] += 1
                elif i+13 <= len(words):
                    key13 = hashlib.sha256(" ".join(words[i:i+13]).encode()).digest()
                    if key13 in index13:
                        matches += 1
                        errors.append(dict(check="sampled-text-overlap-over-12-words", source_id=sid, tracked_files=sorted(index13[key13])))
        leak_samples.append(dict(source_id=sid, available_windows=available, sampled_windows=len(chosen), matches=matches))
    # Inspect identifiers and numerical outputs only; no source-text excerpts enter this report.
    result = dict(passed=not errors, counts=dict(checks), errors=errors, text_exclusion_samples=leak_samples,
                  sample_seed=20261021, scope="Every asset pin and every page reference; 200 random text windows per nonempty source where available.")
    (records / "selftest-1a.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(passed=not errors, counts=dict(checks), errors=errors)))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
