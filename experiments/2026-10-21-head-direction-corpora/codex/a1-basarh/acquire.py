"""Acquire the ten specified source files without reusing a destination.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/acquire.py
Outputs: acquisition records in the package and files and process logs in owned raw paths.
"""
import concurrent.futures
import datetime
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "experiments/2026-10-21-head-direction-corpora"
RAW = ROOT / "data/raw/2026-10-21-head-direction-corpora"
FILES = [
    ("1903-04", "dli207529-pdf", "in.ernet.dli.2015.207529", "2015.207529.Archaeological-Survey.pdf", 204293478, "2d952c7a8a9be1065d425bd5ddaa16f017eeae10"),
    ("1903-04", "dli207529-ocr", "in.ernet.dli.2015.207529", "2015.207529.Archaeological-Survey_djvu.txt", 971300, "f95663462e6b136b3651536940e8a7115c8255ea"),
    ("1903-04", "ignca21816-pdf", "in.gov.ignca.21816", "21816.pdf", 38614635, "9275652c9ad17af56a38e11050f1592c9ad45950"),
    ("1913-14", "ministry09311-pdf", "dli.ministry.09311", "17178.55107.pdf", 50488078, "b304e4ef9197109894fc5f9ba1132531022d7fea"),
    ("1913-14", "ministry09311-ocr", "dli.ministry.09311", "17178.55107_djvu.txt", 992428, "2dd167f2e4f9717130dede795d7eb039c5db657a"),
    ("1913-14", "dli35545-pdf", "in.ernet.dli.2015.35545", "2015.35545.Annual-Report-Of-The-Archaeological-Survey-Of-India-1913-14.pdf", 24146577, "a32a0c2621ccea5dea587fd9b32a87cf6676cd93"),
]


def acquire(task):
    year, label, item, filename, size, sha1 = task
    source = "asi-ar-" + year
    metadata = label.endswith("metadata")
    url = "https://archive.org/metadata/" + item if metadata else "https://archive.org/download/" + item + "/" + quote(filename)
    dest = RAW / ("src-asi-" + year + "-" + label)
    record = PACKAGE / "acquisition" / (source + "-" + label + ".json")
    publication_year = "1906" if year == "1903-04" else "1917"
    note = "Government of India publication of " + publication_year + "; public domain by age in India and the United States (our assessment); Internet Archive item states no licence"
    command = [sys.executable, "-I", str(PACKAGE / "fetch_source.py"), "--url", url,
               "--dest", str(dest), "--name", filename, "--record", str(record),
               "--source-id", source, "--title", "Archaeological Survey of India, Annual Report " + year,
               "--rights-status", "rights-unverified", "--rights-note", note]
    if sha1:
        command.extend(["--expect-sha1", sha1, "--expect-bytes", str(size)])
    if metadata:
        command.extend(["--note", "Observed Internet Archive item metadata; no fixed expected digest was supplied."])
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    log = RAW / "codex-a1" / (source + "-" + label + ".log")
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    summary = {"source": source, "label": label, "returncode": result.returncode, "log": log.relative_to(ROOT).as_posix()}
    if record.exists():
        rec = json.loads(record.read_text(encoding="utf-8"))
        summary.update({k: rec[k] for k in ("bytes", "sha1_matches_expected", "bytes_match_expected", "sha256")})
    elif result.returncode:
        failure = {"source_id": source, "url": url, "failure_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "error": result.stderr, "returncode": result.returncode, "local_directory": dest.relative_to(ROOT).as_posix()}
        failure_path = record.with_name(record.stem + "-failure.json")
        if not failure_path.exists():
            failure_path.parent.mkdir(parents=True, exist_ok=True)
            failure_path.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary), flush=True)
    return summary


def main():
    scratch = RAW / "codex-a1"
    scratch.mkdir(parents=True, exist_ok=True)
    initial = scratch / "git-status-initial.txt"
    if not initial.exists():
        result = subprocess.run(["git", "-c", "safe.directory=" + ROOT.as_posix(), "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, capture_output=True, text=True)
        initial.write_text(result.stdout, encoding="utf-8")
    tasks = FILES.copy()
    for year, label, item in [("1903-04", "dli207529", "in.ernet.dli.2015.207529"), ("1903-04", "ignca21816", "in.gov.ignca.21816"), ("1913-14", "ministry09311", "dli.ministry.09311"), ("1913-14", "dli35545", "in.ernet.dli.2015.35545")]:
        tasks.append((year, label + "-metadata", item, "metadata.json", None, None))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(acquire, tasks))
    (scratch / "acquisition-process-summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
