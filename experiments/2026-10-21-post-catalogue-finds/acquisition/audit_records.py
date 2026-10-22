"""Display acquisition counts and bibliographic diagnostics only."""
import argparse
import collections
import csv
import json
import pathlib
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["frame", "states", "metadata", "front", "summary", "pending"])
    ap.add_argument("--root", type=pathlib.Path, required=True)
    ap.add_argument("--raw", type=pathlib.Path, required=True)
    ap.add_argument("--records", type=pathlib.Path, required=True)
    args = ap.parse_args()
    root, raw, records = args.root.resolve(), args.raw.resolve(), args.records.resolve()
    if args.command == "frame":
        directory = root / "experiments/2026-10-02-six-hour/kanmer-physical-use"
        data = json.loads((directory / "source-register.json").read_text(encoding="utf-8"))
        found = []
        def walk(x, keys=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    walk(v, keys + "/" + k)
            elif isinstance(x, list):
                for v in x:
                    walk(v, keys)
            elif isinstance(x, str) and (re.search(r'\.(?:pdf|html?|png|jpe?g|txt)$', x, re.I) or re.search(r'local|path|file', keys, re.I)):
                if not x.startswith(("http", "sha256")) and len(x) < 240:
                    found.append(dict(key=keys, value=x))
        walk(data)
        paths = re.findall(r'(?:research|data)/[a-zA-Z0-9_./-]+', (directory / "SOURCES.md").read_text(encoding="utf-8"))
        print(json.dumps(dict(references=found, directory_paths=paths, keys=list(data) if isinstance(data, dict) else [[*r.keys()] for r in data if isinstance(r, dict)],
             embedded_paths=re.findall(r'(?:local-witness/|data/|research/)[^\s`<>\"\)\]]+', (directory / "SOURCES.md").read_text(encoding="utf-8")))))
    if args.command == "states":
        items = []
        for path in sorted((raw / "processing").glob("*.json")):
            try:
                r = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            items.append({k: r.get(k) for k in ("source_id", "status", "pdf_pages", "image_only_pages", "text_basis", "observed_volume_year", "text_complete", "text_reason", "printed_page_detected_share")})
        print(json.dumps(items))
    if args.command == "pending":
        result = []
        basis = collections.Counter()
        for path in sorted((raw / "processing").glob("*.json")):
            r = json.loads(path.read_text(encoding="utf-8"))
            basis[r.get("text_basis", "none")] += 1
            if not r.get("text_complete"):
                result.append(dict(source_id=r["source_id"], pages=r.get("pdf_pages"), ocr_pages=len(r.get("needs_ocr", [])), archive_pages=r.get("ocr_page_mismatch"), error=r.get("text_reason"), identifier=r.get("identifier")))
        working = [dict(source_id=p.parent.name, page=p.stem) for p in (raw / "ocr-working").glob("*/*.png")]
        cache = []
        for p in (raw / "ocr-cache").glob("*.json"):
            try:
                c = json.loads(p.read_text(encoding="utf-8"))
                cache.append(dict(source_id=p.stem, completed=len(c.get("completed_pages", [])), last_page=max(c.get("completed_pages", [0]))))
            except json.JSONDecodeError:
                pass
        print(json.dumps(dict(basis=basis, pending=result, interrupted_run_images=working, ocr_cache=cache)))
    if args.command == "metadata":
        data = json.loads((records / "manifest-proposals-1a.json").read_text(encoding="utf-8"))
        print(json.dumps([dict(id=r["id"], title=r["title"], authors=r.get("authors_or_editors"), year=r.get("year_or_volume"), status=r["status"], failed=r.get("acquisition_failure")) for r in data["sources"]]))
    if args.command == "front":
        result = []
        for directory in sorted((raw / "text").iterdir()):
            if not directory.name.startswith("iar-"):
                continue
            pages = []
            for path in sorted(directory.glob("p*.txt"))[:12]:
                text = path.read_text(encoding="utf-8")
                years = re.findall(r'\b(?:19|20)\d{2}\s*[-\u2013\u2014]\s*(?:(?:19|20))?\d{2}\b', text)
                if years:
                    pages.append(dict(page=path.stem, years=years[:20]))
            result.append(dict(source_id=directory.name, front_years=pages))
        print(json.dumps(result))
    if args.command == "summary":
        with (records / "source-register-1a.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        data = json.loads((records / "manifest-proposals-1a.json").read_text(encoding="utf-8"))
        log = [json.loads(s) for s in (records / "acquisition-log-1a.jsonl").read_text(encoding="utf-8").splitlines()]
        print(json.dumps(dict(status=collections.Counter(r["status"] for r in rows), basis=collections.Counter(r["text_basis"] for r in rows),
            failed=[r["source_id"] for r in rows if r["status"] == "failed"], asset_count=len(data["sources"]),
            unpaged=[dict(source_id=r["source_id"], bytes=r["bytes"]) for r in rows if r["text_basis"] == "djvu-txt-unpaged"],
            asset_bytes=sum(r.get("actual_bytes", 0) for r in data["sources"]), network_bytes=sum(r["bytes"] for r in log),
            network_requests=len(log), pdf_pages=sum(int(r["pdf_pages"] or 0) for r in rows))))


if __name__ == "__main__":
    main()
